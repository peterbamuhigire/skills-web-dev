---
name: gis-mapping
description: "Use for web apps that need OpenStreetMap-based GIS mapping, location selection, map-driven UIs, or geofencing validation. Covers Leaflet/OpenLayers setup, data storage, and backend validation patterns."
---

# GIS Mapping (OpenStreetMap)

## Quick Summary

- OpenStreetMap mapping with Leaflet/OpenLayers for web apps
- Location selection (marker, polygon, rectangle) + map UI patterns
- Geofencing enforcement with client + server validation (see geofencing.md)
- Performance, clustering, and safe storage of spatial data

## When to Use

- You need interactive maps for customers, assets, farms, or delivery zones
- Users must select or edit locations on a map
- You must enforce geo-fencing or boundary validation
- You need GIS data display with filters, legends, and clustering

## Key Patterns

- Always include OSM attribution.
- Capture geometry in GeoJSON and validate server-side.
- Use bounding-box checks before deeper polygon math.
- Cluster markers when data is large or dense.

## Stack Choices (Frontend)

- **Leaflet**: Lightweight, fastest to implement, best for most apps.
- **OpenLayers**: Heavyweight GIS controls and projections.
- **MapLibre GL JS**: Vector tiles, smoother at scale.

## Data Model & Storage

- **Point**: `latitude` + `longitude` (DECIMAL(10,7))
- **Polygon/Boundary**: Store as GeoJSON (TEXT/JSON)
- **Metadata**: `location_label`, `address`, `last_updated_at`

Recommended formats:

- GeoJSON for portability across JS + backend
- WKT only if your DB tooling depends on it

## Map Initialization (Leaflet)

```html
<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

```javascript
const map = L.map("map").setView([0.3476, 32.5825], 12);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);
```

## Location Selection Patterns

### Marker (Point)

- Single click adds/updates a marker
- Store coordinates in hidden inputs

```javascript
let marker;
map.on("click", (e) => {
  if (marker) map.removeLayer(marker);
  marker = L.marker(e.latlng).addTo(map);
  document.querySelector("#latitude").value = e.latlng.lat;
  document.querySelector("#longitude").value = e.latlng.lng;
});
```

### Polygon / Rectangle (Area)

Use Leaflet Draw or Geoman. Store GeoJSON geometry.

```javascript
const drawn = new L.FeatureGroup().addTo(map);
const drawControl = new L.Control.Draw({
  draw: { polygon: true, rectangle: true, marker: false, circle: false },
  edit: { featureGroup: drawn },
});
map.addControl(drawControl);

map.on("draw:created", (e) => {
  drawn.clearLayers();
  drawn.addLayer(e.layer);
  document.querySelector("#boundary_geojson").value = JSON.stringify(
    e.layer.toGeoJSON(),
  );
});
```

## Geofencing (Overview)

Geofencing must be enforced at two levels:

- **UI constraint**: prevent invalid selections in the browser
- **Server constraint**: verify boundaries in backend validation

See geofencing.md for full patterns, point-in-polygon checks, and multi-geometry rules.

## UI Patterns

- Filters + stats in a side card, map in a large canvas
- Legend to toggle categories (customer groups, territories)
- Clustering when markers exceed ~200

## Performance & UX

- Debounce search and map redraw
- Use marker clustering or server-side tiling
- Lazy load heavy layers
- Simplify large polygons for UI display

## Backend Validation

Always validate coordinates server-side:

- Ensure latitude is between -90 and 90
- Ensure longitude is between -180 and 180
- Enforce geofence boundaries with the same logic as UI

## Privacy & Security

- Location data is sensitive: protect with permissions
- Never trust client-only validation
- Avoid exposing private coordinates without authorization

## Recommended Plugins

- Leaflet Draw or Leaflet Geoman (drawing tools)
- Leaflet MarkerCluster (performance)
- Leaflet Control Geocoder (search)
- Turf.js (geospatial analysis)

## References

- geofencing.md (sub-skill)
