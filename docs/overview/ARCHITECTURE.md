# Architecture

## System Shape

The repository is a file-based knowledge system. Skill entrypoints live in
`SKILL.md` files, deep references sit beside those skills, and repository-level
docs describe routing, consolidation, planning, and maintenance policy.

## Main Components

| Component | Responsibility |
| --- | --- |
| `skills/` | Main skill catalog for engineering, AI, SaaS, mobile, game development, security, UX, product, and operations, including C#/.NET and consolidated enterprise Java/JVM entrypoints. |
| External `chwezi-accounting-doctrine` checkout | Canonical finance doctrine; kept outside the runtime skill catalog. |
| `00-meta-initialization/` | Entry-point workflow for SDLC documentation setup. |
| `docs/skill-routing-index.md` | Human routing map for consolidated and legacy skill names. |
| `docs/skill-aliases.yml` | Machine-readable alias registry. |
| `docs/source-registers/` | Dated official/current sources for volatile AI, Apple, cloud, security, and framework guidance. |
| `docs/quality-gates/` | Release-blocking gates and engineering anti-slop governance. |
| `docs/world-class-exemplars/` | Shared running example and benchmark reference outputs. |
| `examples/full-stack-saas-reference/` | End-to-end SaaS evidence pack exercising architecture, API, security, reliability, and release skills. |
| `templates/delivery-dod/` | Shared delivery evidence pack template for implementation outputs. |
| `scripts/skill_catalog_guardrails.py` | Static guardrail scan: active count, duplicate names, frontmatter, UTF-8, description length, `SKILL.md` line count, broken `references/`/`templates/` links, and alias integrity (unrouted, stale, dangling). |
| `scripts/routing_smoke_test.py` + fixture YAML files | Routing precision measurement: scores fixtured tasks from `scripts/routing_fixtures.yml` and `tests/routing/edge-fixtures.yml` against skill descriptions and fails when an expected skill drifts out of its top matches. `--collisions` reports near-duplicate skills. |
| `docs/engine-control-plane.json` + `scripts/validate_engine_control_plane.py` | Shared eleven-engine registry and deterministic validation for agents, commands, hooks, evidence, and local routers. |
| `.github/workflows/skill-guardrails.yml` | CI: runs both gates on every push and PR touching skills, doctrine, aliases, fixtures, or the scripts. |
| `skills/sdlc-meta/skill-composition-standards/references/` | Artifact templates (ADR, entity model, threat model, release/rollback plan, runbook, test plan) and the closing Delivery Definition of Done pack. |
| `skills/languages/python-modern-standards/scripts/desktop_suite_packager.py` | Model-neutral project generator for a committed desktop-suite manifest, generated launcher/spec/installer/CI files, stale-generation check, and release evidence. |
| `skills/languages/java-enterprise-development/` | One active Java/JVM implementation route with progressively loaded references for Spring, Jakarta EE, Oracle, persistence, build/test/security, production operations, and modernisation. |
| `skills/ios/` and `skills/mobile-cross/` | Apple/mobile implementation guidance, including WWDC26-era Xcode, Swift, Foundation Models/Core AI, App Intents, StoreKit, PWA/Safari, KMP, release, and security references. |
| `skills/game-development/` | Game orchestration, lean experiments, design, mathematics/simulation, graphics, Unity/Godot/Unreal, Apple delivery, multiplayer/backend, security, 2D/3D content, audio, performance, build/release, testing, data/live economy, accessibility/player safety, studio operations, and live operations. |
| `claude-guides/` | Skill authoring and Claude-specific usage guidance. |
| `book-extractions/` | Long-form source notes and reference summaries. |

## Skill Loading Model

An active skill is any `SKILL.md` under:

- `skills/`
- `00-meta-initialization/`

Reference material should be stored under directories such as `references/`,
`sections/`, `templates/`, `assets/`, or examples, not as extra `SKILL.md`
files. This keeps active skill count controllable.

Legacy entrypoints that should not be active are kept in-place as `ALIAS.md`.
Those files preserve historical content without participating in loader
routing.

## Routing Model

When multiple narrow skills overlap, prefer one retained parent skill and route
legacy names through:

- `docs/skill-routing-index.md` for human-readable policy.
- `docs/skill-aliases.yml` for machine-readable aliases.
- `ALIAS.md` in the old skill directory when the original content is retained
  but no longer active.

Finance, accounting, audit, close, reporting, controls, IFRS, banking,
reconciliation, and finance UX route to the external
`chwezi-accounting-doctrine` engine unless a root skill adds distinct
implementation behaviour. Reference-only finance checkouts stay outside the
runtime skill catalog.

## Validation And Enforcement

The catalogue's invariants are gated, not just documented. Two scripts run in CI
on every push and PR and fail the build on a violation:

- `skill_catalog_guardrails.py` - structural integrity (count, duplicates,
  frontmatter, line count, description length, broken references, alias
  integrity).
- `routing_smoke_test.py` - routing precision against `routing_fixtures.yml`
  and `tests/routing/edge-fixtures.yml`; catches descriptions drifting into
  ambiguity.

Implementation work closes with the Delivery Definition of Done pack
(`skill-composition-standards/references/delivery-definition-of-done.md`), which
bundles tests, release plan, rollback plan, runbook, and maintenance notes so
the output is operable by a team that did not write it.

## Maintenance Flow

1. Read the relevant `SKILL.md`.
2. Load only necessary local references.
3. Apply the smallest accurate edit.
4. Update routing and overview docs if behavior or catalog policy changed.
5. Run both gates: the guardrail report and the routing smoke test.
6. Record significant documentation repairs in `docs/updates/`.

## Known Constraints

- Markdown files should stay under 500 lines.
- `AGENTS.md` should remain a short navigation hub.
- Avoid deleting compatibility aliases without a migration decision.
- When deactivating an entrypoint, rename only `SKILL.md` to `ALIAS.md`, keep
  the directory intact, and add the target route to `docs/skill-aliases.yml`.
- `doctrine` currently behaves like a special tracked path and should not be
  modified incidentally.
