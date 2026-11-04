"""End-to-end tests for SealSend: every promise in the pitch is exercised against the real pipeline."""
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
    for var in ("SMTP_HOST", "RESEND_API_KEY", "ANTHROPIC_API_KEY", "SEALSEND_SIGNING_KEY"):
        monkeypatch.delenv(var, raising=False)
    import sealsend.config as config
    importlib.reload(config)
    monkeypatch.setattr(config, "RETRY_BASE_SECONDS", 0.01)
    from sealsend import crypto, db
    crypto.reset_keys()
    db.reset_connection()
    import sealsend.main as main
    monkeypatch.setattr(main.config, "ADMIN_PASSWORD", "test-pass")
    from fastapi.testclient import TestClient
    with TestClient(main.app) as c:
        yield c
    db.reset_connection()
    crypto.reset_keys()


def login(c):
    assert c.post("/api/login", json={"username": "admin", "password": "test-pass"}).status_code == 200


def upload_sample(c, name="AI Hackathon 2026"):
    with open(ROOT / "sample" / "students.csv", "rb") as f:
        r = c.post("/api/batches", files={"file": ("students.csv", f, "text/csv")}, data={"name": name})
    assert r.status_code == 200, r.text
    return r.json()


def wait_idle(c, bid, timeout=90):
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
    assert c.post(f"/api/batches/{bid}/send", json={"confirm": True}).status_code == 200
    return wait_idle(c, bid)


def outbox(tmp_path):
    return sorted((tmp_path / "outbox").glob("*.eml"))


# ---------------------------------------------------------------- unit level
def test_merkle_and_signatures(client):
    from sealsend import crypto
    for n in range(1, 34):
        leaves = [crypto.leaf_hash(f"SS-{i}", "a" * 64, "lock") for i in range(n)]
        root = crypto.merkle_root(leaves)
        for i in range(n):
            assert crypto.verify_proof(leaves[i], crypto.merkle_proof(leaves, i), root)
        assert not crypto.verify_proof(crypto.leaf_hash("SS-X", "a" * 64, "lock"), crypto.merkle_proof(leaves, 0), root)
    sig = crypto.sign(b"payload")
    assert crypto.verify(b"payload", sig) and not crypto.verify(b"payl0ad", sig) and not crypto.verify(b"payload", "xx")
    assert crypto.mapping_lock("S1", "a@b.co", "Ev", "SS-1") != crypto.mapping_lock("S1", "c@b.co", "Ev", "SS-1")


def test_email_self_healing_rules():
    from sealsend.data import fix_email_typo, normalize_email, pick_email
    sheet = Counter({"college.example.edu": 9})
    cases = {"a@gmial.com": "a@gmail.com", "a@gmail.co": "a@gmail.com", "a@hotmial.com": "a@hotmail.com",
             "a@colege.example.edu": "a@college.example.edu", "a@college.example.con": "a@college.example.edu",
             "a@yahooo.com": "a@yahoo.com"}
    for raw, want in cases.items():
        assert fix_email_typo(normalize_email(raw), sheet)[0] == want, raw
    for untouched in ("a@gmx.com", "a@lime.com", "a@ucla.edu", "a@college.example.edu", "a@gmail.com"):
        assert fix_email_typo(untouched, sheet)[0] == "", untouched
    assert normalize_email(" Mailto:<Omar(at)College.Example.EDU>. ") == "Omar@college.example.edu"
    # real fallback beats a guessed fix of a broken primary; a misspelled primary is still fixed
    assert pick_email("bad@", "real@example.com", "P", "F", True, sheet)["email"] == "real@example.com"
    assert pick_email("me@gmial.com", "", "P", "F", True, sheet)["email"] == "me@gmail.com"
    assert pick_email("me@gmial.com", "", "P", "F", False, sheet)["email"] == "me@gmial.com"


def test_name_checks():
    from sealsend.data import check_name
    for bad in ["#REF!", "N/A", "J0hn Smith", "", "a", "x@y.com", "John_Smith", "null"]:
        assert check_name(bad)[0], bad
    for good in ["José Martínez", "Mary-Jane O'Neil", "Lakshmi Venkataraman-Subramanian", "Fatima Al-Sayed"]:
        assert check_name(good) == ([], []), good
    assert check_name("AISHA RAHMAN")[1]


