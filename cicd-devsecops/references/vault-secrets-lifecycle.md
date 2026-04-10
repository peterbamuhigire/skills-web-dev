# HashiCorp Vault Secrets Lifecycle on Debian/Ubuntu

Purpose: Run a production HashiCorp Vault cluster on Debian/Ubuntu as the single source of truth for secrets.
Covers install, unseal, policies, auth methods, secrets engines, rotation, audit, backup, HA/DR, and integrations.

## Why Vault

A SaaS platform accumulates secrets quickly: DB passwords, API keys, TLS private keys, SSH keys, OAuth client secrets. Scattering them across `.env` files, Ansible inventory, and Jenkins credentials invites breach. Vault centralises them with:

- **Single source of truth** — one place to rotate, revoke, and audit.
- **Dynamic secrets** — DB credentials created on demand, scoped to a TTL, auto-revoked.
- **Fine-grained policies** — HCL policies describe exactly which paths each identity can access.
- **Audit log** — every read, write, and delete is recorded to an append-only log.
- **Encryption as a service** — Transit engine lets apps encrypt data without handling keys.
- **Pluggable auth** — AppRole for apps, Kubernetes for pods, LDAP/OIDC for humans, TLS certs for machines.

## Install Vault on Debian

Vault ships as an apt package from HashiCorp's official repo:

```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg \
  | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
  https://apt.releases.hashicorp.com bookworm main" \
  | sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update
sudo apt install vault
```

Minimum config for a single-node dev-prod trial (store in `/etc/vault.d/vault.hcl`):

```hcl
ui            = true
cluster_addr  = "https://vault01.prod.example.com:8201"
api_addr      = "https://vault01.prod.example.com:8200"

storage "raft" {
  path    = "/opt/vault/data"
  node_id = "vault01"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/etc/vault.d/tls/vault.crt"
  tls_key_file  = "/etc/vault.d/tls/vault.key"
}

telemetry {
  prometheus_retention_time = "24h"
  disable_hostname          = true
}
```

Then `systemctl enable --now vault`.

## Initial unseal and operator setup

Vault starts **sealed** — it cannot read its own data without a cryptographic key.

```bash
export VAULT_ADDR=https://vault01.prod.example.com:8200
vault operator init
```

This returns **5 unseal keys** (Shamir secret-sharing, threshold 3) and **one initial root token**. Rules:

- Distribute the 5 unseal keys to 5 different trustees on 5 different media (hardware tokens, sealed envelopes in different safes).
- Never store all 5 unseal keys in one place — defeats Shamir.
- Never commit unseal keys to git, Jenkins, or cloud storage.
- The root token should be revoked immediately after creating admin policies and admin users: `vault token revoke <root_token>`.
- For production, use **auto-unseal** via a cloud KMS (AWS KMS, GCP KMS, Azure Key Vault) or a hardware TPM so restarts don't require manual unseal.

```bash
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>
vault status
```

## Storage backends

| Backend | Use case | Notes |
|---|---|---|
| **Integrated Raft** | Recommended for HA production | Built-in consensus, no external dependency, snapshot support |
| **Consul** | Legacy HA option | Requires separate Consul cluster; operationally heavier |
| **File** | Dev/test only | No HA, no encryption of index |

For a self-managed Debian SaaS, integrated Raft is the right answer. Deploy 3 or 5 Vault nodes, each with its own Raft storage directory, and they form a consensus cluster.

## Policies

Vault policies are written in HCL and attached to tokens, AppRoles, or auth method mounts.

Read-only policy for an application:

```hcl
# policies/app-read.hcl
path "secret/data/myapp/prod/*" {
  capabilities = ["read"]
}

path "database/creds/myapp-ro" {
  capabilities = ["read"]
}
```

Admin policy for the ops team:

```hcl
# policies/ops-admin.hcl
path "sys/policies/acl/*" { capabilities = ["create","read","update","delete","list"] }
path "sys/auth/*"         { capabilities = ["create","read","update","delete","sudo"] }
path "sys/mounts/*"       { capabilities = ["create","read","update","delete","sudo"] }
path "secret/*"           { capabilities = ["create","read","update","delete","list"] }
path "database/*"         { capabilities = ["create","read","update","delete","list"] }
```

