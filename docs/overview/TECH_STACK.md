# Tech Stack

## Repository Type

This is a documentation and skills repository. Most source files are Markdown
and YAML, with a small amount of Python and PowerShell for maintenance.
The catalog now includes C#/.NET implementation guidance, but .NET is not a
runtime dependency of this repository.
It includes enterprise Java/JVM guidance, but the JDK, Maven, Gradle, Spring,
Jakarta runtimes, application servers, and databases are downstream project
toolchains rather than repository dependencies.
It also includes WWDC26-era Apple development guidance, but Xcode, Swift, and
Apple SDKs are downstream project toolchains rather than runtime dependencies
of this repository.

## Tooling

| Tool | Use |
| --- | --- |
| Git | Version control. |
| PowerShell | Primary local shell on Windows. |
| Python 3 | Catalog guardrail and routing smoke test execution. |
| pytest | Repository validator tests, including temporary portfolio fixtures and malformed-input cases. Live installed-portfolio checks are opt-in and report unavailable execution separately. |
| PyYAML | YAML parsing for `scripts/skill_catalog_guardrails.py` and `scripts/routing_smoke_test.py`. |
| GitHub Actions | CI: runs both gates on every push and PR (`.github/workflows/skill-guardrails.yml`). |
| ripgrep | Fast file and text search. |
| Markdown | Skill bodies, plans, references, guides, and docs. |
| YAML | Skill frontmatter, alias registry, and routing fixtures. |
| JSON | Machine-readable twelve-entry control-plane registry; local checkout validation can target an explicit subset. |
| PyInstaller/Inno Setup guidance | Downstream Windows executable-suite generation; neither tool is a runtime dependency of this repository. |

## Important Commands

```powershell
rg --files -g "SKILL.md"
python -X utf8 scripts\skill_catalog_guardrails.py --report-only
python -X utf8 scripts\routing_smoke_test.py
python -X utf8 scripts\routing_smoke_test.py --collisions
python -X utf8 skills\languages\python-modern-standards\scripts\desktop_suite_packager.py --help
```

The routing smoke test has no external dependency beyond PyYAML; it models the
routing signal (skill name + description) as TF-IDF and asserts fixtured tasks
match the expected skill. It does not call an LLM, so CI stays deterministic.

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
The desktop-suite packager is a standard-library generator; PyInstaller, uv,
Inno Setup, and signing tools are validated in the downstream project where the
generated release pipeline runs.

## Cross-Platform Rules

- Prefer relative paths in documentation.
- Use forward slashes in prose unless showing a Windows command.
- Keep scripts explicit about encoding when reading Markdown or YAML.
- Do not assume case-insensitive paths.
- Avoid OS-specific instructions unless the section is clearly labeled.
