# UX Standards Enforcement Skill

**Skill Name:** `ux-standards`
**Purpose:** Enforce mandatory UX patterns for web SaaS development
**Priority:** CRITICAL - Auto-apply to all web UI development

---

## Section 0 — Foundational UX philosophy (added 2026-05-06)

The bulk of this file (Sections 1+) is SaaS implementation patterns. The philosophy that grounds those patterns lives in the canonical book extractions at `book-extractions/`. Read this section first when evaluating whether a project needs the implementation patterns at all.

### The 5 canonical book extractions

- `book-extractions/levy-ux-strategy-extraction.md` — UX strategy as upstream gate (Four Tenets, Top-10 anti-patterns, Funnel Matrix, landing-page experiments)
- `book-extractions/enterprise-ux-financial-insurance-extraction.md` — enterprise process (5-level maturity, 5 outcomes, activity-by-level matrix)
- `book-extractions/branson-ux-ui-design-extraction.md` — psychology (Three HCI Paradigms, working memory, 4-stage cognitive affordance, persona discipline)
- `book-extractions/deacon-ux-ui-strategy-extraction.md` — UX history + 3 levels of UX scope
- `book-extractions/fekeshazi-pm-ux-guide-extraction.md` — PM collaboration rules and design-as-ongoing-process

### The four cross-cutting rules

1. **Validated user research is non-negotiable** (Levy). No "Field of Dreams" launches. Confront target customers with an MVP/landing page before scaling.
2. **All 5 outcomes must hit, not 4 of 5** (Synechron). Useful + Easy + Efficient + Pleasing + Accessible. One No = no premium launch.
3. **Recognition over recall + 4-stage cognitive affordance** (Branson). Show, don't make users remember. Every interactive element must pass Presence → Visibility → Recognizability → Intelligibility.
4. **Design is ongoing, not a project** (Fekeshazi). Plan for continuous design alongside continuous dev.

### Operational skill

For premium-priced enterprise engagements, invoke `enterprise-ux-process/SKILL.md` — operationalizes the Synechron process into 9 phases with declared maturity-level + 5-outcomes evidence pack.

### Cross-engine consumption map

- `website-skills/` — consumes Levy + Synechron + Branson + Deacon + Fekeshazi (5 skills upgraded; see `website-skills/universal-guidelines/`)
- `social-media-skills/` — consumes Branson personas + Levy tenets + Synechron 5 outcomes (Persona + Strategy clusters; see `social-media-skills/docs/ux-foundations.md`)
- `srs-skills/` — consumes all 5 (UX-spec + Strategic-vision clusters; see `srs-skills/docs/ux-foundations.md`)

### When to apply Sections 1+ (the implementation patterns)

The implementation patterns below (searchable dropdowns, etc.) apply when (a) the project is web SaaS AND (b) the philosophy gate above has been cleared. Don't apply patterns to a project that hasn't yet validated user research.

---

## Auto-Apply Rules

When generating or modifying web UI code, AUTOMATICALLY:

### 1. Searchable Dropdowns (MANDATORY)

**Trigger:** Any `<select>` for entities (stock items, customers, products, vendors, users, etc.)

**Auto-generate:**

```javascript
// Initialize Select2 on all entity dropdowns
$('#entitySelect').select2({
    placeholder: 'Search items...',
    allowClear: true,
    width: '100%',
    dropdownParent: $('#modalId') // Auto-detect if in modal
});
```

**Detection patterns:**

- `name="stock_item_id"` → Stock item select
- `name="product_id"` → Product select
- `name="customer_id"` → Customer select
- `name="unit_id"` → Unit select (UOM)
- `id` contains `Select` or `Dropdown` → Likely needs Select2

### 2. Loading States

**Trigger:** Any button that makes async calls

**Auto-generate:**

```javascript
$('#submitBtn')
    .html('<i class="spinner-border spinner-border-sm me-2"></i>Saving...')
    .prop('disabled', true);

// After complete:
$('#submitBtn')
    .html('<i class="bi bi-check me-2"></i>Save')
    .prop('disabled', false);
```

### 3. Confirmation Dialogs

**Trigger:** Delete, cancel, or destructive action buttons

**Auto-generate:**

