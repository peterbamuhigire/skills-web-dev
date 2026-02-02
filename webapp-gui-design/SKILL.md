---
name: webapp-gui-design
description: "Professional web app UI using commercial templates (Tabler/Bootstrap 5) with strong frontend design direction when needed. Use for CRUD interfaces, dashboards, admin panels with SweetAlert2, DataTables, Flatpickr. Clone seeder-page.php, use modular includes, follow established patterns."
---

# Web App GUI Design

Build professional web UIs using commercial templates with established component patterns.

**Core Principle:** Start with templates, follow modular architecture, maintain consistency.

**API-First Rule (Required):** Frontend must never access the database directly. All reads/writes go through backend services exposed via APIs so future clients (Android, iOS, etc.) reuse the same logic.

## When to Use

✅ CRUD interfaces, admin panels, dashboards
✅ Data management UIs
✅ Need professional look fast

✅ When asked for polished frontend aesthetics inside a web app

❌ Marketing sites (not covered by this skill)
❌ Mobile-native apps

## Stack

- **Base:** Tabler (Bootstrap 5.3.0)
- **Icons:** Bootstrap Icons only (`bi-*`)
- **Alerts:** SweetAlert2 (NO native alert/confirm)
- **Tables:** DataTables + Bootstrap 5
- **Dates:** Flatpickr (auto-applied)
- **Selects:** Select2

## Print/PDF Letterhead (Mandatory)

All report print and PDF outputs MUST include a full letterhead with:

- Organization name
- Physical address
- Phone number
- Email address
- Logo

Never ship a report print/PDF view without the complete letterhead. Print views must auto-trigger the browser print dialog on load.

## Date Formatting (UI Required)

- Never display raw SQL timestamps (e.g., `2026-01-25 00:00:00`).
- Display dates as `d M Y` (e.g., `27 Jan 2026`) or `d F Y` (e.g., `27 January 2026`) depending on context.
- Store and transmit dates as `YYYY-MM-DD`.
- Use a shared formatter for UI rendering to keep consistent output.

```javascript
function formatDisplayDate(value) {
  if (!value) return "-";
  const datePart = String(value).slice(0, 10);
  const parts = datePart.split("-");
  if (parts.length === 3) {
    const date = new Date(
      Number(parts[0]),
      Number(parts[1]) - 1,
      Number(parts[2]),
    );
    return date.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  }
  return value;
}
```

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

## Permissions (Required)

- Apply **page-level permissions** for sensitive screens (e.g., admin settings, financial configuration).
- Apply **action-level permissions** for sensitive buttons (create/edit/delete/export), so users only see actions they are allowed to perform.
- **Do not add new permissions** for features that are available to all users. Use existing roles/permissions and keep access simple unless a business rule requires restriction.
- When in doubt: protect destructive actions, keep read-only views available to broader roles.

## Searchable Dropdowns (Required)

- Any dropdown that can exceed **30 items in production** must be a searchable Select2 (or equivalent).
- Configure search to match **at least two attributes** where possible:
  - Students: name + registration number
  - Clients/customers: name + phone
  - Diseases: disease name + ICD number
  - Medicines: brand name + generic name + item code
  - Stock items/products: name + code

### Dropdown Testing (MANDATORY Before Marking Features Complete)

**CRITICAL:** Never mark a feature as "production ready" or "fully implemented" without testing dropdowns i.e the logic that loads them must return data, test these.

**Testing Requirements:**

✅ **Test in Browser** - Load the page and verify:

- Dropdown populates with data (not empty)
- Search functionality works
- API calls succeed (check Network tab)
- Console shows no errors

✅ **Add Console Logging** - For dynamic dropdowns:

```javascript
async function loadGroups() {
  console.log("Loading customer groups...");
  const result = await apiGet(`${apiBase}/customer-groups.php`, false);

  if (!result || !result.success) {
    console.error("❌ Failed to load customer groups:", result?.message);
    return;
  }

  const groups = result?.data?.groups || [];
  console.log("✅ Customer groups loaded:", groups.length, "items");
  // ... populate dropdown
}
```

