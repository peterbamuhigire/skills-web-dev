# MVT (Mapbox Vector Tiles) From PostGIS

Serve map tiles directly from SQL. Clients (Leaflet with `vectorgrid`, MapLibre GL, Mapbox GL) render locally, so styling changes do not require backend redeploys.

## How tiles work

- A tile is a 256x256 or 512x512 viewport identified by `(z, x, y)`.
- Zoom `z` doubles resolution each step. `z=0` covers the world; `z=22` is ~cm-level.
- Vector tiles carry geometry and properties; client styles them.
- Format: protocol buffers. MIME `application/vnd.mapbox-vector-tile`.

## Minimal tile function

```sql
CREATE OR REPLACE FUNCTION public.tile_listings(
  z int, x int, y int, tenant int
) RETURNS bytea
LANGUAGE sql STABLE PARALLEL SAFE AS $$
  WITH mvtgeom AS (
    SELECT
      ST_AsMVTGeom(
        ST_Transform(geom, 3857),
        ST_TileEnvelope(z, x, y),
        extent      => 4096,
        buffer      => 64,
        clip_geom   => true
      ) AS geom,
      id,
      name,
      price_ugx
    FROM listings
    WHERE tenant_id = tenant
      AND geom && ST_Transform(ST_TileEnvelope(z, x, y), 4326)
  )
  SELECT ST_AsMVT(mvtgeom.*, 'listings', 4096, 'geom')
  FROM mvtgeom
  WHERE geom IS NOT NULL;
$$;
```

Key parts:

- `ST_TileEnvelope(z, x, y)` returns the tile bounds in 3857.
- `ST_AsMVTGeom` transforms and clips geometry to tile coords (0-4096).
- `extent => 4096` is the MVT default; keep it.
- `buffer => 64` prevents line/label clipping at tile edges.
- `clip_geom => true` trims geometry to the tile; set `false` if you want whole features.
- The `&&` bbox filter uses GIST on the 4326 column.

## Zoom-aware simplification

Serving full-resolution geometry at `z=5` wastes bytes and melts the client. Simplify per zoom:

```sql
CREATE OR REPLACE FUNCTION public.tile_zones(
  z int, x int, y int, tenant int
) RETURNS bytea
LANGUAGE sql STABLE PARALLEL SAFE AS $$
  WITH params AS (
    SELECT CASE
      WHEN z < 6  THEN 0.01
      WHEN z < 10 THEN 0.001
      WHEN z < 14 THEN 0.0001
      ELSE 0
    END AS tol
  ),
  mvtgeom AS (
    SELECT
      ST_AsMVTGeom(
        ST_Transform(
          CASE WHEN p.tol > 0
               THEN ST_SimplifyPreserveTopology(z_.geom, p.tol)
               ELSE z_.geom
          END,
          3857
        ),
        ST_TileEnvelope(z, x, y),
        4096, 64, true
      ) AS geom,
      z_.id, z_.slug
    FROM zones z_, params p
    WHERE z_.tenant_id = tenant
      AND z_.geom && ST_Transform(ST_TileEnvelope(z, x, y), 4326)
  )
  SELECT ST_AsMVT(mvtgeom.*, 'zones', 4096, 'geom') FROM mvtgeom WHERE geom IS NOT NULL;
$$;
```

Pre-compute simplified geometries in materialised views for heavy layers.

## Tile cache table

For tiles that change rarely and cost to render, cache in Postgres:

```sql
CREATE TABLE tile_cache (
  layer      text NOT NULL,
  tenant_id  int  NOT NULL,
  z          int  NOT NULL,
  x          int  NOT NULL,
  y          int  NOT NULL,
  version    int  NOT NULL,
  mvt        bytea NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (layer, tenant_id, z, x, y, version)
);

-- Read-through pattern (pseudocode)
-- 1. SELECT mvt FROM tile_cache WHERE layer=... AND z=... LIMIT 1;
-- 2. If miss, call tile_listings(z,x,y,tenant) and INSERT.
-- 3. Bump version column in metadata to invalidate.
```

