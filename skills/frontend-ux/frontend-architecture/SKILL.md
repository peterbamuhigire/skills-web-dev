---
name: frontend-architecture
description: Use when turning a design system, product requirement, or frontend codebase into a maintainable component, content, state, and delivery architecture with measurable quality gates.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Frontend Architecture

<!-- dual-compat-start -->
## Use when

- A website or application needs component boundaries, composition rules, a source of truth, or a sustainable design-system implementation.
- A frontend has duplicated tokens, inconsistent states, slow delivery, fragile responsive behaviour, or unclear ownership between design and code.
- A Kaizen cycle needs to improve the frontend engine or a rendered web product without copying a reference site.

## Do not use when

- The task is only visual mood-board analysis; route to website-skills `design-reference`.
- The task is only page composition; route to `page-builder` after architecture is approved.
- Framework-specific current claims are required without current verification.

## Required inputs

| Input | Required | Purpose |
|---|---:|---|
| Product flows, supported viewports, content/data shapes, design-system source, stack, and quality targets | Yes | Define boundaries and acceptance |
| Existing component inventory, defects, performance/accessibility evidence, and ownership | When available | Expose duplication and risk |
| Reference captures or PDF/image inspiration | Optional | Extract principles only; never copy protected assets or distinctive styling |

## Workflow

1. Inventory routes, user flows, components, tokens, states, content contracts, data dependencies, and delivery owners. Mark unknowns rather than inferring them.
2. Define a single source of truth for tokens, components, patterns, content schemas, and responsive rules. Record which layer owns each decision.
3. Choose the smallest architecture that supports the required flows: composition boundaries, state model, loading/error/empty states, accessibility semantics, and extension points.
4. Connect design, code, documentation, and release checks. Require unit/interaction coverage for logic, visual regression for rendered states, accessibility checks, and performance budgets for critical flows.
5. Validate a representative flow at narrow and wide viewports, with slow network, keyboard, reduced motion, long content, failure, and localisation cases where applicable.
6. For premium or client-facing work, preserve the design thesis, signature choice, real-content
   hierarchy, and state model in the implementation contract. Treat inspiration as a principle,
   never as a copied visual surface.
7. Document the decision record, migration slice, ownership, rollback path, and next measurable improvement. Standardise only after evidence passes.

## Outputs

- architecture decision record and component/content ownership map;
- token/component/state inventory with source-of-truth links;
- representative implementation or migration slice;
- visual, accessibility, interaction, performance, and failure-path evidence;
- Kaizen record with a capped 65/100 baseline and 95/100 improvement target.

## Decision rules

| Finding | Action | Risk avoided |
|---|---|---|
| A component differs only because its state or content contract is undocumented | Consolidate the contract before cloning | System drift |
| A shared abstraction increases coupling or slows a critical flow | Keep the boundary local and record why | Premature generalisation |
| A visual reference is distinctive or its rights are unclear | Reject the asset/style and abstract the user-facing principle | Imitation and IP risk |
| A change improves visual consistency but breaks accessibility or performance budgets | Reject, narrow, or roll back | Local optimisation |

## Anti-patterns

- Choosing a framework pattern before understanding flows, content, and ownership.
- Treating a component catalogue as a design system without states, contracts, docs, or release checks.
- Duplicating tokens or styling from an inspiration source.
- Validating only the happy path or desktop screenshot.
- Increasing the published audit above 65 before the initial evidence-backed improvement cycle.

## References

- `frontend-ux/frontend-performance`
- `frontend-ux/accessibility`
- `frontend-ux/visual-qa`
- `frontend-ux/practical-ui-design`
- `sdlc-meta/kaizen-improvement-system`
- website-skills `skills/build/design-reference` and `skills/build/design-system`

## Capability contract

Read/search of the frontend, requirements and design source is required. Code
edits need an implementation request; architecture review alone is read-only.
Use the available build, test and browser tools for the selected flow. Do not
deploy, publish or replace the design source as an incidental architecture step.

## Degraded mode

Without the target runtime or browser, deliver the ownership map and proposed
migration slice, with interaction, accessibility, visual and performance checks
marked NOT ASSESSED. A static component inspection cannot establish rendered
behaviour. Retain the current implementation until required acceptance checks
can support the migration decision.
<!-- dual-compat-end -->
