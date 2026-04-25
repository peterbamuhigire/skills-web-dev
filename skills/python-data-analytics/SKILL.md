---
name: python-data-analytics
description: Use when computing complex analytics, KPIs, cohort/funnel/retention metrics,
  financial math (IRR/NPV/amortization), statistical tests, anomaly detection, or
  geospatial analytics in Python — for cases where SQL alone gets unwieldy.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Python Data Analytics
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when computing complex analytics, KPIs, cohort/funnel/retention metrics, financial math (IRR/NPV/amortization), statistical tests, anomaly detection, or geospatial analytics in Python — for cases where SQL alone gets unwieldy.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `python-data-analytics` or would be better handled by a more specific companion skill.
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
| Correctness | Analytics test plan | Markdown doc covering KPI computation, cohort/funnel/retention, and edge-case (empty / sparse) tests | `docs/python/analytics-tests.md` |
| Performance | Pandas/Polars performance note | Markdown doc covering DataFrame size, vectorisation choices, and memory footprint per query | `docs/python/analytics-perf-note.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Use Python when SQL stops being the right tool: multi-step transformations, statistical tests, time-series analysis, anomaly detection, complex financial math, or geospatial computation. Pandas / numpy / Polars as the compute engine; results feed back to PHP via FastAPI sidecar or into Excel/PDF via document-generation.

**Prerequisites:** Load `python-modern-standards` and `python-saas-integration` before this skill.

## When this skill applies

- Computing cohort retention, funnel conversion, churn curves.
- Financial math: IRR, NPV, amortization, depreciation schedules at scale.
- Statistical tests: A/B test significance, distribution comparisons, trend detection.
- Outlier/anomaly detection on SaaS metrics.
- Geospatial analytics: territory stats, route distances, geofence compliance reports.
- Any workload where SQL requires >3 subqueries or a window function chain that's hard to read.

## When Python beats raw SQL (decision rule)

```text
Single-table aggregation, < 3 group-bys       -> SQL
Joins + window functions, still readable       -> SQL
Iterative calculation (running state, rolling) -> Python
Statistical test / hypothesis / distribution  -> Python
Financial schedule (amortization, IRR)         -> Python
Multi-source merge (DB + API + file)           -> Python
Requires chart output                          -> Python
Result is a matrix / pivot > 10 columns        -> Python
```

Rule of thumb: if explaining the SQL to a teammate takes more than 60 seconds, move to Python.

## Core stack

- **pandas 2.x** — default DataFrame library. Arrow-backed dtypes on 3.11+.
- **numpy** — array math, used by pandas under the hood.
- **Polars** — use for datasets > 1M rows or where pandas is too slow. Lazy API is great.
- **SQLAlchemy 2.x** — for DB access. Never mix with raw DB cursors in the same module.
- **Shapely + GeoPandas** — for geospatial work.
- **statsmodels + scipy** — statistical tests and time-series.
- **Decimal** (stdlib) — for all currency math; never `float`.

## Loading data

Use SQLAlchemy engine + `pandas.read_sql` with parameters. Chunk for large results.

```python
from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine(settings.database_url, pool_pre_ping=True)

sql = text("""
    SELECT customer_id, invoice_date, total_amount
    FROM invoices
    WHERE tenant_id = :tenant_id
      AND invoice_date >= :start
      AND invoice_date <  :end
""")
df = pd.read_sql(sql, engine, params={"tenant_id": tenant_id, "start": start, "end": end},
                 parse_dates=["invoice_date"])
```

For > 1M rows, chunked reads with `chunksize=100_000` and a generator pipeline. See `references/loading-data.md`.

## Pandas idioms (the ones that matter)

**Vectorize, don't loop.**

```python
# SLOW
df["total"] = df.apply(lambda r: r["qty"] * r["unit_price"], axis=1)

# FAST
df["total"] = df["qty"] * df["unit_price"]
```

**Avoid `inplace=True`.** Leads to chained assignment bugs in 2.x. Use explicit reassignment.

**Use dtypes on load.** `pd.read_sql(..., dtype={"customer_id": "int64"})`. Cast dates, categoricals, booleans early.

**`copy()` when slicing, always.** `df2 = df[df.status == "paid"].copy()` — prevents `SettingWithCopyWarning`.

**`groupby().agg()` with named columns** is clearer than dict form:

```python
summary = (
    df.groupby("tenant_id", as_index=False)
      .agg(
          revenue=("total_amount", "sum"),
          invoices=("id", "count"),
          avg_invoice=("total_amount", "mean"),
      )
)
```

See `references/pandas-idioms.md` for the full catalog (copy vs view, dtypes, datetime handling, common pitfalls).

## Cohort, funnel, retention

The three most-requested SaaS analytics patterns. Full recipes in `references/cohort-funnel-retention.md`. Summary here:

**Cohort retention:**
1. Assign each customer to their signup cohort (month).
2. For each month after signup, count active customers per cohort.
3. Divide by cohort size → retention %.

```python
customers["cohort"] = customers["signup_date"].dt.to_period("M")
activity = activity.merge(customers[["customer_id", "cohort"]], on="customer_id")
activity["period"] = activity["activity_date"].dt.to_period("M")
activity["offset"] = (activity["period"] - activity["cohort"]).apply(lambda x: x.n)