```javascript
Swal.fire({
    icon: 'warning',
    title: 'Delete Item?',
    text: 'This action cannot be undone',
    showCancelButton: true,
    confirmButtonText: 'Yes, Delete',
    confirmButtonColor: '#d63939',
    cancelButtonText: 'Cancel'
}).then((result) => {
    if (result.isConfirmed) {
        // Proceed with action
    }
});
```

### 4. User-Friendly Errors

**Trigger:** Any error handling code

**Auto-generate:**

```javascript
try {
    // API call
} catch (error) {
    console.error('Technical error:', error); // Log technical details
    Swal.fire({
        icon: 'error',
        title: 'Unable to Complete Action',
        html: '<p>Please check your connection and try again.</p><p>If the problem persists, contact support.</p>'
    });
}
```

**NEVER generate:**

```javascript
// BAD - Never show technical errors to users
alert(error.message);
Swal.fire('Error', error.toString(), 'error');
```

### 5. Empty States

**Trigger:** Lists/tables that might be empty

**Auto-generate:**

```html
<div class="empty-state">
    <div class="empty-state-icon">
        <i class="bi bi-inbox"></i>
    </div>
    <h4>No Items Yet</h4>
    <p class="text-muted">Get started by adding your first item</p>
    <button class="btn btn-primary" onclick="openAddModal()">
        <i class="bi bi-plus"></i> Add Item
    </button>
</div>
```

### 6. Pagination

**Trigger:** Any list/table query fetching data

**Auto-include in API:**

```php
$page = (int)($_GET['page'] ?? 1);
$limit = min((int)($_GET['limit'] ?? 50), 200);
$offset = ($page - 1) * $limit;

$sql .= " LIMIT ? OFFSET ?";
$params[] = $limit;
$params[] = $offset;
```

### 7. Mobile-First CSS

**Auto-add to all forms/tables:**

```css
@media (max-width: 768px) {
    .data-table {
        overflow-x: auto;
    }
    .modal {
        margin: 0;
        max-width: 100%;
    }
}
```

### 8. Menu Design Rules (Mandatory)

**Trigger:** Any navigation menus for admin/member panels

**Auto-apply:**
- Keep menus minimal and easy on the eye.
- Group items by job role; a user should find their work in one menu.
- Each menu can have at most **5 submenus**.
- Each submenu can have at most **6 items**.
- If more items are needed, add **one** extra submenu level (no deeper).
- Use Bootstrap Icons on **all** menu headings and entries (`bi-*`).
- Prefer fewer pages by grouping related functions on a single page with permissioned sections/tabs/cards.

### 9. Premium UI/UX Gate (Mandatory For User-Facing Products)

**Trigger:** Any web, Android, iOS, dashboard, report, form-heavy, revenue-critical, or executive-facing interface.

**Auto-apply:**

- Load `premium-ui-ux-design` before finalizing UX requirements or screen implementation.
- Define the product's visual voice and connect it to the user, domain, and business model.
- Require tokenized color, typography, spacing, radius, elevation, icon, chart, and motion decisions.
- Require complete states: loading, empty, error, success, disabled, offline, permission denied, and destructive confirmation.
- Require platform fit: web responsive behavior, Android Material 3/mobile ergonomics, or iOS SwiftUI/native interaction rules.
- Require dashboard and report quality: charts must support a real decision, include context, and avoid decorative distortion.
- Block sign-off unless premium gate categories score at least 8/10.

---

## Quick Decision Tree

```
Is it a dropdown for entities?
├─ YES → Add Select2
└─ NO → Continue

Does it load data async?
├─ YES → Add loading spinner
└─ NO → Continue

Is it a delete/destructive action?
├─ YES → Add confirmation dialog
└─ NO → Continue

Does it show errors?
├─ YES → Use user-friendly messages only
└─ NO → Continue

Can the list be empty?
├─ YES → Add empty state
└─ NO → Continue

Can the list have > 50 items?
├─ YES → Add pagination
└─ NO → Continue

Is the interface user-facing or premium/revenue-critical?
├─ YES → Apply premium-ui-ux-design gate
└─ NO → Continue
```

---

## Code Review Checklist

Before marking code complete, verify:

- [ ] All entity dropdowns use Select2
- [ ] All async buttons show loading states
- [ ] All destructive actions have confirmations
- [ ] All errors are user-friendly
- [ ] All empty states have helpful content
- [ ] All lists > 50 items are paginated
- [ ] Responsive on mobile (320px width)
- [ ] Keyboard navigation works
- [ ] Premium/revenue-critical screens pass the premium UI/UX gate