✅ **Error Handling** - API calls for dropdowns should:

- Not show SweetAlert errors on page load (use `showErrors = false` parameter)
- Log errors to console with clear ❌ prefix
- Show user-friendly warning only if critical data fails
- Handle empty arrays gracefully

❌ **Common Mistakes:**

- Marking feature complete without browser testing
- API returning empty array but no error logged
- Silent failures (dropdown stays empty, no console error)
- Using wrong API endpoint path
- API response structure doesn't match expected format

**Example Error Handling:**

```javascript
async function apiGet(url, showErrors = true) {
  try {
    console.log("API GET:", url);
    const resp = await fetch(url, {
      method: "GET",
      credentials: "same-origin",
    });

    const json = await resp.json().catch((e) => {
      console.error("JSON parse error:", e);
      return null;
    });

    if (!json) {
      if (showErrors)
        await Swal.fire("Error", "Invalid server response", "error");
      return null;
    }

    return json;
  } catch (error) {
    console.error("❌ API GET exception:", error);
    if (showErrors) await Swal.fire("Error", "Network error occurred", "error");
    return null;
  }
}
```

## Page Template

**ALWAYS clone `skeleton.php` for new pages in SaaS Seeder Template.**

```php
<?php
require_once __DIR__ . '/../src/config/auth.php';
requireAuth(); // Automatic auth check + session prefix system

// Set page metadata
$pageTitle = 'Students';
$panel = 'admin'; // or 'member' depending on panel

// Get franchise context (uses session prefix system)
$franchiseId = getSession('franchise_id');
$userType = getSession('user_type');
?>
<!doctype html>
<html lang="en">
<head>
    <?php include __DIR__ . "/includes/head.php"; ?>
</head>
<body>
    <script src="/assets/tabler/js/tabler.min.js"></script>

    <div class="page">
        <div class="sticky-top">
            <?php include __DIR__ . "/includes/topbar.php"; ?>
        </div>
        <div class="page-wrapper">
            <div class="page-header d-print-none">
                <div class="container-xl">
                    <div class="row g-2 align-items-center">
                        <div class="col">
                            <div class="page-pretitle">Student Management</div>
                            <h2 class="page-title">Students</h2>
                        </div>
                        <div class="col-auto">
                            <button class="btn btn-primary" onclick="showAddModal()">
                                <i class="bi bi-plus me-1"></i> Add Student
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="page-body">
                <div class="container-xl">
                    <div class="card">
                        <div class="card-body">
                            <!-- Content -->
                            <table id="studentsTable" class="table table-striped" style="width:100%">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <footer class="footer footer-transparent d-print-none">
                <?php include __DIR__ . '/includes/footer.php'; ?>
            </footer>
        </div>
    </div>

    <?php include __DIR__ . "/includes/foot.php"; ?>
    <script src="./assets/js/pages/students.js"></script>
</body>
</html>
```

**Key Points:**
- Use `__DIR__` for all paths (works in any panel)
- Call `requireAuth()` (automatic session check with prefix system)
- Set `$pageTitle` and `$panel` variables for includes
- Use `getSession('franchise_id')` to get franchise context
- All database queries MUST filter by `franchise_id`

## SweetAlert2 (Mandatory)

**Never use alert/confirm/prompt.**

```javascript
// Success
Swal.fire({ icon: "success", title: "Saved!", timer: 2000 });

// Confirm
const result = await Swal.fire({
  icon: "warning",
  title: "Delete?",
  showCancelButton: true,
  confirmButtonText: "Delete",
  confirmButtonColor: "#d63939",
});
if (result.isConfirmed) {
  await deleteItem(id);
}

// Loading
Swal.fire({ title: "Processing...", didOpen: () => Swal.showLoading() });
Swal.close(); // When done

// Input
const { value } = await Swal.fire({
  title: "Name",
  input: "text",
  inputValidator: (v) => (!v ? "Required" : null),
});
```

