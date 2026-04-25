---
name: doc-architect
description: Generate Triple-Layer AGENTS.md documentation by scanning a project for
  its tech stack, data directory, and planning directory. Use when the user asks to
  standardize project documentation, generate agent files, or create AGENTS.md guides.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Doc Architect
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Generate Triple-Layer AGENTS.md documentation by scanning a project for its tech stack, data directory, and planning directory. Use when the user asks to standardize project documentation, generate agent files, or create AGENTS.md guides.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `doc-architect` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references, templates, protocols` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Triple-Layer AGENTS.md output | Generated AGENTS.md covering project tech stack, data directory, and planning directory layers | `AGENTS.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use the `templates/` directory when the task needs a structured deliverable.
- Use the `protocols/` directory for formal execution order or handoff rules.
<!-- dual-compat-end -->
Design and generate a portable Triple-Layer AGENTS.md documentation set that reflects the project’s real structure and constraints.

**Modularize Instructions (Token Economy):** Avoid consolidating all AI/dev guidance into a single CLAUDE.md. Prefer smaller, focused docs (e.g., docs/setup.md, docs/api.md, docs/workflows.md) and reference them only when needed.

**Documentation Standards (MANDATORY):** ALL generated markdown files must follow strict formatting rules:
- **500-line hard limit** - no exceptions for any .md file
- **Two-tier structure**: High-level TOC (Tier 1) + Deep dive docs (Tier 2)
- **Smart subdirectory grouping** for related documentation
- **See `doc-standards.md` for complete requirements**

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
   - Note template conventions (public/ as web root, per-panel includes, API outside public).

2. **Identify the environment**
   - Determine primary language (PHP/C#/Python or other).
   - Determine DB type (MySQL/PostgreSQL/SQLite/SQL Server/other).
   - Determine deployment environment (Docker/Kubernetes/shared hosting/cloud).

3. **Set up plan grouping (first-time)**
   - Create `docs/plans/<module>/` subdirectories for each discovered module/area.
   - Update `docs/plans/AGENTS.md` with the current module list.
   - Create or update `docs/plans/INDEX.md` as the master plan status index.
   - Ensure the index includes status, urgency, last implementation date, and last modification date.
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

## Cross-References to SDLC Skills

When generating AGENTS.md files, be aware of the complete SDLC documentation ecosystem:

### SDLC Documentation Skills

| Skill | Phase | Documents Generated | When to Reference |
|-------|-------|--------------------|--------------------|
| `sdlc-planning` | Planning | Vision, SDP, SRS, SCMP, QA Plan, Risk Plan, Feasibility | When plans directory contains SDLC planning docs |
| `sdlc-design` | Design | SDD, Tech Spec, ICD, Database Design, API Docs, Code Standards | When referencing architecture and design decisions |
| `sdlc-testing` | Testing | Test Plan, Test Cases, V&V Plan, Test Report, Peer Reviews | When referencing testing and quality standards |
| `sdlc-user-deploy` | Delivery | User Manual, Ops Guide, Training, Release Notes, Maintenance, README | When referencing deployment and user documentation |

### Related Documentation Skills

| Skill | Purpose | Relationship |
|-------|---------|-------------|
| `project-requirements` | Raw requirements interview | Input source for SDLC planning docs |
| `feature-planning` | Feature-level specs + implementation plans | Stored in `docs/plans/` (planning directory) |
| `manual-guide` | End-user manuals and guides | Stored in `/manuals/` (separate from AGENTS.md) |
| `update-claude-documentation` | Keep project docs (README, CLAUDE.md) updated | Maintains project-level docs after changes |

### SDLC Output Directory Structure

When scanning for documentation, expect this structure in projects using SDLC skills:

```
docs/
├── planning/        # sdlc-planning output (7 docs)
├── design/          # sdlc-design output (6 docs)
├── testing/         # sdlc-testing output (5 docs)
├── user-deploy/     # sdlc-user-deploy output (6 docs)
├── plans/           # feature-planning output
│   ├── AGENTS.md    # Plans directory index (doc-architect manages this)
│   ├── INDEX.md     # Plan status tracker
│   └── specs/       # Feature specifications
└── project-requirements/  # project-requirements output
```

**Integration Rule:** When generating the Planning AGENTS.md (`docs/plans/AGENTS.md`), include references to any SDLC documentation directories that exist alongside the plans directory.