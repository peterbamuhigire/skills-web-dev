# Project Layout

Expands the **Project layout** section of `SKILL.md`. Covers the full `src/` layout, a complete `pyproject.toml` template, monorepo vs per-service tradeoffs, and when to split a service into multiple packages.

## Why src/ layout

The `src/` layout prevents the classic "imports work locally but fail after `pip install`" bug. Tests always import via the installed package, never from a sibling directory. This is the layout recommended by the Python Packaging Authority and enforced in every service we build.

Flat layout is prohibited. It hides import errors, pollutes the working directory with the package import path, and encourages test code that only passes in development.

## Full directory layout

```text
service-name/
|-- pyproject.toml            # single source of truth for build + tooling
|-- uv.lock                   # committed lockfile
|-- README.md
|-- CHANGELOG.md              # for anything shipped to another service
|-- .env.example              # documented env vars, no secrets
|-- .gitignore
|-- .python-version           # pinned interpreter for uv / pyenv
|-- .pre-commit-config.yaml
|-- .github/workflows/ci.yml  # (or equivalent for the CI in use)
|-- src/
|   `-- service_name/         # snake_case; matches `project.name` in pyproject
|       |-- __init__.py       # exposes public API only; keep tiny
|       |-- __main__.py       # optional; enables `python -m service_name`
|       |-- main.py           # entrypoint (FastAPI app factory, worker bootstrap)
|       |-- config.py         # pydantic-settings Settings singleton
|       |-- logging_config.py # structlog setup
|       |-- exceptions.py     # custom exception hierarchy
|       |-- api/              # FastAPI routers, request/response models
|       |   |-- __init__.py
|       |   |-- deps.py       # shared FastAPI dependencies (auth, db, etc.)
|       |   `-- v1/
|       |       `-- invoices.py
|       |-- workers/          # queue consumers, scheduled jobs
|       |-- domain/           # pure business logic, no I/O, no frameworks
|       |   |-- __init__.py
|       |   |-- invoicing.py
|       |   `-- subscriptions.py
|       |-- adapters/         # I/O: DB repos, HTTP clients, file stores
|       |   |-- db/
|       |   |   |-- models.py     # SQLAlchemy models
|       |   |   `-- repositories.py
|       |   |-- http/
|       |   |   `-- stripe_client.py
|       |   `-- storage/
|       |-- schemas/          # Pydantic models shared across layers
|       `-- utils/            # small, genuinely generic helpers
|-- tests/
|   |-- conftest.py           # top-level fixtures
|   |-- unit/                 # mirrors src/service_name/
|   |   |-- domain/
|   |   `-- adapters/
|   |-- integration/          # touches DB, Redis, filesystem, fakes
|   `-- e2e/                  # optional; FastAPI TestClient or real HTTP
|-- scripts/                  # one-off CLI scripts invoked via `uv run`
|   `-- backfill_invoices.py
`-- docs/                     # optional; ADRs, runbooks
    `-- adr/
