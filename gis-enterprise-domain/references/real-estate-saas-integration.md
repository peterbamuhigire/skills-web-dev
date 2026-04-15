# Real-Estate SaaS GIS Integration Architecture

Reference architecture for a multi-tenant real-estate SaaS that keeps transactional data in MySQL, spatial in PostGIS, and serves clients via Mapbox GL on web and native map SDKs on mobile. Covers listing sync, search API shape, mobile integration, and operational concerns.

## Target architecture

```text
+------------------+     +----------------------+
| Web app (Next.js)|     | Mobile (iOS, Android)|
| Mapbox GL JS     |     | Mapbox Maps SDK      |
+---------+--------+     +-----------+----------+
          | HTTPS                    | HTTPS
          v                          v
+-----------------------------------------------+
| API gateway (Fastify or PHP)                  |
| - Auth (dual auth: Session + JWT)             |
| - Rate limiting, tenant injection             |
+-----+---------+--------------------+----------+
      |         |                    |
      v         v                    v
+-----------+ +---------+ +--------------------+
| MySQL 8   | | PostGIS | | External services  |
| Listings, | | Spatial | | - Mapbox Isochrone |
| users,    | | features| | - Google Places /  |
| billing,  | | tiles,  | |   geocoding        |
| RBAC,     | | H3 cells| | - OSRM (self-host) |
| audit     | |         | |                    |
+-----------+ +---------+ +--------------------+
      ^         ^
      |         |
      +----+----+
           |
        sync worker
        (listing_id is the join key)
```

Key design rules:

- **Single source of truth per fact.** Listing attributes (price, beds) live in MySQL. Listing geometry lives in PostGIS. `listing_id` is the join key.
- **Tenant isolation everywhere.** Every table, every query, every cache key carries `tenant_id`.
- **Spatial never leaves the spatial tier.** API composes but never cross-queries MySQL ↔ PostGIS in a single SQL statement; the API layer joins in code.
- **External calls are cached.** Isochrones, geocoding, places — all behind PostGIS cache tables with TTL.

## Data split

### MySQL (app DB)

```sql
-- MySQL 8
CREATE TABLE tenants (
  id           BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  slug         VARCHAR(64) NOT NULL UNIQUE,
  name         VARCHAR(255) NOT NULL,
  status       ENUM('active','suspended','trial') NOT NULL,
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE listings (
  id             BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  tenant_id      BIGINT UNSIGNED NOT NULL,
  external_ref   VARCHAR(64) NOT NULL,
  title          VARCHAR(255) NOT NULL,
  description    MEDIUMTEXT,
  status         ENUM('draft','active','pending','sold','expired') NOT NULL,
  price          DECIMAL(14,2),
  currency       CHAR(3) NOT NULL DEFAULT 'UGX',
  bedrooms       TINYINT UNSIGNED,
  bathrooms      TINYINT UNSIGNED,
  area_sqm       DECIMAL(10,2),
  lat            DECIMAL(9,6),
  lng            DECIMAL(9,6),
  listed_at      DATETIME NOT NULL,
  sold_at        DATETIME,
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY u_listing_ext (tenant_id, external_ref),
  KEY k_tenant_status (tenant_id, status),
  CONSTRAINT fk_listing_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
```

### PostGIS (spatial)

```sql
-- PostgreSQL 16 + PostGIS 3
CREATE TABLE listings_spatial (
  id             bigserial PRIMARY KEY,
  tenant_id      bigint NOT NULL,
  listing_id     bigint NOT NULL,       -- FK-by-convention to MySQL
  status         text NOT NULL,
  geom           geometry(Point, 4326) NOT NULL,
  updated_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, listing_id)
);
CREATE INDEX listings_spatial_tenant_status_idx ON listings_spatial (tenant_id, status);
CREATE INDEX listings_spatial_geom_gix          ON listings_spatial USING GIST (geom);
```

