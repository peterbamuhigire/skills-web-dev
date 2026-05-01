# Statistics and Anomalies

This is a decision guide for the tests and detectors worth running on SaaS data, with runnable snippets. Assume `scipy.stats` and `statsmodels` are available. Always filter by `tenant_id` at the SQL layer before the statistics start.

## Descriptive stats first

Before any test, summarise:

```python
summary = (
    df.groupby("variant")["metric"]
      .agg(["count", "mean", "median", "std", "min", "max"])
      .assign(sem=lambda d: d["std"] / d["count"].pow(0.5))
)
```

Rules:

- Report median alongside mean for revenue, session length, or any long-tailed metric. Means lie about SaaS data.
- Use `sem` (standard error of the mean) rather than `std` for confidence intervals.
- Sample size guardrail: do not report a mean with `n < 30`. Use a bootstrap instead.

## Choosing a hypothesis test

| Question                               | Data shape                         | Test                             |
|----------------------------------------|------------------------------------|----------------------------------|
| Do two variants have different means?  | Continuous, roughly normal         | Two-sample Welch's t-test        |
| Do two variants have different medians?| Continuous, skewed                 | Mann-Whitney U                   |
| Do two variants have different rates?  | Binary (converted yes/no)          | Chi-square or two-proportion z   |
| Do two distributions differ overall?   | Continuous, any shape              | Kolmogorov-Smirnov               |
| Does a variable fit a known distribution?| Continuous                       | Anderson-Darling or KS one-sample|
| Is there a monotonic trend over time?  | Time series, any shape             | Mann-Kendall                     |

### Welch's t-test

```python
from scipy import stats

control = df.loc[df["variant"] == "A", "revenue"].to_numpy()
treat   = df.loc[df["variant"] == "B", "revenue"].to_numpy()

t, p = stats.ttest_ind(treat, control, equal_var=False)
diff = treat.mean() - control.mean()
```

