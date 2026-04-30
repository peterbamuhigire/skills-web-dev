# Business Analytics Operating Model

Use this reference when designing analytics capability for a business, SaaS module, ERP,
dashboard, proposal, or management system.

## Operating Principle

Analytics capability matures from reliable reporting to decision support. Do not promise
AI, prediction, or optimization before the organization can produce trusted descriptive
and diagnostic analytics.

## Maturity Path

| Stage | Capability | Required evidence | Typical build |
|---|---|---|---|
| 0. Data capture | Events and records are captured | forms, system logs, transaction records | data model, forms, source controls |
| 1. Descriptive reporting | What happened is visible | reconciled KPIs, reliable dashboards | KPI reports, management accounts |
| 2. Diagnostic analytics | Drivers are explainable | dimensions, drill-downs, variance logic | root-cause dashboards, segment views |
| 3. Predictive analytics | Future risk or demand can be estimated | historical depth, labels, model validation | forecasts, churn scores, anomaly alerts |
| 4. Prescriptive analytics | Actions can be recommended | constraints, cost-benefit logic, trust | next-best-action, optimization, workflows |

## Analytics Capability Components

- Data governance: owners, stewards, definitions, access, retention, privacy.
- Data architecture: source systems, warehouse/lake, transformations, semantic layer.
- Data quality: completeness, validity, accuracy, consistency, timeliness, integrity.
- Method discipline: descriptive, diagnostic, predictive, and prescriptive methods chosen
  by question, data structure, and risk.
- Tooling: SQL, Python, BI dashboards, notebooks, scheduled pipelines, monitoring.
- Decision integration: thresholds, alerts, review cadence, workflow handoff.
- Change management: training, adoption, trust-building, and explanation.

## Business Analytics Use Cases

Finance:

- Cash-flow early warning.
- Receivables aging and collection priority.
- Cost variance and margin leakage.
- Budget vs actual variance.

Operations:

- Demand forecast.
- Inventory stockout and overstock risk.
- Cycle time, bottleneck, and utilization analysis.
- Quality defect and rework analysis.

Commercial:

- Lead scoring and funnel conversion.
- Customer segmentation.
- Pricing sensitivity.
- Retention and churn risk.

Management:

- Balanced Scorecard dashboard.
- Strategy KPI cascade.
- Performance review pack.
- Scenario and sensitivity analysis.

## Governance Questions

Before recommending analytics, answer:

- Who owns each metric definition?
- Which system is the source of truth?
- How often is data refreshed?
- What is the acceptable error rate?
- What action is triggered by green, amber, or red status?
- Which users are authorized to see record-level data?
- What evidence proves the insight changed a decision?

## Responsible AI Analytics

Use AI to summarize, classify, detect patterns, and recommend actions only after the
underlying data and calculation logic are reliable. AI output should explain the evidence,
not replace the evidence.

Minimum controls:

- Human review for high-impact decisions.
- Plain-language explanation of drivers.
- Confidence or uncertainty label.
- Bias and privacy review.
- Drift monitoring for predictive systems.
- Logging of inputs, model version, output, and user action.