Plus tables from `neighbourhood-analysis.md`, `catchment-isochrones.md`, and `market-heatmaps.md`.

## Listing sync

Sync is event-driven. MySQL writes emit an event consumed by a sync worker that upserts into PostGIS.

### Event shape

```json
{
  "event": "listing.upserted",
  "tenant_id": 42,
  "listing_id": 10234,
  "status": "active",
  "lat": 0.3136,
  "lng": 32.5811,
  "updated_at": "2026-04-15T09:21:00Z"
}
```

Transport options (pick one, not all):

- Outbox pattern in MySQL + cron/relay worker → PostGIS. Simplest and robust.
- Kafka / RabbitMQ topic if the rest of the platform already uses it.
- Change Data Capture (Debezium) if volume justifies the ops cost.

### Worker upsert

```sql
-- PostGIS
INSERT INTO listings_spatial (tenant_id, listing_id, status, geom)
VALUES ($1, $2, $3, ST_SetSRID(ST_Point($5, $4), 4326))
ON CONFLICT (tenant_id, listing_id)
DO UPDATE SET status = EXCLUDED.status,
              geom = EXCLUDED.geom,
              updated_at = now();
```

Delete path: soft-delete in MySQL -> emit `listing.deleted` -> hard-delete in PostGIS (listing aggregates need to recompute). Do not leave stale geometries around.

### Reconciliation

A nightly reconciliation job compares counts and hashes between MySQL and PostGIS per tenant; raises an alarm on drift beyond a small tolerance.

## Search API (example shape)

```text
POST /api/v1/listings/search
Body:
{
  "tenant_scope_implicit": true,
  "bbox": [32.55, 0.30, 32.62, 0.34],
  "filters": {
    "price_max": 250000,
    "bedrooms_min": 2,
    "walk_to_transit_m": 800,
    "school_min_rating": 4,
    "within_isochrone": {
      "origin": { "lat": 0.3136, "lng": 32.5811 },
      "mode": "driving",
      "minutes": 20
    }
  },
  "sort": "newest",
  "page": 1,
  "page_size": 25
}
```

Resolution order inside the API:

1. Resolve tenant from the session/JWT. Reject if mismatch with payload.
2. If `within_isochrone` is set, fetch-or-compute isochrone (see `catchment-isochrones.md`).
3. Run spatial filter in PostGIS to get candidate `listing_id`s.
4. Join back to MySQL for full listing attributes (price, title, images).
5. Apply non-spatial filters and sort in MySQL (bedrooms, price) or compose in app code.
6. Return paginated results.

Implementation tip: keep spatial queries under 200 ms p95 by returning only `listing_id`s from PostGIS, then fetching 25 rows by primary key from MySQL.

## Tile / map rendering

Serve vector tiles from PostGIS via `ST_AsMVT` for interactive maps at scale.

```sql
CREATE OR REPLACE FUNCTION tile_listings(z int, x int, y int, p_tenant bigint)
RETURNS bytea
LANGUAGE sql STABLE PARALLEL SAFE AS $$
  WITH mvt AS (
    SELECT ST_AsMVTGeom(s.geom, ST_TileEnvelope(z, x, y),
                        extent => 4096, buffer => 64) AS geom,
           s.listing_id, s.status
    FROM listings_spatial s
    WHERE s.tenant_id = p_tenant
      AND s.status = 'active'
      AND s.geom && ST_TileEnvelope(z, x, y)
  )
  SELECT ST_AsMVT(mvt, 'listings', 4096, 'geom') FROM mvt;
$$;
```

Gateway route: `GET /api/v1/tiles/listings/{z}/{x}/{y}.mvt`. Short CDN TTL (30–60 s), cache key includes `tenant_id`.

## Mobile integration (iOS / Android)