Apply:

```bash
vault policy write app-read policies/app-read.hcl
vault policy write ops-admin policies/ops-admin.hcl
```

Least privilege is the rule: give each identity the narrowest policy that still works.

## Auth methods

| Method | Identity | Best for |
|---|---|---|
| **Token** | Root / issued token | Initial bootstrap only |
| **AppRole** | role_id + secret_id | Automated clients (apps, Jenkins, Ansible) |
| **Kubernetes** | Service account JWT | Pods |
| **LDAP / OIDC** | Human user | Ops team logins |
| **TLS Certificates** | Client cert | Machine-to-machine with PKI already in place |
| **AWS IAM / GCP IAM** | Cloud instance identity | Cloud-native workloads |

### AppRole setup for a PHP app

```bash
# Enable approle once
vault auth enable approle

# Create the role
vault write auth/approle/role/myapp-prod \
  token_policies="app-read" \
  token_ttl=1h \
  token_max_ttl=4h \
  secret_id_ttl=24h \
  bind_secret_id=true

# Fetch role_id (stable, can be embedded in config)
vault read auth/approle/role/myapp-prod/role-id

# Issue secret_id (short-lived, injected at deploy time)
vault write -f auth/approle/role/myapp-prod/secret-id
```

The app logs in with `role_id + secret_id` to receive a short-lived token. Jenkins fetches a fresh secret_id at deploy time and injects it via environment.

## Secrets engines

| Engine | What it stores / does |
|---|---|
| **KV v2** | Generic key/value with versioning and metadata |
| **Database** | Dynamic DB creds with auto-expiry (MySQL, PostgreSQL, MongoDB, MSSQL, Redis) |
| **PKI** | Internal Certificate Authority; issue short-lived TLS certs |
| **Transit** | Crypto as a service — encrypt/decrypt without exposing the key |
| **SSH** | Signed SSH keys with TTL; eliminates long-lived key files |
| **TOTP** | Generate MFA one-time passwords |

Enable:

```bash
vault secrets enable -version=2 -path=secret kv
vault secrets enable database
vault secrets enable pki
vault secrets enable transit
vault secrets enable ssh
```

## Dynamic database credentials example

Give the app short-lived, unique DB credentials instead of a shared password.

```bash
# Configure the DB connection (Vault uses a privileged root account to create users)
vault write database/config/myapp-mysql \
  plugin_name=mysql-database-plugin \
  connection_url='{{username}}:{{password}}@tcp(db01.prod.example.com:3306)/' \
  allowed_roles="myapp-rw,myapp-ro" \
  username="vault_root" \
  password="$(cat /root/vault_mysql_root_pass)"

# Role: what SQL to run when creating a new user
vault write database/roles/myapp-rw \
  db_name=myapp-mysql \
  creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; \
    GRANT SELECT, INSERT, UPDATE, DELETE ON myapp.* TO '{{name}}'@'%';" \
  default_ttl="1h" \
  max_ttl="24h"
```

The app then does:

```bash
vault read database/creds/myapp-rw
# returns username and password, valid for 1h
```

Vault automatically drops the user at the end of the lease. If the app is compromised, the blast radius is one hour.

## Transit engine example

Encrypt PII at rest in your application database without the app ever handling the key:

```bash
vault write -f transit/keys/app-pii

# Encrypt
vault write transit/encrypt/app-pii \
  plaintext=$(echo -n "john@example.com" | base64)
# -> ciphertext: vault:v1:AbCdEf...

# Decrypt
vault write transit/decrypt/app-pii \
  ciphertext="vault:v1:AbCdEf..."
# -> plaintext: am9obkBleGFtcGxlLmNvbQ==
```

The app stores the ciphertext column. To rotate the encryption key, run `vault write -f transit/keys/app-pii/rotate`. Old ciphertexts continue to decrypt because Vault keeps previous key versions.

## Token rotation and lease renewal

Vault tokens are short-lived by design. The app must **renew** before expiry or request a fresh one:

```bash
vault token renew
```

Implement in app code: on login, fetch `lease_duration`; schedule a renewal at 2/3 of the TTL. On renewal failure, re-authenticate from scratch (AppRole).

