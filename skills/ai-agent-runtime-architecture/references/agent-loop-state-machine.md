# Agent Loop State Machine — Formal Reference

This document defines the agent loop as a formal state machine: states, transitions, persisted artifacts, idempotency contract, crash-recovery rules.

## States

| State | Meaning | Terminal? | Side-effects allowed? |
|---|---|---|---|
| `QUEUED` | Task accepted; not yet claimed by a worker | no | no |
| `PLANNING` | LLM is generating a plan | no | no (read-only LLM call) |
| `AWAITING_APPROVAL` | Plan requires HITL approval before any action | no | no |
| `ACTING` | A tool call is in flight | no | yes |
| `OBSERVING` | Observation persisted; loop deciding next state | no | no |
| `COMPLETED` | Final answer emitted, task done | yes | n/a |
| `FAILED` | Unrecoverable error after retries | yes | n/a |
| `BUDGET_EXCEEDED` | Step / token / wallclock / cost budget breached | yes | n/a |
| `KILLED` | Killed manually via back-office or per-tenant kill-switch | yes | n/a |
| `ABANDONED` | Long-running task without progress for > N hours | yes | n/a |

## Transitions

```
QUEUED              -> PLANNING                 (worker claim)
PLANNING            -> AWAITING_APPROVAL        (plan flagged for HITL)
PLANNING            -> ACTING                   (auto-approved plan; non-irreversible)
PLANNING            -> COMPLETED                (plan = "final answer", no action needed)
PLANNING            -> FAILED                   (LLM error after retries)
AWAITING_APPROVAL   -> ACTING                   (approval granted)
AWAITING_APPROVAL   -> KILLED                   (approval rejected, hard reject)
AWAITING_APPROVAL   -> PLANNING                 (approval rejected, soft reject with feedback)
ACTING              -> OBSERVING                (tool returned)
ACTING              -> FAILED                   (tool failure after retries)
OBSERVING           -> PLANNING                 (continue)
OBSERVING           -> COMPLETED                (LLM signalled done)
*                   -> BUDGET_EXCEEDED          (any budget breach)
*                   -> KILLED                   (manual or per-tenant kill-switch)
*                   -> ABANDONED                (no progress within stall_seconds)
```

## Persistence Contract

Two tables:

```sql
CREATE TABLE agent_tasks (
  id                  BIGINT PRIMARY KEY,
  tenant_id           BIGINT NOT NULL,
  user_id             BIGINT NOT NULL,
  feature             VARCHAR(64) NOT NULL,
  state               VARCHAR(32) NOT NULL,
  goal                TEXT NOT NULL,
  plan_summary        TEXT,
  model_pin           VARCHAR(64) NOT NULL,
  prompt_version      VARCHAR(64) NOT NULL,
  tool_set_version    VARCHAR(64) NOT NULL,
  step_budget         INT NOT NULL,
  wallclock_budget_s  INT NOT NULL,
  cost_budget_usd     DECIMAL(10,4) NOT NULL,
  tool_cost_budget_usd DECIMAL(10,4) NOT NULL,
  steps_used          INT NOT NULL DEFAULT 0,
  usd_cost            DECIMAL(10,4) NOT NULL DEFAULT 0,
  tokens_in           BIGINT NOT NULL DEFAULT 0,
  tokens_out          BIGINT NOT NULL DEFAULT 0,
  result              JSON,
  failure_reason      TEXT,
  parent_trace_id     CHAR(32),
  created_at          DATETIME NOT NULL,
  updated_at          DATETIME NOT NULL,
  completed_at        DATETIME,
  INDEX (tenant_id, state, created_at),
  INDEX (state, updated_at)
);

CREATE TABLE agent_steps (
  id              BIGINT PRIMARY KEY,
  task_id         BIGINT NOT NULL,
  tenant_id       BIGINT NOT NULL,
  step_index      INT NOT NULL,
  state_before    VARCHAR(32) NOT NULL,
  state_after     VARCHAR(32) NOT NULL,
  thought         TEXT,
  tool_name       VARCHAR(128),
  tool_args       JSON,
  tool_args_hash  CHAR(64),
  idempotency_key CHAR(64),
  observation     JSON,
  tokens_in       INT,
  tokens_out      INT,
  usd_cost        DECIMAL(10,4),
  latency_ms      INT,
  error           TEXT,
  span_id         CHAR(16),
  created_at      DATETIME NOT NULL,
  UNIQUE KEY uniq_task_step (task_id, step_index)
);
```

Every transition writes a row to `agent_steps` **before** acknowledging the previous one as committed.

## Idempotency Contract

```python
def step_key(task_id: int, step_index: int, tool_name: str, args: dict) -> str:
    canon = json.dumps(args, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{task_id}:{step_index}:{tool_name}:{canon}".encode()).hexdigest()
```

This key is passed to the tool **and** stored on `agent_steps.idempotency_key`. The runtime guarantees: for a given `(task_id, step_index, tool_name, args_hash)`, the tool runs **at most once**, even after worker crash.

Tools that cannot accept an idempotency key must use the outbox pattern: write intent to `agent_outbox`, commit, then a separate worker drains the outbox with deduplication.

## Crash Recovery Algorithm

```
on_worker_start(task_id):
    task = SELECT * FROM agent_tasks WHERE id = task_id FOR UPDATE
    last_step = SELECT * FROM agent_steps WHERE task_id = task_id ORDER BY step_index DESC LIMIT 1
    if task.state in TERMINAL: return
    if task.state == "ACTING" and last_step.observation is NULL:
        # crashed during tool execution
        cached = idempotency_store.get(last_step.idempotency_key)
        if cached is not None:
            # tool actually completed; recover observation
            UPDATE agent_steps SET observation = cached, state_after = "OBSERVING" WHERE id = last_step.id
            UPDATE agent_tasks SET state = "OBSERVING"
        else:
            # tool never started or never persisted; safe to retry
            UPDATE agent_tasks SET state = "ACTING"
    resume_loop(task)
```

## TypeScript Variant (Inngest / Temporal)

```typescript
export const agentTask = inngest.createFunction(
  { id: "agent-task", retries: 0 },
  { event: "agent.task.created" },
  async ({ event, step }) => {
    const taskId = event.data.taskId;
    while (true) {
      const task = await step.run("load", () => loadTask(taskId));
      if (TERMINAL.has(task.state)) return;
      const plan = await step.run(`plan-${task.steps_used}`, () => callPlanner(task));
      if (plan.kind === "final") return await step.run("complete", () => completeTask(taskId, plan));
      if (plan.kind === "needs_approval") {
        await step.waitForEvent("approval", { event: "agent.approval.received", timeout: "24h", match: "data.taskId" });
      }
      await step.run(`act-${task.steps_used}`, () => executeTool(taskId, plan));
    }
  }
);
```

Durable execution engines (`step.run` / `step.waitForEvent`) handle resumability automatically — each `step.run` is memoized by step name.

## Stall Detection

A separate "janitor" job scans every 5 minutes:

```sql
UPDATE agent_tasks
SET state = 'ABANDONED', failure_reason = 'stalled_no_progress'
WHERE state IN ('PLANNING','ACTING','OBSERVING','AWAITING_APPROVAL')
  AND updated_at < NOW() - INTERVAL stall_seconds SECOND;
```

Default `stall_seconds`:
- `AWAITING_APPROVAL`: 24 hours.
- Active states: 30 minutes.

Configurable per feature.
