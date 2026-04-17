---
name: gis-maps-integration
description: Use when integrating Google Maps JavaScript API or Mapbox GL into a web
  app — setup, markers, info windows, geocoding, places autocomplete, routing/directions,
  styling, offline, accessibility, and cost control. Complements gis-mapping (Leaflet).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Google Maps + Mapbox Integration

<!-- dual-compat-start -->
## Use When

- Use when integrating Google Maps JavaScript API or Mapbox GL into a web app — setup, markers, info windows, geocoding, places autocomplete, routing/directions, styling, offline, accessibility, and cost control. Complements gis-mapping (Leaflet).
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `gis-maps-integration` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Maps provider integration test plan | Markdown doc covering markers, info windows, geocoding, and rate-limit handling for Google/Mapbox/MapLibre | `docs/gis/provider-tests.md` |
| Security | API key handling note | Markdown doc covering provider key storage, referrer restrictions, and quota policies | `docs/gis/maps-key-handling.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
When Leaflet isn't enough — Google Maps for ecosystem + Places + Directions, Mapbox GL for WebGL performance, styling, 3D, and offline.

**Prerequisites:** Load `gis-mapping` for the Leaflet baseline and data storage patterns. Load `gis-postgis-backend` for server-side spatial.

## When this skill applies

- Adding a map to a web app where Leaflet doesn't deliver (Places autocomplete, turn-by-turn, Street View, 3D, advanced styling).
- Building property search, store locator, logistics, fleet, or booking flows.
- Replacing a Leaflet map because the feature set is insufficient.
- Keeping Leaflet for basic maps and adding Google/Mapbox for specific features.

## Leaflet vs Google Maps vs Mapbox — decision rule

```text
Simple display + markers + basic layers, cost-sensitive          -> Leaflet (existing gis-mapping)
Places autocomplete, Google ecosystem, directions with traffic   -> Google Maps JS API
Custom styling, 3D buildings, offline on mobile, WebGL perf      -> Mapbox GL
Vector tiles you serve yourself (MVT from PostGIS)               -> Mapbox GL or MapLibre (OSS Mapbox fork)
Open-source stack preference, no vendor lock-in                  -> MapLibre
```

**MapLibre GL** is the OSS fork of Mapbox GL v1. Same API, no vendor keys, compatible with MVT tiles you host yourself. Strong default for cost-conscious SaaS.

See `references/leaflet-vs-google-vs-mapbox.md`.

## Google Maps JavaScript API setup

**Keys and restrictions (do not skip):**

```text
1. Create a key per environment (dev, staging, prod).
2. Restrict by HTTP referrer (exact domains).
3. Restrict by API (enable only Maps JS + what you use).
4. Set daily quota caps per key.
5. Budget alerts at 50% and 80% of monthly cap.
```

Unrestricted keys get abused within hours of exposure. Every public key must be restricted.

**Loader (@googlemaps/js-api-loader):**

```ts
import { Loader } from "@googlemaps/js-api-loader";

const loader = new Loader({
  apiKey: import.meta.env.VITE_GMAPS_KEY,
  version: "weekly",
  libraries: ["places", "geometry"],
});

const { Map, Marker } = await loader.importLibrary("maps");
const map = new Map(el, { center: { lat: 0.3476, lng: 32.5825 }, zoom: 13 });
new Marker({ map, position: { lat: 0.3476, lng: 32.5825 }, title: "Kampala" });
```

See `references/google-maps-setup-keys.md`.

## Markers, InfoWindows, overlays

- **AdvancedMarkerElement** — modern replacement for Marker. Full HTML custom styling.
- **InfoWindow** — popup. Single at a time for accessibility.
- **Polyline / Polygon** — drawn on top of map.
- **Data Layer** — load GeoJSON for bulk rendering.

Clustering for >~200 markers (`@googlemaps/markerclusterer`). Beyond a few thousand, switch to vector tiles.

## Places autocomplete

Cost-controlled pattern: debounce input, cache recent results, restrict bounds/country:

```ts
const ac = new google.maps.places.Autocomplete(inputEl, {
  componentRestrictions: { country: ["ug", "ke", "tz"] },
  fields: ["place_id", "formatted_address", "geometry.location"],
  types: ["address"],
});
ac.addListener("place_changed", () => {
  const p = ac.getPlace();
  onAddressSelected({ address: p.formatted_address, lat: p.geometry!.location!.lat(), lng: p.geometry!.location!.lng() });
});
```

**Fields** parameter is critical — requesting fields you don't use multiplies cost. See `references/google-places-autocomplete.md`.

## Directions + routes

- Directions API gives JSON; Directions Service renders on the map.
- Modes: driving, walking, bicycling, transit.
- **Waypoints** can be reordered (`optimizeWaypoints: true`).
- For turn-by-turn, use Navigation SDK (Android/iOS) or Mapbox.

```ts
const service = new google.maps.DirectionsService();
const renderer = new google.maps.DirectionsRenderer({ map });
const result = await service.route({
  origin, destination,
  travelMode: google.maps.TravelMode.DRIVING,
  provideRouteAlternatives: true,
});
renderer.setDirections(result);
```

See `references/google-routing-directions.md`.

## Styling

- **Cloud-based Map Styles** (Map IDs) — style in Google Cloud Console, reference by ID. Change style without redeploy.
- **In-code JSON styles** — legacy, still works. Harder to iterate.
- **Pick cloud styles** for any serious branding work.

## Mapbox GL basics

```ts
import mapboxgl from "mapbox-gl";

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN!;

