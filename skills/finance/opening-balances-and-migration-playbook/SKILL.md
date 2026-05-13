---
name: opening-balances-and-migration-playbook
description: Cutover from legacy Excel / QuickBooks / Tally / Sage / POS / manual systems into Chwezi. Defines the conversion-date model, CoA mapping, opening trial balance, opening subledgers (AR / AP / Inventory / Fixed Assets / Payroll / Tax), bank / mobile-money / cash opening balances, migration suspense, reviewer sign-off, and acceptance evidence. Use whenever a software system, SRS, SDS, test plan, proposal, or business plan involves data migration, cutover, opening balances, or legacy-system replacement.
---

# Opening Balances and Migration Playbook

## Overview

Migration must not preserve bad architecture. The cutover converts legacy data into the new accounting model with explicit mapping, tie-outs, and reviewer sign-off. Trial-balance-only migration is **not** sufficient where open subledgers exist.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/chart-of-accounts.md`
- `doctrine/references/ledger-invariants.md`
- `doctrine/references/required-patterns.md`
- `doctrine/references/forbidden-patterns.md` (migration section)
- This skill's `references/cutover-pack.md`.

## Conversion-date model

A single named conversion date per entity. All balances are at end-of-business on the conversion date. Operational postings before the conversion date live in the legacy system; postings from the day after live in Chwezi. The conversion-date journal is the opening journal.

## Cutover pack (mandatory contents)

| # | Item |
|---|---|
| 1 | Named conversion date and effective time zone. |
| 2 | Legacy trial balance: legacy account, balance, currency, mapped Chwezi account. |
| 3 | Legacy chart-of-accounts to Chwezi CoA mapping (every legacy account either mapped or routed to Migration Suspense with reason). |
| 4 | Opening journal in Chwezi: balanced; per currency; per book. |
| 5 | AR open items: customer, invoice, date, amount, currency, ageing bucket, document reference. Tied to AR control account. |
| 6 | AP open items: supplier, bill, date, amount, currency, ageing bucket, document reference. Tied to AP control account. |
| 7 | Inventory: SKU, location, quantity, unit cost, valuation method (FIFO / weighted average — never LIFO), total value. Tied to Inventory control accounts. |
| 8 | Fixed assets: asset, class, acquisition date, cost, accumulated depreciation, useful life, depreciation method, residual value, location, custodian. Tied to FA cost and accumulated-depreciation accounts. |
| 9 | Bank balances: account, currency, balance, latest reconciled date, reconciliation evidence. |
| 10 | Mobile-money balances: provider, account, balance, reconciliation evidence. |
| 11 | Cash on Hand / petty cash: location, count, custodian, evidence. |
| 12 | Card / mobile-money settlement clearing balances at cutover. |
| 13 | Payroll liabilities: PAYE, NSSF, WHT, salaries payable, by employee schedule. |
| 14 | Tax liabilities: Output VAT, Input VAT, WHT, income tax payable, by tax-code schedule. |
| 15 | Borrowings: lender, principal outstanding, accrued interest, repayment schedule, security. |
| 16 | Provisions: nature, opening balance, basis, expected timing. |
| 17 | Equity: share capital, share premium, retained earnings, other reserves. |
| 18 | Migration suspense account: must reach zero or be formally waived with sign-off. |
| 19 | Source-evidence index: every figure traceable to a legacy source. |
| 20 | Preparer, reviewer, approver names, roles, sign-offs, timestamps. |

## Workflow

1. **Scope and freeze.** Confirm entities, books, currencies, sectors, integrations, and roles. Freeze legacy data at conversion date.
2. **Map.** CoA mapping; product / SKU mapping; customer / supplier mapping; tax code mapping.
3. **Extract.** Pull legacy trial balance and subledger detail.
4. **Stage.** Import into Chwezi staging; do not post yet.
5. **Tie-out.** Each subledger reconciled to its control balance; variances surfaced.
6. **Suspense.** Unmapped or unresolved balances routed to Migration Suspense with ageing and owner.
7. **Post opening journal.** Through the posting service, balanced by currency, dimensions applied, period state = opening (a special state preceding `open`).
8. **Sign off.** Preparer, reviewer, approver — typically Accountant + Controller + CFO / finance lead.
9. **Go-live.** Period state moves to `open` at the day after conversion. The opening journal is immutable.
10. **Post-cutover review.** First-close governance is enhanced for the first three months.

## Opening journal example (illustrative)

```
Date: 2026-04-30 23:59
Period: opening
Book: IFRS for SMEs
Currency: UGX (entity)
Source: cutover-pack-2026-04-30 v1.0
Approval: Jane Doe (Accountant); Peter Bamuhigire (Controller); Ssempa Joseph (CFO)

