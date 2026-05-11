# Price Rule Resolver — Implementation

The resolver is a pure function from `(feature, tenant, dimension, when, intervention, running_count)` to `(unit_price_cents, currency, rule_version, calculation_trace)`.

## Python

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class ResolvedPrice:
    unit_price_cents: int
    currency: str
    rule_version: str
    calculation_trace: Dict[str, Any]

def resolve(
    *,
    feature: str,
    tenant_id: int,
    dimension: str,                          # 'resolved_task' | 'attempted_only' | 'budget_exceeded_partial' | ...
    when: datetime,
    intervention: str = 'none',
    running_period_count: int = 0,
) -> ResolvedPrice:
    tenant = tenants.get(tenant_id)
    if not tenant:
        raise PricingError(f"unknown tenant {tenant_id}")

    rule = price_rules.find_active(
        feature=feature,
        tier=tenant.plan_tier,
        region=tenant.region,
        currency=tenant.invoice_currency,
        dimension=dimension,
        as_of=when,
    )
    if rule is None:
        rule = price_rules.find_active_fallback(feature, dimension, when)
    if rule is None:
        raise PricingError(f"no rule for {feature}/{dimension}/{tenant.plan_tier}")

    rule = apply_tenant_override(rule, tenant_id, when)

    base_cents = rule.base_unit_price_cents
    multiplier = compute_volume_multiplier(rule, running_period_count)
    intervention_factor = rule.intervention_credit.get(intervention, 1.0)

    final_cents = int(round(base_cents * multiplier * intervention_factor))

    return ResolvedPrice(
        unit_price_cents=final_cents,
        currency=rule.currency,
        rule_version=rule.id,
        calculation_trace={
            "base_unit_cents": base_cents,
            "volume_multiplier": multiplier,
            "intervention": intervention,
            "intervention_factor": intervention_factor,
            "running_period_count": running_period_count,
            "tier": tenant.plan_tier,
            "region": tenant.region,
            "currency": rule.currency,
            "rule_id": rule.id,
            "resolved_at": when.isoformat(),
        },
    )
```

## TypeScript

```typescript
export interface ResolvedPrice {
  unitPriceCents: number;
  currency: string;
  ruleVersion: string;
  calculationTrace: Record<string, unknown>;
}

export function resolve(args: {
  feature: string;
  tenantId: number;
  dimension: 'resolved_task' | 'attempted_only' | 'budget_exceeded_partial' | string;
  when: Date;
  intervention?: 'none' | 'light' | 'heavy' | 'user_completed';
  runningPeriodCount?: number;
}): ResolvedPrice {
  const tenant = tenants.get(args.tenantId);
  if (!tenant) throw new PricingError(`unknown tenant ${args.tenantId}`);

  const rule = priceRules.findActive({
    feature: args.feature,
    tier: tenant.planTier,
    region: tenant.region,
    currency: tenant.invoiceCurrency,
    dimension: args.dimension,
    asOf: args.when,
  }) ?? priceRules.findActiveFallback(args.feature, args.dimension, args.when);

  if (!rule) {
    throw new PricingError(`no rule for ${args.feature}/${args.dimension}/${tenant.planTier}`);
  }

  const finalRule = applyTenantOverride(rule, args.tenantId, args.when);

  const base = finalRule.baseUnitPriceCents;
  const multiplier = computeVolumeMultiplier(finalRule, args.runningPeriodCount ?? 0);
  const interventionFactor = finalRule.interventionCredit[args.intervention ?? 'none'] ?? 1.0;

  const finalCents = Math.round(base * multiplier * interventionFactor);

  return {
    unitPriceCents: finalCents,
    currency: finalRule.currency,
    ruleVersion: finalRule.id,
    calculationTrace: {
      baseUnitCents: base,
      volumeMultiplier: multiplier,
      intervention: args.intervention ?? 'none',
      interventionFactor,
      runningPeriodCount: args.runningPeriodCount ?? 0,
      tier: tenant.planTier,
      region: tenant.region,
      currency: finalRule.currency,
      ruleId: finalRule.id,
      resolvedAt: args.when.toISOString(),
    },
  };
}
```

## Volume Multiplier (graduated)

```python
def compute_volume_multiplier(rule, running_count: int) -> float:
    """
    Returns the multiplier for the NEXT task in the running count.
    Graduated: the multiplier corresponds to the tier the next-task falls into.
    """
    # running_count is the count BEFORE this task is added.
    next_index = running_count + 1
    cumulative = 0
    for tier in rule.volume_tiers:
        cap = tier.up_to
        if cap is None:
            return tier.multiplier
        if next_index <= cumulative + cap:
            return tier.multiplier
        cumulative += cap
    return rule.volume_tiers[-1].multiplier
```

Worked example with tiers `[100@1.00, 500@0.90, 2000@0.80, null@0.70]`:

- Tasks 1..100 → 1.00
- Tasks 101..600 → 0.90
- Tasks 601..2600 → 0.80
- Tasks 2601+ → 0.70

## Tenant Override

```python
def apply_tenant_override(rule, tenant_id, when):
    override = tenant_pricing_overrides.find(
        tenant_id=tenant_id,
        feature=rule.feature,
        dimension=rule.dimension,
        as_of=when,
    )
    if not override:
        return rule
    return rule.with_overrides(
        base_unit_price_cents=override.base_unit_price_cents or rule.base_unit_price_cents,
        volume_tiers=override.volume_tiers or rule.volume_tiers,
        intervention_credit=override.intervention_credit or rule.intervention_credit,
        id=f"{rule.id}::override::{override.contract_ref}",
    )
