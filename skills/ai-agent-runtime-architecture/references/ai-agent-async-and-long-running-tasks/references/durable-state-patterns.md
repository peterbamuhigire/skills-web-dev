# Durable State Patterns for Long-Running Agent Tasks

Three patterns, in order of operational sophistication.

## Pattern 1: Postgres-Native Durable State (Simple)

State lives in `agent_tasks` + `agent_steps` + a queue table. A worker claims a task, runs one step inside a DB transaction (or with explicit checkpointing), and commits.

```sql
-- Claim a task atomically
WITH claimed AS (
  SELECT id FROM agent_tasks
  WHERE state IN ('QUEUED','PLANNING','OBSERVING')
    AND (locked_until IS NULL OR locked_until < NOW())
    AND tenant_kill_switched = FALSE
  ORDER BY priority DESC, created_at
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
UPDATE agent_tasks
SET locked_by = :worker_id, locked_until = NOW() + INTERVAL '120 second'
FROM claimed
WHERE agent_tasks.id = claimed.id
RETURNING agent_tasks.*;
```

The worker:
1. Claims with `FOR UPDATE SKIP LOCKED`.
2. Runs one step.
3. Persists step result + new state.
4. Releases lock.
5. Loop.

On crash: lock expires; another worker picks up.

```python
def run_one_step(task):
    with txn():
        # Determine next action (plan or execute)
        plan = call_planner(task)
        step = persist_step(task, plan)
        # If tool call:
        if plan.is_tool:
            # Idempotency key derived from (task, step_index, tool, args)
            result = execute_tool_with_idem(plan.tool, plan.args, step.idempotency_key)
            persist_observation(step, result)
        # Update task state and budgets
        update_task_state(task, plan, result)
    return task.state
```

