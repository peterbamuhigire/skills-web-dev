---
name: ai-agent-async-and-long-running-tasks
description: Use when designing agentic features that run for minutes-to-days — durable execution, resumability after worker restart, progress UX, notifications on completion or stall, and the abandonment policy. Builds on `ai-agent-runtime-architecture` for state machine; this skill adds durability, progress reporting, and long-horizon operability.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Async and Long-Running Tasks
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- An agent task may run for **more than 5 minutes** of wallclock — investigations, multi-day reconciliations, end-of-month workflows.
- The task survives **process restarts, deploys, and worker crashes** without losing state or repeating side-effects.
- The user is **not actively waiting** — they kicked off the task and want a notification on completion or when input is needed.
- The platform must surface **progress** during the task (steps done, ETA, current activity).
- The task needs an **abandonment policy** — what happens if it stalls or runs too long without progress.

## Do Not Use When

- The task completes in < 5 minutes — `ai-agent-runtime-architecture` is enough.
- The task is a synchronous chat-like agent — agent inbox / approval skills cover this.
- The task is a deterministic workflow — `ai-agent-runtime-architecture` §1 decision matrix.

## Required Inputs

- Agent runtime + state machine (`ai-agent-runtime-architecture`).
- Durable execution engine (Temporal / Inngest / Restate) or robust queue with persistent state.
- Notification channels (email, push, in-app).
- Agent inbox surface (`ai-agent-mobile-and-web-ux-patterns`).

## Workflow

1. Read this `SKILL.md`.
2. Pick the **durable execution substrate** (§1).
3. Implement **durable state patterns** (§2). See `references/durable-state-patterns.md`.
4. Implement **progress reporting** (§3) — what the user sees while waiting.
5. Implement **notification policy** (§4) — when to ping the user.
6. Implement **abandonment policy** (§5) — what stalls look like.
7. Implement **resume after deploy** (§6) — code update mid-task.
8. Apply anti-patterns (§7).

## Quality Standards

- A long-running task **survives** worker restarts, deploy rollouts, and infrastructure crashes without re-executing side effects.
- Progress is updated **at every state transition**; UI consumers see a heartbeat at least every 60 seconds for active tasks.
- Notifications respect user preferences and quiet hours; never spam.
- Abandonment threshold is feature-specific (analyst agent: 1 hour idle; reconciliation: 4 hours).
- A task that runs across a code deploy continues using its **pinned** prompt and tool versions (not the latest deploy).
- A task that exceeds its wallclock budget transitions to `BUDGET_EXCEEDED` cleanly; user is notified.
- The user can **cancel** at any time, and cancellation triggers rollback of in-flight reversible actions.

## Anti-Patterns

- Long-running agent implemented as a background thread inside the web process. First restart loses it.
- "We'll save state every N steps" — first crash between two saves loses progress.
- No heartbeat. UI says "running…" forever; user has no idea if it's stuck.
- Cancel button that kills the worker but leaves staged actions in the queue.
- Notifications fire every step. Notification fatigue; user mutes the channel.
- A deploy in the middle of a 6-hour task → state is corrupt; manual recovery.
- Abandonment threshold = wallclock budget. They're different concepts; conflating them masks real stalls.
- Progress UX shows raw LLM thinking. Token-vomit; user sees confusing chain-of-thought.

## Outputs

- Substrate decision (Temporal / Inngest / Restate / custom).
- Durable state schema.
- Progress reporting contract.
- Notification policy.
- Abandonment policy.
- Resume-across-deploy procedure.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Long-running task substrate | Markdown | `docs/ai/long-running-agents.md` |
| Correctness | Crash-recovery drill report | Markdown | `docs/runbooks/long-running-agent-recovery.md` |
| UX | Progress reporting + notification UX | Markdown + screenshots | `docs/ux/long-running-progress.md` |
| Operability | Abandonment sweeper job | Code + dashboard | `ops/jobs/agent-abandonment.md` |

## References

- `references/durable-state-patterns.md` — durable state implementation across substrates.
- Companion: `ai-agent-runtime-architecture`, `ai-agent-observability-and-replay`, `ai-agent-action-approval-and-hitl`, `ai-agent-mobile-and-web-ux-patterns`, `distributed-systems-patterns`, `reliability-engineering`.

<!-- dual-compat-end -->

## §1 Substrate Decision

| Substrate | Max wallclock | Resumability | Operability | When |
|---|---|---|---|---|
| BullMQ / Celery / RQ + Redis | < 1h | At-least-once with custom idempotency | Mid | Mid-length, you already run it |
| Postgres-backed job queue (Oban, river) | < 4h | Same as queue | High | You already have Postgres |
| Temporal / Inngest / Restate / Cadence | days+ | Exactly-once via workflow primitives | High | Long-running, complex multi-step |
| Custom durable runtime | unlimited | Whatever you build | Variable | You have specific needs not met by above |

