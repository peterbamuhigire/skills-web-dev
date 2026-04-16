---
name: ai-web-apps
description: Use when designing or building an AI-enhanced web app (Next.js + Vercel AI SDK, MCP tools, multi-provider chat/RAG) — produces the module gate, token-ledger + budget schema, provider abstraction, and output guardrails. Specialises the integration patterns in `ai-architecture-patterns` for a web-app runtime; hand off metering depth to `ai-metering-billing` and prompt/threat depth to `ai-security` / `llm-security`.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI-Enhanced Web Apps

<!-- dual-compat-start -->
## Use When

- Designing or building an AI-enhanced web app on Next.js + Vercel AI SDK with streaming chat, tool calling, RAG, multi-modal input, or MCP-exposed tools.
- Wiring an AI feature into a multi-tenant SaaS and needing the module gate, token ledger, and provider abstraction for that feature.
- Reviewing an existing AI web-app route for missing budget, quota, guardrail, or fallback controls.

## Do Not Use When

- The AI feature is purely backend or batch (no interactive web surface) — use `ai-llm-integration` or `python-saas-integration` instead.
- The task is a pure UX pattern question — use `ai-ux-patterns` or `ux-for-ai`.
- The task is full metering / billing strategy — use `ai-metering-billing` or `ai-saas-billing`.
- The task is prompt or threat design — use `ai-prompt-engineering`, `ai-security`, or `llm-security`.

## Required Inputs

- Context map, access patterns, and threat model from upstream skills (see Inputs table below).
- Product scope of the AI feature: user job, authority boundary, cost ceiling.

## Workflow

- Read this `SKILL.md`, then load only the deep-dive references needed for the concrete task.
- Apply the decision tables before writing code — architecture first, implementation second.
- Produce the four formal outputs (module gate, token ledger, provider abstraction, guardrails) as named artifacts, not as scattered edits.

## Quality Standards

- Every AI feature is OFF by default and gated at tenant + user + budget.
- Every model call writes a ledger row before the response reaches the user.
- Every structured output is validated by Zod; every rendered output is Markdown-sanitised.
- `maxTokens` is set on every call; fallback is limited to transient provider errors.

## Anti-Patterns

- Fetching API keys in feature code instead of a single provider factory.
- Gating an AI feature on a single flag and calling it done — three gates (entitlement, user, budget) are required.
- Rendering model output through `dangerouslySetInnerHTML` or unsanitised Markdown.

## Outputs

- Module gate contract (feature catalog, tenant flags, kill switch) — see `references/module-gate.md`.
- Token ledger + budget schema — see `references/token-ledger-and-budgets.md`.
- Provider abstraction contract (factory, fallback, request schema) — see `references/provider-abstraction.md`.
- Output validation + guardrail rules — see `references/output-guardrails.md`.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | AI web app integration test plan | Markdown doc covering Next.js + Vercel AI SDK + MCP tool flow tests | `docs/ai/web-app-tests.md` |
| Security | AI web app security note | Markdown doc covering provider-key handling, prompt-injection defense, and per-tenant isolation | `docs/ai/web-app-security.md` |

## References

- See the `References` section below.
<!-- dual-compat-end -->

This skill specialises the generic integration patterns in `ai-architecture-patterns` for a Next.js + Vercel AI SDK runtime. It is the AI-specialist seat in the architecture: it turns a feature concept plus upstream context/threat artifacts into four concrete deliverables the rest of the stack can depend on.

## Prerequisites

Load the following before this skill, in order:

1. `world-class-engineering` — release gates and production bar.
2. `system-architecture-design` — produces the context map and critical-flow table.
3. `database-design-engineering` — produces the access-pattern list that shapes the ledger schema.
4. `vibe-security-skill` — produces the threat model; `ai-security` and `llm-security` extend it for LLMs.

## When this skill applies

- Introducing an AI-powered route, server action, or streaming UI in a Next.js web app.
- Wiring an MCP server or MCP client into an existing web app.
- Adding a new model, provider, or fallback pair to an existing AI feature.
- Bolting a token ledger, budget guard, or kill switch onto a feature that shipped without one.
- Reviewing an AI web-app PR against the house contract (see Outputs).

