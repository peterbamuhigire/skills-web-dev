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
- **Use PNG images — NOT Bootstrap Icons — on all menu headings and entries.** See PNG Icon Standard below.
- Prefer fewer pages: group related functions on one page with tabs/cards/sections and apply permissions per component.

## PNG Icon Standard for Menus (Mandatory)

**All menu items MUST use `<img>` tags pointing to PNG files. Bootstrap Icon (`<i class="bi bi-...">`) tags are FORBIDDEN in menus.**

### HTML Pattern

Top-level nav icon (24×24):
```html
<span class="nav-link-icon d-md-none d-lg-inline-block">
    <img src="./dist/img/icons/finance.png" width="24" alt="Finance">
</span>
```

Submenu dropdown toggle (28×28):
```html
<a class="dropdown-item dropdown-toggle" href="#" data-bs-toggle="dropdown">
    <img src="./dist/img/icons/billing.png" width="28">
    Billing
</a>
```

Leaf menu item (16×16):
```html
<a href="./invoices.php" class="dropdown-item">
    <img src="./dist/img/icons/invoice.png" width="16">Invoices
</a>
```

### Standard Icons Folder

PNGs live in `./dist/img/icons/` (relative to the web root). The designer provides them; the developer references them by name. PNG files are square, transparent background, suitable for both light and dark themes.

### After Any Menu Update — PNG Audit (MANDATORY)

After adding or modifying any menu items, you MUST:

1. **Scan all menu files** for `<img src="./dist/img/icons/` tags to collect every PNG filename referenced.
2. **Check which files exist** in `./dist/img/icons/`.
3. **Report every missing PNG** to the developer in a clear list before considering the task done.

Output format (present this table whenever any PNGs are missing):

```
## PNG Icons Required — Please Design and Add to ./dist/img/icons/

| Filename           | Used for            | Size hint |
|--------------------|---------------------|-----------|
| billing.png        | Billing submenu     | 28×28     |
| invoice.png        | Invoices leaf item  | 16×16     |
| cash-flow.png      | Cash Flow report    | 16×16     |
```

Do NOT leave the task in a state where menu items point to non-existent PNG files. Always surface the missing list so the designer can action it immediately.

### PNG Naming Convention

Use lowercase, hyphen-separated names that describe the concept, not the icon shape:
- `billing.png` not `receipt-icon.png`
- `staff.png` not `person-filled.png`
- `day-close.png` not `close-door.png`

### Menu Structure Examples (Use as a guide)

Note: `bi-*` codes shown below are **concept hints only** for the designer — they are NOT used in the actual HTML. Each entry maps to a PNG file by the slug shown.

**Finance** → `finance.png`

- Overview → `overview.png`
  - Summary → `summary.png`
  - KPIs → `kpi.png`
  - Cash Position → `cash-position.png`
- Billing → `billing.png`
  - Invoices → `invoice.png`
  - Credit Notes → `credit-note.png`
  - Payments → `payment-method.png`
- Accounts → `accounts.png`
  - AR → `ar.png`
  - AP → `ap.png`
  - Journals → `journal.png`
  - Charts of Accounts → `chart-of-accounts.png`
- Treasury → `treasury.png`
  - Bank Reconciliation → `reconciliation.png`
  - Transfers → `transfer.png`
  - Cashbook → `cashbook.png`
- Reports → `reports.png`
  - P&L → `pnl.png`
  - Balance Sheet → `balance-sheet.png`
  - Cash Flow → `cash-flow.png`
  - Taxes → `taxes.png`

**HR & Payroll** → `hr.png`

- People → `staff.png`
  - Directory → `staff-list.png`
  - Profiles → `profile.png`
  - Documents → `documents.png`
- Attendance → `attendance.png`
  - Clocking → `clocking.png`
  - Shifts → `shifts.png`
  - Leave → `staff-leave.png`
- Payroll → `payroll.png`
  - Pay Runs → `salary-calendar.png`
  - Deductions → `deductions.png`
  - Benefits → `benefits.png`
  - Payslips → `salary-voucher.png`

**Stores & Inventory** → `inventory.png`

- Catalog → `catalog.png`
  - Items → `product.png`
  - Categories → `category.png`
  - Units → `units.png`
- Stock → `stock.png`
  - On Hand → `stock-on-hand.png`
  - Adjustments → `adjustments.png`
  - Transfers → `transfer.png`
- Purchasing → `purchasing.png`
  - Requisitions → `requisition.png`
  - Purchase Orders → `purchase-order.png`
  - GRN → `grn.png`

**System Settings** → `settings.png`

- Access Control → `access-control.png`
  - Roles → `roles.png`
  - Permissions → `permissions.png`
  - Users → `users.png`
- Organization → `franchise.png`
  - Company Profile → `setup.png`
  - Branches → `dpcs.png`
  - Departments → `departments.png`
- Integrations → `integrations.png`
  - Email/SMS → `communication.png`
  - Payments → `payment-method.png`
  - API Keys → `api-keys.png`
