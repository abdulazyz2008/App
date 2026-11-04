"""Runtime configuration, read from environment variables (never hard-coded secrets)."""
import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader so organizers can keep credentials out of the code."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


ROOT = Path(__file__).resolve().parent.parent
_load_dotenv(ROOT / ".env")

DATA_DIR = Path(os.environ.get("CERTIFY_DATA_DIR", ROOT / "data")).resolve()
DB_PATH = DATA_DIR / "certify.db"
UPLOAD_DIR = DATA_DIR / "uploads"
CERT_DIR = DATA_DIR / "certificates"
OUTBOX_DIR = DATA_DIR / "outbox"

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_SECURITY = os.environ.get("SMTP_SECURITY", "starttls").lower()  # starttls | ssl | none
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER or "certificates@example.org")
MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", "Certificate Desk")

SEND_DELAY_SECONDS = float(os.environ.get("SEND_DELAY_SECONDS", "0"))
MAX_SEND_ATTEMPTS = int(os.environ.get("MAX_SEND_ATTEMPTS", "3"))
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "20"))
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000")


def mail_mode() -> str:
    return "smtp" if SMTP_HOST else "outbox"


for d in (DATA_DIR, UPLOAD_DIR, CERT_DIR, OUTBOX_DIR):
    d.mkdir(parents=True, exist_ok=True)
