# Styling comparison — Google, Mapbox Studio, MapLibre

Covers iteration workflow, dark mode, branding, and the decision of where the source of truth for a map style lives.

Companion: `mapbox-gl-basics.md`, `leaflet-vs-google-vs-mapbox.md`.

## Provider summary

| Capability | Google Cloud Map Styles | Mapbox Studio | MapLibre + style.json |
|---|---|---|---|
| Editor | Cloud Console, preset-driven | Studio, full style-spec UI | Maputnik (OSS) |
| Source of truth | Map ID in cloud | Mapbox style URL | Your own `style.json` file |
| Version control | Manual versioning per Map ID | Style versions inside Studio | Git |
| Custom fonts/sprites | Limited | Full (upload) | Full (you host) |
| 3D/terrain | Limited | Full | Full |
| Theme switch (light/dark) | Two Map IDs, runtime swap | Two styles or runtime paint changes | Two `style.json` or runtime paint changes |
| Export | Not possible | Export style JSON (v2+ terms restrict reuse) | Native; JSON is the artefact |
| Collaboration | Cloud Console IAM | Studio team seats | Git branches/PRs |

## Decision rule

```text
Brand-heavy, frequent iteration, design team  -> Mapbox Studio (team) or MapLibre + Maputnik
Single brand, Google-ecosystem app            -> Google Cloud Map Styles
Fully open-source + self-hosted tiles         -> MapLibre + style.json in Git
Multiple white-label tenants                  -> MapLibre + templated style.json per tenant
```

## Google Cloud Map Styles (Map IDs)

Workflow:

1. Create a Map ID in Cloud Console > Google Maps Platform > Map Styles.
2. Choose base (roadmap, satellite, hybrid, terrain).
3. Tune feature types (roads, POI, labels), visibility, colour.
4. Save. Reference the Map ID in `new google.maps.Map(..., { mapId })`.
5. Publish changes without redeploying the app.

```ts
const map = new google.maps.Map(el, {
  mapId: "8e0a97af9386fef",             // runtime switchable
  center: { lat: 0.35, lng: 32.58 }, zoom: 13,
});
```

Pros: no code push to change the look. AdvancedMarkerElement requires a Map ID anyway.

Cons: limited palette range, no custom sprites, no export.

## Mapbox Studio

Workflow:

1. Create a style from a template in Studio.
2. Edit layers, colours, fonts, transitions visually.
3. Publish the style; get a `mapbox://styles/user/styleid` URL.
4. In code: `new Map({ style: "mapbox://styles/..." })`.
5. Versioned drafts; publish promotes draft to live.

Key features:

- Upload custom sprites (SVG icons).
- Upload custom fonts.
- Sources panel for private tilesets.
- Expressions UI for data-driven styling.

Dark mode: either publish two styles (light/dark) and swap at runtime, or change paint properties live.

```ts
const styleLight = "mapbox://styles/user/cl...light";
const styleDark = "mapbox://styles/user/cl...dark";

function applyTheme(map: mapboxgl.Map, dark: boolean) {
  const target = dark ? styleDark : styleLight;
  map.setStyle(target, { diff: true });   // diff: true preserves sources where possible
}

window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
  applyTheme(map, e.matches);
});
```

Rule: after `setStyle`, your custom layers/sources are wiped. Re-add them in `map.once("style.load", ...)`.

## MapLibre + style.json

The style is a JSON file you own. Example minimal OSM raster style:

```json
{
  "version": 8,
  "name": "brand-light",
  "sources": {
    "osm": {
      "type": "raster",
      "tiles": ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      "tileSize": 256,
      "attribution": "© OpenStreetMap contributors"
    }
  },
  "layers": [
    { "id": "bg", "type": "background", "paint": { "background-color": "#F3F4F6" } },
    { "id": "osm", "type": "raster", "source": "osm" }
  ]
}
```

Workflow:

1. Author in Maputnik (online editor, imports/exports style.json).
2. Commit to Git (`styles/brand-light.json`).
3. Deploy as static asset; reference its URL from the map.
4. PR-review style changes like code.

```ts
import maplibregl from "maplibre-gl";
const map = new maplibregl.Map({
  container: "map",
  style: "/styles/brand-light.json",
  center: [32.58, 0.35], zoom: 13,
});
```

## Dark mode — three patterns

**A. Two styles, hot swap** (simplest, brief flicker):

```ts
map.setStyle(isDark ? darkStyle : lightStyle, { diff: true });
map.once("style.load", reattachCustomLayers);
```

**B. Paint-property toggle** (no flicker, more code):

```ts
const paint = isDark
  ? { "background-color": "#111827", "text-color": "#E5E7EB" }
  : { "background-color": "#FFFFFF", "text-color": "#111827" };

map.setPaintProperty("background", "background-color", paint["background-color"]);
map.setPaintProperty("poi-labels", "text-color", paint["text-color"]);
```

**C. Single style with expressions driven by a global feature-state** (advanced, keeps one style file):

```json
"fill-color": ["case", ["==", ["global-state", "theme"], "dark"], "#111827", "#FFFFFF"]
```

## Branding tokens

Maintain colours, fonts, and breakpoints in one place. Reference them from the style:

```ts
// tokens.ts
export const brand = {
  primary: "#E11D48",
  accent: "#0EA5E9",
  surface: "#FFFFFF",
  surfaceInverse: "#111827",
  textPrimary: "#111827",
  textInverse: "#F9FAFB",
};

// style-builder.ts
import { brand } from "./tokens";
export function buildStyle(dark: boolean) {
  return {
    version: 8,
    sources: { /* ... */ },
    layers: [
      { id: "bg", type: "background", paint: { "background-color": dark ? brand.surfaceInverse : brand.surface } },
      { id: "roads", source: "...", type: "line", paint: { "line-color": brand.primary } },
    ],
  };
}
```

This keeps web app and map colours in sync when the brand changes.

## Workflow for iterating styles

1. Designer mocks the map look in Figma (palette, label density, icon language).
2. Engineer re-creates in Studio / Maputnik.
3. Export (Mapbox: URL; MapLibre: JSON file).
4. Preview in staging with actual data layers.
5. A/B test against existing style on a sample of users.
6. Promote to prod after metrics (engagement, readability reports) pass.
7. Version the style; keep the previous for quick rollback.

## Icon and sprite management

- Prefer SVG for vector icons; export 1x/2x PNG for Studio/Maputnik sprite generator.
- Include markers, cluster icons, custom symbols.
- Keep the sprite small (<200 KB); large sprites block the first map render.
- Name icons after meaning (`icon-boda-boda`, `icon-matatu`) not shape (`triangle`).

## Performance notes

- Fewer layers render faster. Merge similar layers with expressions.
- Text labels are the most expensive layer. Turn down label density in dense urban styles.
- Raster basemaps are slower than vector. Use vector where possible.
- Use `minzoom`/`maxzoom` aggressively — no point rendering subway labels at z4.

## Anti-patterns

- Checking `mapbox-gl` tokens into git alongside a custom style.
- Editing the same Mapbox style from multiple Studio accounts simultaneously.
- Not reattaching sources/layers after `setStyle` — blank map.
- Hardcoding hex colours inside the map code instead of using brand tokens.
- Designing only for light mode and hoping dark mode works by inversion — contrast and iconography rarely survive.
- Using Google Maps styling JSON (legacy in-code) for new builds when Map IDs are available.
