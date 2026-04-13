---
name: microservices-ai-integration
description: Integrating AI into a microservices architecture — AI model server as
  a microservice, AI gateway pattern, async AI job pipeline, AI-enhanced orchestration
  (Kubeflow, Seldon Core), and wiring the AI metering/billing layer into a distributed...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Microservices AI Integration

<!-- dual-compat-start -->
## Use When

- Integrating AI into a microservices architecture — AI model server as a microservice, AI gateway pattern, async AI job pipeline, AI-enhanced orchestration (Kubeflow, Seldon Core), and wiring the AI metering/billing layer into a distributed...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `microservices-ai-integration` or would be better handled by a more specific companion skill.
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
## The Central Pattern

Treat AI as a dedicated, independently deployable microservice — the **AI Service**. All AI API calls from across the system route through it. This service enforces the AI Module Gate, Token Budget Guard, and Token Ledger (from `ai-architecture-patterns`) at a single, auditable point.

```
[Any Service] → [AI Gateway] → [AI Service] → [External AI Provider API]
                     ↓               ↓
               Gate Check      Token Ledger
               Budget Guard    ai_usage_log
```

---

## Architecture: AI as a Microservice

### The AI Service Contract

The AI Service is the only service that talks to external AI provider APIs (Anthropic, OpenAI, DeepSeek, Gemini). All other services call the AI Service — never the external API directly.

**Why:**
- Single point for API key management (not distributed across services).
- Token metering happens in one place — no double-counting.
- Model swapping affects one service, not every caller.
- Rate limiting and budget enforcement centralised.

### API Design

```
POST /ai/complete
{
  "tenant_id": 42,
  "user_id": 101,
  "feature_slug": "sales-summary",
  "model": "claude-haiku-4-5",
  "system_prompt": "You are a sales analyst...",
  "user_message": "Summarise today's sales: ...",
  "max_tokens": 400
}

→ 200 OK
{
  "content": "Today's total sales were UGX 2,450,000...",
  "input_tokens": 312,
  "output_tokens": 87,
  "cost_usd": 0.000598,
  "request_id": "req_abc123"
}

→ 402 Payment Required (budget exhausted)
{ "error": "ai_budget_exceeded", "message": "Monthly AI budget exhausted for tenant 42" }

→ 403 Forbidden (module not active)
{ "error": "ai_module_inactive", "message": "AI module not activated for tenant 42" }
```

### PHP/Laravel AI Service Implementation

```php
// app/Http/Controllers/AICompletionController.php
class AICompletionController extends Controller
{
    public function complete(AICompletionRequest $request, AIMeteredClient $client): JsonResponse
    {
        try {
            $response = $client->call(
                tenantId:    $request->tenant_id,
                userId:      $request->user_id,
                featureSlug: $request->feature_slug,
                request:     new AIRequest(
                    model:        $request->model,
                    systemPrompt: $request->system_prompt,
                    userMessage:  AIInputSanitiser::sanitise($request->user_message),
                    maxTokens:    $request->max_tokens ?? 1024,
                )
            );

            return response()->json([
                'content'      => AIOutputValidator::sanitiseText($response->content),
                'input_tokens' => $response->inputTokens,
                'output_tokens'=> $response->outputTokens,
                'cost_usd'     => $response->costUsd,
                'request_id'   => $response->requestId,
            ]);

        } catch (AIModuleNotActiveException $e) {
            return response()->json(['error' => 'ai_module_inactive', 'message' => $e->getMessage()], 403);
        } catch (AIBudgetExceededException $e) {
            return response()->json(['error' => 'ai_budget_exceeded', 'message' => $e->getMessage()], 402);
        }
    }
}
```

---

## Async AI Job Pipeline

For AI features where response time exceeds 3s (report generation, batch analysis, document extraction), use an async queue pattern.

```
User Request → POST /reports/generate
             → 202 Accepted { "job_id": "job_xyz" }
             → Job dispatched to ai-reports queue

Worker Service → dequeues job
               → calls AI Service (POST /ai/complete)
               → stores result in reports table
               → publishes ReportCompleted event

User polls → GET /reports/job_xyz/status
           → { "status": "complete", "download_url": "/reports/job_xyz/download" }
```

**Or push-based with WebSocket/SSE:**
```
Worker publishes ReportCompleted event
→ notification-service listens
→ pushes in-app notification to user ("Your report is ready")
```

### Laravel Queue Implementation

```php
// Dispatching the AI job
class GenerateReportController extends Controller
{
    public function generate(Request $request): JsonResponse
    {
        $job = AIReportJob::create([
            'tenant_id' => $request->tenant_id,
            'user_id'   => $request->user_id,
            'params'    => $request->params,
            'status'    => 'queued',
        ]);

        dispatch(new ProcessAIReportJob($job->id))->onQueue('ai-reports');

        return response()->json(['job_id' => $job->id, 'status' => 'queued'], 202);
    }
}

// The queued job
class ProcessAIReportJob implements ShouldQueue
{
    use InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public int $timeout = 60; // 60s max per attempt

    public function handle(): void
    {
        $job = AIReportJob::findOrFail($this->jobId);
        $job->update(['status' => 'processing']);

        $response = Http::timeout(30)->post('http://ai-service/ai/complete', [
            'tenant_id'   => $job->tenant_id,
            'user_id'     => $job->user_id,
            'feature_slug'=> 'report-generation',
            'model'       => 'claude-haiku-4-5',
            'system_prompt' => '...',
            'user_message'  => $this->buildPrompt($job->params),
            'max_tokens'    => 2000,
        ]);

        $job->update([
            'status'  => 'complete',
            'result'  => $response->json('content'),
            'cost_usd'=> $response->json('cost_usd'),
        ]);

        event(new AIReportCompleted($job->tenant_id, $job->user_id, $job->id));
    }

    public function failed(\Throwable $e): void
    {
        AIReportJob::find($this->jobId)?->update(['status' => 'failed', 'error' => $e->getMessage()]);
    }
}
```

