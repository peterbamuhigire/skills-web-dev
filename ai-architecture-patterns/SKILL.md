---
name: ai-architecture-patterns
description: Integration architecture for AI-powered features — AI Module Gate, Token
  Ledger schema, Budget Guard, provider abstraction, RAG, function calling, and streaming.
  Technology examples for PHP/Laravel, Android/Kotlin, and iOS/Swift. Invoke during...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Architecture Patterns

<!-- dual-compat-start -->
## Use When

- Integration architecture for AI-powered features — AI Module Gate, Token Ledger schema, Budget Guard, provider abstraction, RAG, function calling, and streaming. Technology examples for PHP/Laravel, Android/Kotlin, and iOS/Swift. Invoke during...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-architecture-patterns` or would be better handled by a more specific companion skill.
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
## Core Principle

Every AI feature in a multi-tenant SaaS MUST pass through three gates before making an API call:

```
Request → [1. Module Gate] → [2. Budget Guard] → [3. Provider Abstraction] → AI API
                ↓ fail              ↓ fail
        "AI not activated"    "Budget exceeded"
```

See `ai-metering-billing` for the Token Ledger schema and metering middleware.

---

## Pattern 1: AI Module Gate

The AI module is **off by default** per tenant. Activated only when the tenant has purchased the AI add-on.

### Database Schema

```sql
CREATE TABLE tenant_ai_modules (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id     BIGINT UNSIGNED NOT NULL,
    tier          ENUM('starter','growth','enterprise') NOT NULL,
    is_active     TINYINT(1) NOT NULL DEFAULT 0,
    activated_at  DATETIME NULL,
    expires_at    DATETIME NULL,
    budget_usd    DECIMAL(10,4) NOT NULL DEFAULT 0,  -- monthly hard cap
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tenant_ai (tenant_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE TABLE tenant_ai_features (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id   BIGINT UNSIGNED NOT NULL,
    feature_slug VARCHAR(64) NOT NULL,   -- e.g. 'sales-summary', 'risk-alert'
    is_enabled  TINYINT(1) NOT NULL DEFAULT 1,
    UNIQUE KEY uq_tenant_feature (tenant_id, feature_slug)
);
```

### Gate Check (PHP/Laravel)

```php
// app/Services/AI/AIGate.php
class AIGate
{
    public function check(int $tenantId, string $featureSlug): void
    {
        $module = TenantAIModule::where('tenant_id', $tenantId)->first();

        if (!$module?->is_active) {
            throw new AIModuleNotActiveException('AI module not activated for this tenant.');
        }

        if ($module->expires_at && now()->gt($module->expires_at)) {
            throw new AIModuleExpiredException('AI module subscription has expired.');
        }

        $feature = TenantAIFeature::where(['tenant_id' => $tenantId, 'feature_slug' => $featureSlug])->first();
        if ($feature && !$feature->is_enabled) {
            throw new AIFeatureDisabledException("Feature '{$featureSlug}' is disabled for this tenant.");
        }
    }
}
```

---

## Pattern 2: Budget Guard

Check remaining budget before every AI call. Record usage after.

```php
// app/Services/AI/BudgetGuard.php
class BudgetGuard
{
    public function checkAndRecord(int $tenantId, int $userId, string $feature, AIUsage $usage): void
    {
        $module   = TenantAIModule::where('tenant_id', $tenantId)->firstOrFail();
        $spent    = AIUsageLog::monthToDateCost($tenantId);
        $remaining = $module->budget_usd - $spent;

        if ($remaining <= 0) {
            throw new AIBudgetExceededException('Monthly AI budget exhausted. Contact your administrator.');
        }

        if ($remaining < $module->budget_usd * 0.20) {
            event(new AIBudgetWarning($tenantId, $remaining)); // notify admin at 20% remaining
        }

        AIUsageLog::record($tenantId, $userId, $feature, $usage);
    }
}
```

---

## Pattern 3: Provider Abstraction Layer

Code against an interface. Swap providers without touching feature logic.

```php
// app/Services/AI/Contracts/AIProvider.php
interface AIProvider
{
    public function complete(AIRequest $request): AIResponse;
    public function stream(AIRequest $request): Generator;
}

// app/Services/AI/Providers/AnthropicProvider.php
class AnthropicProvider implements AIProvider
{
    public function complete(AIRequest $request): AIResponse
    {
        $response = Http::withToken(config('ai.anthropic_key'))
            ->post('https://api.anthropic.com/v1/messages', [
                'model'      => $request->model ?? 'claude-haiku-4-5',
                'max_tokens' => $request->maxTokens ?? 1024,
                'system'     => $request->systemPrompt,
                'messages'   => [['role' => 'user', 'content' => $request->userMessage]],
            ]);

        return new AIResponse(
            content:      $response->json('content.0.text'),
            inputTokens:  $response->json('usage.input_tokens'),
            outputTokens: $response->json('usage.output_tokens'),
            model:        $response->json('model'),
        );
    }
}
```

**Bind in `AppServiceProvider`:**
```php
$this->app->bind(AIProvider::class, fn() => match(config('ai.provider')) {
    'anthropic' => new AnthropicProvider(),
    'openai'    => new OpenAIProvider(),
    'deepseek'  => new DeepSeekProvider(),
    default     => new AnthropicProvider(),
});
```

---

## Pattern 4: Feature Service (Full Flow)

```php
// app/Services/AI/Features/SalesSummaryService.php
class SalesSummaryService
{
    public function __construct(
        private AIGate $gate,
        private BudgetGuard $budget,
        private AIProvider $ai,
    ) {}

    public function generate(int $tenantId, int $userId, Carbon $date): string
    {
        $this->gate->check($tenantId, 'sales-summary');

        $sales = Sale::forTenant($tenantId)->on($date)->get(['item', 'qty', 'amount']);
        $prompt = $this->buildPrompt($sales);

        $response = $this->ai->complete(new AIRequest(
            systemPrompt: 'You are a business analyst. Summarise daily sales data concisely.',
            userMessage:  $prompt,
            maxTokens:    400,
        ));

        $this->budget->checkAndRecord($tenantId, $userId, 'sales-summary',
            new AIUsage($response->inputTokens, $response->outputTokens));

        return $response->content;
    }
}
```

---

## Pattern 5: RAG (Retrieval-Augmented Generation)

Use when the AI needs to answer questions about your own data.

```
User Query → Embed query → Vector search → Top-K chunks → Inject into prompt → LLM → Answer
```

**When to use RAG:**
- Policy/procedure Q&A ("What is the leave policy?")
- Large document search (tender documents, legal agreements)
- Knowledge base assistants

**Storage options:** pgvector (PostgreSQL), Pinecone, Qdrant, Chroma

---

## Pattern 6: Function Calling (Structured Actions)

Use when the AI must trigger application actions or return structured data.

```php
$tools = [
    [
        'name'        => 'get_student_grades',
        'description' => 'Retrieve grades for a student',
        'input_schema' => [
            'type'       => 'object',
            'properties' => [
                'student_id' => ['type' => 'integer'],
                'term'       => ['type' => 'string'],
            ],
            'required' => ['student_id'],
        ],
    ],
];
// Pass tools to Claude API; handle tool_use blocks in response
```

---

## Android/Kotlin Implementation

```kotlin
// AI provider via Ktor
class AnthropicClient(private val apiKey: String) {
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) { json() }
    }

    suspend fun complete(request: AIRequest): AIResponse {
        val response: HttpResponse = client.post("https://api.anthropic.com/v1/messages") {
            header("x-api-key", apiKey)
            header("anthropic-version", "2023-06-01")
            contentType(ContentType.Application.Json)
            setBody(request.toApiBody())
        }
        return response.body<AnthropicResponse>().toAIResponse()
    }
}

