# Performance

Document generation burns CPU, memory, and wall-clock. Optimisation targets: time-to-first-byte for sync downloads, per-job RAM ceiling for workers, and throughput (jobs/minute) for scheduled batches.

## Budgets

```text
Sync download (FastAPI response):
  target p95 latency      < 1.5 s
  artefact size           < 2 MB
  peak RAM per request    < 150 MB

Worker job (async):
  target p95 wall time    < 30 s for standard reports
  peak RAM per worker     < 1 GB (hard cap via RLIMIT_AS)
  throughput              >= 20 jobs/min per worker

Scheduled batch (e.g., nightly):
  worker count            2-4 CPU cores
  wall time               fits in the off-peak window
```

If a report is projected to exceed these, push it to the worker and notify on completion. Never ship a 5-second sync endpoint.

## xlsxwriter constant_memory mode

```python
wb = xlsxwriter.Workbook(path, {
    "constant_memory": True,
    "default_date_format": "yyyy-mm-dd",
    "tmpdir": "/var/tmp/xlsxwriter",   # fast local disk, not shared NFS
})
```

Effect: once a row is written, the previous row is flushed and freed. Memory stays flat regardless of row count.

Constraints:

- rows must be written in order; no back-patching.
- `merge_range` works only before subsequent row writes on the merged cells.
- `add_table` must declare the full range before writing rows.

Rule: turn on `constant_memory` for any workbook projected to exceed 50,000 rows or 200 MB.

## openpyxl write_only mode

```python
from openpyxl import Workbook

wb = Workbook(write_only=True)
ws = wb.create_sheet("Data")
ws.append(["id", "date", "amount"])   # header
for row in stream():
    ws.append([row["id"], row["date"], row["amount"]])
wb.save(path)
```

`write_only=True` forbids random access. Rows are streamed to the output XML stream. Memory stays bounded. Formatting must be applied at append time via `WriteOnlyCell`.

## Streaming data into the writer

Never materialise a 1M-row dataframe in memory just to write Excel. Stream:

```python
def stream_rows(conn, query, chunk_size=5000):
    with conn.execute(query) as cur:
        while (rows := cur.fetchmany(chunk_size)):
            for r in rows:
                yield r

for row in stream_rows(conn, sql):
    ws.write_row(r_idx, 0, row)
    r_idx += 1
```

For pandas, use `read_sql` with `chunksize=` and iterate:

```python
for chunk in pd.read_sql(sql, conn, chunksize=5000):
    for _, row in chunk.iterrows():
        ws.write_row(...)
```

`iterrows()` is slow for tight loops; `itertuples(index=False, name=None)` is faster.

## Memory caps (Linux)

### resource.setrlimit (per process)

```python
import resource

def cap_memory(bytes_limit: int = 1024 * 1024 * 1024):   # 1 GB
    resource.setrlimit(resource.RLIMIT_AS, (bytes_limit, bytes_limit))
```

Call at worker boot. Runaway jobs raise `MemoryError` instead of swapping the host to death. Catch in the job runner, mark the job failed with "memory_limit_exceeded", and continue.

### systemd MemoryMax

For worker services run under systemd:

```ini
# /etc/systemd/system/report-worker.service
[Service]
MemoryMax=1G
MemoryHigh=850M
TasksMax=64
```

`MemoryHigh` applies soft throttling (kernel pressures the cgroup). `MemoryMax` is the hard OOM boundary.

### Docker / Kubernetes

```yaml
resources:
  limits:
    memory: 1Gi
    cpu: "2"
  requests:
    memory: 512Mi
    cpu: "1"
```

Always set both limits and requests. Requests drive scheduling; limits prevent neighbours starving.

## Parallelism strategy

### Chart generation — process pool, not threads

matplotlib is not thread-safe for simultaneous figure builds. Use `ProcessPoolExecutor`:

```python
from concurrent.futures import ProcessPoolExecutor
import os

def build_all_charts(spec_list, out_dir):
    workers = min(os.cpu_count() or 2, 4)
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker) as pool:
        list(pool.map(_render_one, spec_list))

def _init_worker():
    import matplotlib
    matplotlib.use("Agg")
```

CPU-bound with high RAM per figure (each process can peak at 100–300 MB during a complex chart). Four workers on a 4 GB container is a safe ceiling.

