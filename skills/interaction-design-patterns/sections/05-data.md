# Data Display Patterns

From Tidwell, *Designing Interfaces*, 3rd ed., Chapter 9: Showing Complex Data.

> "The goal of information graphics is not to show data — it is to help users understand and act on data." — Tidwell.

---

## The Basics of Information Graphics

Before choosing a chart type, answer these five questions:

| Question | Design Response |
|----------|----------------|
| **How is this data organised?** | Hierarchy → tree/treemap. Time series → line chart. Categories → bar chart. Part of whole → pie/donut (only 2–5 slices). |
| **What relationships are important?** | Use preattentive variables to show relationships visually, before the user consciously processes the data. |
| **How can users explore this data?** | Enable navigation: zoom, pan, filter, select. |
| **Can users rearrange the data?** | Sorting, grouping, and pivoting reveal different patterns in the same dataset. |
| **Can users filter to see only what they need?** | Dynamic filtering that updates in real time is far more powerful than static views. |

---

## Preattentive Variables

The most powerful tool in data visualisation. These attributes are processed by the visual system **before conscious thought** — within 200ms. Use them to direct attention to the most important patterns.

| Variable | Best For | Avoid When |
|----------|---------|-----------|
| **Colour (hue)** | Categorical differences (type A vs type B) | Ordinal data (use lightness/saturation instead) |
| **Colour (lightness/saturation)** | Ordered quantity (more = darker) | Categorical data |
| **Size** | Quantity (larger = more) | Comparing multiple dimensions |
| **Position (x/y)** | Most precise comparison — always primary encoding | Never abandon position for an inferior encoding |
| **Shape** | Categorical (use sparingly — max 4–5 shapes) | Ordered data |
| **Orientation** | Direction, angle | Quantitative comparisons |
| **Motion** | Drawing attention to change | Any decorative use — motion is the strongest attractor |

**Design rule:** Always encode the most important relationship with position. Use colour, size, and shape for secondary relationships only.

---

## Data Display Patterns

### Datatips
*"Tell me the exact value when I hover over this data point."*

Datatips (tooltips on data visualisations) reveal the precise value of a data point on hover — without cluttering the chart with labels on every point.
- Show: value, label, timestamp, and any relevant context (e.g., comparison to target or previous period)
- Trigger: hover on desktop, tap on mobile (then dismiss on second tap or tap elsewhere)
- Position: above or to the right of the cursor, never covering the data point itself
- Style: clean, minimal — a white or dark card with shadow, never decorative
- On mobile: datatips should be larger and positioned to not be covered by the user's finger

**Anti-pattern:** No tooltips on data charts — users who need the exact value have no way to get it.

---

### Data Spotlight
*"Highlight what matters in context."*

When a dataset has one or more especially significant data points (anomalies, targets, thresholds, milestones), highlight them in place within the visualisation — without requiring users to search for them.
- Annotate the chart directly: "Target line", "Budget exceeded here", "Record high"
- Use a distinct visual treatment: a labelled vertical line, a highlighted region, a differently coloured point
- The annotation text should be short — max 5 words
- Combine with Datatip: hover reveals detail; annotation gives the story

---

### Dynamic Queries
*"Let me filter the data in real time and see the result immediately."*

Dynamic queries apply filters to a dataset and show the filtered result **instantly** as the user adjusts controls — no "Apply" button, no page reload.
- Filter controls update the visualisation/list in real time (or within 200ms)
- Show the number of results: "Showing 47 of 312 customers"
- Provide a "Clear all filters" button prominently — always visible when any filter is active
- Persist filter state in the URL so results are shareable
- Sliders, checkboxes, date ranges, and text search all work as dynamic query controls

**Design rule:** An "Apply" button on a filter panel adds friction and hides the cause-effect relationship between the filter and the result. Remove it.

---

### Data Brushing
*"When I select data in one chart, highlight it in all the others."*

Data brushing links multiple visualisations on the same screen — selecting a subset of data in one chart highlights the same data in all other related charts simultaneously.
- Useful in dashboards and analytics tools where users need to see how one group relates to others
- Selection in one panel propagates to all panels that share the same dataset
- Provide a "Clear selection" button or click in empty space to reset
- Visual treatment for the selection: highlighted in the primary chart; faded/greyed in the others

---

### Multi-Y Graph
*"Show two data series that have different scales on the same chart."*

When two related metrics have vastly different scales (e.g., revenue in millions and conversion rate in percentage), plot them on the same chart with two Y-axes — one on the left for the primary metric, one on the right for the secondary.
- Left Y-axis: primary metric, primary colour
- Right Y-axis: secondary metric, secondary colour
- Lines/bars for each metric use the corresponding axis colour as a visual link
- Label both axes clearly with units
- Use sparingly — more than two Y-axes creates confusion. Use separate charts for three or more metrics.

---

### Small Multiples
*"Show me the same chart for each category so I can compare them."*

Small multiples are a grid of the same chart type, each showing data for a different dimension value (a different product, region, time period, or user segment). The identical structure makes comparison effortless.
- All charts in the grid use the same axis scales — this is critical for honest comparison
- Arrange in a logical order: alphabetical, by value (highest first), by time
- Keep each chart small enough to fit in a grid but large enough to read trends
- Add a colour indicator per chart for quick identification
- Label each chart clearly — the category name above or below

**When to use:** Comparing the same metric across 4–20 categories. If you have fewer than 4, overlay them on one chart. If more than 20, use filtering instead.

---

## Data Table Patterns

### Sortable Table
Every column header in a data table should be clickable to sort by that column.
- Show sort direction with an arrow icon (↑ ascending, ↓ descending)
- First click: ascending. Second click: descending. Third click: reset to default.
- Default sort should match the user's most common use case — usually most recent first for time-series data
- Multi-column sort: Shift+click on a second column header

### Overview + Detail
*"Give me the summary; let me expand to see detail."*

For complex data objects (invoices, patients, projects), show a compact overview (key fields only) in a list or table, and expand to a detail view on selection.
- Overview: 3–5 key fields sufficient to identify and triage the item
- Detail: full record; opens in a side panel (Two-Panel Selector) or a dedicated detail page
- The Two-Panel Selector pattern keeps the list visible while the detail is open — users can click through items rapidly without navigating back and forth

### Pagination vs Infinite Scroll

| Approach | Use When |
|----------|---------|
| **Pagination** | Users need to jump to a specific page, bookmark a position, or share a specific page of results |
| **Infinite Scroll** | Content is sequential and browsing is the primary activity (social feeds, media galleries) |
| **Load More button** | A middle ground — user controls when new content loads; good for lists with a natural end |

**Anti-pattern:** Infinite scroll on data tables — users can't jump to page 50 of an order history or bookmark their position.

---

## Data Visualisation Anti-Patterns

| Anti-Pattern | Why it Fails |
|-------------|-------------|
| 3D charts | Distorts data values; makes precise comparison impossible; purely decorative |
| Pie charts with > 5 slices | Human perception can't compare angles accurately beyond 5 segments — use a bar chart |
| Truncated Y-axis starting above 0 | Exaggerates differences; misleads about magnitude |
| Dual-Y axis with incompatible data | Users can't determine which axis applies to which line |
| Colour as the only differentiator | 10% of men are colour-blind — always pair with shape, label, or pattern |
| Chart animations on every load | Decorative animation is noise; reserve animation for transitions that communicate change |
| No axis labels or units | Users can't interpret a chart with no context — what are these numbers measuring? |
| Showing all data always | Too much data = too much noise. Filter by default; let users expand if they need more |
