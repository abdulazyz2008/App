"""Persistent app settings (data/settings.json). Secrets are encrypted at rest with a local key.

Organizers configure email, organization branding and the admin password in the app itself,
so nobody has to edit files or environment variables.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import threading

from cryptography.fernet import Fernet, InvalidToken

from . import config

_lock = threading.Lock()
_cache: dict | None = None

PROVIDERS = {
    "gmail": {"label": "Gmail", "host": "smtp.gmail.com", "port": 587, "security": "starttls", "daily_cap": 450},
    "outlook": {"label": "Outlook / Microsoft 365", "host": "smtp.office365.com", "port": 587, "security": "starttls", "daily_cap": 9000},
    "smtp": {"label": "Other SMTP server", "host": "", "port": 587, "security": "starttls", "daily_cap": 2000},
    "resend": {"label": "Resend API", "host": "", "port": 0, "security": "", "daily_cap": 3000},
    "sandbox": {"label": "Sandbox (no real email)", "host": "", "port": 0, "security": "", "daily_cap": 100000},
}
DEFAULT = {
    "mail": {"provider": "", "address": "", "from_name": "", "reply_to": "", "host": "", "port": 587, "security": "starttls",
             "username": "", "password_enc": "", "daily_cap": 0, "delay_seconds": 1.0, "verified_at": ""},
    "org": {"org_name": "", "logo": "", "signer1_name": "", "signer1_title": "Event Coordinator", "signer1_sig": "",
            "signer2_name": "", "signer2_title": "Head of Department", "signer2_sig": ""},
    "admin": {"password_hash": ""},
    "public_base_url": "",
}


def _key() -> bytes:
    path = config.KEY_DIR / "settings.key"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(Fernet.generate_key())
    return path.read_bytes().strip()


def encrypt(value: str) -> str:
    return Fernet(_key()).encrypt(value.encode()).decode() if value else ""


def decrypt(token: str) -> str:
    if not token:
        return ""
    try:
        return Fernet(_key()).decrypt(token.encode()).decode()
    except (InvalidToken, ValueError):
        return ""


def load() -> dict:
    global _cache
    with _lock:
        if _cache is None:
            data = {}
            if config.SETTINGS_PATH.exists():
                try:
                    data = json.loads(config.SETTINGS_PATH.read_text(encoding="utf-8"))
                except ValueError:
                    data = {}
            merged = json.loads(json.dumps(DEFAULT))
            for k, v in data.items():
                if isinstance(v, dict) and isinstance(merged.get(k), dict):
                    merged[k].update(v)
                else:
                    merged[k] = v
            _cache = merged
        return _cache


def save(data: dict) -> None:
    global _cache
    with _lock:
        tmp = config.SETTINGS_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, config.SETTINGS_PATH)  # atomic on every OS
        _cache = data


def reset_cache() -> None:
    global _cache
    with _lock:
        _cache = None


def get(key: str, default=None):
    return load().get(key, default)


def mail() -> dict:
    """Effective mail settings with the password decrypted and provider defaults applied."""
    m = dict(load()["mail"])
    prov = PROVIDERS.get(m.get("provider") or "", {})
    if m.get("provider") in ("gmail", "outlook"):
        m["host"], m["port"], m["security"] = prov["host"], prov["port"], prov["security"]
        m["username"] = m.get("address", "")
    m["password"] = decrypt(m.pop("password_enc", ""))
    m["daily_cap"] = int(m.get("daily_cap") or prov.get("daily_cap", 450))
    return m


def public_mail() -> dict:
    m = mail()
    has = bool(m.pop("password"))
    m["has_password"] = has
    return m


def update_mail(fields: dict) -> None:
    data = load()
    m = data["mail"]
    for k in ("provider", "address", "from_name", "reply_to", "host", "port", "security", "username", "daily_cap", "delay_seconds"):
        if k in fields and fields[k] is not None:
            m[k] = fields[k]
    if fields.get("password"):
        m["password_enc"] = encrypt(fields["password"].replace(" ", "") if m.get("provider") == "gmail" else fields["password"])
    if fields.get("clear_password"):
        m["password_enc"] = ""
    m["verified_at"] = fields.get("verified_at", "")
    save(data)


def mark_verified(when: str) -> None:
    data = load()
    data["mail"]["verified_at"] = when
    save(data)


def org() -> dict:
    return dict(load()["org"])


def update_org(fields: dict) -> None:
    data = load()
    for k in DEFAULT["org"]:
        if k in fields and fields[k] is not None:
            data["org"][k] = str(fields[k])[:200]
    save(data)


# ---------------------------------------------------------------- admin password
def _hash(password: str, salt: bytes) -> str:
    dk = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
    return base64.b64encode(salt).decode() + "$" + base64.b64encode(dk).decode()


def admin_configured() -> bool:
    return bool(config.ADMIN_PASSWORD) or bool(load()["admin"].get("password_hash"))


def set_admin_password(password: str) -> None:
    data = load()
    data["admin"]["password_hash"] = _hash(password, secrets.token_bytes(16))
    save(data)


def check_admin_password(password: str) -> bool:
    if config.ADMIN_PASSWORD:
        return hmac.compare_digest(password.encode(), config.ADMIN_PASSWORD.encode())
    stored = load()["admin"].get("password_hash", "")
    if "$" not in stored:
        return False
    salt = base64.b64decode(stored.split("$")[0])
    return hmac.compare_digest(_hash(password, salt), stored)
