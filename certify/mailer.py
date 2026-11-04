"""Email building and delivery. SMTP when configured, otherwise a local outbox of .eml files."""
import html
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

from . import config


DEFAULT_SUBJECT = "Congratulations {{NAME}}! Your certificate for {{EVENT}}"
DEFAULT_BODY = """Dear {{NAME}},

Congratulations on your {{ACHIEVEMENT}} in {{EVENT}}!

Please find your {{CERT_TYPE}} certificate attached to this email.
Certificate ID: {{CERT_ID}}
You can verify it at any time: {{VERIFY_URL}}

We appreciate your participation and wish you continued success.

Warm regards,
Event Organizing Team"""


def build_message(to_addr: str, to_name: str, subject: str, body: str,
                  attachment: bytes, attachment_name: str, record_code: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = formataddr((config.MAIL_FROM_NAME, config.MAIL_FROM))
    msg["To"] = formataddr((to_name, to_addr))
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=config.MAIL_FROM.split("@")[-1] or "localhost")
    msg["X-Certificate-ID"] = record_code
    msg.set_content(body)
    paragraphs = "".join(
        f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in body.split("\n\n") if p.strip()
    )
    msg.add_alternative(
        f'<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#222">{paragraphs}</div>',
        subtype="html",
    )
    msg.add_attachment(attachment, maintype="application", subtype="pdf", filename=attachment_name)
    return msg


class Sender:
    """Reuses one SMTP connection across a whole batch (much faster for hundreds of emails)."""

    def __init__(self):
        self.mode = config.mail_mode()
        self.smtp = None

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

    def send(self, msg: EmailMessage, outbox_name: str) -> str:
        if self.mode == "outbox":
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
            path = config.OUTBOX_DIR / f"{outbox_name}_{stamp}.eml"
            path.write_bytes(bytes(msg))
            return f"Saved to outbox: {path.name}"
        if self.smtp is None:
            self._connect()
        try:
            self.smtp.send_message(msg)
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPSenderRefused):
            # Connection dropped mid-batch: reconnect once and retry this message.
            self.close()
            self._connect()
            self.smtp.send_message(msg)
        return "Accepted by SMTP server"

    def close(self):
        if self.smtp is not None:
            try:
                self.smtp.quit()
            except Exception:
                pass
            self.smtp = None
