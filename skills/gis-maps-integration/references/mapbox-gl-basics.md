# Mapbox GL JS — sources, layers, expressions, and clustering

Applies to Mapbox GL JS v3 and MapLibre GL JS v4 (API near-identical). Covers style spec, source types, layer types, expressions, markers, popups, and clustering with supercluster.

Companion: `styling-comparison.md`, `mapbox-offline.md`.

## Init

```ts
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN!;

export const map = new mapboxgl.Map({
  container: "map",
  style: "mapbox://styles/mapbox/streets-v12",
  center: [32.5825, 0.3476],           // [lng, lat] — NOT [lat, lng]
  zoom: 13,
  pitch: 0,
  bearing: 0,
  antialias: true,                      // needed for fill-extrusion
  attributionControl: true,
  cooperativeGestures: true,            // two-finger to pan on mobile
});

map.addControl(new mapboxgl.NavigationControl(), "top-right");
map.addControl(new mapboxgl.ScaleControl({ unit: "metric" }), "bottom-left");
map.addControl(new mapboxgl.FullscreenControl());
map.addControl(new mapboxgl.GeolocateControl({ trackUserLocation: true }), "top-right");
```

Rule: coordinates in Mapbox are `[lng, lat]`. This trips up every new developer.

## Style spec basics

A style is a JSON document with:

```json
{
  "version": 8,
  "sources": { "properties": "..." },
  "sprite": "mapbox://sprites/mapbox/streets-v12",
  "glyphs": "mapbox://fonts/mapbox/{fontstack}/{range}.pbf",
  "layers": [ { "id": "...", "source": "...", "type": "...", "paint": {}, "layout": {} } ]
}
```

- `sources` are data; `layers` are rendering.
- One source can feed many layers.
- Layers render in array order; later layers draw on top.

## Sources

### Vector tile source (best for scale)

```ts
map.addSource("buildings", {
  type: "vector",
  url: "https://tiles.example.com/buildings.json", // TileJSON
  minzoom: 12,
  maxzoom: 16,
});
```

Or from a tile URL pattern:

```ts
map.addSource("listings", {
  type: "vector",
  tiles: ["https://tiles.example.com/listings/{z}/{x}/{y}.pbf"],
  minzoom: 6,
  maxzoom: 18,
});
```

### Raster tile source

```ts
map.addSource("osm", {
  type: "raster",
  tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
  tileSize: 256,
  attribution: "© OpenStreetMap contributors",
});
```

### GeoJSON source (inline data)

```ts
map.addSource("properties", {
  type: "geojson",
  data: {
    type: "FeatureCollection",
    features: props.map((p) => ({
      type: "Feature",
      properties: { id: p.id, price: p.price, status: p.status },
      geometry: { type: "Point", coordinates: [p.lng, p.lat] },
    })),
  },
  cluster: true,
  clusterMaxZoom: 14,
  clusterRadius: 50,
});
```

Use GeoJSON for <10k features or frequent updates. Beyond that, generate MVT server-side (see `gis-postgis-backend`).

## Layer types

| Type | Use |
|---|---|
| `circle` | Point markers as circles. Cheap, stylable via expressions. |
| `symbol` | Icons + text labels. Needs sprite. |
| `line` | Polylines. Dashes, gradients, rounded joins. |
| `fill` | Polygons. No height. |
| `fill-extrusion` | 3D polygons (buildings). Needs `antialias: true`. |
| `heatmap` | Density of points. |
| `raster` | Raster tiles (satellite, historical). |
| `hillshade` | Relief from DEM source. |
| `sky` | Atmosphere when pitched. |
| `background` | Flat fill below all layers. |

## Paint vs layout

- **layout** properties affect how the layer is composed (icon image, text field, line cap, line join). Changing a layout property triggers re-layout.
- **paint** properties are cheap visual tweaks (colour, opacity, radius). Changing a paint property does not re-layout.

Prefer paint for dynamic changes (hover, selection, filter). Layout changes should be rare.

## Expressions

Expressions are JSON functions that compute layer properties from feature data or zoom:

```ts
map.addLayer({
  id: "listings-circle",
  source: "listings",
  "source-layer": "listings",  // required for vector tile sources
  type: "circle",
  paint: {
    "circle-radius": [
      "interpolate", ["linear"], ["zoom"],
      8, 3,
      14, 8,
      18, 20
    ],
    "circle-color": [
      "match", ["get", "status"],
      "available", "#22C55E",
      "pending",   "#F59E0B",
      "sold",      "#6B7280",
      "#E11D48"
    ],
    "circle-opacity": [
      "case",
      ["boolean", ["feature-state", "hover"], false], 1,
      0.8
    ],
  },
});
```

Key operators: `get`, `has`, `match`, `case`, `step`, `interpolate`, `zoom`, `feature-state`, `concat`, `to-string`.

Feature-state allows per-feature style changes without mutating the source.

## Markers (HTML)

For a small number of always-visible features:

