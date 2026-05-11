# Refund Execution Pipeline

## Schema

```sql
CREATE TABLE agent_refunds (
  refund_id            CHAR(26) PRIMARY KEY,
  tenant_id            BIGINT NOT NULL,
  task_id              BIGINT NOT NULL,
  feature              VARCHAR(64) NOT NULL,
  abandonment_class    ENUM('technical','user-abort','out-of-scope','budget-exceeded') NOT NULL,
  abandonment_reason   VARCHAR(64) NOT NULL,
  prepaid_units_refunded INT NOT NULL DEFAULT 0,
  fixed_fee_refund_cents BIGINT NOT NULL DEFAULT 0,
  currency             CHAR(3) NOT NULL,
  stripe_refund_id     VARCHAR(64) NULL,
  stripe_balance_tx_id VARCHAR(64) NULL,
  customer_notified_at DATETIME NULL,
  idempotency_key      VARCHAR(96) NOT NULL UNIQUE,
  decided_by           VARCHAR(64) NOT NULL,         -- 'auto' or staff id
  decided_at           DATETIME(3) NOT NULL,
  reason_ref           VARCHAR(64) NULL,             -- ticket id, incident id
  INDEX (tenant_id, decided_at),
  INDEX (task_id)
);
```

Retention 7 years for regulated tenants, 5 years otherwise. Pairs with `billing_events` reversal rows via `task_id`.

## Entry Point

```python
PIPELINE_VERSION = "2026-05.1"

def process_abandonment(task):
    klass = classify_abandonment(task)
    if klass is None:
        return                   # not abandonment (e.g., BUDGET_EXCEEDED with useful output)

    policy = REFUND_POLICY[klass.name]
    if not policy.eligible(task):
        record_no_refund(task, klass)
        return

    idem_key = f"refund:{task.task_id}:{PIPELINE_VERSION}"
    with db.transaction() as txn:
        existing = txn.fetch_one(
            "SELECT refund_id FROM agent_refunds WHERE idempotency_key=%s",
            (idem_key,),
        )
        if existing:
            return existing

        cap_ok = enforce_tenant_refund_cap(task.tenant_id)
        if not cap_ok:
            route_to_finance_preapproval(task, klass, policy)
            return

        amount = compute_refund_amount(task, policy)
        if amount.is_zero():
            record_no_refund(task, klass)
            return

        if klass.name == 'technical' and amount.fixed_fee_cents > 0:
            stripe_refund = issue_stripe_refund(task, amount, idem_key)
        else:
            stripe_refund = issue_credit_balance_entry(task, amount, idem_key)

        persist_refund_row(txn, task, klass, amount, stripe_refund, idem_key)

    emit_event({
        "name": "agent.refund.issued",
        "tenant_id": task.tenant_id,
        "task_id": task.task_id,
        "class": klass.name,
        "amount_cents": amount.total_cents,
        "currency": amount.currency,
    })
    notify_customer(task, klass, amount)
    finance_hooks.on_refund_issued(task, klass, amount)
```

## Refund Amount Calculation

```python
def compute_refund_amount(task, policy):
    prepaid_used = ai_credit_ledger.units_used_for_task(task.task_id)
    fixed_fee = task.fixed_fee_allocated_cents       # 0 for pure-credit pricing
    
    prepaid_refund = prepaid_used if policy.refunds_prepaid else 0
    fixed_refund_cents = fixed_fee if policy.refunds_fixed else 0
    
    if policy.partial_output_useful_check:
        if task.partial_output_useful:
            prepaid_refund = 0
            fixed_refund_cents = 0
    
    return Money(
        prepaid_units=prepaid_refund,
        fixed_fee_cents=fixed_refund_cents,
        currency=task.tenant_invoice_currency,
    )
```

## Stripe Refund (Cash-Back)

For customers who paid cash and we owe them money back (e.g., on annual prepay):

```python
def issue_stripe_refund(task, amount, idem_key):
    if amount.fixed_fee_cents == 0:
        return None
    charge = find_originating_charge(task)        # the invoice/charge from which fees came
    if not charge:
        return issue_credit_balance_entry(task, amount, idem_key)
    return stripe.Refund.create(
        charge=charge.id,
        amount=amount.fixed_fee_cents,
        reason="requested_by_customer",
        metadata={
            "tenant_id": str(task.tenant_id),
            "task_id": str(task.task_id),
            "abandonment_class": task.abandonment_class,
            "pipeline_version": PIPELINE_VERSION,
        },
        idempotency_key=idem_key,
    )
```

## Credit-Balance Entry (Apply to Next Invoice)

For tenants on monthly billing or where applying to next invoice is more appropriate:

```python
def issue_credit_balance_entry(task, amount, idem_key):
    return stripe.Customer.create_balance_transaction(
        task.tenant.stripe_customer_id,
        amount=-amount.total_cents,
        currency=amount.currency.lower(),
        description=f"Refund — task {task.task_id} ({task.abandonment_class})",
        metadata={
            "tenant_id": str(task.tenant_id),
            "task_id": str(task.task_id),
            "abandonment_class": task.abandonment_class,
        },
        idempotency_key=idem_key,
    )
```

## Prepaid Credit Ledger Restoration

