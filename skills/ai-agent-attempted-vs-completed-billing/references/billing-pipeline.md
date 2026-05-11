# Billing Pipeline — Implementation

End-to-end pipeline from `agent.resolution.*` event to invoice line item, with idempotency and audit.

## Event Family

| Event | Emitted by | Consumed by |
|---|---|---|
| `agent.task.completed` | runtime | observability, eval, **not billing** |
| `agent.task.failed` | runtime | observability, refund-check |
| `agent.task.budget_exceeded` | runtime | observability, partial-bill candidate |
| `agent.task.killed` | runtime | observability, refund-check |
| `agent.task.abandoned` | runtime | observability, refund-check |
| `agent.resolution.completed` | verdict pipeline | **billing** |
| `agent.resolution.unresolved` | verdict pipeline | **billing** (partial if contract opts in) |
| `agent.resolution.indeterminate` | verdict pipeline | investigation queue (rare) |
| `agent.intervention.recorded` | runtime (on HITL events) | billing-event annotator |

The runtime emits raw state events; only verdict events drive billing.

## Schema

```sql
CREATE TABLE billing_events (
  event_id              CHAR(26) PRIMARY KEY,
  tenant_id             BIGINT NOT NULL,
  task_id               BIGINT NOT NULL,
  feature               VARCHAR(64) NOT NULL,
  line_item_kind        ENUM('resolved_full','resolved_heavy_intervention',
                              'attempted_only','budget_exceeded_partial',
                              'reversal','sla_credit','refund') NOT NULL,
  verdict               ENUM('resolved','unresolved','indeterminate','n/a') NOT NULL,
  units                 DECIMAL(12,4) NOT NULL,        -- can be negative for reversals
  unit_price_cents      INT NOT NULL,
  currency              CHAR(3) NOT NULL,
  amount_cents          BIGINT NOT NULL,                -- units * unit_price; pre-rounded
  pricing_rule_version  VARCHAR(64) NOT NULL,
  intervention_class    ENUM('none','light','heavy','user_completed') NOT NULL DEFAULT 'none',
  reason_ref            VARCHAR(64) NULL,               -- dispute_id, sla_id, refund_id
  verdict_ref           BIGINT NULL,                    -- task_success_verdicts.task_id
  idempotency_key       VARCHAR(96) NOT NULL UNIQUE,
  occurred_at           DATETIME(3) NOT NULL,
  billed_in_period      CHAR(7) NULL,                   -- '2026-05' once invoiced
  created_at            DATETIME(3) NOT NULL,
  INDEX (tenant_id, occurred_at),
  INDEX (tenant_id, billed_in_period),
  INDEX (task_id)
);
```

## Consumer (Python)

```python
PIPELINE_VERSION = "2026-05.1"

def consume_resolution_completed(event):
    contract = success_contracts.get(event.feature, version=event.contract_version)
    price    = pricing_engine.resolve(
        feature=event.feature,
        tenant_id=event.tenant_id,
        when=event.occurred_at,
    )
    intervention = event.intervention_summary   # light|heavy|none|user_completed
    treatment    = contract.billing_treatment_resolved(intervention)
    if treatment == 'none':
        return

    units = treatment.units_for(1)              # 1 resolution
    unit_price = price.cents_per_unit
    amount = int(round(units * unit_price))

    line_item_kind = (
        'resolved_heavy_intervention' if intervention == 'heavy'
        else 'resolved_full'
    )

    write_billing_event(BillingEvent(
        tenant_id=event.tenant_id,
        task_id=event.task_id,
        feature=event.feature,
        line_item_kind=line_item_kind,
        verdict='resolved',
        units=units,
        unit_price_cents=unit_price,
        currency=price.currency,
        amount_cents=amount,
        pricing_rule_version=price.rule_version,
        intervention_class=intervention,
        verdict_ref=event.verdict_id,
        idempotency_key=f"bill:{event.task_id}:{PIPELINE_VERSION}",
        occurred_at=event.occurred_at,
    ))

def consume_resolution_unresolved(event):
    contract = success_contracts.get(event.feature, version=event.contract_version)
    treatment = contract.billing_treatment_attempted_unresolved
    if treatment == 'none':
        return
    price = pricing_engine.resolve(event.feature, event.tenant_id, event.occurred_at)
    units = treatment.units_for(1)
    amount = int(round(units * price.cents_per_unit))
    write_billing_event(BillingEvent(
        tenant_id=event.tenant_id,
        task_id=event.task_id,
        feature=event.feature,
        line_item_kind='attempted_only',
        verdict='unresolved',
        units=units,
        unit_price_cents=price.cents_per_unit,
        currency=price.currency,
        amount_cents=amount,
        pricing_rule_version=price.rule_version,
        idempotency_key=f"bill:{event.task_id}:{PIPELINE_VERSION}",
        occurred_at=event.occurred_at,
    ))
```

