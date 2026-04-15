# Catchment and Drive-Time Isochrones

Stand up drive/walk isochrones for real-estate search and catchment analysis. Covers self-hosted OSRM, Mapbox Isochrone API, and Google Distance Matrix as alternatives, plus the PostGIS cache schema, refresh policy, and per-tenant partitioning.

## When to use each provider

```text
Provider                Pros                                  Cons
----------------------  ------------------------------------  ------------------------------------
OSRM self-hosted        No per-query cost, full control       Setup cost, no live traffic
Valhalla self-hosted    Multi-modal, time-dependent           More complex install
Mapbox Isochrone API    Turnkey, traffic-aware                Per-request cost, rate limits
Google Distance Matrix  Traffic-aware, point-to-point only    No native polygon; you synthesise it
GraphHopper hosted      Similar to Mapbox                     Licensing terms by plan
```

Default recommendation: **OSRM self-hosted for batch and cache warmup**, **Mapbox Isochrone API for live UI requests** when live traffic matters. Google Distance Matrix is a fallback for markets where Mapbox coverage is weak.

## OSRM setup (Docker)

```bash
# Get an OSM extract
curl -L -o /data/osm/uganda-latest.osm.pbf \
  https://download.geofabrik.de/africa/uganda-latest.osm.pbf

# Prepare the car profile graph
docker run --rm -v /data/osm:/data osrm/osrm-backend \
  osrm-extract -p /opt/car.lua /data/uganda-latest.osm.pbf

docker run --rm -v /data/osm:/data osrm/osrm-backend \
  osrm-partition /data/uganda-latest.osrm

docker run --rm -v /data/osm:/data osrm/osrm-backend \
  osrm-customize /data/uganda-latest.osrm

# Run the routing server
docker run -d --name osrm-car -p 5000:5000 \
  -v /data/osm:/data osrm/osrm-backend \
  osrm-routed --algorithm mld /data/uganda-latest.osrm
```

Repeat for `foot.lua` and `bicycle.lua` on separate ports (5001, 5002).

### Generate an isochrone from OSRM

OSRM does not generate isochrone polygons directly. Synthesise them:

1. Sample a grid or radial set of destination points around the origin.
2. Call `/table/v1/driving/{origin};{d1};{d2};...` to get travel times.
3. Build a concave hull from points within the threshold.

```javascript
// Node.js sketch
import fetch from 'node-fetch';
import concaveman from 'concaveman';

async function isochrone(origin, minutes, profile = 'car') {
  const port = { car: 5000, foot: 5001, bike: 5002 }[profile];
  const radiusKm = profile === 'car' ? 20 : 5;
  const grid = buildGrid(origin, radiusKm, 40); // ~1600 points

  const coords = [origin, ...grid].map(p => `${p.lng},${p.lat}`).join(';');
  const url = `http://localhost:${port}/table/v1/driving/${coords}?sources=0`;
  const res = await fetch(url).then(r => r.json());

  const secs = res.durations[0];
  const within = grid.filter((_, i) => secs[i + 1] !== null && secs[i + 1] <= minutes * 60);
  const polygon = concaveman(within.map(p => [p.lng, p.lat]), 2);
  return polygon; // ring of [lng, lat]
}
```

Trade-off: larger grid = smoother polygon, but exponentially larger table call.

## Mapbox Isochrone API

```bash
curl "https://api.mapbox.com/isochrone/v1/mapbox/driving/${LNG},${LAT}?\
contours_minutes=10,20,30&polygons=true&access_token=${MAPBOX_TOKEN}"
```

Returns a FeatureCollection with one polygon per minute threshold. Use directly, or store in PostGIS.

Rate limits:

- 300 requests per minute per token (at 2026 Mapbox defaults).
- Cache aggressively; live traffic changes matter little for 10–30 minute isochrones unless rush hour.

## PostGIS cache schema

```sql
CREATE TABLE isochrones (
  id           bigserial PRIMARY KEY,
  tenant_id    bigint NOT NULL,
  origin       geometry(Point, 4326) NOT NULL,
  origin_hash  text GENERATED ALWAYS AS (md5(ST_AsText(ST_SnapToGrid(origin, 0.0001)))) STORED,
  mode         text NOT NULL CHECK (mode IN ('driving','walking','cycling','transit')),
  minutes      int NOT NULL CHECK (minutes BETWEEN 5 AND 60),
  provider     text NOT NULL CHECK (provider IN ('osrm','mapbox','google','valhalla')),
  geom         geometry(Polygon, 4326) NOT NULL,
  computed_at  timestamptz NOT NULL DEFAULT now(),
  expires_at   timestamptz NOT NULL,
  UNIQUE (tenant_id, origin_hash, mode, minutes, provider)
);

