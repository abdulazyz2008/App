"""The core workflow: batch creation -> validation -> generation -> sending -> status tracking."""
import json
import multiprocessing
import os
import secrets
import shutil
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from datetime import date
from pathlib import Path

from . import certificate, config, db, mailer
from .data import load_table, placeholders_in, render, safe_filename, suggest_config, validate

_jobs_lock = threading.Lock()
_running: set[int] = set()

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def new_cert_code() -> str:
    return "CRT-" + "".join(secrets.choice(CODE_ALPHABET) for _ in range(10))


def default_config(columns: list[str], event_name: str) -> dict:
    cfg = suggest_config(columns)
    if event_name and "EVENT" not in cfg["mapping"]:
        cfg["mapping"]["EVENT"] = {"type": "text", "value": event_name}
    cfg.update({
        "template": certificate.default_template(),
        "email_subject": mailer.DEFAULT_SUBJECT,
        "email_body": mailer.DEFAULT_BODY,
        "filename_pattern": "{{ID}}_{{NAME}}_{{EVENT}}",
    })
    return cfg


def all_placeholders(cfg: dict) -> dict:
    cert = placeholders_in(*certificate.template_texts(cfg["template"]))
    email = placeholders_in(cfg.get("email_subject", ""), cfg.get("email_body", ""))
    pattern = placeholders_in(cfg.get("filename_pattern", ""))
    ordered = []
    for p in ["NAME", "ID"] + cert + email + pattern:
        if p not in ordered:
            ordered.append(p)
    return {"all": ordered, "certificate": cert, "email": email}


def create_batch(src: Path, original_name: str, batch_name: str) -> int:
    columns, rows = load_table(src)
    cfg = default_config(columns, batch_name)
    with db.tx() as c:
        cur = c.execute(
            "INSERT INTO batches (name, filename, created_at, columns_json, config_json) VALUES (?,?,?,?,?)",
            (batch_name or Path(original_name).stem, original_name, db.now(), json.dumps(columns), json.dumps(cfg)),
        )
        batch_id = cur.lastrowid
        for i, row in enumerate(rows):
            c.execute(
                "INSERT INTO records (batch_id, row_no, data_json, cert_code, updated_at) VALUES (?,?,?,?,?)",
                (batch_id, i + 2, json.dumps(row), new_cert_code(), db.now()),
            )
    revalidate(batch_id)
    return batch_id


def record_values(rec: dict, cfg: dict) -> dict:
    """Everything a template can reference for this one student."""
    from .data import resolve_values

    values = resolve_values(db.record_data(rec), cfg.get("mapping", {}))
    values["CERT_ID"] = rec["cert_code"]
    values["VERIFY_URL"] = f"{config.PUBLIC_BASE_URL.rstrip('/')}/verify/{rec['cert_code']}"
    values["ISSUE_DATE"] = date.today().strftime("%d %B %Y")
    return values


def _delete_cert(rec: dict) -> None:
    if rec.get("cert_file"):
        (config.CERT_DIR / rec["cert_file"]).unlink(missing_ok=True)


def revalidate(batch_id: int) -> dict:
    batch = db.get_batch(batch_id)
    cfg = batch["config"]
    recs = db.query("SELECT * FROM records WHERE batch_id=? ORDER BY row_no", (batch_id,))
    results = validate([db.record_data(r) for r in recs], cfg, all_placeholders(cfg)["certificate"])

    for rec, res in zip(recs, results):
        if rec["status"] in ("Sent", "Sending"):
            continue  # never rewrite history for something already delivered
        warnings = list(res["warnings"])
        if res["dedupe_key"]:
            prev = db.one(
                "SELECT at, email FROM send_log WHERE dedupe_key=? AND result='sent' AND record_id!=? ORDER BY at DESC LIMIT 1",
                (res["dedupe_key"], rec["id"]),
            )
            if prev:
                warnings.append(f"Already sent to {prev['email']} on {prev['at'][:10]}; will be skipped unless resent")
        if rec["status"] == "Generated" or rec["cert_file"]:
            _delete_cert(rec)  # template/mapping changed, the old PDF is stale
        db.update_record(
            rec["id"],
            name=res["name"], student_id=res["student_id"], email=res["email"],
            email_source=res["email_source"], dedupe_key=res["dedupe_key"],
            errors="; ".join(res["errors"]), warnings="; ".join(warnings),
            status="Invalid" if res["errors"] else "Pending",
            cert_file="", cert_sha256="", last_error="", attempts=0,
        )
    return db.status_counts(batch_id)


