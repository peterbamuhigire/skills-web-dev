---
name: ai-predictive-analytics
description: Implement predictive analytics features using LLM APIs — classification (risk scoring, churn, anomaly), regression (demand forecasting, yield prediction), time series analysis, and prescriptive recommendations. Includes domain-specific prompt templates for school, healthcare, POS, farm, and ERP contexts. Sources: Tyagi (AI for Predictive Maintenance), Garn (Data Analytics for Business), Chaudhary (AI-Based Data Analytics).
---

# AI Predictive Analytics

## What Predictive Analytics Does

Predictive analytics uses historical data patterns to forecast future states or classify current situations. In a SaaS product using LLM APIs, you pre-process data from your database and inject a structured summary into an LLM prompt — the model applies reasoning to predict outcomes, identify risks, or recommend actions.

**Not all prediction requires ML models.** For most SaaS analytics features, a well-structured LLM prompt with clean historical data outperforms a custom ML model because:
- No training data required — the model brings general intelligence.
- Reasoning is explainable in plain English.
- Implementation takes days, not months.

Reserve custom ML models (scikit-learn, XGBoost) for high-volume, latency-sensitive predictions where LLM API costs would be prohibitive.

---

## The Four Prediction Task Types

| Task | Question | Example | Model Approach |
|------|---------|---------|---------------|
| **Classification** | Which category does this belong to? | Is this student at risk? | LLM with labeled examples |
| **Regression** | What numeric value is expected? | How many units will we sell next week? | LLM with trend data |
| **Anomaly Detection** | Is this unusual? | Is this transaction suspicious? | LLM with baseline + deviation |
| **Recommendation** | What action should be taken? | Which supplier should we reorder from? | LLM with constraints + history |

---

## Implementation Pattern

For every predictive feature:

```
1. Define the prediction target
   "Predict: will this student fail their term?" → Binary classification

2. Identify the data signals
   Attendance %, assessment scores, fee payment status, login activity, teacher flags

3. Pre-process in SQL — inject only what matters
   SELECT student_id, attendance_pct, avg_score, days_since_login,
          fee_paid, missed_assessments FROM student_analytics_view
   WHERE tenant_id = ? AND term = ?
   LIMIT 50  -- never inject unbounded data

4. Build the prompt (see templates below)

5. Parse and validate the output schema

6. Display with explanation + confidence + recommended action
```

---

## Domain Prediction Templates

### Template 1: Student At-Risk Classification (School)

**Trigger:** Weekly batch job, or when a teacher flags a student.

**Data to inject per student (one row):**
```
Attendance: 58% | Avg score: 41% | Assessments missed: 3/5
Days since last portal login: 8 | Fee status: 1 month overdue
Teacher flag: "Seems disengaged in class"
```

**System prompt:**
```
You are an academic risk analyst for a school management system.
Analyse each student record and classify their risk level for not completing the current term.

Output format — strict JSON array:
[
  {
    "student_id": <integer>,
    "risk_level": "high|medium|low",
    "confidence": "high|medium|low",
    "primary_signals": ["<signal 1>", "<signal 2>", "<signal 3>"],
    "recommended_action": "<one actionable sentence for the class teacher>",
    "urgency": "immediate|this_week|monitor"
  }
]

Rules:
- high risk: 2+ serious signals (attendance < 60%, score avg < 50%, 3+ missed assessments)
- Do not use student names in the output.
- Language: plain English, suitable for a teacher to read.
- Limit recommended_action to 20 words.
```

**Cost estimate:** 1,500 input tokens + 400 output tokens per batch of 20 students → Haiku at ~$0.002/batch.

---

### Template 2: Sales Demand Forecasting (POS/Retail)

**Trigger:** Sunday night batch job — forecast for next 7 days.

**Data to inject:**
```
Product: Maize Flour 2kg | Last 4 weeks daily sales: [42,38,55,61,44,39,51,48,52,49,58,62,44,40,53,50,60,57,44,41,55,61,47,38,54,52,63,59]
Current stock: 180 units | Reorder lead time: 3 days
Upcoming events: End-of-month salary weekend (3 days away)
```

**System prompt:**
```
You are a retail demand forecasting analyst.
Given historical daily sales data and context, forecast the next 7 days and assess reorder need.

Output — strict JSON:
{
  "product_id": <integer>,
  "forecast_7_day": [<int>, <int>, <int>, <int>, <int>, <int>, <int>],
  "total_forecast_7d": <int>,
  "current_stock": <int>,
  "stockout_risk": "high|medium|low",
  "stockout_day": <int or null>,
  "reorder_now": true|false,
  "reorder_quantity": <int>,
  "confidence": "high|medium|low",
  "reasoning": "<2 sentence explanation>"
}

Consider: day-of-week patterns, trend (increasing/decreasing), seasonality signals in context.
```

---

### Template 3: Patient Deterioration Risk (Healthcare)

**Trigger:** Nightly batch, flagging patients for morning ward round.

**Data to inject per patient:**
```
Diagnosis: Hypertension + T2DM | Days since last visit: 45
Medication adherence: 60% (self-reported) | Last BP reading: 158/98
Last HbA1c: 8.2% (target < 7%) | Missed appointments: 2 in last 3 months
Weight trend: +3.2kg over 6 weeks
```

