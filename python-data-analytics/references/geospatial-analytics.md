# Geospatial Analytics

Shapely is for individual geometries; GeoPandas is for tables of geometries. Coordinate reference systems (CRS) are the number-one source of bugs and silent wrong answers, so the first section below is non-optional.

## CRS: EPSG:4326 vs 3857 vs local metric

Three categories of CRS cover most SaaS analytics work:

| EPSG     | Name                    | Units   | When to use                                                |
|----------|-------------------------|---------|------------------------------------------------------------|
| 4326     | WGS84 lat/lon           | degrees | Storage, interchange, GeoJSON, Leaflet input               |
| 3857     | Web Mercator            | metres  | Display on tile maps, quick global distance (inaccurate at poles) |
| 32736, etc. | UTM zones (per region)| metres  | Accurate distance and area within a single region          |

Rules:

- Store everything in EPSG:4326. It is what the database (MySQL `POINT`, PostGIS `geometry`) expects and what Leaflet and Google Maps consume.
- Reproject to a metric CRS before computing distance, buffer, or area. Degrees are not a distance unit; they vary with latitude.
- In East Africa use EPSG:32736 (UTM zone 36S) or EPSG:21037 (Arc 1960 / UTM zone 37S) for area-accurate work within a single country. Web Mercator (3857) distorts area by the `cos(lat)` factor and is only acceptable for rough distance at low latitudes.

```python
import geopandas as gpd
from shapely.geometry import Point

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["lng"], df["lat"]),
    crs="EPSG:4326",
)

# For distance in metres in Kampala area
gdf_m = gdf.to_crs("EPSG:32636")    # UTM zone 36N covers Uganda

# For display on a web tile map
gdf_web = gdf.to_crs("EPSG:3857")
```

Note the `x, y` order in `points_from_xy` is `(lng, lat)`, not `(lat, lng)`. This is the single most common bug in new geo code; all of Shapely uses `(x, y)` i.e. `(lng, lat)`.

## Shapely basics

```python
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union, transform

p = Point(32.5825, 0.3476)                    # Kampala city centre, lng lat
line = LineString([(32.58, 0.34), (32.60, 0.35)])
polygon = Polygon([(32.5, 0.3), (32.6, 0.3), (32.6, 0.4), (32.5, 0.4)])

# Predicates
polygon.contains(p)          # True if p strictly inside
polygon.intersects(line)     # True if any overlap
p.within(polygon)            # opposite of contains

# Constructive
buffered = p.buffer(0.001)   # degrees – do not use for distance!
union    = unary_union([polygon, polygon.buffer(0.001)])
```

Distance in Shapely is in the CRS of the geometry. Always project first:

```python
from shapely.ops import transform
from pyproj import Transformer

to_m = Transformer.from_crs("EPSG:4326", "EPSG:32636", always_xy=True).transform
p_m = transform(to_m, p)
```

## GeoPandas operations

### Spatial join

The workhorse for "which zone does this delivery fall in?" questions.

```python
zones = gpd.read_file("service_zones.geojson").to_crs("EPSG:32636")
deliveries = gdf.to_crs("EPSG:32636")

joined = gpd.sjoin(
    deliveries, zones,
    how="left", predicate="within",
)
# joined has zone columns attached to each delivery row
```

Predicates: `within`, `intersects`, `contains`, `overlaps`, `touches`. Pick the narrowest predicate that expresses your intent. `within` is faster and clearer than `intersects` when points belong to at most one polygon.

### Distance between two layers

```python
# Nearest zone centre for each delivery
zones["centroid"] = zones.geometry.centroid
nearest = gpd.sjoin_nearest(
    deliveries,
    zones.set_geometry("centroid"),
    distance_col="dist_m",
    how="left",
)
```

`sjoin_nearest` is in GeoPandas 0.10+ and is the right tool for "closest depot" reports. Do not write your own O(N*M) nearest-neighbour loop.

### Buffers

Buffers in metres require a metric CRS.

```python
# 500 m catchment around each pickup point
catch = deliveries.copy()
catch["geometry"] = catch.buffer(500)    # metres, because deliveries is in 32636
catch = catch.to_crs("EPSG:4326")        # convert back for storage / display
```

### Intersection and area

```python
customers_in_zone = gpd.overlay(customers, zones, how="intersection")
customers_in_zone["area_km2"] = customers_in_zone.area / 1_000_000
```

For area to make sense the CRS must be metric. `gpd.overlay` is expensive; for simple "does it lie within" questions use `sjoin` with `within` instead.

## Distance calculations

Three ways to compute a distance between two lat/lon points. Pick by accuracy:

- **Great-circle (haversine)**. Closed-form, accurate to ~0.5 % globally, fast in vectorised numpy. Good enough for delivery routing, catchment, reporting.
- **Project to UTM then Euclidean**. Metre-accurate within a single UTM zone. Break across zones.
- **Geodesic (`pyproj.Geod.inv`)**. Most accurate, slower. Use for legal or regulatory reports where sub-metre accuracy matters.

