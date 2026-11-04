"""End-to-end tests for SealSend. Every promise is exercised against the real pipeline."""
import email
import importlib
import json
import smtplib
import time
from collections import Counter
from email import policy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SEALSEND_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ADMIN_PASSWORD", "test-pass")
    for var in ("SMTP_HOST", "RESEND_API_KEY", "ANTHROPIC_API_KEY", "SEALSEND_SIGNING_KEY", "PUBLIC_BASE_URL"):
        monkeypatch.delenv(var, raising=False)
    import sealsend.config as config
    importlib.reload(config)
    monkeypatch.setattr(config, "RETRY_BASE_SECONDS", 0.01)
    from sealsend import crypto, db, settings
    crypto.reset_keys()
    db.reset_connection()
    settings.reset_cache()
    import sealsend.main as main
    from fastapi.testclient import TestClient
    with TestClient(main.app) as c:
        yield c
    db.reset_connection()
    crypto.reset_keys()
    settings.reset_cache()


def login(c):
    assert c.post("/api/login", json={"password": "test-pass"}).status_code == 200


def upload(c, name="students.csv", event="AI Hackathon 2026"):
    with open(ROOT / "sample" / name, "rb") as f:
        r = c.post("/api/batches", files={"file": (name, f)}, data={"name": event})
    assert r.status_code == 200, r.text
    return r.json()


def wait_idle(c, bid, timeout=120):
    end = time.time() + timeout
    while time.time() < end:
        b = c.get(f"/api/batches/{bid}").json()
        if not b["job"]:
            return b
        time.sleep(0.1)
    raise AssertionError("job did not finish")


def records(c, bid, status=""):
    return c.get(f"/api/batches/{bid}/records", params={"status": status, "limit": 1000}).json()["records"]


def by_row(c, bid):
    return {r["row_no"]: r for r in records(c, bid)}


def send(c, bid):
    r = c.post(f"/api/batches/{bid}/send", json={"confirm": True})
    assert r.status_code == 200, r.text
    return wait_idle(c, bid)


def save(c, bid, cfg):
    r = c.put(f"/api/batches/{bid}/config", json=cfg)
    assert r.status_code == 200, r.text
    return r.json()


def outbox(tmp_path):
    return sorted((tmp_path / "outbox").glob("*.eml"))


def audit(bid):
    from sealsend import chaos
    return chaos.audit_deliveries(bid)


# ---------------------------------------------------------------- units
def test_merkle_and_signatures(client):
    from sealsend import crypto
    for n in range(1, 34):
        leaves = [crypto.leaf_hash(f"SS-{i}", "a" * 64, "lock") for i in range(n)]
        root = crypto.merkle_root(leaves)
        for i in range(n):
            assert crypto.verify_proof(leaves[i], crypto.merkle_proof(leaves, i), root)
    sig = crypto.sign(b"payload")
    assert crypto.verify(b"payload", sig) and not crypto.verify(b"payl0ad", sig) and not crypto.verify(b"payload", "xx")


def test_email_self_healing_rules():
    from sealsend.data import fix_email_typo, normalize_email, pick_email
    sheet = Counter({"college.example.edu": 9})
    for raw, want in {"a@gmial.com": "a@gmail.com", "a@gmail.co": "a@gmail.com", "a@hotmial.com": "a@hotmail.com",
                      "a@colege.example.edu": "a@college.example.edu", "a@college.example.con": "a@college.example.edu"}.items():
        assert fix_email_typo(normalize_email(raw), sheet)[0] == want, raw
    for untouched in ("a@gmx.com", "a@lime.com", "a@ucla.edu", "a@college.example.edu", "a@gmail.com"):
        assert fix_email_typo(untouched, sheet)[0] == "", untouched
    assert normalize_email(" Mailto:<Omar(at)College.Example.EDU>. ") == "Omar@college.example.edu"
    assert pick_email("bad@", "real@example.com", "P", "F", True, sheet)["email"] == "real@example.com"
    assert pick_email("me@gmial.com", "", "P", "F", True, sheet)["email"] == "me@gmail.com"
    assert pick_email("a@x.com; b@y.com", "", "P", "F", True, sheet)["email"] == "a@x.com"


