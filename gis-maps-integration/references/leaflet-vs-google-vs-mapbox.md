# Leaflet vs Google Maps vs Mapbox vs MapLibre

Feature, cost, and licensing matrix. Use this to pick a map provider before any code is written, and to decide when a migration is justified.

Companion: `gis-mapping` (Leaflet baseline), `gis-postgis-backend` (self-hosted MVT tiles).

## Head-to-head matrix

| Capability | Leaflet | Google Maps JS | Mapbox GL JS | MapLibre GL JS |
|---|---|---|---|---|
| Rendering | Raster DOM + SVG overlays | Raster + vector, WebGL on new renderer | WebGL vector tiles | WebGL vector tiles |
| Core library licence | BSD-2 | Proprietary (ToS) | Proprietary, source-available | BSD-3 (OSS fork of Mapbox GL v1) |
| Free tier | Tiles depend on provider (OSM, Stadia, Carto) | USD 200/month credit, then per-API pricing | 50k map loads/month free, then per-load | Fully free; pay only for your own tiles and hosting |
| Default basemap | None bundled | Google tiles (paid) | Mapbox styles (paid beyond free) | None bundled; bring your own style JSON |
| Places autocomplete | No (integrate 3rd-party) | First-class (Places API) | Geocoder plugin (paid) | None; use Nominatim, Pelias, or proprietary |
| Directions + traffic | Plugins + 3rd-party API | Directions API + traffic layer | Directions API + traffic tile | None; use OSRM, Valhalla, GraphHopper |
| Custom styling depth | Limited to raster tiles | Cloud-based Map Styles, good range | Studio with full style spec control | Same spec as Mapbox v1; Maputnik editor |
| 3D buildings + terrain | No | Photorealistic 3D (Maps Embed, Aerial View) | `fill-extrusion`, terrain DEM, sky layer | `fill-extrusion`, terrain DEM (v2+), sky layer |
| Mobile offline | Plugin-based, raster only | Limited; maps for Android/iOS SDKs only | Offline regions on mobile SDKs | Mobile SDKs (native-maplibre) with offline packs |
| Bundle size (gzipped) | ~40 KB | ~200 KB initial + async libs | ~220 KB | ~220 KB |
| Vendor lock-in risk | Low | High (keys + pricing + ToS) | Medium (open style spec, closed backend) | Low |
| Self-host tiles | Yes (raster from PostGIS + mod_tile, or MVT via pg_tileserv) | No | Optional (MVT) | Yes (core use case) |

## Cost bands (2025 rates, indicative)

- **Google Maps**: USD 7 per 1,000 dynamic map loads after free credit. Places Autocomplete-per-session USD 2.83 per 1,000 sessions. Directions USD 5 per 1,000. Geocoding USD 5 per 1,000.
- **Mapbox**: USD 5 per 1,000 map loads after first 50,000. Geocoding USD 0.50-0.75 per 1,000. Directions USD 2 per 1,000.
- **MapLibre + OSM**: zero licence cost. You pay only for tile hosting (S3 + CDN) and for any geocoding/routing services you run (Pelias, Valhalla) or buy.

See `cost-control-quotas.md` for quota governance.

## Decision rule

```text
Requirement                                         -> Pick
-----------------------------------------------------  ----------------------
Simple, cost-sensitive, read-only maps             -> Leaflet + OSM tiles
Places autocomplete, Street View, Google ecosystem -> Google Maps
3D, heavy custom branding, offline on mobile       -> Mapbox GL (or MapLibre)
Open-source preference, you host tiles             -> MapLibre + self-hosted MVT
Large volume, cost matters, you can run OSRM       -> MapLibre + OSRM + Nominatim
Turn-by-turn in-app navigation                     -> Mapbox Navigation SDK or
                                                      Google Navigation SDK
```

## MapLibre as OSS fork

Mapbox GL JS v1.x was BSD-3. v2.0 re-licensed to a proprietary licence requiring a Mapbox account. The community forked v1.13 as **MapLibre GL JS** and has since evolved it independently (v4+). Key facts:

- API is near-identical to Mapbox GL JS. Many Mapbox styles work unchanged.
- No access token required. You supply your own `style.json` pointing at your own tile endpoints.
- Same `fill-extrusion`, terrain, sky, and expression features as modern Mapbox.
- Native SDKs exist: `maplibre-native` for Android, iOS, Qt, Node.
- Migration from Mapbox GL JS v1 is near-drop-in; from v2+ requires removing `accessToken` and switching style URLs.

Use MapLibre when you want Mapbox ergonomics without the licence cost or vendor dependency, and when you already run PostGIS + `pg_tileserv` or Tegola for MVT.

## Offline support comparison

| Provider | Web | Android | iOS |
|---|---|---|---|
| Leaflet | Service worker + IndexedDB for raster | leaflet.offline (wraps Android WebView) | same via WebView |
| Google Maps | No public offline for Maps JS | Maps SDK supports limited offline | Maps SDK supports limited offline |
| Mapbox | Manual service worker caching only | Offline region API (style + tiles + fonts + sprites) | Offline region API |
| MapLibre | Service worker caching; style + tiles are plain HTTP | maplibre-native offline pack | maplibre-native offline pack |

See `mapbox-offline.md` for the region download recipe.

## Styling capabilities

- **Google cloud styles**: Map IDs managed in the Cloud Console, good contrast presets, limited custom imagery. Dark mode is a style toggle.
- **Mapbox Studio**: full style spec editor, sprite upload, 3D controls, style inheritance. Excellent for brand work.
- **MapLibre + Maputnik**: open-source WYSIWYG editor, edits the same `style.json`. Less polished but free.

See `styling-comparison.md`.

## 3D and advanced effects

- Google: Photorealistic 3D Tiles (separate product), WebGL Overlay View for custom 3D.
- Mapbox: `fill-extrusion` for building polygons, `raster-dem` terrain source, `sky` layer, free-camera pitch animations.
- MapLibre: parity with Mapbox GL v2 for 3D since v2.0 of MapLibre (2022+). Use `terrain`, `sky`, `fill-extrusion` identically.

## Directions and routing

- Google Directions API: best traffic data, transit in most countries, waypoint optimisation.
- Mapbox Directions API: driving-traffic profile, matrix API, isochrones, turn-by-turn-suitable output.
- MapLibre needs an external router (OSRM for cars, Valhalla for multimodal, GraphHopper for pricing).

Never render turn-by-turn instructions by eyeballing the LineString — use the provider's `legs[].steps[].maneuver` data verbatim.

## When to migrate

Migrate away from Leaflet when you need any of:

- Places autocomplete with typo-tolerance and session billing.
- Vector-tile zoom and rotation without tile-seam flicker.
- Branded styling deeper than tile-provider preset.
- 3D extrusions or pitched cameras.
- Offline packs on mobile.

Migrate away from Google Maps when any of:

- Monthly spend exceeds USD 2,000 and you have repeatable loads.
- You need full control over map styling (Google's range is narrower than Studio).
- You want to self-host tiles.

Migrate away from Mapbox when:

- The v2+ licence change is a procurement blocker.
- You want to host tiles without a Mapbox account.
- Cost per 1,000 loads is material at your scale.

Migration safety: always put the map behind a thin adapter interface (`MapProvider`) with `setView`, `addMarker`, `addLayer`, `onClick`. Swapping providers should not require touching feature code.

## Licensing pitfalls

- Google Maps tiles cannot be cached for more than 30 days (ToS) and cannot be printed for sale.
- Mapbox tiles retrieved via access token cannot be redistributed.
- MapLibre has no tile licence of its own — your tile source (OSM, custom) sets the rules. OSM requires attribution and a share-alike approach for derived tiles.
- OSM attribution line must be visible on the map (`© OpenStreetMap contributors`).

## Anti-patterns

- Picking Google "because everyone knows it" without costing 100k loads/month.
- Using Mapbox GL v2 and treating it as open source — it is not since 2.0.
- Switching to MapLibre without setting up your own tile CDN — you inherit ops overhead.
- Comparing providers on bundle size only — the real cost is per-API call volume.
