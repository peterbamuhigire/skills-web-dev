> Consolidated from skills/ai-agent-observability-and-replay/SKILL.md into ai-agent-observability-evaluation on 2026-05-13. Load this through skills/ai-agent-observability-evaluation/SKILL.md, not as an active skill entrypoint.

# AI Agent Observability and Replay
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing the **trace schema for agent tasks** (one trace = one task; sub-spans = steps; sub-sub-spans = LLM call, tool call).
- Wiring tool I/O capture so support can see exactly what the agent did in < 2 minutes.
- Building **deterministic replay** so a recorded task can be re-run with a new prompt/model/tool version.
- Building "what would the agent do differently" debugging — given a trace, run it through a candidate config and surface the diff.
- Wiring the agent inbox and admin console to per-task traces.

## Do Not Use When

- The task is single-request AI observability — `ai-observability-and-debugging`.
- The task is the eval pipeline — `ai-eval-harness`, `ai-agent-eval`.
- The task is general OTel setup — `observability-monitoring`.

## Required Inputs

- Agent runtime emitting spans per step (`ai-agent-runtime-architecture`).
- LLM gateway emitting cost+tokens per call (`ai-model-gateway`).
- Tool registry (`ai-agent-tool-catalogue-and-action-gating`).
- Trace backend (Honeycomb/Tempo/Jaeger), logs backend, dashboard tool.

## Workflow

1. Read this `SKILL.md`.
2. Define the **agent trace schema** (§1). See `references/trace-schema-agent.md`.
3. Implement **per-step span emission** in the runtime (§2).
4. Implement **tool I/O capture** with sensitive-field redaction (§3).
5. Build the **task viewer** in the admin console (§4).
6. Build **deterministic replay** (§5).
7. Build "**what would the agent do differently**" debugging (§6).
8. Wire **task-level dashboards** (§7).
9. Apply anti-patterns (§8).

## Quality Standards

- Every agent task has exactly one parent trace; every step is a child span; every LLM call and every tool call is a sub-span of its step.
- Tool I/O is captured for every call. Sensitive fields are redacted at capture; raw values are never persisted in trace storage.
- The task viewer renders a complete task in < 3 seconds for tasks up to 100 steps.
- Deterministic replay reproduces the original tool I/O exactly; LLM calls are seeded where provider supports.
- "What would the agent do differently" diff highlights step-level divergence: same input, different tool chosen, different args, different terminal state.
- Task-level dashboards answer: which features fail most, which tenants are most expensive, which tools fail most often, what's the median time-to-completion.

## Anti-Patterns

- One span "agent.task" with no breakdown. Useless for debugging.
- Tool args captured in plaintext including PII / secrets. Trace store becomes a compliance liability.
- Replay calls live tools. Charges real cards.
- "Show me why" surface that just dumps the LLM's chain-of-thought. Not enough; need the structured trace.
- Trace storage with no retention policy. GDPR exposure; unbounded cost.
- Task-level dashboards aggregate across tenants only; no drill into a single task.
- Per-step spans missing `tool.version` and `prompt.version`. Replay impossible.

## Outputs

- OTel trace schema for agent tasks.
- Per-step span emission in the runtime.
- Tool I/O capture + redaction.
- Task viewer (admin / support).
- Deterministic replay implementation.
- "What would differ" debugger.
- Task-level dashboards.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Agent trace schema | Markdown | `docs/ai/agent-trace-schema.md` |
| Operability | Task viewer screenshot + spec | Markdown + image | `docs/ai/task-viewer.md` |
| Release evidence | Replay correctness tests | CI report | `tests/ai/replay/` |
| Compliance | Redaction rules + sample | Markdown | `docs/ai/trace-redaction.md` |

## References

- `references/trace-schema-agent.md` — full OTel schema and conventions.
- Companion: `ai-observability-and-debugging`, `ai-agent-runtime-architecture`, `ai-agent-eval`, `ai-model-gateway`, `observability-monitoring`, `saas-admin-backoffice-tooling`.

<!-- dual-compat-end -->