**Strong default for > 30 min agent tasks: Temporal-class.** The workflow primitive (`step.run`, `step.waitForEvent`) handles resumability automatically.

## §2 Durable State Patterns

Three pieces of state must be durable:

1. **Task state** — current state-machine state, budgets used, plan snapshot.
2. **Step history** — every step that ran, every observation persisted (`agent_steps`).
3. **Pending external dependencies** — awaiting approval, awaiting external webhook, awaiting scheduled time.

Pattern: every state transition is a single write to a single row, and the worker can crash anywhere between writes.

Full pattern catalogue in `references/durable-state-patterns.md`.

## §3 Progress Reporting

A task emits progress events the UI subscribes to:

```typescript
type AgentProgressEvent = {
  task_id: string;
  emitted_at: string;  // ISO
  kind: "phase_started" | "phase_completed" | "step_completed" | "heartbeat" | "stall_warning";
  phase?: string;       // human-readable phase ("gathering data", "analysing", "drafting response")
  step_index?: number;
  message?: string;     // user-facing, sanitised
  estimated_completion?: string;   // ISO, when known
  steps_done?: number;
  steps_estimated_total?: number;
};
```

Heartbeat every 60 seconds even when no state change. UI shows:

```
[ Agent is working — 4 of ~7 steps complete ]
   Currently: analysing May time entries
   Estimated completion: 14:32 (in ~3 min)
   [Cancel]   [View live trace]
```

`message` is the agent's own one-sentence description, scrubbed of token-vomit (no raw chain-of-thought).

## §4 Notification Policy

```yaml
notifications:
  on_completion:
    channels: [push, email_if_offline]
    quiet_hours: respect_user_tz
  on_awaiting_approval:
    channels: [push]
    fallback_after_minutes: 30  → email if no push interaction
  on_stall:
    channels: [push, email]
    after_idle_minutes: 60
  on_budget_exceeded:
    channels: [push, in_app]
  on_failed:
    channels: [push, email]
  on_killed:
    channels: [in_app]    # user initiated; no need to ping back
  no_notification_during_active_session: true   # user is in the chat; UI updates
```

Quiet hours: respect user's timezone + DND settings. For irreversible-action approvals, override DND only if the user opted in.

## §5 Abandonment Policy

Distinct from wallclock budget. Abandonment = "no progress for too long":

```sql
-- Tasks stalled with no progress
SELECT id FROM agent_tasks
WHERE state IN ('PLANNING','ACTING','OBSERVING')
  AND updated_at < NOW() - INTERVAL stall_seconds SECOND;

-- Tasks awaiting approval too long
SELECT id FROM agent_tasks
WHERE state = 'AWAITING_APPROVAL'
  AND updated_at < NOW() - INTERVAL approval_stall_seconds SECOND;
```

Per-feature thresholds:
- Active states: 30-60 min default.
- Awaiting approval: 24h default.

On stall:
- Transition `ABANDONED` (or back to QUEUED for a retry, by policy).
- Notify user.
- Emit `agent.task.abandoned` event.
- If reversible side effects in flight, trigger compensations.

Some features prefer `RETRY_FROM_LAST_STEP` instead of `ABANDONED`. Configurable per feature.

## §6 Resume Across Deploy

When a deploy lands mid-task:

- **Workers drain gracefully.** New tasks wait. Active tasks finish the current step or checkpoint and exit cleanly.
- **State persists.** Worker restart with the new code reads task state and resumes.
- **Prompt and tool versions are pinned on the task row.** The new deploy may include a new prompt v2.4; in-flight tasks continue with v2.3.

For Temporal-class substrates, this works automatically. For custom queues, the worker must implement graceful drain (SIGTERM handler that finishes the current step + checkpoint).

Code changes that break old task state (schema migration to `agent_steps`, prompt format change) are forbidden in the same deploy; they must roll out as a migration with backfill.

## §7 Anti-Patterns

- Long-running task in a web request. Doesn't survive timeout.
- Saved state but no idempotency. Crash → re-send email.
- No heartbeat. UI shows "running…" for hours.
- Cancel kills the worker but doesn't compensate.
- Notify on every step. User mutes.
- Deploy mid-task with no version pinning. Mixed-version traces; flaky behaviour.
- Abandonment policy missing. Tasks linger in `ACTING` forever.
- Progress shows raw chain-of-thought. Confusing; leaks reasoning.
