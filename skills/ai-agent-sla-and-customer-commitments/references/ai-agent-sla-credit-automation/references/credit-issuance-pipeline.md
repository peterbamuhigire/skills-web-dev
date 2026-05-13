# Credit Issuance Pipeline — Implementation

End-to-end pipeline that turns an eligible breach into a Stripe credit-note (or analog), notifies the customer, and writes the audit row. Idempotent throughout.

## Entry Point

```python
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json
import stripe

PIPELINE_VERSION = "2026-05.1"

@dataclass
class Breach:
    tenant_id: int
    sla_id: str
    metric: str
    breach_window_start: datetime
    breach_window_end: datetime
    counter_snapshot: dict
    evidence_refs: list

def process_breach(breach: Breach):
    decision_key = idempotency_key_for(breach)

    with db.transaction() as txn:
        existing = txn.fetch_one(
            "SELECT decision_id FROM sla_credit_decisions WHERE idempotency_key=%s",
            (decision_key,),
        )
        if existing:
            log.info("skip.duplicate", decision_id=existing["decision_id"])
            return existing

        eligibility = check_eligibility(breach)
        if not eligibility.eligible:
            persist_ineligible(txn, breach, eligibility, decision_key)
            return

        clause   = sla_clauses[breach.sla_id]
        tenant   = tenants.get(breach.tenant_id)
        credit   = calculate_credit(breach, eligibility)

        if clause.is_bespoke or credit.amount_cents > clause.auto_threshold_cents:
            route_to_pre_approval_queue(txn, breach, credit, decision_key)
            return

        evidence_pack_ref = persist_evidence_pack(breach, eligibility, credit)
        cn = issue_stripe_credit_note(tenant, credit, decision_key, evidence_pack_ref)

        persist_decision(txn, breach, eligibility, credit, cn, evidence_pack_ref, decision_key)

    emit_event({
        "name": "sla.credit.issued",
        "tenant_id": breach.tenant_id,
        "sla_id": breach.sla_id,
        "amount_cents": credit.amount_cents,
        "currency": credit.currency,
        "stripe_credit_note_id": cn["id"],
        "evidence_pack_ref": evidence_pack_ref,
    })
    notify_customer(breach.tenant_id, credit, evidence_pack_ref)
```

## Idempotency Key

```python
def idempotency_key_for(breach: Breach) -> str:
    raw = json.dumps({
        "tenant": breach.tenant_id,
        "sla": breach.sla_id,
        "metric": breach.metric,
        "window_start": breach.breach_window_start.isoformat(),
        "pipeline_version": PIPELINE_VERSION,
    }, sort_keys=True).encode()
    return "slacred_" + hashlib.sha256(raw).hexdigest()[:32]
```

Stable across detector re-runs. New `pipeline_version` issues a new key (used when fixing detector bugs that would have credited differently — explicit migration only).

## Stripe Credit-Note Issuance

```python
def issue_stripe_credit_note(tenant, credit, idem_key, evidence_pack_ref):
    customer_id = tenant.stripe_customer_id
    invoice = stripe.Invoice.list(
        customer=customer_id,
        status="open",
        limit=1,
    ).data
    if invoice:
        invoice_id = invoice[0].id
    else:
        # No open invoice - create a credit balance entry instead
        return create_customer_credit_balance(tenant, credit, idem_key, evidence_pack_ref)

    cn = stripe.CreditNote.create(
        invoice=invoice_id,
        amount=credit.amount_cents,
        currency=credit.currency.lower(),
        reason="service_unsatisfactory",       # one of Stripe's enumerated reasons
        memo=human_memo(credit, evidence_pack_ref),
        metadata={
            "sla_id": credit.sla_id,
            "tenant_id": str(tenant.id),
            "evidence_pack_ref": evidence_pack_ref,
            "pipeline_version": PIPELINE_VERSION,
        },
        idempotency_key=idem_key,
    )
    return cn
```

