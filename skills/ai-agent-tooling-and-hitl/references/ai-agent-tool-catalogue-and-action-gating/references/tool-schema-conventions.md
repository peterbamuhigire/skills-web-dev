# Tool Schema Conventions

This document is the contract every tool author follows. The contract serves two consumers: the LLM (which selects + invokes the tool) and the agent runtime (which executes, audits, retries).

## Naming

- Format: `<noun>_<verb>` or `<domain>_<noun>_<verb>` for namespaced tools.
- Verbs in present tense, lowercase, underscore-separated.
- Business-domain names only. Never expose implementation: `invoice_create_draft`, NOT `mysql_insert_invoice`.
- Avoid generic verbs like `do`, `execute`, `run`, `query`.

Good: `invoice_create_draft`, `invoice_send_for_approval`, `customer_lookup_by_email`, `report_generate_pdf`.
Bad: `create`, `do_invoice`, `query_db`, `http_call`, `run_python`.

## Description for Model (the most important field)

Three sentences, in this order:

1. **What it does** (one sentence, business-domain).
2. **When to use it** (one sentence, with 2-3 example use cases).
3. **When NOT to use it** (one sentence, explicit alternatives).

Example:

```
Creates a draft invoice for the given customer with line items.
Use when the user asks to bill, invoice, charge, or generate a quote. Examples: "send John a bill for last week's hours", "create a quote for 30 hours of work".
Do NOT use to send the invoice — use invoice_send_for_approval after creation.
```

Keep total under 350 characters when possible. Model attention degrades with verbosity.

## Input Schema (JSON Schema, strict)

```json
{
  "type": "object",
  "properties": {
    "customer_id": { "type": "integer", "description": "Customer to bill. Resolved from customer_lookup_*." },
    "line_items": {
      "type": "array",
      "minItems": 1,
      "maxItems": 50,
      "items": {
        "type": "object",
        "properties": {
          "description": { "type": "string", "minLength": 1, "maxLength": 280 },
          "quantity":    { "type": "number", "minimum": 0.01, "maximum": 99999 },
          "unit_price":  { "type": "number", "minimum": 0, "maximum": 1000000 },
          "currency":    { "type": "string", "enum": ["USD","EUR","UGX","GBP"] }
        },
        "required": ["description","quantity","unit_price","currency"],
        "additionalProperties": false
      }
    },
    "due_date":     { "type": "string", "format": "date" },
    "notes":        { "type": "string", "maxLength": 1000 }
  },
  "required": ["customer_id","line_items"],
  "additionalProperties": false
}
```

Rules:
- `additionalProperties: false` always. Catches model hallucinated args at registration.
- Every field has `description`. The LLM reads them.
- Bounded ranges on numeric / array fields. Stops `quantity: 99999999999` exfil-style attacks.
- Enum strings, not free text, wherever possible.
- Dates: `format: date` or `format: date-time` (ISO-8601).

## Output Schema (also typed)

Return structured JSON, not free text. The agent re-parses output to plan the next step.

```json
{
  "type": "object",
  "properties": {
    "status":     { "type": "string", "enum": ["ok","not_found","blocked","budget_exceeded","error"] },
    "data":       { "type": "object" },
    "error": {
      "type": "object",
      "properties": {
        "code":             { "type": "string" },
        "retriable":        { "type": "boolean" },
        "user_message":     { "type": "string" },
        "operator_message": { "type": "string" }
      }
    }
  },
  "required": ["status"]
}
```

## Error Contract

Errors are values, not exceptions.

| `code` | Meaning | Agent behaviour |
|---|---|---|
| `NOT_FOUND` | Requested resource doesn't exist | Replan with a different query |
| `VALIDATION_ERROR` | Args invalid; included details | Replan with corrected args |
| `PERMISSION_DENIED` | Tenant / role not allowed | Stop and escalate to user |
| `BUDGET_EXCEEDED` | Side-effect budget hit | Stop; summarise progress |
| `RATE_LIMITED` | Provider rate limit | Wait + retry with backoff |
| `TRANSIENT` | Provider/network blip | Retry up to 3 with backoff |
| `IRRECOVERABLE` | Don't retry | Surface to support |

Tools throw exceptions only for runtime bugs that should crash the worker.

## Pagination

Cursor, not offset. Reason: agents iterate; offsets reread; tokens explode.

```json
{
  "type": "object",
  "properties": {
    "cursor":   { "type": ["string","null"] },
    "page_size":{ "type": "integer", "minimum": 1, "maximum": 50, "default": 20 }
  }
}
```

Return:
```json
{ "data": [...], "next_cursor": "...", "has_more": true }
```

## Idempotency

Every tool that writes accepts an optional `idempotency_key` arg (the runtime always sets it). The tool stores `(idempotency_key, result)` for 30 days; a duplicate call returns the stored result.

## Observability

The tool author does **not** add tracing. The runtime wraps every tool call with a span that records: `tool.name`, `tool.version`, `tool.args.hash` (never raw args — may contain PII), `tool.result.status`, `tool.latency_ms`, `tool.usd_cost`.

If the tool needs to log internal details, it writes to its own service log, not the agent trace.

## Authorisation

Authorisation lives **inside** the tool body, not in the prompt. The tool receives `tenant_id`, `user_id`, `role`, `plan_tier` via the runtime context; it checks resource ownership and role permissions before any side effect.

```python
def invoice_create_draft(args, ctx):
    if ctx.role not in {"admin","finance","sales"}:
        return {"status":"error","error":{"code":"PERMISSION_DENIED","retriable":False,
            "user_message":"Only admin, finance, or sales roles can create invoices.",
            "operator_message":f"role={ctx.role} on tenant={ctx.tenant_id}"}}
    customer = customers.get(args["customer_id"], tenant_id=ctx.tenant_id)
    if customer is None:
        return {"status":"not_found","error":{"code":"NOT_FOUND","retriable":False,
            "user_message":"That customer was not found.",
            "operator_message":f"customer_id={args['customer_id']} tenant={ctx.tenant_id}"}}
    ...
```

## Returning Concise Observations

Do NOT dump raw provider responses. Trim to what the agent needs.

- `customer_lookup_by_email`: return `{id, name, plan_tier}`, not the full record with 40 fields.
- List tools: return `id`, `name`, summary fields only. Detail is a separate `_get` tool.
- Long text: truncate to ~2000 tokens with `truncated: true` and `total_chars: N`.

This is both a token-cost control and a leakage control. Whatever the tool returns becomes context the model can be tricked into exfiltrating.