CREATE INDEX isochrones_geom_gix ON isochrones USING GIST (geom);
CREATE INDEX isochrones_expires_idx ON isochrones (expires_at);
```

`ST_SnapToGrid(origin, 0.0001)` is ~11 m; it lets nearby requests share a cache entry without materially changing the answer.

## Refresh policy

```text
Provider     Default TTL   Invalidate on
-----------  ------------  -----------------------------------------------------
OSRM         30 days       OSM import / new routing graph
Valhalla     30 days       Graph rebuild
Mapbox       7 days        Tenant-driven refresh, traffic insensitivity allowance
Google       3 days        High traffic sensitivity markets, shorter
```

Rebuild isochrones when:

- Major road network change (new motorway, closure).
- Public transport schedule change (for transit mode).
- Tenant requests a fresh computation.
- `expires_at < now()` and the entry is requested.

## Fetch-or-compute pattern

```sql
-- 1. Look up
SELECT geom
FROM isochrones
WHERE tenant_id = :tenant_id
  AND origin_hash = md5(ST_AsText(ST_SnapToGrid(ST_SetSRID(ST_Point(:lng, :lat), 4326), 0.0001)))
  AND mode = :mode
  AND minutes = :minutes
  AND provider = :provider
  AND expires_at > now()
LIMIT 1;
```

If no hit, compute, then:

```sql
INSERT INTO isochrones (tenant_id, origin, mode, minutes, provider, geom, expires_at)
VALUES (:tenant_id,
        ST_SetSRID(ST_Point(:lng, :lat), 4326),
        :mode, :minutes, :provider,
        ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326),
        now() + interval '30 days')
ON CONFLICT (tenant_id, origin_hash, mode, minutes, provider)
DO UPDATE SET geom = EXCLUDED.geom,
              computed_at = now(),
              expires_at = EXCLUDED.expires_at;
```

## Using an isochrone in search

"Listings reachable in 20 minutes driving from a point":

```sql
WITH iso AS (
  SELECT geom FROM isochrones
  WHERE tenant_id = :tenant_id AND origin_hash = :h
    AND mode = 'driving' AND minutes = 20 AND provider = 'mapbox'
  ORDER BY computed_at DESC LIMIT 1
)
SELECT l.*
FROM listings l, iso
WHERE l.tenant_id = :tenant_id
  AND l.status = 'active'
  AND ST_Covers(iso.geom, l.geom);
```

Always filter on `tenant_id` and check the isochrone was computed for this tenant's parameters.

## Per-tenant partitioning

For SaaS with many tenants:

- Partition `isochrones` by `tenant_id` (range or list partitioning) once the table exceeds a few hundred thousand rows.
- Keep a per-tenant cap: `DELETE FROM isochrones WHERE tenant_id = :t AND computed_at < now() - interval '90 days' AND id NOT IN (SELECT id ...)`.
- Attribute provider cost back to tenants via a ledger (see `ai-metering-billing` for the shape; reuse for isochrone costs).

## Pre-warming

For popular search origins (city centres, transit hubs), precompute a grid of isochrones nightly so the UI is instant.

```bash
# pseudocode
for origin in popular_origins:
  for mode in [driving, walking]:
    for m in [10, 20, 30]:
      upsert_isochrone(origin, mode, m)
```

## Rate limiting and cost guardrails

- Enforce a per-tenant isochrone quota per day on external providers.
- Reject isochrone requests whose `minutes > 60` or `origin` is outside the tenant's supported regions.
- Log every external provider call with tenant, origin, cost estimate, and cache outcome (hit/miss).
- Alarm when miss rate exceeds a threshold; it usually means a bug in the hash or TTL.

## Anti-patterns

- Calling the provider on every map pan; cache by snapped origin.
- Storing different provider outputs in the same row without the `provider` column — you cannot compare later.
- Forgetting to include `tenant_id` in the uniqueness constraint — cross-tenant leakage.
- Using straight-line buffers and calling them "drive-time".
- Building isochrones synchronously in a request path that also writes them — split fetch vs compute.
- No TTL on cached polygons — they get stale quietly.

## Related references

- `property-search-spatial.md` — combine isochrone filter with other filters.
- `neighbourhood-analysis.md` — transit walk times complement driving isochrones.
- `real-estate-saas-integration.md` — where the isochrone service sits in the overall architecture.
