# Skills Repository Overview

This repository is a working catalog of reusable AI-assistant skills and
supporting documentation. It combines implementation guidance, product strategy,
security patterns, finance-doctrine orchestration, mobile development guidance, SDLC
documentation templates, and catalog maintenance tooling.

## Latest Update

The [2026-09-06 Kaizen cycle](../audits/2026-09-06-kaizen/portfolio-progress.md)
repairs portfolio path resolution, evidence-gate coverage and portable
contract checks. Its evidence distinguishes structural checks from product proof.

The 2026-09-05 enterprise Java addition established one consolidated Java/JVM
route for language and runtime engineering, Spring and Jakarta EE, persistence,
Oracle integration, build/test/security, production diagnostics, deployment,
and staged modernisation. Current platform facts live in a dated source register;
generic architecture, data, security, cloud, SaaS, AI, and finance decisions
remain with their existing owners.

The 2026-08-16 seeding retrospective strengthened full-coverage SaaS seeding
with explicit run classes, schema-compatibility gates, controlled writer-gap
exceptions, branch/facility scope, deterministic time windows, hierarchy
closure checks, partial-failure ledgers, and per-runner replay/reset tests.

The 2026-08-16 POS operations addition established a live ERP POS engineering
route for the three operational POS surfaces, tenant-wide default customers,
product-to-finished-stock identity, manufacturing-versus-sale stock timing,
canonical posting, permissions, idempotency, and reconciliation evidence.

The 2026-08-02 coding-agent optimisation addition added a device-aware workflow
for safely tuning Codex and Claude Code, with a secret-free inventory script,
thin runner adapters, routing fixtures, and rollback-aware verification.

The 2026-06-21 WWDC26 modernization updated the existing Apple and mobile skills
without adding new active entrypoints. The catalog now routes current Apple work
through iOS development, AI/ML, App Intents/Siri/Spotlight, quality/release,
security, StoreKit, PWA/Safari, KMP, and mobile operations guidance, while
presentation-layer Apple UI guidance lives in the external
<a href="https://github.com/peterbamuhigire/design-system-skills" target="_blank" rel="noopener noreferrer">Design System Skills Engine</a>.

## What Is Here

| Area | Location | Notes |
| --- | --- | --- |
| Main skill catalog | `skills/` | Broad software, AI, SaaS, mobile, security, UX, and product skills. |
| Finance doctrine | External <a href="https://github.com/peterbamuhigire/chwezi-accounting-doctrine" target="_blank" rel="noopener noreferrer">Chwezi Accounting Doctrine</a> | Canonical accounting, audit, reporting, IFRS, controls, and close guidance is loaded from the external engine. |
| SDLC initialization | `00-meta-initialization/` | Entry-point project documentation workflow and examples. |
| Routing docs | `docs/skill-routing-index.md` | Human-readable consolidation and routing policy. |
| Alias data | `docs/skill-aliases.yml` | Machine-readable skill alias map. |
| Source registers | `docs/source-registers/` | Dated official/current references for volatile platform, AI, security, and framework facts. |
| Quality gates | `docs/quality-gates/` | Release blockers and engineering anti-slop governance. |
| Full workflow example | `examples/full-stack-saas-reference/` | FieldOps Ledger end-to-end SaaS evidence pack. |
| Delivery templates | `templates/delivery-dod/` | Reusable evidence-pack template for implementation deliverables. |
| Maintenance scripts | `scripts/` | Guardrail validator, routing smoke test, and setup helpers. |
| Engine control plane | `docs/engine-control-plane.json`, `skills/sdlc-meta/engine-control-plane/` | Shared agents, commands, hooks, evidence, handoffs, and bounded recovery across eleven engines. |
| CI gates | `.github/workflows/skill-guardrails.yml` | Runs the guardrails and routing smoke test on every push and PR. |
| Integrator + client docs | `docs/USING-IN-A-PROJECT.md`, `docs/CLIENT-VALUE-BRIEF.md` | How to apply the catalogue in a real repo; plain-language client value. |
| Long-form references | `book-extractions/`, `claude-guides/`, `blog-posts/` | Source material and companion writing. |

## How To Work In This Repo

1. Identify the relevant skill or routing entry.
2. Read the skill `SKILL.md` and only the references needed for the task.
3. Keep skill frontmatter concise and accurate.
4. Update routing docs when a parent skill absorbs or supersedes another skill.
5. Run both gates before finishing catalog maintenance (CI runs the same two):

   ```powershell
   python -X utf8 scripts\skill_catalog_guardrails.py --report-only
   python -X utf8 scripts\routing_smoke_test.py --report-only
   ```

## Current Catalog Policy

- Active roots are `skills/` and `00-meta-initialization/`.
- Target active catalog size is 150-170 skills.
- The guardrail hard cap is 200 active `SKILL.md` files.
- Finance doctrine is canonical in the external <a href="https://github.com/peterbamuhigire/chwezi-accounting-doctrine" target="_blank" rel="noopener noreferrer">Chwezi Accounting Doctrine</a>
  engine; reference-only checkouts stay outside the runtime skill catalog.
- Current active catalog size is 179 skills. This is nine above the 150-170 soft target after intentional
  capability additions and remains below the enforced hard cap of 200.
- Current routing smoke-test suite contains 158 fixtures, with 91% precision@1
  (144/158) and 100% precision@3 (158/158).
- Inactive aliases are retained as `ALIAS.md` and routed through
  `docs/skill-aliases.yml`.
- Duplicate finance entrypoints under `skills/finance/` have been deactivated
  and route to retained finance references or the external finance engine.

## Enforced Invariants

The catalogue is a gated engine, not just a document set. Two scripts run in CI
(`.github/workflows/skill-guardrails.yml`) and fail the build on:

- duplicate frontmatter names, over-cap active count, oversized `SKILL.md`,
  over-length descriptions, malformed frontmatter;
- broken `references/`/`templates/` links and stale or dangling aliases;
- a fixtured routing task whose expected skill drifts out of its top matches
  (routing precision is measured, not assumed).

Meaningful implementation work also carries a Delivery Definition of Done pack
(`skills/sdlc-meta/skill-composition-standards/references/delivery-definition-of-done.md`):
tests, release plan, rollback plan, runbook, and maintenance notes, so output is
operable by a team that did not write it.

## Related Docs

- [Project brief](PROJECT_BRIEF.md)
- [Tech stack](TECH_STACK.md)
- [Architecture](ARCHITECTURE.md)
- [Plans index](../plans/INDEX.md)
- [Next features](../plans/NEXT_FEATURES.md)
- [Agent guide](../../AGENTS.md)
- [Using the catalogue in a project](../USING-IN-A-PROJECT.md)
- [Client value brief](../CLIENT-VALUE-BRIEF.md)
- [Production-readiness audit](../evaluation/2026-05-30-production-readiness-audit.md)
