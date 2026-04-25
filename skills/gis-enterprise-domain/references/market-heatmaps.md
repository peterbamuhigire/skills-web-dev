# Market Heatmaps with H3 Hex Indexing

H3 hex tiles via the `h3-pg` extension, choropleth rendering, small-N privacy suppression, and temporal (last 90/180 days) heatmaps for real-estate price, volume, and activity.

## Why H3 over admin boundaries or a regular grid

- Uniform cell area across latitudes (unlike lat/lng grid cells).
- Stable IDs that work across zoom levels (`h3_index` at multiple resolutions).
- Neighbours and compaction are cheap operations.
- Client libraries exist for all major languages.

Use H3 for heatmaps. Use admin boundaries only when the product narrative is "by district".

## Setup — `h3-pg`

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS h3;
CREATE EXTENSION IF NOT EXISTS h3_postgis;
```

### Resolution choice

```text
Resolution  Edge length      Typical use
----------  ---------------  ----------------------------------------
5           ~9 km            Country-level choropleth
6           ~3.2 km          City region
7           ~1.2 km          Citywide
8           ~460 m           Neighbourhood
9           ~170 m           Street cluster
10          ~66 m            Building cluster (privacy risk)
```

For real-estate price heatmaps, **resolution 7 or 8** is the sweet spot for urban markets. Resolution 9 or 10 raises privacy risk (small N per cell); suppress those cells explicitly.

## Materialised heatmap table

```sql
CREATE TABLE listings_h3 (
  listing_id bigint NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
  h3_r7      h3index NOT NULL,
  h3_r8      h3index NOT NULL,
  PRIMARY KEY (listing_id)
);

CREATE INDEX listings_h3_r7_idx ON listings_h3 (h3_r7);
CREATE INDEX listings_h3_r8_idx ON listings_h3 (h3_r8);

-- Populate on insert / geometry change
CREATE OR REPLACE FUNCTION listings_h3_sync() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO listings_h3 (listing_id, h3_r7, h3_r8)
  VALUES (
    NEW.id,
    h3_lat_lng_to_cell(ST_Y(NEW.geom), ST_X(NEW.geom), 7),
    h3_lat_lng_to_cell(ST_Y(NEW.geom), ST_X(NEW.geom), 8)
  )
  ON CONFLICT (listing_id) DO UPDATE
    SET h3_r7 = EXCLUDED.h3_r7,
        h3_r8 = EXCLUDED.h3_r8;
  RETURN NEW;
END $$;

CREATE TRIGGER listings_h3_aiu
AFTER INSERT OR UPDATE OF geom ON listings
FOR EACH ROW EXECUTE FUNCTION listings_h3_sync();
```

## Aggregate query — price per sqm heatmap

```sql
CREATE OR REPLACE VIEW v_market_heatmap_r8 AS
SELECT
  h.h3_r8                                           AS cell,
  l.tenant_id,
  AVG(l.price / NULLIF(l.area_sqm, 0))              AS avg_price_per_sqm,
  COUNT(*)                                          AS listings,
  h3_cell_to_boundary(h.h3_r8)                       AS geom
FROM listings l
JOIN listings_h3 h ON h.listing_id = l.id
WHERE l.status IN ('active','sold')
GROUP BY h.h3_r8, l.tenant_id;
```

Query pattern with date window and small-N suppression:

```sql
SELECT cell,
       avg_price_per_sqm,
       listings,
       ST_AsGeoJSON(geom) AS geojson
FROM (
  SELECT h.h3_r8 AS cell,
         ROUND(AVG(l.price / NULLIF(l.area_sqm, 0)), 2) AS avg_price_per_sqm,
         COUNT(*) AS listings,
         h3_cell_to_boundary(h.h3_r8) AS geom
  FROM listings l
  JOIN listings_h3 h ON h.listing_id = l.id
  WHERE l.tenant_id = :tenant_id
    AND l.status IN ('active','sold')
    AND COALESCE(l.sold_date, l.listed_at) >= now() - make_interval(days => :days)
  GROUP BY h.h3_r8
) a
WHERE listings >= :min_n;            -- privacy + noise suppression
```

Parameters:

- `:days` — 90 or 180 for temporal windows.
- `:min_n` — 5 for dense markets, 10 for regulated contexts.

## Small-N suppression for privacy

Rules:

- **Hard suppress** any cell with fewer than `min_n` listings.
- **Do not return the cell at all** (do not return cell with a null value — it still leaks existence if combined with the grid).
- **Resolution cap** — do not let clients request resolution above 9 unless the payload passes the suppression rule.
- **Randomised rounding** for prices on tight cells when `min_n <= count < 2*min_n`: round to a coarser currency unit.

Log every request so audit can verify suppression held.

## Temporal heatmaps

Two patterns:

1. **Rolling window** — recompute over the last 90/180 days on demand.
2. **Snapshot table** — weekly snapshot stored separately so UI can show "change since last quarter".

### Snapshot table

```sql
CREATE TABLE market_snapshots (
  id               bigserial PRIMARY KEY,
  tenant_id        bigint NOT NULL,
  snapshot_date    date NOT NULL,
  cell             h3index NOT NULL,
  avg_price_per_sqm numeric,
  listings         int NOT NULL,
  UNIQUE (tenant_id, snapshot_date, cell)
);

