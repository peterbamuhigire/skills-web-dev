# Geofencing Sub-skill (OpenStreetMap + Web Apps)

This sub-skill focuses on enforcing geo-fencing with OpenStreetMap in web apps.

## 1. Popular OSM Libraries

### Leaflet (most common)

```javascript
const map = L.map("map").setView([51.505, -0.09], 13);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);
```

### OpenLayers

```javascript
import Map from "ol/Map";
import View from "ol/View";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";

const map = new Map({
  target: "map",
  layers: [new TileLayer({ source: new OSM() })],
  view: new View({ center: [0, 0], zoom: 2 }),
});
```

## 2. Location Selection

### Point Selection (Marker)

```javascript
let selectedMarker;

map.on("click", (e) => {
  const { lat, lng } = e.latlng;
  if (!isWithinBounds(lat, lng)) {
    Swal.fire(
      "Outside Allowed Area",
      "Pick a location within the boundary.",
      "warning",
    );
    return;
  }
  if (selectedMarker) map.removeLayer(selectedMarker);
  selectedMarker = L.marker([lat, lng]).addTo(map);
});

function isWithinBounds(lat, lng) {
  const bounds = { minLat: 40.0, maxLat: 45.0, minLng: -75.0, maxLng: -70.0 };
  return (
    lat >= bounds.minLat &&
    lat <= bounds.maxLat &&
    lng >= bounds.minLng &&
    lng <= bounds.maxLng
  );
}
```

### Polygon / Boundary Selection

```javascript
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

const drawControl = new L.Control.Draw({
  draw: { polygon: true, rectangle: true, marker: true, circle: false },
  edit: { featureGroup: drawnItems },
});
map.addControl(drawControl);

map.on("draw:created", (e) => {
  const layer = e.layer;
  const bounds = layer.getBounds();
  if (!isBoundsWithinGeoFence(bounds)) {
    Swal.fire(
      "Outside Allowed Area",
      "Selection exceeds allowed boundaries.",
      "warning",
    );
    return;
  }
  drawnItems.clearLayers();
  drawnItems.addLayer(layer);
});
```

## 3. Geo-fencing Core Enforcement

### Restrict Map View

```javascript
const geoFenceBounds = [
  [40.0, -75.0],
  [45.0, -70.0],
];
const map = L.map("map", {
  maxBounds: geoFenceBounds,
  maxBoundsViscosity: 1.0,
}).setView([42.5, -72.5], 10);
```

### Validate Coordinates

```javascript
function validateGeoFence(lat, lng, bounds) {
  const valid =
    lat >= bounds.minLat &&
    lat <= bounds.maxLat &&
    lng >= bounds.minLng &&
    lng <= bounds.maxLng;
  return {
    isValid: valid,
    message: valid
      ? "OK"
      : `Coordinates must be within: Lat ${bounds.minLat}–${bounds.maxLat}, Lng ${bounds.minLng}–${bounds.maxLng}`,
  };
}
```

### Validate Polygon Vertices

```javascript
function validatePolygon(polygonCoords, bounds) {
  for (const [lat, lng] of polygonCoords) {
    if (
      lat < bounds.minLat ||
      lat > bounds.maxLat ||
      lng < bounds.minLng ||
      lng > bounds.maxLng
    ) {
      return false;
    }
  }
  return true;
}
```

## 4. Form Integration Example

```html
<form id="location-form">
  <div id="map"></div>
  <input type="hidden" id="coordinates" name="coordinates" />
  <div id="bounds-error" class="error" style="display:none"></div>
  <button type="submit">Submit</button>
</form>
```