---

## AI Gateway Pattern

Layer the AI Service behind the API gateway to enforce:
- Per-tenant rate limiting on AI endpoints (separate limit from regular API)
- AI-specific authentication (service-to-service API key)
- Circuit breaker for the AI Service itself (if AI Service is slow/down)
- Routing to different AI Service instances by feature type

```nginx
# NGINX — AI Service upstream with circuit breaker
upstream ai_service {
    least_time last_byte;
    server ai-service-1.internal:8080;
    server ai-service-2.internal:8080;
}

location /ai/ {
    # Rate limit: 100 AI requests per minute per tenant
    limit_req zone=ai_per_tenant burst=20 nodelay;

    proxy_pass http://ai_service;
    proxy_read_timeout 60s;  # AI calls can be slow

    # Circuit breaker via health check
    health_check uri=/health interval=5s fails=1;
}
```

---

## AI-Enhanced Orchestration

*Source: Pandiya & Charankar Ch. 3*

AI can enhance the orchestration layer of a microservices system:

### Predictive Scaling
AI analyses historical traffic patterns to pre-scale services before load spikes.
- Tool: Kubernetes + Kubeflow Pipelines
- Kubeflow is an ML toolkit for Kubernetes — runs ML workflows alongside services

### AI-Assisted Fault Tolerance
AI models predict which service instances are likely to fail before they do, triggering preemptive migration.
- Input: CPU trend, memory growth rate, error rate over last 10 minutes
- Output: probability of failure in next 15 minutes → if > 0.8, migrate load

### Seldon Core — AI Model Serving as a Microservice
Seldon Core extends Kubernetes to serve ML models as REST/gRPC services with the same lifecycle as any other microservice (canary deployments, A/B testing, traffic splitting).

```yaml
# Seldon Deployment — serve a scikit-learn model
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: risk-predictor
spec:
  predictors:
  - name: default
    graph:
      name: risk-model
      implementation: SKLEARN_SERVER
      modelUri: gs://my-bucket/risk-model
    replicas: 2
    traffic: 100
```

**When to use Seldon Core:** When you have a custom ML model (not a foundation model) that needs to scale, version, and update independently.

---

## Wiring AI Metering in a Microservices Context

In a distributed system, metering must still be centralised (at the AI Service). Services must not try to record their own token usage.

**Rule:** The AI Service is the sole writer to `ai_usage_log`. All other services are readers (for their own tenant/user data via the usage API).

```
finance-service  ──┐
enrollment-service ├── POST /ai/complete → AI Service writes to ai_usage_log
report-service   ──┘

admin-service → GET /ai/usage?tenant_id=42&period=2026-04 → AI Service reads usage
```

**Usage API in the AI Service:**
```
GET /ai/usage?tenant_id=42&period=2026-04&group_by=user
→ { "period": "2026-04", "users": [ { "user_id": 101, "calls": 82, "tokens": 14500, "cost_usd": 0.0234 } ] }

GET /ai/usage/tenants?period=2026-04   (super-admin only)
→ [ { "tenant_id": 42, "tier": "growth", "budget_usd": 10.00, "spent_usd": 3.21, "pct_used": 32.1 } ]
```

---

## Resilience for the AI Service

The AI Service is a critical dependency. Apply extra resilience:

- **Circuit breaker** on the AI Service itself at the gateway level.
- **Queue-based fallback:** If AI Service is down, synchronous callers get a `503` immediately; async callers' jobs remain in queue and are processed when service recovers.
- **Provider failover:** If primary AI provider (Anthropic) is unreachable, automatically fall back to secondary (OpenAI or DeepSeek) — log the switch to the audit log.
- **Budget hard stop:** Never retry a request that failed with `402 Budget Exceeded` — the budget is not a transient error.

---

## Microservices AI Integration Checklist

- [ ] One AI Service handles all external AI API calls — no other service calls AI APIs directly.
- [ ] AI Module Gate and Budget Guard enforced at AI Service.
- [ ] All AI calls recorded to `ai_usage_log` before response returned.
- [ ] Long-running AI features use async queue (not synchronous HTTP).
- [ ] AI gateway rate-limits AI endpoints separately from regular API.
- [ ] Circuit breaker configured for the AI Service upstream.
- [ ] Provider failover configured (primary → secondary model).
- [ ] AI Service `/health` endpoint checks provider reachability.

---

**See also:**
- `ai-architecture-patterns` — AI Module Gate, Budget Guard, Token Ledger detail
- `ai-metering-billing` — Token ledger schema and billing
- `microservices-resilience` — Circuit breaker and health check implementation
- `microservices-communication` — Async queue pattern for AI jobs
