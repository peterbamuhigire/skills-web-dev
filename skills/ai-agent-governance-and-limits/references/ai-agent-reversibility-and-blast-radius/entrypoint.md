> Consolidated from skills/ai-agent-reversibility-and-blast-radius/SKILL.md into ai-agent-governance-and-limits on 2026-05-13. Load this through skills/ai-agent-governance-and-limits/SKILL.md, not as an active skill entrypoint.

# AI Agent Reversibility and Blast-Radius
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Engineering reversibility into a tool the catalogue currently marks irreversible — adding dry-run, staged commit, or transactional grouping to lower friction without raising risk.
- Capping the **blast radius** of any single agent task — max recipients per email step, max records modified per session, max dollars charged per task.
- Implementing **sandbox-first** execution for new agent features (run in a shadow account before touching production).
- Designing **compensating actions** for tool chains so a saga can roll back a partially-completed agent task.
- Defending against the "agent did a thing, then did 999 more things before anyone noticed" class of incident.

## Do Not Use When

- The task is classifying a tool's reversibility — `ai-agent-tool-catalogue-and-action-gating`.
- The task is human-in-the-loop UX — `ai-agent-action-approval-and-hitl`.
- The task is generic saga / outbox patterns — `distributed-systems-patterns`. This skill applies those patterns specifically to agent tool chains.
- The task is rate-limiting at the platform layer — `saas-rate-limiting-and-quotas`.

## Required Inputs

- Tool catalogue with reversibility classification (`ai-agent-tool-catalogue-and-action-gating`).
- Agent runtime state machine (`ai-agent-runtime-architecture`).
- Tenant plan / tier catalogue with per-tenant caps.
- The list of external systems where actions land (CRM, ERP, payments, email, calendar).

## Workflow

1. Read this `SKILL.md`.
2. For each high-risk tool, choose a **reversibility upgrade pattern** (§1): dry-run, staged commit, transactional group, sandbox-first.
3. Engineer **dry-run mode** where applicable. See `references/dry-run-patterns.md`.
4. Engineer **staged commits** for actions that can stage in our own DB before fan-out.
5. Engineer **transactional groups** with compensating actions. See `references/transactional-group-patterns.md`.
6. Define **blast-radius caps** (§2): per-task / per-session / per-tenant / per-role.
7. Wire **sandbox-first** for new agent features (§3).
8. Engineer **kill-switch with rollback** (§4): the per-task kill must trigger compensations.
9. Apply anti-patterns (§5).

## Quality Standards

- For every tool catalogued `irreversible`, an explicit decision exists on whether a reversibility upgrade (dry-run, staging, saga) is feasible. The decision is logged.
- Dry-run mode produces a **structured preview** that matches the real-mode action 1:1 (same args, same target IDs, same projected effects). No "approximately" outputs.
- Staged commits surface in a "pending" state visible to the actor, with an explicit commit-or-cancel action and a timer.
- Transactional groups have **compensating action contracts** for each step. A failure mid-group triggers compensations in reverse order; partial-success leaves a clean state.
- Blast-radius caps are enforced **atomically** at the tool boundary, not in business logic post-hoc.
- Sandbox-first is the default for the first 14 days of any new agent feature in production. Promotion to "production traffic" requires eval pass + canary report.
- Kill-switch triggers compensations for in-flight reversible / staged steps, not just a worker SIGINT.

## Anti-Patterns

- Dry-run mode that "approximates" what would happen. The agent learns from approximations and behaves differently in real mode.
- Staged commits with no expiry — stage table grows unbounded.
- Saga with no compensating actions; "we'll roll back manually if it fails".
- Per-tenant blast caps that count only one dimension (emails only, ignoring webhook + Slack + SMS).
- Sandbox that's a different code path. Drift accumulates; the sandbox stops catching real bugs.
- Kill-switch that stops the worker but doesn't roll back the 7 reversible actions already in flight.
- Compensating actions that are themselves irreversible (refund triggers email; agent sends both).
- New agent feature shipped to all tenants on day 1 because "we'll watch the dashboards".

## Outputs

- Reversibility-upgrade decision per high-risk tool.
- Dry-run implementation per upgraded tool.
- Staged-commit schema and UX.
- Transactional-group spec per multi-step agent flow.
- Blast-radius caps per dimension per tier.
- Sandbox-first promotion criteria.
- Kill-switch-with-rollback runbook.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Reversibility upgrade decisions | Markdown / CSV | `docs/ai/reversibility-decisions.csv` |
| Correctness | Saga compensation tests | CI report | `tests/ai/saga/` |
| Release evidence | Sandbox promotion report | Markdown | `docs/runbooks/agent-feature-promotion.md` |
| Operability | Kill-with-rollback runbook | Markdown | `docs/runbooks/agent-kill-with-rollback.md` |

## References

