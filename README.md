# Skills Web Dev

`skills-web-dev` is the Chwezi Core Systems software-engineering engine for turning a product decision into well-understood, maintainable software and an operable release. It routes work to the smallest accurate skill and develops it in traceable vertical slices—requirements, architecture, data flow, interaction detail, code, tests, security, observability, performance, rollback, and handoff—so speed from AI does not replace engineering judgement or finish quality.

Engineers, architects, product and delivery teams, and operators use it for AI systems, SaaS, APIs, databases, frontend and mobile applications, games, security, DevOps, cloud, reliability, and SDLC documentation. The route helps them frame the problem, choose system boundaries, make changes, and verify normal and failure paths.

Use it for engineering implementation and SDLC quality; bring in companion engines when ownership moves to visual design, finance and accounting, current external research, premium website operations, or formal requirements and governance. Its boundary is deliberate: it provides the engineering route and evidence expectations, while those specialist engines retain their own domain rules and outputs.

## Capability map

| Need | Primary route |
|---|---|
| AI applications, agents, RAG, gateways, evaluations, and AI safety | `skills/ai/` |
| Architecture, APIs, distributed systems, and contracts | `skills/architecture/` |
| Databases, persistence, migrations, and data reliability | `skills/backend-databases/` |
| Frontend, mobile, TypeScript, Python, PHP, .NET, and enterprise Java/JVM implementation | `skills/frontend-ux/`, `skills/android/`, `skills/ios/`, `skills/languages/` |
| SaaS, billing, tenancy, entitlements, SSO, and admin tooling | `skills/saas/` |
| Security, cloud, deployment, observability, reliability, and testing | `skills/security/`, `skills/devops-cloud/`, `skills/sdlc-meta/` |
| Product, documents, spreadsheets, and delivery control | `skills/product-business/` |
| Game development and production | `skills/game-development/` |

## Current status

Last verified: 2026-09-07.

| Measure | Result |
|---|---:|
| Active `SKILL.md` files | 179 |
| Guardrail maximum | 200 |
| Routing fixtures | 158 |
| Routing precision@1 | 91% (144/158) |
| Routing precision@3 | 100% (158/158) |
| Catalog guardrail findings | 0 |
| July portfolio audit baseline | 63/100, capped |
| Improvement-plan target | 95/100 |

The active count is produced by the guardrail script. Do not update this table after adding or removing skills without rerunning the validators.

### September 2026 Kaizen execution update

The first engineering implementation wave corrected two purpose-critical
examples identified in the current Kaizen plan. The database reliability
example now converts the weekly error-budget ratio to a percentage explicitly
and defines latency errors as events above the SLO boundary rather than the
within-boundary histogram bucket. The multi-tenant permission example now
evaluates tenant-scoped user denial before a narrowly scoped administrative
super-admin bypass and keeps the action audited.

Added regression coverage in
`tests/test_kaizen_semantic_examples.py`. The targeted tests pass, and the
repository routing smoke test passes at 158/158 top-three fixtures. These
changes validate the examples and documentation contract; they do not certify
a running database, tenant isolation, production SLOs, or security posture.
The next planned experiment is the isolated FieldOps slice, subject to the
buyer, environment, finance and operations dependencies in the portfolio plan.

## Start here

1. Read [`SKILL.md`](SKILL.md) for routing, cross-engine ownership, release workflow, and stop conditions.
2. Read [`AGENTS.md`](AGENTS.md) for repository operating rules.
3. Use [`docs/skill-routing-index.md`](docs/skill-routing-index.md) to select the smallest accurate route.
4. Read the selected domain `SKILL.md`, then only the references, templates, and examples it names.
5. For an engine audit, product audit, book-driven upgrade, or post-iteration learning cycle, load [`skills/sdlc-meta/kaizen-improvement-system/SKILL.md`](skills/sdlc-meta/kaizen-improvement-system/SKILL.md).
6. For multi-engine agents, commands, hooks, evidence, or handoffs, load [`skills/sdlc-meta/engine-control-plane/SKILL.md`](skills/sdlc-meta/engine-control-plane/SKILL.md) and validate [`docs/engine-control-plane.json`](docs/engine-control-plane.json).

## Detailed capability routes

| Work type | Primary route |
|---|---|
| AI applications, agents, RAG, gateways, evaluations, human oversight, AI safety and cost | `skills/ai/` |
| APIs, distributed systems, architecture decisions, contracts, migrations and platform engineering | `skills/architecture/` |
| SQL, MySQL, PostgreSQL, schemas, persistence, data reliability and database operations | `skills/backend-databases/` |
| CI/CD, cloud, containers, Kubernetes, deployment, observability, SLOs and reliability | `skills/devops-cloud/` |
| React, Next.js, Tailwind, frontend performance, content UX and web implementation | `skills/frontend-ux/` |
| Android, iOS, Kotlin Multiplatform, PWA and mobile operations | `skills/android/`, `skills/ios/`, `skills/mobile-cross/` |
| TypeScript, JavaScript, Python, PHP, C#/.NET, and enterprise Java/JVM work | `skills/languages/` |
| SaaS tenancy, pricing, billing, entitlements, SSO/SCIM, portability and administration | `skills/saas/` |
| Threat modelling, secure coding, privacy, DPIA, Linux hardening and network security | `skills/security/` |
| Product discovery, metrics, delivery control, proposals, documents and spreadsheets | `skills/product-business/` |
| Games, interactive narrative, game AI, navigation, playtesting and production orchestration | `skills/game-development/` |
| Requirements, architecture documentation, testing, deployment and governance initialization | `skills/sdlc-meta/`, `00-meta-initialization/` |

