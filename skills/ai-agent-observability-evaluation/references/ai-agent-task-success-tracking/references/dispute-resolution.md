# Dispute Resolution — Verdict Disputes

A dispute is a customer claim that a verdict (resolved / unresolved) is wrong.

## Two Directions

| Direction | Customer claim | Vendor risk |
|---|---|---|
| Disputed-resolved | "You said resolved; my problem wasn't solved." | Refund / re-do; reputation |
| Disputed-unresolved | "You said unresolved; it was resolved (so why am I getting a credit?)." | Rare; happens if SLA-credit accumulating wrong |

Most disputes are direction 1.

## Schema

```sql
CREATE TABLE task_success_disputes (
  dispute_id           CHAR(26) PRIMARY KEY,
  task_id              BIGINT NOT NULL,
  tenant_id            BIGINT NOT NULL,
  feature              VARCHAR(64) NOT NULL,
  original_verdict_id  BIGINT NOT NULL,
  filed_by             VARCHAR(128) NOT NULL,    -- user email or 'system'
  filed_at             DATETIME(3) NOT NULL,
  claim                ENUM('disputed_resolved','disputed_unresolved') NOT NULL,
  customer_evidence    JSON NULL,                 -- attachments, descriptions
  state                ENUM('open','in_review','resolved_overturn',
                            'resolved_uphold','withdrawn','expired') NOT NULL,
  reviewer_id          BIGINT NULL,
  reviewed_at          DATETIME NULL,
  reviewer_rationale   TEXT NULL,
  new_verdict_id       BIGINT NULL,              -- if overturned
  refund_or_credit_ref VARCHAR(64) NULL,         -- linked to credit-note or refund row
  INDEX (tenant_id, filed_at),
  INDEX (state)
);
```

## Flow

```
[Customer files dispute]
        │
        ▼
[Acknowledge < 1 business hour]   (email)
        │
        ▼
[Build evidence bundle]
   - original verdict + rationale
   - trace + tool I/O
   - judge prompt + response
   - heuristic signals
   - customer-provided evidence
        │
        ▼
[Route to dispute reviewer]
   - 1 tier above original (judge -> senior reviewer; heuristic -> any reviewer)
        │
        ▼
[Reviewer decides]
        │
        ├── Overturn: new verdict written; billing/credit reversed; audit row
        │
        └── Uphold: rebuttal letter sent with rationale; original stands
        │
        ▼
[Customer receives outcome < 5 business days]
        │
        ▼
[Escalation if customer disagrees]
   - Enterprise: ombudsman / external arbitrator per contract
   - Pro/Business: customer-success escalation; final decision in 10 business days
```

## Per-Tenant Cap (Anti-Abuse)

A tenant can dispute up to **min(20 per month, 5% of attempted tasks per month)**. Above that:
- Disputes are accepted but go to a **batch review** queue.
- Customer is informed of the cap (transparent, in advance, in the SLA page).
- Repeated overturning of the same tenant's disputes raises a *contract review* — the success contract for that tenant may genuinely be too strict.

Cap counters reset on the first of the calendar month.

## Reviewer SLA

| Tier | Reviewed by | SLA |
|---|---|---|
| Original was heuristic | Any trained reviewer | 2 business days |
| Original was judge | Senior reviewer | 5 business days |
| Original was human | Reviewer L2 | 5 business days |
| Disputed-unresolved (vendor-credit-at-risk) | Same | same |
| Enterprise tenant | Senior reviewer or feature owner | 3 business days |

Misses on the reviewer SLA do *not* generate a meta-SLA-credit (don't compound liability). They generate an internal alert.

## Overturn Mechanics

Overturning a "resolved → unresolved" verdict:
- The original billing record (if any) is reversed via `ai-agent-attempted-vs-completed-billing` reversal pipeline.
- An accounting entry is logged (revenue de-recognized; refund-reserve adjusted).
- The customer is notified by email with the rationale and the refund/credit amount.

Overturning an "unresolved → resolved" verdict:
- The original SLA-credit (if any) is *not* clawed back automatically. (We don't take credits back without explicit consent; that destroys trust.)
- The verdict is updated for future-period SLA-rate math.
- The audit row notes the correction.

## Rebuttal Letter (Uphold)

Template:

```
Subject: Dispute review — task <task_id>

Hi <customer>,

We reviewed your dispute on task <task_id> (filed <date>). After reviewing the
task trace, the agent's final response, and your follow-up, we are upholding
the original verdict (<verdict>).

Reasoning (reviewer <name>, <date>):
<reviewer_rationale>

Evidence we examined:
- Task trace: <link>
- Agent response: <quote>
- Tools used: <list>
- Heuristic / judge signals: <summary>

If you disagree, you can escalate to <escalation path>. The contract under
which this task was judged is <success_contract.version>.

— Customer Success
```

The link uses a per-tenant signed URL (`saas-admin-backoffice-tooling`) so the customer can re-examine the evidence themselves.

## Audit Trail

Every dispute writes a chain of audit rows:
- `dispute.filed`
- `dispute.in_review`
- `dispute.decided` (overturn or uphold)
- `dispute.refunded` (if overturn led to refund)
- `dispute.escalated` (if applicable)

Audit rows are retained ≥ 7 years for regulated tenants, ≥ 2 years otherwise.

## Reviewer Calibration

Quarterly:
- Run a sample of last-quarter disputes past two independent reviewers without the original verdict.
- Compare to actual outcome.
- Inter-rater agreement < 85% triggers reviewer training and possibly a contract clarification.

## Anti-Patterns

- "Customer always right" auto-overturn. Encourages abuse; corrodes the contract.
- No per-tenant cap. Abuse vector for SaaS revenue.
- Rebuttal letter that does not cite specific evidence. Looks like a stall.
- Overturn that does not flow into billing reversal. The verdict is fixed; the money isn't.
- Disputes routed to the same reviewer who issued the original verdict.
- Dispute outcomes not feeding a contract clarification loop. Same dispute recurs forever.