## §1 Trace Schema

```
trace: agent.task
  span: agent.task                        (root)
    attributes:
      agent.task.id, agent.tenant.id, agent.feature, agent.model_pin,
      agent.prompt.version, agent.tool_set.version, agent.steps.budget,
      agent.steps.used, agent.usd.total, agent.terminal.state
    span: agent.step.0
      attributes: state_before, state_after, step.index
      span: agent.llm.plan
        attributes: model, tokens_in, tokens_out, usd, latency_ms
      span: agent.tool.{tool_name}
        attributes: tool.version, args.hash, status, latency_ms, usd, idempotency_key
    span: agent.step.1
      ...
```

Convention: span names are stable strings; attribute keys are dotted; redaction is applied at attribute set time.

Full schema in `references/trace-schema-agent.md`.

## §2 Per-Step Span Emission

```python
def run_step(task):
    with tracer.start_as_current_span(f"agent.step.{task.steps_used}") as step:
        step.set_attribute("step.index", task.steps_used)
        step.set_attribute("state_before", task.state)
        plan = call_planner(task)
        step.set_attribute("plan.kind", plan.kind)
        if plan.kind == "tool_call":
            result = execute_tool(plan.tool, plan.args, task)
            step.set_attribute("tool.name", plan.tool)
            step.set_attribute("tool.version", registry.get(plan.tool).version)
            step.set_attribute("tool.args.hash", hash_args(plan.args))
            step.set_attribute("tool.status", result["status"])
        elif plan.kind == "final":
            step.set_attribute("response.length", len(plan.response))
        step.set_attribute("state_after", task.state)
```

## §3 Tool I/O Capture and Redaction

Tool args and observations are captured to a separate store (not the trace attributes — they would blow attribute size limits and leak):

```sql
CREATE TABLE agent_tool_io (
  id              BIGINT PRIMARY KEY,
  task_id         BIGINT NOT NULL,
  step_index      INT NOT NULL,
  tenant_id       BIGINT NOT NULL,
  tool_name       VARCHAR(128) NOT NULL,
  args_redacted   JSON NOT NULL,
  observation_redacted JSON NOT NULL,
  args_hash       CHAR(64) NOT NULL,
  retained_until  DATETIME NOT NULL,
  INDEX (task_id, step_index)
);
```

Redaction rules:

| Pattern | Redaction |
|---|---|
| Email-shaped field (`to`, `email`, `cc`) | `<EMAIL_HASH:xxxx>` |
| Card / bank-account-shaped | `<PAN_HASH:xxxx>` |
| Long free text in `body`, `message`, `notes` | Keep first 500 chars + length; rest replaced with `<TRUNCATED>` |
| Custom PII-tagged fields (per schema annotation) | Replace with `<REDACTED>` |
| Customer IDs | Keep (needed for support) |

Retention: 90 days default. Configurable per tenant (Enterprise can ask for longer; legal hold extends).

## §4 Task Viewer

Admin / support UI per task:

