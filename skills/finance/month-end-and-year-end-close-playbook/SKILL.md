---
name: month-end-and-year-end-close-playbook
description: Controlled month-end and year-end close workflow for any Chwezi-grade finance / accounting system. Covers task list, dependencies, evidence requirements, exception handling, reviewer sign-off, period-state transitions, retained-earnings close, lock and reopen governance, and release states. Use whenever a software system, SRS, SDS, test plan, proposal, or business plan touches month-end close, year-end close, period locking, or audit-period release.
---

# Month-End and Year-End Close Playbook

## Overview

Close is a controlled workflow, not a calendar reminder. Each close task has owner, due date, dependency, evidence, review state, exception state, and release decision. Close ends with a documented release state: `pass`, `pass-with-caveats`, or `fail`. Year-end close adds retained-earnings close, lock-period procedure, reopen governance, audit-request tracking, and a final report freeze.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/ledger-invariants.md` (period state)
- `doctrine/references/required-patterns.md`
- `doctrine/examples/reconciliation-evidence-pack.md`
- `bank-and-mobile-money-reconciliation` SKILL
- `audit-ready-reporting-pack` SKILL
- This skill's `references/close-task-template.md`.

## Close task list (standard)

Grouped by area. The exact list is configurable per entity; the categories are not.

### Pre-close

| Task | Owner | Dependency |
|---|---|---|
| Cut-off review for sales and purchases. | Accountant | None |
| Open-items review (AR ageing, AP ageing). | Accountant | None |
| Goods received not invoiced (GRNI) clear. | Accountant + Inventory Manager | Receiving complete |
| Outstanding journals approved. | Controller | Manual-journal queue |

### Subledger close

| Task | Owner |
|---|---|
| AR — invoices, receipts, credit notes posted. | Accountant |
| AP — bills, payments, credit notes posted. | Accountant |
| Inventory — receipts, issues, transfers, adjustments posted; count variance reviewed. | Inventory Manager + Accountant |
| Fixed Assets — additions, disposals, depreciation run. | Accountant |
| Payroll — payroll run committed; statutory deductions schedules complete. | Payroll Officer + Accountant |

### Reconciliations

| Task | Owner |
|---|---|
| Bank — every bank account reconciled with evidence pack. | Accountant |
| Mobile Money — every provider account reconciled. | Accountant |
| POS — every drawer's Z-reports reconciled. | Accountant |
| Card Acquirer — every acquirer batch reconciled. | Accountant |
| Inventory tie-out — control accounts vs subledger. | Accountant |
| AR / AP control tie-out. | Accountant |
| Tax control accounts tie to return data. | Accountant + Tax Reviewer |
| Petty cash count. | Accountant |
| Cash on Hand count. | Accountant |

### Adjustments

| Task | Owner |
|---|---|
| Accruals and prepayments. | Accountant |
| Depreciation. | Accountant |
| FX revaluation. | Accountant |
| Inventory NRV write-downs (Section 13 / IAS 2). | Accountant + Controller |
| Provisions and contingencies review (Section 21 / IAS 37). | Controller |
| Doubtful-debt allowance (Section 11 / IFRS 9 simplified). | Accountant + Controller |
| Tax provision (Section 29 / IAS 12). | Controller + Tax Reviewer |

### Reports

| Task | Owner |
|---|---|
| Trial balance. | Accountant |
| SFP / SOCI / SCE / SCF. | Controller |
| AR / AP ageing. | Accountant |
| Inventory valuation. | Inventory Manager + Accountant |
| Fixed-asset register and depreciation schedule. | Accountant |
| Payroll register vs GL. | Payroll Officer + Accountant |
| Tax pack (VAT, PAYE, WHT, NSSF, income tax progress). | Tax Reviewer + Accountant |
| Bank, POS, mobile-money, card recon evidence packs. | Accountant |
| Management accounts pack with variance commentary. | Controller |
| Donor / grant utilisation pack (where applicable). | Controller |
| Audit-ready export index. | Controller |

### Release

| Task | Owner |
|---|---|
| Reviewer sign-off (Controller). | Controller |
| Period soft-close. | Controller |
| Release state recorded. | Controller |
| Lock period (after waiting window). | Controller |

## Year-end specifics

- Retained-earnings close: close all 4xxx–9xxx accounts into 3300 Current-Year Profit/Loss; sweep 3300 to 3200 Retained Earnings at year-end.
- Lock-period procedure: after sign-off and audit window, lock all months of the financial year.
- Reopen governance: reopen requires Controller + CFO approval, time-boxed, audit-logged.
- Audit-request tracking: every auditor request logged with respondent, evidence, status, due date.
- Final report freeze: financial statements signed by directors; subsequent corrections become prior-period adjustments under Section 10 / IAS 8.

## Period-state transitions

| From | To | Permitted by |
|---|---|---|
| `open` | `soft-closed` | Controller |
| `soft-closed` | `open` | Controller (with reason) |
| `soft-closed` | `locked` | Controller |
| `locked` | `reopened` | Controller + CFO |
| `reopened` | `locked` | Controller |
| `locked` | `archived` | Controller (after audit window) |

## Release states

- `pass` — no blockers; all checks complete; all reconciliations matched; reviewer sign-off recorded.
- `pass-with-caveats` — no blockers; named items carry forward (e.g. tax provision pending tax-reviewer sign-off) with assigned owner and target date.
- `fail` — blocker(s) remain; close not released.

## Acceptance evidence

| Evidence | Description |
|---|---|
| Close-task register | Every task with owner, due, status, evidence path. |
| Reconciliation evidence packs | Per `bank-and-mobile-money-reconciliation`. |
| Adjustment journal listing | All accruals, depreciation, FX revaluation, provisions, write-downs. |
| Subledger tie-out summary | Control account vs subledger reconciliation by account. |
| Reports pack | All reports per "Reports" task list, with print stylesheet applied. |
| Reviewer sign-off | In the audit log: preparer, reviewer, time stamps. |
| Gate manifest | State, blockers, caveats, evidence-pack path. |

## Forbidden patterns

- Closing a period without subledger tie-out.
- Posting to a locked period via a back door.
- Sign-off without reviewer identity in the audit log.
- Close report missing a print stylesheet.
- Reopen without Controller + CFO approval.

## Files

- `SKILL.md`.
- `references/close-task-template.md` — full task template with owners and dependencies.
- `references/year-end-extras.md` — retained-earnings close, lock window, audit requests.
- `examples/first-close-checklist.md` — first close after go-live.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
