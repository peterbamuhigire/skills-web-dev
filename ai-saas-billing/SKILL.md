---
name: ai-saas-billing
description: Use when implementing AI features in multi-tenant SaaS — AI module gating
  (off by default), per-tenant and per-user token metering, budget enforcement, billing
  aggregation, and quota management for franchise-style SaaS apps
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI SaaS Billing — Token Metering and Module Gating

<!-- dual-compat-start -->
## Use When

- Use when implementing AI features in multi-tenant SaaS — AI module gating (off by default), per-tenant and per-user token metering, budget enforcement, billing aggregation, and quota management for franchise-style SaaS apps
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-saas-billing` or would be better handled by a more specific companion skill.
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

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Overview

AI features cost real money per token. In a multi-tenant SaaS, clients must opt in and pay for AI features. Every token must be tracked for invoicing, cost control, and abuse prevention.

**Rule:** AI module is OFF by default for all tenants. A tenant must explicitly purchase and activate the AI module.

---

## Schema — Complete Billing Foundation

```sql
-- 1. Per-tenant AI configuration
CREATE TABLE tenant_ai_config (
  tenant_id          INT PRIMARY KEY,
  ai_enabled         BOOLEAN DEFAULT FALSE,
  plan_name          VARCHAR(50),            -- 'ai_basic', 'ai_pro', 'ai_enterprise'
  monthly_token_limit BIGINT,               -- NULL = unlimited
  monthly_budget_usd  DECIMAL(10,2),        -- NULL = unlimited
  budget_alert_pct   INT DEFAULT 80,
  overage_action     ENUM('block','alert_only') DEFAULT 'block',
  enabled_at         TIMESTAMP NULL,
  enabled_by         INT,
  created_at         TIMESTAMP DEFAULT NOW(),
  updated_at         TIMESTAMP DEFAULT NOW() ON UPDATE NOW()
);

-- 2. Token usage ledger (append-only)
CREATE TABLE ai_token_usage (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  tenant_id     INT NOT NULL,
  user_id       INT NOT NULL,
  franchise_id  INT,                          -- for franchise/branch structure
  feature_name  VARCHAR(100) NOT NULL,        -- 'invoice_analysis', 'chat', 'report_summary'
  model         VARCHAR(50) NOT NULL,         -- 'gpt-4o', 'gpt-4o-mini', 'claude-3-sonnet'
  tokens_in     INT NOT NULL DEFAULT 0,
  tokens_out    INT NOT NULL DEFAULT 0,
  cost_usd      DECIMAL(10,6) NOT NULL,
  latency_ms    INT,
  request_id    VARCHAR(64),                 -- LLM provider's request ID for debugging
  prompt_version VARCHAR(10),
  created_at    TIMESTAMP DEFAULT NOW(),
  INDEX idx_tenant_date  (tenant_id, created_at),
  INDEX idx_user_date    (user_id, created_at),
  INDEX idx_franchise    (franchise_id, created_at),
  INDEX idx_feature      (tenant_id, feature_name, created_at)
);

-- 3. Monthly usage summary (materialised, refreshed nightly)
CREATE TABLE ai_usage_monthly (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  tenant_id      INT NOT NULL,
  franchise_id   INT,
  year_month     CHAR(7) NOT NULL,            -- '2026-04'
  total_tokens   BIGINT NOT NULL DEFAULT 0,
  total_cost_usd DECIMAL(10,4) NOT NULL DEFAULT 0,
  call_count     INT NOT NULL DEFAULT 0,
  updated_at     TIMESTAMP DEFAULT NOW() ON UPDATE NOW(),
  UNIQUE KEY (tenant_id, franchise_id, year_month)
);
```

---

## Token Pricing Table

```sql
CREATE TABLE ai_model_pricing (
  model          VARCHAR(50) PRIMARY KEY,
  cost_per_1k_in  DECIMAL(10,6) NOT NULL,    -- USD per 1,000 input tokens
  cost_per_1k_out DECIMAL(10,6) NOT NULL,    -- USD per 1,000 output tokens
  updated_at     TIMESTAMP DEFAULT NOW() ON UPDATE NOW()
);

