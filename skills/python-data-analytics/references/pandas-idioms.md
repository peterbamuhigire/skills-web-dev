# Pandas Idioms

Reference companion to `SKILL.md`. The items here are the pandas patterns that actually bite in production SaaS analytics work. Assume pandas 2.x, Python 3.11+, and Arrow as an option.

## Vectorisation is not optional

The first rule is to replace row-wise Python with column-wise numpy.

```python
# Slow: one Python function call per row
df["tax"] = df.apply(lambda r: r["net"] * tax_rate(r["country"]), axis=1)

# Fast: map once, multiply once
tax_by_country = df["country"].map(TAX_RATES).astype("float64")
df["tax"] = df["net"] * tax_by_country
```

Rules of thumb:

- `apply(..., axis=1)` is a last resort. Reach for `map`, `merge`, `where`, `np.select`, or `groupby().transform()` first.
- `iterrows` and `itertuples` have no place in transformation code. Use them only to emit rows to an external system one at a time.
- Use `np.select` for multi-branch logic. It is both faster and easier to review than nested `np.where`.

```python
import numpy as np

conditions = [
    df["status"] == "paid",
    df["status"] == "partial",
    df["due_date"] < pd.Timestamp.utcnow(),
]
choices = ["paid", "partial", "overdue"]
df["bucket"] = np.select(conditions, choices, default="current")
```

## Copy vs view vs SettingWithCopy

In pandas 2.x, Copy-on-Write (CoW) is being rolled out, but the safe default is still to be explicit. Three rules remove the entire class of bug:

1. When slicing a DataFrame and planning to write to it, call `.copy()`.
2. Never chain a filter with an assignment (`df[df.a > 0]["b"] = 1`). Use `.loc` with a boolean mask.
3. Avoid `inplace=True`. The API is inconsistent and the pattern masks mutation.

```python
# Correct mutation pattern
paid = df.loc[df["status"] == "paid"].copy()
paid["net_after_fee"] = paid["net"] - paid["fee"]

# In-place update on a subset of the original frame
df.loc[df["status"] == "paid", "net_after_fee"] = df["net"] - df["fee"]
```

Enable CoW behaviour globally when starting a new codebase:

```python
pd.options.mode.copy_on_write = True
```

## Dtypes, including Arrow-backed

Casting dtypes early saves memory, catches dirty data, and speeds up groupby.

```python
df = df.astype({
    "tenant_id":   "int64",
    "customer_id": "int64",
    "status":      "category",   # 5-20 distinct values
    "currency":    "category",
    "net":         "float64",    # or pd.ArrowDtype(pa.decimal128(19, 4)) for money
})
```

For money, use `Decimal` end-to-end for computation and only cross into pandas when you are ready for display, aggregation by sum, or export. Pandas `float64` is fine for rates and ratios, never for cash.

Arrow-backed dtypes (pandas 2.0+) are worth using when:

- Reading Parquet or the result of a `read_sql` that already returns strings.
- You need nullable integers and booleans that behave like SQL.
- Memory is tight and strings dominate.

```python
import pyarrow as pa
df = pd.read_parquet("invoices.parquet", dtype_backend="pyarrow")

# Or convert after load
df = df.convert_dtypes(dtype_backend="pyarrow")
```

Arrow-backed dtypes are slower for tight numeric loops than numpy-backed. Benchmark before committing a hot path to Arrow.

## .loc vs .iloc vs boolean mask

- `.loc[row_label, col_label]` is the default for label-based access.
- `.iloc[row_pos, col_pos]` is for positional access and is rarely the right choice after load.
- Boolean mask inside `.loc` is how you filter-and-update in one pass.

```python
df.loc[df["currency"] == "UGX", "net_usd"] = df["net"] * ugx_rate
```

Do not mix `.ix` or chained `[]` accessors. They are removed or deprecated and fail silently.

## Datetime handling

All timestamps land in UTC. Convert to tenant time zone for presentation only.

```python
df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
df["created_local"] = df["created_at"].dt.tz_convert(tenant_tz)
```

Truncation traps:

