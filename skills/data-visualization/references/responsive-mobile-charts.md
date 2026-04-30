# Responsive Mobile Charts

Use this reference when a data visualization must work on narrow mobile viewports,
especially 360 px wide screens.

## Core Principle

At 360 px, do not simply shrink the chart. Change what the chart is. Pick the rendering by
the user question, not by the desktop chart type.

## Time Series Decision Table

| Pattern | Use when | How |
|---|---|---|
| Headline + sparkline | The question is "up or down?" | Big number, delta, sparkline, and link to full chart |
| Aggregate at breakpoint | The same period can be shown coarser | Collapse daily to weekly or monthly on mobile |
| Switch chart type | Bars are unreadable but trend matters | Use bars on desktop, line or area on mobile |
| Default-window + zoom | Power users need full detail occasionally | Default to 7 or 14 days; full-screen detail for longer ranges |
| Small multiples | Comparing 3-5 series | Stack each series vertically with shared logic |

## Horizontal Scroll Requirements

If horizontal scrolling is unavoidable:

- Keep the y-axis sticky.
- Use scroll snap so bars are not half-cut.
- Show a visible scroll affordance.

## Bar Chart Rules

- Below about 600 px, avoid more than roughly 12 bars inline.
- If bars are tappable, their hit area must meet the 44 x 44 px touch target.
- Aggregate, switch to a line, or use sparkline + headline instead of cramming bars.

## Headline First

Render the insight as text above the chart. A mobile reader who does not inspect the chart
should still understand the answer.

## Anti-Patterns

- 30 daily bars at 360 px with hidden horizontal scroll.
- Shrinking labels until they are unreadable.
- Using the same chart on every breakpoint.
- Requiring pinch-to-zoom as the primary interaction.
- Hover-only tooltips on touch devices.
