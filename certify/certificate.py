"""Certificate rendering: a template (background + positioned text fields) filled per student."""
import copy
import hashlib
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
FALLBACK_FONTS = {
    "serif": "Times-Roman", "serif-bold": "Times-Bold", "serif-italic": "Times-Italic",
    "sans": "Helvetica", "sans-bold": "Helvetica-Bold",
}
_fonts: dict[str, str] = {}


def font(key: str) -> str:
    key = key if key in FALLBACK_FONTS else "sans"
    if key not in _fonts:
        path = Path(FONT_FILES[key])
        if path.exists():  # Unicode TTF so names with accents etc. render correctly
            name = f"Cert-{key}"
            pdfmetrics.registerFont(TTFont(name, str(path)))
            _fonts[key] = name
        else:
            _fonts[key] = FALLBACK_FONTS[key]
    return _fonts[key]


DEFAULT_TEMPLATE = {
    "orientation": "landscape",
    "background": "",
    "accent": "#1f3a5f",
    "gold": "#b8892d",
    "qr": True,
    "fields": [
        {"text": "CERTIFICATE", "x": 0.5, "y": 0.80, "size": 42, "font": "serif-bold", "color": "#1f3a5f", "align": "center"},
        {"text": "OF {{CERT_TYPE}}", "x": 0.5, "y": 0.735, "size": 15, "font": "sans-bold", "color": "#b8892d", "align": "center", "upper": True},
        {"text": "This certificate is proudly presented to", "x": 0.5, "y": 0.62, "size": 14, "font": "serif-italic", "color": "#555555", "align": "center"},
        {"text": "{{NAME}}", "x": 0.5, "y": 0.50, "size": 40, "font": "serif-bold", "color": "#1f3a5f", "align": "center", "max_width": 0.7, "underline": True},
        {"text": "for {{ACHIEVEMENT}} in {{EVENT}}", "x": 0.5, "y": 0.395, "size": 16, "font": "sans", "color": "#333333", "align": "center", "max_width": 0.75},
        {"text": "held on {{DATE}}", "x": 0.5, "y": 0.345, "size": 13, "font": "sans", "color": "#555555", "align": "center"},
        {"text": "Event Coordinator", "x": 0.25, "y": 0.17, "size": 11, "font": "sans", "color": "#333333", "align": "center", "signature_line": True},
        {"text": "Head of Department", "x": 0.75, "y": 0.17, "size": 11, "font": "sans", "color": "#333333", "align": "center", "signature_line": True},
        {"text": "Certificate ID: {{CERT_ID}}", "x": 0.075, "y": 0.075, "size": 8, "font": "sans", "color": "#777777", "align": "left"},
    ],
}


def default_template() -> dict:
    return copy.deepcopy(DEFAULT_TEMPLATE)


def template_texts(tpl: dict) -> list[str]:
    return [f.get("text", "") for f in tpl.get("fields", [])]


def _page_size(tpl: dict, bg: Path | None):
    if bg is not None:
        iw, ih = ImageReader(str(bg)).getSize()
        width = landscape(A4)[0] if iw >= ih else portrait(A4)[0]
        return width, width * ih / iw
    return portrait(A4) if tpl.get("orientation") == "portrait" else landscape(A4)


def _draw_default_frame(c: canvas.Canvas, w: float, h: float, tpl: dict) -> None:
    accent, gold = HexColor(tpl.get("accent", "#1f3a5f")), HexColor(tpl.get("gold", "#b8892d"))
    c.setFillColor(HexColor("#fdfbf5"))
    c.rect(0, 0, w, h, stroke=0, fill=1)
    c.setStrokeColor(accent)
    c.setLineWidth(10)
    c.rect(18, 18, w - 36, h - 36)
    c.setStrokeColor(gold)
    c.setLineWidth(1.5)
    c.rect(34, 34, w - 68, h - 68)
    c.setLineWidth(0.6)
    c.rect(40, 40, w - 80, h - 80)
    # Corner accents
    c.setFillColor(gold)
    for (x, y) in ((40, 40), (w - 40, 40), (40, h - 40), (w - 40, h - 40)):
        c.circle(x, y, 5, stroke=0, fill=1)
    # Divider under the title block
    c.setStrokeColor(gold)
    c.setLineWidth(1)
    c.line(w * 0.38, h * 0.695, w * 0.62, h * 0.695)


