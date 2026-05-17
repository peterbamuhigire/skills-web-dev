# API

This repository does not expose a runtime HTTP, RPC, GraphQL, or CLI API.

The closest stable interfaces are file conventions:

| Interface | Purpose |
| --- | --- |
| `*/SKILL.md` | Skill entrypoint with YAML frontmatter and execution guidance. |
| `docs/skill-aliases.yml` | Machine-readable routing and alias data. |
| `scripts/skill_catalog_guardrails.py` | Repository guardrail report script. |

## Guardrail Script Interface

```powershell
python -X utf8 scripts\skill_catalog_guardrails.py --report-only
```

Useful options:

| Option | Meaning |
| --- | --- |
| `--root <path>` | Add an active catalog root relative to the repository root. |
| `--max-active <number>` | Override the active skill cap. |
| `--report-only` | Print findings and exit with status 0. |

API documentation for downstream projects should live inside the relevant skill
or project example, not in this repository overview.
