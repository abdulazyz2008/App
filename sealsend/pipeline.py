"""The core workflow and its proofs.

upload -> validate -> map -> template/rules -> generate + sign -> seal (Merkle) ->
verify every attachment (Mapping Lock + hash + signature) -> deliver with self-healing -> ledger
"""
import json
import multiprocessing
import os
import secrets
import shutil
import threading
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from datetime import date
from pathlib import Path

from . import certificate, config, copilot, crypto, db, mailer
from .data import (load_table, normalize_email, fix_email_typo, placeholders_in, render, resolve_values,
                   safe_filename, suggest_config, valid_email, validate)

_jobs_lock = threading.Lock()
_running: set[int] = set()
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ISSUED = ("Sent", "Sending", "Claim", "Claimed")  # never silently rewritten once a student has it


def new_cert_code() -> str:
    return "SS-" + "".join(secrets.choice(CODE_ALPHABET) for _ in range(10))


# ---------------------------------------------------------------- configuration
def default_config(columns: list[str], event_name: str) -> dict:
    cfg = suggest_config(columns)
    if event_name and "EVENT" not in cfg["mapping"]:
        cfg["mapping"]["EVENT"] = {"type": "text", "value": event_name}
    cfg.update({
        "template": certificate.default_template(),
        "email_subject": mailer.DEFAULT_SUBJECT,
        "email_body": mailer.DEFAULT_BODY,
        "filename_pattern": "{{ID}}_{{NAME}}_{{EVENT}}",
        "rules": [],
        "auto_fix_emails": True,
        "claim_links": True,
    })
    return cfg


def all_placeholders(cfg: dict) -> dict:
    cert = placeholders_in(*certificate.template_texts(cfg["template"]))
    email_texts = [cfg.get("email_subject", ""), cfg.get("email_body", "")]
    for r in cfg.get("rules", []):
        p = mailer.PRESETS.get(r.get("email"), {})
        email_texts += [r.get("email_subject", ""), r.get("email_body", ""), p.get("subject", ""), p.get("body", "")]
    email = placeholders_in(*email_texts)
    pattern = placeholders_in(cfg.get("filename_pattern", ""))
    ordered = []
    for p in ["NAME", "ID"] + cert + email + pattern:
        if p not in ordered:
            ordered.append(p)
    return {"all": ordered, "certificate": cert, "email": email}


def create_batch(src: Path, original_name: str, batch_name: str, cfg_overrides: dict | None = None,
                 chaos: dict | None = None) -> int:
    columns, rows = load_table(src)
    cfg = default_config(columns, batch_name)
    cfg.update(cfg_overrides or {})
    with db.tx() as c:
        cur = c.execute(
            "INSERT INTO batches (name, filename, created_at, columns_json, config_json, is_chaos, chaos_json) VALUES (?,?,?,?,?,?,?)",
            (batch_name or Path(original_name).stem, original_name, db.now(), json.dumps(columns), json.dumps(cfg),
             1 if chaos else 0, json.dumps(chaos) if chaos else ""),
        )
        batch_id = cur.lastrowid
        for i, row in enumerate(rows):
            c.execute("INSERT INTO records (batch_id, row_no, data_json, cert_code, updated_at) VALUES (?,?,?,?,?)",
                      (batch_id, i + 2, json.dumps(row), new_cert_code(), db.now()))
    db.log(batch_id, None, "info", "upload", f"Uploaded {original_name}: {len(rows)} rows, {len(columns)} columns")
    log_validation(batch_id, revalidate(batch_id))
    return batch_id


def log_validation(batch_id: int, counts: dict) -> None:
    claims = db.one("SELECT COUNT(*) n FROM records WHERE batch_id=? AND delivery='claim' AND status='Pending'",
                    (batch_id,))["n"]
    fixed = db.one("SELECT COUNT(*) n FROM records WHERE batch_id=? AND email_fix!='' AND status='Pending'",
                   (batch_id,))["n"]
    msg = f"Validation: {counts.get('Pending', 0)} ready, {counts.get('Invalid', 0)} blocked"
    if fixed:
        msg += f", {fixed} emails auto-fixed"
    if claims:
        msg += f", {claims} will get a claim link"
    db.log(batch_id, None, "warn" if counts.get("Invalid") else "ok", "validate", msg)


