# Secret Handling Plan

Parent: [../SKILL.md](../SKILL.md).

The secret handling plan is one of the four baseline artifacts produced by `vibe-security-skill`. Consumed by `deployment-release-engineering` (rotation choreography), `cicd-devsecops` (pipeline scanning and vault integration), and `observability-monitoring` (audit-log field specification).

## What the plan must specify

A complete secret handling plan names, for every distinct secret class in the system:

| Field | Example |
|---|---|
| Secret class | Stripe live key; database app user; JWT signing key |
| Storage | AWS Secrets Manager path / HashiCorp Vault mount / sealed-secret manifest |
| Access | service identity (IAM role, SPIFFE id) that may read |
| Rotation cadence | static ≤ 90d; dynamic 1h–24h |
| Rotation owner | team accountable |
| Rotation procedure | reference the runbook |
| Audit path | log stream that records every read |
| Compromise response | steps, RTO target, communications owner |

## Storage rules

- Runtime only. Never in code, never in git, never in Docker images, never in build artifacts.
- Vault / Secrets Manager per environment. One source of truth per secret, pulled at startup or via sidecar.
- Kubernetes: `external-secrets` or CSI driver, not committed `Secret` manifests.
- Developer machines: `.env.local` ignored by git; production secrets never on developer laptops.

## Access rules

- Service identity → secret path. No long-lived API tokens for service accounts.
- Human access to production secrets: break-glass only, ticketed, time-bound, auto-revoked.
- Least privilege: one secret path per service; no wildcard access.

## Rotation cadence

```text
Long-lived cloud API key (AWS, Stripe, SendGrid)         -> 90 days + immediate on suspected compromise
Internal service-to-service shared secret                 -> 30 days static; prefer mTLS or workload identity
Database credential (static)                              -> 90 days
Database credential (dynamic, via Vault)                  -> 1h–24h; no rotation burden
OAuth client secret                                       -> annually + on personnel change
JWT signing key                                           -> 90-day overlap rotation (kid in header)
Webhook signing secret                                    -> 90 days; per-integration
TLS private key                                           -> certificate lifetime (ACME 90d automated)
Encryption key (data-at-rest)                             -> KMS managed; envelope encryption; rotate DEK on schedule
```

## Rotation procedure (template)

For each static secret:

1. Create the new secret value in Vault.
2. Update the consuming service to accept either old or new value (dual-read window).
3. Roll services (restart / redeploy) to pick up the new value.
4. Confirm all instances use the new value (metric / log check).
5. Revoke the old value.
6. Record rotation in the audit log.

For JWT signing keys specifically:

1. Generate new key pair; publish new public key with new `kid`.
2. Add new `kid` to the signer's key set; keep old `kid` still listed for verification.
3. Signer starts issuing with the new `kid`.
4. Wait max token TTL (e.g. 24h) for old tokens to expire.
5. Remove the old `kid` from verification.

## Audit

Every secret read is logged with:

- caller identity (service or human)
- secret path
- timestamp
- request id
- action (read, rotate, revoke)

Alert when:

- human reads a production secret outside a break-glass window
- a service identity reads a secret it has never read before
- rotation is overdue past the cadence

## Logging guardrails

- Structured logger with a redactor that masks fields matching `password|secret|token|key|authorization|cookie`.
- Payload-body logging is default-off in production; enabled behind a ticketed flag for short windows only.
- Error middleware sanitises exception messages before returning to clients.

## Secret-in-repo response

If a secret is committed to git, or ends up in a build artifact, a tag, or a Docker layer:

1. Treat the secret as compromised. Do not try to "just remove the commit."
2. Rotate the secret in the source of truth.
3. Revoke the old value.
4. Force-push or BFG-rewrite to scrub the value from git history (history rewrite is a belt-and-braces measure; rotation is the real fix).
5. Audit downstream systems for use of the exposed value.
6. Post-incident: add the scanner rule that would have caught it in CI.

## Pipeline scanning

CI must fail on detection of:

- high-entropy strings matching known key patterns (`sk_live_`, `AKIA`, `xoxb-`, `ghp_`, etc.)
- private key headers (`-----BEGIN PRIVATE KEY-----`, SSH keys)
- `.env` files containing values other than placeholders

Use `gitleaks`, `trufflehog`, or the platform's native scanner. See `cicd-devsecops` for pipeline integration.

## Compromise response

Detection → rotation targets:

| Compromise | Response time |
|---|---|
| Live payment key exposed | minutes (rotate via provider, revoke) |
| Production database password exposed | minutes (rotate, confirm redeploy) |
| Developer laptop lost with cached tokens | hours (revoke all tokens, reissue) |
| Signing key exposed | immediate key-set rotation + force token reissue |
| CI secret exposed | hours (rotate, audit pipeline access) |

Each compromise must also produce:

- a timeline-style incident note (who, when, what)
- a change to prevent recurrence (scanner rule, policy, training)
- customer communication if user data was at risk

## Common failures

- Plan says "use Vault" but never specifies rotation cadence → secrets live for years.
- Rotation happens but nobody rolls the services → new secret is correct, old one still valid and leaked.
- JWT key rotation without `kid` overlap → all live sessions fail.
- Audit log exists but nobody alerts on it → compromise goes undetected.
- Break-glass human access has no expiry → tokens live forever.
