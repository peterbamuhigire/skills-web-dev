---
name: gis-postgis-backend
description: Use when building server-side spatial features — PostGIS schema design,
  SRID choice, spatial indexes, core spatial SQL, MVT tile generation, geocoding,
  hybrid MySQL+PostGIS, tenant isolation via RLS.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostGIS Spatial Backend

<!-- dual-compat-start -->
## Use When

- Use when building server-side spatial features — PostGIS schema design, SRID choice, spatial indexes, core spatial SQL, MVT tile generation, geocoding, hybrid MySQL+PostGIS, tenant isolation via RLS.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `gis-postgis-backend` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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
| Data safety | Spatial schema and SRID register | Markdown doc per `skill-composition-standards/references/entity-model-template.md` covering geometry/geography columns, SRID, and spatial indexes | `docs/gis/spatial-schema.md` |
| Performance | Spatial query plan review | Markdown doc covering EXPLAIN ANALYZE for hot spatial queries | `docs/gis/spatial-query-plans.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
The spatial backbone for SaaS features: fast spatial queries, correct coordinate systems, production indexing, and clean integration with an existing MySQL or PHP app.

**Prerequisites:** Load `postgresql-fundamentals` for Postgres basics. Load `gis-mapping` for the Leaflet frontend that consumes this. Load `database-design-engineering` for multi-tenant schema patterns.

## When this skill applies

- Adding location features to a SaaS (nearest, within-radius, routing, service-area).
- Storing user-drawn geofences and querying against them.
- Computing catchment areas, coverage maps, or spatial joins.
- Building map tiles for performance.
- Modelling listings with addresses, boundaries, or routes.

## When PostGIS vs MySQL spatial vs specialised stores

```text
Basic point storage + distance queries, already on MySQL        -> MySQL spatial (ST_Distance_Sphere)
Complex spatial ops (intersects, buffer, union, ST_DWithin)     -> PostGIS
Vector tiles, heavy geospatial analytics                        -> PostGIS
Global real-time location tracking (millions of writes/sec)     -> specialised (TimescaleDB + PostGIS, or geo-specific DB)
```

PostGIS is the default for anything beyond trivial point-in-circle queries. The MySQL spatial support works but lacks breadth, tooling, and ecosystem.

See `references/when-postgis.md`.

## Schema design — SRID choice

Coordinate Reference Systems (CRS) are expressed as SRIDs (Spatial Reference IDs).

**The two SRIDs you will use most:**

- **EPSG:4326** — WGS84 lat/long. Store data here. Never compute distances in degrees.
- **EPSG:3857** — Web Mercator (meters). Transform to this for metric distance/area operations and for web map tiles.

**Regional projections:**

- **EPSG:32636** — UTM Zone 36N (Uganda, Kenya, Tanzania, parts of East Africa). Use for accurate metre distances within this region.
- Pick the UTM zone that covers your business area for best metric accuracy.

Rule of thumb:

```sql
-- Storage: always 4326
ALTER TABLE listings ADD COLUMN geom geometry(Point, 4326);

-- Distance computation: transform to 3857 (global) or UTM zone (regional)
SELECT id, ST_Distance(
  ST_Transform(geom, 32636),
  ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 32636)
) AS metres
FROM listings
WHERE ST_DWithin(
  ST_Transform(geom, 32636),
  ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 32636),
  5000
)
ORDER BY metres
LIMIT 50;
```

See `references/schema-srid-choice.md`.

## Geometry vs geography

**`geometry`** — Euclidean, planar calculations. Fast. Correct only in a projected CRS.
**`geography`** — spherical calculations on WGS84. Slower but produces correct metre distances globally.

```text
Small area (single city, country), use projected geometry        -> geometry + UTM/3857
Global queries, don't want to pick SRID per region               -> geography
Heavy spatial operations (intersects, buffers) at scale          -> geometry
Correct metre distances across continents                        -> geography
```

We default to `geometry(Point, 4326)` + transform on query. It's the most flexible.

## Spatial indexes

Every spatial column needs a GIST index:

```sql
CREATE INDEX idx_listings_geom ON listings USING GIST (geom);
```

For very large tables where writes dominate, **BRIN** can be cheaper:

```sql
CREATE INDEX idx_events_geom ON events USING BRIN (geom) WITH (pages_per_range = 32);
```

Always `ANALYZE` after bulk loads. Always check `EXPLAIN ANALYZE` — a spatial index that's not used means your query is wrong (often SRID mismatch or wrong function).

See `references/spatial-indexes.md`.

## Core spatial SQL you will use

**Within radius (nearest neighbour with distance cap):**

```sql
SELECT id, name,
  ST_Distance(geom::geography, point::geography) AS metres
FROM listings
WHERE ST_DWithin(geom::geography, point::geography, 5000)  -- 5 km
ORDER BY metres
LIMIT 50;
```

**Point in polygon:**

```sql
SELECT l.id FROM listings l
JOIN zones z ON ST_Contains(z.geom, l.geom)
WHERE z.name = 'central-district';
```

**Intersect two geometries:**

```sql
SELECT * FROM roads WHERE ST_Intersects(geom, :polygon::geometry);
```

**Buffer + union (service area):**

```sql
SELECT ST_AsGeoJSON(ST_Union(ST_Buffer(geom::geography, 1000)::geometry))
FROM shops
WHERE tenant_id = :tenant_id;
```

**Nearest N with ORDER BY `<->` (KNN, index-assisted):**

```sql
SELECT id FROM listings
WHERE tenant_id = :tenant_id
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
LIMIT 10;
```

See `references/core-spatial-sql.md`.

## Performance patterns

1. **Filter with bbox first**, then exact:

```sql
WHERE geom && ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 4326)
  AND ST_Contains(z.geom, l.geom)
