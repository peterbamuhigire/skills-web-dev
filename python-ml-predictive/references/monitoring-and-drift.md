# Monitoring and Drift

Models degrade silently. The business keeps acting on numbers that are no longer accurate. Monitoring exists to detect this early.

Three classes of drift, in order of how soon you can catch them:

1. **Feature drift** — distribution of inputs shifts.
2. **Prediction drift** — distribution of outputs shifts.
3. **Performance drift** — metric vs truth changes (needs labels, which arrive later).

## Feature drift

### Population Stability Index (PSI)

Discretise each feature into bins (usually 10 deciles on the **reference** window), then compare bin proportions between reference and recent windows.

```python
import numpy as np
import pandas as pd

def psi(reference: pd.Series, recent: pd.Series, bins: int = 10) -> float:
    # Use reference quantiles so bins are fixed at reference time
    cuts = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    ref_counts, _ = np.histogram(reference, bins=cuts)
    rec_counts, _ = np.histogram(recent,    bins=cuts)
    ref_p = ref_counts / max(ref_counts.sum(), 1)
    rec_p = rec_counts / max(rec_counts.sum(), 1)
    # Laplace smoothing
    ref_p = np.where(ref_p == 0, 1e-6, ref_p)
    rec_p = np.where(rec_p == 0, 1e-6, rec_p)
    return float(np.sum((rec_p - ref_p) * np.log(rec_p / ref_p)))
```

Interpretation (industry rule of thumb):
- PSI < 0.1 — stable.
- 0.1 ≤ PSI < 0.2 — moderate drift, investigate.
- PSI ≥ 0.2 — significant drift, retrain or pause.

Store per-feature PSI as a time series. Alert on breach.

### Kolmogorov-Smirnov (KS) test — continuous features
```python
from scipy.stats import ks_2samp
stat, p = ks_2samp(reference, recent)
# Flag if p < 0.01 and stat > 0.1 (both — tiny shifts in huge samples pass p-test but lack business meaning)
```

### Chi-square — categorical features
```python
from scipy.stats import chi2_contingency
table = pd.crosstab(index=np.concatenate([np.full(len(ref), "ref"), np.full(len(rec), "rec")]),
                    columns=pd.concat([ref, rec]))
chi2, p, _, _ = chi2_contingency(table)
```

### Jensen-Shannon divergence
Symmetric, bounded (0–1 with log2), good for distribution comparison without assuming Gaussian shape.
```python
from scipy.spatial.distance import jensenshannon
# jensenshannon returns the distance (sqrt of divergence). Square it for divergence.
d = jensenshannon(ref_p, rec_p, base=2)
js_divergence = d ** 2
```

### What to monitor per feature
- Mean, std, median.
- Quartiles (p10, p25, p50, p75, p90).
- Share missing.
- PSI vs reference.
- Top 5 categorical values and their share (for categorical features).

Publish these to your metrics backend (Prometheus, CloudWatch, MySQL summary table). Plot per-feature, per-tenant cohort, per-week.

## Prediction drift

Cheap to compute: store every prediction with a timestamp and compare the score distribution across windows.

Metrics:
- Mean predicted probability.
- Share of predictions above operating threshold (e.g., share flagged as high-risk).
- PSI of the prediction score histogram vs reference.

If the feature distribution is stable but predictions drift, something in a feature or encoder changed silently (new category, stale data). Investigate upstream.

## Performance drift

Best but laggy. You need labels.

### How labels arrive
- Churn: confirmed 30–90 days after prediction.
- Demand forecast: actuals come in daily.
- Fraud: confirmed by ops review within days.
- Credit risk: labels may take months or years.

Log predictions with:
- `prediction_id` (UUID)
- `model_version`
- `tenant_id`
- `entity_id` (customer, SKU, transaction)
- `features_snapshot` (JSON)
- `score`
- `predicted_at`

When the label arrives, join on `prediction_id` and compute rolling metrics: MAE, ROC-AUC, precision@k. Alert if metric drops > 10–20% vs training baseline.

## Reference window management

The "reference" is the training window plus a held-out period with known stable performance.

