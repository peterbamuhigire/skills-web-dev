# Spatial Indexes

Without a spatial index, PostGIS degrades to a sequential scan. With the wrong one, you pay maintenance cost and gain nothing. Choose deliberately.

## Index types at a glance

| Index | Strengths | When to use |
| --- | --- | --- |
| GIST  | Balanced tree over bounding boxes, KNN support (`<->`) | Default for every spatial column |
| SP-GiST | Space-partitioning tree; good for non-overlapping point data | Rare; only when profiling says it wins |
| BRIN | Tiny, block-range summary | Very large append-only tables clustered by location |
| B-tree on geohash | Sortable string key | Low-tech alternative on systems without PostGIS |

If unsure, use GIST.

## GIST: the default

```sql
CREATE INDEX idx_listings_geom ON listings USING GIST (geom);
```

Properties:

- Supports `&&` (bbox overlap), `ST_Contains`, `ST_Within`, `ST_Intersects`, `ST_DWithin`, `<->` (KNN).
- Size: roughly 10-20% of the table; acceptable for most workloads.
- Insert/update cost: moderate. Heavy write workloads feel it.

Index the `::geography` cast if you query with `geom::geography`:

```sql
CREATE INDEX idx_listings_geog ON listings USING GIST ((geom::geography));
```

Otherwise, the geography query will do a seq scan even though `idx_listings_geom` exists.

## BRIN: tiny, for huge append-only tables

BRIN works when rows are physically clustered by the indexed column. Append-only GPS traces, telemetry, and time-series spatial data often cluster naturally.

```sql
CREATE INDEX idx_events_geom
  ON events USING BRIN (geom)
  WITH (pages_per_range = 32);
```

- Size: typically 1-2% of a GIST index.
- Selectivity: poor for random access; good for regional scans.
- Use alongside a GIST on a recent-slice partition if reads are bimodal.

Periodically run:

```sql
SELECT brin_summarize_new_values('idx_events_geom');
```

## SP-GiST

Useful for point-only tables where points do not overlap. Rarely a clear win over GIST in real workloads. Profile before switching.

```sql
CREATE INDEX idx_stops_geom ON stops USING SPGIST (geom);
```

## Composite patterns

Most SaaS queries filter by `tenant_id` first, then spatially. Two patterns:

```sql
-- Option A: separate indexes, let the planner combine via bitmap
CREATE INDEX idx_listings_tenant ON listings (tenant_id);
CREATE INDEX idx_listings_geom   ON listings USING GIST (geom);

-- Option B: GIST with tenant_id in INCLUDE for index-only scans
CREATE INDEX idx_listings_geom_tenant
  ON listings USING GIST (geom)
  INCLUDE (tenant_id);

-- Option C: partial index per hot tenant (rare)
CREATE INDEX idx_listings_geom_t42
  ON listings USING GIST (geom)
  WHERE tenant_id = 42;
```

Option A is the default. Option B helps when `tenant_id` scan in the heap dominates. Option C only for extreme tenant skew.

## ANALYZE and VACUUM

Spatial queries rely on the planner's selectivity estimate. After any bulk load:

```sql
ANALYZE listings;
```

Autovacuum handles day-to-day. For heavy update workloads:

```sql
ALTER TABLE listings SET (
  autovacuum_vacuum_scale_factor = 0.02,
  autovacuum_analyze_scale_factor = 0.01
);
```

Bloat check for GIST:

```sql
SELECT relname, pg_size_pretty(pg_relation_size(indexrelid)) AS idx_size
FROM pg_stat_user_indexes
JOIN pg_index USING (indexrelid)
WHERE indrelid = 'listings'::regclass;
```

Rebuild if bloated:

```sql
REINDEX INDEX CONCURRENTLY idx_listings_geom;
```

## CLUSTER for read locality

Physically re-order the heap by the index once, then rely on autovacuum to approximate the order over time:

```sql
CLUSTER listings USING idx_listings_geom;
ANALYZE listings;
```

Expensive; schedule for maintenance windows. Useful for read-heavy workloads where nearby geometries co-locate in the heap.

## Reading EXPLAIN ANALYZE

Run:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id FROM listings
WHERE ST_DWithin(geom::geography, ST_MakePoint(32.58, 0.34)::geography, 5000);
```

Look for:

- `Index Scan using idx_listings_geog` — GIST is used. Good.
- `Seq Scan on listings` — index ignored. Usually means:
  - SRID mismatch (`ST_SRID(query_point) != ST_SRID(geom)`).
  - Missing `::geography` index when the query casts.
  - Function wraps the column (`ST_Transform(geom, 32636)`) without an expression index.
  - Statistics stale — run `ANALYZE`.
- `Bitmap Heap Scan` with `Recheck Cond` — planner combined bbox filter + exact test. Expected for spatial predicates.
- `Rows Removed by Filter: large` — bbox prefilter is loose; consider `ST_DWithin` instead of `ST_Distance < x`.

## Expression indexes for transformed queries

If you always query in UTM 32636:

```sql
CREATE INDEX idx_listings_geom_32636
  ON listings USING GIST ((ST_Transform(geom, 32636)));
```

The query must use the exact expression to hit the index:

```sql
WHERE ST_DWithin(ST_Transform(geom, 32636), :point_utm, 5000)
```

Or add the generated column shown in `references/schema-srid-choice.md` and index that.

## Anti-patterns

- One GIST index but all queries cast to geography. Silent seq scan.
- `CREATE INDEX` without `USING GIST` on a geometry column. Creates a useless B-tree.
- Skipping `ANALYZE` after a bulk load; planner estimates 1 row and picks a bad plan.
- Wrapping the column in a function on every query and wondering why the index is idle.
- Rebuilding indexes during peak traffic. Use `REINDEX CONCURRENTLY`.

## Cross-reference

- `postgresql-performance` — generic planner, statistics, and EXPLAIN.
- `references/performance-patterns.md` — bbox pre-filter, partitioning, subdivide.
- `references/schema-srid-choice.md` — generated columns for projected SRIDs.
