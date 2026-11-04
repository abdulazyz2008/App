"""SealSend HTTP API, organizer UI and the public verify / claim pages."""
import csv
import hmac
import html
import io
import json
import secrets
import time
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel

from . import certificate, chaos, config, copilot, crypto, db, mailer, pipeline
from .data import load_table

STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_app):
    # A crash mid-send leaves records in "Sending"; surface them as Failed so they can be retried.
    with db.tx() as c:
        c.execute("UPDATE records SET status='Failed', last_error='Interrupted while sending; retry' WHERE status='Sending'")
        c.execute("UPDATE batches SET job=''")
    crypto.private_key()  # create the signing key on first start
    yield


app = FastAPI(title="SealSend", docs_url=None, redoc_url=None, lifespan=lifespan)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    return resp


# ---------------------------------------------------------------- auth
SESSIONS: dict[str, float] = {}
SESSION_TTL = 12 * 3600
if not config.ADMIN_PASSWORD:
    config.ADMIN_PASSWORD = secrets.token_urlsafe(9)
    print(f"\n  No ADMIN_PASSWORD set. Temporary login -> user: {config.ADMIN_USER}  password: {config.ADMIN_PASSWORD}\n")


def require_auth(request: Request) -> None:
    token = request.cookies.get("sealsend_session", "")
    exp = SESSIONS.get(token)
    if not exp or exp < time.time():
        SESSIONS.pop(token, None)
        raise HTTPException(401, "Login required")


class Login(BaseModel):
    username: str
    password: str


_failed_logins: list[float] = []


@app.post("/api/login")
def login(body: Login, response: Response):
    now = time.time()
    _failed_logins[:] = [t for t in _failed_logins if now - t < 300]
    if len(_failed_logins) >= 10:
        raise HTTPException(429, "Too many failed attempts. Try again in a few minutes.")
    ok = hmac.compare_digest(body.username, config.ADMIN_USER) & hmac.compare_digest(body.password, config.ADMIN_PASSWORD)
    if not ok:
        _failed_logins.append(now)
        raise HTTPException(401, "Wrong username or password")
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = now + SESSION_TTL
    response.set_cookie("sealsend_session", token, httponly=True, samesite="strict", max_age=SESSION_TTL,
                        secure=config.PUBLIC_BASE_URL.startswith("https"))
    return {"ok": True}


@app.post("/api/logout")
def logout(request: Request, response: Response):
    SESSIONS.pop(request.cookies.get("sealsend_session", ""), None)
    response.delete_cookie("sealsend_session")
    return {"ok": True}


@app.get("/api/me", dependencies=[Depends(require_auth)])
def me():
    import os
    ai = config.COPILOT_ENGINE == "claude" or (config.COPILOT_ENGINE == "auto" and bool(os.environ.get("ANTHROPIC_API_KEY")))
    return {"user": config.ADMIN_USER, "mail_mode": config.mail_mode(), "mail_from": config.MAIL_FROM,
            "key_fingerprint": crypto.fingerprint(), "copilot": f"Claude · {config.COPILOT_MODEL}" if ai else "Offline parser",
            "public_base_url": config.PUBLIC_BASE_URL, "issuer": config.ISSUER_NAME,
            "themes": {k: {"label": v["label"], "description": v["description"]} for k, v in certificate.THEMES.items()},
            "presets": {k: v["label"] for k, v in mailer.PRESETS.items()}}


# ---------------------------------------------------------------- helpers
def get_batch_or_404(batch_id: int) -> dict:
    b = db.get_batch(batch_id)
    if not b:
        raise HTTPException(404, "Batch not found")
    return b


def get_record_or_404(record_id: int) -> dict:
    r = db.get_record(record_id)
    if not r:
        raise HTTPException(404, "Record not found")
    return r


def ensure_idle(batch_id: int) -> None:
    if pipeline.is_running(batch_id):
        raise HTTPException(409, "A job is already running for this batch")


