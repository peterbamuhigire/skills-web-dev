---
name: saas-entitlements-and-plan-gating
description: Use when designing SaaS entitlements, plan limits, gate placement, tenant overrides, upgrade discovery, or runtime permission resolution.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Entitlements and Plan Gating
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

- Designing the runtime that answers "what is this tenant allowed to do?" — every gated feature, every limit-checked action, every plan-tied capability.
- Replacing scattered `if tenant.plan == 'pro'` checks with a single entitlements service.
- Designing the data model for plans, features, limits, overrides, and add-ons.
- Supporting enterprise custom-contract overrides without forking the codebase.
- Pairing in-product upgrade prompts (PLG) with the gate runtime so users hit a wall *and* see the path forward.
- Coordinating entitlements with feature flags (distinct concerns; they overlap dangerously if confused).

## Do Not Use When

- The task is Stripe Billing primitives (Plan / Price / Subscription / Trial) — use `subscription-billing`. This skill consumes those primitives.
- The task is experimentation feature flags (A/B tests, gradual rollout) — feature flags ≠ entitlements; see §3.
- The task is per-tenant data isolation — use `multi-tenant-saas-architecture`.
- The task is enterprise SSO/SCIM — use `saas-sso-scim-enterprise-auth`.

## Required Inputs

- Plan catalogue (from `subscription-billing`): tier names, features per tier, limits per tier.
- Pricing model decisions (per-seat, usage-based, hybrid) from product.
- List of features to gate + list of limits to enforce.
- Override policy: how enterprise contracts customise entitlements without code changes.

## Workflow

1. Read this `SKILL.md` end-to-end.
2. Distinguish **entitlements** (what plan allows) from **feature flags** (rollout/experimentation) — §3.
3. Design the entitlements data model (§4) — plans, features, limits, overrides.
4. Pick the resolution strategy (§5) — pre-resolved on JWT vs runtime lookup vs hybrid.
5. Place the gates (§6) — UI hint, API enforce, worker enforce.
6. Wire the upgrade-discovery UX (§7) — the gate is also a sales surface.
7. Build the override mechanism (§8) for enterprise contracts.
8. Instrument hits + denials (§9) for PLG analytics.

## Quality Standards

- Entitlements resolution < 5ms p99 on the hot path (API request).
- Single source of truth for "which plan has what" — never duplicate in UI code and API code.
- Every denied action emits an event (for PQL scoring + upgrade prompts).
- Overrides logged in the audit log with actor + reason.
- Limit enforcement is **atomic with the action** — checking the limit and then performing the action races; use SELECT FOR UPDATE / Redis atomic counters / DB constraints.

## Anti-Patterns