```python
def restore_credit_ledger(task, amount):
    if amount.prepaid_units == 0:
        return
    ai_credit_ledger.insert(
        tenant_id=task.tenant_id,
        request_id=f"refund:{task.task_id}",
        feature=task.feature,
        units_charged=-amount.prepaid_units,        # negative = refund
        source='refund',
        period=current_period(),
        idempotency_key=f"credit_refund:{task.task_id}:{PIPELINE_VERSION}",
    )
```

## Per-Tenant Cap Enforcement

```python
def enforce_tenant_refund_cap(tenant_id):
    period = current_period()
    refunded_cents = sum_refunds_cents(tenant_id, period)
    monthly_invoice_cents = expected_monthly_invoice_cents(tenant_id, period)
    if refunded_cents >= 0.25 * monthly_invoice_cents:
        return False
    return True
```

When the cap is reached, the refund routes to a finance pre-approval queue; an investigation issue is opened. A spike in refunds is either a regression (we caused it) or an abuse pattern (tenant gaming).

## Customer Comms Templates

Each class has a dedicated template. Approved by legal once, then reused.

### technical

```
Subject: We've refunded task <task_id> — apologies for the issue

Hi <customer_name>,

Task <task_id> in <feature> didn't complete because of a system issue
on our end (<short reason>).

We've refunded:
- <X> prepaid credits
- <Y> currency in fees

This appears on your next invoice as a credit, or as a refund to your
original payment method (whichever is applicable for your plan).

Reference for support: <ticket_id>
Trace: <signed_link>

We're sorry. The engineering team has been paged.

— Customer Success
```

### user-abort

```
Subject: Task <task_id> was cancelled

Hi <customer_name>,

Task <task_id> in <feature> was cancelled <by you / when the approval
window expired>. Cancelled tasks aren't refunded — see our refund policy.

If you'd like to pick up where you left off, you can restart from the
task viewer: <link>

— Customer Success
```

### out-of-scope

```
Subject: Task <task_id> — we couldn't help, refunded

Hi <customer_name>,

Task <task_id> in <feature> wasn't something this agent could handle
(<short reason>). We refunded what was used.

For this kind of task, <recommended_feature> would be the right tool.

We've also flagged this as an intake-rule improvement so the agent
catches it earlier next time.

— Customer Success
```

### budget-exceeded (no useful output)

```
Subject: Task <task_id> stopped at safety limit — refunded

Hi <customer_name>,

Task <task_id> in <feature> reached its safety limit before producing
a usable result. We refunded what was used.

For deeper investigations, the <Business / Enterprise> tier allows
larger budgets per task. Compare: <pricing_link>.

— Customer Success
```

### budget-exceeded (useful output)

Not a refund. The customer receives the standard partial-bill notification (see attempted-vs-completed billing). The dashboard banner notes that the task reached its budget.

## Finance Hooks

```python
def on_refund_issued(task, klass, amount):
    # 1. Revenue de-recognition if the original billing was recognized
    if klass.name in ('technical', 'out-of-scope'):
        revenue_recognition.derecognize_for_task(task.task_id, amount)

    # 2. Refund-reserve burn
    refund_reserve.record_burn(
        tenant_id=task.tenant_id,
        class_name=klass.name,
        amount_cents=amount.total_cents,
        currency=amount.currency,
        period=current_period(),
    )

    # 3. Alert if monthly refund burn > threshold
    monthly_burn = refund_reserve.monthly_burn(current_period(), klass.name)
    if monthly_burn > THRESHOLDS[klass.name]:
        alerts.trigger('refund_burn_threshold', class_name=klass.name, burn=monthly_burn)
```

Revenue de-recognition is handled by `ai-agent-revenue-recognition`.

## Operator Surface

Finance / support staff need:

- Search refunds by tenant / class / period.
- "Issue a manual refund" (with mandatory class, reason, audit row; goes through the same pipeline with `decided_by=<staff_id>`).
- "Reverse a refund decision" (only for not-yet-stripe-acked refunds; otherwise issue a counter-charge with explicit reason).
- Daily refund volume by class dashboard.

Built in the back-office.

## Reconciliation

Nightly job:

1. Sum `agent_refunds` per tenant per period.
2. Sum Stripe refunds + balance-tx entries per customer per period (via `idempotency_key` lookup metadata).
3. Delta > 0.5% per tenant → finance alert.
4. Differential is investigated within 1 business day.

## Tests

```python
def test_technical_refund_full_idempotent():
    task = make_task(state='FAILED', failure_kind='provider_outage', prepaid_used=100)
    process_abandonment(task)
    process_abandonment(task)
    assert agent_refunds.count_for(task.task_id) == 1
    assert stripe_refund_count_for(task.task_id) <= 1

def test_user_abort_no_refund():
    task = make_task(state='KILLED', killed_by='tenant_user')
    process_abandonment(task)
    assert agent_refunds.count_for(task.task_id) == 0

def test_budget_exceeded_useful_no_refund():
    task = make_task(state='BUDGET_EXCEEDED', partial_output_useful=True)
    process_abandonment(task)
    assert agent_refunds.count_for(task.task_id) == 0

def test_cap_routes_to_preapproval():
    # ramp tenant to 25% of monthly invoice in refunds
    process_abandonment(make_task(...))
    assert pre_approval_queue.contains_for_tenant(...)
```