def batch_summary(b: dict) -> dict:
    return {"id": b["id"], "name": b["name"], "filename": b["filename"], "created_at": b["created_at"],
            "job": b["job"], "counts": db.status_counts(b["id"]), "is_chaos": bool(b["is_chaos"]),
            "sealed": bool(b["seal"]), "chaos_phase": (b["chaos"] or {}).get("phase", "")}


async def _save_upload(upload: UploadFile, allowed: tuple[str, ...]) -> Path:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, f"Unsupported file type {suffix or '(none)'}. Allowed: {', '.join(allowed)}")
    data = await upload.read()
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File is larger than {config.MAX_UPLOAD_MB} MB")
    path = config.UPLOAD_DIR / f"{secrets.token_hex(8)}{suffix}"
    path.write_bytes(data)
    return path


def claim_url(rec: dict) -> str:
    return f"{config.PUBLIC_BASE_URL.rstrip('/')}/claim/{rec['claim_token']}" if rec["claim_token"] else ""


def verify_url(rec: dict) -> str:
    return f"{config.PUBLIC_BASE_URL.rstrip('/')}/verify/{rec['cert_code']}"


# ---------------------------------------------------------------- batches
@app.post("/api/batches", dependencies=[Depends(require_auth)])
async def create_batch(file: UploadFile = File(...), name: str = Form("")):
    path = await _save_upload(file, (".csv", ".xlsx", ".xlsm", ".xls", ".txt"))
    try:
        batch_id = pipeline.create_batch(path, file.filename or path.name, name.strip())
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(400, f"Could not read the spreadsheet: {e}")
    return batch_detail(batch_id)


@app.get("/api/batches", dependencies=[Depends(require_auth)])
def list_batches():
    return [batch_summary(db.get_batch(r["id"])) for r in db.query("SELECT id FROM batches ORDER BY id DESC")]


@app.get("/api/batches/{batch_id}", dependencies=[Depends(require_auth)])
def batch_detail(batch_id: int):
    b = get_batch_or_404(batch_id)
    sample = db.query("SELECT data_json FROM records WHERE batch_id=? ORDER BY row_no LIMIT 3", (batch_id,))
    return {**batch_summary(b), "columns": b["columns"], "config": b["config"], "seal": b["seal"], "chaos": b["chaos"],
            "placeholders": pipeline.all_placeholders(b["config"]),
            "sample_rows": [json.loads(r["data_json"]) for r in sample]}


@app.delete("/api/batches/{batch_id}", dependencies=[Depends(require_auth)])
def delete_batch(batch_id: int):
    get_batch_or_404(batch_id)
    ensure_idle(batch_id)
    pipeline.delete_batch(batch_id)
    return {"ok": True}


class ConfigIn(BaseModel):
    mapping: dict
    email_column: str = ""
    fallback_column: str = ""
    template: dict
    email_subject: str
    email_body: str
    filename_pattern: str = "{{ID}}_{{NAME}}_{{EVENT}}"
    rules: list = []
    auto_fix_emails: bool = True
    claim_links: bool = True


@app.put("/api/batches/{batch_id}/config", dependencies=[Depends(require_auth)])
def save_config(batch_id: int, body: ConfigIn):
    b = get_batch_or_404(batch_id)
    ensure_idle(batch_id)
    for col in (body.email_column, body.fallback_column):
        if col and col not in b["columns"]:
            raise HTTPException(400, f"Unknown column: {col}")
    if body.email_column and body.email_column == body.fallback_column:
        raise HTTPException(400, "Fallback email column must differ from the preferred one")
    mapping = {}
    for ph, src in body.mapping.items():
        if not isinstance(src, dict) or src.get("type") not in ("column", "text"):
            continue
        if src["type"] == "column" and src.get("value") not in b["columns"]:
            continue
        mapping[ph.upper()] = {"type": src["type"], "value": str(src.get("value", ""))[:300]}
    tpl = body.template
    if not isinstance(tpl.get("fields"), list) or not all(isinstance(f, dict) for f in tpl["fields"]):
        raise HTTPException(400, "Template must contain a list of fields")
    if tpl.get("theme", "classic") not in certificate.THEMES:
        raise HTTPException(400, "Unknown theme")
    rules, notes = copilot.sanitize(body.rules, b["columns"])
    cfg = body.model_dump()
    cfg.update({"mapping": mapping, "rules": rules})
    db.save_config(batch_id, cfg)
    counts = pipeline.revalidate(batch_id)
    pipeline.log_validation(batch_id, counts)
    return {"counts": counts, "placeholders": pipeline.all_placeholders(cfg), "notes": notes, "rules": rules}


