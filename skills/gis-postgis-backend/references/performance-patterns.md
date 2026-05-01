# Performance Patterns

When spatial queries slow down, the fix is almost never "more hardware". It is usually bbox pre-filter, index-friendly predicates, subdivide, or materialised views.

## 1. Bounding-box pre-filter

GIST indexes work on bounding boxes. Predicates like `ST_Contains`, `ST_Intersects` already use bbox internally. Predicates like `ST_Distance` do not.

```sql
-- Slow: full scan, distance computed on every row
SELECT * FROM listings
WHERE ST_Distance(geom::geography, :p::geography) < 5000;

-- Fast: GIST-indexed bbox prefilter, then exact check
SELECT * FROM listings
WHERE ST_DWithin(geom::geography, :p::geography, 5000);
```

Same answer, 100x faster on 10M rows.

Explicit bbox when your predicate cannot use index:

```sql
SELECT l.id
FROM listings l
JOIN zones z ON z.id = :zone_id
WHERE l.geom && z.geom            -- bbox overlap via GIST
  AND ST_Contains(z.geom, l.geom); -- exact check on the bbox hits
```

## 2. Partitioning

Partition very large spatial tables by:

- **Date** for append-only telemetry:

```sql
CREATE TABLE events (
  id bigserial,
  occurred_at timestamptz NOT NULL,
  geom geometry(Point, 4326) NOT NULL
) PARTITION BY RANGE (occurred_at);

CREATE TABLE events_2026_q1 PARTITION OF events
  FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');

CREATE INDEX ON events_2026_q1 USING GIST (geom);
```

- **Tenant** for multi-tenant isolation at scale:

```sql
CREATE TABLE listings (
  id bigserial,
  tenant_id int NOT NULL,
  geom geometry(Point, 4326) NOT NULL
) PARTITION BY LIST (tenant_id);
```

Per-partition GIST indexes stay small and hot in the buffer cache.

## 3. ST_Subdivide for large polygons

A single 2 million-vertex country boundary ruins index selectivity. Split it:

```sql
CREATE MATERIALIZED VIEW zones_subdivided AS
SELECT id, ST_Subdivide(geom, 256) AS geom
FROM zones;

CREATE INDEX ON zones_subdivided USING GIST (geom);
```

Rewrite joins against the subdivided view:

```sql
SELECT DISTINCT l.id
FROM listings l
JOIN zones_subdivided z ON ST_Intersects(l.geom, z.geom)
WHERE z.id = :zone_id;
```

Tighter bboxes, many more rows, faster queries. Classic 10-100x speedup on country-scale polygons.

## 4. CLUSTER on GIST for read locality

Physical heap order by spatial proximity:

```sql
CLUSTER listings USING idx_listings_geom;
ANALYZE listings;
```

- Run in maintenance windows; it rewrites the table.
- After cluster, nearby rows share buffer pages. Range scans read fewer pages.
- Re-cluster periodically if the heap drifts.

## 5. Materialised views for expensive shapes

Anything that takes seconds to compute and changes rarely goes in a materialised view:

```sql
CREATE MATERIALIZED VIEW tenant_service_areas AS
SELECT tenant_id,
       ST_Union(ST_Buffer(geom::geography, 1000)::geometry) AS geom
FROM shops
GROUP BY tenant_id;

CREATE INDEX ON tenant_service_areas USING GIST (geom);

-- Refresh nightly or on-demand
REFRESH MATERIALIZED VIEW CONCURRENTLY tenant_service_areas;
```

`CONCURRENTLY` requires a unique index on the view.

## 6. Connection pool sizing

Spatial queries are CPU-heavy. A pool 2-4x core count is normal; more than that queues.

```text
pool_size = cpu_cores * 2 to 4
max_connections (Postgres) = pool_size * app_instances + admin headroom
```

Use PgBouncer in transaction mode in front. Spatial queries rarely hold long transactions; transaction pooling is safe unless you use session-state features (advisory locks, `SET LOCAL` outside functions).

## 7. Index-friendly function wrapping

Wrapping the column in a function disables the index:

```sql
-- Bad: function on column
WHERE ST_Buffer(geom, 0.001) && :poly

-- Good: function on literal, or pre-buffer :poly in the app
WHERE geom && ST_Buffer(:poly, 0.001)
```

For transformed queries, use a generated column or expression index (see `references/schema-srid-choice.md`).

## 8. LIMIT + ORDER BY `<->` instead of OFFSET pagination

Geographic pagination by offset is unstable. Use a cursor:

```sql
SELECT id, name, geom
FROM listings
WHERE tenant_id = :tenant_id
  AND (id > :cursor_id)
ORDER BY geom <-> :point, id
LIMIT 25;
```

Combine with `WHERE ST_DWithin(...)` to cap the search radius.

## 9. Cache at the edge

MVT tiles are ideal cache candidates: immutable per `(z, x, y, tenant, layer, version)`. Put a CDN in front and invalidate by layer version. See `references/mvt-tiles.md`.

## 10. Work-memory tuning

Spatial joins and `ST_Union` benefit from higher `work_mem`:

```sql
SET LOCAL work_mem = '256MB';
SELECT ST_Union(geom) FROM large_polygons WHERE tenant_id = :t;
```

Set per session or per role, not globally. Global bumps eat RAM when every query grabs its share.

## 11. Parallel query

PostGIS functions are parallel-safe in recent versions. Verify:

```sql
SELECT proname, proparallel
FROM pg_proc
WHERE proname LIKE 'st\_%'
LIMIT 20;
```

Encourage parallelism:

```sql
SET max_parallel_workers_per_gather = 4;
```

Confirm via `EXPLAIN` that `Gather` or `Parallel Seq Scan` appears on large queries.

## 12. Common slow-query diagnosis

```text
Symptom                             Likely cause                         Fix
---------------------------------   ----------------------------------   ------------------
Seq Scan despite GIST index         SRID mismatch or function on col     Align SRIDs; expression index
ST_Distance < N very slow           No bbox prefilter                    Use ST_DWithin
ST_Union explodes memory            Too many input geometries            ST_Subdivide; partition; batch
KNN slow without LIMIT              No LIMIT makes <-> pointless         Add LIMIT
Tile requests slow at high zoom     No simplification                    ST_SimplifyPreserveTopology per zoom
Tenant-scoped query scans all rows  tenant_id filter lost                Add index and/or RLS check
```

## Cross-reference

- `postgresql-performance` — general query tuning, planner stats, buffer pool.
- `references/spatial-indexes.md` — index selection and EXPLAIN reading.
- `references/mvt-tiles.md` — tile caching and simplification per zoom.
- `references/tenant-isolation-rls.md` — RLS interacts with plan cache.
