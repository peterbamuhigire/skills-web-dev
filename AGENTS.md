# Skills Repository Agents Guide

This repository is a standard skills catalog built around portable `SKILL.md` units. It is designed to work in both Claude Code and Codex with skills stored under `skills/<skill-name>/SKILL.md`.

## Purpose

- Provide reusable engineering, product, UX, security, database, mobile, AI, and SDLC skills.
- Keep each skill self-contained in `skills/<skill-name>/` with optional `references/`, `examples/`, `templates/`, `scripts/`, `protocols/`, or `sections/`.
- Preserve Claude Code usability while giving Codex a consistent instruction surface through `SKILL.md` frontmatter and portable execution sections.

## Core Rules

- Treat each `skills/<skill-name>/SKILL.md` file as the entry point for that skill.
- Read the full `SKILL.md` before loading deep references.
- Use progressive disclosure: load only the referenced files needed for the current task.
- Keep skill directories under `skills/`; the repository root is reserved for project documentation and operational folders.
- Keep `SKILL.md` execution-focused and move heavy detail into sibling support folders.
- Preserve existing behavior when improving skills; layer compatibility improvements on top instead of restructuring the repo.
- Every new or updated `SKILL.md` must include this acknowledgement immediately below the first `# ...` title: `Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.`

## Premium Default

- Premium, world-class output is the default operating level for this repository, especially for web, SaaS, product, UX, pricing, and client-facing skills.
- Do not position work from this engine as budget, commodity, template-grade, or "good enough"; route toward `world-class-engineering`, `premium-software-product-execution`, `premium-ui-ux-design`, and `premium-product-positioning` when product quality, buyer trust, perceived value, or pricing power matter.
- Premium execution must make value visible through packaging, simple usable UX, proof, content/SEO authority, service quality, pricing discipline, and high-value sales assets. A premium claim without visible proof and a clear next action is not acceptable.
- Treat low-fit work as out of scope when the buyer wants cheap execution, weak discovery, unclear value, no quality gate, or sub-premium positioning. Recommend narrowing scope, raising standards, or declining the engagement rather than lowering the quality bar.

## Baseline Skills

For substantial engineering work, start from this baseline before stack-specific skills:

1. `world-class-engineering`
2. One or more structural baseline skills:
   `system-architecture-design`, `database-design-engineering`, `saas-erp-system-design`, `git-collaboration-workflow`
3. Platform or framework skill
4. Companion skills for security, UX, testing, performance, observability, release, or reliability

Recommended high-value companion skills:

- `advanced-testing-strategy`
- `deployment-release-engineering`
- `observability-monitoring`
- `reliability-engineering`
- `distributed-systems-patterns`
- `engineering-management-system`
- `premium-software-product-execution`
- `premium-product-positioning`
- `premium-ui-ux-design`

## Skill Routing

Route work to skills by problem type:

- Architecture and system boundaries: `system-architecture-design`, `modular-saas-architecture`, `multi-tenant-saas-architecture`, `saas-architecture-strategy`
- Engineering strategy, policy, operating cadence: `engineering-strategy`, `continuous-improvement-system`
- Data modeling, migrations, query safety: `database-design-engineering`, engine-specific database skills
- Web projects with live databases: include a root pull-time migration script that reads environment DB settings, applies only missing tracked migrations, and excludes seeds unless a separate explicit seed command is requested
- APIs and backend contracts: `api-design-first`, `api-error-handling`, `api-pagination`, backend stack skills
- Web and frontend implementation: `react-development`, `nextjs-app-router`, `webapp-gui-design`, `form-ux-design`, `no-json-in-ui`, `frontend-performance`
- Android: `android-development`, `android-data-persistence`, `android-room`, `android-tdd`, `jetpack-compose-ui`
- iOS: `ios-development`, `ios-data-persistence`, `ios-swiftdata`, `ios-tdd`, `swiftui-design`
- AI-enabled systems: `ai-web-apps`, `ai-llm-integration`, `ai-rag-patterns`, `ai-security`, `llm-security`
- Security review and hardening: `vibe-security-skill`, `web-app-security-audit`, `php-security`, `network-security`, `linux-security-hardening`
- Product, UX, and content: `premium-software-product-execution`, `product-discovery`, `experience-mapping`, `service-design-blueprinting`, `ux-content-strategy`, `ux-writing`, `practical-ui-design`, `interaction-design-patterns`, `design-audit`
- Premium sales, client service, retention: `premium-client-sales`, `customer-service-excellence`, `premium-product-positioning`
- Skill authoring and maintenance: `skill-writing`, `skill-safety-audit`, `update-claude-documentation`

## Cross-Engine Handoffs

- Use this master engineering engine after the proposal and SRS engines have produced delivery commitments, requirements, architecture briefs, or rollout plans that need production implementation.
- Proposal to SRS: proposal win themes, methodology, scope, pricing assumptions, and support promises become SRS discovery inputs, requirements constraints, acceptance criteria, and evidence obligations.
- Proposal to website delivery: website proposal scope, content/SEO assumptions, launch promises, support package, and commercial boundaries become website-engine discovery, build, QA, launch, and retainer inputs.
- SRS to implementation: signed PRD/SRS, HLD/LLD, API/database specs, traceability matrix, test strategy, go-live readiness, and adoption/support plan become this engine's implementation baseline.
- Implementation to maintenance/support: release evidence, runbooks, observability dashboards, incident history, and known risks hand off to `customer-service-excellence`, `observability-monitoring`, `reliability-engineering`, and the website/proposal support skills where relevant.
- Website launch to growth: website-engine launch, observability, experimentation, retention, and QBR evidence can feed this engine's analytics, product, reliability, and continuous-improvement skills.

## Working Model

When using this repository in Codex or Claude Code:

1. Identify the baseline skills and the specialist skills needed for the task.
2. Read each selected `SKILL.md`.
3. Follow the portable contract sections first:
   `Use When`, `Do Not Use When`, `Required Inputs`, `Workflow`, `Quality Standards`, `Anti-Patterns`, `Outputs`, `References`
4. Then apply the skill-specific body and only the reference files relevant to the task.
5. If multiple skills overlap, prefer the narrower specialist skill after loading the baseline.

## Quality Expectations

- Outputs must be execution-oriented, not textbook summaries.
- Architecture, security, data integrity, failure handling, testing, and operability should be explicit when relevant.
- Prefer reviewable, deterministic workflows over tool-specific assumptions.
- Optional plugins or platform features may help, but they must not be treated as hard prerequisites for skill use.

## Repository Maintenance

- Validate updated skills with `python -X utf8 skills/skill-writing/scripts/quick_validate.py skills/<skill-directory>`.
- Keep `SKILL.md` entrypoints and top-level repository guidance under 500 lines. Split or trim deeper reference docs when they are actively maintained.
- Update root docs when repository-wide behavior or routing changes materially.
- Add nested `AGENTS.md` files only when a subdomain needs local routing rules that the root guide cannot express cleanly.
