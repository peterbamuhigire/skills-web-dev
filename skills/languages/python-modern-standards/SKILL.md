---
name: python-modern-standards
description: Use when writing, reviewing, or distributing Python applications, including PyInstaller, auto-py-to-exe, Nuitka, frozen desktop executables, multi-tool suites, installers, and CI release builds. Defines the Python baseline and routes executable packaging to its desktop-distribution automation.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Python Modern Standards
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when writing or reviewing any Python code in our SaaS projects — defines Python version, project layout, tooling (uv, ruff, mypy), typing, Pydantic v2, logging, configuration, async rules, error handling, testing, and security baseline. Load this before any other Python skill.

## Workflow

- For Python sidecars, FastAPI services, workers, queue consumers, or API integrations, load `references/api-container-sidecar-engineering.md`.
- For containerized Python work, pair with `docker-development`.
- For PyInstaller, auto-py-to-exe, Nuitka, frozen desktop applications, multi-executable suites, portable ZIPs, Windows installers, or code signing, load `references/python-desktop-distribution.md` and use `scripts/desktop_suite_packager.py`.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Test plan | Markdown doc per `skill-composition-standards/references/test-plan-template.md` covering pytest layout, type checks, and coverage targets | `docs/python/test-plan.md` |
| Release evidence | Desktop distribution evidence | Manifest, generated build files, artifact inventory, hashes, smoke results, and signing status | `release/desktop-suite-evidence.json` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use `references/api-container-sidecar-engineering.md` when Python participates in APIs, workers, queues, sidecars, or Dockerized service delivery.
- Use `references/python-desktop-distribution.md` when Python must ship without a separately installed interpreter.
<!-- dual-compat-end -->
The house style for Python in our PHP + Android + iOS SaaS stack. Every Python file in our projects must follow this skill. Other Python skills (saas-integration, data-analytics, document-generation, ml-predictive, data-pipelines) assume you have read this first.

## When this skill applies

- Starting any Python project, service, script, or job worker.
- Adding Python to an existing PHP-backed SaaS.
- Reviewing or refactoring Python code.
- Setting up CI for a Python codebase.

## Non-negotiables

1. Python **3.11+** (we target 3.12 unless a dependency forces 3.11).
2. `src/` layout with `pyproject.toml`. No `setup.py`. No flat layout.
3. **uv** for package management, lockfile committed.
4. **ruff** for formatting + linting (replaces black, isort, flake8).
5. Type hints on every function signature. **mypy --strict** or **pyright** in CI.
6. **Pydantic v2** at every external boundary (API I/O, queue payloads, config, DB DTOs).
7. **structlog** with JSON output in production.
8. Configuration via **pydantic-settings**, never bare `os.environ[...]`.
9. No bare `except:` — ever. Use a custom exception hierarchy.
10. Tests in **pytest**. Coverage threshold enforced in CI.

## Python version

Use 3.12 as the baseline. 3.11 is acceptable when a server can't upgrade yet. Do not target <3.11 — we rely on `TypeAlias`, `match`, exception groups, faster CPython, and PEP 695 type parameter syntax (3.12).

Pin the version in `pyproject.toml`:

```toml
[project]
requires-python = ">=3.11,<3.13"
```

## Project layout