Notes:
- `idempotency_key` parameter is Stripe-native — replay safety end-to-end.
- `memo` is human-readable; appears on the credit-note PDF.
- Stripe's allowed `reason` enum must be verified against the Stripe Credit Notes API reference at integration time.
- For tenants without an open invoice (annual prepaid), use `Customer.create_balance_transaction` with a negative amount instead.

```python
def create_customer_credit_balance(tenant, credit, idem_key, evidence_pack_ref):
    return stripe.Customer.create_balance_transaction(
        tenant.stripe_customer_id,
        amount=-credit.amount_cents,           # negative = credit
        currency=credit.currency.lower(),
        description=human_memo(credit, evidence_pack_ref),
        metadata={
            "sla_id": credit.sla_id,
            "evidence_pack_ref": evidence_pack_ref,
        },
        idempotency_key=idem_key,
    )
```

## Human Memo

```python
def human_memo(credit, evidence_pack_ref):
    return (
        f"Service credit per SLA {credit.sla_id} for "
        f"breach window {credit.breach_window_start.date()}–{credit.breach_window_end.date()}. "
        f"Evidence: {evidence_pack_ref}."
    )
```

Customer sees this on the credit-note. Plain English, references the evidence URL.

## Evidence Pack

```python
def persist_evidence_pack(breach, eligibility, credit):
    pack = {
        "version": PIPELINE_VERSION,
        "tenant_id": breach.tenant_id,
        "sla_id": breach.sla_id,
        "metric": breach.metric,
        "window": {
            "start": breach.breach_window_start.isoformat(),
            "end":   breach.breach_window_end.isoformat(),
        },
        "counter_snapshot": breach.counter_snapshot,
        "evidence_refs": breach.evidence_refs,   # trace ids
        "eligibility": {
            "eligible": eligibility.eligible,
            "excluded_periods": [p.to_dict() for p in eligibility.excluded_periods],
        },
        "credit": {
            "amount_cents": credit.amount_cents,
            "currency": credit.currency,
            "formula_snapshot": credit.formula_snapshot,
        },
        "decided_at": datetime.now(timezone.utc).isoformat(),
    }
    body = json.dumps(pack, sort_keys=True).encode()
    sig  = signer.sign(body)                       # platform signing key
    ref  = evidence_store.put(body, sig)           # object storage
    return ref                                     # e.g., "evidence://2026-05/slacred_abc.json"
```

The signed pack is the auditable proof. Customer dashboards link to a verified-render of it.

## Persistence

```python
def persist_decision(txn, breach, eligibility, credit, cn, evidence_pack_ref, idem_key):
    txn.execute(
        """
        INSERT INTO sla_credit_decisions
          (decision_id, tenant_id, sla_id, metric, breach_window_start,
           breach_window_end, eligible, ineligible_reason, excluded_periods,
           formula_snapshot, evidence_pack_ref, credit_amount_cents,
           credit_currency, stripe_credit_note_id, idempotency_key,
           decided_by, decided_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(3))
        """,
        (
            ulid(), breach.tenant_id, breach.sla_id, breach.metric,
            breach.breach_window_start, breach.breach_window_end,
            True, None, json.dumps(eligibility.excluded_periods_to_dict()),
            json.dumps(credit.formula_snapshot), evidence_pack_ref,
            credit.amount_cents, credit.currency,
            cn["id"] if cn else None, idem_key, "auto",
        ),
    )
```

## Customer Notification

