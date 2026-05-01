---
name: ai-metering-billing
description: Token metering and billing for multi-tenant AI SaaS — token ledger schema,
  metering middleware, per-user and per-tenant usage aggregation, budget cap enforcement,
  invoice line generation, admin dashboards, and pricing tier design. Invoke when...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Metering and Billing
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Token metering and billing for multi-tenant AI SaaS — token ledger schema, metering middleware, per-user and per-tenant usage aggregation, budget cap enforcement, invoice line generation, admin dashboards, and pricing tier design. Invoke when...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-metering-billing` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Token ledger schema register | Markdown doc per `skill-composition-standards/references/entity-model-template.md` covering token, request, and overage tables | `docs/ai/token-ledger-schema.md` |
| Release evidence | Per-tenant metering policy | Markdown doc capturing per-tenant token allocation, overage handling, and billing-cycle reconciliation | `docs/ai/metering-policy.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Purpose

Treat AI token consumption as a **metered utility** — like electricity or SMS. Every call is logged, every token counted, every tenant billed only for what they use. This protects your margins and gives clients full transparency.

---

## Token Ledger Schema

```sql
-- Core usage log — one row per AI API call
CREATE TABLE ai_usage_log (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id       BIGINT UNSIGNED NOT NULL,
    user_id         BIGINT UNSIGNED NOT NULL,
    feature_slug    VARCHAR(64) NOT NULL,   -- e.g. 'sales-summary', 'risk-alert'
    model           VARCHAR(64) NOT NULL,   -- e.g. 'claude-haiku-4-5'
    provider        VARCHAR(32) NOT NULL,   -- 'anthropic' | 'openai' | 'deepseek'
    input_tokens    INT UNSIGNED NOT NULL DEFAULT 0,
    output_tokens   INT UNSIGNED NOT NULL DEFAULT 0,
    total_tokens    INT UNSIGNED GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    cost_usd        DECIMAL(10,6) NOT NULL DEFAULT 0.000000,  -- raw provider cost
    billing_period  CHAR(7) NOT NULL,       -- 'YYYY-MM' for monthly rollup
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_tenant_period  (tenant_id, billing_period),
    INDEX idx_user_period    (user_id, billing_period),
    INDEX idx_feature_period (feature_slug, billing_period),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (user_id)   REFERENCES users(id)
);

-- Monthly rollup cache (updated nightly by scheduled job)
CREATE TABLE ai_usage_monthly (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id       BIGINT UNSIGNED NOT NULL,
    user_id         BIGINT UNSIGNED NULL,   -- NULL = tenant total
    billing_period  CHAR(7) NOT NULL,
    total_calls     INT UNSIGNED NOT NULL DEFAULT 0,
    input_tokens    BIGINT UNSIGNED NOT NULL DEFAULT 0,
    output_tokens   BIGINT UNSIGNED NOT NULL DEFAULT 0,
    total_tokens    BIGINT UNSIGNED NOT NULL DEFAULT 0,
    cost_usd        DECIMAL(10,4) NOT NULL DEFAULT 0.0000,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tenant_user_period (tenant_id, user_id, billing_period),
    INDEX idx_tenant_period (tenant_id, billing_period)
);

-- AI module subscription per tenant
CREATE TABLE tenant_ai_modules (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id       BIGINT UNSIGNED NOT NULL,
    tier            ENUM('starter','growth','enterprise') NOT NULL DEFAULT 'starter',
    is_active       TINYINT(1) NOT NULL DEFAULT 0,
    budget_usd      DECIMAL(10,4) NOT NULL DEFAULT 0.0000,  -- monthly hard cap
    budget_ugx      DECIMAL(14,2) NOT NULL DEFAULT 0.00,    -- retail price charged to tenant
    activated_at    DATETIME NULL,
    expires_at      DATETIME NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tenant_ai (tenant_id)
);

-- Budget alert state (prevent duplicate alert emails)
CREATE TABLE ai_budget_alerts (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id   BIGINT UNSIGNED NOT NULL,
    period      CHAR(7) NOT NULL,
    threshold   TINYINT NOT NULL,           -- 80 or 100
    alerted_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tenant_period_threshold (tenant_id, period, threshold)
);
```

