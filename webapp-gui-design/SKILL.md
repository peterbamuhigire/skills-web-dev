---
name: webapp-gui-design
description: Professional web app UI using commercial templates (Tabler/Bootstrap
  5) with strong frontend design direction when needed. Use for CRUD interfaces, dashboards,
  admin panels with SweetAlert2, DataTables, Flatpickr. Clone seeder-page.php, use...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Web App GUI Design

<!-- dual-compat-start -->
## Use When

- Professional web app UI using commercial templates (Tabler/Bootstrap 5) with strong frontend design direction when needed. Use for CRUD interfaces, dashboards, admin panels with SweetAlert2, DataTables, Flatpickr. Clone seeder-page.php, use...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `webapp-gui-design` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `sections` only as needed.
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
| UX quality | GUI template audit | Markdown doc covering Tabler/Bootstrap 5 component coverage, theme tokens, and accessibility findings | `docs/web/gui-audit-checkout.md` |

## References

- Use the `sections/` directory for modular deep dives and load only the parts relevant to the task.
<!-- dual-compat-end -->
This skill is split into sections to stay under the 500-line limit.

## Sections

1. [Overview & Stack](./sections/01-overview.md)
2. [Security, Print/PDF, Dates](./sections/02-security-print-dates.md)
3. [Architecture, Panels, Menus](./sections/03-architecture-panels-menus.md)
4. [Permissions & Searchable Dropdowns](./sections/04-permissions-dropdowns.md)
5. [Templates & UI Components](./sections/05-templates-components.md)
6. [AJAX & Utilities](./sections/06-ajax-utilities.md)
7. [Responsive, Photo Cards, Flatpickr](./sections/07-responsive-photo-flatpickr.md)
8. [Best Practices & Aesthetics](./sections/08-best-practices-aesthetics.md)
9. [Interface Design](./sections/09-interface-design.md)
10. [SaaS UX Principles](./sections/10-saas-ux-principles.md) — Onboarding, dashboards, empty states, navigation, multi-tenant UI, feedback, performance