-- Weekly insert
INSERT INTO market_snapshots (tenant_id, snapshot_date, cell, avg_price_per_sqm, listings)
SELECT l.tenant_id,
       current_date,
       h.h3_r8,
       AVG(l.price / NULLIF(l.area_sqm, 0)),
       COUNT(*)
FROM listings l
JOIN listings_h3 h ON h.listing_id = l.id
WHERE l.status IN ('active','sold')
  AND COALESCE(l.sold_date, l.listed_at) >= current_date - interval '90 days'
GROUP BY l.tenant_id, h.h3_r8
HAVING COUNT(*) >= 5;
```

### Change metric

```sql
WITH this_qtr AS (
  SELECT cell, avg_price_per_sqm
  FROM market_snapshots
  WHERE tenant_id = :tenant_id AND snapshot_date = :date_this
),
prev_qtr AS (
  SELECT cell, avg_price_per_sqm
  FROM market_snapshots
  WHERE tenant_id = :tenant_id AND snapshot_date = :date_prev
)
SELECT t.cell,
       t.avg_price_per_sqm                                   AS current,
       p.avg_price_per_sqm                                   AS previous,
       (t.avg_price_per_sqm - p.avg_price_per_sqm) /
         NULLIF(p.avg_price_per_sqm, 0) * 100                AS pct_change
FROM this_qtr t
LEFT JOIN prev_qtr p ON p.cell = t.cell;
```

## Choropleth rendering

Client-side with Mapbox GL / MapLibre:

```javascript
map.addSource('market-heatmap', {
  type: 'geojson',
  data: '/api/v1/market/heatmap?days=90&min_n=5&resolution=8'
});

map.addLayer({
  id: 'market-heatmap-fill',
  type: 'fill',
  source: 'market-heatmap',
  paint: {
    'fill-color': [
      'interpolate', ['linear'], ['get', 'avg_price_per_sqm'],
      500,  '#f7fbff',
      1000, '#c6dbef',
      1500, '#6baed6',
      2000, '#2171b5',
      3000, '#08306b'
    ],
    'fill-opacity': 0.7
  }
});
```

Rules for good choropleths:

- Use a perceptually uniform sequential ramp (ColorBrewer `Blues`, `YlOrRd`, Viridis).
- Use divergent ramps only for change metrics with a meaningful midpoint.
- Quantile classification for skewed distributions; equal-interval for uniform.
- Legend always visible; include the time window and `min_n`.
- Click-to-drill: tap a cell to list the contributing listings (respecting privacy rules).

## API shape

```text
GET /api/v1/market/heatmap?days=180&resolution=8&min_n=5

{
  "type": "FeatureCollection",
  "properties": {
    "tenant_id": 42,
    "window_days": 180,
    "min_n": 5,
    "resolution": 8,
    "metric": "avg_price_per_sqm",
    "currency": "UGX"
  },
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Polygon", "coordinates": [ ... ] },
      "properties": { "cell": "88...", "avg_price_per_sqm": 1245, "listings": 23 }
    }
  ]
}
```

Always echo `min_n` and `window_days` so the client can show provenance and so audit can verify compliance.

## Performance notes

- Precompute the heatmap per (tenant, resolution, window_days) on a schedule (every 1–6 hours) and serve from a cached GeoJSON or MVT endpoint.
- Serve as MVT (vector tiles) using `ST_AsMVT` over the precomputed cells for maps that zoom heavily.
- For large tenants, split by region and lazy-load.

## Anti-patterns

- Rendering a heatmap directly from `listings` on every request without aggregation.
- Using a rectangular grid for lat/lng cells — cell area warps badly away from the equator.
- Exposing resolution 10 cells without suppression — single-listing leak.
- Divergent colour ramps for purely positive metrics — misleads viewers.
- Forgetting tenant_id in the aggregate — cross-tenant leak disguised as "market data".

## Related references

- `property-search-spatial.md` — same schema, row-level queries.
- `neighbourhood-analysis.md` — listing-level version of price-per-sqm.
- `real-estate-saas-integration.md` — cache/serve strategy in the full architecture.
