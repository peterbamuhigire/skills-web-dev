# Google Places Autocomplete — cost-safe patterns

Places Autocomplete is the most-abused Google API because each keystroke can spawn a billable request. Get the billing model and field masks right or the monthly bill explodes.

Companion: `cost-control-quotas.md`, `google-maps-setup-keys.md`.

## Billing model (session tokens are the lever)

Two SKUs matter:

1. **Autocomplete (per session)** — USD 2.83 per 1,000 sessions. A session groups autocomplete requests + the eventual Place Details fetch. You pay once per session, regardless of keystrokes.
2. **Autocomplete (per request)** — USD 2.83 per 1,000 requests, no session token. You pay per keystroke.

Rule: **always use a session token.** Without it, a 10-character typed query with 10 predictions costs ~10x more.

The session token is a client-generated UUID you pass with every autocomplete request in that session and then with the `getDetails` call that closes it. A session ends when:

- `getDetails` is called, or
- No request is made for several minutes (Google closes it automatically).

## Widget pattern (simplest)

```ts
import { mapsLoader } from "@/config/maps";

export async function attachAutocomplete(input: HTMLInputElement) {
  const { Autocomplete } = await mapsLoader.importLibrary("places");

  const ac = new Autocomplete(input, {
    componentRestrictions: { country: ["ug", "ke", "tz", "rw"] },
    fields: ["place_id", "formatted_address", "geometry.location", "name"],
    types: ["address"],
  });

  ac.addListener("place_changed", () => {
    const p = ac.getPlace();
    if (!p.geometry?.location) return; // user hit Enter without picking
    onPicked({
      placeId: p.place_id!,
      address: p.formatted_address!,
      lat: p.geometry.location.lat(),
      lng: p.geometry.location.lng(),
      name: p.name,
    });
  });

  return ac;
}
```

The widget manages the session token internally. You do not see it, but billing treats the whole interaction as one session as long as the user picks from the dropdown.

## Headless pattern (full control)

Use when you need a custom UI — listbox, maps-style suggestions, or wrapping in React/Vue components.

```ts
import { mapsLoader } from "@/config/maps";

type Suggestion = { description: string; placeId: string };

export class AddressSearch {
  private service!: google.maps.places.AutocompleteService;
  private details!: google.maps.places.PlacesService;
  private sessionToken!: google.maps.places.AutocompleteSessionToken;

  async init(mapOrDiv: google.maps.Map | HTMLDivElement) {
    const { AutocompleteService, AutocompleteSessionToken, PlacesService } =
      await mapsLoader.importLibrary("places");
    this.service = new AutocompleteService();
    this.details = new PlacesService(mapOrDiv as HTMLDivElement);
    this.sessionToken = new AutocompleteSessionToken();
  }

  async predict(input: string, bounds?: google.maps.LatLngBounds): Promise<Suggestion[]> {
    if (input.length < 3) return [];
    const { predictions } = await this.service.getPlacePredictions({
      input,
      sessionToken: this.sessionToken,
      componentRestrictions: { country: ["ug"] },
      locationBias: bounds,
      types: ["address"],
    });
    return predictions.map((p) => ({ description: p.description, placeId: p.place_id }));
  }

  async resolve(placeId: string): Promise<{ lat: number; lng: number; address: string } | null> {
    return new Promise((resolve) => {
      this.details.getDetails(
        {
          placeId,
          fields: ["formatted_address", "geometry.location"],
          sessionToken: this.sessionToken,
        },
        (place, status) => {
          if (status !== google.maps.places.PlacesServiceStatus.OK || !place?.geometry?.location) {
            resolve(null);
            return;
          }
          resolve({
            address: place.formatted_address!,
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng(),
          });
          // Session closes here. Rotate for next search.
          this.sessionToken = new google.maps.places.AutocompleteSessionToken();
        }
      );
    });
  }
}
```

Key points:

- Rotate the session token after every `resolve`.
- Do not call `getPlacePredictions` without a session token unless you know why.
- The `PlacesService` needs a `Map` or a hidden `<div>` for attribution — pass one.

## Debounce + minimum length

```ts
function debounce<T extends (...a: any[]) => any>(fn: T, ms = 250) {
  let t: any;
  return (...args: Parameters<T>) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}

const search = new AddressSearch();
await search.init(mapDiv);

const onInput = debounce(async (q: string) => {
  if (q.length < 3) return renderSuggestions([]);
  const results = await search.predict(q);
  renderSuggestions(results);
}, 250);

inputEl.addEventListener("input", (e) => onInput((e.target as HTMLInputElement).value));
```

