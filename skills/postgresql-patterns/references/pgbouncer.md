# PgBouncer

PostgreSQL's `max_connections` is bounded (typically 100-200) and each connection consumes memory. PgBouncer keeps a small pool of real PostgreSQL connections and multiplexes many client connections over them. Source: pgbouncer.org/features.html.

## Pooling modes

- Session pooling. Server connection assigned for the entire client session. Supports all PostgreSQL features. Use for clients that depend on session state, prepared statements, or `LISTEN/NOTIFY`.
- Transaction pooling. Server connection assigned only during a transaction. Breaks a few session-based features. Highest throughput for short web/SaaS queries.
- Statement pooling. Multi-statement transactions disallowed. Maximum reuse, narrow applicability.

| Workload | Mode | Why |
|---|---|---|
| Most web/SaaS workloads | Transaction | Highest throughput; compatible with most ORMs |
| Long-lived connections needing prepared statements | Session | Prepared statements survive |
| PL/Proxy / single-statement APIs | Statement | Maximum reuse |

## Prepared-statement pitfall

In transaction pooling, a prepared statement created on one server connection is not visible on the next transaction (which may land on a different server connection). Symptoms: `prepared statement "S_1" does not exist`.

Fix paths:

1. Upgrade to PgBouncer 1.21+ and set `server_prepared_statements = on`. PgBouncer then tracks prepared statements per server connection.
2. Configure the client to use simple-protocol (no automatic prepares). For example, in Node.js `pg`, disable `pg-prepared`; in Python `psycopg`, use `prepare_threshold=None`.
3. Run the offending app against a separate session-mode pool on its own port.

## Sample config (`/etc/pgbouncer/pgbouncer.ini`)

```ini
[databases]
app = host=127.0.0.1 port=5432 dbname=app

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 5
reserve_pool_timeout = 3
server_prepared_statements = on
```

## Sizing

Rule of thumb: `default_pool_size` is approximately 2x the PostgreSQL host's CPU cores. `max_client_conn` may be 10-20x `default_pool_size`. Tune from observed `pg_stat_activity` waiting counts and PgBouncer's own `SHOW POOLS;` output.

PostgreSQL `max_connections` must be at least `default_pool_size * number_of_databases + admin_overhead`. Forgetting this caps you below the pool capacity and produces "remaining connection slots are reserved" errors under load.

## Observability

```sql
-- From inside pgbouncer's admin DB (psql -p 6432 pgbouncer)
SHOW POOLS;
SHOW CLIENTS;
SHOW SERVERS;
SHOW STATS;
```

Watch `cl_waiting` (clients queued for a server) and `sv_used` vs `sv_idle`. Persistent `cl_waiting > 0` means the pool is undersized or queries are too slow.