## Kaizen operating contract

The [2026-09-06 sequential audit](docs/audits/2026-09-06-kaizen/portfolio-progress.md)
records current implementation, baseline failures and remaining evidence gaps.

For a ready-to-run product or project operation, use [`prompts/full-kaizen-operation.md`](prompts/full-kaizen-operation.md).

Continuous improvement is part of the engine, not an optional review activity. Apply this cycle to the engine and to products it produces:

`Observe -> Baseline -> Select -> Experiment -> Check -> Standardise -> Teach -> Re-measure`

The Kaizen skill applies to websites, web/mobile/desktop apps, AI systems, SaaS, APIs, databases, games, infrastructure, and SDLC artefacts. Every audit must:

- inventory routes, skills, references, validators, outputs, and known failures;
- score applicable dimensions with named evidence;
- publish `min(raw_score, 65)` as the audit score;
- keep the raw score and blockers visible;
- produce a gap-to-95 plan with exact files, owners, measures, acceptance evidence, risks, and rollback;
- run a reversible experiment and independent check;
- standardise successful learning in a skill, reference, template, fixture, router, or release gate;
- record the next review date.

The 65/100 ceiling is a reporting rule, not permission to stop at mediocre quality. A plan may target 95/100, but 95 must not be claimed until the evidence exists.

For product audits, assess the applicable combination of requirements, architecture or document correctness, security and privacy, accessibility, reliability, performance, user value, operations, handoff, rollback, and evidence quality. Distinguish defects, risks, assumptions, and unassessed areas.

## 16-book Kaizen upgrade

The engine was upgraded using a structured synthesis of the 16-book portfolio. Books were converted into concise skills, references, evidence requirements, and learning loops; raw book text is not copied into the repository.

| Book themes | Capabilities now represented in this engine |
|---|---|
| Agile/XP, LEAN and Kaizen | Hypothesis-led delivery, value retrospectives, small reversible experiments, evidence-based standardisation, and product feedback loops |
| Platform Enterprise and Tech Lead | Platform-as-product ownership, internal-consumer feedback, cognitive-load reduction, sociotechnical architecture, role clarity, transparent communication, and sustainable ownership |
| Designing for AI | Problem-first AI selection, human/AI/system separation, model-versus-system boundaries, user control and correction, oversight, drift monitoring, and rollback |
| Digital Storytelling and Video Game Storytelling | Narrative/gameplay contracts, player-verb mapping, branch/rejoin reasoning, character intent, cross-discipline language, and narrative playtesting |
| AI for Game Developers | Instrumented behaviour state machines, steering and navigation, behaviour recovery, deterministic fallbacks, telemetry, and warnings about dated APIs or assumptions |
| MSC Software Magazine | Model and simulation lineage, assumptions, independent verification, correlation evidence, sustainability context, and production decision traceability |
| Dynamic Characters and Anatomy for Artists | Game visual readability, silhouette and pose review, composition and value separation, design-to-model handoff, and explicit quarantine of unusable source extraction |
| Strategic planning, facility moves and expert practice | Scope and decision rights, baseline and readiness, continuity and cutover, stabilisation, stakeholder evidence, expert boundaries, and knowledge-product pipelines |

Book-derived references include:

- [`kaizen-game-production-loop.md`](skills/game-development/game-development-orchestration/references/kaizen-game-production-loop.md)
- [`kaizen-ai-product-loop.md`](skills/ai/ai-feature-rollout-and-experimentation/references/kaizen-ai-product-loop.md)
- [`platform-as-product-feedback.md`](skills/architecture/system-architecture-design/references/platform-as-product-feedback.md)
- [`delivery-feedback-evidence.md`](skills/devops-cloud/deployment-release-engineering/references/delivery-feedback-evidence.md)
- [`behaviour-telemetry-and-tuning.md`](skills/game-development/game-ai-behaviour-and-navigation/references/behaviour-telemetry-and-tuning.md)
- [`narrative-playtest-loop.md`](skills/game-development/game-narrative-and-interactive-story-design/references/narrative-playtest-loop.md)
- [`engine-and-product-audit-evidence-matrix.md`](skills/sdlc-meta/skill-engine-audit/references/engine-and-product-audit-evidence-matrix.md)
- [`tech-lead-learning-loop.md`](skills/sdlc-meta/world-class-engineering/references/tech-lead-learning-loop.md)

The implementation record and adoption plan are in [`docs/continuous-improvement/`](docs/continuous-improvement/). The historical upgrade records remain in [`docs/engine-upgrade-july-2026/`](docs/engine-upgrade-july-2026/).

## September 2026 book-driven Kaizen wave

