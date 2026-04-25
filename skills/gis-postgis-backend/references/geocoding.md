# Geocoding

Turn addresses into coordinates (and back). Always cache; every external call costs money or rate-limit budget.

## Options

| Provider | Strength | Cost | Notes |
| --- | --- | --- | --- |
| Google Geocoding API | Best global coverage | Paid, per request | Strict TOS; must display results on a Google map in some tiers |
| Mapbox Geocoding | Strong global, fair pricing | Paid | Permissive TOS; cache allowed |
| Here Geocoding | Enterprise option | Paid | Good for fleet and logistics |
| Nominatim (OSM) | Free, self-hostable | Infra cost | Rate-limited on public server; self-host for volume |
| Photon | OSM-based, typo tolerant | Self-host | Built for autocomplete |
| Pelias | Multi-source OSM | Self-host | Heavier; composable |
| PostGIS Tiger geocoder | US-only | Free | Not relevant for East Africa |
| Custom gazetteer | Your own address table | Your effort | Useful for known estates or project areas |

Rule: prototype with a paid API, move to self-hosted Nominatim when volume or TOS becomes a problem.

## Self-hosted Nominatim

Docker pattern for an Africa-only import to keep the server small:

```bash
docker run -d --name nominatim \
  -e PBF_URL=https://download.geofabrik.de/africa-latest.osm.pbf \
  -e REPLICATION_URL=https://download.geofabrik.de/africa-updates/ \
  -e IMPORT_STYLE=full \
  -e NOMINATIM_PASSWORD=change_me \
  -v nominatim-data:/var/lib/postgresql/14/main \
  -p 8080:8080 \
  mediagis/nominatim:4.4
```

For Uganda only, download the Uganda extract to cut import to ~30 minutes on a 4-core box:

```bash
# https://download.geofabrik.de/africa/uganda-latest.osm.pbf
```

Query:

```bash
curl 'http://localhost:8080/search?q=Garden+City+Kampala&format=jsonv2&limit=1&countrycodes=ug'
```

Reverse:

```bash
curl 'http://localhost:8080/reverse?lat=0.3476&lon=32.5825&format=jsonv2'
```

Respect the [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/) if you ever hit the public server. Self-host for anything above a handful of requests per second.

## Cache schema

Normalised cache keyed by a canonical string, not by raw user input:

```sql
CREATE TABLE geocode_cache (
  id             bigserial PRIMARY KEY,
  address_norm   text        NOT NULL,
  country_code   text        NOT NULL,
  provider       text        NOT NULL,
  lat            double precision NOT NULL,
  lng            double precision NOT NULL,
  geom           geometry(Point, 4326)
                 GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(lng, lat), 4326)) STORED,
  raw_response   jsonb,
  confidence     text,
  hit_count      int         NOT NULL DEFAULT 1,
  first_seen     timestamptz NOT NULL DEFAULT now(),
  last_seen      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (address_norm, country_code, provider)
);

CREATE INDEX idx_geocode_cache_geom ON geocode_cache USING GIST (geom);
CREATE INDEX idx_geocode_cache_last_seen ON geocode_cache (last_seen);
```

## Normalisation function

Whitespace, punctuation, and casing differences are the biggest cache-miss cause.

```sql
CREATE OR REPLACE FUNCTION normalise_address(raw text)
RETURNS text
LANGUAGE sql IMMUTABLE PARALLEL SAFE AS $$
  SELECT
    trim(regexp_replace(
      regexp_replace(
        lower(unaccent(coalesce(raw, ''))),
        '[^a-z0-9 ]', ' ', 'g'
      ),
      '\s+', ' ', 'g'
    ))
$$;
```

Enable once per database:

```sql
CREATE EXTENSION IF NOT EXISTS unaccent;
```

Use:

```sql
INSERT INTO geocode_cache (address_norm, country_code, provider, lat, lng, raw_response)
VALUES (normalise_address(:raw), 'UG', 'nominatim', :lat, :lng, :resp)
ON CONFLICT (address_norm, country_code, provider)
DO UPDATE SET hit_count = geocode_cache.hit_count + 1,
              last_seen = now();
```

## Application flow

```text
raw_input -> normalise -> cache hit? -> return
                         -> miss      -> rate-limit check -> provider call -> store -> return
```

Rate-limit per provider and per user. A pseudocode guard:

```javascript
async function geocode(raw, countryCode = 'UG') {
  const norm = await db.one(`SELECT normalise_address($1) AS n`, [raw]);
  const cached = await db.oneOrNone(
    `SELECT lat, lng FROM geocode_cache
     WHERE address_norm = $1 AND country_code = $2
     ORDER BY provider = 'google' DESC LIMIT 1`,
    [norm.n, countryCode]
  );
  if (cached) return cached;

  await rateLimiter.consume(provider, 1);          // throws if exceeded
  const res = await callProvider(raw, countryCode);
  await db.none(`INSERT INTO geocode_cache ...`, [...]);
  return res;
}
```

## Rate limiting

- Per-provider hard cap (e.g., 1 req/sec for public Nominatim, 50/sec for Mapbox on your plan).
- Per-tenant daily budget to prevent a runaway import from burning the month's quota.
- Circuit breaker on 5xx; fall back to cache-only reads and queue misses.

## Privacy

- Treat geocoded addresses as personal data if tied to a user (home, workplace).
- Retention: expire cache rows after N days unless tied to a persisted record.
- Do not send addresses to third-party APIs if DPIA or data-residency rules say no. Self-hosted Nominatim keeps data in your VPC.
- Log only the `address_norm`, not the raw free-text input, to avoid leaking personal strings into logs.

## Reverse geocoding

```sql
-- Find the nearest cached address
SELECT address_norm, lat, lng,
       ST_Distance(geom::geography, ST_MakePoint(:lng,:lat)::geography) AS metres
FROM geocode_cache
WHERE ST_DWithin(geom::geography, ST_MakePoint(:lng,:lat)::geography, 50)
ORDER BY metres
LIMIT 1;
```

Only as good as your cache. Back with a reverse API call when empty.

## Anti-patterns

- Storing the raw address as the cache key. Whitespace drift guarantees misses.
- No country-code scoping. "Main Street" hits in 50 countries.
- Calling the geocoder inside a synchronous web request without a timeout. Cascading latency.
- Persisting provider-specific opaque IDs as the canonical reference. Providers change.
- Ignoring TOS (e.g., caching Google results long-term when prohibited by your tier).
- Using `pg_trgm` similarity as a replacement for normalisation. Use both.

## Cross-reference

- `references/schema-srid-choice.md` — generated `geom` column pattern.
- `references/tenant-isolation-rls.md` — cache scoped per tenant if addresses are sensitive.
- `gis-maps-integration` — Google/Mapbox geocoding APIs on the frontend.
