# Budget Enforcement Pipeline — Implementation

## Counters

Per-task counters live in Redis for low-latency increment, mirrored to DB at terminal transitions.

```
HSET agent:task:{task_id}:budget
  step_used        0
  tokens_in        0
  tokens_out       0
  usd_llm          0
  usd_tool         0
  started_at_ms    1715424000000
EXPIRE agent:task:{task_id}:budget  86400
```

Caps stored on the `agent_tasks` row (immutable for the lifetime of the task).

## Resolution at Task Creation

```python
def resolve_budgets(tenant_id: int, feature: str) -> Budgets:
    tenant = tenants.get(tenant_id)
    catalogue = agent_budget_catalogue[feature][tenant.plan_tier]
    overrides = (
        tenant_agent_budget_overrides
        .where(tenant_id=tenant_id, feature=feature)
        .where(expires_at__gt=now())
        .order_by("created_at_desc")
        .first()
    )
    if overrides:
        merged = {**catalogue, **overrides.values}
    else:
        merged = catalogue
    return Budgets(**merged)
```

## Pre-Step Check

```python
def check_budgets_before_step(task_id: int) -> Optional[BudgetBreach]:
    task   = db.get(agent_tasks, task_id)
    snap   = redis.hgetall(f"agent:task:{task_id}:budget")
    now_ms = int(time.time() * 1000)
    elapsed_s = (now_ms - int(snap["started_at_ms"])) / 1000.0

    if int(snap["step_used"]) >= task.step_budget:
        return BudgetBreach("step")
    if elapsed_s >= task.wallclock_budget_s:
        return BudgetBreach("wallclock")
    tokens_used = int(snap["tokens_in"]) + int(snap["tokens_out"])
    if tokens_used >= task.token_budget:
        return BudgetBreach("token")
    if float(snap["usd_llm"]) + float(snap["usd_tool"]) >= task.cost_budget_usd:
        return BudgetBreach("cost")
    return None
```

The runtime calls this before each `PLANNING` transition.

## Post-LLM-Call Increment

The gateway returns `tokens_in`, `tokens_out`, `usd_cost` on every LLM call. The runtime increments:

```python
def record_llm_call(task_id: int, tokens_in: int, tokens_out: int, usd_cost: float):
    pipe = redis.pipeline()
    pipe.hincrby(f"agent:task:{task_id}:budget", "tokens_in", tokens_in)
    pipe.hincrby(f"agent:task:{task_id}:budget", "tokens_out", tokens_out)
    pipe.hincrbyfloat(f"agent:task:{task_id}:budget", "usd_llm", usd_cost)
    pipe.execute()
```

## Pre-Tool-Call Estimate

For tools that bill, estimate cost before calling and refuse if it would breach:

```python
def check_tool_budget(task_id: int, tool_name: str, args: dict) -> Optional[BudgetBreach]:
    task = db.get(agent_tasks, task_id)
    tool = tool_registry.get(tool_name)
    estimate_usd = tool.estimate_cost(args)
    snap = redis.hgetall(f"agent:task:{task_id}:budget")
    if float(snap["usd_tool"]) + estimate_usd > task.tool_cost_budget_usd:
        return BudgetBreach("tool_cost", estimate=estimate_usd)
    return None
```

After the tool runs, record the actual cost:

```python
def record_tool_call(task_id: int, usd_cost: float):
    redis.hincrbyfloat(f"agent:task:{task_id}:budget", "usd_tool", usd_cost)
```

## Step Increment

After each `OBSERVING` transition:

```python
redis.hincrby(f"agent:task:{task_id}:budget", "step_used", 1)
```

## Wallclock Timeout