# ---------------------------------------------------------------- per-record values
def record_values(rec: dict, cfg: dict) -> dict:
    values = resolve_values(db.record_data(rec), cfg.get("mapping", {}))
    values["CERT_ID"] = rec["cert_code"]
    values["VERIFY_URL"] = f"{config.PUBLIC_BASE_URL.rstrip('/')}/verify/{rec['cert_code']}"
    values["ISSUE_DATE"] = date.today().strftime("%d %B %Y")
    values["ISSUER"] = config.ISSUER_NAME
    return values


def record_rule(rec: dict, cfg: dict) -> dict | None:
    return copilot.evaluate(cfg.get("rules", []), db.record_data(rec))


def email_texts(rec: dict, cfg: dict, values: dict) -> tuple[str, str]:
    rule = record_rule(rec, cfg)
    subject, body = cfg["email_subject"], cfg["email_body"]
    if rule:
        if rule.get("email") == "custom" and rule.get("email_subject"):
            subject, body = rule["email_subject"], rule.get("email_body") or body
        elif rule.get("email") in mailer.PRESETS and rule["email"] != "standard":
            p = mailer.PRESETS[rule["email"]]
            subject, body = p["subject"], p["body"]
    return render(subject, values), render(body, values)


def cert_filename(rec: dict, cfg: dict, values: dict) -> str:
    stem = safe_filename(render(cfg.get("filename_pattern") or "{{ID}}_{{NAME}}_{{EVENT}}", values))
    if not values.get("ID"):
        stem = f"row{rec['row_no']:04d}_{stem}"
    return f"{stem}.pdf"


def expected_lock(rec: dict, cfg: dict, values: dict | None = None) -> str:
    values = values or record_values(rec, cfg)
    return crypto.mapping_lock(rec["student_id"], rec["email"], values.get("EVENT", ""), rec["cert_code"])


def _delete_cert(rec: dict) -> None:
    if rec.get("cert_file"):
        (config.CERT_DIR / rec["cert_file"]).unlink(missing_ok=True)


# ---------------------------------------------------------------- validation
def revalidate(batch_id: int) -> dict:
    batch = db.get_batch(batch_id)
    cfg = batch["config"]
    recs = db.query("SELECT * FROM records WHERE batch_id=? ORDER BY row_no", (batch_id,))
    results = validate([db.record_data(r) for r in recs], cfg, all_placeholders(cfg)["certificate"])
    dropped_seal = False
    for rec, res in zip(recs, results):
        if rec["status"] in ISSUED:
            continue
        warnings = list(res["warnings"])
        if res["dedupe_key"] and not res["errors"]:
            prev = db.one("SELECT at, email FROM send_log WHERE dedupe_key=? AND result='sent' AND record_id!=? "
                          "ORDER BY at DESC LIMIT 1", (res["dedupe_key"], rec["id"]))
            if prev:
                warnings.append(f"Already sent to {prev['email']} on {prev['at'][:10]}; will be skipped unless resent")
        if rec["cert_file"]:
            _delete_cert(rec)  # template, mapping or data changed: the old PDF is stale
            dropped_seal = True
        rule = copilot.evaluate(cfg.get("rules", []), db.record_data(rec)) if not res["errors"] else None
        db.update_record(
            rec["id"], name=res["name"], student_id=res["student_id"], email=res["email"],
            email_source=res["email_source"], email_fix=res["email_fix"], delivery=res["delivery"],
            dedupe_key=res["dedupe_key"], errors="; ".join(res["errors"]), warnings="; ".join(warnings),
            theme=(rule or {}).get("theme") or cfg["template"].get("theme", "classic"),
            rule_label=(rule or {}).get("label", ""),
            status="Invalid" if res["errors"] else "Pending",
            cert_file="", pdf_sha256="", mapping_lock="", payload_json="", signature="", leaf_hash="",
            last_error="", attempts=0,
        )
    if dropped_seal and batch["seal"]:
        db.set_batch(batch_id, seal_json="")
        db.log(batch_id, None, "info", "seal", "Seal cleared: certificates changed and will be re-sealed")
    return db.status_counts(batch_id)


