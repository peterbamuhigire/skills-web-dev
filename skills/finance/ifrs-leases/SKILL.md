---
name: ifrs-leases
description: Lease accounting under IFRS 16 (full IFRS) and Section 20 (IFRS for SMEs). Lessee single on-balance-sheet model under IFRS 16; lessee operating-vs-finance classification under Section 20. Short-term and low-value exemptions. Lessor classification. Sale-and-leaseback. Use when leases or rental arrangements are in scope. Tier-3 scope — full lessee build deferred until a client materially requires it; Section 20 short-term operating-lease handling and IFRS 16 exemption-test reference are built first.
---

# Leases (IFRS 16 / Section 20)

## Tier-3 scope

This skill is Tier-3 in the build queue. Most Chwezi SME clients have short-term leases (rent, equipment hire) where the IFRS 16 short-term and low-value exemptions or the Section 20 operating-lease model apply. The full IFRS 16 lessee model (right-of-use asset and lease liability with discount-rate computation, reassessment, modification) is built when a real client carries material non-cancellable, non-short-term, non-low-value leases under full IFRS.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/ifrs-for-smes-default.md` (Section 20)
- `doctrine/references/full-ifrs-overlay.md` (IFRS 16)

## Section 20 (IFRS for SMEs)

Lessee classifies leases as finance leases or operating leases at inception. Finance lease: substantially all the risks and rewards of ownership transfer. Operating lease: otherwise. Recognition:

- Operating lease (lessee): rental expense on a straight-line basis over the lease term (unless another systematic basis is more representative).
- Finance lease (lessee): asset and lease liability at the lower of fair value and PV of minimum lease payments; subsequent depreciation of the asset and interest on the liability using the effective-interest method.

Lessor: mirror classification; operating-lease income on a straight-line basis or finance-lease receivable with effective-interest.

## IFRS 16 lessee model

Single on-balance-sheet model for all leases:

- Right-of-use (ROU) asset and lease liability recognised at lease commencement.
- ROU = lease liability + prepayments + initial direct costs + dismantling provision − incentives.
- Lease liability = PV of unpaid lease payments at incremental borrowing rate (or implicit rate if determinable).
- Subsequent: depreciate ROU; unwind interest on liability.

Exemptions:

- Short-term leases (≤ 12 months, no purchase option): may elect straight-line expense.
- Low-value underlying asset (≤ ~USD 5,000 equivalent when new): may elect straight-line expense.

## Initial build (Tier-3 minimum)

- Lease register: lessor, asset, commencement, end, payments schedule, renewal options, purchase options, dismantling obligation.
- Section 20: classification logic; straight-line expense generator.
- IFRS 16: exemption-test calculator; for non-exempt, manual workings until full ROU engine is built.
- Disclosure note generator for both frameworks.

## CoA implications (when full IFRS 16 is implemented)

| Code | Name |
|---|---|
| 1850 Right-of-Use Asset | Non-current, by class. |
| 1859 Accumulated Depreciation — ROU | Non-current contra. |
| 2710 Lease Liability — Current | Current portion. |
| 2720 Lease Liability — Non-current | Non-current portion. |
| 6510 Depreciation of ROU | P&L. |
| 8110 Interest on Lease Liabilities | P&L. |

## Forbidden patterns

- Lessee operating-lease classification under full IFRS without explicit short-term / low-value exemption documentation (blocker).
- Mixing exemption election year-on-year without disclosure (major).
- Section 20 finance-lease accounting on a lease where risk-and-reward transfer is not substantially all (blocker).

## Files

- `SKILL.md`.
- `references/exemption-test.md` (to be built when needed).
- `references/full-ifrs-16-lessee-model.md` (to be built when needed).

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
