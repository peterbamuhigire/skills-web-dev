# Rendering Thresholds — Feature Count vs Strategy

Distilled from *Modern Web Cartography*, *Leaflet in Practice*, and production experience. These are decision rules, not marketing numbers — pick a strategy from the feature count first, not the other way around.

## Decision Table

| Feature count | Geometry type | Strategy | Notes |
|---|---|---|---|
| < 200 | Any | Plain `L.marker` / `L.geoJSON` on DOM/SVG | Simplest; fast enough at interaction time |
| 200 – 2 000 | Points | `Leaflet.markercluster` with `chunkedLoading: true` | Cluster below zoom 14, un-cluster above |
| 200 – 5 000 | Polygons / lines | `preferCanvas: true` on the map, not SVG | Canvas renders 10× faster for dense polygons |
| 2 000 – 10 000 | Points | Server-side bbox filtering + cluster | Query only what fits the current viewport |
| 2 000 – 10 000 | Polygons | Server returns simplified geometry per zoom (`ST_SimplifyPreserveTopology`) | Generalisation table per zoom level |
| > 10 000 any | Mixed | Switch to MVT (vector tiles) — Mapbox GL / MapLibre, or `Leaflet.VectorGrid` | Leaflet's DOM model does not scale beyond this |
| > 50 000 any | Any | WebGL overlay (`Leaflet.glify`, `PixiOverlay`) or leave Leaflet | DOM/SVG will freeze the tab |

## Renderer Choice

- **SVG (default)** — good interactive picking, CSS-stylable, but slow past ~1k shapes.
- **Canvas** — enable with `L.map(id, { preferCanvas: true })`. Faster draw, supports hit-testing, but no CSS styling and no per-feature DOM events beyond click.
- **WebGL (PixiOverlay / glify)** — only for > 10k features where Canvas redraw on pan becomes visible.

Rule: if `layer.getLayers().length > 1000`, you should already be on Canvas.

## Polygon Simplification Per Zoom

Return different geometry tolerances from the backend for each zoom band:

| Zoom | `ST_SimplifyPreserveTopology` tolerance (degrees) | Use |
|---|---|---|
| 0–5 | 0.1 | Country / region outlines |
| 6–9 | 0.01 | Sub-regions, large districts |
| 10–12 | 0.001 | Districts, large neighbourhoods |
| 13–15 | 0.0001 | Parcels, blocks |
| 16+ | unsimplified | Final detail |

Never ship one geometry tolerance for all zooms — either you blow the wire budget at low zoom or you lose detail at high zoom.

## Heatmaps

- `leaflet.heat` is fine up to ~50 000 points.
- Above that, pre-aggregate server-side into an H3 or geohash grid and render the aggregated cells.
- Heatmaps lie under ~200 points — they imply density that isn't statistically there. Use markers.

## Anti-Patterns

- Loading a 4 MB country GeoJSON at zoom 3 "for feature completeness".
- Client-side reprojection of thousands of features every pan.
- Using SVG renderer for 10k+ polygons because "it works on my laptop".
- Clustering below 50 points — the cluster icons hide real information.
- Rendering the same data twice (e.g. GeoJSON layer + markercluster) "in case".

## Observability Hooks

- Track time from `moveend` to `layeradd` — above 200 ms, users perceive lag.
- Track geometry bytes per bbox request — above 500 KB per pan, add simplification or tiling.