def test_names_and_wording():
    from sealsend.data import check_name, classify, honor_phrase, smart_title
    for bad in ["#REF!", "N/A", "J0hn Smith", "", "a", "x@y.com", "John_Smith", "Total"]:
        assert check_name(bad)[0], bad
    for good in ["José Martínez", "Mary-Jane O'Neil", "Lakshmi Venkataraman-Subramanian"]:
        assert check_name(good) == ([], []), good
    assert smart_title("ROHAN AL-MEHTA") == "Rohan Al-Mehta" and smart_title("McDonald") == "McDonald"
    assert honor_phrase("Winner") == "being the Winner" and honor_phrase("First Place") == "securing First Place"
    assert [classify(v) for v in ("Winner", "Runner Up", "Volunteer", "Participant", "Intern", "Coordinator")] == \
        ["winner", "winner", "appreciation", "participation", "completion", "appreciation"]


def test_text_rendering_defaults_and_optional_segments():
    from sealsend.templates_lib import render_text, required_tokens
    v = {"NAME": "A", "EVENT": "Fest", "DATE": ""}
    assert render_text("for {{EVENT}}[[, held on {{DATE}}]]", v) == "for Fest"
    assert render_text("for {{EVENT}}[[, held on {{DATE}}]]", {**v, "DATE": "1 May"}) == "for Fest, held on 1 May"
    assert render_text("{{TITLE|Certificate of Merit}}", v) == "Certificate of Merit"
    assert required_tokens("{{NAME}} {{TITLE|x}} [[{{DATE}}]]") == ["NAME"]


def test_all_builtin_templates_render_deterministically_with_proof(client):
    from sealsend import certificate, templates_lib as T
    v = dict(T.SAMPLE_VALUES, NAME="Анна Иванова")  # Cyrillic falls back to a font that has the glyphs
    for t in T.BUILTINS:
        a = certificate.render_pdf(t["id"], v, "SS-1", "lock1")
        assert a == certificate.render_pdf(t["id"], v, "SS-1", "lock1"), t["id"]
        assert certificate.read_proof(a) == {"code": "SS-1", "lock": "lock1"}
        assert certificate.pdf_to_png(a, 30)[:4] == b"\x89PNG"


def test_messy_excel_is_understood(client):
    from sealsend.data import read_table, suggest_config
    t = read_table(ROOT / "sample" / "tech_fest_2026.xlsx")
    assert t["sheet"] == "Participants" and t["header_row"] == 3 and len(t["rows"]) == 16  # footer row skipped
    cfg = suggest_config(t["columns"], t["rows"])
    assert cfg["mapping"]["NAME"] == {"type": "combine", "value": ["First Name", "Last Name"]}
    assert (cfg["email_column"], cfg["fallback_column"], cfg["category_column"]) == ("College Email ID", "Personal Mail", "Award Category")
    assert cfg["mapping"]["DATE"]["value"] == "Event Date" and "EVENT" not in cfg["mapping"]


# ---------------------------------------------------------------- auth + setup
def test_auth_and_public_pages(client):
    assert client.get("/api/batches").status_code == 401
    assert client.post("/api/login", json={"password": "nope"}).status_code == 401
    assert client.get("/verify").status_code == 200
    assert "BEGIN PUBLIC KEY" in client.get("/.well-known/sealsend-public-key.pem").text
    assert "Not verified" in client.get("/verify/SS-FAKE000000").text
    assert client.get("/manifest.webmanifest").json()["display"] == "standalone"


