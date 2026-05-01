# Async vs Sync

Expands the **Async vs sync rules** section of `SKILL.md`. Covers decision rules, asyncio fundamentals, when FastAPI async helps vs hurts, pitfalls, and `asyncio.to_thread` usage.

## Default to sync

Most of our code should be synchronous. Async adds complexity and a whole category of bugs (blocking the event loop, thread-unsafe client reuse, library compatibility) that you only want to pay for when the performance benefit is clear.

Write sync code when:

- The code is a script, batch job, or worker that processes one item at a time.
- The bottleneck is CPU (pandas, numpy, scikit-learn, Excel generation).
- The code uses sync DB drivers (psycopg2, PyMySQL, sqlite3) or any sync library you cannot replace.
- Latency per request is already under ~20ms and you have few concurrent requests.

Write async code when:

- You have many concurrent I/O-bound operations that would otherwise block (HTTP calls to Stripe, DB queries, sending emails in parallel).
- You are running FastAPI and a handler legitimately does multiple I/O operations it could parallelise.
- You are building a WebSocket or SSE endpoint where long-lived connections are the point.
- You are integrating with an async-native library (asyncpg, httpx, redis.asyncio).

## The cardinal rule

Do not mix. If a call stack starts sync, keep it sync. If it starts async, keep it async all the way down. Mixing produces either:

- Blocking the event loop (calling sync I/O inside `async def`), degrading the whole process.
- Deadlocks (calling `asyncio.run` inside an already-running loop, or awaiting a sync function wrapped in `to_thread` that re-enters the loop).

## asyncio fundamentals worth remembering

- One event loop per process. Created by `asyncio.run(...)` or by the framework (uvicorn, arq).
- `await` hands control back to the loop. `async def` functions that never `await` anything are just coroutines that run synchronously once you start them — no benefit.
- `asyncio.gather(a, b, c)` runs coroutines concurrently on the same loop. Not parallel, concurrent — one thread.
- `asyncio.TaskGroup` (3.11+) is the preferred replacement for `gather` with error handling: if one task raises, siblings are cancelled cleanly.
- Tasks you create with `asyncio.create_task` must have a reference somewhere or they can be GC'd mid-flight. Keep them in a set.
- `contextvars` works correctly with asyncio — each task has its own context. This is why `structlog.contextvars` is safe for request-scoped logging.

```python
import asyncio

async def fetch_all(urls: list[str]) -> list[Response]:
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(client.get(u)) for u in urls]
    return [t.result() for t in tasks]
```

## When FastAPI async helps

- An endpoint calls 2+ external services you can do in parallel. `asyncio.gather` cuts latency roughly in half.
- You have high concurrency (hundreds of concurrent clients) and the handlers are mostly waiting on I/O.
- You use SSE / WebSocket / chunked streaming.

## When FastAPI async hurts

- Endpoint does one DB query and returns. Sync is simpler and just as fast.
- You use a sync ORM (default SQLAlchemy with `psycopg2`). Wrapping sync queries in `to_thread` is not free and you lose connection pool reuse.
- The team is small and time spent debugging async bugs outweighs the latency win.

FastAPI allows sync handlers — they are executed in a thread pool. For most CRUD endpoints this is the right call. Use `async def` only where concurrency inside the handler gives you real gains.

## Pitfalls

### Blocking calls in async

The single most common async bug. The event loop cannot progress while any coroutine is blocked on sync I/O.

```python
# BAD
@app.get("/invoice/{id}")
async def get_invoice(id: int) -> Invoice:
    row = session.query(Invoice).filter_by(id=id).first()  # sync DB call!
    return row

# GOOD option 1: make the whole thing sync
@app.get("/invoice/{id}")
def get_invoice(id: int) -> Invoice:
    return session.query(Invoice).filter_by(id=id).first()

# GOOD option 2: use an async DB driver
@app.get("/invoice/{id}")
async def get_invoice(id: int, session: AsyncSession = Depends(...)) -> Invoice:
    return await session.scalar(select(Invoice).where(Invoice.id == id))
```

Libraries that look innocent but are blocking:

