# Python Skills for the SaaS Stack — Design Spec

**Date:** 2026-04-15
**Author:** Peter Bamuhigire (with Claude Code, Opus 4.6)
**Status:** Approved design — ready for scaffolding

## Purpose

Add Python as a first-class capability alongside the existing PHP + Android + iOS SaaS stack. Python should make analytics, document generation, ML/forecasting, document intelligence, and ETL tasks materially better than what is feasible in PHP alone — without disrupting the existing architecture.

## Stack Assumptions

- Backend: PHP + MySQL serving web UIs and REST APIs to Android (Kotlin/Compose) and iOS (Swift/SwiftUI) clients.
- Servers: Debian / Ubuntu (per existing `linux-security-hardening`, `cicd-jenkins-debian` skills).
- CI/CD: Jenkins or GitHub Actions (existing `cicd-pipelines`, `cicd-jenkins-debian`).
- Deployment baseline: same hosts as PHP, with Python services run via systemd behind nginx.
- Multi-tenant SaaS with strict tenant isolation (existing `multi-tenant-saas-architecture`).

## Integration Pattern (decided)

Two complementary patterns, used per use case:

- **Pattern A — FastAPI sidecar:** Python runs as a small HTTP service on the same host. PHP calls it synchronously for fast operations (compute KPIs, render a one-page Excel summary, score a single record).
- **Pattern C — Background worker:** PHP enqueues jobs (Redis / RQ or Celery + Redis). A Python worker picks them up for long-running work (multi-tab Excel dashboards, bulk forecasting, ETL syncs, OCR pipelines). On completion, the worker writes outputs to storage and notifies the user.

Same Python codebase powers both. Choose per use case based on latency and payload size.

## Skill Set (6 skills, capped)

Read order: `python-modern-standards` + `python-saas-integration` are the two foundation skills, always loaded first. Then load whichever of skills 3–6 fits the task.

### 1. `python-modern-standards`

**Purpose:** Define how Python is written across all our projects so Claude/Codex produce consistent, production-grade code on every file.

**SKILL.md outline:**

- Frontmatter (`name`, `description: Use when writing or reviewing any Python code in our SaaS projects...`)
- Python version baseline (3.11+)
- Project layout (`src/` layout, `pyproject.toml`)
- Package management — **uv** with committed lockfile
- Formatting + linting — **ruff** (replaces black, isort, flake8) with config snippet
- Type hints — required on all signatures, `mypy --strict` or `pyright` in CI
- Pydantic v2 — used at every external boundary (API I/O, queue messages, config)
- Logging — structlog with JSON in production
- Configuration — pydantic-settings + `.env`, never `os.environ` directly
- Async vs sync rules — when to use each, never mix in a single path
- Error handling — custom exception hierarchy, no bare `except`
- Testing — pytest layout + conventions (depth in reference)
- Security baseline — secrets, parameterized SQL, input validation, dependency scanning
- Anti-patterns specific to Python (mutable defaults, blocking I/O in async, etc.)
- Pointer to references for deep dives

**references/:**

- `project-layout.md` — full src layout, pyproject.toml template, monorepo vs per-service trade-offs
- `tooling-uv-ruff.md` — uv commands, ruff config in detail, pre-commit hooks
- `typing-mypy-pyright.md` — strict typing patterns, generics, Protocol, TypedDict, exhaustive checks
- `pydantic-v2-patterns.md` — models, validators, serialization, settings, performance notes
- `logging-structlog.md` — JSON output, request context, correlation IDs, log routing
- `async-vs-sync.md` — decision rules, pitfalls, FastAPI implications
- `error-handling.md` — exception hierarchy, boundary translation, retry semantics
- `testing-pytest.md` — fixtures, parametrize, factories, coverage, integration vs unit
- `security-baseline.md` — secrets, SQL safety, input validation, dependency scanning, SAST
- `anti-patterns.md` — concrete examples of what not to do, with fixes

