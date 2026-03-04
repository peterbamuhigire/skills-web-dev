# MySQL Security Hardening Reference

Deep reference for the `mysql-best-practices` skill. Covers post-installation hardening,
authentication, encryption, auditing, and network security for MySQL 8.x.

**Source:** Mastering MySQL Administration (Kumar et al., 2024)

---

## Post-Installation Hardening (MANDATORY)

Every new MySQL installation MUST be hardened before any application connects to it.
Use `mysql_secure_installation` CLI or run these steps manually:

```sql
-- 1. Change default root password
ALTER USER 'root'@'localhost' IDENTIFIED BY 'StrongPassword!';

-- 2. Remove anonymous users
DELETE FROM mysql.user WHERE User = '';

-- 3. Drop test database
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db = 'test' OR Db = 'test\\_%';

-- 4. Disable remote root access
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- 5. Apply changes
FLUSH PRIVILEGES;
```

### Verify Hardening

```sql
SELECT User, Host FROM mysql.user WHERE User = '';          -- Expected: Empty set
SELECT User, Host FROM mysql.user WHERE User = 'root';      -- Expected: localhost only
SHOW DATABASES LIKE 'test';                                  -- Expected: Empty set
```

---

## Password Policy

```sql
-- Install validate_password component (MySQL 8.0+)
INSTALL COMPONENT 'file://component_validate_password';

-- Configure strong policy
SET GLOBAL validate_password.policy = 'STRONG';
SET GLOBAL validate_password.length = 12;
SET GLOBAL validate_password.mixed_case_count = 1;
SET GLOBAL validate_password.number_count = 1;
SET GLOBAL validate_password.special_char_count = 1;
SET GLOBAL validate_password.check_user_name = ON;
```

| Policy | Requirements |
|--------|-------------|
| `LOW` | Length only |
| `MEDIUM` | Length + numbers + mixed case + special characters |
| `STRONG` | Medium + dictionary file check (rejects common passwords) |

### Password Expiration and History

```sql
SET GLOBAL default_password_lifetime = 90;                        -- Rotate every 90 days
ALTER USER 'app_user'@'%' PASSWORD EXPIRE INTERVAL 180 DAY;      -- Per-user override
ALTER USER 'app_user'@'%' PASSWORD REQUIRE CURRENT;               -- Must provide old password
ALTER USER 'app_user'@'%' PASSWORD HISTORY 5;                     -- No reusing last 5
```

### Persist in my.cnf

```ini
[mysqld]
validate_password.policy = STRONG
validate_password.length = 12
```

---

## User Privilege Management (Least Privilege)

**Core Rule:** Never use `root` for application connections. Create purpose-built users.

### Commonly Used Privileges

| Privilege | Scope | Description |
|-----------|-------|-------------|
| `SELECT` | Table | Read data |
| `INSERT` | Table | Add rows |
| `UPDATE` | Table | Modify existing rows |
| `DELETE` | Table | Remove rows |
| `CREATE` | Database/Table | Create tables, databases |
| `DROP` | Database/Table | Drop tables, databases |
| `ALTER` | Table | Modify table structure |
| `INDEX` | Table | Create/drop indexes |
| `EXECUTE` | Routine | Run stored procedures/functions |
| `CREATE VIEW` | Database | Create views |
| `TRIGGER` | Table | Create/drop triggers |
| `REFERENCES` | Table | Create foreign keys |

**Dangerous -- NEVER grant to application users:**
`FILE`, `PROCESS`, `SHUTDOWN`, `SUPER`, `CREATE USER`, `GRANT OPTION`, `RELOAD`

### Application User Patterns

```sql
-- Standard CRUD (application user)
CREATE USER 'saas_app'@'%' IDENTIFIED BY 'strong_random_password_here';
GRANT SELECT, INSERT, UPDATE, DELETE ON saas_platform.* TO 'saas_app'@'%';

-- Read-only reporting user
CREATE USER 'saas_readonly'@'%' IDENTIFIED BY 'reporting_password_here';
GRANT SELECT ON saas_platform.* TO 'saas_readonly'@'%';

-- Migration user (DDL privileges, localhost only)
CREATE USER 'saas_migrator'@'localhost' IDENTIFIED BY 'migration_password_here';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX,
      CREATE VIEW, TRIGGER, REFERENCES
      ON saas_platform.* TO 'saas_migrator'@'localhost';

-- Backup user (specific grants only)
CREATE USER 'saas_backup'@'localhost' IDENTIFIED BY 'backup_password_here';
GRANT SELECT, SHOW VIEW, TRIGGER, LOCK TABLES, EVENT, RELOAD,
      REPLICATION CLIENT ON *.* TO 'saas_backup'@'localhost';

FLUSH PRIVILEGES;
```