# ---------------------------------------------------------------- generation + signing
PARALLEL_THRESHOLD = 40
CHUNK = 100


def _job(rec: dict, cfg: dict, bg: str):
    values = record_values(rec, cfg)
    lock = expected_lock(rec, cfg, values)
    theme = rec["theme"] or cfg["template"].get("theme", "classic")
    job = (cfg["template"], values, rec["cert_code"], lock, theme, f"Certificate - {values.get('NAME', '')}", bg)
    return job, values, lock


def _render_all(jobs: list[tuple]):
    """Yield PDF bytes or the exception, in order. Large batches use every CPU core."""
    done = 0
    if len(jobs) >= PARALLEL_THRESHOLD and (os.cpu_count() or 1) > 1:
        try:
            ctx = multiprocessing.get_context("spawn")  # safe alongside the web server's threads
            with ProcessPoolExecutor(max_workers=os.cpu_count(), mp_context=ctx) as pool:
                for start in range(0, len(jobs), CHUNK):
                    futures = [pool.submit(certificate.render_job, j) for j in jobs[start:start + CHUNK]]
                    for fut in futures:
                        try:
                            out = fut.result()
                        except BrokenProcessPool:
                            raise
                        except Exception as e:
                            out = e
                        done += 1
                        yield out
        except BrokenProcessPool:
            pass  # worker processes unavailable: finish the remainder in-process
    for job in jobs[done:]:
        try:
            yield certificate.render_job(job)
        except Exception as e:
            yield e


def finalize(rec: dict, cfg: dict, pdf: bytes, values: dict, lock: str) -> dict:
    """Store the PDF, sign it and compute its Merkle leaf."""
    folder = config.CERT_DIR / f"batch_{rec['batch_id']}"
    folder.mkdir(parents=True, exist_ok=True)
    fname = cert_filename(rec, cfg, values)
    taken = db.one("SELECT id FROM records WHERE batch_id=? AND cert_file=? AND id!=?",
                   (rec["batch_id"], f"batch_{rec['batch_id']}/{fname}", rec["id"]))
    if taken:
        fname = f"{Path(fname).stem}_row{rec['row_no']}.pdf"
    (folder / fname).write_bytes(pdf)
    sha = certificate.sha256(pdf)
    payload = {
        "v": 1, "code": rec["cert_code"], "name": values.get("NAME", ""), "event": values.get("EVENT", ""),
        "cert_type": values.get("CERT_TYPE", ""), "achievement": values.get("ACHIEVEMENT", ""),
        "date": values.get("DATE", ""), "issuer": config.ISSUER_NAME, "batch": rec["batch_id"],
        "pdf_sha256": sha, "key": crypto.fingerprint(),
    }
    db.update_record(
        rec["id"], status="Generated" if rec["status"] not in ISSUED else rec["status"],
        cert_file=f"batch_{rec['batch_id']}/{fname}", pdf_sha256=sha, mapping_lock=lock,
        payload_json=json.dumps(payload, ensure_ascii=False), signature=crypto.sign(crypto.canonical(payload)),
        leaf_hash=crypto.leaf_hash(rec["cert_code"], sha, lock),
        claim_token=rec["claim_token"] or secrets.token_urlsafe(16), last_error="",
    )
    return db.get_record(rec["id"])


def regenerate(rec: dict, cfg: dict) -> dict:
    job, values, lock = _job(rec, cfg, certificate.background_path(cfg["template"]))
    return finalize(rec, cfg, certificate.render_job(job), values, lock)


def _generate_records(recs: list[dict], cfg: dict) -> tuple[int, int]:
    bg = certificate.background_path(cfg["template"])
    prepared = [_job(r, cfg, bg) for r in recs]
    ok = failed = 0
    for rec, (job, values, lock), out in zip(recs, prepared, _render_all([p[0] for p in prepared])):
        try:
            if isinstance(out, Exception):
                raise out
            finalize(rec, cfg, out, values, lock)
            ok += 1
        except Exception as e:  # one bad record never stops the batch
            failed += 1
            db.update_record(rec["id"], status="Failed", last_error=f"Generation failed: {e}")
            db.log(rec["batch_id"], rec["id"], "error", "generate", f"Generation failed: {e}")
    return ok, failed


