# Skills Repository

This repository is a curated catalog of reusable AI skills: compact execution
guides that help agents and humans do higher-quality work with less repeated
setup. The skills cover software engineering, AI systems, SaaS operations,
security, product work, UX, mobile development, documentation workflows, and
canonical finance doctrine.

The catalog is designed to be routed by name. A small active surface keeps
skill selection reliable, while deeper references stay available without making
every topic an active entrypoint.

## Why These Skills Matter

| Benefit | What it gives you |
| --- | --- |
| Faster execution | Reusable workflows reduce repeated prompting and rediscovery. |
| Better routing | Clear frontmatter, aliases, and parent skills help agents pick the right guidance. |
| Higher quality | Skills encode checklists, quality gates, anti-patterns, and evidence expectations. |
| Safer specialization | Finance, security, AI, and platform work keep domain constraints close to implementation guidance. |
| Portable knowledge | Markdown, YAML, templates, and scripts work across Windows, Ubuntu, and Debian consumers. |
| Lower catalog noise | Legacy and narrow topics route through aliases instead of competing as duplicate active skills. |
| Enforced quality | CI gates fail the build on broken references, stale aliases, duplicates, oversized files, or a routing regression - the catalogue stays an engine, not a stale pile. |
| Maintainable handoff | Meaningful work closes with a Delivery Definition of Done pack (tests, release, rollback, runbook, maintenance notes). |

## Active Catalog

Active skills are `SKILL.md` files under these roots:

| Root | Purpose |
| --- | --- |
| [`skills/`](skills/) | Main active catalog for engineering, AI, SaaS, mobile, security, UX, product, and operations. |
| [`doctrine/skills/`](doctrine/skills/) | Canonical finance and accounting doctrine for IFRS, controls, close, audit, payroll, inventory, reporting, and finance UX. |
| [`00-meta-initialization/`](00-meta-initialization/) | SDLC documentation initialization and new-project entrypoints. |

Current guardrail baseline:

| Metric | Value |
| --- | ---: |
| Active `SKILL.md` files | 175 |
| Target active catalog size | 150-170 |
| Guardrail hard cap | 200 |
| Duplicate frontmatter names | 0 |
| Near-duplicate skill pairs (collision-checked) | 0 |
| Inactive aliases retained as `ALIAS.md` | 48 |

The guardrail script is the source of truth for these numbers; the table above is
a convenience snapshot. Rerun the report after any catalog change rather than
trusting the prose. The active count sits 3 above the 150-170 soft target (well
under the 200 hard cap). Routing quality is no longer judged by raw count alone:
`scripts/routing_smoke_test.py` measures routing precision against a task fixture
(currently precision@1 87%, precision@3 100%) and its `--collisions` mode
confirms zero genuine duplicate skills - every remaining high-similarity pair is
an intentional platform split (iOS/Android) or concern split (engineering/ops).
The remaining skills are distinct and deliberately retained.

Run the guardrail report with:

```powershell
python -X utf8 scripts\skill_catalog_guardrails.py --report-only
```

## Skill Domains

| Domain | Examples |
| --- | --- |
| AI and agent systems | AI architecture, RAG, evaluations, model gateways, agent runtime, HITL, governance, observability, cost controls, and AI UX. |
| Software engineering | Architecture, APIs, C#/.NET, TypeScript, JavaScript, PHP, Python, Node.js, testing, validation, release engineering, and reliability. |
| SaaS and product | Multi-tenancy, entitlements, pricing, billing, onboarding, metrics, sales operations, product discovery, and product-led growth. |
| Security and compliance | Web app audits, code safety, network security, Linux hardening, DPIA work, and AI security controls. |
| Frontend and UX | React, Next.js, Tailwind, app GUI design, forms, interaction patterns, accessibility, premium UI, and motion. |
| Mobile | Android, iOS, Kotlin Multiplatform, mobile persistence, mobile UX, platform capabilities, app quality, and release workflows. |
| Finance doctrine | Accounting engines, finance audits, bank and mobile money reconciliation, close, controls, reporting, IFRS, payroll, inventory, and finance UI patterns. |
| Documentation and operations | SDLC documentation, project requirements, professional document output, catalog maintenance, skill writing, and update records. |
| Quality guardrails (cross-cutting) | `anti-ai-slop` is a real-time guardrail applied continuously on every generated output. `ai-slop-audit` runs after each major iteration and auto-runs on any request to analyse/review/audit/de-slop any artefact type (app, website, business plan, SRS/spec, proposal, blog, social post, document, image, or codebase); a grade-F verdict blocks progression. |

