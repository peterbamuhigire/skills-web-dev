# Absorbed Skill: postgresql-patterns

Original entrypoint: `skills/postgresql-patterns/SKILL.md`
Active parent skill: `skills/postgresql-engineering/SKILL.md`
Status: Absorbed as reference material; this file preserves the old skill content for progressive disclosure.

---
name: postgresql-patterns
description: Use when adding pgvector to a Debian/Ubuntu PostgreSQL instance, building
  on Supabase, or translating MySQL patterns (AUTO_INCREMENT, ON DUPLICATE KEY,
  LIKE, LAST_INSERT_ID) into PostgreSQL idioms. Covers JSONB and GIN indexing,
  full-text search with tsvector, pgvector HNSW/IVFFlat tuning, Supabase RLS for
  multi-tenant embeddings, PgBouncer pooling, and pg_dump/pg_basebackup operations.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostgreSQL Patterns
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when adding pgvector to a Debian/Ubuntu PostgreSQL instance, building on Supabase, or translating MySQL patterns into PostgreSQL idioms for an AI/embedding workload.
- The task needs reusable judgment about JSONB shape, full-text search, vector indexing, RLS, or pooling rather than ad hoc advice.

## Do Not Use When

- The request is a "migrate from MySQL to PostgreSQL" plan for transactional workloads. MySQL stays primary in this engine; this skill exists to support pgvector and Supabase, not to replace MySQL.
- The work is unrelated to PostgreSQL or would be better handled by `database-design-engineering`, `mysql-best-practices`, or `vector-databases`.

## Required Inputs

- The PostgreSQL major version (13+ required for pgvector), platform (Debian/Ubuntu VPS or Supabase), and whether the workload is OLTP, search, or vector retrieval.
- The embedding model and dimension count if vectors are involved (default assumption: OpenAI `text-embedding-3-small`, 1536 dims).
- Tenancy model: single-tenant, shared schema with `tenant_id`, or schema-per-tenant.

## Workflow

- Read this `SKILL.md` first, then load only the deep-dive references that match the task (JSONB, FTS, pgvector, Supabase RLS, PgBouncer, ops).
- Decide between MySQL-stays-primary, pgvector-on-PostgreSQL, or Supabase using the decision tree in section 1.
- For vector work, design the table, choose HNSW vs IVFFlat with reasoned trade-offs, and verify pre-filters are served by B-tree indexes.
- For multi-tenant Supabase, write RLS policies for every table including embeddings before shipping.
- Validate with `EXPLAIN (ANALYZE, BUFFERS)` on representative queries before declaring done.

## Quality Standards

- Cite the pgvector README, official PostgreSQL docs, Supabase docs, or PgBouncer docs for any non-obvious operator or index syntax.
- Self-managed Debian/Ubuntu PostgreSQL is the default deployment shape. Supabase is the managed alternative; do not over-recommend other cloud-managed services.
- Every multi-tenant deployment must have RLS or equivalent enforcement on every table that holds tenant data, including embeddings.
- Vector indexes do not eliminate the need for metadata indexes. Pre-filters by `tenant_id` should be served by a B-tree.

## Anti-Patterns

- Treating PostgreSQL as a drop-in replacement for MySQL. The engine's polyglot persistence rule says MySQL stays primary.
- Storing transactional data (orders, invoices, RBAC, audit logs) in the vector store.
- Using vector similarity for exact-match lookups.
- Storing un-chunked documents as single embeddings.
- Single-tenant assumptions in multi-tenant deployments.
- Treating embeddings as static and never re-syncing them when the source-of-truth changes.

## Outputs

- A PostgreSQL schema with the right mix of relational, JSONB, and vector columns; a generated tsvector column when full-text search is needed; HNSW or IVFFlat index DDL for vector tables; RLS policies when on Supabase.
- A PgBouncer config recommendation (pooling mode and pool size) sized against the host's CPU count and PG `max_connections`.
- A backup and observability checklist: `pg_dump` or `pg_basebackup`, WAL archiving, replication topology, and the `EXPLAIN (ANALYZE, BUFFERS)` output for the slowest representative query.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Data safety | Schema migration | SQL file with up/down | `db/migrations/2026-05-01-add-embeddings.sql` |
| Performance | Vector index plan | Markdown note with `EXPLAIN (ANALYZE, BUFFERS)` output | `docs/data/pgvector-query-plan.md` |
| Security | RLS policy set | SQL file enabling RLS and tenant policies | `db/policies/embeddings_rls.sql` |