### 2. `python-saas-integration`

**Purpose:** Define how Python services plug into the existing PHP + mobile SaaS — architecture, deployment, communication, observability.

**SKILL.md outline:**

- Frontmatter (`description: Use when integrating Python services into a PHP-backed SaaS — sidecar APIs, queued workers, deployment...`)
- Architecture overview — Pattern A and Pattern C with diagram
- Decision rule — when to use sidecar vs worker
- FastAPI sidecar setup (project skeleton, uvicorn, gunicorn-uvicorn worker)
- Background worker setup — recommend RQ for simple, Celery for complex; Redis as broker
- PHP ↔ Python contract — HTTP auth (shared signed token / mTLS), JSON schema discipline
- Shared file handoff — local storage vs S3, signed URLs, cleanup
- Multi-tenant safety — tenant ID propagation, strict isolation, no cross-tenant queries
- Deployment on Debian — systemd units, nginx reverse proxy, env management, log rotation
- Observability — structured logs aligned with PHP, metrics endpoint, tracing across PHP and Python
- Security — internal-only binding, network policy, secrets, rate limits on internal API
- Failure modes — what happens when Python is down; PHP fallbacks; queue back-pressure
- Versioning + rollouts — blue/green for sidecar, drain-and-restart for workers
- Pointer to references

**references/:**

- `fastapi-sidecar.md` — full project skeleton, routing, dependency injection, health checks, OpenAPI
- `background-workers.md` — RQ setup, Celery setup, when to choose which, worker concurrency, queue topology
- `php-python-contract.md` — auth options (HMAC token, mTLS, IP allowlist), JSON contract conventions, error envelope, idempotency keys
- `file-handoff.md` — temp storage, S3 patterns, signed download URLs, mobile delivery, cleanup jobs
- `tenant-isolation.md` — propagating tenant_id, validating in workers, audit trail
- `deployment-debian.md` — systemd unit templates, nginx config, virtualenv strategy, secrets via env, log rotation
- `observability.md` — structlog → log shipper, OpenTelemetry traces across PHP and Python, key metrics
- `failure-modes.md` — circuit breakers in PHP, retry policies, dead-letter queues, recovery runbooks

### 3. `python-data-analytics`

**Purpose:** Compute analytics, KPIs, financial math, and geospatial calculations from data already in the SaaS — going beyond what is reasonable in pure SQL.

**SKILL.md outline:**

- Frontmatter (`description: Use when computing complex analytics, KPIs, financial math, or geospatial analytics in Python...`)
- When Python beats raw SQL (decision rule)
- Pandas + numpy idioms tuned for SaaS workloads
- Loading data — SQLAlchemy + pandas `read_sql`, chunking for big results
- Cohort, funnel, retention, churn analysis recipes
- Aggregation, pivoting, window-style calculations
- Financial math — IRR, NPV, amortization schedules, depreciation, compounding
- Statistical tests, outlier detection (rule-based + z-score + IQR)
- Geospatial analytics — Shapely, GeoPandas, route optimization basics, geofencing analytics
- Performance — vectorization, memory, when to switch to Polars
- Output handoff — return JSON to PHP, persist to MySQL, feed into document-generation skill
- Pointer to references

**references/:**

- `pandas-idioms.md` — vectorization, copy vs view, dtypes, datetime handling, common pitfalls
- `loading-data.md` — SQLAlchemy + pandas, connection pooling, chunked reads, mysql/postgres specifics
- `cohort-funnel-retention.md` — full recipes with example data shapes
- `financial-math.md` — IRR, NPV, amortization, depreciation, day-count conventions, currency precision (Decimal)
- `statistics-and-anomalies.md` — descriptive stats, hypothesis tests, anomaly detection patterns
- `geospatial-analytics.md` — Shapely, GeoPandas, distance/area, route optimization, geofence stats
- `performance-and-polars.md` — when pandas hurts and Polars helps, profiling, memory tuning

