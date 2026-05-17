# Documentation Update: 2026-05-17

## Summary

Recreated the missing project documentation entrypoints for the skills
repository.

## Files Added

| File | Purpose |
| --- | --- |
| `README.md` | Short root landing page. |
| `AGENTS.md` | Agent navigation and working rules. |
| `docs/overview/README.md` | Canonical project overview. |
| `docs/overview/PROJECT_BRIEF.md` | Project purpose, users, outcomes, risks. |
| `docs/overview/TECH_STACK.md` | Tooling and platform context. |
| `docs/overview/ARCHITECTURE.md` | Repository structure and maintenance flow. |
| `docs/overview/API.md` | Clarifies there is no runtime API. |
| `docs/overview/DATABASE.md` | Clarifies there is no repository database. |
| `docs/plans/INDEX.md` | Planning document index. |
| `docs/plans/NEXT_FEATURES.md` | Current priorities and next work. |

## Verification

Baseline guardrail command:

```powershell
python -X utf8 scripts\skill_catalog_guardrails.py --report-only
```

Known current findings:

- Active skill count is above the cap.
- Duplicate finance frontmatter names exist between `doctrine/skills/` and
  `skills/finance/`.

These are pre-existing catalog issues and were not changed by this documentation
repair.
