# Backup And Migration

Spatial databases back up like any Postgres database, with two extras: the `spatial_ref_sys` table must survive, and you will regularly convert to and from GIS file formats.

## Logical backup: pg_dump

Custom format, compressed, parallel-friendly:

```bash
pg_dump \
  --host=db.internal \
  --username=postgres \
  --dbname=app \
  --format=custom \
  --compress=9 \
  --no-privileges \
  --no-owner \
  --file=app-$(date +%F).dump
```

Flags:

- `--format=custom` (`-Fc`): binary, supports parallel restore.
- `--compress=9`: zstd/gzip; shrinks 4-10x on typical data.
- `--no-privileges --no-owner`: portable across environments.
- Add `--jobs=4` with `--format=directory` for parallel dump.

Exclude non-critical tables (audit logs, tile cache):

```bash
pg_dump -Fc --exclude-table=public.tile_cache --exclude-table-data=public.audit_log ...
```

## Parallel restore

```bash
pg_restore \
  --host=db-new.internal \
  --username=postgres \
  --dbname=app \
  --jobs=4 \
  --no-owner \
  --no-privileges \
  app-2026-04-15.dump
```

Restore order matters for cross-schema FKs. `pg_restore` handles it for dumps; do not split restores across manual phases unless you understand dependencies.

## Roles and extensions

Recreate roles and install extensions on the target before restore:

```sql
CREATE ROLE app_rw WITH LOGIN PASSWORD '...';
CREATE ROLE app_ro WITH LOGIN PASSWORD '...';

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;   -- only if used
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
```

Version-check the spatial extensions match the source:

```sql
SELECT postgis_full_version();
```

Mismatched PostGIS versions can subtly change function output (e.g., `ST_Buffer` quadrant handling). Keep versions aligned.

## `spatial_ref_sys` and `spatial_ref_sys` safety

- `spatial_ref_sys` is populated by the PostGIS extension install.
- `pg_dump` skips it by default when PostGIS is installed as an extension. Do not force-include.
- If you added custom SRIDs, dump them explicitly:

```bash
pg_dump -Fc -t 'public.spatial_ref_sys' \
  --data-only --where="auth_name = 'local'" \
  -f custom-srids.dump
```

## WAL archiving and point-in-time recovery

For production, logical backups are not enough. Configure continuous WAL archiving:

```ini
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'pgbackrest --stanza=app archive-push %p'
max_wal_senders = 5
```

Use `pgBackRest` or `wal-g` for managed WAL streaming to S3/MinIO. Both handle:

- Base backups (often parallel, compressed).
- Continuous WAL push.
- Point-in-time recovery to any timestamp within retention.

Example `pgbackrest` restore to a past time:

```bash
pgbackrest --stanza=app --type=time "--target=2026-04-14 23:10:00+03" restore
```

Operational checklist:

- Test restores monthly on a scratch host. Backups you never restore are not backups.
- Retain at least two full backups plus WAL to span retention.
- Encrypt at rest (S3 SSE or repository-level).
- Document the RPO (WAL lag) and RTO (restore time) targets.

## Physical backup

`pg_basebackup` for whole-cluster base backup:

```bash
pg_basebackup -D /backup/base -F tar -z -X stream -c fast
```

Useful as a base for replicas and PITR. Not a substitute for `pg_dump` when you need logical portability.

## ogr2ogr: the GIS format swiss knife

`ogr2ogr` (from GDAL) converts between PostGIS and every common GIS format.

Shapefile → PostGIS:

```bash
ogr2ogr -f PostgreSQL \
  "PG:host=db user=postgres dbname=app" \
  zones.shp \
  -nln zones_import \
  -nlt PROMOTE_TO_MULTI \
  -lco GEOMETRY_NAME=geom \
  -lco FID=id \
  -t_srs EPSG:4326 \
  -overwrite
```

Flags:

- `-nln`: target table name.
- `-nlt PROMOTE_TO_MULTI`: forces MultiPolygon; avoids mixed geometry errors.
- `-lco GEOMETRY_NAME=geom`: standardise the column name.
- `-t_srs EPSG:4326`: target SRID.
- `-overwrite`: drop+recreate target.

GeoJSON → PostGIS:

```bash
ogr2ogr -f PostgreSQL \
  "PG:host=db user=postgres dbname=app" \
  listings.geojson \
  -nln listings_import \
  -lco GEOMETRY_NAME=geom \
  -t_srs EPSG:4326
```

KML → PostGIS:

```bash
ogr2ogr -f PostgreSQL \
  "PG:host=db user=postgres dbname=app" \
  boundaries.kml \
  -nln boundaries_import \
  -lco GEOMETRY_NAME=geom \
  -t_srs EPSG:4326
```

PostGIS → GeoJSON (for client delivery or backups of a single layer):

```bash
ogr2ogr -f GeoJSON listings.geojson \
  "PG:host=db user=postgres dbname=app" \
  -sql "SELECT id, title, geom FROM listings WHERE tenant_id = 42"
```

PostGIS → Shapefile (legacy interchange, .shp + .dbf + .shx + .prj):

```bash
ogr2ogr -f "ESRI Shapefile" zones_export.shp \
  "PG:host=db user=postgres dbname=app" \
  -sql "SELECT id, slug, geom FROM zones" \
  -lco ENCODING=UTF-8
```

## shp2pgsql (lighter alternative)

For pure Shapefile ingests without GDAL:

```bash
shp2pgsql -s 4326 -I -W UTF-8 zones.shp public.zones_import \
  | psql -h db -U postgres app
```

- `-s 4326`: assign SRID on load.
- `-I`: create GIST index.
- `-W UTF-8`: dbf encoding.

## Post-restore checklist

After any restore or major load:

```sql
ANALYZE;
REINDEX DATABASE CONCURRENTLY app;   -- only if drift is suspected
SELECT postgis_full_version();
SELECT COUNT(*) FROM spatial_ref_sys;
```

Smoke-test a couple of known queries before flipping traffic.

## Migration between PostGIS major versions

1. Install the new server with matching PostGIS major.
2. `pg_dump -Fc` from the old cluster.
3. `CREATE EXTENSION postgis` on the new cluster.
4. `pg_restore -j 4` into the new cluster.
5. `SELECT postgis_extensions_upgrade();` if the minor version differs.
6. Regression-test spatial queries (`EXPLAIN ANALYZE` + result diffs).

## Anti-patterns

- Dumping in plain SQL format for large databases. Slow to restore; no parallelism.
- Forgetting to install PostGIS on the target before restore. Half the restore fails silently.
- Restoring a dump that references a custom SRID you never defined on the target.
- Skipping `ANALYZE` after restore; plans are based on empty statistics.
- Treating `pg_dump` as a high-availability strategy. It is not. Use replication + WAL archiving.

## Cross-reference

- `postgresql-administration` — cluster operations and HA.
- `references/hybrid-mysql-postgis.md` — seeding PostGIS from MySQL.
- `references/tenant-isolation-rls.md` — restore implications for RLS policies.
