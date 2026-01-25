---
name: webapp-gui-design
description: "Professional web app UI using commercial templates (Tabler/Bootstrap 5) with strong frontend design direction when needed. Use for CRUD interfaces, dashboards, admin panels with SweetAlert2, DataTables, Flatpickr. Clone seeder-page.php, use modular includes, follow established patterns."
---

# Web App GUI Design

Build professional web UIs using commercial templates with established component patterns.

**Core Principle:** Start with templates, follow modular architecture, maintain consistency.

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

## Architecture

```
includes/head.php    → CSS, meta
includes/topbar.php  → Navigation
includes/footer.php  → Footer
includes/foot.php    → JS
seeder-page.php      → Template (ALWAYS clone)
```

**JavaScript separation:**
- Keep pages clean—no inline JS blocks in the HTML.
- All global JS lives in `includes/foot.php`.
- Page-specific JS must be in its own file (one file per page) and included by that page.

## Page Template

```php
<?php
require_once 'src/config/auth.php';
if (!isLoggedIn()) { header('Location: ./sign-in.php'); exit(); }
?>
<!doctype html>
<html>
<head><?php include("./includes/head.php"); ?></head>
<body>
    <div class="page">
        <div class="sticky-top"><?php include("./includes/topbar.php"); ?></div>
        <div class="page-wrapper">
            <div class="page-header d-print-none">
                <div class="container-xl">
                    <div class="row g-2 align-items-center">
                        <div class="col">
                            <div class="page-pretitle">Module</div>
                            <h2 class="page-title">Title</h2>
                        </div>
                        <div class="col-auto">
                            <button class="btn btn-primary" onclick="showAddModal()">
                                <i class="bi bi-plus me-1"></i> Add
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
                        </div>
                    </div>
                </div>
            </div>
            <footer><?php include './includes/footer.php'; ?></footer>
        </div>
    </div>
    <?php include("./includes/foot.php"); ?>
    <script src="./assets/js/pages/your-page.js"></script>
</body>
</html>
```

## SweetAlert2 (Mandatory)

**Never use alert/confirm/prompt.**

```javascript
// Success
Swal.fire({icon: 'success', title: 'Saved!', timer: 2000});

// Confirm
const result = await Swal.fire({
    icon: 'warning',
    title: 'Delete?',
    showCancelButton: true,
    confirmButtonText: 'Delete',
    confirmButtonColor: '#d63939'
});
if (result.isConfirmed) { await deleteItem(id); }

// Loading
Swal.fire({title: 'Processing...', didOpen: () => Swal.showLoading()});
Swal.close(); // When done

// Input
const {value} = await Swal.fire({
    title: 'Name',
    input: 'text',
    inputValidator: (v) => !v ? 'Required' : null
});
```

## DataTables

```javascript
$('#myTable').DataTables({
    ajax: {url: './api/items.php', dataSrc: 'data'},
    columns: [
        {data: 'id', visible: false},
        {data: 'code', title: 'Code'},
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
            `
        },
        {data: 'status', render: (d) => `<span class="badge bg-${getStatusColor(d)}">${d}</span>`},
        {
            data: null,
            orderable: false,
            render: (d) => `
                <button class="btn btn-sm btn-primary btn-edit" data-id="${d.id}"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-danger btn-delete" data-id="${d.id}"><i class="bi bi-trash"></i></button>
            `
        }
    ],
    order: [[0, 'desc']],
    pageLength: 25,
    responsive: true
});

$('#myTable').on('click', '.btn-edit', function() { editItem($(this).data('id')); });
```

**HTML:**
```html
<table id="myTable" class="table table-striped" style="width:100%">
    <thead><tr><th>ID</th><th>Code</th><th>Name</th><th>Status</th><th>Actions</th></tr></thead>
</table>
```

## Forms

```html
<form id="itemForm">
    <input type="hidden" id="itemId">
    <div class="row">
        <div class="col-md-6 mb-3">
            <label class="form-label required">Code</label>
            <input type="text" class="form-control" id="code" required>
        </div>
        <div class="col-md-6 mb-3">
            <label class="form-label required">Name</label>
            <input type="text" class="form-control" id="name" required>
        </div>
    </div>
    <div class="mb-3">
        <label class="form-label">Description</label>
        <textarea class="form-control" id="description" rows="3"></textarea>
    </div>
    <div class="row">
        <div class="col-md-6 mb-3">
            <label class="form-label">Category</label>
            <select class="form-select" id="categoryId"><option value="">Select...</option></select>
        </div>
        <div class="col-md-6 mb-3">
            <label class="form-label">Date</label>
            <input type="date" class="form-control" id="date">
        </div>
    </div>
