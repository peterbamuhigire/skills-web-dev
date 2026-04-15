# Tenant Isolation With Row-Level Security

RLS makes cross-tenant leaks structurally impossible, even when a query forgets the `WHERE tenant_id = ...` clause. It is a defence-in-depth layer, not a replacement for application checks.

## Mental model

```text
App auth  ->  set session variable  ->  RLS policy filters every row  ->  query returns only current tenant
```

If the policy is correct, a bug elsewhere in the app cannot leak another tenant's rows.

## Enable RLS on a table

```sql
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings FORCE  ROW LEVEL SECURITY;   -- applies even to table owner
```

`FORCE` matters: by default the table owner bypasses RLS. Force it so that only explicit bypass roles see everything.

## Policy shape

```sql
CREATE POLICY tenant_isolation ON listings
  USING (tenant_id = current_setting('app.tenant_id', true)::int)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::int);
```

Two clauses:

- `USING` filters reads and the existing row in an UPDATE/DELETE.
- `WITH CHECK` filters new rows from INSERT and UPDATE.

Both should use the same expression. Missing `WITH CHECK` lets a tenant write rows for another tenant.

The `true` second argument to `current_setting` returns NULL instead of erroring when the setting is missing. Default-deny when NULL:

```sql
CREATE POLICY tenant_isolation ON listings
  USING (
    tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::int
  )
  WITH CHECK (
    tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::int
  );
```

## Session-setting pattern

The app sets the tenant on every connection check-out:

```sql
SET LOCAL app.tenant_id = '42';     -- per transaction
-- or
SELECT set_config('app.tenant_id', '42', true);   -- true = transaction-local
```

In PgBouncer transaction mode, prefer `SET LOCAL` or `set_config(..., true)` so the setting clears at commit and cannot leak to the next checkout.

Node (`node-postgres`) example:

```javascript
async function withTenant(tenantId, work) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query('SELECT set_config($1, $2, true)',
                       ['app.tenant_id', String(tenantId)]);
    const result = await work(client);
    await client.query('COMMIT');
    return result;
  } catch (e) {
    await client.query('ROLLBACK');
    throw e;
  } finally {
    client.release();
  }
}
```

PHP PDO:

```php
function withTenant(PDO $pdo, int $tenantId, callable $work) {
    $pdo->beginTransaction();
    try {
        $stmt = $pdo->prepare("SELECT set_config('app.tenant_id', :t, true)");
        $stmt->execute([':t' => (string)$tenantId]);
        $result = $work($pdo);
        $pdo->commit();
        return $result;
    } catch (\Throwable $e) {
        $pdo->rollBack();
        throw $e;
    }
}
```

## Bypass role for superadmin and migrations

Some operations legitimately cross tenants: platform admins, billing jobs, migrations, sync workers.

```sql
CREATE ROLE platform_admin NOLOGIN BYPASSRLS;
GRANT platform_admin TO admin_user;
```

- `BYPASSRLS` on the role lets it see every row.
- Keep this role narrow; give it to a dedicated user the app does not normally connect as.
- Audit every query run under this role.

The application user should not have `BYPASSRLS`:

```sql
CREATE ROLE app_user LOGIN PASSWORD '...';
-- Do not grant BYPASSRLS here.
```

## Combining RLS with app-layer checks

RLS is belt. App-layer checks are braces. Keep both:

1. App derives `tenantId` from the authenticated session.
2. App sets `app.tenant_id` on the DB connection.
3. App queries still include `WHERE tenant_id = :tenant_id` for clarity, indexes, and query plans.
4. RLS catches anything the app forgets.

Do not remove the `WHERE` in application SQL just because RLS exists. Query plans and teammates reading the code both benefit from the explicit filter.

## RLS on spatial queries

RLS applies transparently to spatial predicates:

```sql
-- With app.tenant_id = '42', this returns only tenant 42's listings.
SELECT id FROM listings
WHERE ST_DWithin(geom::geography, ST_MakePoint(:lng,:lat)::geography, 5000);
```

Performance notes:

- Keep `tenant_id` indexed alongside the spatial index. Planner uses both.
- For heavy skew (one tenant with 90% of rows), consider partial indexes per tenant or list-partitioning by `tenant_id`.

