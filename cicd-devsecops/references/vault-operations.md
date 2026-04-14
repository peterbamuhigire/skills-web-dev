# Vault Operations — AppRole, Dynamic DB Credentials, PKI, Rotation

Day-to-day Vault operational runbook. For install, unseal, HA, and DR, see `vault-secrets-lifecycle.md`.

## AppRole Authentication (Applications)

AppRole issues a pair of values — `role_id` (semi-public) and `secret_id` (sensitive, short-lived) — that an application exchanges for a Vault token.

### Create an AppRole

```bash
vault auth enable approle

vault write auth/approle/role/web-prod \
  token_policies="web-prod" \
  token_ttl=15m \
  token_max_ttl=1h \
  secret_id_ttl=30m \
  secret_id_num_uses=1 \
  bind_secret_id=true
```

- `secret_id_num_uses=1` — the secret_id is single-use; stolen values are useless after first exchange.
- `token_ttl=15m` — short-lived application token.
- `bind_secret_id=true` — a secret_id is required (the default).

### Distribute Role ID and Secret ID

- `role_id` goes into the deploy config / environment variable. It is not a secret on its own.
- `secret_id` is minted per-deploy by the CI pipeline assuming a Vault admin role, then delivered to the workload via response-wrapping:

```bash
vault write -wrap-ttl=60s -f auth/approle/role/web-prod/secret-id
# returns wrapping_token; pipeline passes it to the instance
```

The instance unwraps exactly once:

```bash
vault unwrap <wrapping_token>
```

### Revocation

```bash
vault list auth/approle/role/web-prod/secret-id-accessor
vault write auth/approle/role/web-prod/secret-id-accessor/destroy accessor=<accessor>
```

Or burn the whole role when compromise is suspected:

```bash
vault delete auth/approle/role/web-prod
```

## Dynamic Database Credentials

Vault creates a DB account on demand and revokes it when the lease expires. No shared password ever touches the application.

### Enable and Configure Database Engine (PostgreSQL example)

```bash
vault secrets enable database

vault write database/config/app-prod \
  plugin_name=postgresql-database-plugin \
  allowed_roles="app-reader,app-writer" \
  connection_url="postgresql://{{username}}:{{password}}@db.prod:5432/app?sslmode=require" \
  username="vault_admin" \
  password="<admin-password-once-then-rotate>"

vault write -force database/rotate-root/app-prod
```

The `rotate-root` step ensures Vault is the only entity that knows the admin password after setup.

### Define a Role

```bash
vault write database/roles/app-reader \
  db_name=app-prod \
  default_ttl=1h \
  max_ttl=24h \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";"
```

### Application Usage

```bash
vault read database/creds/app-reader
# username: v-approle-app-reader-abcd
# password: <generated>
# lease_id: database/creds/app-reader/abc
```

The application renews the lease before expiry or reacquires fresh credentials. Vault revokes the DB account when the lease ends.

## PKI Engine (Service-to-Service mTLS)

Vault issues short-lived certificates for internal mTLS. No cert files on disk for longer than an hour.

### Enable a Intermediate CA

```bash
vault secrets enable -path=pki-int pki
vault secrets tune -max-lease-ttl=8760h pki-int

vault write -field=csr pki-int/intermediate/generate/internal \
  common_name="app-prod intermediate CA" \
  | tee pki_intermediate.csr

# sign with the root CA (offline or separate mount), then:
vault write pki-int/intermediate/set-signed certificate=@signed_intermediate.pem
```

### Define a Role

```bash
vault write pki-int/roles/service-mtls \
  allowed_domains="svc.prod.example.com" \
  allow_subdomains=true \
  max_ttl="24h" \
  ttl="24h"
```

### Issue a Cert

```bash
vault write pki-int/issue/service-mtls \
  common_name="payments.svc.prod.example.com" \
  ttl="1h"
```

The response contains `certificate`, `issuing_ca`, `private_key`, and `serial_number`. Private keys stay in the pod memory that requested them; nothing is written to persistent storage.

## Rotation Runbook (Quarterly)

1. List every mount with static credentials: `vault secrets list`.
2. For each static secret, rotate:
   - DB root: `vault write -force database/rotate-root/<name>`
   - KV2 static secret: write a new version, then ask applications to refresh.
3. Rotate AppRole secret_ids for any role with static secret_ids (avoid if possible).
4. Rotate the Vault unseal keys if threat model requires (hardware rotation).
5. Audit: `vault audit list` — confirm every mount logs to the primary audit device.

## Emergency Revocation

If compromise is suspected on a specific path:

```bash
vault lease revoke -prefix database/creds/app-reader
vault lease revoke -prefix pki-int/issue/service-mtls
```

If the entire Vault is suspected compromised:

1. Seal the Vault: `vault operator seal`.
2. Rotate every upstream root credential (cloud provider root, DB root, CA).
3. Restore from a known-good snapshot on fresh infrastructure.
4. Rebuild auth mounts and reissue AppRole credentials.

## Audit Logging

```bash
vault audit enable file file_path=/var/log/vault/audit.log

vault audit enable -path=syslog_audit syslog tag="vault" facility="AUTH"
```

Ship the audit log to a tamper-evident store (S3 with Object Lock, or an append-only log service). Never let the audit sink fail silently — configure Vault to refuse requests if no audit device responds.

## Common Failures

- AppRole secret_id rejected → already consumed (`secret_id_num_uses=1`) or TTL expired. Mint a new one.
- DB dynamic creds fail to create → `database/config` admin credentials are wrong (did you `rotate-root` before updating the config?).
- PKI cert issuance fails → role's `allowed_domains` or `max_ttl` rejects the request.
- Token renew loop → application forgot to renew before `token_ttl`; increase TTL or implement proper renew.