```ts
new mapboxgl.Marker({ color: "#E11D48" })
  .setLngLat([32.5825, 0.3476])
  .addTo(map);

// Custom HTML
const el = document.createElement("div");
el.className = "marker";
el.innerHTML = `<img src="/pin.svg" alt="" />`;
new mapboxgl.Marker({ element: el, anchor: "bottom" })
  .setLngLat([32.58, 0.35])
  .addTo(map);
```

Rule: HTML markers are DOM-expensive. Beyond ~100, switch to a circle or symbol layer.

## Popups

```ts
const popup = new mapboxgl.Popup({ closeButton: true, closeOnClick: true, maxWidth: "320px" })
  .setLngLat([32.58, 0.35])
  .setHTML(`<h4>Kampala Office</h4><p>Plot 12, Nakasero</p>`)
  .addTo(map);
```

Bind to layer clicks:

```ts
map.on("click", "listings-circle", (e) => {
  const f = e.features?.[0];
  if (!f) return;
  const coords = (f.geometry as GeoJSON.Point).coordinates.slice() as [number, number];
  new mapboxgl.Popup()
    .setLngLat(coords)
    .setHTML(`<strong>${f.properties?.name}</strong><br/>UGX ${f.properties?.price}`)
    .addTo(map);
});

map.on("mouseenter", "listings-circle", () => (map.getCanvas().style.cursor = "pointer"));
map.on("mouseleave", "listings-circle", () => (map.getCanvas().style.cursor = ""));
```

Accessibility: include a keyboard-reachable list of points alongside the map (`a11y-maps.md`).

## Clustering with built-in GeoJSON source

```ts
map.addSource("deliveries", {
  type: "geojson",
  data: fc,
  cluster: true,
  clusterMaxZoom: 14,
  clusterRadius: 50,
  clusterProperties: {
    urgent: ["+", ["case", ["==", ["get", "priority"], "urgent"], 1, 0]],
  },
});

map.addLayer({
  id: "cluster",
  source: "deliveries",
  type: "circle",
  filter: ["has", "point_count"],
  paint: {
    "circle-color": [
      "step", ["get", "point_count"],
      "#51BBD6", 10,
      "#F1F075", 50,
      "#F28CB1",
    ],
    "circle-radius": [
      "step", ["get", "point_count"],
      15, 10,
      22, 50,
      30,
    ],
  },
});

map.addLayer({
  id: "cluster-count",
  source: "deliveries",
  type: "symbol",
  filter: ["has", "point_count"],
  layout: { "text-field": "{point_count_abbreviated}", "text-size": 12 },
});

map.addLayer({
  id: "unclustered",
  source: "deliveries",
  type: "circle",
  filter: ["!", ["has", "point_count"]],
  paint: { "circle-radius": 5, "circle-color": "#11B4DA" },
});

map.on("click", "cluster", (e) => {
  const f = e.features?.[0];
  if (!f) return;
  const clusterId = f.properties?.cluster_id;
  const src = map.getSource("deliveries") as mapboxgl.GeoJSONSource;
  src.getClusterExpansionZoom(clusterId, (err, zoom) => {
    if (err || !zoom) return;
    map.easeTo({ center: (f.geometry as GeoJSON.Point).coordinates as [number, number], zoom });
  });
});
```

## Using supercluster directly

When the built-in clustering isn't enough (custom collision rules, offscreen metrics, external use):

```bash
npm i supercluster
```

```ts
import Supercluster from "supercluster";

const index = new Supercluster({ radius: 40, maxZoom: 16 }).load(features);
const bbox = map.getBounds().toArray().flat() as [number, number, number, number];
const clusters = index.getClusters(bbox, Math.floor(map.getZoom()));
```

Use supercluster in a Web Worker for large datasets (>50k features).

## Layer ordering

- Add `raster`/`background` first.
- Then `fill`, `line`.
- Then `symbol` (labels last to avoid being covered).
- `fill-extrusion` renders between fills and symbols by default; `addLayer(layer, beforeId)` for precise control.

```ts
map.addLayer({ id: "myFill", ... }, "road-label"); // insert below the label layer
```

## Performance rules

- Use vector sources over raster when possible.
- Filter layers by zoom (`minzoom`, `maxzoom`) instead of hiding via `visibility`.
- Prefer `paint` changes over `layout` changes.
- Use `circle` layers with expressions instead of hundreds of HTML markers.
- Use `feature-state` for hover/selection, not style-update loops.
- `map.resize()` after any container size change.

## Anti-patterns

- Placing hundreds of `mapboxgl.Marker` HTML elements instead of a symbol or circle layer.
- Mutating the GeoJSON and calling `setData` on every frame — batch updates.
- Using raster tiles for custom data you could serve as MVT.
- Forgetting `source-layer` on vector sources (silent invisible layer).
- Forgetting `antialias: true` then wondering why 3D buildings have jagged edges.
- Mixing `[lat, lng]` with `[lng, lat]` in a single codebase.
