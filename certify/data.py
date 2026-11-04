"""Spreadsheet loading, column-to-placeholder mapping and record validation."""
import hashlib
import math
import re
from datetime import date, datetime
from pathlib import Path

import pandas as pd

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*\.[A-Za-z]{2,}$")

# Placeholders the system fills in by itself; they never need a column.
BUILTIN = {"CERT_ID", "VERIFY_URL", "ISSUE_DATE"}

# Hints used to pre-fill the mapping from common column names.
HINTS = {
    "NAME": ["student name", "full name", "name", "participant", "student"],
    "ID": ["student id", "roll no", "roll number", "register number", "reg no", "id", "usn", "enrollment"],
    "EVENT": ["event", "event name", "program", "workshop", "competition"],
    "CERT_TYPE": ["certificate type", "cert type", "type", "category"],
    "ACHIEVEMENT": ["achievement", "position", "rank", "award", "result"],
    "DATE": ["date", "event date", "issue date"],
    "DEPARTMENT": ["department", "dept", "branch"],
    "COLLEGE": ["college", "institution", "university", "school"],
}
EMAIL_HINTS = ["student email", "college email", "official email", "institute email", "email", "mail", "e-mail"]
FALLBACK_HINTS = ["personal email", "alternate email", "alt email", "secondary email", "gmail"]


def _clean_cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        if math.isnan(v):
            return ""
        if v.is_integer():
            return str(int(v))
    if isinstance(v, (pd.Timestamp, datetime)):
        return v.strftime("%d %B %Y")
    if isinstance(v, date):
        return v.strftime("%d %B %Y")
    return re.sub(r"\s+", " ", str(v)).strip()


def load_table(path: Path) -> tuple[list[str], list[dict]]:
    """Read CSV/XLSX into (columns, rows). Every value becomes a clean string."""
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path, dtype=object)
    elif suffix in (".csv", ".txt"):
        df = None
        for enc in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding=enc, sep=None, engine="python")
                break
            except UnicodeDecodeError:
                continue
        if df is None:
            raise ValueError("Could not decode the CSV file")
    else:
        raise ValueError("Unsupported file type. Upload .csv or .xlsx")

    columns, seen = [], {}
    for c in df.columns:
        name = _clean_cell(c) or "Column"
        if name.lower().startswith("unnamed:"):
            name = "Column"
        if name in seen:
            seen[name] += 1
            name = f"{name} ({seen[name]})"
        else:
            seen[name] = 1
        columns.append(name)

    rows = []
    for raw in df.itertuples(index=False):
        row = {col: _clean_cell(v) for col, v in zip(columns, raw)}
        if any(row.values()):
            rows.append(row)
    if not columns or not rows:
        raise ValueError("The file has no data rows")
    return columns, rows


def _best_column(columns: list[str], hints: list[str], exclude=()) -> str:
    norm = {c: re.sub(r"[^a-z0-9 ]", " ", c.lower()).strip() for c in columns if c not in exclude}
    for hint in hints:  # exact match first, in hint priority order
        for c, n in norm.items():
            if re.sub(r"\s+", " ", n) == hint:
                return c
    for hint in hints:
        for c, n in norm.items():
            if hint in n:
                return c
    return ""


def suggest_config(columns: list[str]) -> dict:
    email_col = _best_column(columns, EMAIL_HINTS)
    fallback_col = _best_column(columns, FALLBACK_HINTS, exclude=(email_col,))
    if fallback_col and fallback_col == email_col:
        fallback_col = ""
    # If the only "email" match is the personal one, prefer it as primary.
    if email_col and "personal" in email_col.lower() and not fallback_col:
        other = _best_column(columns, ["email"], exclude=(email_col,))
        if other:
            email_col, fallback_col = other, email_col
    mapping = {}
    used = {email_col, fallback_col}
    for ph in ["ID", "NAME", "EVENT", "CERT_TYPE", "ACHIEVEMENT", "DATE", "DEPARTMENT", "COLLEGE"]:
        col = _best_column(columns, HINTS[ph], exclude=used)
        if col:
            mapping[ph] = {"type": "column", "value": col}
            used.add(col)
    return {"mapping": mapping, "email_column": email_col, "fallback_column": fallback_col}