- Use the Mapbox Maps SDK (or MapLibre Native) with the same style as the web app for parity.
- Listings layer = vector tile source pointing at `/api/v1/tiles/listings/...mvt`.
- Listing detail = standard REST call by `listing_id`.
- Offline: bundle a base style + download a limited region pack. Do **not** try to pack listings offline — serve from cache with TTL.
- Location-based search: capture user coordinates, call `/search` with bbox around the user.
- Feature cluster rendering client-side with Mapbox cluster API on the vector tile source.

Mobile rules:

- All Mapbox tokens must be fetched from the API at startup; do not bake secrets into the binary (see `ios-app-security`, `vibe-security-skill`).
- Never send coarse location to the server if the tenant's policy requires fine-grain consent first.
- Geofence triggers (`is this listing in my area?`) should be validated server-side too.

## Geocoding strategy

- Use Google Places or Mapbox Geocoding for address autocomplete.
- Cache the geocoded result in a `geocoded_addresses` table keyed by provider and normalised query string, with TTL 90 days.
- Never send live user keystrokes straight to the provider without debounce + per-tenant rate limit.

## Caching surfaces

```text
Layer                Store            TTL            Invalidation
-------------------  ---------------  -------------  --------------------------------
Listing detail       Redis            5 min          listing.upserted event
Search results       Redis            30–120 sec     listing.upserted event (pattern)
Isochrone            PostGIS          7–30 days      Provider refresh / graph rebuild
Geocoded address     PostGIS          90 days        Manual purge
Vector tiles         CDN              30–60 sec      Tenant tile tag version bump
Heatmap GeoJSON      Object storage   1–6 hours      Scheduled rebuild
```

## Operational concerns

- **Observability** — every search and tile request emits a span tagged with tenant_id, filter shape, result count, and latency. Alerts on p95 breaches.
- **Cost attribution** — external provider calls (Mapbox, Google) are written to a ledger with `tenant_id`; the billing module charges back or enforces quotas.
- **Data retention** — sold listings retain geometry for N years for market heatmaps, then are anonymised (geometry snapped to a coarse grid) per data-protection policy.
- **DPIA / DPPA** — pair with `uganda-dppa-compliance` for Uganda deployments; location data is personal data when tied to a user.
- **Backup** — MySQL and PostGIS have independent backup schedules but a coordinated recovery plan. Document the order of restore (MySQL first, then PostGIS replay).

## Deployment footprint

Small SaaS on a single VPS is possible for MVP but separate MySQL and PostGIS onto their own instances before scaling users past a few hundred per tenant.

```text
Tier         Web/API    MySQL       PostGIS     Redis    Workers
-----------  ---------  ----------  ----------  -------  --------
MVP          1 x 4GB    shared      shared      shared   1
Production   2 x 4GB    2 x 8GB HA  2 x 8GB HA  1 x 2GB  2
Scale        n x 4GB    RDS/Aurora  Managed PG  Managed  n
```

## Anti-patterns

- Cross-tier SQL joins (MySQL ↔ PostGIS). Use ID-based composition in the API layer instead.
- Double-writing location to MySQL and PostGIS from the request path without a sync worker — half-updated state is inevitable.
- Shipping Mapbox tokens to the mobile app as hard-coded strings.
- Exposing PostGIS directly to the internet; always fronted by the API.
- Skipping tenant filter on tile endpoints — tile caches leak across tenants instantly.
- Caching isochrones without including `tenant_id` in the key (if tenants configure their own provider accounts).
- No reconciliation job — drift between MySQL and PostGIS accumulates invisibly.

## Related references

- `property-search-spatial.md` — the search SQL this architecture serves.
- `neighbourhood-analysis.md` — per-listing enrichment pipelines.
- `catchment-isochrones.md` — caching pattern for external routing.
- `market-heatmaps.md` — aggregate views on the same data.
- `gis-postgis-backend` skill — backend patterns.
- `gis-maps-integration` skill — Mapbox/Google client patterns.
- `multi-tenant-saas-architecture` skill — tenant isolation guarantees.