INSERT INTO ai_model_pricing VALUES
  ('gpt-4o',             0.002500, 0.010000),
  ('gpt-4o-mini',        0.000150, 0.000600),
  ('claude-3-5-sonnet',  0.003000, 0.015000),
  ('claude-3-haiku',     0.000250, 0.001250),
  ('text-embedding-3-small', 0.000020, 0.000000);
```

---

## Module Gate — Every AI Endpoint Checks This

```php
// AiService.php

class AiService {
    /**
     * Call before ANY AI feature. Throws exceptions on disabled or over-budget.
     */
    public static function checkGate(int $tenantId): TenantAiConfig {
        $config = TenantAiConfig::find($tenantId);

        if (!$config || !$config->ai_enabled) {
            throw new AiModuleDisabledException(
                'AI features are not enabled for your account. ' .
                'Please upgrade your plan to access AI capabilities.'
            );
        }

        // Check monthly budget
        if ($config->monthly_budget_usd !== null) {
            $spent = self::getCurrentMonthCost($tenantId);
            if ($spent >= $config->monthly_budget_usd) {
                if ($config->overage_action === 'block') {
                    throw new AiBudgetExceededException(
                        "Monthly AI budget of \${$config->monthly_budget_usd} reached. " .
                        "Usage resumes next month or you can upgrade your plan."
                    );
                }
            } elseif ($spent >= $config->monthly_budget_usd * ($config->budget_alert_pct / 100)) {
                self::sendBudgetAlert($tenantId, $spent, $config->monthly_budget_usd);
            }
        }

        // Check token limit
        if ($config->monthly_token_limit !== null) {
            $used = self::getCurrentMonthTokens($tenantId);
            if ($used >= $config->monthly_token_limit) {
                throw new AiTokenLimitExceededException('Monthly AI token limit reached.');
            }
        }

        return $config;
    }

    /**
     * Log every AI call — call after getting the LLM response.
     */
    public static function logUsage(
        int $tenantId,
        int $userId,
        string $feature,
        string $model,
        int $tokensIn,
        int $tokensOut,
        int $latencyMs,
        ?int $franchiseId = null,
        ?string $requestId = null,
        ?string $promptVersion = null
    ): void {
        $pricing = AiModelPricing::find($model);
        $cost = ($tokensIn / 1000 * $pricing->cost_per_1k_in)
              + ($tokensOut / 1000 * $pricing->cost_per_1k_out);

        AiTokenUsage::create([
            'tenant_id'      => $tenantId,
            'user_id'        => $userId,
            'franchise_id'   => $franchiseId,
            'feature_name'   => $feature,
            'model'          => $model,
            'tokens_in'      => $tokensIn,
            'tokens_out'     => $tokensOut,
            'cost_usd'       => $cost,
            'latency_ms'     => $latencyMs,
            'request_id'     => $requestId,
            'prompt_version' => $promptVersion,
        ]);
    }
}
```

---

## Usage Pattern — In Every AI Feature

```php
// InvoiceAnalysisController.php

public function analyse(Request $request): JsonResponse {
    $tenantId = auth()->user()->tenant_id;
    $userId   = auth()->id();
    $franchiseId = auth()->user()->franchise_id;

    // STEP 1: Gate check (throws if disabled or over budget)
    AiService::checkGate($tenantId);

    // STEP 2: Validate input
    $invoiceText = AiInputGuard::validate($request->input('invoice_text'), $tenantId);

    // STEP 3: Call AI
    $startTime = microtime(true);
    $response  = $this->openai->chat($this->buildPrompt($invoiceText));
    $latency   = (int)((microtime(true) - $startTime) * 1000);

    // STEP 4: Log usage (always — even on output validation failure)
    AiService::logUsage(
        tenantId:      $tenantId,
        userId:        $userId,
        feature:       'invoice_analysis',
        model:         'gpt-4o-mini',
        tokensIn:      $response['usage']['prompt_tokens'],
        tokensOut:     $response['usage']['completion_tokens'],
        latencyMs:     $latency,
        franchiseId:   $franchiseId,
        requestId:     $response['id'],
        promptVersion: '1.3'
    );

    // STEP 5: Validate and return output
    return response()->json([
        'result' => AiOutputGuard::validate($response['choices'][0]['message']['content']),
    ]);
}
```

---

## Billing Aggregation Queries

```sql
-- Tenant monthly invoice (for SaaS billing)
SELECT
    t.name AS tenant_name,
    DATE_FORMAT(u.created_at, '%Y-%m') AS month,
    SUM(u.tokens_in + u.tokens_out) AS total_tokens,
    SUM(u.cost_usd) AS total_cost_usd,
    COUNT(*) AS total_calls
