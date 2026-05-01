# Growth Analytics Schema (OLTP vs OLAP Separation)

Source: Okonkwo, *Growth Engineering* (Wiley, 2025), Chapter 4.

## The rule

Never use one data model for both the product and growth analytics. OLTP tables (normalised, FK-enforced, unique-constrained) power the product. OLAP tables (denormalised star schema with fact and dimension tables) power growth analysis. Attempting to run analytics queries against the OLTP model either slows the product, corrupts analytics with transactional constraints, or both.

| Concern | OLTP (product) | OLAP (growth) |
|---|---|---|
| Purpose | transactional reads/writes | analytical scans and aggregates |
| Normalisation | 3NF, foreign keys enforced | denormalised, foreign keys not enforced |
| Row count | bounded by active users | unbounded, append-only |
| Write pattern | high-concurrency, short transactions | batched, typically from ETL |
| Indexing | B-tree on hot lookup columns | columnar store or wide composite indexes |
| Retention | indefinite (with archival) | hot tier 90 days, cold tier 2+ years |
| Consistency | strong, single-row | eventual, arrival-order-tolerant |

## Worked example

Consider a product with a home screen showing cards users can click.

### OLTP side (product)

```sql
CREATE TABLE users (
  user_id       BIGINT PRIMARY KEY,
  email         VARCHAR(255) NOT NULL UNIQUE,
  created_at    DATETIME NOT NULL
);

CREATE TABLE cards (
  card_id       BIGINT PRIMARY KEY,
  title         VARCHAR(255) NOT NULL,
  created_at    DATETIME NOT NULL
);
```

Product queries: "load this user's home cards", "update card content". Simple, narrow, FK-enforced.

### OLAP side (growth)

Evolve in three steps:

**Step 1 — atomic event table.** Append-only.

```sql
CREATE TABLE card_click_events (
  event_id          BIGINT PRIMARY KEY,
  user_id           BIGINT NOT NULL,
  card_id           BIGINT NOT NULL,
  event_timestamp   TIMESTAMP NOT NULL,
  session_id        VARCHAR(64) NOT NULL,
  device_type       VARCHAR(32),
  locale            VARCHAR(16)
);
```

No foreign keys. Denormalised `device_type` and `locale` so dashboards do not require joins. Late-arriving events do not break.

**Step 2 — experiment assignments table.**

```sql
CREATE TABLE experiment_assignments (
  assignment_id     BIGINT PRIMARY KEY,
  experiment_id     VARCHAR(64) NOT NULL,
  user_id           BIGINT NOT NULL,
  variant           VARCHAR(32) NOT NULL,
  assigned_at       TIMESTAMP NOT NULL,
  trigger_event_id  BIGINT
);
```

This is the join key that connects events to experiments. Without it, you cannot slice any metric by variant.

**Step 3 — fact and dimension tables (star schema).**

```sql
CREATE TABLE card_clicks_fact (
  event_date        DATE NOT NULL,
  user_id           BIGINT NOT NULL,
  card_id           BIGINT NOT NULL,
  experiment_id     VARCHAR(64),
  variant           VARCHAR(32),
  click_count       INT NOT NULL,
  KEY (event_date, user_id),
  KEY (experiment_id, variant)
);

CREATE TABLE dim_user (
  user_id           BIGINT PRIMARY KEY,
  signup_date       DATE NOT NULL,
  acquisition_channel VARCHAR(64),
  country           VARCHAR(64),
  plan_tier         VARCHAR(32)
);

CREATE TABLE dim_card (
  card_id           BIGINT PRIMARY KEY,
  title             VARCHAR(255),
  card_type         VARCHAR(32),
  first_published_at DATE
);

CREATE TABLE dim_date (
  date_key          DATE PRIMARY KEY,
  day_of_week       VARCHAR(16),
  week              INT,
  month             INT,
  year              INT,
  is_holiday        BOOLEAN
);
```

Now a single query produces a cohort retention table by experiment variant, acquisition channel, and country in one scan.

## Integrity rules (non-negotiable)

- Unique user IDs: the same person assigned the same ID across all sessions; no collision with anonymous IDs after login stitching.
- Typed timestamps: never store as strings. Use `TIMESTAMP` with explicit timezone (UTC).
- Schema registry: breaking changes to event shape require a new event name, not a silent mutation.
- Null identifier rate: monitor; a spike means tracking is broken upstream.

Silent data corruption is the failure mode. A single column-type change or an identifier collision can invalidate months of analysis before anyone notices.

## Anti-patterns

- Running growth analytics queries against production OLTP replicas (locks, contention, slow dashboards, stale product reads)
- One monolithic `events` table with a JSON blob for properties (no column pruning, no statistics, slow scans)
- Foreign keys on the OLAP event table (late-arriving events fail to insert)
- Deriving experiment variant by re-computing assignment from code in the query (non-deterministic; always store the assignment)
- Hot-schema aggregation tables updated synchronously from the product write path (couples analytics pipeline failure to product writes)

## See also

- `skills/growth-telemetry-pipeline/SKILL.md` — the 5-stage pipeline that feeds this model.
- `skills/experiment-engineering/SKILL.md` — why the assignment table is non-negotiable.
- `skills/database-design-engineering/SKILL.md` — general schema shape, tenancy, and indexing.