const map = new mapboxgl.Map({
  container: "map",
  style: "mapbox://styles/mapbox/streets-v12",
  center: [32.5825, 0.3476],
  zoom: 13,
});

map.on("load", () => {
  map.addSource("listings", { type: "vector", url: "https://tiles.example.com/listings.json" });
  map.addLayer({
    id: "listings-circle",
    source: "listings",
    "source-layer": "listings",
    type: "circle",
    paint: { "circle-color": "#E11D48", "circle-radius": 6 },
  });
});
```

Vector tile sources beat raster for zoom and performance. Style with simple expressions; drive layout from data without re-rendering.

See `references/mapbox-gl-basics.md`.

## Mapbox offline (mobile)

Mobile SDKs (iOS/Android) support offline region downloads. Web Mapbox GL does not have native offline but can use service workers to cache tiles.

See `references/mapbox-offline.md`.

## Styling comparison (quick)

| Need | Winner |
|---|---|
| Rapid branded style iteration | Mapbox Studio |
| Minimal setup, Google-native look | Google Maps cloud styles |
| Custom map with 3D buildings | Mapbox GL |
| Free tier for small apps | MapLibre + OSM |
| Turn-by-turn in mobile | Mapbox Navigation SDK or Google Navigation SDK |

## Cost control

Track by:

- Per-key quota caps.
- Daily alert thresholds.
- Client-side caching of geocode + places results.
- **Server-proxy** the API key for server-side calls (hide the key, rate-limit, cache).
- Switch to MapLibre + OSM tiles for open-source cost-free baseline.

Rule: every map provider request costs real money. Review monthly spend; compare to alternatives yearly.

See `references/cost-control-quotas.md`.

## Accessibility

- Map is a decorative image to screen readers by default — not acceptable.
- Provide a text alternative: list of markers, search with autocomplete, address lookup.
- Keyboard navigation: focusable markers, arrow-key pan/zoom, ESC close popup.
- Labels on interactive elements (`aria-label`).
- Never require drag-to-place without an alternative address input.
- Don't rely solely on colour for differentiation.

See `references/a11y-maps.md`.

## Anti-patterns

- Hardcoding API keys in committed frontend bundles (use env + restrict key).
- Requesting every Places field by default — silent cost multiplier.
- Geocoding repeatedly for the same address — cache it.
- Using raster tiles where a vector tile source would do.
- Cluster markers without clustering at >500 markers.
- No offline plan for mobile.
- No keyboard accessibility.
- Switching providers without an abstraction layer — plan for provider change.

## Read next

- `gis-mapping` — Leaflet baseline.
- `gis-postgis-backend` — MVT tiles from your own data.
- `gis-enterprise-domain` — real-estate and ArcGIS enterprise patterns.

## References

- `references/leaflet-vs-google-vs-mapbox.md`
- `references/google-maps-setup-keys.md`
- `references/google-places-autocomplete.md`
- `references/google-routing-directions.md`
- `references/mapbox-gl-basics.md`
- `references/mapbox-offline.md`
- `references/styling-comparison.md`
- `references/cost-control-quotas.md`
- `references/a11y-maps.md`
- `references/vector-tile-pipeline.md` — MVT vs raster decision, tippecanoe flags, zoom strategy, Mapbox GL per-layer performance rules, self-hosted sprites/glyphs