### Audit Existing Privileges

```sql
-- Show grants for a specific user
SHOW GRANTS FOR 'saas_app'@'%';

-- Find users with dangerous privileges
SELECT User, Host FROM mysql.user
WHERE Super_priv = 'Y' OR File_priv = 'Y' OR Grant_priv = 'Y';
```

---

## Role-Based Access Control (RBAC)

MySQL 8.0 supports named roles that group privileges for easier management.

```sql
-- Create roles
CREATE ROLE 'app_read', 'app_write', 'app_admin';

-- Grant privileges to roles
GRANT SELECT ON saas_platform.* TO 'app_read';
GRANT INSERT, UPDATE, DELETE ON saas_platform.* TO 'app_write';
GRANT CREATE, DROP, ALTER, INDEX ON saas_platform.* TO 'app_admin';

-- Assign roles to users
GRANT 'app_read', 'app_write' TO 'saas_app'@'%';
GRANT 'app_read', 'app_write', 'app_admin' TO 'saas_migrator'@'localhost';
GRANT 'app_read' TO 'saas_readonly'@'%';

-- Set default roles (activated on login)
SET DEFAULT ROLE ALL TO 'saas_app'@'%';
SET DEFAULT ROLE ALL TO 'saas_migrator'@'localhost';

-- Runtime management
SET ROLE 'app_admin';                          -- Activate in current session
SET ROLE NONE;                                 -- Deactivate all
REVOKE 'app_admin' FROM 'saas_app'@'%';       -- Remove role from user
DROP ROLE 'app_admin';                         -- Delete role entirely
```

---

## Authentication Methods

| Method | Plugin | Use Case |
|--------|--------|----------|
| **caching_sha2_password** | `caching_sha2_password` | Default in 8.0. Recommended for all new installs |
| **SHA-256** | `sha256_password` | Secure but slower (no caching). Requires SSL |
| **Native** | `mysql_native_password` | Legacy compatibility. **Deprecated in 8.0** |
| **LDAP Simple** | `authentication_ldap_simple` | Enterprise. Bind to LDAP directory |
| **LDAP SASL** | `authentication_ldap_sasl` | Enterprise. SASL-based LDAP (SCRAM-SHA-256) |
| **PAM** | `authentication_pam` | Enterprise. Linux PAM integration |
| **Windows AD** | `authentication_windows` | Enterprise. Active Directory on Windows |

```sql
-- New user with default (caching_sha2_password)
CREATE USER 'new_user'@'%' IDENTIFIED BY 'password';

-- Explicit legacy plugin (avoid if possible)
CREATE USER 'legacy_user'@'%' IDENTIFIED WITH mysql_native_password BY 'password';

-- Migrate user to recommended plugin
ALTER USER 'old_user'@'%' IDENTIFIED WITH caching_sha2_password BY 'new_password';
```

```ini
# my.cnf -- set default authentication
[mysqld]
default_authentication_plugin = caching_sha2_password
```

---

## Resource Limits Per User

Prevent any single user from monopolizing server resources.

```sql
ALTER USER 'app_user'@'%' WITH
  MAX_QUERIES_PER_HOUR 10000
  MAX_UPDATES_PER_HOUR 5000
  MAX_CONNECTIONS_PER_HOUR 1000
  MAX_USER_CONNECTIONS 50;
```

| Limit | Purpose | Recommended Range |
|-------|---------|-------------------|
| `MAX_QUERIES_PER_HOUR` | Total queries (SELECT + DML) | 5,000 - 50,000 |
| `MAX_UPDATES_PER_HOUR` | Write operations only | 1,000 - 10,000 |
| `MAX_CONNECTIONS_PER_HOUR` | Connection attempts | 500 - 5,000 |
| `MAX_USER_CONNECTIONS` | Simultaneous connections | 20 - 100 |

