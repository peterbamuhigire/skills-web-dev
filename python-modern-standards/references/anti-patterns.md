# Anti-Patterns

Concrete before/after examples for the Python traps we refuse to ship. Each entry is short: what, why, and the rewrite.

## 1. Mutable default arguments

The default is evaluated once, at function definition time. Calls that rely on the default share the same object.

```python
# BAD
def append_to(item, target=[]):
    target.append(item)
    return target

append_to(1)   # [1]
append_to(2)   # [1, 2]  ← surprise
```

```python
# GOOD
def append_to(item, target: list[int] | None = None) -> list[int]:
    if target is None:
        target = []
    target.append(item)
    return target
```

Ruff `B006` catches this.

## 2. `from x import *`

Hides the dependency graph, shadows built-ins, breaks mypy's ability to track names.

```python
# BAD
from datetime import *
from math import *          # now min, max, etc. may or may not be the built-ins

# GOOD
from datetime import datetime, timedelta, UTC
from math import ceil, floor
```

Ruff `F403`, `F405`.

## 3. Blocking I/O in `async def`

Freezes the entire event loop. Every other pending request stops making progress.

```python
# BAD
@app.get("/user/{id}")
async def get_user(id: int) -> User:
    r = requests.get(f"https://api/users/{id}")   # sync!
    return User.model_validate(r.json())
```

```python
# GOOD
@app.get("/user/{id}")
async def get_user(id: int, client: httpx.AsyncClient = Depends(...)) -> User:
    r = await client.get(f"https://api/users/{id}")
    r.raise_for_status()
    return User.model_validate(r.json())
```

See `async-vs-sync.md` for the full list of libraries to swap.

## 4. Bare `except` or `except Exception: pass`

Silences every error including the ones you want to know about. Makes bugs invisible.

```python
# BAD
try:
    charge_customer(order)
except:
    pass                              # the error is gone forever

try:
    charge_customer(order)
except Exception:
    pass                              # nearly as bad
```

```python
# GOOD
try:
    charge_customer(order)
except PaymentDeclinedError:
    mark_order_failed(order, reason="declined")
except ExternalServiceError:
    logger.exception("gateway_unavailable", order_id=order.id)
    raise
```

Catch narrowly. If you truly must catch broadly, log and re-raise.

## 5. Catching `BaseException`

`BaseException` includes `KeyboardInterrupt`, `SystemExit`, and `asyncio.CancelledError`. Catching it breaks Ctrl+C, prevents graceful shutdown, and can trap cancellations.

```python
# BAD
try:
    run_job()
except BaseException:
    logger.error("something happened")

# GOOD
try:
    run_job()
except Exception:
    logger.exception("job_failed")
    raise
```

## 6. SQL built with f-strings

Classic SQL injection. Do not do this, ever — not even "internal", not even for a "trusted" integer.

```python
# BAD
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
# or with SQLAlchemy
session.execute(select(User).where(User.id == user_id))
```

See `security-baseline.md` for dynamic-identifier handling.

## 7. `shell=True` with user input

Command injection. Arbitrary code execution on your server, one tweet away.

```python
# BAD
subprocess.run(f"convert {filename} out.pdf", shell=True)
os.system(f"curl {url}")

# GOOD
subprocess.run(
    ["convert", filename, "out.pdf"],
    check=True, timeout=30, capture_output=True,
)
```

Validate `filename` against a whitelist of extensions on top.

## 8. Global mutable state

Module-level dicts or lists mutated at runtime are a race condition in async and threaded code, and a unit-testing nightmare everywhere.

```python
# BAD
_cache: dict[int, User] = {}

def get_user(id: int) -> User:
    if id not in _cache:
        _cache[id] = load_user(id)
    return _cache[id]
```

```python
# GOOD
from functools import lru_cache

@lru_cache(maxsize=1024)
def get_user(id: int) -> User:
    return load_user(id)

# Or inject a cache instance so tests can swap it:
class UserService:
    def __init__(self, cache: Cache) -> None:
        self._cache = cache
```

## 9. Naive datetimes

`datetime.now()` without a timezone is ambiguous. Comparing a naive and an aware datetime raises `TypeError`. Bugs around DST and JSON serialisation follow.

```python
# BAD
from datetime import datetime
now = datetime.now()                       # naive, local, pain later
expires_at = datetime.utcnow()             # also naive, deprecated in 3.12
```

```python
# GOOD
from datetime import datetime, UTC
now = datetime.now(UTC)
expires_at = datetime.now(UTC) + timedelta(hours=1)
```

Ruff `DTZ` flags naive datetime calls.

## 10. `float` for money

`0.1 + 0.2 != 0.3` in floats. Every currency operation you perform with floats accumulates rounding error. For money, always `Decimal`.

```python
# BAD
price = 0.1
total = price * 3                          # 0.30000000000000004
```

```python
# GOOD
from decimal import Decimal, ROUND_HALF_UP
price = Decimal("0.10")
total = (price * 3).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

Pydantic stores money as `Decimal`. SQLAlchemy uses `Numeric` for the column. JSON-serialise as a string, not a float.

## 11. `is` for equality

`is` tests identity (same object). `==` tests equality. They happen to match for small integers and interned strings, which lulls people into bugs.

```python
# BAD
if status is "pending":            # CPython may warn; logic is wrong outside string interning
    ...

