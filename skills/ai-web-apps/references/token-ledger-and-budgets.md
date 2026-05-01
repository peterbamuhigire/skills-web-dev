# Token Ledger, Budgets, and Quotas

Parent skill: [`ai-web-apps/SKILL.md`](../SKILL.md).

The token ledger + budget schema is one of this skill's four formal outputs. It is the single source of truth for cost attribution, per-tenant / per-user caps, and commercial metering.

Deep billing and metering lives in `ai-metering-billing`. This reference covers only what an AI-enhanced web app must expose: the ledger schema, the budget guard, and the quota gate.

## Ledger schema

Every model call writes one row before returning a response to the caller.

```sql
CREATE TABLE ai_token_ledger (
  id                BIGSERIAL PRIMARY KEY,
  tenant_id         UUID          NOT NULL,
  user_id           UUID          NOT NULL,
  request_id        UUID          NOT NULL,           -- joins prompt, tool calls, cost
  feature_code      TEXT          NOT NULL,           -- e.g. 'chat', 'summarise', 'extract'
  provider          TEXT          NOT NULL,
  model             TEXT          NOT NULL,
  prompt_tokens     INTEGER       NOT NULL,
  completion_tokens INTEGER       NOT NULL,
  cost_micros       BIGINT        NOT NULL,           -- 1 USD cent = 10_000 micros
  latency_ms        INTEGER       NOT NULL,
  status            TEXT          NOT NULL,           -- 'ok' | 'error' | 'fallback'
  created_at        TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE INDEX ix_ledger_tenant_day ON ai_token_ledger (tenant_id, (created_at::date));
CREATE INDEX ix_ledger_user_day   ON ai_token_ledger (user_id,   (created_at::date));
CREATE INDEX ix_ledger_request    ON ai_token_ledger (request_id);
```

Rules:

- Cost is integer micros, not float. Floating-point drift corrupts invoices.
- Never delete ledger rows. Retention is governed by billing, not product.
- Write is append-only. Corrections go into a separate `ai_token_adjustments` table.

## Budget guard (pre-call)

```typescript
// lib/ai/budget-guard.ts
export type BudgetDecision =
  | { allow: true }
  | { allow: false; reason: 'tenant_monthly_cap' | 'user_daily_cap' | 'feature_disabled' };

export async function checkBudget(params: {
  tenantId: string;
  userId: string;
  featureCode: string;
  estimatedCostMicros: number;
}): Promise<BudgetDecision> {
  if (!(await isFeatureEnabledForTenant(params.tenantId, params.featureCode))) {
    return { allow: false, reason: 'feature_disabled' };
  }
  const monthSpent = await sumTenantSpendThisMonth(params.tenantId);
  const monthCap = await getTenantMonthlyCap(params.tenantId);
  if (monthSpent + params.estimatedCostMicros > monthCap) {
    return { allow: false, reason: 'tenant_monthly_cap' };
  }
  const userToday = await countUserCallsToday(params.userId, params.featureCode);
  const userCap = await getUserDailyCap(params.tenantId, params.featureCode);
  if (userToday >= userCap) return { allow: false, reason: 'user_daily_cap' };
  return { allow: true };
}
```

## Quota gate (fast path, per-feature)

For features with a strict per-user daily count (e.g. "10 summaries per user per day") the ledger is authoritative for cost, but a Redis counter is authoritative for rate:

```typescript
// lib/ai/quota.ts
import { redis } from './redis';

export async function consumeDailyQuota(
  userId: string,
  featureCode: string,
  dailyLimit: number
): Promise<boolean> {
  const day = new Date().toISOString().slice(0, 10);
  const key = `quota:${featureCode}:${userId}:${day}`;
  const count = await redis.incr(key);
  if (count === 1) await redis.expire(key, 24 * 60 * 60);
  return count <= dailyLimit;
}
```

Rules:

- Quota key uses the UTC day, not the user's local day — avoids midnight races across timezones.
- Quota is best-effort (Redis may lose data); the ledger is the system of record.
- Expiry is set only on first increment; do not reset TTL on every call.

## Budget-failure response shape

```json
{
  "error": {
    "code": "BUDGET_EXCEEDED",
    "reason": "tenant_monthly_cap",
    "retry_after_seconds": 0,
    "upgrade_path": "/billing/plans"
  }
}
```

The UI uses `upgrade_path` to deep-link into the billing flow. Never silently degrade to a cheaper model without user consent — it corrupts the commercial contract.

## Cost estimation before the call

For streaming requests the exact cost is unknown pre-call. Estimate with a conservative cap:

```text
estimated_cost_micros =
    prompt_tokens * price_per_prompt_token_micros
  + max_completion_tokens * price_per_completion_token_micros
```

Use `max_completion_tokens` (i.e. the `maxTokens` setting), not the expected completion. This makes the budget guard safe: actual cost cannot exceed estimate.

## Joining with the session trace

Every call logs `request_id`. The same `request_id` is set on the server action, propagated through the prompt trace, and written to the ledger. A single query reconstructs the full session cost:

```sql
SELECT feature_code, SUM(cost_micros) AS cost_micros, COUNT(*) AS calls
FROM ai_token_ledger
WHERE request_id = $1
GROUP BY feature_code;
```