**System prompt:**
```
You are a clinical care coordinator assistant.
Review each patient record and identify those needing priority follow-up.
Do not diagnose — only flag for clinical review.

Output — strict JSON array:
[
  {
    "patient_ref": "<anonymised ref>",
    "priority": "urgent|high|routine",
    "clinical_signals": ["<signal>", "<signal>"],
    "suggested_follow_up": "<one sentence — type of contact recommended>",
    "timeframe": "today|this_week|this_month"
  }
]

Rules:
- urgent: vital signs critically out of range OR missed 2+ appointments with uncontrolled condition
- Never include patient names or NINs in output.
- Output must not be used as a substitute for clinical judgement.
```

**DPPA note:** Patient health data is Special Personal Data (DPPA S-tier). Pre-process and anonymise before sending to external AI API. Use `patient_ref` (hash), never name or NIN.

---

### Template 4: Crop Yield Prediction (Agriculture/Kulima)

**Trigger:** Monthly, or on demand before planting season.

**Data to inject:**
```
Field: Plot A3 | Crop: Maize | Area: 2.4 acres
Last 3 seasons yield: [18, 22, 19] bags/acre
Soil pH last reading: 5.8 | Fertiliser used last season: DAP 50kg
Rainfall this season to date: 380mm (expected: 450mm at this point)
Pest incidents reported: 1 (aphid, treated)
```

**System prompt:**
```
You are an agricultural analyst for a farm management system in East Africa.
Based on historical yield data and current season conditions, forecast yield for this plot.

Output — strict JSON:
{
  "field_id": <string>,
  "crop": <string>,
  "forecast_yield_bags_per_acre": <float>,
  "forecast_total_bags": <float>,
  "confidence": "high|medium|low",
  "yield_vs_last_season": "higher|similar|lower",
  "key_risk_factors": ["<factor>", "<factor>"],
  "recommended_actions": ["<action>"],
  "reasoning": "<2 sentences>"
}
```

---

### Template 5: Anomaly Detection — Financial Transactions (ERP)

**Trigger:** Real-time on each transaction, or daily batch on previous day's transactions.

**Data to inject:**
```
Vendor: Kampala Supplies Ltd | Amount: UGX 8,450,000
Payment method: Bank transfer | Approved by: John Okello
User's normal transaction size: UGX 500K–2M | Time: 11:47pm (unusual hour)
Vendor last used: 8 months ago | PO number: missing
```

**System prompt:**
```
You are a financial compliance analyst reviewing transactions for anomalies.
Assess each transaction against the user's normal patterns and flag concerns.

Output — strict JSON:
{
  "transaction_id": <string>,
  "anomaly_score": "critical|high|medium|low|none",
  "anomaly_signals": ["<signal>"],
  "requires_review": true|false,
  "review_urgency": "immediate|today|routine",
  "suggested_reviewer_action": "<one sentence>"
}

Signals to consider: amount vs user baseline, timing, missing PO, vendor dormancy, approver pattern.
```

---

## Batch vs Real-Time Prediction

| Use Case | Mode | Why |
|---------|------|-----|
| Student risk scoring | Batch (weekly) | Low urgency; reduces cost 80% vs real-time |
| Demand forecasting | Batch (daily) | Overnight is fine; data doesn't change minute-by-minute |
| Patient deterioration | Batch (nightly) | Morning review round timing |
| Transaction anomaly | Real-time | Fraud window is minutes |
| Crop yield forecast | Batch (monthly) | Season-level planning |

**Cost impact:** Batch jobs process 20–50 records in one API call (lower cost per prediction). Real-time = one call per event.

---

## Prediction Quality Metrics

Measure these before deploying any predictive feature:

| Metric | How to Measure | Target |
|--------|---------------|--------|
| **Precision** | Of all "high risk" flags, how many were actually at risk? | > 70% |
| **Recall** | Of all truly at-risk cases, how many were flagged? | > 80% |
| **False positive rate** | Flags that were wrong — wastes staff time | < 20% |
| **User acceptance** | % of recommendations acted on | > 50% after 3 months |

Run a 30-day shadow period: generate predictions but don't show them to users. Compare predictions to actual outcomes. Adjust prompts before going live.

---

## Model Evaluation for LLM Predictions

```
Confusion Matrix (Classification):
                     Actual Positive    Actual Negative
Predicted Positive   True Positive (TP) False Positive (FP)  ← wasted intervention
Predicted Negative   False Negative (FN) True Negative (TN)   ← missed case (worse)

Precision = TP / (TP + FP)  → accuracy of flags raised
Recall    = TP / (TP + FN)  → coverage of real cases
F1        = 2 × (Precision × Recall) / (Precision + Recall)  → balanced score
```

For risk scoring, **recall matters more than precision** — it's worse to miss a failing student than to flag one who is actually fine.

---

**See also:**
- `ai-analytics-strategy` — KDD/CRISP-DM process, data quality gates, responsible AI
- `ai-feature-spec` — Full feature blueprint for each prediction template
- `ai-cost-modeling` — Batch vs real-time cost comparison
- `ai-analytics-dashboards` — Displaying predictions in UI
- `ai-nlp-analytics` — Text-based prediction (sentiment, document classification)
