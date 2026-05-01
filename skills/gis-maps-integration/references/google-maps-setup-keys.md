# Google Maps setup, keys, and quota governance

Covers loader usage, key restrictions per environment, budget alerts, quota caps, and the runbook for a leaked key. Pair with `cost-control-quotas.md`.

## Environments and key topology

One key per environment. Never reuse keys between dev, staging, and prod.

```text
GMAPS_KEY_DEV       -> localhost:*, *.dev.example.com
GMAPS_KEY_STAGING   -> staging.example.com
GMAPS_KEY_PROD      -> app.example.com, www.example.com
GMAPS_KEY_SERVER    -> server-side only, IP-restricted
```

Rules:

- Frontend keys are always HTTP-referrer restricted.
- Server-side keys (Geocoding from backend, Directions batch) are IP-restricted.
- Never put the server key in the browser bundle.
- Rotate keys every 90 days or immediately after an incident.

## Loader (`@googlemaps/js-api-loader`)

```ts
import { Loader } from "@googlemaps/js-api-loader";

export const mapsLoader = new Loader({
  apiKey: import.meta.env.VITE_GMAPS_KEY,
  version: "weekly",            // "quarterly" in prod to avoid mid-release regressions
  libraries: ["places", "geometry", "marker"],
  language: "en-GB",
  region: "UG",
  retries: 3,
});

export async function initMap(containerId: string) {
  const { Map } = await mapsLoader.importLibrary("maps");
  const { AdvancedMarkerElement } = await mapsLoader.importLibrary("marker");

  const el = document.getElementById(containerId);
  if (!el) throw new Error(`Map container ${containerId} not found`);

  const map = new Map(el, {
    center: { lat: 0.3476, lng: 32.5825 },
    zoom: 13,
    mapId: import.meta.env.VITE_GMAPS_MAP_ID, // required for AdvancedMarkerElement
    disableDefaultUI: false,
    gestureHandling: "cooperative",
  });

  return { map, AdvancedMarkerElement };
}
```

Decision rules:

- Use `version: "weekly"` in dev to get current library; pin to `"quarterly"` in prod.
- Always set `region` and `language` — affects geocoding bias and UI locale.
- Only load libraries you use; each `importLibrary` triggers a fetch.
- `mapId` is mandatory if you use `AdvancedMarkerElement` or Cloud Map Styles.

## Key restrictions (Cloud Console)

### Application restrictions

- **HTTP referrer (websites)**: exact patterns.
  - Good: `https://app.example.com/*`
  - Bad: `*` or `*.example.com/*` without TLS scheme
- **IP addresses (servers)**: the static egress IP of your API server or NAT gateway.
- **None**: only acceptable for a temporary debug key that never enters source control or bundles.

### API restrictions

Enable only the APIs the key needs. A frontend key typically enables:

- Maps JavaScript API
- Places API (if autocomplete)
- Geocoding API (if client-side reverse geocoding)

Never enable Directions API on a frontend key if you can call it server-side — the routing key is a prime abuse target.

## Quota caps (hard cost ceiling)

Per-API daily quotas in Cloud Console. Set them even if you have billing alerts.

```text
Maps JavaScript API - Dynamic Maps (per-day): 20000
Places Autocomplete - Per Session: 10000
Places Details (per-day): 5000
Geocoding API (per-day): 2000
Directions API (per-day): 1000
```

Formula:

```text
daily_cap = (expected_daily_volume_p95) * 1.5
          + 500 buffer for ops
```

If you hit the cap, users get a graceful error, not an open meter.

## Budget alerts

Configure in Billing > Budgets & Alerts, per billing account:

- Monthly budget = expected spend * 1.2
- Alerts at 50%, 80%, 100% to the engineering pager email.
- Notification channel: email + Pub/Sub -> Slack webhook.

```json
{
  "budget": {
    "displayName": "prod-maps-monthly",
    "budgetFilter": { "projects": ["projects/123"] },
    "amount": { "specifiedAmount": { "currencyCode": "USD", "units": "500" } },
    "thresholdRules": [
      { "thresholdPercent": 0.5 },
      { "thresholdPercent": 0.8 },
      { "thresholdPercent": 1.0 }
    ]
  }
}
```

## Env wiring

```ts
// config/maps.ts
const required = ["VITE_GMAPS_KEY", "VITE_GMAPS_MAP_ID"] as const;

for (const k of required) {
  if (!import.meta.env[k]) {
    throw new Error(`Missing ${k}. Check .env.${import.meta.env.MODE}`);
  }
}

export const MAPS_CONFIG = {
  key: import.meta.env.VITE_GMAPS_KEY as string,
  mapId: import.meta.env.VITE_GMAPS_MAP_ID as string,
  stage: import.meta.env.MODE as "development" | "staging" | "production",
};
```

`.env` files must never be committed. Add them to `.gitignore`. Use your secret manager (AWS Secrets Manager, GCP Secret Manager) for server keys. In CI, inject via encrypted variables.

## Leaked key runbook

Assume the key is leaked the moment it appears anywhere public (GitHub push, client log, screenshot, support ticket).

```text
1. Open Cloud Console > APIs & Services > Credentials.
2. Create a replacement key with the same restrictions.
3. Update .env and CI secrets; deploy the change.
4. Verify the new key works in prod (synthetic check).
5. Delete the leaked key.
6. Inspect "Usage" and "Billing Reports" for the last 48 hours.
7. Run `git log -p --all -S"AIza"` to find any other leaks.
8. File a post-incident doc: what, when, blast radius, cost.
9. Push-protection: enable GitHub Secret Scanning or gitleaks in CI.
```

Common sources of leaks:

- Hardcoded in a committed `config.js`.
- Included in a bundled `.map` file served to the browser.
- Logged in a 500 response body.
- Pasted into a public Slack channel or forum post.
- Embedded in a redistributed Postman collection.

## Key hygiene checks

Run in CI before a deploy:

```bash
# Refuse a commit containing a Google API key pattern
grep -R --exclude-dir=node_modules -E "AIza[0-9A-Za-z_-]{35}" src/ && {
  echo "ERROR: hardcoded Google API key detected"
  exit 1
}
```

Also:

- `gitleaks detect --source . --exit-code 1`
- Review `.env.example` files: they should contain placeholders, never real keys.
- Confirm in prod bundle: only the restricted frontend key, never the server key.

## Loading strategies

- **Defer load**: only call `loader.load()` when the map enters the viewport (IntersectionObserver).
- **Preconnect**: `<link rel="preconnect" href="https://maps.googleapis.com">`.
- **Fallback**: if the loader times out (>5s), render a static map image from Maps Static API as the placeholder.

```ts
async function safeInit(el: HTMLElement) {
  try {
    return await Promise.race([
      initMap(el.id),
      new Promise((_, reject) => setTimeout(() => reject(new Error("timeout")), 5000)),
    ]);
  } catch (err) {
    console.error("maps init failed", err);
    el.innerHTML = `<img src="${staticMapFallback()}" alt="map preview" />`;
    return null;
  }
}
```

## Anti-patterns

- One key for everything: when it leaks you have no recovery path.
- No quota cap: a single abuse campaign can cost thousands overnight.
- Using `version: "latest"` in prod: subtle breakage on Google's release cadence.
- Requesting `places`, `geometry`, `drawing`, `visualization` when you use none of them.
- Skipping `mapId`: advanced markers silently fall back to the old marker with no error.
- Restricting by referrer but allowing `*.example.com/*`: forgotten subdomains become free proxies.
