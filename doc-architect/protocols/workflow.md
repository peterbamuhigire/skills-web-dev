# Doc Architect Workflow

Use this 3-step process to generate the Triple-Layer AGENTS.md set.

## 1) Discovery

Identify the project’s structure and anchors.

- Scan root identifiers: README.md, PROJECT_BRIEF.md, TECH_STACK.md, ARCHITECTURE.md, CLAUDE.md
- Scan build/system files: package.json, composer.json, *.sln, pyproject.toml, requirements.txt
- Locate schema/data paths: database/, schema/, db/, migrations/, sql/
- Locate documentation/planning paths: docs/, docs/plans/, planning/, specs/

## 2) Analysis

Determine the project’s operating context.

- **Language**: PHP / C# / Python (or other)
- **Database**: MySQL / PostgreSQL / SQLite / SQL Server / other
- **Deployment**: Docker / Kubernetes / shared hosting / cloud services

## 3) Generation

Create the three AGENTS.md files using the templates.

- **Root AGENTS.md** (project root)
  - Project identity, tech stack, global standards
- **Data AGENTS.md** (best-fit schema directory)
  - Data integrity, domain rules, no-delete policy
- **Planning AGENTS.md** (best-fit planning directory)
  - Spec-driven development workflow and spec.md format

## 4) Plan Grouping Setup (first-time)

- Identify core modules/areas from menus and docs.
- Create `docs/plans/<module>/` subdirectories for each module.
- Add or update the module list in `docs/plans/AGENTS.md`.
- Allow manual additions: developers can add new folders and update the list.

Populate content based on real findings and reuse constraints from [../references/logic-library.md](../references/logic-library.md).
