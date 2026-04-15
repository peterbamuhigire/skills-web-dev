# Loading Data

How to move rows between MySQL / PostgreSQL and pandas safely, fast, and with tenant isolation intact.

## Engine setup

One engine per process, pool configured for the workload. FastAPI sidecars typically run a handful of concurrent requests; analytics workers may run a single long query at a time.

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,       # catches stale MySQL connections
    pool_recycle=1800,        # under MySQL wait_timeout (default 8h)
    future=True,              # SQLAlchemy 2.x style
    connect_args={"charset": "utf8mb4"},
)
```

Guidelines:

- `pool_pre_ping=True` on every long-lived process. It adds a 1 ms SELECT 1 but eliminates `MySQL server has gone away` in workers.
- `pool_recycle` must be under the server `wait_timeout`. On managed MySQL that is often 1800s.
- Share a single engine across the module. Never construct one per request.

## Parameterised read_sql

Always parameterise. Never string-interpolate into SQL. Parameter syntax is driver-specific; in SQLAlchemy 2.x use `text()` with named binds.

```python
from sqlalchemy import text
import pandas as pd

sql = text("""
    SELECT id, customer_id, invoice_date, total_amount, currency, status
    FROM invoices
    WHERE tenant_id   = :tenant_id
      AND invoice_date >= :start
      AND invoice_date <  :end
""")

df = pd.read_sql(
    sql,
    engine,
    params={"tenant_id": tenant_id, "start": start, "end": end},
    parse_dates=["invoice_date"],
    dtype={"customer_id": "int64"},
)
```

Rules:

- `tenant_id` is always a bound parameter. No exceptions.
- Ranges use half-open intervals (`>= start AND < end`) to avoid boundary bugs around daylight saving and fractional seconds.
- `parse_dates` pushes conversion into pandas' C parser. Faster and cleaner than converting after.

## Chunked reads with a generator

For result sets over ~500k rows, stream in chunks and aggregate as you go. Do not load then aggregate.

```python
def stream_invoices(tenant_id: int, start, end, chunksize: int = 100_000):
    sql = text("""
        SELECT customer_id, invoice_date, total_amount
        FROM invoices
        WHERE tenant_id = :tenant_id
          AND invoice_date >= :start
          AND invoice_date <  :end
        ORDER BY id
    """)
    yield from pd.read_sql(
        sql, engine,
        params={"tenant_id": tenant_id, "start": start, "end": end},
        chunksize=chunksize,
        parse_dates=["invoice_date"],
    )


def monthly_revenue(tenant_id: int, start, end) -> pd.DataFrame:
    parts = []
    for chunk in stream_invoices(tenant_id, start, end):
        parts.append(
            chunk
            .assign(month=lambda d: d["invoice_date"].dt.to_period("M"))
            .groupby("month", as_index=False)["total_amount"].sum()
        )
    combined = pd.concat(parts, ignore_index=True)
    return combined.groupby("month", as_index=False)["total_amount"].sum()
```

Key points:

- `ORDER BY id` for deterministic iteration. Without it, MySQL returns server-side-cursor order, which is undefined.
- For MySQL, install `mysqlclient` or `PyMySQL` with `stream_results=True` in the execution options for true server-side streaming.
- Aggregate then concat then aggregate again. The final aggregation resolves overlaps between chunks.

## MySQL dtype tips

Decimal handling is the top gotcha.

- MySQL `DECIMAL(19,4)` arrives as Python `Decimal`. Pandas stores it as `object`. Do not convert to `float` if the column will sum to an invoice total; instead keep as `Decimal` for arithmetic, then convert to `float` only for display or charting.
- `DATETIME` columns arrive tz-naive. MySQL itself stores them as naive UTC by convention in this codebase. Wrap with `pd.to_datetime(..., utc=True)` if you need tz-aware semantics.
- `JSON` columns arrive as `str`. Parse with `df["meta"].apply(json.loads)` and then `pd.json_normalize` if you need columnar access.
- `BIT(1)` arrives as `bytes`. Cast with `df["flag"] = df["flag"].map({b"\x00": False, b"\x01": True}).astype("boolean")`.

Decimal pattern:

```python
from decimal import Decimal

