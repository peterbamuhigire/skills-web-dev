> Consolidated from skills/ai-agent-sla-credit-automation/SKILL.md into ai-agent-sla-and-customer-commitments on 2026-05-13. Load this through skills/ai-agent-sla-and-customer-commitments/SKILL.md, not as an active skill entrypoint.

# AI Agent SLA Credit Automation
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building the pipeline that turns an SLA-breach detection into an issued credit on the customer's next invoice — without a human ticket in the loop for the common case.
- Wiring the **breach detector** that watches `agent_resolution_30d`, `agent_irreversible_offscript`, and availability rollups.
- Building the **eligibility check** that applies exclusions (force majeure, customer-caused, beta) before issuing credit.
- Building the **credit calculator** that turns a breach into a numeric credit using the per-tier formula from `ai-agent-sla-and-commitments`.
- Wiring **Stripe credit-note** issuance (or analog) with idempotency keys.
- Wiring the **customer notification** (email + dashboard banner + audit row).
- Coordinating with the **incident-response runbook** for mass-breach events.

## Do Not Use When

- The task is defining what to commit to — `ai-agent-sla-and-commitments`.
- The task is measuring success on production traffic — `ai-agent-task-success-tracking`.
- The task is per-resolution / hybrid pricing — `ai-agent-pricing-engine`.
- The task is one-off finance refunds (non-SLA) — `subscription-billing` + manual operator.
- The task is revenue recognition for credits — `ai-agent-revenue-recognition`.

## Required Inputs

- SLA-clause catalogue with counter names + credit formulas (`ai-agent-sla-and-commitments`).
- Production resolution / intervention / irreversible rollups (`ai-agent-task-success-tracking`).
- Availability rollups from the LLM gateway + agent runtime (`ai-agent-runtime-architecture`, `ai-model-gateway`).
- Stripe Billing account (or analog) with credit-note API access.
- Audit-log spine (`saas-control-plane-engineering`).
- Customer-comms infrastructure (`tabler-email-templates`).

## Workflow

1. Read this `SKILL.md`.
2. Implement the **breach detector** (§1) — periodic scan over the 30d windows + event-driven irreversible detector.
3. Implement the **eligibility check** (§2). See `references/eligibility-rules.md`.
4. Implement the **credit calculator** (§3) — formula → currency amount with FX corridor.
5. Implement the **credit-note issuance pipeline** (§4) idempotently. See `references/credit-issuance-pipeline.md`.
6. Wire **customer notification** (§5) — email + dashboard banner.
7. Wire the **audit log** (§6).
8. Wire **incident-response handoff** (§7) for mass-breach.
9. Apply anti-patterns (§8).

## Quality Standards

- Every breach detected by the system produces a credit decision within 1 hour (resolution-rate breaches) or 5 minutes (irreversible incidents) or 15 minutes (availability breaches).
- The pipeline is **idempotent on `(tenant_id, sla_id, breach_window_start)`** — re-running the detector never double-credits.
- Every credit issued is backed by an **evidence pack**: trace IDs of failed tasks, counter snapshot at breach moment, eligibility-check result, formula application, signed bundle.
- Customers receive notification within 1 business hour of credit issuance.
- Stripe credit-notes use a stable idempotency key derived from `(tenant_id, sla_id, period)`.
- Credits never exceed the per-period cap defined in the SLA class.
- Bespoke (Enterprise) clauses route through a human pre-approval queue (default; configurable per contract).

## Anti-Patterns

- Detector that fires while the breach window is partial (e.g., halfway through a "7 consecutive day" window). Premature credit.
- Credit issued without an evidence pack. Disputes become "trust us".
- No idempotency. Re-run on Monday morning issues second credit-note for last week's breach.
- Manual finance review for *every* credit. Defeats automation; trust erodes between breach and credit.
- Force-majeure exclusion applied silently. Customer sees breach in dashboard but no credit — feels gaslit.
- No per-tenant cap enforcement. A pathological feature outage drains the gross margin.
- Credit-note in wrong currency on multi-currency tenant. Customer disputes; reconciliation breaks.
- Bespoke contract clauses run through generic auto-path without contract reference.

## Outputs