def generate(batch_id: int) -> None:
    cfg = db.get_batch(batch_id)["config"]
    recs = db.query("SELECT * FROM records WHERE batch_id=? AND status='Pending' ORDER BY row_no", (batch_id,))
    t = time.time()
    ok, failed = _generate_records(recs, cfg)
    db.log(batch_id, None, "ok" if not failed else "warn", "generate",
           f"Generated and signed {ok} certificates in {time.time() - t:.1f}s" + (f"; {failed} failed" if failed else ""))
    seal_batch(batch_id)


# ---------------------------------------------------------------- batch seal
def _sealed_records(batch_id: int) -> list[dict]:
    return db.query("SELECT * FROM records WHERE batch_id=? AND leaf_hash!='' ORDER BY row_no", (batch_id,))


def seal_batch(batch_id: int) -> dict | None:
    recs = _sealed_records(batch_id)
    if not recs:
        return None
    body = {"v": 1, "batch": batch_id, "root": crypto.merkle_root([r["leaf_hash"] for r in recs]),
            "count": len(recs), "sealed_at": db.now(), "key": crypto.fingerprint(),
            "algo": "SHA-256 Merkle tree, Ed25519 signature"}
    seal = {**body, "signature": crypto.sign(crypto.canonical(body))}
    db.set_batch(batch_id, seal_json=json.dumps(seal))
    db.log(batch_id, None, "ok", "seal", f"Batch sealed: {len(recs)} certificates, Merkle root {body['root'][:16]}…")
    return seal


def verify_batch(batch_id: int) -> dict:
    """Recompute everything from the files on disk and check it against the signed seal."""
    seal = db.get_batch(batch_id)["seal"]
    if not seal:
        return {"sealed": False, "intact": False, "problems": [], "checked": 0}
    body = {k: v for k, v in seal.items() if k != "signature"}
    sig_ok = crypto.verify(crypto.canonical(body), seal["signature"])
    problems, leaves = [], []
    for rec in _sealed_records(batch_id):
        path = config.CERT_DIR / rec["cert_file"]
        sha_now = certificate.sha256(path.read_bytes()) if path.exists() else "missing"
        leaves.append(crypto.leaf_hash(rec["cert_code"], sha_now, rec["mapping_lock"]))
        who = f"Row {rec['row_no']} · {rec['name']}"
        if sha_now == "missing":
            problems.append({"record_id": rec["id"], "who": who, "reason": "Certificate file is missing"})
        elif sha_now != rec["pdf_sha256"]:
            problems.append({"record_id": rec["id"], "who": who, "reason": "File changed after it was signed"})
        try:
            payload = json.loads(rec["payload_json"])
        except ValueError:
            payload = {}
        if not crypto.verify(crypto.canonical(payload), rec["signature"]) or payload.get("pdf_sha256") != rec["pdf_sha256"]:
            problems.append({"record_id": rec["id"], "who": who, "reason": "Signed record does not match"})
    root_now = crypto.merkle_root(leaves)
    root_ok = root_now == seal["root"] and len(leaves) == seal["count"]
    return {"sealed": True, "intact": sig_ok and root_ok and not problems, "signature_valid": sig_ok,
            "root_matches": root_ok, "sealed_root": seal["root"], "recomputed_root": root_now,
            "count": seal["count"], "checked": len(leaves), "problems": problems, "checked_at": db.now()}