def placeholders_in(*texts: str) -> list[str]:
    found = []
    for t in texts:
        for m in PLACEHOLDER_RE.findall(t or ""):
            m = m.upper()
            if m not in found:
                found.append(m)
    return found


def render(text: str, values: dict) -> str:
    return PLACEHOLDER_RE.sub(lambda m: values.get(m.group(1).upper(), ""), text or "")


def resolve_values(row: dict, mapping: dict) -> dict:
    """Apply the organizer's mapping to a row. Unmapped placeholders resolve to ''."""
    values = {}
    for ph, src in mapping.items():
        if not src:
            continue
        if src.get("type") == "text":
            values[ph.upper()] = src.get("value", "")
        else:
            values[ph.upper()] = row.get(src.get("value", ""), "")
    return values


def valid_email(addr: str) -> bool:
    return bool(addr) and len(addr) <= 254 and ".." not in addr and bool(EMAIL_RE.match(addr))


def dedupe_key(values: dict, email: str) -> str:
    identity = (values.get("ID") or email or values.get("NAME", "")).strip().lower()
    parts = [identity] + [values.get(k, "").strip().lower() for k in ("EVENT", "CERT_TYPE", "ACHIEVEMENT")]
    return hashlib.sha1("|".join(parts).encode()).hexdigest()


def validate(rows: list[dict], cfg: dict, cert_placeholders: list[str]) -> list[dict]:
    """Return per-row validation results: name, id, email, email_source, errors, warnings, dedupe_key."""
    mapping = cfg.get("mapping", {})
    email_col = cfg.get("email_column", "")
    fallback_col = cfg.get("fallback_column", "")
    required = [p for p in cert_placeholders if p not in BUILTIN]

    results, seen_id, seen_email = [], {}, {}
    for i, row in enumerate(rows):
        values = resolve_values(row, mapping)
        errors, warnings = [], []

        name = values.get("NAME", "").strip()
        if "NAME" not in mapping or not mapping["NAME"]:
            errors.append("NAME is not mapped to a column")
        elif not name:
            errors.append("Missing name")

        primary = row.get(email_col, "").strip() if email_col else ""
        fallback = row.get(fallback_col, "").strip() if fallback_col else ""
        email, source = "", ""
        if valid_email(primary):
            email, source = primary, email_col
        elif valid_email(fallback):
            email, source = fallback, fallback_col
            warnings.append(f"Used fallback email ({'invalid' if primary else 'missing'} {email_col or 'primary'})")
        if not email_col:
            errors.append("No email column selected")
        elif not email:
            if primary or fallback:
                errors.append(f"Invalid email: {primary or fallback}")
            else:
                errors.append("Missing email")

        for ph in required:
            if ph == "NAME":
                continue
            if ph not in mapping or not mapping[ph]:
                errors.append(f"{{{{{ph}}}}} is used in the certificate but not mapped")
            elif not values.get(ph, "").strip():
                errors.append(f"Missing {ph}")

        sid = values.get("ID", "").strip()
        if sid:
            if sid.lower() in seen_id:
                errors.append(f"Duplicate of row {seen_id[sid.lower()]} (same ID)")
            else:
                seen_id[sid.lower()] = i + 2  # +2: header row + 1-based rows, matches the spreadsheet
        if email:
            ekey = (email.lower(), name.lower())
            if ekey in seen_email and not any(e.startswith("Duplicate") for e in errors):
                errors.append(f"Duplicate of row {seen_email[ekey]} (same name and email)")
            else:
                seen_email.setdefault(ekey, i + 2)

        results.append({
            "name": name,
            "student_id": sid,
            "email": email,
            "email_source": source,
            "errors": errors,
            "warnings": warnings,
            "dedupe_key": dedupe_key(values, email) if email else "",
            "values": values,
        })
    return results


def safe_filename(text: str, max_len: int = 120) -> str:
    text = re.sub(r"[^\w\s.-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s]+", "_", text.strip())
    text = re.sub(r"_+", "_", text).strip("._")
    return text[:max_len] or "certificate"
