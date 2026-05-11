---
name: ai-agent-action-approval-and-hitl
description: Use when designing the human-in-the-loop layer for agentic features — multi-step plan approval UX, single-shot approval, bulk approval, just-in-time approval, "explain the plan", undo windows, partial-plan edits, and mobile-safe approval flows. Distinct from `ai-agents-tools` (which sketches a SQL approval table) by being the full UX + approval-state-machine contract.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Action Approval and Human-in-the-Loop
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Adding approval to agent actions that are irreversible or above a blast-radius threshold.
- Designing the **plan preview** UX (show the user the full plan before any action runs).
- Designing **bulk approval** ("approve all 12 outgoing emails" — with edit / drop per item).
- Designing **just-in-time approval** ("this step needs approval now"); choosing between blocking the agent vs background continuation.
- Designing **undo windows** for reversible actions ("Sending in 8s — Undo").
- Building the **agent inbox** where pending approvals queue when the user isn't actively in the conversation.
- Mobile-safe approval flows (notification → one-tap approve / preview).

## Do Not Use When

- The task is the tool's reversibility classification itself — `ai-agent-tool-catalogue-and-action-gating`.
- The task is the agent loop state machine — `ai-agent-runtime-architecture`.
- The task is generic SaaS approval workflows (PO approval, leave approval) — use `saas-erp-system-design`.
- The task is the back-office approval (staff overriding tenant approvals) — `saas-admin-backoffice-tooling`.

## Required Inputs

- Tool reversibility classification (`ai-agent-tool-catalogue-and-action-gating`).
- Agent runtime state machine (`ai-agent-runtime-architecture`).
- Customer-facing UX framework (premium-ui-ux-design, `ai-agentic-ui`).
- Notification infrastructure (email, push, in-app).
- Mobile clients in scope: web responsive, native iOS, native Android.

## Workflow

1. Read this `SKILL.md`.
2. Pick the **approval pattern** per feature (§1). See `references/approval-ux-patterns.md`.
3. Define the **approval state machine** (§2). Includes timeouts, expiry, escalation.
4. Implement **plan preview** (§3) — what the user sees before approving.
5. Implement **bulk approval with per-item edit/drop** (§4).
6. Implement **just-in-time approval** (§5) and decide blocking vs background. See `references/just-in-time-approval-flow.md`.
7. Implement **undo window** for reversible auto-executed actions (§6).
8. Wire the **agent inbox** (§7) where pending approvals queue.
9. Apply **mobile-safe approval flow** (§8).
10. Apply anti-patterns (§9).

## Quality Standards

- Every irreversible action passes through an explicit approval; no auto-execute.
- Plan preview is **complete** — every action the agent will take is shown, in order, with concrete arguments.
- Approval payload shows **what** the agent will do, **why** (one-line rationale), and **what cannot be undone**.
- Bulk approval allows per-item edit and per-item drop without re-running the agent.
- Just-in-time approval offers two paths: block-and-wait or background-and-notify; user chooses on first approval.
- Reversible actions have an undo window of at least 5 seconds (configurable per feature).
- Mobile approval works from a push notification → one-tap approve or one-tap "show details".
- Expired approvals do **not** auto-deny; they queue and notify so the user finishes the task on their schedule.

## Anti-Patterns

- "Are you sure?" modal as the entire approval UX. The user doesn't know what they're approving.
- Approval payload is the agent's natural-language summary only, with no concrete tool arguments.
- Bulk approval that auto-runs everything if any one item is approved.
- Just-in-time approval that holds the agent thread open for 24 hours, blocking other tasks.
- Mobile approval flow that requires the user to load a 4MB chat page to see context.
- Undo window with no actual undo wired up (button is fake or 500s).
- "Approve all future actions of this kind" — escalation of consent without scope (and without an expiry).
- Approval persisted in user session only — refresh loses it.

## Outputs

