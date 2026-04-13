---
name: ai-analytics-strategy
description: Business strategy for AI-powered analytics — analytics maturity model,
  KDD and CRISP-DM process frameworks, data quality requirements, responsible AI principles,
  analytics ROI measurement, and how to build analytics into SaaS modules from day...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Analytics Strategy

<!-- dual-compat-start -->
## Use When

- Business strategy for AI-powered analytics — analytics maturity model, KDD and CRISP-DM process frameworks, data quality requirements, responsible AI principles, analytics ROI measurement, and how to build analytics into SaaS modules from day...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-analytics-strategy` or would be better handled by a more specific companion skill.
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

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## What Analytics Is

*"Data Analytics is the discipline of extracting actionable insights by structuring, processing, analysing and visualising data using methods and software tools."* — Garn (2024)

Insights must be **actionable** — they exist to trigger a decision or action, not to be interesting. Every analytics feature must answer: "What decision does this enable?"

---

## The Four Types of Analytics

Build analytics capabilities in this order — each level requires the previous.

| Level | Type | Question Answered | AI Role | Example |
|-------|------|------------------|---------|---------|
| 1 | **Descriptive** | What happened? | Summarise, aggregate | Daily sales total, attendance rate |
| 2 | **Diagnostic** | Why did it happen? | Identify correlations, anomalies | Which students missed the most classes? |
| 3 | **Predictive** | What will happen? | ML models, LLM analysis | Which students are likely to fail this term? |
| 4 | **Prescriptive** | What should we do? | Decision support, recommendations | "Contact Aisha today — 80% fail risk, last seen 4 days ago" |

Do not offer prescriptive analytics without solid descriptive and diagnostic data first. Predictions on dirty data destroy trust in the product.

---

## Analytics Maturity Model

Assess where a client is before recommending AI analytics:

| Stage | Description | What to Build |
|-------|------------|--------------|
| **0 — No Data** | Data lives in paper, Excel files, or disconnected systems | First build the data-capture system; analytics later |
| **1 — Reporting** | Basic reports exist; data is in a database but scattered | Standardised dashboards, KPI reports |
| **2 — Business Intelligence** | Consistent data model; users can explore data | Interactive dashboards, drill-down, export |
| **3 — Predictive** | 12+ months of clean, structured historical data | AI risk scoring, demand forecasting, anomaly alerts |
| **4 — Prescriptive** | Predictive models trusted; users act on recommendations | AI-driven action prompts, automated workflows |

**Rule:** Do not skip stages. A client at Stage 0 who buys AI analytics wastes money.

---

## The KDD Process

*Knowledge Discovery in Databases* — the end-to-end data-to-insight pipeline. Source: Garn (2024).

```
1. Problem Definition
   ↓ What business question are we answering? What decision will the insight trigger?

2. Data Selection
   ↓ Which tables, fields, and date ranges are relevant?

3. Data Preprocessing / Cleansing
   ↓ Handle missing values, outliers, duplicates, inconsistent formats

4. Data Transformation
   ↓ Aggregate, normalise, encode categorical variables, engineer features

5. Data Mining (Model / Prompt)
   ↓ Apply ML model OR construct LLM prompt with processed data

6. Evaluation
   ↓ Measure accuracy, precision, recall, F1, or business metric (did the action happen?)

7. Interpretation and Exploitation
   ↓ Translate model output to business language; embed in product; drive action
```

**For LLM-based analytics (steps 5–7):**
- Step 5 = the AI API call with curated, pre-processed data
- Step 6 = human review of sample outputs; thumbs up/down feedback
- Step 7 = the UI that presents the insight and the recommended action

---

## CRISP-DM for AI-Powered Analytics Projects

*Cross-Industry Standard Process for Data Mining* — the project management framework. Source: Garn (2024).

```
Business Understanding → Data Understanding → Data Preparation
         ↑                                              ↓
    Deployment ← Evaluation ← Modelling ←────────────────
