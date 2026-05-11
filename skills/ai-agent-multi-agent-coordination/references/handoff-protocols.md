# Agent-to-Agent Handoff Protocols

A handoff transfers control of a conversation or task from one agent to another with a structured message. The receiving agent treats structured fields as ground truth and the free-text summary as advisory only.

## Why Structured

Free-text handoffs are tempting ("@billing_agent, the customer wants a refund of $80 for invoice INV-1234"). They fail in three ways:

1. **Loss of fidelity**: the receiving agent has to re-parse, often introducing errors.
2. **Non-replayability**: traces are opaque.
3. **Prompt-injection vector**: malicious user input flows from sender's context into receiver's prompt.

Structured handoffs treat the receiver as a function call with typed args.

## Handoff Message Schema

```json
{
  "$schema": "https://platform.example/schemas/agent-handoff.json",
  "handoff_id": "h_<ulid>",
  "task_id": "tsk_<ulid>",
  "tenant_id": 42,
  "conversation_id": "c_<ulid>",
  "from_agent": "sales_agent",
  "to_agent": "billing_agent",
  "initiated_at": "2026-05-11T10:00:00Z",
  "deadline_iso": "2026-05-11T10:15:00Z",
  "reason_code": "billing_request",
  "reason_text": "Customer requested refund of overcharge.",
  "structured_state": {
    "customer_id": 88,
    "invoice_id": 1234,
    "issue": "overcharge",
    "amount_disputed_usd": 80.00,
    "evidence_doc_ids": ["doc_456"]
  },
  "expected_outcome_schema": {
    "type": "object",
    "properties": {
      "resolution": { "type": "string", "enum": ["refund_issued","refund_denied","escalated"] },
      "amount_usd": { "type": "number" },
      "communication_id": { "type": "string" }
    }
  },
  "trust_level": "structured_only",
  "user_facing_context_summary": "We discussed refund eligibility; needs billing review.",
  "audit_trail_pointer": "task:tsk_xxx/steps?range=1-12"
}
```

## Trust Levels

| Level | Meaning |
|---|---|
| `structured_only` | Receiver acts only on `structured_state`. `user_facing_context_summary` is for UX continuity, not decision-making. |
| `structured_plus_summary` | Receiver may use the summary as soft context but must validate any actionable claim via its own tools. |
| `full_trust` | Reserved for internal supervisor → worker handoffs where both agents share the same trust boundary. |

External-facing agents (chatbots) only use `structured_only` for handoffs.

## Receiving the Handoff

```python
class BillingAgent:
    def receive_handoff(self, h: Handoff) -> SubtaskResult:
        validate_schema(h, BILLING_HANDOFF_SCHEMA)
        # Re-fetch ground truth; never trust the sender's facts
        invoice = invoices.get(h.structured_state.invoice_id, tenant_id=h.tenant_id)
        if invoice is None:
            return SubtaskResult(status="failed", error="invoice_not_found")
        # Build my own prompt, with the structured state as facts, not the sender's text
        my_prompt = self.system + format_facts({
            "invoice": invoice.snapshot(),
            "customer": customers.get(invoice.customer_id),
            "issue": h.structured_state.issue,
            "amount_disputed_usd": h.structured_state.amount_disputed_usd,
        })
        # Append the handoff context for traceability, marked as untrusted
        my_prompt += f"\n[handoff context from sales_agent, advisory only]: {redact(h.user_facing_context_summary)}"
        return self.run(my_prompt, budget=...)
```

## Bidirectional Handoffs

The receiver may need to hand back. The protocol supports a `handoff_chain`:

```
sales_agent → billing_agent → support_agent → sales_agent (back to user)
```

Each hop appends to `handoff_chain[]`. A circular hop (returning to an agent already in the chain) requires explicit `cycle_allowed: true` from the supervisor — otherwise the handoff is rejected as a likely loop.

## Conversation-Style (User-Facing) Handoff

When the user is aware of the handoff (chat interface):

```
User: "Can I get a refund on this?"
sales_agent: "I'm going to bring in our billing team. One moment."

[system] handoff from sales_agent → billing_agent
billing_agent: "Hi, I'm billing. I've reviewed the invoice and..."
```

The transition is **explicit and visible** to the user. The handoff is logged. The user can opt out ("no, please stay with the same agent").

## Internal Handoff (Supervisor → Worker)

In a supervisor/worker topology, handoffs are not user-visible. The supervisor dispatches; workers report back. See `supervisor-worker.md`.

## Failure Modes

| Failure | Handling |
|---|---|
| Receiver agent not registered | Sender retains the task; surface error |
| Receiver returns `blocked: needs_approval` | Sender prompts the user; on approval, re-handoff |
| Receiver exceeds deadline | Sender escalates or aborts |
| Receiver returns malformed result | Sender validates; if invalid, re-handoff with constraints; if persistent, abort |
| Handoff chain exceeds max length (default 5) | Abort; page on-call |
| Cross-tenant handoff requested | Reject; security violation logged |

## Audit and Observability

Every handoff writes a row to `agent_handoffs`:

```sql
CREATE TABLE agent_handoffs (
  id              VARCHAR(64) PRIMARY KEY,    -- handoff_id
  task_id         BIGINT NOT NULL,
  tenant_id       BIGINT NOT NULL,
  from_agent      VARCHAR(64) NOT NULL,
  to_agent        VARCHAR(64) NOT NULL,
  reason_code     VARCHAR(64) NOT NULL,
  structured_state JSON NOT NULL,
  trust_level     VARCHAR(32) NOT NULL,
  initiated_at    DATETIME NOT NULL,
  completed_at    DATETIME,
  outcome         JSON,
  INDEX (task_id, initiated_at)
);
```

Traces show handoffs as a special span kind (`handoff`) linking the two agent spans.

## Anti-Patterns

- Free-text "tell billing about this" handoff.
- Receiver acts on the sender's textual claims without re-validation.
- No deadline → receiver hangs forever.
- Handoff chain unbounded → loops.
- Cross-tenant handoff allowed for "marketplace" features without explicit consent and federation contract.
- Handoff state lives in process memory, not the database. Crash loses the trail.
