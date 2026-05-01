# Secrets — External Secrets, Vault, SOPS, Sealed Secrets

A `Secret` manifest is base64, not encryption. Putting one in Git leaks the secret. This reference covers the four patterns that actually work.

## Pattern selection

```text
Cloud-managed workloads + cloud secret store   -> External Secrets Operator + AWS SM / GCP SM / Azure KV
Multi-cloud / hybrid / on-prem with HSM needs  -> External Secrets Operator + HashiCorp Vault
GitOps-first, no external KMS wanted           -> SOPS + age + Argo/Flux plugin
Simple GitOps, no operator install             -> Sealed Secrets (Bitnami)
CI-injected secrets, short-lived, no cluster   -> OIDC workload identity (no secret at all)
```

Default: **External Secrets Operator + cloud secret manager**. It wins on rotation, audit, and centralisation.

## External Secrets Operator (ESO)

Operator that syncs secrets from external stores into native Kubernetes `Secret` objects. Applications keep reading `Secret` as usual; operator handles the fetch and refresh.

### Install

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm upgrade --install external-secrets external-secrets/external-secrets \
  -n external-secrets --create-namespace \
  --set installCRDs=true \
  --set webhook.port=9443
```

### AWS Secrets Manager with IRSA

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata: { name: aws-sm }
spec:
  provider:
    aws:
      service: SecretsManager
      region: eu-west-1
      auth:
        jwt:
          serviceAccountRef:
            name: eso-sa
            namespace: external-secrets
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: api-db, namespace: production }
spec:
  refreshInterval: 1h                   # poll the store hourly
  secretStoreRef: { name: aws-sm, kind: ClusterSecretStore }
  target:
    name: api-db                         # Kubernetes Secret name
    creationPolicy: Owner
    template:
      type: Opaque
      data:
        DATABASE_URL: "postgres://{{ .username }}:{{ .password }}@{{ .host }}:5432/{{ .dbname }}?sslmode=require"
  data:
    - secretKey: username
      remoteRef: { key: prod/api/db, property: username }
    - secretKey: password
      remoteRef: { key: prod/api/db, property: password }
    - secretKey: host
      remoteRef: { key: prod/api/db, property: host }
    - secretKey: dbname
      remoteRef: { key: prod/api/db, property: dbname }
```

### HashiCorp Vault with Kubernetes auth

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata: { name: vault }
spec:
  provider:
    vault:
      server: https://vault.internal:8200
      path: kv
      version: v2
      auth:
        kubernetes:
          mountPath: kubernetes
          role: eso-reader
          serviceAccountRef:
            name: eso-sa
            namespace: external-secrets
```

Vault server side:

```bash
vault auth enable -path=kubernetes kubernetes
vault write auth/kubernetes/config \
  token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  kubernetes_host="https://kubernetes.default.svc" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

vault policy write eso-reader - <<EOF
path "kv/data/prod/*" { capabilities = ["read"] }
EOF

vault write auth/kubernetes/role/eso-reader \
  bound_service_account_names=eso-sa \
  bound_service_account_namespaces=external-secrets \
  policies=eso-reader ttl=1h
```

### GCP Secret Manager with Workload Identity

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata: { name: gcp-sm }
spec:
  provider:
    gcpsm:
      projectID: my-project
      auth:
        workloadIdentity:
          clusterLocation: europe-west1
          clusterName: prod
          serviceAccountRef:
            name: eso-sa
            namespace: external-secrets
```

### PushSecret — for round-tripping

ESO can push values from cluster secrets up to the external store (useful for bootstrapping generated credentials):

```yaml
apiVersion: external-secrets.io/v1alpha1
kind: PushSecret
metadata: { name: api-generated, namespace: production }
spec:
  secretStoreRefs: [{ name: aws-sm, kind: ClusterSecretStore }]
  selector:
    secret: { name: api-generated }
  data:
    - match:
        secretKey: token
        remoteRef: { remoteKey: prod/api/generated-token }
```

## SOPS + age — GitOps-friendly encryption

Encrypted manifests live in Git. Decryption happens in-cluster via a controller (ArgoCD plugin or Flux `SopsProvider`).

### Generate key and encrypt

```bash
age-keygen -o sops-age.key
export SOPS_AGE_RECIPIENTS=$(grep "# public key" sops-age.key | cut -d: -f2 | tr -d ' ')

# Encrypt only the data/stringData fields
sops --encrypt --age $SOPS_AGE_RECIPIENTS \
     --encrypted-regex '^(data|stringData)$' \
     secret-plain.yaml > secret.enc.yaml
```