## Tile functions and RLS

Tile-serving SQL functions run as `SECURITY INVOKER` by default. The caller's `app.tenant_id` applies:

```sql
CREATE OR REPLACE FUNCTION public.tile_listings(z int, x int, y int)
RETURNS bytea LANGUAGE sql STABLE PARALLEL SAFE
SECURITY INVOKER AS $$
  WITH mvtgeom AS (
    SELECT ST_AsMVTGeom(ST_Transform(geom,3857), ST_TileEnvelope(z,x,y), 4096,64,true) AS geom,
           id, name
    FROM listings
    WHERE geom && ST_Transform(ST_TileEnvelope(z,x,y), 4326)
  )
  SELECT ST_AsMVT(mvtgeom.*, 'listings', 4096, 'geom') FROM mvtgeom;
$$;
```

Drop the `tenant` parameter; RLS handles it. The tile proxy sets `app.tenant_id` from the authenticated request, never from a URL parameter.

Avoid `SECURITY DEFINER` on tile functions unless you fully understand the implications; it bypasses the caller's policies.

## Testing RLS

Write explicit tests that prove tenants cannot see each other's rows.

```sql
-- As app_user:
SET LOCAL app.tenant_id = '1';
INSERT INTO listings(tenant_id, title, geom) VALUES
  (1, 'T1-A', ST_SetSRID(ST_MakePoint(32.58, 0.34), 4326));

SET LOCAL app.tenant_id = '2';
INSERT INTO listings(tenant_id, title, geom) VALUES
  (2, 'T2-A', ST_SetSRID(ST_MakePoint(32.58, 0.34), 4326));

-- Tenant 1 sees only T1-A.
SET LOCAL app.tenant_id = '1';
SELECT title FROM listings;  -- expect: T1-A

-- Tenant 2 sees only T2-A.
SET LOCAL app.tenant_id = '2';
SELECT title FROM listings;  -- expect: T2-A

-- Tenant 1 cannot write as tenant 2.
SET LOCAL app.tenant_id = '1';
INSERT INTO listings(tenant_id, title, geom) VALUES
  (2, 'hack', ST_SetSRID(ST_MakePoint(0,0),4326));
-- expect: ERROR: new row for relation "listings" violates row-level security policy
```

Automate these in the test suite. Every new tenant-scoped table should come with an RLS test.

## Diagnostics

List policies:

```sql
SELECT schemaname, tablename, policyname, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public';
```

Check a role's RLS status:

```sql
SELECT rolname, rolbypassrls
FROM pg_roles
WHERE rolname IN ('app_user','platform_admin');
```

See the current tenant on a connection:

```sql
SELECT current_setting('app.tenant_id', true) AS tenant;
```

## Performance considerations

- RLS expressions are inlined into the query plan; cost is similar to adding the predicate manually.
- Plan cache: different `app.tenant_id` values usually share the same plan. Confirm with `EXPLAIN`.
- Very complex policies (subqueries, joins) can suppress optimisations. Keep policies to simple equality on an indexed column.

## Anti-patterns

- Relying on app-layer WHERE only. One missed filter and tenants see each other.
- Using `SET app.tenant_id` (no `LOCAL`) in PgBouncer transaction mode. Value leaks to the next checkout.
- Running migrations as `app_user`. DDL on RLS-enabled tables without `BYPASSRLS` fails confusingly.
- Enabling RLS without `FORCE`. Table owner silently bypasses.
- Adding `BYPASSRLS` to any web-facing application role.
- Trusting a URL or query parameter for `tenant_id` in tile services. Always derive from the authenticated session.
- Writing a policy with `USING` but no `WITH CHECK`. Cross-tenant writes become possible.

## Cross-reference

- `multi-tenant-saas-architecture` — overall tenancy strategy.
- `postgresql-fundamentals` — roles, grants, `SET LOCAL` semantics.
- `references/mvt-tiles.md` — tile functions relying on RLS instead of a tenant parameter.
- `references/hybrid-mysql-postgis.md` — ensuring sync workers use `BYPASSRLS`.