@app.post("/api/batches/{batch_id}/background", dependencies=[Depends(require_auth)])
async def upload_background(batch_id: int, file: UploadFile = File(...)):
    b = get_batch_or_404(batch_id)
    ensure_idle(batch_id)
    path = await _save_upload(file, (".png", ".jpg", ".jpeg"))
    cfg = b["config"]
    cfg["template"]["background"] = path.name
    db.save_config(batch_id, cfg)
    pipeline.revalidate(batch_id)
    return {"background": path.name}


class CopilotIn(BaseModel):
    text: str


@app.post("/api/batches/{batch_id}/copilot", dependencies=[Depends(require_auth)])
def run_copilot(batch_id: int, body: CopilotIn):
    b = get_batch_or_404(batch_id)
    rows = [json.loads(r["data_json"]) for r in db.query("SELECT data_json FROM records WHERE batch_id=? ORDER BY row_no", (batch_id,))]
    return copilot.suggest(body.text, b["columns"], rows, b["config"]["mapping"])


RECORD_FIELDS = ("id", "row_no", "name", "student_id", "email", "email_source", "email_fix", "delivery", "theme",
                 "rule_label", "status", "errors", "warnings", "cert_code", "cert_file", "attempts", "last_error",
                 "sent_at", "claimed_at")


@app.get("/api/batches/{batch_id}/records", dependencies=[Depends(require_auth)])
def list_records(batch_id: int, status: str = "", q: str = "", limit: int = 200, offset: int = 0):
    get_batch_or_404(batch_id)
    sql, params = "SELECT * FROM records WHERE batch_id=?", [batch_id]
    if status == "Issues":
        sql += " AND (status IN ('Invalid','Failed') OR warnings!='')"
    elif status == "Ready":
        sql += " AND status IN ('Pending','Generated')"
    elif status == "Claims":
        sql += " AND status IN ('Claim','Claimed')"
    elif status:
        sql += " AND status=?"
        params.append(status)
    if q:
        sql += " AND (name LIKE ? OR email LIKE ? OR student_id LIKE ? OR cert_code LIKE ?)"
        params += [f"%{q}%"] * 4
    total = db.one(sql.replace("SELECT *", "SELECT COUNT(*) n", 1), params)["n"]
    rows = db.query(sql + " ORDER BY row_no LIMIT ? OFFSET ?", params + [min(max(limit, 1), 1000), max(offset, 0)])
    return {"total": total, "records": [{k: r[k] for k in RECORD_FIELDS} for r in rows]}