The transaction wraps the planning + tool decision + observation persistence. The **tool execution itself is outside the transaction** (it's external), but the idempotency key + outbox guarantees at-most-once.

Pros: simple, one technology, observable in SQL.
Cons: hard to model long waits (awaiting approval that takes 24h holds nothing); limited primitives.

## Pattern 2: Outbox + Job Queue (Mid)

Same Postgres state, but:
- Tool calls go through an outbox (`agent_outbox`) drained by a dedicated worker.
- Long waits (approvals, external webhooks) are modeled as separate queue jobs with a `wakeup_at` timestamp.

```sql
CREATE TABLE agent_outbox (
  id              BIGINT PRIMARY KEY,
  task_id         BIGINT NOT NULL,
  step_index      INT NOT NULL,
  tool_name       VARCHAR(128) NOT NULL,
  args            JSON NOT NULL,
  idempotency_key CHAR(64) NOT NULL UNIQUE,
  state           ENUM('queued','running','succeeded','failed','canceled') NOT NULL,
  attempts        INT NOT NULL DEFAULT 0,
  next_attempt_at DATETIME NOT NULL,
  result          JSON,
  created_at      DATETIME NOT NULL
);

CREATE TABLE agent_wakeups (
  id          BIGINT PRIMARY KEY,
  task_id     BIGINT NOT NULL UNIQUE,   -- one wakeup per task
  reason      VARCHAR(64) NOT NULL,     -- 'approval_timeout', 'scheduled', 'external_webhook'
  wake_at     DATETIME NOT NULL,
  payload     JSON
);
```

A scheduler scans `agent_wakeups WHERE wake_at < NOW()` and pushes those tasks back into the planning queue.

Pros: still Postgres-native; clean separation of side-effects; resumable across crash.
Cons: building primitives the durable engines provide.

## Pattern 3: Durable Workflow Engine (Strong Default for Long Tasks)

Use Temporal / Inngest / Restate / Cadence. The agent loop is a workflow function; each step is a `step.run(...)`; waits are `step.waitForEvent(...)` or `step.sleep(...)`.

Example (Inngest TypeScript):

```typescript
export const agentTask = inngest.createFunction(
  { id: "agent-task", retries: 0, concurrency: { limit: 50 } },
  { event: "agent/task.created" },
  async ({ event, step, logger }) => {
    const taskId = event.data.taskId;
    let stepIdx = 0;
    
    while (true) {
      const task = await step.run(`load-${stepIdx}`, () => loadTask(taskId));
      if (TERMINAL.has(task.state)) return;
      
      // Plan
      const plan = await step.run(`plan-${stepIdx}`, () => callPlanner(task));
      
      if (plan.kind === "final") {
        await step.run(`complete-${stepIdx}`, () => completeTask(taskId, plan));
        return;
      }
      
      if (plan.kind === "needs_approval") {
        const decision = await step.waitForEvent(`approval-${stepIdx}`, {
          event: "agent/approval.decided",
          timeout: "24h",
          match: "data.taskId",
        });
        if (!decision || decision.data.decision !== "approved") {
          await step.run(`pause-or-fail-${stepIdx}`, () => handleApproval(taskId, decision));
          return;
        }
      }
      
      if (plan.kind === "tool_call") {
        await step.run(`exec-${stepIdx}`, () =>
          executeTool(taskId, plan.tool, plan.args, idemKey(taskId, stepIdx, plan))
        );
      }
      
      stepIdx++;
    }
  }
);
```

Inngest / Temporal handle:
- Memoization of `step.run` results (worker crash → resume reads cached results).
- Durable `waitForEvent` / `sleep` (24h wait survives any process restart).
- Concurrency limits, retries, signal-based cancellation.
- History replay for "what did this task do?" — already a built-in audit.

Pros: rock solid; primitives match agent needs; observability built-in.
Cons: one more system; learning curve; cost.

## Idempotency Keys

Across all patterns:

```python
def step_idem_key(task_id: int, step_index: int, tool: str, args: dict) -> str:
    canon = json.dumps(args, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{task_id}:{step_index}:{tool}:{canon}".encode()).hexdigest()
```

Used by:
- Tools that support it (preferred).
- An outbox unique-index where tools don't.
- A dedup table for one-off external calls.

Never derive from `time.now()` or `random()`.

## Graceful Worker Shutdown

```python
import signal

class GracefulRunner:
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGTERM, self._on_sigterm)
        signal.signal(signal.SIGINT, self._on_sigterm)
    
    def _on_sigterm(self, *_):
        self.shutdown = True
    
    def run_loop(self):
        while not self.shutdown:
            task = claim_task()
            if task is None:
                time.sleep(0.5); continue
            try:
                run_one_step(task)
            finally:
                release_lock(task)
            # Do not start a new step if shutdown was requested mid-step
            if self.shutdown:
                break
```

Deploy targets (Kubernetes etc.) must give the worker enough grace period to finish the current step. Default `terminationGracePeriodSeconds`: 120 (long enough for one step including a slow tool).

## Long Waits

For awaiting approval or scheduled wakeups:

```python
def schedule_approval_timeout(task_id, timeout_seconds=86400):
    db.insert(agent_wakeups, {
        "task_id": task_id,
        "reason": "approval_timeout",
        "wake_at": now() + timedelta(seconds=timeout_seconds),
    })
```

Scheduler runs every 30s:

```sql
SELECT task_id, reason, payload
FROM agent_wakeups
WHERE wake_at < NOW()
FOR UPDATE SKIP LOCKED;
```

Re-enqueues the task with the wakeup reason. Task state machine handles the cause (approval expired → ABANDONED, scheduled wakeup → resume planning).

In Temporal/Inngest: `step.waitForEvent` with `timeout` does this natively.

## Heartbeats

Workers update `agent_tasks.heartbeat_at` periodically:

```python
def heartbeat(task_id):
    db.execute("UPDATE agent_tasks SET heartbeat_at = NOW() WHERE id = ?", task_id)
```

A janitor job detects stuck-locked tasks:

```sql
UPDATE agent_tasks SET locked_by = NULL, locked_until = NULL
WHERE locked_until < NOW();
```

Or for the "is the worker dead" case:

```sql
SELECT id FROM agent_tasks
WHERE heartbeat_at < NOW() - INTERVAL '5 minute'
  AND state IN ('PLANNING','ACTING');
```

## Cross-Deploy Resumability

- Workflow / task version pinned on the task row: `prompt_version`, `tool_set_version`, `model_pin`.
- New deploy can register a v2 of the prompt; v1 is kept and pinned in-flight tasks continue.
- Schema migrations to `agent_steps` / `agent_tasks` are forward-compatible during the rollout window.
- Breaking changes (column dropped, semantic shift) deploy as a two-phase migration: deploy reads both shapes; backfill; deploy drops the old shape; minimum 24h between phases for in-flight long tasks.

## Drill: Crash-Recovery

Run quarterly:
1. Pick 10 long-running tasks from staging.
2. SIGKILL the worker.
3. Restart with new commit.
4. Verify all 10 resume cleanly. No duplicate side-effects.
5. Document.

This is the **only** way to know recovery works. Trust no design that hasn't been killed.
