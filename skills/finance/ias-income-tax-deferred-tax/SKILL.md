---
name: ias-income-tax-deferred-tax
description: Income tax accounting under IFRS for SMEs Section 29 (practical default) and IAS 12 (full IFRS overlay). Current tax, deferred tax, temporary differences, recognition of deferred-tax assets, valuation allowance, tax-rate reconciliation, presentation. Use when corporate income tax, deferred tax, tax expense disclosure, or tax-rate reconciliation is in scope.
---

# Income Tax and Deferred Tax (Section 29 / IAS 12)

## Overview

Both Section 29 and IAS 12 use the **temporary-differences approach**: deferred tax arises on differences between the carrying amount of an asset or liability and its tax base. The system computes current tax and deferred tax per book per period, recognises them through P&L (or OCI / equity as required), and discloses the tax-rate reconciliation.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/ifrs-for-smes-default.md` (Section 29)
- `doctrine/references/full-ifrs-overlay.md` (IAS 12)
- `doctrine/references/live-rate-verification-protocol.md` (tax rates)
- `doctrine/references/chart-of-accounts.md`

## Current tax

Current tax is the amount payable (or recoverable) for the period based on taxable profit (loss) using tax rates enacted or substantively enacted by the reporting date. The system computes:

- Accounting profit (per the entity book).
- Adjustments for non-taxable income, non-deductible expense, timing items.
- Taxable profit.
- Current tax expense = taxable profit × current tax rate (read from source register).
- Income tax payable: posted to 2150 Income Tax Payable.

## Deferred tax — temporary differences

Identify temporary differences between carrying amount and tax base, by asset / liability.

| Origin | Direction |
|---|---|
| Accelerated tax depreciation vs accounting depreciation | Deferred tax liability (asset earlier deductible for tax). |
| Receivables allowance not yet tax-deductible | Deferred tax asset (future tax deduction). |
| Inventory NRV write-down not yet tax-deductible | Deferred tax asset. |
| Provisions not yet tax-deductible | Deferred tax asset. |
| Unused tax losses (where probable) | Deferred tax asset. |
| Revaluation of PPE | Deferred tax liability (through OCI / revaluation reserve). |
| Lease right-of-use asset minus lease liability (IFRS 16) | Net temporary difference (possibly DTL or DTA). |

Deferred tax measured at the rate expected to apply when the difference reverses; current statutory rate where reversal pattern is uncertain.

## Recognition of deferred tax assets

DTA recognised only to the extent it is probable that taxable profit will be available against which the deductible temporary difference / tax loss can be utilised.

Under Section 29: same probable threshold; assessment less onerous than IAS 12 in some aspects but the principle is the same.

## Valuation allowance

Where probable threshold is not met for some portion, the unrecognised DTA is disclosed as a tax loss / temporary difference with no carrying amount.

## Presentation

- Current tax assets and liabilities offset where legal right exists and intention to settle net.
- Deferred tax assets and liabilities offset where same authority and same taxable entity (or group with intention to settle net).
- Deferred tax balances are non-current; never current.
- Tax expense broken into current and deferred components in the SOCI.
- Tax effect of items recognised in OCI / equity goes through OCI / equity, not P&L.

## Tax-rate reconciliation (disclosure)

```
Profit before tax × statutory rate                 = (a)
+ effect of non-deductible expenses                = (b)
- effect of non-taxable income                     = (c)
+/- effect of changes in tax rates                 = (d)
+/- effect of unrecognised / re-recognised DTA     = (e)
+/- effect of WHT credits utilised                 = (f)
+/- effect of group / consolidation items          = (g)
+/- other                                          = (h)
= Tax expense per books                            = (i)
```

The reconciliation is a year-end disclosure note item; the build supports the data behind it from the journals.

## CoA implications

| Account | Notes |
|---|---|
| 2150 Income Tax Payable | Current liability. |
| 1610 Tax Receivable — Income Tax | Where overpaid or carried forward. |
| 1900 Deferred Tax Asset | Non-current. |
| 2800 Deferred Tax Liability | Non-current. |
| 9000 Current Income Tax Expense | P&L. |
| 9100 Deferred Tax Expense / Credit | P&L (or OCI where appropriate). |

## Live-rate verification

Income tax rate (corporate, presumptive, small-taxpayer) — verified per `doctrine/references/live-rate-verification-protocol.md`. The system reads the rate from the source register at provision time; the source-register entry carries the verified rate, effective period, source URL, and date accessed.

## Build implications

- A tax-base engine per asset / liability class.
- Temporary-difference computation by class at each reporting date.
- Recognition rule per DTA: probability assessment captured.
- Tax-rate version control via source register.
- Journal generator for current tax and deferred tax provisions.
- Tax-rate reconciliation report.
- Audit-trail of every assumption, with reviewer sign-off.

## Forbidden patterns

- Deferred tax computed on intangible (e.g. on goodwill initial recognition in scenarios where IFRS forbids).
- DTA recognised without probability assessment (blocker).
- Tax rate hardcoded in code or templates (blocker).
- Current tax presented as non-current (blocker).
- Tax-rate reconciliation missing in disclosures for full IFRS entities (major).

## Acceptance evidence

- Tax-base reconciliation by class.
- Temporary-difference register.
- Recognition decisions logged per DTA component.
- Source-register entry for the current tax rate `verified-current`.
- Tax provision journals via posting service.
- Tax-rate reconciliation disclosure.

## Files

- `SKILL.md`.
- `references/temporary-difference-catalog.md`.
- `references/recognition-checklist.md`.
- `examples/sme-tax-provision-2026-04.md`.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