## Inputs

| Artifact | Produced by | Required? | Why |
|---|---|---|---|
| Context map | `system-architecture-design` | required | names the module boundary the AI feature sits inside |
| Critical-flow table | `system-architecture-design` | required | sets latency + availability budget for the feature |
| Access-pattern list | `database-design-engineering` | required | shapes the ledger, quota, and corpus-retrieval queries |
| Threat model | `vibe-security-skill` / `ai-security` / `llm-security` | required | informs prompt-injection, PII, and abuse controls |
| Auth/authz matrix | `vibe-security-skill` | required | drives the role check inside the module gate |
| SLO set | `observability-monitoring` | optional | calibrates fallback thresholds and kill-switch triggers |
| Pricing / plan catalog | `saas-subscription-mastery` / `subscription-billing` | optional | determines `min_plan_tier` in the feature catalog |

## Outputs

| Artifact | Consumed by | Template |
|---|---|---|
| Module gate contract | `ai-saas-billing`, platform admin UI, feature routes | `references/module-gate.md` |
| Token ledger + budget schema | `ai-metering-billing`, `observability-monitoring`, finance reporting | `references/token-ledger-and-budgets.md` |
| Provider abstraction contract | every AI route, `ai-feature-spec`, `ai-evaluation` | `references/provider-abstraction.md` |
| Output validation + guardrail rules | every AI route, `ai-evaluation`, `ai-security` | `references/output-guardrails.md` |
| Streaming + UI implementation notes | frontend integrators | `references/streaming-and-ui-patterns.md` |
| MCP server/client contract | internal tool owners, `ai-agents-tools` | `references/mcp-integration.md` |

Each of the four formal outputs has a template; other outputs are implementation references.

## Non-negotiables

- AI features ship **OFF**. Enablement is an explicit tenant admin action recorded in audit.
- Every model call writes a ledger row with tenant, user, request, provider, model, tokens, cost, latency, status.
- Every call sets `maxTokens`; cost estimation uses `maxTokens`, not an optimistic expected completion.
- Tool outputs are validated before they influence writes, prompts, or UI.
- Model fallback fires only on transient provider errors (429, 5xx). Never on 4xx input errors.
- Rendered output goes through a Markdown sanitiser; `dangerouslySetInnerHTML` is banned.
- Secrets never reach the browser; `NEXT_PUBLIC_*` for an AI key is a release blocker.

## Decision rules

### When to expose a tool via MCP vs inline `tools:`

```text
Single app, single model, <5 tools             -> inline tools in streamText
Reused across apps or across models             -> MCP server (stdio transport)
Tools require out-of-process credentials        -> MCP server, separate service account
Latency budget <150 ms per tool call            -> inline; MCP handshake adds overhead
```

Wrong choice cost: inline-when-should-be-MCP means every app duplicates the tool surface; MCP-when-should-be-inline pays handshake latency for no composition benefit.

### Provider / model selection (short form)

| Need | First choice | Fallback | Why not the other way |
|---|---|---|---|
| Latency-critical chat, short replies | Gemini Flash | GPT-3.5 | frontier model burns budget on a task that does not need it |
| High-quality reasoning, long tool chains | Claude Sonnet | GPT-4o | flash model hallucinates multi-step chains |
| Cheapest structured extraction | Gemini Flash | GPT-3.5 | frontier cost is a 10–30x multiplier with no quality gain |
| Strict schema adherence (`generateObject`) | GPT-4o | Claude Sonnet (tool-call) | flash models drift from the schema under pressure |
| Residency / on-prem constraint | regional deployment | fail closed | cross-region fallback is a compliance breach |

Full selection table: `references/provider-abstraction.md`.

### Three-gate evaluation order

```text
1. Module gate   (entitlement + enablement + role + consent)
2. Quota gate    (Redis counter, per user per feature per day)
3. Budget guard  (ledger sum + estimated cost vs tenant cap)
4. Execute call  (factory -> model with maxTokens)
5. Ledger write  (onFinish, real tokens + real cost)
6. Guardrails    (structural -> semantic -> render)
```