- `if (user.plan == 'pro') { … }` scattered across the codebase. Fix: single resolver.
- Entitlements stored only in the front-end (the gate is bypassable). Fix: server-side enforcement is primary; UI mirrors.
- Counting limits via SELECT then INSERT (race condition). Fix: atomic counter or DB unique constraint per period.
- Feature flags and entitlements implemented in the same code path (a feature toggle ends up gating purchases). Fix: separate runtimes.
- Hard-coding "Enterprise" overrides as `if tenant.id == 12345` branches in the code. Fix: data-driven override table.
- No upgrade prompt when a gate denies (user hits a wall, doesn't know why). Fix: every denial response carries `upgrade_url` + reason.

## Outputs

- Plan × feature × limit catalogue (single source of truth).
- Entitlements resolver service + API.
- Gate placement map (UI / API / worker).
- Override schema and admin tool.
- Denial-event analytics dashboard (PQL surface).

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Entitlements model spec | Markdown doc | `docs/saas/entitlements-model.md` |
| Release evidence | Plan × Feature × Limit matrix | Markdown table | `docs/saas/plan-feature-matrix.md` |
| Operability | Gate-denial analytics dashboard | Dashboard link | `docs/saas/gate-denials-dashboard.md` |

## References

- `references/entitlements-vs-feature-flags.md` — when each applies; how they coexist.
- `references/limit-enforcement-patterns.md` — atomic counters, period rollover, distributed quotas.
- `references/enterprise-override-model.md` — data-driven overrides for custom contracts.
- Companion: `subscription-billing`, `product-led-growth`, `saas-rate-limiting-and-quotas`, `saas-control-plane-engineering`.

<!-- dual-compat-end -->

## §1 What Entitlements Are

An **entitlement** is "this tenant is allowed to do X" — derived from the tenant's plan, contract overrides, add-ons, and trial state.

Examples:
- "Tenant on Pro plan can have up to 10 users."
- "Tenant on Free plan cannot use the API."
- "Tenant on Enterprise plan has unlimited storage."
- "Tenant on Pro+API_addon can call the API 100k times/month."
- "Tenant in trial has access to all Pro features."

The entitlements engine answers two questions:
1. **Boolean**: "Can this tenant access feature X?" (feature gate)
2. **Limit**: "Has this tenant exceeded its quota of Y this period?" (limit gate)

## §2 The Three Inputs to a Resolution

```
plan baseline   →  plan_features (tier 'pro' has feature 'reporting')
                   plan_limits   (tier 'pro' has limit 'users' = 10)

contract        →  tenant_overrides (tenant 123 has feature 'reporting' even on Free)
overrides           tenant_overrides (tenant 123 has limit 'users' = 25 by negotiation)

add-ons         →  tenant_addons (tenant 123 purchased API add-on)
                   addon_features / addon_limits
```

Resolution precedence: **override > add-on > plan baseline**. Trial state is a special case — usually a tenant in trial inherits the target plan's entitlements.

## §3 Entitlements vs Feature Flags

| | Entitlements | Feature Flags |
|---|---|---|
| Purpose | Commercial gating (what plan allows) | Rollout / experimentation (who sees what) |
| Lifetime | Long-lived; tied to plan | Short-lived; removed after rollout |
| Audience | Tenants (by plan) | Users / tenants / cohorts (by criteria) |
| Source of truth | Billing system + entitlements DB | Feature-flag service (LaunchDarkly, Unleash, PostHog) |
| Default for new code | Inherit plan capabilities | Off (gradual rollout) |
| Audited? | Yes — overrides are commercial decisions | Lightly — flag state changes |

**Keep them separate.** Both runtimes can exist in the same app, but their data models, deploy cadence, and ownership differ. Commercial decisions don't belong in the feature-flag tool, and experimentation doesn't belong in the billing-driven entitlements DB.

## §4 Data Model

```sql
-- Catalogue
CREATE TABLE plans (
    code        VARCHAR(32) PRIMARY KEY,    -- 'free', 'starter', 'pro', 'enterprise'
    display_name VARCHAR(64),
    trial_days  INT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE features (
    code        VARCHAR(64) PRIMARY KEY,    -- 'api_access', 'sso_saml', 'reporting_export'
    display_name VARCHAR(128),
    description TEXT
);

CREATE TABLE plan_features (
    plan_code     VARCHAR(32) NOT NULL,
    feature_code  VARCHAR(64) NOT NULL,
    PRIMARY KEY (plan_code, feature_code),
    FOREIGN KEY (plan_code) REFERENCES plans(code),
    FOREIGN KEY (feature_code) REFERENCES features(code)
);

CREATE TABLE limits (
    code        VARCHAR(64) PRIMARY KEY,    -- 'users', 'api_calls_monthly', 'storage_gb', 'projects'
    display_name VARCHAR(128),
    period      ENUM('lifetime','monthly','daily','none') NOT NULL DEFAULT 'lifetime',
    unit        VARCHAR(32)                 -- 'count', 'bytes', 'tokens'
);

CREATE TABLE plan_limits (
    plan_code   VARCHAR(32) NOT NULL,
    limit_code  VARCHAR(64) NOT NULL,
    value       BIGINT,                     -- NULL = unlimited
    PRIMARY KEY (plan_code, limit_code)
);

-- Per-tenant overrides (enterprise contracts)
CREATE TABLE tenant_feature_overrides (
    tenant_id     BIGINT UNSIGNED NOT NULL,
    feature_code  VARCHAR(64) NOT NULL,
    enabled       BOOLEAN NOT NULL,
    reason        VARCHAR(128),
    expires_at    DATETIME,
    granted_by    BIGINT UNSIGNED,
    granted_at    DATETIME NOT NULL,
    PRIMARY KEY (tenant_id, feature_code)
);

CREATE TABLE tenant_limit_overrides (
    tenant_id     BIGINT UNSIGNED NOT NULL,
    limit_code    VARCHAR(64) NOT NULL,
    value         BIGINT,
    reason        VARCHAR(128),
    expires_at    DATETIME,
    granted_by    BIGINT UNSIGNED,
    granted_at    DATETIME NOT NULL,
    PRIMARY KEY (tenant_id, limit_code)
);

-- Add-ons (e.g., extra seats, API package, storage pack)
CREATE TABLE addons (
    code         VARCHAR(64) PRIMARY KEY,
    display_name VARCHAR(128)
);

CREATE TABLE addon_features (
    addon_code   VARCHAR(64) NOT NULL,
    feature_code VARCHAR(64) NOT NULL,
    PRIMARY KEY (addon_code, feature_code)
);

CREATE TABLE addon_limits (
    addon_code   VARCHAR(64) NOT NULL,
    limit_code   VARCHAR(64) NOT NULL,
    value_delta  BIGINT NOT NULL,           -- added to base limit
    PRIMARY KEY (addon_code, limit_code)
);

CREATE TABLE tenant_addons (
    tenant_id   BIGINT UNSIGNED NOT NULL,
    addon_code  VARCHAR(64) NOT NULL,
    quantity    INT NOT NULL DEFAULT 1,
    starts_at   DATETIME NOT NULL,
    ends_at     DATETIME,
    PRIMARY KEY (tenant_id, addon_code)
);

-- Usage counters (for limit checks)
CREATE TABLE tenant_usage_counters (
    tenant_id   BIGINT UNSIGNED NOT NULL,
    limit_code  VARCHAR(64) NOT NULL,
    period_key  VARCHAR(16) NOT NULL,       -- '2026-05' for monthly, '2026-05-11' for daily, 'lifetime'
    used        BIGINT NOT NULL DEFAULT 0,
    updated_at  DATETIME NOT NULL,
    PRIMARY KEY (tenant_id, limit_code, period_key)
);
```

## §5 Resolution Strategies

| Strategy | Latency | Freshness | Use case |
|---|---|---|---|
| **JWT-embedded** | < 0.1ms (no I/O) | Until token refresh (15min) | Boolean feature checks; tier-level limits |
| **Runtime DB lookup** | 1-5ms | Real-time | Limit checks needing current counter; just-changed plans |
| **Redis cache + DB fallback** | < 1ms hit / 5ms miss | Configurable TTL | High-traffic feature checks |
| **Hybrid** | Mixed | Mixed | **Default**: boolean checks in JWT, limit checks against Redis counter |

**Default architecture:**
```
Auth issues JWT with: plan, features[], limits[]  (snapshot at issue)
On every request:
  - Boolean feature check: read JWT (free, instant)
  - Limit check: Redis INCR + compare against JWT limit (atomic, fast)
  - Periodic re-issue (15min) refreshes JWT against DB
On plan change / override:
  - Invalidate user's JWT (force re-issue)
  - Update DB
  - Emit `entitlements.changed` event
```

## §6 Gate Placement

```
UI gates       — Hide / disable features the user can't access. NEVER trust as enforcement.
                Show "Upgrade to Pro" CTAs.
API gates      — Primary enforcement. Reject with 402 Payment Required or 403 Forbidden + upgrade info.
Worker gates   — Background jobs must check too. A bypass of API gates via direct queue insertion is an exploit.
DB constraints — For hard limits (max users per tenant), enforce at DB level too.
```

Pattern for an API gate:
```python
@require_entitlement(feature='api_access')
@require_within_limit(limit='api_calls_monthly')
def api_endpoint(request):
    Entitlements.consume_limit(tenant_id, 'api_calls_monthly', amount=1)
    # ... work
```

Denial response:
```json
{
  "error": {
    "code": "ENTITLEMENT_REQUIRED",
    "feature": "api_access",
    "message": "API access is available on the Pro plan and above.",
    "upgrade_url": "https://app.example.com/billing/upgrade?target=pro&context=api"
  }
}
```

## §7 Upgrade-Discovery UX

The gate is a sales surface, not just a wall. Every denial:
1. **Tells the user what they tried to do** and why it's blocked.
2. **Names the required plan** explicitly.
3. **Links to one-click upgrade** with deep-link context (so post-upgrade they land back where they were).
4. **Emits a `gate.denied` event** for PQL scoring + lifecycle email.

In-product approaching-limit UX:
- 70% of limit: passive indicator (progress bar).
- 80%: in-app banner suggesting upgrade.
- 95%: stronger CTA + email.
- 100%: hard block with one-click upgrade + email.

## §8 Enterprise Override Model

Enterprise contracts often grant custom entitlements. Implement as **data**, never as **code branches**:

```
Admin Console → POST /admin/tenants/123/entitlements
  body: { feature: 'sso_saml', enabled: true, reason: 'Q2 contract Acme', expires_at: '2027-04-01' }
  → writes to tenant_feature_overrides
  → writes audit_log entry
  → emits entitlements.changed event
```

Read-time resolution merges plan + add-ons + overrides automatically.

## §9 Analytics — The Gate Is the PQL Source

Every gate denial is a Product-Qualified-Lead signal. Materialize:
- `gate_denials_per_tenant_per_day` (with `feature`/`limit`, `severity`)
- `tenants_hitting_limit_80pct` (the upgrade pipeline)
- `feature_lock_topN` (which features drive the most upgrade-intent signal)

Feed into `product-led-growth` skill's PQL scoring; coordinate with `saas-lifecycle-email-orchestration` (don't email *and* in-app prompt the same denial — pick one or stagger).

