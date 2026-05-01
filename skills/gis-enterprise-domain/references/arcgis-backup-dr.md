# ArcGIS Enterprise Backup and Disaster Recovery

`webgisdr` utility, Data Store backups, config-store backups, restore drills, and RPO/RTO planning for a production ArcGIS deployment.

## What must be backed up

```text
Component          Backup tool                                    Cadence
-----------------  ---------------------------------------------  -----------------
Portal content     webgisdr (export/import mode)                  Daily
Server config      config-store + server-directories on shared FS Daily
Relational DS      Data Store backup tool OR webgisdr              Hourly WAL + daily full
Tile cache DS      File-level copy / object storage snapshot       Weekly
Spatiotemporal DS  Data Store backup tool                          Per retention policy
Hosted item data   Covered by Data Store backup                    Same as relational
Registered DB      Your own DBA backup (SQL Svr, Oracle, PG)       Per your DBA standard
Web Adaptor        None — reinstall from config as code            On change
IdP / SAML config  Export metadata and store in secrets repo       On change
```

## `webgisdr` — the coordinated backup tool

`webgisdr.bat` / `webgisdr.sh` ships with Portal. It performs a coordinated export of Portal content and federated Server configuration, and can optionally back up the relational Data Store.

### Backup modes

```text
BACKUP_RESTORE_MODE = full      # complete export each run, self-contained
BACKUP_RESTORE_MODE = incremental  # delta since last full
BACKUP_RESTORE_MODE = backup    # Data Store on-disk backup only
```

Rule of thumb: **full weekly + incremental daily** is a reasonable default. Pure "full daily" works for small portals and is simpler to reason about.

### Example `webgisdr.properties`

```properties
# Core connection
PORTAL_ADMIN_USERNAME=portaladmin
PORTAL_ADMIN_PASSWORD=***
PORTAL_ADMIN_URL=https://gis.example.org/portal

# Backup location
BACKUP_STORE_PROVIDER=FileSystem
SHARED_LOCATION=\\backup-nas\arcgis-backup\webgisdr

# Mode
BACKUP_RESTORE_MODE=full
INCLUDE_SCENE_TILE_CACHES=false

# Notifications
NOTIFICATION_EMAIL=gisops@example.org
NOTIFICATION_SMTP_SERVER=smtp.example.org

# Retention handled externally (rsync+find, or cloud lifecycle policy)
```

### Running on a schedule

```bash
#!/usr/bin/env bash
# /opt/arcgis/cron/webgisdr-nightly.sh
set -euo pipefail

LOG=/var/log/arcgis/webgisdr-$(date +%Y%m%d).log
cd /home/arcgis/portal/tools/webgisdr

./webgisdr.sh --export --file /opt/arcgis/config/webgisdr.properties \
  >> "$LOG" 2>&1

# Prune old backups beyond retention
find /mnt/backup/webgisdr -type f -mtime +30 -delete
```

Cron:

```cron
0 2 * * * /opt/arcgis/cron/webgisdr-nightly.sh
```

### Restore

```bash
./webgisdr.sh --import \
  --file /opt/arcgis/config/webgisdr.properties \
  --BACKUP_LOCATION /mnt/backup/webgisdr/2026-04-10-full
```

Never run an import against a healthy production portal. Always restore into a clean or dev environment first, verify, then cut over.

## Relational Data Store backups

Two complementary paths:

1. **Data Store backup tool** (`backupdatastore.bat` / `.sh`) — ships with the Data Store install. Produces a consistent backup to a shared location.
2. **Continuous WAL archiving** — for RPO under 1 hour, configure write-ahead log archiving to the shared backup location and keep a rolling chain for point-in-time recovery.

```bash
# Configure backup location (one-off)
./configurebackuplocation.sh --operation register \
  --store relational \
  --location "type=fs;location=/mnt/backup/datastore-relational;name=primary"

# Manual backup
./backupdatastore.sh
```

## Config-store backup

The ArcGIS Server config-store and server directories should already be on highly available shared storage. Snapshot that share on a schedule (daily is typical) with a retention matching your DR window.

If the shared storage is cloud object storage, enable versioning + lifecycle policies.

## Tile cache data store

Tile caches are rebuild-able from source. You have two honest options:

- Back them up as files (weekly) to restore fast.
- Treat them as ephemeral and plan a rebuild in DR — only acceptable if rebuild time is under RTO.

## Third-party registered data

Enterprise geodatabases (SQL Server, Oracle, PostgreSQL with ArcSDE) are backed up by your DBA team with normal database tooling. Make sure the schedules align:

- Portal backup and EGDB backup should cover the same moment in time within minutes.
- Document the ordering for coordinated restore.

## Restore drill (quarterly)

Run this end-to-end drill at least once per quarter:

```text
1. Stand up a dev or DR environment with blank ArcGIS Enterprise install at same version.
2. Restore Portal + Server + Data Store via webgisdr --import.
3. Restore any registered EGDB.
4. Validate:
     - Log in as test user.
     - Open 5 representative web maps.
     - Query a known feature via the REST endpoint.
     - Edit a test feature layer and see the edit persist.
     - Run a geoprocessing service end-to-end.
5. Record time-to-ready; compare to RTO.
6. Record data loss window; compare to RPO.
7. Capture any drift or missing steps in the runbook.
```

Without the drill, you have backups, not recovery.

## RPO and RTO planning

Typical starting tiers for a mid-size deployment:

```text
Tier                       RPO          RTO          Backup design
-------------------------  -----------  -----------  ----------------------------------
Gold (critical)            <= 15 min    <= 4 hours   Full nightly + WAL + warm standby
Silver (important)         <= 1 hour    <= 24 hours  Full nightly + hourly WAL
Bronze (internal)          <= 24 hours  <= 72 hours  Full nightly, cold restore
```

Choose the tier by product impact, not by "everything should be gold". Warm standbys cost real money.

## DR architecture patterns

- **Same region, multi-AZ** — covers AZ failure; cheapest HA improvement.
- **Cross-region standby with replicated Data Store** — covers region failure; use Esri-supported streaming replication.
- **Cold-restore from object storage** — cheapest option; matches Bronze tier only.
- **Blue/green site swap** — run two full environments, swap via DNS; highest cost, lowest RTO.

## Security of backups

- Encrypt backup artifacts at rest (cloud KMS or file-system level).
- Restrict access to the backup share with the principle of least privilege.
- Treat `webgisdr.properties` as a secret — it contains admin credentials.
- Rotate the admin password used for backups periodically and update the file from your secrets manager.
- Keep off-site copies immune to ransomware (WORM buckets or object lock).

## Anti-patterns

- "We have daily backups" with no documented restore procedure.
- Running `webgisdr` but skipping the relational Data Store export.
- Running restores into production to "test them".
- Keeping backups on the same host as the primary.
- Retaining backups forever — shrink retention to what the business really needs.
- No alerting on backup failure. Silent failure is the worst failure.

## Related references

- `arcgis-components.md` — what each backup covers in the topology.
- `arcgis-security-roles.md` — admin credentials used by webgisdr must be managed as secrets.
