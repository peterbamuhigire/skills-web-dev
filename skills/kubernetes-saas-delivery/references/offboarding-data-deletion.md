# Offboarding and Data Deletion Runbook

Step-by-step tenant offboarding for Kubernetes-hosted SaaS. Read after
`SKILL.md` and `tenant-onboarding-automation.md`. Cross-reference
`multi-tenant-saas-architecture` for auth and data-layer scope, and
`uganda-dppa-compliance` or your regional equivalent for legal
specifics.

## Why a runbook

Offboarding failures create:

- Orphaned resources that cost money forever.
- Retained personal data in violation of GDPR, DPPA, and similar laws.
- Compromised audit trails (nobody knows what was deleted or when).
- Security risk from stale credentials.

A deletion process must be reviewable, repeatable, and verifiable.

## Preconditions

- Written deletion request captured with actor, tenant, reason,
  timestamp.
- Contractual retention terms retrieved (some contracts require
  6-12 months retention; some require deletion within 30 days).
- Legal hold check: no active litigation that prevents deletion.
- Break-glass read access available to Support for 48 hours after
  offboarding in case the customer reverses.

## Step-by-step runbook

### 1. Mark tenant offboarding

```sql
UPDATE tenants
SET    state = 'offboarding',
       offboarding_requested_at = now(),
       offboarding_requested_by = :actor_id,
       offboarding_reason = :reason
WHERE  id = :tenant_id;
```

Emit `tenant.offboarding_requested` event on the bus. Control-plane
schedules a verification window (24-72 hours) before hard deletion.

### 2. Suspend ingress

Block all new traffic to the tenant. Use a NetworkPolicy flip plus an
ingress rule that returns 410 Gone:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: deny-all, namespace: tenant-acme }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: acme-gone
  namespace: tenant-acme
  annotations:
    nginx.ingress.kubernetes.io/permanent-redirect: "https://status.example.com/offboarded"
    nginx.ingress.kubernetes.io/permanent-redirect-code: "410"
spec:
  rules:
    - host: acme.app.example.com
```

### 3. Final backup to off-cluster storage

Export tenant data per retention contract. Store encrypted in a
separate bucket with object-lock matching the retention period.

```bash
pg_dump -Fc \
  --dbname "$TENANT_DB_URL" \
  --no-owner --no-privileges \
  | gpg --encrypt --recipient compliance@example.com \
  | aws s3 cp - "s3://backups-retention/tenants/acme/final.dump.gpg" \
    --sse aws:kms --sse-kms-key-id "$KMS_KEY_ID" \
    --metadata "tenant=acme,created=$(date -u +%FT%TZ),retention-until=2027-04-15"
```

Record the object URL, checksum, size, and retention-until date in the
audit log.

### 4. Delete tenant namespace

The namespace delete cascades to Pods, Services, Secrets, PVCs, and
ConfigMaps. PersistentVolumes with `Retain` reclaim policy survive on
purpose — clean them up in step 5.

```bash
kubectl delete namespace tenant-acme --wait=true --timeout=10m
```

If the namespace is managed by ArgoCD, removing the tenant directory
in Git is the canonical action. ArgoCD prunes the Application, which
deletes the namespace.

### 5. Reclaim storage

```bash
# Identify PVs that were bound to the tenant
kubectl get pv -o json \
  | jq -r '.items[] | select(.spec.claimRef.namespace=="tenant-acme") | .metadata.name' \
  | xargs -r kubectl delete pv
```

For cloud disks with `Retain` policy, schedule explicit deletion after
the retention window closes. Tag snapshots accordingly.

### 6. Git repo cleanup

```bash
git rm -r tenants/acme
git commit -m "chore(tenant): offboard acme per request 2026-04-15"
```

Verify ArgoCD prunes the Application. Confirm no lingering Applications
reference `tenant-acme`.

### 7. Cloud secret cleanup

Vault:

```bash
vault kv delete -mount=kv tenants/acme/database-url
vault kv delete -mount=kv tenants/acme/stripe-webhook-secret
vault kv metadata delete -mount=kv tenants/acme/database-url
vault policy delete tenant-acme
```

AWS Secrets Manager:

```bash
for arn in $(aws secretsmanager list-secrets \
  --filters Key=tag-value,Values=acme \
  --query 'SecretList[].ARN' --output text); do
  aws secretsmanager delete-secret --secret-id "$arn" \
    --recovery-window-in-days 7
done
aws iam delete-role-policy --role-name tenant-acme-sa --policy-name tenant-access
aws iam delete-role --role-name tenant-acme-sa
```

### 8. Observability cleanup

- Grafana: delete the `Tenants/acme` folder and all dashboards under
  it. Revoke the `acme-admins` team.
- Alertmanager: remove any tenant-specific routes or silences.
- Loki: drop the per-tenant label namespace or let retention age it
  out (cheapest).
- Kubecost: rows for the namespace will age out naturally.

### 9. Billing and control-plane cleanup

- Cancel the Stripe subscription; issue any pro-rated refund per
  policy.
- Archive the tenant in the control-plane DB rather than hard delete,
  so audit history survives. Hard delete personal data columns
  (email, names) to satisfy data-minimisation rules.

```sql
UPDATE tenants
SET    state = 'offboarded',
       offboarded_at = now(),
       contact_email = NULL,
       contact_name  = NULL
WHERE  id = :tenant_id;
```

### 10. Audit log

Write a single consolidated audit record with:

- Tenant id, slug, tier, signup date.
- Request actor, reason, timestamps for each step.
- Artefacts deleted (resource types and counts).
- Backup ARN and retention-until date.
- Cloud secret ARNs deleted.
- Operator who ran the procedure; reviewer who approved.
- Verification hash (SHA-256 over the record JSON).

Store in append-only storage (CloudTrail, S3 Object Lock, or a
purpose-built audit store). Retain for at least the longer of
contract term plus 1 year and legal minimum (frequently 7 years).

## Verification checks

Run 48 hours after step 4, and 30 days after step 3:

- [ ] No namespace matching `tenant-<slug>` exists.
- [ ] No ArgoCD Application matches the tenant label.
- [ ] No PV references the deleted namespace.
- [ ] Vault path `tenants/<slug>/*` returns 404.
- [ ] Cloud secret search by tag returns empty.
- [ ] Loki query `{tenant="<slug>"}` returns nothing (after retention).
- [ ] kubecost namespace cost is zero for the last 7 days.
- [ ] Stripe subscription status is `canceled`.

Automate these checks in a scheduled job. File a ticket if any step
fails.

## GDPR / DPIA / regional notes

- Right to erasure (GDPR Art. 17): respond within 30 days; document
  proportionality of retained backups (legal basis: contract, legal
  obligation).
- Uganda DPPA 2019: deletion must be verifiable; logs kept for at
  least 5 years. See `uganda-dppa-compliance` skill for the annex
  template.
- HIPAA (if applicable): PHI in backups must be encrypted with keys
  under your control; retention aligns with covered-entity agreement.
- Data residency: confirm the retention bucket is in the contracted
  region; cross-region replication must be disabled for deleted
  tenants.

## Anti-patterns

- Deleting the namespace without taking the backup first.
- Leaving Vault paths and IAM roles in place "just in case".
- Purging audit logs along with the tenant — retention of the audit
  is the point.
- Offboarding by hand without a runbook — the first step missed is
  the one that ends in the breach report.
- Treating the namespace delete as the end of the process — cloud
  resources, secrets, observability, and billing all outlive the
  namespace.