def test_rendering_is_deterministic_and_carries_proof(client):
    from sealsend import certificate
    v = {"NAME": "A B", "EVENT": "E", "CERT_TYPE": "T", "ACHIEVEMENT": "X", "DATE": "D", "VERIFY_URL": "http://x/v"}
    for theme in certificate.THEMES:
        a = certificate.render_pdf(certificate.default_template(), v, "SS-1", "lock1", theme)
        assert a == certificate.render_pdf(certificate.default_template(), v, "SS-1", "lock1", theme)
        assert certificate.read_proof(a) == {"code": "SS-1", "lock": "lock1"}
    forged = certificate.forge_copy(a, "Mallory")
    assert certificate.read_proof(forged)["code"] == "SS-1" and certificate.sha256(forged) != certificate.sha256(a)


# ---------------------------------------------------------------- API + workflow
def test_requires_login_but_public_pages_are_open(client):
    assert client.get("/api/batches").status_code == 401
    assert client.post("/api/login", json={"username": "admin", "password": "nope"}).status_code == 401
    assert client.get("/verify").status_code == 200
    assert "BEGIN PUBLIC KEY" in client.get("/.well-known/sealsend-public-key.pem").text
    assert "Not verified" in client.get("/verify/SS-FAKE000000").text
    assert client.get("/claim/not-a-real-token-123").status_code == 404


def test_mapping_and_validation(client):
    login(client)
    b = upload_sample(client)
    cfg = b["config"]
    assert (cfg["email_column"], cfg["fallback_column"]) == ("Student Email", "Personal Email")
    assert cfg["mapping"]["NAME"]["value"] == "Student Name" and cfg["mapping"]["ID"]["value"] == "Student ID"
    r = by_row(client, b["id"])
    assert r[9]["email"] == "omar.h@example.com" and "fallback" in r[9]["warnings"]       # invalid primary
    assert r[10]["delivery"] == "claim" and r[10]["status"] == "Pending"                 # invalid, no fallback
    assert r[11]["status"] == "Invalid" and "Missing name" in r[11]["errors"]
    assert r[12]["delivery"] == "claim"                                                   # no email at all
    assert r[13]["status"] == "Invalid" and "Duplicate of row 3" in r[13]["errors"]
    assert b["counts"] == {"Invalid": 2, "Pending": 13, "Total": 15}

    # Turning claim links off makes missing/invalid emails hard errors (Rule 8)
    cfg["claim_links"] = False
    res = client.put(f"/api/batches/{b['id']}/config", json=cfg).json()
    assert res["counts"]["Invalid"] == 4
    r = by_row(client, b["id"])
    assert "Invalid email" in r[10]["errors"] and "Missing email" in r[12]["errors"]


