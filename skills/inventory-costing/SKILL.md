---
name: inventory-costing
description: Use when implementing or reviewing IFRS-aligned inventory accounting, IAS 2 stock valuation, FIFO, weighted average, specific identification, landed cost, stock receipts, stock-to-COGS posting, stocktake variances, obsolete stock, lower-of-cost-and-NRV write-downs, inventory subledger reconciliation, and manufacturing cost flows. Never use LIFO for IFRS tenants.
metadata:
  portable: true
---

# Inventory Costing

## Use When

- The system buys, manufactures, stores, transfers, counts, sells, or writes down stock.
- A sale must post both revenue and COGS.
- Inventory valuation must reconcile to the GL.

## Hard Rules

- NEVER allow LIFO for IFRS or IFRS for SMEs tenants.
- MUST post COGS at sale/issue time for perpetual inventory, or at period close for approved periodic inventory.
- MUST reconcile inventory GL balance to stock-on-hand value by item, location, and cost layer.
- MUST write down inventory to lower of cost and net realisable value when required; do not silently change item cost.

## Supported Costing Methods

- FIFO for perishable, batch, or layer-tracked stock.
- Weighted average for high-volume interchangeable stock.
- Specific identification for serialized or high-value unique items.

## Posting Flow

Receipt on credit:

- Debit Inventory.
- Credit Accounts Payable.

Cash purchase:

- Debit Inventory.
- Credit Cash/Bank/Mobile Money.

Sale of stocked item:

- Debit Cash/AR.
- Credit Revenue.
- Credit Output VAT where applicable.
- Debit COGS.
- Credit Inventory.

Stocktake loss:

- Debit Inventory Shrinkage or Loss.
- Credit Inventory.

NRV write-down:

- Debit Inventory Write-down Expense.
- Credit Inventory Allowance or Inventory.

## Landed Cost

Capitalise directly attributable costs needed to bring inventory to location and condition for sale or use: freight, import duties not recoverable, handling, insurance in transit, and allocated purchasing costs where policy permits. Recoverable VAT is not inventory cost.

## Outputs

- Costing policy.
- Stock movement to journal posting matrix.
- Inventory reconciliation report.
- Cost-layer schema and tests.
- Stocktake and write-down workflow.
