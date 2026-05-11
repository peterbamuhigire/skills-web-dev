# Agent Trace Schema (OpenTelemetry)

This is the stable schema every agent trace conforms to. Renaming attributes breaks dashboards and replay; treat as a contract.

## Span Hierarchy

```
agent.task                                                     (root, one per task)
 ├── agent.step.N                                              (one per step, ordered)
 │    ├── agent.llm.{planner|generator|judge|summariser}       (1+ per step)
 │    └── agent.tool.{tool_name}                               (0..1 per step)
 ├── agent.handoff                                             (when handing off to another agent)
 └── agent.approval                                            (when awaiting approval)
```

Multi-agent traces nest: `agent.task` (parent) contains `agent.subtask` spans, each itself parent of its own `agent.step.N` children.

## Common Attributes (set on every span)

| Attribute | Type | Example |
|---|---|---|
| `agent.tenant.id` | int | 42 |
| `agent.user.id` | int | 17 |
| `agent.task.id` | string (ulid) | `tsk_01HXY...` |
| `agent.feature` | string | `support_copilot` |
| `agent.environment` | string | `prod`, `staging`, `sandbox` |
| `agent.region` | string | `eu-west-1` |

## `agent.task` Attributes

| Attribute | Type | Notes |
|---|---|---|
| `agent.task.goal` | string | Sanitised |
| `agent.task.state` | string | terminal state |
| `agent.task.steps.used` | int |  |
| `agent.task.steps.budget` | int |  |
| `agent.task.tokens.in` | int |  |
| `agent.task.tokens.out` | int |  |
| `agent.task.usd.llm` | float |  |
| `agent.task.usd.tool` | float |  |
| `agent.task.usd.total` | float |  |
| `agent.task.wallclock.s` | float |  |
| `agent.task.model_pin` | string |  |
| `agent.task.prompt.version` | string |  |
| `agent.task.tool_set.version` | string |  |
| `agent.task.failure_reason` | string | when state != COMPLETED |
| `agent.task.parent_trace_id` | string | if invoked from another task |

## `agent.step.N` Attributes

| Attribute | Type | Notes |
|---|---|---|
| `agent.step.index` | int | 0-based |
| `agent.step.state_before` | string | PLANNING / ACTING / OBSERVING |
| `agent.step.state_after` | string |  |
| `agent.step.thought.snippet` | string | First 500 chars of planner output |
| `agent.step.plan.kind` | string | `tool_call` / `final` / `handoff` / `needs_approval` |

## `agent.llm.*` Attributes

| Attribute | Type | Notes |
|---|---|---|
| `agent.llm.purpose` | string | `planner` / `generator` / `judge` / `summariser` |
| `agent.llm.model` | string | `claude-x-flagship` |
| `agent.llm.tokens.in` | int |  |
| `agent.llm.tokens.out` | int |  |
| `agent.llm.usd` | float |  |
| `agent.llm.latency_ms` | int |  |
| `agent.llm.cache.hit` | bool | prompt cache hit |
| `agent.llm.provider_request_id` | string | for upstream correlation |
| `agent.llm.seed` | int | when deterministic mode |

## `agent.tool.*` Attributes

| Attribute | Type | Notes |
|---|---|---|
| `agent.tool.name` | string | from registry |
| `agent.tool.version` | string |  |
| `agent.tool.args.hash` | string | sha256 of canonical args |
| `agent.tool.args.size` | int | bytes |
| `agent.tool.observation.size` | int | bytes |
| `agent.tool.status` | string | `ok` / `not_found` / `blocked` / `budget_exceeded` / `error` |
| `agent.tool.latency_ms` | int |  |
| `agent.tool.usd` | float |  |
| `agent.tool.idempotency_key` | string |  |
| `agent.tool.reversibility` | string | `read_only` / `reversible` / `irreversible` |
| `agent.tool.blast_radius` | string |  |
| `agent.tool.dry_run` | bool |  |
| `agent.tool.replay.no_match` | bool | replay only; original trace lacked matching call |

## `agent.handoff` Attributes

| Attribute | Type | Notes |
|---|---|---|
| `agent.handoff.id` | string |  |
| `agent.handoff.from` | string | agent name |
| `agent.handoff.to` | string |  |
| `agent.handoff.trust_level` | string |  |
| `agent.handoff.reason_code` | string |  |
| `agent.handoff.outcome` | string | `accepted` / `rejected` / `expired` |

## `agent.approval` Attributes

| Attribute | Type | Notes |
|---|---|---|
| `agent.approval.id` | int |  |
| `agent.approval.pattern` | string | `single_shot` / `plan_preview` / `jit` / etc. |
| `agent.approval.state` | string | `pending` / `approved` / etc. |
| `agent.approval.decided_by` | int | user_id |
| `agent.approval.decided_at_ms` | int | epoch ms |
| `agent.approval.edits.fields` | list[string] | which fields the user edited |
| `agent.approval.blast_radius` | json | summary of impact |

## Event Records (Span Events)

For things that happen *within* a span:

| Event | When | Attributes |
|---|---|---|
| `agent.budget.checked` | Before each transition | dim, used, limit |
| `agent.budget.breach` | On breach | dim |
| `agent.retry` | Tool call retry | attempt, backoff_ms, reason |
| `agent.injection.detected` | Safety classifier flag | source, score |
| `agent.kill_switch.fired` | Manual kill | actor, reason |

## Redaction Rules

| Attribute | Redaction |
|---|---|
| `agent.task.goal` | Strip emails, phones, names; truncate to 500 chars |
| `agent.step.thought.snippet` | Strip emails, phones; truncate to 500 chars |
| `agent.tool.args.*` | Hash only; raw args go to the redacted I/O store |
| `agent.tool.observation.*` | Size only |
| `agent.llm.prompt.*` | Hash only |

Raw I/O is captured in the separate `agent_tool_io` table with field-level redaction (`ai-agent-observability-and-replay` §3). The trace store holds metadata + hashes.

## Sampling

100% of agent task traces are kept by default. Cost mitigation:
- Drop traces older than 90 days (configurable per tenant).
- Move > 30-day-old traces to cold storage (S3 + queryable archive).
- Always retain traces for tasks that hit FAILED / BUDGET_EXCEEDED / SAFETY events (incident forensics).

## Correlation IDs

- `trace_id` (OTel) — propagated to every downstream call (LLM provider, tool internal API, webhook).
- `parent_trace_id` set on `agent.task` when one task spawns another (handoff or sub-agent).
- `request_id` from the originating API call carried into the trace.
- Tenant-side trace links: every agent task in the customer UI shows a "View trace" deep-link (admin/support only, role-gated).

## Naming Migration

If you must rename an attribute:
1. Emit both old and new names for a deprecation window (60 days).
2. Update dashboards to use new name.
3. Update agent eval to use new name.
4. Drop the old name after the window.

Never rename `agent.task.id` or `agent.tenant.id`. They are the spine.
