# Tech Stack

## Repository Type

This is a documentation and skills repository. Most source files are Markdown
and YAML, with a small amount of Python and PowerShell for maintenance.

## Tooling

| Tool | Use |
| --- | --- |
| Git | Version control. |
| PowerShell | Primary local shell on Windows. |
| Python 3 | Catalog guardrail script execution. |
| PyYAML | YAML parsing for `scripts/skill_catalog_guardrails.py`. |
| ripgrep | Fast file and text search. |
| Markdown | Skill bodies, plans, references, guides, and docs. |
| YAML | Skill frontmatter and alias registry data. |

## Important Commands

```powershell
rg --files -g "SKILL.md"
python -X utf8 scripts\skill_catalog_guardrails.py --report-only
```

Optional PDF helper setup:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-pdf-binaries.ps1
```

## Runtime And Deployment Context

| Environment | Role | Requirements |
| --- | --- | --- |
| Windows | Primary editing and maintenance environment. | PowerShell, Git, Python 3, ripgrep recommended. |
| Ubuntu | Secondary validation target. | Python 3, Git, shell-compatible paths where possible. |
| Debian | Production-like downstream environment. | Keep docs and scripts portable. |

There is no repository-owned application runtime, database server, web server,
or package manager manifest. Database references inside skills describe
downstream project patterns rather than this repository's infrastructure.

## Cross-Platform Rules

- Prefer relative paths in documentation.
- Use forward slashes in prose unless showing a Windows command.
- Keep scripts explicit about encoding when reading Markdown or YAML.
- Do not assume case-insensitive paths.
- Avoid OS-specific instructions unless the section is clearly labeled.