Set to `0` to remove a limit. Check with:
`SELECT User, Host, max_questions, max_updates, max_connections, max_user_connections FROM mysql.user WHERE User = 'app_user';`

---

## Transparent Data Encryption (TDE)

Two-tier key architecture: a master key encrypts per-tablespace keys. Decryption
is transparent to applications.

### Keyring Plugin Setup (my.cnf)

```ini
[mysqld]
early-plugin-load = keyring_file.so
keyring_file_data = /var/lib/mysql-keyring/keyring
default_table_encryption = ON
```

### Encrypt Tables and Logs

```sql
-- Encrypt a specific table
ALTER TABLE customers ENCRYPTION = 'Y';

-- Encrypt all tables in a tablespace
ALTER TABLESPACE ts_sensitive ENCRYPTION = 'Y';

-- Encrypt redo log (protects transaction recovery data)
ALTER INSTANCE ENABLE INNODB REDO_LOG ENCRYPTION;

-- Encrypt undo log (protects rollback data)
ALTER INSTANCE ENABLE INNODB UNDO_LOG ENCRYPTION;

-- Verify encryption status
SELECT TABLE_SCHEMA, TABLE_NAME, CREATE_OPTIONS
FROM information_schema.TABLES WHERE CREATE_OPTIONS LIKE '%ENCRYPTION%';
```

### Master Key Rotation

Rotate periodically (re-encrypts tablespace keys, NOT the data itself).

```sql
ALTER INSTANCE ROTATE INNODB MASTER KEY;
```

---

## Encryption in Transit (SSL/TLS)

### Server Configuration (my.cnf)

```ini
[mysqld]
ssl_ca   = /etc/mysql/ssl/ca-cert.pem
ssl_cert = /etc/mysql/ssl/server-cert.pem
ssl_key  = /etc/mysql/ssl/server-key.pem
require_secure_transport = ON
tls_version = TLSv1.2,TLSv1.3    # MySQL 8.0.28+ drops TLSv1.0/1.1
```

### Require SSL Per User

```sql
CREATE USER 'secure_user'@'%' IDENTIFIED BY 'password' REQUIRE SSL;
CREATE USER 'cert_user'@'%' IDENTIFIED BY 'password' REQUIRE X509;
CREATE USER 'strict_user'@'%' IDENTIFIED BY 'password'
  REQUIRE ISSUER '/CN=MySQL CA' AND SUBJECT '/CN=client1';
```

### Verify TLS

```sql
SHOW VARIABLES LIKE '%ssl%';
SHOW STATUS LIKE 'Ssl_cipher';    -- Non-empty = encrypted connection
```

---

## Enterprise Audit (Enterprise Edition)

```sql
INSTALL PLUGIN audit_log SONAME 'audit_log.so';
```

```ini
# my.cnf
[mysqld]
plugin-load-add = audit_log.so
audit_log_format = JSON
audit_log_policy = ALL                         # ALL, LOGINS, QUERIES, NONE
audit_log_file = /var/log/mysql/audit.log
audit_log_rotate_on_size = 104857600           # 100MB rotation
```

```sql
-- Selective filtering
SET GLOBAL audit_log_include_accounts = 'saas_app@%,saas_migrator@localhost';
SET GLOBAL audit_log_exclude_accounts = 'saas_backup@localhost';
```

---

## Enterprise Firewall (Enterprise Edition)

Learns normal query patterns, then blocks anomalous queries in production.

| Mode | Behavior |
|------|----------|
| `OFF` | Firewall disabled for this user |
| `RECORDING` | Learning phase -- records all query patterns |
| `PROTECTING` | Blocks queries not matching recorded patterns |
| `DETECTING` | Logs anomalous queries without blocking |

```sql
-- 1. Install
INSTALL PLUGIN MYSQL_FIREWALL SONAME 'firewall.so';

-- 2. Record normal queries
CALL mysql.sp_set_firewall_mode('saas_app@%', 'RECORDING');
-- Run application through typical workflows...

-- 3. Switch to protecting mode
CALL mysql.sp_set_firewall_mode('saas_app@%', 'PROTECTING');

-- 4. View allowlist
SELECT * FROM mysql.firewall_whitelist WHERE USERHOST = 'saas_app@%';
```

