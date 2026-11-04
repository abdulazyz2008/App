"""Certificate rendering: themes, positioned text fields, QR code and embedded proof metadata."""
import copy
import hashlib
import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from . import config
from .data import render

FONT_FILES = {
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "serif-bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif-italic": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans-bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}
FALLBACK_FONTS = {"serif": "Times-Roman", "serif-bold": "Times-Bold", "serif-italic": "Times-Italic",
                  "sans": "Helvetica", "sans-bold": "Helvetica-Bold"}
_fonts: dict[str, str] = {}


def font(key: str) -> str:
    key = key if key in FALLBACK_FONTS else "sans"
    if key not in _fonts:
        path = Path(FONT_FILES[key])
        if path.exists():  # Unicode TTF so names with accents render correctly
            name = f"Seal-{key}"
            pdfmetrics.registerFont(TTFont(name, str(path)))
            _fonts[key] = name
        else:
            _fonts[key] = FALLBACK_FONTS[key]
    return _fonts[key]


THEMES = {
    "classic": {"label": "Classic", "description": "Navy and gold, the all-round default",
                "paper": "#fdfbf5", "frame": "#1f3a5f", "accent": "#b8892d", "title": "#1f3a5f",
                "name": "#1f3a5f", "text": "#333333", "muted": "#666666", "medal": False},
    "gold": {"label": "Gold", "description": "For winners: gold frame and a winner's medal",
             "paper": "#fffbf0", "frame": "#8a6a12", "accent": "#c9a227", "title": "#7a5a0c",
             "name": "#3d2f08", "text": "#3d3420", "muted": "#7a6b4f", "medal": True},
    "participation": {"label": "Participation", "description": "Calm slate tones for participants",
                      "paper": "#ffffff", "frame": "#4b5563", "accent": "#9ca3af", "title": "#374151",
                      "name": "#111827", "text": "#374151", "muted": "#6b7280", "medal": False},
    "mono": {"label": "Mono", "description": "Pure black and white, minimal",
             "paper": "#ffffff", "frame": "#000000", "accent": "#000000", "title": "#000000",
             "name": "#000000", "text": "#1a1a1a", "muted": "#666666", "medal": False},
}

DEFAULT_TEMPLATE = {
    "orientation": "landscape",
    "background": "",
    "theme": "classic",
    "qr": True,
    "fields": [
        {"text": "CERTIFICATE", "x": 0.5, "y": 0.80, "size": 42, "font": "serif-bold", "color": "title", "align": "center"},
        {"text": "OF {{CERT_TYPE}}", "x": 0.5, "y": 0.735, "size": 15, "font": "sans-bold", "color": "accent", "align": "center", "upper": True},
        {"text": "This certificate is proudly presented to", "x": 0.5, "y": 0.62, "size": 14, "font": "serif-italic", "color": "muted", "align": "center"},
        {"text": "{{NAME}}", "x": 0.5, "y": 0.50, "size": 40, "font": "serif-bold", "color": "name", "align": "center", "max_width": 0.7, "underline": True},
        {"text": "for {{ACHIEVEMENT}} in {{EVENT}}", "x": 0.5, "y": 0.395, "size": 16, "font": "sans", "color": "text", "align": "center", "max_width": 0.75},
        {"text": "held on {{DATE}}", "x": 0.5, "y": 0.345, "size": 13, "font": "sans", "color": "muted", "align": "center"},
        {"text": "Event Coordinator", "x": 0.25, "y": 0.17, "size": 11, "font": "sans", "color": "text", "align": "center", "signature_line": True},
        {"text": "Head of Department", "x": 0.75, "y": 0.17, "size": 11, "font": "sans", "color": "text", "align": "center", "signature_line": True},
        {"text": "Certificate ID: {{CERT_ID}}", "x": 0.075, "y": 0.075, "size": 8, "font": "sans", "color": "muted", "align": "left"},
    ],
}


def default_template() -> dict:
    return copy.deepcopy(DEFAULT_TEMPLATE)


def template_texts(tpl: dict) -> list[str]:
    return [f.get("text", "") for f in tpl.get("fields", [])]


def background_path(tpl: dict) -> str:
    if tpl.get("background"):
        candidate = config.UPLOAD_DIR / Path(tpl["background"]).name
        if candidate.exists():
            return str(candidate)
    return ""


