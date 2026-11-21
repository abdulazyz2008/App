# Graph Report - App  (2026-11-21)

## Corpus Check
- 38 files · ~64,694 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 27 file(s) not represented in the graph (top: .ttf 18, (none) 3, .command 2)
- WARNING: 27 of 74 files seen (36%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 902 nodes · 2338 edges · 36 communities (33 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `32cb1400`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- data.py
- test_pipeline.py
- config.py
- templates_lib.py
- settings.py
- mailer.py
- gsheets.py
- one
- certificate.py
- crypto.py
- db.py
- pipeline.py
- get
- main.py
- AI Automation Agency
- json
- html
- Skills catalog
- Feature list
- time
- services
- with
- SendEZ
- post
- steps
- scheduler_tick
- SendEZ: features added beyond the original instructions
- publish
- build
- desktop.yml
- include
- release
- lifespan
- CLAUDE.md
- start-linux.sh
- start-online-linux.sh

## God Nodes (most connected - your core abstractions)
1. `get()` - 42 edges
2. `query()` - 29 edges
3. `one()` - 29 edges
4. `login()` - 29 edges
5. `send()` - 28 edges
6. `get_batch_or_404()` - 25 edges
7. `get_batch()` - 24 edges
8. `log()` - 23 edges
9. `upload()` - 22 edges
10. `record_values()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `next_day()` --calls--> `tx()`  [EXTRACTED]
  tests/test_pipeline.py → sealsend/db.py
- `start_tunnel()` --uses--> `TunnelError`  [INFERRED]
  run.py → sealsend/tunnel.py
- `ensure_password()` --calls--> `admin_configured()`  [EXTRACTED]
  run.py → sealsend/settings.py
- `ensure_password()` --calls--> `set_admin_password()`  [EXTRACTED]
  run.py → sealsend/settings.py
- `test_all_builtin_templates_render_deterministically_with_proof()` --calls--> `read_proof()`  [EXTRACTED]
  tests/test_pipeline.py → sealsend/certificate.py

## Import Cycles
- 2-file cycle: `sealsend/config.py -> sealsend/settings.py -> sealsend/config.py`

## Communities (36 total, 3 thin omitted)

### Community 0 - "data.py"
Cohesion: 0.05
Nodes (48): branding_for(), column_profile(), count_matches(), _email_in(), evaluate(), matches(), parse_claude(), parse_local() (+40 more)

### Community 1 - "test_pipeline.py"
Cohesion: 0.07
Nodes (48): reset_keys(), reset_connection(), reset_cache(), audit(), by_row(), client(), _fake_smtp(), _gmail() (+40 more)

### Community 2 - "config.py"
Cohesion: 0.06
Nodes (24): _arg(), _free_port(), _healthy(), main(), _open_window(), main(), call(), send_and_wait() (+16 more)

### Community 3 - "templates_lib.py"
Cohesion: 0.06
Nodes (40): _clean_cell(), all_tokens(), _bg(), _color(), _corner_flourish(), d_arts(), d_corporate(), d_gold() (+32 more)

### Community 4 - "settings.py"
Cohesion: 0.08
Nodes (40): set_logo(), app_url(), hosted_url(), is_temporary_url(), mail_mode(), public_base_url(), check_connection(), sender_identity() (+32 more)

### Community 5 - "mailer.py"
Cohesion: 0.09
Nodes (13): AuthFailure, build_message(), _classify_smtp(), connect_smtp(), PermanentFailure, QuotaFailure, Sender, TransientFailure (+5 more)

### Community 6 - "gsheets.py"
Cohesion: 0.08
Nodes (19): answer_claude(), answer_offline(), ask(), _fix_typos(), match(), _norm(), _tailor(), download() (+11 more)

### Community 7 - "one"
Cohesion: 0.11
Nodes (35): delete_template(), create(), get_batch(), one(), query(), save_config(), status_counts(), batch_detail() (+27 more)

### Community 8 - "certificate.py"
Cohesion: 0.07
Nodes (22): forge_copy(), pdf_to_png(), proof_keywords(), render_job(), render_pdf(), resolve(), sample_values(), thumbnail() (+14 more)

### Community 9 - "crypto.py"
Cohesion: 0.10
Nodes (22): sha256(), canonical(), fingerprint(), leaf_hash(), _lock_secret(), mapping_lock(), merkle_proof(), merkle_root() (+14 more)

### Community 10 - "db.py"
Cohesion: 0.12
Nodes (22): import_template(), conn(), get_record(), log(), _migrate(), now(), tx(), update_record() (+14 more)

### Community 11 - "pipeline.py"
Cohesion: 0.12
Nodes (25): placeholders_in(), render(), required_in(), safe_filename(), record_data(), get_record_or_404(), preview_certificate(), preview_email() (+17 more)

### Community 12 - "get"
Cohesion: 0.09
Nodes (27): catalog(), public_pem(), batch_feedback_csv(), branding_image(), certificates_zip(), chaos_forged(), claim_url(), club_report() (+19 more)

### Community 13 - "main.py"
Cohesion: 0.15
Nodes (15): AskIn, category_counts(), CategoryIn, ConfigIn, CopilotIn, OrgIn, PasswordIn, _rows() (+7 more)

### Community 14 - "AI Automation Agency"
Cohesion: 0.10
Nodes (19): D-001: Keep project memory in a dedicated Obsidian folder, D-00X: Short title, Decisions: AI Automation Agency, 2026-11-05, Progress: AI Automation Agency, YYYY-MM-DD, AI Automation Agency, File map (+11 more)

### Community 15 - "json"
Cohesion: 0.15
Nodes (12): read_proof(), update_template_fields(), audit_deliveries(), _events(), _outbox_for(), _rec(), _rows(), run() (+4 more)

### Community 16 - "html"
Cohesion: 0.19
Nodes (16): claim_download(), claim_page(), _claim_rec(), feedback_page(), _feedback_rec(), feedback_submit(), _footer(), page() (+8 more)

### Community 17 - "Skills catalog"
Cohesion: 0.10
Nodes (19): Advanced engineering (10), Browser & Python (6), Business growth (5), Engineering (8), Finance (6), Founder pack (11), Marketing (Corey Haines) (41), Marketing (original pack) (26) (+11 more)

### Community 18 - "Feature list"
Cohesion: 0.11
Nodes (18): Certificates, Checking and fixing the data, Demo, Email, Every event (4 steps), Feature list, First time only, Good to know (+10 more)

### Community 19 - "time"
Cohesion: 0.21
Nodes (11): first_run_setup(), _is_local(), login(), Login, logout(), open_in_browser(), require_auth(), security_headers() (+3 more)

### Community 20 - "services"
Cohesion: 0.12
Nodes (16): mountPath, name, sizeGB, key, sync, value, services, autoDeployTrigger (+8 more)

### Community 21 - "with"
Cohesion: 0.13
Nodes (15): with, body, cache, cache-dependency-path, files, if-no-files-found, make_latest, merge-multiple (+7 more)

### Community 22 - "SendEZ"
Cohesion: 0.14
Nodes (13): Certificate designs, Download the app (Mac or Windows, nothing else to install), Files, First-time setup (2 minutes), Free public link without the app (no account, no card), Handling the messy cases, Issue certificates: 4 steps, Or run it from the source code (advanced) (+5 more)

### Community 23 - "post"
Cohesion: 0.28
Nodes (10): create_batch(), create_batch_from_sheet_link(), import_template(), _read_upload(), share_start(), share_status(), _share_status(), share_stop() (+2 more)

### Community 24 - "steps"
Cohesion: 0.29
Nodes (11): steps, PUBLISH, steps, env, id, if, name, run (+3 more)

### Community 25 - "scheduler_tick"
Cohesion: 0.33
Nodes (7): set_batch(), _parse_ts(), quota_reset_at(), run_job(), worker(), scheduler_tick(), _ts()

### Community 26 - "SendEZ: features added beyond the original instructions"
Cohesion: 0.20
Nodes (9): 1. Trust and proof (certificates that can't be faked), 2. Handling messy spreadsheets, 3. Certificates and design, 4. Mahindra University clubs, 5. Email and sending, 6. For students, 7. Ease of use and access, 8. Records (+1 more)

### Community 27 - "publish"
Cohesion: 0.22
Nodes (9): publish, on, push, workflow_dispatch, default, description, required, tags (+1 more)

### Community 28 - "build"
Cohesion: 0.25
Nodes (8): needs, runs-on, timeout-minutes, jobs, build, test, runs-on, timeout-minutes

### Community 29 - "desktop.yml"
Cohesion: 0.29
Nodes (6): concurrency, cancel-in-progress, group, name, permissions, contents

### Community 30 - "include"
Cohesion: 0.29
Nodes (7): strategy, exe, name, os, include, fail-fast, matrix

### Community 31 - "release"
Cohesion: 0.33
Nodes (6): HAS_PUBLIC_TOKEN, release, env, if, needs, runs-on

### Community 32 - "lifespan"
Cohesion: 0.33
Nodes (6): set_awake(), lifespan(), start_scheduler(), loop(), stop_scheduler(), _wants_awake()

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `send()` connect `db.py` to `settings.py`, `mailer.py`, `one`, `pipeline.py`, `json`, `scheduler_tick`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Should `data.py` be split into smaller, more focused modules?**
  _Cohesion score 0.052982456140350874 - nodes in this community are weakly interconnected._
- **Should `test_pipeline.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0715372907153729 - nodes in this community are weakly interconnected._
- **Should `config.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._
- **Should `templates_lib.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06284153005464481 - nodes in this community are weakly interconnected._
- **Should `settings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08315863032844165 - nodes in this community are weakly interconnected._
- **Should `mailer.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08536585365853659 - nodes in this community are weakly interconnected._