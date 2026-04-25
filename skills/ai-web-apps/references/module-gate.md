# AI Module Gate — Off by Default, Per-Tenant Enablement

Parent skill: [`ai-web-apps/SKILL.md`](../SKILL.md).

The module gate is one of this skill's four formal outputs. Every AI-powered feature is gated at three independent points: tenant entitlement, user role, and runtime budget. All three must pass for the feature to execute.

## Why three gates, not one

| Gate | Question answered | Failure mode if removed |
|---|---|---|
| Tenant entitlement | Is the AI module enabled in this tenant's plan? | Free tenants consume paid-plan features and cost |
| User role / consent | Does this user have permission, and has consent been recorded? | Data leaves tenant boundary without user agreement |
| Budget guard | Is there budget and quota headroom right now? | Runaway spend, noisy neighbour, surprise bills |

Collapsing the gates (e.g. only checking entitlement) means a single bug becomes a billing incident.

## Default posture

```text
Every AI feature defaults to OFF.
Enablement is an explicit tenant admin action.
Disablement is immediate and unilateral (no migration required).
```

This matters for: rollouts, incident response (kill switch), plan downgrades, and GDPR / DPPA right-to-refuse.

## Schema

```sql
CREATE TABLE ai_feature_catalog (
  feature_code      TEXT PRIMARY KEY,          -- 'chat', 'summarise', 'rag-search'
  display_name      TEXT NOT NULL,
  description       TEXT NOT NULL,
  min_plan_tier     TEXT NOT NULL,             -- 'free' | 'pro' | 'enterprise'
  default_enabled   BOOLEAN NOT NULL DEFAULT false,
  deprecated_at     TIMESTAMPTZ
);

CREATE TABLE tenant_ai_features (
  tenant_id         UUID NOT NULL,
  feature_code      TEXT NOT NULL REFERENCES ai_feature_catalog (feature_code),
  enabled           BOOLEAN NOT NULL DEFAULT false,
  enabled_by        UUID,                       -- user who flipped the switch
  enabled_at        TIMESTAMPTZ,
  monthly_cap_micros BIGINT NOT NULL DEFAULT 0, -- 0 = inherit plan default
  PRIMARY KEY (tenant_id, feature_code)
);
```

Rules:

- A tenant row is created lazily on first enablement; absence = disabled.
- `monthly_cap_micros = 0` means "inherit from plan", not "unlimited".
- `deprecated_at` lets product retire a feature without deleting ledger history.

## Gate function

```typescript
// lib/ai/module-gate.ts
export type GateResult =
  | { ok: true }
  | { ok: false; reason: 'not_entitled' | 'not_enabled' | 'forbidden' | 'consent_missing' };

export async function checkModuleGate(params: {
  tenantId: string;
  userId: string;
  featureCode: string;
}): Promise<GateResult> {
  const catalog = await getFeatureCatalog(params.featureCode);
  if (!catalog || catalog.deprecated_at) return { ok: false, reason: 'not_entitled' };

  const plan = await getTenantPlan(params.tenantId);
  if (!planMeetsTier(plan, catalog.min_plan_tier)) return { ok: false, reason: 'not_entitled' };

  const tenantFlag = await getTenantAiFeature(params.tenantId, params.featureCode);
  if (!tenantFlag?.enabled) return { ok: false, reason: 'not_enabled' };

  const role = await getUserRole(params.userId, params.tenantId);
  if (!roleMayUseFeature(role, params.featureCode)) return { ok: false, reason: 'forbidden' };

  if (catalog.requires_consent) {
    const consent = await getUserConsent(params.userId, params.featureCode);
    if (!consent?.granted) return { ok: false, reason: 'consent_missing' };
  }

  return { ok: true };
}
```

Call this first in every AI route, before the budget guard.

## Kill-switch pattern

For incident response, a platform-level feature flag overrides per-tenant enablement:

```typescript
if (await platformFlag('ai.global_kill_switch')) {
  return { ok: false, reason: 'not_enabled' };
}
```

Flipping the kill switch must take effect within one minute across all regions. Cache the platform flag in memory with a 30-second TTL — no longer.

## Tenant admin UI surface

Admins see one toggle per catalog entry, plus:

- Current month spend vs cap, with a progress bar.
- Last activity timestamp.
- "Deprecated" badge when `deprecated_at` is set, with a scheduled-off date.

Users never see a feature that isn't entitled for their tenant. Non-admins never see the enablement toggle.

## Audit

Every flip writes to `ai_feature_audit`:

| column | value |
|---|---|
| `tenant_id` | tenant |
| `feature_code` | feature |
| `action` | `enable` \| `disable` \| `cap_change` |
| `actor_user_id` | who |
| `from_value` | prior state |
| `to_value` | new state |
| `reason` | free text (required for enterprise plans) |
| `created_at` | timestamp |

Audit rows are immutable. Use them to answer "who turned this on?" during billing disputes and incident reviews.

## Rollout choreography

1. Add `feature_code` to catalog with `default_enabled = false`, `min_plan_tier = 'enterprise'`.
2. Enable for internal-test tenant. Validate ledger rows land with the correct `feature_code`.
3. Enable for two pilot tenants, monitor budget + quality for one week.
4. Expand `min_plan_tier` to the target tier once SLOs are green.
5. Only then advertise the feature in pricing pages.

Never ship a feature that is entitled before the ledger, gate, and budget guard are all in production.