### 4. `python-document-generation`

**Purpose:** Generate beautiful, branded, downloadable Excel, Word, and PDF documents that end users access from web, Android, and iOS apps.

**SKILL.md outline:**

- Frontmatter (`description: Use when generating downloadable Excel dashboards, Word documents, or PDF reports in Python — branded, designer-grade output...`)
- Output strategy — sync (small files via sidecar) vs async (large files via worker + signed URL)
- Excel dashboards — openpyxl vs xlsxwriter, when to pick each
- Excel patterns — multi-sheet, charts, conditional formatting, pivots, branded headers, cell protection, formulas
- Word documents — python-docx, branded letterhead, sections, tables, embedded charts, headers/footers
- PDF reports — reportlab for programmatic precision, weasyprint for HTML/CSS-driven layouts; when to choose which
- Chart generation — matplotlib / plotly static export, embedding into Excel/Word/PDF
- Branding system — central palette, fonts, logo placement, header/footer templates
- Delivery to web/Android/iOS — temp storage, signed URLs, mobile-friendly filenames, MIME types
- Async generation flow — enqueue → worker writes file → notify client → client downloads
- Performance — streaming, memory caps, parallel sheet generation
- Pointer to references

**references/:**

- `excel-openpyxl-vs-xlsxwriter.md` — feature matrix, examples, pick-list
- `excel-dashboard-patterns.md` — multi-sheet template, charts, conditional formatting, pivot tables, formulas
- `word-python-docx.md` — letterhead template, structured sections, embedded charts, tables, footers
- `pdf-reportlab.md` — programmatic layouts, financial statements, audit trails
- `pdf-weasyprint.md` — HTML/CSS-driven PDF, when this beats reportlab, CSS quirks
- `charts-for-embedding.md` — matplotlib + plotly static export tuned for Excel/Word/PDF
- `branding-system.md` — palette, fonts, logo, headers/footers reused across all output types
- `delivery-and-downloads.md` — async flow, signed URLs, mobile delivery, MIME, filename conventions
- `performance.md` — streaming writers, memory, parallelism, very large workbook strategies

### 5. `python-ml-predictive`

**Purpose:** Add real predictive analytics — forecasting, classification, anomaly detection — to the SaaS, complementing LLM-based AI features with statistical/ML rigor.

**SKILL.md outline:**

- Frontmatter (`description: Use when adding forecasting, classification, regression, or anomaly detection to a SaaS feature...`)
- When to use ML vs LLM vs rules (decision rule)
- Data preparation discipline — train/validation/test splits, leakage prevention
- Time-series forecasting — Prophet, statsmodels (ARIMA, ETS), holidays, seasonality
- Classification + regression — scikit-learn pipelines, feature engineering, common models
- Anomaly detection — isolation forest, statistical methods, streaming patterns
- Model evaluation — appropriate metrics per task (no accuracy on imbalanced data)
- Versioning + serving — model registry (lightweight), serialization, loading at startup
- Integration — exposing predictions via FastAPI sidecar, batch scoring via worker
- Monitoring — drift detection, performance over time, retraining triggers
- Trust + explainability — confidence intervals, feature importance, presenting predictions to users
- Pointer to references

**references/:**

- `when-ml-vs-llm-vs-rules.md` — decision rules with concrete examples
- `data-prep.md` — splits, leakage, scaling, encoding, imbalanced data handling
- `forecasting-prophet.md` — Prophet usage, seasonality, holidays, regressors
- `forecasting-statsmodels.md` — ARIMA, ETS, when these beat Prophet
- `classification-regression-sklearn.md` — pipeline patterns, common models, hyperparameter tuning
- `anomaly-detection.md` — isolation forest, statistical detectors, streaming
- `evaluation-metrics.md` — picking metrics by problem type, business-aligned thresholds
- `model-serving.md` — serialization, loading, versioning, A/B, rollback
- `monitoring-and-drift.md` — drift detection, retraining triggers, performance dashboards
- `explainability.md` — feature importance, SHAP basics, confidence display in UI

