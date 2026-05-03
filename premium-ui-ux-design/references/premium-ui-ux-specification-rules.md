# Premium UI/UX Specification Rules

Use these rules when generating formal SRS or UX specification documents.

## Business-Aligned UX Requirements

Every premium UX specification must state:

- Primary user segments and their high-value tasks.
- Business outcome supported by the interface.
- Trust, conversion, retention, efficiency, or risk-reduction goal.
- Platform context: web, Android, iOS, tablet, desktop, kiosk, or dashboard.
- Evidence required to verify the UX requirement.

Example requirement shape:

`UX-NFR-###: The system shall present [information/action] so that [user segment] can [decision/task] within [target condition], verified by [test/evidence].`

## Visual Quality Requirements

- The system shall define a visual voice appropriate to the buyer, domain, and price point.
- The system shall document color, typography, spacing, radius, elevation, icon, chart, and motion tokens.
- The system shall avoid one-off styling outside documented token layers.
- The system shall define responsive behavior for mobile, tablet, desktop, and large desktop where applicable.
- The system shall include state-complete component specifications: default, hover, focus, pressed, selected, disabled, loading, empty, error, success, offline, and permission denied.

## Usability Requirements

- Frequent tasks shall be reachable through the shortest defensible path.
- Primary actions shall be visually distinct and described with outcome-oriented labels.
- Forms shall use grouped fields, inline validation, loading feedback, error recovery, and confirmation.
- Search, filters, sorting, and pagination shall be specified for large data sets.
- Destructive actions shall require confirmation or provide undo when reversible.

## Accessibility Requirements

- Web products shall meet WCAG 2.1/2.2 AA or the project's stated stricter target.
- Android products shall support TalkBack, font scaling, contrast, reduced motion, and 48 dp touch targets.
- iOS products shall support VoiceOver, Dynamic Type, Increase Contrast, Reduce Motion, Dark Mode, and 44 pt touch targets.
- Color shall not be the only carrier of meaning.
- Every requirement shall include a verification method: automated check, manual keyboard/screen reader test, design review, usability test, or device test.

## Dashboard And Data Requirements

- Each dashboard shall define its decision owner, monitoring job, metrics, thresholds, update frequency, and required actions.
- KPI displays shall include context: target, prior period, trend, threshold, or benchmark where needed.
- Charts shall be selected by relationship: category comparison, time trend, distribution, geography, relationship, part-to-whole, or exact lookup.
- Data tables shall right-align numbers, use tabular figures, support sorting/filtering where needed, and avoid unnecessary gridlines.
- Dashboards shall avoid decorative gauges, 3D charts, loud colors, disconnected legends, and chart junk unless a justified exception is documented.

## Platform-Specific Requirements

### Web

- The first viewport of marketing or revenue pages shall communicate brand/offer, credibility, and next action.
- The product shall be tested at small mobile, tablet, laptop, and desktop widths.
- Performance budgets shall include image, font, script, and interaction responsiveness constraints.

### Android

- The system shall use Material 3 and adaptive navigation unless a justified product standard overrides it.
- The system shall use bottom navigation, navigation rail, or pane layouts according to window size and task complexity.
- Compose screens shall model loading, content, empty, error, offline, permission-denied, and syncing states.

### iOS

- The system shall use SwiftUI-native navigation, tab bars, sheets, forms, lists, and menus unless a justified exception exists.
- The system shall preserve swipe-back and platform gesture expectations.
- iPad variants shall specify split views, sidebars, or multi-column layouts when productivity benefits.

## Premium Gate Acceptance

The UX specification shall include a gate with these categories:

- Business clarity.
- Visual quality.
- Usability and efficiency.
- Content and communication.
- Accessibility and inclusiveness.
- Data and decision quality.
- Platform and production fit.

Any category below 8/10 shall generate remediation requirements before design sign-off.