## References

- `references/mysql-to-postgres.md` for the side-by-side translation table.
- `references/jsonb-and-fts.md` for JSONB operators, GIN indexing, and full-text search.
- `references/pgvector.md` for pgvector install, distance operators, and HNSW vs IVFFlat tuning.
- `references/supabase-rls.md` for the Supabase position and worked RLS policies on embeddings.
- `references/pgbouncer.md` for pooling modes, sizing, and the prepared-statement pitfall.
- `references/operations.md` for pg_dump, pg_basebackup, replication, and EXPLAIN ANALYZE.
<!-- dual-compat-end -->

## 1. Why PostgreSQL is in this engine

PostgreSQL is added alongside MySQL to enable pgvector and Supabase projects. MySQL stays primary for transactional workloads. A reader who reaches this skill expecting a "migrate to Postgres" guide is in the wrong place. See `00-front-matter/polyglot-persistence.md` and `references/mysql-to-postgres.md`.

Decision tree:

| Project shape | Database choice |
|---|---|
| Existing MySQL SaaS, want to add semantic search | Keep MySQL; add Pinecone or Qdrant alongside (`vector-databases`). pgvector only if the team already wants to learn Postgres. |
| Greenfield SaaS that wants auth + DB + vectors managed | Supabase from day one. |
| Self-hosted, single DB process, comfortable with PG ops | pgvector on PostgreSQL (Debian/Ubuntu VPS). |
| Multi-modal (text + image embeddings) | Weaviate or Qdrant. Out of scope here. |

## 2. PostgreSQL for MySQL developers

Use modern PostgreSQL idioms over the legacy SQL most MySQL devs already know. The full translation table is in `references/mysql-to-postgres.md`. Five things you need now:

Auto-incrementing primary keys. Use `GENERATED ALWAYS AS IDENTITY` (PostgreSQL 10+), not the legacy `SERIAL` macro. Source: postgresql.org/docs/current/ddl-identity-columns.html.

```sql
-- MySQL
CREATE TABLE users (id BIGINT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255));

-- PostgreSQL (modern)
CREATE TABLE users (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email TEXT NOT NULL
);
```

Pattern matching. `LIKE` is case-sensitive in PostgreSQL. Use `ILIKE` for case-insensitive, `~` and `~*` for regex. MySQL's default case-insensitive `LIKE` is not the PostgreSQL default. Source: postgresql.org/docs/current/functions-matching.html.

`RETURNING`. PostgreSQL `INSERT ... RETURNING` returns generated values in the same statement, replacing the MySQL `INSERT then SELECT LAST_INSERT_ID()` pattern.

```sql
INSERT INTO users (email) VALUES ('a@b.test') RETURNING id, created_at;
```

Upsert. Use `INSERT ... ON CONFLICT (col) DO UPDATE SET ...`. The conflict target (a unique constraint or column) must be named.

```sql
INSERT INTO users (email, name) VALUES ('a@b.test', 'A')
ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name;
```

UUIDs, ENUM, and ARRAY. `gen_random_uuid()` ships in PostgreSQL 13+ without requiring `pgcrypto`. ENUM (`CREATE TYPE ... AS ENUM (...)`) and ARRAY (`base_type[]`) are first-class but constrain refactoring later, so use sparingly. Source: postgresql.org/docs/current/functions-uuid.html, datatype-enum.html, arrays.html.

## 3. JSONB

JSONB is binary-decomposed JSON with operator support and indexability. The full operator reference and decision table are in `references/jsonb-and-fts.md`. Working set:

| Operator | Meaning | Example |
|---|---|---|
| `->` | Extract field as JSONB | `'{"a":1}'::jsonb -> 'a'` returns `1` (jsonb) |
| `->>` | Extract field as text | `'{"a":1}'::jsonb ->> 'a'` returns `'1'` (text) |
| `@>` | Containment (left contains right) | `'[1,2,3]'::jsonb @> '[1,3]'::jsonb` is true |
| `?` | Key existence | `'{"foo":"bar"}'::jsonb ? 'foo'` is true |
| `@?` | JSONPath match (boolean) | `jdoc @? '$.tags[*] ? (@ == "qui")'` |
| `@@` | JSONPath match (returning value) | `jdoc @@ '$.tags[*] == "qui"'` |

