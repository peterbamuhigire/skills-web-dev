---
name: ai-analytics-dashboards
description: Design AI-powered analytics dashboards — what metrics to show, how to
  display AI predictions and confidence, drill-down patterns, KPI cards, trend visualisation,
  AI Insights panels, export design, and role-based dashboard variants. Invoke when...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Analytics Dashboards

<!-- dual-compat-start -->
## Use When

- Design AI-powered analytics dashboards — what metrics to show, how to display AI predictions and confidence, drill-down patterns, KPI cards, trend visualisation, AI Insights panels, export design, and role-based dashboard variants. Invoke when...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-analytics-dashboards` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | AI dashboard design audit | Markdown doc covering metric clarity, confidence display, drill-down paths, and AI-output explanation surfaces | `docs/ai/dashboard-audit.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Design Principle

An analytics dashboard exists to trigger a decision or action — not to display data. Every widget must answer a specific question a specific user asks daily. If a chart answers no decision, remove it.

*"We are drowning in data but are starved for knowledge."* — Garn (2024)

---

## Dashboard Anatomy

Every analytics dashboard has four zones:

```
┌──────────────────────────────────────────────────────────────────┐
│ ZONE 1 — KPI Summary Bar                                         │
│ [Total Revenue] [Active Students] [At-Risk: 12] [Stockouts: 3]  │
├───────────────────────────────┬──────────────────────────────────┤
│ ZONE 2 — Trend Charts         │ ZONE 3 — AI Insights Panel      │
│ Sales over last 30 days       │ ✦ 12 students flagged high risk  │
│ Attendance rate trend         │ ✦ 3 products forecast stockout  │
│ Revenue vs target             │ ✦ Sentiment: 8% negative (↑2%)  │
├───────────────────────────────┴──────────────────────────────────┤
│ ZONE 4 — Detail Table / Drill-Down                               │
│ List of at-risk students | Top-selling products | Pending alerts │
└──────────────────────────────────────────────────────────────────┘
```

---

## Zone 1: KPI Cards

Show the most important number for this role. Keep it to 4–6 KPIs maximum.

**KPI card anatomy:**
```
┌─────────────────────────┐
│ Total Sales Today       │
│ UGX 2,450,000           │  ← primary value (large)
│ ↑ 12% vs yesterday      │  ← comparison (trend arrow + delta)
│ Target: UGX 2.2M ✓      │  ← target status
└─────────────────────────┘
```

**KPI card rules:**
- Use trend arrows (↑↓) with colour: green for good direction, red for bad.
- Show a comparison (vs yesterday, vs last week, vs target) — a number alone has no context.
- For AI-derived KPIs, add ✦ badge: "✦ AI Forecast: UGX 2.6M tomorrow."
- Never show more than one decimal place for currency or percentages on cards.

**Domain KPI examples:**

| Domain | KPI 1 | KPI 2 | KPI 3 | KPI 4 |
|--------|-------|-------|-------|-------|
| School | Students enrolled | Attendance rate today | Students at risk (AI) | Fees outstanding |
| Healthcare | Patients seen today | Appointment adherence % | Patients flagged (AI) | Avg wait time |
| POS/Retail | Revenue today | Units sold | Stockout alerts (AI) | Top product |
| Farm | Active plots | Avg yield forecast (AI) | Pest alerts | Harvest days remaining |
| ERP | Revenue MTD | Payables due this week | Anomaly flags (AI) | Cash runway (days) |

---

## Zone 2: Trend Charts

### Chart Selection Guide

| Data | Chart Type | When to Use |
|------|-----------|------------|
| Value over time (1 metric) | Line chart | Sales trend, attendance over weeks |
| Value over time (compare 2–3 metrics) | Multi-line chart | Revenue vs target vs last year |
| Part-to-whole | Donut chart (not pie) | Sentiment breakdown, product mix |
| Ranking / comparison | Horizontal bar chart | Top 10 products, class performance |
| Distribution | Histogram | Score distribution, transaction sizes |
| Two variables (correlation) | Scatter plot | Attendance vs score correlation |
| Geographic | Choropleth map | Sales by district, yield by region |

**Rules:**
- Maximum 3 lines on a line chart. More = unreadable.
- Always label axes with units (UGX, %, students).
- Use 30-day default view with selector: 7d / 30d / 90d / custom.
- Colour-blind safe palette: use shape/pattern differentiation in addition to colour.
- AI forecast extension: show historical line (solid) + forecast (dashed) on the same chart.

### AI Forecast Band Pattern

```
Revenue (UGX) │
              │    ___________
   2,500,000  │  /            \........ (AI forecast, dashed)
              │ /              \       ░░░░░ (confidence band)
   2,000,000  │/                \
              └──────────────────────────────────
               Apr 1          Apr 7    Apr 14
               Historical →        Forecast →
```

Show confidence band (shaded area) around the forecast line. Narrow band = high confidence; wide band = low confidence. Label the band.

---

## Zone 3: AI Insights Panel

The AI Insights panel surfaces the most important AI-generated findings. It is the fastest path from data to action.