def test_full_flow_mapping_lock_signatures_seal_and_dedupe(client, tmp_path):
    login(client)
    b = upload_sample(client)
    bid = b["id"]
    pv = client.get(f"/api/batches/{bid}/preview/email").json()
    assert "Aisha Rahman" in pv["subject"] and pv["attachment"] == "STU001_Aisha_Rahman_AI_Hackathon_2026.pdf"
    assert client.get(f"/api/batches/{bid}/preview/certificate").headers["content-type"] == "application/pdf"
    assert client.post(f"/api/batches/{bid}/send", json={"confirm": False}).status_code == 400

    done = send(client, bid)
    assert done["counts"] == {"Invalid": 2, "Sent": 11, "Claim": 2, "Total": 15}
    assert done["sealed"]

    # Open every delivered email: right person, right attachment, valid lock + hash
    from sealsend import chaos as chaos_mod
    audit = chaos_mod.audit_deliveries(bid)
    assert audit == {"emails_checked": 11, "wrong": 0, "wrong_files": []}

    # Seal verifies; every record has a valid signature + Merkle inclusion proof
    seal = client.post(f"/api/batches/{bid}/verify-seal").json()
    assert seal["intact"] and seal["count"] == 13
    sent = records(client, bid, "Sent")
    detail = client.get(f"/api/records/{sent[0]['id']}").json()
    assert detail["proof"]["valid"] and detail["proof"]["lock_check"] == []

    # Public verification: QR page and file upload
    code = sent[0]["cert_code"]
    page = client.get(f"/verify/{code}").text
    assert "Verified" in page and sent[0]["name"] in page
    pdf = client.get(f"/api/records/{sent[0]['id']}/certificate").content
    assert "Authentic certificate" in client.post("/verify", files={"file": ("c.pdf", pdf)}).text
    from sealsend import certificate
    forged = certificate.forge_copy(pdf, "Mallory Impostor")
    assert "This file has been altered" in client.post("/verify", files={"file": ("f.pdf", forged)}).text
    assert "Not a SealSend certificate" in client.post("/verify", files={"file": ("x.pdf", b"%PDF-1.4 junk")}).text

    # Duplicate prevention: second click, then a re-uploaded sheet
    n = len(outbox(tmp_path))
    send(client, bid)
    assert len(outbox(tmp_path)) == n
    b2 = upload_sample(client)
    assert any("Already sent" in r["warnings"] for r in records(client, b2["id"]))
    send(client, b2["id"])
    assert len(records(client, b2["id"], "Skipped")) == 11 and len(outbox(tmp_path)) == n

    # Authorized resend still works
    assert client.post(f"/api/records/{sent[0]['id']}/resend").status_code == 200
    wait_idle(client, bid)
    assert len(outbox(tmp_path)) == n + 1

    report = client.get(f"/api/batches/{bid}/report.csv").text
    assert "Mapping Lock" in report and "Missing name" in report
    z = client.get(f"/api/batches/{bid}/certificates.zip")
    assert z.status_code == 200 and b"SEAL.json" in z.content


def test_claim_links(client):
    login(client)
    bid = upload_sample(client)["id"]
    send(client, bid)
    claim = by_row(client, bid)[12]  # Daniel Okafor, no email
    assert claim["status"] == "Claim"
    url = client.get(f"/api/records/{claim['id']}").json()["claim_url"]
    token = url.rsplit("/", 1)[1]
    assert "Your certificate" in client.get(f"/claim/{token}").text
    assert "doesn’t match" in client.post(f"/claim/{token}", data={"student_id": "WRONG"}).text
    ok = client.post(f"/claim/{token}", data={"student_id": "stu011"})
    assert ok.headers["content-type"] == "application/pdf"
    assert by_row(client, bid)[12]["status"] == "Claimed"
    for _ in range(5):
        client.post(f"/claim/{token}", data={"student_id": "nope"})
    assert "Link locked" in client.post(f"/claim/{token}", data={"student_id": "stu011"}).text


def test_swapped_and_tampered_files_are_blocked_and_healed(client, tmp_path):
    login(client)
    bid = upload_sample(client)["id"]
    client.post(f"/api/batches/{bid}/generate")
    wait_idle(client, bid)
    gen = [r for r in records(client, bid, "Generated") if r["email"]]
    a, z = gen[0], gen[1]
    pa, pz = tmp_path / "certificates" / a["cert_file"], tmp_path / "certificates" / z["cert_file"]
    da, dz = pa.read_bytes(), pz.read_bytes()
    pa.write_bytes(dz)
    pz.write_bytes(da)
    assert not client.post(f"/api/batches/{bid}/verify-seal").json()["intact"]
    send(client, bid)
    for rid in (a["id"], z["id"]):
        d = client.get(f"/api/records/{rid}").json()
        assert d["status"] == "Sent"
        assert any(e["level"] == "block" for e in d["events"]) and any(e["level"] == "heal" for e in d["events"])
    from sealsend import chaos as chaos_mod
    assert chaos_mod.audit_deliveries(bid)["wrong"] == 0
    assert client.post(f"/api/batches/{bid}/verify-seal").json()["intact"]