## Idempotency

```python
def write_billing_event(be: BillingEvent):
    with db.transaction() as txn:
        existing = txn.fetch_one(
            "SELECT event_id FROM billing_events WHERE idempotency_key=%s",
            (be.idempotency_key,),
        )
        if existing:
            return existing
        txn.execute(
            "INSERT INTO billing_events (...) VALUES (...)",
            (...)
        )
        # Emit to Stripe Meter or queue for invoice item creation
        enqueue_stripe_meter_event(be)
        return txn.fetch_one(
            "SELECT event_id FROM billing_events WHERE idempotency_key=%s",
            (be.idempotency_key,),
        )
```

The idempotency key includes `PIPELINE_VERSION`. Bumping the version is the only way to *recompute* a billing decision (e.g., to fix a bug); this is an explicit migration.

## Stripe Wiring

Use Stripe Meters with `identifier` = `event_id` (Stripe dedups). One meter per `line_item_kind` (or one meter with a `line_item_kind` dimension if your Stripe meter setup supports it):

```python
def enqueue_stripe_meter_event(be: BillingEvent):
    stripe.billing.MeterEvent.create(
        event_name=METER_NAMES[be.line_item_kind],     # e.g., 'agent_resolution_full'
        payload={
            "value": str(be.units),
            "stripe_customer_id": stripe_customer_for(be.tenant_id),
            "feature": be.feature,
            "intervention_class": be.intervention_class,
        },
        identifier=be.event_id,
    )
```

Reconciliation: monthly job sums `billing_events` per tenant per meter and compares with Stripe's meter summary; > 0.5% delta is an alert.

## Reversal Pipeline

```python
def on_verdict_overturned(event):
    original = db.fetch_one("""
        SELECT * FROM billing_events
        WHERE task_id=%s
          AND line_item_kind IN ('resolved_full','resolved_heavy_intervention',
                                  'attempted_only','budget_exceeded_partial')
        ORDER BY created_at ASC LIMIT 1
    """, (event.task_id,))
    if not original:
        return
    write_billing_event(BillingEvent(
        tenant_id=original.tenant_id,
        task_id=original.task_id,
        feature=original.feature,
        line_item_kind='reversal',
        verdict=event.new_verdict,
        units=-original.units,
        unit_price_cents=original.unit_price_cents,
        currency=original.currency,
        amount_cents=-original.amount_cents,
        pricing_rule_version=original.pricing_rule_version,
        reason_ref=event.dispute_id,
        verdict_ref=event.new_verdict_id,
        idempotency_key=f"bill:reversal:{event.task_id}:{event.dispute_id}",
        occurred_at=now(),
    ))
    # Then either reduce the open invoice or issue a credit note for closed periods.
    if original.billed_in_period and original.billed_in_period < current_period():
        stripe_credit_note_for_closed_period(original, event)
```

## Tentative-Verdict Handling

```python
def consume_tentative_verdict(event):
    if not success_contracts[event.feature].bill_on_tentative:
        # Default: do nothing. Wait for final.
        return
    # If opted-in, write a "pending" billing event that is finalised on final verdict.
    write_pending_billing_event(...)
```

Default behavior: tentative verdicts do *not* bill. The customer sees the task on their dashboard as "pending confirmation" rather than billed.

## Reproducibility Test

```python
def test_monthly_invoice_reproducible():
    # Drop the Stripe-side state; replay all events from the source table
    expected = sum_billing_events_for(tenant, period='2026-05')
    actual = stripe_meter_total_for(tenant, period='2026-05')
    assert abs(expected - actual) / max(1, expected) < 0.005   # 0.5% tolerance
```

## Bill-to-Trace Audit Chain

For any line item, an auditor or support engineer must trace:

```
billing_event
   ↓ (verdict_ref)
task_success_verdicts
   ↓ (evidence_ref)
evidence_pack
   ↓ (trace_ids)
agent_tasks + agent_steps + agent_tool_io
```

Auditor must reach the trace in < 5 minutes from a Stripe customer + period.

Built as a single tool in `saas-admin-backoffice-tooling` with the search by `customer / period / task_id / dispute_id`.

## Performance Targets

| Stage | Target |
|---|---|
| Verdict event → billing_event row | < 2s |
| Billing event → Stripe meter | < 5s (async; retried) |
| Monthly reconciliation drift | ≤ 0.5% per tenant |
| Reversal → credit-note | < 1 business day |
