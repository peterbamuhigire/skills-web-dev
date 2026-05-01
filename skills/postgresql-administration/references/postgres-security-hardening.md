# PostgreSQL 16 Security Hardening (Debian/Ubuntu)

Hardening playbook for PostgreSQL 16 on Debian/Ubuntu SaaS hosts, from package install through RLS, audit, and backup. Focused on controls that actually fit a self-managed stack.

## 1. Network Exposure

Never let PostgreSQL listen on a public interface. Keep it on localhost or a private subnet and rely on the firewall as an additional gate.

Edit `/etc/postgresql/16/main/postgresql.conf`:

```conf
listen_addresses = 'localhost'
# Multi-host deployments — use the private interface only:
# listen_addresses = '10.0.1.15'

port = 5432
```

Restart and verify:

```bash
sudo systemctl restart postgresql@16-main
sudo ss -tlnp | grep 5432
```

Firewall as well:

```bash
sudo ufw deny 5432/tcp
sudo ufw allow from 10.0.1.0/24 to any port 5432 proto tcp
```

## 2. TLS Everywhere

Enable TLS and reject anything below TLS 1.3 where clients allow it:

```conf
ssl = on
ssl_cert_file = '/etc/postgresql/ssl/server.crt'
ssl_key_file  = '/etc/postgresql/ssl/server.key'
ssl_ca_file   = '/etc/postgresql/ssl/ca.crt'
ssl_min_protocol_version = 'TLSv1.3'
ssl_prefer_server_ciphers = on
```

Key file must be owned by `postgres` and mode 600:

```bash
sudo chown postgres:postgres /etc/postgresql/ssl/server.key
sudo chmod 600 /etc/postgresql/ssl/server.key
```

Verify from a client:

```bash
psql "host=db.internal user=app dbname=app sslmode=verify-full sslrootcert=/etc/ssl/certs/ca.pem"
```

Check the session:

```sql
SELECT ssl, version, cipher
FROM pg_stat_ssl
WHERE pid = pg_backend_pid();
```

## 3. pg_hba.conf Access Control

`pg_hba.conf` is the first gate a client hits. The rule syntax is:

```
# TYPE      DATABASE     USER          ADDRESS          METHOD
```

Rules are evaluated top-to-bottom and the first match wins. A client that matches no rule is denied, so the structure should be a series of explicit allows followed by an implicit deny.

A production template for a multi-tenant SaaS:

```
# Local admin via unix socket only
local   all             postgres                                peer

# Per-app role, TLS-only, from private subnet, scram-sha-256
hostssl billing_db      billing_app     10.0.1.0/24             scram-sha-256
hostssl reporting_db    reporting_ro    10.0.1.0/24             scram-sha-256

# Read replica streams
hostssl replication     repl            10.0.1.0/24             scram-sha-256

# Deny everything else explicitly for audit clarity
host    all             all             0.0.0.0/0               reject
host    all             all             ::/0                    reject
```

Key rules:

- Always use `hostssl` (not `host`) for network connections.
- Always use `scram-sha-256`, never `md5`, `password`, or `trust`.
- `trust` is acceptable only on local unix sockets for the `postgres` superuser, and only because the OS already authenticates that user.

Reload to apply:

```bash
sudo systemctl reload postgresql@16-main
```

## 4. Role Hardening

The `postgres` superuser is for administration, never for applications. Create a per-app role with a connection cap:

```sql
CREATE ROLE billing_app LOGIN
  PASSWORD '...'
  CONNECTION LIMIT 50
  VALID UNTIL '2027-01-01';

-- Read-only reporting role:
CREATE ROLE billing_ro LOGIN
  PASSWORD '...'
  CONNECTION LIMIT 10;
```

Lock down `PUBLIC`. From Postgres 15 onwards, `PUBLIC` no longer has CREATE on the `public` schema, but you still need to revoke other defaults:

```sql
REVOKE ALL ON DATABASE postgres FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;

GRANT CONNECT ON DATABASE billing_db TO billing_app, billing_ro;
GRANT USAGE ON SCHEMA billing TO billing_app, billing_ro;

GRANT SELECT, INSERT, UPDATE, DELETE
  ON ALL TABLES IN SCHEMA billing
  TO billing_app;

GRANT SELECT
  ON ALL TABLES IN SCHEMA billing
  TO billing_ro;

-- Future tables inherit the same grants:
ALTER DEFAULT PRIVILEGES IN SCHEMA billing
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO billing_app;
```

Audit existing privileges regularly:

```sql
SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolreplication
FROM pg_roles
ORDER BY rolname;

-- Per-object grants:
\dp billing.*
```

## 5. Row-Level Security (RLS)

RLS is the Postgres feature that makes per-tenant isolation structurally safe: the database enforces the rule, not the application. A bug in one query cannot leak data across tenants.

Enable on each tenant-scoped table:

```sql
ALTER TABLE billing.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.invoices FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation
  ON billing.invoices
  USING      (tenant_id = current_setting('app.tenant_id')::int)
  WITH CHECK (tenant_id = current_setting('app.tenant_id')::int);
```

