# Projections Deep Dive — CRS Choice

Distilled from *GIS Succinctly* and *Modern Web Cartography*. CRS choice is the single most common source of spatial bugs — wrong SRID produces silently wrong distances, areas, and spatial joins.

## Decision Rule

1. **Storage CRS**: `geometry(Point, 4326)` (WGS84) for global data, or a suitable projected SRID (UTM/State Plane) for local, measurement-heavy data.
2. **Measurement**: never measure distance or area on `geometry(4326)`. Either cast to `geography` (for distance, spheroidal) or `ST_Transform` to a local projected SRID (for area and precise distance).
3. **Rendering**: always deliver to the web client in 4326 (or 3857 for raster-like flows). Project on the server, never on the client.

## Which Projection for Which Problem

| Task | Recommended projection family | Example SRID |
|---|---|---|
| Global storage / interchange | Geographic (WGS84) | 4326 |
| Web map tiles | Web Mercator | 3857 |
| Distance / buffering, country-scale | UTM (zone-specific) | 32636 (Uganda zone 36N) |
| Area calculations, country-scale | Equal-area (Albers / Lambert) | 102022 (Africa Albers Equal Area) |
| Navigation / direction preservation | Conformal (Mercator, Lambert Conformal) | 3857 |
| National cadastre | National grid | Uganda: 21096 (Arc 1960 / UTM 36N) |

Rule: distance → UTM zone covering the centroid; area → Albers/Lambert equal-area for the region; shape preservation → conformal.

## UTM Zones for East Africa

| Zone | Covers |
|---|---|
| 35M | S Uganda, W Tanzania, Rwanda, Burundi |
| 35S | Southern Tanzania, Zambia |
| 36M | E Uganda, Central Kenya, NW Tanzania |
| 36S | SE Tanzania, Malawi |
| 37M | NE Kenya, Somalia coast |
| 37S | coastal Tanzania south of Dar |

Pick the zone whose central meridian is closest to the data's centroid. If the dataset crosses two zones (e.g. Uganda east–west extent), prefer a national grid (e.g. Arc 1960 / UTM 36N, SRID 21096) over switching per row.

## Conformal vs Equivalent vs Equidistant

- **Conformal** (Mercator, Lambert Conformal Conic) preserves *angles* locally. Good for navigation and for map styles; bad for area at high latitudes (Greenland looks larger than Africa).
- **Equivalent / Equal-area** (Albers, Lambert Azimuthal Equal-Area, Mollweide) preserves *area*. Use for choropleths, density, any `ST_Area` that must be comparable across the dataset.
- **Equidistant** preserves *distance* from one point or along a meridian only. Rare in application code; used for range maps.

No single projection preserves all three. Pick the invariant that matters for the question being asked.

## `geometry` vs `geography` (PostGIS)

- `geometry` is planar math. `ST_Distance` and `ST_Area` return units of the SRID (degrees for 4326, metres for UTM).
- `geography` is spheroidal math. `ST_Distance` returns metres regardless of input. Slower; no full index support for all functions.

Use `geography` when:

- The query is a one-shot distance within or between countries.
- You cannot pick a single UTM zone because data spans many.
- Precision within ~0.3% is acceptable.

Use `geometry` with a projected SRID when:

- You need precise area or repeated distance queries.
- You already reproject once at ingest and can index in the local SRID.

Never use `ST_Distance` on unprojected `geometry(4326)` — the result is degrees, not metres.

## KNN Index Rule

- `<->` (distance operator) only uses a spatial index if it's a **GIST** index on the geometry column.
- `SP-GIST` is optional for points but does not accelerate `<->` for polygons.
- If ordering by `geom <-> :p LIMIT n` is slow, run `CREATE INDEX ... USING GIST (geom);` and `ANALYZE`.

## Large Polygons — `ST_Subdivide`

For country- or region-level polygons that get `ST_Intersects`-joined against millions of points, pre-split:

```sql
CREATE TABLE districts_subdivided AS
SELECT district_id, ST_Subdivide(geom, 256) AS geom
FROM districts;
CREATE INDEX ON districts_subdivided USING GIST(geom);
```

Subdivided geometries can fit in leaf index pages; single huge polygons cannot, and the join degenerates to full scan.

## BRIN for Huge Append-Only Data

For timestamp + location tables > 100M rows that are mostly append-only (GPS tracks, sensor readings):

```sql
CREATE INDEX ON trackpoints USING BRIN (recorded_at, geom) WITH (pages_per_range = 32);
```

BRIN is ~1000× smaller than GIST and sufficient for range scans on clustered data. Not a replacement for GIST on the hot query geometry.

## Anti-Patterns

- Storing `geometry(Point)` without an SRID — silent 0, joins break at the first reprojection.
- Mixing SRIDs in the same column — PostGIS accepts it if SRID is unconstrained in the type, then spatial joins return empty.
- `ST_Area(geom)` on 4326 and reporting "square degrees" as if they were m² (they are not — a square degree is ~12 300 km² at the equator).
- `ST_Buffer(geom, 1000)` on 4326 — buffers by 1000 degrees, not 1000 metres. Use `geography` or reproject first.
- Projecting on every query instead of storing an additional projected column with its own GIST index.
