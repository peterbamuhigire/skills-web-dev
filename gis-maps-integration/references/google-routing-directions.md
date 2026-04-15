# Google Directions, Distance Matrix, and turn-by-turn

Covers when to use Directions vs Distance Matrix, waypoint optimisation, traffic, alternatives, travel modes, and how to bind routes to the map. Turn-by-turn itself belongs in the Navigation SDK on mobile — the web renders routes but should not pretend to navigate.

Companion: `cost-control-quotas.md`.

## Services at a glance

| Service | Purpose | Billing |
|---|---|---|
| Directions API | One origin + one destination + optional waypoints, returns a route. | USD 5 per 1,000 |
| Directions + `optimizeWaypoints` | As above, reorders waypoints to minimise distance/time. | USD 10 per 1,000 (advanced) |
| Directions with traffic | Driving mode, `drivingOptions.trafficModel`. | USD 10 per 1,000 (advanced) |
| Distance Matrix | M origins x N destinations, returns a matrix of distances/times. | USD 5 per 1,000 elements |
| Routes API (new) | Successor to Directions + Matrix. Better pricing and features. | See Routes API pricing |

Rule: for new code, prefer the **Routes API** (`routes.googleapis.com`). It supports compute-routes, compute-route-matrix, better tolls/traffic, and Field Masks. The legacy Directions service is still widely used in Maps JS.

## Basic directions (legacy, Maps JS)

```ts
async function renderRoute(
  map: google.maps.Map,
  origin: google.maps.LatLngLiteral,
  destination: google.maps.LatLngLiteral
) {
  const { DirectionsService, DirectionsRenderer, TravelMode } =
    await mapsLoader.importLibrary("routes");

  const service = new DirectionsService();
  const renderer = new DirectionsRenderer({
    map,
    suppressMarkers: false,
    draggable: false,
    polylineOptions: { strokeColor: "#E11D48", strokeWeight: 5, strokeOpacity: 0.8 },
  });

  const result = await service.route({
    origin,
    destination,
    travelMode: TravelMode.DRIVING,
    provideRouteAlternatives: true,
    drivingOptions: {
      departureTime: new Date(),
      trafficModel: google.maps.TrafficModel.BEST_GUESS,
    },
  });

  renderer.setDirections(result);
  return result;
}
```

Key options:

- `provideRouteAlternatives: true` — returns up to three routes; the first is the recommended.
- `drivingOptions.trafficModel` — `BEST_GUESS`, `OPTIMISTIC`, `PESSIMISTIC`. Requires `departureTime`.
- `avoid: ["tolls", "highways", "ferries"]` — hard avoidance.
- `region: "UG"` — biases geocoding of string origins/destinations.

## Waypoint optimisation (VRP-lite)

Directions handles up to 25 waypoints per request with `optimizeWaypoints`:

```ts
const result = await service.route({
  origin: depot,
  destination: depot,                            // return to start = round trip
  waypoints: stops.map((s) => ({ location: s, stopover: true })),
  optimizeWaypoints: true,
  travelMode: TravelMode.DRIVING,
});

const ordered = result.routes[0].waypoint_order.map((i) => stops[i]);
```

Limits:

- Max 25 waypoints (10 for free-tier, 25 advanced).
- Optimisation is a TSP heuristic, not exact. For >25 stops or constraints (time windows, capacities), use a VRP engine (OR-Tools, Routific).
- Each request with optimisation counts as Advanced Directions — USD 10 per 1,000.

## Alternatives + choosing

```ts
if (result.routes.length > 1) {
  const choice = result.routes
    .map((r, i) => ({ i, duration: r.legs[0].duration!.value }))
    .sort((a, b) => a.duration - b.duration)[0];
  renderer.setRouteIndex(choice.i);
}
```

Common selection rules:

- Pick fastest under current traffic (`duration_in_traffic`).
- Pick shortest distance for a fuel-sensitive fleet.
- Prefer a route without tolls for cash-paying couriers.

## Travel modes

| Mode | Notes |
|---|---|
| `DRIVING` | Default; supports traffic, tolls, and alternatives. |
| `WALKING` | No traffic; avoid highways automatically. |
| `BICYCLING` | Availability varies by country. Often missing in East Africa. |
| `TRANSIT` | Schedules, modes (bus/rail), accessibility. Needs `transitOptions`. |
| `TWO_WHEELER` | Routes API only; motorcycle-friendly. Critical for boda-boda logistics. |