---

## Common Patterns Library

### Pattern: Stock Item Dropdown

```html
<select id="stockItemSelect" name="stock_item_id" class="form-select" required style="width: 100%;">
    <option value="">Select stock item...</option>
</select>
<small class="text-muted">Type to search</small>

<script>
$('#stockItemSelect').select2({
    placeholder: 'Search stock items...',
    allowClear: true,
    width: '100%'
});
</script>
```

### Pattern: Customer Dropdown

```html
<select id="customerSelect" name="customer_id" class="form-select" style="width: 100%;">
    <option value="">Select customer...</option>
</select>

<script>
$('#customerSelect').select2({
    placeholder: 'Search customers...',
    allowClear: true,
    width: '100%',
    ajax: {
        url: './api/customers/search.php',
        dataType: 'json',
        delay: 250,
        data: function (params) {
            return { q: params.term, page: params.page || 1 };
        },
        processResults: function (data) {
            return {
                results: data.items.map(item => ({
                    id: item.id,
                    text: item.name
                }))
            };
        }
    },
    minimumInputLength: 2
});
</script>
```

### Pattern: Submit Button with Loading

```html
<button type="submit" id="submitBtn" class="btn btn-primary">
    <i class="bi bi-check me-2"></i>Save
</button>

<script>
$('#form').on('submit', async function(e) {
    e.preventDefault();

    const $btn = $('#submitBtn');
    $btn.html('<i class="spinner-border spinner-border-sm me-2"></i>Saving...').prop('disabled', true);

    try {
        const res = await fetch('./api/save.php', {
            method: 'POST',
            body: new FormData(this)
        });
        const data = await res.json();

        if (data.success) {
            Swal.fire('Success', data.message, 'success');
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error(error);
        Swal.fire('Error', 'Unable to save. Please try again.', 'error');
    } finally {
        $btn.html('<i class="bi bi-check me-2"></i>Save').prop('disabled', false);
    }
});
</script>
```

### Pattern: Delete Confirmation

```javascript
function deleteItem(id, name) {
    Swal.fire({
        icon: 'warning',
        title: 'Delete Item?',
        html: `<p>This will permanently delete <strong>${name}</strong>.</p><p>This action cannot be undone.</p>`,
        showCancelButton: true,
        confirmButtonText: 'Yes, Delete',
        confirmButtonColor: '#d63939',
        cancelButtonText: 'Cancel',
        focusCancel: true
    }).then(async (result) => {
        if (result.isConfirmed) {
            try {
                const res = await fetch(`./api/items/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.success) {
                    Swal.fire('Deleted', data.message, 'success');
                    reloadList();
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                console.error(error);
                Swal.fire('Error', 'Unable to delete. Please try again.', 'error');
            }
        }
    });
}
```

---

## Integration with Development Workflow

### When Claude Code generates new forms

1. Identify all dropdowns → Apply Select2
2. Identify submit buttons → Add loading states
3. Identify delete buttons → Add confirmations
4. Wrap API calls in try-catch → User-friendly errors
5. Add empty state HTML for lists
6. Add pagination params to queries

### When reviewing existing code

1. Search for `<select>` → Verify Select2
2. Search for `delete` → Verify confirmation
3. Search for `fetch(` → Verify error handling
4. Search for `.innerHTML = ''` → Check for empty state
5. Search for SQL queries → Verify pagination

---

## Priority Levels

**P0 - BLOCKING (must fix before deploy):**

- Non-searchable dropdown with entity data
- Delete without confirmation
- Technical errors shown to users
- No loading state on async actions

**P1 - HIGH (fix within sprint):**

- Missing empty states
- Lists without pagination (> 50 items)
- Poor mobile responsiveness

**P2 - MEDIUM (fix in next sprint):**

- Missing keyboard shortcuts
- No success animations
- Inconsistent spacing/styling

---

## References

- Full Standards: `/docs/standards/UX-STANDARDS.md`
- Quick Checklist: `/docs/standards/QUICK-UX-CHECKLIST.md`

---

**Last Updated:** 2026-01-29
**Status:** ACTIVE - Enforce in all web development
