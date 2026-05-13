# Tool Side-Effect Budgets

A side-effect budget caps how many times a tool can fire per scope (task, session, user, tenant, time window). It is a defence against:

- runaway agent loops re-invoking the same tool;
- prompt-injected agents being asked to "send 10,000 emails";
- compound effects that emerge from many individually-reversible calls;
- provider-side rate limit breaches that take down the whole platform.

## Budget Schema

```yaml
name: email_send_external
side_effect_budget:
  per_task_max: 5
  per_session_max: 20
  per_user_per_hour: 50
  per_tenant_per_hour: 500
  per_tenant_per_day: 5000
  burst:
    window_seconds: 60
    max_count: 10
```

Every dimension is optional. Sensible defaults:

| Tool class | per_task_max | per_tenant_per_hour |
|---|---|---|
| Read-only | none | 10,000 |
| Reversible (internal-only) | 50 | 5,000 |
| Reversible (touches external) | 10 | 1,000 |
| Irreversible | 3 | 200 |

## Enforcement

Atomic counters in Redis, checked **before** the tool body runs.

```python
def check_and_charge_budget(tool: str, ctx: ToolContext) -> Optional[BudgetError]:
    budget = registry.get(tool).side_effect_budget
    keys = [
        (f"budget:task:{ctx.task_id}:{tool}",       budget.per_task_max,       None),
        (f"budget:session:{ctx.session_id}:{tool}", budget.per_session_max,    None),
        (f"budget:user:{ctx.user_id}:{tool}:hour",  budget.per_user_per_hour,  3600),
        (f"budget:tenant:{ctx.tenant_id}:{tool}:hour", budget.per_tenant_per_hour, 3600),
        (f"budget:tenant:{ctx.tenant_id}:{tool}:day",  budget.per_tenant_per_day,  86400),
    ]
    pipe = redis.pipeline()
    for key, limit, ttl in keys:
        if limit is None: continue
        pipe.incr(key)
        if ttl: pipe.expire(key, ttl, nx=True)
    counts = pipe.execute()

    for (key, limit, _), count in zip([k for k in keys if k[1] is not None], counts[::2]):
        if count > limit:
            # rollback: decrement the keys we already incremented
            redis.decr(key)
            return BudgetError(scope=key, limit=limit, count=count)
    return None
```

This is a check-and-charge pattern. On exceed, decrement is best-effort; tolerable because the next check still blocks.

## What the Tool Returns on Exceed

```json
{
  "status": "budget_exceeded",
  "error": {
    "code": "BUDGET_EXCEEDED",
    "retriable": false,
    "user_message": "I've reached my safety limit on outbound emails for this session.",
    "operator_message": "scope=per_session_max limit=20 tool=email_send_external task=12345 tenant=42"
  }
}
```

The agent treats this as a stop signal. It must not retry the same tool; it should summarise progress and ask the user.

## Per-Tenant Overrides

Enterprise tenants often need higher budgets. Override via:

```sql
INSERT INTO tenant_tool_budget_overrides
  (tenant_id, tool_name, override, reason, expires_at, granted_by)
VALUES
  (42, 'email_send_external',
   '{"per_session_max": 200, "per_tenant_per_hour": 5000}',
   'Migration project, signed-off by VP Customer Success', '2026-12-31', 'maria@platform.example');
```

Overrides are time-boxed and audited. They merge atop the default budget.

## Observability

Every budget block emits an event:

```json
{
  "event": "agent.tool.budget_blocked",
  "tenant_id": 42,
  "task_id": 12345,
  "tool": "email_send_external",
  "scope": "per_session_max",
  "limit": 20,
  "count": 21,
  "timestamp": "2026-05-11T10:23:45Z"
}
```

Dashboards on these events surface:
- which tools hit budgets most often (probably budgeted too tight or agent is misusing);
- which tenants hit budgets most often (probably need an override or are abusing);
- temporal patterns (budget pressure rising → tool may be in a loop).

## Anti-Patterns

- Budgets enforced "in application code" instead of at the tool boundary. Easy to bypass.
- Budgets only on per-tenant. Misses the "one agent task that runs in a loop" case.
- No `per_task_max`. The most common runaway-loop case.
- Budgets in environment variables. Not auditable, not per-tenant.
- Override granted in chat without an audit row.
- No alert when a tenant hits the same budget 5 days running. That tenant needs a different plan or a different agent design.

## Budget Tuning Loop

After 30 days of agent traffic, query:

```sql
SELECT tool, scope, COUNT(*) AS blocks
FROM agent_tool_budget_blocks
WHERE created_at > NOW() - INTERVAL 30 DAY
GROUP BY tool, scope
ORDER BY blocks DESC;
```

For each high-block row:
- If most blocks are from one tenant → consider override or move them to a higher plan.
- If blocks are spread across tenants → budget is too tight; raise default with a security review.
- If blocks correlate with agent-loop incidents → budget is correct; the agent loop needs fixing.
