# Cohort, Funnel, Retention

Runnable recipes for the three most-requested SaaS analytics patterns. Each section lists the input shape, the code, and the expected output shape.

## Monthly cohort retention matrix

### Input

Two DataFrames, already filtered by `tenant_id`.

`customers`:

| column        | dtype              |
|---------------|--------------------|
| customer_id   | int64              |
| signup_date   | datetime64[ns, UTC]|

`activity`:

| column        | dtype              |
|---------------|--------------------|
| customer_id   | int64              |
| activity_date | datetime64[ns, UTC]|

Activity means any event that defines "retained" for the business. Common choices: any login, any paid invoice, any completed order. Document the definition next to the report.

### Recipe

```python
import pandas as pd

def monthly_cohort_retention(
    customers: pd.DataFrame,
    activity: pd.DataFrame,
    tenant_tz: str = "UTC",
) -> pd.DataFrame:
    # Normalise to tenant local month so cohorts align with how the business reports.
    customers = customers.assign(
        cohort=customers["signup_date"].dt.tz_convert(tenant_tz).dt.to_period("M")
    )

    activity = activity.assign(
        period=activity["activity_date"].dt.tz_convert(tenant_tz).dt.to_period("M")
    ).merge(customers[["customer_id", "cohort"]], on="customer_id", how="inner")

    activity["offset"] = (activity["period"] - activity["cohort"]).apply(lambda x: x.n)
    activity = activity.loc[activity["offset"] >= 0]  # drop pre-signup noise

    cohort_size = customers.groupby("cohort").size().rename("cohort_size")

    matrix = (
        activity
        .groupby(["cohort", "offset"])["customer_id"].nunique()
        .unstack(fill_value=0)
    )
    retention = matrix.div(cohort_size, axis=0).mul(100).round(2)
    retention.insert(0, "cohort_size", cohort_size)
    return retention
```

### Output

Rows are cohorts (`2025-01`, `2025-02`, ...). Columns are month offsets (`0, 1, 2, ...`). Values are percentages. Month 0 is always 100 % by definition and is useful as a sanity check.

| cohort   | cohort_size | 0   | 1    | 2    | 3    |
|----------|-------------|-----|------|------|------|
| 2025-01  | 120         | 100 | 78.3 | 61.7 | 52.5 |
| 2025-02  | 145         | 100 | 82.1 | 65.5 |      |

Notes:

- Convert to tenant tz before `to_period("M")`. A UK-based customer who signed up at 01:00 UTC on 1 February is a February cohort in Kampala but a January cohort in London.
- `unique` on `customer_id` matters. A customer who logs in 40 times in month 2 is still one retained user.

## Funnel conversion with step drop-off

### Input

A long-format event stream.

`events`:

| column      | dtype               |
|-------------|---------------------|
| user_id     | int64               |
| event       | category            |
| occurred_at | datetime64[ns, UTC] |

### Recipe

```python
from typing import Sequence

def funnel(
    events: pd.DataFrame,
    steps: Sequence[str],
    window: pd.Timedelta = pd.Timedelta(days=7),
) -> pd.DataFrame:
    """Ordered funnel: each step must happen after the previous, within window."""
    pivot = (
        events.loc[events["event"].isin(steps)]
        .sort_values("occurred_at")
        .groupby(["user_id", "event"], observed=True)["occurred_at"]
        .min()
        .unstack()
        .reindex(columns=steps)
    )

    reached = pd.DataFrame(index=pivot.index)
    reached[steps[0]] = pivot[steps[0]].notna()
    prev = pivot[steps[0]]
    for step in steps[1:]:
        ok = pivot[step].notna() & (pivot[step] >= prev) & (pivot[step] - prev <= window)
        reached[step] = reached[steps[steps.index(step) - 1]] & ok
        prev = pivot[step].where(ok)

    counts = reached.sum()
    total = counts.iloc[0] or 1
    return pd.DataFrame({
        "users":       counts,
        "pct_total":   (counts / total * 100).round(2),
        "pct_prev":    (counts / counts.shift(1).fillna(total) * 100).round(2),
        "drop_off":    (1 - counts / counts.shift(1).fillna(total)) * 100,
    })
```

### Output

