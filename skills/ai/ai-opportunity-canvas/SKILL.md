---
name: ai-opportunity-canvas
description: Use when discovering and ranking AI use cases for a project or module and producing an opportunity register with impact, effort, cost, risk, and evidence gaps.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Opportunity Canvas

## Operating contract

## Inputs

| Input | Required | Purpose |
|---|---|---|
| Domain evidence | yes | project or module scope, user jobs, current process metrics, available data, constraints, and decision owner |

## Outputs

- Produce: ranked opportunity register, impact/effort/cost assumptions, risks, evidence gaps, and next-step recommendation.

## Capability and permission boundaries

Default to read-only analysis. Read only scoped records; redact secrets and regulated data. Writes, execution, network calls, production configuration, customer communication, billing changes, and delegation require explicit authority and an identified owner. Never widen tenant, time-window, or system scope implicitly.

## Degraded mode

When required telemetry, evidence, execution, network access, or write authority is unavailable, return a partial result with each unassessed item labelled, preserve the safest existing state, and state the evidence or approval needed to continue. Never convert missing evidence into a pass.

## Decision rules

| Condition | Action |
|---|---|
| Scope, owner, or threshold is missing | Stop the affected decision and request it |
| Evidence is incomplete but read-only analysis is safe | Produce a qualified partial result and gap list |
| A mutation exceeds authority or tenant boundary | Block it and route for approval |
| Evidence meets the stated threshold | Issue the output with provenance and owner |

## Anti-Patterns

- Treating absent evidence as success. Fix: mark the check unassessed and name the missing source.
- Expanding one tenant or workflow to all tenants. Fix: enforce supplied scope at every query and action.
- Performing a production write during analysis. Fix: emit a reviewed change plan until authority is explicit.
- Reporting a metric without population, window, or source. Fix: attach all three.
- Hiding a failed threshold inside an average. Fix: report failure slices and the remediation owner.

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Systematically discover and rank AI use cases for any software project or module. Produces a prioritised AI Opportunity Register with business impact, implementation effort, and cost estimates. Invoke after any project description or module...

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | AI Opportunity Roadmap | Prioritised Markdown roadmap covering ranked AI use cases per project or module | `docs/ai/opportunity-roadmap-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Purpose

Identify every realistic place AI adds measurable value to a client's system. Output is an **AI Opportunity Register** — a ranked list of AI features with business case, effort estimate, and cost tier, ready for client presentation.

**Invoke this skill:** After project/module description, before HLD or feature planning.

---

## The 10 Universal AI Opportunity Patterns

For each pattern, assess whether it applies to the current project module.

| # | Pattern | Business Value | Typical Token Cost Tier |
|---|---------|---------------|------------------------|
| 1 | **Smart Summarisation** | Compress reports, meeting notes, transactions into executive summaries | Low |
| 2 | **Predictive Alerts** | Forecast stock-outs, overdue payments, exam failures, crop risks | Medium |
| 3 | **Intelligent Search** | Semantic search across records (find "all unpaid invoices from March") | Medium |
| 4 | **Auto-Classification** | Categorise expenses, tickets, documents, leads automatically | Low |
| 5 | **Decision Support** | "Should I approve this loan?" with supporting evidence | Medium |
| 6 | **Natural Language Reports** | Generate narrative reports from raw data in plain English/Luganda | Medium |
| 7 | **Anomaly Detection** | Flag unusual transactions, attendance patterns, sensor readings | Low |
| 8 | **Recommendation Engine** | Suggest products, courses, treatments, suppliers based on history | Medium |
| 9 | **Conversational Assistant** | In-app chat bot for staff help, policy lookup, FAQs | Medium-High |
| 10 | **Document Intelligence** | Extract data from uploaded receipts, invoices, forms, ID cards | Medium |

---

## Discovery Protocol

Run through these questions for every major module in the system:

### Step 1 — Module Scan

For each module, ask:

1. What decisions does a user make daily in this module?
2. What data does this module accumulate over time?
3. What manual work in this module is repetitive but requires judgement?
4. What questions do users ask supervisors that could be answered by data?
5. What early warnings would save this user money or time?

### Step 2 — Pattern Matching

For each "yes" answer above, map it to one or more of the 10 patterns.

### Step 3 — Score Each Opportunity

Score on three dimensions (1–5 each):

| Dimension | 1 | 3 | 5 |
|-----------|---|---|---|
| **Business Impact** | Nice-to-have | Saves hours/week | Core competitive advantage |
| **Data Availability** | No data exists | Partial data | Rich historical data |
| **Implementation Effort** | Custom ML needed | Standard LLM call | Single prompt |

**Priority Score** = Impact × Data × (6 − Effort)

Rank opportunities by priority score descending.

### Step 4 — Gate Assessment

For each opportunity, state:
- Is this a candidate for the **paid AI module** (yes/no)?
- Recommended pricing tier: Starter / Growth / Enterprise AI add-on

---

## AI Opportunity Register Template

```
## AI Opportunity Register — [Project Name] — [Date]