def record_proof(rec: dict) -> dict:
    """Signature + Merkle inclusion status for one certificate (used by the public verify page)."""
    try:
        payload = json.loads(rec["payload_json"] or "{}")
    except ValueError:
        payload = {}
    sig_ok = bool(payload) and crypto.verify(crypto.canonical(payload), rec["signature"])
    consistent = sig_ok and payload.get("pdf_sha256") == rec["pdf_sha256"] and payload.get("code") == rec["cert_code"]
    batch = db.get_batch(rec["batch_id"])
    seal = batch["seal"] if batch else None
    out = {"payload": payload, "signature_valid": sig_ok, "record_consistent": consistent,
           "sealed": bool(seal), "in_seal": False, "seal_signature_valid": False, "proof": [], "seal": seal}
    if seal:
        body = {k: v for k, v in seal.items() if k != "signature"}
        out["seal_signature_valid"] = crypto.verify(crypto.canonical(body), seal["signature"])
        leaves = [r["leaf_hash"] for r in _sealed_records(rec["batch_id"])]
        if rec["leaf_hash"] in leaves:
            idx = leaves.index(rec["leaf_hash"])
            proof = crypto.merkle_proof(leaves, idx)
            out["proof"] = proof
            out["in_seal"] = crypto.verify_proof(rec["leaf_hash"], proof, seal["root"])
            out["leaf_index"], out["leaf_count"] = idx, len(leaves)
    out["valid"] = consistent and out["in_seal"] and out["seal_signature_valid"]
    return out


# ---------------------------------------------------------------- send-time checks
def check_attachment(rec: dict, data: bytes, cfg: dict) -> list[str]:
    """Every reason this file must NOT be attached to this student's email (empty list = safe)."""
    problems = []
    meta = certificate.read_proof(data)
    if meta["code"] and meta["code"] != rec["cert_code"]:
        problems.append(f"Attachment belongs to certificate {meta['code']}, not {rec['cert_code']}")
    if meta["lock"] != expected_lock(rec, cfg):
        problems.append("Mapping Lock mismatch: student, email and event do not match this file")
    if certificate.sha256(data) != rec["pdf_sha256"]:
        problems.append("File differs from the signed original")
    try:
        payload = json.loads(rec["payload_json"] or "{}")
    except ValueError:
        payload = {}
    if not crypto.verify(crypto.canonical(payload), rec["signature"]) or payload.get("pdf_sha256") != rec["pdf_sha256"]:
        problems.append("Signature check failed")
    return problems


def verified_attachment(rec: dict, cfg: dict) -> tuple[dict, bytes, bool]:
    """Return (record, pdf bytes, healed). Blocks wrong files; self-heals by regenerating once."""
    path = config.CERT_DIR / rec["cert_file"] if rec["cert_file"] else None
    data = path.read_bytes() if path and path.exists() else b""
    problems = check_attachment(rec, data, cfg) if data else ["Certificate file is missing"]
    if not problems:
        return rec, data, False
    db.log(rec["batch_id"], rec["id"], "block", "lock", "Blocked before sending: " + "; ".join(problems))
    rec = regenerate(rec, cfg)
    data = (config.CERT_DIR / rec["cert_file"]).read_bytes()
    problems = check_attachment(rec, data, cfg)
    if problems:
        raise RuntimeError("Still failing after regeneration: " + "; ".join(problems))
    db.log(rec["batch_id"], rec["id"], "heal", "lock", "Self-healed: regenerated from source data, re-signed, verified")
    return rec, data, True


def alternate_email(rec: dict, cfg: dict) -> tuple[str, str]:
    row = db.record_data(rec)
    for col in (cfg.get("email_column"), cfg.get("fallback_column")):
        if not col:
            continue
        raw = normalize_email(row.get(col, ""))
        cand = raw if valid_email(raw) else ""
        if not cand and cfg.get("auto_fix_emails", True):
            cand = fix_email_typo(raw, Counter())[0]
        if cand and cand.lower() != rec["email"].lower():
            return cand, col
    return "", ""


def _log_send(rec: dict, attachment: str, result: str, detail: str) -> None:
    with db.tx() as c:
        c.execute("INSERT INTO send_log (record_id, dedupe_key, email, attachment, result, detail, at) VALUES (?,?,?,?,?,?,?)",
                  (rec["id"], rec["dedupe_key"], rec["email"], attachment, result, detail, db.now()))


