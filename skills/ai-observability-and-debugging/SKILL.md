---
name: ai-observability-and-debugging
description: Use when building the observability stack for AI features in a multi-tenant SaaS — prompt/response tracing, semantic logging, replay tooling, "show me why this answer", per-stage latency/cost breakdown, ticket→trace tie-back, and dashboards that answer the operational questions (which tenant, which feature, which prompt version, which model).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Observability and Debugging
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- A support ticket arrives saying "this answer is wrong" and you need to pull up the exact prompt, model, retrieval state, and reasoning in < 2 minutes.
- Building the AI tracing schema (OTel + custom attributes) so every request can be replayed and explained.
- Wiring debugging surfaces in the back-office and (for some products) tenant-facing "show me why".
- Diagnosing a latency or cost regression with the per-stage breakdown.

## Do Not Use When

- The task is generic platform observability — `observability-monitoring`.
- The task is the eval harness — `ai-eval-harness`.
- The task is the audit log as compliance record — that's a separate lens (`ai-on-saas-architecture` §5).

## Required Inputs

- Gateway emits per-stage spans (`ai-model-gateway`).
- AI audit log writes synchronously per request.
- A trace backend (OTel + Jaeger/Tempo/Honeycomb) and a logs backend.
- Back-office tooling baseline (`saas-admin-backoffice-tooling`).

## Workflow

1. Read this `SKILL.md`.
2. Define the **AI trace schema** (§1) — span names, attributes, conventions.
3. Wire **per-stage spans** in the gateway pipeline (§2).
4. Implement **replay tooling** (§3) — exact reproduction from a trace.
5. Build **"show me why"** surfaces (§4) — per-request explanation.
6. Build **ticket → trace tie-back** (§5) — every customer report links to a trace.
7. Build the **operational dashboards** (§6).
8. Apply anti-patterns (§7).

## Quality Standards

- Every AI request has a single trace covering all stages and the provider call.
- Trace attributes are stable and documented; dashboards never break from renames.
- Replay reproduces the original output deterministically within tolerance (modulo provider non-determinism).
- Support ticket → root-cause time < 15 minutes for typical cases.
- Per-stage latency and cost are queryable; not hidden in unstructured logs.

## Anti-Patterns

- Single span "ai.call" with no breakdown. Latency mystery; no diagnosis.
- Logging full prompts to plaintext logs accessible to all engineers.
- No request_id propagation to the provider — can't correlate provider-side incidents.
- Replay tool that calls live providers — distorts production cost and rate limits.
- Per-tenant dashboards that aggregate everything; no drill into a specific request.
- "Show me why" that's a model-generated rationalisation rather than actual citations + retrieval traces.

## Outputs

- AI trace schema spec.
- Gateway span instrumentation.
- Replay CLI + back-office UI.
- "Show me why" UX patterns.
- Ticket-trace linking workflow.
- Dashboard set.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Trace schema | Markdown | `docs/ai/trace-schema.md` |
| Operability | Replay CLI | Code + docs | `tools/ai/replay.py` |
| Operability | Per-feature ops dashboard | Dashboard link | `docs/ai/dashboards/feature-ops.md` |
| Operability | Triage runbook | Runbook | `docs/runbooks/ai-triage.md` |

## References

- `references/trace-schema.md` — span names, attributes, examples.
- Companion: `ai-on-saas-architecture`, `ai-model-gateway`, `ai-eval-harness`, `ai-prompt-injection-and-tenant-safety`, `observability-monitoring`, `saas-admin-backoffice-tooling`.
- Incident-mode: during a paged AI incident, the trace and replay tooling must support a one-command **evidence bundle export** (`ai-evidence-export --signal <id> --window <range> --output <dir>`) that snapshots state-at-window-end (prompt/model/index/price registries), pulls a stratified sample of failing traces, and generates reproduce scripts. See `ai-incident-evidence-capture/references/evidence-bundle-spec.md` for the schema and `ai-incident-evidence-capture/references/reproduce-script-template.md` for the script generator. The replay tooling must support a "show me everything from <time> for <tenant> on <feature>" mode usable by an on-call engineer at T+5 of an incident.

<!-- dual-compat-end -->

## §1 AI Trace Schema

A standard `ai.*` namespace under OpenTelemetry semantic conventions. See `references/trace-schema.md` for the full schema. Summary:

- Root span: `ai.gateway.request`
- Children: `ai.entitlement`, `ai.kill_switch`, `ai.rate_limit`, `ai.caps`, `ai.prompt.render`, `ai.safety.in`, `ai.retrieval`, `ai.provider.call`, `ai.safety.out`, `ai.cost`, `ai.audit`.
- Attributes on root: `ai.tenant_id`, `ai.feature`, `ai.prompt_id`, `ai.prompt_version`, `ai.model_used`, `ai.region`, `ai.tokens_in`, `ai.tokens_out`, `ai.usd_cost`, `ai.fallback_used`.

## §2 Per-Stage Spans

Each pipeline stage produces a span with:
- `service.name = "llm-gateway"`
- `ai.stage = "<name>"`
- `ai.outcome = "ok|denied|error"`
- duration

```python
with tracer.start_as_current_span("ai.entitlement") as span:
    span.set_attribute("ai.stage", "entitlement")
    span.set_attribute("ai.tenant_id", ctx.tenant_id)
    span.set_attribute("ai.feature", ctx.feature)
    try:
        await entitlements.check(ctx)
        span.set_attribute("ai.outcome", "ok")
    except NotEntitled as e:
        span.set_attribute("ai.outcome", "denied")
        span.set_attribute("ai.denial_key", e.key)
        raise
```

