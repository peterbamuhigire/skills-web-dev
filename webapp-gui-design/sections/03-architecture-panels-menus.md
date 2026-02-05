## Architecture

```
includes/head.php    → CSS, meta
includes/topbar.php  → Navigation
includes/footer.php  → Footer
includes/foot.php    → JS
seeder-page.php      → Template (ALWAYS clone)
```

## Three-Tier Panel Structure (Multi-Tenant SaaS)

**CRITICAL: Three-tier architecture with separate includes per panel:**

1. **`/public/` (root)** - Franchise Admin Panel (THE MAIN WORKSPACE)
   - Includes: `public/includes/` (head.php, topbar.php, footer.php, foot.php)
   - Pages: `dashboard.php`, `students.php`, `inventory.php`, etc.
   - Users: franchise owners, staff
   - **This is NOT a member panel - it's the franchise management workspace!**

2. **`/public/adminpanel/`** - Super Admin Panel
   - Includes: `public/adminpanel/includes/` (head.php, topbar.php, footer.php, foot.php)
   - Pages: franchise management, system settings, cross-franchise analytics
   - Users: super admins
   - Menu: `menus/admin.php`

3. **`/public/memberpanel/`** - End User Portal
   - Includes: `public/memberpanel/includes/` (head.php, topbar.php, footer.php, foot.php)
   - Pages: self-service features for end users
   - Users: students, customers, patients, members
   - Menu: `menus/member.php`

**Shared Resources:**

- Assets: `public/assets/` (CSS, JS, images)
- Uploads: `public/uploads/` (user-uploaded files)
- APIs: Can live outside `public/`, route `/api` to `api/index.php` via web server

**JavaScript separation:**

- Keep pages clean—no inline JS blocks in the HTML.
- All global JS lives in `includes/foot.php`.
- Page-specific JS must be in its own file (one file per page) and included by that page.

## Menu Design Rules (Mandatory)

- Keep menus minimal, calm, and easy on the eye.
- Group items by job role so a user can find their work in one place.
- Each menu can have at most **5 submenus**.
- Each submenu can have at most **6 items**.
- If more items are required, add **one** extra submenu level (no deeper than that).
- Use Bootstrap Icons on **all** menu headings and entries (`bi-*`).
- Prefer fewer pages: group related functions on one page with tabs/cards/sections and apply permissions per component.

### Menu Structure Examples (Use as a guide)

**Finance** `bi-cash-stack`

- Overview `bi-speedometer2`
  - Summary `bi-clipboard-data`
  - KPIs `bi-graph-up`
  - Cash Position `bi-wallet2`
- Billing `bi-receipt`
  - Invoices `bi-file-earmark-text`
  - Credit Notes `bi-file-minus`
  - Payments `bi-credit-card`
- Accounts `bi-journal-text`
  - AR `bi-person-check`
  - AP `bi-person-x`
  - Journals `bi-journal`
  - Charts of Accounts `bi-diagram-3`
- Treasury `bi-bank`
  - Bank Reconciliation `bi-check2-circle`
  - Transfers `bi-arrow-left-right`
  - Cashbook `bi-book`
- Reports `bi-file-bar-graph`
  - P&L `bi-graph-down`
  - Balance Sheet `bi-columns-gap`
  - Cash Flow `bi-water`
  - Taxes `bi-percent`
  - More Reports `bi-folder2`
    - Aging `bi-clock-history`
    - Audit Trail `bi-shield-check`

**HR & Payroll** `bi-people`

- People `bi-person-badge`
  - Directory `bi-people`
  - Profiles `bi-person-lines-fill`
  - Documents `bi-folder2-open`
- Attendance `bi-calendar-check`
  - Clocking `bi-alarm`
  - Shifts `bi-calendar-week`
  - Leave `bi-calendar-minus`
- Payroll `bi-cash-coin`
  - Pay Runs `bi-calculator`
  - Deductions `bi-dash-circle`
  - Benefits `bi-gift`
  - Payslips `bi-receipt-cutoff`
- Compliance `bi-clipboard-check`
  - Taxes `bi-percent`
  - Pension `bi-shield`
  - Contracts `bi-file-earmark-text`

**Stores & Inventory** `bi-box-seam`

- Catalog `bi-boxes`
  - Items `bi-box`
  - Categories `bi-tags`
  - Units `bi-rulers`
- Stock `bi-stack`
  - On Hand `bi-box2`
  - Adjustments `bi-sliders`
  - Transfers `bi-arrow-left-right`
- Purchasing `bi-bag`
  - Requisitions `bi-clipboard-plus`
  - Purchase Orders `bi-file-earmark-plus`
  - GRN `bi-inbox-arrow-down`
- Warehousing `bi-house-gear`
  - Locations `bi-geo`
  - Bin Cards `bi-card-list`
  - Pick/Pack `bi-box2-heart`
- Reports `bi-file-bar-graph`
  - Valuation `bi-currency-exchange`
  - Slow Movers `bi-hourglass`
  - Stock Ledger `bi-journal-text`

**System Settings** `bi-gear`

- Access Control `bi-shield-lock`
  - Roles `bi-person-gear`
  - Permissions `bi-key`
  - Users `bi-person`
- Organization `bi-building`
  - Company Profile `bi-building-gear`
  - Branches `bi-diagram-2`
  - Departments `bi-diagram-3`
- Integrations `bi-plug`
  - Email/SMS `bi-envelope`
  - Payments `bi-credit-card`
  - API Keys `bi-key-fill`
- System `bi-sliders`
  - Preferences `bi-toggles`
  - Audit Logs `bi-clipboard-data`
  - Backups `bi-hdd`