`FORCE ROW LEVEL SECURITY` makes the policy apply even to the table owner, preventing the application role from bypassing it by accident.

The application sets the tenant context per request (or per transaction when pooling):

```sql
SET LOCAL app.tenant_id = 42;
SELECT * FROM billing.invoices;   -- only tenant 42's rows
```

For admin/cross-tenant operations, use a `SECURITY DEFINER` function owned by a dedicated role that is allowed to bypass RLS:

```sql
CREATE OR REPLACE FUNCTION admin.all_invoices_for_audit()
RETURNS SETOF billing.invoices
LANGUAGE sql
SECURITY DEFINER
SET search_path = billing, pg_temp
AS $$ SELECT * FROM billing.invoices $$;
```

PgBouncer and RLS need care. `SET` without `LOCAL` leaks across pooled connections; `SET LOCAL` only holds for the current transaction. In transaction pooling mode, the app must set `app.tenant_id` at the start of every transaction, not at connection time.

## 6. Password Encryption and Rotation

`scram-sha-256` is the only acceptable method. Make it the default so any `CREATE USER ... PASSWORD '...'` stores a scram hash:

```conf
password_encryption = scram-sha-256
```

Rotation policy:

- Application credentials rotate on a 90-day schedule via Vault dynamic secrets (see `cicd-devsecops`).
- DBA credentials are personal and tied to offboarding.
- `VALID UNTIL` on each role forces the rotation to actually happen.

## 7. Connection Pooling Security (PgBouncer)

PgBouncer is the standard pooler. Configure TLS on both sides:

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
billing_db = host=127.0.0.1 port=5432 dbname=billing_db

[pgbouncer]
listen_addr = 10.0.1.20
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

client_tls_sslmode = require
client_tls_cert_file = /etc/pgbouncer/ssl/bouncer.crt
client_tls_key_file  = /etc/pgbouncer/ssl/bouncer.key

server_tls_sslmode = verify-full
server_tls_ca_file = /etc/pgbouncer/ssl/ca.crt

pool_mode = transaction
max_client_conn = 2000
default_pool_size = 50
```

Transaction pool mode affects RLS: tenant context variables must be set with `SET LOCAL` at the start of every transaction, not once at connection time.

## 8. Encryption at Rest

Postgres does not have native tablespace encryption. The standard layered approach is:

1. **LUKS** on the data volume at the OS level. This is the baseline and protects against disk theft.
2. **pgcrypto** for per-column application encryption of the most sensitive fields. The key lives in Vault; the application fetches it and encrypts before `INSERT`:

   ```sql
   CREATE EXTENSION IF NOT EXISTS pgcrypto;

   -- Encrypt at insert:
   INSERT INTO patient (id, full_name_ct)
   VALUES (1, pgp_sym_encrypt('Jane Doe', current_setting('app.dek')));

   -- Decrypt on read:
   SELECT pgp_sym_decrypt(full_name_ct, current_setting('app.dek')) AS full_name
   FROM patient;
   ```

3. **Key management** via Vault or a KMS. The data-encryption key (DEK) is set per-session from a secret fetched by the app.

Never store the key in `postgresql.conf`, in a table, or in application source.

## 9. Audit Logging

Built-in logging gives you a baseline:

```conf
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB

log_connections = on
log_disconnections = on
log_hostname = off
log_line_prefix = '%m [%p] %q%u@%d/%a '
log_statement = 'ddl'        -- or 'mod' for all writes
log_duration = off
log_min_duration_statement = 1000  -- log queries slower than 1s
log_lock_waits = on
log_temp_files = 0
log_error_verbosity = default
```

For structured per-command audit, install `pgAudit`:

```bash
sudo apt install postgresql-16-pgaudit
```

```conf
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'write, ddl, role'
pgaudit.log_catalog = off
pgaudit.log_parameter = off   -- avoid logging bind values with PII
pgaudit.log_relation = on
```

Ship logs with `promtail` or `vector` to Loki/SigNoz. Local logs are lost when the host is lost.

## 10. Secure Backups

`pg_dump` output is plaintext by default. Compress and encrypt before writing to disk:

```bash
#!/bin/bash
set -euo pipefail
TS=$(date +%F-%H%M)
DEST=/var/backups/postgres
mkdir -p "$DEST"

PGPASSFILE=/root/.pgpass \
pg_dump --host=127.0.0.1 --username=backup --dbname=billing_db \
        --format=custom --compress=9 \
  | gpg --batch --yes --encrypt \
        --recipient backup@example.com \
        --output "$DEST/billing_db-$TS.dump.gpg"

find "$DEST" -name '*.dump.gpg' -mtime +14 -delete
```

`~/.pgpass` is owned by root, mode 600.

For physical base backups:

```bash
pg_basebackup --host=127.0.0.1 --username=repl \
              --pgdata=/var/backups/postgres/base-$TS \
              --format=tar --gzip --checkpoint=fast \
              --wal-method=stream