## DataTables

**Always paginate** with a default of **25 rows per page**. Use server-side pagination for large datasets.
**Default ordering:** disable client-side sorting unless explicitly required. Keep ordering from the API/query.
**Number formatting:** display numeric values with thousands separators (e.g., 254,150.35).

```javascript
$("#myTable").DataTables({
  ajax: { url: "./api/items.php", dataSrc: "data" },
  columns: [
    { data: "id", visible: false },
    { data: "code", title: "Code" },
    {
      data: null,
      render: (d) => `
                <div class="d-flex align-items-center">
                    <span class="avatar me-2" style="background-image:url('${d.photo_url}')"></span>
                    <div>
                        <div>${escapeHtml(d.name)}</div>
                        <small class="text-muted">${d.category}</small>
                    </div>
                </div>
            `,
    },
    {
      data: "status",
      render: (d) => `<span class="badge bg-${getStatusColor(d)}">${d}</span>`,
    },
    {
      data: null,
      orderable: false,
      render: (d) => `
                <button class="btn btn-sm btn-primary btn-edit" data-id="${d.id}"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-danger btn-delete" data-id="${d.id}"><i class="bi bi-trash"></i></button>
            `,
    },
  ],
  ordering: false,
  pageLength: 25,
  responsive: true,
});

$("#myTable").on("click", ".btn-edit", function () {
  editItem($(this).data("id"));
});
```

**HTML:**

```html
<table id="myTable" class="table table-striped" style="width:100%">
  <thead>
    <tr>
      <th>ID</th>
      <th>Code</th>
      <th>Name</th>
      <th>Status</th>
      <th>Actions</th>
    </tr>
  </thead>
</table>
```

## Forms

```html
<form id="itemForm">
  <input type="hidden" id="itemId" />
  <div class="row">
    <div class="col-md-6 mb-3">
      <label class="form-label required">Code</label>
      <input type="text" class="form-control" id="code" required />
    </div>
    <div class="col-md-6 mb-3">
      <label class="form-label required">Name</label>
      <input type="text" class="form-control" id="name" required />
    </div>
  </div>
  <div class="mb-3">
    <label class="form-label">Description</label>
    <textarea class="form-control" id="description" rows="3"></textarea>
  </div>
  <div class="row">
    <div class="col-md-6 mb-3">
      <label class="form-label">Category</label>
      <select class="form-select" id="categoryId">
        <option value="">Select...</option>
      </select>
    </div>
    <div class="col-md-6 mb-3">
      <label class="form-label">Date</label>
      <input type="date" class="form-control" id="date" />
    </div>
  </div>
</form>
```

**Required CSS:**

```css
.form-label.required::after {
  content: " *";
  color: #d63939;
}
```

## Modals

```html
<div class="modal fade" id="itemModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 id="modalTitle">Add Item</h5>
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="modal"
        ></button>
      </div>
      <div class="modal-body"><!-- Form --></div>
      <div class="modal-footer">
        <button class="btn btn-secondary" data-bs-dismiss="modal">
          Cancel
        </button>
        <button class="btn btn-primary" id="saveBtn">
          <i class="bi bi-check me-1"></i> Save
        </button>
      </div>
    </div>
  </div>
</div>
```

```javascript
const modal = new bootstrap.Modal($("#itemModal")[0]);
$("#itemModal").on("hidden.bs.modal", resetForm);

function showAddModal() {
  resetForm();
  $("#modalTitle").text("Add Item");
  modal.show();
}
```

## Icons (Bootstrap Icons Only)

```html
<i class="bi bi-plus"></i>
<!-- Add -->
<i class="bi bi-pencil"></i>
<!-- Edit -->
<i class="bi bi-trash"></i>
<!-- Delete -->
<i class="bi bi-eye"></i>
<!-- View -->
<i class="bi bi-search"></i>
<!-- Search -->
<i class="bi bi-download"></i>
<!-- Export -->

<button class="btn btn-primary"><i class="bi bi-plus me-1"></i> Add</button>
```

