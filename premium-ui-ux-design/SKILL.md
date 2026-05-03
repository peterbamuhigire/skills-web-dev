---
name: premium-ui-ux-design
description: SRS and UX-specification layer for premium UI/UX requirements. Use when formal software requirements must produce beautiful, pleasant, efficient, accessible, business-sound web, Android, iOS, or dashboard products.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Premium UI/UX Design
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Writing or reviewing SRS, UX specifications, acceptance criteria, or design handoff requirements for user-facing systems.
- The final software must be beautiful, pleasant, efficient, accessible, and commercially credible.
- The product includes web screens, dashboards, reports, Android, iOS, or data-heavy workflows.

## Do Not Use When

- The requirements are backend-only, infrastructure-only, or not user-facing.
- A narrower downstream implementation skill is already handling screen-level design and the SRS does not need UX requirements.

## Required Inputs

- Product vision, target users, business goals, platform, user stories or SRS draft, HLD, constraints, and any existing UI evidence.

## Workflow

1. Translate business goals into explicit UX outcomes: trust, speed, conversion, error reduction, adoption, or operational efficiency.
2. Add premium UI/UX non-functional requirements for visual quality, usability, accessibility, responsiveness, platform conventions, performance feel, and production consistency.
3. Define platform-specific acceptance criteria for web, Android, iOS, dashboards, reports, forms, and data tables.
4. Require evidence: wireframes, token tables, component state matrices, screenshots, accessibility checks, usability test metrics, and premium gate score.
5. Link every premium UI/UX requirement to SRS IDs and verification methods.

## Quality Standards

- Requirements must be testable, not taste-based.
- UI aesthetics must be connected to business and user outcomes.
- Dashboards must define the decisions they support, not only the metrics they display.
- Android and iOS requirements must respect platform conventions and accessibility.
- Design-system requirements must include tokens, component states, ownership, source of truth, and governance.

## Anti-Patterns

- Writing subjective requirements such as "make it beautiful" without measurable evidence.
- Treating dashboard requirements as a list of metrics without decisions, thresholds, or actions.
- Ignoring Android/iOS platform conventions in a generic cross-platform UX spec.

## Outputs

- Premium UX requirement set, UX specification sections, acceptance criteria, traceability matrix entries, or review findings.

## References

- `references/premium-ui-ux-specification-rules.md`
- `references/source-register.md`
<!-- dual-compat-end -->