- `references/dry-run-patterns.md` — implementation patterns for dry-run.
- `references/transactional-group-patterns.md` — saga + compensating actions for agent flows.
- Companion: `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-action-approval-and-hitl`, `ai-agent-runtime-architecture`, `ai-agent-safety-and-red-team`, `distributed-systems-patterns`, `reliability-engineering`, `saas-admin-backoffice-tooling`.

<!-- dual-compat-end -->

## §1 Reversibility Upgrade Patterns

For each tool the catalogue marks irreversible, ask whether one of these patterns applies. **Each pattern lowers approval friction without lowering safety.**

| Pattern | What it does | When it works |
|---|---|---|
| **Dry-run** | Tool runs with `dry_run=true`, returns the would-be result without committing | When the tool can compute its effect without external commit |
| **Staged commit** | Tool writes to our DB in a `staged` state; commit step fans out externally | When we own the boundary between draft and "real" |
| **Transactional group (saga)** | Multi-tool sequence with compensating actions per step | When external systems are involved |
| **Sandbox-first** | The tool calls a sandbox tenant of the external system, not production | New features, new integrations |

Worked example: turning `email_send_to_customer` from irreversible to a layered flow:

1. Dry-run: `email_render(...)` returns the rendered HTML + plain text + recipient list. No send.
2. Staged commit: `email_stage(...)` writes to `outgoing_emails` table with `state='staged', send_at=NOW()+60s`. UI shows the user the staged email with "Cancel send".
3. Commit: a worker picks up `state='staged' AND send_at < NOW()` and actually sends via the provider. Idempotency on the outbox row.
4. Compensation: within the 60s window, the user / agent / kill-switch can transition `staged → canceled`. After send, compensation is to send a correction email (a new action).

After this re-engineering, the **agent surface** of `email_send_to_customer` is effectively reversible for 60 seconds. The catalogue can lower it to `reversible_with_window`, approvals become undo-window pattern (`ai-agent-action-approval-and-hitl` §6).

## §2 Blast-Radius Caps

Caps are per dimension and per scope. Define a default; allow per-tenant override.

| Dimension | Per-task default | Per-session default | Per-tenant-day default |
|---|---|---|---|
| `external_recipients` (emails, SMS, webhooks combined) | 5 | 20 | 200 |
| `dollar_amount_total` (charges, refunds combined) | 1,000 | 5,000 | 50,000 |
| `records_deleted` | 10 | 50 | 500 |
| `records_modified` | 50 | 500 | 10,000 |
| `external_api_calls` | 20 | 100 | 2,000 |
| `messages_to_external_channels` (Slack ext, SMS, etc.) | 5 | 20 | 200 |

Caps are **the union** of all tools' side-effect budgets that fall in the dimension; the cap is hit when *any* combination of tools exhausts it.

Atomic counter in Redis. On exceed: the next tool call returns `BLAST_RADIUS_EXCEEDED`, agent transitions to `AWAITING_APPROVAL` (or `BUDGET_EXCEEDED` for terminal).

## §3 Sandbox-First

New agent features deploy in two phases:

| Phase | Days | Traffic | Compensations |
|---|---|---|---|
| Sandbox | 0-14 | Internal staff + opt-in pilot tenants | All tool calls route to sandbox accounts at external providers; emails sent to `+sandbox` aliases; payments to test mode |
| Canary | 14-21 | 10% of eligible tenants | Real calls; reduced blast caps (50% of normal) |
| GA | 21+ | 100% eligible | Full caps |

Promotion gates: eval suite passes, no Sev-1/2 incidents, < 5% intervention rate, COGS within target.

`sandbox_first` is set per-feature in the entitlement / rollout layer (`ai-feature-rollout-and-experimentation`).

## §4 Kill-Switch With Rollback

A kill-switch that only kills the worker is not enough. It must:

1. Mark the task `state='KILLED'` and emit `agent.task.killed`.
2. Enumerate `agent_steps` for this task in reverse order.
3. For each step where `tool.reversibility ∈ {reversible, staged}` AND `state='committed'` within the undo window: call the compensating action.
4. For each `staged_until > now()` step: cancel.
5. For irreversible-already-committed steps: log `unrecoverable_action` event; surface in incident dashboard with the user contact info.
6. Notify the user.

Runbook in `docs/runbooks/agent-kill-with-rollback.md`.

## §5 Anti-Patterns

- Treating dry-run as a UI feature, not a tool feature. The agent loop should be able to call dry-run by itself.
- Staged-commits that linger forever because the cron worker is broken. Add monitoring on `staged` age.
- Saga compensation that re-issues a side effect when the original step never committed.
- Per-tenant caps that don't cover the burstable case (10 emails in 5s vs 10 per day).
- Sandbox accounts that share rate limits with production. A flaky test storm starves real customers.
- Kill-switch that requires SSH to the worker. Means there is no kill-switch.