- `df["created_at"].dt.date` discards tz and returns Python `date`. Acceptable for export, dangerous for joins.
- `dt.normalize()` zeroes the time but keeps tz, which is usually what you want.
- `dt.to_period("M")` converts to a tz-naive monthly period. Use it for cohort labels, not for arithmetic that needs tz awareness.

Resampling must happen on a `DatetimeIndex`:

```python
daily = (
    df.set_index("created_at")
      .tz_convert(tenant_tz)
      .resample("D")["net"]
      .sum()
)
```

Rolling windows need a sorted index. Always `sort_index()` before `rolling`.

## Category dtype for memory

`category` cuts memory by 10-50x when cardinality is low. It also speeds up `groupby` on that column.

```python
df["status"]   = df["status"].astype("category")
df["country"]  = df["country"].astype("category")
```

Trap: joining on a category column with a non-matching ordering raises or silently upgrades to object. Align categories with `df["x"] = df["x"].cat.set_categories(other["x"].cat.categories)` before merging.

## Method chaining and .pipe()

Long chains are easier to read than intermediate variables when each step is a transformation.

```python
monthly = (
    df
    .loc[df["tenant_id"] == tenant_id]
    .assign(month=lambda d: d["created_at"].dt.to_period("M"))
    .groupby(["month", "product"], as_index=False)
    .agg(revenue=("net", "sum"), orders=("id", "count"))
    .sort_values(["month", "revenue"], ascending=[True, False])
)
```

Wrap custom steps in `.pipe()` rather than breaking the chain:

```python
def attach_fx(df: pd.DataFrame, rates: pd.DataFrame) -> pd.DataFrame:
    return df.merge(rates, on=["currency", "as_of_date"], how="left")

result = (
    df.pipe(attach_fx, rates=fx_rates)
      .assign(net_usd=lambda d: d["net"] * d["rate"])
)
```

Guidelines:

- Keep each step under ~3 lines. Break out a helper via `.pipe()` beyond that.
- Never chain more than ~8 operations. After that, extract the pipeline into a named function.

## groupby essentials

Named aggregation is the only form worth using:

```python
summary = (
    df.groupby(["tenant_id", "product"], as_index=False, observed=True)
      .agg(
          revenue=("net", "sum"),
          orders=("id", "count"),
          customers=("customer_id", "nunique"),
          avg_order=("net", "mean"),
      )
)
```

Always pass `observed=True` when grouping on `category` columns. Without it, pandas produces the Cartesian product of every category, including unused ones, and fills with NaN.

`groupby().transform()` returns a frame of the same length as the original, ideal for per-group rates:

```python
df["share"] = df["net"] / df.groupby("customer_id")["net"].transform("sum")
```

## Merge safety

Always specify `how` and `validate`:

```python
merged = df.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

`validate` values: `"one_to_one"`, `"one_to_many"`, `"many_to_one"`, `"many_to_many"`. Lying here is a frequent source of row-count bugs.

Use `indicator=True` during development to see which rows came from where.

## Common pitfalls

- Comparing tz-aware and tz-naive timestamps raises in 2.x. Pick one policy and stick to it.
- Float equality on money. Always compare rounded Decimals or use `np.isclose` on floats.
- Silent int-to-float promotion on NaN. Use nullable `Int64` or Arrow integers if NaN is expected.
- `read_csv` default `dtype=object` for string columns. Pass `dtype_backend="pyarrow"` or explicit dtypes.
- Group keys disappearing. `as_index=False` or `.reset_index()` keeps keys as columns.
- Mutating a DataFrame passed into a function. Treat inputs as immutable; copy at the boundary.

## Tenant hygiene inside pandas

Every DataFrame loaded from MySQL has already been filtered by `tenant_id` at the SQL layer. Two guardrails inside Python:

1. Assert it on load: `assert (df["tenant_id"] == tenant_id).all()`.
2. Drop `tenant_id` after the assertion to avoid accidentally grouping by it and producing confusing one-row-per-tenant outputs.

```python
df = pd.read_sql(sql, engine, params={"tenant_id": tenant_id})
assert (df["tenant_id"] == tenant_id).all(), "tenant leakage"
df = df.drop(columns=["tenant_id"])
```
