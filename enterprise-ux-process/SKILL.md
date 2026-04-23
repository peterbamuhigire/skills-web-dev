---
name: enterprise-ux-process
description: Enterprise product-discovery and feature-definition workflow for web, Android, and iOS teams. Use when a feature is fuzzy, politically noisy, or requirement-heavy and the team needs fast user context, low-fidelity prototyping, stakeholder alignment, and evidence-based go / refine / drop decisions before delivery.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Enterprise UX Process
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- The team is defining a new feature or major change but the problem, requirements, or success criteria are still fuzzy.
- Stakeholders are arguing about solutions before the user task, risk, or evidence is clear.
- Product, design, and engineering need a fast discovery loop that produces testable requirements instead of speculative tickets.

## Do Not Use When

- The work is already well defined and ready for implementation planning.
- The request is a narrow UI polish task with no discovery ambiguity.
- The team only needs delivery sequencing; use `feature-planning`.

## Required Inputs

- Current feature idea, pressure or business ask, and the target user or operator.
- Access to any existing screens, flows, tickets, complaints, research, or stakeholder notes.
- A decision owner who can accept go / refine / drop outcomes.

## Workflow

- Read this `SKILL.md` first, then load only the references required for the exact discovery gap.
- Build context fast, prototype early, and derive requirements from evidence rather than committee language.
- End every cycle with an explicit recommendation and evidence bundle.

## Quality Standards

- Discovery outputs must reduce uncertainty, not decorate it.
- Requirements must describe user success, system behavior, and acceptance evidence.
- Features that remain fuzzy after repeated discovery loops should be tabled or killed.

## Anti-Patterns

- Writing polished user stories before the team understands the workflow.
- Treating stakeholder opinion as a substitute for user context or prototype evidence.
- Continuing discovery indefinitely without a go / refine / drop decision.

## Outputs

- Discovery brief, contextual scenario, low-fidelity flow, evidence-based requirements, risk register, and go / refine / drop recommendation.

## References

- Use `references/natoli-enterprise-playbook.md` for the core process and decision rules.
- Use `references/discovery-evidence-bundle.md` for the artifact contract and evidence expectations.
<!-- dual-compat-end -->

## Workflow

1. Frame the problem in one page.
   Capture the trigger, target user, task, environmental constraints, and the business reason this matters now.
2. Replace abstract personas with context.
   Use real user situations, recent examples, support patterns, or operator constraints.
3. Prototype before formal requirements.
   Build the lowest-fidelity flow that can expose information gaps, action gaps, and stakeholder disagreement.
4. Validate with the right people.
   Prefer target users; if unavailable, validate task realism with proximate operators and record the limitation.
5. Convert findings into requirements.
   Write only what the prototype and task evidence justify.
6. Decide.
   Recommend `go`, `refine`, or `drop`. If the feature is still vague after two serious cycles, stop spending time on it.

## Companion Skills

- `product-discovery` for broader opportunity and risk framing.
- `feature-planning` after discovery is resolved.
- `webapp-gui-design`, `jetpack-compose-ui`, or `swiftui-design` for platform execution after the flow is defined.