```
┌─ Task tsk_abc123 ─────────────────────────────────────────────────────┐
│ Tenant: ACME  Feature: support_copilot  State: COMPLETED              │
│ Steps: 6 / 12   Tokens: 8.4k   Cost: $0.18   Wallclock: 14s           │
│ Model: claude-x-flagship v2  Prompt: v2.3  Tools: v1.5                │
│ Trace: [open in Honeycomb]   Replay: [run with...]                    │
├───────────────────────────────────────────────────────────────────────┤
│ User: "I think I was charged twice..."                                │
│                                                                       │
│ ▼ Step 1 — PLANNING — 280ms / $0.02                                   │
│   thought: "Need to check both invoices. Will look up charges."       │
│   plan: call charge_lookup(invoice_id=1234)                           │
│                                                                       │
│ ▼ Step 2 — ACTING — 320ms                                              │
│   tool: charge_lookup  args: {invoice_id: 1234}                       │
│   observation: {amount: $89, status: paid, charged_at: ...}           │
│                                                                       │
│ ▼ Step 3 — ACTING — 290ms                                              │
│   tool: charge_lookup  args: {invoice_id: 1235}                       │
│   observation: {amount: $89, status: paid, note: "second charge"}     │
│                                                                       │
│ ▼ Step 4 — PLANNING — 420ms / $0.03                                   │
│   thought: "Both same amount within 2 min. Likely duplicate.          │
│            Will check KB for refund policy then propose refund."      │
│                                                                       │
│ ▼ Step 5 — AWAITING_APPROVAL                                          │
│   tool proposed: payment_refund  args: {invoice_id: 1235, amount: 89} │
│   approval: APPROVED by user@acme  at 10:00:34Z                       │
│                                                                       │
│ ▼ Step 6 — ACTING — 1.2s                                              │
│   tool: payment_refund  args: {invoice_id: 1235, amount: 89}          │
│   observation: {status: ok, refund_id: rf_...}                        │
│                                                                       │
│ ✓ COMPLETED                                                           │
│ Final response: "I've refunded $89 for invoice 1235. The original     │
│   charge for 1234 is unchanged. You'll see the refund in 5-7 days."   │
└───────────────────────────────────────────────────────────────────────┘
```

Filterable, searchable. Linked from support ticket → trace.

## §5 Deterministic Replay

Given a `task_id`, re-execute the task with the same or a candidate config:

```python
def replay(task_id, candidate=None, mock_tools=True):
    original = load_full_trace(task_id)
    runtime = build_runtime(
        prompt_version=candidate.prompt if candidate else original.prompt_version,
        model_pin=candidate.model if candidate else original.model_pin,
        tool_runtime=ReplayToolRuntime(original.steps) if mock_tools else live_tool_runtime,
        budgets=original.budgets,
    )
    new_trace = runtime.run(original.goal, ctx=original.context)
    return diff(original, new_trace)
```

`mock_tools=True` is mandatory in production replay UI — never re-execute side effects.

LLM calls use the provider's `seed` parameter where supported. Non-determinism residual (top-k sampling) is acceptable; replay aims for "close enough for diagnosis".

## §6 "What Would Differ" Debugger

A side-by-side view:

```
Original (trace tsk_abc)          | Candidate (prompt v2.4)
----------------------------------|----------------------------------
Step 1: charge_lookup(1234)       | Step 1: charge_lookup(1234)
Step 2: charge_lookup(1235)       | Step 2: charge_lookup(1235)
Step 3: kb_search("refund")       | Step 3: payment_refund(1235, 89)  ⚠ off-script irreversible
Step 4: payment_refund(1235, 89)  | (terminal — completed in 3 steps)
Step 5: respond(...)              |
```

Highlights:
- Step-level alignment by canonical signature.
- Off-script irreversibles flagged red.
- Step count delta.
- Cost delta.
- Final response diff (text diff).

This is the engineering surface for prompt-tuning, model upgrades, and tool changes.

## §7 Task-Level Dashboards

| Dashboard | What it answers |
|---|---|
| Feature health | Per-feature success rate, intervention rate, median cost, p90 cost over time |
| Tenant cost (agent share) | Per-tenant agent cost / total AI cost; outliers |
| Tool reliability | Per-tool error rate, p90 latency, budget-block rate |
| Trajectory length | Distribution of steps used per feature; outliers |
| Approval flow | Approval rate, time-to-decide median, edit rate per feature |
| Failure modes | Top reasons for FAILED / BUDGET_EXCEEDED / ABANDONED |

Every dashboard links into the task viewer for drill-down.

## §8 Anti-Patterns

- Single span per task. Cannot diagnose.
- Tool args in plaintext. PII / cards in traces.
- Replay calls live tools. Charges customers in support sessions.
- Task viewer that times out on tasks with > 50 steps. Long-running tasks become opaque.
- No retention policy on traces. Cost + compliance disaster.
- "Show me why" surface that's just the LLM's chain-of-thought, no tool spans. Misleading.
- Dashboards that aggregate without drill-down. Trends without diagnosis.


