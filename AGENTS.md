# Agent Guide

## Universal agent integration

See `.skills-engine/engine-manifest.yaml` for the declarative contract used by the optional universal coordination package. The router and domain SKILL.md files remain authoritative.

The package may read the router, discover skills, inspect Git, and run only declared checks. Missing evidence is NOT ASSESSED; writes, pulls, publication, submissions, ledger/filing changes, deployment, or control changes require explicit approval.

## Mandatory Digital Research currentness gate for Kaizen

Every Kaizen audit, skill edit, reference update, validator change, and
standardisation decision MUST begin with the Digital Research Engine at
`C:\wamp64\www\digital-research-engine`. Read its `source-evaluation` and
`source-verification` skills and the currentness gate reference
`docs/continuous-improvement/kaizen-currentness-gate.md`.

Before admitting any standard, policy, law, technology, platform capability,
software version, command, security control, benchmark, or lifecycle claim,
record source scope, publication/version date, access date, freshness class,
review date, support status, and uncertainty. Use current authoritative
primary sources; quarantine stale/ambiguous/unsupported claims and mark them
`NOT_ASSESSED`. Books are durable concept inputs only.

This file is the short navigation hub for coding agents working in this
repository. Keep detailed explanations in `docs/` and link to them from here.

## Project Purpose

This repository stores reusable AI skills, documentation workflows, domain
doctrine, and maintenance scripts. The main task is keeping the skill catalog
accurate, portable, easy to route, and below the active skill cap.

## Read First

| Need | File |
| --- | --- |
| Project overview | `docs/overview/README.md` |
| Architecture | `docs/overview/ARCHITECTURE.md` |
| Tech stack | `docs/overview/TECH_STACK.md` |
| Skill routing | `docs/skill-routing-index.md` |
| Alias registry | `docs/skill-aliases.yml` |
| Current priorities | `docs/plans/NEXT_FEATURES.md` |

## Working Rules

- Prefer `rg` and `rg --files` for searches.
- Do not move, delete, or rename skill directories as part of routine docs work.
- Treat the external `chwezi-accounting-doctrine` checkout as the canonical
  finance source, resolved through the global engine-routing table. Keep its
  reference-only checkout outside this runtime tree.
- Preserve user edits. If the worktree is dirty, inspect before editing.
- Keep Markdown files below 500 lines where practical.
- Use ASCII unless the existing file already requires another character set.
- Update docs when changing skill routing, catalog policy, scripts, or active
  skill behavior.
- For multi-workstream bids or consulting delivery programmes, route control
  operations through `skills/product-business/consulting-delivery-control-room`.
- Before promising Word, PDF, Excel, workbook, scoring matrix, application
  register, budget, or dashboard outputs, route through
  `skills/product-business/document-spreadsheet-tooling-readiness`.
- For high-stakes bid submission or donor/client deliverable release gates,
  route final review through
  `skills/sdlc-meta/world-class-bid-red-team-and-delivery-qc`.

## Active Catalog Roots

| Root | Meaning |
| --- | --- |
| `skills/` | Main active skills. |
| `00-meta-initialization/` | SDLC documentation entry skills. |

An active skill is a `SKILL.md` under one of those roots. Reference-only engine
checkouts must live outside this runtime tree and are not part of the active
catalog.

Inactive aliases are kept as `ALIAS.md` in the original skill directory and
must be routed through `docs/skill-aliases.yml`.

## Guardrails

Run this after catalog routing or skill frontmatter changes:

```powershell
python -X utf8 scripts\skill_catalog_guardrails.py --report-only
```

For a Codex or plugin runtime, also run the cross-engine validator from
`chwezi-engine-agents/scripts/validate-runtime-skill-budget.py` against the
exact skill roots exposed by that host. The per-repository guardrail cannot
measure the assembled runtime metadata budget.

Known baseline as of 2026-08-11 (verify with the script; do not trust this prose):

- Active `SKILL.md` files: 179.
- Target active catalog size: 150-170. Intentional capability additions leave the catalogue
  nine skills above that soft target and well under the enforced 200 cap; the next safe alias or
  consolidation review should return it to range without deleting knowledge.
- Hard cap tracked by the guardrail script: 200.
- Duplicate frontmatter names: 0; near-duplicate pairs (collision-checked): 0.
- The guardrail script now also fails on broken `references/`/`templates/` links
  and on stale or dangling aliases, and runs in CI on every push and PR.
- The same gate rejects raw ebook formats, large files under book-extraction
  paths, and marker-rich full-text conversions. Books are temporary inputs:
  commit only concise, attributed, independently structured synthesis.
- `scripts/routing_smoke_test.py` measures routing precision against
  `scripts/routing_fixtures.yml` and runs in the same CI job; `--collisions`
  reports near-duplicate skills. Add a fixture when you add a skill a neighbour
  could steal traffic from.

