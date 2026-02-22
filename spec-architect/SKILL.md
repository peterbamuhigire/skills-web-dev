# Skill: Spec Architect

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
   `skills/spec-architect/templates/feature-spec.md.template`
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
