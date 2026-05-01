# Schema And SRID Choice

Pick the coordinate reference system once, up front. Changing SRIDs on populated tables is painful and tends to break every spatial query that survived the migration.

## Core SRIDs

| SRID | Name | Units | Use for |
| --- | --- | --- | --- |
| 4326 | WGS84 lat/long | degrees | Storage; interchange with GeoJSON, Leaflet, Mapbox |
| 3857 | Web Mercator | metres (distorted) | Tile rendering, rough metric ops at global zoom |
| 32636 | UTM Zone 36N | metres | Accurate distance/area in Uganda, Kenya, Tanzania, Rwanda |
| 32735 | UTM Zone 35S | metres | Southern East Africa (parts of Tanzania, Zambia) |
| 2163 | US National Atlas | metres | US-wide accurate ops |
| 3035 | ETRS89 LAEA | metres | Europe-wide accurate ops |

Find the right UTM zone at <https://www.epsg.io> or `SELECT ST_UTMZone(geom)` in newer PostGIS.

## The "store in 4326, transform on query" rule

Default for almost every SaaS:

```sql
-- Store as WGS84 lat/long
ALTER TABLE listings ADD COLUMN geom geometry(Point, 4326);

-- Transform for metric work
SELECT id,
       ST_Distance(
         ST_Transform(geom, 32636),
         ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 32636)
       ) AS metres
FROM listings
WHERE ST_DWithin(
  ST_Transform(geom, 32636),
  ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 32636),
  5000
);
```

Why:

- 4326 is the interchange format. GeoJSON is always 4326. Leaflet expects 4326.
- Transform cost is cheap compared to getting distances wrong.
- Storing in a projected SRID locks you to one region and breaks the day you expand.

## When to pre-project

Pre-project the column if all of the following are true:

- Data is single-region and will stay single-region (e.g., city of Kampala only).
- Queries are metric-dominated (buffers, unions, intersects in metres).
- You measured the transform overhead and it matters for your workload.

Then use an indexed expression column instead of replacing the 4326 column:

```sql
ALTER TABLE listings
  ADD COLUMN geom_utm geometry(Point, 32636)
  GENERATED ALWAYS AS (ST_Transform(geom, 32636)) STORED;

CREATE INDEX idx_listings_geom_utm ON listings USING GIST (geom_utm);
```

Keep the 4326 column and index. Use the projected column for metric queries only.

## Geometry vs geography column types

```text
geometry(Point, 4326)        Planar maths on degrees. Wrong for distance unless transformed.
geometry(Point, 32636)       Planar maths in metres. Correct in region. Fast.
geometry(Polygon, 4326)      Standard for stored shapes.
geography(Point, 4326)       Spherical maths. Correct metres globally. Slower.
geography(Polygon, 4326)     Spherical maths on polygons. Much slower than geometry.
```

Decision rule:

- Default: `geometry(Point, 4326)` + transform on query.
- Global workload, no regional projection fits: `geography(Point, 4326)`.
- Large polygons (country boundaries, service areas): `geometry` + projected SRID, not `geography`.
- Mixing both types in one query without explicit casts: always wrong, fix it.

## Typed vs untyped columns

Always type the column:

```sql
-- Good: enforces Point + 4326
geom geometry(Point, 4326)

-- Bad: accepts anything, invites silent SRID mismatches
geom geometry
```

Typed columns reject a `LineString` insert, reject an SRID-0 insert, and make the intent visible to readers.

## Dimensionality

- 2D (XY) is the default. Use it unless you need elevation.
- 3D (XYZ) for altitude-aware data: flight paths, drone, terrain. Use `geometry(PointZ, 4326)`.
- Avoid M (measure) unless you actually use linear referencing (pgRouting, roads).

## Example schema for a listings SaaS

```sql
CREATE TABLE listings (
  id              bigserial PRIMARY KEY,
  tenant_id       int         NOT NULL,
  title           text        NOT NULL,
  address_raw     text        NOT NULL,
  address_norm    text        NOT NULL,
  geom            geometry(Point, 4326) NOT NULL,
  geom_utm        geometry(Point, 32636)
                  GENERATED ALWAYS AS (ST_Transform(geom, 32636)) STORED,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_listings_geom     ON listings USING GIST (geom);
CREATE INDEX idx_listings_geom_utm ON listings USING GIST (geom_utm);
CREATE INDEX idx_listings_tenant   ON listings (tenant_id);

-- Composite for tenant-scoped spatial queries
CREATE INDEX idx_listings_tenant_geom ON listings USING GIST (geom)
  INCLUDE (tenant_id);
```

## Checking existing data

```sql
-- What SRIDs are actually in the table
SELECT DISTINCT ST_SRID(geom) FROM listings;

-- Invalid geometries
SELECT id, ST_IsValidReason(geom) FROM listings WHERE NOT ST_IsValid(geom);

-- Force SRID on legacy rows (only if you know they are 4326)
UPDATE listings SET geom = ST_SetSRID(geom, 4326) WHERE ST_SRID(geom) = 0;
```

## Anti-patterns

- Two `double precision` columns for lat and lng. You lose index support, type safety, and distance correctness.
- Mixing SRIDs in one table. The index works; the results are wrong.
- Storing distance-computed values in 3857 and calling them metres. Web Mercator distorts badly away from the equator.
- `geometry` without type and SRID constraints. Do not let production accept `geometry` blobs of unknown shape.

## Cross-reference

- `postgresql-fundamentals` — DDL and constraints.
- `references/spatial-indexes.md` — GIST on typed columns.
- `references/core-spatial-sql.md` — query patterns per SRID.
