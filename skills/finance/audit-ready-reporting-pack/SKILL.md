---
name: audit-ready-reporting-pack
description: The audit-ready reporting pack standard for any Chwezi-grade entity. Defines the minimum reports, their content, the drilldown chain, the auditor-export index, the print fidelity, the sign-off, and the release governance. Use whenever a software system, SRS, SDS, test plan, proposal, or business plan involves financial statement preparation, monthly management accounts, donor reports, statutory reports, audit-ready exports, or external audit support.
---

# Audit-Ready Reporting Pack

## Overview

Every entity in scope produces a release-grade reporting pack at month-end and an enhanced pack at year-end. The pack supports management decision-making, statutory filing, and external audit. Every figure is drillable to its source; every page prints correctly; every release carries reviewer sign-off.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/chart-of-accounts.md`
- `doctrine/references/print-fidelity.md`
- `doctrine/references/required-patterns.md`
- `month-end-and-year-end-close-playbook` SKILL
- `finance-ui-pattern-library/references/print-stylesheet-template.md`

## Pack contents — monthly

| # | Report | Purpose |
|---|---|---|
| 1 | Trial balance (summary and detail variants) | TB by account, opening / movement / closing. |
| 2 | GL detail by account | Every line in the period. |
| 3 | Journal listing by period | Every posted journal with status. |
| 4 | Statement of Financial Position | Snapshot at period end, with comparative. |
| 5 | Statement of Comprehensive Income | Period and YTD, with comparative. |
| 6 | Statement of Changes in Equity | Period movements. |
| 7 | Statement of Cash Flows | Direct or indirect; entity-policy. |
| 8 | AR ageing | By customer with ageing buckets. |
| 9 | AP ageing | By supplier with ageing buckets. |
| 10 | Inventory valuation | By item, location, valuation method. |
| 11 | Fixed-asset register and depreciation schedule | Asset detail, accumulated depreciation. |
| 12 | Payroll register-to-GL reconciliation | Gross, deductions, net per employee; GL tie-out. |
| 13 | Bank, POS, cash drawer, mobile-money reconciliation evidence packs | Per `bank-and-mobile-money-reconciliation`. |
| 14 | Tax pack (VAT, PAYE, WHT, NSSF) | Return-ready data with source mapping. |
| 15 | Management accounts | KPI dashboard, variance commentary, contribution-margin and dimension cuts. |
| 16 | Donor / grant utilisation | Where applicable, per restriction. |
| 17 | Auditor export index | Cross-reference table. |

## Pack contents — year-end additions

| # | Addition |
|---|---|
| 18 | Notes to the financial statements (per IFRS for SMEs Section 8 or full IFRS) |
| 19 | Significant accounting policies note |
| 20 | Critical judgements and estimates note |
| 21 | Related-party disclosures |
| 22 | Post-balance-sheet events log |
| 23 | Going-concern assessment |
| 24 | Provisions roll-forward |
| 25 | Income tax reconciliation (effective rate to statutory rate) |
| 26 | Deferred tax computation |
| 27 | PPE roll-forward |
| 28 | Inventory NRV testing |
| 29 | Allowance for doubtful debts methodology |
| 30 | Audit-request log (status during audit) |

## Drilldown chain

Every figure on every report is drillable. The chain is consistent:

```
Report line → CoA account → Journal → Journal line → Source document → Evidence file → Audit-log entry
```

The drilldown affordance is mandatory on web and mobile, and the PDF / printed report contains a section ID enabling cross-reference into the auditor export.

## Auditor export index

The auditor export is a single bundle:

```
audit-export-<entity>-<YYYY-MM>/
├── 00-index.md
├── 01-trial-balance.csv
├── 02-gl-detail.csv
├── 03-journal-listing.csv
├── 04-financial-statements.pdf
├── 05-ar-detail/
├── 06-ap-detail/
├── 07-inventory/
├── 08-fixed-assets/
├── 09-payroll/
├── 10-reconciliations/
│   ├── bank/
│   ├── mobile-money/
│   ├── pos/
│   └── card/
├── 11-tax/
│   ├── vat/
│   ├── paye/
│   ├── wht/
│   ├── nssf/
│   └── income-tax/
├── 12-management-accounts.pdf
├── 13-donor-grants/
├── 14-source-documents/         # PDFs, images, structured files
├── 15-audit-log.csv
└── manifest.yaml
```

`manifest.yaml` records: entity, period, framework, preparer, reviewer, approver, release state, doctrine version, quality-gate manifest, hash of every file.

## Print fidelity

Every report has a print stylesheet per `doctrine/references/print-fidelity.md`. Mandatory printed elements:

- Entity name, TIN, address, period, framework.
- Page X of Y on every page.
- Money triplet (net / tax / gross) preserved where applicable.
- Status chips with text labels (no colour-only signals).
- Sign-off boxes on the last page of every audit-relevant report.
- 60 × 60 mm stamp area on the cover of every audit-relevant report.
- `DRAFT` watermark while status is pre-sign-off.

## Sign-off

| Report group | Preparer | Reviewer | Approver |
|---|---|---|---|
| TB / GL / journal listing | Accountant | Controller | — |
| Financial statements | Accountant | Controller | CFO / Directors (year-end) |
| AR / AP / Inventory / FA / Payroll | Accountant | Controller | — |
| Reconciliation evidence packs | Accountant | Controller | — |
| Tax pack | Accountant | Tax Reviewer + Controller | — |
| Management accounts | Controller | CFO | — |
| Donor / grant pack | Controller | CFO (or grant manager) | — |

Sign-off recorded in the audit log with role, name, timestamp, and report version.

## Release governance

A pack is `released` after Controller sign-off and after all caveats are resolved or formally waived. A year-end pack is `released` after Director sign-off. Once released, the pack is immutable: subsequent corrections become prior-period adjustments per Section 10 / IAS 8.

## Acceptance evidence

- Pack content list complete per the table above.
- Print preview validated for every report.
- Drilldown chain validated by random sample (auditor walks five figures back to source).
- Sign-off audit-log entries present.
- Quality-gate manifest attached.

## Forbidden patterns

- Reports without a print stylesheet (blocker).
- Summary figures without drilldown (blocker).
- Released pack edited in place after release (use prior-period adjustment).
- Auditor export missing the index or the audit-log CSV.
- PDF exports re-rendered as image (loss of text searchability).

## Files

- `SKILL.md`.
- `references/notes-templates.md` — note templates for IFRS for SMEs and full IFRS.
- `references/auditor-export-format.md` — full file-format spec.
- `examples/may-2026-monthly-pack.md` — worked example pack manifest.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