## AJAX

```javascript
// GET
async function loadItems() {
  try {
    const res = await fetch("./api/items.php?action=list");
    const data = await res.json();
    return data.success ? data.data : [];
  } catch (error) {
    Swal.fire("Error", error.message, "error");
    return [];
  }
}

// POST
async function saveItem(itemData) {
  try {
    const res = await fetch("./api/items.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(itemData),
    });
    const data = await res.json();
    if (data.success) {
      Swal.fire("Success!", "", "success");
      return data;
    }
    throw new Error(data.message);
  } catch (error) {
    Swal.fire("Error", error.message, "error");
    return null;
  }
}

// DELETE
async function deleteItem(id) {
  const result = await Swal.fire({
    icon: "warning",
    title: "Delete?",
    showCancelButton: true,
    confirmButtonText: "Delete",
    confirmButtonColor: "#d63939",
  });
  if (!result.isConfirmed) return;

  const res = await fetch(`./api/items.php?id=${id}`, { method: "DELETE" });
  const data = await res.json();
  if (data.success) {
    Swal.fire("Deleted!", "", "success");
    dataTable.ajax.reload();
  }
}
```

## Utilities

```javascript
function formatCurrency(amount, currency = "USD") {
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(
    amount || 0,
  );
}

function formatDate(dateString) {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function escapeHtml(text) {
  if (!text) return "";
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return String(text).replace(/[&<>"']/g, (m) => map[m]);
}

function debounce(func, wait) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

function getStatusColor(status) {
  const colors = {
    active: "success",
    inactive: "secondary",
    pending: "warning",
    deleted: "danger",
  };
  return colors[status?.toLowerCase()] || "secondary";
}
```

## Responsive

```css
/* Mobile first */
@media (max-width: 575.98px) { }
@media (max-width: 767px) { }
@media (max-width: 991.98px) { }

/* Mobile nav */
@media (max-width: 767px) {
    .navbar-nav .nav-link {
        font-size: 1.5rem !important;
        padding: 1.2rem 1.35rem !important;
    }
    .page-header .btn-list .btn { flex: 1 1 100%; }
}

/* Responsive tables */
@media (max-width: 768px) {
    .priority-2, .priority-3 { display: none; }
}

## Photo Cards (Lists)

Use consistent visual patterns for card lists with photos:

- **People entities** (staff, customers, patients): social-style cards with circular avatar and banner background.jpg.
- **Non-people entities** (products, assets, vehicles): banner cards using a random photo; fallback to default.jpg.
- Always use `object-fit: cover` and fixed heights to prevent layout shift.
- Keep actions compact (view/edit) and align to the right.
- Avoid clipping avatar overlaps: set card `overflow: visible` or absolutely position the avatar within the banner.
- Overlap **only the avatar** (not the name/role text) by applying negative margin on the avatar itself.
```

## Flatpickr

Auto-applied to `<input type="date">` with `Y-m-d` value, `d F Y` display.

```javascript
// Manual
flatpickr("#date", { dateFormat: "Y-m-d", altInput: true, altFormat: "d M Y" });

// DateTime
flatpickr("#datetime", { enableTime: true, dateFormat: "Y-m-d H:i" });

// Range
flatpickr("#range", { mode: "range", dateFormat: "Y-m-d" });
```

## Best Practices

**DO:**
✅ Clone seeder-page.php
✅ Use SweetAlert2
✅ Bootstrap Icons only
✅ Escape HTML
✅ Fetch API
✅ CSRF tokens

**DON'T:**
❌ Native alert/confirm
❌ Mix icon sets
❌ Create from scratch
❌ Inline handlers
❌ Skip auth checks

✅ Auto-trigger `window.print()` in `*-print.php` views so the dialog appears as soon as the DOM is ready, keeping `no-print` controls only for reprints.

