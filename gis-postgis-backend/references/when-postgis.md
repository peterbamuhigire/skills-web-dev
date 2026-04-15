# When To Use PostGIS

Decision rules for choosing a spatial data store. PostGIS is the default beyond trivial point-in-circle work, but not every project needs it.

## Quick decision matrix

```text
Requirement                                        Store
-----------------------------------------------    -------------------------------
Two points + distance on existing MySQL app        MySQL spatial (ST_Distance_Sphere)
Point-in-polygon, intersects, buffer, union        PostGIS
Nearest-N with index-assisted KNN                  PostGIS (<-> operator)
Vector tiles for web maps                          PostGIS (ST_AsMVT)
Geofences, service areas, catchment                PostGIS
Global write-heavy telemetry (> 50k/s)             TimescaleDB + PostGIS, or geo DB
Real-time device tracking, low-latency reads       Redis GEO + PostGIS for analytics
Massive ArcGIS ecosystem, enterprise               ArcGIS Enterprise (see gis-enterprise-domain)
Single-instance mobile/desktop spatial             SQLite + SpatiaLite
```

## MySQL spatial vs PostGIS

MySQL 8 has `POINT`, `ST_Distance_Sphere`, `ST_Contains`, `ST_Within` and SRID-aware R-tree indexes. It is enough when:

- All you do is find rows within N metres of a point.
- The dataset is modest (< 1 million spatial rows per tenant).
- Nobody needs buffers, unions, MVT tiles, or isochrones.
- The team already operates MySQL and cannot take on a second engine.

Move to PostGIS when any of the following become true:

- You need `ST_Buffer`, `ST_Union`, `ST_Intersection`, `ST_Subdivide`, `ST_ClusterKMeans`, `ST_ConcaveHull`.
- You need to serve Mapbox Vector Tiles from SQL.
- You need KNN via `<->` with index assistance (MySQL's sort is unindexed).
- You need `geography` type for correct metre distances across continents.
- You need `ST_DWithin` semantics (index-using radius search).
- You need routing (pgRouting), raster (postgis_raster), or topology.

## PostGIS vs specialised stores

| Workload | Recommended | Why |
| --- | --- | --- |
| Property listings, zones, service areas | PostGIS | General-purpose, SQL, broad tooling |
| Fleet telemetry, 100k+ points/sec | TimescaleDB + PostGIS extension | Hypertable partitioning on time, PostGIS for geometry |
| Sub-10ms "nearest driver" lookups | Redis GEO + PostGIS for analytics | In-memory geohash index |
| Full-text + geo (listings with search) | PostGIS + `pg_trgm` or Elasticsearch geo | Choose Elasticsearch only if search is the primary workload |
| Raster (satellite imagery) | PostGIS raster, or object storage + COG | Do not shove TIFFs into `bytea` |
| Enterprise mapping portal | ArcGIS Enterprise | See `gis-enterprise-domain` |

## Query-complexity threshold

Rough rule, per tenant:

```text
Rows    Queries per second    Spatial ops
------  --------------------  -------------------------------------------
< 10k   < 10                  Anything works; stay on existing DB
< 1M    < 100                 MySQL spatial if ops are point-distance
< 10M   < 500                 PostGIS, single node, GIST indexes
> 10M   > 500                 PostGIS + partitioning, connection pool, replicas
> 100M  or heavy analytics    PostGIS + Citus, or dedicated analytics cluster
```

## Team-readiness check

Before introducing PostGIS, confirm the team can:

1. Operate a second database (backups, monitoring, upgrades).
2. Read `EXPLAIN ANALYZE` for spatial plans.
3. Debug SRID mismatches (the silent index-killer).
4. Keep PostGIS version aligned across dev, staging, production.
5. Sync data from MySQL if the main app stays there (see `references/hybrid-mysql-postgis.md`).

If no, consider staying on MySQL spatial for a prototype and revisiting when spatial features graduate to a revenue-critical path.

## Real-estate example (from the source text)

Real-estate SaaS typically needs: draw-a-polygon search, nearest schools/transit, catchment area, price heatmaps, MVT tiles for listings at zoom 12-18. That is squarely PostGIS territory. MySQL spatial cannot serve tiles or compute catchments cheaply.

## Anti-patterns

- Choosing PostGIS for a two-query MVP because "spatial is cool". Operational cost is real.
- Refusing PostGIS after the third `ST_Buffer` workaround in MySQL. You are paying the cost without the benefit.
- Introducing a third store (Elasticsearch, Redis GEO) before PostGIS is saturated.
- Running PostGIS on an app-server box with 2 GB RAM and expecting GIST to fly.

## Cross-reference

- `postgresql-fundamentals` — Postgres basics before PostGIS.
- `postgresql-performance` — index strategy and `EXPLAIN` reading.
- `gis-mapping` — Leaflet frontend that consumes PostGIS output.
- `gis-enterprise-domain` — ArcGIS Enterprise path.
- `references/hybrid-mysql-postgis.md` — keeping MySQL as system of record.
