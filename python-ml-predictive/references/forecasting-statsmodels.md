# Forecasting with statsmodels

Use statsmodels when you need statistical rigour: AIC-based selection, residual diagnostics, significance tests, classical ARIMA / SARIMA / SARIMAX / ETS.

## When statsmodels wins over Prophet

- Sub-daily data (hourly latency, per-minute transactions).
- Short series (under 2 years) where Prophet overfits seasonality.
- You want diagnostic output the audit or finance team expects (p-values, AIC).
- Series behaviour is clearly autoregressive, with few calendar effects.
- Multivariate (VAR) or exogenous regressors with interpretable coefficients.

When in doubt with daily SaaS data, try Prophet first, statsmodels second.

## Stationarity — the precondition

ARIMA-family models assume the differenced series is stationary (constant mean and variance).

### Augmented Dickey-Fuller (ADF)
```python
from statsmodels.tsa.stattools import adfuller

stat, p, *_ = adfuller(y)
print(p)                 # p < 0.05 -> stationary
```
Null hypothesis: unit root (non-stationary). Small p-value means stationary.

### KPSS (complementary)
```python
from statsmodels.tsa.stattools import kpss

stat, p, *_ = kpss(y, regression="c", nlags="auto")
print(p)                 # p > 0.05 -> stationary
```
Null is opposite: trend-stationary. Large p means stationary.

Run both. Agreement is strong evidence. Disagreement means the series may be borderline.

### Differencing
If non-stationary, difference:
```python
y_diff = y.diff().dropna()
```
Check again. Most business series need `d = 1`. Seasonal differencing `D = 1` handles yearly or weekly patterns. Over-differencing harms the model — stop at the smallest `d` that yields stationarity.

## Order selection — ACF and PACF

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

plot_acf(y_diff, lags=40)
plot_pacf(y_diff, lags=40, method="ywm")
```

Interpretation rules:

| Pattern | Suggested model |
| --- | --- |
| ACF decays slowly, PACF cuts off at lag p | AR(p) |
| ACF cuts off at lag q, PACF decays slowly | MA(q) |
| Both decay | ARMA(p, q), try small values |
| Spikes at seasonal lags | Add SARIMA seasonal terms |

Auto-selection with `pmdarima`:
```python
from pmdarima import auto_arima
model = auto_arima(y, seasonal=True, m=12, stepwise=True, suppress_warnings=True)
print(model.order, model.seasonal_order, model.aic())
```
Good first pass. Always sanity-check the chosen order against ACF/PACF.

## ARIMA

```python
from statsmodels.tsa.arima.model import ARIMA

res = ARIMA(y_train, order=(2, 1, 1)).fit()
print(res.summary())

forecast = res.get_forecast(steps=30)
mean = forecast.predicted_mean
ci = forecast.conf_int(alpha=0.2)   # 80% CI
```

`order=(p, d, q)` — autoregressive, differencing, moving-average. Keep each ≤ 3 unless theory says otherwise.

## SARIMA — seasonal ARIMA

For data with seasonality (monthly sales, day-of-week effects):
```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

res = SARIMAX(
    y_train,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 12),      # (P, D, Q, s); s=12 monthly, 7 daily-with-weekly
    enforce_stationarity=False,
    enforce_invertibility=False,
).fit(disp=False)
forecast = res.get_forecast(steps=12)
```

Pick `s` by data granularity:
- Daily data with weekly seasonality: `s = 7`.
- Daily data with yearly seasonality: `s = 365` (expensive — prefer Prophet).
- Monthly data: `s = 12`.
- Hourly data with daily cycle: `s = 24`.

## SARIMAX — with exogenous regressors

```python
exog_train = df_train[["marketing_spend", "is_holiday"]]
exog_test  = df_test[["marketing_spend", "is_holiday"]]

res = SARIMAX(y_train, exog=exog_train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)).fit()
forecast = res.get_forecast(steps=len(y_test), exog=exog_test)
```
Regressor values must be available for the forecast horizon. Standardise continuous regressors.

## ETS / exponential smoothing

Strong baseline and often under-rated. Three flavours:

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Simple: level only
res = ExponentialSmoothing(y, trend=None, seasonal=None).fit()

# Holt: level + trend
res = ExponentialSmoothing(y, trend="add", seasonal=None).fit()

# Holt-Winters: level + trend + seasonality
res = ExponentialSmoothing(y, trend="add", seasonal="add", seasonal_periods=12).fit()

forecast = res.forecast(steps=12)
```

Multiplicative seasonality when variance grows with the trend. Use when ARIMA is unstable on short series.

`ETSModel` (state-space) gives proper forecast intervals:
```python
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
res = ETSModel(y, error="add", trend="add", seasonal="add", seasonal_periods=12).fit()
pred = res.get_prediction(start=len(y), end=len(y) + 11)
pred.summary_frame(alpha=0.2)     # mean, pi_lower, pi_upper
```

## State-space models

Statsmodels exposes state-space internals for SARIMAX, Unobserved Components, ETS. Useful when:
- You need to combine multiple components (level, trend, seasonal, cycle) with custom structure.
- You want time-varying parameters.
- You need Kalman-filter smoothing for missing values mid-series.

Start with SARIMAX or ETS; drop into `UnobservedComponents` only if needed.

## Residual diagnostics

Always check after fit:
```python
res.plot_diagnostics(figsize=(12, 8))
```
Four panels: residual time series, histogram + normality, Q-Q plot, correlogram (ACF of residuals).

Goals:
- Residuals centred on zero.
- No pattern over time.
- Histogram roughly normal.
- ACF: no significant spikes (Ljung-Box `res.test_serial_correlation("ljungbox")` p > 0.05).

Failures:
- ACF spikes -> increase `p` or `q` or add seasonal term.
- Trending residuals -> missing trend/regressor.
- Heteroscedasticity (fan-shaped) -> log-transform target or use multiplicative seasonality.

## Forecast intervals

Both `get_forecast` and `get_prediction` return `conf_int()` / `summary_frame()` with prediction intervals. Always display them in the UI — stakeholders need the band, not just the point.

Wider interval over longer horizon is normal. Abnormally narrow intervals suggest under-fitting of uncertainty (common when regressors mask variance).

## Cross-validation for time series

`sklearn.model_selection.TimeSeriesSplit` for rolling-origin CV:
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5, test_size=30)
maes = []
for train_idx, test_idx in tscv.split(y):
    res = SARIMAX(y.iloc[train_idx], order=(1, 1, 1)).fit(disp=False)
    yhat = res.forecast(steps=len(test_idx))
    maes.append((y.iloc[test_idx] - yhat).abs().mean())
```

Report mean MAE + per-fold distribution. Variance across folds is as informative as the mean.

## Picking Prophet vs statsmodels — quick matrix

| Situation | Pick |
| --- | --- |
| Daily, yearly seasonality, holidays matter | Prophet |
| Monthly financial series, need AIC + residual diagnostics | SARIMA |
| Short series (< 2 yrs), stable seasonality | ETS |
| Hourly/minute data | SARIMAX |
| External drivers with interpretable coefficients | SARIMAX |
| Audit/regulatory forecast | statsmodels (ARIMA/SARIMA) |
| Thousands of series, minimal tuning | Prophet or ETS |
| Intermittent demand (many zeros) | Croston's method (statsmodels) or specialist libs |

## Multi-tenant notes

- Per-tenant SARIMA fits are cheap; store order per tenant as part of the artifact.
- Use `auto_arima` once a month during retraining, not per request.
- For cold-start tenants, fall back to a peer-group ETS fit.
