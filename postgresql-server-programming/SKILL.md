---
name: postgresql-server-programming
description: PostgreSQL server-side programming sourced from "PostgreSQL Server Programming"
  (Usama Dar, Packt) and "Introduction to PostgreSQL for the Data Professional". Covers
  PL/pgSQL functions and procedures (structure, variables, error handling, loops,
  cursors), trigger functions (row-level, statement-level, WHEN conditions), event
  triggers (DDL auditing), extensions (creating and publishing), and best practices
  (SOA, DRY, KISS). Companion to postgresql-fundamentals and postgresql-advanced-sql.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostgreSQL Server Programming

<!-- dual-compat-start -->
## Use When

- PostgreSQL server-side programming sourced from "PostgreSQL Server Programming" (Usama Dar, Packt) and "Introduction to PostgreSQL for the Data Professional". Covers PL/pgSQL functions and procedures (structure, variables, error handling, loops, cursors), trigger functions (row-level, statement-level, WHEN conditions), event triggers (DDL auditing), extensions (creating and publishing), and best practices (SOA, DRY, KISS). Companion to postgresql-fundamentals and postgresql-advanced-sql.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `postgresql-server-programming` or would be better handled by a more specific companion skill.
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
## Why Program in the Server

- **Data locality** — avoid network round trips for complex logic
- **Integrity enforcement** — triggers fire regardless of which client writes
- **Security** — grant EXECUTE on functions, deny direct table access
- **Performance** — reduce per-row round trips in batch operations
- **Auditability** — triggers capture changes transparently

Use server-side code for integrity, auditing, and data-local transformation. Keep business logic that requires application context in the application layer.

## PL/pgSQL Function Structure

```sql
CREATE OR REPLACE FUNCTION function_name(param1 type, param2 type)
RETURNS return_type
LANGUAGE plpgsql
AS $$
DECLARE
    var1  data_type := initial_value;
    var2  data_type;
    rec   RECORD;
BEGIN
    -- body
    RETURN result;
END;
$$;
```

### Volatility Categories

| Category | Description | Optimiser Benefit |
|---|---|---|
| `IMMUTABLE` | Same input always gives same output, no DB access | Most aggressive inlining |
| `STABLE` | Same input gives same output within a transaction | Safe for index scans |
| `VOLATILE` (default) | Can return different results or modify data | No optimisation |

```sql
-- Immutable: pure computation
CREATE FUNCTION slugify(text) RETURNS text LANGUAGE sql IMMUTABLE AS $$
    SELECT lower(regexp_replace(regexp_replace($1, '[^a-zA-Z0-9\s-]', '', 'g'), '\s+', '-', 'g'));
$$;

-- Stable: reads DB but doesn't modify it
CREATE FUNCTION get_exchange_rate(currency text) RETURNS numeric LANGUAGE sql STABLE AS $$
    SELECT rate FROM exchange_rates WHERE code = currency;
$$;
```

## Variables and Data Types

```sql
CREATE FUNCTION demo_variables() RETURNS void LANGUAGE plpgsql AS $$
DECLARE
    user_count  INT := 0;
    user_email  TEXT;
    order_rec   RECORD;
    order_row   orders%ROWTYPE;       -- same shape as a table row
    col_val     orders.total%TYPE;    -- same type as a specific column
    result_set  REFCURSOR;
BEGIN
    -- Assignment
    user_count := 42;
    SELECT email INTO user_email FROM users LIMIT 1;

    -- Implicit: SELECT INTO
    SELECT * INTO order_row FROM orders WHERE id = 1;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Order not found';
    END IF;
END;
$$;
```

## Control Flow

### IF / CASE

```sql
CREATE FUNCTION classify_order(amount numeric) RETURNS text LANGUAGE plpgsql AS $$
BEGIN
    IF amount >= 1000 THEN
        RETURN 'large';
    ELSIF amount >= 100 THEN
        RETURN 'medium';
    ELSE
        RETURN 'small';
    END IF;
END;
$$;

-- Searched CASE in PL/pgSQL
CASE
    WHEN score >= 90 THEN grade := 'A';
    WHEN score >= 80 THEN grade := 'B';
    ELSE grade := 'F';
END CASE;
```

### Loops

```sql
-- LOOP (explicit exit)
LOOP
    EXIT WHEN counter > 10;
    counter := counter + 1;
END LOOP;

-- FOR (integer range)
FOR i IN 1..10 LOOP
    RAISE NOTICE 'i = %', i;
END LOOP;

-- FOR (reverse)
FOR i IN REVERSE 10..1 LOOP ... END LOOP;

-- FOR (query results)
FOR rec IN SELECT id, email FROM users WHERE active LOOP
    RAISE NOTICE 'User: % %', rec.id, rec.email;
END LOOP;

-- WHILE
WHILE condition LOOP ... END LOOP;

-- FOREACH (array)
FOREACH item IN ARRAY tag_array LOOP
    INSERT INTO tag_log(tag) VALUES (item);
END LOOP;
```

