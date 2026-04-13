---
name: postgresql-advanced-sql
description: Advanced PostgreSQL SQL patterns sourced from "Mastering PostgreSQL"
  (Supabase/Manning) and "Introduction to PostgreSQL for the Data Professional". Covers
  modern SQL (CTEs, recursive queries, window functions), JSONB operators, array operations,
  full-text search (tsvector/tsquery, GIN indexes, ranking), LATERAL joins, and anonymous
  code blocks. Companion to postgresql-fundamentals and postgresql-performance.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostgreSQL Advanced SQL

<!-- dual-compat-start -->
## Use When

- Advanced PostgreSQL SQL patterns sourced from "Mastering PostgreSQL" (Supabase/Manning) and "Introduction to PostgreSQL for the Data Professional". Covers modern SQL (CTEs, recursive queries, window functions), JSONB operators, array operations, full-text search (tsvector/tsquery, GIN indexes, ranking), LATERAL joins, and anonymous code blocks. Companion to postgresql-fundamentals and postgresql-performance.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `postgresql-advanced-sql` or would be better handled by a more specific companion skill.
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
## Common Table Expressions (CTEs)

CTEs name a subquery for reuse within a single statement. Use them for readability and to avoid repeating complex subqueries.

```sql
-- Basic CTE
WITH active_orders AS (
    SELECT id, customer_id, total, created_at
    FROM orders
    WHERE status NOT IN ('cancelled', 'refunded')
),
customer_totals AS (
    SELECT customer_id, SUM(total) AS lifetime_value
    FROM active_orders
    GROUP BY customer_id
)
SELECT c.email, ct.lifetime_value
FROM customers c
JOIN customer_totals ct ON ct.customer_id = c.id
ORDER BY ct.lifetime_value DESC;
```

### Writable CTEs (Data-Modifying)

```sql
-- Move rows atomically: delete from one table, insert into another
WITH deleted AS (
    DELETE FROM staging_orders
    WHERE created_at < NOW() - INTERVAL '7 days'
    RETURNING *
)
INSERT INTO archive_orders SELECT * FROM deleted;
```

### Materialised vs Inline CTEs

```sql
-- Force materialisation (PostgreSQL 12+) — evaluate once, cache result
WITH MATERIALIZED expensive_query AS (
    SELECT ... FROM large_table WHERE complex_condition
)
SELECT * FROM expensive_query WHERE ...;

-- Default: planner decides inline vs materialised
WITH sales AS ( SELECT ... ) SELECT * FROM sales;
```

## Recursive Queries

Recursive CTEs model hierarchies (org charts, category trees, bill of materials).

```sql
-- Org chart: find all reports under a manager
WITH RECURSIVE reports AS (
    -- Anchor: start with the manager
    SELECT id, name, manager_id, 0 AS depth
    FROM employees
    WHERE id = 42

    UNION ALL

    -- Recursive: employees whose manager_id is in prior results
    SELECT e.id, e.name, e.manager_id, r.depth + 1
    FROM employees e
    JOIN reports r ON e.manager_id = r.id
)
SELECT id, name, depth
FROM reports
ORDER BY depth, name;
```

```sql
-- Category tree: full path
WITH RECURSIVE category_path AS (
    SELECT id, name, parent_id, name::TEXT AS path
    FROM categories WHERE parent_id IS NULL

    UNION ALL

    SELECT c.id, c.name, c.parent_id, cp.path || ' > ' || c.name
    FROM categories c
    JOIN category_path cp ON c.parent_id = cp.id
)
SELECT id, path FROM category_path ORDER BY path;
```

## Window Functions

Window functions compute across a set of rows related to the current row without collapsing them (unlike GROUP BY).

```sql
-- Syntax
function_name(args) OVER (
    [PARTITION BY column]
    [ORDER BY column]
    [ROWS/RANGE BETWEEN ...]
)
```

### Ranking

```sql
SELECT
    employee_id,
    department_id,
    salary,
    RANK()        OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank,
    DENSE_RANK()  OVER (PARTITION BY department_id ORDER BY salary DESC) AS dense_rank,
    ROW_NUMBER()  OVER (PARTITION BY department_id ORDER BY salary DESC) AS row_num,
    NTILE(4)      OVER (ORDER BY salary DESC) AS quartile
FROM employees;
```

