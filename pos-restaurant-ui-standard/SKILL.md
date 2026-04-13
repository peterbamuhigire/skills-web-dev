---
name: pos-restaurant-ui-standard
description: Standard Restaurant POS UI derived from the Restaurant POS redesign plan.
  Use for any restaurant POS screen to enforce the approved layout, components, accessibility,
  and speed workflow.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Claude Code: use Superpowers or similar helpers when they are available and materially useful.
- Codex: apply this skill normally; do not treat optional plugins as a prerequisite.

# Restaurant POS UI Standard

<!-- dual-compat-start -->
## Use When

- Standard Restaurant POS UI derived from the Restaurant POS redesign plan. Use for any restaurant POS screen to enforce the approved layout, components, accessibility, and speed workflow.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `pos-restaurant-ui-standard` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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
<!-- dual-compat-end -->
Use this skill for any restaurant POS screen. It enforces the approved UI layout, workflow, and accessibility targets from the Restaurant POS redesign plan.

## When to Use

- Building or refactoring restaurant POS screens
- Reviewing restaurant POS UX for speed and clarity
- Standardizing restaurant order entry workflow

## Required Baseline

- Follow the three-level hierarchy (context, order, actions)
- Use large touch targets (>= 56px; 64px preferred)
- Auto-focus search on load
- Quick access lanes (Recent, Favorites, Popular)
- Sticky or floating cart with dominant Pay CTA
- Never generate invoices until Pay is clicked
- WCAG 2.1 AA compliance for all interactive elements

## Canonical Source

The canonical layout and component specs live in:
- [docs/plans/restaurant-pos/2026-02-03-restaurant-pos-ui-redesign.md](../../docs/plans/restaurant-pos/2026-02-03-restaurant-pos-ui-redesign.md)

## References

- [references/restaurant-pos-ui-standard.md](references/restaurant-pos-ui-standard.md)