The portfolio study and implementation record is in
[`docs/continuous-improvement/book-driven-kaizen-2026-09-01.md`](docs/continuous-improvement/book-driven-kaizen-2026-09-01.md). It adds algorithm selection as a routed capability and strengthens AI collaboration, data-foundation, and metadata-platform quality references.

## Delivery workflow

For any substantial deliverable:

1. Define the decision, audience, constraints, success measure, and failure consequences.
2. Route to the smallest domain skill and load its required references.
3. Use current source verification for volatile AI, cloud, framework, security, legal, or standards claims.
4. Produce the artefact with its evidence pack, not as unsupported prose or code alone.
5. Verify normal paths, failure paths, security, accessibility, performance, operations, and rollback as applicable.
6. Run the anti-slop gate and the relevant domain tests.
7. Record the release verdict and feed defects, incidents, feedback, evals, playtests, and postmortems into the Kaizen backlog.

The standard evidence pack is [`templates/delivery-dod/evidence-pack.md`](templates/delivery-dod/evidence-pack.md). It should normally contain a decision record, contract evidence, test evidence, security evidence, operational evidence, source/currency evidence, anti-slop verdict, and release decision.

## Cross-engine routing

This engine owns engineering implementation and SDLC quality. It does not replace specialist doctrine:

| Need | Route with this engine to |
|---|---|
| Current web, AI, cloud, security, framework, standards, or market evidence | <a href="https://github.com/peterbamuhigire/digital-research-skills" target="_blank" rel="noopener noreferrer">Digital Research Engine</a> at `C:\wamp64\www\digital-research-engine` |
| IFRS, accounting, tax, payroll, treasury, close, audit, or statutory values | <a href="https://github.com/peterbamuhigire/chwezi-accounting-doctrine" target="_blank" rel="noopener noreferrer">Chwezi Accounting Doctrine</a> |
| Typography, visual design, UI appearance, design systems, document/slides/spreadsheet presentation | <a href="https://github.com/peterbamuhigire/design-system-skills" target="_blank" rel="noopener noreferrer">Design System Skills</a> |
| Premium website strategy, content, SEO, conversion, launch operations, and website orchestration | <a href="https://github.com/peterbamuhigire/website-skills" target="_blank" rel="noopener noreferrer">Website Skills</a> |
| Formal standards-driven SRS, requirements, architecture, testing, deployment, and governance artifacts | <a href="https://github.com/peterbamuhigire/srs-skills" target="_blank" rel="noopener noreferrer">SRS Skills</a> |

Current claims must be verified through Digital Research. Do not infer current platform capabilities from a historical book or an early-release book chapter.

## Validation

Run these commands from the repository root after routing, frontmatter, reference, template, fixture, or catalog-policy changes:

```powershell
python -X utf8 scripts\skill_catalog_guardrails.py --report-only
python -X utf8 scripts\routing_smoke_test.py --report-only
```

Expected counts and routing results must be taken from the current validator output, not this prose. Also run the relevant domain tests, anti-slop gate, evidence-pack checks, and `git diff --check` for the changed workstream.

## Honest limitations

- Routing precision@1 is 91%; precision@3 is 100%. The engine still requires human review for close domain collisions.
- The 179 active skills remain below the hard cap of 200, but catalogue size alone is not proof of quality or production readiness.
- Some book inputs are historical, partial early releases, or have unusable extraction. They inform patterns only where the available text supports them; current claims require independent verification.
- `AI for Game Developers` contains durable algorithmic foundations but dated APIs and production assumptions. Treat it as conceptual input, not current platform documentation.
- Game and design guidance does not replace hands-on playtesting, visual review, accessibility testing, security testing, or production telemetry.
- A green catalog or routing test proves repository integrity and route selection, not that a downstream product is correct, safe, accessible, performant, or ready to ship.
- Finance, visual design, live research, premium website operations, and formal SRS doctrine remain owned by their canonical companion engines.

## Repository map

| Path | Purpose |
|---|---|
| `skills/` | Main active engineering catalog |
| `00-meta-initialization/` | Documentation initialization and project setup skills |
| `docs/` | Routing, plans, quality gates, source registers, and upgrade records |
| `examples/` | Sanitised end-to-end workflow examples |
| `templates/` | Reusable evidence, architecture, API, security, and reliability templates |
| `references/` | Shared engineering standards and ownership references |
| `scripts/` | Catalog guardrails and routing smoke tests |
| `tests/` | Routing fixtures and negative quality fixtures |
| `docs/engine-control-plane.json` | Eleven-engine agent/command/hook/evidence registry |
| `scripts/validate_engine_control_plane.py` | Deterministic registry and local-router validator |

## Maintenance rules

- Preserve existing user work and do not move, delete, or rename skill directories during routine documentation work.
- Keep active skills below the 200 hard cap and add routing fixtures when a new skill could collide with an existing route.
- Update documentation when routing, catalog policy, scripts, or active skill behaviour changes.
- Keep book inputs outside the active repository as temporary research inputs; commit only concise, attributed, independently structured synthesis.
- Keep Markdown below 500 lines where practical.
- Use the owning specialist engine instead of duplicating its doctrine.
