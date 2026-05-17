# Next Features

This file tracks the next practical work for the skills repository.

## Critical Priority

| Work | Why | Start Point |
| --- | --- | --- |
| Reduce active skill count below 200 | The guardrail script reports 209 active `SKILL.md` files. | Use `docs/skill-routing-index.md` and `docs/skill-aliases.yml`. |
| Resolve finance duplicate frontmatter names | Duplicate names reduce routing reliability and are already reported by guardrails. | Consolidate or redirect `skills/finance/*` to `doctrine/skills/*`. |

## High Priority

| Work | Why | Start Point |
| --- | --- | --- |
| Normalize documentation entrypoints | Root docs were missing and needed reconstruction. | Keep `README.md`, `AGENTS.md`, and `docs/overview/*` aligned. |
| Add a lightweight catalog verification workflow | Guardrails are manual today. | Consider a GitHub Actions workflow for `scripts/skill_catalog_guardrails.py`. |

## Medium Priority

| Work | Why | Start Point |
| --- | --- | --- |
| Review `docs/skills-trimminhg.md` filename | The apparent typo makes discovery harder. | Rename only if references are updated in the same change. |
| Add dependency notes for Python tooling | PyYAML is required but no requirements file exists. | Add `requirements.txt` or document install steps. |

## Recently Completed

| Date | Work | Summary |
| --- | --- | --- |
| 2026-05-17 | Documentation reconstruction | Restored root README, agent guide, overview docs, plan index, next-feature tracker, API/database notes, and update record. |

## Recommended Next Session

1. Decide whether `skills/finance/*` compatibility aliases should remain active
   or be converted to non-active references.
2. Bring active skill count below 200.
3. Run `python -X utf8 scripts\skill_catalog_guardrails.py --report-only` and
   update this file with the new baseline.