- Breach detector (cron + event-driven).
- Eligibility-check service.
- Credit calculator (Python or TS).
- Stripe credit-note issuance pipeline.
- Customer-notification templates and triggers.
- Audit-log schema for credit decisions.
- Mass-breach handoff hook into incident-response.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Architecture | Credit-issuance pipeline design | Markdown | `docs/sla/credit-issuance-pipeline.md` |
| Compliance | Credit decision audit log | DB | `sla_credit_decisions` |
| Release evidence | Idempotency test report | CI | `tests/sla/credit_idempotency_test.py` |
| Operability | Mass-breach runbook | Markdown | `docs/runbooks/sla-mass-breach.md` |

## References

- `references/credit-issuance-pipeline.md` — Stripe credit-note code, idempotency, audit, multi-currency.
- `references/eligibility-rules.md` — exclusions matrix, applied evaluation order, evidence per exclusion class.
- Companion: `ai-agent-sla-and-commitments`, `ai-agent-task-success-tracking`, `ai-agent-customer-sla-dashboard`, `ai-agent-attempted-vs-completed-billing`, `ai-agent-revenue-recognition`, `subscription-billing`, `stripe-payments`, `saas-admin-backoffice-tooling`, `ai-incident-response-runbook`.

<!-- dual-compat-end -->

## §1 Breach Detector

Two detector classes, different cadence:

### Continuous (event-driven)

For metrics that can breach instantly:

- `agent.irreversible.offscript` (any single off-script irreversible = breach)
- `agent.killswitch.latency` (any kill-switch action > 60s = breach)
- `agent.feature.availability` window-failures past tolerance

```python
def on_irreversible_offscript(event):
    tenant_id = event['tenant_id']
    feature   = event['feature']
    clauses = sla_clauses_for(tenant_id, feature, metric='irreversible_offscript')
    for clause in clauses:
        breach = Breach(
            tenant_id=tenant_id,
            sla_id=clause.id,
            metric='irreversible_offscript',
            value=1,
            window=event['ts_date'],
            breach_window_start=event['ts'],
            evidence_refs=[event['trace_id']],
        )
        enqueue_credit_pipeline(breach)
```

### Periodic (cron, hourly)

For rolling-window metrics:

```python
def hourly_breach_scan():
    for clause in active_sla_clauses_with_window():
        rows = fetch_window_values(clause)        # SLA-counter query
        for row in rows:
            if breach_condition(row, clause):
                breach = build_breach(row, clause)
                if not already_credited(breach):
                    enqueue_credit_pipeline(breach)
```

The `already_credited` check uses the idempotency key (see §4).

### Breach Window Semantics

A "7 consecutive days below floor" clause:
- Detector scans daily values for the last 30 days.
- If 7 consecutive day-buckets are below floor, the breach window starts on the first of those days.
- Re-scan with one more day below the floor *extends* the same window; does **not** open a second breach.
- Window closes when daily value rises above floor.
- Credit is issued **once per window** (idempotency).

## §2 Eligibility Check

Every breach goes through the eligibility check before credit issues.

```python
def check_eligibility(breach) -> Eligibility:
    clause = sla_clauses[breach.sla_id]
    excluded_periods = []

    for exclusion in clause.exclusions:
        rule = EXCLUSION_RULES[exclusion]
        hits = rule.applies_during(breach.window_start, breach.window_end, breach.tenant_id)
        excluded_periods.extend(hits)

    # Subtract excluded periods; re-evaluate
    adjusted_value = recompute_metric_excluding(breach, excluded_periods)
    if not breach_condition_value(adjusted_value, clause):
        return Eligibility(eligible=False, reason='exclusion-cleared',
                           excluded_periods=excluded_periods)

    # Per-tenant cap
    spent_this_period = credit_spent(breach.tenant_id, clause.period_for(breach))
    cap = clause.cap_for(breach.tenant_id)
    if spent_this_period >= cap:
        return Eligibility(eligible=False, reason='cap-reached',
                           cap=cap, spent=spent_this_period)

    return Eligibility(eligible=True, excluded_periods=excluded_periods)
```

Exclusion rules and evidence in `references/eligibility-rules.md`.

## §3 Credit Calculator

