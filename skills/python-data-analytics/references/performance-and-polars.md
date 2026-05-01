# Performance and Polars

Profile first, optimise second, rewrite into Polars third. Every section here gives a measurable decision rule.

## Measuring before optimising

Guessing which step is slow is almost always wrong. Measure.

### Wall-clock timing

```python
import time
from contextlib import contextmanager

@contextmanager
def timed(label: str):
    t0 = time.perf_counter()
    yield
    print(f"{label}: {time.perf_counter() - t0:.3f}s")

with timed("load"):
    df = pd.read_sql(sql, engine, params=params)
with timed("groupby"):
    result = df.groupby("product").agg(total=("net", "sum"))
```

Rule: any step over 1 second in a request path deserves a profile; over 5 seconds is mandatory to investigate.

### cProfile for function-level attribution

```python
import cProfile, pstats

profiler = cProfile.Profile()
profiler.enable()
run_report(tenant_id=42)
profiler.disable()
pstats.Stats(profiler).sort_stats("cumulative").print_stats(25)
```

- `cumulative` reveals which high-level function is slow.
- `tottime` reveals which low-level function does the heavy lifting.
- Ignore anything under ~1 % of wall time; it is noise.

### py-spy for live or already-running processes

```bash
py-spy record -o profile.svg --pid 1234 --duration 30
py-spy top --pid 1234
```

Use `py-spy` when:

- The process is a long-running worker and you do not want to add instrumentation.
- `cProfile` overhead skews the result.
- You want a flamegraph the team can read.

`py-spy` uses sampling and does not need to modify the code.

## Memory footprint

### Measuring

```python
df.memory_usage(deep=True).sum() / 1024**2   # MB, includes string overhead
```

`deep=True` is essential for object columns; without it, you are measuring 8 bytes per pointer, not the actual strings.

### Dtype tricks that actually help

Ordered by typical impact:

1. **Categorical for low-cardinality strings.** Cuts a 100 MB column to 2-10 MB when there are under a few thousand distinct values.
2. **Downcast numerics.** `pd.to_numeric(col, downcast="integer")` shrinks `int64` to `int32` or `int16` where safe.
3. **Arrow-backed strings.** `dtype_backend="pyarrow"` on load gives 30-60 % savings on string-heavy frames.
4. **Drop unused columns before the expensive step.** The cheapest byte is the one you never loaded.

```python
df = df.astype({
    "status":   "category",
    "country":  "category",
    "currency": "category",
})
for col in ("customer_id", "invoice_id"):
    df[col] = pd.to_numeric(df[col], downcast="integer")
```

### When memory is still tight

- Process in chunks (see below) instead of loading the whole table.
- Use `parquet` as the intermediate format. Column-oriented, typed, compressed.
- Move to Polars. Its Arrow memory model is substantially smaller than numpy-backed pandas for mixed-type frames.

## Chunked processing for huge data

When the source is too large to hold in memory, stream:

```python
def run(tenant_id: int) -> pd.DataFrame:
    reducer = None
    for chunk in pd.read_sql(sql, engine, params=..., chunksize=200_000):
        grouped = chunk.groupby("product", as_index=False)["net"].sum()
        reducer = grouped if reducer is None else (
            pd.concat([reducer, grouped])
              .groupby("product", as_index=False)["net"].sum()
        )
    return reducer
```

Guidelines:

- Chunk size 100k-250k rows is a good default. Below that, per-chunk overhead dominates; above that, memory spikes.
- Aggregations and simple transforms fit the chunked pattern. Joins and sorts do not; move those to Polars or SQL.
- Always sort the source by a stable key so re-runs process the same rows per chunk.

## Polars decision rules

Polars is worth the switch when any of these hold:

- **Row count > 5M** in a single frame.
- **Group-by or join** with > 10 key columns or > 100k groups.
- **Memory pressure** where pandas uses more than 50 % of the host RAM.
- **You want lazy evaluation** to push predicates into the scan and skip work.
- **Multi-core** is available. Polars uses all cores; pandas is single-threaded by default.

Polars is not worth the switch when:

- The frame is under ~500k rows. Pandas is fine and the ecosystem around it is larger.
- Downstream tooling (Matplotlib, scikit-learn, statsmodels) expects pandas. Conversion at every boundary defeats the point.
- The team has no Polars experience. The API is similar but different enough that a day of onboarding is needed.

## Migrating common pandas patterns

### Read and filter