</form>
```

**Required CSS:**
```css
.form-label.required::after { content: " *"; color: #d63939; }
```

## Modals

```html
<div class="modal fade" id="itemModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 id="modalTitle">Add Item</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body"><!-- Form --></div>
            <div class="modal-footer">
                <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button class="btn btn-primary" id="saveBtn"><i class="bi bi-check me-1"></i> Save</button>
            </div>
        </div>
    </div>
</div>
```

```javascript
const modal = new bootstrap.Modal($('#itemModal')[0]);
$('#itemModal').on('hidden.bs.modal', resetForm);

function showAddModal() {
    resetForm();
    $('#modalTitle').text('Add Item');
    modal.show();
}
```

## Icons (Bootstrap Icons Only)

```html
<i class="bi bi-plus"></i>       <!-- Add -->
<i class="bi bi-pencil"></i>     <!-- Edit -->
<i class="bi bi-trash"></i>      <!-- Delete -->
<i class="bi bi-eye"></i>        <!-- View -->
<i class="bi bi-search"></i>     <!-- Search -->
<i class="bi bi-download"></i>   <!-- Export -->

<button class="btn btn-primary"><i class="bi bi-plus me-1"></i> Add</button>
```

## AJAX

```javascript
// GET
async function loadItems() {
    try {
        const res = await fetch('./api/items.php?action=list');
        const data = await res.json();
        return data.success ? data.data : [];
    } catch (error) {
        Swal.fire('Error', error.message, 'error');
        return [];
    }
}

// POST
async function saveItem(itemData) {
    try {
        const res = await fetch('./api/items.php', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(itemData)
        });
        const data = await res.json();
        if (data.success) {
            Swal.fire('Success!', '', 'success');
            return data;
        }
        throw new Error(data.message);
    } catch (error) {
        Swal.fire('Error', error.message, 'error');
        return null;
    }
}

// DELETE
async function deleteItem(id) {
    const result = await Swal.fire({
        icon: 'warning',
        title: 'Delete?',
        showCancelButton: true,
        confirmButtonText: 'Delete',
        confirmButtonColor: '#d63939'
    });
    if (!result.isConfirmed) return;

    const res = await fetch(`./api/items.php?id=${id}`, {method: 'DELETE'});
    const data = await res.json();
    if (data.success) {
        Swal.fire('Deleted!', '', 'success');
        dataTable.ajax.reload();
    }
}
```

## Utilities

```javascript
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {style: 'currency', currency}).format(amount || 0);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'};
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

function debounce(func, wait) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

function getStatusColor(status) {
    const colors = {active: 'success', inactive: 'secondary', pending: 'warning', deleted: 'danger'};
    return colors[status?.toLowerCase()] || 'secondary';
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
flatpickr('#date', {dateFormat: 'Y-m-d', altInput: true, altFormat: 'd M Y'});

// DateTime
flatpickr('#datetime', {enableTime: true, dateFormat: 'Y-m-d H:i'});

// Range
flatpickr('#range', {mode: 'range', dateFormat: 'Y-m-d'});
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

## Frontend Design Direction (When Asked for Bespoke Aesthetics)

Use this only when the user asks for custom aesthetic direction beyond the standard Tabler look.

### Design Thinking

Before coding, understand the context and commit to a bold aesthetic direction:
- **Purpose:** What problem does this interface solve? Who uses it?
- **Tone:** Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc.
- **Constraints:** Technical requirements (framework, performance, accessibility).
- **Differentiation:** What makes this unforgettable? What’s the one thing someone will remember?

**Critical:** Choose a clear conceptual direction and execute it with precision. Intentionality matters more than intensity.

### Aesthetics Guidelines

Focus on:
- **Typography:** Choose distinctive fonts. Avoid generic choices like Arial/Inter. Pair a characterful display font with a refined body font.
- **Color & Theme:** Commit to a cohesive aesthetic. Use CSS variables. Dominant colors with sharp accents outperform timid palettes.
- **Motion:** Use animations for high-impact moments (staggered reveals, hover states). CSS-first for static HTML; use Motion libraries in React when available.
- **Spatial Composition:** Unexpected layouts, asymmetry, overlap, generous negative space or controlled density.
- **Backgrounds & Visual Details:** Add atmosphere with gradient meshes, noise textures, patterns, layered transparencies, dramatic shadows, decorative borders, and grain overlays.

**Avoid:** Generic AI aesthetics—overused fonts, cliché palettes, predictable layouts, and cookie-cutter components.

**Implementation Fit:** Match complexity to the aesthetic vision. Maximalist = elaborate code. Minimalist = restraint and precision.

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
