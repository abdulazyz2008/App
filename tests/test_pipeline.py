"""End-to-end tests of the core workflow: CSV -> validation -> certificates -> correctly mapped emails."""
import email
import importlib
import os
import time
from email import policy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("CERTIFY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ADMIN_PASSWORD", "test-pass")
    monkeypatch.setenv("SMTP_HOST", "")
    import certify.config, certify.db, certify.pipeline, certify.main
    for m in (certify.config, certify.db, certify.pipeline, certify.main):
        importlib.reload(m)
    certify.db.reset_connection()
    from fastapi.testclient import TestClient
    with TestClient(certify.main.app) as c:
        yield c


def login(c):
    assert c.post("/api/login", json={"username": "admin", "password": "test-pass"}).status_code == 200


def upload_sample(c):
    with open(ROOT / "sample" / "students.csv", "rb") as f:
        r = c.post("/api/batches", files={"file": ("students.csv", f, "text/csv")}, data={"name": "AI Hackathon 2026"})
    assert r.status_code == 200, r.text
    return r.json()


def wait_idle(c, bid, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        if not c.get(f"/api/batches/{bid}").json()["job"]:
            return
        time.sleep(0.2)
    raise AssertionError("job did not finish")


def records(c, bid, status=""):
    return c.get(f"/api/batches/{bid}/records", params={"status": status, "limit": 1000}).json()["records"]


def test_requires_login(client):
    assert client.get("/api/batches").status_code == 401
    assert client.post("/api/login", json={"username": "admin", "password": "wrong"}).status_code == 401


def test_mapping_suggestion_and_validation(client):
    login(client)
    b = upload_sample(client)
    cfg = b["config"]
    assert cfg["email_column"] == "Student Email"
    assert cfg["fallback_column"] == "Personal Email"
    assert cfg["mapping"]["NAME"]["value"] == "Student Name"
    assert cfg["mapping"]["ID"]["value"] == "Student ID"

    recs = {r["row_no"]: r for r in records(client, b["id"])}
    assert recs[9]["status"] == "Pending" and recs[9]["email"] == "omar.h@example.com"  # fallback used
    assert "fallback" in recs[9]["warnings"]
    assert recs[10]["status"] == "Invalid" and "Invalid email" in recs[10]["errors"]
    assert recs[11]["status"] == "Invalid" and "Missing name" in recs[11]["errors"]
    assert recs[12]["status"] == "Invalid" and "Missing email" in recs[12]["errors"]
    assert recs[13]["status"] == "Invalid" and "Duplicate of row 3" in recs[13]["errors"]
    counts = client.get(f"/api/batches/{b['id']}").json()["counts"]
    assert counts["Invalid"] == 4 and counts["Pending"] == 11


def test_full_flow_correct_mapping_and_duplicate_prevention(client, tmp_path):
    login(client)
    b = upload_sample(client)
    bid = b["id"]

    # Preview works before anything is generated
    assert client.get(f"/api/batches/{bid}/preview/certificate").headers["content-type"] == "application/pdf"
    pv = client.get(f"/api/batches/{bid}/preview/email").json()
    assert "Aisha Rahman" in pv["subject"] and pv["attachment"] == "STU001_Aisha_Rahman_AI_Hackathon_2026.pdf"

    assert client.post(f"/api/batches/{bid}/send", json={"confirm": False}).status_code == 400
    assert client.post(f"/api/batches/{bid}/send", json={"confirm": True}).status_code == 200
    wait_idle(client, bid)

    sent = records(client, bid, "Sent")
    assert len(sent) == 11
    assert not records(client, bid, "Failed")

    # Every outbox email goes to the right person with *their* certificate.
    from certify.certificate import pdf_subject
    by_code = {r["cert_code"]: r for r in sent}
    emls = list((tmp_path / "outbox").glob("*.eml"))
    assert len(emls) == 11
    for p in emls:
        msg = email.message_from_bytes(p.read_bytes(), policy=policy.default)
        rec = by_code[msg["X-Certificate-ID"]]
        assert rec["email"] in msg["To"]
        assert rec["name"] in msg.get_body(("plain",)).get_content()
        atts = list(msg.iter_attachments())
        assert len(atts) == 1
        assert rec["student_id"] in atts[0].get_filename()
        assert pdf_subject(atts[0].get_content()) == rec["cert_code"]

    # Sending again does nothing: everyone already has their certificate.
    client.post(f"/api/batches/{bid}/send", json={"confirm": True})
    wait_idle(client, bid)
    assert len(list((tmp_path / "outbox").glob("*.eml"))) == 11

    # Re-uploading the same sheet: duplicates across batches are skipped too.
    b2 = upload_sample(client)
    assert any("Already sent" in r["warnings"] for r in records(client, b2["id"]))
    client.post(f"/api/batches/{b2['id']}/send", json={"confirm": True})
    wait_idle(client, b2["id"])
    assert len(records(client, b2["id"], "Skipped")) == 11
    assert len(list((tmp_path / "outbox").glob("*.eml"))) == 11

    # Authorized resend of one record is allowed.
    rid = sent[0]["id"]
    assert client.post(f"/api/records/{rid}/resend").status_code == 200
    wait_idle(client, bid)
    assert len(list((tmp_path / "outbox").glob("*.eml"))) == 12

    report = client.get(f"/api/batches/{bid}/report.csv").text
    assert report.count("Sent") >= 11 and "Invalid email" in report

    # Public verification page
    assert "Valid certificate" in client.get(f"/verify/{sent[0]['cert_code']}").text
    assert "Not found" in client.get("/verify/CRT-NOPE").text


def test_failure_does_not_stop_batch_and_retry(client, monkeypatch):
    login(client)
    b = upload_sample(client)
    bid = b["id"]
    import certify.mailer as mailer
    import certify.config as config
    monkeypatch.setattr(config, "MAX_SEND_ATTEMPTS", 1)
    real_send = mailer.Sender.send

    def flaky(self, msg, name):
        if "rohan" in msg["To"]:
            raise ConnectionError("mailbox unavailable")
        return real_send(self, msg, name)

    monkeypatch.setattr(mailer.Sender, "send", flaky)
    client.post(f"/api/batches/{bid}/send", json={"confirm": True})
    wait_idle(client, bid)
    assert len(records(client, bid, "Sent")) == 10
    failed = records(client, bid, "Failed")
    assert len(failed) == 1 and "mailbox unavailable" in failed[0]["last_error"]

    monkeypatch.setattr(mailer.Sender, "send", real_send)
    assert client.post(f"/api/batches/{bid}/retry").json()["started"]
    wait_idle(client, bid)
    assert len(records(client, bid, "Sent")) == 11


def test_tampered_certificate_is_never_attached(client, tmp_path):
    login(client)
    b = upload_sample(client)
    bid = b["id"]
    client.post(f"/api/batches/{bid}/generate")
    wait_idle(client, bid)
    gen = records(client, bid, "Generated")
    a, z = gen[0], gen[1]
    # Swap two students' PDFs on disk: the integrity check must catch it.
    pa, pz = tmp_path / "certificates" / a["cert_file"], tmp_path / "certificates" / z["cert_file"]
    da, dz = pa.read_bytes(), pz.read_bytes()
    pa.write_bytes(dz); pz.write_bytes(da)
    client.post(f"/api/batches/{bid}/send", json={"confirm": True})
    wait_idle(client, bid)
    failed = {r["id"]: r for r in records(client, bid, "Failed")}
    assert a["id"] in failed and z["id"] in failed
    assert "Integrity check failed" in failed[a["id"]]["last_error"]


def test_xlsx_upload(client, tmp_path):
    import pandas as pd
    login(client)
    src = pd.read_csv(ROOT / "sample" / "students.csv", dtype=str, keep_default_na=False)
    xlsx = tmp_path / "s.xlsx"
    src.to_excel(xlsx, index=False)
    with open(xlsx, "rb") as f:
        r = client.post("/api/batches", files={"file": ("s.xlsx", f)}, data={"name": "X"})
    assert r.status_code == 200
    assert r.json()["counts"]["Total"] == 15


def test_smtp_mode_reuses_one_connection(client, monkeypatch):
    import certify.config as config
    import certify.mailer as mailer
    sent, connections = [], []

    class FakeSMTP:
        def __init__(self, host, port, timeout=30):
            connections.append((host, port))
        def starttls(self, context=None): pass
        def login(self, u, p): assert (u, p) == ("user", "secret")
        def send_message(self, msg): sent.append(msg)
        def quit(self): pass

    monkeypatch.setattr(config, "SMTP_HOST", "smtp.test")
    monkeypatch.setattr(config, "SMTP_USER", "user")
    monkeypatch.setattr(config, "SMTP_PASSWORD", "secret")
    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)
    login(client)
    bid = upload_sample(client)["id"]
    client.post(f"/api/batches/{bid}/send", json={"confirm": True})
    wait_idle(client, bid)
    assert len(sent) == 11 and connections == [("smtp.test", 587)]
