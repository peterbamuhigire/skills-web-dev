# Leaflet Capability Breakdown (Leaflet-First)

Use only the sections you need. Each section lists common Leaflet equivalents for ArcGIS-style workflows and the minimal plugin bundle.

## 1) Basic Mapping & Visualization (Core Leaflet)

- **Use when:** map display, base layers, markers, popups, legends.
- **Core only:** no plugins required.
- **Pattern:** `L.map()` + `L.tileLayer()` + `L.control.layers()`.

## 2) Spatial Queries (Turf.js)

- **Use when:** find features within radius, point-in-polygon, attribute filtering.
- **Plugin:** `@turf/turf` (or cherry-pick `booleanPointInPolygon`, `buffer`, `nearestPoint`).
- **Note:** keep heavy geospatial logic server-side when datasets are large.

## 3) Geocoding (Search + Reverse)

- **Use when:** address search, reverse geocode from point.
- **Options:**
  - `leaflet-control-geocoder` (Nominatim by default)
  - Direct Nominatim API calls
- **Policy:** if using a paid provider, store API keys in `system_settings` and never hardcode.

## 4) Buffering & Zone Analysis

- **Use when:** service area buffers, overlap detection, coverage analysis.
- **Plugin:** `@turf/turf` (`buffer`, `intersect`, `union`, `area`).

## 5) Heatmaps & Density

- **Use when:** density visualization (sales density, delivery hotspots).
- **Plugin:** `leaflet.heat`.

## 6) Routing & Network Analysis

- **Use when:** route lines, ETA, nearest route, isochrones.
- **Options:**
  - OSRM (open source)
  - GraphHopper (API)
- **Plugin:** `leaflet-routing-machine` (optional).

## 7) Drawing & Editing

- **Use when:** draw polygons/rectangles/markers for boundaries.
- **Plugin:** `leaflet.draw` or `Leaflet-Geoman`.
- **Storage:** save GeoJSON in DB (TEXT/JSON).

## 8) Measurement Tools

- **Use when:** user measures distance/area on map.
- **Plugin:** `leaflet-measure` or custom map.distance + polygon area.

## 9) Clustering & Aggregation

- **Use when:** 200+ markers or dense datasets.
- **Plugin:** `leaflet.markercluster`.
- **Tip:** enable chunked loading for large lists.

## 10) Spatial Analysis

- **Use when:** nearest neighbor, spatial joins, density grids.
- **Plugin:** `@turf/turf`.

## 11) Time-Based Analysis

- **Use when:** display changes over time (weekly sales, incident history).
- **Approach:** layer groups + time slider; optionally heat layer per time slice.

## 12) Export & Printing

- **Use when:** PDF/PNG export, GeoJSON export.
- **Plugins:** `html2canvas`, `jsPDF` for raster/PDF; use GeoJSON from layers.

## Recommended Plugin Bundle (Typical 80%)

- `leaflet.markercluster`
- `leaflet.draw`
- `leaflet.heat`
- `leaflet-control-geocoder`
- `@turf/turf` (or cherry-pick functions)
- `leaflet-routing-machine` (optional)

## Notes for BIRDC ERP

- Leaflet is the default GIS engine.
- Use [public/farmer-profile.php](public/farmer-profile.php) as the canonical Leaflet pattern.
- Keep tile providers configurable and always include attribution.
