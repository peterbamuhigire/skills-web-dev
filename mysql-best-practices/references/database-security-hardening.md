# MySQL 8 Database Security Hardening (Debian/Ubuntu)

Hardening playbook for MySQL 8.x on Debian/Ubuntu SaaS hosts — from package install to ongoing audit. Distilled from Database and Application Security, adapted for self-managed production deployments.

## 1. The Attack Surface of a Database

A database is not a single perimeter; it is a stack of layers, each of which can be the weakest link. Think of hardening as reducing the surface at every layer, not just at the network.

| Layer | Example exposure |
|---|---|
| Network | `bind-address = 0.0.0.0`, port 3306 reachable from the internet |
| Authentication | Weak passwords, `mysql_native_password`, reused creds |
| Authorization | `GRANT ALL`, `*.*` privileges, shared app users |
| Schema | Plaintext PII columns, no row-level isolation |
| Query plan | Untrusted SQL fragments, `prepare`/`execute` abuse |
| Audit logs | Disabled, local-only, rotated too aggressively |
| Backups | Plaintext `mysqldump` files on unencrypted disks |
| Replication | Unencrypted replica streams carrying PII |

The goal of the rest of this document is to shrink every row in that table.

## 2. Network Exposure

Never expose MySQL directly to the public internet. The database lives on a private network or on localhost, and the application talks to it over a trusted subnet.

Edit `/etc/mysql/mysql.conf.d/mysqld.cnf`:

```ini
[mysqld]
bind-address = 127.0.0.1
# Multi-host deployments — use private subnet interface only:
# bind-address = 10.0.1.15
require_secure_transport = ON
skip_name_resolve = ON
```

Restart and verify:

```bash
sudo systemctl restart mysql
sudo ss -tlnp | grep 3306
# Must show 127.0.0.1:3306 or the private IP, never 0.0.0.0:3306
```

Enforce at the firewall too:

```bash
sudo ufw deny 3306/tcp
sudo ufw allow from 10.0.1.0/24 to any port 3306 proto tcp
```

## 3. TLS for Client Connections

Even on a private network, encrypt client traffic. `require_secure_transport = ON` rejects any non-TLS client.

