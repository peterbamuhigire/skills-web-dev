# Publishing Services on ArcGIS Enterprise

Covers map, feature, image, geocoding, and geoprocessing services; branch vs traditional versioning; caching strategy; and a concrete publishing workflow.

## Service types and when to use each

```text
Service type       Best for                                       Backing data
-----------------  ---------------------------------------------  ----------------------
Map service        Styled map layers (dynamic or tiled)           ArcSDE, file GDB, shp
Feature service    Editable or queryable vector features, REST    Hosted or registered DB
Vector tile svc    Fast styled vector tiles at all zoom levels     Vector tile package (VTPK)
Image service      Raster, imagery, DEM, mosaic datasets           Mosaic dataset, raster
Scene service      3D buildings, meshes, point clouds              Scene layer package (SLPK)
Geocoding svc      Address-to-coordinate, reverse geocoding        Locator file (.loc)
GeoProcessing svc  Analytic tool as an HTTP endpoint               Python toolbox / model
Network Analysis   Routing, service area, closest facility         Network dataset
```

Rule of thumb: expose **feature services** for interactive editing and query; expose **vector tile services** for fast styled read; expose **map services** only when you need legacy dynamic rendering or a specific cartographic style that vector tiles cannot reproduce.

## Hosted vs registered data

- **Hosted feature layers** — data lives in the Portal's relational Data Store. Easiest to publish, fewest moving parts, good for new data.
- **Registered (referenced) services** — data lives in your own enterprise geodatabase (SQL Server, Oracle, PostgreSQL with ArcSDE). Use when the data is the authoritative system of record and you cannot copy it.

Pick hosted when you can, registered when you must.

## Versioning: traditional vs branch

| Aspect | Traditional versioning | Branch versioning |
| --- | --- | --- |
| Storage | Delta tables (A/D) in SDE | Archive-based, row-level |
| Concurrent editing | Yes, reconcile/post model | Yes, simpler merge model |
| Requires SDE compression | Yes, regular maintenance | No |
| Service type support | Map services | Feature services only |
| Web-friendly | Less | Yes, designed for web |
| Recommended for new work | No | Yes |

Use **branch versioning** for all new editable feature services. Keep **traditional versioning** only where a legacy Parcel Fabric or asset model depends on it.

## Caching strategy

Map tile and vector tile caches dramatically reduce load but have lifecycle cost.

Decision rules:

- Features change hourly or faster, audience small -> skip cache, serve dynamic.
- Features change daily, audience large -> build tiled vector tile cache, rebuild nightly.
- Features static, audience large -> full pre-built cache, rebuild monthly.
- Raster / imagery -> always cached; build on ingest.

Cache build levers:

```text
Lever                    Impact
-----------------------  ----------------------------------------------
Scale levels             Drives disk + build time exponentially
Cache format             Exploded vs compact; compact saves disk
On-demand vs pre-built   On-demand = cheaper build, slower first request
Antialiasing             Higher quality, bigger tiles
```

For web basemaps, use vector tile packages (VTPK) published as vector tile services; they are resolution-independent and much smaller than raster tile caches.

## Publishing workflow (standard recipe)

```text
1. Prepare data in ArcGIS Pro
     - Project to the service SRID (usually Web Mercator 3857).
     - Fix geometry errors (Check Geometry / Repair Geometry).
     - Add indexes on commonly filtered attributes.
     - Define domains, subtypes, and field aliases.
2. Author the map
     - Symbology, labelling, scale ranges, definition queries.
     - Use scale-dependent drawing for cartographic clarity.
3. Share as web layer
     - Choose feature / tile / vector tile target.
     - Set summary, tags, licence, description for discovery.
     - Target folder and sharing (Portal group).
4. Analyze
     - Resolve every error. Address warnings intentionally.
5. Publish
     - To the federated hosting Server.
6. Configure service properties
     - Pool sizes (min/max instances), timeouts, caching, max record count.
     - Capabilities: Query, Create, Update, Delete, Sync, Extract.
7. Apply security
     - Sharing: private / group / org / public.
     - RBAC on the Server side if needed.
8. Register in the organisation catalogue
     - Item thumbnail, documentation link, data owner.
9. Smoke test
     - Query a known feature via the REST endpoint.
     - Render via web map; verify scale ranges.
10. Release and monitor
     - Usage reports, logs, alerts.
```

## Service configuration cheats

- **Max record count** — default 1000. Raise for feature services serving analytics clients; never remove entirely or clients can DoS the service.
- **Instances per machine** — drives concurrency and RAM use. Start low, raise under load.
- **Timeouts** — tune `usage timeout`, `wait timeout`, `idle timeout` to match the slowest legitimate request.
- **Sync** — enable only when Field Maps or Survey123 offline is a real requirement; it doubles storage and complicates versioning.

## Geocoding and geoprocessing publishing specifics

Geocoding services need a **locator (.loc)** built from an authoritative address dataset. Publish once, consume widely. Keep a refresh pipeline (monthly or quarterly) to re-index new addresses.

Geoprocessing services should be built from ModelBuilder models or Python toolboxes that were run successfully in ArcGIS Pro. Expose them as **synchronous** only for fast (under 30s) tools; everything else should be **asynchronous** with job-id polling.

```python
# Python toolbox sketch for a geoprocessing service
import arcpy

class Toolbox(object):
    def __init__(self):
        self.label = "Neighbourhood Tools"
        self.alias = "nhood"
        self.tools = [WalkScore]

class WalkScore(object):
    def __init__(self):
        self.label = "Compute Walk Score"

    def getParameterInfo(self):
        return [
            arcpy.Parameter("listing_point", "Listing Point",
                            "Input", "GPFeatureRecordSetLayer", "Required"),
            arcpy.Parameter("score", "Walk Score",
                            "Output", "GPLong", "Derived"),
        ]

    def execute(self, params, messages):
        point = params[0].value
        # ... spatial analysis ...
        params[1].value = int(score)
```

Publish the toolbox result as a geoprocessing service.

## Anti-patterns

- Publishing a service straight from a shapefile on a user's desktop. It will break on reboot.
- Shipping a service with **Analyze warnings unresolved** — you are accepting unknown risk.
- Leaving **Public sharing** on a feature service with edit capability.
- Building a cache at zoom levels the client never uses (wasted disk, longer rebuild).
- Exposing geoprocessing services with unbounded inputs — validate input sizes server-side.
- Using map services where vector tile services would do; performance and maintainability lose.
- Forgetting to set `maxRecordCount` and discovering it at go-live under real load.

## Related references

- `arcgis-security-roles.md` — RBAC on top of published services.
- `arcgis-backup-dr.md` — backing up service configs and item metadata.
- `arcgis-components.md` — topology that hosts these services.
