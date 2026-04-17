# Vector Tile Pipeline

Distilled from *Modern Web Cartography*. Vector tiles (MVT / PBF) are the default for map data above ~5k features or any dataset that needs per-feature styling. Raster tiles stay useful for basemaps and static imagery.

## When to Use Vector Tiles vs Raster

| Need | Use vector tiles | Use raster tiles |
|---|---|---|
| Styling changes client-side (filter by attribute, switch theme, dark mode) | ✓ | ✗ |
| Text labels that scale and rotate | ✓ | ✗ |
| Satellite / aerial imagery | ✗ | ✓ |
| Large static basemap (country-scale roads) | ✓ preferred | ✓ acceptable |
| Offline-first mobile with limited storage | ✓ (smaller files) | ✗ |
| 3D terrain / hillshade | ✗ | ✓ |
| Feature interactivity (hover, click on a road) | ✓ | ✗ |

Rule: if the user will change styling or filter features, vector tiles. If the tiles are purely decorative imagery, raster.

## Tile Generation with Tippecanoe

`tippecanoe` is the standard tool for generating MVT from GeoJSON. Key flags:

```bash
tippecanoe \
  -o parcels.mbtiles \
  --minimum-zoom=10 \
  --maximum-zoom=16 \
  --drop-densest-as-needed \
  --coalesce-smallest-as-needed \
  --extend-zooms-if-still-dropping \
  --no-tile-compression \   # only if your CDN compresses
  --layer=parcels \
  parcels.geojson
```

Non-obvious flags:

- `--drop-densest-as-needed` — drops features in dense tiles to stay under the 500 KB tile limit (MVT hard ceiling).
- `--coalesce-smallest-as-needed` — merges tiny polygons at low zoom instead of dropping them.
- `--extend-zooms-if-still-dropping` — increases max zoom automatically if features still do not fit.
- `--no-tile-compression` — skip gzip if your CDN already compresses; else leave default.
- `--read-parallel` — speed up ingestion of large GeoJSON.

## Zoom-Level Strategy

- Decide minimum zoom from the data's geographic scale: country-level → 3, city-level → 10, parcel-level → 14.
- Keep the gap between `minzoom` and `maxzoom` to ~6 levels per layer; beyond that, split into multiple layers.
- Generate per-layer, not per-dataset: roads / parcels / points-of-interest as separate tile sets you can upgrade independently.

## Serving Tiles

- Pre-render and serve from a CDN (S3 + CloudFront / MinIO + nginx) — fastest, cheapest at scale.
- `tileserver-gl` or `martin` for dynamic PostGIS → MVT. Use only when data changes hourly; otherwise pre-render.
- Cache key must include the tile set version. URL pattern `/tiles/{version}/{z}/{x}/{y}.pbf` lets you purge a version without touching others.

## Mapbox GL / MapLibre Performance

Per-layer rules that matter in practice:

- Always set `minzoom` and `maxzoom` on every layer — otherwise the renderer pays the cost of every layer at every zoom.
- Use `filter` expressions to hide features at low zoom, not `visibility: none` on the whole layer.
- Avoid `symbol` layers with `text-field` across > 100 k features at once; text layout is expensive.
- Keep total simultaneously-visible layers under ~40. Above that, paint times climb on mid-range devices.
- Sprite and glyph (font) URLs must be hosted alongside tiles; don't reuse Mapbox's free sprite/glyph URLs in production — they are rate-limited.

## Cost Model

- Pre-rendered tiles: cost = storage + CDN egress. A country-scale parcel tile set at z10–16 is typically 2–20 GB.
- Dynamic tile server: cost = PostGIS CPU + cache. Add a CDN or `varnish` in front; never expose `martin` directly to the internet.

## Anti-Patterns

- One giant layer spanning z0–z22 — the generator will either drop features or produce > 500 KB tiles.
- Regenerating the whole tile set on every data change — diff the regions that changed and re-tile only those.
- Using Mapbox's hosted sprites/glyphs at https://api.mapbox.com in self-hosted deployments — rate-limited and a supply-chain risk.
- Skipping `minzoom`/`maxzoom` on GL layers — measurable frame drop at pan.