### Aggregate Windows

```sql
SELECT
    order_id,
    customer_id,
    amount,
    SUM(amount)   OVER (PARTITION BY customer_id ORDER BY created_at) AS running_total,
    AVG(amount)   OVER (PARTITION BY customer_id) AS customer_avg,
    COUNT(*)      OVER (PARTITION BY customer_id) AS order_count,
    -- 7-day moving average
    AVG(amount)   OVER (
        PARTITION BY customer_id
        ORDER BY created_at
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM orders;
```

### Lead/Lag — Access Adjacent Rows

```sql
SELECT
    month,
    revenue,
    LAG(revenue, 1)  OVER (ORDER BY month) AS prev_month_revenue,
    LEAD(revenue, 1) OVER (ORDER BY month) AS next_month_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY month) AS month_delta
FROM monthly_revenue;
```

### First/Last Value

```sql
SELECT
    product_id,
    sale_date,
    price,
    FIRST_VALUE(price) OVER (PARTITION BY product_id ORDER BY sale_date) AS original_price,
    LAST_VALUE(price)  OVER (
        PARTITION BY product_id
        ORDER BY sale_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS latest_price
FROM price_history;
```

## LATERAL Joins

LATERAL allows a subquery on the right side to reference columns from the left side — like a correlated subquery in a FROM clause.

```sql
-- Get the 3 most recent orders per customer
SELECT c.id, c.email, o.id AS order_id, o.total, o.created_at
FROM customers c
CROSS JOIN LATERAL (
    SELECT id, total, created_at
    FROM orders
    WHERE customer_id = c.id
    ORDER BY created_at DESC
    LIMIT 3
) o;
```

```sql
-- Function producing rows per input row
SELECT u.id, stats.*
FROM users u
CROSS JOIN LATERAL get_user_stats(u.id) AS stats;
```

## JSONB Operations

```sql
-- Operators
payload->>'key'          -- extract as text
payload->'key'           -- extract as jsonb
payload#>>'{a,b}'        -- nested path as text
payload @> '{"key":"val"}' -- contains
payload ? 'key'          -- key exists
payload ?| ARRAY['a','b']  -- any key exists
payload ?& ARRAY['a','b']  -- all keys exist

-- Update: merge (PostgreSQL 16+)
UPDATE configs
SET payload = payload || '{"theme": "light"}'::jsonb
WHERE id = 1;

-- Update: remove key
UPDATE configs
SET payload = payload - 'deprecated_key'
WHERE id = 1;

-- Expand to rows
SELECT key, value
FROM configs, jsonb_each_text(configs.payload);

-- Aggregate to JSON
SELECT jsonb_agg(row_to_json(u)) FROM users u WHERE active;
SELECT jsonb_object_agg(id, name) FROM categories;
```

### JSONB Index Types

```sql
-- GIN for @>, ?, ?|, ?& operators (containment/existence)
CREATE INDEX configs_payload_gin ON configs USING GIN (payload);

-- GIN with jsonb_path_ops (smaller, only for @>)
CREATE INDEX configs_payload_path ON configs USING GIN (payload jsonb_path_ops);

-- B-tree on extracted value (for = and ORDER BY)
CREATE INDEX configs_theme ON configs ((payload->>'theme'));
```

## Array Operations

```sql
-- Operators
ARRAY['a','b'] @> ARRAY['a']     -- contains
ARRAY['a','b'] <@ ARRAY['a','c'] -- is contained by
ARRAY['a','b'] && ARRAY['b','c'] -- overlap (any common)

-- Functions
array_length(tags, 1)             -- length of dimension 1
array_append(tags, 'new')         -- append element
array_remove(tags, 'old')         -- remove all occurrences
array_to_string(tags, ',')        -- join to string
string_to_array('a,b,c', ',')     -- split to array
unnest(tags)                      -- expand to rows
array_agg(name ORDER BY name)     -- aggregate to array

-- Index for array operators
CREATE INDEX products_tags_gin ON products USING GIN (tags);
```

## Full-Text Search

### Basic Setup