@app.get("/api/records/{record_id}", dependencies=[Depends(require_auth)])
def record_detail(record_id: int):
    rec = get_record_or_404(record_id)
    cfg = db.get_batch(rec["batch_id"])["config"]
    out = {k: rec[k] for k in RECORD_FIELDS}
    out.update({
        "batch_id": rec["batch_id"], "source_row": db.record_data(rec), "values": pipeline.record_values(rec, cfg),
        "mapping_lock": rec["mapping_lock"], "pdf_sha256": rec["pdf_sha256"], "signature": rec["signature"],
        "leaf_hash": rec["leaf_hash"], "verify_url": verify_url(rec) if rec["payload_json"] else "",
        "claim_url": claim_url(rec) if rec["cert_file"] else "",
        "events": db.query("SELECT at, level, kind, message FROM events WHERE record_id=? ORDER BY id", (record_id,)),
        "proof": None,
    })
    if rec["payload_json"]:
        p = pipeline.record_proof(rec)
        out["proof"] = {k: p.get(k) for k in ("signature_valid", "record_consistent", "sealed", "in_seal",
                                              "seal_signature_valid", "valid", "leaf_index", "leaf_count", "proof")}
        if rec["cert_file"] and (config.CERT_DIR / rec["cert_file"]).exists():
            out["proof"]["lock_check"] = pipeline.check_attachment(rec, (config.CERT_DIR / rec["cert_file"]).read_bytes(), cfg)
    return out


def _preview_record(batch_id: int, record_id: int | None) -> dict:
    if record_id:
        rec = get_record_or_404(record_id)
        if rec["batch_id"] != batch_id:
            raise HTTPException(404, "Record not in this batch")
        return rec
    rec = db.one("SELECT * FROM records WHERE batch_id=? AND status!='Invalid' ORDER BY row_no LIMIT 1", (batch_id,))
    rec = rec or db.one("SELECT * FROM records WHERE batch_id=? ORDER BY row_no LIMIT 1", (batch_id,))
    if not rec:
        raise HTTPException(404, "No records")
    return rec


@app.get("/api/batches/{batch_id}/preview/certificate", dependencies=[Depends(require_auth)])
def preview_certificate(batch_id: int, record_id: int | None = None, format: str = "pdf"):
    cfg = get_batch_or_404(batch_id)["config"]
    rec = _preview_record(batch_id, record_id)
    values = pipeline.record_values(rec, cfg)
    pdf = certificate.render_pdf(cfg["template"], values, rec["cert_code"], pipeline.expected_lock(rec, cfg, values),
                                 rec["theme"] or cfg["template"].get("theme", "classic"))
    if format == "png":
        png = certificate.pdf_to_png(pdf)
        if png is None:
            raise HTTPException(404, "PNG preview unavailable (install poppler-utils)")
        return Response(png, media_type="image/png", headers={"Cache-Control": "no-store"})
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=preview.pdf"})


@app.get("/api/batches/{batch_id}/preview/email", dependencies=[Depends(require_auth)])
def preview_email(batch_id: int, record_id: int | None = None):
    cfg = get_batch_or_404(batch_id)["config"]
    rec = _preview_record(batch_id, record_id)
    values = pipeline.record_values(rec, cfg)
    subject, body = pipeline.email_texts(rec, cfg, values)
    to = f"{rec['name']} <{rec['email']}>" if rec["email"] else (
        "Claim link (no usable email)" if rec["delivery"] == "claim" else "(no valid email)")
    return {"record_id": rec["id"], "row_no": rec["row_no"], "status": rec["status"], "errors": rec["errors"],
            "warnings": rec["warnings"], "theme": rec["theme"], "rule_label": rec["rule_label"],
            "from": f"{config.MAIL_FROM_NAME} <{config.MAIL_FROM}>", "to": to, "subject": subject, "body": body,
            "attachment": pipeline.cert_filename(rec, cfg, values)}


class SendIn(BaseModel):
    confirm: bool = False
    allow_resend: bool = False


@app.post("/api/batches/{batch_id}/generate", dependencies=[Depends(require_auth)])
def start_generate(batch_id: int):
    get_batch_or_404(batch_id)
    if not pipeline.run_job(batch_id, "generating", pipeline.generate):
        raise HTTPException(409, "A job is already running for this batch")
    return {"started": True}


@app.post("/api/batches/{batch_id}/send", dependencies=[Depends(require_auth)])
def start_send(batch_id: int, body: SendIn):
    get_batch_or_404(batch_id)
    if not body.confirm:
        raise HTTPException(400, "Sending requires explicit confirmation")
    if not pipeline.run_job(batch_id, "sending", pipeline.send, allow_resend=body.allow_resend):
        raise HTTPException(409, "A job is already running for this batch")
    return {"started": True}


