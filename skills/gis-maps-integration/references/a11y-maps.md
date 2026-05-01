# Accessible maps — text alternatives, keyboard, screen readers, ARIA

Maps are image-heavy interactive widgets. Default implementations are hostile to screen readers and keyboard users. This reference gives concrete patterns for WCAG 2.2 AA compliance on Google, Mapbox, and MapLibre maps.

Companion: `laws-of-ux`, `ux-principles-101`.

## Core rule

A map is not a replacement for accessible information. It is an **enhancement** of accessible information. Always provide an accessible equivalent of what the map shows.

## Text alternative patterns

### Pattern 1: Sibling list

Alongside every data map, render a list of the same data:

```html
<section aria-labelledby="branches-heading">
  <h2 id="branches-heading">Our branches</h2>

  <div id="map" role="application" aria-label="Map showing 12 branches in Kampala. Use Tab to focus the list below."></div>

  <ul aria-label="List of branches">
    <li>
      <button data-lat="0.315" data-lng="32.582">
        Kampala Central, Plot 12 Kampala Road. Open 8am to 6pm.
      </button>
    </li>
    <!-- ... -->
  </ul>
</section>
```

- The map is decorative-plus-interactive. The list is authoritative.
- Clicking a list button pans/zooms the map and opens the popup.
- The list is always keyboard-reachable and screen-reader-friendly.

### Pattern 2: Search + results

For "find the nearest X" flows, the primary interface is a search box and results list. The map is a visual aid next to it.

### Pattern 3: Static image with text

For purely decorative "find us" pages, a static map image plus address text beats a full interactive map.

## Keyboard controls

### Google Maps

Google Maps has built-in keyboard navigation when the map is focused:

- Arrow keys pan.
- `+` / `-` zoom.
- `Tab` moves between interactive elements.
- Focus indicators work out of the box.

Ensure:

```ts
const map = new google.maps.Map(el, {
  keyboardShortcuts: true,   // default is true
  gestureHandling: "cooperative",  // prevents page-jump scroll traps
});
```

### Mapbox GL / MapLibre

Keyboard handler is on by default but initial focus is not. Provide a clear focus path:

```ts
map.getCanvas().setAttribute("tabindex", "0");
map.getCanvas().setAttribute("role", "application");
map.getCanvas().setAttribute("aria-label", "Map of delivery zones. Arrow keys to pan, plus and minus to zoom.");

// Ensure visible focus ring
const style = document.createElement("style");
style.textContent = `.mapboxgl-canvas:focus { outline: 2px solid #2563EB; outline-offset: 2px; }`;
document.head.appendChild(style);
```

Built-in bindings (Mapbox/MapLibre):

- Arrow keys pan.
- `=`/`+` zoom in, `-`/`_` zoom out.
- `Shift+arrows` rotate (bearing).
- `Q` reset bearing.

### Escape to close popups

```ts
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    document.querySelectorAll(".mapboxgl-popup-close-button").forEach((b) => (b as HTMLButtonElement).click());
  }
});
```

## Screen reader announcements

Use an ARIA live region to announce map state changes:

```html
<div id="map-live" aria-live="polite" aria-atomic="true" class="sr-only"></div>
```

```ts
function announce(msg: string) {
  const el = document.getElementById("map-live");
  if (!el) return;
  el.textContent = "";
  requestAnimationFrame(() => (el.textContent = msg));
}

map.on("zoomend", () => announce(`Zoom level ${Math.round(map.getZoom())}`));
map.on("moveend", () => {
  const c = map.getCenter();
  announce(`Centred at ${c.lat.toFixed(3)}, ${c.lng.toFixed(3)}`);
});
```

Use `aria-live="polite"` — not `assertive` — to avoid interrupting the user.

Rate-limit announcements: moving the map continuously should not flood the screen reader.

```ts
let announceTimer: any;
function debouncedAnnounce(msg: string) {
  clearTimeout(announceTimer);
  announceTimer = setTimeout(() => announce(msg), 400);
}
```

## ARIA for markers

HTML markers (Mapbox) can be made accessible:

```ts
const el = document.createElement("button");
el.className = "marker";
el.setAttribute("aria-label", `Delivery point ${point.code}, ${point.address}`);
el.setAttribute("type", "button");
el.textContent = point.code;
el.addEventListener("click", () => openPopup(point));
el.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    openPopup(point);
  }
});

