# Skills catalog

**200 skills** listed here. 132 live in `.claude/skills`. The other 68 come from the plugins enabled in `.claude/settings.json` and are shown with their plugin prefix (for example `/pw:pw` or `/marketing-skills:cold-email`); the repo no longer keeps its own copies of them. Type `/name` to use one, or describe the task and Claude picks the skill. The ECC plugin adds 314 more skills (`/ecc:*`) that are not listed here.

Also installed: 26 commands (23 `/gsd-*` from GSD, plus `/python-review`, `/fastapi-review`, `/test-coverage`) and 25 helper agents (22 `gsd-*`, `planner`, `python-reviewer`, `fastapi-reviewer`).

## Overview

| Group | Skills | What it's for |
|---|---|---|
| Founder pack | 11 | Test, plan and launch a business idea end to end. |
| Whale pack | 11 | Find customers and get them to pay before you build. |
| Marketing (Corey Haines) | 41 | Modern marketing playbooks: CRO, ads, SEO, prospecting, offers, launches. |
| Marketing (original pack) | 26 | Copywriting, SEO audits, content and social skills. |
| UI/UX Pro Max (design) | 7 | Design intelligence for websites and apps: styles, palettes, fonts, components, branding. |
| Product | 14 | PRDs, UX research, roadmaps, landing pages. |
| Business growth | 5 | Customer success, sales engineering, proposals and contracts. |
| Finance | 6 | Valuation, SaaS metrics, month-end close. |
| Replica pack | 11 | Reverse-engineer an app and build your own better version. |
| Research | 1 | What people said online in the last 30 days. |
| Writing & output style | 2 | Make text sound human, or make Claude's replies ADHD-friendly. |
| Superpowers (coding workflow) | 15 | Careful coding habits: plan, test first, debug, verify. |
| Engineering | 8 | Website, backend, payments, email and code-review skills. |
| Advanced engineering | 11 | AI agents, automation, MCP servers, databases, multilingual sites, finding new skills. |
| Playwright testing | 10 | Write, fix and run website tests. |
| Vercel (React, Next.js & deploy) | 9 | React and Next.js best practices, Vercel deploys and cost tuning, UI and writing reviews. |
| Browser & Python | 6 | Website automation, FastAPI and Python best practices. |
| Self-improving memory | 6 | Save lessons so Claude remembers them across sessions. |

## Founder pack (11)

Test, plan and launch a business idea end to end.