def _cert_filename(rec: dict, cfg: dict, values: dict) -> str:
    stem = safe_filename(render(cfg.get("filename_pattern") or "{{ID}}_{{NAME}}_{{EVENT}}", values))
    if not values.get("ID"):
        stem = f"row{rec['row_no']:04d}_{stem}"
    return f"{stem}.pdf"


def generate_one(rec: dict, cfg: dict, pdf: bytes | None = None) -> dict:
    values = record_values(rec, cfg)
    if pdf is None:
        pdf = certificate.render_pdf(cfg["template"], values, rec["cert_code"], title=f"Certificate - {values.get('NAME', '')}")
    folder = config.CERT_DIR / f"batch_{rec['batch_id']}"
    folder.mkdir(parents=True, exist_ok=True)
    fname = _cert_filename(rec, cfg, values)
    taken = db.one(
        "SELECT id FROM records WHERE batch_id=? AND cert_file=? AND id!=?",
        (rec["batch_id"], f"batch_{rec['batch_id']}/{fname}", rec["id"]),
    )
    if taken:
        fname = f"{Path(fname).stem}_row{rec['row_no']}.pdf"
    (folder / fname).write_bytes(pdf)
    rel = f"batch_{rec['batch_id']}/{fname}"
    db.update_record(rec["id"], status="Generated", cert_file=rel, cert_sha256=certificate.sha256(pdf), last_error="")
    return db.one("SELECT * FROM records WHERE id=?", (rec["id"],))


PARALLEL_THRESHOLD = 40
CHUNK = 100


def _render_all(recs: list[dict], cfg: dict):
    """Yield (record, pdf bytes or exception). Large batches render across all CPU cores."""
    bg = certificate.background_path(cfg["template"])
    jobs = [(cfg["template"], record_values(r, cfg), r["cert_code"], f"Certificate - {r['name']}", bg) for r in recs]
    if len(recs) < PARALLEL_THRESHOLD or (os.cpu_count() or 1) < 2:
        for rec, job in zip(recs, jobs):
            try:
                yield rec, certificate.render_job(job)
            except Exception as e:
                yield rec, e
        return
    done = 0
    try:
        ctx = multiprocessing.get_context("spawn")  # safe with the web server's threads
        with ProcessPoolExecutor(max_workers=os.cpu_count(), mp_context=ctx) as pool:
            for start in range(0, len(jobs), CHUNK):
                futures = [pool.submit(certificate.render_job, j) for j in jobs[start:start + CHUNK]]
                for rec, fut in zip(recs[start:start + CHUNK], futures):
                    try:
                        pdf = fut.result()
                    except BrokenProcessPool:
                        raise
                    except Exception as e:
                        pdf = e
                    done += 1
                    yield rec, pdf
    except BrokenProcessPool:
        pass  # worker processes unavailable: finish the remainder in-process
    for rec, job in zip(recs[done:], jobs[done:]):
        try:
            yield rec, certificate.render_job(job)
        except Exception as e:
            yield rec, e


def generate(batch_id: int) -> None:
    cfg = db.get_batch(batch_id)["config"]
    recs = db.query("SELECT * FROM records WHERE batch_id=? AND status='Pending' ORDER BY row_no", (batch_id,))
    for rec, result in _render_all(recs, cfg):
        try:
            if isinstance(result, Exception):
                raise result
            generate_one(rec, cfg, result)
        except Exception as e:  # one bad record must not stop the batch
            db.update_record(rec["id"], status="Failed", last_error=f"Generation failed: {e}")


def verified_attachment(rec: dict) -> tuple[bytes, str]:
    """Load the PDF for this record and prove it belongs to it before attaching (Rule 6)."""
    path = config.CERT_DIR / rec["cert_file"]
    data = path.read_bytes()
    if certificate.sha256(data) != rec["cert_sha256"]:
        raise RuntimeError("Integrity check failed: certificate file changed since generation")
    if certificate.pdf_subject(data) != rec["cert_code"]:
        raise RuntimeError("Integrity check failed: certificate does not belong to this student")
    return data, path.name


