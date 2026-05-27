---
name: premium-ui-ux-design
description: Premium UI/UX design intelligence for web, SaaS, dashboard, Android, and iOS products. Use when a product must look expensive, feel pleasant, communicate clearly, and justify high customer trust or high-ticket pricing.
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

- Designing or reviewing a website, SaaS app, dashboard, Android app, or iOS app where perceived quality, trust, usability, and commercial value matter.
- A product must feel premium, beautiful, calm, efficient, and worth paying serious money for.
- Existing UI work looks generic, cluttered, one-note, hard to scan, or visually cheap.
- Creating a design system, visual QA report, UX specification, or screen-by-screen implementation plan.
- Writing or reviewing an SRS, acceptance criteria, traceability matrix, or design handoff requirements where premium UI/UX must be specified as testable, non-taste-based requirements.

## Do Not Use When

- The request is copy-only, backend-only, or not user-facing.
- A platform-specific companion skill owns the implementation detail and already loaded this premium layer.

## Required Inputs

- Product goal, target users, business model, brand position, platform, and primary user tasks.
- Existing screenshots, designs, or product screens when available.
- Domain constraints: data density, performance budget, accessibility needs, device classes, and revenue-critical flows.

## Workflow

1. Define the business promise: what the user must understand, trust, and accomplish quickly.
2. Choose a visual voice: restrained enterprise, editorial premium, operational dense, consumer polished, luxury minimal, or another defensible direction.
3. Build hierarchy before style: one primary action, obvious navigation, clear content priority, and explicit next steps.
4. Create a tokenized visual system: color, type, spacing, radius, elevation, motion, icons, charts, and image treatment.
5. Design every state: loading, empty, error, success, disabled, offline, slow network, permissions denied, and destructive confirmation.
6. Apply platform conventions: web, Android, and iOS must feel native to their medium, not like resized versions of one another.
7. Run the premium UI/UX gate before calling the work done.
8. Produce evidence: screenshots, score, defects, and concrete improvements.
9. When operating in SRS mode, translate the above into testable non-functional requirements linked to SRS IDs and verification methods (see `premium-ui-ux-specification-rules.md`).

## Quality Standards

- Beauty must serve comprehension, trust, efficiency, and conversion. Decoration that does not improve these outcomes is removed.
- The interface has a clear visual path. Size, weight, color, spacing, placement, and grouping agree about what matters.
- Color has a job: brand recognition, hierarchy, grouping, status, warning, emotion, or navigation. It is never random garnish.
- Text remains readable at all breakpoints and in dark/light modes. Contrast, line length, line height, and hierarchy are verified.
- Dashboards and charts prioritize perceptual accuracy, direct labels, context, comparisons, and actionability.
- Mobile UI uses platform-native ergonomics, navigation, gestures, touch targets, accessibility, and motion expectations.
- Implementation must be production-ready: responsive, fast, accessible, documented, tokenized, and screenshot-verified.

## Anti-Patterns

- Generic AI aesthetic: oversized cards, vague gradients, decorative blobs, one-color palettes, weak typography, and stock-like imagery.
- Pretty but slow, inaccessible, or hard to use.
- Dashboard decoration: gauges, 3D effects, unnecessary shadows, loud colors, disconnected legends, and chart junk.
- Native apps that look like squeezed websites.
- Design systems that define colors and fonts but omit component states, usage rules, ownership, and quality gates.

## Outputs

- Premium UI/UX brief, visual direction, token plan, component/pattern guidance, dashboard guidance, mobile guidance, or review findings.
- A premium UI/UX score with specific remediation items when reviewing finished work.
- Source notes for any book-derived reasoning used in the decision.

## References

- Use companion skill `premium-product-positioning` when the UI/UX work must connect to premium offer architecture, affluent or executive buyer psychology, high-ticket pricing, sales proof, onboarding, or service design.
- `references/premium-visual-principles.md` - hierarchy, layout, typography, perceived value, and pleasantness.
- `references/color-emotion-brand-systems.md` - color choice, palette systems, emotion, hierarchy, and accessibility.
- `references/data-visualization-dashboard-ux.md` - chart, table, KPI, and dashboard rules.
- `references/production-quality-handoff.md` - production polish, asset quality, handoff, and implementation QA.
- `references/mobile-android-ios-premium-ux.md` - platform-specific Android and iOS UX guidance.
- `references/mobile-dashboard-ux-patterns.md` - mobile navigation, onboarding, dashboard, and mobile app quality patterns.
- `references/saas-ux-scope-costing.md` - SaaS UX scope, Uganda-calibrated fee bands, cost drivers, and SRS handoff requirements.
- `references/premium-ui-ux-gate.md` - scoring rubric and blocking checks.
- `references/premium-ui-ux-specification-rules.md` - SRS/UX-specification rules: how to translate premium UI/UX into testable, traceable requirements and acceptance criteria.
- `references/source-register.md` - local book sources dissected for this skill.
<!-- dual-compat-end -->