def send(batch_id: int, record_ids: list[int] | None = None, allow_resend: bool = False) -> None:
    batch = db.get_batch(batch_id)
    cfg = batch["config"]
    chaos = batch["chaos"] or {}
    statuses = ["Pending", "Generated", "Failed"] + (["Sent", "Skipped", "Claim", "Claimed"] if allow_resend else [])
    sql = f"SELECT * FROM records WHERE batch_id=? AND status IN ({','.join('?' * len(statuses))})"
    params: list = [batch_id, *statuses]
    if record_ids is not None:
        sql += f" AND id IN ({','.join('?' * len(record_ids))})"
        params += record_ids
    targets = db.query(sql + " ORDER BY row_no", params)

    missing = [r for r in targets if not r["cert_file"] or not (config.CERT_DIR / r["cert_file"]).exists()]
    if missing:
        ok, failed = _generate_records(missing, cfg)
        db.log(batch_id, None, "ok", "generate", f"Generated and signed {ok} certificates before sending")
    if missing or not db.get_batch(batch_id)["seal"]:
        seal_batch(batch_id)
    db.log(batch_id, None, "info", "send", f"Delivery started for {len(targets)} records"
           + (" (sandbox, chaos faults armed)" if chaos else ""))

    reseal = False
    sent = failed = skipped = claim = 0
    with mailer.Sender(mode="sandbox" if batch["is_chaos"] else None, faults=chaos.get("faults")) as sender:
        for rec in targets:
            rec = db.get_record(rec["id"])
            if rec["status"] == "Failed" and rec["last_error"].startswith("Generation failed"):
                try:
                    rec = regenerate(rec, cfg)
                    reseal = True
                except Exception as e:
                    db.update_record(rec["id"], last_error=f"Generation failed: {e}")
                    failed += 1
                    continue
            if not allow_resend:
                prev = db.one("SELECT at, email FROM send_log WHERE dedupe_key=? AND result='sent' LIMIT 1",
                              (rec["dedupe_key"],))
                if prev:
                    db.update_record(rec["id"], status="Skipped",
                                     last_error=f"Already sent to {prev['email']} on {prev['at'][:10]}")
                    db.log(batch_id, rec["id"], "warn", "dedupe", f"Duplicate prevented: already sent to {prev['email']}")
                    skipped += 1
                    continue
            if rec["delivery"] == "claim":
                db.update_record(rec["id"], status="Claim", last_error="")
                db.log(batch_id, rec["id"], "heal", "claim", "No usable email: claim link issued instead of failing")
                claim += 1
                continue
            try:
                rec, pdf, healed = verified_attachment(rec, cfg)
                reseal |= healed
            except Exception as e:
                db.update_record(rec["id"], status="Failed", last_error=str(e), attempts=rec["attempts"] + 1)
                db.log(batch_id, rec["id"], "error", "lock", str(e))
                _log_send(rec, rec["cert_file"], "failed", str(e))
                failed += 1
                continue

            result = _deliver(sender, rec, cfg, pdf)
            if result["rebound"]:
                reseal = True
            if result["ok"]:
                sent += 1
            else:
                failed += 1
            if config.SEND_DELAY_SECONDS:
                time.sleep(config.SEND_DELAY_SECONDS)

    if reseal:
        seal_batch(batch_id)
    db.log(batch_id, None, "ok" if not failed else "warn", "send",
           f"Delivery finished: {sent} sent, {claim} claim links, {skipped} duplicates skipped, {failed} failed")


