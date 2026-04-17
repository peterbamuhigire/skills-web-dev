# Leaflet Plugin Selection Matrix

Battle-tested plugin picks distilled from *Leaflet in Practice* and the Leaflet ecosystem. Pick one per capability — running two plugins for the same job causes event collisions.

## Plugin Matrix

| Capability | First choice | Fallback | When to switch |
|---|---|---|---|
| Drawing / editing | `@geoman-io/leaflet-geoman-free` | `Leaflet.draw` | Geoman has live editing and snapping out of the box; pick `leaflet-draw` only for legacy codebases |
| Clustering | `Leaflet.markercluster` | `Supercluster` (manual) | Switch to Supercluster if you need cluster math on a web worker at > 20k points |
| Heatmap | `leaflet.heat` | `leaflet-heatmap.js` | `leaflet.heat` is simpler; switch only if you need radius-per-point |
| Routing | `leaflet-routing-machine` + OSRM or GraphHopper | `leaflet.polylineDecorator` for static lines | LRM requires a routing backend — do not expect client-only routes |
| Measurement | `leaflet-measure` | custom with Turf | Built-in plugin is enough for 90% of UIs |
| Geocoding UI | `leaflet-control-geocoder` | Custom Nominatim fetch | Built-in control accepts any provider (Nominatim, Google, Pelias) |
| Large point layers | `Leaflet.VectorGrid` (MVT) | `Leaflet.glify` (WebGL) | VectorGrid for vector tiles from server; glify when you have raw coords and need to draw > 50k |
| Rasters / overlays | `Leaflet.ImageOverlay.Rotated` | `Leaflet.TileLayer.WMS` | WMS for live GIS servers; rotated image for scanned floorplans / parcel maps |
| Time slider | `Leaflet.TimeDimension` | custom slider | TimeDimension integrates WMS-T; custom is fine for client-only time series |
| ESRI basemap / service | `esri-leaflet` | none | Required if you must talk to ArcGIS Server feature services |
| Freehand / trace | `leaflet-freedraw` | Geoman + pen mode | Only if the UX specifically calls for lasso/freehand |
| Side-by-side | `leaflet-side-by-side` | two synced maps | Before/after imagery comparison |
| Fullscreen | `leaflet.fullscreen` | browser Fullscreen API | Plugin handles the map resize event for you |

## Compatibility Checklist

Before adding any plugin:

1. Confirm it declares `leaflet` as a peer dependency (not bundled).
2. Check it supports the Leaflet version in use (1.9.x is current; many older plugins break on it).
3. Confirm it accepts the map's chosen renderer (Canvas vs SVG) — some plugins assume SVG.
4. Ensure it does not hard-code tile attribution or URLs.
5. Verify it cleans up on `map.remove()` — leaky plugins are a top cause of SPA memory growth.
6. If it ships CSS, scope it (plugins that style `.leaflet-popup` globally will break other popups).

## Plugins to Avoid Without Review

- Any plugin last updated before 2020 — Leaflet 1.7 changed internal events.
- Plugins that monkey-patch `L.Map.prototype` — they collide with each other.
- Plugins that require jQuery — Leaflet itself does not, and adding jQuery for one plugin is a smell.
- "All-in-one" plugins that bundle clustering + draw + heat — you lose replaceability.

## Plugin Load Order

Leaflet must be loaded first, then plugins, then your app code. When bundling:

```js
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
// app code after
```

Plugins attach to `L.*`, so the order of side-effect imports matters.

## Decision Rule: Plugin vs Custom

Write custom Leaflet code when:

- The plugin ships > 3× more code than the feature needs.
- The plugin pulls in a UI framework you are not using (Bootstrap, jQuery UI).
- You need control over the exact DOM structure for accessibility.

Otherwise use the plugin — Leaflet's internal APIs are stable and a well-maintained plugin survives upgrades better than custom code.
