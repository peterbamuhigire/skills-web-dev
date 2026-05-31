---
name: ai-agent-runtime-architecture
description: Use when designing the runtime that hosts agentic LLM features in a multi-tenant SaaS â€” the agent loop as a control-plane service, formal state machine (PERCEIVE â†’ PLAN â†’ ACT â†’ OBSERVE), retries, idempotency, max-step caps, deterministic resumability, and the "agent vs workflow vs cron" decision. Distinct from `ai-agents-tools` (agent fundamentals) and `ai-on-saas-architecture` (overall AI architecture).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Runtime Architecture
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Standing up an agent runtime as a **control-plane service**, not as a function inside a web request.
- Deciding whether the work is an agent (LLM plans), a deterministic workflow (no LLM in the loop), or a cron (scheduled).
- Designing the state machine so a crashed worker can resume a 30-minute task without re-charging the customer.
- Adding step caps, wallclock caps, and idempotency so a runaway agent cannot spend USD 40k of provider budget overnight.
- Wiring agent task lifecycle events (`agent.task.started`, `agent.step.completed`, `agent.task.paused`, `agent.task.killed`, `agent.task.completed`) for observability and back-office.

## Do Not Use When

- The task is the fundamentals of the ReAct loop / tool contract â€” `ai-agents-tools`.
- The task is the multi-agent coordination pattern â€” `ai-agent-multi-agent-coordination`.
- The task is long-running (hours-to-days) durability and progress UX â€” `ai-agent-async-and-long-running-tasks` builds on this skill.
- The task is the overall AI architecture â€” `ai-on-saas-architecture`.

## Required Inputs

- The AI on SaaS architecture decision (`ai-on-saas-architecture`) â€” gateway, audit log, prompt registry.
- The agent feature catalogue (which features are agentic, which are single-shot).
- The plan / tier catalogue with agent entitlements (`ai-entitlements-and-feature-gating`).
- Tenant-aware queue / worker infrastructure (`distributed-systems-patterns`, `reliability-engineering`).
- The eval and red-team posture (`ai-agent-eval`, `ai-agent-safety-and-red-team`).

## Workflow

1. Read this `SKILL.md`.
2. Apply the **agent vs workflow vs cron decision** (Â§1). Reject "agent" as the default. Many agentic features are actually workflows with an LLM step.
3. Design the **agent loop state machine** (Â§2) with explicit states and idempotent transitions.
4. Pick the **execution substrate** (Â§3) â€” inline / queue worker / durable execution engine â€” based on max wallclock and resumability requirements.
5. Wire **step / token / wallclock / cost budgets** (Â§4) into the loop (delegates to `ai-agent-cost-and-step-budgets` for full enforcement).
6. Make every step **idempotent and resumable** (Â§5).
7. Emit **task lifecycle events** (Â§6) for observability, back-office, and customer-facing UI.
8. Apply anti-patterns (Â§7).

## Quality Standards

- The agent runtime is a **separate deployment** from request-serving web/API workers. Crash-isolated.
- Every task has a `task_id`, `tenant_id`, `feature`, `model_pin`, `prompt_version`, `tool_set_version`, `step_budget`, `wallclock_budget`, `cost_budget`, `created_at`, `state`.
- Every step writes a row to `agent_steps` with `step_index`, `state_before`, `action`, `observation`, `tokens`, `usd_cost`, `latency_ms` before the next step runs.
- A worker crash mid-step does **not** re-execute irreversible actions on restart â€” idempotency keys are mandatory on side-effects.
- A task that exceeds any budget is **terminated cleanly**, emits `agent.task.budget_exceeded`, and surfaces in the agent inbox.
- Every task has a **per-tenant kill-switch** the back-office can flip in < 5 seconds (`ai-agent-safety-and-red-team`, `saas-admin-backoffice-tooling`).
- An agent task is **never** started inside an HTTP request handler with `max_execution_time > 30s`. Always queued.

## Anti-Patterns

- "Agent" implemented as a `while (not_done) { call_llm(); execute_tool(); }` inside a Flask/Express request handler. First failure leaves orphan side-effects.
- No state machine. Worker restart re-plans from scratch and re-sends the email it already sent.
- No idempotency keys on tools. Retried `send_email` sends twice.
- No max-step cap (`maxSteps` not enforced or set to 100). One bad prompt drains USD-thousands.
- Step / token / wallclock budgets only logged, not enforced. Logging is not a control.
- Agent loop and tool execution in the same process as the web app. A runaway agent OOMs the API.
- No `feature` or `prompt_version` recorded on the task row. Replay impossible.