Skip step 1: free tenants consume paid features. Skip step 2: one user drains tenant cap. Skip step 3: fallback to cheaper model masks runaway spend. Skip step 5: cost attribution breaks; billing disputes become unresolvable. Skip step 6: XSS or bad-data writes reach production.

### Sync route vs queued job

| Signal | Route (streaming) | Queue (background) |
|---|---|---|
| p95 total work | <25 s | >25 s |
| User must see partial output as it arrives | yes | no |
| Multi-step tool chain with web fetches | mixed | queue |
| Result is persisted regardless of UI | optional | queue |
| Retry on failure must be automatic | hard in route | natural in queue |

Wrong choice: running a 90-second multi-tool task in a route blows the 30 s Vercel function cap; running a fast chat through a queue destroys the streaming UX users expect.

### Structural vs semantic vs render guardrail

```text
Zod schema missing          -> silent data corruption downstream
Business rule check missing -> valid-looking nonsense reaches users / DB
Markdown sanitiser missing  -> XSS via model output
```

All three run; skipping any layer imports that layer's failure mode.

## Architecture

```text
User (React UI)
  |
  v  Server Actions / HTTP
Next.js App Router (middleware: CORS, IP rate limit, auth)
  |
  v
Module Gate  ->  Quota Gate  ->  Budget Guard
  |
  v  Provider Factory (allow-listed)
Vercel AI SDK  ----------------------->  OpenAI / Gemini / Anthropic
  |                                       ^
  v                                       |  ai-fallback on 429/5xx
MCP Client (optional)  ---------------->  MCP Server(s) -> internal APIs + vector stores
  |
  v  Guardrails (structural, semantic, render)
Ledger Write (onFinish)  ->  Streaming response back to client
```

The four dashed boxes in this diagram correspond to the four formal outputs. Everything else is glue.

## Core workflow

### 1. Define the AI interaction contract

Write these down before touching code:

- User job to be done and success signal.
- Input shape + size limits + validation (Zod schema).
- Output shape + fallback shape when the model fails (Zod schema).
- Allowed tools, authority boundary per tool, and whether tool results can trigger writes.
- Latency budget (p50, p95) and cost budget per request + per user per day.
- Consent requirement (e.g. data leaving tenant boundary).

This is the `ai-feature-spec` deliverable. This skill consumes it.

### 2. Declare the three gates

Implement the module gate (`references/module-gate.md`) and the quota + budget pair (`references/token-ledger-and-budgets.md`) **before** writing the route. The route wires them together; it does not invent them.

Order in the route:

```text
moduleGate -> quotaGate -> budgetGuard -> factory -> streamText -> guardrails -> ledgerWrite
```

### 3. Centralise the provider

All model access goes through the factory in `references/provider-abstraction.md`. Feature code never imports a provider SDK directly. This is how:

- Cost attribution stays correct (factory is the single place that knows which model is live).
- Fallback stays policy-driven, not ad hoc per route.
- Swapping a provider is a one-file change.

### 4. Stream safely

Streaming gives a great UX and a fragile validation point. Rules:

- Stream raw text to the UI for responsiveness.
- Do not persist or trigger side effects until `onFinish` has validated the final object.
- Validate each tool call's parameters before executing the tool, never after.
- Write the ledger row in `onFinish` with real usage; never use the estimate as the billed amount.

Implementation: `references/streaming-and-ui-patterns.md`.

### 5. Enforce guardrails in three layers

Structural (Zod on `generateObject` and tools), semantic (business rules, PII scrub, confidence thresholds), render (Markdown-only with a sanitiser). Full rules in `references/output-guardrails.md`.

### 6. Observability

Every call logs a single `request_id` that joins the prompt trace, tool calls, and the ledger row. Metrics at minimum:

- `ai.requests_total{feature, model, status}`
- `ai.tokens_total{feature, model, kind=prompt|completion}`
- `ai.cost_micros_total{tenant, feature}`
- `ai.guard_failures_total{guard, feature}`
- `ai.fallback_triggered_total{from_model, to_model}`

Alert on sustained fallback (>5% for 5 min), sustained guard failures (>1% for 10 min), and any tenant crossing 80% of monthly cap.

### 7. Setup