def test_first_run_setup_is_local_only(client, monkeypatch):
    from sealsend import config, main, settings
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "")
    settings.reset_cache()
    assert client.get("/api/setup-status").json()["needs_setup"]
    assert client.post("/api/setup", json={"password": "short"}).status_code == 400
    assert client.post("/api/setup", json={"password": "long-enough-pw"}).status_code == 200
    assert client.post("/api/setup", json={"password": "another-password"}).status_code == 400  # only once
    assert client.post("/api/login", json={"password": "long-enough-pw"}).status_code == 200
    assert "long-enough-pw" not in config.SETTINGS_PATH.read_text()
    req = lambda host, headers: type("R", (), {"client": type("C", (), {"host": host})(), "headers": headers})()  # noqa: E731
    assert not main._is_local(req("192.168.1.50", {}))
    assert main._is_local(req("127.0.0.1", {}))
    assert not main._is_local(req("127.0.0.1", {"cf-connecting-ip": "203.0.113.9"}))  # came through the public tunnel
    assert not main._is_local(req("127.0.0.1", {"x-forwarded-for": "203.0.113.9"}))


# ---------------------------------------------------------------- workflow
def test_upload_validation_and_categories(client):
    login(client)
    b = upload(client, "tech_fest_2026.xlsx", "National Tech Fest 2026")
    cfg = b["config"]
    assert cfg["template_id"] == "tech-hackathon" and cfg["mapping"]["EVENT"] == {"type": "text", "value": "National Tech Fest 2026"}
    assert [r["label"] for r in cfg["rules"]] == ["Winner", "Runner Up", "Best Paper Award", "Volunteer", "Coordinator", "Participant"]
    assert [r["template"] for r in cfg["rules"]][:3] == ["gold-excellence"] * 3
    r = by_row(client, b["id"])
    assert r[9]["email"] == "omar.h@example.com" and r[10]["email"] == "sara.kim@gmail.com"
    assert r[11]["delivery"] == "claim" and r[16]["status"] == "Invalid" and "Duplicate of row 5" in r[17]["errors"]
    assert b["counts"] == {"Invalid": 2, "Pending": 14, "Total": 16}
    pv = client.get(f"/api/batches/{b['id']}/preview/email", params={"record_id": r[4]["id"]}).json()
    assert pv["title"] == "Certificate of Excellence" and "being the Winner" in pv["body"]
    vol = client.get(f"/api/batches/{b['id']}/preview/email", params={"record_id": r[12]["id"]}).json()
    assert vol["title"] == "Certificate of Appreciation" and vol["subject"].startswith("Thank you for your contribution")
    cfg["fix_caps"] = True
    save(client, b["id"], cfg)
    assert by_row(client, b["id"])[5]["name"] == "Rohan Mehta"
    sw = client.post(f"/api/batches/{b['id']}/sheet", json={"sheet": "Instructions"})
    assert sw.status_code == 200 and sw.json()["counts"]["Total"] == 0 or sw.status_code == 400


def test_full_flow_lock_signatures_seal_dedupe(client, tmp_path):
    login(client)
    b = upload(client)
    bid = b["id"]
    assert client.post(f"/api/batches/{bid}/send", json={"confirm": False}).status_code == 400
    done = send(client, bid)
    assert done["counts"] == {"Invalid": 2, "Sent": 11, "Claim": 2, "Total": 15} and done["sealed"]
    assert audit(bid) == {"emails_checked": 11, "wrong": 0, "wrong_files": []}
    seal = client.post(f"/api/batches/{bid}/verify-seal").json()
    assert seal["intact"] and seal["count"] == 13
    sent = records(client, bid, "Sent")
    detail = client.get(f"/api/records/{sent[0]['id']}").json()
    assert detail["proof"]["valid"] and detail["proof"]["lock_check"] == []
    page = client.get(f"/verify/{sent[0]['cert_code']}").text
    assert "Verified" in page and sent[0]["name"] in page
    pdf = client.get(f"/api/records/{sent[0]['id']}/certificate").content
    assert "Authentic certificate" in client.post("/verify", files={"file": ("c.pdf", pdf)}).text
    from sealsend import certificate
    assert "This file has been altered" in client.post("/verify", files={"file": ("f.pdf", certificate.forge_copy(pdf, "Mallory"))}).text
    n = len(outbox(tmp_path))
    send(client, bid)
    assert len(outbox(tmp_path)) == n
    b2 = upload(client)
    send(client, b2["id"])
    assert len(records(client, b2["id"], "Skipped")) == 11 and len(outbox(tmp_path)) == n
    assert client.post(f"/api/records/{sent[0]['id']}/resend").status_code == 200
    wait_idle(client, bid)
    assert len(outbox(tmp_path)) == n + 1
    csv_text = client.get(f"/api/batches/{bid}/report.csv").content.decode("utf-8")
    assert csv_text.startswith("﻿") and "Missing name" in csv_text and "José Martínez" in csv_text
    z = client.get(f"/api/batches/{bid}/certificates.zip")
    assert z.status_code == 200 and b"SEAL.json" in z.content