def _fit_size(text: str, font_name: str, size: float, max_w: float) -> float:
    while size > 6 and pdfmetrics.stringWidth(text, font_name, size) > max_w:
        size -= 0.5
    return size


def background_path(tpl: dict) -> str:
    if tpl.get("background"):
        candidate = config.UPLOAD_DIR / Path(tpl["background"]).name
        if candidate.exists():
            return str(candidate)
    return ""


def render_job(job: tuple) -> bytes:
    """Process-pool entry point: (template, values, code, title, background path)."""
    tpl, values, code, title, bg = job
    return render_pdf(tpl, values, code, title, bg_path=bg)


def render_pdf(tpl: dict, values: dict, cert_code: str = "", title: str = "Certificate",
               bg_path: str | None = None) -> bytes:
    """Render one certificate to PDF bytes. `values` maps placeholder -> text."""
    if bg_path is None:
        bg_path = background_path(tpl)
    bg = Path(bg_path) if bg_path else None
    w, h = _page_size(tpl, bg)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h), invariant=1)
    c.setTitle(title)
    c.setAuthor(config.MAIL_FROM_NAME)
    c.setSubject(cert_code)  # read back before sending to prove the attachment belongs to this record
    c.setKeywords(f"certify-record:{cert_code}")

    if bg is not None:
        c.drawImage(ImageReader(str(bg)), 0, 0, width=w, height=h, mask="auto")
    else:
        _draw_default_frame(c, w, h, tpl)

    for f in tpl.get("fields", []):
        text = render(f.get("text", ""), values).strip()
        if f.get("upper"):
            text = text.upper()
        if not text:
            continue
        fname = font(f.get("font", "sans"))
        x, y = float(f.get("x", 0.5)) * w, float(f.get("y", 0.5)) * h
        size = _fit_size(text, fname, float(f.get("size", 14)), float(f.get("max_width", 0.85)) * w)
        c.setFont(fname, size)
        c.setFillColor(HexColor(f.get("color", "#000000")))
        align = f.get("align", "center")
        tw = pdfmetrics.stringWidth(text, fname, size)
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
            c.setStrokeColor(HexColor(tpl.get("gold", "#b8892d")))
            c.setLineWidth(1)
            pad = 20
            c.line(left - pad, y - size * 0.35, left + tw + pad, y - size * 0.35)
        if f.get("signature_line"):
            c.setStrokeColor(HexColor("#333333"))
            c.setLineWidth(0.8)
            c.line(x - 85, y + size + 6, x + 85, y + size + 6)

    if tpl.get("qr", True) and values.get("VERIFY_URL"):
        size = 62
        widget = qr.QrCodeWidget(values["VERIFY_URL"])
        bx0, by0, bx1, by1 = widget.getBounds()
        d = Drawing(size, size, transform=[size / (bx1 - bx0), 0, 0, size / (by1 - by0), 0, 0])
        d.add(widget)
        renderPDF.draw(d, c, w - 0.075 * w - size + 6, 0.075 * h + 2)
        c.setFont(font("sans"), 6.5)
        c.setFillColor(HexColor("#777777"))
        c.drawCentredString(w - 0.075 * w - size / 2 + 6, 0.075 * h - 4, "Scan to verify")

    c.showPage()
    c.save()
    return buf.getvalue()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pdf_subject(data: bytes) -> str:
    """Read the record code embedded in a generated PDF (used as a send-time integrity check)."""
    from pypdf import PdfReader

    meta = PdfReader(BytesIO(data)).metadata or {}
    return str(meta.get("/Subject", "") or "")


def pdf_to_png(data: bytes, dpi: int = 110) -> bytes | None:
    """Rasterize for previews that work in every browser (incl. mobile). Needs poppler's pdftoppm."""
    import shutil
    import subprocess

    exe = shutil.which("pdftoppm")
    if not exe:
        return None
    import tempfile

    try:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([exe, "-png", "-r", str(dpi), "-singlefile", "-", str(Path(tmp) / "page")],
                           input=data, capture_output=True, timeout=30, check=True)
            out = Path(tmp) / "page.png"
            return out.read_bytes() if out.exists() else None
    except Exception:
        return None