Fail-safe pattern: if Vault is unreachable and the token has expired, fail closed (reject requests) rather than continuing with stale creds.

## Audit log

Enable a file audit device immediately after init. Without audit, you cannot prove who read which secret.

```bash
sudo mkdir -p /var/log/vault && sudo chown vault:vault /var/log/vault

vault audit enable file file_path=/var/log/vault/audit.log
```

- Every request and response is logged as JSON.
- Sensitive values are HMAC'd, not recorded in plaintext.
- Ship the log to SigNoz, Loki, or an external SIEM. Never rotate in place without first shipping — audit log loss is a compliance finding.

## Key rotation

Two different things to rotate:

1. **Encryption key** (the key Vault uses to encrypt its own storage):
   ```bash
   vault operator rotate
   ```
   Safe to run any time; Vault starts using the new key for new writes.

2. **Root key / unseal keys** (Shamir key rekey ceremony):
   ```bash
   vault operator rekey -init -key-shares=5 -key-threshold=3
   ```
   Required when a key custodian leaves the team.

Per-secret rotation policies are configured on each engine (database: `default_ttl`; PKI: cert TTL; KV: manual versioning).

## Backup

Raft snapshots are the recommended backup:

```bash
vault operator raft snapshot save /backup/vault-$(date +%F).snap
```

- Run nightly via cron or systemd timer.
- Encrypt snapshots at rest — they contain all secrets in encrypted form but still the full storage.
- Store off-host (S3, MinIO, another region).
- Test restore quarterly: `vault operator raft snapshot restore backup.snap`.
- **Never** store unseal keys alongside the snapshot; an attacker with both gets everything.

## High availability and disaster recovery

### Active/standby HA

With Raft storage, 3 or 5 Vault nodes form a cluster. One is active (accepts writes), others forward requests to the active node. Failover is automatic on active node loss.

- Load balancer should send all traffic to the active node (Vault exposes `sys/health` for health checks).
- Unseal all nodes after a restart (or use auto-unseal so nodes come up sealed-but-auto-unsealing).

### DR replication (Enterprise)

HashiCorp Vault Enterprise offers disaster-recovery and performance replication across regions. For OSS, equivalent is nightly snapshots restored to a warm standby.

## Integrations

| Platform | How to integrate |
|---|---|
| **Ansible** | `community.hashi_vault.hashi_vault` lookup plugin — fetch at playbook runtime |
| **Jenkins** | HashiCorp Vault plugin — inject secrets as env vars, bound to a credential ID |
| **PHP** | `csharpru/vault-php` SDK or raw cURL to `/v1/secret/data/...` |
| **Node.js** | `node-vault` npm package |
| **Python** | `hvac` library |
| **Kubernetes** | Vault Agent Injector — sidecar writes secrets to a shared volume |

## Anti-patterns

- **Root token in an environment variable** — only use root for initial setup; revoke immediately after.
- **All unseal keys in one backup** — defeats Shamir; distribute across people and media.
- **Unauthenticated Vault access on an admin network** — Vault is a high-value target; require mTLS and network policies even internally.
- **Long-lived tokens where AppRole would work** — a leaked 10-year token is a breach; short-lived + renewal closes the window.
- **Secrets in .env files as a "backup" for when Vault is down** — defeats the point. Instead, design for Vault HA and fail-safe defaults.
- **Not enabling audit logging** — no audit means no detection, no forensics, and audit findings.
- **Manual unseal in production** — every restart becomes a ceremony. Use cloud KMS auto-unseal.
- **Giving apps `list` on sensitive paths** — they only need `read` on specific keys.

## Cross-references

- `cicd-devsecops/SKILL.md` — parent skill: DevSecOps CI/CD hardening
- `cicd-devsecops/references/ansible-security-automation.md` — Ansible + Vault integration
- `cicd-devsecops/references/compliance-mapping.md` — audit log requirements for compliance
- `cicd-jenkins-debian/SKILL.md` — Jenkins + Vault credential injection
- `network-security/SKILL.md` — network policies around Vault cluster
- `dual-auth-rbac/SKILL.md` — how apps authenticate to Vault and propagate identity
