---
name: saas-managed-visual-assets
description: Use when implementing or reviewing Super Admin or tenant-scoped managed visual assets—background image pools, light/dark logos, or favicons—with secure upload, preview, ordering, activation, replacement, quotas, and audit evidence.
metadata:
  portable: true
  category: saas
  compatible_with:
  - claude-code
  - codex
---

# SaaS Managed Visual Assets

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

This skill defines the platform contract for managed authentication backgrounds, surface-aware
logos, and favicons. It owns scope, authorization, lifecycle, APIs, storage boundaries, and
release evidence. Use `image-compression` for codec and quality mechanics and the external
design-system engine for visual composition.

<!-- dual-compat-start -->
## Use When

- Building a Super Admin or tenant-admin visual-asset manager.
- Adding a managed pool of sign-in, registration, recovery, or tenant-entry backgrounds.
- Managing one light-surface logo, one dark-surface logo, or one favicon per scope.
- Reviewing upload, activation, ordering, replacement, deletion, fallback, or audit behaviour.
- Standardising the capability across several SaaS products or technology stacks.

## Do Not Use When

- Optimising ordinary content images without an administrative lifecycle; use
  `image-compression`.
- Designing the appearance of the authentication page; route additionally to
  `design-system-skills/webapp-gui-design`.
- Managing arbitrary documents or user attachments; use the applicable upload/storage and
  security skills.

## Required Inputs

| Input | Source | Required | Purpose |
|---|---|---|---|
| Platform-versus-tenant scope and fallback policy | Product/architecture contract | yes | Prevent cross-scope leakage and ambiguous precedence |
| Actor, role, permission, and CSRF/session model | Identity/security contract | yes | Authorize every mutation server-side |
| Existing image pipeline and storage topology | Repository/infrastructure | yes | Reuse safe primitives and preserve deployment constraints |
| Visual slots, limits, dimensions, and quality targets | Product/design contract | yes | Make validation deterministic |
| Audit, retention, and rollback requirements | Compliance/operations | yes | Define evidence and recovery |

## Workflow

1. Inspect the repository's tenant context, RBAC, CSRF, upload, storage, audit, and public asset
   delivery paths. Do not invent parallel infrastructure before checking existing services.
2. Write the scope and fallback contract. Derive platform/tenant authority from the authenticated
   server context; never trust a client-supplied tenant identifier.
3. Define the asset model and invariants using
   `references/asset-domain-and-api-contract.md`.
4. Threat-model ingest, decoding, storage, public delivery, replacement, and deletion. Apply
   `image-compression` and `references/secure-image-pipeline-and-storage.md`.
5. Implement list, upload, preview, activate/deactivate, reorder, replace, delete, and public
   manifest/read operations behind least-privilege permissions and CSRF protection.
6. Make quota checks and order/activation changes concurrency-safe. Preserve the old active asset
   until a replacement has completed canonical processing and metadata commit.
7. Emit actor/scope/before/after/result audit events without original filenames, secrets, or raw
   image content. Add operational metrics and orphan cleanup.
8. Exercise the lifecycle and failure matrix in
   `references/asset-lifecycle-and-test-matrix.md`; record release and rollback evidence.

## Decision Rules

| Condition | Choice | Wrong-choice failure |
|---|---|---|
| Platform owns a default and tenant may customise | Tenant override with explicit platform fallback | Copying platform files per tenant creates drift and waste |
| Upload would become background 21 in one scope | Reject before commit under a lock/transaction | Concurrent requests can exceed the exact limit |
| Replacement processing fails | Keep the current asset and discard/quarantine the candidate | Broken branding becomes public |
| Asset is served to unauthenticated auth pages | Resolve an opaque public identifier through a controlled endpoint/manifest | Direct storage paths expose internals and bypass policy |
| Alpha is meaningful for logo/favicon | Canonical PNG or alpha-capable WebP | JPEG conversion produces boxes or destroys the mark |
| The visual is a photographic background | Canonical WebP/JPEG within the delivery budget | Lossless output wastes bandwidth with no visible gain |

## Quality Standards

