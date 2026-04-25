# ArcGIS Pro Workflows for Enterprise Data

Distilled from the *ArcGIS Pro Manual* for day-to-day enterprise GIS work. These are the workflows that govern data quality and what an enterprise GIS administrator must enforce before publishing services.

## Geodatabase Design Invariants

1. A **feature dataset** shares a single spatial reference (SRID). All feature classes in it must match — verify before ingest, not after.
2. Use **domains** to constrain attribute values (enum-like). Coded-value domains for categories; range domains for numeric bounds. Never rely on free-text for classification — the drift ("Hydrography" vs "hydrography" vs "hydro") destroys spatial joins.
3. Use **subtypes** when one feature class represents logically different things with different rules (e.g. `roads` with subtypes `highway`, `street`, `trail`). Subtypes let you attach different domains and default values per type without splitting the class.
4. Every feature class should have a **globalID** column and optional **editor-tracking** metadata (`created_user`, `created_date`, `last_edited_user`, `last_edited_date`).

## Topology Rules (Parcel / Admin Data)

Topology prevents invalid geometry from entering the database. Minimum rules for parcel data:

| Rule | Purpose |
|---|---|
| Must-not-overlap | Parcels cannot double-cover a surface |
| Must-not-have-gaps | No slivers between parcels within a block |
| Must-be-covered-by (parcels by block) | Every parcel is contained by exactly one block |
| Boundary must-be-covered-by (roads by centerline) | Road polygons align with their centerlines |
| Must-not-self-overlap (lines) | A polyline cannot cross itself |

Run topology validation before any public publication. An error count > 0 is a release blocker — you do not ship a parcel map with overlapping parcels.

## Versioning Strategy

- **Default version** — production, read-mostly.
- **Branch versioning** — asynchronous edits, supports long transactions, plays well with services and web editing.
- **Traditional versioning** — only for legacy DBMS deployments. Needs a reconcile-and-post cadence (weekly minimum).

Rule: use branch versioning for any modern enterprise deployment that publishes feature services. Traditional versioning has operational costs (reconcile/post) that branch versioning avoids.

## Georeferencing Workflow (Scanned Maps / Aerials)

Use when you must add a raster (scanned cadastral map, historical aerial, floorplan) to the map:

1. Load the unreferenced raster.
2. Identify 4+ control points that are stable in both the raster and a known reference layer (road intersections, building corners, administrative markers).
3. Apply a transformation:
   - **1st-order polynomial (affine)** — shift, scale, rotate. Fine for already-projected scans.
   - **2nd / 3rd-order polynomial** — small non-linear distortion. Only when residuals demand it.
   - **Spline** — warps to control points exactly. Use only when local distortion exists (paper stretch, poorly-projected scan) and you understand it will displace non-control areas.
4. Check the **RMS error** — for 1:1000 cadastral work, aim for < 0.5 m RMS; above 2 m, add more control points or re-scan.
5. Rectify and save the transformed raster, then catalogue it in the enterprise geodatabase.

## Publishing Services — Pre-Flight Checklist

Before pushing a map or feature service to ArcGIS Enterprise:

1. Spatial reference of all layers matches (or the map has a defined output projection).
2. All layers are in a registered data source (not a local file path) — services referencing local files fail on the server.
3. Symbology uses server-renderable symbols (no custom fonts missing on the server).
4. Scale dependencies are set — otherwise heavy layers draw at zoom 0 and kill performance.
5. A cached tile strategy chosen: dynamic, pre-cached, or vector tile package. For > 50 k features, cached or vector.
6. Anonymous access is off unless explicitly required; token/OAuth enabled.
7. Service shares appropriate to tenant and role (see gis-enterprise-domain/references/arcgis-security-roles.md).

## Enterprise Topology / QA

- Run **Data Reviewer** batch jobs nightly on authoritative datasets. Catches invalid geometry, duplicate features, attribute-domain violations.
- Maintain a **QA dashboard** for dataset editors that shows topology errors, review check failures, and unresolved feedback.

## Anti-Patterns

- Parcels stored without topology rules — overlap and slivers will accumulate.
- Attribute columns with no domain — free-text classification drifts across users and breaks reports.
- Single-node Portal / ArcGIS Server in production — no HA, one patch window away from downtime.
- Publishing services pointing at local file paths — breaks on restart or migration.
- Long-running traditional versions that are never reconciled — the version tree grows unbounded and slows every query.
- Using branch versioning without scheduled maintenance (compress/reconcile) — same outcome over time.

## Backup Discipline

- Full geodatabase backup weekly, differential daily.
- Test **restore**, not just backup, monthly. A backup that has never been restored is not a backup.
- Document which services reference which datasets so a restore preserves the service graph.
