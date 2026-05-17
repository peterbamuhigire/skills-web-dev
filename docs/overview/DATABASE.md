# Database

This repository does not own a database schema or runtime datastore.

Database-related content appears as skill guidance for downstream projects, for
example MySQL, PostgreSQL, accounting ledgers, migrations, and reporting
patterns. Those docs are domain references, not infrastructure used by this
repository.

## Data Files

| File | Role |
| --- | --- |
| `docs/skill-aliases.yml` | Skill alias and planned route registry. |
| `docs/skill-routing-index.md` | Human-readable routing source. |
| `*/SKILL.md` | Skill metadata and instructions. |

## Maintenance Notes

- Keep YAML parseable by `PyYAML`.
- Keep Markdown valid UTF-8.
- Treat skill frontmatter `name` values as catalog identifiers.
- Resolve finance duplicates through doctrine routing or alias consolidation.
