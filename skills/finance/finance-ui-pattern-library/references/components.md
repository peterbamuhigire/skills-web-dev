# Component Contracts

Production component specifications. The implementation language is project-specific; the contract is identical.

## MoneyCell

```tsx
<MoneyCell
  amount={118000}
  currency="UGX"
  signed={false}                   // true for P&L lines and variance columns
  drilldownTo="/journal/J-2026-05-11-0123"
  className="..."
/>
```

- Renders with tabular numerals.
- Currency code rendered once per column (in column header) where the table is single-currency. Inline currency label only when the column mixes currencies.
- `signed=true` shows the amount in `gain` (positive) or `loss` (negative) semantic colour. `signed=false` uses neutral foreground.
- Negative is shown with a leading minus in workflow surface; parentheses in ledger surface (configurable per entity, but consistent within a product).
- Drilldown affordance: hover underline, click navigates.
- Right-aligned in tables.
- Required props: `amount`, `currency`. Optional: `signed`, `drilldownTo`, `precision` (defaults to currency's minor-unit count).

## NetTaxGrossTriplet

```tsx
<NetTaxGrossTriplet
  net={100000}
  tax={18000}
  gross={118000}
  taxCode="UG-VAT-STD"
  currency="UGX"
/>
```

- Three adjacent cells.
- Tax cell carries the tax code as a small subscript / tooltip-on-hover (the code is always visible on print).
- Never collapsed into one cell. Never with tax in a tooltip only.

## StatusChip

```tsx
<StatusChip status="awaiting-approval" />
```

- Status drawn from the controlled taxonomy in `status-taxonomy.md`.
- Renders label + semantic colour + optional icon.
- Same chip used in web, mobile, and print.
- Sentence-case label rendering with localisation key lookup.

## PeriodChip

```tsx
<PeriodChip entity="..." book="..." periodState="locked" period="2026-04" />
```

- Always present in the top bar.
- Click expands a small popover showing the period state, lock date, and (where state is `locked`) a "Request reopen" button gated by role.

## EntityBookSwitcher / RoleSwitcher

- Visible only when the user has more than one. Otherwise renders as a label.
- Switching produces an audit-log entry.
- Switching to a different role triggers a confirmation when transitioning into a higher-privilege role (e.g. Cashier → Accountant).

## EnvironmentBanner

- Full-width banner across the top of the page when environment is non-prod.
- Different background colour per environment (token `env-staging`, `env-test`).
- Text: `Staging environment — do not use for production work.` / `Test environment.`

## DrilldownBreadcrumb

```tsx
<DrilldownBreadcrumb path={[
  { label: 'P&L 2026-05', to: '/reports/pnl?period=2026-05' },
  { label: '4000 Sales — Goods', to: '/coa/4000?period=2026-05' },
  { label: 'J-2026-05-12-0042', to: '/journal/J-2026-05-12-0042' },
  { label: 'Line 2', to: '/journal/J-2026-05-12-0042#line-2' },
  { label: 'POS-2026-05-12-0042', to: '/source/pos/POS-2026-05-12-0042' },
  { label: 'Receipt.pdf', to: '/evidence/POS-2026-05-12-0042/receipt.pdf' }
]}/>
```

## PostingForm

- Header: business-event label, date, source document reference.
- Lines: each line carries account (CoA picker), dimensions (per-account required / permitted), description, amount (net / tax / gross triplet where the tax flag is non-`none`).
- Evidence dropzone above the Save button.
- Audit-log preview below.
- Buttons: `Save draft`, `Submit for approval` (if maker-checker), `Post` (if direct-post permitted). Never `Delete`.

## ReconciliationTriage

- Two columns: left = imported items, right = ledger items.
- Centre: `Match`, `Unmatch`, `Split`, `Mark exception`.
- Filters across the top.
- Ageing summary across the top.
- Evidence pack export top-right.
- Drag-and-drop or keyboard match.

## LedgerGrid

- Dense table with sticky headers.
- Keyboard shortcuts visible in a `?` overlay.
- Filter row below header.
- Totals row sticky at the bottom of the viewport for visible columns.
- Bulk-action toolbar appears when rows are selected.

## CloseBoard

- Task list grouped by area (AR, AP, Bank recon, Inventory, Fixed Assets, Payroll, Tax, Adjustments, Reports).
- Each task: owner avatar, due date, dependency arrows, evidence count, status chip.
- "Release" button gated by role and by all-tasks-complete.

## ReturnPackViewer

- Header: jurisdiction, authority, period, return type, template version, state.
- Tabs: `Lines`, `Source transactions`, `Evidence pack`, `Sign-off`.
- Export buttons: PDF (signed), CSV (machine), authority-format file where supported.

## EvidenceDropzone

- Accepts PDF, images (jpg, png, heic), structured files (csv, xml).
- Captures file hash, uploader, timestamp.
- Files stored against the parent record; deletion requires reviewer sign-off and audit-log entry.

## PrintHeader / PrintFooter / SignOffBoxes

- Header on every printed page: entity, report title, period, framework, page X of Y.
- Footer on every printed page: generator, generated-at, preparer, reviewer.
- Sign-off boxes on the last page: preparer, reviewer, approver (with named space and date).

## Accessibility for each component

All components carry `aria-label` for money values, `aria-live="polite"` for status changes, keyboard handlers, and focus rings.

## Storybook organisation

```
stories/
├── 00-tokens/
├── 01-status/
├── 02-money/
├── 03-shell/
├── 04-posting/
├── 05-reconciliation/
├── 06-ledger-grid/
├── 07-close-board/
├── 08-return-pack/
├── 09-evidence/
└── 10-print/
```

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
