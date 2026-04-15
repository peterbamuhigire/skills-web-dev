# When ArcGIS Enterprise Is the Right Choice

Decision rules, licensing economics, sector mandates, and exit cost analysis for picking ArcGIS Enterprise over the PostGIS + open-source mapping alternative.

## Quick decision matrix

```text
Factor                               ArcGIS Enterprise    PostGIS + OSS stack
-----------------------------------  -------------------  ----------------------
Government / regulated mandate       Yes                   No (usually blocked)
Team trained on ArcGIS Pro           Yes                   Retrain cost is real
ESRI data licences already paid      Yes                   Duplicate spend
Need Network Analyst / LocateXT      Yes                   Hard to replicate
Modern SaaS startup, cost-first      No                    Yes
Embedded in third-party web app      No (licence friction) Yes
Tile-heavy consumer workload         Either                Yes (cheaper at scale)
Offline mobile GIS editing           ArcGIS Field Maps     Needs custom build
Asset-management, utility networks   Yes (Utility Network) Needs heavy custom
```

## Hard triggers that force ArcGIS

Pick ArcGIS Enterprise when one or more of the following is true:

- A regulator, ministry, or grant funder has named ArcGIS as the authoritative system of record.
- Internal GIS analysts already live in ArcGIS Pro and produce weekly deliverables as MXD/APRX files.
- The organisation has active ELA (Enterprise Licence Agreement) or bought Utility Network, Parcel Fabric, or LGIM data models.
- The system must host authoritative services other agencies consume (for example, a national cadastre feeding neighbouring ministries).
- Field crews use ArcGIS Field Maps or Survey123 with offline map packages and replication.
- A named analytical tool is required: Network Analyst, Spatial Analyst, Geostatistical Analyst, Business Analyst, or ArcGIS Insights.

## Hard triggers that force the OSS stack

Pick PostGIS + MapLibre/Mapbox/Leaflet when any of these apply:

- The product is a commercial SaaS where per-user licences from Esri would wreck unit economics.
- The spatial features are one component of a broader web/mobile app, not a GIS product.
- The data volume is large and mostly vector tiles for public consumers — MVT from PostGIS scales cheaper.
- The tech team is web/backend engineers, not GIS analysts.
- The deployment target is a serverless or container-native cloud footprint.

## Licensing cost anchors (2026 guidance)

Prices are illustrative and vary by region and ELA negotiation; use as order-of-magnitude only.

```text
Line item                                     Annual cost (order of magnitude)
--------------------------------------------  --------------------------------
ArcGIS Enterprise (Standard, single machine)  USD 15,000–30,000
ArcGIS Enterprise (Advanced + extensions)     USD 50,000–150,000+
ArcGIS Online named users (Creator)           USD 500 per user
ArcGIS Pro named user                         Included with Creator
Network Analyst extension                     USD 2,500–5,000 per machine
Utility Network                               USD 25,000+ per deployment
Esri Maintenance and support                  ~20% of licence per year
ELA (org-wide)                                USD 150k–multi-million
---
PostGIS + MapLibre                            USD 0 licence
Mapbox GL + tiles (commercial)                USD 0–5k per month by load
OSRM / Valhalla self-hosted routing           USD 0 licence, infra cost only
```

Hidden costs when you do pick ArcGIS: mandatory Esri training courses, certified hosting skills, Windows Server licences, SSL/identity tuning, and ArcGIS Monitor for SLA evidence.

## Sectors where ArcGIS is effectively mandated

- National mapping agencies and cadastre authorities.
- Electricity, water, and gas utilities (Utility Network is the de facto standard).
- Ministries of lands, environment, and disaster management in many African and Asian governments.
- Defence and intelligence communities.
- Large municipalities with long-running LGIM (Local Government Information Model) investments.
- Oil and gas upstream and pipeline operators.
- Transport agencies using Roads and Highways or LRS.

In these sectors, picking an OSS stack is often a political fight you will lose; budget for ArcGIS plus an OSS web channel in front of it.

## Migration exit cost (from ArcGIS to OSS)

Rough cost model for leaving ArcGIS Enterprise once adopted:

```text
Cost bucket                                   Effort
--------------------------------------------  -----------------------------------
Re-platform feature services to PostGIS+API   4–12 weeks per system of record
Rebuild symbology and cartography in MapLibre 2–6 weeks per map product
Replace Network Analyst with Valhalla/OSRM    4–8 weeks and accuracy regression
Retrain analyst team on QGIS / web tools       1 quarter minimum
Rewrite geoprocessing models (ModelBuilder)    2–4 weeks per model, per person
Data custodian process and governance rewrite  1 quarter, cross-team
Sunset window with dual-run                    2 quarters of parallel operation
```

Rule of thumb: a fully committed ArcGIS Enterprise shop spending USD 100k per year on licences needs 6–18 months and 2–4 engineers to migrate credibly. Do not start a migration without an executive sponsor and a hard deadline.

## Recommended default posture

For most SaaS products in this repository (real estate, ERP, field operations), start on the OSS stack with PostGIS, MapLibre or Mapbox GL, and OSRM or Valhalla. Reserve ArcGIS Enterprise for deployments where a client or regulator names it, or where the team is already operating it.

When integrating with an existing ArcGIS Enterprise customer, treat their Portal as an upstream system of record: consume feature services, do not try to replace them, and push enriched results back as hosted feature layers if the workflow requires it.

## Red flags during pre-sales or kickoff

- A client demands ArcGIS but has never run it, and has no Esri account manager.
- A client demands OSS only because "ArcGIS is expensive", but their parent ministry mandates ArcGIS.
- The proposed budget does not include Esri maintenance or Windows Server licensing.
- The RFP lists both "must integrate with Portal for ArcGIS" and "must be fully cloud-native serverless" — these pull in opposite directions.
- No named GIS custodian on the client side to own publishing, versioning, and retirement of services.

## Related references

- `arcgis-components.md` — what you actually deploy if you pick ArcGIS.
- `real-estate-saas-integration.md` — PostGIS + Mapbox reference architecture for the OSS path.
- `gis-postgis-backend` skill — spatial backbone for the OSS path.
- `gis-maps-integration` skill — map client integration patterns.