```javascript
const GEO_FENCE = { minLat: 40.0, maxLat: 45.0, minLng: -75.0, maxLng: -70.0 };

const map = L.map("map").setView([42.5, -72.5], 10);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

L.rectangle(
  [
    [GEO_FENCE.minLat, GEO_FENCE.minLng],
    [GEO_FENCE.maxLat, GEO_FENCE.maxLng],
  ],
  { color: "#ff7800", weight: 1, fillOpacity: 0.1 },
).addTo(map);

const drawnItems = new L.FeatureGroup().addTo(map);
const drawControl = new L.Control.Draw({
  draw: { polygon: true, rectangle: true, marker: true },
  edit: { featureGroup: drawnItems },
});
map.addControl(drawControl);

map.on("draw:created", (e) => {
  const layer = e.layer;
  if (!isFeatureWithinGeoFence(layer)) {
    showError("Selection exceeds allowed boundaries");
    return;
  }
  clearError();
  drawnItems.clearLayers();
  drawnItems.addLayer(layer);
  document.getElementById("coordinates").value = JSON.stringify(
    layer.toGeoJSON(),
  );
});

function isFeatureWithinGeoFence(layer) {
  const bounds = layer.getBounds();
  return (
    bounds.getNorth() <= GEO_FENCE.maxLat &&
    bounds.getSouth() >= GEO_FENCE.minLat &&
    bounds.getEast() <= GEO_FENCE.maxLng &&
    bounds.getWest() >= GEO_FENCE.minLng
  );
}

function showError(message) {
  const errorDiv = document.getElementById("bounds-error");
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
}

function clearError() {
  document.getElementById("bounds-error").style.display = "none";
}
```

## 5. Any-Shape Geo-fencing (Point-in-Polygon)

### Ray-Casting Algorithm

```javascript
function isPointInPolygon(point, polygon) {
  const [x, y] = point;
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    const intersect =
      yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}
```

### Validate User Shape Against Fence

```javascript
function validateShapeAgainstGeoFence(userShape, fencePolygon) {
  const bounds = userShape.getBounds();
  if (!fencePolygon.getBounds().contains(bounds)) {
    return { isValid: false, message: "Shape exceeds boundary box" };
  }
  const points = getShapePoints(userShape);
  const fencePoints = fencePolygon.getLatLngs()[0];
  const fenceCoords = fencePoints.map((p) => [p.lat, p.lng]);
  for (const point of points) {
    if (!isPointInPolygon([point.lat, point.lng], fenceCoords)) {
      return { isValid: false, message: "Shape exceeds fence" };
    }
  }
  return { isValid: true, message: "Shape within fence" };
}
```

## 6. Advanced Techniques

### Multi-Polygon Support

```javascript
function isPointInAnyPolygon(point, polygons) {
  return polygons.some((polygon) => isPointInPolygon(point, polygon));
}
```

### Exclusion Zones (Holes)

```javascript
function isPointInPolygonWithHoles(point, outerPolygon, holes = []) {
  if (!isPointInPolygon(point, outerPolygon)) return false;
  return !holes.some((hole) => isPointInPolygon(point, hole));
}
```

### Buffer Zones

```javascript
const EPSILON = 0.000001;
function isPointNearBoundary(point, polygon, bufferDegrees) {
  for (let i = 0; i < polygon.length; i++) {
    const next = (i + 1) % polygon.length;
    const d = pointToLineDistance(point, polygon[i], polygon[next]);
    if (d <= bufferDegrees + EPSILON) return true;
  }
  return false;
}
```

## 7. Accuracy & Scale

- For areas > 10 km, use Turf.js geodesic checks
- Use bounding-box checks before point-in-polygon for performance
- Treat boundary points consistently (define inside/outside rules)

## 8. Backend Validation (Always Required)

Perform server-side validation before saving any geometry:

```javascript
function validateCoordinates(lat, lng, bounds) {
  return (
    lat >= bounds.minLat &&
    lat <= bounds.maxLat &&
    lng >= bounds.minLng &&
    lng <= bounds.maxLng
  );
}
```

## 9. Useful Plugins & Libraries

- leaflet-draw or leaflet-geoman (drawing)
- leaflet-control-geocoder (search)
- leaflet-markercluster (performance)
- @turf/turf (geospatial analysis)
- rbush (spatial indexing)
- martinez (polygon operations)

## 10. Production Notes

- Always show attribution for OSM tiles
- Cache tiles if you host your own tile server
- Debounce map interactions
- Validate on the backend even if UI blocks invalid selections
