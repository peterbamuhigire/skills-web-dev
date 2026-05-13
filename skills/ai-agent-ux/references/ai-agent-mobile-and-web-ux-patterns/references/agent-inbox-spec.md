# Agent Inbox — Component Spec

The agent inbox is the single user-visible queue of: pending approvals, in-flight tasks, recently completed tasks, failed tasks. It is reachable in ≤ 2 clicks from anywhere in the product.

## Information Architecture

```
Inbox
├── Pending approvals          (default tab; badge shows count)
├── In-flight                  (badge shows count)
├── Completed                  (last 30 days)
└── Failed / abandoned         (last 30 days, with retry)
```

Top nav: a bell icon with a count badge; the badge counts pending approvals + in-flight stalls (anything needing user attention).

## Row Model

Each row:

```
┌────────────────────────────────────────────────────────────────┐
│ [icon]  Send invoice to ACME — $12,400                         │
│         Pending approval · expires in 22h 12m                  │
│         Agent: support_copilot · Task tsk_abc · 4 steps        │
│         [Approve]  [View plan]  [Reject]                       │
└────────────────────────────────────────────────────────────────┘
```

Fields:
- Title — agent's one-line summary of the task / approval.
- Status — pending / in-flight / completed / failed + time annotation.
- Meta — agent feature name, task id (short), step count.
- Primary action (Approve / View / Resume / Retry).
- Secondary actions (Reject / Cancel / Forget).

Hover reveals: full agent name, exact times, cost, model.

## Filters

```
Filter: [ Feature ▾ ] [ Status ▾ ] [ Date ▾ ] [ Blast-radius ▾ ]
Sort:   [ Expiring soonest ▾ ]
Search: [______________]
```

Power users with many concurrent tasks need filters to triage.

## Bulk Actions

When multiple rows are selected:

```
3 items selected
[Approve all]  [Reject all]  [Cancel all]
```

Bulk approval still respects per-item edits (each item must have its args confirmed; otherwise bulk-approve only applies to items that don't require edits).

## Empty States

| State | Copy |
|---|---|
| No pending | "No approvals pending. Agents will queue here when they need you." |
| No in-flight | "No agent tasks running. Start one from a feature, or use the AI panel." |
| First-time | "Agents work in the background and queue here when they need approval or finish a task. Tap a task to see what's happening." |

## Mobile

```
┌───────────────────────┐
│  Inbox      ●3        │ ← tab bar
│  ─────────────────    │
│  Pending  In-flight   │
│  ▔▔▔▔▔▔               │
│                       │
│  ┌─────────────────┐  │
│  │ Send invoice    │  │
│  │ $12,400 · 22h   │  │
│  │ [Approve][View] │  │
│  └─────────────────┘  │
│                       │
│  ┌─────────────────┐  │
│  │ Refund customer │  │
│  │ $89 · 18h       │  │
│  │ [Approve][View] │  │
│  └─────────────────┘  │
│                       │
└───────────────────────┘
```

Pull-to-refresh; swipe-left on a row reveals quick Approve / Reject; swipe-right reveals Snooze (defer for 1h).

## Lifecycle Display

```
Created → Awaiting approval → Approved → Acting → Completed
                          → Rejected (terminal)
                          → Expired (re-engageable)
```

The inbox row shows the current state and the time in state. Transitions animate (fade + slide).

## Push Coupling

Every state transition that needs user attention fires a push:

| Transition | Push |
|---|---|
| → AWAITING_APPROVAL | yes |
| stall warning | yes |
| → COMPLETED | yes (unless user opted out per-feature) |
| → FAILED | yes |
| approval expiring in 1h | yes |

Tap-through to the specific inbox row.

## Privacy

The inbox can be shared in a multi-user tenant. Permissions:

- Approvals: visible only to the user who initiated, the assignee (if explicit), and tenant admins.
- In-flight tasks: same.
- Other users in the same tenant: do not see by default. Configurable per-feature (some teams want a shared queue).

Role-based access enforced server-side; UI hides what server hides.

## Trace Link

Every row has a "View trace" affordance:

- Visible to: customer admins (their own tasks), platform staff (any task).
- Visible content: redacted (PII tombstoned).
- Deep-link to the task viewer (`ai-agent-observability-and-replay` §4).

## Performance

- Inbox loads p95 < 600ms for 50 rows.
- Real-time updates via SSE / WebSocket; new approvals fade in.
- Stale state warning if connection drops > 30s.

## Accessibility

- All actions keyboard-reachable.
- Screen-reader labels: "Pending approval, expires in 22 hours, 12 minutes. Send invoice to ACME for 12,400 dollars. Primary action: Approve."
- High-contrast mode: status colour-coding paired with icons + text.
- Focus order: filters, then rows, then actions per row.

## Telemetry

- Inbox open count per user / day.
- Time-to-decision per approval (from row visible → action taken).
- Bulk-action usage rate.
- Push-to-inbox open rate.
- Inbox-to-trace click-through rate (staff).
- Approval-expired-from-inbox rate (UX failure indicator).

## Anti-Patterns

- Inbox available only inside the agent feature; not surfaced globally.
- Inbox loads slowly for users with many tasks. Power users abandon.
- No filters; power user can't find the task they need.
- Bulk actions absent. Tedious for high-volume agents.
- Trace link visible to customers (leaks internal reasoning).
- Push doesn't deep-link to the exact row; user must scroll/filter to find it.
- Inbox empty state is the default "404"-looking screen, doesn't explain what an inbox is.
- Mobile inbox built only as a responsive web view; native tab missing.
