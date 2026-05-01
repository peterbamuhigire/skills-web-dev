# Staging / Production Environment Management

Environment parity is the foundation of safe promotion. Drift between staging and production produces "works on my machine" outages at deploy time. The reliable rule: build the artifact once; deploy it many times by changing configuration alone.

## Four Axes of Separation

| Axis | Staging | Production |
|------|---------|------------|
| Data | Anonymised production-like fixture; never live PII. Restore monthly from a sanitised production snapshot. | Live data, encrypted at rest (KMS or LUKS), backed up with tested restore. |
| Secrets | Separate Vault path (`secret/staging/*`); non-production keys only; rotation optional. | Vault production path (`secret/prod/*`); rotation enforced; access via short-lived tokens. |
| Traffic | Synthetic + internal users only. Block external ingress at the edge. | Real users; protected by WAF + rate limits + bot mitigation. |
| Observability | Same instrumentation as prod; lower retention (7–14 days); alerts page no one. | Full retention (30–90 days); on-call paging on SLO-linked alerts. |

## Build Once, Deploy Many

The same image SHA that passed staging is the image that runs in production. Configuration differs across environments (env vars, secrets, replica count, scale targets); the artifact does not. This is the foundational continuous-delivery rule: the binary you tested is the binary you ship.

Promotion checklist:

- [ ] Image SHA recorded in the staging deploy log.
- [ ] Smoke tests passed against staging.
- [ ] Schema migration is backwards compatible across both versions.
- [ ] Same image SHA referenced in the production deploy manifest.
- [ ] Deploy record signed with who, what, when, and the artifact digest.

## Configuration Layering

Use a three-layer model:

1. Image-baked defaults — safe values that work in any environment.
2. Environment configuration — env vars, ConfigMaps, or `.env` rendered by the deploy pipeline from Vault.
3. Runtime overrides — feature flags and dynamic config served by a control-plane service.

Never bake environment-specific URLs, hostnames, or credentials into the image.

## Data Hygiene

- Refresh staging from a sanitised production dump on a fixed cadence (weekly or monthly).
- Sanitisation strips PII columns (email, phone, name, address) and resets payment tokens.
- Retain the sanitisation script in the repo; review changes through the standard PR process.
- Never copy production data into developer laptops.

## Promotion Flow

```text
feature branch  -->  PR + checks  -->  main  -->  staging deploy  -->  smoke + soak  -->  production deploy (same SHA)
```

Each arrow is automated. Manual gates exist only at the production deploy step, where required reviewers approve the GitHub Actions environment.