---

## Metering Middleware (PHP/Laravel)

```php
// app/Services/AI/AIMeteredClient.php
class AIMeteredClient
{
    public function __construct(
        private AIProvider $provider,
        private AIGate $gate,
        private CostCalculator $costs,
    ) {}

    public function call(int $tenantId, int $userId, string $featureSlug, AIRequest $request): AIResponse
    {
        // 1. Gate check
        $this->gate->check($tenantId, $featureSlug);

        // 2. Budget pre-check
        $this->assertBudgetAvailable($tenantId);

        // 3. Make the AI call
        $response = $this->provider->complete($request);

        // 4. Record usage
        $this->record($tenantId, $userId, $featureSlug, $request->model, $response);

        // 5. Post-call budget check (triggers alerts)
        $this->checkBudgetAlerts($tenantId);

        return $response;
    }

    private function record(int $tenantId, int $userId, string $slug, string $model, AIResponse $r): void
    {
        $costUsd = $this->costs->calculate($model, $r->inputTokens, $r->outputTokens);

        AIUsageLog::create([
            'tenant_id'      => $tenantId,
            'user_id'        => $userId,
            'feature_slug'   => $slug,
            'model'          => $model,
            'provider'       => $this->costs->providerFor($model),
            'input_tokens'   => $r->inputTokens,
            'output_tokens'  => $r->outputTokens,
            'cost_usd'       => $costUsd,
            'billing_period' => now()->format('Y-m'),
        ]);
    }

    private function assertBudgetAvailable(int $tenantId): void
    {
        $module = TenantAIModule::where('tenant_id', $tenantId)->firstOrFail();
        $spent  = AIUsageLog::where('tenant_id', $tenantId)
                             ->where('billing_period', now()->format('Y-m'))
                             ->sum('cost_usd');

        if ($spent >= $module->budget_usd) {
            throw new AIBudgetExceededException('Monthly AI budget exhausted.');
        }
    }

    private function checkBudgetAlerts(int $tenantId): void
    {
        $module = TenantAIModule::where('tenant_id', $tenantId)->firstOrFail();
        $spent  = AIUsageLog::where('tenant_id', $tenantId)
                             ->where('billing_period', now()->format('Y-m'))
                             ->sum('cost_usd');

        $pct = ($spent / $module->budget_usd) * 100;
        $period = now()->format('Y-m');

        foreach ([80, 100] as $threshold) {
            if ($pct >= $threshold) {
                $inserted = DB::table('ai_budget_alerts')->insertOrIgnore([
                    'tenant_id' => $tenantId, 'period' => $period, 'threshold' => $threshold,
                    'alerted_at' => now(),
                ]);
                if ($inserted) {
                    event(new AIBudgetThresholdReached($tenantId, $threshold, $spent, $module->budget_usd));
                }
            }
        }
    }
}
```

---

## Cost Calculator

```php
// app/Services/AI/CostCalculator.php
class CostCalculator
{
    // USD per 1M tokens — update when provider pricing changes
    private array $pricing = [
        'claude-haiku-4-5'    => ['in' => 0.80,  'out' => 4.00],
        'claude-sonnet-4-6'   => ['in' => 3.00,  'out' => 15.00],
        'gpt-4o-mini'         => ['in' => 0.15,  'out' => 0.60],
        'gpt-4o'              => ['in' => 2.50,  'out' => 10.00],
        'deepseek-v3'         => ['in' => 0.27,  'out' => 1.10],
        'gemini-2.0-flash'    => ['in' => 0.10,  'out' => 0.40],
    ];

    public function calculate(string $model, int $inputTokens, int $outputTokens): float
    {
        $p = $this->pricing[$model] ?? $this->pricing['claude-haiku-4-5'];
        return round(($inputTokens * $p['in'] + $outputTokens * $p['out']) / 1_000_000, 6);
    }

    public function providerFor(string $model): string
    {
        return match(true) {
            str_starts_with($model, 'claude')   => 'anthropic',
            str_starts_with($model, 'gpt')      => 'openai',
            str_starts_with($model, 'deepseek') => 'deepseek',
            str_starts_with($model, 'gemini')   => 'google',
            default                              => 'unknown',
        };
    }
}
```