```text
service-name/
|-- pyproject.toml
|-- uv.lock
|-- README.md
|-- .env.example
|-- .gitignore
|-- src/
|   `-- service_name/
|       |-- __init__.py
|       |-- main.py              # entrypoint (FastAPI app, worker bootstrap)
|       |-- config.py            # pydantic-settings Settings
|       |-- logging_config.py    # structlog setup
|       |-- exceptions.py        # custom exception hierarchy
|       |-- api/                 # FastAPI routers (if sidecar)
|       |-- workers/             # worker tasks (if queue consumer)
|       |-- domain/              # pure business logic, no I/O
|       |-- adapters/            # DB, HTTP, file system — anything with I/O
|       |-- schemas/             # Pydantic models
|       `-- utils/
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- conftest.py
`-- scripts/                     # one-off CLI scripts
```

See `references/project-layout.md` for the full `pyproject.toml` template, monorepo considerations, and when to split a service into multiple packages.

## Package management — uv

Use `uv` (Astral). Fast, drop-in replacement for pip + pip-tools + virtualenv. Commit the lockfile.

```bash
uv init                   # bootstrap a project
uv add fastapi            # add a dependency
uv add --dev pytest ruff  # add a dev dependency
uv sync                   # install exact versions from lockfile
uv run pytest             # run a command in the venv
uv lock --upgrade         # upgrade lockfile
```

Never mix uv with pip, poetry, or pipenv in the same project. See `references/tooling-uv-ruff.md`.

## Frozen desktop distribution

Treat executable distribution as a release pipeline, not a GUI conversion step. For a suite of tools, prefer a PyInstaller one-folder multipackage build with a generated launcher, shared collection directory, portable ZIP, and platform installer. Keep the product and application list in a committed manifest; generate the spec, launcher, installer, CI workflow, and verification script from it.

Load `references/python-desktop-distribution.md`, then run:

```powershell
python -X utf8 scripts/desktop_suite_packager.py init --project-root <project> --product-name "Example Suite" --publisher "Example Ltd" --app "editor=editor.py" --app "converter=converter.py"
python -X utf8 scripts/desktop_suite_packager.py generate --config <project>/packaging/desktop-suite.toml
python -X utf8 scripts/desktop_suite_packager.py doctor --config <project>/packaging/desktop-suite.toml
```

The script path above is relative to this skill directory. Commit generated project files so CI does not depend on the skills engine being installed on the runner.

## Formatting + linting — ruff

Ruff is the only formatter/linter. It replaces black, isort, flake8, pyupgrade, bugbear, and more.

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E", "F", "W",        # pycodestyle + pyflakes
    "I",                  # isort
    "UP",                 # pyupgrade
    "B",                  # bugbear
    "S",                  # bandit (security)
    "C4",                 # comprehensions
    "SIM",                # simplify
    "RET",                # return
    "PL",                 # pylint
    "RUF",                # ruff-specific
]
ignore = ["E501"]         # line length handled by formatter

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]      # allow assert in tests
```

Pre-commit hook runs `ruff format` + `ruff check --fix`. CI runs `ruff check` (no auto-fix).

## Typing — mypy --strict or pyright

Every function signature has types. No untyped `def`. Use `mypy --strict` or `pyright --strict` in CI. Pick one per project, not both.

```python
# GOOD
def compute_mrr(subscriptions: list[Subscription], as_of: date) -> Decimal:
    return sum((s.monthly_price for s in subscriptions if s.is_active(as_of)), Decimal(0))

# BAD
def compute_mrr(subscriptions, as_of):
    ...
```

For complex typing (generics, Protocols, TypedDict, overloads, exhaustive matching), see `references/typing-mypy-pyright.md`.

## Pydantic v2 — at every boundary

Use Pydantic v2 models for:

- FastAPI request/response bodies
- Queue message payloads (RQ, Celery)
- Configuration (via pydantic-settings)
- DTOs crossing module boundaries when validation matters
- External API responses (validate before trusting)

```python
from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal

class InvoiceCreate(BaseModel):
    tenant_id: int = Field(..., gt=0)
    customer_email: EmailStr
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(..., pattern=r"^[A-Z]{3}$")

    model_config = {"frozen": True, "extra": "forbid"}
```

Never pass raw dicts across module boundaries when you can use a Pydantic model. Do not use Pydantic v1 syntax (`@validator`, `Config` class, `.dict()`). See `references/pydantic-v2-patterns.md`.

## Logging — structlog, JSON in production

Use structlog. Bind request/tenant/correlation IDs to every log line. JSON output in production, plain console in development.

```python
import structlog

logger = structlog.get_logger()
logger.info("invoice_created", invoice_id=inv.id, tenant_id=inv.tenant_id, amount=str(inv.amount))
```

Never use `print()`. Never use f-strings inside log calls — pass structured kwargs so fields are queryable. See `references/logging-structlog.md`.

## Configuration — pydantic-settings

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    php_app_base_url: str
    internal_shared_secret: str = Field(..., min_length=32)
    environment: str = Field(default="development", pattern=r"^(development|staging|production)$")

settings = Settings()  # fails fast on startup if anything is missing/invalid
```

Never call `os.environ[...]` outside `config.py`. Never hardcode secrets.

## Async vs sync rules

- **Sync by default** for scripts, workers, data jobs.
- **Async for FastAPI** — but consistent: if a handler is `async def`, everything it awaits must be async. Never call blocking I/O inside an async handler (use `asyncio.to_thread` if you must).
- **Never mix** in one path. If a codepath is sync, don't sprinkle `async def` in it. If it's async, don't call `.sync()` wrappers.
- pandas, numpy, scikit-learn, and most ORMs are sync. Treat that as a signal.

See `references/async-vs-sync.md`.

## Error handling — custom exception hierarchy

Define a root app exception and subclass by category. Translate at boundaries (infra exception → domain exception → HTTP response).

```python
class AppError(Exception):
    """Base for all application errors."""

