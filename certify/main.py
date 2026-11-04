"""HTTP API + web UI for the certificate automation platform."""
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
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from pydantic import BaseModel

from . import certificate, config, db, mailer, pipeline
from .data import render

@asynccontextmanager
async def lifespan(_app):
    # A crash mid-send leaves records in "Sending"; surface them as Failed so they can be retried.
    with db.tx() as c:
        c.execute("UPDATE records SET status='Failed', last_error='Interrupted while sending; retry' WHERE status='Sending'")
        c.execute("UPDATE batches SET job=''")
    yield


app = FastAPI(title="Certify - Certificate Automation", docs_url=None, redoc_url=None, lifespan=lifespan)
STATIC = Path(__file__).parent / "static"

# ---------------------------------------------------------------- auth
SESSIONS: dict[str, float] = {}
SESSION_TTL = 12 * 3600
if not config.ADMIN_PASSWORD:
    config.ADMIN_PASSWORD = secrets.token_urlsafe(9)
    print(f"\n  No ADMIN_PASSWORD set. Temporary login -> user: {config.ADMIN_USER}  password: {config.ADMIN_PASSWORD}\n")


def require_auth(request: Request) -> None:
    token = request.cookies.get("certify_session", "")
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
    response.set_cookie("certify_session", token, httponly=True, samesite="strict", max_age=SESSION_TTL,
                        secure=config.PUBLIC_BASE_URL.startswith("https"))
    return {"ok": True}


@app.post("/api/logout")
def logout(request: Request, response: Response):
    SESSIONS.pop(request.cookies.get("certify_session", ""), None)
    response.delete_cookie("certify_session")
    return {"ok": True}


@app.get("/api/me", dependencies=[Depends(require_auth)])
def me():
    return {"user": config.ADMIN_USER, "mail_mode": config.mail_mode(), "mail_from": config.MAIL_FROM}


# ---------------------------------------------------------------- helpers
def get_batch_or_404(batch_id: int) -> dict:
    b = db.get_batch(batch_id)
    if not b:
        raise HTTPException(404, "Batch not found")
    return b


def get_record_or_404(record_id: int) -> dict:
    r = db.one("SELECT * FROM records WHERE id=?", (record_id,))
    if not r:
        raise HTTPException(404, "Record not found")
    return r


def ensure_idle(batch_id: int) -> None:
    if pipeline.is_running(batch_id):
        raise HTTPException(409, "A job is already running for this batch")


def batch_summary(b: dict) -> dict:
    return {
        "id": b["id"], "name": b["name"], "filename": b["filename"], "created_at": b["created_at"],
        "job": b["job"], "counts": db.status_counts(b["id"]),
    }


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
    rows = db.query("SELECT id FROM batches ORDER BY id DESC")
    return [batch_summary(db.get_batch(r["id"])) for r in rows]


@app.get("/api/batches/{batch_id}", dependencies=[Depends(require_auth)])
def batch_detail(batch_id: int):
    b = get_batch_or_404(batch_id)
    sample = db.query("SELECT data_json FROM records WHERE batch_id=? ORDER BY row_no LIMIT 3", (batch_id,))
    return {
        **batch_summary(b),
        "columns": b["columns"],
        "config": b["config"],
        "placeholders": pipeline.all_placeholders(b["config"]),
        "sample_rows": [json.loads(r["data_json"]) for r in sample],
    }


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


@app.put("/api/batches/{batch_id}/config", dependencies=[Depends(require_auth)])
def save_config(batch_id: int, body: ConfigIn):
    b = get_batch_or_404(batch_id)
    ensure_idle(batch_id)
    for col in (body.email_column, body.fallback_column):
        if col and col not in b["columns"]:
            raise HTTPException(400, f"Unknown column: {col}")
    mapping = {}
    for ph, src in body.mapping.items():
        if not isinstance(src, dict) or src.get("type") not in ("column", "text"):
            continue
        if src["type"] == "column" and src.get("value") not in b["columns"]:
            continue
        mapping[ph.upper()] = {"type": src["type"], "value": str(src.get("value", ""))}
    tpl = body.template
    if not isinstance(tpl.get("fields"), list):
        raise HTTPException(400, "Template must contain a list of fields")
    cfg = body.model_dump()
    cfg["mapping"] = mapping
    db.save_config(batch_id, cfg)
    counts = pipeline.revalidate(batch_id)
    return {"counts": counts, "placeholders": pipeline.all_placeholders(cfg)}


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