```bash
npm install ai @ai-sdk/openai @ai-sdk/google @ai-sdk/anthropic ai-fallback zod
npm install @modelcontextprotocol/sdk     # if exposing or consuming MCP tools
npm install lru-cache                     # only for dev / single-instance rate limit
```

Production rate limits are Redis-backed (e.g. Upstash); the LRU snippet in `references/streaming-and-ui-patterns.md` is a dev fallback.

## Anti-patterns

- **Reading `OPENAI_API_KEY` directly in a route handler.** Fix: all keys resolve inside `lib/ai/factory.ts`; feature code calls `getSupportedModel(provider, model)` only. A missing key becomes a typed error, not a runtime 500.
- **Shipping an AI feature with a single feature flag.** Fix: three independent gates — `tenant_ai_features.enabled`, `roleMayUseFeature`, `checkBudget`. All three must pass; any one is sufficient to block.
- **Estimating billing cost from the actual completion.** Fix: estimate with `maxTokens` pre-call for the budget guard; record the real usage in the ledger `onFinish`. Estimating with expected completion lets runaway responses blow through the cap.
- **`toDataStreamResponse()` without `maxTokens` on `streamText`.** Fix: `maxTokens` is always set; the budget guard uses the same value. Otherwise a jailbroken prompt can produce a 10 000-token reply on your dime.
- **Rendering AI Markdown with `dangerouslySetInnerHTML` for "formatting".** Fix: render through `react-markdown` + `rehype-sanitize`, disable raw HTML, allow-list link protocols. Direct HTML injection is a live XSS vector.
- **Falling back to a cheaper model on any error.** Fix: fallback only fires on transient provider errors (429, 5xx). A 400 from input validation must surface to the user so they can fix the request; masking it wastes money and hides bugs.
- **Tool result used directly to authorise a write.** Fix: model-driven flows propose; user-driven events dispose. A tool that "sends payment" surfaces a confirmation UI, and the write is triggered by the user clicking confirm, not by the model returning `status: "confirmed"`.
- **MCP client opened per request and never closed.** Fix: close in `onFinish` and on request abort; cache the tool list per worker. Otherwise stdio subprocesses accumulate and the worker OOMs.
- **Quota key using server-local date.** Fix: use the UTC day (`toISOString().slice(0, 10)`). Local-date keys cause midnight races for users in other timezones and let them double their quota on travel days.
- **Prompt includes raw tool output from an untrusted source.** Fix: tag fetched content as `untrusted` in the system prompt, strip to text-only, and never let untrusted content trigger privileged tools in the same turn. See `llm-security` for the trust-tiering pattern.

## Read next

- `skill-composition-standards` — the house style and contract gates this skill implements.
- `ai-architecture-patterns` — the generic integration patterns this skill specialises.
- `ai-security` — prompt-injection defence, PII handling, abuse controls.
- `ai-evaluation` — offline evals, regression tests, AI-as-judge for quality gates.
- `ai-metering-billing` — depth on ledger-to-invoice, unit economics, rev-share models.
- `llm-security` — OWASP Top 10 for LLMs, trust-tiering, instruction hierarchy.
- `ai-feature-spec` — how to write the feature contract this skill consumes.
- `ai-ux-patterns` — streaming UX, confidence indicators, progressive disclosure.
- `nextjs-app-router` — server/client components, middleware, RBAC three-tier.

## References

- `references/module-gate.md` — feature catalog, tenant flags, kill switch, audit, rollout choreography.
- `references/token-ledger-and-budgets.md` — ledger schema, budget guard, quota gate, cost estimation, join queries.
- `references/provider-abstraction.md` — factory, request schema, model selection table, fallback policy.
- `references/output-guardrails.md` — three-layer guardrails, tool-result validation, streaming validation, prompt-injection hooks.
- `references/streaming-and-ui-patterns.md` — streaming route, `useChat`, `streamUI` generators, multi-modal, middleware pipeline, light rate limits.
- `references/mcp-integration.md` — MCP server + client, authority tiers, lifecycle, observability.

*Source base: Despoudis, T. — Build AI-Enhanced Web Apps (Packt, 2024), adapted to the repository contract model.*
