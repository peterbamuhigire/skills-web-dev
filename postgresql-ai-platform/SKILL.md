---
name: postgresql-ai-platform
description: PostgreSQL as an AI data platform, sourced from "Building a Data and
  AI Platform with PostgreSQL" (2025). Covers pgvector for embeddings storage and
  ANN search (IVFFlat/HNSW), Retrieval-Augmented Generation (RAG) pipeline design,
  AI application design patterns (schema-aware LLM, NL2SQL guardrails, chunking strategies),
  16 critical AI build fault lines, pgai extension, and sovereign data platform principles.
  Companion to ai-rag-patterns, postgresql-fundamentals, and postgresql-advanced-sql.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostgreSQL as an AI Data Platform

<!-- dual-compat-start -->
## Use When

- PostgreSQL as an AI data platform, sourced from "Building a Data and AI Platform with PostgreSQL" (2025). Covers pgvector for embeddings storage and ANN search (IVFFlat/HNSW), Retrieval-Augmented Generation (RAG) pipeline design, AI application design patterns (schema-aware LLM, NL2SQL guardrails, chunking strategies), 16 critical AI build fault lines, pgai extension, and sovereign data platform principles. Companion to ai-rag-patterns, postgresql-fundamentals, and postgresql-advanced-sql.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `postgresql-ai-platform` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Data safety | pgvector schema and embedding pipeline | Markdown doc covering embedding model choice, vector dimensions, and tenancy scoping for AI workloads | `docs/data/pgvector-schema.md` |
| Performance | Vector index performance plan | Markdown doc covering ivfflat / hnsw choice, recall vs latency budget, and EXPLAIN samples | `docs/data/pgvector-perf.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Why PostgreSQL for AI

- **Single source of truth** — transactional data + vector embeddings in one database
- **pgvector** — native approximate nearest-neighbour search (ANN)
- **ACID guarantees** — embeddings stay consistent with the data they represent
- **Rich SQL + AI** — join embedding search results with structured filters in one query
- **Sovereignty** — your data stays in your infrastructure

## pgvector — Embeddings in PostgreSQL

### Setup

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Storing Embeddings

```sql
-- Documents with embeddings (1536 dims = OpenAI text-embedding-3-small)
CREATE TABLE documents (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    content     TEXT NOT NULL,
    metadata    JSONB,
    embedding   vector(1536),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 3072 dims for text-embedding-3-large
-- 768 dims for nomic-embed-text
-- 384 dims for all-MiniLM-L6-v2
```

### Inserting Embeddings

```sql
-- Insert with embedding (from application layer)
INSERT INTO documents (content, metadata, embedding)
VALUES (
    'PostgreSQL supports full-text search natively.',
    '{"source": "docs", "section": "fts"}',
    '[0.021, -0.034, ...]'::vector   -- array from embedding API
);
```

### Similarity Search

```sql
-- Cosine distance (recommended for text embeddings — angle, not magnitude)
SELECT id, content, metadata,
       1 - (embedding <=> '[0.021, -0.034, ...]'::vector) AS similarity
FROM documents
ORDER BY embedding <=> '[0.021, -0.034, ...]'::vector
LIMIT 10;

-- L2 distance (Euclidean — good for image embeddings)
SELECT id, content, embedding <-> query_vec AS distance
FROM documents
ORDER BY embedding <-> '[...]'::vector LIMIT 10;

-- Inner product (for normalized vectors)
SELECT id, content, (embedding <#> query_vec) * -1 AS score
FROM documents ORDER BY embedding <#> '[...]'::vector LIMIT 10;
```

### Hybrid Search: Vector + Metadata Filter

```sql
-- Combine semantic search with structured filter (critical for multi-tenant)
SELECT id, content,
       1 - (embedding <=> $1::vector) AS score
FROM documents
WHERE metadata->>'tenant_id' = $2       -- hard filter
  AND metadata->>'section' = 'faq'      -- structured filter
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

### Index Types for ANN

```sql
-- IVFFlat: faster build, lower memory, slightly less accurate
-- lists: sqrt(row_count) is a good starting point
CREATE INDEX documents_embedding_ivf ON documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- HNSW: faster queries, higher recall, more memory
-- Recommended for production: better accuracy/speed tradeoff
CREATE INDEX documents_embedding_hnsw ON documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Adjust search quality at query time (HNSW)
SET hnsw.ef_search = 100;   -- higher = more accurate, slower

-- Adjust probe count at query time (IVFFlat)
SET ivfflat.probes = 10;
```

### Choosing Index Type

| | IVFFlat | HNSW |
|---|---|---|
| Build speed | Fast | Slower |
| Memory | Low | Higher |
| Query recall | Good | Excellent |
| Recommended | Dev / low-memory | Production |

## RAG Pipeline Design

### Architecture

```
User Query
    │
    ▼
Embed Query (LLM API)
    │
    ▼
Vector Search (pgvector) + Metadata Filters
    │
    ▼
Retrieve Top-K Chunks
    │
    ▼
Build Prompt (system + chunks + user query)
    │
    ▼
LLM Generation
    │
    ▼
Response to User
```

### Chunking Strategy

Chunk quality determines retrieval quality. Rules from the book:

| Strategy | When to Use |
|---|---|
| **Fixed-size with overlap** | Homogeneous text (logs, support tickets) |
| **Sentence / paragraph** | Articles, documentation — preserve semantic units |
| **Section-based** | Structured docs (manuals, legal) — chunk at headings |
| **Semantic chunking** | Use embedding similarity to find natural break points |

```sql
-- Store chunk metadata for context reconstruction
CREATE TABLE chunks (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id   BIGINT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index   INT NOT NULL,
    content       TEXT NOT NULL,
    token_count   INT,
    embedding     vector(1536),
    metadata      JSONB,   -- {section, page, heading, source_url}
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX chunks_embedding_hnsw ON chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

### Keeping Embeddings Fresh

```sql
-- Track embedding generation status
ALTER TABLE chunks ADD COLUMN embedded_at TIMESTAMPTZ;
ALTER TABLE chunks ADD COLUMN embedding_model TEXT;

-- Queue-based re-embedding on content change
CREATE FUNCTION queue_reembedding() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.content IS DISTINCT FROM OLD.content THEN
        NEW.embedding := NULL;
        NEW.embedded_at := NULL;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER chunks_reembed
    BEFORE UPDATE ON chunks
    FOR EACH ROW EXECUTE FUNCTION queue_reembedding();

-- Application worker polls:
SELECT id, content FROM chunks WHERE embedding IS NULL LIMIT 100;
```

### Metadata-Rich Retrieval

```sql
-- Retrieve with full context for prompt building
SELECT
    c.content,
    c.metadata->>'heading' AS section,
    c.metadata->>'source_url' AS source,
    d.metadata->>'document_title' AS doc_title,
    1 - (c.embedding <=> $1::vector) AS score
FROM chunks c
JOIN documents d ON d.id = c.document_id
WHERE d.metadata->>'tenant_id' = $2
ORDER BY c.embedding <=> $1::vector
LIMIT 5;
```

## AI Application Design Patterns

### Schema-Aware LLM (NL2SQL)

Provide schema context to the LLM so it generates valid SQL:

```sql
-- Store schema snapshots for LLM context
CREATE TABLE schema_context (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name  TEXT NOT NULL,
    description TEXT NOT NULL,   -- business-level description
    columns     JSONB NOT NULL,  -- [{name, type, description}]
    sample_data JSONB,           -- 2-3 representative rows
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

**NL2SQL guardrails (mandatory):**

```sql
-- Validate generated SQL before execution
-- 1. Only allow SELECT — reject DML
-- 2. Enforce row limit
-- 3. Timeout guard
-- 4. Schema-bound: only allow known tables

SET statement_timeout = '5s';
SET row_security = on;   -- RLS as second safety layer
```

### Inserting AI Outputs Safely

```sql
-- Never pass LLM output directly to SQL — always parameterised
-- Application must extract structured fields, not interpolate raw text

-- Structured AI output schema
CREATE TABLE ai_insights (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_query TEXT NOT NULL,
    model_used   TEXT NOT NULL,
    insight      TEXT NOT NULL,
    confidence   NUMERIC(3,2),
    raw_response JSONB,         -- full API response for debugging
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

### pgai Extension

```sql
CREATE EXTENSION IF NOT EXISTS ai;

-- Generate embeddings via pgai (calls OpenAI internally)
SELECT ai.openai_embed('text-embedding-3-small', content) AS embedding
FROM documents;

-- Generate text
SELECT ai.openai_chat_complete(
    'gpt-4o',
    jsonb_build_array(
        jsonb_build_object('role', 'user', 'content', 'Summarise: ' || content)
    )
)->>'content' AS summary
FROM documents WHERE id = 1;
```

## 16 Critical AI Build Fault Lines

From "Building a Data and AI Platform with PostgreSQL":

### Business Fault Lines

1. **Team misalignment** — data engineers, ML engineers, and product must agree on data definitions before building
2. **GenUX too early** — validate core data quality before adding AI UI features
3. **Unscalable feedback loops** — build structured human feedback from day one (`ai_feedback` table)
4. **Undefined ROI / success metrics** — define evaluation metrics before shipping any AI feature
5. **AI ethics and data privacy oversights** — classify data sensitivity before sending to LLM APIs
6. **Insufficient data product thinking** — treat data as a product with SLAs, not a by-product

### Technical Fault Lines

7. **Schema drift** — generated SQL breaks when columns are renamed; use schema versioning
8. **Latent infrastructure debt** — connection pooling, index maintenance, VACUUM — all affect AI query latency
9. **Lack of embedding/retrieval optimisation** — wrong chunking kills retrieval quality
10. **Overdependence on a single AI provider** — always abstract the LLM client layer
11. **Missing real-world use case playbooks** — test with real user queries, not synthetic ones
12. **SQL generation without guardrails** — LLM-generated SQL must be validated before execution
13. **Lack of multi-tiered architecture** — separate OLTP (transactions), OLAP (analytics), and vector (RAG)
14. **Inadequate prompt engineering lifecycle** — version and evaluate prompts like code
15. **Lack of real-time schema awareness** — LLM context must reflect current schema, not a stale snapshot
16. **Lack of observability** — log every LLM call: model, tokens, latency, cost, success/failure

### Observability Schema

```sql
CREATE TABLE llm_call_log (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    feature         TEXT NOT NULL,         -- 'rag_qa', 'nl2sql', 'summarise'
    model           TEXT NOT NULL,
    prompt_tokens   INT,
    completion_tokens INT,
    total_tokens    INT,
    latency_ms      INT,
    cost_usd        NUMERIC(10,6),
    success         BOOLEAN NOT NULL,
    error_message   TEXT,
    user_id         BIGINT,
    tenant_id       BIGINT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX llm_log_tenant_feature ON llm_call_log (tenant_id, feature, created_at DESC);
```

## Sovereign AI Data Platform Principles

1. **Data stays in your infrastructure** — use local models (Ollama + pgvector) or private cloud when data is sensitive
2. **Transactional data is the competitive moat** — your proprietary data is what makes AI valuable
3. **Platform over silos** — one PostgreSQL cluster with pgvector + PostGIS + JSONB beats five specialised databases
4. **Build on open standards** — PostgreSQL extensions, not vendor-locked vector databases
5. **Compliance by design** — data classification, RLS, and audit triggers before AI features

## AI Extension Stack

```sql
CREATE EXTENSION vector;         -- pgvector: ANN search
CREATE EXTENSION ai;             -- pgai: LLM calls from SQL
CREATE EXTENSION pg_trgm;        -- fuzzy text search (hybrid retrieval)
CREATE EXTENSION pg_stat_statements; -- query observability
CREATE EXTENSION pg_cron;        -- schedule embedding jobs

-- Optional
CREATE EXTENSION postgis;        -- geospatial AI (location-aware RAG)
CREATE EXTENSION timescaledb;    -- time-series AI (sensor + event data)
```

## Anti-Patterns

- Creating a vector database silo separate from your OLTP database — sync complexity + consistency issues
- Storing raw LLM output in TEXT without structured fields — unqueryable, unauditable
- IVFFlat index built before data is loaded — lists parameter becomes wrong
- Querying embeddings without metadata pre-filters in multi-tenant systems — returns other tenants' data
- Sending PII to external embedding APIs without privacy review
- No re-embedding pipeline when source content changes — stale embeddings = wrong answers
- Missing `statement_timeout` on NL2SQL execution — runaway queries possible