@app.get("/api/batches/{batch_id}/records", dependencies=[Depends(require_auth)])
def list_records(batch_id: int, status: str = "", q: str = "", limit: int = 200, offset: int = 0):
    get_batch_or_404(batch_id)
    sql, params = "SELECT * FROM records WHERE batch_id=?", [batch_id]
    if status:
        sql += " AND status=?"
        params.append(status)
    if q:
        sql += " AND (name LIKE ? OR email LIKE ? OR student_id LIKE ?)"
        params += [f"%{q}%"] * 3
    total = db.one(sql.replace("SELECT *", "SELECT COUNT(*) n", 1), params)["n"]
    rows = db.query(sql + " ORDER BY row_no LIMIT ? OFFSET ?", params + [min(limit, 1000), offset])
    keep = ("id", "row_no", "name", "student_id", "email", "email_source", "status", "errors", "warnings",
            "cert_code", "cert_file", "attempts", "last_error", "sent_at")
    return {"total": total, "records": [{k: r[k] for k in keep} for r in rows]}


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
    pdf = certificate.render_pdf(cfg["template"], pipeline.record_values(rec, cfg), rec["cert_code"])
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
    return {
        "record_id": rec["id"], "row_no": rec["row_no"], "status": rec["status"], "errors": rec["errors"],
        "from": f"{config.MAIL_FROM_NAME} <{config.MAIL_FROM}>",
        "to": f"{rec['name']} <{rec['email']}>" if rec["email"] else "(no valid email)",
        "subject": render(cfg["email_subject"], values),
        "body": render(cfg["email_body"], values),
        "attachment": pipeline._cert_filename(rec, cfg, values),
    }


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
    if not pipeline.run_job(rec["batch_id"], "sending", pipeline.send, record_ids=[record_id], allow_resend=True):
        raise HTTPException(409, "A job is already running for this batch")
    return {"started": True}


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
    w.writerow(["Row", "Student ID", "Name", "Email", "Email Source", "Status", "Certificate ID",
                "Certificate File", "Attempts", "Sent At", "Errors", "Warnings", "Last Error"])
    for r in db.query("SELECT * FROM records WHERE batch_id=? ORDER BY row_no", (batch_id,)):
        w.writerow([r["row_no"], r["student_id"], r["name"], r["email"], r["email_source"], r["status"],
                    r["cert_code"], Path(r["cert_file"]).name if r["cert_file"] else "", r["attempts"],
                    r["sent_at"], r["errors"], r["warnings"], r["last_error"]])
    fname = f"report_{b['id']}_{b['name']}.csv".replace(" ", "_")
    return Response(out.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@app.get("/api/batches/{batch_id}/certificates.zip", dependencies=[Depends(require_auth)])
def certificates_zip(batch_id: int):
    get_batch_or_404(batch_id)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for r in db.query("SELECT cert_file FROM records WHERE batch_id=? AND cert_file!=''", (batch_id,)):
            p = config.CERT_DIR / r["cert_file"]
            if p.exists():
                z.write(p, p.name)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition": f'attachment; filename="certificates_batch_{batch_id}.zip"'})


@app.get("/api/defaults", dependencies=[Depends(require_auth)])
def defaults():
    return {"template": certificate.default_template(), "email_subject": mailer.DEFAULT_SUBJECT,
            "email_body": mailer.DEFAULT_BODY}


# ---------------------------------------------------------------- public verification
@app.get("/verify/{code}", response_class=HTMLResponse)
def verify(code: str):
    rec = db.one("SELECT * FROM records WHERE cert_code=? AND status IN ('Generated','Sent','Sending')", (code,))
    if rec:
        b = db.get_batch(rec["batch_id"])
        values = pipeline.record_values(rec, b["config"])
        rows = "".join(
            f"<tr><th>{k}</th><td>{html.escape(values.get(v, ''))}</td></tr>"
            for k, v in (("Name", "NAME"), ("Event", "EVENT"), ("Certificate", "CERT_TYPE"),
                         ("Achievement", "ACHIEVEMENT"), ("Date", "DATE")) if values.get(v)
        )
        body = f'<h1 class="ok">✓ Valid certificate</h1><p class="code">{html.escape(code)}</p><table>{rows}</table>'
    else:
        body = f'<h1 class="bad">✗ Not found</h1><p>No issued certificate matches <b>{html.escape(code)}</b>.</p>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Certificate Verification</title><style>
body{{font-family:system-ui,sans-serif;background:#f4f5f7;margin:0;display:flex;justify-content:center;padding:48px 16px;color:#1d2433}}
.card{{background:#fff;border-radius:12px;padding:32px;max-width:460px;width:100%;box-shadow:0 2px 12px rgba(0,0,0,.08)}}
h1{{font-size:22px;margin:0 0 4px}}.ok{{color:#127a3e}}.bad{{color:#b42318}}.code{{color:#667;font-family:monospace;margin:0 0 20px}}
table{{width:100%;border-collapse:collapse}}th{{text-align:left;color:#667;font-weight:500;padding:8px 12px 8px 0;width:35%}}
td{{padding:8px 0;font-weight:600}}tr+tr{{border-top:1px solid #eee}}</style></head>
<body><div class="card">{body}</div></body></html>"""


# ---------------------------------------------------------------- UI
@app.get("/sample/students.csv", dependencies=[Depends(require_auth)])
def sample_csv():
    return FileResponse(config.ROOT / "sample" / "students.csv", media_type="text/csv", filename="students.csv")


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC / "index.html").read_text()
