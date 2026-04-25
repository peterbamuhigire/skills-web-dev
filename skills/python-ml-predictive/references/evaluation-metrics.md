# Evaluation Metrics

Wrong metric -> wrong model. Pick the metric before the model.

## Classification

### Binary, balanced (~30–70% positive)
- **ROC-AUC.** Rank-based, threshold-free. Primary metric.
- **F1-score.** Balances precision and recall at a chosen threshold.
- **Log-loss.** Penalises over-confident wrong predictions; use when probabilities matter.

```python
from sklearn.metrics import roc_auc_score, f1_score, log_loss
y_prob = model.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= 0.5).astype(int)

print("AUC:", roc_auc_score(y_test, y_prob))
print("F1 :", f1_score(y_test, y_pred))
print("LL :", log_loss(y_test, y_prob))
```

### Binary, imbalanced (churn, fraud, late payment)
ROC-AUC flatters on highly imbalanced data. Prefer:

- **Precision-Recall AUC (PR-AUC).** Sensitive to the minority class.
- **Precision@k / Recall@k.** "Of the top 100 risky customers, how many actually churn?" matches how the business acts.
- **Matthews correlation coefficient (MCC).** Robust single-number summary across imbalance.

```python
from sklearn.metrics import average_precision_score, matthews_corrcoef

pr_auc = average_precision_score(y_test, y_prob)

# Precision @ top-k
k = 100
top_idx = np.argsort(-y_prob)[:k]
precision_at_k = y_test[top_idx].sum() / k
```

Business rule: **pick the metric that maps to the action**. If CS will call the top 50 at-risk accounts per week, `precision@50` is the metric. If compliance must review any flagged case, `recall@threshold` matters more.

### Multiclass
- **Macro-F1.** Averages F1 per class. Treats classes equally — use when rare classes matter.
- **Micro-F1 / accuracy.** Weighted by class frequency. Use when common classes dominate importance.
- **Log-loss.** When probabilities are displayed or used downstream.
- **Per-class confusion matrix.** Always inspect; aggregate metrics hide failure modes.

### Ranking / top-K recommenders
- **NDCG@k**, **MAP@k**, **MRR**. See recommender-specific references.

## Regression

### MAE — Mean Absolute Error
- Average absolute deviation, same units as target.
- Robust to outliers.
- Default for business-facing reports ("our forecast is off by X units on average").

### RMSE — Root Mean Squared Error
- Penalises large errors more heavily.
- Use when big misses matter disproportionately (capacity planning).
- Same units as target.

### R² — coefficient of determination
- Fraction of variance explained.
- 0.9 on one dataset can be worse than 0.6 on another — depends on variance of `y`.
- Good for relative comparison of models on the same test set.

### MAPE — Mean Absolute Percentage Error
- `mean(|y - yhat| / |y|)` expressed as a percentage.
- Unitless, intuitive.
- **Undefined when `y = 0`.** Any forecast series that might have zeros (retail, demand) breaks MAPE.
- Asymmetric: under-prediction is capped at 100%, over-prediction is unbounded.

### sMAPE — symmetric MAPE
- `mean(2 * |y - yhat| / (|y| + |yhat|))`.
- Handles zeros better.
- Bounded 0–200%.
- Still misleading when both `y` and `yhat` are tiny.

### MASE — Mean Absolute Scaled Error
- Scales MAE by the MAE of a naive seasonal forecast.
- Unitless. Comparable across series.
- `MASE < 1` means you beat the naive baseline; `> 1` means you do not.
- Preferred for comparing forecast quality across many SKUs or tenants.

### Huber loss
- Hybrid MAE/RMSE, robust to outliers while smooth near zero.
- Useful as a training loss, not typically as a reported metric.

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
r2 = r2_score(y_test, y_pred)
```

MAPE / sMAPE / MASE:
```python
import numpy as np
def mape(y, yhat):
    mask = y != 0
    return np.mean(np.abs((y[mask] - yhat[mask]) / y[mask])) * 100

def smape(y, yhat):
    return np.mean(2 * np.abs(y - yhat) / (np.abs(y) + np.abs(yhat) + 1e-9)) * 100

def mase(y, yhat, y_train, season=1):
    naive = np.mean(np.abs(np.diff(y_train, n=season)))
    return np.mean(np.abs(y - yhat)) / (naive + 1e-9)
```

## Forecasting

Same metrics as regression, with these priorities:

- **MAE** for operational reporting.
- **RMSE** when large misses are costly.
- **MAPE** if the target has no zeros and business likes percentages.
- **sMAPE** when zeros exist and percentages still wanted.
- **MASE** when comparing across series.

Always report metrics **by horizon band** (1-7d, 8-30d, 31-90d). A model that is excellent at short horizons and poor at long horizons is common; a single average hides that.

Plot actual vs predicted over time — metrics alone miss systematic bias (always forecasting 10% too high).

## Business-aligned thresholds

A metric without a business target is decoration. Establish targets before training:

| Feature | Reasonable first-model targets |
| --- | --- |
| Demand forecast (daily sales) | MAPE < 15%, MAE beats last-year-as-forecast |
| Churn prediction | Precision@top-5% customers > 30%, beats random by > 3× |
| Fraud flagging | Recall > 80% at < 1% false positive rate |
| Cash-flow forecast | MAE < 5% of monthly revenue |
| Anomaly detection | < 1 false alarm per day per tenant |
| Credit / risk score | AUC > 0.7, Brier score calibrated within 5% |

Targets that are too ambitious early discourage teams. Set a "ship if better than baseline, iterate toward target" bar.

## When accuracy is misleading

- **Imbalanced classes.** 98% accuracy is trivial at 2% churn.
- **Shifted cost.** A false negative in fraud may cost $1000; a false positive costs a support call. Weighted cost matrix > accuracy.
- **Time-dependent baseline.** Accuracy drifts with seasonality; compare to seasonal baseline.
- **Micro vs macro.** Micro averages hide rare-class failure.
- **Single train/test split.** Report CV mean and standard deviation.

## Always report

1. Metric on held-out test set.
2. Metric from K-fold CV on train+val (mean, std).
3. Baseline metric (majority class, previous period, naive forecast).
4. Per-segment breakdown (per tenant, per plan, per country).
5. Calibration plot for probability outputs.
6. Error distribution (histogram of residuals or miss sizes).
7. Confusion matrix at the chosen operating point (classification).
