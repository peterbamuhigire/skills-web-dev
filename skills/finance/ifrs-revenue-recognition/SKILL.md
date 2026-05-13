---
name: ifrs-revenue-recognition
description: IFRS 15 (full IFRS) and Section 23 (IFRS for SMEs) revenue recognition for Chwezi systems. Covers contract identification, performance obligations, transaction price, allocation, timing of recognition, contract assets and liabilities, refunds, warranties, principal-vs-agent, and disclosures. Use when revenue, sales contracts, subscription billing, multi-element arrangements, deferred revenue, retention, percentage of completion, agency fees, or revenue disclosures are in scope.
---

# IFRS Revenue Recognition (IFRS 15 / Section 23)

## Overview

Revenue recognition policy in Chwezi systems follows IFRS for SMEs Section 23 by default and IFRS 15 for full-IFRS entities. The two standards converge on outcome for most simple sales; they diverge on multi-element, long-duration, and variable-consideration contracts.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/ifrs-for-smes-default.md` (Section 23)
- `doctrine/references/full-ifrs-overlay.md` (IFRS 15)
- `doctrine/references/tax-vat-and-returns.md` (VAT interaction)
- `doctrine/references/chart-of-accounts.md`

## Section 23 (IFRS for SMEs) summary

Revenue from sale of goods is recognised when:

1. The entity has transferred to the buyer the significant risks and rewards of ownership.
2. The entity retains no continuing managerial involvement to the degree usually associated with ownership.
3. The amount of revenue can be measured reliably.
4. It is probable that the economic benefits will flow to the entity.
5. The costs incurred can be measured reliably.

Revenue from rendering of services is recognised by reference to the stage of completion when the outcome can be estimated reliably. Otherwise, recognise revenue only to the extent of recoverable expenses incurred.

Construction-type contracts use the percentage-of-completion method when outcome is reliable.

Interest, royalties, and dividends have specific rules (effective-interest, accrual, right-to-receive).

## IFRS 15 five-step model

1. Identify the contract(s) with a customer.
2. Identify the performance obligations in the contract.
3. Determine the transaction price.
4. Allocate the transaction price to the performance obligations.
5. Recognise revenue when (or as) the entity satisfies a performance obligation.

## When to apply which

The entity's `Framework:` header determines the standard:

- IFRS → IFRS 15.
- IFRS for SMEs → Section 23.

Where outcome is materially the same, the system uses one engine; the framework header drives disclosure differences.

## Build implications

### Contract / performance-obligation model

- Contract entity persists the customer agreement, term, and total price.
- Performance obligations are line-level rows: distinct goods or services promised. Each carries an allocated transaction price and a recognition method (point-in-time or over-time).
- Recognition triggers per performance obligation: delivery, acceptance, time elapsed, milestone, customer use, %-of-completion measure.

### Transaction price

- Fixed and variable components (discounts, rebates, incentives, performance bonuses, penalties).
- Variable consideration estimated at expected value or most-likely-amount; constrained to highly probable amounts.
- Significant financing component recognised separately where the contract spans more than one year and the time-value-of-money is material.
- Non-cash consideration at fair value.
- Consideration payable to a customer (rebates, slotting fees) deducted from revenue unless it is payment for a distinct good or service.

### Allocation

- Stand-alone selling prices used to allocate the transaction price across performance obligations.
- Where stand-alone is not observable, adjusted-market, expected-cost-plus-margin, or residual approach.

### Timing

- **Point-in-time:** when control transfers (delivery, acceptance, transfer of risks and rewards under Section 23).
- **Over-time:** when one of the IFRS 15 over-time criteria is met; output method or input method to measure progress.
- **Construction-type:** Section 23 mandates % of completion when outcome reliable.

### Contract assets and liabilities

- **Contract asset** when entity has performed but not yet billed (unbilled receivable).
- **Contract liability** (deferred revenue / customer advance) when entity has been paid but not yet performed.
- Trade receivable only when an unconditional right to consideration exists.

### Refunds, warranties, returns

- Refund liability and right to recover product asset for expected returns.
- Assurance-type warranties: provision under IAS 37 / Section 21.
- Service-type warranties: separate performance obligation.

### Principal vs agent

- The entity is a **principal** if it controls the good or service before transfer; otherwise an **agent** earning a commission.
- Indicators: primary responsibility for fulfilment, inventory risk, pricing discretion, credit risk.
- Principal recognises gross revenue; agent recognises net commission.

### Disclosures

- Disaggregation of revenue (by category, geography, market, type, contract duration).
- Contract balances roll-forward.
- Performance obligation descriptions and timing.
- Significant judgements.
- Costs to obtain or fulfil a contract (capitalised vs expensed).

## CoA implications

| Concept | Account |
|---|---|
| Revenue | 4000 / 4100 / sub-accounts by line. |
| Sales returns | 4200 (contra). |
| Trade discounts | 4300 (contra). |
| Contract asset | 1320 Other Receivables (or a dedicated 1330-range account). |
| Contract liability / deferred revenue | 2200 Customer Advances / Deferred Revenue. |
| Refund liability | new account under 2200-range. |
| Right-to-recover product | new asset under 1500-range inventory. |
| Costs to obtain a contract (capitalised) | new intangible asset account (Section 23 generally expenses; IFRS 15 may capitalise). |

## VAT interaction

VAT applies at the point of supply per the country's VAT Act; this may not coincide with IFRS 15 / Section 23 recognition. The posting service records the tax effect at the VAT point of supply (output VAT on supply) and the revenue effect per IFRS / Section 23; the two effects sit on different journal lines. The VAT return uses the supply date; the revenue report uses the recognition date.

## Forbidden patterns

- Recognising revenue when the conditions in step 5 / Section 23.14 are not met (blocker).
- Recognising gross when the entity is acting as agent (blocker).
- Cash-basis revenue presented as IFRS-compliant (blocker).
- Mixing percentage-of-completion and completed-contract within the same project type (blocker without policy change).
- Deferred revenue collapsed into trade payables (blocker).

## Acceptance evidence

- Contract registry with performance obligations and recognition triggers.
- Allocation worksheet for multi-element contracts.
- Variable-consideration estimation log with reviewer.
- Contract-balances roll-forward.
- Recognition journals tested for trigger-driven posting.
- Disclosure pack generated.

## Files

- `SKILL.md`.
- `references/section-23-summary.md`.
- `references/ifrs-15-five-step.md`.
- `examples/multi-element-software-licence-plus-support.md`.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
