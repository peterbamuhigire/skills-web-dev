# Transactional Group Patterns for Agent Tool Chains

When an agent's task involves several side-effecting steps that should succeed-or-fail together, group them as a saga. Each step ships with a compensating action; on failure, compensations run in reverse.

This is `distributed-systems-patterns` saga, specialised for agent runtimes.

## Group Lifecycle

```
created → executing → committed | compensating → compensated | partially_failed
```

`partially_failed` is the worst outcome — log it, page on it, surface it. Treat it as an incident.

## Schema

```sql
CREATE TABLE agent_transactional_groups (
  id              BIGINT PRIMARY KEY,
  task_id         BIGINT NOT NULL,
  tenant_id       BIGINT NOT NULL,
  state           ENUM('created','executing','committed','compensating','compensated','partially_failed') NOT NULL,
  steps           JSON NOT NULL,        -- ordered list of {tool, args, compensator, idempotency_key}
  results         JSON NOT NULL DEFAULT '[]',
  created_at      DATETIME NOT NULL,
  updated_at      DATETIME NOT NULL,
  completed_at    DATETIME
);

CREATE TABLE agent_compensations (
  id              BIGINT PRIMARY KEY,
  group_id        BIGINT NOT NULL,
  step_index      INT NOT NULL,
  compensator     VARCHAR(128) NOT NULL,
  args            JSON NOT NULL,
  state           ENUM('pending','running','succeeded','failed') NOT NULL,
  attempts        INT NOT NULL DEFAULT 0,
  last_error      TEXT,
  created_at      DATETIME NOT NULL,
  succeeded_at    DATETIME
);
```

## The Compensator Registry

Each tool that participates in groups registers its compensator:

```python
@register_tool(name="invoice_create_draft", compensator="invoice_delete_draft")
def invoice_create_draft(args, ctx): ...

@register_tool(name="invoice_delete_draft")
def invoice_delete_draft(args, ctx): ...

@register_tool(name="email_send_to_customer", compensator=None)  # irreversible
def email_send_to_customer(args, ctx): ...
```

A tool with `compensator=None` cannot participate in a group except as the **last** step (no compensations need to run after it).

## Group Execution

```python
def run_group(group_id):
    grp = groups.get(group_id, for_update=True)
    grp.state = 'executing'; grp.save()
    completed = []

    for idx, step in enumerate(grp.steps):
        try:
            result = tool_runtime.run(step.tool, step.args, ctx, idempotency_key=step.idempotency_key)
            if result['status'] != 'ok':
                raise StepFailure(idx, result)
            grp.results.append(result); grp.save()
            completed.append((idx, step, result))
        except Exception as e:
            grp.state = 'compensating'; grp.save()
            compensate(grp, completed)
            return

    grp.state = 'committed'; grp.completed_at = now(); grp.save()


def compensate(grp, completed):
    failures = []
    for idx, step, result in reversed(completed):
        if step.compensator is None:
            failures.append((idx, "no_compensator"))
            continue
        comp_args = build_compensator_args(step, result)
        comp_row = compensations.create(group_id=grp.id, step_index=idx,
            compensator=step.compensator, args=comp_args, state='pending')
        try:
            tool_runtime.run(step.compensator, comp_args, ctx, retries=3)
            comp_row.state = 'succeeded'; comp_row.save()
        except Exception as e:
            comp_row.state = 'failed'; comp_row.last_error = str(e); comp_row.save()
            failures.append((idx, str(e)))
    grp.state = 'partially_failed' if failures else 'compensated'
    grp.save()
    if failures:
        page_oncall(...)
```

## Worked Example: "Bill ACME for May"

Steps:

| # | Tool | Compensator | Reversibility |
|---|---|---|---|
| 1 | `invoice_create_draft` | `invoice_delete_draft` | reversible |
| 2 | `attach_timesheet_to_invoice` | `detach_timesheet_from_invoice` | reversible |
| 3 | `invoice_finalise` | `invoice_void` | reversible (within window) |
| 4 | `email_send_to_customer` | none | irreversible — must be last |

If step 4 fails after 1-3 succeed: compensations run for 3, 2, 1 (void invoice, detach timesheet, delete draft).

If step 3 fails after 1-2 succeed: compensations for 2, 1.

If a compensator itself fails: `partially_failed`; on-call paged; the saga row carries the residue for manual cleanup.

## Idempotency

Idempotency keys are deterministic per step:

```python
step.idempotency_key = sha256(f"group:{group_id}:step:{idx}:{tool}:{stable_json(args)}")
```

A worker crash + restart re-runs `run_group(group_id)` from the start; tools short-circuit to cached results for already-run steps.

## Building Group Args at Plan Time

The agent's plan-preview pattern fits well: agent emits a plan, the runtime materialises it as a group:

```json
{
  "group": {
    "task_id": 12345,
    "steps": [
      {"tool": "invoice_create_draft", "args": {...}},
      {"tool": "attach_timesheet_to_invoice", "args": {...}},
      {"tool": "invoice_finalise", "args": {...}},
      {"tool": "email_send_to_customer", "args": {...}}
    ]
  }
}
```

Approval is on the group, not per step. Compensators are auto-resolved from the registry. The user approves the entire group; it commits-or-rolls-back as one unit.

## Partial Approval

The user can edit the group: drop a step, edit args, reorder (rare). Drop → step removed; compensator no longer needed. Edit → re-validates against tool schema. Reorder → re-validates dependency ordering (each step declares `depends_on: [step_indexes]`).

## Compensator Design Rules

1. **Compensators are tools too.** Same contract, same idempotency, same auditing.
2. **Compensators must be safe to run multiple times.** Idempotent.
3. **Compensators must work without the original tool's full context.** They take `original_args` and `original_result` plus their own args.
4. **A compensator should not have a compensator of its own.** Compensating a compensation creates loops.
5. **A compensator that sends a customer-facing message is itself irreversible.** Prefer compensators that don't externalise.

## Anti-Patterns

- "We'll roll back in code" — no explicit compensator registry, no audit, no replay.
- Compensators that "best-effort" without persistence. Worker crash, compensation lost.
- Saga with irreversible step in the middle. Always last, or split the saga.
- Compensator that re-runs a side effect (e.g., compensating refund = email customer; combined with original = customer gets two messages).
- No `partially_failed` state. The team thinks compensations always succeed.
- Group execution in one DB transaction — too long, locks, doesn't survive long external calls.
