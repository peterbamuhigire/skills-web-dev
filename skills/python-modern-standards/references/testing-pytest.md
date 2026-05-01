# Testing with pytest

Expands the **Testing** section of `SKILL.md`. Covers layout, fixtures, parametrize, factories (factory-boy), coverage, unit vs integration separation, time mocking, and HTTP mocking.

## Layout

Tests mirror the package they test, one `test_*.py` per source module at minimum.

```text
tests/
|-- conftest.py                 # top-level fixtures (db, settings, http client)
|-- unit/                       # no I/O, no network, no DB
|   |-- domain/
|   |   |-- test_invoicing.py
|   |   `-- test_subscriptions.py
|   `-- adapters/               # test the adapter layer with mocks/fakes
|       `-- test_stripe_client.py
|-- integration/                # real DB, Redis; one `conftest.py` per subdir
|   |-- conftest.py
|   |-- test_invoice_repo.py
|   `-- test_worker_jobs.py
|-- e2e/                        # FastAPI TestClient, full stack
|   `-- test_invoicing_api.py
`-- factories.py                # factory-boy factories shared across tests
```

Run:

```bash
uv run pytest                             # everything
uv run pytest tests/unit                  # fast feedback
uv run pytest -m 'not integration'        # skip slow stuff
uv run pytest -k invoice                  # all tests whose name matches
uv run pytest -x --ff                     # stop on first failure, run failed first next
uv run pytest --cov=src --cov-report=term-missing
```

## Fixtures

Fixtures are the backbone of pytest. Use them for setup/teardown, shared context, and dependency injection. Prefer explicit fixtures over `autouse=True`.

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service_name.config import Settings

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        environment="development",
        database_url="postgresql://test:test@localhost:5432/test",
        internal_shared_secret="x" * 32,
        php_app_base_url="http://php-app.test",
    )

@pytest.fixture(scope="session")
def db_engine(test_settings):
    engine = create_engine(str(test_settings.database_url), future=True)
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(db_engine):
    """Per-test session wrapped in a rollback."""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, future=True)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
```

Rules:

- Fixture scope: `session` for expensive things (engines, app factories), `module` when cross-test state is cheap, `function` (default) for per-test isolation.
- Return fixtures are for data; yield fixtures are for resources that need teardown.
- Use `tmp_path` for filesystem tests — pytest cleans it up automatically.
- Use `monkeypatch` for env vars, attribute patching; it auto-reverts.

## Parametrize — table-driven tests

The cleanest way to cover many input/output pairs.

```python
import pytest
from decimal import Decimal
from service_name.domain.tax import compute_vat

@pytest.mark.parametrize(
    "amount, rate, expected",
    [
        (Decimal("100.00"), Decimal("0.18"), Decimal("18.00")),
        (Decimal("0.00"), Decimal("0.18"), Decimal("0.00")),
        (Decimal("33.33"), Decimal("0.18"), Decimal("6.00")),
        pytest.param(
            Decimal("-10.00"),
            Decimal("0.18"),
            None,
            marks=pytest.mark.xfail(reason="negative amounts not supported yet"),
        ),
    ],
    ids=["standard", "zero", "rounding", "negative"],
)
def test_compute_vat(amount, rate, expected):
    assert compute_vat(amount, rate) == expected
```

- Always provide `ids=` or pytest will generate noisy ones like `test_compute_vat[Decimal('100.00')-Decimal('0.18')-Decimal('18.00')]`.
- Use `pytest.param(..., marks=pytest.mark.xfail)` for known failures rather than commenting cases out.

## Factories with factory-boy

Stop inlining test data. factory-boy builds model instances with sensible defaults that you override only where the test cares.

```python
# tests/factories.py
import factory
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime, UTC
from decimal import Decimal

from service_name.adapters.db.models import Invoice, Tenant

class TenantFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Tenant
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Tenant {n}")
    balance_limit = Decimal("10000.00")
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))

class InvoiceFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Invoice
        sqlalchemy_session_persistence = "commit"

    tenant = factory.SubFactory(TenantFactory)
    amount = Decimal("100.00")
    status = "pending"

# Usage in tests:
def test_overdue_invoices(db_session):
    TenantFactory._meta.sqlalchemy_session = db_session
    InvoiceFactory._meta.sqlalchemy_session = db_session

    InvoiceFactory(status="pending")
    InvoiceFactory.create_batch(5, status="overdue")
    assert count_overdue(db_session) == 5
```

## Time mocking with freezegun

Code that uses `datetime.now()` is hard to test deterministically. Freeze time.

```python
from freezegun import freeze_time
from datetime import datetime, UTC

