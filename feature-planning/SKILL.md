---
name: feature-planning
description: Complete feature planning from specification to implementation. Create
  structured specs with user stories and acceptance criteria, then generate detailed
  implementation plans with TDD workflow, exact file paths, and complete code examples.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Feature Planning

<!-- dual-compat-start -->
## Use When

- Complete feature planning from specification to implementation. Create structured specs with user stories and acceptance criteria, then generate detailed implementation plans with TDD workflow, exact file paths, and complete code examples.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `feature-planning` or would be better handled by a more specific companion skill.
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

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use the `templates/` directory when the task needs a structured deliverable.
- Use the `protocols/` directory for formal execution order or handoff rules.
<!-- dual-compat-end -->
Complete feature development planning from **specification** to **implementation**. This skill combines requirements engineering with detailed implementation planning to ensure features are both well-specified and properly implemented.

**Standard plan directory (required):** `/docs/plans/`

**Save specs to:** `docs/plans/specs/[domain]/[feature-name].md`
**Save implementation plans to:** `docs/plans/YYYY-MM-DD-[feature-name].md`
**Save multi-file plans to:** `docs/plans/[feature-name]/` (implementation details)

**Documentation Standards (MANDATORY):** ALL plan and spec files must follow strict formatting rules:
- **500-line hard limit** per file - no exceptions
- **Two-tier structure**: Plan overview/index + Detailed section files (max 500 lines each)
- **Smart subdirectory grouping** for complex plans
- **See `doc-standards.md` for complete requirements**

**Plan directory index (required):** Update `docs/plans/AGENTS.md` whenever a plan or spec is added.
**Plans status index (required):** Update `docs/plans/INDEX.md` whenever a plan is created, modified, implemented, or completed. Record status, urgency, last implementation date, and last modification date.

**Deployment awareness:** All features deploy to Windows dev, Ubuntu staging, and Debian production. Plans must account for cross-platform compatibility (case-sensitive filesystems, `utf8mb4_unicode_ci` collation, forward-slash paths). Database migrations for production go in `database/migrations-production/` (non-destructive, idempotent).

## Additional Guidance

Extended guidance for `feature-planning` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `📋 Two-Phase Planning Process`
- `🎯 Phase 1: Specification (Spec-Driven Development)`
- `User Story`
- `Acceptance Criteria (Definition of Done)`
- `Technical Constraints`
- `Data Model`
- `High-Level Execution Plan`
- `Testing Strategy`
- `Rollout Strategy`
- `🔧 Phase 2: Implementation Planning (TDD Workflow)`
- `📚 Learning Resources`
- `📱 Android SaaS App — Mandatory Phase 1 Bootstrap`
- Additional deep-dive sections continue in the reference file.