Provision certificates (internal CA or Let's Encrypt for a public hostname) and add to `mysqld.cnf`:

```ini
[mysqld]
ssl_ca   = /etc/mysql/ssl/ca.pem
ssl_cert = /etc/mysql/ssl/server-cert.pem
ssl_key  = /etc/mysql/ssl/server-key.pem
tls_version = TLSv1.2,TLSv1.3
```

Set strict permissions on the key:

```bash
sudo chown mysql:mysql /etc/mysql/ssl/*.pem
sudo chmod 600 /etc/mysql/ssl/server-key.pem
```

Connect from a client with verification:

```bash
mysql --host=db.internal --user=app \
      --ssl-mode=VERIFY_IDENTITY \
      --ssl-ca=/etc/ssl/certs/ca.pem \
      -p
```

Verify the session is actually encrypted:

```sql
SHOW STATUS LIKE 'Ssl_cipher';
-- Value must be non-empty, e.g. TLS_AES_256_GCM_SHA384
SHOW STATUS LIKE 'Ssl_version';
```

## 4. Authentication Plugins

MySQL 8 defaults to `caching_sha2_password`, which uses SHA-256 with a salted hash and is resistant to rainbow-table attacks. `mysql_native_password` exists for backward compatibility only and must not be used for new users.

```ini
[mysqld]
default_authentication_plugin = caching_sha2_password
```

```sql
CREATE USER 'app'@'10.0.1.%'
  IDENTIFIED WITH caching_sha2_password BY '...';

-- Audit existing accounts:
SELECT user, host, plugin FROM mysql.user;
```

For enterprise environments, MySQL supports LDAP and PAM authentication plugins so that DBA accounts tie into centralised identity. Application accounts should still use caching_sha2_password with per-service credentials.

## 5. User and Privilege Hardening

Run `mysql_secure_installation` on every fresh install to remove the test database, drop anonymous users, and disallow remote root.

```bash
sudo mysql_secure_installation
```

Then enforce these rules manually:

- Each application gets its own MySQL user, with a password unique to that service.
- No shared credentials between services.
- No application ever uses `root`.
- Grants are scoped to a specific database and IP range.

```sql
CREATE USER 'billing_app'@'10.0.1.%'
  IDENTIFIED BY '...'
  PASSWORD EXPIRE INTERVAL 90 DAY
  FAILED_LOGIN_ATTEMPTS 5
  PASSWORD_LOCK_TIME 2;

GRANT SELECT, INSERT, UPDATE, DELETE
  ON billing_db.*
  TO 'billing_app'@'10.0.1.%';

-- Read-only reporting user:
GRANT SELECT ON billing_db.* TO 'billing_ro'@'10.0.1.%';

-- Migration user (only used by the release pipeline):
GRANT ALL PRIVILEGES ON billing_db.* TO 'billing_migrate'@'10.0.1.50';
```

Reject `GRANT ALL` in production except for a dedicated migration credential that is used only by CI/CD at deploy time. Never use `*.*`.

The one legitimate exception is the backup user, which requires global read-level privileges but nothing destructive:

```sql
CREATE USER 'backup'@'localhost' IDENTIFIED BY '...';
GRANT RELOAD, LOCK TABLES, PROCESS, REPLICATION CLIENT, SELECT
  ON *.* TO 'backup'@'localhost';
```

Audit grants regularly:

```sql
SHOW GRANTS FOR 'billing_app'@'10.0.1.%';

SELECT grantee, privilege_type
FROM information_schema.user_privileges
WHERE privilege_type IN ('SUPER','FILE','PROCESS','SHUTDOWN')
ORDER BY grantee;
```

## 6. Password Policy Enforcement

MySQL 8 ships the `validate_password` component. Install and configure it once:

```sql
INSTALL COMPONENT 'file://component_validate_password';

SET GLOBAL validate_password.policy = 'STRONG';
SET GLOBAL validate_password.length = 14;
SET GLOBAL validate_password.mixed_case_count = 1;
SET GLOBAL validate_password.number_count = 1;
SET GLOBAL validate_password.special_char_count = 1;
SET GLOBAL validate_password.check_user_name = ON;
```

Persist to `my.cnf`:

```ini
[mysqld]
validate_password.policy = STRONG
validate_password.length = 14
```

## 7. Account Lockout on Failed Login

Brute-force protection is handled per-user in MySQL 8. Apply to every interactive account:

```sql
ALTER USER 'admin'@'10.0.1.%'
  FAILED_LOGIN_ATTEMPTS 5
  PASSWORD_LOCK_TIME 2;   -- lock for 2 days; UNBOUNDED to require manual unlock
```

Application accounts are a judgement call — locking them causes downtime, so prefer a lower network blast radius (rate-limit at the app and firewall) rather than auto-lock.

## 8. Per-Row Encryption of Sensitive Fields

Encrypt PII columns at the application layer, not with MySQL's `AES_ENCRYPT()` using a hardcoded key. The app fetches the key from a secrets manager (HashiCorp Vault, AWS KMS) and performs AES-256-GCM before the value touches the database.

Schema pattern:

```sql
CREATE TABLE patient (
  id            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  tenant_id     INT NOT NULL,
  -- Plaintext is fine for non-PII:
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  -- PII columns store ciphertext + per-row IV + key version:
  full_name_ct  VARBINARY(512) NOT NULL,
  full_name_iv  BINARY(12)     NOT NULL,
  key_version   SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  INDEX idx_tenant (tenant_id)
);
```

Key rotation is possible because each row records `key_version`. The application layer decrypts with the matching version from Vault. Never store the key in `my.cnf`, in code, or in the same database as the data.

## 9. Encryption at Rest

Enable InnoDB tablespace encryption for data files and redo logs:

```sql
-- Per-table:
ALTER TABLE patient ENCRYPTION='Y';

-- System tablespace (requires keyring):
ALTER TABLESPACE innodb_system ENCRYPTION='Y';
```

Install a keyring plugin. For a single-host deployment the file-based keyring is acceptable if the keyring file lives on a volume with separate access control:

```ini
[mysqld]
early-plugin-load = keyring_file.so
keyring_file_data = /var/lib/mysql-keyring/keyring
```

```bash
sudo mkdir -p /var/lib/mysql-keyring
sudo chown mysql:mysql /var/lib/mysql-keyring
sudo chmod 750 /var/lib/mysql-keyring
```

Enterprise deployments should use KMIP or Vault-backed keyrings so the master key is never on the same host as the data files.

A complementary layer is LUKS full-disk encryption at the OS level. LUKS protects against disk theft; InnoDB encryption protects against unauthorised file-level access by another OS user. Use both.

## 10. Audit Logging

The community edition does not ship the Enterprise Audit Log plugin. Use a combination of the built-in logs plus ship them off-host:

```ini
[mysqld]
log_error       = /var/log/mysql/error.log
slow_query_log  = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 1
log_queries_not_using_indexes = 1

# General log is expensive — enable briefly during investigations:
general_log      = 0
general_log_file = /var/log/mysql/general.log
```

What to review on the error log:

- Authentication failures (`Access denied for user`)
- Plugin load/unload
- Unexpected restarts or crashes
- DDL events (captured by the audit plugin or binary log)

Ship logs to a central host (Loki, Elasticsearch, SigNoz) using `promtail` or `vector`. Local-only logs are useless if the host is compromised.

For Enterprise-level auditing without a licence, the `audit_log` plugin from Percona Server is a drop-in replacement that writes JSON audit events.

## 11. SQL Injection Defence in Depth

SQL injection is primarily an application-layer bug — see `php-security/references/injection-attack-patterns.md` and `php-security/references/db-layer-security.md`. At the database layer, hardening limits the blast radius:

- Least-privilege users mean an injection cannot `DROP` other databases.
- Revoked `FILE` privilege prevents `SELECT ... INTO OUTFILE`.
- Revoked `PROCESS` prevents reading other sessions' queries.
- `max_execution_time` prevents a slow injection from exhausting connections.

## 12. Backup Security

Backups are a full copy of production data, so they need the same or stronger protection as the live database. A `mysqldump` file is plaintext by default.

Encrypted backup script (cron-friendly):

```bash
#!/bin/bash
set -euo pipefail
TS=$(date +%F-%H%M)
DEST=/var/backups/mysql
mkdir -p "$DEST"

mysqldump --defaults-file=/etc/mysql/backup.cnf \
          --single-transaction --quick --routines --triggers \
          --all-databases \
  | gzip \
  | gpg --batch --yes --encrypt \
        --recipient backup@example.com \
        --output "$DEST/backup-$TS.sql.gz.gpg"

# Retain 14 days:
find "$DEST" -name 'backup-*.sql.gz.gpg' -mtime +14 -delete
```

`/etc/mysql/backup.cnf` contains the backup user credentials, owned by root, mode 600.

Verify backups with a monthly restore test to a scratch host:

```bash
gpg --decrypt backup-2026-04-10-0200.sql.gz.gpg | gunzip | mysql -u root -p scratch
```

A backup you have never restored is not a backup.

## 13. Replication Security

For every replica:

```ini
# Primary
[mysqld]
log_bin       = /var/log/mysql/mysql-bin
binlog_format = ROW
binlog_row_image = MINIMAL
server_id     = 1

# Replica
[mysqld]
server_id     = 2
read_only     = ON
super_read_only = ON
```

Create a dedicated replication user with the minimum privilege:

```sql
CREATE USER 'repl'@'10.0.1.%' IDENTIFIED BY '...';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'10.0.1.%';
```

Require TLS on the replication link:

```sql
ALTER USER 'repl'@'10.0.1.%' REQUIRE SSL;

CHANGE REPLICATION SOURCE TO
  SOURCE_HOST = 'db1.internal',
  SOURCE_USER = 'repl',
  SOURCE_PASSWORD = '...',
  SOURCE_SSL = 1,
  SOURCE_SSL_CA = '/etc/mysql/ssl/ca.pem',
  SOURCE_SSL_VERIFY_SERVER_CERT = 1;
```

Binary logs contain row images of every change — protect `/var/log/mysql` with mode 750 and encrypt the disk.

## 14. Performance Schema and Information Leakage

`performance_schema.events_statements_history` and `events_statements_summary_by_digest` can contain substrings of recent queries, which may leak email, phone numbers, or tokens from WHERE clauses.

Restrict access:

```sql
REVOKE SELECT ON performance_schema.* FROM 'billing_app'@'10.0.1.%';
-- Keep SELECT only for a dedicated DBA/monitoring user.
```

Sanitize before exporting any diagnostics to a support ticket.

## 15. Denial of Service Controls

Caps that prevent one client from saturating the server:

```ini
[mysqld]
max_connections       = 500
max_user_connections  = 100
max_connect_errors    = 100
wait_timeout          = 300
interactive_timeout   = 300
max_execution_time    = 5000         # milliseconds, for SELECT
max_allowed_packet    = 64M
```

Per-user limits on top of globals:

```sql
ALTER USER 'billing_app'@'10.0.1.%'
  WITH MAX_USER_CONNECTIONS 50
       MAX_QUERIES_PER_HOUR 200000
       MAX_UPDATES_PER_HOUR 50000;
```

For multi-tenant workloads, MySQL 8 Resource Groups let you cap CPU affinity by tenant:

```sql
CREATE RESOURCE GROUP tenant_slow
  TYPE = USER
  VCPU = 2-3
  THREAD_PRIORITY = 5;
```

## 16. Defender's Checklist

- [ ] `bind-address` is `127.0.0.1` or a private IP — never `0.0.0.0`
- [ ] `require_secure_transport = ON` and TLS 1.2+ enforced
- [ ] `mysql_secure_installation` run on fresh installs
- [ ] No anonymous users, no remote root
- [ ] Every app has its own MySQL user with least-priv grants
- [ ] No production account has `*.*` (except the backup user)
- [ ] `caching_sha2_password` for all accounts
- [ ] `validate_password` component installed with STRONG policy
- [ ] `FAILED_LOGIN_ATTEMPTS` and `PASSWORD_LOCK_TIME` set on privileged users
- [ ] InnoDB encryption enabled for tablespaces containing PII
- [ ] Keyring plugin configured; keyring file not on the data volume
- [ ] App-layer AES-256-GCM on the most sensitive PII columns
- [ ] Error, slow, and (where licensed) audit logs shipped to central store
- [ ] `mysqldump` output encrypted with GPG or `openssl enc`
- [ ] Backup restore drill completed within the last 30 days
- [ ] Replication uses TLS and a dedicated `REPLICATION SLAVE` user
- [ ] `performance_schema` SELECT revoked from app accounts
- [ ] `max_execution_time`, `max_connections`, and per-user caps set

## 17. Anti-Patterns

- `GRANT ALL PRIVILEGES ON *.* TO 'app'@'%'` — universal access, universal risk
- Sharing one MySQL user across every microservice
- Using `root` as the application credential
- `bind-address = 0.0.0.0` with port 3306 reachable from a public interface
- Storing PII in plaintext columns because "the database is private"
- Hardcoding encryption keys in `my.cnf` or in application code
- Plaintext `mysqldump` files left in `/tmp` or S3 without encryption
- Disabling TLS "for performance" — modern CPUs handle AES-NI at line rate
- Running `mysql_native_password` for new accounts to support an old driver
- Never testing a backup restore
- Exposing the MySQL port to the internet for "remote admin"

## 18. Cross-References

- `mysql-best-practices/SKILL.md` — overall MySQL 8 patterns
- `mysql-administration/SKILL.md` — replication, backup, PITR
- `cicd-devsecops/SKILL.md` — Vault for MySQL credentials and keyring
- `linux-security-hardening` — OS-level controls underneath MySQL
- `network-security` — firewalling the database subnet
- `php-security/references/db-layer-security.md` — app side of the trust boundary
- `php-security/references/injection-attack-patterns.md` — SQLi details
- `multi-tenant-saas-architecture` — tenant isolation patterns on top of MySQL