Index a JSONB column with GIN. Source: postgresql.org/docs/current/datatype-json.html.

```sql
CREATE INDEX idxgin ON api USING GIN (jdoc);
```

The default GIN operator class supports `?`, `?|`, `?&`, `@>`, `@?`, and `@@`. The `jsonb_path_ops` operator class is faster for containment-only workloads but does not support key-existence operators.

Decision: relational column for fixed-schema queryable data, JSONB with a GIN index for genuinely variable per-row schemas (AI metadata, integration payloads), child table for fixed-shape one-to-many, and `TEXT`/`BYTEA` for opaque blobs read whole. JSONB is not a substitute for normalisation.

## 4. Full-text search

PostgreSQL FTS uses `tsvector` (a normalised, lexeme-indexed document) and `tsquery` (a normalised query). Match operator is `@@`. Source: postgresql.org/docs/current/textsearch-intro.html.

```sql
SELECT to_tsvector('fat cats ate fat rats') @@ to_tsquery('fat & rat');
 ?column?
----------
 t
```

Query operators: `&` AND, `|` OR, `!` NOT, `<->` FOLLOWED BY, `<N>` N positions apart.

The production pattern is a stored generated column plus a GIN index plus `ts_rank_cd`:

```sql
ALTER TABLE articles
  ADD COLUMN search_doc tsvector
  GENERATED ALWAYS AS (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body,''))) STORED;

CREATE INDEX articles_search_gin ON articles USING GIN (search_doc);

SELECT id, ts_rank_cd(search_doc, q) AS rank
FROM articles, to_tsquery('english', 'database & postgres') q
WHERE search_doc @@ q
ORDER BY rank DESC LIMIT 10;
```

PostgreSQL FTS supports stemming dictionaries per language, weighted ranking via `setweight()`, and phrase distance operators. MySQL InnoDB FULLTEXT is simpler but lacks multi-language stemming. For multi-language SaaS workloads, PostgreSQL FTS is materially stronger.

## 5. pgvector

This is the section that earns the skill its place in the engine. All snippets below are from the pgvector README at github.com/pgvector/pgvector v0.8.2. Full HNSW vs IVFFlat tuning detail is in `references/pgvector.md`.

Install (PostgreSQL 13+ required):

```sh
cd /tmp
git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
make && make install
```

Enable the extension:

```sql
CREATE EXTENSION vector;
```

Each vector takes `4 * dimensions + 8 bytes` of storage; each element is a single-precision float. Maximum supported dimensionality is 16,000.

Vector column for OpenAI `text-embedding-3-small` (1536 dims):

```sql
CREATE TABLE items (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id BIGINT NOT NULL,
  source_id BIGINT NOT NULL,             -- FK back to MySQL source row
  embedding vector(1536) NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
```

Distance operators: `<->` L2 (Euclidean), `<#>` negative inner product, `<=>` cosine, `<+>` L1 (taxicab), `<~>` Hamming (binary), `<%>` Jaccard (binary). For L2-normalised embeddings (such as OpenAI `text-embedding-3-*`), cosine and inner product give equivalent rankings.

Top-k similarity with metadata filtering:

```sql
SELECT id, source_id, 1 - (embedding <=> $1) AS similarity
FROM items
WHERE tenant_id = $2
  AND metadata @> '{"doc_type":"article"}'::jsonb
ORDER BY embedding <=> $1
LIMIT 10;
```

Index choice:

| Index | Build cost | Query speed | Tuning knobs | Notes |
|---|---|---|---|---|
| HNSW (multilayer graph) | Slower build, more memory | Faster query | `m`, `ef_construction`, `ef_search` | Generally preferred when memory permits. |
| IVFFlat (inverted lists) | Faster build, less memory | Tunable | `lists`, `probes` | Build after data is loaded; `lists` approximately rows/1000 for under 1M rows. |