### .sops.yaml at repo root

```yaml
creation_rules:
  - path_regex: k8s/.*secret.*\.ya?ml$
    encrypted_regex: '^(data|stringData)$'
    age: age1abcd...public...key
```

### Flux decryption

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: app, namespace: flux-system }
spec:
  decryption:
    provider: sops
    secretRef: { name: sops-age }        # contains the age private key
  path: ./k8s/production
  sourceRef: { kind: GitRepository, name: main }
```

Rotation: generate a new age key, re-encrypt with `sops updatekeys`, commit.

## Sealed Secrets — encrypted manifests, no KMS

The `sealed-secrets-controller` runs in the cluster with a keypair. You encrypt with the public key and commit the `SealedSecret` to Git; the controller decrypts and creates a `Secret`.

```bash
# Install controller
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm upgrade --install sealed-secrets sealed-secrets/sealed-secrets \
  -n kube-system --set-string fullnameOverride=sealed-secrets-controller

# Encrypt
kubectl create secret generic api-db \
  --from-literal=password='s3cret' --dry-run=client -o yaml \
  | kubeseal --controller-namespace kube-system -o yaml > sealed.yaml
git add sealed.yaml
```

Gotchas:
- Sealed Secrets are scoped to namespace+name by default. Moving secrets across namespaces requires `--scope` flag.
- Key rotation is the controller's job; backup the master key or you cannot decrypt old SealedSecrets after restore.
- No audit trail beyond Git history — unlike Vault/SM you cannot see *who* read the secret.

## Rotation patterns

### Static long-lived secret

- Rotate quarterly in Vault/SM.
- ESO `refreshInterval: 1h` picks up new value.
- App must reload — either via rolling restart (ESO can trigger via `reloader` controller) or file-watcher.

### Dynamic secrets (Vault database secrets engine)

Vault issues a short-lived DB credential per workload instance:

```bash
vault write database/config/postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readonly" \
  connection_url="postgresql://{{username}}:{{password}}@db:5432/app"

vault write database/roles/readonly \
  db_name=postgres \
  creation_statements="CREATE ROLE \"{{name}}\" ..." \
  default_ttl="1h" max_ttl="24h"
```

ESO `ExternalSecret` with `refreshInterval: 30m` pulls a new credential; pair with `reloader` annotation:

```yaml
metadata:
  annotations:
    reloader.stakater.com/auto: "true"   # restart Pods when secret changes
```

### Workload identity (the real answer)

Whenever possible, eliminate the secret:

- AWS: IRSA → IAM role assumed by ServiceAccount.
- GCP: Workload Identity → GSA bound to KSA.
- Azure: Workload Identity Federation → managed identity.
- Vault: Kubernetes auth with short TTL tokens (see above).

No static credential in `Secret` = no rotation problem.

## Mount as file, not env var

```yaml
spec:
  template:
    spec:
      containers:
        - name: app
          volumeMounts:
            - name: secrets
              mountPath: /etc/secrets
              readOnly: true
      volumes:
        - name: secrets
          secret:
            secretName: api-db
            defaultMode: 0400
```

Why:
- Env vars leak via `/proc/<pid>/environ`, crash dumps, `ps`, log statements.
- File mounts support atomic updates when the Secret changes (kubelet projects new symlink).
- `defaultMode: 0400` restricts to the container user.

## Anti-patterns

- Committing plain `Secret` YAML to Git (base64 is not encryption).
- `envFrom: secretRef:` in a container with `/debug` or error pages that dump env.
- Sharing one ServiceAccount across workloads that access different secrets.
- Using the default KSA token for Vault auth.
- No `automountServiceAccountToken: false` on workloads that do not need the token.
- Rotating a secret but never restarting the Pod (stale value in memory).
- Storing Vault unseal keys in the same vault infrastructure.

## Review checklist

- [ ] Zero `Secret` YAMLs with plaintext data in Git
- [ ] ESO `ClusterSecretStore` uses workload identity (IRSA/WIF/K8s auth), not a static API key
- [ ] `ExternalSecret.refreshInterval` set appropriately (1h typical)
- [ ] Secrets mounted as files, not env vars
- [ ] Reloader or app-native file watcher picks up rotation
- [ ] SOPS key / Sealed Secrets master key backed up off-cluster
- [ ] Audit logs enabled on Vault / Secrets Manager
- [ ] Dynamic secrets used for DB credentials where supported
- [ ] `automountServiceAccountToken: false` on workloads without K8s API needs
