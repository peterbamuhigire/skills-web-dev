# Analytics Dashboard Decision Story

Use this reference when designing dashboards and visuals for analytics outputs, business
plans, proposals, research reports, SaaS modules, or management systems.

## Dashboard Purpose

A dashboard is a decision surface, not a chart gallery. Before selecting visuals, state:

- Who decides.
- What decision they need to make.
- Which metric changes the decision.
- What threshold triggers action.
- What drill-down explains the result.
- What the viewer should do next.

## Analytics-to-Visual Router

| Analytics task | Best visual pattern | Notes |
|---|---|---|
| Descriptive KPI | KPI card + trend sparkline | Include period, baseline, target, and delta |
| Diagnostic variance | Waterfall, bar decomposition, small multiples | Show driver contribution, not just total gap |
| Forecast | Line chart with interval band | Separate actuals from forecast and label uncertainty |
| Classification/risk | Ranked table, segmented bar, confusion matrix for technical users | Non-technical users need action labels, not raw scores |
| Clustering/segments | Profile table + small multiples | Explain segment meaning before showing algorithmic output |
| Optimization | Scenario table + trade-off chart | Show objective, constraints, and recommended option |
| Data quality | Scorecard + exception table | Display missingness, duplicates, stale data, and source reliability |

## Dashboard Minimums

Every decision dashboard needs:

- Metric definition visible or one click away.
- Source and refresh time.
- Baseline, target, and threshold.
- Owner or accountable role.
- Status logic: green, amber, red, or equivalent.
- Drill-down path from aggregate to cause.
- Exportable or citable view for reports.
- Accessibility: readable labels, colour-safe status, keyboard navigation where interactive.

## Story Structure

Use a short analytical narrative:

1. What changed?
2. Why does it matter?
3. What likely caused it?
4. What are the options?
5. What action is recommended?
6. What should be monitored next?

For static reports, make the chart title an action title: "Inventory stockout risk is
concentrated in three branches" instead of "Inventory by branch."

## Anti-Patterns

- Showing all available KPIs because the database has them.
- Mixing exploratory analysis with executive reporting.
- Using red/green as the only status cue.
- Presenting forecasts without uncertainty bands.
- Showing model scores without explanation or action thresholds.
- Hiding stale data or quality warnings.
