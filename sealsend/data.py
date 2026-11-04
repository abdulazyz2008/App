"""Spreadsheet loading, column mapping, validation and self-healing of student data."""
import hashlib
import math
import re
import unicodedata
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import pandas as pd

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*\.[A-Za-z]{2,}$"
)

# Placeholders the system fills in by itself; they never need a column.
BUILTIN = {"CERT_ID", "VERIFY_URL", "ISSUE_DATE", "ISSUER"}

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

POPULAR_DOMAINS = [
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.in", "yahoo.co.uk", "ymail.com", "outlook.com",
    "hotmail.com", "live.com", "msn.com", "icloud.com", "me.com", "aol.com", "protonmail.com", "proton.me",
    "rediffmail.com", "zoho.com", "gmx.com", "mail.com",
]
TLD_FIXES = {"con": "com", "cmo": "com", "ocm": "com", "comm": "com", "coom": "com", "cm": "com", "om": "com",
             "vom": "com", "xom": "com", "ner": "net", "nte": "net", "ogr": "org", "orgg": "org", "eud": "edu"}

JUNK_NAMES = {"#n/a", "#ref!", "#value!", "#name?", "#div/0!", "#null!", "#num!", "n/a", "na", "null", "none",
              "nil", "undefined", "nan", "-", "--", "?", "test", "xxx", "name", "student name", "full name", "tbd",
              "unknown", "{{name}}"}


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
    norm = {c: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", c.lower())).strip() for c in columns if c not in exclude}
    for hint in hints:
        for c, n in norm.items():
            if n == hint:
                return c
    for hint in hints:
        for c, n in norm.items():
            if hint in n:
                return c
    return ""


def suggest_config(columns: list[str]) -> dict:
    email_col = _best_column(columns, EMAIL_HINTS, exclude=[c for c in columns if "personal" in c.lower()])
    fallback_col = _best_column(columns, FALLBACK_HINTS, exclude=(email_col,))
    if not email_col and fallback_col:
        email_col, fallback_col = fallback_col, ""
    mapping, used = {}, {email_col, fallback_col}
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
    values = {}
    for ph, src in mapping.items():
        if not src:
            continue
        if src.get("type") == "text":
            values[ph.upper()] = src.get("value", "")
        else:
            values[ph.upper()] = row.get(src.get("value", ""), "")
    return values


# ---------------------------------------------------------------- names
def check_name(name: str) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    if not name:
        return ["Missing name"], []
    low = name.lower().strip()
    if low in JUNK_NAMES or low.startswith("#"):
        errors.append(f"Name looks like a placeholder or spreadsheet error: “{name}”")
    elif "@" in name:
        errors.append(f"Name looks like an email address: “{name}”")
    elif any(ch.isdigit() for ch in name):
        errors.append(f"Name contains digits: “{name}”")
    elif len(name) < 2:
        errors.append(f"Name is too short: “{name}”")
    elif len(name) > 70:
        errors.append(f"Name is too long ({len(name)} characters)")
    else:
        bad = {ch for ch in name if not (unicodedata.category(ch)[0] in "LM" or ch in " .'-,’")}
        if bad:
            errors.append(f"Name has unexpected characters {' '.join(sorted(bad))}: “{name}”")
    if not errors and len(name) > 3 and name == name.upper() and any(c.isalpha() for c in name):
        warnings.append("Name is ALL CAPS")
    elif not errors and name == name.lower():
        warnings.append("Name is all lowercase")
    return errors, warnings


# ---------------------------------------------------------------- emails
def valid_email(addr: str) -> bool:
    return bool(addr) and len(addr) <= 254 and ".." not in addr and bool(EMAIL_RE.match(addr))


def normalize_email(raw: str) -> str:
    """Safe, lossless cleanup: whitespace, mailto:, <>, trailing punctuation, (at), domain case."""
    s = (raw or "").strip()
    s = re.sub(r"^mailto:", "", s, flags=re.I).strip()
    s = s.strip("<>").rstrip(".,;:").strip("<>").strip()
    s = re.sub(r"\s*[\(\[]\s*at\s*[\)\]]\s*", "@", s, flags=re.I)
    s = s.rstrip(".,;:")
    if s.count("@") == 1:
        local, domain = s.split("@")
        domain = domain.strip().lower().replace(",", ".")
        s = f"{local.strip()}@{domain}"
    return s


def _osa(a: str, b: str) -> int:
    """Optimal string alignment distance (Levenshtein + adjacent transpositions)."""
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[-1][-1]


def _risky_substitution(a: str, b: str) -> bool:
    """A single swapped letter in a short domain (lime.com vs live.com) is often a different real domain."""
    return len(a) == len(b) and len(a) < 9 and sum(x != y for x, y in zip(a, b)) == 1


def fix_email_typo(addr: str, sheet_domains: Counter) -> tuple[str, str]:
    """Return (fixed_address, description) or ("", "") if no confident fix exists."""
    if addr.count("@") != 1:
        return "", ""
    local, domain = addr.split("@")
    if not local or not domain:
        return "", ""
    known = set(POPULAR_DOMAINS) | {d for d, n in sheet_domains.items() if n >= 3}
    if domain in known or sheet_domains.get(domain, 0) >= 2:
        return "", ""  # a domain several students use is real, not a typo
    candidate = ""
    # (a) one or two keystrokes away from a known domain
    scored = sorted((_osa(domain, k), k) for k in known)
    if scored:
        dist = scored[0][0]
        best = [k for d, k in scored if d == dist]
        limit = 2 if len(domain) >= 10 else 1
        if dist <= limit and len(best) == 1 and not _risky_substitution(domain, best[0]):
            candidate = best[0]
    # (b) right name, broken ending: college.example.con -> college.example.edu (a domain in this sheet)
    base, _, tld = domain.rpartition(".")
    if not candidate and base and tld not in ("com", "org", "net", "edu", "in", "co", "uk", "io", "ac", "gov"):
        same_base = [k for k in known if k.rpartition(".")[0] == base]
        if len(same_base) == 1:
            candidate = same_base[0]
    # (c) common TLD slips with no better evidence: .con -> .com
    if not candidate and base and tld in TLD_FIXES:
        candidate = f"{base}.{TLD_FIXES[tld]}"
    if not candidate:
        return "", ""
    fixed = f"{local}@{candidate}"
    if candidate == domain or not valid_email(fixed):
        return "", ""
    return fixed, f"{domain} → {candidate}"


def dedupe_key(values: dict, email: str) -> str:
    identity = (values.get("ID") or email or values.get("NAME", "")).strip().lower()
    parts = [identity] + [values.get(k, "").strip().lower() for k in ("EVENT", "CERT_TYPE", "ACHIEVEMENT")]
    return hashlib.sha1("|".join(parts).encode()).hexdigest()


def pick_email(primary_raw: str, fallback_raw: str, primary_col: str, fallback_col: str,
               auto_fix: bool, sheet_domains: Counter) -> dict:
    """Choose the best deliverable address. Order: exact/cleaned primary, cleaned fallback,
    typo-fixed primary, typo-fixed fallback. Guesses come last, real addresses first."""
    cands = [(primary_raw, primary_col), (fallback_raw, fallback_col)]
    for raw, col in cands:
        norm = normalize_email(raw)
        if raw and valid_email(norm):
            if auto_fix:  # well-formed but misspelled: name@gmial.com
                fixed, desc = fix_email_typo(norm, sheet_domains)
                if fixed:
                    return {"email": fixed, "source": col, "fix": f"typo {desc}"}
            fix = f"cleaned “{raw}”" if norm != raw else ""
            return {"email": norm, "source": col, "fix": fix}
    if auto_fix:
        for raw, col in cands:
            norm = normalize_email(raw)
            if raw:
                fixed, desc = fix_email_typo(norm, sheet_domains)
                if fixed:
                    return {"email": fixed, "source": col, "fix": f"typo {desc}"}
    return {"email": "", "source": "", "fix": ""}


def validate(rows: list[dict], cfg: dict, cert_placeholders: list[str]) -> list[dict]:
    mapping = cfg.get("mapping", {})
    email_col = cfg.get("email_column", "")
    fallback_col = cfg.get("fallback_column", "")
    auto_fix = cfg.get("auto_fix_emails", True)
    claim_missing = cfg.get("claim_links", True)
    required = [p for p in cert_placeholders if p not in BUILTIN and p != "NAME"]

    sheet_domains = Counter()
    for row in rows:
        for col in (email_col, fallback_col):
            norm = normalize_email(row.get(col, "")) if col else ""
            if valid_email(norm):
                sheet_domains[norm.split("@")[1]] += 1

    results, seen_id, seen_email = [], {}, {}
    for i, row in enumerate(rows):
        sheet_row = i + 2  # header is row 1
        values = resolve_values(row, mapping)
        errors, warnings = [], []

        name = values.get("NAME", "").strip()
        if not mapping.get("NAME"):
            errors.append("NAME is not mapped to a column")
        else:
            e, w = check_name(name)
            errors += e
            warnings += w

        for ph in required:
            if not mapping.get(ph):
                errors.append(f"{{{{{ph}}}}} is used on the certificate but not mapped")
            elif not values.get(ph, "").strip():
                errors.append(f"Missing {ph.replace('_', ' ').title()}")

        primary = row.get(email_col, "").strip() if email_col else ""
        fallback = row.get(fallback_col, "").strip() if fallback_col else ""
        picked = pick_email(primary, fallback, email_col, fallback_col, auto_fix, sheet_domains)
        email, delivery = picked["email"], "email"
        if picked["fix"]:
            warnings.append(f"Auto-fixed email: {picked['fix']}")
        if email and picked["source"] == fallback_col and fallback_col:
            warnings.append(f"Using fallback email ({'invalid' if primary else 'missing'} {email_col})")
        if not email_col:
            errors.append("No email column selected")
        elif not email:
            problem = f"Invalid email “{primary or fallback}”" if (primary or fallback) else "Missing email"
            if claim_missing and not errors:
                delivery = "claim"
                warnings.append(f"{problem}: certificate will be issued through a claim link")
            else:
                errors.append(problem)

        sid = values.get("ID", "").strip()
        if sid:
            if sid.lower() in seen_id:
                errors.append(f"Duplicate of row {seen_id[sid.lower()]} (same ID {sid})")
            else:
                seen_id[sid.lower()] = sheet_row
        if email and not any(e.startswith("Duplicate") for e in errors):
            ekey = (email.lower(), name.lower())
            if ekey in seen_email:
                errors.append(f"Duplicate of row {seen_email[ekey]} (same name and email)")
            else:
                seen_email[ekey] = sheet_row

        if errors:
            delivery = "email"
        results.append({
            "name": name, "student_id": sid, "email": email, "email_source": picked["source"],
            "email_fix": picked["fix"], "delivery": delivery, "errors": errors, "warnings": warnings,
            "dedupe_key": dedupe_key(values, email), "values": values,
        })
    return results


def safe_filename(text: str, max_len: int = 120) -> str:
    text = re.sub(r"[^\w\s.-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "_", text.strip())
    text = re.sub(r"_+", "_", text).strip("._")
    return text[:max_len] or "certificate"