### Document writers — one process per job

Do not parallelise within a single document build (race conditions on the workbook object, headers, fonts). Instead, parallelise at the job level:

```text
N worker processes  x  1 job each  =  N concurrent reports
```

Run N = cores, capped by memory budget. A 16-core machine with 32 GB RAM and a 1 GB job ceiling handles 16 concurrent jobs.

### Threads — only for I/O

Threads are fine for:

- fetching raw data via HTTP (async or `ThreadPoolExecutor`)
- uploading finished artefacts to S3
- sending webhook notifications

They are not fine for matplotlib, numpy-heavy transforms, or python-docx/reportlab writes.

## Caching brand assets

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def load_logo_bytes(tenant_id: int, logo_version: str) -> bytes:
    tenant = Tenant.load(tenant_id)
    return tenant.logo_path.read_bytes()

@lru_cache(maxsize=1)
def register_brand_fonts_once():
    # Expensive: parse TTF headers. Do it once per process.
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont("Inter", FONT_DIR / "Inter-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Inter-B", FONT_DIR / "Inter-Bold.ttf"))
    return True
```

Cache key includes `logo_version` so brand updates invalidate. Cache bounded by `maxsize` to avoid unbounded memory growth on many-tenant workers.

## Avoiding formula-heavy huge workbooks

Excel must recalculate every formula at open time. A 100,000-row workbook with SUMIFS in each row takes 30+ seconds to open. Rules:

- under 1,000 rows: formulas are fine.
- 1,000 – 10,000 rows: formulas for totals rows only.
- over 10,000 rows: pre-compute everything in pandas, write values (not formulas).

Pre-computed totals stay correct; formulas do not update to reflect the underlying data change anyway because the source sheet is static.

```python
# Bad: recalc cost scales with rows.
ws.write_formula(r, 5, f"=D{r+1}*E{r+1}")

# Good: compute in pandas, write value.
ws.write_number(r, 5, qty * price)
```

## Volatile formulas

Avoid `NOW()`, `TODAY()`, `OFFSET()`, `INDIRECT()`, `INDEX` chains with `MATCH`. They trigger recalc on every edit. If a timestamp is needed, write the current timestamp as a value at generation time.

## Chart count per workbook

Each native xlsxwriter chart adds overhead to open time. Budget:

- < 10 charts per workbook: fine.
- 10 – 25 charts: acceptable for dashboards.
- \> 25 charts: prefer matplotlib PNGs inserted as images. Faster to open, smaller file on balance when total raster size stays reasonable.

## File I/O

Always write to a temp path and rename on success:

```python
tmp_path = final_path.with_suffix(final_path.suffix + ".tmp")
workbook_write(tmp_path)
tmp_path.replace(final_path)   # atomic on POSIX
```

Consumers never see a half-written file.

Use local fast disk for temp (`/var/tmp` on a fast SSD, not NFS). Final artefacts can live on network storage; the writer's temp path should not.

## Long-running workers

Matplotlib's state and python's font cache grow slowly. Recycle workers:

```python
# RQ / Celery / Arq
WORKER_MAX_JOBS = 200   # after 200 jobs, exit and let the supervisor respawn
```

A fresh worker re-imports, clears caches, and the RSS drops back to baseline.

## Profiling

Before optimising, measure. `cProfile` for CPU, `memory_profiler` or `tracemalloc` for memory.

```python
import tracemalloc
tracemalloc.start()
build_report(...)
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics("lineno")[:10]:
    print(stat)
```

Run on representative tenant data (large, medium, small) — not toy fixtures.

## Anti-patterns

- Parallelising chart builds with threads — silent corruption and crashes.
- Loading a 500 MB DataFrame into memory to write 50k rows — stream instead.
- Cached logos with no version key — stale logos after brand updates.
- Enabling `constant_memory` then trying to `merge_range` across rows — runtime error mid-write.
- Workers with no `MemoryMax` or `RLIMIT_AS` — a single runaway job swaps the host and hangs all other jobs.
- Formulas across 100k rows with volatile functions — the file opens in minutes.
- Temp files on the same disk as the artefact store NFS mount — pathological write amplification.
- Recycling workers only on crash — slow memory drift invisible until an OOM storm.
