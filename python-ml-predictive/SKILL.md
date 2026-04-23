---
name: python-ml-predictive
description: Use when adding forecasting, classification, regression, or anomaly detection
  to a SaaS feature — demand/sales/cash-flow forecasting, churn and risk scoring,
  anomaly detection — with scikit-learn, Prophet, and statsmodels. Covers data prep,
  model serving, monitoring, and explainability.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Python ML & Predictive Analytics
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when adding forecasting, classification, regression, or anomaly detection to a SaaS feature — demand/sales/cash-flow forecasting, churn and risk scoring, anomaly detection — with scikit-learn, Prophet, and statsmodels. Covers data prep, model serving, monitoring, and explainability.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `python-ml-predictive` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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
| Correctness | Model evaluation report | Markdown doc covering train/test split, baseline comparison, and per-segment metrics | `docs/python/ml-eval-2026-04-16.md` |
| Operability | Model deployment runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` covering deploy, drift detection, and re-train procedure | `docs/python/ml-runbook.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Real statistical / machine-learning models for SaaS features: forecasting, classification, regression, anomaly detection. Complements the LLM-based `ai-*` skills — use ML/stats when the problem is numeric, data-rich, and requires explainable, stable outputs.

**Prerequisites:** Load `python-modern-standards` and `python-saas-integration` before this skill. Load `python-data-analytics` for feature engineering.

## When this skill applies

- Demand / sales / cash-flow forecasting (time-series).
- Churn prediction, credit / risk scoring, fraud flagging (classification).
- Price optimization, quantity regression (regression).
- Anomaly detection on SaaS metrics (transaction volume, latency, error rates).
- Any feature where a PHP developer would write a rule that needs tuning from data.

## When ML vs LLM vs rules (decision rule)

```text
Output is a number or label derived from many numeric features  -> ML
Output is text, summary, classification of language, extraction -> LLM
Output can be stated in < 5 unambiguous rules                    -> Rules (PHP)
Hybrid (e.g., LLM extracts features -> ML classifies)            -> both, pipeline
```

Rules beat ML whenever you can enumerate them — faster, explainable, testable. Reach for ML when the signal is in the data, the rules are fuzzy, and the cost of a wrong answer is modest.

See `references/when-ml-vs-llm-vs-rules.md`.

## Core stack

- **scikit-learn** — classification, regression, clustering, model pipelines, metrics. Default for non-timeseries.
- **statsmodels** — ARIMA / ETS / SARIMA, rigorous statistical output.
- **Prophet** (or NeuralProphet) — seasonal + holiday-aware forecasts with minimal tuning.
- **XGBoost / LightGBM** — when trees beat linear models, which is often.
- **PyOD** — anomaly detection algorithms (isolation forest, LOF, ECOD).
- **SHAP** — explainability.
- **joblib** — model serialization.
- **numpy / pandas** — pre-/post-processing.

Avoid starting with deep learning. Tabular SaaS problems are almost always best solved with gradient-boosted trees or linear models. Deep learning earns its keep only for unstructured data (text, images, audio) — for which we usually call LLMs or pre-trained models instead of training from scratch.

## Data preparation discipline

Leakage is the silent killer. Prevent it with process, not vigilance.

**Splits:**
- Random split for IID tabular → `train_test_split(..., stratify=y)`.
- Time-series → **time-based split** only. Training data must precede validation, which must precede test. No shuffling.
- Grouped data (per customer, per tenant) → `GroupKFold`. Never let the same customer appear in train and test.

**Leakage sources to eliminate:**
- Target-derived features (e.g., "days since last invoice" when predicting next invoice).
- Future data in features (aggregations that include the label row).
- Preprocessing on full data before split (fit scalers/encoders on train only).

Always wrap preprocessing in a **Pipeline** so fit-on-train/apply-on-test is automatic:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier

preprocess = ColumnTransformer([
    ("num", StandardScaler(), numeric_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=10), categorical_cols),
])

model = Pipeline([("prep", preprocess), ("clf", GradientBoostingClassifier(random_state=42))])
model.fit(X_train, y_train)   # scaler fits only on train
```

See `references/data-prep.md`.

## Time-series forecasting

**Prophet** — use when you have daily or weekly data with yearly / weekly seasonality and holidays matter. Minimal tuning, business-friendly confidence intervals.

```python
from prophet import Prophet

df_fc = df.rename(columns={"date": "ds", "sales": "y"})
m = Prophet(yearly_seasonality=True, weekly_seasonality=True, holidays=kenya_holidays)
m.fit(df_fc)
future = m.make_future_dataframe(periods=90, freq="D")
forecast = m.predict(future)     # yhat, yhat_lower, yhat_upper
```

**statsmodels ARIMA / SARIMA / ETS** — use when you need rigor (AIC, residual diagnostics, significance), simple series without holidays, or when Prophet is overkill.

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

model = SARIMAX(y_train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
res = model.fit(disp=False)
forecast = res.get_forecast(steps=12)
mean = forecast.predicted_mean
ci = forecast.conf_int()
```

**Always produce intervals**, not just point forecasts. Users need to see uncertainty. See `references/forecasting-prophet.md` and `references/forecasting-statsmodels.md`.

## Classification & regression (tabular)

Default model order to try:

1. Logistic regression (classification) / Ridge (regression) — fast, interpretable baseline.
2. Gradient Boosting (sklearn / XGBoost / LightGBM) — usually the winner on tabular.
3. Random Forest — second try if GB is unstable.
4. Neural network — only if you have > 100K rows, heavy feature engineering fails, and you have time.