def _page_size(tpl: dict, bg: Path | None):
    if bg is not None:
        iw, ih = ImageReader(str(bg)).getSize()
        width = landscape(A4)[0] if iw >= ih else portrait(A4)[0]
        return width, width * ih / iw
    return portrait(A4) if tpl.get("orientation") == "portrait" else landscape(A4)


def _color(value: str, theme: dict):
    return HexColor(theme.get(value, value) if not str(value).startswith("#") else value)


def _draw_frame(c: canvas.Canvas, w: float, h: float, th: dict) -> None:
    c.setFillColor(HexColor(th["paper"]))
    c.rect(0, 0, w, h, stroke=0, fill=1)
    c.setStrokeColor(HexColor(th["frame"]))
    c.setLineWidth(10)
    c.rect(18, 18, w - 36, h - 36)
    c.setStrokeColor(HexColor(th["accent"]))
    c.setLineWidth(1.5)
    c.rect(34, 34, w - 68, h - 68)
    c.setLineWidth(0.6)
    c.rect(40, 40, w - 80, h - 80)
    c.setFillColor(HexColor(th["accent"]))
    for (x, y) in ((40, 40), (w - 40, 40), (40, h - 40), (w - 40, h - 40)):
        c.circle(x, y, 5, stroke=0, fill=1)
    c.setStrokeColor(HexColor(th["accent"]))
    c.setLineWidth(1)
    c.line(w * 0.38, h * 0.695, w * 0.62, h * 0.695)


def _draw_medal(c: canvas.Canvas, x: float, y: float, th: dict) -> None:
    gold, dark = HexColor(th["accent"]), HexColor(th["frame"])
    c.setFillColor(dark)
    p = c.beginPath()  # ribbons
    p.moveTo(x - 16, y - 8); p.lineTo(x - 26, y - 46); p.lineTo(x - 14, y - 40); p.lineTo(x - 6, y - 50); p.lineTo(x - 2, y - 10)
    p.moveTo(x + 16, y - 8); p.lineTo(x + 26, y - 46); p.lineTo(x + 14, y - 40); p.lineTo(x + 6, y - 50); p.lineTo(x + 2, y - 10)
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(gold)
    c.circle(x, y, 30, stroke=0, fill=1)
    c.setStrokeColor(dark)
    c.setLineWidth(1.2)
    c.circle(x, y, 25, stroke=1, fill=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont(font("sans-bold"), 9)
    c.drawCentredString(x, y + 1, "WINNER")
    c.setFont(font("sans"), 6)
    c.drawCentredString(x, y - 9, "★ ★ ★")


def proof_keywords(cert_code: str, lock: str) -> str:
    return f"sealsend:v1:{cert_code}:{lock}"


def render_pdf(tpl: dict, values: dict, cert_code: str = "", lock: str = "", theme: str = "",
               title: str = "Certificate", bg_path: str | None = None) -> bytes:
    """Render one certificate. Output is byte-for-byte deterministic for the same inputs."""
    th = THEMES.get(theme or tpl.get("theme", "classic"), THEMES["classic"])
    if bg_path is None:
        bg_path = background_path(tpl)
    bg = Path(bg_path) if bg_path else None
    w, h = _page_size(tpl, bg)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h), invariant=1)
    c.setTitle(title)
    c.setAuthor(config.ISSUER_NAME)
    c.setCreator("SealSend")
    c.setSubject(cert_code)
    c.setKeywords(proof_keywords(cert_code, lock))  # the Mapping Lock travels inside the file

    if bg is not None:
        c.drawImage(ImageReader(str(bg)), 0, 0, width=w, height=h, mask="auto")
    else:
        _draw_frame(c, w, h, th)

    for f in tpl.get("fields", []):
        text = render(f.get("text", ""), values).strip()
        if f.get("upper"):
            text = text.upper()
        if not text:
            continue
        fname = font(f.get("font", "sans"))
        x, y = float(f.get("x", 0.5)) * w, float(f.get("y", 0.5)) * h
        size = float(f.get("size", 14))
        max_w = float(f.get("max_width", 0.85)) * w
        while size > 6 and pdfmetrics.stringWidth(text, fname, size) > max_w:
            size -= 0.5
        c.setFont(fname, size)
        c.setFillColor(_color(f.get("color", "text"), th))
        tw = pdfmetrics.stringWidth(text, fname, size)
        align = f.get("align", "center")
        if align == "center":
            c.drawCentredString(x, y, text)
            left = x - tw / 2
        elif align == "right":
            c.drawRightString(x, y, text)
            left = x - tw
        else:
            c.drawString(x, y, text)
            left = x
        if f.get("underline"):
            c.setStrokeColor(HexColor(th["accent"]))
            c.setLineWidth(1)
            c.line(left - 20, y - size * 0.35, left + tw + 20, y - size * 0.35)
        if f.get("signature_line"):
            c.setStrokeColor(HexColor(th["text"]))
            c.setLineWidth(0.8)
            c.line(x - 85, y + size + 6, x + 85, y + size + 6)

    if th.get("medal") and bg is None:
        _draw_medal(c, w * 0.5, h * 0.215, th)

    if tpl.get("qr", True) and values.get("VERIFY_URL"):
        size = 62
        widget = qr.QrCodeWidget(values["VERIFY_URL"])
        bx0, by0, bx1, by1 = widget.getBounds()
        d = Drawing(size, size, transform=[size / (bx1 - bx0), 0, 0, size / (by1 - by0), 0, 0])
        d.add(widget)
        renderPDF.draw(d, c, w - 0.075 * w - size + 6, 0.075 * h + 2)
        c.setFont(font("sans"), 6.5)
        c.setFillColor(HexColor(th["muted"]))
        c.drawCentredString(w - 0.075 * w - size / 2 + 6, 0.075 * h - 4, "Scan to verify")

    c.showPage()
    c.save()
    return buf.getvalue()


