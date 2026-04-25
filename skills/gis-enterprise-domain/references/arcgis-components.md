# ArcGIS Enterprise Components and Deployment Topologies

Covers Portal for ArcGIS, ArcGIS Server, Data Store (relational, tile cache, spatiotemporal, graph, object), Web Adaptor, and typical base vs HA deployment patterns with sizing guidance.

## The four mandatory components

A valid ArcGIS Enterprise base deployment includes, at minimum, all four of:

- **Portal for ArcGIS** — identity, sharing model, groups, item catalogue, web maps, web apps, hosted layer metadata.
- **ArcGIS Server** (hosting server) — publishes and runs services (map, feature, image, geoprocessing, geocoding).
- **ArcGIS Data Store** — backing store for hosted feature layers, scene layers, caches, and analytic data.
- **Web Adaptor** — IIS or Java web-tier shim for HTTPS, custom context paths, and external exposure.

Portal must be federated with at least one Server (the hosting server). The hosting server must be configured with a Data Store. These three form the "web GIS" and are managed and backed up together.

## Data Store flavours

```text
Type              Use                                               Engine under the hood
----------------  ------------------------------------------------  ----------------------------------
Relational        Hosted feature layers, editable features          PostgreSQL (managed by Esri)
Tile cache        Vector tile and scene tile caches                 File-backed store
Spatiotemporal    High-velocity IoT/GeoEvent feeds, observations     Elasticsearch-based
Graph             Knowledge graph (newer)                            Internal graph engine
Object            3D objects, BIM, mesh layers                       File-backed store
```

Not every deployment needs every type. A typical real-estate or government portal uses relational + tile cache only. Add spatiotemporal only when you run GeoEvent or Velocity.

## Supporting components (optional)

- **ArcGIS GeoEvent Server** — real-time streams, alerts, routing rules.
- **ArcGIS Image Server** — raster analytics, orthomosaic processing, dynamic image services at scale.
- **ArcGIS GeoAnalytics Server** — big-data batch spatial analytics.
- **ArcGIS Notebook Server** — hosted Jupyter for ArcGIS Python API work.
- **ArcGIS Knowledge / Workflow Manager / Mission** — domain add-ons.
- **ArcGIS Monitor** — external telemetry and SLA evidence; do not confuse with Portal logs.

## Base deployment (single machine or small multi-machine)

Minimum usable production topology:

```text
[ Load balancer / reverse proxy ]
            |
        HTTPS 443
            |
[ Web Adaptor (IIS or Tomcat) ]
            |
  +---------+-----------+
  |                     |
[ Portal ]          [ Server (hosting) ]
                         |
                    [ Data Store: relational + tile cache ]
```

Sizing anchor for a base deployment:

```text
Role               vCPU   RAM      Disk               Notes
-----------------  -----  -------  -----------------  -------------------------------
Portal             4      16 GB    100 GB SSD         Content + config grows slowly
Hosting Server     8      32 GB    200 GB SSD         Scales with concurrent services
Data Store (rel)   8      32 GB    500 GB SSD         Separate data disk, IOPS matters
Web Adaptor host   2      4 GB     40 GB              Stateless, cheap, 2 for HA
```

This supports tens of named users and a few dozen concurrent service requests. Go to HA once you cross that.

## Highly Available (HA) deployment

In HA every stateful role is at least doubled and fronted by a load balancer. The minimum HA topology:

```text
                    [ External LB / WAF ]
                           |
                  +--------+---------+
                  |                  |
             [ WA host 1 ]      [ WA host 2 ]
                  |                  |
         +--------+--------+ +-------+---------+
         |                 | |                 |
   [ Portal A ] <---->  [ Portal B ]           (shared content dir on NFS/SMB
                                                 or cloud object store)
   [ Server A ] <---->  [ Server B ]           (shared config-store + server dirs
                                                 on HA file share)
   [ Data Store primary ] <----> [ Data Store standby ]  (streaming replication)
   [ Tile cache store A ] <----> [ Tile cache store B ]  (shared or replicated)
```

Key HA rules:

- Portal content directory must live on a highly available file share (NFS for Linux, SMB for Windows) or cloud object store supported by Esri.
- Server config-store and server directories must be on shared storage so any Server node can take over.
- Relational Data Store runs primary/standby with synchronous replication. Promotion is automatic via Esri tooling; do not hand-roll it.
- Tile cache data store can be deployed in standby mode; scene caches can be on object storage.
- Web Adaptor hosts are stateless. Run two behind the load balancer for availability, not for state.

## Sizing for HA at scale

```text
Scale tier        Named users  Concurrent reqs    Portal   Server   Data Store
----------------  -----------  -----------------  -------  -------  -------------
Small HA          <200          <100 RPS          2x med   2x med   2x 8vCPU/32GB
Medium HA         200-1000      100-500 RPS       2x lg    4x lg    2x 16vCPU/64GB
Large / multisite 1000+         500+ RPS          2x xl    site x2  primary+standby+read replica
```

Across a single deployment, do not mix Windows and Linux Server machines. Pick one OS family per site.

## Operating system and version matrix

- Windows Server 2019 / 2022 with IIS + ARR for Web Adaptor is the most common path.
- Red Hat / Rocky / Ubuntu LTS supported for Linux installs; use Tomcat-based Web Adaptor.
- Match patch levels across all nodes. A mismatch between Portal and Server minor versions breaks federation.

## Common deployment anti-patterns

- Putting Portal, Server, and Data Store on the same machine in production. OK for dev, never for production.
- Running Data Store on a general-purpose disk without dedicated IOPS. The relational store will be the first to fall over.
- Exposing ArcGIS Server directly to the internet without a Web Adaptor and WAF.
- Mixing ArcGIS Online and ArcGIS Enterprise identity stores without planning single sign-on.
- Not federating Server with Portal — you lose hosted feature services and cross-product sharing.
- Using the built-in "hosted services" Server as a general-purpose Server — split hosting vs GIS services if load grows.

## Cloud deployment shortcuts

- Esri provides **ArcGIS Enterprise on Kubernetes** (EoK) for newer deployments. It bundles all components into Helm-managed charts with managed internal storage and is the preferred path for new large deployments.
- **CloudFormation / ARM / Terraform** Esri-authored templates exist for AWS and Azure; prefer them over hand-rolled installs for consistency.
- **Object storage for caches** — store tile and scene caches in S3/Azure Blob where supported; it dramatically simplifies HA.

## Capacity planning checklist

- Estimate peak concurrent map requests and peak feature-layer edit rate.
- Baseline IOPS for the relational Data Store (measure with `iostat` or cloud metrics).
- Alarm on Portal content directory disk usage — it only grows.
- Pre-provision tile cache disk; on-demand caching can thrash.
- Plan Windows licence costs when sizing.

## Related references

- `publishing-services.md` — how services are created and versioned on top of this topology.
- `arcgis-backup-dr.md` — which components each backup tool covers.
- `arcgis-security-roles.md` — identity and federation sit on top of this stack.
