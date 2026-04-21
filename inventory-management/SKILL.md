---
name: inventory-management
description: Coordinate infrastructure for inventory, stock movement, BOMs, valuation,
  and multi-location controls while referencing the existing ERP implementation, inventory
  docs, and the small-business bookkeeping playbook.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Inventory Management Skill

<!-- dual-compat-start -->
## Use When

- Coordinate infrastructure for inventory, stock movement, BOMs, valuation, and multi-location controls while referencing the existing ERP implementation, inventory docs, and the small-business bookkeeping playbook.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `inventory-management` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Data safety | Inventory data model | Markdown doc per `skill-composition-standards/references/entity-model-template.md` covering stock, movement, BOM, and valuation entities | `docs/inventory/data-model.md` |
| Correctness | Inventory workflow test plan | Markdown doc covering receive, issue, transfer, valuation, and multi-location scenarios | `docs/inventory/workflow-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->

## Overview

Pair the existing stock-tracking implementation (stock ledgers, unit conversion, movements, purchase and sales flows, asset-level constraints) with general bookkeeping principles such as multi-location control, valuation methods, auditing, and SKU types. Use this skill whenever a change touches stock items, transfers, inventory valuation, assembly or BOM flows, stock adjustments, or reporting.

## Inventory Data Model

Ledger-first design: every quantity change appends a row to `stock_movements`; `stock_levels` is a materialised view of the ledger for fast reads. Never mutate historical rows.

```sql
CREATE TABLE products (
  id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  tenant_id       BIGINT UNSIGNED NOT NULL,
  sku_root        VARCHAR(64)  NOT NULL,
  name            VARCHAR(255) NOT NULL,
  category_id     BIGINT UNSIGNED NULL,
  unit_of_measure VARCHAR(16)  NOT NULL DEFAULT 'each',
  is_stock_item   TINYINT(1)   NOT NULL DEFAULT 1,
  is_perishable   TINYINT(1)   NOT NULL DEFAULT 0,
  created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_products_tenant_sku (tenant_id, sku_root),
  KEY idx_products_category (tenant_id, category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE skus (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  product_id  BIGINT UNSIGNED NOT NULL,
  sku_code    VARCHAR(64)  NOT NULL,
  variant     VARCHAR(128) NULL,
  barcode     VARCHAR(32)  NULL,
  unit_cost   DECIMAL(14,4) NOT NULL DEFAULT 0,
  UNIQUE KEY uq_skus_code (sku_code),
  KEY idx_skus_barcode (barcode),
  CONSTRAINT fk_skus_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;

CREATE TABLE locations (
  id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  tenant_id    BIGINT UNSIGNED NOT NULL,
  code         VARCHAR(64) NOT NULL,
  name         VARCHAR(255) NOT NULL,
  parent_id    BIGINT UNSIGNED NULL,
  kind         ENUM('company','region','warehouse','zone','aisle','bay','shelf','bin') NOT NULL,
  UNIQUE KEY uq_loc_code (tenant_id, code),
  KEY idx_loc_parent (parent_id)
) ENGINE=InnoDB;

CREATE TABLE stock_levels (
  sku_id      BIGINT UNSIGNED NOT NULL,
  location_id BIGINT UNSIGNED NOT NULL,
  on_hand_qty DECIMAL(14,4) NOT NULL DEFAULT 0,
  reserved_qty DECIMAL(14,4) NOT NULL DEFAULT 0,
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (sku_id, location_id),
  CONSTRAINT fk_sl_sku FOREIGN KEY (sku_id) REFERENCES skus(id),
  CONSTRAINT fk_sl_loc FOREIGN KEY (location_id) REFERENCES locations(id)
) ENGINE=InnoDB;

CREATE TABLE stock_movements (
  id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  tenant_id      BIGINT UNSIGNED NOT NULL,
  sku_id         BIGINT UNSIGNED NOT NULL,
  location_id    BIGINT UNSIGNED NOT NULL,
  movement_type  ENUM('receive','issue','transfer_out','transfer_in','adjust','stocktake','return') NOT NULL,
  qty_delta      DECIMAL(14,4) NOT NULL,
  unit_cost      DECIMAL(14,4) NOT NULL DEFAULT 0,
  batch_no       VARCHAR(64)  NULL,
  expiry_date    DATE         NULL,
  reference_type VARCHAR(32)  NULL,
  reference_id   BIGINT UNSIGNED NULL,
  reason_code    VARCHAR(32)  NULL,
  user_id        BIGINT UNSIGNED NOT NULL,
  created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_mv_sku_loc (sku_id, location_id, created_at),
  KEY idx_mv_ref (reference_type, reference_id),
  KEY idx_mv_batch (batch_no),
  CONSTRAINT fk_mv_sku FOREIGN KEY (sku_id) REFERENCES skus(id),
  CONSTRAINT fk_mv_loc FOREIGN KEY (location_id) REFERENCES locations(id)
) ENGINE=InnoDB;

CREATE TABLE suppliers (
  id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  tenant_id      BIGINT UNSIGNED NOT NULL,
  name           VARCHAR(255) NOT NULL,
  contact_email  VARCHAR(255) NULL,
  contact_phone  VARCHAR(32)  NULL,
  payment_terms  VARCHAR(64)  NULL,
  lead_time_days INT UNSIGNED NOT NULL DEFAULT 7,
  moq            DECIMAL(14,4) NOT NULL DEFAULT 1,
  currency       CHAR(3)      NOT NULL DEFAULT 'UGX',
  UNIQUE KEY uq_supplier (tenant_id, name)
) ENGINE=InnoDB;

CREATE TABLE purchase_orders (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  tenant_id   BIGINT UNSIGNED NOT NULL,
  supplier_id BIGINT UNSIGNED NOT NULL,
  location_id BIGINT UNSIGNED NOT NULL,
  po_number   VARCHAR(32)  NOT NULL,
  status      ENUM('draft','sent','confirmed','partial','received','closed','cancelled') NOT NULL DEFAULT 'draft',
  currency    CHAR(3)      NOT NULL,
  ordered_at  DATETIME     NULL,
  expected_at DATE         NULL,
  UNIQUE KEY uq_po_number (tenant_id, po_number),
  CONSTRAINT fk_po_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
  CONSTRAINT fk_po_location FOREIGN KEY (location_id) REFERENCES locations(id)
) ENGINE=InnoDB;

CREATE TABLE purchase_order_lines (
  id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  po_id        BIGINT UNSIGNED NOT NULL,
  sku_id       BIGINT UNSIGNED NOT NULL,
  ordered_qty  DECIMAL(14,4) NOT NULL,
  received_qty DECIMAL(14,4) NOT NULL DEFAULT 0,
  unit_cost    DECIMAL(14,4) NOT NULL,
  KEY idx_pol_po (po_id),
  CONSTRAINT fk_pol_po  FOREIGN KEY (po_id)  REFERENCES purchase_orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_pol_sku FOREIGN KEY (sku_id) REFERENCES skus(id)
) ENGINE=InnoDB;
```

## Stock Level Tracking

- On-hand qty lives in `stock_levels.on_hand_qty` and is updated by a trigger or service on every `stock_movements` insert.
- Reserved qty reflects allocations for unfulfilled sales orders, picking tasks, or in-transit transfers.
- Available qty is always derived, never stored: `available_qty = on_hand_qty - reserved_qty`.

Reorder point formula:

`reorder_point = (avg_daily_demand * lead_time_days) + safety_stock`

Safety stock formula (normal-demand approximation):

`safety_stock = z * stddev_daily_demand * sqrt(lead_time_days)`

Service level `z` table: `z=1.28` for 90%, `z=1.65` for 95%, `z=2.33` for 99%. Recompute weekly from the last 90 days of `stock_movements` where `movement_type = 'issue'`.

```sql
SELECT sku_id,
       AVG(daily_qty)               AS avg_daily_demand,
       STDDEV_SAMP(daily_qty)       AS stddev_daily_demand
FROM (
  SELECT sku_id, DATE(created_at) d, SUM(-qty_delta) daily_qty
  FROM stock_movements
  WHERE movement_type = 'issue' AND created_at >= NOW() - INTERVAL 90 DAY
  GROUP BY sku_id, DATE(created_at)
) t
GROUP BY sku_id;
```

## Reorder Triggers

- A daily cron job (02:00 local) scans `stock_levels` joined against `skus.reorder_point` and finds rows where `(on_hand_qty - reserved_qty) <= reorder_point`.
- Candidates are grouped by `preferred_supplier_id`, one draft PO per supplier per location.
- PO is created with `status = 'draft'` and emailed to procurement with an approval link. No goods move until a human confirms `status = 'sent'`.
- Manual override: any user with `inventory.reorder.create` permission can open a draft PO directly from the product screen, bypassing the cron.
- Do not auto-send to supplier. Auto-send violates approval controls and risks duplicate POs after ERP restarts.

## Barcode Scanning

EAN-13 and Code128 are mandatory for African retail (EAN for FMCG, Code128 for internal labels and cartons). Support three capture methods:

1. Camera via browser: use the native `BarcodeDetector` API on Chromium; fall back to `@zxing/browser` on Safari and older browsers.
2. Camera via native: ML Kit `BarcodeScanning` on Android, `Vision` framework `VNDetectBarcodesRequest` on iOS.
3. USB HID scanner: device presents as a keyboard and types the code followed by `Enter`. Capture the stream by timing keydown events.

```js
// USB HID scanner listener (web)
let buffer = '';
let lastKeyAt = 0;
document.addEventListener('keydown', (e) => {
  const now = performance.now();
  if (now - lastKeyAt > 50) buffer = '';
  lastKeyAt = now;
  if (e.key === 'Enter' && buffer.length >= 6) {
    handleScan(buffer);
    buffer = '';
    return;
  }
  if (e.key.length === 1) buffer += e.key;
});
```

- Debounce duplicate scans within 500 ms.
- Never trust the barcode alone for price; resolve `barcode -> sku_id -> unit_cost` on the server.

## Goods Receive

Three supported patterns; every pattern writes `stock_movements` rows with `movement_type = 'receive'` and positive `qty_delta`:

1. PO-matched receive: receiver selects an open PO, scans each line, and confirms line-by-line. System updates `purchase_order_lines.received_qty` and transitions PO to `partial` or `received`.
2. Blind receive: receiver sees only the SKU list (no ordered qty). This prevents "count to match the PO" fraud. System compares counts to PO after submission and flags variance.
3. Quantity variance: if `received_qty != ordered_qty`, prompt for a reason code (`short_shipped`, `damaged_in_transit`, `over_shipped`, `wrong_item`). Variance over 5% or `$100` requires manager approval.

## Stock Transfer

Inter-location transfer runs a two-phase state machine to prevent phantom stock:

- States: `draft -> in_transit -> completed | cancelled`.
- Draft: receiver and sender both see the request. No stock moves.
- In-transit: sending location fires a `transfer_out` movement (negative delta at source). A `transfer_in` row is NOT created yet. The stock belongs to a synthetic `in_transit` location owned by the company, not the destination.
- Completed: receiving location confirms arrival. System writes a `transfer_in` movement (positive delta at destination) and empties the `in_transit` bucket for that transfer ID.
- Cancelled before in-transit: no movement rows exist; delete the draft.
- Cancelled after in-transit (e.g., lost in transit): write a `transfer_in` back to the source location with `reason_code = 'transfer_reversal'`.

## Stock Adjustment

- Write-off: negative `qty_delta` with `movement_type = 'adjust'` and `reason_code` from `damaged`, `expired`, `miscounted`, `theft`, `donation`, `sample`.
- Write-up: positive `qty_delta` with `reason_code = 'found'` or `'correction'`.
- Threshold rule: any adjustment whose absolute value of `qty_delta * unit_cost` exceeds a tenant-configurable threshold (default UGX 370,000 equivalent to roughly $100) requires manager approval before the movement is inserted. Store pending adjustments in `stock_adjustments` with `approval_state`.
- Every adjustment posts a matching journal entry to the accounting ledger: write-off debits an expense account (`Inventory Shrinkage`) and credits `Inventory Asset`.

## Batch Operations

CSV import supports `receive`, `adjust`, and `transfer` in bulk with a dry-run preview that shows resulting stock levels before commit.

CSV columns:

| Column | Required | Type | Notes |
|--------|----------|------|-------|
| operation | yes | enum | receive, adjust, transfer |
| sku_code | yes | string | must exist |
| location_code | yes | string | must exist |
| dest_location_code | conditional | string | required when operation=transfer |
| qty | yes | decimal | non-negative unless operation=adjust |
| unit_cost | conditional | decimal | required on receive |
| batch_no | optional | string | required on receive if product is_perishable |
| expiry_date | optional | date | ISO 8601 (YYYY-MM-DD) |
| reason_code | conditional | string | required when operation=adjust |

Example:

```csv
operation,sku_code,location_code,dest_location_code,qty,unit_cost,batch_no,expiry_date,reason_code
receive,SKU-1001,UG-KLA-WH1,,120,4500,B2026-04,2026-10-31,
adjust,SKU-1002,UG-KLA-WH1,,-5,,,,damaged
transfer,SKU-1003,UG-KLA-WH1,UG-MBR-WH2,20,,,,
```

Validation: SKU must exist, location must exist, numeric parse must succeed, reason_code in allowed set, dry-run renders projected `stock_levels`. Commit runs inside a single transaction per upload.

## Stock-Take (Physical Count)

- Cycle count: weekly sweep of a rotating SKU subset (ABC class A weekly, B monthly, C quarterly). Counters scan each bin and enter the physical qty; variance is committed immediately.
- Full stock-take: freeze sales (`POS` enters read-only mode), count every SKU in every bin, reconcile, then reopen sales. Usually run at financial year-end.
- Variance report: `variance = counted_qty - system_on_hand`. Negative variance is shrinkage; positive variance usually indicates earlier miscount.
- Automatic adjustment: the reconciliation step writes one `stock_movements` row per SKU with `movement_type = 'stocktake'` and `qty_delta = variance`. Variance over the adjustment threshold still requires manager approval.

## FIFO / LIFO / Weighted Average

Costing method is selected per product, not per tenant. Document the choice in the product master.

- FIFO (default for perishables and most retail): oldest stock consumed first; COGS reflects older costs; ending inventory reflects current costs.
- LIFO: newest stock consumed first; rare outside USA tax contexts and banned under IFRS.
- Weighted average: recomputed after every receive as `total_cost / total_qty`; smooths price spikes, common in manufacturing.

Layers table (FIFO/LIFO implementation):

```sql
CREATE TABLE stock_layers (
  id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  sku_id        BIGINT UNSIGNED NOT NULL,
  location_id   BIGINT UNSIGNED NOT NULL,
  received_at   DATETIME NOT NULL,
  qty_remaining DECIMAL(14,4) NOT NULL,
  unit_cost     DECIMAL(14,4) NOT NULL,
  KEY idx_layer_consume (sku_id, location_id, received_at)
) ENGINE=InnoDB;
```

On sale under FIFO, deduct from the oldest layer first; on sale under LIFO, deduct from the newest. On weighted average, ignore layers and use `products.moving_avg_cost`, recomputed as `(old_qty * old_avg + received_qty * received_cost) / (old_qty + received_qty)`.

## Expiry Date Tracking

- `stock_movements.batch_no` and `stock_movements.expiry_date` are mandatory for any product with `is_perishable = 1`.
- FEFO (First Expired First Out) picking order overrides FIFO for perishables: pick the batch with the earliest `expiry_date` whose `qty_remaining > 0`.
- Daily job flags items where `expiry_date <= CURRENT_DATE + INTERVAL 30 DAY` and emails the store manager. A second alert fires at 7 days.
- Mandatory for pharmacy (NDA compliance), food service, cosmetics, and any regulated SKU class.
- Expired stock is written off with `reason_code = 'expired'` and must not be sold, even at discount.

## Supplier Management

- Catalog columns: name, contact email and phone, payment terms (`net30`, `net45`, `cod`), `lead_time_days`, MOQ, preferred currency.
- PO workflow: `draft -> sent -> confirmed -> partial -> received -> closed`; `cancelled` is a terminal state reachable from any pre-`received` state.
- Supplier performance KPIs (recomputed monthly):
  - On-time delivery rate = `deliveries_on_or_before_expected_at / total_deliveries`.
  - Fill rate = `sum(received_qty) / sum(ordered_qty)` per line.
  - Defect rate = `returned_qty / received_qty` over rolling 90 days.
- Suppliers with on-time rate under 80% or fill rate under 90% are flagged for review; procurement decides whether to renegotiate or drop.

## Multi-Location Inventory

- Location hierarchy: `company -> region -> warehouse -> zone -> aisle -> bay -> shelf -> bin`. Use the `kind` enum in `locations`.
- Location codes encode hierarchy for zone-picking efficiency, e.g., `UG-KLA-WH1-A-03-2-B`:
  - `UG` country, `KLA` city/region, `WH1` warehouse, `A` zone, `03` aisle, `2` bay, `B` bin.
- Stock levels are stored at the lowest location level the tenant tracks; rollups to warehouse or region are computed on read.
- In-transit stock belongs to a synthetic location per transfer (`TRANSFER-<id>`), not to source or destination, until the transfer is completed.
- Cross-location visibility is governed by role: a clerk at `WH1` should not see `WH2` stock unless given the `inventory.read_all_locations` permission.

## Reporting

Four core reports every deployment must ship:

1. Stock valuation: `SUM(on_hand_qty * unit_cost)` grouped by location and category. Uses the product's costing method (FIFO layers, LIFO layers, or moving average).
2. Slow-moving items: SKUs with no `issue` movement in the last 90 days. Output: SKU, location, on-hand qty, tied-up cost, last movement date. Action: clearance, markdown, or supplier return.
3. Stock turnover rate: `COGS / average_inventory_value` over the reporting window. Target bands by industry: grocery 10-20, pharmacy 6-10, electronics 4-6, fashion 3-5. Under-target means dead stock; over-target can mean stockouts.
4. Stock ageing: bucket each SKU by days since last receive into `0-30`, `31-60`, `61-90`, `90+`. Ageing stock over 90 days ties up working capital and usually loses value.

Example ageing query:

```sql
SELECT sku_id,
  CASE
    WHEN DATEDIFF(NOW(), MAX(received_at)) <= 30  THEN '0-30'
    WHEN DATEDIFF(NOW(), MAX(received_at)) <= 60  THEN '31-60'
    WHEN DATEDIFF(NOW(), MAX(received_at)) <= 90  THEN '61-90'
    ELSE '90+'
  END AS age_bucket,
  SUM(qty_remaining) AS qty
FROM stock_layers
GROUP BY sku_id, age_bucket;
```

## Mobile Interface Patterns

- Scan-first design: the barcode scanner is the primary input. Do not force keyboard entry of SKU codes; offer it only as fallback.
- Large input targets: minimum 48 x 48 dp for every tap target (Material guideline and iOS HIG floor). Receive screens should push this to 56 dp.
- Offline-capable: warehouse cold rooms, basements, and upcountry branches frequently lose WiFi. Queue movements locally (IndexedDB for web, Room for Android, SwiftData for iOS) and sync with conflict resolution on reconnect.
- Field-friendly contrast: default to high-contrast dark-on-light themes. Warehouse lighting is inconsistent; avoid grey-on-grey.
- Glove-usable buttons: no tiny tap targets; no gesture-only actions; every primary action must have a visible button at least 48 dp tall. Capacitive touch fails through thick gloves, so pair scan inputs with physical trigger handhelds where possible.

## Companion Skills

- `saas-erp-system-design` — multi-module ERP architecture where inventory fits
- `pos-sales-ui-design` — retail sales that consume inventory
- `pos-restaurant-ui-standard` — restaurant inventory depletes on order fire
- `mysql-data-modeling` / `postgresql-fundamentals` — database patterns for ledger-style movements
- `pwa-offline-first` — offline-capable warehouse and field workflows
- `mobile-saas-planning` — mobile app that drives inventory operations

## Sources

- *Warehouse Management* — Gwynne Richards (Kogan Page)
- *Operations Management* — Jay Heizer (Pearson)
- FEFO / FIFO methodology — `en.wikipedia.org/wiki/FIFO_and_LIFO_accounting`
- Uganda Revenue Authority EFRIS inventory requirements — `efris.ura.go.ug`
