# Reversible vs Irreversible Tool Classification

Every tool is classified. The classification governs whether approval is required, how long the undo window is, and whether the tool can be auto-executed by an agent.

## The Three Buckets

### `read_only`
No state change. No external call with side-effect. Pure information retrieval or computation.
- Approval: never required.
- Auto-execute: yes.
- Examples: `search_kb`, `get_customer`, `calculate`, `fetch_dashboard`, `list_invoices`, `current_time`.

### `reversible`
State change exists, but can be undone in **under 5 minutes** via a documented compensating action that the platform actually implements. No customer-visible exposure during the window.
- Approval: optional (configurable per feature; default approval on Free/Pro tier, auto on Enterprise with audit).
- Undo window: at least 60 seconds before the change "settles" (e.g., a "Sending..." toast with an Undo button).
- Examples: `invoice_create_draft` (deletable until sent), `task_assign` (reassignable), `tag_add` (untag), `note_create`, `event_schedule_internal`.

### `irreversible`
Cannot be undone, OR undo is costly, customer-visible, or regulated.
- Approval: **always** required.
- Auto-execute: forbidden, even for Enterprise. The most senior tier can bulk-pre-approve, but each action still records consent.
- Examples: `email_send_external`, `payment_charge`, `payment_refund`, `record_delete`, `account_close`, `public_post_publish`, `government_form_file`, `slack_message_send_external`, `webhook_call_external`.

## The Decision Tree

For every new tool, answer:

```
1. Does it change state? 
   No  → read_only
   Yes → 2

2. Does it touch anyone outside the tenant's own staff?
   (sends external email, posts to public channel, charges a card, files a form, calls a public webhook)
   Yes → irreversible
   No  → 3

3. Is the undo a clean, documented platform operation that completes in < 5 min?
   No  → irreversible
   Yes → 4

4. During the undo window, can anyone other than the actor see / use the change?
   Yes → irreversible (because the leakage is irreversible even if the record isn't)
   No  → reversible
```

## Per-Field Sub-Classification

A tool with mixed effects splits into multiple tools, each with its own classification. **Do not** ship a single tool that's reversible *or* irreversible depending on args.

Bad:
```
invoice_action(action: "draft" | "send", ...)   # reversibility depends on `action`
```

Good:
```
invoice_create_draft(...)        # reversible
invoice_send_for_approval(...)   # reversible (it's still a draft pending human review)
invoice_finalise_and_send(...)   # irreversible
```

The model picks the right tool; approval is wired to the right one.

## Worked Examples

| Tool | Classification | Reason |
|---|---|---|
| `customer_lookup_by_email` | read_only | Pure read |
| `kb_search` | read_only | Pure read |
| `invoice_create_draft` | reversible | Draft, deletable |
| `invoice_send_to_customer` | irreversible | External party receives email |
| `note_create_internal` | reversible | Internal note, deletable, no external eyes |
| `task_assign(user_id)` | reversible | Reassignable; only internal staff sees |
| `task_complete` | reversible if undo restores all state; otherwise irreversible |
| `record_delete` | irreversible | Even with soft-delete, dependent state and audit make rollback painful |
| `record_soft_delete` | reversible | If undo is a single click and within window |
| `payment_charge` | irreversible | Card charged, statement landed |
| `payment_refund` | irreversible | Customer notified, money moved |
| `email_send_internal` | reversible | Internal email, recallable on Outlook within window? Treat as irreversible for safety. |
| `email_send_external` | irreversible | Always |
| `public_post_publish` | irreversible | Public eyes |
| `webhook_call_internal` | reversible if idempotent + dedupable; else irreversible |
| `slack_post_to_internal_channel` | reversible | Editable / deletable within minutes |
| `slack_post_to_customer_channel` | irreversible | External eyes |
| `calendar_event_create_for_customer` | irreversible | Customer's calendar pinged |
| `calendar_event_create_internal` | reversible | Internal only |
| `report_generate_pdf` | read_only | Generation alone is read-only; delivery is separate |
| `report_email_pdf_to_customer` | irreversible | External |
| `data_export_to_customer_workspace` | irreversible | Egress; cannot recall |
| `account_close` | irreversible | Cascade effects |
| `password_reset_force` | irreversible | Customer notified, sessions invalidated |

## Side-Effect Burst Sub-Classification

A tool may be individually reversible but **collectively irreversible** in burst.

Example: `task_assign` is reversible per call. But "reassign 10,000 tasks to a different user" floods notifications, alerts, integration webhooks, and emails — irreversibility emerges from volume.

Mitigation: side-effect budgets cap burst (`references/tool-side-effect-budgets.md`).

## Documentation Requirement

Every tool's classification must be documented with:

```yaml
name: invoice_send_to_customer
classification: irreversible
reason: |
  Sends email to the customer's external address with the invoice
  PDF attached. Customer cannot un-receive the email. Aging clock
  starts on receipt. Tax record generated.
undo_procedure: |
  None. Compensating action is to send an email correction or void
  the invoice and re-issue.
approval_required: true
approval_blast_radius: per_recipient
```

This documentation is reviewed by the security team during tool onboarding.

## Re-Classification

Classifications can be raised (read_only → reversible → irreversible) any time without a deprecation cycle. Lowering (irreversible → reversible) requires a security review and 30-day notice, and is rare.

## Anti-Patterns

- "It's mostly reversible, so we'll call it reversible." If 1% of calls are irreversible, treat the tool as irreversible.
- Classification based on the *intent* of the user. The agent has access to the tool whether or not the intent was benign.
- Reclassifying a tool down to "reversible" to skip approval and ship faster.
- A `tool_action` arg that toggles reversibility. Split into separate tools.
