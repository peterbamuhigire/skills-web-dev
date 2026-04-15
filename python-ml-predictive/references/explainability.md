# Explainability

Users ask "why?" Regulators demand it. Ops needs it to debug. Build explanations in from day one.

Two scopes:

- **Global** — what drives the model overall.
- **Local** — why *this specific* prediction came out this way.

## Global importance

### Tree-based native importance
```python
import pandas as pd
importances = pd.Series(model.named_steps["clf"].feature_importances_,
                        index=model.named_steps["prep"].get_feature_names_out())
importances.sort_values(ascending=False).head(15)
```

Caveats:
- Sklearn's tree `feature_importances_` is biased toward high-cardinality features.
- Scale with caution: absolute ranks matter more than exact values.

### Permutation importance (preferred)
Shuffle one feature at a time on the held-out set; measure metric drop.

```python
from sklearn.inspection import permutation_importance
result = permutation_importance(model, X_test, y_test,
                                n_repeats=10, random_state=42, n_jobs=-1,
                                scoring="roc_auc")
pd.Series(result.importances_mean, index=X_test.columns).sort_values(ascending=False).head(15)
```

- Model-agnostic.
- Uses the actual metric you care about.
- Slower but trustworthy.
- Correlated features share importance — interpret by group.

### Linear model coefficients
For logistic or ridge, after scaling:
```python
coefs = pd.Series(model.named_steps["clf"].coef_[0],
                  index=model.named_steps["prep"].get_feature_names_out())
coefs.sort_values(key=abs, ascending=False).head(15)
```
Only meaningful when features are scaled consistently. Sign tells direction (positive coefficient increases log-odds).

### Reporting
Publish a top-15 feature list for each model version. Include direction (up/down) and a short plain-language description. This becomes the "what the model cares about" doc for the business.

## Local — per-prediction reasons

Business UIs need "We flagged this customer because: X, Y, Z" — not 80 numbers.

### SHAP values

Shapley values from game theory: exact contribution of each feature to the prediction, summing to the difference from baseline.

#### TreeExplainer — for GBDT/RF/XGBoost
Fast, exact.
```python
import shap
explainer = shap.TreeExplainer(model.named_steps["clf"])
X_trans = model.named_steps["prep"].transform(X_sample)
shap_values = explainer.shap_values(X_trans)         # shape: (n_samples, n_features)
```

#### KernelExplainer — model-agnostic fallback
Slow. Use when TreeExplainer is not applicable (arbitrary pipelines, custom models).
```python
explainer = shap.KernelExplainer(model.predict_proba, X_background)
shap_values = explainer.shap_values(X_sample, nsamples=200)
```

#### LinearExplainer — for linear models
```python
explainer = shap.LinearExplainer(model.named_steps["clf"], X_background)
```

### Top-3 reasons for the UI

Production pattern: compute SHAP per prediction, return top reasons that increased (or decreased) the score.

```python
def top_reasons(bundle, X_row, n: int = 3) -> list[str]:
    prep = bundle["model"].named_steps["prep"]
    clf  = bundle["model"].named_steps["clf"]
    X_t  = prep.transform(X_row)
    shap_values = bundle["explainer"].shap_values(X_t)[0]  # one row
    feat_names  = prep.get_feature_names_out()

    # Pair (name, contribution); pick largest positive contributions
    contribs = sorted(zip(feat_names, shap_values), key=lambda kv: -kv[1])
    top = contribs[:n]

    return [humanise(name, X_row, value) for name, value in top]
```

`humanise` maps feature names to sentences users understand:
- `logins_30d = 2` -> "Logged in only 2 times in the last 30 days (low)."
- `tickets_open = 5` -> "Has 5 open support tickets (high)."
- `mrr = 50` -> "Monthly revenue USD 50 (below cohort median)."

Keep a mapping in code (not inline strings scattered across modules). Translate per locale when serving multiple languages.

### Precomputing the explainer
TreeExplainer is cheap to build. Build it at training time and ship it inside the artifact:
```python
artifact["explainer"] = shap.TreeExplainer(model.named_steps["clf"])
```
Avoid recomputing per request.

### Sampling for aggregate explanations
For global SHAP summaries, compute on a sample (1000–5000 rows) and plot:
```python
shap.summary_plot(shap_values, X_sample, plot_type="bar", max_display=15)
shap.summary_plot(shap_values, X_sample, max_display=15)   # dot-plot
```

## Calibration plots

A probability of 0.4 must mean "~40% of such cases are positive." Otherwise the UI lies to users.

```python
from sklearn.calibration import CalibrationDisplay
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
CalibrationDisplay.from_estimator(model, X_val, y_val, n_bins=10, ax=ax)
plt.title("Churn model calibration")
```

Read:
- Below diagonal = model over-confident (claims 80% but only 60% are positive).
- Above diagonal = model under-confident.
- Step-like = poor fit, too few bins or too few samples.

Recalibrate with `CalibratedClassifierCV` if points stray > 5–10% from the diagonal in production-relevant bins (usually the 0.3–0.7 range).

## Confidence intervals

For forecasts (Prophet, SARIMA) use the library's native intervals. For regression GBDT use quantile regression (see `classification-regression-sklearn.md`).

Display in the UI:
- "Forecast: 1,250 units (80% range 1,050–1,450)."
- Never show a bare number for a decision that costs money.

## UI patterns

- **Score + range + 3 reasons.** Standard card.
- **Show uncertainty.** Colour the band, not just a line.
- **Avoid false precision.** Do not show "74.2836%"; show "74% (moderate confidence)".
- **Let users disagree.** Capture "looks wrong" feedback tied to `prediction_id`. Feeds retraining.

## Regulatory context

### Credit / scoring (adverse-action notices)
Where regulation applies (FCRA in US, similar rules elsewhere), a denial based on a model must state specific reasons. SHAP top-features mapped to plain English is the standard approach.

- Store the reasons alongside the decision for the legal retention period.
- Reasons must be truthful — they must be the features that actually drove the denial, not a sanitised summary.
- Human review path must exist.

### East African data-protection (Uganda DPPA, Kenya DPA, Tanzania DPA)
For automated decisions about individuals:
- Document the purpose and logic of the model in the DPIA.
- Allow subjects to request a human review of a decision.
- Inform subjects when an automated decision was made and what factors mattered.

Cross-reference: `uganda-dppa-compliance`, `dpia-generator`.

### Audit trail
Log per prediction:
- `prediction_id`, `model_version`, `timestamp`.
- Feature snapshot used.
- Score.
- Top-N reasons returned.
- Any subsequent override.

Retain per retention policy. Without this trail you cannot defend or debug a decision weeks later.

## Deep learning explanation — brief

- **Attention weights** are not faithful explanations of transformer outputs. Do not present them to users as "reasons".
- **Integrated gradients, GradCAM** exist for neural nets but add noise.
- For tabular problems, GBDT + SHAP dominates for both accuracy and explainability. Deep learning rarely earns the complexity.

## Anti-patterns

- Showing raw SHAP values to users (numbers are meaningless out of context).
- Using global importance as the per-prediction reason (wrong: reasons differ per row).
- Calibration ignored — "40% risk" means nothing.
- Reasons that are always the same three features regardless of input (sign your SHAP pipeline is broken).
- No human override path for high-stakes decisions.
- Hiding low-confidence predictions behind a friendly number.