- Use Welch's (`equal_var=False`). Student's t-test assumes equal variance which rarely holds.
- `p < 0.05` is a convention, not a law. For revenue decisions demand `p < 0.01` and an effect size you can defend.
- Report effect size (Cohen's d) alongside `p`. Statistical significance without practical significance wastes engineering time.

### Mann-Whitney U

```python
u, p = stats.mannwhitneyu(treat, control, alternative="two-sided")
```

Use when the metric is skewed: revenue per user, session length, time to first action. Compares rank distributions. Robust to outliers.

### Chi-square for proportions

```python
from scipy.stats import chi2_contingency

table = pd.crosstab(df["variant"], df["converted"])
chi2, p, dof, expected = chi2_contingency(table)
```

Guardrail: if any expected cell is `< 5`, use Fisher's exact test instead (`scipy.stats.fisher_exact`).

Two-proportion z-test is a simpler form for a single binary outcome:

```python
from statsmodels.stats.proportion import proportions_ztest

counts = np.array([df.loc[df["variant"] == v, "converted"].sum() for v in ("A", "B")])
nobs   = np.array([(df["variant"] == v).sum()                        for v in ("A", "B")])
z, p = proportions_ztest(counts, nobs)
```

### Kolmogorov-Smirnov

Use when you want to know if two distributions differ anywhere, not just in mean.

```python
stat, p = stats.ks_2samp(treat, control)
```

Good for detecting drift in the shape of a distribution over time. Bad for small samples (say `< 50` per group).

## Multiple comparisons

Running ten tests at `p < 0.05` means roughly one false positive by chance. When comparing many variants or many metrics:

```python
from statsmodels.stats.multitest import multipletests

_, p_adj, *_ = multipletests(p_values, method="holm")
```

Default to Holm-Bonferroni. Use Benjamini-Hochberg (`method="fdr_bh"`) when false discovery rate is the right framing, typically in exploratory work.

## Power and sample size

Plan the experiment before running it.

```python
from statsmodels.stats.power import NormalIndPower, tt_ind_solve_power

n_per_group = tt_ind_solve_power(
    effect_size=0.2,   # Cohen's d for the minimum effect you care about
    alpha=0.05,
    power=0.8,
    ratio=1.0,
    alternative="two-sided",
)
```

Rules:

- `power=0.8` is the minimum. Prefer 0.9 for revenue-critical decisions.
- `effect_size` should reflect the smallest effect that is worth shipping, not the effect you hope to find.
- An experiment under-powered to detect the effect is waste; stop and re-scope.

## Outlier detection

### Z-score

```python
from scipy.stats import zscore

z = zscore(df["value"], nan_policy="omit")
outliers = df.loc[abs(z) > 3]
```

- Z-score assumes roughly normal. Do not use it on revenue data without a log transform.
- Thresholds: 2.5 is liberal, 3 is standard, 3.5 is conservative.

### Modified Z-score (median-based)

Preferred when the data has outliers that would otherwise inflate the mean and std used to detect outliers.

```python
import numpy as np

def modified_zscore(x: np.ndarray) -> np.ndarray:
    median = np.median(x)
    mad = np.median(np.abs(x - median))
    if mad == 0:
        return np.zeros_like(x)
    return 0.6745 * (x - median) / mad

mz = modified_zscore(df["value"].to_numpy())
outliers = df.loc[abs(mz) > 3.5]
```

### IQR method

Simple, robust, and well understood.

```python
q1, q3 = df["value"].quantile([0.25, 0.75])
iqr = q3 - q1
lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
outliers = df.loc[(df["value"] < lo) | (df["value"] > hi)]
```

Use 1.5×IQR as standard. 3×IQR is a "far outlier" threshold sometimes called the Tukey fence.

### STL-residual anomalies for time series

For seasonal metrics (daily logins, weekly orders), remove trend and seasonality first, then apply z-score to the residual.

```python
from statsmodels.tsa.seasonal import STL

decomp = STL(df["daily_orders"], period=7, robust=True).fit()
resid = decomp.resid
mz = modified_zscore(resid.to_numpy())
anomalies = df.loc[abs(mz) > 4]
```

Rules:

- Match `period` to the dominant seasonality (7 for weekly, 12 for yearly on monthly data, 365 for daily-annual).
- `robust=True` is essential when the history contains incidents you don't want to bias the decomposition.
- Threshold 4 for high-precision alerts; 3 for broader discovery.

## Trend detection: Mann-Kendall

Mann-Kendall tests whether a series has a monotonic trend without assuming linearity or normality.

```python
def mann_kendall(x: np.ndarray) -> tuple[float, float]:
    """Returns (tau, p_value). Positive tau = increasing trend."""
    from scipy.stats import kendalltau
    idx = np.arange(len(x))
    tau, p = kendalltau(idx, x)
    return tau, p
```

- `tau > 0` and `p < 0.05` indicates an increasing trend.
- Mann-Kendall is insensitive to outliers and ignores magnitude.
- Sen's slope estimator pairs well with Mann-Kendall to quantify the trend. `scipy.stats.theilslopes(x, idx)` returns median slope.

## Changepoint detection (brief)

When a metric has a regime change rather than a trend, use `ruptures`:

```python
import ruptures as rpt

algo = rpt.Pelt(model="rbf").fit(df["daily_orders"].to_numpy())
breakpoints = algo.predict(pen=10)
```

- Use `model="rbf"` for distributional changes.
- `pen` controls sensitivity: higher means fewer breakpoints. Tune on historical data where you know the truth.

## Common mistakes

- Running a test, getting `p > 0.05`, declaring "no effect". Absence of evidence is not evidence of absence; report the confidence interval.
- Reporting mean revenue without median. A single whale moves the mean but not the median.
- Treating all tenants as one population. Segment first; pooled tests hide tenant-specific effects.
- Running A/B on a metric that has a strong weekly cycle without blocking by weekday.
- Using z-score on heavy-tailed data. Use modified z-score or IQR.

## Reporting pattern

For every stats result rendered to PHP or Excel:

```python
{
    "metric":            "revenue_per_user",
    "sample_size_a":     n_a,
    "sample_size_b":     n_b,
    "mean_a":            round(mean_a, 2),
    "mean_b":            round(mean_b, 2),
    "median_a":          round(median_a, 2),
    "median_b":          round(median_b, 2),
    "effect_size":       round(cohens_d, 3),
    "test":              "welch_t",
    "p_value":           round(p, 4),
    "ci_95_lower":       round(ci_lo, 2),
    "ci_95_upper":       round(ci_hi, 2),
    "conclusion":        "Variant B increases revenue by 4.2 % (p=0.012).",
}
```

The `conclusion` field is for humans; the numbers are for auditors and dashboards.
