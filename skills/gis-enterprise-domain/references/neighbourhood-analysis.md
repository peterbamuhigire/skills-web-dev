# Neighbourhood Analysis for Real-Estate GIS

Walk-score, transit access, comparable sales, and demographic overlay patterns. All queries are PostGIS-first and reuse the schema from `property-search-spatial.md`.

## Walk score (categorised amenity density)

The classic walk score is a weighted count of amenities within a walking buffer, by category, with a distance decay.

### Schema

```sql
CREATE TABLE amenities (
  id         bigserial PRIMARY KEY,
  category   text NOT NULL,       -- 'grocery','school','restaurant','park','pharmacy','transit'
  subtype    text,
  name       text,
  geom       geometry(Point, 4326) NOT NULL
);
CREATE INDEX amenities_geom_gix ON amenities USING GIST (geom);
CREATE INDEX amenities_cat_idx  ON amenities (category);
```

### Category weights and max distance

```sql
CREATE TABLE walk_score_weights (
  category   text PRIMARY KEY,
  weight     numeric NOT NULL,    -- relative importance
  max_m      int NOT NULL         -- cap for distance decay
);

INSERT INTO walk_score_weights VALUES
  ('grocery',    3.0, 1200),
  ('school',     2.5, 1200),
  ('restaurant', 2.0,  800),
  ('park',       1.5, 1200),
  ('pharmacy',   1.5, 1000),
  ('transit',    3.0,  800);
```

### Walk-score computation

Distance decay: 1.0 at 0 m, 0.0 at `max_m`, linear in between. This is good enough for most real-estate presentations; replace with logistic if product demands it.

```sql
CREATE OR REPLACE FUNCTION walk_score(p_listing_id bigint)
RETURNS numeric
LANGUAGE sql
STABLE
AS $$
  WITH target AS (
    SELECT geom FROM listings WHERE id = p_listing_id
  ),
  nearby AS (
    SELECT a.category,
           ST_Distance(a.geom::geography, t.geom::geography) AS d,
           w.weight,
           w.max_m
    FROM target t
    JOIN amenities a
      ON ST_DWithin(a.geom::geography, t.geom::geography, 1600)
    JOIN walk_score_weights w ON w.category = a.category
  ),
  weighted AS (
    SELECT category,
           SUM(weight * GREATEST(0, 1.0 - d / max_m)) AS s
    FROM nearby
    GROUP BY category
  )
  SELECT LEAST(100, ROUND(SUM(s) * 5.0))::numeric AS score
  FROM weighted;
$$;
```

Scale the raw sum to 0–100; the `5.0` constant is tuned against a reference set of listings. Calibrate per market; rural markets need a smaller constant than dense urban cores.

### Bulk refresh

Do not compute walk score per request. Materialise per listing:

```sql
CREATE TABLE listing_walk_score (
  listing_id bigint PRIMARY KEY REFERENCES listings(id) ON DELETE CASCADE,
  score      numeric NOT NULL,
  computed_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO listing_walk_score (listing_id, score)
SELECT id, walk_score(id)
FROM listings
WHERE tenant_id = :tenant_id
ON CONFLICT (listing_id) DO UPDATE
  SET score = EXCLUDED.score,
      computed_at = now();
```

Refresh nightly, plus on listing geometry change.

## Transit access (nearest N stops with travel time)

Straight-line distance is usable for UI summaries; walking time is a better proxy for lived experience.

```sql
SELECT t.id, t.name, t.mode,
       ST_Distance(t.geom::geography, l.geom::geography) AS dist_m,
       -- 80 m/min average walking pace
       ROUND(ST_Distance(t.geom::geography, l.geom::geography) / 80.0) AS walk_min
FROM listings l
JOIN transit_stops t
  ON ST_DWithin(t.geom::geography, l.geom::geography, 1200)
WHERE l.id = :listing_id
ORDER BY t.geom <-> l.geom
LIMIT 3;
```

Notes:

- `<->` uses the GiST index for k-NN ordering.
- 80 m/min is an average urban adult pace; adjust per market.
- For true network walking time, use an isochrone (see `catchment-isochrones.md`).

## Comparable sales (comps)

"Within 2 km, same bed/bath, sold in last 180 days".