A separate sweeper job scans tasks in non-terminal states and forces `BUDGET_EXCEEDED` on wallclock breach (defence against worker that doesn't check):

```sql
UPDATE agent_tasks
SET state = 'BUDGET_EXCEEDED', failure_reason = 'wallclock_exceeded'
WHERE state IN ('PLANNING','ACTING','OBSERVING','AWAITING_APPROVAL')
  AND (UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(started_at)) > wallclock_budget_s;
```

Runs every 30 seconds.

## On Budget Breach

```python
def on_breach(task_id: int, dim: str):
    task = db.get(agent_tasks, task_id, for_update=True)
    if task.state in TERMINAL: return
    snap = redis.hgetall(f"agent:task:{task_id}:budget")
    task.state = "BUDGET_EXCEEDED"
    task.failure_reason = f"{dim}_budget_exceeded"
    task.steps_used = int(snap["step_used"])
    task.tokens_in = int(snap["tokens_in"])
    task.tokens_out = int(snap["tokens_out"])
    task.usd_cost = float(snap["usd_llm"]) + float(snap["usd_tool"])
    task.save()
    
    # Final cheap summary (configurable; default capped at $0.01 LLM cost)
    summary = generate_progress_summary(task, max_usd=0.01)
    
    bus.emit("agent.task.budget_exceeded", {
        "task_id": task.id, "tenant_id": task.tenant_id,
        "feature": task.feature, "dimension": dim,
        "summary": summary, "usd_cost": task.usd_cost
    })
```

## Per-Task Cost Ledger Write

On terminal state (`COMPLETED`, `FAILED`, `BUDGET_EXCEEDED`, `KILLED`, `ABANDONED`):

```sql
INSERT INTO agent_task_cost_ledger (
  task_id, tenant_id, feature, model_pin, terminal_state,
  step_used, tokens_in, tokens_out, usd_llm_cost, usd_tool_cost, usd_total,
  wallclock_seconds, created_at, completed_at
) VALUES (
  ?, ?, ?, ?, ?,
  ?, ?, ?, ?, ?, ?,
  ?, ?, NOW()
);
```

This row is the canonical source for the cost-per-tenant attribution rollup. Redis counters are discarded (TTL).

## Daily Rollup

```sql
INSERT INTO agent_daily_tenant_cost (date, tenant_id, plan_tier, feature, tasks, usd_total, usd_p50, usd_p90, success_rate)
SELECT
  DATE(completed_at) AS date,
  tenant_id,
  (SELECT plan_tier FROM tenants WHERE id = a.tenant_id) AS plan_tier,
  feature,
  COUNT(*) AS tasks,
  SUM(usd_total) AS usd_total,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY usd_total) AS usd_p50,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY usd_total) AS usd_p90,
  SUM(CASE WHEN terminal_state = 'COMPLETED' THEN 1 ELSE 0 END) / COUNT(*) AS success_rate
FROM agent_task_cost_ledger a
WHERE DATE(completed_at) = CURDATE() - INTERVAL 1 DAY
GROUP BY DATE(completed_at), tenant_id, feature;
```

This row is what `ai-cost-per-tenant-attribution` reads for its agent rollup.

## Test Suite (Required)

```python
def test_step_budget_blocks_after_n_steps():
    task = create_task(step_budget=3, token_budget=999999, wallclock_budget_s=999, cost_budget_usd=999)
    for _ in range(3):
        run_one_step(task.id)  # planner returns "continue"
    state = run_one_step(task.id)
    assert state == "BUDGET_EXCEEDED"

def test_wallclock_breach_via_sweeper():
    task = create_task_with_started_at(now() - 2_hours, wallclock_budget_s=3600)
    run_wallclock_sweeper()
    assert db.get(agent_tasks, task.id).state == "BUDGET_EXCEEDED"

def test_cost_budget_blocks_on_expensive_tool():
    task = create_task(tool_cost_budget_usd=0.10)
    # Tool that will return estimate 0.20
    breach = check_tool_budget(task.id, "expensive_tool", {})
    assert breach is not None

def test_terminal_writes_ledger():
    task = create_task_and_complete()
    row = db.query("SELECT * FROM agent_task_cost_ledger WHERE task_id = ?", task.id).first()
    assert row is not None
    assert row.usd_total > 0
```

These tests run on every PR that touches the runtime or the budget code.

## Observability

Per-step span attributes:
- `agent.task.budget.step.used`, `agent.task.budget.step.limit`
- `agent.task.budget.tokens.used`, `agent.task.budget.tokens.limit`
- `agent.task.budget.usd.used`, `agent.task.budget.usd.limit`
- `agent.task.budget.wallclock_s.elapsed`, `agent.task.budget.wallclock_s.limit`

Dashboards:
- % of tasks ending in `BUDGET_EXCEEDED` (per feature, per plan).
- Median budget utilisation at terminal (sanity: should not be 99% on average; that means budgets are too tight).
- Cost-per-completed-task vs cost-per-attempted-task.

## Tuning Loop

After 30 days of agent traffic:
- High `BUDGET_EXCEEDED` rate on a feature → budget too tight or agent too wasteful. Eval the agent design.
- Low median utilisation (< 30%) → budgets too generous; tighten.
- High variance → consider per-feature sub-budgets (e.g., per-step max cost).