def test_claim_links(client):
    login(client)
    bid = upload(client)["id"]
    send(client, bid)
    claim = by_row(client, bid)[12]
    assert claim["status"] == "Claim"
    token = client.get(f"/api/records/{claim['id']}").json()["claim_url"].rsplit("/", 1)[1]
    assert "Your certificate" in client.get(f"/claim/{token}").text
    assert "doesn’t match" in client.post(f"/claim/{token}", data={"student_id": "WRONG"}).text
    assert client.post(f"/claim/{token}", data={"student_id": "stu011"}).headers["content-type"] == "application/pdf"
    assert by_row(client, bid)[12]["status"] == "Claimed"
    for _ in range(5):
        client.post(f"/claim/{token}", data={"student_id": "nope"})
    assert "Link locked" in client.post(f"/claim/{token}", data={"student_id": "stu011"}).text


def test_swapped_files_blocked_and_healed(client, tmp_path):
    login(client)
    bid = upload(client)["id"]
    client.post(f"/api/batches/{bid}/generate")
    wait_idle(client, bid)
    a, z = [r for r in records(client, bid, "Generated") if r["email"]][:2]
    pa, pz = tmp_path / "certificates" / a["cert_file"], tmp_path / "certificates" / z["cert_file"]
    da, dz = pa.read_bytes(), pz.read_bytes()
    pa.write_bytes(dz)
    pz.write_bytes(da)
    assert not client.post(f"/api/batches/{bid}/verify-seal").json()["intact"]
    send(client, bid)
    for rid in (a["id"], z["id"]):
        ev = client.get(f"/api/records/{rid}").json()["events"]
        assert any(e["level"] == "block" for e in ev) and any(e["level"] == "heal" for e in ev)
    assert audit(bid)["wrong"] == 0 and client.post(f"/api/batches/{bid}/verify-seal").json()["intact"]


def test_database_tampering_breaks_verification(client):
    login(client)
    bid = upload(client)["id"]
    send(client, bid)
    rec = records(client, bid, "Sent")[0]
    from sealsend import db
    payload = json.loads(db.get_record(rec["id"])["payload_json"])
    payload["name"] = "Someone Else"
    db.update_record(rec["id"], payload_json=json.dumps(payload))
    assert "Verification failed" in client.get(f"/verify/{rec['cert_code']}").text
    assert not client.post(f"/api/batches/{bid}/verify-seal").json()["intact"]


