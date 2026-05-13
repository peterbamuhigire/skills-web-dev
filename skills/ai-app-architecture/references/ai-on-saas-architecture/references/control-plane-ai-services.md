# Control-Plane AI Services — Reference

The five AI control-plane services in depth. These are the cross-cutting AI services every feature in a multi-tenant SaaS consumes. They sit alongside the seven generic control-plane services (`saas-control-plane-engineering/references/control-plane-services.md`).

## 1. LLM Gateway

See `ai-on-saas-architecture/references/llm-gateway-design.md` and `ai-model-gateway/SKILL.md`.

Single outbound surface to all LLM providers. Owns model resolution, rate limit, fallback, audit, cost capture, safety hooks.

## 2. Prompt Registry

**Owns:** Versioned prompts, per-tenant pinning, A/B variants, rollback.

**Schema:**
```sql
CREATE TABLE prompts (
    prompt_id          VARCHAR(64) PRIMARY KEY,    -- e.g. 'support.answer'
    description        TEXT,
    owner_team         VARCHAR(64),
    created_at         DATETIME NOT NULL
);

CREATE TABLE prompt_versions (
    prompt_id          VARCHAR(64) NOT NULL,
    version            VARCHAR(32) NOT NULL,        -- e.g. 'v17' or 'v17-experimental'
    template           TEXT NOT NULL,
    variables_schema   JSON NOT NULL,
    model_hint         VARCHAR(64),
    eval_dataset_id    VARCHAR(64),
    status             ENUM('draft','published','deprecated') NOT NULL,
    published_at       DATETIME,
    PRIMARY KEY (prompt_id, version)
);

CREATE TABLE tenant_prompt_pins (
    tenant_id          BIGINT UNSIGNED NOT NULL,
    prompt_id          VARCHAR(64) NOT NULL,
    pinned_version     VARCHAR(32) NOT NULL,
    pinned_by          BIGINT UNSIGNED,
    pinned_at          DATETIME NOT NULL,
    PRIMARY KEY (tenant_id, prompt_id)
);
```

**Rules:**
- Prompts are referenced by `prompt_id` + `version` everywhere. Never inline.
- Default version is the published latest; tenants can pin a version (enterprise feature).
- Promoting a draft → published requires the eval harness to pass.
- Deprecating a published version requires no tenant to be pinned to it.

## 3. Knowledge-Base (KB) Service

**Owns:** Per-tenant document ingestion, chunking, embedding, vector storage, retrieval.

See `ai-rag-multi-tenant/SKILL.md` for the data plane.

**API surface (v1):**
- `POST /kb/tenants/{tenant_id}/sources` — register a source (S3 bucket, Notion workspace, URL list).
- `POST /kb/tenants/{tenant_id}/ingest` — trigger ingestion run.
- `GET  /kb/tenants/{tenant_id}/status` — chunks, embeddings, last-ingest, size.
- `POST /kb/tenants/{tenant_id}/search` — retrieve top-k chunks for a query.
- `DELETE /kb/tenants/{tenant_id}` — purge (called by erasure cascade).

**Critical:** every API method takes `tenant_id` and the service refuses to operate without it.

## 4. Eval Harness

**Owns:** Golden datasets, prompt regression, judge runs, CI gate, drift detection.

See `ai-eval-harness/SKILL.md`.

**Modes:**
- **CI gate**: blocks deploy if a candidate prompt regresses the golden suite.
- **Nightly drift**: replays the last 24h sampled production traffic; compares output distribution.
- **On-demand**: a developer runs `eval run --prompt support.answer.v18` against goldens.
- **Per-tenant gate**: before promoting a prompt change to a flagship tenant, run their per-tenant golden subset.

## 5. AI Audit Log

**Owns:** Append-only ledger of every AI request. Source of truth for cost attribution, compliance evidence, replay/debug.

**Schema (Postgres + S3 for payloads):**
```sql
CREATE TABLE ai_requests (
    request_id         CHAR(26) PRIMARY KEY,        -- ulid
    tenant_id          BIGINT UNSIGNED NOT NULL,
    user_id            BIGINT UNSIGNED,
    feature            VARCHAR(64) NOT NULL,
    prompt_id          VARCHAR(64),
    prompt_version     VARCHAR(32),
    model_used         VARCHAR(64) NOT NULL,
    region             VARCHAR(32) NOT NULL,
    tokens_in          INT NOT NULL,
    tokens_out         INT NOT NULL,
    usd_cost           DECIMAL(10,6) NOT NULL,
    latency_ms         INT NOT NULL,
    fallback_used      BOOLEAN NOT NULL DEFAULT FALSE,
    safety_findings    JSON,
    eval_score         DECIMAL(5,4),
    grounding_score    DECIMAL(5,4),
    citations          JSON,
    payload_s3_key     VARCHAR(255),                -- redacted prompt + response
    created_at         DATETIME(3) NOT NULL,
    INDEX (tenant_id, created_at),
    INDEX (feature, created_at)
);
```

**Retention:** 90 days hot in Postgres; archive to S3/Parquet for 13 months; purged on tenant erasure.

**Why not just OTel traces?** Traces are operational; the audit log is the legal/billing/compliance record. Different retention, different access control, different write semantics (append-only, no edit).

## v1 Stack

For an early-stage SaaS launching its first real AI feature:

- Gateway (services 1) — required.
- Prompt registry (service 2) — required; trivial v1 = a YAML directory + a service that loads it.
- KB service (service 3) — only if launching RAG. Otherwise skip.
- Eval harness (service 4) — minimum: a `pytest` directory of goldens that runs in CI.
- Audit log (service 5) — required; v1 = the `ai_requests` table only.