- Per-feature approval-pattern decision (single-shot / bulk / JIT / undo-window).
- Approval state-machine spec.
- Plan-preview UI component spec.
- Bulk approval list spec with per-item edit/drop.
- JIT approval blocking-vs-background decision.
- Undo window infrastructure (timer + cancel hook).
- Agent inbox spec.
- Mobile push approval flow.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX | Approval pattern decision per feature | Markdown / table | `docs/ai/agent-approval-patterns.md` |
| Architecture | Approval state machine spec | Markdown + diagram | `docs/ai/agent-approval-state-machine.md` |
| Release evidence | Approval flow user test report | Markdown | `docs/ux/agent-approval-test-2026-04.md` |
| Operability | Expired approval / escalation runbook | Markdown | `docs/runbooks/agent-approval-expiry.md` |

## References

- `references/approval-ux-patterns.md` — six patterns with when-to-use, screenshots/wireframes, anti-patterns.
- `references/just-in-time-approval-flow.md` — JIT implementation, blocking vs background, mobile.
- Companion: `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-runtime-architecture`, `ai-agent-reversibility-and-blast-radius`, `ai-agent-mobile-and-web-ux-patterns`, `ai-agentic-ui`, `premium-ui-ux-design`.

<!-- dual-compat-end -->

## §1 Approval Patterns at a Glance

| Pattern | Best for | Friction |
|---|---|---|
| **Single-shot** | One irreversible action at the end of an agent run | Low |
| **Plan-preview** | Agent has a clear multi-step plan, all steps shown upfront | Medium |
| **Bulk approval** | Many similar items (12 emails, 30 invoices) | Medium |
| **Just-in-time** | Plan emerges as agent runs; irreversibility appears mid-task | High |
| **Undo window** | Reversible action, want low friction + safety | Very low |
| **Standing approval** | Trusted user, narrow scope, time-boxed | Lowest, riskiest |

See `references/approval-ux-patterns.md` for the full taxonomy and selection rule.

## §2 Approval State Machine

```
              created
        ┌────────────────┐
        ▼                │
   ┌─────────┐    edit   │
   │ pending │ ─────────►│
   └────┬────┘           │
        │ ┌──── reject ──┘
        │ │
        │ ▼
        │ ┌────────┐
        │ │rejected│   terminal
        │ └────────┘
        │ approve
        ▼
   ┌──────────┐    undo (within window)
   │ approved │ ────────────► canceled (terminal)
   └────┬─────┘
        │ executed
        ▼
   ┌──────────┐
   │ executed │   terminal
   └──────────┘
        ▲
        │ expire (no decision)
   ┌────┴─────┐
   │ expired  │   terminal (does NOT auto-execute, does NOT auto-deny)
   └──────────┘
```

Key invariants:

- An expired approval is **inert**. It does not run, and it does not block — but the agent task is paused awaiting a fresh approval cycle.
- `undo` is only valid within `undo_window_seconds`. After that, undo becomes a compensating action (a new agent task or manual flow).
- `executed` is the terminal success. Anything that wants to "undo executed" creates a compensating task; the original approval row is immutable.

```sql
CREATE TABLE agent_approvals (
  id                  BIGINT PRIMARY KEY,
  task_id             BIGINT NOT NULL,
  tenant_id           BIGINT NOT NULL,
  user_id             BIGINT NOT NULL,
  approver_id         BIGINT,         -- may differ from user_id
  pattern             ENUM('single_shot','plan_preview','bulk','jit','undo_window','standing') NOT NULL,
  state               ENUM('pending','approved','rejected','expired','executed','canceled') NOT NULL,
  plan_payload        JSON NOT NULL,  -- full plan + concrete args
  rationale           TEXT,
  blast_radius        JSON,           -- estimated impact (e.g., recipients, amount)
  created_at          DATETIME NOT NULL,
  expires_at          DATETIME NOT NULL,
  decided_at          DATETIME,
  executed_at         DATETIME,
  undo_until          DATETIME,
  decision_reason     TEXT,
  decision_edits      JSON,           -- per-item edits
  notification_sent   JSON            -- {email, push, sms}
);
```

## §3 Plan Preview Component

A plan preview is **not** the agent's chat output. It is a structured component:

```
┌─ Plan ───────────────────────────────────────────────────┐
│  Goal: send invoice to ACME for May hours                │
│                                                          │
│  1. Look up ACME's billing contact   (read-only)         │
│  2. Calculate hours from time entries (read-only)        │
│  3. Create invoice draft #INV-1234   (reversible)        │
│  4. Send invoice to ben@acme.example (irreversible)  ⚠   │
│                                                          │
│  Estimated cost: $0.12                                   │
│  Will email: ben@acme.example                            │
│                                                          │
│  [Approve all]  [Edit step 4]  [Approve through step 3]  │
└──────────────────────────────────────────────────────────┘
```

- Each step lists tool name, business label, classification, expected effect.
- Irreversible steps marked visually (⚠).
- "Approve through step N" allows partial approval — the agent will run to step N and pause for replanning.

## §4 Bulk Approval

For "send 12 emails" cases:

```
☐ Approve all   12 items selected
┌─ #1  Email to ben@acme.example ─ "May invoice" ──── [edit] [drop]
│   To: ben@acme.example
│   Subject: ACME — May 2026 invoice
│   Preview: Hi Ben, attached is the invoice for hours...
├─ #2  Email to ana@beta.example ─ "May invoice" ──── [edit] [drop]
│   To: ana@beta.example
│   ...
```

Per item:
- Edit: opens the args in a form; saves over the plan.
- Drop: removes from the bulk; doesn't fire.
- Selection: only ticked items execute. Default all ticked.

The agent does not re-plan on a drop — it skips that item. If the user edits, the edit is applied to the args; the tool runs with the edited args.

## §5 Just-In-Time Approval

When an irreversible action emerges mid-task:

1. Agent transitions to `AWAITING_APPROVAL`.
2. UI shows the **current step preview** (not the original plan), with: what just happened, what's next, why approval is needed.
3. The user picks one path:
   - **Approve and stay**: blocking, agent resumes when user clicks.
   - **Approve and run in background**: agent continues, notification on completion or next approval.
   - **Approve and auto-approve similar for this task**: standing approval within this task's scope.

After 24h with no decision → `expired`; agent stays paused, queued in agent inbox.

Full implementation in `references/just-in-time-approval-flow.md`.

## §6 Undo Window

For **reversible** auto-executed actions only. The action fires; UI shows:

```
[ ✓ Tagged 15 leads ]    Undo (8s)
```

Implementation:
1. Tool executes the action with a `staged_until` timestamp.
2. UI starts a countdown.
3. If user clicks Undo within the window, the agent runtime calls the tool's compensating action.
4. After the window, the tool transitions `staged → committed`. Undo becomes "create a new compensating task".

Tools that support undo register a `compensate(args, original_result)` function.

## §7 Agent Inbox

Where pending approvals queue when the user is not actively in the agent's conversation:

- One row per pending approval.
- Sort: oldest expiring first.
- Bulk select + approve / reject from inbox.
- Filter by feature / agent / blast-radius.
- Mobile push for new pending items.
- Auto-archive on `expired`, `executed`, `rejected`.

Component spec in `references/agent-inbox-spec.md` (under `ai-agent-mobile-and-web-ux-patterns`).

## §8 Mobile Approval

Push notification payload:

```json
{
  "title": "Approve agent action",
  "body": "Send invoice $12,400 to ACME?",
  "actions": [
    { "id": "approve",     "title": "Approve" },
    { "id": "view",        "title": "View plan" },
    { "id": "reject",      "title": "Reject" }
  ],
  "data": { "approval_id": 12345, "tenant_id": 42 }
}
```

`approve` / `reject` from the notification require: app installed, user signed in, biometric or PIN re-auth for irreversible.
`view` deep-links to the plan preview screen.

## §9 Anti-Patterns

- Approval phrased as "Do you want me to proceed?" with no concrete args.
- Bulk approval that runs all items as a single transaction — one item's failure rolls back everything (often not desired).
- JIT approval that blocks the agent's thread holding a database transaction open.
- Expired approvals auto-execute "because the user probably meant yes".
- Undo button that's actually a delete-after-the-fact (sends two emails: one wrong, one correction).
- Standing approval with no scope and no expiry. Power user gets phished, agent drains the org.
- Approval payload renders the agent's free-text plan only. User cannot inspect actual arguments.
- Mobile approval that doesn't re-auth before an irreversible action.