## How To Use The Catalog

1. Start with the active roots above or the overview in
   [`docs/overview/README.md`](docs/overview/README.md).
2. If an old skill name is mentioned, check
   [`docs/skill-routing-index.md`](docs/skill-routing-index.md) or
   [`docs/skill-aliases.yml`](docs/skill-aliases.yml).
3. Read the selected skill's `SKILL.md`.
4. Load only the specific `references/`, `templates/`, or `scripts/` files the
   skill tells you to use.
5. When changing routing, frontmatter, or active skill behavior, update the
   routing docs and rerun the guardrail report.

## Routing And Aliases

The catalog intentionally keeps aliases outside the active skill count. Legacy
entrypoints that should no longer compete for routing are retained as
`ALIAS.md` files in their original directories. Their targets are recorded in:

- [`docs/skill-routing-index.md`](docs/skill-routing-index.md) for human-readable policy.
- [`docs/skill-aliases.yml`](docs/skill-aliases.yml) for machine-readable routing.

Finance aliases route to `doctrine/skills/` first. Root-level finance skills
remain active only when they add implementation or orchestration behavior beyond
canonical doctrine.

## Repository Map

| Path | Role |
| --- | --- |
| [`docs/`](docs/) | Overview docs, architecture, routing policy, plans, analysis, and update records. |
| [`.github/workflows/`](.github/workflows/) | CI gates: catalog guardrails and routing smoke test on every push and PR. |
| [`scripts/`](scripts/) | Catalog guardrail validator, routing smoke test (`routing_smoke_test.py` + `routing_fixtures.yml`), and setup helpers. |
| [`claude-guides/`](claude-guides/) | Claude-specific skill creation and invocation guidance. |
| [`book-extractions/`](book-extractions/) | Curated source notes and long-form reference material. |
| [`blog-posts/`](blog-posts/) | Draft educational and marketing content. |

## Maintenance Rules

- Do not delete or move skill directories casually.
- Deactivate legacy entrypoints by renaming `SKILL.md` to `ALIAS.md` and adding
  a route in `docs/skill-aliases.yml`.
- Keep finance and accounting doctrine canonical under `doctrine/skills/`.
- Keep Markdown files below 500 lines where practical.
- Use ASCII unless an existing file requires another character set.
- Preserve user edits and inspect the worktree before modifying files.
- Record substantive documentation repairs under [`docs/updates/`](docs/updates/).

## Key Docs

| Document | Purpose |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Short working rules for coding agents. |
| [`docs/overview/PROJECT_BRIEF.md`](docs/overview/PROJECT_BRIEF.md) | One-page project brief. |
| [`docs/overview/ARCHITECTURE.md`](docs/overview/ARCHITECTURE.md) | Repository structure and ownership boundaries. |
| [`docs/overview/TECH_STACK.md`](docs/overview/TECH_STACK.md) | Tooling, runtime assumptions, and platform notes. |
| [`docs/plans/INDEX.md`](docs/plans/INDEX.md) | Planning document index. |
| [`docs/plans/NEXT_FEATURES.md`](docs/plans/NEXT_FEATURES.md) | Current priorities and next work. |
| [`docs/USING-IN-A-PROJECT.md`](docs/USING-IN-A-PROJECT.md) | How to apply the catalogue in a real project without copying doctrine. |
| [`docs/CLIENT-VALUE-BRIEF.md`](docs/CLIENT-VALUE-BRIEF.md) | Plain-language value statement for clients (architecture-free). |