```sql
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

For cosine distance use `vector_cosine_ops`; for inner product use `vector_ip_ops`.

Operational notes: build HNSW indexes `CONCURRENTLY` to avoid blocking writes; IVFFlat needs data present before index creation for good centroid placement; raise `ef_search` (HNSW) or `probes` (IVFFlat) at query time to trade latency for recall; vector indexes do not eliminate the need for B-tree indexes on `tenant_id`.

## 6. Supabase

Supabase wraps PostgreSQL + pgvector + auth + realtime + storage as a managed service. Treat it as the managed alternative for greenfield AI projects.

pgvector is a one-click extension on Supabase. Their position is "the best vector database is the database you already have" (supabase.com/docs/guides/ai).

Enable RLS on every tenant-scoped table, including embeddings. Worked policy:

```sql
alter table embeddings enable row level security;

create policy "tenant_isolation_select" on embeddings
  for select using ( tenant_id = (select auth.jwt() ->> 'tenant_id')::bigint );

create policy "tenant_isolation_insert" on embeddings
  for insert to authenticated
  with check ( tenant_id = (select auth.jwt() ->> 'tenant_id')::bigint );
```

The supabase-js query builder does not natively understand pgvector operators. Wrap vector queries in a SQL function and call it via `supabase.rpc()`. See `references/supabase-rls.md` for the full pattern and a per-tenant policy template.

## 7. PgBouncer

PostgreSQL `max_connections` is bounded (typically 100-200) and each connection consumes memory. PgBouncer maintains a small pool of real PG connections and multiplexes many client connections over them. Source: pgbouncer.org/features.html.

Modes:

- Session pooling. Server connection assigned for the entire client session. Supports all PostgreSQL features.
- Transaction pooling. Server connection assigned only during a transaction. Breaks a few session-based features. Highest throughput.
- Statement pooling. Multi-statement transactions disallowed. Maximum reuse.

Default for web/SaaS workloads: transaction pooling. Switch to session pooling for clients that depend on prepared statements or session state.

Prepared-statement pitfall. Prepared statements break in transaction pooling unless the client uses simple-protocol or PgBouncer 1.21+ with `server_prepared_statements = on`. Fix by upgrading PgBouncer, enabling that setting, or moving the offending app to a session-mode pool on a separate port.

Sizing rule of thumb: `pool_size` per database is roughly twice the PostgreSQL host's CPU cores; total client connections may be 10-20x `pool_size`. Tune from observed `pg_stat_activity` waiting counts. See `references/pgbouncer.md`.

## 8. Operations

Logical backup with `pg_dump` (single database, portable across PG versions):

```sh
pg_dump -Fc -d mydb -f mydb.dump
pg_restore -d mydb_new mydb.dump
```

Physical backup with `pg_basebackup` (full cluster, foundation for streaming replication):

```sh
pg_basebackup -D /var/lib/postgresql/backup -Ft -z -P
```

WAL archiving uses `archive_mode = on` and `archive_command` in `postgresql.conf`. Point-in-time recovery requires WAL plus a base backup. Streaming replication ships WAL to a hot standby; logical replication ships row-level changes through publications and subscriptions. See `references/operations.md`.

`EXPLAIN (ANALYZE, BUFFERS)` is the single most valuable habit:

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM items
WHERE tenant_id = 42
ORDER BY embedding <=> $1 LIMIT 10;
```

Read top-down looking for: index scan vs sequential scan, actual rows vs estimated rows (off by more than 10x means stats are out of date; run `ANALYZE`), and whether the vector index is actually selected. If the planner chose a sequential scan, check that the operator class on the index matches the operator in the query (`vector_l2_ops` with `<->`, `vector_cosine_ops` with `<=>`, `vector_ip_ops` with `<#>`).

## 9. Anti-patterns

1. "Migrate from MySQL to PostgreSQL" to enable pgvector. Add a vector store alongside instead.
2. Storing transactional data in the vector store (orders, invoices, RBAC, audit logs).
3. Using vector similarity for exact-match lookups.
4. Storing un-chunked documents as single embeddings.
5. Single-tenant assumptions in multi-tenant deployments.
6. Treating embeddings as static (no sync to source-of-truth changes).

## 10. Cross-references

- `vector-databases` for embedding generation, chunking, hybrid search, and vector store comparison.
- `ai-rag-patterns` for production RAG using pgvector or external vector stores.
- `database-design-engineering` for tenancy, indexing, migrations.
- `mysql-best-practices` for the engine's primary OLTP database.
- `cicd-devsecops` for `DATABASE_URL` and embedding-API key handling.

