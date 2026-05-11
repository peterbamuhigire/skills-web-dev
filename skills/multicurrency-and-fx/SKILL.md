---
name: multicurrency-and-fx
description: Use when implementing IAS 21 multicurrency accounting: functional currency, presentation currency, transaction currency, exchange-rate tables, transaction-date rates, settlement, realised forex gains/losses, month-end revaluation of monetary items, unrealised forex gains/losses, foreign currency invoices, USD/EUR/ZAR/UGX tenants, and currency-safe ledger design.
metadata:
  portable: true
---

# Multicurrency And FX

## Use When

- A tenant books in one functional currency but invoices, pays, or receives in another currency.
- A group needs presentation currency reporting.
- Month-end FX revaluation is required.

## Hard Rules

- MUST define one tenant functional currency.
- MUST store transaction currency and functional-currency equivalent on journal lines or linked valuation records.
- MUST not mix functional and presentation currency as if they are the same ledger amount.
- MUST revalue open monetary items at period end where required.
- MUST distinguish realised from unrealised forex gains/losses.

## Currency Model

Track:

- Functional currency: primary economic environment of the tenant.
- Transaction currency: currency of invoice/payment/document.
- Presentation currency: reporting currency where different from functional currency.
- Rate source, rate date, rate type, and approval status.

## Posting Patterns

Foreign currency invoice:

- Post AR/AP and revenue/expense using transaction-date rate in functional currency.
- Preserve transaction-currency amount for settlement and subledger ageing.

Settlement:

- Clear AR/AP at original functional-currency carrying amount.
- Post cash at settlement-date rate.
- Difference goes to realised forex gain/loss.

Month-end revaluation:

- Revalue open monetary items at closing rate.
- Difference goes to unrealised forex gain/loss and revaluation adjustment.
- Reverse or update according to the tenant close policy in the next period.

## Outputs

- Currency policy.
- FX-rate schema.
- Revaluation job design.
- Realised/unrealised FX posting matrix.
- FX reconciliation report.