@app.post("/api/batches/{batch_id}/retry", dependencies=[Depends(require_auth)])
def retry_failed(batch_id: int):
    get_batch_or_404(batch_id)
    ids = [r["id"] for r in db.query("SELECT id FROM records WHERE batch_id=? AND status='Failed'", (batch_id,))]
    if not ids:
        return {"started": False, "message": "No failed records"}
    if not pipeline.run_job(batch_id, "sending", pipeline.send, record_ids=ids):
        raise HTTPException(409, "A job is already running for this batch")
    return {"started": True, "count": len(ids)}


@app.post("/api/records/{record_id}/resend", dependencies=[Depends(require_auth)])
def resend_record(record_id: int):
    rec = get_record_or_404(record_id)
    if rec["status"] == "Invalid":
        raise HTTPException(400, "Fix the record's errors first")
    if rec["delivery"] == "claim":
        raise HTTPException(400, "This student has no usable email; share the claim link instead")
    if not pipeline.run_job(rec["batch_id"], "sending", pipeline.send, record_ids=[record_id], allow_resend=True):
        raise HTTPException(409, "A job is already running for this batch")
    db.log(rec["batch_id"], record_id, "info", "resend", "Organizer authorized a resend")
    return {"started": True}


@app.post("/api/batches/{batch_id}/verify-seal", dependencies=[Depends(require_auth)])
def verify_seal(batch_id: int):
    get_batch_or_404(batch_id)
    result = pipeline.verify_batch(batch_id)
    if result["sealed"]:
        db.log(batch_id, None, "ok" if result["intact"] else "block", "seal",
               "Seal verified: batch intact" if result["intact"] else f"Seal check FAILED: {len(result['problems'])} problems")
    return result


@app.get("/api/batches/{batch_id}/events", dependencies=[Depends(require_auth)])
def batch_events(batch_id: int, limit: int = 300, after: int = 0):
    get_batch_or_404(batch_id)
    rows = db.query("SELECT e.id, e.at, e.level, e.kind, e.message, e.record_id, r.name, r.row_no FROM events e "
                    "LEFT JOIN records r ON r.id=e.record_id WHERE e.batch_id=? AND e.id>? ORDER BY e.id DESC LIMIT ?",
                    (batch_id, after, min(limit, 2000)))
    return rows


@app.get("/api/records/{record_id}/certificate", dependencies=[Depends(require_auth)])
def download_certificate(record_id: int):
    rec = get_record_or_404(record_id)
    if not rec["cert_file"]:
        raise HTTPException(404, "Certificate not generated yet")
    path = config.CERT_DIR / rec["cert_file"]
    return FileResponse(path, media_type="application/pdf", filename=path.name)


@app.get("/api/batches/{batch_id}/report.csv", dependencies=[Depends(require_auth)])
def report(batch_id: int):
    b = get_batch_or_404(batch_id)
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Row", "Student ID", "Name", "Email", "Email Source", "Email Fix", "Delivery", "Theme", "Rule",
                "Status", "Certificate ID", "Certificate File", "SHA-256", "Mapping Lock", "Attempts", "Sent At",
                "Claim Link", "Verify Link", "Errors", "Warnings", "Last Error"])
    for r in db.query("SELECT * FROM records WHERE batch_id=? ORDER BY row_no", (batch_id,)):
        w.writerow([r["row_no"], r["student_id"], r["name"], r["email"], r["email_source"], r["email_fix"],
                    r["delivery"], r["theme"], r["rule_label"], r["status"], r["cert_code"],
                    Path(r["cert_file"]).name if r["cert_file"] else "", r["pdf_sha256"], r["mapping_lock"],
                    r["attempts"], r["sent_at"], claim_url(r) if r["cert_file"] else "",
                    verify_url(r) if r["payload_json"] else "", r["errors"], r["warnings"], r["last_error"]])
    fname = f"sealsend_report_{b['id']}.csv"
    return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@app.get("/api/batches/{batch_id}/certificates.zip", dependencies=[Depends(require_auth)])
