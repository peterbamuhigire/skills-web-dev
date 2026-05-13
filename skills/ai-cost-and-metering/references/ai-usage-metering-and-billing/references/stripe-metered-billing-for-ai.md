# Stripe Metered Billing for AI — Reference

Recipe to wire `ai.cost.recorded` events to Stripe so the customer's invoice line items match the audit log to the cent.

## Concepts (Stripe Meters)

- **Meter** — a billable dimension defined in Stripe (e.g., `ai_credits_overage`). Has a name, an event_name, a default_aggregation, and an event_payload_key.
- **Meter Event** — a single usage report keyed by an `identifier` for idempotency. Aggregated by Stripe into the meter.
- **Price (metered)** — a price object referencing a meter; charged at invoice close.
- **Customer** — the Stripe customer = the tenant's billing entity (often same as the platform's Stripe Customer mirror, `saas-control-plane-engineering`).

## Setup

```python
# one-time at provisioning
meter = stripe.billing.Meter.create(
    display_name="AI Credits Overage",
    event_name="ai_credits_overage",
    default_aggregation={"formula": "sum"},
    event_payload_key="value",
    customer_mapping={"event_payload_key": "stripe_customer_id", "type": "by_id"},
)

price = stripe.Price.create(
    product=ai_product_id,
    currency="usd",
    unit_amount_decimal="1.5",      # $0.015 per credit (in cents-with-decimals)
    recurring={"interval": "month", "usage_type": "metered", "meter": meter.id},
)
```

Subscriptions attach this metered price. The plan's included allowance is encoded internally; only **overage** is reported to Stripe.

## Reporting from `ai.cost.recorded`

The bus consumer:

```python
def on_ai_cost_recorded(evt):
    tenant_id = evt["tenant_id"]
    request_id = evt["request_id"]
    units = compute_units(evt)             # tokens / divisor

    # 1. drain the credit ledger
    drain = drain_credits(tenant_id, request_id, units)
    if drain.cap_hit:
        publish("ai.budget.threshold", {"tenant_id": tenant_id, "stage": "cap_hit"})
        return

    # 2. if any of `units` came from overage, report to Stripe
    if drain.overage_units > 0:
        stripe.billing.MeterEvent.create(
            event_name="ai_credits_overage",
            identifier=request_id,         # idempotency
            payload={
                "value": str(drain.overage_units),
                "stripe_customer_id": stripe_customer_for(tenant_id),
            },
        )

    # 3. mark ledger row as Stripe-reported
    mark_reported(tenant_id, request_id)
```

Idempotency: the `identifier` field is the Stripe-side idempotency key; a retry with the same id is a no-op. The ledger's `idempotency_key` is the internal one.

## Backfill / replay

To re-report a window (after fixing a bug):

```sql
SELECT tenant_id, request_id, source, units_charged
FROM ai_credit_ledger
WHERE source = 'overage' AND ts BETWEEN :start AND :end
  AND reported_to_stripe IS NOT TRUE;
```

Loop and call `MeterEvent.create` with the same `identifier`. Stripe dedups.

## Reconciliation

Monthly at T+2 days (after Stripe meter aggregation finalises):

```python
def reconcile_month(period):
    for tenant in active_tenants():
        internal = ledger_sum(tenant.id, period, source='overage')
        stripe_total = stripe_meter_sum(meter_id, tenant.stripe_customer_id, period)
        if abs(internal - stripe_total) / max(internal, 1) > 0.005:
            alert("recon_drift", tenant=tenant.id, internal=internal, stripe=stripe_total)
```

Common drift causes:
- Stripe meter event sent before ledger row committed (cross-system race) → fix with transactional outbox.
- Replay produced a different `request_id` for the same logical event → fix idempotency at the source.
- Webhook retries lost in a queue → switch to durable consumer with at-least-once.

## Transactional outbox

Don't call Stripe from the gateway hot path. Instead:

```
ai.cost.recorded → durable queue → outbox table → cron worker → Stripe API
```

The outbox row's primary key is `(tenant_id, request_id, "overage_report")`. The worker reads pending rows in batches, calls Stripe, updates the row to `sent`. Retries on the same row are safe (Stripe `identifier` dedups).

## Customer-facing reconciliation

When a customer disputes a line:

1. Pull the invoice's line item id.
2. Pull all `MeterEvents` aggregated into that line (by customer + period).
3. Pull `ai_credit_ledger` rows with matching `request_id`s where `source='overage'`.
4. Pull `ai_requests` rows for those `request_id`s.
5. Present: per-request timestamp, feature, prompt id, tokens in/out, units charged.

The trail must reconstruct in < 15 minutes.

## Edge cases

- **Cancellation mid-period**: Stripe pro-rates the metered charges to cancel date.
- **Refund**: issue a credit note (not a negative meter event — Stripe meter events are summed and don't accept negatives).
- **Currency**: meter price in subscription currency; ledger stays in USD; FX done at invoice time by Stripe.
- **Tax**: Stripe Tax handles VAT/GST on the metered line if enabled.

## Operational checklist

- [ ] Meter created and price attached to product.
- [ ] All paid plans' subscriptions have the metered price.
- [ ] Free plan has NO metered price (no Stripe usage reported).
- [ ] Outbox worker runs every minute with idempotent retries.
- [ ] Reconciliation job runs at T+2 and pages on > 0.5% drift.
- [ ] Dispute runbook documented; latest-month evidence pull < 15 min.
