# Analytics Method Selection and Governance

Use this reference when building analytics features, KPI computations, statistical tests,
Python notebooks, dashboards, or decision-support modules. It consolidates transformed
guidance from big-data mathematics, business analytics, Python analytics, and accounting
analytics sources.

## Core Workflow

Use the AMPS-style sequence for every serious analysis:

1. Ask the question: define the business decision, owner, and action that will follow.
2. Master the data: identify tables/files, grain, codebook, ownership, quality, privacy,
   and lineage.
3. Prepare the data: clean, type, join, reshape, transform, and document assumptions.
4. Perform the analysis: choose the simplest defensible method for the question.
5. Share the story: present the finding, uncertainty, limitation, and recommended action.

Do not start with a model. Start with the decision.

## Analytics Type Router

| Question | Analytics type | Typical methods | Output |
|---|---|---|---|
| What happened? | Descriptive | summaries, trends, ratios, cohort tables, pivots | KPI report or dashboard |
| Why did it happen? | Diagnostic | variance analysis, drill-down, correlation, segmentation, root-cause trees | cause hypotheses and evidence |
| What is likely to happen? | Predictive | regression, time series, classification, clustering, anomaly models | forecast, risk score, probability band |
| What should we do? | Prescriptive | optimization, scenario analysis, sensitivity analysis, constraints, recommendations | recommended action and trade-off |

Prescriptive outputs require clear constraints. Predictive outputs require history, labels
or target definitions, validation, and a monitoring plan. Diagnostic outputs require a
plausible causal explanation, not just correlation.

## Mathematical Guardrails

- Probability and uncertainty are part of the output. Show confidence intervals,
  prediction intervals, or qualitative confidence where possible.
- Correlation is not causation. Use domain logic, temporal order, controls, experiments,
  or quasi-experimental design before claiming causality.
- Regression needs enough observations, sensible features, residual checks, and outlier
  review. Avoid extrapolating beyond the observed range.
- Classification needs class balance checks and appropriate metrics. Do not use accuracy
  alone on imbalanced data; use precision, recall, F1, ROC-AUC, PR-AUC, or cost-weighted
  metrics as the decision requires.
- Clustering is exploratory. Validate clusters by business usefulness, stability, and
  interpretability before turning them into product rules.
- Feature selection matters. More variables can reduce predictive power when data is
  limited; avoid high-dimensional models without enough examples.
- Optimization is only as good as the objective and constraints. State both explicitly.

## Data Quality Gate

Before modelling or publishing:

- Completeness: required fields populated, missingness pattern understood.
- Validity: types, ranges, units, dates, IDs, and categorical codes make sense.
- Accuracy: sample records trace back to source documents or operational systems.
- Consistency: entities, currencies, time zones, and category names agree across sources.
- Timeliness: freshness matches the decision rhythm.
- Integrity: joins do not duplicate or lose records unexpectedly.
- Privacy: personal or sensitive data is minimized, protected, and authorized.

Document row counts before and after each cleaning step. Dropping rows without a reason is
data loss, not cleaning.

## Python Implementation Pattern

Use Python when the analysis needs multi-step transformation, statistical modelling,
forecasting, anomaly detection, simulation, optimization, matrix operations, chart output,
or multi-source joins.

Recommended pipeline:

1. Load with explicit schema, date parsing, and tenant/client filters.
2. Profile the dataset: rows, columns, dtypes, missingness, duplicates, min/max, category
   cardinality, outliers, and date coverage.
3. Normalize data grain before joins.
4. Validate every merge with expected cardinality.
5. Use vectorized pandas/Polars operations rather than row-wise loops.
6. Compute metrics in tested functions, not inline notebook cells.
7. Return both values and metadata: source period, filters, assumptions, limitations, and
   refresh time.
8. Persist reproducible outputs: cleaned data, summary tables, model artifacts where
   needed, and audit notes.

## Business Management Analytics

For management systems and SaaS dashboards, analytics must support an operating decision:

- Finance: cash flow, receivables risk, margin, variance, budget vs actual, working capital.
- Sales and marketing: funnel conversion, CAC, channel ROI, lead quality, retention.
- Operations: throughput, backlog, cycle time, quality defects, stockouts, utilization.
- Customer success: activation, churn risk, support burden, satisfaction, expansion.
- Governance: data quality, compliance, privacy, audit trails, access monitoring.

For each metric define owner, formula, source, frequency, threshold, and action trigger.
Metrics without actions become dashboard decoration.

## AI-Based Analytics Controls

When AI or ML is involved:

- Explain what data influenced the result.
- Label AI-generated summaries and recommendations.
- Keep a human decision point for high-impact actions.
- Monitor drift, stale data, and degraded model performance.
- Avoid training or inference on data the user is not authorized to use.
- Keep generated explanations grounded in computed metrics.

## Deliverable Standard

Every analytics deliverable should include:

- Business question.
- Data sources and grain.
- Data quality notes.
- Method selected and why.
- Result with uncertainty or limitations.
- Visual or table designed for the audience.
- Recommended action.
- Reproducibility note: where the data, code, and assumptions live.
