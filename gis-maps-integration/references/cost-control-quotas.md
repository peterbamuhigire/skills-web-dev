# Cost control, quotas, and yearly spend review

Every map provider request is a line-item on the bill. This file covers Google, Mapbox, and MapLibre+OSM pricing shape, caching rules, server proxies, per-user rate limits, and the yearly review process.

Companion: `google-maps-setup-keys.md`, `google-places-autocomplete.md`.

## Provider pricing (2025 indicative)

### Google Maps Platform

Monthly USD 200 credit (effectively free tier). After that, per 1,000:

| API | Price (USD/1k) | Notes |
|---|---|---|
| Maps JS Dynamic Map | 7.00 | Per load |
| Maps JS Embed | 0 | Free with link attribution |
| Places Autocomplete (per-session) | 2.83 | Use session tokens |
| Places Autocomplete (per-request) | 2.83 per request | Avoid; missing session tokens |
| Place Details (Basic fields) | 17.00 | Free tier 40/s |
| Place Details (Contact) | 20.00 | |
| Place Details (Atmosphere) | 22.00 | |
| Geocoding | 5.00 | |
| Directions (basic) | 5.00 | |
| Directions (advanced) | 10.00 | `optimizeWaypoints`, traffic |
| Distance Matrix | 5.00 per 1k elements | rows * columns |
| Static Maps | 2.00 | Free tier: 28k/month |

### Mapbox

50,000 free map loads/month. After:

| Product | Price (USD/1k) |
|---|---|
| Map Loads (Web) | 5.00 |
| Vector Tiles API | ~0.50 |
| Raster Tiles API | ~0.50 |
| Geocoding | 0.50 - 0.75 |
| Directions | 2.00 |
| Matrix | 2.00 per 1k |
| Isochrone | 2.00 |
| Temporary/offline downloads | Varies |

### MapLibre + OSM

Library free. Tiles:

- Public OSM tile server: **not permitted for production**. Use only for prototyping.
- Commercial OSM relays: Stadia Maps, MapTiler, Thunderforest, Carto — all offer free tiers and per-1k pricing similar to Mapbox tiles.
- Self-hosted MVT from PostGIS via `pg_tileserv` or Tegola: your only costs are CDN + origin compute (usually $20-200/month for moderate traffic).

## Unit economics

A "reasonable" SaaS uses ~3-5 map views per active user per day in map-heavy flows. At 10k DAU:

- Google: 10k * 4 views * 30 days = 1.2M loads/month - 28k free = 1.17M * 7/1000 = **USD 8,200/month**.
- Mapbox: 1.2M - 50k free = 1.15M * 5/1000 = **USD 5,750/month**.
- MapLibre + self-hosted MVT: CDN bandwidth cost only, perhaps **USD 150/month**.

Cost models scale non-linearly if Places Autocomplete or Directions are used in hot paths.

## Quota architecture

Three layers of cost ceilings:

1. **Provider hard cap** (Cloud Console quota / Mapbox token scope).
2. **Application cap** (your server rate limiter).
3. **User cap** (per-session/per-IP limiter).

### Google quotas

Per-API, per-day, in Cloud Console > IAM & Admin > Quotas:

```text
maps.googleapis.com/maps-javascript-api     20000
places.googleapis.com/autocomplete          10000
places.googleapis.com/details                 5000
geocoding.googleapis.com/geocode              2000
directions.googleapis.com/directions          1000
```

### Mapbox token scopes

Generate separate tokens per use-case:

- `pk.*` public tokens: URL-restricted to your domain; scope `styles:read`, `fonts:read`, `tiles:read`.
- `sk.*` secret tokens: server-only; include `tilesets:*`, `downloads:read`.
- Rotate secret tokens every 90 days.

Mapbox does not have a hard daily cap — use application-level controls.

## Client-side caching

### Places + Geocoding

```ts
class GeocodeCache {
  private readonly ttlMs = 24 * 60 * 60 * 1000; // 24h is typical
  private readonly cache = new Map<string, { value: any; exp: number }>();

  async lookup(q: string, fn: () => Promise<any>) {
    const key = q.toLowerCase().trim();
    const hit = this.cache.get(key);
    if (hit && hit.exp > Date.now()) return hit.value;
    const value = await fn();
    this.cache.set(key, { value, exp: Date.now() + this.ttlMs });
    return value;
  }
}
```

Google Places ToS forbids caching Place IDs or prediction data beyond 30 days and forbids display of stale data without refresh. Autocomplete predictions should **not** be cached long-term.

### Tiles