Dr 1000  Cash on Hand                                          1,200,000
Dr 1100  Bank — Stanbic UGX                                   25,400,000
Dr 1200  Mobile Money — MTN Business                           4,250,000
Dr 1300  Trade Receivables Control                            15,600,000
Dr 1500  Inventory Control — Main Warehouse                   18,900,000
Dr 1700  Fixed Assets — Land                                  60,000,000
Dr 1710  Fixed Assets — Buildings                             40,000,000
Dr 1730  Fixed Assets — Furniture & Fittings                   3,500,000
Dr 1990  Migration Suspense                                            0
                                                              -----------
                                                              168,850,000

Cr 1790  Accumulated Depreciation Control                     12,500,000
Cr 2000  Trade Payables Control                                7,800,000
Cr 2100  Output VAT Control                                    1,250,000
Cr 2110  PAYE Payable                                            450,000
Cr 2120  NSSF Payable                                            260,000
Cr 2300  Salaries Payable                                        140,000
Cr 2600  Borrowings — Bank Loan Current Portion               10,000,000
Cr 2700  Borrowings — Bank Loan Non-current                   45,000,000
Cr 3000  Issued Share Capital                                 20,000,000
Cr 3200  Retained Earnings                                    71,450,000
                                                              -----------
                                                              168,850,000

Suspense: 0  (waiver: not required)
```

## Migration suspense

Migration Suspense (CoA 1990) is a cutover-only clearing. It accepts items that cannot be mapped at cutover. Each suspense item carries:

- Description
- Legacy reference
- Amount
- Ageing target (default: cleared within 30 days of go-live)
- Owner
- Resolution plan
- Status

A non-zero suspense at sign-off requires a formal waiver: scope, value, plan, due date, approver.

## Tie-outs (mandatory)

| Tie-out | Source A | Source B | Acceptance |
|---|---|---|---|
| AR | AR control account balance | AR subledger open-item sum | Equal to the cent. |
| AP | AP control account balance | AP subledger open-item sum | Equal. |
| Inventory by location | Inventory control account | Inventory subledger sum | Equal per location. |
| Fixed Assets | FA cost - Accumulated depreciation control | Asset register sum | Equal. |
| Bank | Bank GL closing | Bank statement closing | Equal as at conversion date. |
| Mobile money | MoMo GL closing | Provider statement closing | Equal. |
| Cash on Hand | Cash GL | Physical count | Equal. |
| Payroll liabilities | Payroll GL controls | Payroll schedule sum by liability | Equal. |
| Tax control accounts | Tax GL | Tax-return schedules | Equal. |

## Sign-off

Preparer (Accountant) + Reviewer (Controller) + Approver (CFO / finance lead) — recorded in the audit log with timestamps and role context. Approval also includes confirmation that:

- LIFO is not the inventory valuation method.
- Tax-control balances are tied to verifiable schedules.
- Suspense is zero or waiver is documented.
- Conversion date is recorded.

## Acceptance evidence

- Cutover pack (per content list above).
- Tie-out reports.
- Opening journal posted and locked.
- Sign-off audit-log entries.
- Gate manifest state: `pass` or `pass-with-caveats` if suspense is waived.

## Forbidden patterns

- Trial-balance-only migration where open subledgers exist (blocker).
- LIFO inventory in opening balances under IFRS / IFRS for SMEs (blocker).
- Hardcoded statutory liability balances copied from legacy without tie-out (blocker).
- Suspense waived without sign-off (blocker).
- Posting opening journal outside the posting service (blocker).

## Files

- `SKILL.md`.
- `references/cutover-pack.md` — full template.
- `references/legacy-source-extractors.md` — extractors for QuickBooks, Tally, Sage, Excel.
- `examples/sme-cutover-pack-2026-04-30.md` — worked example.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