- Exactly 20 stored backgrounds are permitted per scope, including inactive backgrounds.
- Exactly one light-surface logo, one dark-surface logo, and one favicon slot exist per scope.
- The active background pool contains only successfully processed, authorized assets; selection
  is randomized once per auth journey and remains stable through errors and recovery steps.
- The server validates byte size, detected content type, decoder success, pixel count, dimensions,
  and output size, then re-encodes to a canonical raster format before durable storage.
- Client validation and compression are usability/performance optimizations only, never security
  authority.
- Storage keys are cryptographically random and unrelated to original names. Originals and
  canonical files stay private unless a controlled delivery policy explicitly publishes them.
- All mutations are RBAC-protected, CSRF-protected where browser sessions are used, auditable,
  tenant/platform scoped, transactional or compensating, and safe under retries/concurrency.
- Public responses set a correct content type, `X-Content-Type-Options: nosniff`, bounded caching,
  and safe bundled fallbacks.

## Capability and Permission Contract

Read and search are required. Editing and local execution are allowed only when implementation is
authorized. Database/storage mutation must remain inside the named development/test scope;
production writes, bucket-policy changes, destructive cleanup, or external publication require
separate authority, rollback proof, and least-privilege credentials. Delegation is optional and
must use disjoint write scopes.

## Degraded Mode

If decoder, malware scanning, rendering, storage, or database execution is unavailable, return a
labelled implementation or dry-run with those checks unverified. Keep existing assets live, do not
activate an unverified candidate, and do not call the result production-ready. If tenant authority
or permission semantics are ambiguous, stop mutation and resolve the contract first.

## Anti-Patterns

- Trusting `file.type`, extension, or browser compression. Fix: detect, decode, constrain, and
  re-encode on the server.
- Accepting `tenant_id` from the upload form. Fix: derive scope from authenticated server context.
- Deleting the old logo before processing its replacement. Fix: stage and atomically swap.
- Saving an original filename under a public web root. Fix: use a random private key and a
  controlled read endpoint.
- Counting only active backgrounds toward the 20-item quota. Fix: count every stored background
  in the scope.
- Drag-only ordering and visual-only status. Fix: expose keyboard actions and semantic state.
- Cascading file deletion before metadata commit. Fix: commit the logical change first and use a
  recoverable garbage-collection queue.

## Outputs

| Output | Consumer | Acceptance evidence |
|---|---|---|
| Asset domain and API contract | Backend/frontend/mobile teams | Invariants, permissions, errors, idempotency, and fallback are explicit |
| Threat model and secure processing policy | Security/infrastructure | Ingress, decoder, storage, delivery, and deletion controls are tested |
| Lifecycle and concurrency design | Engineering/operations | Replacement, quota, rollback, orphan, and retry cases pass |
| Admin and public-delivery implementation | Product/QA | Role, scope, accessibility, and representative render checks pass |
| Release evidence bundle | Release owner/audit | Tests, audit samples, metrics, rollback, residual risks, and owners are linked |

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Correctness | Managed visual-asset contract | Markdown/API schema | `docs/platform/managed-visual-assets.md` |
| Security | Image ingest threat model and policy | Threat model + test evidence | `docs/security/visual-assets.md` |
| Correctness | Lifecycle and concurrency test record | Test matrix/results | `docs/testing/visual-assets.md` |
| Operability | Audit/metrics/cleanup runbook | Runbook | `docs/runbooks/visual-assets.md` |

## References

- `references/asset-domain-and-api-contract.md` — load when defining scope, invariants, API
  operations, errors, or fallback precedence.
- `references/secure-image-pipeline-and-storage.md` — load for ingress, canonicalization, private
  storage, controlled delivery, and deletion.
- `references/asset-lifecycle-and-test-matrix.md` — load for replacement, concurrency, cleanup,
  rollback, telemetry, and verification.
- `examples/managed-visual-assets-worked.md` — end-to-end platform/tenant example.
- Companion skills: `image-compression`, `multi-tenant-saas-architecture`,
  `saas-admin-backoffice-tooling`, `vibe-security-skill`, `advanced-testing-strategy`, and
  `deployment-release-engineering`.
<!-- dual-compat-end -->