## Frontend Design Standards

This skill guides the construction of distinctive, production-grade frontend interfaces that avoid generic “AI slop” aesthetics. Implement real working code with exceptional attention to detail and creative choices. When the user provides frontend requirements—be it a component, page, application, or interface—treat the ask as a chance to craft something unforgettable rather than a safe, templated layout. Refer to the complete terms in LICENSE.txt when invoking this aesthetic directive.

### Design Thinking

Before coding, understand the context and commit to a bold aesthetic direction:

- **Purpose:** What problem does this interface solve? Who uses it?
- **Tone:** Pick an extreme (brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc.). Use those flavors for inspiration and design something true to the chosen aesthetic.
- **Constraints:** Technical requirements such as framework, performance, or accessibility.
- **Differentiation:** What makes this unforgettable? What is the single thing someone will remember?

**CRITICAL:** Choose a clear conceptual direction and execute it with precision. Both bold maximalism and refined minimalism work—the key is intentionality, not intensity. Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is production-grade, visually striking, cohesive, and meticulously refined.

### Frontend Aesthetics Guidelines

Focus on:

- **Typography:** Choose beautiful, unique, and expressive fonts. Avoid generic families (Arial, Inter, Roboto, system stacks); opt for distinctive pairings where a characterful display font meets a refined body font.
- **Color & Theme:** Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents create more impact than timid, evenly-distributed palettes.
- **Motion:** Deliver animations for high-impact moments (staggered reveals, hero transitions, hover surprises). Favor CSS-only solutions for static HTML and use Motion libraries for React when appropriate. Staggered delays and scroll-triggered reveals beat scattershot micro-interactions.
- **Spatial Composition:** Exploit asymmetry, overlap, diagonal flow, generous negative space, or controlled density. Break the grid when it reinforces the concept.
- **Backgrounds & Visual Details:** Build atmosphere with gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, or grain overlays.

NEVER ship generic AI-generated aesthetics: avoid overused fonts (Inter, Roboto, Arial, system), cliché palettes (especially purple-on-white gradients), predictable layouts, and cookie-cutter component patterns. Every design should feel tailored to its context.

Interpret creatively, pick unexpected choices, and rotate through light/dark themes, different fonts, and varied aesthetics. DON’T repeat the same set of design decisions across outputs (e.g., no repeated Space Grotesk + monochrome combos).

**IMPORTANT:** Match the implementation complexity to the aesthetic vision. Maximalist concepts demand elaborate code (animations, layered effects); minimalist ideas require restraint, pixel-perfect spacing, and subtle refinements. Claude can deliver extraordinary creative work—commit fully to a distinctive vision.

## Common Mistakes

❌ `alert('Success!');` → ✅ `Swal.fire('Success!', '', 'success');`
❌ `<div>${data.name}</div>` → ✅ `<div>${escapeHtml(data.name)}</div>`
❌ `<i class="fa fa-plus">` → ✅ `<i class="bi bi-plus">`

## Checklist

- [ ] Cloned seeder-page.php
- [ ] Auth check
- [ ] Includes loaded
- [ ] Bootstrap Icons only
- [ ] SweetAlert2 for dialogs
- [ ] DataTables configured
- [ ] Fetch API
- [ ] HTML escaped
- [ ] Responsive
- [ ] CSRF tokens
- [ ] **Dropdowns tested in browser** (not empty, search works, console clean)
- [ ] **Console logging added** for dynamic dropdowns (✅ success, ❌ errors)
- [ ] **Error handling** implemented (graceful failures, user-friendly messages)

## Summary

**Principles:**

1. Clone seeder-page.php
2. Tabler/Bootstrap 5
3. SweetAlert2, DataTables, Flatpickr
4. Modular includes
5. Mobile-first

**Stack:**
Tabler, Bootstrap Icons, SweetAlert2, DataTables, Flatpickr, Select2

**Remember:** Professional UIs = Consistent patterns + Commercial templates.