```sql
-- tsvector: pre-processed document
-- tsquery: search query

-- On-the-fly (not recommended for large tables)
SELECT title FROM articles
WHERE to_tsvector('english', title || ' ' || body) @@ to_tsquery('english', 'PostgreSQL & performance');

-- Stored tsvector column (recommended)
ALTER TABLE articles ADD COLUMN search_vector tsvector;

UPDATE articles
SET search_vector = to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body,''));

-- Auto-update with trigger
CREATE FUNCTION articles_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', coalesce(NEW.title,'') || ' ' || coalesce(NEW.body,''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER articles_search_update
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION articles_search_trigger();

-- GIN index (required for performance)
CREATE INDEX articles_search_gin ON articles USING GIN (search_vector);
```

### Search Query Syntax

```sql
-- Basic search
SELECT title FROM articles
WHERE search_vector @@ to_tsquery('english', 'PostgreSQL');

-- AND
to_tsquery('english', 'PostgreSQL & performance')

-- OR
to_tsquery('english', 'PostgreSQL | MySQL')

-- NOT
to_tsquery('english', 'PostgreSQL & !MySQL')

-- Phrase (proximity)
to_tsquery('english', 'PostgreSQL <-> performance')   -- adjacent
to_tsquery('english', 'PostgreSQL <2> tuning')        -- within 2 words

-- Prefix search (autocomplete)
to_tsquery('english', 'Postgre:*')

-- plainto_tsquery: natural language input, no operators
WHERE search_vector @@ plainto_tsquery('english', 'postgres full text search')

-- websearch_to_tsquery: Google-style (PostgreSQL 11+)
WHERE search_vector @@ websearch_to_tsquery('english', '"full text" postgres -mysql')
```

### Ranking Results

```sql
SELECT
    title,
    ts_rank(search_vector, query)          AS rank,
    ts_rank_cd(search_vector, query, 32)   AS rank_cover_density
FROM articles, to_tsquery('english', 'PostgreSQL & performance') query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;
```

### Highlighting Matches

```sql
SELECT
    title,
    ts_headline('english', body, to_tsquery('english', 'PostgreSQL'),
        'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=20'
    ) AS excerpt
FROM articles
WHERE search_vector @@ to_tsquery('english', 'PostgreSQL');
```

### Trigram Fuzzy Search (pg_trgm)

For typo-tolerant search and LIKE/ILIKE acceleration:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Index
CREATE INDEX users_email_trgm ON users USING GIN (email gin_trgm_ops);

-- Fuzzy similarity
SELECT email, similarity(email, 'john@example.com') AS sim
FROM users
WHERE email % 'john@example.com'    -- similarity > threshold (default 0.3)
ORDER BY sim DESC;

-- Accelerate LIKE/ILIKE
SELECT * FROM products WHERE name ILIKE '%coffee%';  -- uses trgm index
```

## Anonymous Code Blocks (DO)

```sql
DO $$
DECLARE
    counter INT := 0;
    rec     RECORD;
BEGIN
    FOR rec IN SELECT id FROM users WHERE migrated = false LOOP
        UPDATE users SET migrated = true WHERE id = rec.id;
        counter := counter + 1;
    END LOOP;
    RAISE NOTICE 'Migrated % users', counter;
END $$;
```

## Useful Utility Queries

```sql
-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) AS total
FROM pg_class WHERE relkind = 'r' ORDER BY pg_total_relation_size(oid) DESC LIMIT 20;

-- Index usage
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes ORDER BY idx_scan;

-- Long-running queries
SELECT pid, age(clock_timestamp(), query_start), usename, query
FROM pg_stat_activity
WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%'
ORDER BY query_start;

-- Duplicate rows
SELECT col1, col2, COUNT(*) FROM table GROUP BY col1, col2 HAVING COUNT(*) > 1;

-- Generate series
SELECT generate_series('2026-01-01'::date, '2026-12-31'::date, '1 month'::interval) AS month;
```

## Anti-Patterns

- `SELECT *` in CTEs with large tables — materialisation pulls all columns
- Recursive CTE without depth limit — add `WHERE depth < 100` guard
- `to_tsvector()` in WHERE without a GIN index — full sequential scan
- Using `LIKE '%term%'` without pg_trgm index — sequential scan
- Missing `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` for `LAST_VALUE` — returns wrong result
- Extracting JSONB value in WHERE without functional index — full scan
