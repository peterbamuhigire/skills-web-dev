# Approval UX Patterns — Six Patterns and When to Use Each

## 1. Single-Shot Approval

**Pattern:** Agent does all read/reversible work autonomously. Stops at the single irreversible step and asks once.

**Use when:** the agent's job culminates in one external action (one email, one charge, one filing).

**UX:**
```
✓ Pulled May time entries
✓ Calculated $12,400
✓ Drafted invoice INV-1234

The invoice is ready to send to ben@acme.example.

[ Approve and send ]   [ Edit invoice ]   [ Cancel ]
```

**Pros:** lowest friction, clearest mental model.
**Cons:** doesn't work when multiple irreversibles emerge.

## 2. Plan-Preview Approval

**Pattern:** Agent plans all steps upfront, shows the user the full plan, user approves the whole thing or partially.

**Use when:** the agent can plan ahead reliably, the user wants to see the full scope before anything runs.

**UX:** See SKILL §3 wireframe.

**Pros:** user has full context; can approve a sub-prefix; no surprises mid-run.
**Cons:** requires the agent to plan reliably; if mid-execution requires re-plan, you must re-show the preview.

## 3. Bulk Approval

**Pattern:** Agent generates N similar items (12 invoices, 30 emails). User reviews all, edits any, drops any, then approves the rest.

**Use when:** outputs are repetitive but each requires sanity check.

**UX:** See SKILL §4 wireframe.

**Pros:** scales review across many items.
**Cons:** review fatigue → blanket-approve risk. Mitigate with "preview the first 3 fully, summarise the rest".

## 4. Just-In-Time (JIT) Approval

**Pattern:** Agent proceeds; when it hits an irreversible step it cannot predict ahead of time, it pauses and asks.

**Use when:** plans are emergent; the agent genuinely cannot enumerate steps upfront (e.g., investigation agent).

**UX:**
```
[Running — step 4 of ~7]

Step 4 needs your approval:
  Tool: payment_refund
  Customer: bob@example.com
  Amount: $89.00
  Why: customer reported double charge in step 2's lookup

[ Approve ]  [ Edit ]  [ Reject ]  [ Approve & continue without further approvals (this task) ]
```

**Pros:** flexible, doesn't waste planning effort.
**Cons:** highest friction; can train users to rubber-stamp.

Anti-rubber-stamp: vary the visual treatment based on blast-radius; force a re-read for high-impact items.

## 5. Undo Window

**Pattern:** For *reversible* actions, fire immediately and show an undo button.

**Use when:** action is unambiguously reversible and approval friction is hurting product flow (e.g., agent tagging records).

**UX:**
```
✓ Tagged 15 leads as "high intent"   [ Undo (8s) ]
```

**Pros:** feels fast, still safe.
**Cons:** only works for genuinely reversible actions. Misclassification creates real damage.

Tunings:
- Length: 5-60s depending on impact.
- Cancellation pause: do not show next "✓" until window expires; otherwise undo cascades.
- Mobile: longer window (10s+), banner persists, haptic on appear.

## 6. Standing Approval

**Pattern:** User pre-approves a class of action within a scope ("this agent may send up to 5 emails per task, no per-email approval").

**Use when:** trusted power user, repeated workflow, narrow scope, time-boxed.

**UX:**
```
Standing approvals for agent "Sales Follow-up":
   ✓  Send emails to leads in pipeline (max 20/day, expires Jun 30)
   ✓  Update lead stage (always)
   —  Delete leads (NEVER — requires per-action approval)

[ Manage standing approvals ]
```

**Pros:** removes friction for repetitive trusted tasks.
**Cons:** highest risk. Always:
- Scope explicitly (which tool, which subset of args).
- Expire (default 30 days).
- Cap (max-per-day).
- Audit (every use logged with "standing approval applied").
- Allow tenant admin to revoke any standing approval at any time.

## Selection Rule

```
if single irreversible at end:                  → single-shot
elif plan is enumerable upfront, ≤ 8 steps:     → plan-preview
elif many similar items:                        → bulk
elif emergent plan, irreversibles mid-task:     → JIT
elif fully reversible auto-fire desired:        → undo window
elif power user wants repeat-flow autonomy:     → standing (with caps)
```

## Cross-Pattern Anti-Patterns

- Mixing JIT + standing without clear scope. The user thinks they pre-approved one thing; the agent fires something else.
- Plan-preview that doesn't actually pin the args — the agent regenerates args at execution time, drifting from what was approved.
- Bulk approval that fires all items in one transaction. One item's failure rolls back everyone's approval.
- Undo window without a real undo. The button does nothing.
- Standing approval that can be granted from a chat message ("you can always send emails on my behalf") without a UI consent flow.
- Mobile push approval that doesn't require re-auth for irreversibles.

## Telemetry to Collect

| Metric | Why |
|---|---|
| Approval rate (%) | Are we asking too often / too rarely? |
| Time to decide (median) | Friction; below 5s = rubber stamp; above 60s = bad payload |
| Edit rate per pattern | Does the agent generate good args? |
| Reject rate | Is the agent confused, or are we asking wrong things? |
| Undo rate (undo window) | Did we misclassify reversibility? |
| Standing approval invocation count | Power user load; spike → review scope |
| Expired approvals | UX failure; user can't tell what to do |
