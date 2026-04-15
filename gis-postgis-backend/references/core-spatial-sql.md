# Core Spatial SQL Recipes

Copy-paste starting points. Replace parameters (`:lng`, `:lat`, `:tenant_id`, `:polygon`) and verify SRIDs match your schema.

## 1. Within radius (metres)

Preferred: geography cast, indexed, correct globally.

```sql
SELECT id, name,
       ST_Distance(geom::geography,
                   ST_MakePoint(:lng, :lat)::geography) AS metres
FROM listings
WHERE tenant_id = :tenant_id
  AND ST_DWithin(geom::geography,
                 ST_MakePoint(:lng, :lat)::geography,
                 5000)
ORDER BY metres
LIMIT 50;
```

Regional alternative, faster on single-region data (UTM Zone 36N shown):

```sql
WITH q AS (
  SELECT ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 32636) AS g
)
SELECT id, name,
       ST_Distance(ST_Transform(geom, 32636), q.g) AS metres
FROM listings, q
WHERE tenant_id = :tenant_id
  AND ST_DWithin(ST_Transform(geom, 32636), q.g, 5000)
ORDER BY metres
LIMIT 50;
```

Requires the matching expression index (see `references/spatial-indexes.md`).

## 2. Point in polygon

```sql
-- Listings inside a named zone
SELECT l.id, l.name
FROM listings l
JOIN zones z ON ST_Contains(z.geom, l.geom)
WHERE l.tenant_id = :tenant_id
  AND z.slug     = 'central-division';
```

For a one-off polygon passed from the app:

```sql
SELECT id, name
FROM listings
WHERE tenant_id = :tenant_id
  AND ST_Contains(
        ST_SetSRID(ST_GeomFromGeoJSON(:polygon_json), 4326),
        geom
      );
```

## 3. Intersects (overlap, touch, or contain)

```sql
SELECT r.id, r.name
FROM roads r
WHERE ST_Intersects(
        r.geom,
        ST_SetSRID(ST_GeomFromGeoJSON(:polygon_json), 4326)
      );
```

Rule: `ST_Intersects` is the broadest predicate. Use `ST_Contains`, `ST_Within`, `ST_Overlaps`, `ST_Touches` when you need stricter semantics.

## 4. Buffer plus union (service area)

Produce a single polygon covering everything within N metres of each shop:

```sql
SELECT ST_AsGeoJSON(
         ST_Transform(
           ST_Union(
             ST_Buffer(geom::geography, 1000)::geometry
           ),
           4326
         )
       ) AS service_area
FROM shops
WHERE tenant_id = :tenant_id;
```

Notes:

- Buffer on `::geography` produces a real-metre buffer globally.
- Result geometry returns to 4326 for the client.
- For many overlapping buffers, `ST_Union` is expensive. Precompute into a materialised view.

## 5. KNN with `<->` (index-assisted nearest N)

```sql
SELECT id, name
FROM listings
WHERE tenant_id = :tenant_id
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
LIMIT 10;
```

- `<->` uses GIST to return nearest-first without scanning the whole table.
- The distance is in degrees (because both operands are 4326). Do not treat as metres; it is only for ordering.
- To return metres alongside:

```sql
SELECT id, name,
       ST_Distance(geom::geography, p::geography) AS metres
FROM listings,
     LATERAL (SELECT ST_SetSRID(ST_MakePoint(:lng, :lat), 4326) AS p) q
WHERE tenant_id = :tenant_id
ORDER BY geom <-> q.p
LIMIT 10;
```

## 6. Nearest neighbour per row (LATERAL join)

For each shop, the nearest transit stop:

```sql
SELECT s.id AS shop_id,
       t.id AS stop_id,
       ST_Distance(s.geom::geography, t.geom::geography) AS metres
FROM shops s,
     LATERAL (
       SELECT id, geom
       FROM transit_stops
       ORDER BY geom <-> s.geom
       LIMIT 1
     ) t
WHERE s.tenant_id = :tenant_id;
```

`LATERAL` + `<->` + `LIMIT 1` is the idiomatic KNN-per-row pattern.

## 7. Polygon simplification (for transport and MVT)

```sql
-- Tolerance in SRID units. For 4326 (degrees), 0.0001 ~ 11 m at the equator.
SELECT id,
       ST_SimplifyPreserveTopology(geom, 0.0001) AS geom_simple
FROM zones
WHERE tenant_id = :tenant_id;
```

- `ST_Simplify` is faster; `ST_SimplifyPreserveTopology` avoids invalid output.
- Simplify per zoom level and cache. See `references/mvt-tiles.md`.

## 8. Clip to bounding box or polygon

```sql
-- Clip to viewport
SELECT id,
       ST_Intersection(geom,
                       ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 4326)) AS geom
FROM zones
WHERE geom && ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 4326);
```

`&&` is the bbox-overlap operator and uses the GIST index.

## 9. Area, length, centroid

```sql
SELECT id,
       ST_Area(geom::geography)   AS m2,
       ST_Perimeter(geom::geography) AS perimeter_m,
       ST_Centroid(geom)          AS centroid
FROM zones
WHERE tenant_id = :tenant_id;
```

`ST_Area` on `::geography` returns square metres globally. On raw `geometry(Polygon, 4326)` it returns square-degrees, which is never what you want.

## 10. Transform and output GeoJSON

```sql
SELECT id,
       ST_AsGeoJSON(geom, 6) AS geojson  -- 6 decimals ~ 10 cm precision
FROM listings
WHERE tenant_id = :tenant_id;
```

Use `ST_AsGeoJSON(row)` to include properties alongside geometry:

```sql
SELECT ST_AsGeoJSON(t.*)
FROM (SELECT id, name, geom FROM listings WHERE tenant_id = :tenant_id) t;
```

## 11. Clustering

`ST_ClusterKMeans` groups points into k clusters; useful for map thinning:

```sql
SELECT id,
       ST_ClusterKMeans(geom, 50) OVER () AS cluster_id
FROM listings
WHERE tenant_id = :tenant_id;
```

`ST_ClusterDBSCAN` for density-based (no fixed k):

```sql
SELECT id,
       ST_ClusterDBSCAN(geom, eps := 0.001, minpoints := 5) OVER () AS cluster_id
FROM listings
WHERE tenant_id = :tenant_id;
```

## 12. Convex and concave hulls

```sql
-- Convex hull of all listings in a zone
SELECT z.id, ST_ConvexHull(ST_Collect(l.geom)) AS hull
FROM zones z
JOIN listings l ON ST_Contains(z.geom, l.geom)
WHERE z.tenant_id = :tenant_id
GROUP BY z.id;

-- Concave hull, target ratio 0.8 (closer to the shape of the points)
SELECT ST_ConcaveHull(ST_Collect(geom), 0.8)
FROM listings
WHERE tenant_id = :tenant_id;
```

## Anti-patterns

- `ST_Distance(geom, point) < 5000` with no `ST_DWithin` prefilter. Full scan.
- Using `<->` distance as metres. It is only an ordering key.
- `ST_Area(geom)` on 4326 geometry expecting square metres.
- Sequential `ST_Buffer` + `ST_Union` in a loop from the app. Do the union server-side.
- Returning raw `geometry` to the web layer. Always emit GeoJSON or MVT.

## Cross-reference

- `references/spatial-indexes.md` — what indexes each predicate uses.
- `references/performance-patterns.md` — pre-filter, subdivide, materialise.
- `references/mvt-tiles.md` — simplification + serving tiles.
