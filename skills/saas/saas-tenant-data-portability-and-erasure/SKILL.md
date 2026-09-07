---
name: saas-tenant-data-portability-and-erasure
description: Use when designing verified tenant data export, retention, erasure, backup handling, audit evidence, or privacy-law portability workflows.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Tenant Data Portability and Erasure
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.


## Required Inputs

| Input | Required | Use |
|---|---|---|
| Tenant, product, and lifecycle scope | yes | Bound the SaaS decision |
| Current architecture, plans, policies, and constraints | yes | Preserve enforceable behaviour |
| Production data or verified evidence | conditional | Validate thresholds and migrations |

## Capability and permission contract

Default to read-only analysis. Change configuration, billing, identity, tenant data, infrastructure, or customer communications only with explicit authority, least-privilege credentials, tenant scope, rollback, and auditable approval. Never expose secrets or cross tenant boundaries.

## Degraded mode

If production access, policy, telemetry, or authoritative records are unavailable, produce a labelled design or dry-run plan. Do not claim deployment, reconciliation, deletion, delivery, or measured outcomes; list missing evidence and verification.

## Decision rules

| Condition | Action | Stop condition |
|---|---|---|
| Tenant isolation, money, identity, or deletion is affected | Require approval and rollback evidence | Scope or authority is ambiguous |
| Evidence supports a reversible change | Stage, test, and record it | Acceptance checks fail |
| Only partial context is available | Return assumptions and validation | A production claim cannot be verified |

## Domain Anti-Patterns

- Applying one tenant's policy or data to another. Fix: enforce tenant scope at every boundary.
- Mutating production from an advisory request. Fix: remain read-only until authority is explicit.
- Inventing limits, prices, metrics, or compliance claims. Fix: use authoritative records or mark them unresolved.
- Shipping without rollback and audit evidence. Fix: stage and retain before/after proof.
- Treating a missing dependency as successful. Fix: name the blocked verification.


<!-- dual-compat-start -->
## Use When

- Implementing the data-portability (export) and erasure (delete) workflows mandated by GDPR Article 20 / 17, POPIA, CCPA, Uganda DPPA, Kenya DPA.
- Designing the cascade that purges a tenant's data through every store the SaaS uses — primary DB, search index, file storage, warehouse, caches, backups, ESP suppression list, CRM, analytics, third-party processors.
- Handling user-level vs tenant-level erasure (a user leaving a tenant vs a tenant leaving the platform).
- Designing requester verification so an attacker can't erase a competitor's tenant.
- Designing the retention policy and the documented backup window (what survives erasure and for how long).

## Do Not Use When

- The task is general data classification — use compliance audit work in `vibe-security-skill` / `web-app-security-audit`.
- The task is tenant lifecycle state machine — use `saas-control-plane-engineering`.
- The task is region-specific compliance content — use `uganda-dppa-compliance` for Ugandan specifics.

## Required Inputs

- Tenant lifecycle states (`saas-control-plane-engineering`).
- Map of every data store the SaaS uses (primary DBs, search, object storage, warehouse, CRM, ESP, analytics, third-party processors).
- Regulatory profile (GDPR? POPIA? Uganda DPPA? CCPA? sector-specific HIPAA?).
- Retention obligations (audit log 7 years; financial 10 years in most jurisdictions; backups 30 days).

## Workflow

1. Read this `SKILL.md`.
2. Inventory every data store (§2).
3. Map every store to user-level + tenant-level erasure capability (§3).
4. Design the export workflow (§4).
5. Design the erasure workflow (§5).
6. Design requester verification (§6) — protect against malicious erasure.
7. Document retention exceptions (§7) — what survives, why, for how long.
8. Wire into the back-office (§8).
9. Apply anti-patterns (§9).

## Quality Standards

- Export delivered within 30 days (GDPR ceiling); aim for hours-to-days.
- Erasure cascades through every store; documented retention exceptions only.
- Backups handled honestly — document the retention window after which erased data is also purged from backups; don't claim instant deletion of backups when it's not true.
- Every export and erasure logged in the audit log with actor, target, verification trail.
- Requester verification appropriate to risk — primary-admin email confirmation + MFA for tenant-level erasure.

## Anti-Patterns

- "Delete" implemented as `SET deleted_at = NOW()` (soft delete) — fails the regulatory test.
- Forgetting the warehouse — analytics data still contains PII years later.
- Forgetting the ESP suppression list — email still goes out to "deleted" addresses.
- Forgetting backups — claim "deleted" while the customer's PII sits in S3 for 90 days.
- One-click tenant erasure with no verification — competitor / disgruntled user destroys the tenant.
- No audit trail of the erasure itself — cannot prove compliance.

