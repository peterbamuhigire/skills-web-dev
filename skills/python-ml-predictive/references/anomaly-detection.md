# Anomaly Detection

Find unusual transactions, metric spikes, fraud candidates, or broken pipelines. Three tiers of complexity; start at the simplest that works.

## Tier 1 — Threshold-based

Simplest, cheapest, explainable. Always the first attempt.

### Static threshold
```python
anomalies = df[df["latency_ms"] > 1000]
```
Use when the business has a hard rule (response time SLA, max transaction size).

### Rolling window
```python
window = 30     # days
roll = df["value"].rolling(window, min_periods=window // 2)
mu = roll.mean()
sd = roll.std()
z = (df["value"] - mu) / sd
df["is_anomaly"] = z.abs() > 3
```
Reacts to drift. Tune `k` (here 3) on a known-clean period. `k=2` more sensitive, `k=4` more conservative.

Caveats:
- Symmetric — detects high and low. If you only care about high, use `z > k`.
- Sensitive to seasonality. Do STL decomposition first, then threshold the residual.

## Tier 2 — Statistical

When the distribution is non-Gaussian or has outliers that inflate standard deviation.

### Modified Z-score (robust)
Uses median and MAD (median absolute deviation) instead of mean/std.
```python
from scipy.stats import median_abs_deviation
med = df["value"].median()
mad = median_abs_deviation(df["value"], scale="normal")   # equivalent to std for normal data
modified_z = (df["value"] - med) / mad
df["is_anomaly"] = modified_z.abs() > 3.5
```
Threshold 3.5 is the common reference from Iglewicz & Hoaglin.

### Generalised ESD (multiple outliers)
Statsmodels does not ship this; `pyod` has `GeneralizedESDTest`. For most SaaS use cases Modified Z-score is enough.

### STL decomposition residuals
When the series has trend and seasonality, a raw threshold flags normal peaks. Decompose first:
```python
from statsmodels.tsa.seasonal import STL
stl = STL(series, period=7, robust=True).fit()
residual = stl.resid
mad = median_abs_deviation(residual.dropna(), scale="normal")
flags = residual.abs() > 3.5 * mad
```
The residual is the "unexpected" component. Thresholding it catches anomalies the raw series would hide.

### Seasonal hybrid for daily SaaS metrics
1. STL decompose (period=7 for weekly, 365 for yearly on daily data).
2. Z-score the residual on a 30-day rolling window.
3. Flag when `|z| > 3`.

Good default for dashboards that watch transaction volume, latency, error rate.

## Tier 3 — Model-based

When features are multi-dimensional and the signal is in their combination.

### IsolationForest (sklearn)
Fast, robust, few parameters.
```python
from sklearn.ensemble import IsolationForest

iso = IsolationForest(
    n_estimators=200,
    contamination=0.01,         # expected fraction of anomalies
    random_state=42,
).fit(X_train)

raw_scores = iso.score_samples(X_new)        # higher = more normal
anomaly_scores = -raw_scores                  # higher = more anomalous
is_anomaly = iso.predict(X_new) == -1         # boolean using contamination threshold
```
Use `decision_function` or `score_samples` for continuous ranking; `predict` when you want boolean under a fixed rate.

### Local Outlier Factor (LOF)
Density-based. Good when normal data forms clusters.
```python
from sklearn.neighbors import LocalOutlierFactor
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.01, novelty=True)
lof.fit(X_train)
scores = -lof.score_samples(X_new)
```
Slower than IsolationForest on large data. `novelty=True` required for scoring new rows.

### ECOD / COPOD (PyOD)
Parameter-free, interpretable, fast on tabular data.
```python
from pyod.models.ecod import ECOD
model = ECOD(contamination=0.01).fit(X_train)
scores = model.decision_function(X_new)
```
ECOD uses the empirical CDF per feature; COPOD uses copulas. ECOD is the easiest default in PyOD.

### One-Class SVM — avoid unless you must
Slow, sensitive to kernel choice. Rarely wins.

## Streaming / online detection

For live metrics arriving per minute:

- **Exponentially weighted moving stats.** Maintain running mean/variance; score each new point.
- **River (package)**: `river.anomaly.HalfSpaceTrees`, `OneClassSVM`.
- **CUSUM, EWMA charts**: classical process-control; good for detecting shifts in the mean.

Pattern for a sidecar:
```python
# Maintain per-metric, per-tenant state in Redis
# On each arrival:
#   1. update running stats
#   2. compute z-score
#   3. if |z| > k, emit an event
```

Keep state scoped by tenant or feature — one global state hides per-tenant anomalies.

## Calibrating contamination

`contamination` is the expected fraction of anomalies. Getting it wrong:
- Too high -> false positives flood ops.
- Too low -> misses.

Calibration workflow:
1. Hold out a known-clean period (N weeks where no incidents were reported).
2. Fit on a larger window including that period.
3. Tune `contamination` (or threshold on `score_samples`) so the false-positive rate on the clean period meets target (e.g., < 1 alert/day).
4. Re-tune monthly or when traffic shape changes.

Better than `contamination`: compute `score_samples` and threshold on a percentile of the score distribution from the clean period, e.g., 99.9th percentile.

## Which method when

| Situation | Pick |
| --- | --- |
| Single metric, SLA-style rule | Static threshold |
| Single metric, drifting baseline | Rolling z-score |
| Single metric with seasonality | STL residual + z-score |
| Multi-feature row-level (transactions, logins) | IsolationForest or ECOD |
| Small dataset, clustered normal data | LOF |
| Need interpretability per feature | ECOD |
| Live stream, low-state needs | EWMA / CUSUM |
| Labelled anomalies available (rare) | Supervised classifier |

## Multi-tenant patterns

- Fit one model per tenant when tenants differ materially (volume, timezone, plan).
- Fit a global model with `tenant_id` + per-tenant z-score of each feature when tenants are similar.
- Cold-start tenants: bootstrap with global thresholds; switch to per-tenant after 4–6 weeks of clean data.

## Alert noise control

- **Debounce.** Require N consecutive anomalies within a window before alerting.
- **Group by cause.** De-duplicate alerts from the same upstream event.
- **Severity tiers.** `score > 5` = page; `score > 3` = dashboard flag.
- **Feedback loop.** Let ops mark alerts as "not useful"; feed back into threshold tuning quarterly.

## Anti-patterns

- Using mean/std on heavy-tailed metrics like latency — use median/MAD.
- Alerting on raw daily metric when seasonality is strong — decompose first.
- Retraining the detector on data that includes the anomalies you want to catch.
- Shipping a detector with no operator-facing "suppress" or "mark benign" action.
- `contamination=0.5` or similar defaults; always calibrate.