class ValidationError(AppError): ...
class NotFoundError(AppError): ...
class AuthorizationError(AppError): ...
class ExternalServiceError(AppError): ...
class ConfigurationError(AppError): ...
```

Never `except:` or `except Exception:` without re-raising. Log with context, then raise. See `references/error-handling.md`.

## Testing — pytest

- Tests in `tests/unit/` and `tests/integration/` mirroring `src/` layout.
- `conftest.py` for shared fixtures; one per package level.
- Use `pytest.mark.parametrize` for table-driven tests.
- Never mock what you own. Mock only external boundaries (HTTP, filesystem, time).
- Coverage threshold **80%** for domain code, **60%** overall; enforced in CI.
- Separate unit from integration: `pytest -m 'not integration'` for fast local loops.

See `references/testing-pytest.md`.

## Security baseline

- Secrets only via env → pydantic-settings. Never in code, never in logs.
- SQL always parameterized (SQLAlchemy Core/ORM or `cursor.execute(sql, params)`). No `f"SELECT ... {user_input}"`.
- Validate all external input with Pydantic at the boundary.
- Dependency scanning: `pip-audit` or `safety` in CI, weekly schedule.
- SAST: `ruff` with `S` rules (bandit); `semgrep` optional for deeper checks.
- Never `eval`, `exec`, `pickle.load` from untrusted sources. Never `shell=True` with user input.
- File paths validated against a safe base directory.
- See `references/security-baseline.md` for the full checklist, and cross-reference with `vibe-security-skill` for web-app concerns when the Python service exposes HTTP.

## Anti-patterns (do not do these)

- Mutable default arguments (`def f(x=[])`) — use `None` and initialize inside.
- `from x import *` — explicit imports only.
- Blocking I/O in `async def` handlers — will deadlock the event loop.
- `time.sleep` in workers — use `asyncio.sleep` or scheduler delays.
- `except Exception: pass` — silences bugs. Always log and re-raise or handle specifically.
- Catching `BaseException` — catches `KeyboardInterrupt`, `SystemExit`. Don't.
- Building SQL with f-strings — SQL injection.
- `os.system()` / `shell=True` with user data — command injection.
- Global mutable state (module-level lists/dicts mutated at runtime) — race conditions in async/threaded code.
- `datetime.now()` without tz — use `datetime.now(UTC)`.
- `Decimal` vs `float` confusion for money — always `Decimal` for currency, never `float`.

See `references/anti-patterns.md`.

## CI gates (what must pass before merge)

```text
ruff format --check .
ruff check .
mypy --strict src/
pytest --cov=src --cov-fail-under=80
pip-audit
```

## Read next

When the task requires it, load:

- `references/python-saas-integration.md` — how Python plugs into PHP + mobile SaaS.
- `python-data-analytics` — pandas, KPI computation, financial math.
- `python-document-generation` — Excel, Word, PDF output.
- `python-ml-predictive` — forecasting, classification, anomaly detection.
- `python-data-pipelines` — ETL, OCR, image processing, API syncs.
- `references/python-desktop-distribution.md` — executable suites, installers, signing, CI, and clean-machine release checks.

## References

- `references/project-layout.md`
- `references/tooling-uv-ruff.md`
- `references/typing-mypy-pyright.md`
- `references/pydantic-v2-patterns.md`
- `references/logging-structlog.md`
- `references/async-vs-sync.md`
- `references/error-handling.md`
- `references/testing-pytest.md`
- `references/security-baseline.md`
- `references/anti-patterns.md`
- `references/api-container-sidecar-engineering.md`
- `references/python-desktop-distribution.md`
- `scripts/desktop_suite_packager.py`

## Decision Rules

| Condition | Action |
|---|---|
| Work is I/O-bound and dependencies support async | Use one coherent async boundary |
| Value crosses an external boundary | Validate it with an explicit typed model |
| Tooling conflicts with repository policy | Preserve policy and document the exception |

## Capability Contract

Read and search are required. Editing, dependency changes, and execution require authorisation; network access is optional.

## Degraded Mode

Fallback: without execution, provide exact formatter, type-checker, security, and test commands; do not claim compatibility.

## Domain Anti-Patterns

- Adding an untyped dictionary at a trust boundary.
- Mixing blocking calls into an async path.
- Catching broad exceptions without recovery.
- Reading secrets from committed configuration.
- Changing tooling without checking the lockfile.
## Inputs
| Artefact | Required? | Purpose |
|---|---|---|
| Python version, project layout, dependency policy, and code scope | yes | Apply compatible standards |
## Outputs
- Produce Python code or findings with typing, lint, test, configuration, logging, and security evidence.