```

**Rules**:

- `domain/` never imports from `adapters/`, `api/`, or any framework.
- `adapters/` imports from `domain/` (to implement interfaces), never the other way round.
- `api/` and `workers/` are the only layers that wire `domain` + `adapters` together.
- `utils/` is a last resort. If something lives there for more than a sprint, it belongs in a named module.

## Complete pyproject.toml template

Copy this into a new service and edit the top-level metadata. Every field below is load-bearing.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "service-name"
version = "0.1.0"
description = "One-line description of what this service does."
readme = "README.md"
requires-python = ">=3.11,<3.13"
license = { text = "Proprietary" }
authors = [{ name = "Peter Bamuhigire" }]

dependencies = [
    "fastapi>=0.115",
    "pydantic>=2.9",
    "pydantic-settings>=2.5",
    "structlog>=24.4",
    "httpx>=0.27",
    "sqlalchemy>=2.0",
    "asyncpg>=0.29",        # or PyMySQL/aiomysql for MySQL-backed services
]

[project.optional-dependencies]
# Group deps by deployment shape when a service has multiple entrypoints.
worker = ["redis>=5.0", "rq>=1.16"]

[dependency-groups]
# uv-native dev groups. Not installed in prod images.
dev = [
    "pytest>=8.3",
    "pytest-cov>=5.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.6",
    "mypy>=1.11",
    "respx>=0.21",
    "freezegun>=1.5",
    "pip-audit>=2.7",
]

[project.scripts]
service-name = "service_name.main:cli"

[tool.hatch.build.targets.wheel]
packages = ["src/service_name"]

# --- ruff ------------------------------------------------------------------
[tool.ruff]
line-length = 100
target-version = "py312"
extend-exclude = ["migrations", "scripts/legacy"]

[tool.ruff.lint]
select = [
    "E", "F", "W",     # pycodestyle + pyflakes
    "I",               # isort
    "UP",              # pyupgrade
    "B",               # bugbear
    "S",               # bandit (security)
    "C4",              # comprehensions
    "SIM",             # simplify
    "RET",             # return
    "PL",              # pylint
    "RUF",             # ruff-specific
    "ASYNC",           # asyncio gotchas
    "DTZ",             # datetime tz-aware
]
ignore = ["E501", "PLR0913"]  # line length handled by formatter; allow wide constructors

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "PLR2004"]     # allow assert + magic numbers in tests
"scripts/*" = ["T201"]              # allow print() in scripts

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

# --- mypy ------------------------------------------------------------------
[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]
mypy_path = "src"
namespace_packages = true
explicit_package_bases = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false    # fixtures and parametrize values are often Any

# --- pytest ----------------------------------------------------------------
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--import-mode=importlib",
]
markers = [
    "integration: touches DB, Redis, or external services",
    "slow: takes more than 1 second",
]
filterwarnings = ["error", "ignore::DeprecationWarning:pydantic.*"]
asyncio_mode = "auto"

# --- coverage --------------------------------------------------------------
[tool.coverage.run]
source = ["src/service_name"]
branch = true
omit = ["*/migrations/*", "*/__main__.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = true
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

## Monorepo vs per-service repo

| Signal | Choose per-service repo | Choose monorepo |
| --- | --- | --- |
| Services share 0 code | yes | no |
| Services share typed contracts (Pydantic schemas, events) | fine either way | better |
| Teams deploy independently and have different release cadences | yes | only with strong tooling |
| Fewer than 4 services total | yes | overkill |
| Need atomic cross-service refactors | no | yes |
| CI budget is tight | yes | no (monorepo CI needs change-based filtering) |

**Our default**: per-service repo for independent services (e.g. `invoicing-service`, `reporting-service`). Use a shared PyPI-published internal package for cross-cutting concerns (event schemas, auth helpers). A monorepo is only worth it once you have 5+ services, shared domain types, and the tooling to run targeted CI.

## When to split one service into multiple packages

Most services are a single Python package in a single repo. Split only when one of these applies:

- A genuinely reusable library emerges (event schemas, a client SDK) and at least 2 services consume it. Publish it to an internal index.
- The service grows two deployment shapes that share no dependencies (e.g. a FastAPI API and a heavyweight ML worker pulling in torch). Use extras (`[project.optional-dependencies]`) first. Only split into separate packages when the Docker image sizes diverge by more than 500MB or cold-start budgets diverge sharply.
- Clear bounded contexts that are deployed separately. At that point they are separate services, not separate packages — give each its own repo.

Do **not** split because:

- The codebase "feels big" — 50k lines in one well-layered package is fine.
- A team wants "their own" module — modules inside `src/service_name/` are enough.
- You anticipate a future split — YAGNI. Wait until the split is obvious.

## Cross-references

- Tooling details: `tooling-uv-ruff.md`.
- Typing config: `typing-mypy-pyright.md`.
- Testing layout: `testing-pytest.md`.
- Deployment shape (sidecar, worker): `python-saas-integration` skill.
