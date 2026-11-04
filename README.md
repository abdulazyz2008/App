# SealSend

> Upload your student list once. Every student gets their own congratulatory email with the right certificate attached, and every certificate can be verified as genuine.

SealSend reads any reasonable Excel or CSV file, works out who each student is and which category they belong to, picks the right certificate design for each category, and emails each student their own digitally signed PDF from your Gmail account. Before each email goes out, it checks that the attachment really belongs to that student.

---

## Start it

**You need Python 3.10 or newer** (free from [python.org](https://www.python.org/downloads/); on Windows tick *“Add Python to PATH”* during install).

| Computer | Do this |
|---|---|
| **Windows** | Double-click `start-windows.bat` |
| **Mac** | Double-click `start-mac.command` (first time: right-click → Open) |
| **Linux** | Run `./start-linux.sh` |

The first start takes 1–3 minutes to set itself up (needs internet once). Then your browser opens SealSend. Keep the black window open while you use it.

**iPhone, iPad, Android:** connect to the same Wi-Fi as the computer, then in SealSend tap **Open on phone/iPad** and scan the QR code. Use *Share → Add to Home Screen* to install it like an app.

## First-time setup (2 minutes)

1. **Create a password** (only possible on the computer running SealSend).
2. **Connect Gmail:** Settings → Gmail → your address + a **Gmail App Password**:
   - turn on [2-Step Verification](https://myaccount.google.com/signinoptions/twosv), then open [App passwords](https://myaccount.google.com/apppasswords), type “SealSend”, and copy the 16 letters.
   - Your normal Gmail password will **not** work; Google requires an App Password.
3. Press **Save & Test**, then **Send test** to your own address. If the test arrives with its sample certificate, you’re ready.

Until Gmail is connected, SealSend runs in **test mode**: emails and certificates are saved in `data/outbox/` instead of being sent.

## Issue certificates: 4 steps

| Step | What happens |
|---|---|
| **1 · Students** | Upload the Excel/CSV. SealSend finds the right sheet, skips title rows, and detects the name (even split across *First Name* / *Last Name*), email, backup email, ID, date and **category** columns. You can correct any of them. Problem rows are flagged with their row number. |
| **2 · Certificates** | Each category value (e.g. *Winner, Runner Up, Volunteer, Participant*) gets a design, a title and an email, guessed from its name: winners get **Gold Excellence** and a congratulations email, volunteers get *Certificate of Appreciation*, and so on. Click any design to choose another, add your organization name, logo and signatories. |
| **3 · Email** | Check the sending account and edit the default message if you like. Each category already has a ready-written email (winner, participation, appreciation, completion). |
| **4 · Review & Send** | A checklist, then a preview of exactly what any student will receive (certificate + email). Press **Send**. Progress, a live activity log, a CSV delivery report and a ZIP of all certificates are on the same page. |

## Certificate designs

14 original designs, made for this app, so there are no licensing issues:

| Niche | Design |
|---|---|
| Academic | University Classic |
| Competitions & Awards | Gold Excellence |
| Technology | Tech Hackathon |
| Corporate & Training | Corporate Modern |
| Schools | School Stars |
| Sports | Sports Champion |
| Healthcare | Medical & CME |
| NGO & Community | Volunteer Appreciation |
| Workshops & Seminars | Workshop Minimal |
| Arts & Culture | Arts & Culture |
| Government & Institutions | Official Formal |
| Internships | Internship |
| General | Participation, Mono Minimal |

**Your own design from Canva:** Templates → *Import from Canva*. Design or pick a certificate in your Canva account, delete the sample name, then download it as **PDF Standard** or PNG and drop it in. Drag the name, description and QR code to where they belong, then press Save. Canva’s own template library can’t be bundled into another app (their license forbids it), but anything you export from your account works.

## Handling the messy cases

| Problem in the sheet | What SealSend does |
|---|---|
| Title rows above the header, several sheets, a “Total” row | Finds the real header and the sheet that has emails; skips the footer |
| `name@gmial.com`, `.con`, spaces, `name(at)college` | Fixes it and shows what it changed |
| Broken main email, valid personal email | Uses the backup column |
| No email at all | Creates a private **claim link** (the student confirms their ID to download) |
| `#REF!`, `N/A`, digits in a name, blank name | Blocks that row and shows why |
| Same student twice | Blocks the duplicate (by ID, or by name + email) |
| ALL CAPS names | Optional switch: *ROHAN MEHTA → Rohan Mehta* |
| Gmail daily limit (~500/day) | Stops safely at your limit; press Send again the next day and it continues with the rest. Nobody gets two emails. |
| Wrong App Password | Refuses to start and tells you exactly what to fix, without marking anyone as failed |
| Network blocks port 587 | Falls back to port 465 automatically |
| A mailbox bounces | Retries with the student’s backup email |
| Send pressed twice / sheet uploaded again | Already-delivered students are skipped |

## Why it can be trusted

- **Mapping Lock:** each PDF carries a hidden keyed hash of *student ID + email + event*. Right before sending, it is recomputed from the recipient, together with the file’s hash and signature. A wrong attachment is blocked, rebuilt from the source data, and checked again.
- **Signed certificates + QR:** every certificate is signed (Ed25519). Scanning the QR opens *“Verified, issued to X for Y”*. Uploading an edited PDF at `/verify` shows *“This file has been altered”*.
- **Batch seal:** a signed Merkle root covers the whole batch. *Proof → Verify Batch Now* re-checks every file.
- **Chaos Test** (sidebar, demo): injects 15 real faults into a sandbox batch and shows each one being contained. Results come from opening every delivered email, not from what the app says about itself.

**About the QR link:** QR codes open the address in *Settings → Verification link*. By default that is your computer on the local Wi-Fi, which is fine for a demo. For certificates students will show to employers later, host SealSend online (any server that runs Python) and enter its public address **before** creating certificates.

## Tests

```bash
pip install -r requirements.txt
python -m pytest -q
```

26 tests cover the messy Excel reader, the email and name rules, all 14 designs, Canva import and the field editor, branding, the full send flow (with an audit of every delivered email), claim links, swapped and tampered files, database tampering, Gmail login failure, the port 465 fallback, the daily limit with pause and resume, provider quota errors, bounces with a switch to the backup email, retries, Resend, the copilot (offline and Claude), the full Chaos Test, and a 120-student parallel batch.

`sample/tech_fest_2026.xlsx` is a deliberately messy workbook for trying everything.

## Files

```
run.py, start-*.{bat,command,sh}   one-click start on Windows / macOS / Linux
sealsend/
  data.py           spreadsheet reading, column + category detection, validation, email self-healing
  templates_lib.py  the 14 designs, fonts, text layout, imported (Canva) templates
  certificate.py    rendering, previews, imports, proof metadata
  pipeline.py       generate → sign → seal → verify-or-heal → deliver, daily limit, pause/resume
  mailer.py         Gmail / Outlook / SMTP / Resend / test mode, email wording per category
  settings.py       in-app settings (App Password encrypted at rest), admin password
  crypto.py         Ed25519, Mapping Lock, Merkle seal
  copilot.py        plain-English rules (Claude or offline)
  chaos.py          Chaos Test
  main.py           web server, public /verify and /claim pages
  static/           the app (black-and-white, iOS-style, works on phones)
  fonts/            bundled open-licensed fonts (SIL OFL), so certificates look identical everywhere
```