| step             | users | pct_total | pct_prev | drop_off |
|------------------|-------|-----------|----------|----------|
| signup           | 1000  | 100.00    | 100.00   | 0.00     |
| email_verified   | 820   | 82.00     | 82.00    | 18.00    |
| first_project    | 540   | 54.00     | 65.85    | 34.15    |
| first_invite     | 310   | 31.00     | 57.41    | 42.59    |
| paid_invoice     | 180   | 18.00     | 58.06    | 41.94    |

Decision rules:

- Use `pct_prev` to decide which step to fix. A 42 % drop between invite and paid is a much bigger lever than the 18 % drop at email verification.
- The `window` parameter must be chosen by business, not default. A B2B onboarding funnel may reasonably take 30 days; a consumer app 15 minutes.

## Retention / survival curves

Kaplan-Meier style curve without pulling in lifelines. For SaaS, a simple first-drop model is usually enough.

```python
def survival_curve(
    customers: pd.DataFrame,
    activity: pd.DataFrame,
    as_of: pd.Timestamp,
    tenant_tz: str = "UTC",
) -> pd.DataFrame:
    last_seen = (
        activity.groupby("customer_id")["activity_date"].max()
        .dt.tz_convert(tenant_tz)
        .dt.normalize()
    )
    sign = customers.set_index("customer_id")["signup_date"].dt.tz_convert(tenant_tz).dt.normalize()
    observed = (last_seen - sign).dt.days

    # Anyone active within the last 30 days is treated as still alive (censored)
    censored = (as_of.tz_convert(tenant_tz) - last_seen).dt.days <= 30
    days = pd.Series(range(0, int(observed.max()) + 1), name="day")

    at_risk = pd.Series([(observed >= d).sum() for d in days], index=days)
    events  = pd.Series([((observed == d) & ~censored).sum() for d in days], index=days)

    surv = (1 - events / at_risk.replace(0, pd.NA)).fillna(1).cumprod()
    return surv.reset_index().rename(columns={0: "survival"})
```

## Churn rate

Multiple definitions. Pick one, document it, ship both time series and a clear label.

```python
def monthly_churn(customers: pd.DataFrame, churn_events: pd.DataFrame) -> pd.DataFrame:
    churn_events = churn_events.assign(
        month=churn_events["churned_at"].dt.to_period("M")
    )
    churns = churn_events.groupby("month").size().rename("churned")

    # Customers active at the start of each month
    starts = customers.assign(
        start_month=customers["signup_date"].dt.to_period("M")
    )
    months = pd.period_range(starts["start_month"].min(), churns.index.max())
    actives = pd.Series(
        [((starts["start_month"] <= m) & ((starts.get("churn_month", pd.NaT) > m) | starts["churn_month"].isna())).sum()
         for m in months],
        index=months,
        name="active_start",
    )
    return pd.concat([actives, churns], axis=1).fillna(0).assign(
        churn_rate=lambda d: (d["churned"] / d["active_start"].replace(0, pd.NA) * 100).round(2)
    )
```

## Net Revenue Retention (NRR)

NRR measures expansion net of churn and downgrades, relative to a cohort's starting MRR.

```
NRR_t = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR
```

```python
def nrr_by_cohort(
    subscriptions: pd.DataFrame,  # tenant_id, customer_id, month, mrr
    cohort_month: pd.Period,
) -> pd.DataFrame:
    cohort_customers = (
        subscriptions.loc[subscriptions["month"] == cohort_month, "customer_id"].unique()
    )
    sub = subscriptions.loc[subscriptions["customer_id"].isin(cohort_customers)]
    starting = sub.loc[sub["month"] == cohort_month, "mrr"].sum()
    monthly  = sub.groupby("month", as_index=False)["mrr"].sum()
    monthly["nrr_pct"] = (monthly["mrr"] / starting * 100).round(2) if starting else 0
    monthly["offset"]  = (monthly["month"] - cohort_month).apply(lambda x: x.n)
    return monthly
```

Interpretation:

- NRR > 100 % means the cohort expanded net of churn. World-class SaaS targets NRR above 110 %.
- Pair NRR with Gross Revenue Retention (GRR) which excludes expansion. GRR isolates churn and contraction.

## Common mistakes

- Mixing cohort definitions (signup vs first-paid) in the same report. State which one.
- Counting events rather than unique customers per period.
- Forgetting month 0 is always 100 %; including it as a "retention rate" in a headline is misleading.
- Computing rates without guarding `cohort_size == 0`.
- Resolving periods in UTC when tenants are in a time zone that flips the calendar boundary. Always tz-convert before `to_period`.