## Eleven-engine control plane

The shared agent, command, hook, evidence, and handoff contract is defined in
`docs/engine-control-plane.md` and registered in
`docs/engine-control-plane.json`. Validate it with
`python scripts/validate_engine_control_plane.py`; use
`--workspace-root C:\wamp64\www` for the local eleven-engine router check.

Domain engines remain the source of truth for their doctrine. This engine owns
the cross-engine orchestration vocabulary and implementation patterns. Native
hooks are optional; scripts, CI gates, or explicit skill steps must preserve
the same fail-closed and NOT ASSESSED semantics.

## Quality Guardrails (always-on)

Two cross-cutting skills under `skills/sdlc-meta/` govern output quality for every
artefact type, above any domain skill:

- `anti-ai-slop` — real-time guardrail. Apply continuously while generating ANY
  output (text, document, UI, code, image brief, social post) and at the pre-ship
  gate. Load first; it overrides stylistic preferences.
- `ai-slop-audit` — detection/scoring auditor. Run after EACH major iteration of
  work (log the verdict; block progression on grade F), as the final gate, and
  auto-run whenever the user asks to analyse, review, evaluate, audit, critique, or
  de-slop any project, app, website, plan, spec, document, image, or codebase, or
  asks "does this look AI-generated?".

## Cross-Platform Context

| Environment | Role | Notes |
| --- | --- | --- |
| Windows | Primary local editing environment. | PowerShell examples should work here. |
| Ubuntu | Secondary validation environment. | Keep paths and scripts portable. |
| Debian | Production-like consumer environment. | Avoid OS-specific assumptions in skills. |

This repository has no app database. If a skill discusses MySQL, PostgreSQL, or
another datastore, that is domain guidance for downstream projects rather than a
repository runtime dependency.

## Human-facing English standard

For software, apps, websites, APIs with user-facing text, technical guides, and
skill documentation, load [`docs/continuous-improvement/english-output-standard-2026-09-02.md`](docs/continuous-improvement/english-output-standard-2026-09-02.md). It governs the reader, collocation, register, terminology, idiom, proof, and anti-slop layer. The website engine remains the primary website-content route; the design engine supplies visual and UX doctrine rather than owning prose.

## Documentation Updates

When documentation is changed, keep these files aligned:

- `README.md`
- `docs/overview/README.md`
- `docs/overview/PROJECT_BRIEF.md`
- `docs/overview/TECH_STACK.md`
- `docs/overview/ARCHITECTURE.md`
- `docs/plans/INDEX.md`
- `docs/plans/NEXT_FEATURES.md`

Record substantive documentation repairs under `docs/updates/`.

<!-- design-system-skills:trigger v1 -->
### Design / typography / UI/UX (cross-cutting — consult IN ADDITION)

Any work touching how an artifact LOOKS — font/typeface choice, type scale, colour, layout/grid,
visual identity, web/desktop/mobile UI screens, or the visual formatting of a DOCX/PPTX/PDF/XLSX
— routes to the **`design-system-skills`** engine, the single home for ALL design/UI/UX skills
and the anti-AI-slop doctrine.

**Resolve its location on THIS device from your global engine-routing table** (`~/.claude/CLAUDE.md`,
or `AGENTS.md` for Codex) — never assume an absolute path; it varies per machine. Then read its
`README.md` → `doctrine/design-doctrine.md` → glob `skills/**/SKILL.md` fresh and route by
frontmatter (read SKILL.md directly, not via the Skill tool). Content and structure stay in THIS
engine; presentation comes from design-system-skills. Hard rule: never use a banned AI-slop font
(Inter, Geist, Roboto, Arial, Open Sans, Lato, Space Grotesk, bare system stacks) as primary
type — state the chosen typeface and reason before producing any artifact.
<!-- /design-system-skills:trigger -->

## PORTFOLIO CRAFT CONTRACT

Load `C:\wamp64\www\chwezi-engine-agents\docs\operations\portfolio-craft-standard-2026-09-04.md` when available. Build software, APIs, AI systems, and technical artefacts in named vertical slices: frame the user outcome and failure consequence, select one flow, inspect existing architecture and data flow, make the smallest useful change, run normal and failure checks, review rendered or operational behaviour where relevant, refine, and record evidence before proceeding. Code must be understood in context; interfaces, dependencies, states, observability, and rollback are part of the work. Do not generate a whole product as one opaque batch. Apply `Observe -> Baseline -> Select -> Experiment -> Check -> Standardise -> Teach -> Re-measure` to kaizen itself. Missing execution, render, production, source, reviewer, or stakeholder evidence is `NOT ASSESSED`, never a pass.