# ---------------------------------------------------------------- templates
def test_template_gallery_import_and_editor(client, tmp_path):
    login(client)
    cat = client.get("/api/templates").json()
    assert len([t for t in cat if not t["custom"]]) == 14
    assert client.get("/api/templates/gold-excellence/thumb.png").content[:4] == b"\x89PNG"
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("RGBA", (2000, 1414), (240, 230, 210, 255)).save(buf, "PNG")
    t = client.post("/api/templates/import", files={"file": ("canva.png", buf.getvalue())}, data={"name": "Canva Gala"}).json()
    assert t["custom"] and t["fields"][0]["key"] == "name"
    fields = t["fields"]
    fields[0]["x"], fields[0]["y"], fields[0]["font"] = 0.4, 0.55, "script"
    assert client.put(f"/api/templates/{t['id']}", json={"fields": fields, "name": "Gala"}).status_code == 200
    assert client.get(f"/api/templates/{t['id']}").json()["fields"][0]["x"] == 0.4
    from sealsend import templates_lib as T
    pdf_bg = T.render(dict(T.BUILTIN_BY_ID["arts-ornate"], fields=[]), {}, {}, {})
    t2 = client.post("/api/templates/import", files={"file": ("canva.pdf", pdf_bg)}, data={"name": "PDF"}).json()
    b = upload(client)
    cfg = b["config"]
    cfg["template_id"] = t2["id"]
    save(client, b["id"], cfg)
    assert client.delete(f"/api/templates/{t2['id']}").status_code == 400  # still in use
    done = send(client, b["id"])
    assert done["counts"]["Sent"] == 11 and audit(b["id"])["wrong"] == 0
    assert client.post("/api/templates/import", files={"file": ("x.txt", b"hi")}).status_code == 400
    assert client.delete("/api/templates/gold-excellence").status_code == 400


def test_branding_appears_on_certificates(client):
    login(client)
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("RGBA", (400, 200), (0, 0, 0, 255)).save(buf, "PNG")
    logo = client.post("/api/branding/upload", files={"file": ("logo.png", buf.getvalue())}, data={"kind": "logo"}).json()["file"]
    b = upload(client)
    cfg = b["config"]
    cfg["branding"].update({"org_name": "ABC College", "logo": logo, "signer1_name": "Dr. Priya Sharma"})
    save(client, b["id"], cfg)
    r = records(client, b["id"])[0]
    assert client.get(f"/api/records/{r['id']}").json()["values"]["ORG_NAME"] == "ABC College"
    png = client.get(f"/api/batches/{b['id']}/preview/certificate", params={"record_id": r["id"]})
    assert png.headers["content-type"] == "image/png"


# ---------------------------------------------------------------- delivery
def test_settings_mail_encrypted_and_validated(client):
    login(client)
    assert client.put("/api/settings/mail", json={"provider": "gmail", "address": "me@gmail.com", "password": "short"}).status_code == 400
    assert client.put("/api/settings/mail", json={"provider": "gmail", "address": "nope", "password": ""}).status_code == 400
    r = client.put("/api/settings/mail", json={"provider": "gmail", "address": "me@gmail.com", "password": "abcd efgh ijkl mnop"})
    assert r.status_code == 200 and r.json()["mode"] == "smtp"
    from sealsend import config, settings
    assert "abcd" not in config.SETTINGS_PATH.read_text() and settings.mail()["password"] == "abcdefghijklmnop"
    s = client.get("/api/settings").json()
    assert s["mail"]["has_password"] and "password" not in s["mail"]


def _fake_smtp(monkeypatch, behaviour):
    from sealsend import mailer
    log = {"sent": [], "connects": []}

    class FakeSMTP:
        def __init__(self, host, port, timeout=20, context=None):
            log["connects"].append((host, port))
            behaviour.get("connect", lambda h, p: None)(host, port)
        def ehlo(self): pass
        def starttls(self, context=None): pass
        def login(self, u, p): behaviour.get("login", lambda u, p: None)(u, p)
        def send_message(self, msg):
            behaviour.get("send", lambda m: None)(msg)
            log["sent"].append(msg)
        def quit(self): pass

    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(mailer.smtplib, "SMTP_SSL", FakeSMTP)
    return log


def _gmail(client, cap=450):
    assert client.put("/api/settings/mail", json={"provider": "gmail", "address": "me@gmail.com", "password": "abcdefghijklmnop",
                                                  "daily_cap": cap, "delay_seconds": 0}).status_code == 200