## Outputs

- Data store inventory + erasure capability matrix.
- Export workflow + format spec.
- Erasure workflow + cascade order.
- Requester verification policy.
- Retention exceptions document.
- Customer-facing data-processing addendum (DPA) annex.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Data safety | Data store + erasure capability matrix | Markdown table | `docs/compliance/data-store-erasure-matrix.md` |
| Release evidence | Export workflow spec | Markdown doc + sample export | `docs/compliance/export-workflow.md` |
| Release evidence | Erasure workflow spec | Markdown doc | `docs/compliance/erasure-workflow.md` |
| Data safety | Retention exceptions document | Markdown doc | `docs/compliance/retention-exceptions.md` |

## References

- `references/erasure-cascade.md` — the per-store cascade including backups + warehouse.
- `references/export-format-spec.md` — JSON-LD / CSV export package contents.
- `references/requester-verification.md` — verification strength per request type.
- Companion: `saas-control-plane-engineering`, `saas-admin-backoffice-tooling`, `multi-tenant-saas-architecture`, `uganda-dppa-compliance`, `vibe-security-skill`.

<!-- dual-compat-end -->

## §1 The Two Request Types

| Request type | Initiator | Scope |
|---|---|---|
| **User export / erasure** | Individual user | That user's personal data across tenants where they appear |
| **Tenant export / erasure** | Tenant primary admin | All data for that tenant (organisation-wide) |