def test_database_tampering_breaks_verification(client):
    login(client)
    bid = upload_sample(client)["id"]
    send(client, bid)
    rec = records(client, bid, "Sent")[0]
    from sealsend import db
    payload = json.loads(db.get_record(rec["id"])["payload_json"])
    payload["name"] = "Someone Else"
    db.update_record(rec["id"], payload_json=json.dumps(payload))
    assert "Verification failed" in client.get(f"/verify/{rec['cert_code']}").text
    res = client.post(f"/api/batches/{bid}/verify-seal").json()
    assert not res["intact"] and any("Signed record" in p["reason"] for p in res["problems"])


def test_transient_failure_isolated_then_retried(client, monkeypatch):
    login(client)
    bid = upload_sample(client)["id"]
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
    failed = records(client, bid, "Failed")[0]
    assert failed["attempts"] == 2 and "421 busy" in failed["last_error"]
    monkeypatch.setattr(mailer.Sender, "send", real)
    assert client.post(f"/api/batches/{bid}/retry").json()["started"]
    assert wait_idle(client, bid)["counts"]["Sent"] == 11


def test_smtp_reuses_connection_and_bounce_rebinds_to_fallback(client, monkeypatch):
    from sealsend import config, mailer
    sent, connections = [], []

    class FakeSMTP:
        def __init__(self, host, port, timeout=30):
            connections.append((host, port))
        def starttls(self, context=None): pass
        def login(self, u, p): assert (u, p) == ("user", "secret")
        def send_message(self, msg):
            if msg["To"].endswith("<rohan.mehta@college.example.edu>"):
                raise smtplib.SMTPRecipientsRefused({"rohan.mehta@college.example.edu": (550, b"no such user")})
            sent.append(msg)
        def quit(self): pass

    for k, v in {"SMTP_HOST": "smtp.test", "SMTP_USER": "user", "SMTP_PASSWORD": "secret"}.items():
        monkeypatch.setattr(config, k, v)
    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)
    login(client)
    bid = upload_sample(client)["id"]
    send(client, bid)
    assert len(sent) == 11 and connections == [("smtp.test", 587)]
    rohan = by_row(client, bid)[3]
    assert rohan["status"] == "Sent" and rohan["email"] == "rohan.m@example.com"
    att = next(m for m in sent if "rohan.m@example.com" in m["To"])
    from sealsend import certificate, db
    data = next(att.iter_attachments()).get_content()
    assert certificate.read_proof(data)["lock"] == db.get_record(rohan["id"])["mapping_lock"]


def test_resend_api_request_shape(client, monkeypatch):
    from sealsend import config, mailer
    captured = {}

    class Resp:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return b'{"id":"re_123"}'

    def fake_urlopen(req, timeout=30):
        captured["url"], captured["body"] = req.full_url, json.loads(req.data)
        captured["auth"] = req.headers["Authorization"]
        return Resp()

    monkeypatch.setattr(config, "RESEND_API_KEY", "re_key")
    monkeypatch.setattr(mailer.urllib.request, "urlopen", fake_urlopen)
    msg = mailer.build_message("a@b.co", "A", "Hi", "Body", b"%PDF", "x.pdf", "SS-1")
    out = mailer.Sender(mode="resend").send(msg, "a@b.co", "n")
    assert out.endswith("re_123") and captured["url"] == "https://api.resend.com/emails"
    assert captured["auth"] == "Bearer re_key" and captured["body"]["attachments"][0]["filename"] == "x.pdf"


def test_copilot_rules_drive_templates_and_emails(client):
    login(client)
    b = upload_sample(client)
    bid = b["id"]
    prop = client.post(f"/api/batches/{bid}/copilot", json={"text": "winners get gold template, others participation"}).json()
    assert prop["engine"] == "offline" and [r["theme"] for r in prop["rules"]] == ["gold", "participation"]
    assert prop["counts"] == [6, 9]
    cfg = b["config"]
    cfg["rules"] = prop["rules"] + [{"theme": "nope", "match": {"op": "always"}}]  # junk rule is dropped
    res = client.put(f"/api/batches/{bid}/config", json=cfg).json()
    assert len(res["rules"]) == 2
    r = by_row(client, bid)
    assert r[2]["theme"] == "gold" and r[5]["theme"] == "participation"
    win = client.get(f"/api/batches/{bid}/preview/email", params={"record_id": r[2]["id"]}).json()
    part = client.get(f"/api/batches/{bid}/preview/email", params={"record_id": r[5]["id"]}).json()
    assert win["subject"].startswith("🏆 Aisha Rahman") and part["subject"].startswith("Thank you for taking part")
    vague = client.post(f"/api/batches/{bid}/copilot", json={"text": "make it nice"}).json()
    assert vague["rules"] == [] and vague["notes"]


