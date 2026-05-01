# Accounting and Finance Analytics in Python

Use this reference when pandas, Polars, numpy, or Python services calculate accounting, bookkeeping, finance, reconciliation, or cost-accounting outputs.

## Data Principles

- Use `Decimal` for currency calculations in services. In pandas, store money as integer minor units or fixed-scale decimals where possible; avoid binary float for final postings.
- Preserve source-document IDs, tenant IDs, account IDs, fiscal periods, currencies, and timestamps through every transformation.
- Never compute finance outputs from UI labels. Use stable account codes, account types, posting dimensions, and document types.
- Treat analytics results as reconciliations or management views, not as replacements for the ledger.

## Core Analytics Patterns

### Trial Balance

- Group journal lines by account and period.
- Compute debit total, credit total, and closing balance using account normal balance.
- Assert total debits equal total credits for every period and tenant.

### AR/AP Aging

- Start from invoices/bills and allocation/payment records.
- Calculate outstanding balance per document, not only per customer/supplier.
- Age from due date for credit control and from invoice date for exposure analysis.
- Reconcile aging totals back to AR/AP control accounts.

### Bank Reconciliation

- Normalize bank statement descriptions, dates, references, and amounts.
- Match exact amount/date/reference first, then use fuzzy matching only for candidates.
- Keep unmatched book items and unmatched bank items as explicit reconciling items.
- Never auto-delete or silently net unmatched differences.

### Cost and Variance Analytics

- Build standard cost tables by item, BOM, operation, labour rate, overhead rate, and effective date.
- Compare actuals to standards by price/rate, usage/efficiency, volume, mix/yield, and overhead where data allows.
- Report favourable/adverse signs consistently: sales above budget is favourable; cost above budget is adverse.
- Use flexible budgets for actual volume before blaming managers for volume-driven cost changes.

### Forecast and Budget Analytics

- Keep forecast, target, plan, and budget as distinct dataset types.
- Use driver tables for customers, volume, price, utilisation, COGS rate, staffing, inventory days, receivable days, payable days, and capex.
- Generate scenarios by changing driver tables, not by hand-editing output statements.
- Use rolling forecasts where the business needs management visibility beyond the fiscal year end.

## Required Reconciliation Checks

- `sum(debits) == sum(credits)` for journal lines.
- Trial balance debits equal credits.
- Balance sheet balances after mapping accounts.
- AR aging equals AR control account.
- AP aging equals AP control account.
- Inventory valuation equals inventory control account.
- Fixed asset NBV equals GL fixed asset cost less accumulated depreciation.
- Opening cash + cash movements equals closing cash.
- Currency revaluation and realized FX gains/losses are traceable to exchange-rate source.

## Output Standards

- Return finance values with explicit currency and scale.
- Include `as_of_date`, `period_start`, `period_end`, and data freshness metadata.
- Provide exception tables, not just summary numbers.
- Write deterministic tests with small ledgers where expected balances are hand-checkable.
- When exporting to Excel, include a Checks sheet and reconcile dashboard totals to source totals.