```

**Applied to AI analytics development:**

| Phase | Deliverable | Key Question |
|-------|------------|-------------|
| **Business Understanding** | Analytics brief: what decision, who decides, what triggers action | "What will the manager do with this insight?" |
| **Data Understanding** | Data audit: tables available, data quality score, history depth | "Do we have 12 months of clean data?" |
| **Data Preparation** | SQL views or pre-processing scripts that feed the AI prompt | "What is the minimum clean dataset for a useful prediction?" |
| **Modelling** | Prompt template + AI API call + output schema | "Does the AI output match what the manager needs?" |
| **Evaluation** | 20 real examples tested; accuracy rated by domain expert | "Is this accurate enough to act on?" |
| **Deployment** | Feature integrated into product, gated, metered | "Is it live, gated, and billing correctly?" |

---

## Data Quality Requirements for Analytics

Before any AI analytics feature goes live, score the data on four dimensions:

| Dimension | What to Check | Minimum Standard |
|-----------|--------------|-----------------|
| **Completeness** | % of records with all required fields populated | > 90% |
| **Accuracy** | Sample validation against source documents | > 95% match |
| **Timeliness** | How fresh is the data? | < 24h old for operational; < 7 days for strategic |
| **Consistency** | Same entity represented the same way across tables | No conflicting IDs or naming conventions |

Flag data quality issues to the client before promising AI analytics. Poor data quality is the #1 reason AI analytics fails.

---

## Responsible AI in Analytics

From Wilson (HBR, 2023) and Tyagi (2024):

### The Five Principles

1. **Transparency** — Users must know they are seeing AI-generated content, not just reports. Label all AI outputs clearly.
2. **Explainability** — Every AI prediction must show the reason: "Based on: 3 missed assessments, attendance 58%, last login 6 days ago."
3. **Fairness** — Audit predictions for bias. If the AI consistently flags students from a particular background, investigate.
4. **Human Oversight** — No automated irreversible action without human confirmation. AI recommends; humans decide.
5. **Privacy** — Analytical aggregations must not expose individual records to unauthorised viewers. Enforce RBAC on analytics views.

### Explainable AI (XAI) Requirements

For every AI prediction or recommendation, show:
- The 3–5 data points that most influenced the outcome.
- The confidence level (High / Medium / Low).
- A "Why this?" link that shows the reasoning in plain language.

Do not show raw probability scores (e.g., "0.73 failure probability") to non-technical users. Translate to business language ("High risk of not completing this term").

---

## Analytics ROI Measurement

When justifying analytics investment to clients:

| Metric | How to Measure | Example |
|--------|---------------|---------|
| **Time saved** | Hours/week staff spent on manual reports before vs after | "Reduced weekly report preparation from 8h to 20 min" |
| **Decision speed** | Time from event to action before vs after | "At-risk student identified in 24h vs 2 weeks" |
| **Error rate** | Manual calculation errors before vs AI-assisted | "Payment misclassification rate dropped 94%" |
| **Revenue impact** | Stockout reduction, upsell success, churn reduction | "Stockout incidents down 60% after predictive alerts" |
| **Cost avoidance** | Equipment failures prevented, bad debts avoided | "2 crop failures avoided → UGX 4.2M saved" |

Build these KPIs into the product's own analytics dashboard — clients renew subscriptions when they can see the ROI in their own data.

---

## Domain Analytics Opportunities Quick Reference

| Domain | Maturity Required | Best Starting Analytics Feature |
|--------|------------------|-------------------------------|
| School Management | Stage 1+ | Term-end performance report by class |
| Healthcare | Stage 2+ | Patient appointment adherence report |
| POS / Retail | Stage 1+ | Daily/weekly sales trend with top products |
| Farm Management | Stage 2+ | Crop yield comparison by field/season |
| ERP / Finance | Stage 2+ | Cash flow forecast based on receivables pipeline |

---

**See also:**
- `ai-opportunity-canvas` — Discover analytics opportunities per module
- `ai-predictive-analytics` — Implement predictive models
- `ai-nlp-analytics` — Text-based analytics (sentiment, classification)
- `ai-analytics-dashboards` — Design the analytics UI
- `data-visualization` — Chart selection and storytelling with data