```

Bespoke contracts always write overrides here, never inline in the contract document.

## Rule Storage

```sql
CREATE TABLE pricing_rules (
  rule_id              VARCHAR(128) PRIMARY KEY,
  feature              VARCHAR(64) NOT NULL,
  tier                 VARCHAR(32) NOT NULL,
  region               VARCHAR(16) NOT NULL DEFAULT 'global',
  currency             CHAR(3) NOT NULL,
  dimension            VARCHAR(64) NOT NULL,
  base_unit_price_cents INT NOT NULL,
  volume_tiers         JSON NOT NULL,
  intervention_credit  JSON NOT NULL,
  vendor_pass_through  JSON NULL,
  effective_from       DATETIME NOT NULL,
  effective_to         DATETIME NULL,
  superseded_by        VARCHAR(128) NULL,
  created_by           VARCHAR(64) NOT NULL,
  created_at           DATETIME(3) NOT NULL,
  replay_evidence_ref  VARCHAR(128) NULL,
  INDEX (feature, tier, region, currency, dimension, effective_from, effective_to)
);

CREATE TABLE tenant_pricing_overrides (
  tenant_id            BIGINT NOT NULL,
  feature              VARCHAR(64) NOT NULL,
  dimension            VARCHAR(64) NOT NULL,
  base_unit_price_cents INT NULL,
  volume_tiers         JSON NULL,
  intervention_credit  JSON NULL,
  contract_ref         VARCHAR(64) NOT NULL,
  effective_from       DATETIME NOT NULL,
  effective_to         DATETIME NULL,
  PRIMARY KEY (tenant_id, feature, dimension, effective_from)
);
```

## Resolver-Trace Audit Log

The resolver does not write to DB, but the billing consumer that calls it writes the trace into `pricing_resolutions`:

```sql
CREATE TABLE pricing_resolutions (
  resolution_id        CHAR(26) PRIMARY KEY,
  tenant_id            BIGINT NOT NULL,
  feature              VARCHAR(64) NOT NULL,
  dimension            VARCHAR(64) NOT NULL,
  resolved_at          DATETIME(3) NOT NULL,
  rule_version         VARCHAR(128) NOT NULL,
  unit_price_cents     INT NOT NULL,
  currency             CHAR(3) NOT NULL,
  calculation_trace    JSON NOT NULL,
  task_id              BIGINT NULL,
  billing_event_id     CHAR(26) NULL,
  INDEX (tenant_id, resolved_at),
  INDEX (task_id),
  INDEX (rule_version)
);
```

Auditors and disputes use this. Linked from `billing_events.pricing_rule_version` and the calculation trace.

## Replay Tool

A "what-if" tool to test a proposed rule change:

```python
def replay_pricing(new_rule, period_start, period_end):
    """Replay last period's billing events against a proposed rule.
       Returns per-tenant delta and aggregate gross-margin impact."""
    events = billing_events.in_period(period_start, period_end)
    deltas = []
    for ev in events:
        old_price = ev.unit_price_cents * ev.units
        new_resolved = resolve_with(new_rule, ev.feature, ev.tenant_id, ev.dimension,
                                    ev.occurred_at, ev.intervention_class,
                                    running_period_count=...)
        new_price = new_resolved.unit_price_cents * ev.units
        deltas.append((ev.tenant_id, ev.feature, old_price, new_price))
    return aggregate_replay(deltas)
```

Replay output is the *price-impact analysis* attached to the rule-change PR. Required for any rule change.

## Caching

The resolver is called once per billing event (low QPS). Cache per `(feature, tier, region, currency, dimension, when_date)` is acceptable but not necessary at typical volumes.

For very-high-volume features, cache the rule lookup with a 5-minute TTL and bust on rule-publication events.

## Tests

```python
def test_volume_tier_graduated():
    # Tier table [100@1.00, 500@0.90, ...]
    base = 120
    assert price_for_index(rule, 1).unit_price_cents == 120
    assert price_for_index(rule, 100).unit_price_cents == 120
    assert price_for_index(rule, 101).unit_price_cents == int(round(120 * 0.90))
    assert price_for_index(rule, 600).unit_price_cents == int(round(120 * 0.90))
    assert price_for_index(rule, 601).unit_price_cents == int(round(120 * 0.80))

def test_intervention_credit_applied():
    p = resolve(..., intervention='heavy')
    assert p.unit_price_cents == int(round(120 * 0.30))

def test_tenant_override_wins():
    create_override(tenant_id=42, feature='support_copilot',
                    dimension='resolved_task', base_unit_price_cents=80)
    p = resolve(feature='support_copilot', tenant_id=42, dimension='resolved_task',
                when=now(), intervention='none')
    assert p.unit_price_cents == 80

def test_purity():
    inputs = {'feature':'x','tenant_id':1,'dimension':'resolved_task','when':T,
              'intervention':'none','running_period_count':0}
    assert resolve(**inputs) == resolve(**inputs)

def test_no_rule_raises():
    with pytest.raises(PricingError):
        resolve(feature='nonexistent', ...)
```

## Operational Notes

- Rules ship via PR. Replay analysis attached. Two-person review.
- Effective date set ≥ 14 days out (customer-notification window).
- Customers on annual plans receive 60-day advance notice of base-price changes.
- Bespoke overrides: 2-person review (account owner + finance).
