---
name: ai-agent-mobile-and-web-ux-patterns
description: Use when designing the in-product UX for agentic features — the agent inbox, plan preview, approve/edit/cancel surfaces, "agent at work" indicators, mobile-safe approval flows, agent persona patterns, and trust-building affordances. Distinct from `ai-agentic-ui` (general AI UI patterns) by being agent-product specific.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Mobile and Web UX Patterns
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing the agent's UI surfaces inside a SaaS product — chat panel, agent inbox, plan preview, approval modals, "agent at work" banner.
- Designing **mobile-safe approval flows** — push notification → one-tap approve / preview / reject, with biometric step-up for irreversibles.
- Designing the **agent inbox** that queues pending approvals when the user isn't in the conversation.
- Designing **status / progress** indicators for long-running tasks.
- Designing **agent persona** boundaries (when does the agent speak as itself vs as the platform).
- Designing **trust-building affordances** ("View trace", "Why this action", "Forget this").

## Do Not Use When

- The task is general AI UI patterns — `ai-agentic-ui`.
- The task is the approval state machine / patterns — `ai-agent-action-approval-and-hitl`.
- The task is general premium product UX — `premium-ui-ux-design`.

## Required Inputs

- Brand and design system (`premium-ui-ux-design`, design tokens).
- Approval pattern decisions (`ai-agent-action-approval-and-hitl`).
- Mobile platforms in scope (web responsive, native iOS, native Android).
- Notification infrastructure.
- Agent-persona definition (voice, tone, scope from `ux-content-strategy`).

## Workflow

1. Read this `SKILL.md`.
2. Build the **agent inbox** (§1). See `references/agent-inbox-spec.md`.
3. Build the **plan preview component** (§2).
4. Build the **approval modal / sheet** (§3) — web + mobile.
5. Build the **"agent at work" indicator** (§4).
6. Build the **progress for long-running tasks** (§5).
7. Define the **agent persona boundaries** (§6).
8. Build **trust-building affordances** (§7).
9. Apply **mobile-safe approval flow** (§8).
10. Apply anti-patterns (§9).

## Quality Standards

- The agent inbox is reachable in **≤ 2 clicks** from anywhere in the app.
- Pending approvals are visible **on every page**, not just inside the agent feature.
- Approval payload shows concrete args, not free text — never "send the invoice?".
- Mobile push notifications support **inline actions** (Approve / View / Reject) where the OS permits.
- Irreversible approvals require **biometric or PIN** re-auth on mobile.
- The "agent at work" indicator does **not** block the rest of the product — the user can navigate while the agent runs.
- Every agent surface has a "View trace" affordance that opens the task viewer (role-gated).
- Agent persona is consistent; the agent speaks **as itself** ("I"), not as the platform ("we").
- Trust affordances ("Forget this", "Why did the agent...?") are reachable in 1 click from any agent surface.

## Anti-Patterns

- Agent surfaces look identical to non-agent surfaces. Users don't notice an agent did the thing.
- Pending approval only visible inside the agent chat. User forgets; expires.
- Approval modal that's full-screen + 500ms loading + 4MB of JS. Mobile abandonment.
- Push notifications without inline actions. User must launch app for one tap.
- Push notification leaks customer name / amount in the body. Lock-screen exposure.
- Agent persona drifts ("we" / "I" / "the system" all on the same screen).
- "View trace" affordance shown to customers who shouldn't see internal traces.
- Progress indicator that's a spinner with no detail. User thinks it's broken.
- Agent inbox without filters. Power users with many pending approvals can't triage.
- Long-running task with no cancel button.

## Outputs

- Agent inbox component spec.
- Plan preview component spec.
- Approval modal / sheet spec (web + mobile).
- "Agent at work" indicator.
- Progress UX for long-running tasks.
- Agent persona guide.
- Trust affordances catalogue.
- Mobile push notification templates.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX | Agent inbox spec | Markdown + Figma | `docs/ux/agent-inbox.md` |
| UX | Approval flow walkthrough | Markdown + screens | `docs/ux/agent-approval-flow.md` |
| UX | Mobile push templates | Markdown | `docs/ux/agent-push-templates.md` |
| Release evidence | Usability test report | Markdown | `docs/ux/agent-usability-2026-04.md` |

## References

- `references/agent-inbox-spec.md` — full inbox component spec.
- Companion: `ai-agentic-ui`, `ai-agent-action-approval-and-hitl`, `premium-ui-ux-design`, `ux-content-strategy`, `practical-ui-design`, `form-ux-design`, `ai-output-design`.

<!-- dual-compat-end -->

## §1 Agent Inbox

The single place a user finds:
- Pending approvals (sorted by expiry).
- In-flight tasks (with progress).
- Recently completed (with outcome).
- Failed / abandoned (with reason + retry).

Full component spec in `references/agent-inbox-spec.md`.

Reachable from: top-nav badge, global keyboard shortcut, mobile tab.

## §2 Plan Preview Component