// Gate check via repository
class AIGateRepository(private val db: AppDatabase) {
    suspend fun isActive(tenantId: Long, feature: String): Boolean =
        db.tenantAIDao().getModule(tenantId)?.isActive == true
}
```

---

## iOS/Swift Implementation

```swift
// AI provider using URLSession
struct AnthropicProvider: AIProvider {
    func complete(request: AIRequest) async throws -> AIResponse {
        var urlRequest = URLRequest(url: URL(string: "https://api.anthropic.com/v1/messages")!)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue(apiKey, forHTTPHeaderField: "x-api-key")
        urlRequest.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request.toAPIBody())

        let (data, _) = try await URLSession.shared.data(for: urlRequest)
        return try JSONDecoder().decode(AnthropicResponseDTO.self, from: data).toAIResponse()
    }
}
```

---

## Architecture Decision Record

When selecting a pattern, document:

```
## AI Architecture Decision — [Feature] — [Date]

Pattern chosen:   [Direct / RAG / Function Calling / Streaming]
Provider:         [Anthropic / OpenAI / DeepSeek / Gemini]
Model:            [specific model ID]
Rationale:        [why this combination]
Gate slug:        [feature_slug used in tenant_ai_features]
Budget impact:    [estimated cost/user/month — link to ai-cost-modeling]
Fallback:         [what happens if provider is unreachable]
```

---

**See also:**
- `ai-metering-billing` — Token Ledger schema and metering middleware
- `ai-feature-spec` — Prompt design and output schema
- `ai-cost-modeling` — Budget cap calculation
- `ai-security` — Input sanitisation and output validation
