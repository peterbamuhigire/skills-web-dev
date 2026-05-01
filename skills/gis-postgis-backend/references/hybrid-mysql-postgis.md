# Hybrid MySQL + PostGIS

Most of our SaaS apps run on MySQL. Adding PostGIS as a spatial sidecar is the common pattern. Design for eventual consistency; do not attempt distributed transactions.

## Topology

```text
 ┌───────────┐      writes       ┌───────────┐
 │  PHP app  │ ────────────────► │   MySQL   │  system of record
 └─────┬─────┘                   └─────┬─────┘
       │ reads spatial                 │ binlog / Debezium
       ▼                               ▼
 ┌───────────┐                   ┌───────────┐
 │ Tile /    │  SQL + MVT        │  PostGIS  │  spatial replica + analytics
 │ API svc   │ ◄──────────────── │           │
 └───────────┘                   └───────────┘
```

- MySQL owns transactional writes.
- PostGIS holds a denormalised, spatial-optimised copy.
- Spatial reads (within-radius, tiles, analytics) go to PostGIS.
- App reads that need a transactional guarantee still go to MySQL.

## Sync patterns

### 1. Debezium change data capture (recommended at scale)

Debezium reads the MySQL binary log and streams row-level changes to Kafka. A consumer upserts into PostGIS.

```json
// debezium mysql connector config
{
  "connector.class": "io.debezium.connector.mysql.MySqlConnector",
  "database.hostname": "mysql",
  "database.port": "3306",
  "database.user": "debezium",
  "database.password": "${env:DEBEZIUM_PASSWORD}",
  "database.server.id": "184054",
  "topic.prefix": "saas",
  "database.include.list": "app",
  "table.include.list": "app.listings,app.zones",
  "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
  "schema.history.internal.kafka.topic": "schemahistory.app"
}
```

Consumer (Node outline):

```javascript
consumer.on('message', async (m) => {
  const evt = JSON.parse(m.value);
  const after = evt.payload.after;
  if (!after) {
    await pg.query(`DELETE FROM listings WHERE id = $1`, [evt.payload.before.id]);
    return;
  }
  await pg.query(
    `INSERT INTO listings (id, tenant_id, title, lat, lng, geom)
     VALUES ($1,$2,$3,$4,$5, ST_SetSRID(ST_MakePoint($5,$4),4326))
     ON CONFLICT (id) DO UPDATE
       SET tenant_id = EXCLUDED.tenant_id,
           title     = EXCLUDED.title,
           lat       = EXCLUDED.lat,
           lng       = EXCLUDED.lng,
           geom      = EXCLUDED.geom`,
    [after.id, after.tenant_id, after.title, after.lat, after.lng]
  );
});
```

### 2. Trigger + outbox table (medium scale)

If Kafka is too much, write an outbox table in MySQL in the same transaction as the business write:

```sql
-- MySQL
CREATE TABLE spatial_outbox (
  id bigint AUTO_INCREMENT PRIMARY KEY,
  entity varchar(64) NOT NULL,
  entity_id bigint NOT NULL,
  op enum('upsert','delete') NOT NULL,
  payload json NOT NULL,
  created_at datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  processed_at datetime(3) NULL,
  INDEX (processed_at, id)
);
```

A worker polls unprocessed rows, applies them to PostGIS, then marks them processed. Idempotent upserts keyed by `entity_id`.

### 3. Nightly dump (small scale)

For datasets under ~100k rows that change infrequently, a nightly `mysqldump` + load script is enough. Wrap in a deterministic ETL:

```bash
mysql -e "SELECT id, tenant_id, lng, lat, title FROM app.listings" --batch > listings.tsv
psql -c "TRUNCATE staging_listings; \copy staging_listings FROM 'listings.tsv'"
psql -f promote_listings.sql   # upsert into listings with geom = ST_SetSRID(ST_MakePoint(lng,lat), 4326)
```

## Cross-database joins

Two safe patterns. Neither tries to JOIN across engines in a single query.

### Shared IDs