Traces export to OTel; sampled at 100% for AI traces by default (volumes are low enough; signal is critical). Reduce sampling once volume scales.

## §3 Replay

Given a `request_id`, the replay tool:

1. Pulls the full audit row from `ai_requests` + S3 payload.
2. Pulls the resolved binding at the time of the request (snapshot in payload).
3. Reconstructs the exact gateway input.
4. Runs the gateway pipeline in **replay mode**:
   - Real provider call OR replayed provider response (from payload).
   - Same prompt version, same KB partition, same model.
   - Same safety classifier version.
5. Diffs the response with the original; shows differences.

Two modes:
- `--with-provider`: re-issue to provider (costs money; useful for "is this still broken?").
- `--from-cache`: use stored provider response (free; useful for analysing pipeline changes).

CLI: `replay --request-id ai_req_01HXY... --mode from-cache`

Replay is **read-only**; never charges credits, never affects metrics.

## §4 "Show Me Why" Surfaces

Two audiences:

**Back-office operator view:** full trace, payload, retrieval chunks with scores, safety findings, judge-LLM score (if sampled). Filterable by tenant, feature, time, error class. Drill from a customer ticket.

**Tenant admin view (optional, premium):** for each AI answer, an "explain" affordance that shows:
- The retrieval chunks used (with snippets, scores, sources).
- The prompt template id and version.
- The model used.
- The grounding score and citations.

Hide:
- The platform system prompt.
- Any internal classifier scores.
- Cost.

Make tenant-facing explanations always derived from the audit log; never re-generated by the model (that would be the model rationalising, not explaining).

## §5 Ticket → Trace Tie-Back

Every AI feature surfaces a copyable `request_id` (often the last 8 chars) in the UI as a small badge or in a "report issue" flow. The support tool accepts the id and:

1. Resolves the audit row.
2. Renders the operator view.
3. Links to the trace.
4. Links to the replay tool.

For high-volume features, also expose a "feedback?" thumbs-up/down per response, recorded with the `request_id`.

## §6 Dashboards

Standard set per feature:

| Dashboard | Panels |
|---|---|
| Feature ops | QPS, p50/p95/p99 latency by stage, error rate by stage, fallback ratio, abstain rate |
| Cost | USD per hour, per tenant top-20, per model, per feature share |
| Quality | faithfulness, correctness, citation density, judge agreement (rolling) |
| Safety | injection detect rate, output blocks, tool denials, jailbreak suspicions |
| Tenant view | per-tenant requests, cost, errors, denials, top features |

Each panel filterable by time, tenant, region, model, prompt version.

## §7 Anti-Patterns

- Mixing AI traces with general request traces with no namespace — discoverability rot.
- Storing payloads in trace attributes (massive cardinality, cost). Use S3 with a key in attributes.
- Logging full prompt to stdout (printed to log aggregator with no redaction). PII leak.
- No way to see retrieval chunks in the operator UI. Half the diagnosis missing.
- Dashboards built once by a single engineer; no shared template. Drift across features.
- Replay tool that uses the current price table to compute cost on historical replays. Misleading.
- Sampling at < 10% on AI requests. AI volume is usually small enough to keep 100%.

## §8 Agent Trace Patterns

Single-request AI observability is insufficient for agentic features. An agent task is **one trace** spanning many LLM calls and tool calls, often running for minutes or hours. The trace schema, replay tooling, and task-level dashboards live in `ai-agent-observability-and-replay`.

Key differences from request-level traces:

| Dimension | Request | Agent task |
|---|---|---|
| Trace lifetime | seconds | seconds to days |
| Spans per trace | 5-20 | 50-500+ |
| Replay | re-call with same inputs | re-run loop with mocked tool I/O |
| Failure modes | latency, content, cost | + step-loop, hallucinated tool args, off-script irreversibles, deadlock |
| Dashboards | per-request metrics | per-task metrics: success rate, intervention rate, step efficiency |

Required schema additions when agents are in scope — root span `agent.task` with attributes for `agent.task.id`, `agent.feature`, `agent.prompt.version`, `agent.tool_set.version`, `agent.task.steps.used/budget`, `agent.task.usd.total`, `agent.task.terminal.state`. Per-step child spans `agent.step.N`. Per-LLM-call and per-tool-call sub-spans. Special spans: `agent.handoff`, `agent.approval`. Full schema: `ai-agent-observability-and-replay/references/trace-schema-agent.md`.

Required dashboards: per-feature task success rate, intervention rate, irreversible-action rate, step efficiency, median cost per completed task; per-tenant agent task volume, agent cost share, wasted-spend share; top-10 tasks by cost in last hour; failure-mode distribution.

Required replay surface: per-task replay re-running a recorded task with candidate prompt/model/tool version; side-by-side step diff; never call live tools in replay.

## §9 Read Next

- `ai-agent-observability-and-replay` — the **agent-specific** complement with full trace schema, replay tooling, task viewer, and "what would the agent do differently" debugger.
- `ai-agent-runtime-architecture` — emits the task-level trace events.
- `ai-agent-eval` — consumes traces for replay-based eval.
- `ai-on-saas-architecture` — control-plane positioning.
- `ai-model-gateway` — instrumented from.
- `ai-eval-harness` — surfaces quality signal to dashboards.
- `ai-prompt-injection-and-tenant-safety` — safety signals to dashboards.
- `observability-monitoring` — broader observability.
- `saas-admin-backoffice-tooling` — operator UI.
## Consolidated Child References

- Load [references/routing.md](references/routing.md) to map retired AI child skill slugs to their reference modules.