def render_job(job: tuple) -> bytes:
    """Process-pool entry point."""
    tpl, values, code, lock, theme, title, bg = job
    return render_pdf(tpl, values, code, lock, theme, title, bg_path=bg)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_proof(data: bytes) -> dict:
    """Extract (code, lock) that SealSend embedded in a PDF. Empty if absent or unreadable."""
    from pypdf import PdfReader

    try:
        meta = PdfReader(BytesIO(data)).metadata or {}
    except Exception:
        return {"code": "", "lock": ""}
    kw = str(meta.get("/Keywords", "") or "")
    parts = kw.split(":")
    if len(parts) == 4 and parts[0] == "sealsend":
        return {"code": parts[2], "lock": parts[3]}
    return {"code": str(meta.get("/Subject", "") or ""), "lock": ""}


def forge_copy(data: bytes, new_name: str, name_y: float = 0.50) -> bytes:
    """Demo helper: what a forger does. Paints over the name and writes a different one,
    keeping the original metadata so the file still *claims* to be the real certificate."""
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(BytesIO(data))
    page = reader.pages[0]
    w, h = float(page.mediabox.width), float(page.mediabox.height)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h))
    c.setFillColor(HexColor("#fdfbf5"))
    c.rect(w * 0.12, h * name_y - 18, w * 0.76, 58, stroke=0, fill=1)
    c.setFillColor(HexColor("#1f3a5f"))
    c.setFont(font("serif-bold"), 40)
    c.drawCentredString(w * 0.5, h * name_y, new_name)
    c.save()
    overlay = PdfReader(BytesIO(buf.getvalue())).pages[0]
    page.merge_page(overlay)
    writer = PdfWriter()
    writer.add_page(page)
    writer.add_metadata({k: v for k, v in (reader.metadata or {}).items()})
    out = BytesIO()
    writer.write(out)
    return out.getvalue()


def pdf_to_png(data: bytes, dpi: int = 110) -> bytes | None:
    """Rasterize for previews that work in every browser (incl. mobile). Needs poppler's pdftoppm."""
    exe = shutil.which("pdftoppm")
    if not exe:
        return None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([exe, "-png", "-r", str(dpi), "-singlefile", "-", str(Path(tmp) / "page")],
                           input=data, capture_output=True, timeout=30, check=True)
            out = Path(tmp) / "page.png"
            return out.read_bytes() if out.exists() else None
    except Exception:
        return None
