# Restaurant POS UI Standard (Reference)

This reference mirrors the approved Restaurant POS redesign plan. Use it to implement consistent UI across all restaurant POS screens.

## Index

- Overview: docs/plans/restaurant-pos/00-overview.md
- Architecture and Skills: docs/plans/restaurant-pos/01-architecture-and-skills.md
- Current State and Targets: docs/plans/restaurant-pos/02-current-state-and-targets.md
- UI Architecture and Layout: docs/plans/restaurant-pos/03-ui-architecture-and-layout.md
- Components A-C: docs/plans/restaurant-pos/04-components-header-search-quick-access.md
- Components D-E: docs/plans/restaurant-pos/05-components-category-menu-grid.md
- Component F: docs/plans/restaurant-pos/06-components-cart-panel.md
- Component G: docs/plans/restaurant-pos/07-components-customization-modal.md
- Responsive and Interaction: docs/plans/restaurant-pos/08-responsive-and-interaction.md
- Accessibility Checklist: docs/plans/restaurant-pos/09-accessibility-checklist.md
- Implementation Tasks: docs/plans/restaurant-pos/10-implementation-tasks.md
- Testing, Rollout, KPIs: docs/plans/restaurant-pos/11-testing-rollout-kpis-appendix.md

## Standard Layout Summary

- Three-column desktop: context, menu, cart
- Two-column tablet: menu + cart
- Single-column mobile: stacked menu with floating cart bar
- Sticky context header
- Search-first workflow with auto-focus
- Quick access lanes (Recent, Favorites, Popular)
- Menu grid with quick add (+1, +2) and optional customize
- Cart panel always visible and Pay CTA dominant

## Interaction Rules (Required)

- Search debounce: 300ms
- Add-to-cart: single tap
- Confirm destructive actions only
- Focus cues on programmatic focus changes
- Invoice generation only on payment action

## Accessibility Rules (Required)

- WCAG 2.1 AA contrast
- Visible focus indicators
- Keyboard navigation for all actions
- ARIA labels for dynamic regions
- Touch targets >= 56px

## Performance Targets

- Time-to-3-items <= 30 seconds
- First-item latency <= 5 seconds
- Mobile load <= 2 seconds