### 6. `python-data-pipelines`

**Purpose:** Bring data into the SaaS from external systems and unstructured inputs — APIs, files, images — and transform it for downstream use.

**SKILL.md outline:**

- Frontmatter (`description: Use when building ETL jobs, document intelligence, OCR, or image processing pipelines in Python...`)
- Pipeline architecture — scheduling, idempotency, reconciliation, retry, dead-letter
- ETL / external API sync — Stripe, payment gateways, bank feeds, tax portals, government APIs
- Document intelligence — OCR (Tesseract), PDF text + table extraction (pdfplumber, camelot)
- Image / media processing — Pillow, server-side optimization, thumbnails, watermarking, PDF↔image
- Scheduling — APScheduler vs cron, when to choose which
- Data validation — Pydantic at ingestion boundaries, dead-letter on validation failures
- Storage handoff — landing zone → cleaned → loaded into MySQL with audit
- Multi-tenant pipelines — strict isolation, per-tenant credentials, rate-limit per tenant
- Observability — pipeline runs, success/failure metrics, lag monitoring, alert thresholds
- Pointer to references

**references/:**

- `pipeline-architecture.md` — patterns, idempotency, reconciliation, retry, dead-letter queue
- `etl-external-apis.md` — Stripe, payment gateways, bank feeds, tax portals — auth, rate limits, pagination
- `ocr-tesseract.md` — Tesseract setup, image preprocessing, multi-language, accuracy tuning
- `pdf-extraction.md` — pdfplumber for text, camelot for tables, ocrmypdf for scanned docs
- `image-processing-pillow.md` — optimization, thumbnails, watermarks, format conversion, EXIF
- `scheduling.md` — APScheduler vs cron vs Celery beat, pros/cons
- `validation-and-deadletter.md` — Pydantic at ingest, quarantine bad records, replay
- `multi-tenant-pipelines.md` — credential vault per tenant, isolation, rate limiting
- `observability-pipelines.md` — run tracking, lag, success rate, alerts

## Cross-references between skills

- Every skill 3–6 references skills 1 and 2 in its SKILL.md ("assumes you've read python-modern-standards and python-saas-integration").
- `python-document-generation` references `python-data-analytics` for the "compute then render" pattern.
- `python-data-pipelines` references `python-data-analytics` for post-load enrichment.
- `python-ml-predictive` references `python-data-analytics` for feature engineering and `python-data-pipelines` for training data ingestion.

## Validation

After scaffolding each skill, run:

```text
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

## Out of scope (explicit non-goals)

- Django, Flask templating, or Python-rendered web UIs — UI stays in PHP / Android / iOS.
- Replacing PHP for any existing functionality — Python adds capability, does not migrate.
- Heavy MLOps tooling (MLflow, Kubeflow, SageMaker) — keep ML serving lightweight.
- A separate `python-tdd` skill — testing standards live inside `python-modern-standards`. May be split later if it grows.
- Real-time streaming (Kafka, Flink) — out of scope for v1; revisit if needed.

## Update points for repository docs after implementation

- `README.md` — add Python skills to the list.
- `PROJECT_BRIEF.md` — note that the repository now covers Python alongside PHP, JS/TS, Android, iOS.
- `CLAUDE.md` — add Python to the language standards section and reference the read order.

## Sequencing

1. Scaffold all 6 directories with SKILL.md outlines (this step).
2. Fill out SKILL.md content per skill.
3. Fill out references/ files per skill.
4. Validate each skill with `quick_validate.py`.
5. Update `README.md`, `PROJECT_BRIEF.md`, `CLAUDE.md`.

Skill content is filled in this order: 1 → 2 → 3 → 4 → 5 → 6.
