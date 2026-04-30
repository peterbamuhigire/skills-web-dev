# Finance and Accounting Workbook Patterns

Use this reference for accounting workbooks, finance dashboards, budgets, forecasts, trial balances, ledger reviews, cost models, and management accounts.

## Workbook Architecture

- Separate sheets into Inputs, Data, Calculations, Checks, Reports, and Dashboard.
- Keep raw ledgers and exports in Excel Tables; never hard-code formulas inside raw import tables.
- Use named assumptions for tax rates, exchange rates, depreciation rates, payment terms, VAT settings, and scenario switches.
- Build outputs from source tables through formulas, Power Query, PivotTables, or Python-generated calculation tables.
- Protect formula sheets and leave user-input cells visibly distinct.
- Add a Checks sheet with visible pass/fail tests before delivery.

## Accounting Workbook Types

| Workbook | Required sheets | Key checks |
|---|---|---|
| Bookkeeping ledger | ChartOfAccounts, Journal, Cashbook, Customers, Suppliers, Reports | total debits = total credits, no missing account codes, no unbalanced entries |
| Trial balance | Accounts, Opening, Movements, TrialBalance, Adjustments | debit total = credit total, all accounts mapped to statement lines |
| AR/AP aging | Invoices/Bills, Payments, Allocations, Aging, Statements | aging total = control account, no negative age, no unapplied receipt hidden |
| Bank reconciliation | Cashbook, BankStatement, Matches, Outstanding, Reconciliation | book balance plus/minus reconciling items = bank statement balance |
| Fixed asset register | Assets, Additions, Disposals, Depreciation, NBV | cost - accumulated depreciation = net book value |
| Budget and forecast | Assumptions, Drivers, P&L, CashFlow, BalanceSheet, Scenarios | statements balance, cash never silently goes negative, drivers reconcile |
| Cost accounting | BOM/Standards, Actuals, Variance, CostCentres, Margin | variance split into price/rate, usage/efficiency, volume, overhead where relevant |

## Formula and Model Rules

- Use `SUMIFS`, `XLOOKUP`, `FILTER`, `UNIQUE`, `SORT`, `LET`, and structured references for repeatable finance calculations.
- Avoid manual subtotal rows inside raw tables; use PivotTables, Power Pivot, or report sheets.
- Use positive/negative signs consistently and document the convention.
- Use separate rows for accruals, prepayments, depreciation, tax, inventory, receivables, payables, and loan repayments; do not bury them in "other".
- For loans, match rate period and payment period (`annual_rate/12` with monthly `nper`).
- For NPV, keep period-zero investment outside Excel `NPV()` and add it separately.
- For IRR, verify the cash-flow series has one sensible sign change; flag multiple-IRR risk where signs alternate.

## Control Checks

- Trial balance debit total equals credit total.
- Balance sheet balances: assets equal liabilities plus equity.
- Opening cash + net cash movement equals closing cash.
- AR aging equals AR control account.
- AP aging equals AP control account.
- Inventory valuation equals inventory control account.
- Fixed asset NBV equals cost less accumulated depreciation.
- Forecast P&L profit flows into retained earnings and cash flow.
- No `#REF!`, `#VALUE!`, `#DIV/0!`, or blank required assumptions.

## Dashboard Patterns

- Show actual vs budget, current month, year-to-date, and rolling 12 months where data permits.
- Highlight gross margin, operating margin, cash balance, receivable days, payable days, inventory days, burn/runway, and DSCR where relevant.
- Use variance columns with F/A labels and conditional formatting. Do not rely only on red/green if users may print in grayscale.
- Use waterfall charts for profit bridge, cash bridge, and price-to-pocket-price analysis.
- Use scenario controls for base, downside, upside, and stress cases.

## Power Query and Python Integration

- Use Power Query for repeatable import, cleanup, appending monthly files, unpivoting exports, and standardising chart-of-accounts mappings.
- Use Python/pandas when reconciliation, matching, statistical forecasting, or large ledger analysis becomes too complex for formulas.
- Export Python results back as clean Tables with checks rather than static screenshots.