df = pd.read_sql(sql, engine, params=params)
# Sum Decimals precisely; convert only for charts
totals_decimal = df.groupby("product")["total_amount"].apply(
    lambda s: sum(s, Decimal("0"))
)
totals_float = totals_decimal.astype("float64")
```

## PostgreSQL-specific tips

- `JSONB` arrives as parsed `dict`. No `json.loads` needed. Use `pd.json_normalize(df["meta"])` directly.
- `NUMERIC` arrives as `Decimal` as with MySQL.
- Arrays arrive as Python `list`. Explode with `df.explode("tags")` before grouping.
- `TIMESTAMP WITH TIME ZONE` arrives tz-aware. Prefer this over `TIMESTAMP WITHOUT TIME ZONE` to avoid the MySQL-style convention trap.
- Use `psycopg[binary]>=3` over `psycopg2`; it is faster for DataFrames and handles JSONB natively.

## Upserting back to the database

`df.to_sql` is only acceptable for throw-away scratch tables under ~10k rows. Production writes use SQLAlchemy Core with a dialect-specific upsert.

### MySQL: INSERT ... ON DUPLICATE KEY UPDATE

```python
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.mysql import insert

metadata = MetaData()
metric = Table("metric_daily", metadata, autoload_with=engine)

def upsert_metrics(df: pd.DataFrame, batch_size: int = 1_000) -> None:
    rows = df.to_dict("records")
    with engine.begin() as conn:
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            stmt = insert(metric).values(batch)
            stmt = stmt.on_duplicate_key_update(
                value=stmt.inserted.value,
                updated_at=stmt.inserted.updated_at,
            )
            conn.execute(stmt)
```

### PostgreSQL: INSERT ... ON CONFLICT

```python
from sqlalchemy.dialects.postgresql import insert as pg_insert

stmt = pg_insert(metric).values(batch)
stmt = stmt.on_conflict_do_update(
    index_elements=["tenant_id", "metric_date", "metric_key"],
    set_={"value": stmt.excluded.value, "updated_at": stmt.excluded.updated_at},
)
```

Guidelines:

- Wrap each batch in `engine.begin()`. If the batch fails, the transaction rolls back and you retry.
- Keep batch size around 1 000 rows. Larger batches hit MySQL `max_allowed_packet` and PostgreSQL statement parse limits.
- Pre-validate Decimals; the database will reject `float('nan')` values in a `NUMERIC` column, but will accept `None`.

## Connection lifecycle and session scoping

- Short-lived FastAPI request: acquire a connection inside the request handler, release it on return. Use `with engine.connect() as conn:` or the SQLAlchemy `Session` context manager.
- Long-lived worker loop: open one connection per unit of work, not per run. Close on error so the pool prunes the bad socket.
- Never share a connection across threads. Share the engine and let each thread check out its own.

## ORM vs Core for reads into pandas

- Core with `text()` is the default for analytics reads. The schema you need for a report rarely matches the ORM model exactly, and the ORM loses its value when the destination is a DataFrame.
- Use the ORM for CRUD against modelled tables, not for bulk analytics reads.

## Tenant isolation checklist

Before any `read_sql` lands in production code:

1. `tenant_id = :tenant_id` appears in the `WHERE` clause of the query and all subqueries.
2. `tenant_id` is a bound parameter, not a formatted string.
3. Every join to a tenant-scoped table also joins on `tenant_id`.
4. The resulting DataFrame asserts single-tenant content: `assert df["tenant_id"].nunique() <= 1`.
5. `tenant_id` is dropped from the frame before any group-by, to prevent accidentally producing cross-tenant breakdowns if the filter is ever weakened.

Missing any of these is a production-blocking issue.