### Module: [Module Name]

| ID | Opportunity | Pattern | Impact | Data | Effort | Score | AI Module Tier |
|----|-------------|---------|--------|------|--------|-------|----------------|
| AI-001 | [name] | [pattern #] | /5 | /5 | /5 | [calc] | [Starter/Growth/Enterprise] |

**Business Case:** [One sentence: who benefits, what they save/gain]
**Data Required:** [What data the AI needs to function]
**Cost Tier:** [Low / Medium / High — detail in ai-cost-modeling]
**Dependencies:** [Any data quality or integration prerequisites]
**Gate Default:** OFF — activated per tenant when AI module is purchased
```

---

## Domain Quick-Reference: Common Opportunities

### School Management (Academia Pro, similar)
- Predict students at risk of failing before end-of-term → Decision Support
- Summarise teacher remarks into report card narrative → Summarisation
- Auto-classify fee payment exceptions for bursar review → Auto-Classification
- Answer parent queries via in-app assistant → Conversational Assistant

### POS / Retail (Maduuka, Longhorn)
- Predict stock-outs 7 days in advance → Predictive Alert
- Flag transactions that deviate from user's normal patterns → Anomaly Detection
- Recommend reorder quantities by SKU → Recommendation Engine
- Generate daily sales narrative for owner → Natural Language Reports

### Healthcare (Medic8)
- Flag patients overdue for follow-up → Predictive Alert
- Summarise patient history for attending clinician → Summarisation
- Extract structured data from uploaded lab reports → Document Intelligence
- Suggest drug interaction warnings → Decision Support

### Farm Management (Kulima)
- Predict harvest yield from weather + soil data → Predictive Alert
- Classify crop disease from uploaded photo description → Auto-Classification
- Recommend fertiliser application by field zone → Recommendation Engine
- Generate farm performance report for cooperative → Natural Language Reports

### ERP / Finance (Longhorn, BIRDC)
- Detect duplicate or anomalous payments → Anomaly Detection
- Classify GL accounts for uploaded receipts → Auto-Classification
- Summarise monthly P&L into board narrative → Summarisation
- Flag budget overruns before period close → Predictive Alert

---

## Output Format

Deliver the AI Opportunity Register as a markdown table (above template) followed by:

1. **Top 3 Quick Wins** — highest score, lowest effort, implement first
2. **Top 1 Strategic Bet** — highest business impact, even if effort is high
3. **Cost Overview** — reference `ai-cost-modeling` for token estimates
4. **Recommended AI Module Tier** — which opportunities bundle into Starter vs Growth vs Enterprise

---

## What NOT to Include

- Do not propose building custom ML models — only LLM API integrations.
- Do not propose AI for features where a simple rule/filter suffices (e.g., "flag invoices > $10,000" does not need AI).
- Do not include opportunities where data does not yet exist and cannot be collected within 6 months.

---

**See also:**
- `references/analytics-patterns.md` — Extended analytics opportunity patterns (A1–A10) with domain maps for school, healthcare, POS, farm, and ERP — use for analytics-heavy modules
- `ai-feature-spec` — Design any opportunity from this register into a full feature blueprint
- `ai-cost-modeling` — Token cost estimates per opportunity
- `ai-metering-billing` — How to gate and charge for AI features
- `ai-integration-section` — Add AI section to SRS/PRD/HLD documents
- `ai-analytics-strategy` — Analytics maturity assessment before selecting opportunities