def test_copilot_uses_claude_when_configured_and_falls_back(client, monkeypatch):
    import anthropic
    from sealsend import copilot, config
    calls = {}

    class Block:
        type = "text"
        text = json.dumps({"rules": [{"label": "Winners", "match": {"column": "Achievement", "op": "any_of", "values": ["First Place"]},
                                      "theme": "gold", "email": "winner", "email_subject": "", "email_body": ""}], "notes": []})

    class Fake:
        def __init__(self, **kw):
            self.beta = self
            self.messages = self
        def create(self, **kw):
            calls.update(kw)
            return type("R", (), {"stop_reason": "end_turn", "content": [Block()]})()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(anthropic, "Anthropic", Fake)
    cols = ["Student Name", "Achievement"]
    rows = [{"Student Name": "A", "Achievement": "First Place"}, {"Student Name": "B", "Achievement": "Participation"}]
    out = copilot.suggest("first place gets gold", cols, rows, {})
    assert out["engine"].startswith("Claude") and out["counts"] == [1]
    assert calls["model"] == config.COPILOT_MODEL and calls["output_config"]["format"]["type"] == "json_schema"

    def boom(**kw):
        raise anthropic.APIConnectionError(request=None)
    monkeypatch.setattr(Fake, "create", lambda self, **kw: boom())
    out = copilot.suggest("first place gets gold", cols, rows, {})
    assert out["engine"] == "offline" and "Claude unavailable" in out["notes"][0] and out["rules"]


def test_chaos_test_contains_every_fault(client, tmp_path):
    login(client)
    bid = client.post("/api/chaos").json()["batch_id"]
    wait_idle(client, bid, timeout=120)
    b = client.get(f"/api/batches/{bid}").json()
    rep = b["chaos"]["report"]
    failed = [i for i in rep["items"] if not i["passed"]]
    assert not failed, failed
    assert rep["passed"] == rep["total"] == 15 and rep["wrong_attachments_delivered"] == 0
    assert rep["batch_finished"] and rep["audit"]["emails_checked"] == 11
    forged = client.get(f"/api/batches/{bid}/chaos/forged.pdf")
    assert "This file has been altered" in client.post("/verify", files={"file": ("f.pdf", forged.content)}).text


def test_xlsx_upload(client, tmp_path):
    import pandas as pd
    login(client)
    src = pd.read_csv(ROOT / "sample" / "students.csv", dtype=str, keep_default_na=False)
    xlsx = tmp_path / "s.xlsx"
    src.to_excel(xlsx, index=False)
    with open(xlsx, "rb") as f:
        r = client.post("/api/batches", files={"file": ("s.xlsx", f)}, data={"name": "X"})
    assert r.status_code == 200 and r.json()["counts"]["Total"] == 15


def test_bulk_generation_is_parallel_and_correct(client, tmp_path):
    import csv
    login(client)
    p = tmp_path / "big.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Student Name", "Student ID", "Student Email", "Event", "Certificate Type", "Achievement", "Date"])
        for i in range(120):
            w.writerow([f"Student {chr(65 + i % 26)}{chr(97 + i // 26)}", f"B{i:04d}", f"s{i}@example.edu", "Bulk Fest",
                        "Participation", "Participation", "04 November 2026"])
    with open(p, "rb") as f:
        bid = client.post("/api/batches", files={"file": ("big.csv", f)}, data={"name": "Bulk"}).json()["id"]
    done = send(client, bid)
    assert done["counts"] == {"Sent": 120, "Total": 120}
    from sealsend import chaos as chaos_mod
    assert chaos_mod.audit_deliveries(bid) == {"emails_checked": 120, "wrong": 0, "wrong_files": []}
    assert client.post(f"/api/batches/{bid}/verify-seal").json()["intact"]