```

Stream WAL archives to an encrypted target (encrypted S3 bucket, LUKS volume on a separate host). A full PITR story needs base backup + WAL archive + tested restore.

Test restores monthly. Backups without a successful restore drill are not backups.

## 11. Replication Security

Create a minimal replication role:

```sql
CREATE ROLE repl WITH REPLICATION LOGIN PASSWORD '...';
```

`pg_hba.conf` entries for replicas, TLS-only:

```
hostssl replication     repl            10.0.1.20/32            scram-sha-256
hostssl replication     repl            10.0.1.21/32            scram-sha-256
```

On the replica, `primary_conninfo` uses `sslmode=verify-full` and a `.pgpass` file:

```conf
primary_conninfo = 'host=db1.internal port=5432 user=repl
                    sslmode=verify-full sslrootcert=/etc/postgresql/ssl/ca.crt
                    application_name=replica1'
```

Logical replication uses the same network controls plus `CREATE PUBLICATION`/`SUBSCRIPTION`. Keep the publication narrowly scoped — publishing `FOR ALL TABLES` leaks anything added later.

## 12. Extensions

`shared_preload_libraries` should only contain extensions you actively use. Many extensions require superuser to install and run with extended privileges, so audit:

```sql
SELECT extname, extversion, extowner::regrole
FROM pg_extension
ORDER BY extname;
```

Common production set:

- `pgaudit` — audit logging
- `pg_stat_statements` — query stats (sanitise before export; can contain literals)
- `pgcrypto` — column encryption
- `pgvector` — embeddings (see below)

Disable extensions you are not using.

## 13. pgvector for RAG

Vector columns contain embeddings that are derived from source text. If that source text is sensitive (tickets, medical notes, contracts), the embedding is also sensitive — it reveals semantic similarity and, with enough queries, can leak content. Protect vector tables with the same RLS policies and role grants as the source tables they derive from.

```sql
ALTER TABLE rag.doc_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_embeddings
  ON rag.doc_chunks
  USING (tenant_id = current_setting('app.tenant_id')::int);
```

Never expose the raw vector column to untrusted clients — return similarity scores and the plain chunk text only when the tenant has the right to read the underlying document.

## 14. Defender's Checklist

- [ ] `listen_addresses` restricted to localhost or private IP
- [ ] `ssl = on`, TLS 1.3 minimum, key file 600
- [ ] `pg_hba.conf` uses `hostssl` + `scram-sha-256` on every network rule
- [ ] No `trust`, `md5`, or `password` methods in pg_hba
- [ ] Explicit `reject` lines at the end of `pg_hba.conf`
- [ ] `password_encryption = scram-sha-256`
- [ ] `REVOKE ALL ... FROM PUBLIC` applied to database and schemas
- [ ] Per-app LOGIN roles with `CONNECTION LIMIT` and `VALID UNTIL`
- [ ] RLS enabled and `FORCE`d on all tenant-scoped tables
- [ ] `app.tenant_id` set per transaction (PgBouncer safe)
- [ ] LUKS on data volume
- [ ] pgcrypto for the most sensitive columns; key in Vault
- [ ] `pgaudit` configured or `log_statement = 'ddl'`/`'mod'` set
- [ ] Logs shipped off-host
- [ ] `pg_dump` output encrypted (GPG) before hitting disk
- [ ] WAL archive target is encrypted
- [ ] Replication uses a `REPLICATION`-only role and `hostssl`
- [ ] Restore drill completed within the last 30 days
- [ ] `shared_preload_libraries` contains only needed extensions

## 15. Anti-Patterns

- `listen_addresses = '*'` on a public-facing host
- Using the `postgres` superuser as the application credential
- `host ... trust` or `host ... md5` rules in `pg_hba.conf`
- Granting `CREATE` on `public` schema to application users
- Enabling RLS but forgetting `FORCE ROW LEVEL SECURITY` for table owners
- Setting `app.tenant_id` once at connection time when using transaction pooling
- Storing pgcrypto keys in `postgresql.conf`, environment variables on the DB host, or a dedicated table
- Unencrypted `pg_dump` files in `/tmp` or on a shared NFS mount
- Publishing `CREATE PUBLICATION ... FOR ALL TABLES` across a trust boundary
- Exposing `pg_stat_statements` to application roles — it can contain query literals with PII
- Loading every extension "just in case" — each one is extra attack surface

## 16. Cross-References

- `postgresql-administration/SKILL.md` — backup, replication, upgrades
- `postgresql-fundamentals/SKILL.md` — roles, schemas, data types
- `postgresql-performance/SKILL.md` — indexes, MVCC, VACUUM
- `postgresql-ai-platform/SKILL.md` — pgvector and RAG patterns
- `cicd-devsecops/SKILL.md` — Vault dynamic Postgres credentials
- `linux-security-hardening` — LUKS, OS-level controls
- `network-security` — firewalling the database subnet
- `php-security/references/db-layer-security.md` — PHP-side controls
- `multi-tenant-saas-architecture` — tenant isolation patterns