Rules:
- Reference window must be **frozen** until the next retrain.
- Do not roll the reference automatically. Drift disappears if you do.
- Store reference summary stats (not the raw data) inside the model artifact.

Example artifact metadata:
```python
artifact = {
    "model": model,
    "version": "churn_v3",
    "trained_at": "2026-01-15",
    "reference_stats": {
        "mrr":        {"mean": 812.5, "std": 430.1, "p10": 99, "p50": 650, "p90": 1800},
        "logins_30d": {"mean": 28.4, "std": 15.2, "p10": 6, "p50": 27, "p90": 55},
        "plan":       {"free": 0.42, "pro": 0.48, "enterprise": 0.10},
    },
    "prediction_reference": {
        "score_mean": 0.087, "score_p90": 0.23, "flag_rate": 0.05,
    },
}
```

## Alert thresholds

| Signal | Warn | Alert |
| --- | --- | --- |
| PSI per feature | 0.1 | 0.2 |
| Share missing per feature | +50% vs ref | +100% vs ref |
| Prediction flag rate | 1.5× ref | 2× ref |
| New unknown category share | > 5% | > 15% |
| Rolling MAE / MAPE | +10% vs ref | +25% vs ref |
| ROC-AUC (when labels arrive) | −0.02 vs ref | −0.05 vs ref |

Never alert on every feature at once. Prioritise the top-N features by model importance (see `explainability.md`). A PSI spike in a feature with 2% importance is noise; the same spike in a top feature is critical.

## Retraining triggers

Retrain on any of:

1. **Calendar** — monthly or quarterly, scheduled.
2. **Drift alert** — PSI > 0.2 for important features across two consecutive windows.
3. **Performance drop** — rolling metric exceeds alert threshold for a week.
4. **Business KPI regression** — the thing the model was supposed to help (churn, revenue) moves the wrong way.
5. **Data schema change** — new feature added, old feature deprecated, source system changed.

Do **not** retrain nightly. Nightly retraining hides drift (the model chases it) and mixes development with production.

## Multi-tenant notes

- Compute drift **per tenant** for large tenants. A single global drift signal hides a big customer silently breaking.
- For the long tail of small tenants, aggregate. Alert on aggregate.
- Tenant onboarding often creates a drift spike — exclude new tenants from the denominator for the first N weeks.

## Evidently AI (optional)

`evidently` gives a batteries-included drift report:
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset

report = Report(metrics=[DataDriftPreset(), TargetDriftPreset()])
report.run(reference_data=ref_df, current_data=recent_df)
report.save_html("drift.html")
```

Worth it when:
- You want HTML reports for stakeholders.
- You need out-of-the-box widgets (feature plots, PSI, KS, target drift).

Skip it when:
- You have fewer than three models and just want per-feature PSI in your dashboard.
- Your monitoring stack is Prometheus + Grafana and you want custom metrics.

## Implementation sketch

A monitoring worker (daily or hourly):
```python
def monitoring_job():
    bundle = load("artifacts/churn_current.joblib")
    recent = fetch_recent_predictions(days=7)
    ref_stats = bundle["reference_stats"]

    results = []
    for feat, ref in ref_stats.items():
        if isinstance(ref, dict) and "mean" in ref:
            psi_val = psi(get_training_values(feat), recent[feat])
            results.append({"feature": feat, "metric": "psi", "value": psi_val})

    pred_psi = psi(get_training_scores(), recent["score"])
    results.append({"feature": "__prediction__", "metric": "psi", "value": pred_psi})

    write_metrics(results)
    alert_if_breaches(results)
```

Persist `results` to a table; Grafana reads from it; alert rules live in Alertmanager / PagerDuty.

## Anti-patterns

- Monitoring only accuracy — it lags by weeks.
- Rolling reference without locking — drift never shows up.
- Alerting on every feature — noise kills ops.
- Treating drift alerts as model failures instead of signals — sometimes the world changed and the model was right to be confident; sometimes the model is broken. Investigate, don't auto-rollback.
- No ownership — drift alerts with no named owner get ignored.