**Hyperparameter tuning:** `RandomizedSearchCV` with a small budget first, then refine. Don't grid-search over 10,000 combinations.

**Metrics — never just accuracy:**
- Binary classification, balanced: ROC-AUC, F1.
- Binary classification, imbalanced (churn, fraud): precision@k, recall@k, precision-recall AUC.
- Multiclass: macro-F1, log-loss.
- Regression: MAE, RMSE, R². MAPE only when no zeros in target.

See `references/classification-regression-sklearn.md` and `references/evaluation-metrics.md`.

## Anomaly detection

Three tiers in order of complexity:

1. **Threshold on a metric** (simplest): rolling mean ± 3 × rolling std. Catch big, easy anomalies, run cheap.
2. **Statistical distribution**: Modified Z-score (robust to outliers), ESD test, STL decomposition residuals.
3. **Model-based**: **IsolationForest** (sklearn) or **ECOD** (PyOD). Best for multi-feature anomalies.

```python
from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.01, random_state=42).fit(X_train)
scores = -iso.score_samples(X_new)   # higher = more anomalous
```

Calibrate thresholds on a known-clean period. Re-calibrate monthly. See `references/anomaly-detection.md`.

## Model serving

Lightweight by default. No MLflow/Kubeflow unless you're genuinely running dozens of models.

**Serialization:** `joblib.dump(model, path)`. Pin sklearn/xgboost versions in `pyproject.toml` — pickle format breaks across major versions.

**Loading:** eager-load at sidecar startup or worker startup. Keep the model in memory for the life of the process. Never load per request.

```python
# src/service_name/ml/churn.py
from joblib import load
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "artifacts" / "churn_v3.joblib"
_model = load(MODEL_PATH)     # loads once at import

def score(features: dict) -> float:
    X = build_feature_frame(features)
    return float(_model.predict_proba(X)[0, 1])
```

**Versioning:** filename includes semver or date (`churn_v3.joblib`, `demand_20260301.joblib`). Current version is a symlink. Rollback = flip symlink + restart.

**A/B tests / shadow mode:** run new model alongside old on same inputs, log both predictions, compare offline.

See `references/model-serving.md`.

## Monitoring & drift

Models degrade silently. Detect it.

**Feature drift:** distributions of inputs shift over time. Monitor `mean`, `std`, `quantiles` of each input feature vs. a reference window. Use population stability index (PSI) or Kolmogorov-Smirnov statistic.

**Prediction drift:** distribution of predictions shifts. Cheap proxy for feature drift.

**Performance drift:** requires labels (arriving later). Log predictions, match to truth when it arrives, compute rolling metric.

**Alert when:** PSI > 0.2 for any feature, or monthly metric deviates > N% from training baseline.

**Retraining triggers:** calendar (monthly/quarterly), drift alert, or drop in business KPI.

See `references/monitoring-and-drift.md`.

## Explainability

Users and regulators ask "why?" Have an answer.

**Global:** feature importance from the model (`model.feature_importances_` for trees, coefficients for linear).

**Local (per prediction):** SHAP values. Log top-3 contributing features per prediction for high-stakes scores (credit, risk, fraud).

```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_sample)
```

Confidence intervals on predictions matter as much as the prediction itself. Regressors: use quantile regressors or bootstrap. Classifiers: calibrate probabilities with `CalibratedClassifierCV`.

See `references/explainability.md`.

## Integration patterns

**Sidecar (sync scoring):** small, fast models. `POST /score` → features in → prediction + confidence out. Latency budget < 200ms.

**Worker (batch scoring):** nightly scoring of all customers for churn; bulk forecast for all SKUs. Writes results to MySQL where PHP reads them.

**Training:** worker job, runs on a schedule. Output: new model artifact + metrics report. Never train in a sidecar.

## Pitfalls specific to SaaS

- **Multi-tenant models:** one global model vs. per-tenant models? Start global + tenant as a feature. Go per-tenant only with evidence.
- **Cold start:** new tenants have no history. Fall back to global model or rules. Plan this from day one.
- **Label leakage via user actions:** if users can act on a prediction (e.g., flagging fraud), make sure those actions don't become features for the next model version without an offset.
- **Class imbalance:** 2% churn rate = baseline accuracy of 98% with a constant "no" predictor. Use `class_weight="balanced"`, or downsample, or use threshold tuning.
- **Currency / units:** check whether you're predicting log(amount) or amount; mismatched exponents produce nonsense.

## Anti-patterns

- Training on the full dataset "to get better results." You can't measure the result.
- Deploying a model with no baseline (constant predictor, simple rule). You won't know if it's actually helping.
- Serving with `model.predict(X)` inside the request handler without timeout or concurrency limits.
- Storing model artifacts in git. Use a models/ directory that's gitignored; artifact store is S3 or similar.
- Retraining nightly "just because." Retrain on a trigger.
- Ignoring calibration on probability outputs shown to users. A "40% churn risk" is meaningless unless calibrated.

## References

- `references/when-ml-vs-llm-vs-rules.md`
- `references/data-prep.md`
- `references/forecasting-prophet.md`
- `references/forecasting-statsmodels.md`
- `references/classification-regression-sklearn.md`
- `references/anomaly-detection.md`
- `references/evaluation-metrics.md`
- `references/model-serving.md`
- `references/monitoring-and-drift.md`
- `references/explainability.md`

## See also

- `ai-predictive-analytics` — LLM-based prediction (use when features are unstructured text).
- `ai-evaluation` — for LLM output quality; ML evaluation is different (this skill).
- `saas-business-metrics` — to decide which outcome to model.