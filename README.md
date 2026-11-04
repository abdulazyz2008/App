# Certify: Certificate Automation

> Upload once, generate automatically, and send every student their personalized certificate, without manually editing a single certificate or email.

Certify turns an Excel/CSV of students into individual PDF certificates and emails each student **their own** certificate, with validation, previews, status tracking, retries and duplicate protection.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env            # set ADMIN_PASSWORD (and SMTP_* to send real email)
python -m uvicorn certify.main:app --port 8000
```

Open http://localhost:8000, sign in, then click **"Use the sample sheet"** to try the full flow with `sample/students.csv`.

Without `SMTP_HOST` the app runs in **outbox mode**: every email (with its attachment) is written to `data/outbox/*.eml` so you can demo safely and open the files in any mail client. Fill in the SMTP settings to deliver for real (Gmail, Outlook/Office 365, SendGrid SMTP, etc.).

## Workflow

| Step | What happens |
|---|---|
| 1. Upload | `.xlsx` / `.csv`. Excel dates and numeric IDs are normalized, blank rows dropped. |
| 2. Map | Columns are auto-matched to placeholders (`{{NAME}}`, `{{ID}}`, `{{EVENT}}`, `{{CERT_TYPE}}`, `{{ACHIEVEMENT}}`, `{{DATE}}`, …). Any placeholder can also be a fixed text, e.g. the event name. Choose the preferred email column and a fallback. |
| 3. Validate | Missing names, missing/invalid emails, duplicate IDs, duplicate name+email, and empty required fields are flagged with the spreadsheet row number. Invalid rows are never sent. |
| 4. Template & email | Built-in design, or upload your own artwork (PNG/JPG) and position text fields. Subject/body/file names use the same placeholders. |
| 5. Preview | Step through real students and see their certificate and exact email before sending. |
| 6. Generate & send | One PDF per student (generated in parallel), one email per student with only that PDF attached. |
| 7. Track | Pending → Generated → Sending → Sent / Failed / Skipped, with retry, per-student resend, CSV report and ZIP of certificates. |

## How the rulebook is covered

| Rule | Implementation |
|---|---|
| 1 Excel/CSV input | `certify/data.py:load_table` (CSV encodings/delimiters auto-detected, XLSX via openpyxl) |
| 2 Dynamic mapping | Column or fixed-text mapping for every `{{PLACEHOLDER}}` found in template, email and file name |
| 3–4 Template generation | `certify/certificate.py` renders each record; long names auto-shrink to fit |
| 5 Personalized email | Subject + body templates, plain text and HTML parts |
| **6 Correct mapping** | Certificate and email are built from the same DB record. Before attaching, the PDF's SHA-256 must match the one recorded at generation **and** the record code embedded in the PDF metadata must match the recipient's record. A swapped/tampered file is blocked (see `test_tampered_certificate_is_never_attached`). |
| 7 Email selection | Preferred column + fallback column (used when preferred is missing/invalid, flagged as a warning) |
| 8 Validation | Missing/invalid/duplicate checks with row numbers |
| 9 Preview | PNG/PDF certificate preview and the exact email, per student |
| 10 Bulk | Parallel rendering (~2,000 certificates in ~18 s on 4 cores), one reused SMTP connection, background jobs with live progress |
| 11 Status | Per-record status, attempts, timestamps, errors |
| 12 Failure handling | Each record is isolated; transient SMTP errors retry with backoff; "Retry failed" button; interrupted sends recovered on restart |
| 13 Duplicates | Send log keyed by student + event + type: re-sending (even from a re-uploaded sheet) is skipped unless an organizer explicitly clicks **Resend** |
| 14 File naming | Configurable, default `{{ID}}_{{NAME}}_{{EVENT}}.pdf` → `STU001_Aisha_Rahman_AI_Hackathon_2026.pdf` |
| 15 Security | Login required for everything except the verify page; HttpOnly SameSite cookie; login rate-limit; secrets only from `.env`; uploads size/type-checked and stored under random names; explicit confirmation before sending |

**Extra:** every certificate has a unique ID and a QR code linking to `/verify/<ID>`, a public page that confirms it is genuine.

## Tests

```bash
python -m pytest -q
```

The tests cover validation, the full send flow (every outbox email is checked to have the right recipient, name, and attachment), duplicate prevention across batches, failure isolation and retry, tamper detection, XLSX input, and SMTP connection reuse.

## Project layout

```
certify/
  main.py         FastAPI routes + auth + verify page
  pipeline.py     batch → validate → generate → send → status
  data.py         spreadsheet loading, mapping, validation
  certificate.py  PDF rendering (ReportLab), QR, integrity helpers
  mailer.py       email building, SMTP / outbox delivery
  static/index.html  single-page UI
sample/students.csv  demo data (includes deliberately broken rows)
tests/
```