Check mode availability per region before committing — `BICYCLING` returns `ZERO_RESULTS` in much of Africa.

## Distance Matrix (many-to-many)

For "which of these 20 drivers is closest to this pickup?":

```ts
const { DistanceMatrixService } = await mapsLoader.importLibrary("routes");
const dm = new DistanceMatrixService();

const res = await dm.getDistanceMatrix({
  origins: drivers.map((d) => d.location),
  destinations: [pickup],
  travelMode: google.maps.TravelMode.DRIVING,
  drivingOptions: { departureTime: new Date(), trafficModel: google.maps.TrafficModel.BEST_GUESS },
});

const closest = drivers
  .map((d, i) => ({ d, secs: res.rows[i].elements[0].duration_in_traffic?.value ?? Infinity }))
  .sort((a, b) => a.secs - b.secs)[0];
```

Billing is per element (rows x columns). A 20x20 request = 400 elements. Keep matrices small.

## Traffic layer (visualisation only)

```ts
const trafficLayer = new google.maps.TrafficLayer();
trafficLayer.setMap(map);
// To hide
trafficLayer.setMap(null);
```

This is purely visual. It does not affect routing; for traffic-aware routes, set `drivingOptions`.

## Rendering custom route UI

```ts
const route = result.routes[0];
const leg = route.legs[0];

console.log("Distance:", leg.distance!.text);     // "12.4 km"
console.log("Duration:", leg.duration!.text);     // "24 mins"
console.log("With traffic:", leg.duration_in_traffic?.text);

for (const step of leg.steps) {
  console.log(step.instructions);                 // HTML; sanitise before rendering
  console.log(step.distance?.text, step.maneuver); // e.g. "turn-right"
}
```

Rule: `step.instructions` is HTML from Google. Do not `innerHTML` without sanitising (DOMPurify) or use only the text content.

## Turn-by-turn on web?

Short answer: no. The web Directions API is not designed for live turn-by-turn voice guidance. For that, use:

- **Mapbox Navigation SDK** on mobile.
- **Google Navigation SDK** on Android/iOS (enterprise licence required).
- A custom UI that shows the next step as the user crosses step thresholds (approximation; do not market as navigation).

## Integrating with a live map

Pattern: render the route, fit bounds, show origin/destination markers, keep one `DirectionsRenderer` instance.

```ts
class RouteController {
  private renderer?: google.maps.DirectionsRenderer;
  constructor(private map: google.maps.Map) {}

  async route(o: google.maps.LatLngLiteral, d: google.maps.LatLngLiteral) {
    const { DirectionsService, DirectionsRenderer } =
      await mapsLoader.importLibrary("routes");
    if (!this.renderer) this.renderer = new DirectionsRenderer({ map: this.map });
    const svc = new DirectionsService();
    const result = await svc.route({ origin: o, destination: d, travelMode: google.maps.TravelMode.DRIVING });
    this.renderer.setDirections(result);
    const bounds = result.routes[0].bounds;
    if (bounds) this.map.fitBounds(bounds, 48);
    return result;
  }

  clear() {
    this.renderer?.setDirections({ routes: [] } as any);
  }
}
```

## Error handling

```ts
try {
  const r = await service.route({ ... });
} catch (err: any) {
  switch (err.code) {
    case "ZERO_RESULTS": return showToast("No route found");
    case "OVER_QUERY_LIMIT": return showToast("Please try again shortly");
    case "REQUEST_DENIED":
    case "INVALID_REQUEST":
      captureException(err); return showToast("Routing unavailable");
    default: throw err;
  }
}
```

## Routes API (new) — why migrate

- Field masks (only pay for what you request).
- Two-wheeler profile (critical for bike/moto delivery).
- Better pricing tiers.
- Eco-friendly routes (fuel-consumption model).
- Route Optimization API (real VRP solver).

Migration is a server-side concern — the client still displays a polyline either way. Start server-side in new features and leave widget-driven renderers on the legacy API until there is a reason to change.

## Anti-patterns

- Re-routing on every map pan or marker drag (expensive).
- Using Distance Matrix when one-to-one Directions would do.
- Ignoring `duration_in_traffic` and showing only `duration` in driver ETA UIs.
- Building turn-by-turn voice guidance with the web Directions API.
- Hardcoding step instructions; always read from `step.instructions` to stay localised.
- Storing routes for >30 days (violates Google ToS).
