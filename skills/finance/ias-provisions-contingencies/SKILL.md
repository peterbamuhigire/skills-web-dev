---
name: ias-provisions-contingencies
description: Provisions, contingent liabilities and contingent assets under IAS 37 (full IFRS) and Section 21 (IFRS for SMEs). Recognition criteria (present obligation, probable outflow, reliable estimate), measurement, onerous contracts, restructuring, warranties, contingent disclosures. Use when provisions, litigation, warranties, onerous contracts, restructuring, decommissioning, or guarantee disclosures are in scope.
---

# Provisions and Contingencies (Section 21 / IAS 37)

## Overview

A provision is recognised when:

1. The entity has a present obligation (legal or constructive) as a result of a past event.
2. It is probable an outflow of resources embodying economic benefits will be required to settle the obligation.
3. The amount can be measured reliably.

Otherwise, a contingent liability is disclosed (unless the possibility of outflow is remote).

A contingent asset is disclosed when an inflow of economic benefits is probable but not virtually certain; if virtually certain, the asset is recognised.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/ifrs-for-smes-default.md` (Section 21)
- `doctrine/references/full-ifrs-overlay.md` (IAS 37)

## Measurement

Best estimate of the expenditure required to settle the present obligation at the reporting date. For a large population (e.g. warranties), the expected-value method. For a single obligation, the most-likely-outcome method (potentially adjusted for skewness).

Provisions discounted to present value where the effect is material and a reliable discount rate is available.

## Common provisions

- Warranty obligations.
- Restructuring (announced before reporting date with detailed plan).
- Onerous contracts (unavoidable costs > expected economic benefits).
- Decommissioning, restoration, environmental remediation.
- Legal claims (probable settlement).
- Customer refunds (where return policy is constructive obligation).

## Contingent liabilities — disclosure only

- Possible obligations confirmed only by uncertain future events.
- Present obligations not recognised because outflow not probable or amount not reliably measurable.

Disclosure: nature, estimate of effect, uncertainties, possibility of reimbursement (where applicable).

## Build implications

- Provisions register: nature, opening balance, additions, utilisations, reversals, closing.
- Quarterly review by Controller; reviewer sign-off.
- Recognition checklist applied to each candidate item.
- Disclosure note generator with movements table.
- Contingent register: separate from provisions register.

## CoA implications

| Code | Name |
|---|---|
| 2500 Provisions — Short-term | Current. |
| 2900 Provisions — Long-term | Non-current. |
| 6850 Provision Movement | P&L. |
| 6860 Unwinding of Discount on Provisions | P&L (finance cost). |

## Forbidden patterns

- Provision recognised without a present obligation (blocker — common error: provisioning for future operating losses).
- "Smoothing" provisions (blocker).
- General provisions not tied to specific obligations (major).
- Contingent liabilities recognised as provisions (blocker).
- Contingent assets recognised before virtually certain (blocker).

## Files

- `SKILL.md`.
- `references/recognition-decision-tree.md`.
- `references/onerous-contract-test.md`.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