```sql
SELECT c.id, c.external_ref, c.price, c.area_sqm,
       c.price / NULLIF(c.area_sqm, 0) AS price_per_sqm,
       ST_Distance(c.geom::geography, l.geom::geography) AS dist_m,
       c.sold_date
FROM listings l
JOIN listings c
  ON c.tenant_id = l.tenant_id
 AND c.status = 'sold'
 AND c.sold_date >= now() - interval '180 days'
 AND c.bedrooms BETWEEN l.bedrooms - 1 AND l.bedrooms + 1
 AND c.bathrooms BETWEEN l.bathrooms - 1 AND l.bathrooms + 1
 AND ST_DWithin(c.geom::geography, l.geom::geography, 2000)
 AND c.id <> l.id
WHERE l.id = :listing_id
ORDER BY dist_m
LIMIT 10;
```

Refinements:

- Constrain by property type (detached / apartment) when the schema has it.
- Weight comps by recency: closer date -> higher weight in the derived "comp price".
- Cap at 10 comps to keep the UI clean.
- Store a per-listing comp snapshot for audit trails.

### Derived estimate

```sql
SELECT AVG(c.price / NULLIF(c.area_sqm, 0)) AS median_ppsqm,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c.price / NULLIF(c.area_sqm, 0)) AS p50
FROM listings c
JOIN listings l ON l.id = :listing_id
WHERE c.tenant_id = l.tenant_id
  AND c.status = 'sold'
  AND c.sold_date >= now() - interval '180 days'
  AND ST_DWithin(c.geom::geography, l.geom::geography, 2000);
```

Always present comp-derived numbers with a date range and a count; a "price estimate" based on two comps is marketing copy, not analysis.

## Demographics overlay

Many markets have census/block statistics. Model as small-area polygons with attributes:

```sql
CREATE TABLE demographics (
  id          bigserial PRIMARY KEY,
  area_code   text NOT NULL UNIQUE,
  pop_total   int,
  households  int,
  median_income numeric,
  under_18_pct numeric,
  over_65_pct  numeric,
  geom        geometry(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX demographics_geom_gix ON demographics USING GIST (geom);
```

### Attach demographics to a listing

```sql
SELECT d.area_code, d.pop_total, d.median_income, d.under_18_pct, d.over_65_pct
FROM listings l
JOIN demographics d ON ST_Covers(d.geom, l.geom)
WHERE l.id = :listing_id
LIMIT 1;
```

If small-area polygons overlap (unlikely but possible), pick the smallest area:

```sql
ORDER BY ST_Area(d.geom) ASC
LIMIT 1
```

### Buffer-based summary

For a 1 km buffer summary around a listing, area-weight the demographic attributes:

```sql
WITH buf AS (
  SELECT ST_Buffer(l.geom::geography, 1000)::geometry AS geom
  FROM listings l
  WHERE l.id = :listing_id
)
SELECT
  SUM(d.pop_total * ST_Area(ST_Intersection(d.geom, b.geom)) / NULLIF(ST_Area(d.geom),0))::int AS pop_1km,
  AVG(d.median_income) AS avg_median_income
FROM demographics d, buf b
WHERE ST_Intersects(d.geom, b.geom);
```

This is an area-weighted approximation; it is not exact because demographics are not uniformly distributed within an area, but it is the correct default without finer data.

## Caching and refresh policy

```text
Artefact                     Refresh cadence               Trigger
---------------------------  ----------------------------  -----------------------------
listing_walk_score           Nightly + on listing move     Listing geometry change
listing_comps_snapshot       Nightly                        New sold status, weekly anyway
listing_demographics         On listing create, annual      Listing move, new census drop
Transit top-3                On listing create              Listing move, new stops
```

Store everything tenant-scoped. Demographics are shared but attachment to listings is not.

## API shape

```text
GET /api/v1/listings/{id}/neighbourhood

{
  "walk_score": 78,
  "transit": [
    { "name": "Kampala Central", "mode": "bus_rapid", "walk_min": 6 },
    { "name": "Market Station",  "mode": "bus",        "walk_min": 9 }
  ],
  "comps": {
    "count": 8,
    "median_price_per_sqm": 1240,
    "window_days": 180
  },
  "demographics": {
    "area_code": "KLA-0421",
    "pop_total": 18420,
    "median_income": 3_200_000,
    "under_18_pct": 28.4,
    "over_65_pct": 6.1
  }
}
```

Always expose the `window_days` and `area_code` so the client can show provenance.

## Anti-patterns

- Recomputing walk score per page view.
- Presenting a comps-derived estimate with fewer than 3 comps.
- Ignoring sold_date and including decade-old sales as comps.
- Using demographics at the wrong scale ("national median income" for a listing card).
- Sharing demographic data across tenants without licensing awareness.

## Related references

- `property-search-spatial.md` — filter layer; composable with these outputs.
- `catchment-isochrones.md` — for accurate walk / drive time rather than buffers.
- `market-heatmaps.md` — aggregate version of price-per-sqm analysis.
