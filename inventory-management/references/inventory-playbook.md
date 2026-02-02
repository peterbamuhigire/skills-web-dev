# Inventory Playbook Reference

These notes synthesize the small-business bookkeeping overview so Claude can borrow consistent terminology when advising on stock changes.

## Product Categories

- **Service Products**: Mark as non-inventoriable—skip stock queries and ensure they are excluded from warehouse flows.
- **Direct Stock Items**: Maintain perpetual inventory records, update stock at each transaction, and keep audit trails aligned with general ledger entries.
- **Product Sets (Bundles)**: Decrease each component’s stock atomically and report bundle revenue separately; BOM logic must respect base units and conversion factors.
- **Manufactured/Assembled Products**: Manage recipes/BOMs, decrement components on assembly, increment finished goods, and track labor/overhead if relevant.

## Multi-Location Architecture

- Support unlimited warehouses/stores with independent ledgers and layered access controls.
- Provide global stock visibility plus location accuracy; surface low-stock alerts per location.
- Treat transfers as out/in operations that log source, destination, authorization, and allow partial/staged deliveries.

## Core Transactions

- **Purchases**: Include PO receipt, three-way matching, discrepancy handling, and GL entries for assets and shrinkage.
- **Sales**: Reserve stock, decrement on confirmed shipment, track COGS via FIFO/LIFO/weighted/specific methods, and support picking/backorders.
- **Transfers**: Track outbound/inbound adjustments, approvals, and automatic reversals for incomplete transfers.
- **Adjustments**: Require supervisor sign-off for large adjustments, log reasons, and book to loss/gain accounts; generate exception reports for abnormal variances.
- **Consumption/Manufacturing**: Reference BOMs, auto-decrement components, increment finished goods, record wastage, and log production costs.

## Financial Integrity

- Support multiple valuation methods per category but enforce consistency within each (FIFO, LIFO, weighted average, specific identification).
- Favor perpetual inventory with periodic physical counts and variance reports.
- Prevent negative stock unless backorders are explicitly allowed per category.
- Track expiration dates (FEFO) for perishables and enforce min/max thresholds with alerts.
- Report cost variances for management review.

## Audit & Compliance

- Log every inventory movement with user, timestamp, location, quantity, and approvals; prohibit deletion of historical records.
- Automate reconciliation between inventory ledgers and the general ledger; highlight discrepancies.
- Ensure inventory affects balance sheet (current assets) and income statement (COGS).

## Experience & Controls

- Enforce role-based permissions across warehouse/mobile/office roles.
- Support mobile/offline operations with barcode scanning and sync-friendly flows.
- Provide analytics/dashboards for aging, turnover, ABC analysis, and location-level performance.
- Plan implementations with phased rollouts, data migration validation, and user training to minimize disruption.
