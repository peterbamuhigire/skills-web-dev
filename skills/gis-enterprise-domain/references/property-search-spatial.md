# Property Search with Spatial Filters (PostGIS Recipe)

Full SQL recipe for "find active listings in selected districts, within walking distance to a transit stop, inside a school zone", plus caching, pagination, and the REST API shape.

Assumes the spatial backend follows the `gis-postgis-backend` skill: SRID 4326 for storage, geography casts for metric distances, GiST indexes on all geometry columns.

## Schema sketch

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE districts (
  id          bigserial PRIMARY KEY,
  code        text NOT NULL UNIQUE,
  name        text NOT NULL,
  geom        geometry(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX districts_geom_gix ON districts USING GIST (geom);

CREATE TABLE zones (
  id          bigserial PRIMARY KEY,
  type        text NOT NULL,       -- 'school','health','flood',...
  rating      int,                 -- 1..5 when applicable
  geom        geometry(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX zones_geom_gix ON zones USING GIST (geom);
CREATE INDEX zones_type_idx  ON zones (type);

CREATE TABLE transit_stops (
  id          bigserial PRIMARY KEY,
  mode        text NOT NULL,       -- 'bus','rail','bus_rapid',...
  name        text,
  geom        geometry(Point, 4326) NOT NULL
);
CREATE INDEX transit_stops_geom_gix ON transit_stops USING GIST (geom);

CREATE TABLE listings (
  id             bigserial PRIMARY KEY,
  tenant_id      bigint NOT NULL,
  external_ref   text NOT NULL,
  status         text NOT NULL,    -- 'active','pending','sold','expired'
  price          numeric(14,2),
  bedrooms       int,
  bathrooms      int,
  area_sqm       numeric(10,2),
  listed_at      timestamptz NOT NULL DEFAULT now(),
  geom           geometry(Point, 4326) NOT NULL
);
CREATE INDEX listings_tenant_status_idx ON listings (tenant_id, status);
CREATE INDEX listings_geom_gix          ON listings USING GIST (geom);
CREATE UNIQUE INDEX listings_tenant_extref ON listings (tenant_id, external_ref);
```

## The search query

Parameters:

- `:tenant_id` — current tenant.
- `:district_codes` — array of district codes the user selected.
- `:transit_walk_m` — walking distance in metres (typical 800).
- `:school_min_rating` — minimum school-zone rating (typical 3 or 4).
- `:limit`, `:offset` — pagination.

```sql
WITH search_area AS (
  SELECT ST_Union(d.geom) AS geom
  FROM districts d
  WHERE d.code = ANY(:district_codes)
),
school_zones AS (
  SELECT ST_Union(z.geom) AS geom
  FROM zones z
  WHERE z.type = 'school'
    AND z.rating >= :school_min_rating
),
candidate_listings AS (
  SELECT l.*
  FROM listings l, search_area s, school_zones sz
  WHERE l.tenant_id = :tenant_id
    AND l.status = 'active'
    AND ST_Covers(s.geom, l.geom)
    AND ST_Covers(sz.geom, l.geom)
),
with_transit AS (
  SELECT c.*,
         EXISTS (
           SELECT 1
           FROM transit_stops t
           WHERE ST_DWithin(
                   t.geom::geography,
                   c.geom::geography,
                   :transit_walk_m
                 )
         ) AS transit_ok
  FROM candidate_listings c
)
SELECT id, external_ref, price, bedrooms, bathrooms, area_sqm,
       ST_Y(geom) AS lat, ST_X(geom) AS lng,
       listed_at
FROM with_transit
WHERE transit_ok
ORDER BY listed_at DESC
LIMIT :limit OFFSET :offset;
```

Why this shape:

- `ST_Union` of districts and school zones happens once per query (CTE).
- `ST_Covers` is slightly cheaper than `ST_Contains` and is correct for "point inside polygon" on valid geometries.
- The transit check uses `ST_DWithin` on geography so the distance is in metres regardless of projection.
- `EXISTS` avoids duplicating listings when multiple transit stops are close.

## Index-friendly rewrite for very large tables

When `listings` exceeds a few million rows, push the district filter into the main scan so the spatial index drives the plan:

```sql
WITH search_area AS MATERIALIZED (
  SELECT ST_Union(geom) AS geom FROM districts WHERE code = ANY(:district_codes)
),
school_zones AS MATERIALIZED (
  SELECT ST_Union(geom) AS geom FROM zones WHERE type = 'school' AND rating >= :school_min_rating
)
SELECT l.*
FROM listings l
JOIN search_area s   ON ST_Intersects(l.geom, s.geom)  AND ST_Covers(s.geom, l.geom)
JOIN school_zones sz ON ST_Intersects(l.geom, sz.geom) AND ST_Covers(sz.geom, l.geom)
WHERE l.tenant_id = :tenant_id
  AND l.status    = 'active'
  AND EXISTS (
    SELECT 1 FROM transit_stops t
    WHERE ST_DWithin(t.geom::geography, l.geom::geography, :transit_walk_m)
  )
ORDER BY l.listed_at DESC
LIMIT :limit OFFSET :offset;
```

`MATERIALIZED` forces the CTEs to run once, and `ST_Intersects` on the indexed column enables bbox pre-filtering by the GiST index before the precise `ST_Covers` check.

## Pagination

- Use **keyset pagination** for infinite-scroll UIs: `ORDER BY listed_at DESC, id DESC` with `(listed_at, id) < (:last_listed_at, :last_id)`.
- Use offset pagination only for numbered pages under a few thousand rows.
- Always cap `limit` server-side (for example, 50).

## Caching strategy

Tiers:

1. **Per-listing cache** — not for search; for the detail page.
2. **Search-result cache** — key = hash of (tenant_id, district_codes, walk_m, rating, sort, page). TTL 30–120 seconds for active listings.
3. **Tile-style cache** — for map views, serve MVT from PostGIS with `ST_AsMVT` and a short CDN TTL.
4. **Aggregates cache** — neighbourhood summary tables refreshed nightly (see `neighbourhood-analysis.md`).

Invalidate search caches on listing create/update/delete events via a message queue.

## REST API shape

```text
GET /api/v1/listings/search
  ?district=KAM01,KAM02
  &walk_to_transit_m=800
  &school_min_rating=4
  &bedrooms_min=2
  &price_max=250000
  &sort=newest
  &page=1
  &page_size=25

Response:
{
  "data": [
    {
      "id": 10234,
      "external_ref": "RE-10234",
      "price": 185000,
      "currency": "UGX",
      "bedrooms": 3,
      "bathrooms": 2,
      "area_sqm": 140,
      "location": { "lat": 0.3136, "lng": 32.5811 },
      "listed_at": "2026-04-02T09:21:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 25, "total": 412 },
  "filters_applied": {
    "districts": ["KAM01","KAM02"],
    "walk_to_transit_m": 800,
    "school_min_rating": 4
  }
}
```

Rules:

- Parameter names are snake_case and explicit about units (`walk_to_transit_m`).
- Pagination is standard across all list endpoints in the SaaS.
- Response includes `filters_applied` so the client can render active filter chips without reparsing the URL.

## Query-time observability

- Log `EXPLAIN (ANALYZE, BUFFERS)` output for searches over 500 ms in dev and staging.
- Emit a span per search with tags for district count, result count, and total duration.
- Track p50 / p95 / p99 latency — tune the index and CTE strategy if p95 exceeds 400 ms under normal load.

## Anti-patterns

- Forgetting the `tenant_id` filter — a tenant-isolation breach is a P0 incident.
- Using `ST_Distance` instead of `ST_DWithin` for "within N metres" — `ST_Distance` cannot use the index.
- Doing the walking-distance check with Euclidean metres on SRID 4326 — off by a factor depending on latitude.
- Sorting by spatial distance from a point and paginating by offset under churn — results shift between pages.
- Unbounded district arrays that explode `ST_Union` — cap the selection UI.

## Related references

- `neighbourhood-analysis.md` — comparables and walk score (reuse the same schema).
- `catchment-isochrones.md` — drive-time filters instead of walking distance.
- `real-estate-saas-integration.md` — how this endpoint fits into the wider architecture.
- `gis-postgis-backend` skill — SRID rules, GiST index patterns.