| Skill | What it does |
|---|---|
| `/founder-board` | Your board of directors. Puts a business idea in front of a three-member board, each a sub-agent reading the idea through one published framework: the Offers lens (from Alex Hormozi's $100M Offers), the Monopoly lens (from Peter Thiel's Zero to One) and the Product lens (from Walter Isaacson's… |
| `/founder-brand` | Your brand designer. Names the business (with the trademark, domain and handle checks to run before falling in love with a name), writes the voice, a one-line promise and a tagline, and briefs the look: colours, type, logo and the first things a customer sees, so they match the positioning the… |
| `/founder-cfo` | Your CFO. Builds the unit economics of a business before money is spent: what one unit earns after its direct costs, the real profit margin at the planned volume, the break-even point in units a day, year 1 month by month, the cash needed before it pays for itself, how long the startup spend takes… |
| `/founder-competitors` | Maps every competitor and the gap they leave. Finds the direct competitors, indirect ones and the substitutes a buyer would use instead, from public sources only, and records what each sells, at what price, how they position themselves and what their customers complain about in public reviews… |
| `/founder-consumer` | The consumer panel. Spins up a swarm of buyer sub-agents (default 100, --quick for 20) trained on the user's target customer, each with a different income, age, buying behaviour and objection, shows every one the same pitch, and runs the business through 100 buyer scenarios to see who buys, who… |
| `/founder-launch` | Your launch lead. Builds a dated, step-by-step launch plan: a cheap real-world test first (a waitlist, a pre-sale or a pop-up with a real price, so real buyers confirm what the simulated panel said), then the countdown to opening day with owners and deadlines, the launch-day run sheet, and the… |
| `/founder-marketing` | Your marketing director. Turns the buyer panel and the competitor map into positioning, the channels the target customer actually uses, a 30-day launch campaign with dated posts and ads, the first ten hooks, a budget split and the numbers to watch. |
| `/founder-offer` | Builds an offer too good to refuse. Lists every problem the buyer hits on the way to the result they want, turns each into a solution, trims to what is cheap to deliver and valuable to the buyer, and stacks it with honest bonuses, a guarantee the CFO can afford, real urgency and a clear name. |
| `/founder-ops` | Your operations manager. Works out how the business actually runs on day one: suppliers and what they cost, who works when, the step-by-step routines for opening, serving or shipping and closing, the tools to run it, the licences and permits to check, and a risk register with what to do when each… |
| `/founder-plan` | Your business planner. Compiles everything the other founder skills wrote (the board's verdict, the competitors, the buyer panel, pricing, the offer, the CFO's numbers, marketing, brand, operations and the launch plan) into one business plan with a verdict at the top that is computed from the… |
| `/founder-pricing` | Finds the price buyers will actually pay. Reads the consumer panel's four price answers per buyer into a Van Westendorp price-sensitivity range (too cheap, a bargain, getting expensive, too expensive), sets it against what competitors really charge and against the CFO's margin, and recommends a… |

## Whale pack (11)

Find customers and get them to pay before you build.

| Skill | What it does |
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

## Marketing (Corey Haines) (41)

Modern marketing playbooks: CRO, ads, SEO, prospecting, offers, launches.

| Skill | What it does |
|---|---|
| `/ab-testing` | When the user wants to plan, design, or implement an A/B test or experiment, or build a growth experimentation program. |
| `/ads` | When the user wants help with paid advertising campaigns on Google Ads, Meta (Facebook/Instagram), LinkedIn, Twitter/X, or other ad platforms. |
| `/ai-seo` | When the user wants to optimize content for AI search engines, get cited by LLMs, or appear in AI-generated answers. |
| `/analytics` | When the user wants to set up, improve, or audit analytics tracking and measurement. Also use when the user mentions "set up tracking," "GA4," "Google Analytics," "event tracking," "UTM parameters," "tag manager," "GTM," "analytics implementation," "tracking plan," "how do I measure this,"… |
| `/aso` | When the user wants to audit or optimize an App Store or Google Play listing. Also use when the user mentions 'ASO audit,' 'app store optimization,' 'optimize my app listing,' 'improve app visibility,' 'app store ranking,' 'audit my listing,' 'why aren't people downloading my app,' 'improve my app… |
| `/attribution` | When the user wants to figure out which marketing actually drives conversions and revenue, choose or interpret an attribution model, or reconcile conflicting numbers across tools. |
| `/co-marketing` | When the user wants to find co-marketing partners, plan joint campaigns, or brainstorm partnership opportunities. |
| `/community-marketing` | Build and leverage online communities to drive product growth and brand loyalty. Use when the user wants to create a community strategy, grow a Discord or Slack community, manage a forum or subreddit, build brand advocates, increase word-of-mouth, drive community-led growth, engage users… |
| `/competitor-profiling` | When the user wants to research, profile, or analyze competitors from their URLs. Also use when the user mentions 'competitor profile,' 'competitor research,' 'competitor analysis,' 'profile this competitor,' 'analyze competitor,' 'competitive intelligence,' 'competitor deep dive,' 'who are my… |
| `/competitors` | When the user wants to create competitor comparison or alternative pages for SEO and buyer-facing use. |
| `/conversion-tracking` | Set up, audit, verify, or fix website conversion tracking. Use when the conversion is a form submission, booked meeting, chat, phone call, signup, or purchase; when conversions must reach Google Ads, Meta, GA4, LinkedIn, TikTok, or Microsoft Ads; when the work involves GTM tags and dataLayer… |
| `/cro` | When the user wants to optimize, improve, or increase conversions on any marketing page or form — including homepage, landing pages, pricing pages, feature pages, lead capture forms, or contact forms. |
| `/customer-research` | When the user wants to conduct, analyze, or synthesize customer research. Use when the user mentions "customer research," "ICP research," "talk to customers," "analyze transcripts," "customer interviews," "survey analysis," "support ticket analysis," "voice of customer," "VOC," "build personas,"… |
| `/directory-submissions` | When the user wants to submit their product to startup, SaaS, AI, agent, MCP, no-code, or review directories for backlinks, domain rating, and discovery. |
| `/emails` | When the user wants to create or optimize an email sequence, drip campaign, automated email flow, or lifecycle email program. |
| `/events` | When the user wants to plan, run, sponsor, speak at, or get pipeline from events — webinars, conferences, trade shows, meetups, dinners, workshops, virtual summits, or user conferences. |
| `/free-tools` | When the user wants to plan, evaluate, or build a free tool for marketing purposes — lead generation, SEO value, or brand awareness. |
| `/image` | When the user wants to create, generate, edit, or optimize images for marketing — blog heroes, social graphics, product mockups, profile banners, listing visuals, or brand assets. |
| `/influencer-marketing` | When the user wants to run influencer, creator, or ambassador partnerships to promote their product — finding and vetting partners, structuring deals, briefing creators, disclosure compliance, and measuring ROI. |
| `/launch` | When the user wants to plan a product launch, feature announcement, or release strategy. Also use when the user mentions 'launch,' 'Product Hunt,' 'feature release,' 'announcement,' 'go-to-market,' 'beta launch,' 'early access,' 'waitlist,' 'product update,' 'how do I launch this,' 'site launch,'… |
| `/lead-magnets` | When the user wants to create, plan, or optimize a lead magnet for email capture or lead generation. |
| `/link-building` | When the user wants to earn backlinks or third-party mentions that lift rankings and AI citations. |
| `/marketing-council` | When the user wants multiple expert perspectives on a marketing question — a simulated board of advisors staffed by legendary marketers (Seth Godin, David Ogilvy, Eugene Schwartz, April Dunford, Rory Sutherland, Alex Hormozi, Byron Sharp, and more). |
| `/marketing-loops` | When the user wants to set up a recurring, self-running marketing workflow — a repeatable loop an AI agent runs on a cadence (weekly, daily, on a trigger) rather than a one-off task. |
| `/marketing-plan` | When the user needs a comprehensive marketing plan for a client, a company they advise, or their own product. |
| `/offers` | When the user wants to design, construct, or improve an offer — the thing they actually sell — including value framing, bonus stacking, guarantee design, scarcity/urgency, naming, and payment structure. |
| `/onboarding` | When the user wants to optimize post-signup onboarding, user activation, first-run experience, or time-to-value. |
| `/paywalls` | When the user wants to create or optimize in-app paywalls, upgrade screens, upsell modals, or feature gates. |
| `/popups` | When the user wants to create or optimize popups, modals, overlays, slide-ins, or banners for conversion purposes. |
| `/product-marketing` | When the user wants to create or update their product marketing context document. Also use when the user mentions 'product context,' 'marketing context,' 'set up context,' 'positioning,' 'who is my target audience,' 'describe my product,' 'ICP,' 'ideal customer profile,' 'brand voice,' 'tone of… |
| `/prospecting` | When the user wants to find, qualify, and build a list of prospects to reach out to, across B2B SaaS, general B2B, or local small businesses. |
| `/public-relations` | When the user wants help with public relations, earned media, press coverage, journalist outreach, or media strategy (not pull requests). |
| `/referrals` | When the user wants to create, optimize, or analyze a referral program, affiliate program, or word-of-mouth strategy. |
| `/reverse-engineer-marketing` | When the user wants to reverse engineer how another company grew and copy what worked. Also use when the user mentions 'reverse engineer,' 'how did X grow,' 'how does X get customers,' 'growth teardown,' 'marketing teardown,' 'GTM teardown,' 'what is X doing for marketing,' 'what made X take off,'… |
| `/revops` | When the user wants help with revenue operations, lead lifecycle management, or marketing-to-sales handoff processes. |
| `/sales-enablement` | When the user wants to create sales collateral, pitch decks, one-pagers, objection handling docs, or demo scripts. |
| `/schema` | When the user wants to add, fix, or optimize schema markup and structured data on their site. |
| `/signup` | When the user wants to optimize signup, registration, account creation, or trial activation flows. |
| `/sms` | When the user wants to plan, build, or optimize SMS, MMS, or WhatsApp marketing — including welcome flows, abandoned cart texts, post-purchase, win-back, promotional sends, or transactional/auth SMS. |
| `/social` | When the user wants help creating, scheduling, or optimizing social media content for LinkedIn, Twitter/X, Instagram, TikTok, or Facebook, or wants to do social listening and engagement triage. |
| `/video` | When the user wants to create, generate, or produce video content using AI tools or programmatic frameworks. |

## Marketing (original pack) (26)

Copywriting, SEO audits, content and social skills.

| Skill | What it does |
|---|---|
| `/marketing-skills:ad-creative` | Use for any ad copy request (RSA headlines, Meta, LinkedIn or TikTok ads, bulk variations), before writing. |
| `/marketing-skills:ai-decision-authority` | Use before letting AI or an agent act on a marketing or GTM task without human review, or when writing an AI review policy. |
| `/brand-guidelines` | Use when writing or enforcing brand guidelines (colors, typography, logo rules, imagery, tone of voice), or checking an asset against them. |
| `/marketing-skills:business-name-fit` | Use when naming a company, brand or product, or checking whether a name works abroad, before committing to one. |
| `/marketing-skills:campaign-analytics` | Analyze campaign performance on the user's numbers: ROAS, CPA, ROI, multi-touch attribution and funnel drop-off. |
| `/marketing-skills:churn-prevention` | Use when designing a cancel flow, save offers, exit surveys or dunning emails, or cutting failed-payment churn. |
| `/marketing-skills:cold-email` | Use for any cold outreach or SDR email or follow-up sequence to prospects who did not opt in, before drafting. |
| `/content-production` | Write a blog post, article or guide end to end: research, outline, draft, SEO pass and quality gates. |
| `/content-strategy` | Use when deciding what content to create (topics, clusters, a blog or content plan), before listing ideas. |
| `/copy-editing` | Edit, proofread and tighten existing marketing copy in focused passes: clarity, voice, proofreading, specificity, readability and AI tells. |
| `/copywriting` | Use for any headline, tagline, CTA, landing, pricing or about-page copy request, before drafting. |
| `/marketing-skills:local-seo-manager` | Use for any local business's Google Business Profile, Maps ranking, service-area pages, citations or review replies, before writing. |
| `/marketing-skills:marketing-demand-acquisition` | Use when planning demand generation, paid acquisition across Google, LinkedIn and Meta, or a marketing budget, before allocating spend. |
| `/marketing-skills:marketing-ideas` | Use when asked for marketing or growth ideas for a SaaS or software product. Picks from 139 tactics by stage, budget and channel instead of a generic list. |
| `/marketing-ops` | Use when a marketing request spans several skills (a campaign across content, SEO, CRO and channels) or it is unclear which skill fits. |
| `/marketing-skills:marketing-psychology` | Apply persuasion and behavioral science ethically to a page, offer or campaign, from 70+ mental models. |
| `/marketing-skills:marketing-strategy-pmm` | Use for product positioning, ICP, competitive battlecards or a go-to-market plan, before drafting. |
| `/marketing-skills:pricing-strategy` | Use for SaaS pricing tiers, value metric, packaging, a pricing page or a price increase, before proposing numbers. |
| `/marketing-skills:programmatic-seo` | Use when building many SEO pages from a template and data (location, integration, comparison or directory pages), before generating them. |
| `/marketing-skills:prompt-engineer-toolkit` | Use when a marketing team's AI prompts need testing, versioning or governance, before shipping a prompt. |
| `/marketing-skills:seo-audit` | Find why a site is not ranking: technical SEO, on-page issues, meta tags, site health. Use whenever the user asks why a page is not on Google, why traffic dropped or for an SEO audit. |
| `/marketing-skills:site-architecture` | Use for URL structure, navigation, internal linking, hub pages or orphan pages, or when SEO problems are structural. |
| `/marketing-skills:social-media-analyzer` | Score social performance: engagement rate, reach, ROI per platform, benchmarks. Load whenever the user asks which platform performs best, if posts are working, or shares social metrics to compare. |
| `/marketing-skills:social-media-manager` | Plan social media: strategy, content calendar, community management, follower growth. Use whenever the user asks what to post and when, or how to grow followers. |
| `/marketing-skills:x-twitter-growth` | Use for growing on X/Twitter: tweets, threads, profile audit, competitors or posting plan. |
| `/marketing-skills:youtube-full` | Use for any YouTube URL, video ID or @handle, or a request for transcripts, video search, channel, playlist or new-upload monitoring. |
## UI/UX Pro Max (design) (7)

Design intelligence for websites and apps: styles, palettes, fonts, components, branding.

| Skill | What it does |
|---|---|
| `/banner-design` | Design banners for social media, ads, website heroes, creative assets, and print. Multiple art direction options with optional generated or supplied visuals. |
| `/brand` | Brand voice, visual identity, messaging frameworks, asset management, brand consistency. Activate for branded content, tone of voice, marketing assets, brand compliance, style guides. |
| `/design` | Comprehensive design skill: brand identity, design tokens, UI styling, logo generation (55 styles, Gemini, Atlas Cloud, or MuAPI AI), corporate identity program (50 deliverables, CIP mockups), HTML presentations (Chart.js), banner design (22 styles, social/ads/web/print), icon design (15 styles… |
| `/design-system` | Token architecture, component specifications, and slide generation. Three-layer tokens (primitive→semantic→component), CSS variables, spacing/typography scales, component specs, strategic slide creation. |
| `/slides` | Create strategic HTML presentations with Chart.js, design tokens, responsive layouts, copywriting formulas, and contextual slide strategies. |
| `/ui-styling` | Create beautiful, accessible user interfaces with shadcn/ui components (built on Radix UI + Tailwind), Tailwind CSS utility-first styling, and canvas-based visual designs. |
| `/ui-ux-pro-max` | UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, building, reviewing, or fixing interfaces, including pages, components, design systems, accessibility, interaction, responsive layout, typography, color, charts, and stack-specific UI implementation. |

## Product (14)

PRDs, UX research, roadmaps, landing pages.

| Skill | What it does |
|---|---|
| `/product-skills:competitive-teardown` | Deep competitor teardown: pricing, reviews, hiring, SEO, UX, scored across 12 dimensions with SWOT and positioning maps. |
| `/product-skills:design-qa` | Use when a UI screen, page or component is about to be called done, handed off or shipped, or when generated UI looks generic or half-finished. |
| `/product-skills:experiment-designer` | Plan A/B tests and product experiments: hypotheses, sample size, priority, reading results. |
| `/product-skills:landing-page-generator` | Use when asked for a landing, marketing or campaign page as a Next.js TSX component with Tailwind. |
| `/product-skills:product-analytics` | Use when defining product KPIs, building metric dashboards, running cohort or retention analysis, or interpreting feature adoption trends across product stages. |
| `/product-skills:product-discovery` | Validate product ideas: map assumptions, plan discovery sprints, test problem-solution fit. |
| `/product-skills:product-manager-toolkit` | PM toolkit: RICE prioritization, customer interview synthesis, PRDs and go-to-market. Use whenever the user asks what to build next, to rank features, write a PRD or sum up interview notes. |
| `/product-skills:product-skills` | Use when a product request needs routing across the product-team skills (prioritization, OKRs, UX research, experiments, discovery, roadmaps), or to run the continuous discovery loop. |
| `/product-skills:product-strategist` | Head of Product: quarterly OKRs cascaded from company to team, product vision, roadmap, team structure. |
| `/product-skills:roadmap-communicator` | Write roadmap narratives, release notes, changelogs, stakeholder updates. Use whenever the user explains plans to execs, engineers or customers. |
| `/product-skills:saas-scaffolder` | Use when starting a new SaaS app with auth, database, Stripe billing and a dashboard (Next.js App Router, TypeScript, Tailwind, shadcn/ui, Drizzle). |
| `/product-skills:spec-to-repo` | Use when the user says 'build me an app', 'create a project from this spec', 'scaffold a new repo', 'generate a starter', 'turn this idea into code', 'bootstrap a project', 'I have requirements and need a codebase', or provides a natural-language project specification and expects a complete… |
| `/product-skills:ui-design-system` | Use when building a design system: tokens, component docs, responsive scales or developer handoff. |
| `/product-skills:ux-researcher-designer` | UX research: personas, journey maps, usability test plans, synthesis. Use whenever the user asks who their users are or why they struggle. |

## Business growth (5)

Customer success, sales engineering, proposals and contracts.

| Skill | What it does |
|---|---|
| `/business-growth-skills:business-growth-skills` | Use when a growth request needs routing between customer-success-manager, sales-engineer, revenue-operations and contract-and-proposal-writer. |
| `/business-growth-skills:contract-and-proposal-writer` | Use when drafting a freelance contract, proposal, SOW, NDA or MSA for US, EU, UK or DACH jurisdictions. |
| `/business-growth-skills:customer-success-manager` | Use when reviewing customer accounts for health, churn risk or expansion. Scores health with health_score_calculator.py, churn with churn_risk_analyzer.py and upsell with expansion_opportunity_scorer.py. |
| `/business-growth-skills:revenue-operations` | Check sales pipeline and forecasts: pipeline coverage, forecast accuracy, magic number, CAC payback. |
| `/business-growth-skills:sales-engineer` | Use for pre-sales work: RFP coverage gaps, competitive feature matrices or planning and scoring a proof of concept. |

## Finance (6)

Valuation, SaaS metrics, month-end close.

| Skill | What it does |
|---|---|
| `/finance-skills:finance-skills` | Pick the right finance skill: ratios, DCF, forecasts (financial-analyst), ARR, churn, CAC, LTV (saas-metrics-coach), month-end-close. |
| `/finance-skills:financial-analyst` | Analyze financial statements, value a company with a DCF, explain budget variance, build rolling forecasts. |
| `/finance-skills:month-end-close` | Use when running, planning or speeding up a month-end (or quarter-end) close — building or reviewing the close checklist and calendar, reconciling a bank statement or sub-ledger to the general ledger, writing or reviewing flux (variance) explanations, or finding why the close takes too many days. |
| `/finance-skills:passive-deal-screener` | Use when a passive investor shares a private deal (syndication, preferred equity, bridge fund, private credit) to screen as an LP. |
| `/finance-skills:saas-metrics-coach` | Use when someone shares SaaS revenue or customer numbers, or asks about ARR, MRR, churn, LTV, CAC, NRR or how their SaaS is doing. |
| `/finance-skills:stock-analysis` | Analyze, research or value a listed stock or company (US, global, NSE or BSE) with verified data, ratios, scores and valuation. |

## Replica pack (11)

Reverse-engineer an app and build your own better version.

| Skill | What it does |
|---|---|
| `/replica-architect` | Plans the stack, database schema and API for an app clone, from the recon map replica-recon wrote. |
| `/replica-backend` | Builds the backend of an app clone: auth, database migrations and access rules, payments with Stripe, email, background jobs and third-party integrations through official APIs only, plus a security checklist. |
| `/replica-brand` | Names and rebrands an app clone so it is the user's own: name candidates with the trademark, domain, store and handle checks to run, a new palette checked for contrast, a logo brief, a voice guide, and a sweep tool that finds anything of the original left in the codebase. |
| `/replica-build` | Rebuilds an app screen by screen from the recon map: app shell first, then the core flow as a vertical slice, then every screen with all its states, ticking off the feature matrix as it goes. |
| `/replica-deploy` | Ships an app clone live on the user's own domain: a preflight gate (tests green, parity must-haves done, rebrand sweep clean, listing linted, legal pages up), production database and env vars, the host, DNS records for the domain and for email, Stripe live mode, OAuth redirects, monitoring, and… |
| `/replica-design` | Rebuilds an app's design system for a clone: colour roles, type scale, spacing, radius, shadows and every component with its states, as design tokens plus component specs, with original assets instead of the target's logos, icons, illustrations or licensed fonts. |
| `/replica-diff` | Compares an app clone against the original: a feature parity score from the feature matrix (weighted by must, should, could) with the missing list in build order, plus a screenshot layout diff that ignores colour so a rebrand does not count against you. |
| `/replica-entrepreneur` | Researches the app being cloned and reads what its real users say in public reviews (App Store, Google Play, G2, Capterra, Trustpilot, Reddit, Hacker News, its own feature-request board), then ranks what they hate, what is missing and what is unsolved, turns it into a fix plan for the clone and a… |
| `/replica-launch` | Writes the launch for an app clone: the landing page built on the positioning angle, pricing set against the original's public pricing and its users' complaints, and the App Store and Google Play listing linted against the stores' limits and copycat rules. |
| `/replica-recon` | Reverse-engineers any app into a recon map: screen inventory, user flows, component list, inferred data model and a feature matrix, from public pages, screenshots, app store listings, help docs and the user's own account. |
| `/replica-test` | Clicks through every flow of an app clone and tests it for bugs: a test plan generated from the recon flows with happy paths and edge cases, Playwright end-to-end tests where possible, a browser click-through where not, and bug reports in a fixed format with severity, steps and evidence. |

## Research (1)

What people said online in the last 30 days.

| Skill | What it does |
|---|---|
| `/last30days` | Research what people actually say about any topic in the last 30 days. Pulls posts and engagement from Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, and the web. |

## Writing & output style (2)

Make text sound human, or make Claude's replies ADHD-friendly.

| Skill | What it does |
|---|---|
| `/humanizer` | Rewrite AI-sounding text so it reads like the writer without changing what it says. Use when editing or reviewing prose for AI tells: not-X-but-Y contrasts, one-line closers, staged openers, forced triads, dashes everywhere, inflated claims, sales language, stock AI words, bold labels, or filler. |
| `/i-have-adhd` | Shape output for a reader with ADHD: lead with the next action, number multi-step work, restate state across turns, suppress tangents, give specific time estimates, make wins visible. |

## Superpowers (coding workflow) (15)

Careful coding habits: plan, test first, debug, verify.

| Skill | What it does |
|---|---|
| `/brainstorming` | You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning anything new, in software or out of it (a talk, a business, a renovation). |
| `/diagnosing-superpowers` | Use when a superpowers session went wrong and your human partner wants to know why — repeated work, ignored plans, stumbles, poor results, a skill that didn't fire, "it took too long", "why is it so expensive", "what is it doing" — or wants to build a bug report for the superpowers maintainers, for… |
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

## Engineering (8)

Website, backend, payments, email and code-review skills.

| Skill | What it does |
|---|---|
| `/code-reviewer` | Use for any code review: a pull request, a diff, a commit, or a pasted function, handler or file in TypeScript, JavaScript, Python, Go, Swift, Kotlin, C#/.NET, Java, C, C++, Rust, Ruby, PHP or Dart/Flutter. |
| `/email-template-builder` | Use when adding or reworking transactional email (React Email templates, Resend, Postmark, SendGrid or SES, preview, i18n, dark mode, deliverability). |
| `/epic-design` | Use for any landing page, hero section or scroll-driven web design that should feel cinematic (parallax, scrollytelling, overlapping sections, text reveals, Apple-style animation), before coding. |
| `/senior-backend` | Build and fix backend services: REST or GraphQL APIs, auth, microservices, PostgreSQL queries, migrations and load tests. |
| `/senior-frontend` | Build and review React, Next.js, TypeScript or Tailwind frontends: components, scaffolding, performance and bundle size. |
| `/senior-fullstack` | Start a fullstack project or audit a codebase: pick a stack (Next.js, FastAPI, MERN, Django), scaffold it and score code quality. |
| `/senior-prompt-engineer` | Improve prompts and measure LLM quality: fix inconsistent prompts, build eval sets, score RAG retrieval, check agent tool configs. |
| `/stripe-integration-expert` | Use for any Stripe integration: subscriptions, trials, proration, checkout, usage billing, webhooks, customer portal or invoicing in Next.js, Express or Django. |

## Advanced engineering (11)

AI agents, automation, MCP servers, databases, multilingual sites.

| Skill | What it does |
|---|---|
| `/agent-designer` | Design multi-agent systems (supervisor, swarm, pipeline) and tool schemas; find bottlenecks in run logs. |
| `/agent-workflow-designer` | Use when architecting a multi-step LLM or agent pipeline, choosing single vs multi-agent, or fixing context bloat and broken handoffs. |
| `/find-skills` | Find and install more agent skills. Use when you ask "is there a skill for X" or "how do I do X" and an installable skill might already exist. |
| `/browser-automation` | Automate a browser: scrape websites, fill forms, pull structured data from web pages. Use whenever the user wants to grab data from a site, fill a web form or extract a table. |
| `/database-designer` | Design a database schema: tables, relationships, indexes, normalization, SQL vs NoSQL, migration plans. |
| `/full-page-screenshot` | Use when asked for a full-page or long screenshot of a web page. Captures SPA scroll containers, lazy images and very tall pages through Chrome DevTools Protocol with no extra dependencies. |
| `/grill-me:grill-me` | Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. |
| `/i18n-localization` | Use when adding UI text, adding or shipping a language, reviewing translation files, or building i18n into an app. |
| `/karpathy-coder:karpathy-coder` | Check a diff for overbuilt code: hidden assumptions, needless abstraction, non-surgical changes, unverified goals (Karpathy's four principles). |
| `/mcp-server-builder` | Use when exposing an API as an MCP server or scaffolding a new MCP server in Python or TypeScript, before hand-writing tool wrappers. |
| `/rag-architect` | Design a RAG pipeline: chunk size, embedding model, vector database and retrieval quality metrics. |

## Playwright testing (10)

Write, fix and run website tests.

| Skill | What it does |
|---|---|
| `/pw:browserstack` | Use when running Playwright tests on BrowserStack or across a browser matrix ('browserstack', 'cross-browser', 'test on safari or firefox', 'browser compatibility'). |
| `/pw:coverage` | Find what is not tested: map untested pages and flows and coverage gaps. Use whenever the user asks what needs tests, about missing tests or test coverage. |
| `/pw:fix` | Diagnose and fix a failing or flaky Playwright test. Use whenever a test fails, passes only sometimes, breaks intermittently or needs fixing. |
| `/pw:generate` | Use when asked to write Playwright or e2e tests for a page, component or feature ('write tests', 'add tests for', 'e2e test'). |
| `/pw:migrate` | Use when moving tests from Cypress or Selenium to Playwright ('migrate tests', 'convert tests', 'replace selenium'). |
| `/pw:pw` | Use for any Playwright or end-to-end browser testing work: writing tests, fixing flaky ones, migrating from Cypress or Selenium, CI setup, TestRail or BrowserStack. |
| `/pw:pw-init` | Use when setting up Playwright in a project ('set up playwright', 'add e2e tests', 'configure playwright', 'init playwright'). |
| `/pw:pw-review` | Use when reviewing Playwright tests for quality ('review tests', 'audit tests', 'playwright best practices check'). |
| `/pw:report` | Summarize Playwright results. Use whenever the user asks how tests went, for a test report or status. |
| `/pw:testrail` | Use when syncing Playwright tests with TestRail ('testrail', 'sync test cases', 'push results to testrail', 'import from testrail'). |

## Vercel (React, Next.js & deploy) (9)

React and Next.js best practices, Vercel deploys and cost tuning, UI and writing reviews.

| Skill | What it does |
|---|---|
| `/deploy-to-vercel` | Deploy an app or website to Vercel and return the link, including a temporary preview deploy without logging in. |
| `/vercel-cli-with-tokens` | Deploy and manage Vercel projects with an access token instead of an interactive login, including environment variables. |
| `/vercel-optimize` | Cut Vercel cost and speed up a deployed Next.js, SvelteKit, Nuxt or Astro app, using its real metrics and usage. Needs the Vercel CLI. |
| `/vercel-composition-patterns` | React component patterns that scale: compound components, context providers, fewer boolean props. Includes React 19 changes. |
| `/vercel-react-best-practices` | React and Next.js performance rules from Vercel Engineering, for writing, reviewing or refactoring components and pages. |
| `/vercel-react-native-skills` | React Native and Expo best practices: fast lists, animations, native modules. |
| `/vercel-react-view-transitions` | Smooth page and element animations with React's View Transition API, including Next.js route changes. |
| `/web-design-guidelines` | Review UI code against Vercel's Web Interface Guidelines (accessibility, UX, design). Fetches the latest rules from GitHub each time. |
| `/writing-guidelines` | Review docs and other prose against Vercel's writing guidelines. Fetches the latest rules from GitHub each time. |

## Browser & Python (6)

Website automation, FastAPI and Python best practices.

| Skill | What it does |
|---|---|
| `/agent-browser` | Browser automation CLI for AI agents. Use when the user needs to interact with websites, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task. |
| `/ecc:api-design` | REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production APIs. |
| `/ecc:fastapi-patterns` | FastAPI best practices covering project structure, Pydantic v2 schemas, dependency injection, async handlers, authentication, authorization, transactional service layers, and testing with httpx and pytest. |
| `/ecc:python-patterns` | Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications. |
| `/ecc:python-testing` | Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements. |
| `/ecc:verification-loop` | Run a six-phase verification of a Claude Code session's work — build, type check, lint, tests with coverage, security grep, and diff review — then produce a PASS/FAIL verification report. |

## Self-improving memory (6)

Save lessons so Claude remembers them across sessions.

| Skill | What it does |
|---|---|
| `/self-improving-agent:extract` | Turn a fix or pattern that keeps coming up into a reusable skill with SKILL.md, reference docs and examples. |
| `/self-improving-agent:memory-review` | Review what the agent has learned in auto-memory: what to promote to permanent rules, stale entries to prune, duplicates to merge. |
| `/self-improving-agent:memory-status` | Health check of agent auto-memory: line counts, topic files, capacity, stale entries and what to prune. |
| `/self-improving-agent:promote` | Graduate a proven pattern from auto-memory (MEMORY.md) to CLAUDE.md or .claude/rules/ for permanent enforcement. |
| `/self-improving-agent:remember` | Save something important to auto-memory with a timestamp and context. Use whenever the user says remember this, note it for next time or don't forget, wants you to stop repeating a mistake across sessions, or a discovery is too important for auto-capture. |
| `/self-improving-agent:self-improving-agent` | Curate what the agent has learned into durable project knowledge. Reviews Claude Code auto-memory (MEMORY.md and its topic files) for learnings worth keeping, promotes proven ones into CLAUDE.md or .claude/rules/, records a correction as a lesson that persists across sessions, prunes stale or… |