cohort_size = customers.groupby("cohort").size()
retention = (
    activity.groupby(["cohort", "offset"])["customer_id"].nunique()
            .unstack(fill_value=0)
            .div(cohort_size, axis=0) * 100
)
```

**Funnel conversion:** sequential step counts → percentage drop-offs.

**Retention curves:** for each cohort, plot offset vs %retained — identify where users churn.

## Financial math — always Decimal, never float

Currency math is Decimal. Period.

```python
from decimal import Decimal, ROUND_HALF_UP

def amortization_schedule(principal: Decimal, annual_rate: Decimal, months: int) -> list[dict]:
    monthly_rate = annual_rate / Decimal(12) / Decimal(100)
    # Payment formula using Decimal throughout
    ...
```

Recipes for IRR, NPV, amortization, depreciation (straight-line, declining, units-of-production), and day-count conventions (30/360, actual/365) in `references/financial-math.md`.

## Statistical tests and anomalies

- **A/B test significance:** two-sample t-test, chi-square for proportions, Mann-Whitney U when non-normal.
- **Outliers:** z-score (thresholds: 2.5–3), IQR method (1.5×IQR), Modified Z-score with median.
- **Trend detection:** Mann-Kendall for monotonic trends; decompose seasonality with STL.
- **Anomaly detection:** rolling-window mean ± k·std; isolation forest when rules aren't enough.

See `references/statistics-and-anomalies.md` for choosing the right test per question, and `python-ml-predictive` for model-based anomaly detection.

## Geospatial analytics

Use Shapely for geometry, GeoPandas when you have many features. Coordinate reference systems matter — always tag CRS (EPSG:4326 for WGS84 lat/lng).

```python
import geopandas as gpd
from shapely.geometry import Point

deliveries = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.lng, df.lat), crs="EPSG:4326"
).to_crs("EPSG:3857")   # project to meters for distance

zones = gpd.read_file("zones.geojson").to_crs("EPSG:3857")
joined = gpd.sjoin(deliveries, zones, how="left", predicate="within")
```

Distance calculations in EPSG:3857 (meters), not 4326 (degrees — degrees ≠ distance). See `references/geospatial-analytics.md`.

## Performance — when to leave pandas

- **Rows < 100K:** pandas is fine.
- **Rows 100K–5M:** pandas works; profile and optimize dtypes (`category`, Arrow-backed).
- **Rows > 5M or memory tight:** switch to **Polars**. Its lazy API (`pl.scan_csv`/`scan_parquet`) beats pandas substantially on aggregations.
- **Truly large (> 100M rows):** this doesn't belong in a sidecar. Move to worker + chunked processing, or to a warehouse (ClickHouse / DuckDB / BigQuery) and let Python orchestrate.

Always profile with `cProfile` or `py-spy` before optimizing. See `references/performance-and-polars.md`.

## Output handoff

Analytics results don't live in Python — they return to PHP or become documents.

- **JSON back to PHP:** Pydantic models → FastAPI response. Decimal → string (IEEE754 will bite you).
- **Persist to MySQL:** `df.to_sql(...)` is OK for < 10K rows; beyond that, use `SQLAlchemy Core` with `INSERT ... ON DUPLICATE KEY UPDATE` and chunked inserts.
- **Feed into document-generation:** pass the DataFrame directly to the skill's Excel/Word/PDF generators. See `python-document-generation`.

## Pitfalls specific to SaaS analytics

- **Timezone:** store UTC, report in tenant-local. `df["created_at"].dt.tz_convert(tenant_tz)`.
- **Currency:** if invoices have mixed currencies, convert to a common reporting currency at the tenant's chosen rate (spot vs transaction-date rate — decide and document).
- **Dates vs datetimes:** trimming to midnight UTC can shift dates by a day in the user's TZ. Always round-trip through the tenant TZ before truncating.
- **Division by zero in rates:** guard every rate calc (`retention_rate = active / cohort_size if cohort_size else 0`).
- **Tenant isolation:** every DataFrame loaded must be filtered by tenant at SQL level. Never filter in Python after loading — you'll paginate the wrong data.

## Read next

- `python-document-generation` — render the DataFrame as a branded Excel dashboard or PDF.
- `python-ml-predictive` — when the question is "what happens next" instead of "what happened".
- `python-data-pipelines` — when data needs to be fetched/cleaned before analysis.

## References

- `references/pandas-idioms.md`
- `references/loading-data.md`
- `references/cohort-funnel-retention.md`
- `references/financial-math.md`
- `references/statistics-and-anomalies.md`
- `references/geospatial-analytics.md`
- `references/performance-and-polars.md`