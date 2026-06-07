# Agent Guide

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
- Treat `doctrine/skills/` as canonical for finance and accounting doctrine.
- Preserve user edits. If the worktree is dirty, inspect before editing.
- Keep Markdown files below 500 lines where practical.
- Use ASCII unless the existing file already requires another character set.
- Update docs when changing skill routing, catalog policy, scripts, or active
  skill behavior.

## Active Catalog Roots

| Root | Meaning |
| --- | --- |
| `skills/` | Main active skills. |
| `doctrine/skills/` | Canonical finance doctrine skills. |
| `00-meta-initialization/` | SDLC documentation entry skills. |

An active skill is a `SKILL.md` under one of those roots. Reference material
should not be named `SKILL.md`.

Inactive aliases are kept as `ALIAS.md` in the original skill directory and
must be routed through `docs/skill-aliases.yml`.

## Guardrails

Run this after catalog routing or skill frontmatter changes:

```powershell
python -X utf8 scripts\skill_catalog_guardrails.py --report-only
```

Known baseline as of 2026-05-30 (verify with the script; do not trust this prose):

- Active `SKILL.md` files: 171.
- Target active catalog size: 150-170 (1 over soft target, well under the 200 cap).
- Hard cap tracked by the guardrail script: 200.
- Duplicate frontmatter names: 0; near-duplicate pairs (collision-checked): 0.
- The guardrail script now also fails on broken `references/`/`templates/` links
  and on stale or dangling aliases, and runs in CI on every push and PR.
- `scripts/routing_smoke_test.py` measures routing precision against
  `scripts/routing_fixtures.yml` and runs in the same CI job; `--collisions`
  reports near-duplicate skills. Add a fixture when you add a skill a neighbour
  could steal traffic from.

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