**Design:**
```
┌─────────────────────────────────────────────────┐
│ ✦ AI Insights                      [Refresh]   │
├─────────────────────────────────────────────────┤
│ 🔴 12 students at HIGH RISK this term           │
│    Top signal: attendance + missed assessments  │
│    [View List]  [Generate Letters]              │
├─────────────────────────────────────────────────┤
│ 🟡 Maize Flour forecast to STOCK OUT in 3 days  │
│    Current: 180 units | Forecast demand: 210    │
│    [Reorder Now]  [Adjust Forecast]             │
├─────────────────────────────────────────────────┤
│ 🟢 Sentiment improving: Negative down to 8%     │
│    vs 14% last term — parent comms working      │
│    [View Feedback]                              │
└─────────────────────────────────────────────────┘
```

**Rules:**
- Maximum 5 insights at a time — prioritised by urgency.
- Each insight has one action button (primary) and optionally a secondary.
- Use traffic-light colours: 🔴 urgent, 🟡 attention needed, 🟢 positive signal.
- Always show the reason under the headline — never show a bare "12 students at risk" with no explanation.
- Include a timestamp: "Updated 2 hours ago" — stale insights decay trust.
- Show a spinner/skeleton when loading — insights can take 5–10 seconds.

---

## Zone 4: Detail Tables

The drill-down table shows the items behind the KPI or insight.

**Design rules:**
- Default to 25 rows; paginate the rest.
- Sortable columns with a visible sort indicator.
- Inline status badges (coloured pills) for AI classification outputs.
- Inline action buttons at row level (not just at top): "Contact" | "Flag" | "Review".
- Search and filter bar above the table.
- Export button: CSV and PDF.

**At-Risk Students Table example:**

| Student | Class | Risk | Attendance | Score | Last Login | Action |
|---------|-------|------|-----------|-------|-----------|--------|
| **S.Nakato** | S.4A | 🔴 High | 58% | 41% | 8 days ago | [Contact Parent] |
| **T.Okello** | S.3B | 🟡 Medium | 71% | 53% | 3 days ago | [Flag to Teacher] |

---

## Role-Based Dashboard Variants

Different users need different views of the same data.

| Role | Dashboard Focus | Key Differences |
|------|----------------|----------------|
| **Executive / Owner** | Revenue, growth, portfolio view | Aggregated across all branches; AI summary narrative |
| **Branch/School Manager** | Operational KPIs for their unit | Their data only; AI alerts for their team |
| **Teacher / Clinician** | Their students / patients | No financial data; clinical/academic focus |
| **Finance Officer** | Payments, receivables, budget | No academic/clinical data; financial drill-down |
| **Super-Admin (SaaS)** | All tenants, system health, AI billing | Token usage per tenant, AI module status |

Enforce with RBAC — never mix roles in a single view.

---

## AI Summary Narrative Card

For executive dashboards, generate a plain-English summary of the period's performance.

**Prompt template:**
```
You are a business performance analyst.
Generate a concise executive summary (3–4 sentences) of this period's performance.
Highlight: top achievement, top concern, one recommended action.

Data:
- Revenue: UGX [X] vs target [Y] ([Z]% of target)
- Active users: [N] (trend: [up/down] [%] vs last period)
- AI alerts raised: [N] (top: [most common alert type])
- Sentiment score: [X]% positive (trend: [+/-X%])

Output: plain English narrative only, no JSON.
Language: formal, suitable for a board report.
Length: 3–4 sentences.
```

**Display as a highlighted card:**
```
┌──────────────────────────────────────────────────────────┐
│ ✦ AI Executive Summary — April 2026                     │
│                                                          │
│ Revenue reached UGX 48.2M, 96% of the monthly target,  │
│ driven by strong performance in the Kampala branch.     │
│ Twelve students were flagged at high academic risk —    │
│ early intervention is recommended before week 6.        │
│ Parent sentiment improved to 74% positive, up 8pp       │
│ from last term.                                         │
│                                   Generated 06:00 today │
└──────────────────────────────────────────────────────────┘
```

---

## Export Design

Every dashboard must support export:

| Format | Content | Use Case |
|--------|---------|---------|
| **PDF** | Dashboard as rendered (charts + tables) | Board reports, regulatory submissions |
| **CSV** | Raw data behind the current view | Further analysis in Excel |
| **Excel** | Formatted tables with headers | Finance officer reconciliation |

**Export rules:**
- Always include: report title, tenant name, date generated, date range of data, "Generated by [System Name] AI Analytics."
- Never export PII to CSV without explicit user confirmation and audit log entry.
- Mark AI-generated content in exports: "✦ AI Forecast" beside predicted values.

---

## Dashboard Performance Requirements

| Metric | Target |
|--------|--------|
| Initial dashboard load (cached) | ≤ 1.5s |
| Chart rendering | ≤ 500ms per chart |
| AI Insights panel load (streaming) | ≤ 8s; show skeleton immediately |
| Data refresh (on demand) | ≤ 3s for aggregated KPIs |
| Export PDF generation | ≤ 10s |

Use server-side caching for KPIs (TTL = 15 min for operational; 24h for historical). Never re-query the database on every page render.

---

**See also:**
- `ai-analytics-strategy` — What analytics to build and for whom
- `ai-predictive-analytics` — The prediction data displayed in Zone 3
- `ai-nlp-analytics` — Sentiment data displayed in Zone 3
- `data-visualization` — Chart selection and visual storytelling (Knaflic)
- `ai-ux-patterns` — Loading states, AI badges, confidence display
- `ai-cost-modeling` — Cost of generating AI narratives per dashboard refresh
