# Forecasting with Prophet

Prophet is the right default for daily or weekly business series with holidays and seasonality. Minimal tuning, business-friendly intervals.

## When Prophet fits

- Daily or weekly granularity (not sub-hourly).
- Clear yearly or weekly seasonality.
- Holidays or known events shift the series.
- Users will ask "what is the uncertainty band?" — Prophet gives it by default.
- Missing data and irregular gaps — Prophet tolerates them.

## When to prefer statsmodels instead

- Sub-daily granularity, stationary series, rigorous AIC-based model selection needed.
- Need multivariate VAR or clear autoregressive structure.
- Academic or audit context where SARIMA is expected.

See `forecasting-statsmodels.md`.

## Minimal usage

```python
import pandas as pd
from prophet import Prophet

# df has columns: date, sales
df_fc = df.rename(columns={"date": "ds", "sales": "y"})

m = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    interval_width=0.8,
)
m.fit(df_fc)

future = m.make_future_dataframe(periods=90, freq="D")
forecast = m.predict(future)

forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail()
```

`ds` must be datetime. `y` must be numeric (no commas, no currency codes). Clean before fit.

## Seasonality modes

### Additive (default)
Seasonal effect is a fixed magnitude in the target units. Use when fluctuations are roughly constant in size regardless of trend.

### Multiplicative
Seasonal effect scales with the trend. Use when peaks grow as the business grows (retail, SaaS MRR approaching market saturation is an exception).
```python
Prophet(seasonality_mode="multiplicative")
```

Diagnostic: plot `y` over time. If the peak-to-trough range grows proportionally with the trend, use multiplicative.

### Custom seasonality
For monthly paydays, weekly payroll runs, or quarterly cycles:
```python
m.add_seasonality(name="monthly", period=30.5, fourier_order=5)
m.add_seasonality(name="quarterly", period=91.25, fourier_order=8)
```
`fourier_order` controls smoothness. Start at 5–10. Higher fits more wiggles and risks overfit.

Disable a default seasonality if you are adding a replacement:
```python
Prophet(weekly_seasonality=False).add_seasonality("weekly", 7, fourier_order=3)
```

## Holidays and events

### Country holidays
```python
m.add_country_holidays(country_name="KE")   # Kenya
m.add_country_holidays(country_name="UG")   # Uganda
m.add_country_holidays(country_name="TZ")   # Tanzania
```
Built from the `holidays` Python package. Check the list is current.

### Custom events (product launches, stock-outs, marketing campaigns)
```python
promotions = pd.DataFrame({
    "holiday": "black_friday",
    "ds": pd.to_datetime(["2024-11-29", "2025-11-28"]),
    "lower_window": 0,
    "upper_window": 3,
})
m = Prophet(holidays=promotions)
```
`lower_window`/`upper_window` capture lead-up and tail-off days.

### Combining country + custom
Build a combined DataFrame or call `add_country_holidays` after constructing with a custom `holidays` argument.

## External regressors (`add_regressor`)

When an external driver (marketing spend, weather, gold price) affects the series:
```python
m = Prophet()
m.add_regressor("marketing_spend", standardize=True)
m.add_regressor("is_promo", standardize=False)
m.fit(df_fc)     # df_fc must contain those columns

future = m.make_future_dataframe(periods=90, freq="D")
future["marketing_spend"] = planned_spend
future["is_promo"] = planned_promo_flags
forecast = m.predict(future)
```
Rules:
- Regressor values must be known for the forecast window. Do not add a driver you cannot provide at prediction time.
- Standardise continuous regressors. Leave booleans as 0/1.
- Correlated regressors confuse coefficients. Remove near-duplicates.

## Cross-validation with cutoffs

Prophet ships a rolling-origin CV:
```python
from prophet.diagnostics import cross_validation, performance_metrics

df_cv = cross_validation(
    m,
    initial="730 days",   # first training window
    period="90 days",     # step between cutoffs
    horizon="30 days",    # forecast horizon
)
df_metrics = performance_metrics(df_cv)
df_metrics[["horizon", "mae", "rmse", "mape"]].head()
```

Rules of thumb:
- `initial` should contain at least 2 full seasonal cycles (so 2+ years for yearly seasonality).
- `horizon` must match the business forecast horizon (don't validate at 7 days if you ship 90-day forecasts).
- Report metrics by horizon band, not just the average. Accuracy degrades as horizon grows.

## Hyperparameter tuning

Prophet has few knobs; tune these only:

| Parameter | Effect | Typical range |
| --- | --- | --- |
| `changepoint_prior_scale` | Trend flexibility | 0.001 to 0.5 (default 0.05) |
| `seasonality_prior_scale` | Seasonal flexibility | 0.01 to 10 (default 10) |
| `holidays_prior_scale` | Holiday effect size | 0.01 to 10 (default 10) |
| `seasonality_mode` | additive / multiplicative | both |
| `changepoint_range` | Fraction of history where changepoints allowed | 0.8 to 0.95 |

Small grid search:
```python
import itertools
param_grid = {
    "changepoint_prior_scale": [0.01, 0.05, 0.1, 0.5],
    "seasonality_prior_scale": [1.0, 10.0],
    "seasonality_mode": ["additive", "multiplicative"],
}
best = (None, float("inf"))
for params in (dict(zip(param_grid, v)) for v in itertools.product(*param_grid.values())):
    m = Prophet(**params).fit(df_fc)
    cv = cross_validation(m, initial="730 days", period="90 days", horizon="30 days")
    mae = performance_metrics(cv)["mae"].mean()
    if mae < best[1]:
        best = (params, mae)
```

Do not tune on final test set. Tune with CV, then fit once on full history for deployment.

## Diagnostics

Always review:
- `m.plot(forecast)` — does the fit make sense visually?
- `m.plot_components(forecast)` — are trend, weekly, yearly components sensible?
- Residuals (`y - yhat`): should be roughly zero-mean and unstructured. Trend in residuals = missed signal.
- Compare MAPE and MAE by horizon band (1-7 days vs 30+ days).

Target metrics for SaaS forecasting (sales, demand):
- MAPE < 10%: excellent.
- MAPE 10–20%: acceptable.
- MAPE > 25%: investigate seasonality, holidays, regressors, or wrong model.

MAPE fails when target has zeros; use sMAPE or MASE. See `evaluation-metrics.md`.

## Known limitations

- **Not probabilistic under the hood for regressors.** `yhat_lower`/`yhat_upper` come from trend uncertainty plus seasonality uncertainty; with many regressors the interval can be too narrow.
- **Cannot handle negative trends that flip sign.** If your series goes from growing to shrinking, Prophet adapts slowly.
- **Bad for short series.** Under 2 years of daily data, prefer exponential smoothing.
- **Bad for sub-daily.** Use statsmodels or a specialised library.
- **Single-variable only.** No VAR. Use regressors or statsmodels for multivariate.
- **Python-only.** Fitted object cannot be serialised cross-language; keep scoring in Python.

## Multi-tenant patterns

- **Per-tenant Prophet models** are common (one per SKU, per store, per tenant). Fit in a worker job; store per-tenant artifact. Use joblib per model.
- **Global Prophet with tenant regressor** is weaker because Prophet is univariate at heart. Avoid unless tenants are near-identical.
- **Cold start:** new tenant/SKU with < 60 data points — fall back to a peer-group median or a global baseline.
- **Serving:** fit artifacts can be large. Consider lazy-loading per request only if you have thousands of models; otherwise eager-load the active set.

See `model-serving.md` for artifact management.