def certificates_zip(batch_id: int):
    b = get_batch_or_404(batch_id)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        manifest = []
        for r in db.query("SELECT * FROM records WHERE batch_id=? AND cert_file!='' ORDER BY row_no", (batch_id,)):
            p = config.CERT_DIR / r["cert_file"]
            if p.exists():
                z.write(p, p.name)
                manifest.append({"file": p.name, "code": r["cert_code"], "sha256": r["pdf_sha256"],
                                 "leaf": r["leaf_hash"], "signature": r["signature"], "payload": json.loads(r["payload_json"] or "{}")})
        z.writestr("SEAL.json", json.dumps({"seal": b["seal"], "public_key_pem": crypto.public_pem(),
                                            "certificates": manifest}, indent=2, ensure_ascii=False))
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition": f'attachment; filename="sealsend_batch_{batch_id}.zip"'})


@app.get("/api/defaults", dependencies=[Depends(require_auth)])
def defaults():
    return {"fields": certificate.default_template()["fields"], "email_subject": mailer.DEFAULT_SUBJECT,
            "email_body": mailer.DEFAULT_BODY}


# ---------------------------------------------------------------- chaos test
@app.post("/api/chaos", dependencies=[Depends(require_auth)])
def start_chaos():
    batch_id = chaos.create()
    pipeline.run_job(batch_id, "chaos", chaos.run)
    return {"batch_id": batch_id}


@app.get("/api/batches/{batch_id}/chaos/forged.pdf", dependencies=[Depends(require_auth)])
def chaos_forged(batch_id: int):
    b = get_batch_or_404(batch_id)
    rep = (b["chaos"] or {}).get("report")
    if not rep:
        raise HTTPException(404, "Run the Chaos Test first")
    return FileResponse(config.DATA_DIR / "chaos" / rep["forged_file"], media_type="application/pdf",
                        filename=f"FORGED_{rep['verify_code']}.pdf")


@app.get("/sample/students.csv", dependencies=[Depends(require_auth)])
def sample_csv():
    return FileResponse(config.ROOT / "sample" / "students.csv", media_type="text/csv", filename="students.csv")


# ---------------------------------------------------------------- public pages
PUBLIC_CSS = """
:root{--bg:#f2f2f2;--card:#fff;--ink:#000;--sub:#6e6e73;--line:#e5e5e5;--fill:#000;--on:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#000;--card:#1c1c1e;--ink:#fff;--sub:#98989f;--line:#38383a;--fill:#fff;--on:#000}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 -apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:520px;margin:0 auto;padding:40px 16px 60px}
.brand{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--sub);text-align:center;margin-bottom:28px}
.icon{width:76px;height:76px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:38px;font-weight:700}
.icon.ok{background:var(--fill);color:var(--on)}.icon.bad{border:3px solid var(--ink);color:var(--ink)}
h1{font-size:30px;line-height:1.15;margin:0 0 6px;text-align:center;letter-spacing:-.02em}
.lead{text-align:center;color:var(--sub);margin:0 0 26px}.lead b{color:var(--ink)}
.group{background:var(--card);border-radius:14px;overflow:hidden;margin:0 0 22px}
.row{display:flex;justify-content:space-between;gap:16px;padding:13px 16px;border-top:.5px solid var(--line);font-size:15px}
.row:first-child{border-top:0}.row span:first-child{color:var(--sub)}.row span:last-child{text-align:right;font-weight:500;word-break:break-all}
.cap{font-size:13px;color:var(--sub);text-transform:uppercase;letter-spacing:.04em;margin:0 16px 8px}
.btn{display:block;width:100%;border:0;border-radius:12px;padding:15px;font-family:inherit;font-size:17px;font-weight:600;line-height:1.2;background:var(--fill);color:var(--on);cursor:pointer;text-align:center;text-decoration:none}
input[type=text],input[type=file]{width:100%;font:inherit;padding:13px 14px;border-radius:12px;border:1px solid var(--line);background:var(--card);color:var(--ink);margin-bottom:12px}
.note{font-size:13px;color:var(--sub);text-align:center;margin-top:18px}.mono{font-family:ui-monospace,Menlo,monospace;font-size:13px}
"""


