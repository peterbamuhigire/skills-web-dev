---
name: inventory-management
description: Coordinate infrastructure for inventory, stock movement, BOMs, valuation, and multi-location controls while referencing the existing ERP implementation, inventory docs, and the small-business bookkeeping playbook.
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, code generation, debugging, quality checks, and any task where it offers enhanced capabilities. If superpowers provides a better way to accomplish something, prefer it over the default approach.

# Inventory Management Skill

## Overview
Pair the existing Maduuka stock-tracking implementation (stock-ledgers, UnitConversionService, stock movements, purchase/sales flows, asset-level constraints) with general bookkeeping principles such as multi-location control, valuation methods, auditing, and SKU types. Use this skill whenever a change touches stock items, transfers, inventory valuation, assembly/BOM flows, stock adjustments, or reporting so Claude can recommend consistent behavior.

**Database Standards:** All inventory database changes (tables, stored procedures, triggers) MUST follow **mysql-best-practices** skill migration checklist to ensure schema-code synchronization.

**Cross-Platform:** Inventory code deploys to Windows dev (MySQL 8.4.7), Ubuntu staging, and Debian production (both MySQL 8.x). Use `utf8mb4_unicode_ci` collation. Production schema changes go in `database/migrations-production/` (non-destructive, idempotent).

## Quick Reference
- **Product categories**: Recognize services (no stock), direct stock items, bundles, and manufactured assemblies before touching inventory code.
- **Stock flows**: Follow the purchase → receiving → movement → sale path and keep logs for adjustments/transfers.
- **Valuation**: Document FIFO/LIFO/weighted average/specific-cost usage per product class and reconcile perpetual vs periodic records.
- **Controls**: Enforce franchise_id filtering, warehouse visibility rules, negative stock prevention, alerts, and approvals before processing inventory adjustments.

## Core Instructions
1. **Match existing implementation**: Reference `src/Inventory/Services/UnitConversionService.php`, `api/advanced-inventory/conversions.php`, `advanced-inventory-bom.php`, and `api/restaurant/kots.php` to understand how conversions, BOM previews, and stock deductions currently work.
2. **Translate bookkeeping guidance**: When a feature touches bundles, manufacturing, purchase orders, transfers, or adjustments, mention how the new behavior supports record keeping (three-way matching, COGS updates, journals for adjustments, variance reports). Use the attached `references/inventory-playbook.md` for editorial guidance.
3. **Multi-location architecture**: Document warehouse/store hierarchy, location-level ledgers, and transfer procedures (outbound reduction, inbound increase, approval trails, automatic reversals) before recommending UI or API changes.
4. **Valuation and audit**: Capture valuation method selection and reconciliation steps in code comments or docs; highlight FEFO/expiration tracking for perishables and variance thresholds for adjustments.
5. **Inventory enforcement**: Negative stock prevention, supervisor approvals for large adjustments, and fully auditable stock movements (user/timestamp/location) must accompany every stock change. Reference the `docs/updates/IMPLEMENTATION_PROGRESS.md` and `docs/sales/SALES_SUMMARY_FIXES.md` for examples of existing enforcement.

## References
- `references/inventory-playbook.md` — distills bookkeeping concepts, multi-location rules, valuation methods, and audit controls pulled from the provided executive overview.
- `docs/updates/IMPLEMENTATION_PROGRESS.md` and `docs/sales/SALES_SUMMARY_FIXES.md` — show how recent inventory fixes document changes, so future content should link to these when referencing implementation examples.
- `docs/DATABASE.md`, `docs/API.md`, and `docs/workflows.md` — ensure any inventory rule update mentions the tenant-centric query standards, API response expectations, and spec-driven workflow.

## Common Mistakes
- Updating only one doc or code area (e.g., API without docs) — always sync code with `docs/API.md`, `docs/architecture/ARCHITECTURE.md`, and `docs/overview/README.md`.
- Allowing franchise_id leakage or loose aggregation logic — require `MAX()`/`ANY_VALUE()` for non-aggregated columns and `franchise_id` filtering on every join.
- Ignoring valuation/COGS updates when components change — tie each stock movement to the appropriate journal entry.