x = 300
y = 300
x is y                              # False on most runtimes
```

```python
# GOOD
if status == "pending":
    ...

# `is` only for singletons:
if value is None:
    ...
if flag is True:    # rare; usually use `if flag:` instead
    ...
```

## 12. Not using context managers

Files, sockets, DB sessions, locks, HTTP clients — anything with a close method needs a context manager. `try/finally` with explicit `.close()` is error-prone.

```python
# BAD
f = open("data.csv")
data = f.read()
# if read() raises, the file never closes; the GC might close it eventually

# GOOD
with open("data.csv", encoding="utf-8") as f:
    data = f.read()
```

Same rule for DB sessions (wrap in a `contextmanager` helper), HTTP clients (`async with httpx.AsyncClient() as client`), `tempfile.TemporaryDirectory()`, `threading.Lock()`.

## 13. Using `print` for logging

`print` bypasses levels, filters, formatters, request context, and your JSON pipeline.

```python
# BAD
print(f"invoice {invoice.id} failed: {reason}")

# GOOD
logger.warning("invoice_failed", invoice_id=invoice.id, reason=reason)
```

See `logging-structlog.md`.

## 14. F-strings inside log messages

Loses all structure. Each call produces a unique string the log pipeline can't group.

```python
# BAD
logger.info(f"processed {count} invoices for tenant {tid}")

# GOOD
logger.info("invoices_processed", count=count, tenant_id=tid)
```

## 15. Bare `raise e` inside except

Truncates the traceback at the re-raise line, losing the original location.

```python
# BAD
try:
    risky()
except Exception as e:
    logger.exception("failed")
    raise e                              # traceback points here, not at risky()

# GOOD
try:
    risky()
except Exception:
    logger.exception("failed")
    raise                                # preserves original traceback
```

## 16. Untyped `def`

mypy --strict rejects it, but it also breaks reader expectations. Every function has types.

```python
# BAD
def apply_discount(order, rate):
    return order.total * (1 - rate)

# GOOD
def apply_discount(order: Order, rate: Decimal) -> Decimal:
    return order.total * (Decimal(1) - rate)
```

## 17. Catching error just to re-raise a generic one

Loses the original cause unless you chain with `from`.

```python
# BAD
try:
    client.get(url)
except httpx.HTTPError:
    raise Exception("request failed")            # cause lost, type generic

# GOOD
try:
    client.get(url)
except httpx.HTTPError as e:
    raise ExternalServiceError(f"GET {url} failed") from e
```

## 18. `os.path` instead of `pathlib`

`pathlib` is typed, object-oriented, cross-platform, and readable. Use `Path` for everything new. `os.path` is legacy.

```python
# BAD
import os.path
full = os.path.join(os.path.dirname(__file__), "data", "config.json")
with open(full) as f:
    ...

# GOOD
from pathlib import Path
full = Path(__file__).parent / "data" / "config.json"
config = full.read_text(encoding="utf-8")
```

## 19. Overusing `*args, **kwargs`

Forwarding everything erases the type signature, defeats mypy, and hides breakage when the callee changes.

```python
# BAD
def create_invoice(*args, **kwargs):
    return _repo.insert(*args, **kwargs)

# GOOD
def create_invoice(
    tenant_id: int,
    amount: Decimal,
    currency: str,
) -> Invoice:
    return _repo.insert(tenant_id=tenant_id, amount=amount, currency=currency)
```

Reserve `**kwargs` for genuinely open-ended helpers (e.g. logger.bind).

## 20. Swallowing warnings

`warnings.filterwarnings("ignore")` at module level hides deprecation signals from dependencies. Fix the warning, or silence it with a targeted filter.

```python
# BAD
import warnings
warnings.filterwarnings("ignore")

# GOOD
import warnings
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module="some_library",
    message="deprecated since.*",
)
```

Better: configure in pytest (`filterwarnings = ["error"]`) so new warnings fail tests.

## 21. Checking types with `type(x) == X`

Breaks subclassing. Use `isinstance`.

```python
# BAD
if type(obj) == User:
    ...

# GOOD
if isinstance(obj, User):
    ...
```

## 22. Assertions for runtime validation

`assert` is stripped under `python -O`. Never use for input validation.

```python
# BAD
def transfer(amount: Decimal) -> None:
    assert amount > 0, "amount must be positive"
    ...

# GOOD
def transfer(amount: Decimal) -> None:
    if amount <= 0:
        raise ValidationError("amount must be positive")
    ...
```

`assert` is fine for developer invariants during tests or `assert_never` exhaustiveness checks.

## Cross-references

- `security-baseline.md` covers the SQL, shell, and deserialisation anti-patterns in more depth.
- `async-vs-sync.md` lists the libraries that block the event loop.
- `error-handling.md` covers proper re-raising and translation.
- `logging-structlog.md` covers print-vs-logger and f-string-in-log.
- `testing-pytest.md` covers assertion vs validation.