def test_gmail_bounce_rebinds_and_connection_reused(client, monkeypatch):
    def send_(msg):
        if "<rohan.mehta@college.example.edu>" in msg["To"]:
            raise smtplib.SMTPRecipientsRefused({"rohan.mehta@college.example.edu": (550, b"no such user")})
    log = _fake_smtp(monkeypatch, {"send": send_})
    login(client)
    _gmail(client)
    bid = upload(client)["id"]
    send(client, bid)
    assert len(log["sent"]) == 11 and log["connects"].count(("smtp.gmail.com", 587)) == 2  # preflight + batch
    rohan = by_row(client, bid)[3]
    assert rohan["status"] == "Sent" and rohan["email"] == "rohan.m@example.com"
    from sealsend import certificate, db
    att = next(m for m in log["sent"] if "rohan.m@example.com" in m["To"])
    assert certificate.read_proof(next(att.iter_attachments()).get_content())["lock"] == db.get_record(rohan["id"])["mapping_lock"]
    assert att["From"].endswith("<me@gmail.com>")


def test_wrong_gmail_password_never_starts_or_fails_students(client, monkeypatch):
    def bad_login(u, p):
        raise smtplib.SMTPAuthenticationError(535, b"5.7.8 Username and Password not accepted")
    _fake_smtp(monkeypatch, {"login": bad_login})
    login(client)
    _gmail(client)
    bid = upload(client)["id"]
    r = client.post(f"/api/batches/{bid}/send", json={"confirm": True})
    assert r.status_code == 400 and "App Password" in r.json()["detail"]
    assert not records(client, bid, "Failed") and not records(client, bid, "Sent")
    assert not client.post("/api/settings/test-connection").json()["ok"]


def test_port_587_blocked_falls_back_to_465(client, monkeypatch):
    def connect(host, port):
        if port == 587:
            raise OSError("Connection refused")
    log = _fake_smtp(monkeypatch, {"connect": connect})
    login(client)
    _gmail(client)
    assert client.post("/api/settings/test-connection").json()["ok"]
    assert ("smtp.gmail.com", 465) in log["connects"]


def test_daily_cap_pauses_and_resumes_without_loss(client, monkeypatch):
    log = _fake_smtp(monkeypatch, {})
    login(client)
    _gmail(client, cap=5)
    bid = upload(client)["id"]
    done = send(client, bid)
    assert len(log["sent"]) == 5 and "Daily sending limit" in done["pause_reason"]
    assert done["counts"].get("Failed", 0) == 0
    from sealsend import db

    def next_day():
        with db.tx() as c:
            c.execute("UPDATE send_log SET at='2000-01-01T00:00:00Z'")
    next_day()
    done = send(client, bid)  # 11 deliverable students, 5 per day: 5, 5, then 1
    assert done["counts"]["Sent"] == 10 and "Daily sending limit" in done["pause_reason"]
    next_day()
    done = send(client, bid)
    assert done["counts"]["Sent"] == 11 and done["pause_reason"] == ""
    assert len(log["sent"]) == 11 and len({m["To"] for m in log["sent"]}) == 11  # nobody emailed twice


def test_provider_quota_error_pauses(client, monkeypatch):
    calls = {"n": 0}

    def send_(msg):
        calls["n"] += 1
        if calls["n"] > 3:
            raise smtplib.SMTPDataError(550, b"5.4.5 Daily user sending quota exceeded.")
    _fake_smtp(monkeypatch, {"send": send_})
    login(client)
    _gmail(client)
    bid = upload(client)["id"]
    done = send(client, bid)
    assert done["counts"]["Sent"] == 3 and "limit" in done["pause_reason"].lower() and not done["counts"].get("Failed")


def test_transient_failure_isolated_then_retried(client, monkeypatch):
    login(client)
    bid = upload(client)["id"]
    from sealsend import config, mailer
    monkeypatch.setattr(config, "MAX_SEND_ATTEMPTS", 2)
    real = mailer.Sender.send

    def flaky(self, msg, to_addr, name):
        if "rohan" in to_addr:
            raise mailer.TransientFailure("421 busy")
        return real(self, msg, to_addr, name)

    monkeypatch.setattr(mailer.Sender, "send", flaky)
    done = send(client, bid)
    assert done["counts"]["Sent"] == 10 and done["counts"]["Failed"] == 1
    monkeypatch.setattr(mailer.Sender, "send", real)
    assert client.post(f"/api/batches/{bid}/retry").json()["started"]
    assert wait_idle(client, bid)["counts"]["Sent"] == 11