def _log(rec: dict, attachment: str, result: str, detail: str) -> None:
    with db.tx() as c:
        c.execute(
            "INSERT INTO send_log (record_id, dedupe_key, email, attachment, result, detail, at) VALUES (?,?,?,?,?,?,?)",
            (rec["id"], rec["dedupe_key"], rec["email"], attachment, result, detail, db.now()),
        )


def send(batch_id: int, record_ids: list[int] | None = None, allow_resend: bool = False) -> None:
    cfg = db.get_batch(batch_id)["config"]
    statuses = ["Pending", "Generated", "Failed"] + (["Sent", "Skipped"] if allow_resend else [])
    sql = f"SELECT * FROM records WHERE batch_id=? AND status IN ({','.join('?' * len(statuses))})"
    params: list = [batch_id, *statuses]
    if record_ids is not None:
        sql += f" AND id IN ({','.join('?' * len(record_ids))})"
        params += record_ids
    recs = db.query(sql + " ORDER BY row_no", params)

    with mailer.Sender() as sender:
        for rec in recs:
            # Duplicate prevention: same student + event + type already delivered somewhere.
            if not allow_resend:
                prev = db.one(
                    "SELECT at, email FROM send_log WHERE dedupe_key=? AND result='sent' LIMIT 1", (rec["dedupe_key"],)
                )
                if prev:
                    db.update_record(rec["id"], status="Skipped",
                                     last_error=f"Already sent to {prev['email']} on {prev['at'][:10]}")
                    continue
            try:
                if not rec["cert_file"] or not (config.CERT_DIR / rec["cert_file"]).exists():
                    rec = generate_one(rec, cfg)
                values = record_values(rec, cfg)
                pdf, fname = verified_attachment(rec)
                msg = mailer.build_message(
                    rec["email"], rec["name"],
                    render(cfg["email_subject"], values), render(cfg["email_body"], values),
                    pdf, fname, rec["cert_code"],
                )
            except Exception as e:
                db.update_record(rec["id"], status="Failed", last_error=str(e), attempts=rec["attempts"] + 1)
                _log(rec, rec.get("cert_file", ""), "failed", str(e))
                continue

            db.update_record(rec["id"], status="Sending")
            attempts, last_err = rec["attempts"], ""
            for attempt in range(config.MAX_SEND_ATTEMPTS):
                attempts += 1
                try:
                    detail = sender.send(msg, f"{rec['cert_code']}_{Path(fname).stem}")
                    db.update_record(rec["id"], status="Sent", sent_at=db.now(), attempts=attempts, last_error="")
                    _log(rec, fname, "sent", detail)
                    break
                except Exception as e:
                    last_err = f"{type(e).__name__}: {e}"
                    sender.close()
                    if attempt + 1 < config.MAX_SEND_ATTEMPTS:
                        time.sleep(min(2 ** attempt, 8))
            else:
                db.update_record(rec["id"], status="Failed", attempts=attempts, last_error=last_err)
                _log(rec, fname, "failed", last_err)
            if config.SEND_DELAY_SECONDS:
                time.sleep(config.SEND_DELAY_SECONDS)


def run_job(batch_id: int, kind: str, fn, *args, **kwargs) -> bool:
    """Run generate/send in the background. Only one job per batch at a time."""
    with _jobs_lock:
        if batch_id in _running:
            return False
        _running.add(batch_id)
    db.set_job(batch_id, kind)

    def worker():
        try:
            fn(batch_id, *args, **kwargs)
        finally:
            db.set_job(batch_id, "")
            with _jobs_lock:
                _running.discard(batch_id)

    threading.Thread(target=worker, daemon=True).start()
    return True


def is_running(batch_id: int) -> bool:
    with _jobs_lock:
        return batch_id in _running


def delete_batch(batch_id: int) -> None:
    shutil.rmtree(config.CERT_DIR / f"batch_{batch_id}", ignore_errors=True)
    with db.tx() as c:
        c.execute("DELETE FROM records WHERE batch_id=?", (batch_id,))
        c.execute("DELETE FROM batches WHERE id=?", (batch_id,))