---

## Usage Aggregation Queries

```sql
-- Per-user usage for current month
SELECT
    u.name,
    COUNT(*)                AS total_calls,
    SUM(l.input_tokens)     AS input_tokens,
    SUM(l.output_tokens)    AS output_tokens,
    SUM(l.cost_usd)         AS cost_usd,
    l.feature_slug          AS top_feature
FROM ai_usage_log l
JOIN users u ON u.id = l.user_id
WHERE l.tenant_id = :tenantId
  AND l.billing_period = DATE_FORMAT(NOW(), '%Y-%m')
GROUP BY l.user_id, l.feature_slug
ORDER BY cost_usd DESC;

-- Per-tenant monthly summary (super-admin)
SELECT
    t.name                        AS tenant,
    m.tier,
    m.budget_ugx,
    SUM(l.cost_usd)               AS raw_cost_usd,
    SUM(l.cost_usd) * 3700        AS raw_cost_ugx,
    m.budget_ugx - SUM(l.cost_usd) * 3700 AS margin_ugx,
    ROUND(SUM(l.cost_usd) / m.budget_usd * 100, 1) AS budget_pct_used
FROM ai_usage_log l
JOIN tenants t ON t.id = l.tenant_id
JOIN tenant_ai_modules m ON m.tenant_id = l.tenant_id
WHERE l.billing_period = DATE_FORMAT(NOW(), '%Y-%m')
GROUP BY l.tenant_id
ORDER BY raw_cost_usd DESC;
```

---

## Invoice Line Generation

At month-end, generate one AI line item per tenant invoice:

```php
// app/Services/Billing/AIInvoiceLineGenerator.php
class AIInvoiceLineGenerator
{
    public function generateForTenant(int $tenantId, string $period): InvoiceLine
    {
        $module = TenantAIModule::where('tenant_id', $tenantId)->firstOrFail();
        $calls  = AIUsageLog::where(['tenant_id' => $tenantId, 'billing_period' => $period])
                             ->selectRaw('COUNT(*) as calls, SUM(total_tokens) as tokens')->first();

        return new InvoiceLine(
            description: "AI Module ({$module->tier}) — {$period} — {$calls->calls} calls / " .
                         number_format($calls->tokens) . " tokens",
            amount_ugx:  $module->budget_ugx,
            line_type:   'ai_module',
        );
    }
}
```

---

## Pricing Tiers (Reference)

| Tier | Token Budget/Tenant/Month | Hard Cap (USD) | Retail Price (UGX) | Target Gross Margin |
|------|--------------------------|---------------|-------------------|---------------------|
| Starter AI | 2M tokens | $2.00 | 50,000 | ~65% |
| Growth AI | 10M tokens | $10.00 | 200,000 | ~70% |
| Enterprise AI | 50M tokens | $50.00 | 800,000 | ~75% |

*Overage: charge UGX 25 per 1,000 tokens above cap, or upgrade to next tier.*

---

## Scheduled Jobs

```php
// Monthly rollup — runs daily at 01:00
Schedule::call(fn() => AIUsageRollupJob::dispatch())->dailyAt('01:00');

// Budget warning check — runs every hour
Schedule::call(fn() => AIBudgetCheckJob::dispatch())->hourly();

// Month-end invoice line generation — runs on 1st of each month
Schedule::call(fn() => AIInvoiceGenerationJob::dispatch())->monthlyOn(1, '06:00');
```

---

**See also:**
- `ai-architecture-patterns` — AIGate and BudgetGuard middleware
- `ai-cost-modeling` — Pricing inputs and margin calculations
- `ai-ux-patterns` — Usage dashboard UX for users and admins
- `ai-security` — Audit logging alongside metering