- `requests` — blocks. Use `httpx.AsyncClient` in async code.
- `boto3` — blocks. Use `aioboto3` in async code, or wrap calls in `to_thread`.
- `psycopg2` — blocks. Use `asyncpg` or `psycopg` (the new one, it has async support).
- `PyMySQL` — blocks. Use `aiomysql` for async MySQL.
- `redis.Redis` — blocks. Use `redis.asyncio.Redis`.
- `open(...)` — blocks for filesystem I/O. For large files under async, use `aiofiles` or `to_thread`.
- `time.sleep` — blocks. Always use `asyncio.sleep`.

### Sync DB drivers with SQLAlchemy

If you must use sync SQLAlchemy inside FastAPI, prefer sync endpoints. Wrapping `session.execute(...)` in `to_thread` breaks connection pool affinity and produces subtle concurrency bugs.

### Thread safety

- `asyncio` itself is single-threaded. Coroutines on the same loop don't need locks for each other (yield points are explicit).
- The thread pool (`to_thread`, sync endpoints in FastAPI) is multi-threaded. Code run there must be thread-safe — avoid module-level mutable state.
- httpx clients, asyncpg pools, redis.asyncio clients are safe to share across tasks on the same loop; not safe across threads.

### Long-running CPU work

CPU-bound code in `async def` pauses the loop just as hard as a blocking I/O call. For CPU work:

- Short hot section (<50ms): run inline, measure, move on.
- Longer work: offload to `asyncio.to_thread` (releases the GIL during numpy/pandas ops) or a `ProcessPoolExecutor` for pure-Python CPU work.
- Really heavy: move the work to a queue worker.

### Unawaited coroutines

```python
fetch_user(id)   # ruff catches this with ASYNC100 / similar rules
```

A coroutine object sitting there does nothing. Always `await` it or `asyncio.create_task(...)` it.

## asyncio.to_thread — the escape hatch

When you must call sync code from async code, `asyncio.to_thread` runs it in the default thread pool and returns a coroutine you can await.

```python
import asyncio
import pandas as pd

async def build_report(raw: bytes) -> bytes:
    # heavy pandas work — CPU bound but releases the GIL during numpy ops
    def _compute() -> pd.DataFrame:
        df = pd.read_csv(io.BytesIO(raw))
        return df.groupby("tenant_id").agg(...)

    df = await asyncio.to_thread(_compute)
    return df.to_csv().encode()
```

Rules:

- Keep the synchronous callable pure — do not mutate shared state.
- Do not call back into the async world from the thread. If you think you need to, you actually need a queue worker.
- The default thread pool has ~40 threads. If you schedule hundreds of `to_thread` calls concurrently, you will saturate it. For batch work, chunk.

## run_in_executor with a custom pool

If you need isolation (e.g. keep the default pool free for other things) or more threads:

```python
from concurrent.futures import ThreadPoolExecutor

_export_pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="export")

async def export(data: pd.DataFrame) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_export_pool, render_pdf, data)
```

## Our SaaS shape

- FastAPI sidecar services that talk to Stripe, mail providers, webhooks: async with `httpx.AsyncClient`.
- Workers (Redis RQ, arq) for long-running jobs: sync is usually fine because one job at a time.
- Data jobs (pandas, numpy): sync.
- Internal-to-internal HTTP between our services: async if the caller is async, otherwise sync.

## Anti-patterns

- `async def` functions that don't `await` anything — drop the async.
- Sharing `httpx.AsyncClient` across requests as a module-level singleton before first use — use FastAPI's `lifespan` to create one on startup.
- Calling `asyncio.run(something())` from inside an async function — use `await something()`.
- `time.sleep(1)` in async code — always `await asyncio.sleep(1)`.
- Using `requests` in async code — replace with `httpx.AsyncClient`.
- Forgetting to cancel tasks on shutdown — use `TaskGroup` or track them in a set and cancel in a `finally`.

## Cross-references

- FastAPI patterns: `python-saas-integration` skill.
- Worker patterns: `python-saas-integration` skill (Redis / arq section).
- Logging in async contexts: `logging-structlog.md` (contextvars work correctly).
- Anti-patterns summary: `anti-patterns.md`.