## Outputs

- Agent vs workflow vs cron decision table for every candidate feature.
- `agent_tasks` and `agent_steps` table schemas.
- State-machine diagram + transitions.
- Execution substrate decision (inline / queue / Temporal-class) with rationale.
- Budget enforcement integration points.
- Task lifecycle event taxonomy.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Agent runtime service spec | Markdown + diagram | `docs/ai/agent-runtime.md` |
| Correctness | State-machine transition test suite | CI report | `tests/ai/agent_state_machine_test.py` |
| Release evidence | Resumability drill report | Markdown | `docs/runbooks/agent-resumability-drill.md` |
| Operability | Task lifecycle event taxonomy | YAML | `ops/events/agent-task-events.yaml` |

## References

- `references/agent-loop-state-machine.md` â€” formal state machine, transitions, idempotency contract.
- `references/agent-vs-workflow-vs-cron-decision.md` â€” decision matrix with worked examples.
- `references/agentic-ai-operating-model-source-synthesis.md` - autonomy ladder, production spine, tool contracts, memory/RAG discipline, multi-agent roles, deployment stages, and human-agent operating model distilled from supplied agentic AI source material.
- Companion: `ai-agents-tools`, `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-cost-and-step-budgets`, `ai-agent-observability-and-replay`, `ai-agent-async-and-long-running-tasks`, `ai-on-saas-architecture`, `distributed-systems-patterns`, `reliability-engineering`.

<!-- dual-compat-end -->

## Â§1 Agent vs Workflow vs Cron â€” The First Decision

Most "we need an agent" requests are **workflows in disguise**. An agent is *only* the right tool when:

- The steps cannot be enumerated in advance.
- Branching depends on intermediate observations only the LLM can interpret.
- Tool choice itself depends on the observation, not the input.

If steps are fixed, **prefer a workflow** â€” same LLM calls, deterministic order, vastly cheaper to test, debug, and operate. See `references/agent-vs-workflow-vs-cron-decision.md`.

## Â§2 The Agent Loop State Machine

```
                â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       enqueue  â”‚   QUEUED     â”‚
                â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
                       â”‚ worker claims
                       â–¼
                â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                â”‚   PLANNING   â”‚ â—„â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜                â”‚
                       â”‚ plan emitted           â”‚ revise plan
           needs HITL? â”‚                        â”‚
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”               â”‚
              â–¼                 â–¼               â”‚
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”‚
       â”‚ AWAITING_    â”‚  â”‚   ACTING     â”‚       â”‚
       â”‚  APPROVAL    â”‚  â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚
       â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜         â”‚ tool result   â”‚
              â”‚ approved/       â–¼               â”‚
              â”‚ rejected â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”‚
              â””â”€â”€â”€â”€â”€â”€â”€â”€â–º â”‚  OBSERVING   â”‚â”€â”€â”€â”€â”€â”€â”€â”˜ continue
                         â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
                                â”‚ done
                                â–¼
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚  COMPLETED   â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

Terminal states: `COMPLETED`, `FAILED`, `BUDGET_EXCEEDED`, `KILLED`, `ABANDONED`.

All state transitions write to `agent_steps` *before* the next state is entered. A worker crash between two steps re-enters the loop in the last persisted state. See `references/agent-loop-state-machine.md`.

## Â§3 Execution Substrate

| Wallclock cap | Resumability requirement | Substrate |
|---|---|---|
| < 30s | Best-effort | Inline in HTTP request (only for read-only agents) |
| < 5 min | At-least-once | Queue worker (BullMQ, Celery, RQ, Sidekiq) |
| < 1 hour | Exactly-once | Durable workflow engine (Temporal, Inngest, Restate) |
| Hours / days | Exactly-once + resume on deploy | Durable workflow engine, mandatory |

For anything writing to customer state, **never** run inline in the HTTP handler. The customer's request times out and the agent keeps spending.

## Â§4 Budgets Wired Into the Loop

Before entering `PLANNING` and `ACTING`, the loop checks four budgets:

| Budget | Check point | Action on exceed |
|---|---|---|
| `step_budget` (max iterations) | Before each `PLANNING` | Transition to `BUDGET_EXCEEDED`, emit event, summarise progress |
| `wallclock_budget_seconds` | Before each state transition | Same |
| `cost_budget_usd` | After each LLM call | Same |
| `tool_cost_budget_usd` | Before each `ACTING` | Same |

Budgets come from `ai-agent-cost-and-step-budgets`. The runtime is the **enforcement point**.

## Â§5 Idempotency and Resumability

Every side-effecting tool call carries an idempotency key derived from `(task_id, step_index, tool_name, arg_hash)`. If a worker crashes after the side-effect but before persistence, the next worker's tool call short-circuits to the recorded result.

```python
def execute_tool_with_idempotency(task_id, step_idx, tool_name, args):
    idem_key = sha256(f"{task_id}:{step_idx}:{tool_name}:{stable_json(args)}")
    cached = idempotency_store.get(idem_key)
    if cached:
        return cached  # tool already ran; replay the recorded observation
    result = tools[tool_name].run(args, idempotency_key=idem_key)
    idempotency_store.put(idem_key, result, ttl_days=30)
    return result