def _deliver(sender: mailer.Sender, rec: dict, cfg: dict, pdf: bytes) -> dict:
    batch_id = rec["batch_id"]
    rebound, attempts = False, rec["attempts"]
    db.update_record(rec["id"], status="Sending")
    attempt = 0
    while attempt < config.MAX_SEND_ATTEMPTS:
        values = record_values(rec, cfg)
        subject, body = email_texts(rec, cfg, values)
        fname = Path(rec["cert_file"]).name
        msg = mailer.build_message(rec["email"], rec["name"], subject, body, pdf, fname, rec["cert_code"])
        attempt += 1
        attempts += 1
        try:
            detail = sender.send(msg, rec["email"], f"{rec['cert_code']}_{Path(fname).stem}")
            db.update_record(rec["id"], status="Sent", sent_at=db.now(), attempts=attempts, last_error="")
            _log_send(rec, fname, "sent", detail)
            db.log(batch_id, rec["id"], "ok", "send", f"Sent to {rec['email']} with {fname}"
                   + (f" (attempt {attempt})" if attempt > 1 else ""))
            return {"ok": True, "rebound": rebound}
        except mailer.PermanentFailure as e:
            _log_send(rec, fname, "failed", str(e))
            alt, col = alternate_email(rec, cfg) if not rebound else ("", "")
            if alt:
                db.log(batch_id, rec["id"], "heal", "bounce", f"{rec['email']} bounced ({e}); switching to {col}: {alt}")
                db.update_record(rec["id"], email=alt, email_source=col)
                rec = regenerate(db.get_record(rec["id"]), cfg)  # Mapping Lock is re-bound to the new address
                rec, pdf, _ = verified_attachment(rec, cfg)
                rebound, attempt = True, 0
                continue
            db.update_record(rec["id"], status="Failed", attempts=attempts,
                             last_error=f"{e}. Share the claim link instead.")
            db.log(batch_id, rec["id"], "error", "bounce", f"Permanent failure, no alternative address: {e}")
            return {"ok": False, "rebound": rebound}
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            db.log(batch_id, rec["id"], "warn", "retry", f"Attempt {attempt} failed ({last})"
                   + ("; retrying" if attempt < config.MAX_SEND_ATTEMPTS else ""))
            sender.close()
            if attempt < config.MAX_SEND_ATTEMPTS:
                time.sleep(min(config.RETRY_BASE_SECONDS * 2 ** (attempt - 1), 8))
            else:
                db.update_record(rec["id"], status="Failed", attempts=attempts, last_error=last)
                _log_send(rec, fname, "failed", last)
                return {"ok": False, "rebound": rebound}
    return {"ok": False, "rebound": rebound}


# ---------------------------------------------------------------- jobs
def run_job(batch_id: int, kind: str, fn, *args, **kwargs) -> bool:
    with _jobs_lock:
        if batch_id in _running:
            return False
        _running.add(batch_id)
    db.set_batch(batch_id, job=kind)

    def worker():
        try:
            fn(batch_id, *args, **kwargs)
        except Exception as e:
            db.log(batch_id, None, "error", kind, f"Job stopped unexpectedly: {type(e).__name__}: {e}")
        finally:
            db.set_batch(batch_id, job="")
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
        c.execute("DELETE FROM events WHERE batch_id=?", (batch_id,))
        c.execute("DELETE FROM records WHERE batch_id=?", (batch_id,))
        c.execute("DELETE FROM batches WHERE id=?", (batch_id,))


# ---------------------------------------------------------------- public verification of a file
def verify_file(data: bytes) -> dict:
    """What the public verifier says about an uploaded PDF."""
    meta = certificate.read_proof(data)
    if not meta["code"]:
        return {"status": "unknown", "title": "Not a SealSend certificate",
                "reasons": ["This PDF carries no SealSend certificate ID."], "record": None}
    rec = db.one("SELECT * FROM records WHERE cert_code=?", (meta["code"],))
    if not rec or not rec["payload_json"]:
        return {"status": "not_found", "title": "No such certificate",
                "reasons": [f"Certificate {meta['code']} was never issued by this issuer."], "record": None}
    proof = record_proof(rec)
    signed = proof["payload"]
    if certificate.sha256(data) != rec["pdf_sha256"]:
        return {"status": "modified", "title": "This file has been altered",
                "reasons": ["Its fingerprint does not match the signed original.",
                            f"The genuine certificate {rec['cert_code']} was issued to {signed.get('name', '?')}."],
                "record": rec, "proof": proof}
    if not proof["valid"]:
        return {"status": "invalid", "title": "Signature checks failed",
                "reasons": ["The issuer's records for this certificate fail verification."], "record": rec, "proof": proof}
    return {"status": "valid", "title": "Authentic certificate",
            "reasons": ["Byte-for-byte identical to the signed original."], "record": rec, "proof": proof}
