"""SQLite storage for batches, student records and the send log."""
import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone

from . import config

_lock = threading.RLock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    filename TEXT NOT NULL,
    created_at TEXT NOT NULL,
    columns_json TEXT NOT NULL,
    config_json TEXT NOT NULL DEFAULT '{}',
    job TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL REFERENCES batches(id),
    row_no INTEGER NOT NULL,
    data_json TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    student_id TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    email_source TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'Pending',
    errors TEXT NOT NULL DEFAULT '',
    warnings TEXT NOT NULL DEFAULT '',
    cert_code TEXT NOT NULL DEFAULT '',
    cert_file TEXT NOT NULL DEFAULT '',
    cert_sha256 TEXT NOT NULL DEFAULT '',
    dedupe_key TEXT NOT NULL DEFAULT '',
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT NOT NULL DEFAULT '',
    sent_at TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_records_batch ON records(batch_id, status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_records_code ON records(cert_code) WHERE cert_code != '';
CREATE TABLE IF NOT EXISTS send_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    dedupe_key TEXT NOT NULL,
    email TEXT NOT NULL,
    attachment TEXT NOT NULL,
    result TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_send_log_key ON send_log(dedupe_key, result);
"""


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


_conn = None


def conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = _connect()
        _conn.executescript(SCHEMA)
    return _conn


def reset_connection() -> None:
    """Used by tests that point CERTIFY_DATA_DIR somewhere new."""
    global _conn
    if _conn is not None:
        _conn.close()
    _conn = None


@contextmanager
def tx():
    with _lock:
        c = conn()
        try:
            yield c
            c.commit()
        except Exception:
            c.rollback()
            raise


def query(sql: str, params=()) -> list[dict]:
    with _lock:
        return [dict(r) for r in conn().execute(sql, params).fetchall()]


def one(sql: str, params=()):
    rows = query(sql, params)
    return rows[0] if rows else None


def get_batch(batch_id: int):
    b = one("SELECT * FROM batches WHERE id=?", (batch_id,))
    if b:
        b["columns"] = json.loads(b.pop("columns_json"))
        b["config"] = json.loads(b.pop("config_json"))
    return b


def save_config(batch_id: int, cfg: dict) -> None:
    with tx() as c:
        c.execute("UPDATE batches SET config_json=? WHERE id=?", (json.dumps(cfg), batch_id))


def set_job(batch_id: int, job: str) -> None:
    with tx() as c:
        c.execute("UPDATE batches SET job=? WHERE id=?", (job, batch_id))


def update_record(record_id: int, **fields) -> None:
    fields["updated_at"] = now()
    cols = ", ".join(f"{k}=?" for k in fields)
    with tx() as c:
        c.execute(f"UPDATE records SET {cols} WHERE id=?", (*fields.values(), record_id))


def record_data(rec: dict) -> dict:
    return json.loads(rec["data_json"])


def status_counts(batch_id: int) -> dict:
    rows = query("SELECT status, COUNT(*) n FROM records WHERE batch_id=? GROUP BY status", (batch_id,))
    counts = {r["status"]: r["n"] for r in rows}
    counts["Total"] = sum(counts.values())
    return counts
