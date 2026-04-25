# Tooling: uv, ruff, pre-commit, CI

Expands the **Package management** and **Formatting + linting** sections of `SKILL.md`. Covers uv commands we actually use, the ruff rule catalogue with enable/disable guidance, pre-commit configuration, and CI integration.

## uv — the only package manager

uv (from Astral) replaces pip, pip-tools, virtualenv, pipx, and pyenv for our Python work. It is written in Rust, resolves dependencies 10–100x faster than pip-tools, and produces reproducible lockfiles.

### Commands we actually use

```bash
# --- project bootstrap ---
uv init --package service-name         # creates pyproject.toml, src/ layout
uv python pin 3.12                     # writes .python-version

# --- daily dependency work ---
uv add fastapi pydantic                # runtime deps
uv add --dev pytest ruff mypy          # dev deps (legacy; prefer groups)
uv add --group test pytest respx       # dep groups (preferred on uv >= 0.4)
uv remove sqlalchemy                   # removes + updates lockfile
uv sync                                # installs from lockfile, exact versions
uv sync --frozen                       # CI mode: fail if lockfile is stale
uv sync --no-dev                       # production images
uv lock --upgrade                      # refresh entire lockfile
uv lock --upgrade-package fastapi      # bump one package

# --- running code ---
uv run pytest                          # runs inside the managed venv
uv run --with ipython python           # temporary extra package
uv run python -m service_name

# --- tool management (pipx replacement) ---
uv tool install pre-commit             # installs globally, isolated
uv tool run ruff check .               # ephemeral tool run
uv tool upgrade --all
```

### Lockfile discipline

- Commit `uv.lock`. Never edit it by hand.
- CI must use `uv sync --frozen` so a stale lockfile fails the build instead of silently resolving new versions.
- Treat lockfile changes in PRs as a review signal: they appear only when someone ran `uv add`, `uv remove`, or `uv lock --upgrade`. Reviewers should confirm the change matches the PR's intent.

### Never mix

Do not use pip, poetry, pipenv, conda, or `requirements.txt` in the same repo as uv. They fight the lockfile. If you must interoperate (e.g. a legacy deployment target), export with `uv export --format requirements-txt > requirements.txt` at build time and never check that file in.

## ruff — the only formatter and linter

Ruff replaces black, isort, flake8, pyupgrade, bugbear, pydocstyle, pylint (for the rules we use), and several smaller tools. One binary, one config, one format pass, sub-second runs on medium codebases.

### Rule categories — what to enable and why

Always enabled across every service:

| Prefix | Rule set | Why |
| --- | --- | --- |
| `E`, `W` | pycodestyle errors/warnings | Basic style conformance |
| `F` | pyflakes | Unused imports, undefined names, real bugs |
| `I` | isort | Deterministic import order |
| `UP` | pyupgrade | Keeps syntax modern (e.g. `dict[str, int]` over `Dict[str, int]`) |
| `B` | flake8-bugbear | Catches the most common real bugs (mutable defaults, loop vars, etc.) |
| `S` | flake8-bandit | Security rules — SQL injection, `eval`, weak crypto |
| `C4` | flake8-comprehensions | Encourages readable comprehensions |
| `SIM` | flake8-simplify | Simpler conditionals, `dict.get`, etc. |
| `RET` | flake8-return | Cleaner return flow |
| `PL` | pylint subset | Broad sanity rules; noisy ones are ignored individually |
| `RUF` | ruff-specific | Catches things only ruff can see |
| `ASYNC` | flake8-async | Blocking calls in `async def`, forgotten `await` |
| `DTZ` | flake8-datetimez | Forces tz-aware `datetime` |

Enable per-service when relevant:

| Prefix | When to enable |
| --- | --- |
| `ANN` | Only if mypy/pyright strict mode is insufficient — usually skip, mypy is enough |
| `D` | Only for library packages published externally; internal services don't need docstring enforcement |
| `T20` | On worker code where `print()` must never leak — replaces human review |
| `N` | Name conventions — enable when onboarding non-Python developers |
| `PTH` | Encourage `pathlib` over `os.path` — enable for new services |
| `TRY` | Exception-handling style — useful once your exception hierarchy stabilises |
| `TID` | Forbid relative imports — enable in monorepos |
| `PERF` | Performance anti-patterns — enable on hot paths; too noisy globally |

Do not enable:

- `CPY` (copyright headers) — we don't use them internally.
- `COM` (trailing commas) — fights the formatter.
- `Q` (quote style) — the formatter owns this.
- `E501` (line length) — the formatter owns this. Keep it in `ignore`.

### Per-file ignores we use

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "PLR2004", "ANN"]     # assert, magic numbers, annotations
"scripts/*" = ["T201", "S603", "S607"]     # print, subprocess in scripts
"src/*/migrations/*" = ["E501", "I001"]    # auto-generated
"__init__.py" = ["F401"]                   # re-exports
"conftest.py" = ["S101", "ANN"]
```

### ruff vs mypy division of labour

Ruff catches lint and style. Mypy catches type errors. Do not try to make ruff do type checking (the `ANN` rules are shallow). Do not try to make mypy enforce style.

## Pre-commit hooks

Pre-commit runs formatters and linters before each commit. It catches 90% of CI failures locally.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: detect-private-key

  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.4.18
    hooks:
      - id: uv-lock      # keeps uv.lock in sync with pyproject.toml
```

Install once per checkout:

```bash
uv tool install pre-commit
pre-commit install
pre-commit run --all-files     # run against the whole repo
```

Do not add mypy to pre-commit. Mypy is slow on cold cache and frustrating as a commit-time hook. Run it in CI and via `uv run mypy src/` locally on demand.

## CI integration

The CI block below runs in under 2 minutes for a typical 10k-LOC service. Caching uv's wheel store and mypy's cache are the main levers.

```yaml
# .github/workflows/ci.yml (GitHub Actions shape; adapt for Gitea/GitLab)
name: ci
on:
  pull_request:
  push:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          version: "0.4.18"
          enable-cache: true
      - run: uv sync --frozen
      - run: uv run ruff format --check .
      - run: uv run ruff check .
      - name: mypy
        run: uv run mypy src/
      - name: tests
        run: uv run pytest --cov=src --cov-fail-under=80
      - name: dependency audit
        run: uv run pip-audit --strict
```

Notes:

- `--frozen` fails the build if `uv.lock` is out of sync. This is what we want.
- Run `ruff format --check` before `ruff check`; a format diff often masks real lint issues.
- `mypy` runs after lint because mypy cache invalidation is expensive; fail fast on cheap checks first.
- `pip-audit` only needs to run on schedule (weekly) for most services; include it on PR when a security window is short.

## Common gotchas

- Do not put `rev` values in pre-commit as floating tags. Pin to a version and bump intentionally.
- `uv sync` installs dev deps by default. Production images must pass `--no-dev` or build-time wheel size balloons.
- `ruff check --fix` is safe for formatting-adjacent fixes (`I`, `UP`). For `B`, `PL`, `S` changes review the diff before committing.
- If ruff and the formatter disagree about something, the formatter wins. Remove the conflicting lint rule.

## Cross-references

- Project layout: `project-layout.md`.
- Typing config: `typing-mypy-pyright.md`.
- Security rules for ruff `S`: `security-baseline.md`.
- CI gates: see "CI gates" section in `SKILL.md`.