```

2. **Partition** very large spatial tables by date or tenant.
3. **CLUSTER on GIST** periodically for spatial locality of reads.
4. **Cache** computed expensive shapes (isochrones, service areas) in a table.
5. **Use ST_Subdivide** for queries against very large polygons — splits them into indexable pieces.
6. **Index the `::geography` cast** if you use it often:

```sql
CREATE INDEX idx_listings_geog ON listings USING GIST ((geom::geography));
```

See `references/performance-patterns.md`.

## Vector tiles (MVT)

Serve map tiles from PostGIS directly for fast, flexible client-side rendering:

```sql
CREATE OR REPLACE FUNCTION public.tile_listings(z int, x int, y int, tenant int)
RETURNS bytea AS $$
  WITH mvtgeom AS (
    SELECT ST_AsMVTGeom(
      ST_Transform(geom, 3857),
      ST_TileEnvelope(z, x, y),
      4096, 64, true
    ) AS geom, id, name
    FROM listings
    WHERE tenant_id = tenant
      AND geom && ST_Transform(ST_TileEnvelope(z, x, y), 4326)
  )
  SELECT ST_AsMVT(mvtgeom.*, 'listings', 4096, 'geom') FROM mvtgeom;
$$ LANGUAGE SQL STABLE;
```

Serve via `pg_tileserv` or a lightweight Node/Python service. Leaflet / Mapbox GL consume as vector tiles. Cache at the CDN.

See `references/mvt-tiles.md`.

## Geocoding

- **External APIs** — Google, Mapbox, OpenStreetMap Nominatim. Cache aggressively; every API hit costs money.
- **Self-hosted** — Nominatim (OSM-based), Photon, Pelias. Good for privacy + volume.
- **PostGIS Tiger geocoder** — US-focused; not useful in East Africa.
- **Cache results** in your DB keyed by normalised address string.

Pattern:

```text
User address -> normalise -> cache lookup -> API call (if miss) -> store lat/lng + provider -> return
```

See `references/geocoding.md`.

## Hybrid MySQL + PostGIS

Many of our SaaS apps run on MySQL. Pattern: keep MySQL as app DB, add PostGIS as a spatial sidecar:

- **One-way sync:** app writes to MySQL; change-capture (Debezium or CDC) → Postgres. Use PostGIS for spatial queries returned via an API layer.
- **Shared reference data:** geofences stored in PostGIS, ID joined back to MySQL rows.
- **Spatial answers cached** in MySQL where needed (e.g., `listing.nearest_transit_id`).

Transactions don't span the two DBs — design for eventual consistency. See `references/hybrid-mysql-postgis.md`.

## Backup + migration

- `pg_dump -Fc --no-privileges --no-owner` — custom format, restore with `pg_restore -j 4`.
- Spatial reference table (`spatial_ref_sys`) survives `pg_dump`; don't drop it.
- `ogr2ogr` for converting between formats (Shapefile, GeoJSON, KML → PostGIS, and back).
- Keep `postgis_full_version()` output with backups — version drift matters.

See `references/backup-migration.md`.

## Tenant isolation — Row-Level Security

```sql
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON listings
  USING (tenant_id = current_setting('app.tenant_id')::int);
```

Set `app.tenant_id` per session from the application. RLS makes cross-tenant leaks structurally impossible even if a query forgets the `WHERE` clause.

See `references/tenant-isolation-rls.md`.

## Anti-patterns

- Storing lat/lng as two separate `double precision` columns and computing distance manually.
- Computing distance in degrees (1° latitude ≠ 1° longitude, and neither equals metres).
- No GIST index on a spatial column.
- SRID mismatch between table and query — no index use, no error, silently wrong.
- Mixing `geometry` and `geography` in the same query without explicit casts.
- Using `ST_Distance` with a large table without `ST_DWithin` pre-filter.
- Storing projected coordinates (3857) — lose fidelity, hard to change later.
- Unnormalised addresses in geocoding cache — cache miss on whitespace differences.
- Cross-tenant queries because RLS isn't enabled.

## Read next

- `gis-mapping` — Leaflet frontend consuming this backend.
- `gis-maps-integration` — Google Maps / Mapbox when richer features are needed.
- `gis-enterprise-domain` — ArcGIS Enterprise + real-estate patterns.
- `postgresql-administration` — operating Postgres in production.

## References

- `references/when-postgis.md`
- `references/schema-srid-choice.md`
- `references/spatial-indexes.md`
- `references/core-spatial-sql.md`
- `references/performance-patterns.md`
- `references/mvt-tiles.md`
- `references/geocoding.md`
- `references/hybrid-mysql-postgis.md`
- `references/backup-migration.md`
- `references/tenant-isolation-rls.md`
