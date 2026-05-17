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

## Guardrails

Run this after catalog routing or skill frontmatter changes:

```powershell
python -X utf8 scripts\skill_catalog_guardrails.py --report-only
```

Known baseline as of 2026-05-17:

- Active `SKILL.md` files: 209.
- Target active catalog size: 150-170.
- Hard cap tracked by the guardrail script: 200.
- Known duplicate names exist between `doctrine/skills/` and `skills/finance/`.

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