def page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · SealSend</title>
<style>{PUBLIC_CSS}</style></head><body><div class="wrap"><div class="brand">SealSend Verify</div>{body}</div></body></html>""")


def _upload_form() -> str:
    return """<p class="cap">Check a PDF file</p>
<form class="group" style="padding:16px" method="post" action="/verify" enctype="multipart/form-data">
<input type="file" name="file" accept="application/pdf" required><button class="btn">Verify file</button></form>"""


def _footer() -> str:
    return (f'<p class="note">Issuer: {html.escape(config.ISSUER_NAME)}<br>Signing key '
            f'<span class="mono">{crypto.fingerprint()}</span> · <a href="/.well-known/sealsend-public-key.pem" '
            'style="color:inherit">public key</a></p>')


def _proof_rows(rec: dict, proof: dict) -> str:
    p = proof["payload"]
    tick = lambda ok: "✓ Valid" if ok else "✕ Failed"  # noqa: E731
    rows = [("Certificate ID", rec["cert_code"]), ("Issued by", p.get("issuer", "")),
            ("Digital signature", f"Ed25519 {tick(proof['signature_valid'] and proof['record_consistent'])}"),
            ("Batch seal", (f"✓ Included (#{proof.get('leaf_index', 0) + 1} of {proof.get('leaf_count', 0)})"
                            if proof["in_seal"] else "✕ Not in seal")),
            ("Seal signature", tick(proof["seal_signature_valid"])),
            ("File fingerprint", f"{rec['pdf_sha256'][:12]}…{rec['pdf_sha256'][-6:]}")]
    return "".join(f"<div class='row'><span>{html.escape(k)}</span><span>{html.escape(str(v))}</span></div>" for k, v in rows)


@app.get("/verify", response_class=HTMLResponse)
def verify_home():
    return page("Verify a certificate", f"""<h1>Verify a certificate</h1>
<p class="lead">Scan the QR code on a certificate, or upload the PDF to check it hasn’t been edited.</p>
<form class="group" style="padding:16px" method="get" onsubmit="location.href='/verify/'+encodeURIComponent(this.c.value.trim());return false">
<input type="text" name="c" placeholder="Certificate ID, e.g. SS-ABCD234567" required><button class="btn">Look up</button></form>
{_upload_form()}{_footer()}""")


@app.get("/verify/{code}", response_class=HTMLResponse)
def verify(code: str):
    rec = db.one("SELECT * FROM records WHERE cert_code=? AND payload_json!=''", (code,))
    if not rec:
        return page("Not found", f"""<div class="icon bad">✕</div><h1>Not verified</h1>
<p class="lead">No certificate <b>{html.escape(code)}</b> was issued by this issuer. It may be fake.</p>{_upload_form()}{_footer()}""")
    proof = pipeline.record_proof(rec)
    p = proof["payload"]
    if not proof["valid"]:
        return page("Verification failed", f"""<div class="icon bad">✕</div><h1>Verification failed</h1>
<p class="lead">The issuer’s records for <b>{html.escape(code)}</b> do not pass the cryptographic checks.</p>
<div class="group">{_proof_rows(rec, proof)}</div>{_footer()}""")
    detail = " · ".join(html.escape(x) for x in (p.get("achievement"), p.get("event")) if x)
    return page("Verified", f"""<div class="icon ok">✓</div><h1>Verified</h1>