```

Tools that cannot accept an idempotency key (legacy APIs) must be wrapped in an outbox pattern with a deduplication table. See `distributed-systems-patterns`.

## Â§6 Task Lifecycle Events

| Event | When | Used by |
|---|---|---|
| `agent.task.created` | Enqueue | Audit log, observability |
| `agent.task.started` | Worker claims | Observability, agent inbox UI |
| `agent.step.completed` | After OBSERVING | Trace, replay |
| `agent.task.awaiting_approval` | HITL transition | Approval UI, mobile push |
| `agent.task.approved` / `agent.task.rejected` | HITL outcome | Audit, resume |
| `agent.task.budget_exceeded` | Budget hit | Cost ops, support |
| `agent.task.killed` | Manual kill | Back-office, audit |
| `agent.task.completed` | Success | Customer notification, eval |
| `agent.task.failed` | Unrecoverable error | Support, eval |

## Â§7 Anti-Pattern Reminders

- Implementing the loop inline in the API handler.
- Treating step-budget as a comment.
- Tool-call idempotency keys derived from `random.uuid()`.
- Logging the plan but not persisting it â€” replay is impossible.
- The agent loop process is the same process as the web app â€” runaway OOM crashes API.

---

## Â§8 Compliance-Evidence Emissions (Enhancement)

Every state-machine transition emits a **compliance event** onto the hash-chained action audit log (`ai-agent-audit-log-integrity`). The runtime is the canonical source of compliance evidence for `ai-agent-soc2-controls` CC7.2 (monitoring), PI1.1 (processing integrity), and `ai-agent-iso27001-controls` A.12.4 (logging).

Minimum event taxonomy emitted by the loop:

| Transition | `event_class` | Required fields |
|---|---|---|
| Task accepted | `task_accepted` | task_id, tenant_id, agent_id, intent_summary, policy_version |
| Plan committed | `plan_committed` | task_id, plan_hash, step_count |
| Tool call started | `tool_call_started` | task_id, step_index, tool_name, tool_version, reversibility, data_class |
| Tool call ended | `tool_call_ended` | task_id, step_index, outcome, idempotency_key, latency_ms |
| Approval required | `approval_required` | task_id, step_index, tool_name, approver_role |
| Approval received | `approval_received` | task_id, step_index, approval_id, approver_id |
| Kill-switch flipped | `kill_switch_flipped` | scope, actor, reason, drill_run_id (nullable) |
| Budget breached | `budget_breached` | task_id, budget_kind, threshold, observed |
| Memory write | `memory_write` | task_id, tier, retention_class, subject_id (hashed) |
| Erasure step | `erasure_step` | request_id, step, status |
| Task closed | `task_closed` | task_id, terminal_state, verdict_ref |

Every event carries `policy_version` so historical authority checks resolve correctly (see `ai-agent-approval-audit-completeness`). Emissions are synchronous on the critical path for irreversible-action transitions and `kill_switch_flipped`; everything else may be batched with at-most-1s drain.

Cross-links: `ai-agent-audit-log-integrity`, `ai-agent-soc2-controls`, `ai-agent-evidence-automation`, `ai-agent-approval-audit-completeness`.
## Consolidated Child References

- Load `references/routing.md` to map retired AI child skill slugs to their reference modules.