---

## Secure Backup Practices

### Credential Storage (No Plaintext Passwords)

```bash
# Store credentials securely
mysql_config_editor set --login-path=backup \
  --host=localhost --user=saas_backup --password

# Use login path in scripts (no password exposed)
mysqldump --login-path=backup --single-transaction --all-databases > backup.sql
mysql_config_editor print --all    # List stored paths
```

### Encrypted Backups

```bash
# Backup + encrypt with OpenSSL (AES-256-CBC)
mysqldump --login-path=backup --single-transaction --routines --triggers \
  saas_platform | openssl enc -aes-256-cbc -salt -pbkdf2 \
  -out /backups/saas_platform_$(date +%Y%m%d).sql.enc

# Decrypt and restore
openssl enc -aes-256-cbc -d -pbkdf2 \
  -in /backups/saas_platform_20260304.sql.enc | mysql --login-path=restore saas_platform

# Restrict backup directory access
chmod 700 /backups && chown mysql:mysql /backups
```

---

## Network Security

### Port, Bind Address, and Hardening (my.cnf)

```ini
[mysqld]
port = 33061                 # Change default port (avoid 3306 scans)
bind_address = 127.0.0.1     # Localhost only (most secure)
symbolic-links = 0           # Prevent symlink attacks
local_infile = 0             # Prevent LOAD DATA LOCAL file reads
```

**Bind address options:** `127.0.0.1` (localhost only), specific IP like `10.0.1.50`
(for replication), `0.0.0.0` (all interfaces -- requires firewall rules).

### OS Firewall Rules

```bash
# UFW: allow MySQL only from application server subnet
ufw allow from 10.0.1.0/24 to any port 33061 proto tcp
ufw deny 33061

# iptables equivalent
iptables -A INPUT -p tcp --dport 33061 -s 10.0.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 33061 -j DROP
```

---

## Security Checklist

**Post-Installation:**
- [ ] Root password changed | Anonymous users removed | Test DB dropped
- [ ] Remote root access disabled | `FLUSH PRIVILEGES` executed

**Authentication and Passwords:**
- [ ] `validate_password` set to STRONG with length >= 12
- [ ] Password expiration and history configured
- [ ] All users on `caching_sha2_password` (no legacy plugins)

**Privilege Management:**
- [ ] Application uses dedicated user (never root)
- [ ] Each user has minimum required privileges only
- [ ] No app user has `SUPER`, `FILE`, or `GRANT OPTION`
- [ ] Separate users: app (CRUD), readonly (SELECT), migrator (DDL), backup
- [ ] RBAC roles used for privilege grouping

**Encryption:**
- [ ] TDE enabled with keyring plugin configured
- [ ] Redo/undo log encryption enabled
- [ ] Master key rotation scheduled (quarterly)
- [ ] SSL/TLS enabled with `require_secure_transport = ON`
- [ ] TLS minimum version set to TLSv1.2
- [ ] Sensitive columns encrypted at application layer (AES-256)

**Network:**
- [ ] Default port changed | `bind_address` restricted
- [ ] OS firewall rules limit access to trusted IPs
- [ ] `symbolic-links = 0` and `local_infile = 0` set

**Auditing and Backup:**
- [ ] Audit plugin or query logging active
- [ ] Credentials stored via `mysql_config_editor` (no plaintext)
- [ ] Backups encrypted with restricted file permissions

**Application Layer:**
- [ ] All queries parameterized (no string concatenation)
- [ ] `tenant_id` in every query | UUIDs for public IDs
- [ ] Resource limits configured per user

---

## Cross-References

- **PHP application security:** See `../../php-modern-standards/SKILL.md`
- **Web application security audit:** See `../../vibe-security-skill/SKILL.md`
- **Multi-tenant isolation patterns:** See main `../SKILL.md` (Security section)
- **Dual auth + RBAC at application layer:** See `../../dual-auth-rbac/SKILL.md`

---

**Source:** Mastering MySQL Administration (Kumar et al., 2024)
**Last Updated:** 2026-03-04
**Maintained by:** Peter Bamuhigire