- Google tiles: cache max 30 days. Browser's HTTP cache handles this; do not extend artificially.
- Mapbox tiles: cache as per response headers. Do not redistribute.
- OSM tiles: Tile Usage Policy; cache aggressively (~1 week+) and always attribute.

## Server proxies

Rationale: hide the key on untrusted clients, add rate-limiting, log usage per tenant, enforce cache.

```ts
// /api/maps/geocode
import { RateLimiter } from "limiter";

const perUser = new Map<string, RateLimiter>();

export async function POST(req: Request) {
  const userId = await authenticate(req);
  if (!userId) return new Response("Unauthorized", { status: 401 });

  const limiter = perUser.get(userId) ??
    perUser.set(userId, new RateLimiter({ tokensPerInterval: 30, interval: "minute" })).get(userId)!;
  if (!(await limiter.tryRemoveTokens(1))) return new Response("Too many requests", { status: 429 });

  const { address } = await req.json();
  const cacheKey = `geo:${address.toLowerCase()}`;
  const cached = await redis.get(cacheKey);
  if (cached) return Response.json(JSON.parse(cached));

  const url = new URL("https://maps.googleapis.com/maps/api/geocode/json");
  url.searchParams.set("address", address);
  url.searchParams.set("key", process.env.GMAPS_SERVER_KEY!);
  url.searchParams.set("region", "UG");
  const r = await fetch(url);
  const data = await r.json();

  await redis.set(cacheKey, JSON.stringify(data), "EX", 24 * 60 * 60);
  await usageLog({ userId, api: "geocode", ts: Date.now() });
  return Response.json(data);
}
```

Benefits:

- Per-user rate limiting.
- Response cache (Redis), cutting repeat spend.
- Usage log for cost attribution per tenant.
- Abuse detection (IP + user-id anomaly).

## Per-user rate limiting rules

Guide for common endpoints:

| Endpoint | Per-user limit |
|---|---|
| Geocoding | 30/minute, 500/day |
| Places Autocomplete | 60/minute, 1000/day |
| Directions | 30/minute, 300/day |
| Distance Matrix | 10/minute, 100/day |

Trigger a captcha or tier-up requirement when a user consistently hits limits.

## Tile caching for self-hosted MVT

```text
Client -> CDN (CloudFront/Cloudflare) -> Origin (pg_tileserv)
```

Rules:

- `Cache-Control: public, max-age=86400, s-maxage=604800` on MVT tiles.
- `ETag`-based revalidation for data that changes daily.
- Invalidate cache by path pattern when the underlying dataset changes.
- Precompute and store PMTiles for read-heavy, static layers.

## Monitoring and alerting

Metrics to track per provider:

```text
maps_requests_total{provider, api}
maps_spend_usd{provider}           # computed from request counts * unit price
maps_errors_total{provider, code}
maps_cache_hits_total{api}
maps_rate_limit_drops_total{user}
```

Alert rules:

- Spend pace >120% of monthly budget at day-10 projection.
- Errors > 1% of requests over 15 min.
- Single-user spend > 1% of tenant cap.
- New unique-referrer domain appears (possible key leak).

## Yearly cost review

Every January:

1. Pull last 12 months of invoices by API and by day.
2. Compute per-user and per-tenant cost.
3. Rank by cost; look for one or two APIs dominating (usually Places + Directions).
4. Compare to MapLibre + OSRM + Pelias migration cost:
   - Engineering: ~1 engineer-month for basic migration.
   - Ops: tile server + OSRM/Valhalla on VMs or managed (Stadia, MapTiler) — budget USD 200-2,000/month.
5. Decide:
   - Spend < 2x migration amortised over 12 months: stay.
   - Spend > 2x: migrate at least the highest-cost API.
6. Document the decision as an ADR; revisit next year.

## ADR template

```markdown
# ADR-012 Map provider choice for 2026

## Context
Current spend: USD X/month. Fastest-growing API: Places Autocomplete.
Alternatives considered: MapLibre + Pelias, switch Directions to OSRM.

## Decision
Keep Google Maps for Places. Migrate Directions to Mapbox Directions API.
Expected saving: USD Y/month.

## Consequences
- Requires adding Mapbox provider abstraction.
- Removes waypoint optimisation from some flows (acceptable: <50 uses/month).
- Revisit in Q3 2026 once tenant growth is known.
```

## Anti-patterns

- Shipping to prod without any quota cap.
- Not proxying Geocoding through the server — every tenant hits the browser key.
- Caching Places Autocomplete predictions for weeks (ToS violation).
- Treating MapLibre as "free" without costing the ops work to host tiles.
- No yearly review; spend drifts 3-5x in two years.
- Using Google `billing_alerts` without also setting quota caps — alerts without caps are post-mortems.
