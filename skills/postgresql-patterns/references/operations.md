# PostgreSQL Operations

Backup, replication, and query diagnosis for self-managed Debian/Ubuntu PostgreSQL.

## Logical backup with pg_dump

Single database, portable across PostgreSQL versions.

```sh
# Custom-format dump (compressed, parallel-restorable)
pg_dump -Fc -d mydb -f mydb.dump

# Restore to a fresh database
createdb mydb_new
pg_restore -d mydb_new --jobs=4 mydb.dump
```

`-Fc` (custom format) is preferred over plain SQL because it supports parallel restore (`--jobs`) and selective restore (`--table`, `--schema`).

For a whole cluster (all databases, roles, tablespaces), use `pg_dumpall --globals-only` for roles plus per-database `pg_dump`.

## Physical backup with pg_basebackup

Full cluster, foundation for streaming replication and point-in-time recovery.

```sh
sudo -u postgres pg_basebackup \
  -D /var/lib/postgresql/backup \
  -Ft -z -P -X stream
```

Options: `-Ft` tar format, `-z` gzip, `-P` progress, `-X stream` include WAL needed to make the backup self-consistent.

## WAL archiving and PITR

In `postgresql.conf`:

```conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/wal_archive/%f && cp %p /var/lib/postgresql/wal_archive/%f'
```

Point-in-time recovery requires a base backup plus the WAL archive. Restore by extracting the base backup, creating `recovery.signal`, and setting `restore_command` and `recovery_target_time` in `postgresql.conf`. Source: postgresql.org/docs/current/continuous-archiving.html.

For production, replace the toy `cp` archive_command with a tool that handles compression, retention, and verification (`pgbackrest`, `wal-g`, or `barman`).

## Replication

Streaming replication. Hot standby receives WAL from the primary in near-real-time.

```conf
# primary postgresql.conf
wal_level = replica
max_wal_senders = 10
hot_standby = on
```

```sh
# on the standby host
sudo -u postgres pg_basebackup \
  -h primary.example.com -U replicator \
  -D /var/lib/postgresql/16/main \
  -P -R -X stream
```

`-R` writes `standby.signal` and the `primary_conninfo` connection string into `postgresql.auto.conf`.

Logical replication. Row-level changes via publications and subscriptions; works across major versions.

```sql
-- on publisher
CREATE PUBLICATION items_pub FOR TABLE items;

-- on subscriber
CREATE SUBSCRIPTION items_sub
  CONNECTION 'host=publisher.example.com dbname=app user=repl'
  PUBLICATION items_pub;
```

## EXPLAIN ANALYZE

The single most valuable operational habit.

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM items
WHERE tenant_id = 42
ORDER BY embedding <=> $1 LIMIT 10;
```

Read the plan top-down. Look for:

- Index scan vs sequential scan. A sequential scan on a large table almost always means a missing index or an operator-class mismatch on a vector index.
- Actual rows vs estimated rows. Off by more than 10x means statistics are out of date. Run `ANALYZE` on the table.
- `Buffers: shared hit=... read=...`. High `read` on hot data means the working set does not fit in `shared_buffers`.
- For vector queries, confirm the planner picked the HNSW or IVFFlat index. If not, check the operator class (`vector_l2_ops` with `<->`, `vector_cosine_ops` with `<=>`, `vector_ip_ops` with `<#>`).

## Useful catalogue queries

```sql
-- Largest tables
SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
FROM pg_class WHERE relkind='r' ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;

-- Slow query candidates (requires pg_stat_statements)
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 20;

-- Active sessions and waits
SELECT pid, usename, state, wait_event_type, wait_event, query
FROM pg_stat_activity WHERE state <> 'idle';
```

Enable `pg_stat_statements` by adding it to `shared_preload_libraries` and running `CREATE EXTENSION pg_stat_statements;`. It is the cheapest serious observability you can add to a PostgreSQL instance.
