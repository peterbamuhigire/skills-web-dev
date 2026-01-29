---
name: doc-architect
description: "Generate Triple-Layer AGENTS.md documentation by scanning a project for its tech stack, data directory, and planning directory. Use when the user asks to standardize project documentation, generate agent files, or create AGENTS.md guides."
---

# Doc Architect

Design and generate a portable Triple-Layer AGENTS.md documentation set that reflects the project’s real structure and constraints.

**Modularize Instructions (Token Economy):** Avoid consolidating all AI/dev guidance into a single CLAUDE.md. Prefer smaller, focused docs (e.g., docs/setup.md, docs/api.md, docs/workflows.md) and reference them only when needed.

## Core Outcome

Produce three aligned AGENTS.md files:

- **Root AGENTS.md**: Project identity, tech stack, global standards
- **Data AGENTS.md**: Data integrity rules and schema governance
- **Planning AGENTS.md**: Spec-driven development workflow

## Trigger Phrases

The skill should activate when the user asks to:

- Standardize project documentation
- Generate agent files

## Standard Operating Procedure (SOP)

1. **Scan the workspace**
   - Inspect the root for identifiers (README, PROJECT_BRIEF, TECH_STACK, ARCHITECTURE, CLAUDE, package.json, composer.json, \*.sln, pyproject.toml).
   - Locate likely data directories (database/, schema/, migrations/, sql/, db/).
   - Locate planning/documentation directories (docs/, docs/plans/, planning/, specs/).
   - Identify module/area entry points (menus, docs, feature folders) to group specs.

2. **Identify the environment**
   - Determine primary language (PHP/C#/Python or other).
   - Determine DB type (MySQL/PostgreSQL/SQLite/SQL Server/other).
   - Determine deployment environment (Docker/Kubernetes/shared hosting/cloud).

3. **Set up plan grouping (first-time)**
   - Create `docs/plans/<module>/` subdirectories for each discovered module/area.
   - Update `docs/plans/AGENTS.md` with the current module list.
   - Keep `docs/plans/AGENTS.md` updated whenever plans are added or their status changes.
   - Maintain a folder map at the top of `docs/plans/AGENTS.md` and update it when requested.
   - Note that developers can add new folders and update the list manually.

4. **Generate Triple-Layer docs**
   - Use the templates in [templates/root-agents.md.template](templates/root-agents.md.template), [templates/data-agents.md.template](templates/data-agents.md.template), and [templates/plan-agents.md.template](templates/plan-agents.md.template).
   - Populate with real findings and pull constraints from [references/logic-library.md](references/logic-library.md) as needed.
   - Create files at:
     - **Root**: AGENTS.md at project root
     - **Data**: database/schema/AGENTS.md (or best-fit schema directory)
     - **Planning**: docs/plans/AGENTS.md (or best-fit planning directory)

## Bundled Resources

- [protocols/workflow.md](protocols/workflow.md): 3-step workflow used during generation
- [templates/root-agents.md.template](templates/root-agents.md.template): Root AGENTS.md template
- [templates/data-agents.md.template](templates/data-agents.md.template): Data AGENTS.md template
- [templates/plan-agents.md.template](templates/plan-agents.md.template): Planning AGENTS.md template
- [references/logic-library.md](references/logic-library.md): Domain constraint library for reuse

## Common Pitfalls

- Do not invent tech stacks. Only infer from files found in the workspace.
- Do not place AGENTS.md in arbitrary locations; follow the best-fit paths above.
- Do not include contradictory rules across the three layers.

## Quick Example

If a project uses Laravel + MySQL with docs/plans and database/schema:

- Root: AGENTS.md → PHP/Laravel, MySQL, deployment standards
- Data: database/schema/AGENTS.md → referential integrity, no-delete rules
- Plans: docs/plans/AGENTS.md → spec.md format and workflow steps
