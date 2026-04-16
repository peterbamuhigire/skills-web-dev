---
name: gis-enterprise-domain
description: Use when administering ArcGIS Enterprise or building real-estate-specific
  GIS features — ArcGIS components, publishing services, security/roles, backup/DR,
  plus property search, neighbourhood analysis, catchment/isochrones, market heatmaps,
  and real-estate-SaaS integration.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Enterprise and Domain GIS

<!-- dual-compat-start -->
## Use When

- Use when administering ArcGIS Enterprise or building real-estate-specific GIS features — ArcGIS components, publishing services, security/roles, backup/DR, plus property search, neighbourhood analysis, catchment/isochrones, market heatmaps, and real-estate-SaaS integration.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `gis-enterprise-domain` or would be better handled by a more specific companion skill.
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
| Operability | ArcGIS Enterprise admin runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` covering portal, Server, and Data Store ops | `docs/gis/arcgis-runbook.md` |
| Data safety | Real-estate domain data model | Markdown doc per `skill-composition-standards/references/entity-model-template.md` covering parcel, ownership, and valuation entities | `docs/gis/real-estate-model.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
ArcGIS Enterprise administration for regulated / established GIS environments, plus real-estate-specific GIS patterns that map cleanly to PostGIS + map clients.

**Prerequisites:** Load `gis-postgis-backend` for the spatial backend, `gis-mapping` or `gis-maps-integration` for the map client, and `multi-tenant-saas-architecture` for tenant isolation.

## When this skill applies

- Operating or integrating with ArcGIS Enterprise (Portal, Server, Data Store, Web Adaptor).
- Publishing authoritative GIS services (map, feature, image, geocoding).
- Designing GIS features for real estate: property search, neighbourhood analysis, catchment, market heatmaps.
- Building a real-estate SaaS that needs spatial features at a high bar.

## When ArcGIS Enterprise is right

```text
Government / regulated sector with ArcGIS mandated               -> ArcGIS Enterprise
Team already trained on ArcGIS Pro                               -> ArcGIS Enterprise
Need authoritative imagery/demographics datasets under licence    -> ArcGIS Online/Enterprise
Small startup, modern stack, cost-sensitive                       -> PostGIS + Mapbox/MapLibre
You need ESRI-specific analytical tools (Network Analyst)        -> ArcGIS Enterprise
```

Most SaaS startups pick the PostGIS + OSS map stack. ArcGIS Enterprise earns its cost in sectors where it's already the standard (government, utilities, defence) or when licenced datasets are critical.

See `references/when-arcgis-enterprise.md`.

## ArcGIS Enterprise components

- **Portal for ArcGIS** — identity, sharing, groups, content catalogue.
- **ArcGIS Server** — publishes services (map, feature, image, geoprocessing, geocoding).
- **Data Store** — relational, tile, and spatiotemporal data backends.
- **Web Adaptor** — IIS/Java web server integration for HTTPS, custom URLs.

Typical base deployment: one of each, highly available variant adds replication for each.

See `references/arcgis-components.md`.

## Publishing services

- **Feature services** — CRUD + query on features, the workhorse for interactive apps.
- **Map services** — pre-rendered tiles for fast display at fixed scales.
- **Image services** — raster data (imagery, DEM).
- **Geocoding services** — address to coordinate.
- **GeoProcessing services** — spatial analysis functions as endpoints.

**Versioning:** branch versioning for concurrent editing without conflicts; default version for most read workloads.

See `references/publishing-services.md`.

## Security + roles

Portal users assigned roles: Viewer, Data Editor, Publisher, Administrator. Groups control sharing.

Server-side Role-Based Access Control on published services. Integrate with enterprise IdP (SAML / OIDC).

Audit logs — enable and ship to the SIEM.

See `references/arcgis-security-roles.md`.

## Backup + DR

```text
1. Portal content — webgisdr utility (export + import).
2. Data Store — automated backups + geo-replicate for HA.
3. Server config — backup the machine's `config-store` directory.
4. Web Adaptor — stateless, reinstall from config.
5. Restore drill quarterly.
```

webgisdr is authoritative for Portal/Server/Data Store coordinated backup.

See `references/arcgis-backup-dr.md`.

## Real estate GIS recipes

### Property search with spatial filters