Keep MySQL as the ID authority. PostGIS rows carry the MySQL primary key. The app fetches IDs from PostGIS (spatial query) then reads rows from MySQL.

```text
1. PostGIS: SELECT id FROM listings WHERE ST_DWithin(...);
2. App:     SELECT * FROM app.listings WHERE id IN (...);
```

Cheap, correct, and avoids driver-level federation.

### Postgres FDW to MySQL (read-only)

`mysql_fdw` exposes MySQL tables in Postgres. Useful for joining a spatial result with a small MySQL lookup table.

```sql
CREATE EXTENSION mysql_fdw;
CREATE SERVER mysql_app FOREIGN DATA WRAPPER mysql_fdw OPTIONS (host 'mysql', port '3306');
CREATE USER MAPPING FOR CURRENT_USER SERVER mysql_app OPTIONS (username 'readonly', password '...');

CREATE FOREIGN TABLE mysql_tenants (
  id int, name text, plan text
) SERVER mysql_app OPTIONS (dbname 'app', table_name 'tenants');

-- Spatial + tenant info in one query
SELECT l.id, t.name
FROM listings l
JOIN mysql_tenants t ON t.id = l.tenant_id
WHERE ST_DWithin(l.geom::geography, :p::geography, 5000);
```

Treat FDW as read-only for operational reasons. Keep joins narrow; FDW pushes what it can but can surprise you on selectivity.

## Eventual consistency

- Lag budget: write to MySQL → visible in PostGIS. Target P95 under 30 seconds for app-driven sync; under 1 hour for nightly.
- Alert on lag. Track `MAX(mysql_updated_at) - MAX(postgis_updated_at)`.
- Read-your-writes guarantee: the UI must not rely on PostGIS for "did my save succeed". Show the MySQL write result; let the map refresh asynchronously.

## Conflict resolution

Source-of-truth is MySQL. PostGIS is derived. Conflicts resolve by re-running the sync for the affected entity.

- If a replay is needed: DELETE from PostGIS, re-emit from outbox or re-stream from binlog.
- Debezium snapshots can rebuild the whole replica.
- Version each entity with `updated_at` or a CDC log sequence number (LSN); last-write-wins by LSN.

## Schema drift

- Changes to MySQL columns do not automatically reach PostGIS. Add migration checklists that update both.
- Keep the spatial schema minimal: only columns needed for spatial queries or tile rendering. Everything else stays in MySQL and is fetched by ID.

## Failure modes and mitigations

| Failure | Mitigation |
| --- | --- |
| Consumer falls behind | Scale consumers; monitor Kafka lag; batch upserts |
| PostGIS down | Degrade to MySQL-only reads; disable map-heavy features with a flag |
| MySQL schema change breaks consumer | Contract tests on the change stream; canary consumer on staging |
| Duplicate events | Upserts keyed by primary key; idempotent by design |
| Out-of-order events | Compare LSN/`updated_at`; apply only if newer |

## Security

- Replication user on MySQL has `REPLICATION SLAVE, REPLICATION CLIENT, SELECT`. No writes.
- PostGIS has no direct network path from the public internet. Tile/API services in front.
- Tenant scoping re-enforced in PostGIS via RLS. Do not rely on the sync job to enforce isolation. See `references/tenant-isolation-rls.md`.

## Anti-patterns

- Two-phase commit across MySQL and PostGIS. Operationally painful, rarely needed.
- Making PostGIS the source of truth "just because it is newer". MySQL is the app DB; PostGIS is a derived replica.
- Syncing raw JSON columns without shape contracts; consumers break silently.
- Polling MySQL every second to populate PostGIS. Use CDC or an outbox.
- Skipping `ANALYZE` after bulk loads on the PostGIS side. Plans go bad fast.

## Cross-reference

- `references/backup-migration.md` — seeding PostGIS from a MySQL dump.
- `references/tenant-isolation-rls.md` — isolation on the spatial side.
- `distributed-systems-patterns` — eventual consistency, outbox, idempotency.
- `mysql-administration` — binlog configuration for CDC.
