---
name: ai-opportunity-canvas — Analytics Patterns Reference
description: Extended analytics opportunity patterns for the AI Opportunity Canvas — descriptive, diagnostic, predictive, and prescriptive analytics by business domain.
type: reference
---

# Analytics Opportunity Patterns

*Supplement to `ai-opportunity-canvas/SKILL.md` — use during opportunity discovery for analytics-heavy modules.*

## The Analytics Opportunity Spectrum

Every analytics feature sits on a spectrum from simple to sophisticated. Identify the right level for the client's data maturity before recommending.

```
Descriptive → Diagnostic → Predictive → Prescriptive
  (What?)      (Why?)      (What next?)  (Do this)

Low cost                                   High cost
Low data need                         High data need
Low AI involvement              High AI involvement
```

---

## Extended Analytics Patterns (Beyond the 10 Core)

These extend the 10 universal patterns in the main skill for analytics-specific use cases.

| # | Pattern | Type | Token Cost | Batch/Real-time |
|---|---------|------|-----------|----------------|
| A1 | **KPI Narrative** | Descriptive | Low | Batch (daily) |
| A2 | **Trend Explanation** | Diagnostic | Medium | Batch (weekly) |
| A3 | **Cohort Analysis** | Diagnostic | Medium | Batch (monthly) |
| A4 | **Risk Scoring** | Predictive | Medium | Batch (weekly) |
| A5 | **Demand Forecasting** | Predictive | Medium | Batch (daily/weekly) |
| A6 | **Churn Prediction** | Predictive | Medium | Batch (monthly) |
| A7 | **Sentiment Aggregation** | Diagnostic | Low-Med | Batch (on submission) |
| A8 | **Action Recommendation** | Prescriptive | Medium | Batch or Real-time |
| A9 | **Anomaly Explanation** | Diagnostic | Low | Real-time |
| A10 | **Executive Summary** | Descriptive | Low | Batch (daily/weekly) |

---

## Domain Analytics Opportunity Maps

### School Management

| Opportunity | Pattern | Data Required | Maturity Needed |
|------------|---------|--------------|----------------|
| At-risk student identification | A4 Risk Scoring | Attendance, scores, login activity (12+ weeks) | Stage 2+ |
| Term performance narrative | A1 KPI Narrative | Grade summary, attendance rate | Stage 1+ |
| Parent feedback sentiment | A7 Sentiment Aggregation | Free-text feedback (50+ responses) | Stage 1+ |
| Fee default prediction | A6 Churn Prediction | Payment history (2+ terms) | Stage 2+ |
| Class performance comparison | A3 Cohort Analysis | Cross-class score data | Stage 2+ |
| Teacher-parent communication recommendations | A8 Action Recommendation | Risk scores + contact history | Stage 3+ |

### Healthcare / Medic8

| Opportunity | Pattern | Data Required | Maturity Needed |
|------------|---------|--------------|----------------|
| Patient deterioration risk | A4 Risk Scoring | Vitals trend, appointment adherence (3+ months) | Stage 2+ |
| Appointment no-show prediction | A6 Churn Prediction | 6+ months appointment history | Stage 2+ |
| Patient feedback themes | A7 Sentiment Aggregation | Post-visit feedback (30+ responses) | Stage 1+ |
| Prescription adherence alert | A5 Demand Forecasting | Repeat prescription patterns | Stage 2+ |
| Diagnostic summary from notes | A1 KPI Narrative | Clinical notes (doctor input) | Stage 1+ |
| Resource demand forecast | A5 Demand Forecasting | Daily patient volume 12+ months | Stage 2+ |

### POS / Retail / Maduuka

| Opportunity | Pattern | Data Required | Maturity Needed |
|------------|---------|--------------|----------------|
| Stockout prediction | A5 Demand Forecasting | Daily sales per SKU (8+ weeks) | Stage 1+ |
| Sales trend explanation | A2 Trend Explanation | Sales time series + event calendar | Stage 1+ |
| Customer churn risk | A6 Churn Prediction | Purchase frequency per customer (3+ months) | Stage 2+ |
| Transaction anomaly explanation | A9 Anomaly Explanation | Transaction history + user baseline | Stage 1+ |
| Daily sales narrative for owner | A1 KPI Narrative | Day's transaction summary | Stage 1+ |
| Product mix recommendation | A8 Action Recommendation | Sales + margin + stock data | Stage 2+ |

### Farm Management / Kulima

| Opportunity | Pattern | Data Required | Maturity Needed |
|------------|---------|--------------|----------------|
| Crop yield forecast | A5 Demand Forecasting | 3+ seasons yield history + weather | Stage 2+ |
| Pest risk alert | A4 Risk Scoring | Pest incident history + weather | Stage 2+ |
| Harvest timing recommendation | A8 Action Recommendation | Yield forecast + market price trend | Stage 2+ |
| Cooperative performance comparison | A3 Cohort Analysis | Member yield and input cost data | Stage 2+ |
| Soil health trend narrative | A2 Trend Explanation | Soil pH + fertiliser records | Stage 1+ |

### ERP / Finance / Longhorn / BIRDC

| Opportunity | Pattern | Data Required | Maturity Needed |
|------------|---------|--------------|----------------|
| Cash flow forecast | A5 Demand Forecasting | 6+ months receivables/payables | Stage 2+ |
| Payment anomaly explanation | A9 Anomaly Explanation | Transaction history + vendor baseline | Stage 1+ |
| Budget variance narrative | A1 KPI Narrative | Budget vs actuals by cost centre | Stage 1+ |
| Vendor performance scoring | A4 Risk Scoring | Delivery time, quality, price history | Stage 2+ |
| Board report executive summary | A10 Executive Summary | Monthly P&L, KPIs, alerts | Stage 1+ |
| Procurement demand forecast | A5 Demand Forecasting | 12+ months purchase orders | Stage 2+ |

---

## Analytics Opportunity Scoring Addendum

When scoring analytics opportunities, add a **Data Readiness** factor:

| Score | Data Readiness |
|-------|---------------|
| 1 | Data does not exist or is in paper/Excel |
| 2 | Data is in the database but incomplete or dirty |
| 3 | Data is complete and clean for 6+ months |
| 4 | 12+ months of complete, clean, consistent data |
| 5 | Multi-year, validated, enriched with external signals |

**Adjusted priority score for analytics:** Impact × DataReadiness × (6 − Effort)

This prevents recommending sophisticated predictive analytics to clients who have 2 weeks of data.

---

## Data Quality Pre-Check Questions

Before registering any analytics opportunity, ask:

1. How long has data been collected in this module? *(Need minimum 8 weeks for descriptive; 6 months for predictive)*
2. Is there a free-text field that could be analysed? *(Unlocks NLP analytics)*
3. Does the client already export reports manually? *(Automation = high perceived value)*
4. Is there a KPI the manager checks every day? *(That KPI belongs on the dashboard)*
5. What decision is delayed because the manager lacks information? *(That's the predictive feature)*