```python
# pandas
df = pd.read_parquet("invoices.parquet")
df = df.loc[df["status"] == "paid"]

# polars eager
import polars as pl
df = pl.read_parquet("invoices.parquet").filter(pl.col("status") == "paid")

# polars lazy (preferred for large files)
df = (
    pl.scan_parquet("invoices.parquet")
      .filter(pl.col("status") == "paid")
      .collect()
)
```

`scan_parquet` reads only the columns and row groups needed after the filter is applied. That is where Polars wins hardest.

### Group-by with named aggregations

```python
# pandas
summary = (
    df.groupby(["month", "product"], as_index=False)
      .agg(revenue=("net", "sum"), orders=("id", "count"))
)

# polars
summary = (
    df.group_by(["month", "product"])
      .agg([
          pl.col("net").sum().alias("revenue"),
          pl.col("id").count().alias("orders"),
      ])
      .sort(["month", "product"])
)
```

### Window / rolling

```python
# pandas
df["revenue_28d"] = df["revenue"].rolling(28, min_periods=1).sum()

# polars
df = df.with_columns(
    pl.col("revenue").rolling_sum(window_size=28, min_periods=1).alias("revenue_28d")
)
```

### Joins

```python
# pandas
merged = df.merge(customers, on="customer_id", how="left", validate="many_to_one")

# polars
merged = df.join(customers, on="customer_id", how="left", validate="m:1")
```

Polars `validate` uses `m:1`, `1:m`, `1:1`. Use it; join row-count bugs are the same in both libraries.

### Converting back to pandas

```python
df_pd = df.to_pandas()               # copy
df_pd = df.to_pandas(use_pyarrow_extension_array=True)   # cheaper if downstream handles Arrow
```

Do the conversion at the boundary, not in the middle of a pipeline.

## Lazy API in practice

Lazy Polars plans the whole pipeline before executing, enabling predicate pushdown, projection pushdown, and parallel execution.

```python
lazy = (
    pl.scan_parquet("invoices/*.parquet")
      .filter(pl.col("tenant_id") == tenant_id)
      .filter(pl.col("invoice_date").is_between(start, end))
      .group_by(["month", "product"])
      .agg([
          pl.col("net").sum().alias("revenue"),
          pl.col("id").n_unique().alias("orders"),
      ])
)

# Inspect the plan before running
print(lazy.explain(optimized=True))

summary = lazy.collect(streaming=True)
```

`streaming=True` processes the data in batches that do not need to fit in memory, trading some speed for the ability to handle very large files on modest hardware.

## Parallelism inside a single process

Pandas itself is single-threaded for most operations. Options:

- **Polars**: default multi-threaded.
- **numba**: JIT the hot numeric kernel. Useful when pandas has pushed you to `apply` and you cannot vectorise.
- **multiprocessing**: split by a natural partition key (tenant, date) and run workers. Aggregate with `pd.concat`.

```python
from concurrent.futures import ProcessPoolExecutor

def run_tenant(tenant_id: int) -> pd.DataFrame:
    return report_for_tenant(tenant_id)

with ProcessPoolExecutor(max_workers=4) as pool:
    frames = list(pool.map(run_tenant, tenant_ids))
combined = pd.concat(frames, ignore_index=True)
```

Process-level parallelism is the right fit for tenant-scoped analytics because tenant isolation is already a natural partition.

## When to leave Python altogether

Some analytics are better done in SQL or in a warehouse:

- **DuckDB.** For over 100M rows with columnar queries on a laptop or single server, DuckDB beats any Python option and queries Parquet directly. Mount over files; skip the round trip to the DB.
- **ClickHouse.** For billions of rows and multi-user concurrency, ClickHouse is the right layer.
- **BigQuery / Snowflake.** When the data already lives in a warehouse, push the aggregation there and return a small result to Python.

Rule of thumb:

- Up to 5M rows: pandas.
- 5M to 100M rows: Polars or DuckDB.
- 100M rows and up: warehouse, with Python orchestrating.

## Performance checklist

Before calling a pipeline optimised:

1. `cProfile` or `py-spy` has attributed 80 %+ of wall time to a handful of functions.
2. Dtypes are deliberate (no stray `object` columns, categoricals where they help).
3. Loads are filtered at SQL, not in Python.
4. Joins declare `validate`; row-count sanity checks exist.
5. Rolling / window operations happen on a sorted index or a Polars lazy frame.
6. Memory high-water mark is under 50 % of host RAM during the worst tenant.
7. The report runs within its SLO on the slowest real tenant, not a toy dataset.

Anything short of that and the work is not finished.