```python
import numpy as np

def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0088
    lat1, lng1, lat2, lng2 = map(np.radians, (lat1, lng1, lat2, lng2))
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

df["km_to_depot"] = haversine_km(df["lat"], df["lng"], depot_lat, depot_lng)
```

Because it is vectorised over numpy arrays, it handles millions of rows per second.

## Route optimisation introduction

For anything beyond nearest-depot, use a library; do not write a TSP solver by hand.

- `OR-Tools` (`ortools.constraint_solver`) is Google's production-quality solver. Good for 10-500 stop problems with time windows and vehicle capacities.
- `OSMnx` + `NetworkX` for road-network shortest path using OpenStreetMap. Good for "actual drive distance" in a report, not for live routing.

Minimal OR-Tools VRP sketch:

```python
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

manager = pywrapcp.RoutingIndexManager(len(stops), num_vehicles, depot_index)
routing = pywrapcp.RoutingModel(manager)

def distance_cb(from_idx, to_idx):
    f = manager.IndexToNode(from_idx)
    t = manager.IndexToNode(to_idx)
    return int(distance_matrix[f][t])

transit = routing.RegisterTransitCallback(distance_cb)
routing.SetArcCostEvaluatorOfAllVehicles(transit)

params = pywrapcp.DefaultRoutingSearchParameters()
params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
params.time_limit.seconds = 5

solution = routing.SolveWithParameters(params)
```

Rules for SaaS route reports:

- Compute the distance matrix once per run in metres (project to UTM, then pairwise haversine or true road distance).
- Use a time limit rather than waiting for optimality. 5 seconds is plenty for 50-stop problems.
- Return the tour order and per-leg distance; do not return raw solver indices to PHP.

## Geofencing compliance recipes

Typical SaaS needs: "was this field agent within the client site during the shift?" or "flag deliveries outside the licensed service area".

### Point-in-polygon batch check

```python
sites = gpd.read_file("client_sites.geojson").to_crs("EPSG:4326")
events = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df["lng"], df["lat"]), crs="EPSG:4326",
)

flagged = gpd.sjoin(events, sites, how="left", predicate="within")
flagged["on_site"] = flagged["index_right"].notna()
report = flagged.groupby(["agent_id", "shift_id"]).agg(
    on_site_events=("on_site", "sum"),
    total_events=("on_site", "size"),
).assign(
    on_site_pct=lambda d: (d["on_site_events"] / d["total_events"] * 100).round(1)
)
```

### Buffer-based compliance

Fields sometimes need a tolerance; a GPS reading with 20 m accuracy should not mark a worker as off-site for standing by a fence.

```python
sites_m = sites.to_crs("EPSG:32636")
sites_m["geometry"] = sites_m.buffer(25)        # 25 m tolerance
sites_tol = sites_m.to_crs("EPSG:4326")
```

### Speed and dwell time

Compute time-differenced positions per agent, derive speed, and flag dwell windows.

```python
df = df.sort_values(["agent_id", "ts"])
df["dx_m"] = haversine_km(
    df["lat"], df["lng"],
    df.groupby("agent_id")["lat"].shift(),
    df.groupby("agent_id")["lng"].shift(),
) * 1000
df["dt_s"] = df.groupby("agent_id")["ts"].diff().dt.total_seconds()
df["speed_kph"] = (df["dx_m"] / df["dt_s"]).replace([np.inf, -np.inf], np.nan) * 3.6
df["dwelling"] = (df["speed_kph"] < 1) & (df["dt_s"] > 60)
```

## MySQL spatial types

MySQL 8 supports `POINT`, `POLYGON`, and `ST_*` functions. Integration tips:

- Use `POINT(lng, lat)` consistently. Many drivers accept `ST_GeomFromText('POINT(lng lat)', 4326)`.
- Read into pandas with `ST_AsText(geom) AS geom_wkt`, then parse with `shapely.wkt.loads`.
- Spatial indexes (`SPATIAL INDEX`) speed up `ST_Within` queries substantially; confirm they are used with `EXPLAIN`.

```python
from shapely import wkt

df["geometry"] = df["geom_wkt"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
```

## Common geo mistakes

- Putting `lat` before `lng` in `Point(...)` or `points_from_xy(...)`. Shapely wants `(x, y) = (lng, lat)`.
- Computing distance or area in degrees. Always reproject first.
- Forgetting to tag CRS on a GeoDataFrame. `gdf.crs is None` means every spatial operation is silently wrong.
- Using Web Mercator (3857) for area analysis. It is visual-only at non-equatorial latitudes.
- Running `sjoin` without indexes on very large frames. GeoPandas builds an R-tree automatically, but if you disable it, queries become O(N*M).
- Mixing GPS readings from different devices without filtering for accuracy. Always require `accuracy < 50 m` for compliance reports.