## Error Handling

```sql
CREATE FUNCTION safe_insert(p_email text) RETURNS boolean LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO users(email) VALUES (p_email);
    RETURN true;
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE 'Duplicate email: %', p_email;
        RETURN false;
    WHEN not_null_violation THEN
        RAISE EXCEPTION 'Email cannot be null';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Unexpected error: % %', SQLSTATE, SQLERRM;
END;
$$;
```

### RAISE Levels

```sql
RAISE DEBUG   'Debug: %', value;      -- visible at log_min_messages = debug
RAISE INFO    'Info: %', value;       -- always visible to client
RAISE NOTICE  'Notice: %', value;     -- client notice
RAISE WARNING 'Warning: %', value;    -- client warning
RAISE EXCEPTION 'Error: %', value;   -- raises error, rolls back
RAISE EXCEPTION 'Custom error' USING ERRCODE = 'P0001';
```

## Returning Structured Data

### Return a Single Row

```sql
CREATE FUNCTION get_user(p_id bigint)
RETURNS TABLE(id bigint, email text, created_at timestamptz)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT u.id, u.email, u.created_at FROM users u WHERE u.id = p_id;
END;
$$;
```

### Return a Set

```sql
CREATE FUNCTION active_users_by_country(p_country text)
RETURNS SETOF users
LANGUAGE sql STABLE AS $$
    SELECT * FROM users WHERE country = p_country AND active = true;
$$;

-- Usage
SELECT * FROM active_users_by_country('UG');
```

### OUT Parameters

```sql
CREATE FUNCTION get_stats(
    OUT user_count   bigint,
    OUT order_count  bigint,
    OUT revenue      numeric
) LANGUAGE plpgsql AS $$
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*), SUM(total) INTO order_count, revenue FROM orders;
END;
$$;

SELECT * FROM get_stats();
```

## Stored Procedures

Procedures (PostgreSQL 11+) can manage transactions — functions cannot.

```sql
CREATE PROCEDURE process_batch(p_batch_size int)
LANGUAGE plpgsql AS $$
DECLARE
    processed int := 0;
BEGIN
    LOOP
        UPDATE jobs SET status = 'processing', started_at = NOW()
        WHERE id IN (
            SELECT id FROM jobs WHERE status = 'pending'
            ORDER BY created_at LIMIT p_batch_size
            FOR UPDATE SKIP LOCKED
        );

        EXIT WHEN NOT FOUND;

        COMMIT;   -- commit each batch (only valid in procedures)
        processed := processed + p_batch_size;
        RAISE NOTICE 'Processed %', processed;
    END LOOP;
END;
$$;

-- Call a procedure
CALL process_batch(100);
```

## Trigger Functions

### Row-Level Trigger

```sql
-- Trigger function must return TRIGGER
CREATE FUNCTION set_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;   -- RETURN NEW to keep the modified row; RETURN NULL to cancel
END;
$$;

CREATE TRIGGER orders_updated_at
    BEFORE INSERT OR UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

### Audit Trigger

```sql
CREATE TABLE audit_log (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name  TEXT,
    operation   TEXT,
    old_row     JSONB,
    new_row     JSONB,
    changed_by  TEXT DEFAULT current_user,
    changed_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE FUNCTION audit_trigger() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO audit_log(table_name, operation, old_row, new_row)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD)::jsonb ELSE NULL END,
        CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW)::jsonb ELSE NULL END
    );

    IF TG_OP = 'DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
END;
$$;

CREATE TRIGGER orders_audit
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

### Conditional Trigger (WHEN clause)

```sql
-- Only fire when status actually changes
CREATE TRIGGER orders_status_change
    AFTER UPDATE ON orders
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION notify_status_change();
```

### Statement-Level Trigger

```sql
-- Fires once per statement, not per row
CREATE TRIGGER after_bulk_import
    AFTER INSERT ON staging_data
    FOR EACH STATEMENT EXECUTE FUNCTION refresh_summary_table();
```

### Special Trigger Variables

| Variable | Type | Description |
|---|---|---|
| `NEW` | RECORD | New row (INSERT/UPDATE) |
| `OLD` | RECORD | Old row (UPDATE/DELETE) |
| `TG_OP` | TEXT | `'INSERT'`, `'UPDATE'`, `'DELETE'`, `'TRUNCATE'` |
| `TG_TABLE_NAME` | TEXT | Table name |
| `TG_WHEN` | TEXT | `'BEFORE'` or `'AFTER'` |
| `TG_LEVEL` | TEXT | `'ROW'` or `'STATEMENT'` |