new mapboxgl.Marker({ element: el }).setLngLat([point.lng, point.lat]).addTo(map);
```

For symbol or circle layers, markers are drawn in canvas and are **not** keyboard-reachable. This is fine when you provide the sibling list; that list is the keyboard path.

For Google `AdvancedMarkerElement`, markers are DOM and keyboard-focusable by default with `gmpClickable: true`.

## Focus management

- Focus should go **into** the map container, not on stray sub-elements first.
- After interacting (picking an address), return focus to a predictable place — usually the input or next control.
- Popups should trap focus while open and return it on close.

```ts
function openPopupAccessibly(popup: mapboxgl.Popup, trigger: HTMLElement) {
  popup.addTo(map);
  const el = popup.getElement();
  const closeBtn = el.querySelector<HTMLButtonElement>(".mapboxgl-popup-close-button");
  closeBtn?.focus();
  popup.once("close", () => trigger.focus());
}
```

## Colour contrast

WCAG 2.2 AA requires:

- 4.5:1 for text over the map.
- 3:1 for non-text UI (markers on map, controls, focus indicator).

Checks:

- Dark markers on light map: aim for #1F2937 on #F3F4F6 = 13:1.
- Coloured status markers (green/amber/red) must pair with shape or label, not colour alone.
- Labels over imagery (satellite layers) need halo/stroke for contrast:

```ts
map.setPaintProperty("labels", "text-halo-color", "#FFFFFF");
map.setPaintProperty("labels", "text-halo-width", 1.5);
```

## Colour-independent indicators

Never rely on colour alone:

- Use icon shape + colour (triangle for warning, circle for info).
- Use text label ("Available", "Sold") in the popup.
- Pattern-fill polygons (stripes for restricted, solid for allowed).

## Drag-to-place alternative

If the UX allows dragging a marker to set a location:

- Always offer a text address input as the primary path.
- The drag is an enhancement, not a requirement.
- Provide a "Use current location" button that calls `navigator.geolocation.getCurrentPosition`.

```html
<label for="addr-input">Enter the delivery address</label>
<input id="addr-input" autocomplete="street-address" />
<button type="button" id="use-location">Use my current location</button>
```

## Reduced motion

Disable animations for users who prefer reduced motion:

```ts
const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

map.easeTo({
  center: [lng, lat],
  duration: prefersReduced ? 0 : 500,
});
```

Set Mapbox's global:

```ts
if (prefersReduced) {
  map.getMap().setRenderWorldCopies(false);
  // No auto-rotate, no fly-to; use jumpTo instead of flyTo
}
```

## High-contrast and forced-colours mode

In Windows high contrast mode (`forced-colors: active`), the map canvas is still rendered but controls may lose visual distinction:

```css
@media (forced-colors: active) {
  .mapboxgl-ctrl button { border: 1px solid ButtonText; }
  .mapboxgl-popup-content { border: 1px solid CanvasText; }
}
```

Do not rely on background colours — use the system colour keywords.

## Testing

- Screen readers: test with NVDA (Windows), VoiceOver (macOS/iOS), TalkBack (Android).
- Keyboard-only: unplug mouse, tab through the page, verify every map action has a non-map equivalent.
- axe DevTools or Lighthouse > Accessibility for automated coverage.
- Manual: zoom to 200% page zoom, ensure controls still usable.
- Colour vision: use Sim Daltonism / Chrome DevTools > Rendering > Emulate vision deficiency.

## Legal baseline

- WCAG 2.2 AA is the target.
- EU EN 301 549 and US Section 508 incorporate WCAG.
- Add an **accessibility statement** page linking to the text alternatives.

## Anti-patterns

- Relying on the map as the only way to find information.
- Canvas-rendered markers without a sibling list or search.
- Auto-open tooltip on hover that screen-reader users can never trigger.
- Rainbow status markers with no shape or label difference.
- No focus indicator on the map canvas (Mapbox default until `tabindex` is set).
- `aria-live="assertive"` on map state changes — overwhelms screen-reader users.
- Pop-up with close button not keyboard-reachable.
- Drag-to-place with no typed-address alternative.
