---
name: postgresql-fundamentals
description: PostgreSQL core concepts for developers and DBAs coming from MySQL or
  MSSQL. Covers terminology differences (cluster/instance, role/user, tuple/row),
  unique data types (TEXT, TIMESTAMP WITH TIME ZONE, ARRAY, JSONB, UUID), tools (psql,
  pgAdmin, DBeaver), roles and privileges (GRANT/REVOKE, HBA), object types (schemas,
  sequences, views, materialized views, domains), extensions ecosystem, and server
  configuration. Pair with postgresql-advanced-sql, postgresql-performance, postgresql-administration
  for complete coverage.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostgreSQL Fundamentals

<!-- dual-compat-start -->
## Use When

- PostgreSQL core concepts for developers and DBAs coming from MySQL or MSSQL. Covers terminology differences (cluster/instance, role/user, tuple/row), unique data types (TEXT, TIMESTAMP WITH TIME ZONE, ARRAY, JSONB, UUID), tools (psql, pgAdmin, DBeaver), roles and privileges (GRANT/REVOKE, HBA), object types (schemas, sequences, views, materialized views, domains), extensions ecosystem, and server configuration. Pair with postgresql-advanced-sql, postgresql-performance, postgresql-administration for complete coverage.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `postgresql-fundamentals` or would be better handled by a more specific companion skill.
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

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Why PostgreSQL

- **ACID by default** — full transactional integrity, no MyISAM-like footguns
- **Extensible** — add types, operators, index methods, FDWs, procedural languages
- **Standard SQL compliance** — lateral joins, window functions, CTEs, recursive queries
- **Rich ecosystem** — PostGIS, pgvector, pg_cron, timescaledb, Citus
- **Open source governance** — no vendor lock-in, transparent commitfest release process

## Terminology Differences from MySQL / MSSQL

| PostgreSQL | MySQL / MSSQL Equivalent | Notes |
|---|---|---|
| **Cluster** | Instance / Server | A running PostgreSQL process serving multiple databases |
| **Database** | Database / Catalog | Strict isolation — no cross-database joins |
| **Schema** | Schema / Namespace | A namespace within a database (default: `public`) |
| **Role** | User / Login | Unified concept — users and groups are both roles |
| **Tuple** | Row | Internal term; "row" is fine in SQL |
| **TOAST** | Row overflow | Automatic out-of-line storage for large values |
| `COPY` | `BULK INSERT` | Fast bulk data loading |
| `SERIAL`/`IDENTITY` | `AUTO_INCREMENT` | Use `GENERATED ALWAYS AS IDENTITY` (SQL standard) |
| `LIMIT` | `TOP` / `FETCH FIRST` | `LIMIT n OFFSET m` syntax |
| `ILIKE` | `LIKE` (case-insensitive) | PostgreSQL is case-sensitive by default |

## Data Types Unique to PostgreSQL

### Text and Strings

```sql
-- Use TEXT — no length penalty, same storage as VARCHAR
CREATE TABLE articles (
    id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title   TEXT NOT NULL,
    body    TEXT
);

-- VARCHAR(n) only when you need a constraint, not for performance
```

### Date and Time

```sql
-- Always use TIMESTAMPTZ (stores in UTC, displays in session timezone)
CREATE TABLE events (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scheduled  TIMESTAMPTZ
);

-- Interval arithmetic
SELECT NOW() + INTERVAL '30 days';
SELECT AGE(TIMESTAMPTZ '2026-01-01', NOW());   -- returns interval
SELECT DATE_PART('year', NOW());               -- extract year
SELECT EXTRACT(DOW FROM NOW());               -- day of week 0-6
```

### Arrays

```sql
CREATE TABLE products (
    id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tags  TEXT[]
);

INSERT INTO products (tags) VALUES (ARRAY['electronics', 'sale']);

-- Query: any element matches
SELECT * FROM products WHERE 'sale' = ANY(tags);

-- Query: contains all
SELECT * FROM products WHERE tags @> ARRAY['electronics'];

-- Append element
UPDATE products SET tags = tags || 'clearance' WHERE id = 1;
```

### JSONB

```sql
CREATE TABLE configs (
    id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payload JSONB NOT NULL
);

-- Insert
INSERT INTO configs (payload) VALUES ('{"theme": "dark", "lang": "en"}');

-- Query operators
SELECT payload->>'theme' FROM configs;                   -- text
SELECT payload->'settings'->>'notifications' FROM configs; -- nested text

-- Filter
SELECT * FROM configs WHERE payload @> '{"theme": "dark"}';
SELECT * FROM configs WHERE payload ? 'theme';           -- key exists

-- Index (critical for performance)
CREATE INDEX configs_payload_gin ON configs USING GIN (payload);
```

### UUID

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- or "uuid-ossp"

CREATE TABLE users (
    id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL
);
```

### Enums

```sql
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status order_status NOT NULL DEFAULT 'pending'
);

-- Add a new value (cannot remove or reorder)
ALTER TYPE order_status ADD VALUE 'refunded' AFTER 'delivered';
```

## Tools

### psql — Command Line

```bash
# Connect
psql -h localhost -U postgres -d mydb
psql postgresql://user:password@host:5432/dbname

# Key meta-commands
\l              -- list databases
\c mydb         -- connect to database
\dt             -- list tables in current schema
\dt schema.*    -- list tables in schema
\d tablename    -- describe table (columns, indexes, constraints)
\di             -- list indexes
\df             -- list functions
\du             -- list roles
\x              -- toggle expanded output (great for wide rows)
\timing         -- show query execution time
\e              -- open query in $EDITOR
\i script.sql   -- execute SQL file
\copy table TO 'file.csv' CSV HEADER   -- export
\q              -- quit
```

### pgAdmin 4

Web-based GUI. Best for: schema browsing, query editor with EXPLAIN visualiser, backup/restore wizard. Access at `http://localhost:5050` (Docker) or system install.

