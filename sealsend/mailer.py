"""Email building and delivery: sandbox (.eml files), SMTP or the Resend API."""
import base64
import html
import json
import smtplib
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

from . import config

DEFAULT_SUBJECT = "Congratulations {{NAME}}! Your certificate for {{EVENT}}"
DEFAULT_BODY = """Dear {{NAME}},

Congratulations on your {{ACHIEVEMENT}} in {{EVENT}}!

Your {{CERT_TYPE}} certificate is attached to this email.
Certificate ID: {{CERT_ID}}
Anyone can confirm it is genuine here: {{VERIFY_URL}}

Warm regards,
{{ISSUER}}"""

PRESETS = {
    "standard": {"label": "Standard", "subject": DEFAULT_SUBJECT, "body": DEFAULT_BODY},
    "winner": {
        "label": "Winner congratulations",
        "subject": "🏆 {{NAME}}, you won {{ACHIEVEMENT}} at {{EVENT}}!",
        "body": """Dear {{NAME}},

Huge congratulations! You earned {{ACHIEVEMENT}} at {{EVENT}}, and the whole committee is proud of you.

Your winner's certificate is attached. It is digitally signed, so anyone can confirm it is genuine:
{{VERIFY_URL}}
Certificate ID: {{CERT_ID}}

Keep building great things.

Warm regards,
{{ISSUER}}""",
    },
    "participation": {
        "label": "Thank you for participating",
        "subject": "Thank you for taking part in {{EVENT}}, {{NAME}}",
        "body": """Dear {{NAME}},

Thank you for participating in {{EVENT}}. Your effort and ideas made the event what it was.

Your certificate of {{CERT_TYPE}} is attached. You can verify it at any time:
{{VERIFY_URL}}
Certificate ID: {{CERT_ID}}

We hope to see you at the next one!

Warm regards,
{{ISSUER}}""",
    },
}


class PermanentFailure(Exception):
    """The address itself was rejected; retrying the same address is pointless."""


class TransientFailure(Exception):
    """Temporary problem (network, rate limit, server busy); a retry may succeed."""


def build_message(to_addr: str, to_name: str, subject: str, body: str,
                  attachment: bytes, attachment_name: str, cert_code: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = formataddr((config.MAIL_FROM_NAME, config.MAIL_FROM))
    msg["To"] = formataddr((to_name, to_addr))
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=config.MAIL_FROM.split("@")[-1] or "localhost")
    msg["X-SealSend-Certificate"] = cert_code
    msg.set_content(body)
    paragraphs = "".join(
        f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in body.split("\n\n") if p.strip()
    )
    msg.add_alternative(
        '<div style="font-family:-apple-system,Segoe UI,Arial,sans-serif;font-size:15px;line-height:1.55;'
        f'color:#111;max-width:560px">{paragraphs}</div>', subtype="html")
    msg.add_attachment(attachment, maintype="application", subtype="pdf", filename=attachment_name)
    return msg


class Sender:
    """One delivery channel per batch run. Reuses a single SMTP connection across the batch.

    `faults` (Chaos Test only, sandbox only) simulates a flaky provider:
    {"transient": [addresses that fail once], "reject": [addresses that bounce permanently]}
    """

    def __init__(self, mode: str | None = None, faults: dict | None = None):
        self.mode = mode or config.mail_mode()
        self.smtp = None
        self.faults = {k: {a.lower() for a in v} for k, v in (faults or {}).items()}
        self._tripped: set[str] = set()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _connect(self):
        if config.SMTP_SECURITY == "ssl":
            s = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, context=ssl.create_default_context(), timeout=30)
        else:
            s = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30)
            if config.SMTP_SECURITY == "starttls":
                s.starttls(context=ssl.create_default_context())
        if config.SMTP_USER:
            s.login(config.SMTP_USER, config.SMTP_PASSWORD)
        self.smtp = s

    def _simulate(self, to_addr: str) -> None:
        addr = to_addr.lower()
        if addr in self.faults.get("reject", set()):
            raise PermanentFailure(f"550 5.1.1 <{to_addr}>: mailbox does not exist (simulated)")
        if addr in self.faults.get("transient", set()) and addr not in self._tripped:
            self._tripped.add(addr)
            raise TransientFailure("421 4.7.0 Try again later: server busy (simulated)")

    def send(self, msg: EmailMessage, to_addr: str, outbox_name: str) -> str:
        if self.mode == "sandbox":
            self._simulate(to_addr)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
            path = config.OUTBOX_DIR / f"{outbox_name}_{stamp}.eml"
            path.write_bytes(bytes(msg))
            return f"Sandbox: saved {path.name}"
        if self.mode == "resend":
            return self._send_resend(msg, to_addr)
        return self._send_smtp(msg)

    def _send_smtp(self, msg: EmailMessage) -> str:
        try:
            if self.smtp is None:
                self._connect()
            try:
                self.smtp.send_message(msg)
            except smtplib.SMTPServerDisconnected:
                self.close()
                self._connect()
                self.smtp.send_message(msg)
        except smtplib.SMTPRecipientsRefused as e:
            raise PermanentFailure(f"Recipient refused: {e.recipients}") from e
        except smtplib.SMTPResponseException as e:
            if 500 <= e.smtp_code < 600 and e.smtp_code not in (500, 503, 530, 535):
                raise PermanentFailure(f"{e.smtp_code} {e.smtp_error!r}") from e
            raise TransientFailure(f"{e.smtp_code} {e.smtp_error!r}") from e
        except (OSError, smtplib.SMTPException) as e:
            self.close()
            raise TransientFailure(f"{type(e).__name__}: {e}") from e
        return "Accepted by SMTP server"

    def _send_resend(self, msg: EmailMessage, to_addr: str) -> str:
        att = next(msg.iter_attachments())
        payload = {
            "from": msg["From"], "to": [to_addr], "subject": msg["Subject"],
            "text": msg.get_body(("plain",)).get_content(),
            "html": msg.get_body(("html",)).get_content(),
            "attachments": [{"filename": att.get_filename(),
                             "content": base64.b64encode(att.get_content()).decode()}],
            "headers": {"X-SealSend-Certificate": msg["X-SealSend-Certificate"]},
        }
        req = urllib.request.Request(
            "https://api.resend.com/emails", data=json.dumps(payload).encode(), method="POST",
            headers={"Authorization": f"Bearer {config.RESEND_API_KEY}", "Content-Type": "application/json",
                     "User-Agent": "SealSend/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return f"Resend accepted: {json.loads(r.read() or b'{}').get('id', '')}"
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code in (429,) or e.code >= 500:
                raise TransientFailure(f"Resend {e.code}: {detail}") from e
            raise PermanentFailure(f"Resend {e.code}: {detail}") from e
        except (urllib.error.URLError, OSError) as e:
            raise TransientFailure(f"Resend unreachable: {e}") from e

    def close(self):
        if self.smtp is not None:
            try:
                self.smtp.quit()
            except Exception:
                pass
            self.smtp = None
