# SaaS Metrics Event Contract — Reference

The typed event stream that finance, sales, and CS all read. If this contract is missing or sloppy, every MRR / ARR / NRR number is reconstructed by hand from Stripe each month.

## Core Principle

Every change to a tenant's subscription state emits a typed event with:
- `idempotency_key` (so replays don't double-count)
- `event_type` (one of a small enum)
- `tenant_id`, `customer_id`
- `mrr_delta_usd` (signed; positive for new / expansion, negative for churn / contraction)
- `currency` (always USD-normalised; original currency captured separately)
- `effective_date` (when the change takes effect, not when the event is emitted)
- `reason_code` (free / paid_conversion / upgrade / downgrade / cancel / payment_failure / etc.)
- `is_new_customer` (true on first paying subscription for this customer)
- `prev_mrr_usd`, `new_mrr_usd` (so finance can audit the delta)

## Event Schema

```json
{
  "event_id": "evt_2026_05_11_abc",
  "idempotency_key": "sub_xyz_2026_05_11_upgrade",
  "event_type": "subscription.created | subscription.upgraded | subscription.downgraded | subscription.cancelled | subscription.reactivated | subscription.payment_failed | subscription.payment_recovered | subscription.expanded | subscription.contracted",
  "occurred_at": "2026-05-11T10:23:00Z",
  "effective_date": "2026-05-11T10:23:00Z",
  "tenant_id": "ten_456",
  "customer_id": "cus_stripe_abc",
  "subscription_id": "sub_stripe_xyz",
  "is_new_customer": false,
  "prev_mrr_usd": 50.00,
  "new_mrr_usd": 100.00,
  "mrr_delta_usd": 50.00,
  "currency_original": "EUR",
  "amount_original": 47.50,
  "fx_rate": 1.0526,
  "plan": "pro",
  "previous_plan": "starter",
  "reason_code": "user_initiated_upgrade",
  "actor_user_id": "usr_789"
}
```

## Where Events Are Emitted

| Source | Emits |
|---|---|
| Stripe webhook handler | All subscription/payment events from Stripe |
| In-app upgrade controller | `subscription.upgraded` (after Stripe confirms) |
| Cancellation flow | `subscription.cancelled` |
| Back-office refund | `subscription.contracted` (with reason `admin_credit`) |
| Annual renewal | `subscription.renewed` |
| Trial conversion | `subscription.created` with `is_new_customer=true` |
| Dunning recovery | `subscription.payment_recovered` |

## Where Events Are Consumed

| Consumer | Use |
|---|---|
| Warehouse | Materialise MRR / ARR / Net New MRR / Churn / NRR daily |
| CRM (HubSpot/Salesforce) | Update account MRR, status, expansion |
| Slack #revenue channel | Real-time deal closures |
| Finance close | Monthly reconciliation source |
| Lifecycle email | Trigger upgrade / retention sequences |
| AE / CSM dashboards | Pipeline + portfolio MRR |

## Warehouse Views

Daily snapshot from the event stream:
```sql
CREATE OR REPLACE VIEW v_mrr_daily AS
SELECT
  day,
  SUM(CASE WHEN event_type IN ('subscription.created') AND is_new_customer THEN mrr_delta_usd ELSE 0 END) AS new_mrr,
  SUM(CASE WHEN event_type = 'subscription.expanded' THEN mrr_delta_usd ELSE 0 END) AS expansion_mrr,
  SUM(CASE WHEN event_type = 'subscription.contracted' THEN -mrr_delta_usd ELSE 0 END) AS contraction_mrr,
  SUM(CASE WHEN event_type = 'subscription.cancelled' THEN -mrr_delta_usd ELSE 0 END) AS churned_mrr,
  SUM(mrr_delta_usd) AS net_new_mrr
FROM events.subscription_events
GROUP BY day;
```

`v_arr_running`, `v_nrr_by_cohort`, `v_gross_margin_by_tenant` follow similar patterns.

## Anti-Patterns

- Events emitted **before** Stripe confirms — local state ahead of source-of-truth.
- No idempotency key — replay double-counts.
- No `is_new_customer` flag — finance can't separate New from Expansion.
- `mrr_delta_usd` computed inconsistently (some events use original currency, some USD).
- Currency conversion done at consume time inconsistently — different consumers report different MRR.
- No `effective_date` separate from `occurred_at` — proration math impossible.

## Companion Files

- `cohort-analysis-engineering.md` — using these events for cohort retention.
- `cost-per-tenant-attribution.md` — joined with the events to compute gross margin.