Rules:

- Minimum 3 characters before first call.
- Debounce 200-300 ms on keystrokes.
- Abort in-flight requests when a newer one starts (AbortController if using REST).

## Field masks (critical cost lever)

Fields fall into three billing tiers. Requesting an expensive field pulls the whole request into that tier for the session.

| Tier | Examples | Cost per 1,000 |
|---|---|---|
| Basic | `place_id`, `name`, `geometry.location`, `formatted_address`, `address_components`, `types` | USD 17 per 1k Place Details calls |
| Contact | `website`, `formatted_phone_number`, `opening_hours` | USD 20 per 1k |
| Atmosphere | `rating`, `reviews`, `user_ratings_total`, `price_level`, `photos` | USD 22 per 1k |

Rule: request only the fields you render. Never `fields: ["ALL_FIELDS"]` or omit `fields` altogether.

## Country + bounds restrictions

```ts
// Country restriction (hard filter)
componentRestrictions: { country: ["ug"] }

// Location bias (soft, prefers nearby)
locationBias: new google.maps.LatLngBounds(
  { lat: 0.2, lng: 32.4 },
  { lat: 0.5, lng: 32.7 }
)

// Strict bounds (old API; prefer locationBias)
bounds: latLngBounds,
strictBounds: true,
```

Choose:

- One country, fixed: `componentRestrictions`.
- Multi-country cross-border region (East Africa): array of countries in `componentRestrictions`.
- Prefer-local but allow-out-of-bounds: `locationBias`.

## Caching + client-side deduplication

```ts
const cache = new Map<string, Suggestion[]>();

async function predictCached(q: string): Promise<Suggestion[]> {
  const key = q.toLowerCase().trim();
  if (cache.has(key)) return cache.get(key)!;
  const r = await search.predict(q);
  cache.set(key, r);
  // Bounded cache to avoid memory leak
  if (cache.size > 200) cache.delete(cache.keys().next().value);
  return r;
}
```

- Store by normalised query string.
- Never cache Place Details results per-user if they are billed per session — Google's caching rules forbid long-term caching of autocomplete predictions.

## Server-side fallback (proxy pattern)

For compliance, audit, or hiding the key on untrusted clients, proxy through your backend:

```ts
// Next.js route handler
export async function GET(req: Request) {
  const q = new URL(req.url).searchParams.get("q") ?? "";
  const session = new URL(req.url).searchParams.get("session") ?? "";
  if (q.length < 3) return Response.json({ predictions: [] });

  const url = new URL("https://maps.googleapis.com/maps/api/place/autocomplete/json");
  url.searchParams.set("input", q);
  url.searchParams.set("sessiontoken", session);
  url.searchParams.set("components", "country:ug");
  url.searchParams.set("key", process.env.GMAPS_SERVER_KEY!); // IP-restricted
  const r = await fetch(url);
  return new Response(await r.text(), { headers: { "content-type": "application/json" } });
}
```

Trade-off: you now pay for each request (no widget session billing optimisation) unless you explicitly forward a session token end-to-end including to the Place Details proxy. Design the session lifecycle carefully.

## Error handling

```ts
try {
  const { predictions } = await service.getPlacePredictions({ input, sessionToken });
} catch (err: any) {
  if (err?.code === "ZERO_RESULTS") return [];
  if (err?.code === "OVER_QUERY_LIMIT") {
    showToast("Search temporarily unavailable");
    captureException(err);
    return [];
  }
  if (err?.code === "REQUEST_DENIED") {
    // Key misconfigured or restriction failed
    captureException(err);
    return [];
  }
  return [];
}
```

Graceful degradation: on hard failure, fall back to a plain address input (manual typing), not an empty list that confuses the user.

## Accessibility

- Listbox pattern with `role="combobox"`, `aria-expanded`, `aria-autocomplete="list"`.
- Arrow keys navigate, Enter selects, Escape closes.
- Announce "3 addresses suggested" via `aria-live="polite"` for screen readers.
- See `a11y-maps.md`.

## Anti-patterns

- No session token — silent 5-10x overspend.
- Requesting atmosphere fields for every address lookup.
- Calling autocomplete on every keystroke without debounce.
- Not rotating the session token after `getDetails`.
- Relying only on `componentRestrictions` without `locationBias` when a city-level preference exists.
- Trusting the client to pass the right fields — always validate server-side when proxying.