```python
def notify_customer(tenant_id, credit, evidence_pack_ref):
    tenant = tenants.get(tenant_id)
    template = email_templates.get("sla-credit-issued")
    ctx = {
        "tenant_name": tenant.name,
        "credit_amount_display": format_money(credit.amount_cents, credit.currency),
        "sla_id": credit.sla_id,
        "evidence_url": signed_url(evidence_pack_ref, tenant_id, ttl_days=90),
        "dashboard_url": tenant_dashboard_url(tenant_id, "sla"),
    }
    email.send(to=tenant.billing_email, template=template, context=ctx)
    dashboard.add_banner(
        tenant_id=tenant_id,
        kind="sla_credit_issued",
        body=template.dashboard_text(ctx),
        expires_at=days_from_now(30),
    )
    if tenant.sla_webhook_url:
        sla_webhook.send(tenant.sla_webhook_url, credit.to_public_dict())
```

## Multi-Currency Notes

```python
def calculate_credit_amount(formula, breach, tenant):
    # MRR is denominated in the tenant's invoice currency, queried as-of breach start
    mrr = tenant.mrr_as_of(breach.breach_window_start)
    if mrr.currency != tenant.invoice_currency:
        raise PipelineError("currency mismatch on tenant MRR; manual review")
    return Money(
        amount_cents=int(round(formula.coefficient * mrr.amount_cents)),
        currency=tenant.invoice_currency,
    )
```

FX corridor rule: a tenant's `invoice_currency` is locked at the contract for the contract period. SLA credits are computed in that currency. We do not re-FX into other currencies for SLA credits; that would create accidental gain/loss exposure.

## Auto-Threshold and Pre-Approval

```python
clause.auto_threshold_cents = 50_000   # USD 500 default; configurable per tier
```

Below threshold → auto-issue. Above threshold → pre-approval queue (1 finance staff click). Bespoke contracts always go to pre-approval.

```python
def route_to_pre_approval_queue(txn, breach, credit, idem_key):
    approval_id = pre_approval_queue.enqueue({
        "type": "sla_credit",
        "tenant_id": breach.tenant_id,
        "sla_id": breach.sla_id,
        "amount_cents": credit.amount_cents,
        "currency": credit.currency,
        "evidence_pack_preview": build_preview(breach),
        "idempotency_key": idem_key,
    })
    persist_pending_decision(txn, breach, credit, approval_id, idem_key)
```

Finance staff click approve → pipeline resumes from the idempotency check. If staff edits the amount, a new `decision_key` is generated and the old one is voided in audit.

## Tests

```python
def test_idempotent_under_replay():
    breach = make_breach(...)
    d1 = process_breach(breach)
    d2 = process_breach(breach)
    assert d1.decision_id == d2.decision_id
    assert count_stripe_credit_notes(...) == 1

def test_excluded_period_no_credit():
    breach = make_breach(...)
    with patch_provider_status_page_during(breach.window_start, breach.window_end):
        process_breach(breach)
    assert no_credit_for(breach.tenant_id, breach.sla_id, breach.breach_window_start)

def test_per_tenant_cap_enforced():
    # Spend up to the cap, next breach should be capped
    for _ in range(N):
        process_breach(make_breach(...))
    last = process_breach(make_breach(...))
    assert last.credit_amount_cents == 0
    assert last.ineligible_reason == "cap-reached"

def test_bespoke_routes_to_pre_approval():
    breach = make_breach(tenant_sla_class='bespoke', ...)
    process_breach(breach)
    assert no_stripe_credit_note_yet(breach.tenant_id)
    assert pre_approval_queue.contains_for(breach.tenant_id)
```

## Cost and Performance

| Stage | Latency target |
|---|---|
| Detection → eligibility | < 60s |
| Eligibility → calculation | < 5s |
| Calculation → Stripe credit-note | < 3s |
| Stripe → customer notification | < 60s |

End-to-end target: under 5 minutes for irreversible incidents, under 1 hour for rolling-window breaches.

## Operator Surface

Finance staff need:
- Queue of pending approvals (bespoke / over-threshold).
- Search by tenant / period / SLA id.
- "Re-run with override" for genuine mistakes (writes new decision; voids old in audit with reason).
- Export to accounting (link to `ai-agent-revenue-recognition`).

Built in `saas-admin-backoffice-tooling` with the SLA console module.
