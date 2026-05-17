# Architecture

## System Shape

The repository is a file-based knowledge system. Skill entrypoints live in
`SKILL.md` files, deep references sit beside those skills, and repository-level
docs describe routing, consolidation, planning, and maintenance policy.

## Main Components

| Component | Responsibility |
| --- | --- |
| `skills/` | Main skill catalog for engineering, AI, SaaS, mobile, security, UX, product, and operations. |
| `doctrine/skills/` | Canonical finance and accounting doctrine. |
| `00-meta-initialization/` | Entry-point workflow for SDLC documentation setup. |
| `docs/skill-routing-index.md` | Human routing map for consolidated and legacy skill names. |
| `docs/skill-aliases.yml` | Machine-readable alias registry. |
| `scripts/skill_catalog_guardrails.py` | Static guardrail scan for active skill count, duplicate names, frontmatter, UTF-8, description length, and `SKILL.md` line count. |
| `claude-guides/` | Skill authoring and Claude-specific usage guidance. |
| `book-extractions/` | Long-form source notes and reference summaries. |

## Skill Loading Model

An active skill is any `SKILL.md` under:

- `skills/`
- `doctrine/skills/`
- `00-meta-initialization/`

Reference material should be stored under directories such as `references/`,
`sections/`, `templates/`, `assets/`, or examples, not as extra `SKILL.md`
files. This keeps active skill count controllable.

## Routing Model

When multiple narrow skills overlap, prefer one retained parent skill and route
legacy names through:

- `docs/skill-routing-index.md` for human-readable policy.
- `docs/skill-aliases.yml` for machine-readable aliases.

Finance, accounting, audit, close, reporting, controls, IFRS, banking,
reconciliation, and finance UX route first to `doctrine/skills/` unless a root
skill adds distinct implementation behavior.

## Maintenance Flow

1. Read the relevant `SKILL.md`.
2. Load only necessary local references.
3. Apply the smallest accurate edit.
4. Update routing and overview docs if behavior or catalog policy changed.
5. Run the guardrail report.
6. Record significant documentation repairs in `docs/updates/`.

## Known Constraints

- Markdown files should stay under 500 lines.
- `AGENTS.md` should remain a short navigation hub.
- Avoid deleting compatibility aliases without a migration decision.
- `doctrine` currently behaves like a special tracked path and should not be
  modified incidentally.