FROM ai_token_usage u
JOIN tenants t ON t.id = u.tenant_id
WHERE u.tenant_id = :tenant_id
  AND u.created_at BETWEEN :start AND :end
GROUP BY tenant_id, month;

-- Usage by franchise/branch (for franchise transparency)
SELECT
    f.name AS franchise_name,
    SUM(u.tokens_in + u.tokens_out) AS tokens,
    SUM(u.cost_usd) AS cost_usd,
    COUNT(*) AS calls
FROM ai_token_usage u
JOIN franchises f ON f.id = u.franchise_id
WHERE u.tenant_id = :tenant_id
  AND u.created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY franchise_id
ORDER BY cost_usd DESC;

-- Top AI features by cost
SELECT feature_name, model,
       SUM(cost_usd) AS total_cost,
       AVG(tokens_in + tokens_out) AS avg_tokens_per_call,
       COUNT(*) AS calls
FROM ai_token_usage
WHERE tenant_id = :tenant_id
  AND created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY feature_name, model
ORDER BY total_cost DESC;

-- Heavy users (for capacity planning + abuse detection)
SELECT user_id, COUNT(*) AS calls, SUM(cost_usd) AS cost
FROM ai_token_usage
WHERE tenant_id = :tenant_id
  AND created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
GROUP BY user_id
HAVING cost > 5.00   -- flag users spending > $5/day
ORDER BY cost DESC;
```

---

## Admin Dashboard Data Points

Expose these to clients in their billing/settings dashboard:

| Metric | Display |
|---|---|
| AI module status | Enabled / Disabled (toggle) |
| Current month spend | $X.XX of $Y.YY budget |
| Budget alert threshold | 80% (configurable) |
| Top features by cost | Bar chart: feature vs cost |
| Usage by branch | Table: franchise → tokens → cost |
| Daily usage trend | Line chart: cost per day this month |
| Remaining token quota | X of Y tokens used |

---

## AI Pricing Plans (Example Tiers)

```sql
-- Tenant upgrades trigger this
UPDATE tenant_ai_config SET
  ai_enabled         = TRUE,
  plan_name          = 'ai_pro',
  monthly_budget_usd = 50.00,
  monthly_token_limit = 1000000,
  budget_alert_pct   = 80,
  overage_action     = 'block',
  enabled_at         = NOW()
WHERE tenant_id = :tenant_id;
```

| Plan | Monthly Budget | Token Limit | Features |
|---|---|---|---|
| AI Basic | $10 | 200K tokens | Chat, summarisation |
| AI Pro | $50 | 1M tokens | + Analysis, agents |
| AI Enterprise | $200 | 5M tokens | + Custom models, RAG |
| Unlimited | — | No limit | Enterprise contracts |

---

## Anti-Patterns

- **AI enabled by default** — one viral post can drain your entire OpenAI credit
- **No token logging** — you cannot invoice clients or debug runaway costs
- **Logging only totals** — log every individual call for debugging and dispute resolution
- **No per-franchise breakdown** — franchise owners need to see their own branch's AI costs
- **Shared token budget across tenants** — each tenant must have independent metering

---

## Sources
Peter Bamuhigire's architecture requirement (2026-04-07); Chip Huyen — *AI Engineering* (2025); David Spuler — *Generative AI Applications* (2024) Ch.9
