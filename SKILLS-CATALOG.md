# Skills catalog

343 skills installed in `.claude/skills`. Type `/name` to use one, or just describe the task and Claude picks the skill.


## Founder pack (start a business) (11)

| Skill | What it's for |
|---|---|
| `/founder-board` | Your board of directors. Puts a business idea in front of a three-member board, each a sub-agent reading the idea through one published framework: the Offers lens (from Alex Hormozi's $100M Offers), the Monopoly lens… |
| `/founder-brand` | Your brand designer. Names the business (with the trademark, domain and handle checks to run before falling in love with a name), writes the voice, a one-line promise and a tagline, and briefs the look: colours, type… |
| `/founder-cfo` | Your CFO. Builds the unit economics of a business before money is spent: what one unit earns after its direct costs, the real profit margin at the planned volume, the break-even point in units a day, year 1 month by… |
| `/founder-competitors` | Maps every competitor and the gap they leave. |
| `/founder-consumer` | The consumer panel. Spins up a swarm of buyer sub-agents (default 100, --quick for 20) trained on the user's target customer, each with a different income, age, buying behaviour and objection, shows every one the same… |
| `/founder-launch` | Your launch lead. Builds a dated, step-by-step launch plan: a cheap real-world test first (a waitlist, a pre-sale or a pop-up with a real price, so real buyers confirm what the simulated panel said), then the countdown… |
| `/founder-marketing` | Your marketing director. Turns the buyer panel and the competitor map into positioning, the channels the target customer actually uses, a 30-day launch campaign with dated posts and ads, the first ten hooks, a budget… |
| `/founder-offer` | Builds an offer too good to refuse. Lists every problem the buyer hits on the way to the result they want, turns each into a solution, trims to what is cheap to deliver and valuable to the buyer, and stacks it with… |
| `/founder-ops` | Your operations manager. Works out how the business actually runs on day one: suppliers and what they cost, who works when, the step-by-step routines for opening, serving or shipping and closing, the tools to run it… |
| `/founder-plan` | Your business planner. Compiles everything the other founder skills wrote (the board's verdict, the competitors, the buyer panel, pricing, the offer, the CFO's numbers, marketing, brand, operations and the launch plan)… |
| `/founder-pricing` | Finds the price buyers will actually pay. |

## Replica pack (clone & improve an app) (11)

| Skill | What it's for |
|---|---|
| `/replica-architect` | Plans the stack, database schema and API for an app clone, from the recon map replica-recon wrote. |
| `/replica-backend` | Builds the backend of an app clone: auth, database migrations and access rules, payments with Stripe, email, background jobs and third-party integrations through official APIs only, plus a security checklist. |
| `/replica-brand` | Names and rebrands an app clone so it is the user's own: name candidates with the trademark, domain, store and handle checks to run, a new palette checked for contrast, a logo brief, a voice guide, and a sweep tool that… |
| `/replica-build` | Rebuilds an app screen by screen from the recon map: app shell first, then the core flow as a vertical slice, then every screen with all its states, ticking off the feature matrix as it goes. |
| `/replica-deploy` | Ships an app clone live on the user's own domain: a preflight gate (tests green, parity must-haves done, rebrand sweep clean, listing linted, legal pages up), production database and env vars, the host, DNS records for… |
| `/replica-design` | Rebuilds an app's design system for a clone: colour roles, type scale, spacing, radius, shadows and every component with its states, as design tokens plus component specs, with original assets instead of the target's… |
| `/replica-diff` | Compares an app clone against the original: a feature parity score from the feature matrix (weighted by must, should, could) with the missing list in build order, plus a screenshot layout diff that ignores colour so a… |
| `/replica-entrepreneur` | Researches the app being cloned and reads what its real users say in public reviews (App Store, Google Play, G2, Capterra, Trustpilot, Reddit, Hacker News, its own feature-request board), then ranks what they hate, what… |
| `/replica-launch` | Writes the launch for an app clone: the landing page built on the positioning angle, pricing set against the original's public pricing and its users' complaints, and the App Store and Google Play listing linted against… |
| `/replica-recon` | Reverse-engineers any app into a recon map: screen inventory, user flows, component list, inferred data model and a feature matrix, from public pages, screenshots, app store listings, help docs and the user's own… |
| `/replica-test` | Clicks through every flow of an app clone and tests it for bugs: a test plan generated from the recon flows with happy paths and edge cases, Playwright end-to-end tests where possible, a browser click-through where not… |

## Trader pack (stocks) (11)

| Skill | What it's for |
|---|---|
| `/trader-alerts` | Price Alerts. Rings when a price target, a stop or the opening bell hits: above / below / stop rules, percent moves from the previous close, and the NYSE opening bell, each ringing once so you are not spammed. |
| `/trader-analyst` | The Earnings Analyst. Reads a company's reported numbers straight from SEC EDGAR (XBRL company facts from its 10-Qs and 10-Ks, plus the latest earnings 8-K and its press release) and sums up what changed: revenue… |
| `/trader-broker` | Order Executor. Places APPROVED orders through your brokerage connector, one at a time, and never without your explicit yes. |
| `/trader-budget` | Budget Manager. Sizes every position to your budget before anything is bought: keeps a cash buffer, caps any one stock (the excess is shared out to the others), drops slices under your minimum order, rounds so every… |
| `/trader-copycat` | The Reverse Engineer. Reads a famous investor's public SEC filings (the quarterly 13F-HR, plus Form 4 if you want the insider trades) and rebuilds their portfolio as weights you can copy: every position, its share of… |
| `/trader-news` | The News Monitor. Watches breaking market news and SEC filings for the stocks you hold (or are about to copy): Yahoo Finance headlines per ticker and each company's 8-K filings on SEC EDGAR (earnings, CEO changes… |
| `/trader-pelosi` | The Pelosi Tracker. Watches the stock trades members of Congress must disclose under the STOCK Act: reads the House Clerk's public Periodic Transaction Reports (PTRs) as soon as they are posted, alerts once per new… |
| `/trader-rebalance` | Rebalancer. Brings the portfolio back to its target weights when it drifts: values every holding at current prices, works out each stock's drift from its target in percentage points, trades only the stocks outside a… |
| `/trader-risk` | Risk Manager. Checks every proposed order against your limits before it can reach the broker and blocks anything over them: blocked tickers, max order size, minimum order, max position percent after the fill, the cash… |
| `/trader-screener` | The Stock Screener. Checks a list of companies against the user's own rules (revenue growth, margins, EPS, P/E, earnings yield, sector, anything in the metrics file), says exactly which rule each company passes or fails… |
| `/trader-tax` | Tax Optimizer. Tracks cost-basis lots for every position (FIFO, highest cost first, or specific lots), shows unrealized gains and losses by lot with short or long term, works out what a sale would realize before you… |

## Whale pack (pre-sell to customers) (11)

| Skill | What it's for |
|---|---|
| `/case-study` | Case Study. Turns the first customer into proof, with their permission. |
| `/demo-builder` | Demo Builder. Builds a demo showing how your product solves the problem, before the product exists. |
| `/follow-up` | Follow-Up. Keeps the deal moving. |
| `/launch-planner` | Launch Planner. Plans the launch once it is paid for. |
| `/market-researcher` | Market Researcher. Finds problems businesses already pay thousands to solve. |
| `/objection-handler` | Objection Handler. Answers every objection, and knows a no when it hears one. |
| `/offer-builder` | Offer Builder. Writes the offer they can say yes to. |
| `/pre-sale` | Pre-Sale. Gets customers to pay up front, and uses what they ask for to build the exact product. |
| `/pricing` | Pricing. Sets the price from what they pay today. |
| `/requirements` | Requirements. Turns what paying customers asked for into the build list. |
| `/whale-hunter` | Whale Hunter. Finds the decision makers and pitches them. |

## Research (1)

| Skill | What it's for |
|---|---|
| `/last30days` | Research what people actually say about any topic in the last 30 days. |

## Browser & Python (ECC) (6)

| Skill | What it's for |
|---|---|
| `/agent-browser` | Browser automation CLI for AI agents. Use when the user needs to interact with websites, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating… |
| `/api-design` | REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production APIs. |
| `/fastapi-patterns` | FastAPI best practices covering project structure, Pydantic v2 schemas, dependency injection, async handlers, authentication, authorization, transactional service layers, and testing with httpx and pytest. |
| `/python-patterns` | Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications. |
| `/python-testing` | Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements. |
| `/verification-loop` | Run a six-phase verification of a Claude Code session's work — build, type check, lint, tests with coverage, security grep, and diff review — then produce a PASS/FAIL verification report. |

## Claude-skills: Advanced engineering (49)

| Skill | What it's for |
|---|---|
| `/agent-designer` | Design multi-agent systems (supervisor, swarm, pipeline) and tool schemas; find bottlenecks in run logs. |
| `/agent-regression-evals` | Use before shipping any agent, prompt, model or tool change, or when a pass-rate drop needs a verdict. |
| `/agent-run-forensics` | Use when asked why an agent did something, what a past session or run changed, whether tests really passed, or to verify a session summary. |
| `/agent-workflow-designer` | Use when architecting a multi-step LLM or agent pipeline, choosing single vs multi-agent, or fixing context bloat and broken handoffs. |
| `/api-design-reviewer` | Use for any PR or spec that adds or changes REST endpoints, before approving it. |
| `/api-test-suite-builder` | Use when asked to write API, integration or contract tests for REST endpoints. |
| `/boost-asio-pro` | Use for any C++ networking code with Boost.Asio or standalone Asio (TCP/UDP, SSL, timers, strands, io_context, co_spawn, awaitable, completion handlers), before writing or reviewing it. |
| `/browser-automation` | Automate a browser: scrape websites, fill forms, pull structured data from web pages. |
| `/changelog-generator` | Write release notes and CHANGELOG.md from commits and pick the next semver version. |
| `/chaos-engineering` | Use before running a chaos experiment, gameday or fault injection, or after one to write it up. |
| `/ci-cd-pipeline-builder` | Generate a CI/CD workflow for a repo from its detected stack: lint, test, build, deploy. |
| `/codebase-onboarding` | Explain an unfamiliar repo: architecture brief and onboarding docs. |
| `/coding-agent-rollout` | Roll out Claude Code to a team: shared or managed settings, MCP and plugin approval, layered CLAUDE.md, adoption. |
| `/commit-craft` | Turn a mix of changes into clean, reviewable commits with good messages, blocking staged secrets and .env files. |
| `/database-designer` | Design a database schema: tables, relationships, indexes, normalization, SQL vs NoSQL, migration plans. |
| `/database-schema-designer` | Use when asked for an ERD, table relationships, normalization or a schema migration plan. |
| `/dependency-auditor` | Audit project dependencies for CVEs and licenses and plan safe upgrades. |
| `/engineering-advanced-skills` | Pick the right advanced engineering skill: agents, RAG, MCP, CI/CD, databases, observability, release. |
| `/env-secrets-manager` | Use when auditing .env files, planning credential rotation, chasing a missing env var in production or hardening a repo against leaked secrets. |
| `/feature-flags-architect` | Use before adding, rolling out or retiring a feature flag or kill switch, or when flag debt piles up. |
| `/focused-fix` | Use when a whole feature or module is broken and needs fixing end to end ('make X work', 'the Y module is broken'). |
| `/full-page-screenshot` | Use when asked for a full-page or long screenshot of a web page. |
| `/git-worktree-manager` | Use when running several branches or agents in parallel on one repo. |
| `/grill-me` | Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. |
| `/i18n-localization` | Use when adding UI text, adding or shipping a language, reviewing translation files, or building i18n into an app. |
| `/interview-system-designer` | Use when designing a hiring loop, competency matrix, scoring rubric or question bank, or checking interviewer calibration. |
| `/karpathy-coder` | Check a diff for overbuilt code: hidden assumptions, needless abstraction, non-surgical changes, unverified goals (Karpathy's four principles). |
| `/kubernetes-operator` | Use when building a Kubernetes operator or CRD (controller-runtime, kubebuilder, operator-sdk, KOPF), before writing the controller. |
| `/mcp-oauth-triage` | Use when an MCP connector that used to authenticate now fails (tool calls 401 after a good token exchange, breaks after refresh, returns another account's data), before changing code. |
| `/mcp-server-builder` | Use when exposing an API as an MCP server or scaffolding a new MCP server in Python or TypeScript, before hand-writing tool wrappers. |
| `/migration-architect` | Plan a migration with zero or minimal downtime: phased plan, compatibility check, rollback scripts, for schemas, databases and services. |
| `/minimalist` | Write the least code: no over-engineering, fewer dependencies. |
| `/monorepo-navigator` | Use for Turborepo, Nx, pnpm-workspace or Lerna setup, affected-only builds, remote caching or a multi-repo to monorepo move. |
| `/observability-designer` | Use when adding metrics, logs and traces to a service, fixing noisy alerts or designing dashboards. |
| `/performance-profiler` | Use for a slow endpoint, memory leak, CPU spike, large bundle or performance budget in Node.js, Python or Go, before optimizing. |
| `/pr-review-expert` | File-by-file pull request review for bugs, security and quality, with a merge verdict. |
| `/rag-architect` | Design a RAG pipeline: chunk size, embedding model, vector database and retrieval quality metrics. |
| `/runbook-generator` | Use when a service needs runbooks for deploy, incident response, maintenance or rollback, before launch. |
| `/secrets-vault-manager` | Use when setting up HashiCorp Vault, AWS Secrets Manager, Azure Key Vault or GCP Secret Manager, rotating secrets or auditing secret access. |
| `/self-eval` | Grade finished work honestly on two axes with a devil's-advocate pass against inflation. |
| `/ship-gate` | Use before deploying or going live ('am I ready to ship', 'can I deploy', 'preflight check'). |
| `/skill-security-auditor` | Use before installing any skill or plugin from an untrusted source, or when asked if a skill is safe. |
| `/skill-tester` | Use when authoring or auditing a skill in this ecosystem, before release. |
| `/slo-architect` | Use when defining or reviewing SLOs, SLIs, error budgets or burn-rate alerts. |
| `/spec-driven-workflow` | Use when a feature should be specified before coding (acceptance criteria, spec-first, tests from specs). |
| `/sql-database-assistant` | Write, fix and speed up SQL: slow queries, EXPLAIN plans, indexes, ORM migrations (Prisma, Drizzle, SQLAlchemy). |
| `/strict-api` | Use when the user says 'no hallucinations', 'verify APIs' or 'don't invent functions', or code depends on a library version you have not checked. |
| `/tc-tracker` | Use when tracking technical changes as records, or handing work between AI sessions with a change record. |
| `/tech-debt-tracker` | Find, rank and track tech debt in a codebase. |

## Claude-skills: Business growth (5)

| Skill | What it's for |
|---|---|
| `/business-growth-skills` | Use when a growth request needs routing between customer-success-manager, sales-engineer, revenue-operations and contract-and-proposal-writer. |
| `/contract-and-proposal-writer` | Use when drafting a freelance contract, proposal, SOW, NDA or MSA for US, EU, UK or DACH jurisdictions. |
| `/customer-success-manager` | Use when reviewing customer accounts for health, churn risk or expansion. |
| `/revenue-operations` | Check sales pipeline and forecasts: pipeline coverage, forecast accuracy, magic number, CAC payback. |
| `/sales-engineer` | Use for pre-sales work: RFP coverage gaps, competitive feature matrices or planning and scoring a proof of concept. |

## Claude-skills: C-suite advisors (34)

| Skill | What it's for |
|---|---|
| `/founder-coach` | Use when a founder is the bottleneck, can't delegate, is burning out or is moving from IC to CEO. |
| `/agent-protocol` | Use when C-suite advisor agents need to call each other or run a multi-role meeting. |
| `/arquiteto-de-empresa` | Use when a founder wants to document or design a whole company as version-controlled markdown (company as code, a company wiki agents can read, an OKF bundle). |
| `/board-deck-builder` | Use when building a board deck, investor update or QBR from all C-suite perspectives. |
| `/board-meeting` | Use for /c-level-agents:boardroom or a strategic question that needs a structured multi-executive deliberation. |
| `/c-level-skills` | Find which C-level advisor fits a question: 14 C-suite roles, board meetings, culture, M&A. |
| `/ceo-advisor` | Advice for a CEO or founder on running the company: board and investor trouble, raise or cut, strategy bets, org and culture. |
| `/cfo-advisor` | Startup finance: runway and burn, unit economics (LTV, CAC, payback), fundraising and dilution. |
| `/change-management` | Use when rolling out a reorg, pivot, tool switch, leadership change or product kill. |
| `/chief-ai-officer-advisor` | Use for AI strategy decisions: API vs fine-tune vs build, EU AI Act or US state risk classification, when self-hosting pays off, or AI hiring order. |
| `/chief-customer-officer-advisor` | Use for retention strategy, customer segmentation or CS team sizing decisions (GRR vs NRR, churn causes, pooled vs named CSMs). |
| `/chief-data-officer-advisor` | Use for data strategy decisions: training models on customer data, warehouse vs lakehouse vs mesh, valuing data for a raise or M&A, or data hiring order. |
| `/chief-of-staff` | Use when a founder question needs routing to the right C-suite advisor, or a cross-functional decision needs a board meeting convened. |
| `/chro-advisor` | People strategy: hiring plans, comp bands, org structure, performance, retention. |
| `/ciso-advisor` | Use for security leadership decisions: a security program, budget justification in dollars, SOC 2 vs ISO 27001 vs HIPAA roadmap, or board security reporting. |
| `/cmo-advisor` | Marketing leadership: positioning, product-led vs sales-led vs community-led growth, budget split across channels, marketing team design. |
| `/company-os` | Use when choosing or setting up how the company runs: EOS, Scaling Up or OKRs, accountability chart, scorecard, meeting rhythm, quarterly rocks. |
| `/competitive-intel` | Use for competitor analysis, battlecards, win/loss review or positioning against alternatives. |
| `/context-engine` | Use when starting a C-suite advisor session, when company context is missing or older than 90 days, or before company data goes to an external service. |
| `/coo-advisor` | Use for operations leadership: process design, OKR execution, operating cadence, bottlenecks or scaling playbooks. |
| `/cpo-advisor` | Product leadership: PMF measurement, product vision, portfolio investment, product org design, board product reporting. |
| `/cro-advisor` | Use for B2B revenue leadership: forecasting, quotas, sales model, NRR and churn, pricing or sales capacity. |
| `/cs-onboard` | Use when setting up the C-suite advisors for the first time, or when company context is missing or stale after a raise or pivot. |
| `/cto-advisor` | CTO decisions: tech debt, architecture direction, scaling the engineering team, technology evaluation, DORA metrics. |
| `/culture-architect` | Use when defining company values, turning them into behaviors, assessing culture health or designing rituals. |
| `/decision-logger` | Use when logging a decision after a board meeting, reviewing past decisions or checking overdue actions. |
| `/general-counsel-advisor` | Legal review of contracts and term sheets (MSA, SaaS, NDA, DPA, employment), IP strategy and regulatory exposure (HIPAA, GDPR, FDA, fintech). |
| `/internal-narrative` | Use when preparing an all-hands, investor update, recruiting pitch or crisis message, or when stories told to different audiences drift apart. |
| `/intl-expansion` | Use when expanding to a new country: market selection, entry mode, localization, regulation and regional go-to-market. |
| `/ma-playbook` | Buy a company or sell yours: diligence, valuation, terms, integration. |
| `/org-health-diagnostic` | Use for a whole-company health check before a board review or when functions seem at risk. |
| `/scenario-war-room` | Use for compound what-if questions ('what if X and Y both happen?') with major downside across functions. |
| `/strategic-alignment` | Use when teams pull in different directions, OKRs don't connect or departments optimize locally. |
| `/vpe-advisor` | Use when delivery is slowing, eng hiring is broken, team structure is unclear or you need to decide when to add an eng manager. |

## Claude-skills: Engineering (35)

| Skill | What it's for |
|---|---|
| `/adversarial-reviewer` | Tough, critical review of a diff or PR before merge, through hostile reviewer personas that catch shared blind spots. |
| `/ai-security` | Use when assessing an AI/ML system or LLM agent for prompt injection, jailbreaks, model inversion, data poisoning or tool abuse. |
| `/aws-solution-architect` | Use when designing or costing an AWS architecture (serverless, Lambda, API Gateway, DynamoDB, ECS, Aurora, CloudFormation, migration to AWS). |
| `/azure-cloud-architect` | Use when designing or costing an Azure architecture (AKS, App Service, Functions, Cosmos DB, Bicep or ARM, Azure DevOps, migration to Azure). |
| `/cloud-security` | Use when checking AWS, Azure or GCP for security misconfigurations: IAM privilege escalation, public buckets, open security groups, IaC gaps. |
| `/code-reviewer` | Use for any code review: a pull request, a diff, a commit, or a pasted function, handler or file in TypeScript, JavaScript, Python, Go, Swift, Kotlin, C#/.NET, Java, C, C++, Rust, Ruby, PHP or Dart/Flutter. |
| `/email-template-builder` | Use when adding or reworking transactional email (React Email templates, Resend, Postmark, SendGrid or SES, preview, i18n, dark mode, deliverability). |
| `/embedded-iot-mentor` | Use for any embedded or IoT hardware project (ESP32, STM32, Arduino, Pico, firmware, PCB, MQTT, Home Assistant, sensor dashboards), before buying parts. |
| `/engineering-skills` | Find which engineering skill fits a task: architecture, frontend, backend, QA, DevOps, security, AI/ML, data, cloud. |
| `/epic-design` | Use for any landing page, hero section or scroll-driven web design that should feel cinematic (parallax, scrollytelling, overlapping sections, text reveals, Apple-style animation), before coding. |
| `/gcp-cloud-architect` | Design, deploy and cut the cost of Google Cloud setups: Cloud Run, GKE, Functions, Cloud SQL, BigQuery, moving to GCP. |
| `/incident-commander` | Use when declaring or running a production incident or outage, or writing its post-incident review. |
| `/incident-response` | Handle a suspected security breach: triage, SEV1-SEV4 severity, escalation and forensic evidence, per NIST SP 800-61. |
| `/ms365-tenant-manager` | Use for Microsoft 365 tenant administration (Entra ID users, Exchange Online, Teams, licenses, Conditional Access, compliance reports). |
| `/named-persona-adversarial-review` | Use when a PR has architectural or UX impact, or automated review feels generic, and you want it reviewed through named engineers' documented views (Torvalds, Thompson, Carmack, Beck, Jobs, Cagan). |
| `/red-green-proof` | Turns a suspected bug into a proven one. |
| `/red-team` | Use when planning or running an authorized red team engagement or attack path analysis. |
| `/security-pen-testing` | Authorized penetration testing of an app or API: vulnerability scans, OWASP Top 10 checks, dependency audits and a pentest report. |
| `/senior-architect` | System architecture decisions with a written rationale: monolith vs microservices, database choice, scaling limits, ADRs, Mermaid diagrams. |
| `/senior-backend` | Build and fix backend services: REST or GraphQL APIs, auth, microservices, PostgreSQL queries, migrations and load tests. |
| `/senior-computer-vision` | Computer vision models: object detection, segmentation, training a custom model, and optimizing or deploying inference (YOLO, DETR, SAM, ONNX, TensorRT). |
| `/senior-data-engineer` | Data pipelines: Airflow DAGs, Spark, dbt, Kafka, ETL/ELT, data quality checks. |
| `/senior-data-scientist` | Design experiments and analyze tabular data: A/B tests, causal inference, feature engineering, model evaluation. |
| `/senior-devops` | Set up CI/CD pipelines, infrastructure as code, containers and deployments on AWS, GCP or Azure. |
| `/senior-frontend` | Build and review React, Next.js, TypeScript or Tailwind frontends: components, scaffolding, performance and bundle size. |
| `/senior-fullstack` | Start a fullstack project or audit a codebase: pick a stack (Next.js, FastAPI, MERN, Django), scaffold it and score code quality. |
| `/senior-ml-engineer` | Use for putting ML models or LLM features into production: deployment, MLOps, drift monitoring, RAG pipelines, LLM API cost and retries. |
| `/senior-prompt-engineer` | Improve prompts and measure LLM quality: fix inconsistent prompts, build eval sets, score RAG retrieval, check agent tool configs. |
| `/senior-qa` | Write and improve tests for React or Next.js apps: Jest, React Testing Library, MSW mocks, Playwright E2E, coverage gaps. |
| `/senior-secops` | Find and fix application security problems: security reviews, CVE remediation, hardening, secrets and auth, SOC 2, PCI-DSS, HIPAA and GDPR checks. |
| `/senior-security` | Check if a design or code is secure: STRIDE threat model, DREAD risk scores, leaked secret scan. |
| `/stripe-integration-expert` | Use for any Stripe integration: subscriptions, trials, proration, checkout, usage billing, webhooks, customer portal or invoicing in Next.js, Express or Django. |
| `/tdd-guide` | Test-first development and test generation for Jest, Pytest, JUnit, Vitest or Mocha: red-green-refactor, fixtures and mocks, coverage gaps. |
| `/tech-stack-evaluator` | Compare frameworks or tech stacks before committing: side-by-side scoring, total cost of ownership, ecosystem health and migration risk. |
| `/threat-detection` | Use when hunting threats, sweeping IOCs or looking for anomalies in logs and telemetry. |

## Claude-skills: Finance (6)

| Skill | What it's for |
|---|---|
| `/finance-skills` | Pick the right finance skill: ratios, DCF, forecasts (financial-analyst), ARR, churn, CAC, LTV (saas-metrics-coach), month-end-close. |
| `/financial-analyst` | Analyze financial statements, value a company with a DCF, explain budget variance, build rolling forecasts. |
| `/month-end-close` | Use when running, planning or speeding up a month-end (or quarter-end) close — building or reviewing the close checklist and calendar, reconciling a bank statement or sub-ledger to the general ledger, writing or… |
| `/passive-deal-screener` | Use when a passive investor shares a private deal (syndication, preferred equity, bridge fund, private credit) to screen as an LP. |
| `/saas-metrics-coach` | Use when someone shares SaaS revenue or customer numbers, or asks about ARR, MRR, churn, LTV, CAC, NRR or how their SaaS is doing. |
| `/stock-analysis` | Analyze, research or value a listed stock or company (US, global, NSE or BSE) with verified data, ratios, scores and valuation. |

## Claude-skills: Marketing (49)

| Skill | What it's for |
|---|---|
| `/ab-test-setup` | Use before planning or launching any A/B, split or multivariate test, or when asked if a result is significant. |
| `/ad-creative` | Use for any ad copy request (RSA headlines, Meta, LinkedIn or TikTok ads, bulk variations), before writing. |
| `/aeo` | Use when content should be cited by ChatGPT, Perplexity, Claude or Gemini (answer engine optimization), before rewriting it. |
| `/ai-decision-authority` | Use before letting AI or an agent act on a marketing or GTM task without human review, or when writing an AI review policy. |
| `/analytics-tracking` | Use for any GA4, Google Tag Manager, event-tracking or conversion-tracking setup, audit or broken-event debug, before touching tags. |
| `/app-store-optimization` | Use for any App Store or Google Play listing, keyword, ranking or review question, before writing metadata. |
| `/brand-guidelines` | Use when writing or enforcing brand guidelines (colors, typography, logo rules, imagery, tone of voice), or checking an asset against them. |
| `/business-name-fit` | Use when naming a company, brand or product, or checking whether a name works abroad, before committing to one. |
| `/campaign-analytics` | Analyze campaign performance on the user's numbers: ROAS, CPA, ROI, multi-touch attribution and funnel drop-off. |
| `/churn-prevention` | Use when designing a cancel flow, save offers, exit surveys or dunning emails, or cutting failed-payment churn. |
| `/cold-email` | Use for any cold outreach or SDR email or follow-up sequence to prospects who did not opt in, before drafting. |
| `/competitor-alternatives` | Use when creating an 'X vs Y', '[product] alternative' or comparison page, before drafting. |
| `/content-creator` | Use when someone asks for 'content creator' by name. |
| `/content-humanizer` | Make a draft sound less like AI: fix generic, robotic text with rhythm, specifics, personality and brand voice. |
| `/content-production` | Write a blog post, article or guide end to end: research, outline, draft, SEO pass and quality gates. |
| `/content-strategy` | Use when deciding what content to create (topics, clusters, a blog or content plan), before listing ideas. |
| `/copy-editing` | Edit, proofread and tighten existing marketing copy in focused passes: clarity, voice, proofreading, specificity, readability and AI tells. |
| `/copywriting` | Use for any headline, tagline, CTA, landing, pricing or about-page copy request, before drafting. |
| `/email-sequence` | Use for any drip, nurture, onboarding, welcome or re-engagement email sequence to opted-in users, before writing emails. |
| `/form-cro` | Use when a lead, contact, demo or checkout form is underperforming or being designed, before changing fields. |
| `/free-tool-strategy` | Use when considering a free calculator, grader, checker or generator as a marketing asset, before building it. |
| `/launch-strategy` | Plan a product or feature launch: readiness score and a phased plan by channel. |
| `/local-seo-manager` | Use for any local business's Google Business Profile, Maps ranking, service-area pages, citations or review replies, before writing. |
| `/marketing-context` | Use at the start of any marketing project, or when ICP, positioning or brand voice are missing, before other marketing skills. |
| `/marketing-demand-acquisition` | Use when planning demand generation, paid acquisition across Google, LinkedIn and Meta, or a marketing budget, before allocating spend. |
| `/marketing-ideas` | Use when asked for marketing or growth ideas for a SaaS or software product. |
| `/marketing-ops` | Use when a marketing request spans several skills (a campaign across content, SEO, CRO and channels) or it is unclear which skill fits. |
| `/marketing-psychology` | Apply persuasion and behavioral science ethically to a page, offer or campaign, from 70+ mental models. |
| `/marketing-skills` | Use when looking for which of the 44 marketing skills fits a task. |
| `/marketing-strategy-pmm` | Use for product positioning, ICP, competitive battlecards or a go-to-market plan, before drafting. |
| `/onboarding-cro` | Use when activation, time-to-value or a first-run experience after signup needs work, before redesigning it. |
| `/page-cro` | Fix a page that is not converting: section by section audit with fixes ranked by impact. |
| `/paid-ads` | Use for paid campaign strategy on Google, Meta, LinkedIn or X: structure, targeting, bids, retargeting and budgets. |
| `/paywall-upgrade-cro` | Use when designing or fixing an in-app paywall, upgrade modal, feature gate or trial-expiry screen. |
| `/popup-cro` | Use when creating or fixing a popup, modal, exit-intent, slide-in or banner meant to convert. |
| `/pricing-strategy` | Use for SaaS pricing tiers, value metric, packaging, a pricing page or a price increase, before proposing numbers. |
| `/programmatic-seo` | Use when building many SEO pages from a template and data (location, integration, comparison or directory pages), before generating them. |
| `/prompt-engineer-toolkit` | Use when a marketing team's AI prompts need testing, versioning or governance, before shipping a prompt. |
| `/referral-program` | Use when designing or fixing a referral, affiliate or ambassador program, before setting rewards. |
| `/schema-markup` | Use for any JSON-LD, schema.org, rich-result or structured-data request, before writing markup. |
| `/seo-audit` | Find why a site is not ranking: technical SEO, on-page issues, meta tags, site health. |
| `/signup-flow-cro` | Use when signup, registration or trial-start conversion is low or a signup flow is being designed. |
| `/site-architecture` | Use for URL structure, navigation, internal linking, hub pages or orphan pages, or when SEO problems are structural. |
| `/social-content` | Write a LinkedIn post, X thread, Instagram, TikTok or Facebook post with each platform's hook, length and format. |
| `/social-media-analyzer` | Score social performance: engagement rate, reach, ROI per platform, benchmarks. |
| `/social-media-manager` | Plan social media: strategy, content calendar, community management, follower growth. |
| `/webinar-marketing` | Use when planning, promoting or fixing a webinar or virtual event (registrations, show-up, follow-up, conversion). |
| `/x-twitter-growth` | Use for growing on X/Twitter: tweets, threads, profile audit, competitors or posting plan. |
| `/youtube-full` | Use for any YouTube URL, video ID or @handle, or a request for transcripts, video search, channel, playlist or new-upload monitoring. |

## Claude-skills: Playwright testing (pw) (10)

| Skill | What it's for |
|---|---|
| `/browserstack` | Use when running Playwright tests on BrowserStack or across a browser matrix ('browserstack', 'cross-browser', 'test on safari or firefox', 'browser compatibility'). |
| `/coverage` | Find what is not tested: map untested pages and flows and coverage gaps. |
| `/fix` | Diagnose and fix a failing or flaky Playwright test. |
| `/generate` | Use when asked to write Playwright or e2e tests for a page, component or feature ('write tests', 'add tests for', 'e2e test'). |
| `/migrate` | Use when moving tests from Cypress or Selenium to Playwright ('migrate tests', 'convert tests', 'replace selenium'). |
| `/pw` | Use for any Playwright or end-to-end browser testing work: writing tests, fixing flaky ones, migrating from Cypress or Selenium, CI setup, TestRail or BrowserStack. |
| `/pw-init` | Use when setting up Playwright in a project ('set up playwright', 'add e2e tests', 'configure playwright', 'init playwright'). |
| `/pw-review` | Use when reviewing Playwright tests for quality ('review tests', 'audit tests', 'playwright best practices check'). |
| `/report` | Summarize Playwright results. Use whenever the user asks how tests went, for a test report or status. |
| `/testrail` | Use when syncing Playwright tests with TestRail ('testrail', 'sync test cases', 'push results to testrail', 'import from testrail'). |

## Claude-skills: Product (14)

| Skill | What it's for |
|---|---|
| `/competitive-teardown` | Deep competitor teardown: pricing, reviews, hiring, SEO, UX, scored across 12 dimensions with SWOT and positioning maps. |
| `/design-qa` | Use when a UI screen, page or component is about to be called done, handed off or shipped, or when generated UI looks generic or half-finished. |
| `/experiment-designer` | Plan A/B tests and product experiments: hypotheses, sample size, priority, reading results. |
| `/landing-page-generator` | Use when asked for a landing, marketing or campaign page as a Next.js TSX component with Tailwind. |
| `/product-analytics` | Use when defining product KPIs, building metric dashboards, running cohort or retention analysis, or interpreting feature adoption trends across product stages. |
| `/product-discovery` | Validate product ideas: map assumptions, plan discovery sprints, test problem-solution fit. |
| `/product-manager-toolkit` | PM toolkit: RICE prioritization, customer interview synthesis, PRDs and go-to-market. |
| `/product-skills` | Use when a product request needs routing across the product-team skills (prioritization, OKRs, UX research, experiments, discovery, roadmaps), or to run the continuous discovery loop. |
| `/product-strategist` | Head of Product: quarterly OKRs cascaded from company to team, product vision, roadmap, team structure. |
| `/roadmap-communicator` | Write roadmap narratives, release notes, changelogs, stakeholder updates. |
| `/saas-scaffolder` | Use when starting a new SaaS app with auth, database, Stripe billing and a dashboard (Next.js App Router, TypeScript, Tailwind, shadcn/ui, Drizzle). |
| `/spec-to-repo` | Use when the user says 'build me an app', 'create a project from this spec', 'scaffold a new repo', 'generate a starter', 'turn this idea into code', 'bootstrap a project', 'I have requirements and need a codebase', or… |
| `/ui-design-system` | Use when building a design system: tokens, component docs, responsive scales or developer handoff. |
| `/ux-researcher-designer` | UX research: personas, journey maps, usability test plans, synthesis. |

## Claude-skills: Project management (Jira/Confluence) (9)

| Skill | What it's for |
|---|---|
| `/atlassian-admin` | Use for Atlassian org administration: Jira or Confluence users and groups, permissions, SSO, marketplace apps or security policy. |
| `/atlassian-templates` | Use when creating or changing Jira or Confluence templates, blueprints or page layouts for reuse across the org. |
| `/confluence-expert` | Use when building or restructuring a Confluence space: page hierarchy, permissions, templates, Jira macros or a content audit. |
| `/jira-expert` | Jira setup and queries: JQL, workflows, custom fields, automation, dashboards. |
| `/meeting-analyzer` | Use when the user shares meeting transcripts (.vtt, .srt, .txt, Otter, Granola, Zoom) or asks how they come across in meetings. |
| `/pm-skills` | Router for project-management skills: sprints, portfolio health, Jira, Confluence, stakeholder comms, plus a delivery loop. |
| `/scrum-master` | Use for sprint and team analytics: velocity forecasts, sprint health, retrospectives, burndown or blockers. |
| `/senior-pm` | Project and portfolio management for multi-workstream programs: plans, status reports, risk registers, capacity, executive reporting. |
| `/team-communications` | Use for any internal communication: 3P updates, weekly or status reports, newsletters, FAQs, incident reports, leadership updates ('write my update'). |

## Claude-skills: Regulatory & quality (medical devices, ISO, GDPR) (19)

| Skill | What it's for |
|---|---|
| `/access-lifecycle` | Use when preparing or running a user access review, checking that leavers lost their access, finding orphaned or ownerless service accounts, answering an auditor's access-control request for SOC 2, ISO 27001, PCI DSS… |
| `/agent-decision-receipts` | Use when an autonomous agent takes a side-effecting action (deploy, delete, pay, grant access) that may need proving later, or for EU AI Act Art. |
| `/capa-officer` | Use for CAPA work in a medical device QMS: root cause analysis (5-Why, fishbone), corrective action plans, effectiveness checks or CAPA metrics. |
| `/cmmc-readiness` | Use when a defense contractor or subcontractor is preparing for a CMMC 2.0 Level 2 self-assessment or C3PAO assessment, calculating or checking an SPRS score against NIST SP 800-171 Rev 2, deciding what can go on a… |
| `/eu-ai-act-specialist` | Use for EU AI Act (Regulation 2024/1689) compliance work: classifying an AI system's risk tier, planning the Art. |
| `/fda-consultant-specialist` | Use for FDA medical device questions: 510(k) vs De Novo vs PMA, predicates and substantial equivalence, QMSR (21 CFR 820), HIPAA or device cybersecurity. |
| `/gdpr-dsgvo-expert` | Use for GDPR or DSGVO work: scanning a codebase for privacy risks, writing a DPIA or tracking data subject requests against the Art. |
| `/information-security-manager-iso27001` | Use when designing or running an ISO 27001 ISMS in HealthTech or MedTech: risk assessment, control implementation, certification or security incidents. |
| `/isms-audit-expert` | Use for ISO 27001 audit work: internal or surveillance audits, Annex A control evidence, Statement of Applicability, nonconformities, Stage 1 and 2 prep. |
| `/iso42001-specialist` | Use for ISO/IEC 42001 AI management system work: gap analysis against Clauses 4-10, the AI risk register and Annex A controls, or the internal audit plan. |
| `/mdr-745-specialist` | Use for EU MDR 2017/745 work: device classification under Annex VIII, technical file gaps (Annex II/III), clinical evaluation, PMS and PSUR cadence, notified body prep. |
| `/qms-audit-expert` | Use for ISO 13485 internal audits: planning the program, running an audit, classifying findings or preparing for an external audit. |
| `/quality-documentation-manager` | Use for QMS document control: numbering, versioning, change control or 21 CFR Part 11 e-signatures. |
| `/quality-manager-qmr` | Use for QMR duties under ISO 13485 5.5.2: management review, quality policy and objectives, quality KPIs and cost of quality. |
| `/quality-manager-qms-iso13485` | Build or maintain an ISO 13485 medical device QMS: design, documentation, CAPA, audit prep. |
| `/ra-qm-skills` | Router for regulatory and quality skills: ISO 13485, MDR, FDA, ISO 14971, CAPA, ISO 27001, ISO 42001, EU AI Act, GDPR, SOC 2. |
| `/regulatory-affairs-head` | Use for medical device market access strategy: FDA 510(k), De Novo or PMA packages, CE marking under MDR, pre-sub meetings, agency deficiency responses or multi-market plans. |
| `/risk-management-specialist` | Use for ISO 14971 medical device risk management: hazard analysis, FMEA, fault trees, risk controls, benefit-risk or residual risk. |
| `/soc2-compliance` | Use when the user asks to prepare for SOC 2 audits, map Trust Service Criteria, build control matrices, collect audit evidence, perform gap analysis, or assess SOC 2 Type I vs Type II readiness. |

## Claude-skills: Self-improving memory (6)

| Skill | What it's for |
|---|---|
| `/extract` | Turn a fix or pattern that keeps coming up into a reusable skill with SKILL.md, reference docs and examples. |
| `/memory-review` | Review what the agent has learned in auto-memory: what to promote to permanent rules, stale entries to prune, duplicates to merge. |
| `/memory-status` | Health check of agent auto-memory: line counts, topic files, capacity, stale entries and what to prune. |
| `/promote` | Graduate a proven pattern from auto-memory (MEMORY.md) to CLAUDE.md or .claude/rules/ for permanent enforcement. |
| `/remember` | Save something important to auto-memory with a timestamp and context. |
| `/self-improving-agent` | Curate what the agent has learned into durable project knowledge. |

## Superpowers (coding workflow) (15)

| Skill | What it's for |
|---|---|
| `/brainstorming` | You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning anything new, in software or out of it (a talk, a business, a renovation). |
| `/diagnosing-superpowers` | Use when a superpowers session went wrong and your human partner wants to know why — repeated work, ignored plans, stumbles, poor results, a skill that didn't fire, "it took too long", "why is it so expensive", "what is it doing" — or wants to build a bug report for the superpowers maintainers, for the current session or a past one identified by id or path, on any harness. |
| `/dispatching-parallel-agents` | Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies |
| `/executing-plans` | Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or no subagent tool is available |
| `/finishing-a-development-branch` | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work |
| `/receiving-code-review` | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation |
| `/requesting-code-review` | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| `/subagent-driven-development` | Use when executing implementation plans with independent tasks in the current session |
| `/systematic-debugging` | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| `/test-driven-development` | Use when implementing any feature or bugfix, before writing implementation code |
| `/using-git-worktrees` | Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback |
| `/using-superpowers` | Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions |
| `/verification-before-completion` | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always |
| `/writing-plans` | Use when you have a spec or requirements for a multi-step task, before touching code |
| `/writing-skills` | Use when creating new skills, editing existing skills, or verifying skills work before deployment |

## Marketing skills by Corey Haines (41)

| Skill | What it's for |
|---|---|
| `/ab-testing` | When the user wants to plan, design, or implement an A/B test or experiment, or build a growth experimentation program. |
| `/ads` | When the user wants help with paid advertising campaigns on Google Ads, Meta (Facebook/Instagram), LinkedIn, Twitter/X, or other ad platforms. |
| `/ai-seo` | When the user wants to optimize content for AI search engines, get cited by LLMs, or appear in AI-generated answers. |
| `/analytics` | When the user wants to set up, improve, or audit analytics tracking and measurement. |
| `/aso` | When the user wants to audit or optimize an App Store or Google Play listing. |
| `/attribution` | When the user wants to figure out which marketing actually drives conversions and revenue, choose or interpret an attribution model, or reconcile conflicting numbers across tools. |
| `/co-marketing` | When the user wants to find co-marketing partners, plan joint campaigns, or brainstorm partnership opportunities. |
| `/community-marketing` | Build and leverage online communities to drive product growth and brand loyalty. |
| `/competitor-profiling` | When the user wants to research, profile, or analyze competitors from their URLs. |
| `/competitors` | When the user wants to create competitor comparison or alternative pages for SEO and buyer-facing use. |
| `/conversion-tracking` | Set up, audit, verify, or fix website conversion tracking. |
| `/cro` | When the user wants to optimize, improve, or increase conversions on any marketing page or form — including homepage, landing pages, pricing pages, feature pages, lead capture forms, or contact forms. |
| `/customer-research` | When the user wants to conduct, analyze, or synthesize customer research. |
| `/directory-submissions` | When the user wants to submit their product to startup, SaaS, AI, agent, MCP, no-code, or review directories for backlinks, domain rating, and discovery. |
| `/emails` | When the user wants to create or optimize an email sequence, drip campaign, automated email flow, or lifecycle email program. |
| `/events` | When the user wants to plan, run, sponsor, speak at, or get pipeline from events — webinars, conferences, trade shows, meetups, dinners, workshops, virtual summits, or user conferences. |
| `/free-tools` | When the user wants to plan, evaluate, or build a free tool for marketing purposes — lead generation, SEO value, or brand awareness. |
| `/image` | When the user wants to create, generate, edit, or optimize images for marketing — blog heroes, social graphics, product mockups, profile banners, listing visuals, or brand assets. |
| `/influencer-marketing` | When the user wants to run influencer, creator, or ambassador partnerships to promote their product — finding and vetting partners, structuring deals, briefing creators, disclosure compliance, and measuring ROI. |
| `/launch` | When the user wants to plan a product launch, feature announcement, or release strategy. |
| `/lead-magnets` | When the user wants to create, plan, or optimize a lead magnet for email capture or lead generation. |
| `/link-building` | When the user wants to earn backlinks or third-party mentions that lift rankings and AI citations. |
| `/marketing-council` | When the user wants multiple expert perspectives on a marketing question — a simulated board of advisors staffed by legendary marketers (Seth Godin, David Ogilvy, Eugene Schwartz, April Dunford, Rory Sutherland, Alex… |
| `/marketing-loops` | When the user wants to set up a recurring, self-running marketing workflow — a repeatable loop an AI agent runs on a cadence (weekly, daily, on a trigger) rather than a one-off task. |
| `/marketing-plan` | When the user needs a comprehensive marketing plan for a client, a company they advise, or their own product. |
| `/offers` | When the user wants to design, construct, or improve an offer — the thing they actually sell — including value framing, bonus stacking, guarantee design, scarcity/urgency, naming, and payment structure. |
| `/onboarding` | When the user wants to optimize post-signup onboarding, user activation, first-run experience, or time-to-value. |
| `/paywalls` | When the user wants to create or optimize in-app paywalls, upgrade screens, upsell modals, or feature gates. |
| `/popups` | When the user wants to create or optimize popups, modals, overlays, slide-ins, or banners for conversion purposes. |
| `/product-marketing` | When the user wants to create or update their product marketing context document. |
| `/prospecting` | When the user wants to find, qualify, and build a list of prospects to reach out to, across B2B SaaS, general B2B, or local small businesses. |
| `/public-relations` | When the user wants help with public relations, earned media, press coverage, journalist outreach, or media strategy (not pull requests). |
| `/referrals` | When the user wants to create, optimize, or analyze a referral program, affiliate program, or word-of-mouth strategy. |
| `/reverse-engineer-marketing` | When the user wants to reverse engineer how another company grew and copy what worked. |
| `/revops` | When the user wants help with revenue operations, lead lifecycle management, or marketing-to-sales handoff processes. |
| `/sales-enablement` | When the user wants to create sales collateral, pitch decks, one-pagers, objection handling docs, or demo scripts. |
| `/schema` | When the user wants to add, fix, or optimize schema markup and structured data on their site. |
| `/signup` | When the user wants to optimize signup, registration, account creation, or trial activation flows. |
| `/sms` | When the user wants to plan, build, or optimize SMS, MMS, or WhatsApp marketing — including welcome flows, abandoned cart texts, post-purchase, win-back, promotional sends, or transactional/auth SMS. |
| `/social` | When the user wants help creating, scheduling, or optimizing social media content for LinkedIn, Twitter/X, Instagram, TikTok, or Facebook, or wants to do social listening and engagement triage. |
| `/video` | When the user wants to create, generate, or produce video content using AI tools or programmatic frameworks. |
