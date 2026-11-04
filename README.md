# SealSend

> Others automate certificates. SealSend makes them **impossible to get wrong** and **impossible to fake**.

Upload a student Excel/CSV once. SealSend validates it, maps the columns, applies plain-English design rules, then generates, signs and seals one PDF per student. Before every send it checks that the attachment really belongs to that student, then delivers it with self-healing retries and logs every step.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env          # set ADMIN_PASSWORD
python -m uvicorn sealsend.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 and sign in. Then try:

1. **Use the sample sheet** for the normal flow: Data → Map → Design → Preview → Send → Proof.
2. **⚡ Run Chaos Test** for the demo. It injects 15 faults into a sandbox batch and shows how each one was contained.

With no `SMTP_*` or `RESEND_API_KEY` set, SealSend runs in **sandbox mode**: every email (with its attachment) is saved as an `.eml` file in `data/outbox/`. Chaos batches always use the sandbox.

## What's built (mapped to the plan)

| Plan item | Where | How it works |
|---|---|---|
| **1. Core flow** | `pipeline.py`, `data.py` | CSV/XLSX → validation → column mapping → template → individual PDFs → personalized emails → status ledger + retry |
| **2. Mapping Lock** | `crypto.mapping_lock`, `pipeline.check_attachment` | A keyed HMAC of (student ID + email + event + certificate ID) is embedded in each PDF. Right before sending it is recomputed from the recipient's record. The file hash, embedded ID and Ed25519 signature are also checked. A wrong file is **blocked**, regenerated from source and re-verified. |
| **3. Signed certificates + QR** | `crypto.py`, `/verify/{id}` | Each certificate's data plus its PDF SHA-256 is signed with Ed25519. The QR opens a public page: "Verified, issued to X for Y". Uploading a PDF that was edited (even one character) shows "This file has been altered". Fake IDs show "Not verified". The public key is at `/.well-known/sealsend-public-key.pem`. |
| **4. Batch seal** | `pipeline.seal_batch`, `verify_batch` | A SHA-256 Merkle tree over every certificate (ID, file hash, lock), with the root signed. "Verify Batch Now" re-hashes every file on disk, and the verify page shows each certificate's inclusion proof. The ZIP export includes `SEAL.json`. |
| **5. AI rules copilot** | `copilot.py` | "winners get gold template, others participation" → ordered rules (column condition → design + email preset), shown with match counts and applied only on approval. Uses Claude (`claude-opus-5-5`, structured JSON output, server-side refusal fallback) when `ANTHROPIC_API_KEY` is set, and otherwise an offline parser, so the demo never depends on Wi-Fi. |
| **6. Self-healing delivery** | `data.pick_email`, `pipeline._deliver` | Typo fix (`gmial.com → gmail.com`, `.con → .edu` when the sheet's domain is `.edu`, `(at)` → `@`), fallback email, retry with backoff for 4xx errors, a 550 bounce re-binding to the fallback address (with a fresh lock), and **claim links** (a private download link checked against the student ID, locked after 5 wrong tries) for students with no usable email. |
| **Chaos Test** | `chaos.py` | Junk names (`#REF!`, `J0hn`, blank), a duplicate, typo/broken/missing emails, two PDFs swapped on disk, a name edited inside a signed PDF, a stalling mail server, a bouncing mailbox, a double-clicked Send and a forged copy sent to the verifier. Results are computed from the database and by **opening every delivered `.eml`**, not from what the pipeline reports. |

## Hackathon rulebook coverage

| Rule | Status |
|---|---|
| 1 Excel/CSV input | ✓ `.xlsx`/`.csv`, delimiter and encoding detection, Excel dates and numeric IDs normalized |
| 2 Dynamic field mapping | ✓ Any `{{PLACEHOLDER}}` mapped to a column or a fixed value |
| 3 Individual generation | ✓ One PDF per valid student, generated in parallel |
| 4 Template-based | ✓ 4 built-in themes or uploaded PNG/JPG artwork, positioned text fields, auto-shrink for long names |
| 5 Personalized email | ✓ Default, winner and thank-you emails, selectable per rule |
| **6 Correct mapping** | ✓ Mapping Lock + hash + signature checked before every send. Proven by the Chaos Test and the tests. |
| 7 Email selection | ✓ Preferred column + fallback column |
| 8 Validation | ✓ Missing/junk names, invalid/missing emails, duplicates, empty required fields, with row numbers |
| 9 Preview | ✓ Every student's certificate (PNG) and exact email |
| 10 Bulk | ✓ Parallel rendering (~2,000 certificates in ~18 s on 4 cores), one reused SMTP connection, background jobs |
| 11 Status tracking | ✓ Pending · Generated · Sending · Sent · Failed, plus Claim · Claimed · Skipped · Invalid |
| 12 Failure handling | ✓ Per-record isolation, retries, Retry Failed, recovery after a restart |
| 13 Duplicate prevention | ✓ Send log across batches; organizer-authorized Resend |
| 14 File naming | ✓ `{{ID}}_{{NAME}}_{{EVENT}}.pdf`, configurable |
| 15 Security | ✓ Login, HttpOnly SameSite cookie, login rate limit, secrets only in `.env`, key file `0600`, size/type-checked uploads, explicit send confirmation |

## Live demo script (about 3 minutes)

1. **Upload** the sample sheet. Point at the blocked rows (missing name, duplicate) and the self-healed ones (fallback email, claim link).
2. **Design → copilot**: type "winners get gold template, others participation" → Apply → Preview shows the gold certificate and the winner email.
3. **Send**, then show the live activity feed. **Proof → Verify Batch Now** shows the batch is intact.
4. **⚡ Run Chaos Test**: 15/15 contained, 0 wrong attachments, batch finished.
5. A judge **scans the QR** on a certificate: "Verified, issued to Aisha Rahman for First Place".
6. **Download the forged PDF** from the Chaos Report and upload it to the verifier: "This file has been altered".

For step 5, run the server on your LAN (`--host 0.0.0.0`) and set `PUBLIC_BASE_URL=http://<laptop-ip>:8000` **before** generating, so the QR points to a reachable address.

## Tests

```bash
python -m pytest -q
```

There are 18 tests. They cover: Merkle proofs and signatures, typo and name rules, deterministic rendering, the full flow with an audit of every delivered email, claim links, swapped and tampered files being blocked and healed, database tampering, transient failure and retry, SMTP connection reuse and bounce → fallback, the Resend request format, the copilot (offline, Claude, and fallback when Claude fails), the full Chaos Test, XLSX input, and a 120-student parallel batch.

## Layout

```
sealsend/
  main.py         API, auth, public /verify and /claim pages
  pipeline.py     validate → generate+sign → seal → verify-or-heal → deliver
  crypto.py       Ed25519 keys, Mapping Lock, Merkle tree
  data.py         spreadsheet loading, mapping, validation, email self-healing
  certificate.py  themes, PDF rendering, QR, embedded proof, forgery demo
  mailer.py       sandbox / SMTP / Resend, email presets
  copilot.py      plain-English rules (Claude + offline parser)
  chaos.py        Chaos Test
  static/index.html  black-and-white, iOS-style organizer UI
```