A user-level request inside a tenant context (a tenant admin asks for a specific user's data) is a third variant: scope is one user within one tenant.

## §2 Data Store Inventory

For every SaaS, enumerate stores:

| Store | Examples | Erasure mechanic |
|---|---|---|
| **Primary OLTP DB** | MySQL/Postgres tenant data | DELETE with cascade or per-tenant TRUNCATE / drop schema |
| **Search index** | Elasticsearch / Meilisearch / Algolia | Delete by tenant prefix or index |
| **Object storage** | S3 / R2 / GCS / Azure Blob | Delete by per-tenant prefix |
| **Caches** | Redis / Memcached | Flush by tenant key namespace |
| **Message queues** | SQS / Kafka / RabbitMQ | Drain + per-tenant filter; usually short retention |
| **Warehouse** | BigQuery / Snowflake / Redshift | Per-tenant partition delete or pseudonymise |
| **Analytics** | Mixpanel / Amplitude / PostHog / Heap | Vendor delete API; per-distinct-id or per-tenant property |
| **CRM** | Salesforce / HubSpot | API-driven delete; verify cascade |
| **ESP / suppression** | Postmark / SendGrid / Customer.io | API + central suppression-list update |
| **Logs** | CloudWatch / Datadog / Loki | Time-based purge; redact PII; document window |
| **Backups** | RDS snapshots / S3 backups | Retention window; redaction policy on rotation |
| **Audit log** | Internal | **Kept** (regulatory) but PII fields redacted |
| **Third-party processors** | Stripe / Twilio / OpenAI / etc. | Per-vendor delete API; document each |

Every store gets a column: "Per-user delete?" "Per-tenant delete?" "Retention window after request?"

## §3 The Erasure Capability Matrix

Example:
| Store | Per-user delete | Per-tenant delete | Backup retention |
|---|---|---|---|
| MySQL primary | Yes (cascade by user_id) | Yes (cascade by tenant_id) | 30 days |
| Elasticsearch | Yes (delete-by-query) | Yes (drop tenant index) | 7 days |
| S3 documents | Yes (per-key) | Yes (per-tenant prefix) | 30 days (S3 versioning) |
| Redis | Yes (per-user key namespace) | Yes (per-tenant namespace) | None (TTL) |
| Snowflake warehouse | Yes (DELETE on event tables) | Yes (per-tenant partition) | 7 days (Time Travel) |
| Postmark suppression | Yes (per-email API) | n/a | Permanent |
| Stripe Customer | Yes (delete API; PII redacted in retained financial records) | n/a | 7 years (financial) |
| Audit log | PII pseudonymise (email → hash) | n/a | 7 years |

## §4 Export Workflow

**Trigger:** Customer initiates via in-product "Export my data" or tenant admin's "Export tenant data".

**Steps:**
1. Verify requester (§6).
2. Create export job (`exports` table; status `queued`).
3. Worker dumps data:
   - Primary DB tables relevant to the user/tenant → CSV or JSON-Lines.
   - Object storage files → keep folder structure.
   - Settings / preferences → JSON.
   - Audit log subset (the customer's own actions) → JSON.
4. Package as ZIP / TAR.GZ.
5. Upload to a private bucket; generate a signed URL with 7-day expiry.
6. Email the requester (to the verified email on file) with the link.
7. Update job `status = ready`; audit-log the event.

**Format guidance:**
- Use JSON-LD or plain JSON with schemas; CSV for tabular tables; manifest file at the root listing contents.
- Document field meanings in a `README.md` inside the bundle.
- Include a manifest of *what is not included* and why (retained for legal reasons, etc.).

**Time:** GDPR allows 30 days. Aim for hours-to-days; queue for big tenants.

## §5 Erasure Workflow

**Trigger:** customer-initiated OR admin-initiated GDPR erasure request.

**Pre-conditions:**
- Outstanding obligations resolved (paid up, no pending refund, no legal hold).
- Final export offered to the customer (last chance to retrieve data).
- Cool-down window (e.g., 7 days) to prevent rage-deletion regret.

**Cascade order** (top to bottom; failures retried):
1. **Mark tenant `pending_erasure`** — no new data accepted; UI blocks; sessions invalidated.
2. **External processors first** (irreversible, slowest): Stripe Customer marked deleted (PII redacted, financial retained); Twilio/SendGrid/Customer.io contacts deleted; analytics vendor delete API.
3. **Search indexes** — delete-by-tenant.
4. **Caches** — flush per-tenant namespace.
5. **Object storage** — delete per-tenant prefix.
6. **Primary OLTP** — per-tenant DELETE cascade or schema drop.
7. **Warehouse** — DELETE / pseudonymise; rebuild materialised views.
8. **Audit log** — pseudonymise PII fields (email → hash); keep the records for regulatory retention; document this in the retention exceptions.
9. **Backups** — flag for redaction at the next rotation; do not delete the running backup retention window (operational risk).
10. **Tenant record** — `status = deleted`, `deleted_at = NOW()`, identifiers retained as opaque hashes only.
11. **Audit log entry** — `TENANT_ERASURE_COMPLETED` with the cascade outcome JSON.
12. **Email requester** confirming completion + summary of retention exceptions.

**Failure handling:**
- Each step is idempotent and retriable.
- Per-step status persisted (`erasure_runs.step_status`).
- On unrecoverable failure (e.g., Stripe API down), pause; alert ops; resume.

## §6 Requester Verification

| Request type | Verification |
|---|---|
| User export (their own data) | Authenticated session + email confirmation link |
| User erasure | Authenticated session + email confirmation link + 7-day cool-down |
| Tenant export | Primary-admin authenticated + MFA + email confirmation |
| Tenant erasure | Primary-admin authenticated + MFA + email confirmation + 7-day cool-down + cannot have active subscription unless cancelled first |
| Admin-initiated (back-office, e.g., regulatory request) | Super-admin + co-sign + justification + ticket reference |

Reject any request that fails the bar. Audit every successful and failed attempt.

## §7 Retention Exceptions (Document These Publicly)

Some data must be retained even after erasure for legal/financial reasons:

| Data | Retention | Why |
|---|---|---|
| Financial records (invoices, payments) | 7 years (typical), check jurisdiction | Tax law, accounting standards |
| Audit log entries (PII pseudonymised) | 7 years | SOC2, internal control |
| Tax ID, VAT number on invoice | 7 years | Tax law |
| Backup snapshots | 30-90 days (then erased data is also erased from backups) | Operational recovery |
| Court / legal-hold data | As required | Litigation |
| Anti-fraud / abuse signals | 1-2 years pseudonymised | Platform safety |

Document this in the Data Processing Agreement (DPA) annex. Customers signing the DPA accept these retention exceptions. POPIA / GDPR / DPPA all permit these for "legitimate interest" and "legal obligation".

## §8 Back-Office Integration

The back-office console (`saas-admin-backoffice-tooling`) exposes:
- View pending export/erasure jobs.
- Manually trigger export/erasure for a tenant (with co-sign + justification).
- Pause/resume cascade if external processor is failing.
- View completed erasure with cascade outcome.

All require super-admin + audit log + co-sign for tenant-level erasure.

## §9 Anti-Patterns

- **Soft delete only.** `deleted_at = NOW()` does not constitute erasure; PII still in DB.
- **Forgetting the warehouse.** PII lives in analytics tables for years.
- **Forgetting the CRM.** Sales tools have full email/name copies.
- **Forgetting the ESP suppression list.** Old email addresses keep appearing in `email_suppressions` — these are personal data too.
- **Claiming instant backup deletion.** It's almost never true. Document the rolling window.
- **No cool-down.** Mistaken erasure is irreversible; cool-down + final confirmation email is the safety net.
- **No proof of erasure.** Audit log lacks structured outcome JSON; cannot answer "did you erase tenant X completely?"
- **One single "GDPR endpoint" that doesn't actually cascade through all stores.** Big risk during a regulator audit.

## §10 Regional Specifics

- **EU GDPR:** Articles 15 (access), 17 (erasure), 20 (portability). 30-day response.
- **UK GDPR:** Mirror of EU.
- **South Africa POPIA:** Sections 23-24 (access, correction). Information Officer required.
- **Uganda Data Protection and Privacy Act:** See `uganda-dppa-compliance`. NITA-U registration; 30-day response.
- **Kenya Data Protection Act 2019:** Similar framework; Office of the Data Protection Commissioner.
- **Nigeria NDPR:** Compliance audit annually for large processors.
- **US CCPA / CPRA:** California-specific; "do not sell or share" plus deletion right.
- **Brazil LGPD:** Similar to GDPR.

For an African-focused agency: ensure POPIA + Uganda DPPA + Kenya DPA + GDPR are all simultaneously satisfiable. They're broadly compatible; the engineering is the same; the legal text in the DPA changes per region.

## §11 Read Next

- `saas-control-plane-engineering` — the tenant lifecycle this skill integrates with.
- `saas-admin-backoffice-tooling` — the staff workflow.
- `multi-tenant-saas-architecture` — tenant isolation that underpins cascading deletes.
- `uganda-dppa-compliance` — Ugandan specifics.
- `vibe-security-skill` — security review baseline.
- `subscription-billing` — financial-record retention vs erasure tension.

## AI Data Erasure Addendum

The erasure cascade must include all AI-side stores in addition to the transactional and analytic ones:

| AI store | Erasure operation |
|---|---|
| Vector store namespace / partition | drop namespace / delete per-tenant collection |
| Embeddings (raw vectors) | drop with namespace |
| KB source documents | delete from object storage |
| KB chunk metadata rows | DELETE FROM kb_chunks WHERE tenant_id = ? |
| Conversation / chat history | DELETE per-tenant rows; purge S3 transcripts |
| AI audit log rows (`ai_requests`) | per retention; payload S3 keys deleted; envelope-encrypted with tenant KEK — revoke KEK |
| AI request payloads in S3 | delete prefix `ai-audit/<tenant_id>/...` |
| Fine-tunes / adapters | delete tenant-specific adapters; do NOT delete shared base |
| Eval datasets (per-tenant goldens) | delete per-tenant rows |
| Retrieval cache | `SCAN MATCH t<tenant_id>:*` and delete |
| Prompt pins / overrides | DELETE from tenant_prompt_pins |
| AI consents | DELETE from tenant_ai_consents |
| AI cost / usage rows | retained per finance policy; anonymise tenant_id after legal retention |

Per-tenant **KEK revocation** is the strongest erasure for encrypted at-rest data — without the key, the data is unreadable.

Cross-references:
- `ai-tenant-isolation-patterns` — BYOK / KEK strategy.
- `ai-rag-multi-tenant` — KB erasure cascade.
- `ai-on-saas-architecture` — AI audit log retention.
- `ai-observability-and-debugging` — trace retention.

---

## Agent-Memory Erasure Proof (Enhancement)

For tenants whose erasure includes agent-derived memory (working, episodic, semantic, vectors, fine-tune corpora, uploads, derivatives), the agent-memory leg is delegated to **`ai-agent-memory-erasure-proof`**. That skill runs the 9-step cascade, then runs **independent verification probes** (separate code path) to assert residue=0 across every tier, then emits a **signed proof-of-erasure pack** (manifest + step records + verification + subprocessor receipts + audit-log redaction record + DPO signature).

This skill's orchestrator invokes the agent-memory leg as one of its tier coordinators; the produced pack is referenced from the tenant erasure response and retained as compliance evidence for ≥6 years.

Audit-log entries about the tenant / subject are **redacted, not deleted** — see `ai-agent-audit-log-integrity`. Deleting log rows destroys the evidence that the erasure happened.

Cross-links: `ai-agent-memory-erasure-proof`, `ai-agent-audit-log-integrity`, `ai-agent-soc2-controls` (C1.2, P5), `ai-agent-hipaa-security-controls`, `uganda-dppa-compliance`.
