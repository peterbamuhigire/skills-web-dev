# Just-In-Time Approval Flow — Implementation

## Sequence

```
agent runtime
   │
   │  plans next step → step.tool.reversibility == 'irreversible'
   │  OR step.tool.blast_radius > threshold
   │
   ├──> persist agent_approvals row (state='pending')
   ├──> publish agent.task.awaiting_approval event
   ├──> transition task.state = 'AWAITING_APPROVAL'
   └──> exit worker loop (release resources)

notifier
   │
   ├──> push notification to user (if mobile registered)
   ├──> in-product banner (if user is online)
   └──> email (if no mobile + offline > 5 min)

user
   │
   ├──> opens approval (mobile push deep-link OR in-app)
   ├──> sees plan preview / step preview
   └──> decides: approve / approve-and-background / edit / reject

API
   │
   ├──> PATCH /approvals/{id}  { decision: 'approved', edits?: {...} }
   ├──> update agent_approvals.state
   ├──> publish agent.approval.received event
   └──> enqueue resume task

agent runtime (resumed worker)
   │
   ├──> reads approval (state, edits)
   ├──> if edits: merge into step args
   ├──> transition task.state = 'ACTING'
   └──> execute the tool with idempotency key
```

## Blocking vs Background

On first JIT approval per session, the UI asks:

> "Stay here while the agent works, or get a notification when it's done or needs you again?"

| Choice | UX | Backend |
|---|---|---|
| Stay | Loading state, agent continues, UI streams updates | Live connection (WebSocket / SSE) |
| Background | Approval accepted, screen returns user to inbox; push when next event | Disconnects; resumes via push |

Persist the choice per `(user_id, agent_feature)` — don't ask again.

## Expiry and Escalation

```
approval lifecycle:
   created_at        = T0
   reminder_at       = T0 + 4h       → send "this is still waiting"
   expires_at        = T0 + 24h      → state='expired', no auto-action
   re-prompt_at      = T0 + 48h      → notification "we abandoned this; resume?"
```

Tunable per feature:
- Production-system irreversibles: shorter expiry (e.g., 1 hour) — stale data.
- Customer-facing emails: longer expiry (24h) — relationship-time scales.

On `expired`:
- Task moves to `AWAITING_APPROVAL`-but-stale; visible in agent inbox.
- User can `resume`, which causes the agent to re-plan from current state (not re-run from scratch) and re-issue an approval.

## Mobile Push Implementation

```typescript
// On agent.task.awaiting_approval event
function notifyApprover(approval: AgentApproval) {
  const user = users.get(approval.user_id);
  const tokens = user.push_tokens.filter(t => t.platform_supports_actions);

  for (const t of tokens) {
    push.send({
      token: t.token,
      payload: {
        title: titleFor(approval),
        body: bodyFor(approval),  // includes blast-radius summary
        category: 'agent_approval',
        actions: [
          { id: 'approve', title: 'Approve', authenticationRequired: irreversible(approval) },
          { id: 'view',    title: 'View plan' },
          { id: 'reject',  title: 'Reject' }
        ],
        data: {
          approval_id: approval.id,
          tenant_id: approval.tenant_id,
          deeplink: `app://approval/${approval.id}`
        }
      }
    });
  }
}
```

For irreversible actions, the mobile OS prompts for biometric/PIN before sending the response. This is a platform feature (`UNNotificationActionOptionAuthenticationRequired` on iOS).

## Edits

The user can edit the args before approval:

```typescript
PATCH /approvals/12345
{
  "decision": "approved",
  "edits": {
    "step_index": 4,
    "args": {
      "to": "ben@acme.example",
      "subject": "ACME — Q2 invoice (updated)",
      "body": "...edited body..."
    }
  }
}
```

The agent runtime merges `edits.args` into the planned tool call. The merged args are persisted in `agent_steps.tool_args` so traces show what actually ran, not what was originally planned. The `agent_approvals.decision_edits` field stores the diff.

## Approve-And-Background

```typescript
// User chose "approve and run in background"
PATCH /approvals/12345
{ "decision": "approved", "execution_mode": "background" }

// Agent runtime resumes; user is disconnected from streaming.
// On next awaiting_approval OR task completion:
//   - notify via push
//   - banner shows in app on next visit
```

## "Approve & Auto-Approve Similar This Task"

Scoped standing approval within the task's lifetime. The rules:

- Scope: same tool name, same shape of args (whitelisted fields), same blast-radius bucket.
- Audit: every auto-approved step records `auto_approved_under: approval_id`.
- Revoke: user can revoke from inbox; revocation applies to future steps in the task only.

Implementation:

```sql
CREATE TABLE agent_standing_approvals (
  id          BIGINT PRIMARY KEY,
  task_id     BIGINT NOT NULL,
  approval_id BIGINT NOT NULL,        -- parent approval
  tool_name   VARCHAR(128) NOT NULL,
  args_match  JSON NOT NULL,          -- field whitelist or pattern
  max_uses    INT NOT NULL,
  uses        INT NOT NULL DEFAULT 0,
  expires_at  DATETIME NOT NULL,
  revoked_at  DATETIME
);
```

Hard cap `max_uses` (default 5) to prevent runaway. After hitting `max_uses`, the agent must request a fresh approval.

## Failure Modes

| Failure | Handling |
|---|---|
| User approves, but tool fails | Task transitions to FAILED; user notified; approval marked `executed=false, error=...` |
| User approves, tool succeeds, but post-step fails | Action was executed (audited); next step retries; approval stays `executed=true` |
| Worker crashes between approval read and tool call | Idempotency key on the tool call; restart re-attempts safely (see runtime architecture) |
| User edits args to something invalid | Pre-flight validation against tool schema before allowing approval; reject edit if invalid |
| User rejects with "soft" feedback | Agent re-plans with feedback in context; new approval cycle if needed |

## Telemetry

- `approval.shown_to_decided_seconds` — median, p90, p99
- `approval.rejection_rate` — by feature, by tool
- `approval.edit_rate` — by feature, by tool (high edit rate = agent generates wrong args)
- `approval.expiry_rate` — UX failure indicator
- `approval.standing_invocations_per_task` — power-user load
- `approval.background_mode_rate` — preference signal
