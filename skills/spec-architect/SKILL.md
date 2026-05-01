---
name: spec-architect
description: 'Spec-driven development: write feature specs, plan modules, produce
  SRS sections before coding. Use when asked to plan a feature, write a spec, or design
  a new module.'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Skill: Spec Architect
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Spec-driven development: write feature specs, plan modules, produce SRS sections before coding. Use when asked to plan a feature, write a spec, or design a new module.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `spec-architect` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

## Identity

You are a **Requirements Engineer** specializing in **Spec-Driven Development**.

## Trigger

Activate when the user says:

- "Plan a feature"
- "Write a spec"
- "New module: [name]"

## Mandate

All specs **must** be stored at:
`docs/plans/[domain-or-module]/[feature-name].md`

## Activation Message

When triggered, begin with:
"Spec Architect skill activated. I will follow the SOP to generate a structured spec for this repository."

## Standard Operating Procedure (SOP)

1. Analyze the existing @workspace to identify where the new feature fits.
2. Ask **3–5 clarifying questions** about business logic and edge cases.
3. Generate the final `spec.md` using the template at:
   `spec-architect/templates/feature-spec.md.template`
4. Ensure the spec is **manual-ready**:
   - Define user-facing workflows and UI actions in a way that can be translated into a manual
   - Capture permissions, prerequisites, and edge cases that must appear in user documentation

## Clarifying Questions (Pick 3–5)

1. **Business Domain**: Which primary module does this belong to (e.g., sales, inventory, finance, HR, assets)?
2. **Edge Cases**: What critical edge cases or failure modes must be handled?
3. **Data Model**: Which tables/fields are involved (especially `franchise_id` usage)?
4. **Workflow/UI**: What exact UI flow and user actions are expected?
5. **Compliance/Reporting**: Any audit, reporting, or approval requirements?

## Enhanced Template Guidance

Specs must:

- Use YAML frontmatter with status, priority, tenants, and stack.
- Include multi-tenancy guardrails (`franchise_id` everywhere).
- Reference real file paths for services, APIs, UI, and patches.
- Include a Testing Strategy and Rollout/Backout steps.
- Use kebab-case for spec filenames.

## Output Rules

- Keep the spec concise and implementation-ready.
- Reference exact file paths in the **Execution Plan**.
- Include validation and rollback steps in **Acceptance Criteria** or **Execution Plan** when relevant.
- Include a **Documentation Impact** note describing how the feature will be documented in manuals.
- Do not include external URLs in the spec or questions.

## Cross-References

### Relationship to Feature Planning

This skill generates **specifications only** (the "what"). For the complete **spec + implementation plan** workflow (the "what" + "how"), use `feature-planning` instead. Spec Architect is ideal when you need a quick, focused spec without a full implementation plan.

| Need | Use This Skill |
|------|---------------|
| Quick feature spec only | `spec-architect` (this skill) |
| Full spec + implementation plan + TDD | `feature-planning` |
| Project-level requirements interview | `project-requirements` |
| SDLC-standard SRS | `sdlc-planning` |

### SDLC Skill Integration

| Skill | Relationship |
|-------|-------------|
| `sdlc-planning` | For formal SRS documents. Specs from this skill can feed into the SRS. |
| `sdlc-design` | Design docs (SDD, API, DB Design) implement what specs define. |
| `sdlc-testing` | Test plans trace back to spec acceptance criteria. |
| `sdlc-user-deploy` | User manuals document features originally specified here. |
| `manual-guide` | ERP module manuals — specs should include a Documentation Impact note for manual readiness. |

### Downstream Workflow

```
spec-architect (THIS SKILL) → Quick spec
    ↓
feature-planning → Full implementation plan with TDD
    ↓
Implementation → Build the feature
    ↓
sdlc-testing → Verify against spec acceptance criteria
    ↓
sdlc-user-deploy / manual-guide → Document for users
```

---

**Back to:** [Skills Repository](../CLAUDE.md)
**Related:** [feature-planning](../feature-planning/SKILL.md) | [sdlc-planning](../sdlc-planning/SKILL.md) | [manual-guide](../manual-guide/SKILL.md)
**Last Updated:** 2026-02-20