def test_resend_api_request_shape(client, monkeypatch):
    from sealsend import config, mailer
    captured = {}

    class Resp:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return b'{"id":"re_123"}'

    def fake_urlopen(req, timeout=30):
        captured["body"], captured["auth"] = json.loads(req.data), req.headers["Authorization"]
        return Resp()

    monkeypatch.setattr(config, "RESEND_API_KEY", "re_key")
    monkeypatch.setattr(mailer.urllib.request, "urlopen", fake_urlopen)
    msg = mailer.build_message("a@b.co", "A", "Hi", "Body", b"%PDF", "x.pdf", "SS-1")
    assert mailer.Sender(mode="resend").send(msg, "a@b.co", "n").endswith("re_123")
    assert captured["auth"] == "Bearer re_key" and captured["body"]["attachments"][0]["filename"] == "x.pdf"


# ---------------------------------------------------------------- copilot + chaos + scale
def test_copilot_offline_and_claude(client, monkeypatch):
    login(client)
    b = upload(client)
    prop = client.post(f"/api/batches/{b['id']}/copilot", json={"text": "winners get gold template, others participation"}).json()
    assert prop["engine"] == "offline" and [r["template"] for r in prop["rules"]] == ["gold-excellence", "participation-clean"]
    import anthropic
    from sealsend import copilot

    class Block:
        type = "text"
        text = json.dumps({"rules": [{"label": "Winners", "match": {"column": "Achievement", "op": "any_of", "values": ["First Place"]},
                                      "theme": "gold-excellence", "email": "winner", "email_subject": "", "email_body": ""}], "notes": []})

    class Fake:
        def __init__(self, **kw):
            self.beta = self
            self.messages = self
        def create(self, **kw):
            return type("R", (), {"stop_reason": "end_turn", "content": [Block()]})()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(anthropic, "Anthropic", Fake)
    rows = [{"Achievement": "First Place"}, {"Achievement": "Participation"}]
    out = copilot.suggest("first place gets gold", ["Achievement"], rows, {})
    assert out["engine"].startswith("Claude") and out["counts"] == [1] and out["rules"][0]["style"] == "winner"
    monkeypatch.setattr(Fake, "create", lambda self, **kw: (_ for _ in ()).throw(anthropic.APIConnectionError(request=None)))
    out = copilot.suggest("first place gets gold", ["Achievement"], rows, {})
    assert out["engine"] == "offline" and "Claude unavailable" in out["notes"][0]


def test_chaos_test_contains_every_fault(client):
    login(client)
    bid = client.post("/api/chaos").json()["batch_id"]
    wait_idle(client, bid, timeout=150)
    rep = client.get(f"/api/batches/{bid}").json()["chaos"]["report"]
    assert not [i for i in rep["items"] if not i["passed"]], rep["items"]
    assert rep["passed"] == rep["total"] == 15 and rep["wrong_attachments_delivered"] == 0 and rep["batch_finished"]


def test_bulk_parallel_generation(client, tmp_path):
    import csv
    login(client)
    p = tmp_path / "big.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Student Name", "Student ID", "Student Email", "Event", "Category"])
        for i in range(120):
            w.writerow([f"Student {chr(65 + i % 26)}{chr(97 + i // 26)}", f"B{i:04d}", f"s{i}@example.edu", "Bulk Fest",
                        "Winner" if i < 3 else "Participant"])
    with open(p, "rb") as f:
        bid = client.post("/api/batches", files={"file": ("big.csv", f)}, data={"name": "Bulk"}).json()["id"]
    done = send(client, bid)
    assert done["counts"] == {"Sent": 120, "Total": 120}
    assert audit(bid) == {"emails_checked": 120, "wrong": 0, "wrong_files": []}
    assert client.post(f"/api/batches/{bid}/verify-seal").json()["intact"]
