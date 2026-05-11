# Dry-Run Patterns for Agent Tools

A dry-run mode runs a tool's logic without committing the side-effect. It returns the *projected result* — the same shape the real call would return, with a flag indicating it was a preview.

## Contract

Every dry-run-capable tool accepts `dry_run: bool` (default `false`) in args, and returns `dry_run: bool` in the result.

```json
{
  "name": "invoice_send",
  "input_schema": {
    "properties": {
      "invoice_id": { "type": "integer" },
      "to_email":   { "type": "string", "format": "email" },
      "dry_run":    { "type": "boolean", "default": false }
    },
    "required": ["invoice_id"]
  },
  "output_schema": {
    "properties": {
      "status": { "type": "string" },
      "dry_run": { "type": "boolean" },
      "preview": {
        "type": "object",
        "properties": {
          "to": { "type": "string" },
          "subject": { "type": "string" },
          "body_html_truncated": { "type": "string" },
          "attachments": { "type": "array" },
          "would_send_at": { "type": "string", "format": "date-time" }
        }
      },
      "side_effects_would_occur": {
        "type": "array",
        "items": { "type": "string" }
      }
    }
  }
}
```

## Implementation Skeleton (Python)

```python
def invoice_send(args: dict, ctx: ToolContext) -> dict:
    invoice = invoices.get(args["invoice_id"], tenant_id=ctx.tenant_id)
    if invoice is None:
        return _not_found("invoice_id")

    to_email = args.get("to_email") or invoice.customer.billing_email
    rendered = render_invoice_email(invoice, to=to_email)

    side_effects = [
        f"send_email to {to_email}",
        f"transition invoice {invoice.id} state draft→sent",
        f"create audit row invoices_sent",
        f"emit invoice.sent event",
    ]

    if args.get("dry_run", False):
        return {
            "status": "ok",
            "dry_run": True,
            "preview": {
                "to": to_email,
                "subject": rendered.subject,
                "body_html_truncated": rendered.html[:1500],
                "attachments": [{"name": a.name, "size_bytes": a.size} for a in rendered.attachments],
                "would_send_at": now_iso(),
            },
            "side_effects_would_occur": side_effects,
        }

    # Real path
    email_id = email_provider.send(rendered)
    invoice.transition_to_sent(via=email_id)
    audit.write(...)
    bus.emit("invoice.sent", ...)
    return {
        "status": "ok",
        "dry_run": False,
        "email_id": email_id,
        "side_effects_occurred": side_effects,
    }
```

## TypeScript Variant

```typescript
export const invoiceSend = registerTool({
  name: "invoice_send",
  schema: invoiceSendSchema,
  async run(args, ctx) {
    const invoice = await invoices.get(args.invoice_id, ctx.tenant_id);
    if (!invoice) return notFound("invoice_id");
    const to = args.to_email ?? invoice.customer.billing_email;
    const rendered = renderInvoiceEmail(invoice, to);

    const preview = {
      to,
      subject: rendered.subject,
      body_html_truncated: rendered.html.slice(0, 1500),
      attachments: rendered.attachments.map(a => ({ name: a.name, size_bytes: a.size })),
      would_send_at: new Date().toISOString(),
    };
    const sideEffects = [
      `send_email to ${to}`,
      `transition invoice ${invoice.id} state draft->sent`,
    ];

    if (args.dry_run) return { status: "ok", dry_run: true, preview, side_effects_would_occur: sideEffects };

    const emailId = await emailProvider.send(rendered);
    await invoice.transitionToSent(emailId);
    return { status: "ok", dry_run: false, email_id: emailId, side_effects_occurred: sideEffects };
  }
});
```

## Quality Bar: 1:1 Parity

The single most important rule: **the dry-run path must exercise the same code as the real path, up to the commit boundary.**

Wrong:
```python
if args.get("dry_run"):
    return {"status": "ok", "preview": "Email would be sent to customer."}  # ← guesses
```

Right:
```python
# Render fully. Validate fully. Only the final provider call is gated.
rendered = render_invoice_email(...)
validate_attachments(...)
check_recipient_consent(...)
if args.get("dry_run"):
    return {"status":"ok", "dry_run":True, "preview": serialize(rendered), ...}
```

If dry-run and real diverge — for example, dry-run skips a validation that real-mode does — the agent learns a faulty model of what works, then real-mode fails. Drift between dry and real is the single most common dry-run failure.

## Pre-Approval Dry-Run

In the approval flow, the system can call `dry_run=true` automatically to populate the plan preview with concrete projected effects:

```
Plan step 4: send_invoice_email
   Will send to: ben@acme.example
   Subject: ACME — May 2026 invoice
   Body preview (1500 chars): "Hi Ben, attached is..."
   Attachments: INV-1234.pdf (84KB)
   Side effects: email send, state transition, audit row, event
```

This makes plan-preview approval (`ai-agent-action-approval-and-hitl` pattern 2) substantially more truthful — the user sees the actual computed result, not a guess.

## When Dry-Run Isn't Feasible

- Tool reads from a billable upstream service (each dry-run still costs). Solution: cache the upstream read; only call once per agent task.
- Tool's "effect" is opaque without committing (e.g., a payments provider that doesn't expose a /preview endpoint). Solution: emulate with a recorded fixture in sandbox-first phase; mark this tool as non-dry-runnable in production.
- Tool's effect depends on real-time state that the dry-run path can't see (e.g., racing inventory). Solution: dry-run returns "could-be" with explicit uncertainty; approval payload notes "may fail at commit".

## Testing Dry-Run vs Real Parity

A property test for every dry-run-capable tool:

```python
@property_test
def dry_real_parity(args, ctx):
    dry = tool.run({**args, "dry_run": True}, ctx)
    real = tool.run({**args, "dry_run": False}, ctx)
    # The "preview" and "actually-occurred" shapes match
    assert canonicalise(dry["preview"]) == canonicalise(real["effects_snapshot"])
```

Run this on every PR that touches a dry-run-capable tool.

## Anti-Patterns

- Stub responses in dry-run that the agent learns to expect.
- Dry-run path that's shorter / faster than real path. Performance lessons don't transfer.
- Dry-run that mutates anything (a "log dry_run was requested" insert is fine; a "stage row" insert is not).
- No `dry_run` echoed in the result — agent can't tell preview from real.
- Dry-run that calls expensive upstream (each preview costs $$ and adds latency).
