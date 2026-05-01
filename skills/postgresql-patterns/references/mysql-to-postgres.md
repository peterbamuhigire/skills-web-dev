# MySQL to PostgreSQL Translation

This file is the lookup table for developers fluent in MySQL who occasionally write PostgreSQL for pgvector or Supabase work. It is not a migration guide. The engine's polyglot persistence rule says MySQL stays primary for transactional workloads; PostgreSQL is added to support pgvector and Supabase.

## Side-by-side translation

| Concept | MySQL | PostgreSQL (modern) |
|---|---|---|
| Auto-increment PK | `id BIGINT AUTO_INCREMENT PRIMARY KEY` | `id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY` |
| Last inserted id | `SELECT LAST_INSERT_ID()` | `INSERT ... RETURNING id` |
| Upsert | `INSERT ... ON DUPLICATE KEY UPDATE ...` | `INSERT ... ON CONFLICT (col) DO UPDATE SET ...` (named target required) |
| Case-insensitive LIKE | `LIKE 'foo%'` (default) | `ILIKE 'foo%'` or `~* '^foo'` |
| Regex match | `REGEXP` / `RLIKE` | `~` (sensitive), `~*` (insensitive) |
| UUID generation | `UUID()` | `gen_random_uuid()` (PG 13+, no extension) |
| Boolean type | `TINYINT(1)` | `BOOLEAN` |
| Timestamp with TZ | `TIMESTAMP` (interpretation tied to session TZ) | `TIMESTAMPTZ` (stored as UTC, native) |
| String type | `VARCHAR(n)` / `TEXT` | `TEXT` (no length penalty) |
| ENUM | `ENUM('a','b')` inline | `CREATE TYPE ... AS ENUM (...)`, then column references the type |
| Array | None native | `int[]`, `text[]`, etc. |
| JSON | `JSON` (textual, limited indexing) | `JSONB` (binary, GIN indexable) |
| Full-text search | `FULLTEXT INDEX` | `tsvector` generated column + GIN |
| Schema namespace | One DB = one namespace | Schemas inside a database (`CREATE SCHEMA app`) |
| Show tables | `SHOW TABLES` | `\dt` in psql, or `SELECT * FROM pg_catalog.pg_tables WHERE schemaname='public'` |

## Notes on each

Identity columns. `GENERATED ALWAYS AS IDENTITY` is the SQL-standard form, introduced in PostgreSQL 10. Prefer it over the legacy `SERIAL` macro (which is `INTEGER NOT NULL DEFAULT nextval(...)`). Source: postgresql.org/docs/current/ddl-identity-columns.html.

`RETURNING`. Available on `INSERT`, `UPDATE`, and `DELETE`. Removes the round-trip pattern from MySQL. Source: postgresql.org/docs/current/dml-returning.html.

`ON CONFLICT`. The conflict target must be a unique constraint or column list. Use `EXCLUDED.<col>` to refer to the row that would have been inserted. There is no implicit "any unique key" form like MySQL's `ON DUPLICATE KEY UPDATE`.

UTF-8. PostgreSQL stores text in the database encoding (typically `UTF8`). There is no `utf8mb4` distinction. Collation is per-column or per-database. `TEXT` and `VARCHAR(n)` perform identically; the length is just a check constraint.

ENUM and ARRAY. First-class but constrain refactoring. Adding values to an ENUM is fine (`ALTER TYPE ... ADD VALUE`), but renaming or removing values requires a controlled migration. Arrays are convenient for short lists but make joins awkward; prefer a child table when the array would have more than a handful of stable elements.

Schemas. PostgreSQL has a layer above tables that MySQL does not. A connection sees a `search_path` (default `"$user", public`). Use schemas to separate tenants only when you have a small, fixed number of tenants; otherwise use a `tenant_id` column.