## Event Triggers (DDL Auditing)

Event triggers fire on DDL events (CREATE, ALTER, DROP) rather than DML.

```sql
CREATE TABLE ddl_log (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event      TEXT,
    tag        TEXT,
    object     TEXT,
    executed_by TEXT DEFAULT current_user,
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE FUNCTION log_ddl_event() RETURNS event_trigger LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO ddl_log(event, tag)
    VALUES (TG_EVENT, TG_TAG);
END;
$$;

CREATE EVENT TRIGGER ddl_logger ON ddl_command_end
    EXECUTE FUNCTION log_ddl_event();
```

## Cursors

Cursors process large result sets row-by-row without loading all into memory.

```sql
CREATE PROCEDURE migrate_users() LANGUAGE plpgsql AS $$
DECLARE
    cur CURSOR FOR SELECT id, email FROM users WHERE migrated = false;
    rec RECORD;
BEGIN
    OPEN cur;
    LOOP
        FETCH cur INTO rec;
        EXIT WHEN NOT FOUND;

        UPDATE users SET migrated = true WHERE id = rec.id;

        -- Commit every 1000 rows
        IF MOD(rec.id, 1000) = 0 THEN COMMIT; END IF;
    END LOOP;
    CLOSE cur;
END;
$$;
```

## Extensions

### Using Key Extensions

```sql
-- pg_crypto: hashing and encryption
CREATE EXTENSION pgcrypto;
SELECT crypt('my_password', gen_salt('bf'));          -- bcrypt hash
SELECT encode(digest('data', 'sha256'), 'hex');       -- SHA-256

-- pg_cron: scheduled jobs (requires superuser)
CREATE EXTENSION pg_cron;
SELECT cron.schedule('nightly-vacuum', '0 2 * * *', 'VACUUM ANALYZE orders');
SELECT cron.schedule('hourly-refresh', '0 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_stats');
SELECT * FROM cron.job;   -- list scheduled jobs
SELECT cron.unschedule('nightly-vacuum');

-- postgres_fdw: query remote PostgreSQL databases
CREATE EXTENSION postgres_fdw;
CREATE SERVER remote_db FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'remote.host', port '5432', dbname 'analytics');
CREATE USER MAPPING FOR current_user SERVER remote_db
    OPTIONS (user 'fdw_user', password 'secret');
CREATE FOREIGN TABLE remote_events (
    id bigint, event_type text, created_at timestamptz
) SERVER remote_db OPTIONS (schema_name 'public', table_name 'events');
```

### Creating an Extension

```sql
-- myext.control
comment = 'My custom extension'
default_version = '1.0'
relocatable = true

-- myext--1.0.sql
\echo Use "CREATE EXTENSION myext" to load this file. \quit

CREATE FUNCTION myext_version() RETURNS text LANGUAGE sql AS $$ SELECT '1.0'::text $$;

-- Install
CREATE EXTENSION myext;
```

## Programming Best Practices

### KISS — Keep It Simple

Write the simplest function that solves the problem. Avoid premature abstraction inside PL/pgSQL.

### DRY — Don't Repeat Yourself

Extract shared logic into helper functions rather than duplicating WHERE clauses or transformation logic across multiple triggers.

### SOA — Service-Oriented

Group functions by domain. Grant EXECUTE on function groups to roles, deny direct table DML. Applications call functions, not tables.

```sql
-- Application role: no table access, only function access
GRANT EXECUTE ON FUNCTION place_order(bigint, jsonb) TO app_role;
GRANT EXECUTE ON FUNCTION cancel_order(bigint, text) TO app_role;
REVOKE ALL ON TABLE orders FROM app_role;
```

### Security Definer

```sql
-- Runs with the owner's privileges, not the caller's
CREATE FUNCTION admin_only_stats() RETURNS TABLE(count bigint)
LANGUAGE sql SECURITY DEFINER AS $$
    SELECT COUNT(*) FROM audit_log;
$$;

-- Always set search_path in security definer functions
ALTER FUNCTION admin_only_stats() SET search_path = public;
```

## Anti-Patterns

- Using SECURITY DEFINER without setting `search_path` — search path injection
- Trigger that queries the same table it fires on — infinite recursion
- Functions with `VOLATILE` that only read data — prevents planner optimisation
- Raising `EXCEPTION` for flow control instead of business errors
- Missing `RETURN NEW`/`RETURN OLD` in trigger functions — silently drops rows
- Large cursors without periodic `COMMIT` in procedures — transaction bloat
- Event triggers in production without testing DDL rollback behaviour