For high volume, push this cache out of the DB into Redis or CDN.

## Serving the tile

### Option 1: `pg_tileserv`

<https://github.com/CrunchyData/pg_tileserv>. Auto-exposes any function returning `bytea` named as a tile function. Minimal config:

```toml
# pg_tileserv.toml
DbConnection = "postgres://tiles:pass@db:5432/app"
HttpHost = "0.0.0.0"
HttpPort = 7800
CacheTTL = 60
```

URL pattern: `http://host:7800/public.tile_listings/{z}/{x}/{y}.pbf?tenant=42`.

### Option 2: Node proxy

```javascript
// tiles.js
import fastify from 'fastify';
import pg from 'pg';

const app = fastify();
const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });

app.get('/tiles/listings/:z/:x/:y.pbf', async (req, reply) => {
  const { z, x, y } = req.params;
  const tenant = Number(req.query.tenant);
  const { rows } = await pool.query(
    'SELECT tile_listings($1,$2,$3,$4) AS mvt',
    [z, x, y, tenant]
  );
  reply
    .header('Content-Type', 'application/vnd.mapbox-vector-tile')
    .header('Cache-Control', 'public, max-age=3600, s-maxage=86400')
    .send(rows[0].mvt);
});

app.listen({ port: 7800, host: '0.0.0.0' });
```

### Option 3: Python (FastAPI)

```python
from fastapi import FastAPI, Response
import asyncpg

app = FastAPI()
pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

@app.get("/tiles/listings/{z}/{x}/{y}.pbf")
async def tile(z: int, x: int, y: int, tenant: int):
    async with pool.acquire() as c:
        mvt = await c.fetchval(
            "SELECT tile_listings($1,$2,$3,$4)", z, x, y, tenant
        )
    return Response(
        content=mvt,
        media_type="application/vnd.mapbox-vector-tile",
        headers={"Cache-Control": "public, max-age=3600, s-maxage=86400"},
    )
```

## CDN caching

MVT tiles are immutable given a stable dataset. Put CloudFront, Fastly, Cloudflare, or nginx in front:

```nginx
location ~ ^/tiles/ {
    proxy_pass http://tile_backend;
    proxy_cache tiles;
    proxy_cache_valid 200 24h;
    proxy_cache_key "$scheme$host$request_uri";
    add_header Cache-Control "public, max-age=3600, s-maxage=86400";
}
```

Invalidate by bumping a `?v=N` parameter in the client, or purging a path prefix.

## Client integration

- Leaflet: `Leaflet.VectorGrid` to render MVT.
- MapLibre GL / Mapbox GL: set `type: vector`, `tiles: ["/tiles/listings/{z}/{x}/{y}.pbf"]` in the style source.
- Always pass authentication (cookie, bearer) through the tile proxy and enforce tenant in SQL.

## Security

- Never trust the `tenant` query parameter. Derive from the session or JWT on the server.
- Rate-limit tile endpoints; clients can request thousands per pan/zoom.
- Do not expose arbitrary SQL through query parameters.

## Anti-patterns

- Returning tiles in 4326 pixel space. MVT is 3857; transform before `ST_AsMVTGeom`.
- `clip_geom => false` at high zoom; geometries explode tile size.
- No simplification at low zoom; 50 MB tiles kill clients.
- Tile cache keyed only on `(z,x,y)` without `tenant` or version. Cross-tenant leaks.
- Serving unauthenticated tiles from a multi-tenant DB.

## Cross-reference

- `references/performance-patterns.md` — simplification per zoom, CLUSTER, materialised views.
- `references/tenant-isolation-rls.md` — enforcing tenant at the DB layer.
- `gis-mapping` — Leaflet client consuming these tiles.