## §10 Anti-Patterns

- **Single big `plans.json` file in the repo** consumed by both UI and API at compile time — drift, redeploys to change limits.
- **No override audit trail** — "who gave Acme unlimited seats?" unanswerable. Fix: every override writes audit_log.
- **Limit check via `SELECT COUNT(*)`** on every request — slow + race-condition prone. Fix: maintained counter + atomic INCR.
- **No expiry on overrides** — a promo grant becomes permanent by accident. Fix: `expires_at` mandatory for promo overrides.
- **No "upgrade context" preserved through the upgrade flow** — user clicks upgrade, lands on pricing page, forgets why. Fix: `upgrade_url` carries `context=` param; post-upgrade redirects back to original action.

## §11 Read Next

- `subscription-billing` — plan / price / subscription primitives.
- `product-led-growth` — PQL + activation; coordinate with gates.
- `saas-rate-limiting-and-quotas` — runtime quota enforcement.
- `saas-control-plane-engineering` — the admin tool that issues overrides.
- `saas-transactional-email-infrastructure` + `saas-lifecycle-email-orchestration` — coordinate gate denials with upgrade email sequences.

## AI Entitlements Addendum

When the SaaS includes AI features, the entitlement catalogue extends with AI-specific keys (model tier, context length, generations/day, tools allow-list, KB size, agent steps, BYOK, fine-tune). The mapping and gateway-enforcement contract live in `ai-entitlements-and-feature-gating`.

Cross-references:
- `ai-entitlements-and-feature-gating` — AI-specific entitlement keys + gateway enforcement.
- `ai-usage-metering-and-billing` — what is gated vs metered.
- `ai-model-gateway` — runtime enforcement chokepoint.
- `ai-on-saas-architecture` — control-plane positioning.