```python
def calculate_credit(breach, eligibility) -> Credit:
    clause   = sla_clauses[breach.sla_id]
    tenant   = tenants[breach.tenant_id]
    mrr_local = tenant.current_mrr_local_currency()
    formula   = clause.credit_formula_for(tenant.sla_class, tenant.contract_ref)

    base_amount = formula.apply(breach=breach, mrr=mrr_local)

    # Already-spent and cap
    spent = credit_spent(tenant.id, clause.period_for(breach))
    remaining_cap = max(0, clause.cap_for(tenant.id) - spent)
    final_amount = min(base_amount, remaining_cap)

    return Credit(
        tenant_id=tenant.id,
        sla_id=clause.id,
        currency=tenant.invoice_currency,
        amount=round_to_cents(final_amount, tenant.invoice_currency),
        applied_at_next_invoice=True,
        formula_snapshot=formula.snapshot(),
        eligibility=eligibility,
    )
```

Multi-currency: credits are denominated in the **tenant's invoice currency**. FX corridor applies if base MRR is in a different currency (rare; see `references/credit-issuance-pipeline.md`).

## §4 Issuance Pipeline

```
[Breach detected]
        │
        ▼
[Eligibility check] → ineligible → audit row + dashboard note (no credit issued)
        │ eligible
        ▼
[Credit calculator]
        │
        ▼
[Idempotency check]
   key = sha256(tenant_id + sla_id + period)
        │
        ▼
[Bespoke route?]
   ├── yes → human pre-approval queue
   └── no  → proceed
        │
        ▼
[Stripe credit_note.create with idempotency_key]
        │
        ▼
[Persist sla_credit_decisions row]
        │
        ▼
[Emit sla.credit.issued event]
        │
        ▼
[Trigger customer notification + dashboard banner]
```

Full code in `references/credit-issuance-pipeline.md`.

## §5 Customer Notification

Within 1 business hour:

- Transactional email (template: `tabler-email-templates` `sla-credit-issued.html`) with:
  - Plain-language description of breach
  - Period
  - Credit amount + currency
  - Link to evidence dashboard
  - Link to invoice where credit applies
- In-product dashboard banner on the SLA panel (auto-dismissable, persisted)
- Optional webhook to a tenant-configured URL (Enterprise)

Notification copy is reviewed by legal once and reused; never AI-generated per-message.

## §6 Audit Log

```sql
CREATE TABLE sla_credit_decisions (
  decision_id          CHAR(26) PRIMARY KEY,
  tenant_id            BIGINT NOT NULL,
  sla_id               VARCHAR(128) NOT NULL,
  metric               VARCHAR(64) NOT NULL,
  breach_window_start  DATETIME NOT NULL,
  breach_window_end    DATETIME NOT NULL,
  eligible             BOOLEAN NOT NULL,
  ineligible_reason    VARCHAR(64) NULL,
  excluded_periods     JSON NULL,
  formula_snapshot     JSON NOT NULL,
  evidence_pack_ref    VARCHAR(128) NOT NULL,
  credit_amount_cents  BIGINT NULL,
  credit_currency      CHAR(3) NULL,
  stripe_credit_note_id VARCHAR(64) NULL,
  customer_notified_at DATETIME NULL,
  idempotency_key      VARCHAR(64) NOT NULL UNIQUE,
  decided_by           VARCHAR(64) NOT NULL,  -- 'auto' or staff user id
  decided_at           DATETIME(3) NOT NULL,
  INDEX (tenant_id, breach_window_start)
);
```

Retained ≥ 7 years for regulated tenants, ≥ 5 years otherwise.

## §7 Mass-Breach Handoff

Two indicators of mass breach:
- A single SLA clause breaches for > 10 tenants in the same hour.
- An incident classified as `sla-impact` opens.

The pipeline switches mode:
- Pre-approval queue for *all* credits in the affected feature.
- Comms team is paged (incident channel).
- Aggregate evidence bundle prepared.
- Coordination with `ai-incident-customer-comms` for the public status message.
- After incident closes, batch credit issuance with a consolidated email.

This prevents:
- Independent credit emails for one mass event (looks chaotic).
- Credits issued before the incident is contained (causes confusion).

Runbook in `docs/runbooks/sla-mass-breach.md`.

## §8 Anti-Patterns

- Premature credit on partial windows.
- Credit issued without evidence pack.
- Issuance without idempotency key → double credit on detector re-run.
- Bespoke contracts forced through the auto-path.
- Exclusion applied silently without notifying the customer.
- Per-tenant cap not enforced.
- Wrong currency on credit note.
- Customer notified before Stripe credit-note acknowledged (race).
- Mass-breach issuing per-tenant emails simultaneously (looks like chaos rather than competence).


