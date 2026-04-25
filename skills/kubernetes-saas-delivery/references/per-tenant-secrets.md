# Per-Tenant Secrets

Secrets management for multi-tenant SaaS on Kubernetes. Read after the
`SKILL.md` overview. Cross-reference `cicd-devsecops` for Vault
lifecycle and `multi-tenant-saas-architecture` for identity and
authorisation boundaries.

## Principles

- One tenant, one secret path. Never share credentials across tenants.
- Secrets never in Git, never in container images, never in env vars
  committed to manifests.
- Rotation is automatic, not a quarterly ticket.
- External Secrets Operator (ESO) is the synchronisation layer;
  Vault or a cloud KMS is the system of record.

## External Secrets Operator with Vault

### Vault layout

```text
kv/
  tenants/
    acme/
      database-url
      stripe-webhook-secret
      smtp-password
    globex/
      database-url
      ...
  shared/
    observability-token
    dockerhub-pull-token
```

Per tenant, grant a Vault policy that allows reads only under
`kv/data/tenants/<slug>/*` — never the `shared/` tree from a tenant
namespace.

```hcl
path "kv/data/tenants/acme/*" {
  capabilities = ["read"]
}
```

### ClusterSecretStore

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata: { name: vault-tenants }
spec:
  provider:
    vault:
      server: https://vault.infra.svc:8200
      path: kv
      version: v2
      auth:
        kubernetes:
          mountPath: kubernetes
          role: tenant-reader
          serviceAccountRef:
            name: external-secrets
            namespace: external-secrets
```

### ExternalSecret per tenant

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: tenant-db, namespace: tenant-acme }
spec:
  refreshInterval: 1h
  secretStoreRef: { name: vault-tenants, kind: ClusterSecretStore }
  target:
    name: tenant-db
    creationPolicy: Owner
    template:
      type: Opaque
  data:
    - secretKey: DATABASE_URL
      remoteRef: { key: tenants/acme/database-url }
    - secretKey: STRIPE_WEBHOOK_SECRET
      remoteRef: { key: tenants/acme/stripe-webhook-secret }
```

Decision rule: `refreshInterval` must be shorter than the shortest
rotation window you intend to support. One hour is a sensible default;
tighten for high-risk credentials.

## AWS Secrets Manager with IRSA

On EKS, prefer IAM Roles for Service Accounts (IRSA) over Vault when
the rest of the stack is AWS-native.

### SecretStore scoped to the tenant namespace

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata: { name: aws-sm, namespace: tenant-acme }
spec:
  provider:
    aws:
      service: SecretsManager
      region: eu-west-1
      auth:
        jwt:
          serviceAccountRef:
            name: tenant-acme-sa
```

### IAM policy scoped by prefix

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:eu-west-1:1234:secret:tenants/acme/*"
  }]
}
```

Trust policy binds the IAM role to the ServiceAccount via OIDC. Any
leak of the Pod credentials yields access only to that tenant's secret
path.

### ExternalSecret referencing the AWS store

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: tenant-db, namespace: tenant-acme }
spec:
  refreshInterval: 15m
  secretStoreRef: { name: aws-sm, kind: SecretStore }
  target: { name: tenant-db }
  dataFrom:
    - extract: { key: tenants/acme/runtime }
```

## Rotation patterns

- Database credentials: short-lived Vault dynamic credentials (hours)
  or AWS RDS IAM auth with 15-minute tokens.
- Webhook signing keys: rotate on tenant action; ESO refresh picks up
  within `refreshInterval`.
- Long-lived API keys: avoid. Mint on demand, rotate via cron.

Rolling the workload after rotation is unnecessary if the app reloads
secrets on file change. Mount ExternalSecret outputs as files (not env
vars) and use a file watcher in the app, or Reloader to bounce Pods on
a secret revision change.

```yaml
metadata:
  annotations:
    reloader.stakater.com/auto: "true"
```

## Lifecycle on tenant delete

Offboarding must remove secrets, not just the Kubernetes Secret.

1. Revoke Vault or IAM policy that references `tenants/<slug>/*`.
2. Delete secrets at source (Vault KV delete, AWS
   `DeleteSecret --recovery-window-in-days 7`).
3. Delete the `ExternalSecret` and `Secret` from the namespace
   (handled automatically when the namespace is deleted).
4. Audit-log the deletion with actor, time, and secret ARNs.
5. Confirm backups of the secrets store do not retain plaintext
   beyond contracted retention.

## Break-glass access

- Separate Vault path `break-glass/tenants/<slug>` with a short-lived
  policy that is off by default.
- Enable via a two-person rule (PR + approver) that flips an
  OIDC group membership.
- Auto-expire after 4 hours.
- Every use pages on-call and writes an audit event.

## Anti-patterns

- Shared Secret across tenant namespaces — one compromise is a
  platform compromise.
- `imagePullSecrets` with a single registry token copied per namespace
  instead of IRSA-scoped pull credentials.
- Secrets baked into ConfigMaps because "ConfigMaps sync nicely" —
  ConfigMaps are not secrets; they are not encrypted at rest by
  default.
- No rotation story — rotation is the difference between a 2024
  incident and a 2025 breach.
- Using `stringData` in Git-committed Secret manifests — even if
  sealed-secrets is used later, the plaintext leaks from git history.