Filter by district/neighbourhood + within walking distance to transit + inside a school zone:

```sql
WITH search_area AS (
  SELECT ST_Union(geom) AS geom FROM districts WHERE code IN ('KAM01', 'KAM02')
), school_zones AS (
  SELECT ST_Union(geom) AS geom FROM zones WHERE type = 'school' AND rating >= 4
), transit AS (
  SELECT ST_Buffer(geom::geography, 800)::geometry AS geom FROM transit_stops  -- 800m walking
)
SELECT l.*
FROM listings l
JOIN search_area s ON ST_Contains(s.geom, l.geom)
JOIN school_zones sz ON ST_Contains(sz.geom, l.geom)
JOIN LATERAL (SELECT 1 FROM transit t WHERE ST_Intersects(t.geom, l.geom) LIMIT 1) tr ON TRUE
WHERE l.tenant_id = :tenant_id AND l.status = 'active';
```

See `references/property-search-spatial.md`.

### Neighbourhood analysis

For a listing, compute:

- **Walk score** — count of amenities within 800m / 1600m weighted by category.
- **Transit access** — nearest N transit stops with travel time.
- **Comparables** — similar listings within 2 km in last 180 days.
- **Demographics** — join to census or tenant-provided block statistics.

Cache per-listing summaries; refresh nightly.

See `references/neighbourhood-analysis.md`.

### Catchment / drive-time isochrones

- Simple: buffer by straight-line distance.
- Better: drive-time isochrones from OSRM, Mapbox Isochrone API, or Google Distance Matrix.
- Cache isochrone polygons in PostGIS; key by (point, mode, minutes).
- Use in "find listings I can reach in 20 minutes" features.

```sql
CREATE TABLE isochrones (
  id serial PRIMARY KEY,
  point geometry(Point, 4326) NOT NULL,
  mode text NOT NULL,
  minutes int NOT NULL,
  geom geometry(Polygon, 4326) NOT NULL,
  computed_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (point, mode, minutes)
);
```

See `references/catchment-isochrones.md`.

### Market heatmaps

Heatmap of listing price per square metre by small area (H3 hex index, grid, or admin boundary):

```sql
SELECT h.cell, AVG(l.price_per_sqm) AS avg_price, COUNT(*) AS listings
FROM listings l
JOIN h3_cells_resolution_8 h ON h3_indexes_contain(h.cell, l.geom)
WHERE l.tenant_id = :tenant_id AND l.sold_date > now() - interval '180 days'
GROUP BY h.cell
HAVING COUNT(*) >= 5;
```

Render client-side as a choropleth on Mapbox/MapLibre. Suppress cells with low N to avoid privacy + noise.

See `references/market-heatmaps.md`.

### Real-estate-SaaS integration

Architecture:

```text
Web app (Next.js/React)
  -> API (Fastify/PHP) reads MySQL listings table
  -> API joins to PostGIS for spatial queries
  -> Client renders map (Mapbox GL with MVT tiles from PostGIS)
  -> Geocoding via Google Places (cached)
  -> Isochrones via Mapbox Isochrone (cached in PostGIS)
```

Keep transactional listing data in MySQL; keep spatial in PostGIS; keep them linked by `listing_id`.

See `references/real-estate-saas-integration.md`.

## Anti-patterns

- Double-entry of property location in MySQL and PostGIS without a canonical source.
- Heatmaps rendered per-request without caching (expensive queries every pan/zoom).
- Isochrones computed live instead of cached.
- Exposing raw ArcGIS service URLs on the public internet without auth and rate limits.
- ArcGIS Enterprise on a single node for production (no HA).
- No webgisdr backup schedule.
- Publishing feature services without field-level visibility rules for multi-tenant contexts.

## Read next

- `gis-postgis-backend` — spatial backbone.
- `gis-maps-integration` — client mapping.
- `multi-tenant-saas-architecture` — tenant isolation end-to-end.

## References

- `references/when-arcgis-enterprise.md`
- `references/arcgis-components.md`
- `references/publishing-services.md`
- `references/arcgis-security-roles.md`
- `references/arcgis-backup-dr.md`
- `references/property-search-spatial.md`
- `references/neighbourhood-analysis.md`
- `references/catchment-isochrones.md`
- `references/market-heatmaps.md`
- `references/real-estate-saas-integration.md`