### DBeaver

Cross-platform GUI. Supports multiple database types. Best for: data comparison, ER diagrams, CSV import/export, SSH tunnelling.

## Roles and Privileges

### Role Attributes

```sql
-- Create a login role (user)
CREATE ROLE app_user WITH
    LOGIN
    PASSWORD 'secure_password'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    CONNECTION LIMIT 20;

-- Create a group role (no login)
CREATE ROLE readonly_group NOLOGIN;

-- Grant group membership
GRANT readonly_group TO app_user;
```

### Privilege System

```sql
-- Database privileges
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT CREATE ON DATABASE mydb TO developer_role;

-- Schema privileges
GRANT USAGE ON SCHEMA public TO app_user;
GRANT CREATE ON SCHEMA public TO developer_role;

-- Table privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_group;

-- Default privileges (apply to future objects)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO readonly_group;

-- Revoke
REVOKE INSERT ON orders FROM app_user;
```

### Host-Based Authentication (pg_hba.conf)

```
# TYPE  DATABASE  USER       ADDRESS         METHOD
local   all       postgres                   peer
host    mydb      app_user   192.168.1.0/24  scram-sha-256
host    all       all        0.0.0.0/0       reject
```

Changes to `pg_hba.conf` require `SELECT pg_reload_conf();` or service restart.

## Object Types

```sql
-- Schema (namespace)
CREATE SCHEMA analytics;
SET search_path TO analytics, public;

-- Sequence
CREATE SEQUENCE invoice_seq START 1000 INCREMENT 1;
SELECT nextval('invoice_seq');

-- View
CREATE VIEW active_users AS
    SELECT id, email, created_at FROM users WHERE deleted_at IS NULL;

-- Materialized View (stores results, must be refreshed)
CREATE MATERIALIZED VIEW monthly_revenue AS
    SELECT DATE_TRUNC('month', paid_at) AS month, SUM(amount) AS revenue
    FROM payments GROUP BY 1;

REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;

-- Domain (constrained type)
CREATE DOMAIN email_address AS TEXT
    CHECK (VALUE ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$');

CREATE TABLE contacts (
    id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email email_address NOT NULL
);
```

## Server Configuration (postgresql.conf)

Key parameters to tune after install:

| Parameter | Default | Recommendation |
|---|---|---|
| `shared_buffers` | 128MB | 25% of RAM |
| `work_mem` | 4MB | 16–64MB (per sort/hash op) |
| `maintenance_work_mem` | 64MB | 256MB–1GB for VACUUM/index builds |
| `effective_cache_size` | 4GB | 75% of RAM (planner hint only) |
| `max_connections` | 100 | Use PgBouncer for pooling; keep <200 |
| `random_page_cost` | 4.0 | 1.1 for SSD storage |
| `wal_buffers` | -1 (auto) | 16MB for write-heavy workloads |
| `checkpoint_completion_target` | 0.9 | Leave at 0.9 |
| `log_min_duration_statement` | -1 | Set 1000 (log queries > 1s) |

```bash
# Apply without restart
SELECT pg_reload_conf();

# Check current value
SHOW shared_buffers;
SELECT current_setting('work_mem');

# Change in session
SET work_mem = '64MB';
```

## Extensions Ecosystem

```sql
-- List installed extensions
SELECT name, default_version, installed_version FROM pg_available_extensions
WHERE installed_version IS NOT NULL;

-- Install
CREATE EXTENSION IF NOT EXISTS pgcrypto;      -- cryptographic functions
CREATE EXTENSION IF NOT EXISTS pg_trgm;       -- trigram fuzzy search
CREATE EXTENSION IF NOT EXISTS postgis;       -- geospatial
CREATE EXTENSION IF NOT EXISTS pg_stat_statements; -- query statistics
CREATE EXTENSION IF NOT EXISTS pg_cron;       -- cron job scheduler
CREATE EXTENSION IF NOT EXISTS vector;        -- pgvector for AI embeddings
CREATE EXTENSION IF NOT EXISTS postgres_fdw;  -- foreign data wrapper

-- Update
ALTER EXTENSION pg_trgm UPDATE;

-- Remove
DROP EXTENSION IF EXISTS pg_trgm;
```

## Mandatory Rules

1. **Use `TIMESTAMPTZ` not `TIMESTAMP`** — always store time zone aware values
2. **Use `TEXT` not `VARCHAR(255)`** — no performance difference, fewer migrations
3. **Use `GENERATED ALWAYS AS IDENTITY`** — not `SERIAL` (deprecated pattern)
4. **Use `gen_random_uuid()`** for UUIDs — requires `pgcrypto` (included in PostgreSQL 13+)
5. **Never cross-database JOIN** — split schema concerns within one database via schemas
6. **GIN index on JSONB columns** — always index JSONB if querying inside the payload
7. **`scram-sha-256` in pg_hba.conf** — never `md5` or `trust` in production
8. **Least privilege** — grant only what the role needs; use group roles for sharing

## Anti-Patterns

- Using `TIMESTAMP` instead of `TIMESTAMPTZ` — silent time zone bugs
- Using `VARCHAR(255)` cargo-culted from MySQL — unnecessary constraint
- Using `SERIAL` — use `GENERATED ALWAYS AS IDENTITY` instead
- Storing JSON as `TEXT` — use `JSONB` for indexing and operators
- Superuser application accounts — always create a restricted role
- No `search_path` discipline — always qualify schema or set explicitly
- Missing `IF NOT EXISTS` on `CREATE EXTENSION` — breaks idempotent migrations
