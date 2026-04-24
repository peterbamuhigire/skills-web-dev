# Progress Tiers — Component Specs

Four tiers, promoted/demoted by information density and audit need.

---

## Notifications (top layer)

Topmost info only. Dismissable. Never more than one line.

**Copy templates:**

- "Agent finished your task."
- "Needs permission to continue."
- "Agent paused - 3 retries failed."

Show in the system notification area (toast, OS notification, or persistent bell). Dismiss on click-through to the run.

---

## Tier 1 — Overview

One line. Always visible while the agent runs.

**Fields:**

- Stage name (current step label).
- Elapsed time.
- Active permission count (if any).

**Layout:**

```
[Running] Step 3 of 5 - "Drafting response"   |   00:04:18   |   0 pending
```

No reasoning, no tool details, no sources. If the user needs more, they expand to Tier 2.

---

## Tier 2 — Detail

One panel. Opens on click from Tier 1.

**Fields:**

- Subtask breakdown (checklist with step state).
- Current reasoning — **collapsed accordion by default** (Lovable pattern).
- Tool/source references for the current step.
- Action buttons: Pause, Rollback, Edit plan.

**Layout:**

```
+----------------------------------------------------------+
| Step 3: Drafting response                                |
|   [OK] Gather context                                    |
|   [OK] Select tone                                       |
|   [..] Draft body                                        |
|   [ ] Review and finalize                                |
|                                                          |
|   > Reasoning  (click to expand)                         |
|                                                          |
|   Tools used this step:                                  |
|     - web_search (2 calls)                               |
|     - draft_writer (1 call)                              |
|                                                          |
|   [Pause]  [Rollback]  [Edit plan]                       |
+----------------------------------------------------------+
```

Reasoning stays collapsed because most users do not want the raw stream. Those who do click once.

---

## Tier 3 — Full Record

Separate view. Complete auditable log.

**Fields:**

- Every tool call with full parameters and returned payload.
- Every checkpoint with artifacts.
- Every permission prompt with timestamp and outcome.
- Every error with full trace.
- Full reasoning stream, not collapsed.

**Use cases:**

- Debugging a bad run.
- Compliance audit (DPPA, SOC 2).
- Post-mortem for agent behavior review.

Never show Tier 3 by default. Link from Tier 2 as "View full log".

---

## Promotion/Demotion Rules

- Start at Notifications + Tier 1.
- Promote to Tier 2 when the user clicks the Tier 1 line, or on first permission prompt, or on first error.
- Tier 3 is always on-demand. Never auto-promote.
- On completion, demote to a Notification with a link back to Tier 2 for review.

**Never** collapse a pending permission prompt into a notification — the user must see it.
