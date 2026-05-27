# Mobile And Dashboard UX Patterns

This reference is self-contained. It distills the user's supplied Design Studio UI/UX
mobile navigation, mobile onboarding, dashboard, and mobile app examples articles into
reusable execution rules.

Sources used:

- https://www.designstudiouiux.com/blog/mobile-navigation-ux/
- https://www.designstudiouiux.com/blog/mobile-app-onboarding-best-practices/
- https://www.designstudiouiux.com/blog/dashboard-ui-design-guide/
- https://www.designstudiouiux.com/blog/mobile-app-design-examples/

## Mobile Navigation Rules

- Use 3-5 primary destinations for bottom navigation or iOS tab bars.
- Put daily-use destinations in visible navigation; keep drawers and "More" menus for
  secondary or infrequent items.
- Keep labels visible for primary destinations. Icon-only navigation is acceptable only
  when the icon is universally understood and accessibility labels are present.
- Treat gestures as accelerators, not the only way to complete a core action.
- Respect platform conventions: iOS tab bars, safe areas, and swipe-back expectations;
  Android bottom navigation, system back, navigation rail or drawer where appropriate.
- Measure navigation with task success, time to first tap, taps to destination, mis-taps,
  screen drop-off, and support questions caused by wayfinding.

## Mobile Onboarding Rules

- Show value before demanding registration, permissions, or profile completion.
- Keep onboarding as short as the risk level allows. High-risk apps may need security
  setup; low-risk apps should let users reach value immediately.
- Prefer progressive onboarding: teach features when the user first needs them.
- Avoid 5+ static intro slides that describe features instead of helping users do the
  first valuable task.
- Ask for permissions in context, after explaining the benefit.
- Track activation, first value time, permission acceptance, onboarding completion,
  first-session task completion, day-1 retention, and day-7 retention.

## Dashboard UX Rules

- Every dashboard must have a decision owner and a monitoring job.
- KPIs need context: target, threshold, trend, prior period, benchmark, or action path.
- Use hierarchy: urgent exceptions first, then core metrics, then exploration.
- Show data freshness and drill-down path; stale dashboards create false confidence.
- Prefer readable tables and direct labels over decorative charts.
- Avoid decorative gauges, 3D charts, disconnected legends, unlabelled axes, and
  dashboard cards that do not lead to a decision.

## Mobile Quality Signals

Successful mobile apps tend to share these traits:

- Core task completion with minimal friction.
- Fast loading and stable feedback across devices.
- Strong visual hierarchy, consistent components, and clear recovery paths.
- Trust-building content near the risky decision: reviews, ratings, security messages,
  proof, progress, or confirmation.
- Visual voice aligned to product purpose: calm apps should feel calm; finance apps
  should feel precise and trustworthy; travel or commerce apps should make inspection
  and comparison easy.

## Acceptance Checklist

- Primary navigation has no more than five visible destinations.
- High-frequency actions are reachable in the thumb zone on common phones.
- First-run flow reaches value before optional setup.
- Permission prompts are contextual and deferrable where possible.
- Dashboard cards answer "so what?" and link to the next action.
- Loading, empty, error, offline, and permission-denied states are designed.
- VoiceOver/TalkBack labels, focus order, touch targets, and contrast are verified.