<p class="lead">Issued to <b>{html.escape(p.get('name', ''))}</b><br>{detail}{('<br>' + html.escape(p['date'])) if p.get('date') else ''}</p>
<div class="group">{_proof_rows(rec, proof)}</div>{_upload_form()}{_footer()}""")


@app.post("/verify", response_class=HTMLResponse)
async def verify_upload(file: UploadFile = File(...)):
    data = await file.read(config.MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, "File too large")
    r = pipeline.verify_file(data)
    ok = r["status"] == "valid"
    reasons = "".join(f"<div class='row'><span>{html.escape(x)}</span><span></span></div>" for x in r["reasons"])
    extra = f"<div class='group'>{_proof_rows(r['record'], r['proof'])}</div>" if r.get("record") and r.get("proof") else ""
    name = ""
    if ok:
        p = r["proof"]["payload"]
        name = f"<p class='lead'>Issued to <b>{html.escape(p.get('name', ''))}</b><br>{html.escape(p.get('event', ''))}</p>"
    return page(r["title"], f"""<div class="icon {'ok' if ok else 'bad'}">{'✓' if ok else '✕'}</div><h1>{html.escape(r['title'])}</h1>
{name}<div class="group">{reasons}</div>{extra}{_upload_form()}{_footer()}""")


@app.get("/.well-known/sealsend-public-key.pem", response_class=PlainTextResponse)
def public_key():
    return crypto.public_pem()


def _claim_rec(token: str) -> dict:
    rec = db.one("SELECT * FROM records WHERE claim_token=? AND cert_file!=''", (token,)) if len(token) >= 16 else None
    if not rec:
        raise HTTPException(404, "This claim link is not valid")
    return rec


@app.get("/claim/{token}", response_class=HTMLResponse)
def claim_page(token: str):
    rec = _claim_rec(token)
    p = json.loads(rec["payload_json"] or "{}")
    ask = (f'<input type="text" name="student_id" placeholder="Your student ID" autocomplete="off" required>'
           if rec["student_id"] else "")
    return page("Claim your certificate", f"""<h1>Your certificate</h1>
<p class="lead">{html.escape(p.get('event', ''))}<br>Confirm it’s you to download it.</p>
<form class="group" style="padding:16px" method="post">{ask}<button class="btn">Download certificate</button></form>
<p class="note">Certificate {html.escape(rec['cert_code'])}. Anyone can verify it at /verify.</p>""")


@app.post("/claim/{token}")
def claim_download(token: str, student_id: str = Form("")):
    rec = _claim_rec(token)
    if rec["claim_attempts"] >= 5:
        return page("Locked", '<div class="icon bad">✕</div><h1>Link locked</h1><p class="lead">Too many wrong attempts. Ask the organizer for help.</p>')
    if rec["student_id"] and not hmac.compare_digest(student_id.strip().lower(), rec["student_id"].strip().lower()):
        db.update_record(rec["id"], claim_attempts=rec["claim_attempts"] + 1)
        db.log(rec["batch_id"], rec["id"], "warn", "claim", "Claim attempt with a wrong student ID")
        left = 4 - rec["claim_attempts"]
        return page("Try again", f'<div class="icon bad">✕</div><h1>That ID doesn’t match</h1>'
                                 f'<p class="lead">{left} attempt{"s" if left != 1 else ""} left.</p>'
                                 f'<a class="btn" href="/claim/{html.escape(token)}">Try again</a>')
    if rec["status"] == "Claim":
        db.update_record(rec["id"], status="Claimed", claimed_at=db.now())
    db.log(rec["batch_id"], rec["id"], "ok", "claim", "Certificate downloaded through the claim link")
    path = config.CERT_DIR / rec["cert_file"]
    return FileResponse(path, media_type="application/pdf", filename=path.name)


# ---------------------------------------------------------------- organizer UI
@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC / "index.html").read_text()