```
┌─ Agent plan ────────────────────────────────────────────────┐
│  Goal: Send invoice to ACME for May hours                   │
│                                                             │
│  Step 1.  Look up ACME billing contact                      │
│           tool: customer_lookup                              │
│           [Read-only]                                        │
│                                                             │
│  Step 2.  Calculate hours from time entries                 │
│           [Read-only]                                        │
│                                                             │
│  Step 3.  Create invoice draft INV-1234                     │
│           [Reversible — undo within 24h]                    │
│                                                             │
│  Step 4.  Send invoice to ben@acme.example     ⚠ External   │
│           [Irreversible — requires approval]                 │
│                                                             │
│  Estimated cost: $0.12   ·   Wallclock: ~30s                │
│                                                             │
│  [Approve plan]   [Approve through step 3]   [Edit step 4]  │
│  [Cancel]                                                   │
└─────────────────────────────────────────────────────────────┘
```

Design rules:
- Reversibility badge on every step.
- Irreversible steps stand out (warning colour, icon).
- Estimated cost / time visible — sets expectation.
- Partial approval ("through step N") for plans where the user wants to vet later steps individually.

## §3 Approval Modal / Sheet

Web: modal centered, max-width 600, dismissible by Escape.
Mobile: bottom sheet, swipe-down to dismiss, primary action thumb-reachable.

Critical content order (top → bottom):
1. **What** (tool / business label).
2. **Concrete args** — recipient, amount, target ID.
3. **Reversibility / blast radius**.
4. **Why** (one-line rationale from the agent).
5. **Actions** — primary: Approve. Secondary: Edit. Tertiary: Reject.

Edit opens a form populated with the args. Save → re-validate against tool schema → submit.

## §4 "Agent at Work" Indicator

Inline (non-blocking):

```
[Agent] is working on "investigate Q1 churn" — step 3 of ~6   [View]   [Cancel]
```

- Persistent banner top of viewport, dismissible (collapses to badge).
- Click "View" → opens task in inbox.
- Cancel triggers compensation flow (`ai-agent-reversibility-and-blast-radius`).

For multiple concurrent agent tasks, badge shows count.

## §5 Progress for Long-Running Tasks

```
Investigating last month's churn   [Cancel]

Step 4 of ~7         ████████░░░░░ 57%
Currently: analysing canceled accounts by segment
ETA: ~3 minutes
Started 2 min ago
                                          [View live trace] (admin only)
```

Heartbeat at least every 60s. If heartbeat stops, show "still working… (last update 2 min ago)" then "appears stalled — [Resume] [Cancel]" after threshold.

## §6 Agent Persona Boundaries

| Speaker | Voice | When |
|---|---|---|
| The agent | "I" | Performing the task, reporting steps, asking for input |
| The platform | "we" / "Platform Name" | Settings, billing, security messages, policy |
| The user | "you" / "your" | Addressing the user |

The agent does not speak for the platform ("our policy says...") — it cites the platform ("Platform Name's refund policy says..." with link). This keeps liability surfaces clean.

Visual: the agent has a small avatar / name tag. The platform speaks without that.

## §7 Trust Affordances

| Affordance | Where | What it does |
|---|---|---|
| "View trace" | Every agent message, every inbox row | Role-gated (admin / staff) deep-link to the task viewer |
| "Why this?" | Next to any tool call surfaced to the user | Shows the agent's one-line rationale |
| "Forget this" | Memory items | Triggers `agent-memory` forget flow |
| "Export plan" | Plan preview | Download as PDF (audit, share) |
| "How accurate is this?" | Final response | Surfaces grounding citations (`ai-hallucination-slo-and-grounding`) |
| "Report a bad answer" | Final response | Creates a ticket linked to the trace |

## §8 Mobile-Safe Approval Flow

```
[ Lock screen push ]
  Approve agent action — $89 refund to a customer
  [Approve]  [View]  [Reject]

  ↓ tap Approve
  [iOS / Android] Authenticate with Face/Touch ID

  ↓ success
  [Notification fades]
  In-app: "Approved · refund processing"
  [Push back-confirmation 2-5s later]
```

Rules:
- Lock-screen body is generic enough to avoid PII leak ("Approve refund to a customer" not "Approve refund $89 to Jane Doe ben@acme.example").
- Irreversible actions require biometric / PIN at the OS layer.
- A "View" action deep-links into the app on the approval screen with the full context.
- Network failure on Approve → retry up to 3 times with exponential backoff; on final fail, surface "Couldn't reach our servers — pending in your inbox".

Templates:

```yaml
push.agent_approval.irreversible:
  title: "Approve agent action"
  body: "{{ blast_summary }}"            # e.g., "$89 refund"
  category: "agent_approval_irreversible"
  authentication_required: true
  actions: [approve, view, reject]
  deeplink: "app://agent/approval/{{ id }}"

push.agent_approval.reversible:
  title: "Approve agent action"
  body: "{{ blast_summary }}"
  category: "agent_approval_reversible"
  authentication_required: false
  actions: [approve, view, reject]
  deeplink: "app://agent/approval/{{ id }}"
```

## §9 Anti-Patterns

- No badge on the top-nav for pending approvals. Users miss expirations.
- "Are you sure?" as the entire approval UX.
- Approval modal renders the agent's natural-language plan with no concrete args.
- Mobile push leaks customer PII in body.
- Spinner with no detail for tasks > 10s.
- Inline actions on push absent on Android even though available.
- Agent voice drifts between "I" and "we".
- "View trace" surfaced to customers.
- No cancel on long-running tasks.
- Agent's avatar identical to user's avatar in chat. Confusing turn attribution.
