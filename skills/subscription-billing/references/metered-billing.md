# Metered Billing

Use this reference when usage-based pricing must be fair, monitorable, and operationally safe.

## Good Metered Units

- seats in use
- API requests
- compute minutes
- documents processed
- storage consumed

## Bad Metered Units

- opaque “credits” with no visible customer meaning
- units customers cannot audit from the product
- metrics with delayed or disputed measurement rules

## Reporting Patterns

- report usage continuously or in bounded batches
- keep usage records idempotent and replay-safe
- store the billing period, measured unit, source event, and internal account correlation
- provide the customer with a usage dashboard before invoicing surprises them

## Billing-Cycle Reset Rules

- define whether usage resets every billing period or accumulates to a cap
- if changing metered prices mid-cycle, decide whether usage should bill immediately, at next invoice, or not at all
- document how overage, tier thresholds, and seat minimums interact

## Pricing Models

- per-seat: easiest for workforce products, but needs seat audit rules
- per-unit: good for measurable output like messages or reports
- per-API-call: good for developer platforms when customers can inspect usage reliably