@freeze_time("2025-04-15 12:00:00")
def test_invoice_is_overdue_after_30_days():
    invoice = make_invoice(issued_at=datetime(2025, 3, 10, tzinfo=UTC))
    assert invoice.is_overdue()

def test_reminder_window(freezer):   # the freezer fixture from pytest-freezegun
    freezer.move_to("2025-04-15")
    ...
    freezer.tick(delta=timedelta(days=1))
    ...
```

Two rules: always write application code that takes a `now` parameter or reads a clock you can inject, and use freezegun only when that is not practical.

## HTTP mocking with respx (httpx) or pytest-httpx

Do not hit real external services in tests. Mock at the HTTP layer so your adapter tests exercise the real request-building code.

```python
import respx
import httpx
import pytest
from service_name.adapters.http.stripe_client import StripeClient

@pytest.mark.asyncio
@respx.mock
async def test_charge_success():
    route = respx.post("https://api.stripe.com/v1/charges").mock(
        return_value=httpx.Response(200, json={"id": "ch_123", "status": "succeeded"})
    )
    async with httpx.AsyncClient(base_url="https://api.stripe.com") as http:
        client = StripeClient(http)
        result = await client.charge(Decimal("10.00"), token="tok_visa")
    assert route.called
    assert result.id == "ch_123"

@pytest.mark.asyncio
@respx.mock
async def test_charge_rate_limited():
    respx.post("https://api.stripe.com/v1/charges").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "2"})
    )
    async with httpx.AsyncClient(base_url="https://api.stripe.com") as http:
        client = StripeClient(http)
        with pytest.raises(RateLimitedError):
            await client.charge(Decimal("10.00"), token="tok_visa")
```

For sync `requests`, use `responses`. For general socket-level mocking, `vcrpy` records real interactions; useful for tight third-party contracts, dangerous if you forget to refresh cassettes.

## Unit vs integration

- **Unit tests** mock out every external dependency. They run in <100ms each. No DB, no network, no filesystem beyond `tmp_path`.
- **Integration tests** use a real DB (Postgres/MySQL container), real Redis, real migrations. Slower but closer to production. Run in CI always; run locally on demand.
- **E2E tests** hit the FastAPI `TestClient` and assert on HTTP responses. A handful of these per service cover the happy paths for every endpoint.

Mark integration tests and slow tests:

```python
@pytest.mark.integration
def test_repo_reads_real_rows(db_session): ...

@pytest.mark.slow
def test_report_generation_under_5_seconds(): ...
```

Marker config lives in `pyproject.toml` (see `project-layout.md`).

## Coverage

```toml
[tool.coverage.run]
source = ["src/service_name"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
```

Rules:

- 80% coverage on domain code, 60% overall. Branch coverage on, not just line coverage.
- Coverage is a floor for "is this module tested at all?" — not a goal. Aim for meaningful tests, not the last 5%.
- Exclude auto-generated code (migrations, schema dumps).
- `# pragma: no cover` on tiny branches that genuinely can't be exercised (defensive `if TYPE_CHECKING`, exhaustive match fall-through).

## What to test

Test at the boundary where behaviour becomes interesting:

- Pure domain functions: unit tests with parametrize.
- Adapters: mock the lower-level driver, test the wrapper logic and error translation.
- Use-cases that orchestrate domain + adapters: unit test with fake adapters (Protocol-based).
- API endpoints: a handful of e2e tests per endpoint covering success, validation failure, and authorization.
- Workers: test the handler function directly with a fake queue message.

Do not mock what you own. If you're mocking your own domain class, the test is testing the mock, not the code.

## Async tests

Use `pytest-asyncio` with `asyncio_mode = "auto"` in `pyproject.toml`. Every `async def test_*` is then a coroutine test automatically.

```python
import pytest

async def test_async_charge(stripe_client):
    result = await stripe_client.charge(Decimal("10.00"), token="tok_visa")
    assert result.status == "succeeded"
```

## Anti-patterns

- Tests that mock six things to exercise one line. Refactor the code; the coupling is the smell, not the test.
- Tests that import from `src/service_name/*/private_module.py`. If you test it, it's public API.
- Tests that rely on ordering (`test_a` creates, `test_b` reads). Each test must set up its own world.
- `time.sleep` in tests to "wait for the thread". Use a synchronisation primitive or a deterministic clock.
- Overly DRY tests. A little duplication in tests is fine; clarity matters more.
- Asserting on log output as the behaviour being tested (unless logging *is* the behaviour). Assert on return values and state changes.

## Cross-references

- Overall test strategy (test pyramid, risk-based coverage): `advanced-testing-strategy` skill.
- Test-driven workflow: `superpowers:test-driven-development`.
- Project layout: `project-layout.md`.
- Verifying before marking work done: `superpowers:verification-before-completion`.
