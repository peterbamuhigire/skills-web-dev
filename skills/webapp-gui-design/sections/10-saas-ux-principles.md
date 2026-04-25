## SaaS UX/UI Design Principles

Reference for building user-centered SaaS interfaces with Bootstrap 5 / Tabler + PHP.

### 1. SaaS Design Philosophy

- **User-centered approach:** every design decision starts from the user's perspective
- **Clarity over cleverness:** users should never wonder what a button does
- **Trust through consistency:** uniform visual language, predictable interactions across every module
- **Performance perception:** instant feedback makes apps feel fast even when processing
- **88% of SaaS users won't return** after a poor experience (industry research)
- **UX can increase conversion rates by up to 400%** — invest in usability before features

**Core rule:** If a user has to think about how the interface works, the interface has failed.

### 2. Onboarding Patterns

**First-run experience:** guided setup wizard, 3-5 steps maximum. Single concern per step.

**Progressive disclosure:** reveal features as users need them. Don't show everything at once.

**Role-aware onboarding:** admin sees organization setup, standard user sees personal workspace, viewer sees read-only orientation.

**Skip option:** always allow users to bypass onboarding. Never trap them.

#### Onboarding Checklist Card

```html
<div class="card" id="onboardingCard">
  <div class="card-header">
    <h3 class="card-title"><i class="bi bi-rocket-takeoff me-2"></i>Getting Started</h3>
    <div class="card-actions">
      <span class="badge bg-primary">3 of 7 complete</span>
    </div>
  </div>
  <div class="card-body">
    <div class="steps steps-green steps-counter my-3">
      <a href="/settings/profile" class="step-item active">Profile</a>
      <a href="/settings/team" class="step-item active">Team</a>
      <a href="/settings/billing" class="step-item active">Billing</a>
      <a href="/inventory" class="step-item">Products</a>
      <a href="/customers" class="step-item">Customers</a>
      <a href="/settings/integrations" class="step-item">Integrations</a>
      <a href="/reports" class="step-item">First Report</a>
    </div>
    <div class="progress progress-sm mt-3">
      <div class="progress-bar bg-primary" style="width: 42.8%"></div>
    </div>
  </div>
</div>
```

#### Contextual Tooltips (First Encounter)

```html
<button class="btn btn-primary" data-bs-toggle="popover"
  data-bs-trigger="focus" data-bs-placement="bottom"
  data-bs-content="Create your first invoice to start tracking revenue.">
  <i class="bi bi-plus me-1"></i> New Invoice
</button>
<script>
document.addEventListener('DOMContentLoaded', () => {
  if (!localStorage.getItem('seen_invoice_hint')) {
    const btn = document.querySelector('[data-bs-toggle="popover"]');
    const popover = new bootstrap.Popover(btn);
    popover.show();
    setTimeout(() => popover.hide(), 6000);
    localStorage.setItem('seen_invoice_hint', '1');
  }
});
</script>
```

### 3. Dashboard Design

**Role-specific dashboards:** Admin sees KPIs and system health. Standard user sees tasks. Viewer sees summary reports.

**Above the fold:** 3-4 most important metrics visible without scrolling.

#### Stat Card Row

Each stat card: subheader label + large value + trend indicator (color + arrow) + optional sparkline.

```html
<div class="row row-deck row-cards mb-3">
  <!-- Repeat this col pattern for each metric (3-4 cards) -->
  <div class="col-sm-6 col-lg-3">
    <div class="card">
      <div class="card-body">
        <div class="subheader">Total Revenue</div>
        <div class="d-flex align-items-baseline mt-1">
          <div class="h1 mb-0 me-2">$45,230</div>
          <div class="me-auto">
            <span class="text-green d-inline-flex align-items-center lh-1">
              12% <i class="bi bi-arrow-up ms-1"></i>
            </span>
          </div>
        </div>
        <div id="sparkline-revenue" class="chart-sm mt-2"></div>
      </div>
    </div>
  </div>
  <!-- More col-sm-6 col-lg-3 cards: Active Users, Pending Orders, Support Tickets -->
  <!-- Use text-green + bi-arrow-up for positive, text-red + bi-arrow-down for negative,
       text-yellow + bi-arrow-right for neutral -->
</div>
```

**Action shortcuts:** place "Quick Add" buttons for frequent tasks near the top.

**Activity feed:** recent events relevant to user's role in a card list.

**Time filter:** global date range selector (Flatpickr range mode) affecting all dashboard cards.

### 4. Navigation Best Practices

**Sidebar:** collapsible, grouped by module with icons. Active item highlighted.

**Breadcrumbs:** always show current location path. Users must know where they are.

**Module badges:** show counts for pending items (orders, messages, approvals).

**Mobile:** hamburger menu collapsing sidebar to off-canvas.

#### Breadcrumb Pattern

```html
<div class="page-header d-print-none">
  <div class="container-xl">
    <div class="row align-items-center">
      <div class="col-auto">
        <ol class="breadcrumb" aria-label="breadcrumbs">
          <li class="breadcrumb-item"><a href="/dashboard">Home</a></li>
          <li class="breadcrumb-item"><a href="/sales">Sales</a></li>
          <li class="breadcrumb-item active" aria-current="page">Invoice #1042</li>
        </ol>
      </div>
    </div>
  </div>
</div>
```

#### Global Search (Ctrl+K)

```html
<div class="modal fade" id="searchModal" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-body p-2">
        <div class="input-icon">
          <span class="input-icon-addon"><i class="bi bi-search"></i></span>
          <input type="text" id="globalSearchInput" class="form-control form-control-lg border-0"
            placeholder="Search customers, invoices, products..." autofocus>
        </div>
        <div id="searchResults" class="list-group list-group-flush mt-2"
          style="max-height: 300px; overflow-y: auto;"></div>
      </div>
    </div>
  </div>
</div>
<script>
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    new bootstrap.Modal(document.getElementById('searchModal')).show();
  }
});
document.getElementById('globalSearchInput')?.addEventListener('input', debounce(async function() {
  const q = this.value.trim();
  if (q.length < 2) { document.getElementById('searchResults').innerHTML = ''; return; }
  const res = await fetch(`/api/search.php?q=${encodeURIComponent(q)}`);
  const data = await res.json();
  document.getElementById('searchResults').innerHTML = (data.data || []).map(item =>
    `<a href="${item.url}" class="list-group-item list-group-item-action">
      <i class="bi ${item.icon} me-2 text-muted"></i>${escapeHtml(item.label)}
      <small class="text-muted ms-2">${item.type}</small>
    </a>`
  ).join('');
}, 300));
</script>
```

### 5. Empty States

**Never show blank pages.** Always provide helpful empty states with a clear CTA.

Structure: optional illustration + heading + description + CTA button.

```html
<!-- No data -->
<div class="card">
  <div class="card-body">
    <div class="empty">
      <div class="empty-icon"><i class="bi bi-receipt" style="font-size: 3rem;"></i></div>
      <p class="empty-title">No invoices yet</p>
      <p class="empty-subtitle text-muted">
        Create your first invoice to start tracking revenue.
      </p>
      <div class="empty-action">
        <button class="btn btn-primary" onclick="showAddModal()">
          <i class="bi bi-plus me-1"></i> Create Invoice
        </button>
      </div>
    </div>
  </div>
</div>

<!-- No search results -->
<div class="empty">
  <div class="empty-icon"><i class="bi bi-search" style="font-size: 3rem;"></i></div>
  <p class="empty-title">No matches found</p>
  <p class="empty-subtitle text-muted">Try adjusting your search or filters.</p>
  <div class="empty-action">
    <button class="btn btn-outline-primary" onclick="resetFilters()">
      <i class="bi bi-x-circle me-1"></i> Clear Filters
    </button>
  </div>
</div>

<!-- No permission -->
<div class="empty">
  <div class="empty-icon"><i class="bi bi-shield-lock" style="font-size: 3rem;"></i></div>
  <p class="empty-title">Access restricted</p>
  <p class="empty-subtitle text-muted">
    You don't have permission to view this section. Contact your administrator.
  </p>
</div>
```

### 6. Data Tables (SaaS Patterns)

**Server-side pagination** for large datasets (reference: api-pagination skill). **Column sorting** with visual indicators. **Global search** + per-column filters. **Bulk actions:** select-all checkbox + action dropdown. **Export:** CSV, PDF, print. **Loading skeleton** while data fetches. **Responsive:** horizontal scroll on mobile.

```javascript
const table = $("#customersTable").DataTable({
  ajax: { url: "./api/customers.php?action=list", dataSrc: "data" },
  columns: [
    { data: null, orderable: false, className: "dt-center",
      render: (d) => `<input type="checkbox" class="row-select" value="${d.id}">` },
    { data: "name", title: "Customer" },
    { data: "email", title: "Email" },
    { data: "plan", title: "Plan",
      render: (d) => `<span class="badge bg-${d === 'Pro' ? 'primary' : 'secondary'}">${d}</span>` },
    { data: "status", title: "Status",
      render: (d) => `<span class="badge bg-${getStatusColor(d)}">${d}</span>` },
    { data: null, orderable: false, title: "Actions",
      render: (d) => `
        <button class="btn btn-sm btn-ghost-primary btn-edit" data-id="${d.id}"><i class="bi bi-pencil"></i></button>
        <button class="btn btn-sm btn-ghost-info btn-view" data-id="${d.id}"><i class="bi bi-eye"></i></button>
        <button class="btn btn-sm btn-ghost-danger btn-delete" data-id="${d.id}"><i class="bi bi-trash"></i></button>` }
  ],
  ordering: false, pageLength: 25, responsive: true,
  dom: '<"d-flex justify-content-between align-items-center mb-3"<"bulk-actions">f>rtip',
  language: { search: "", searchPlaceholder: "Search customers..." }
});

// Bulk action toolbar
$('.bulk-actions').html(`
  <div class="d-none" id="bulkToolbar">
    <span class="me-2"><strong id="selectedCount">0</strong> selected</span>
    <div class="btn-group">
      <button class="btn btn-sm btn-outline-primary" onclick="bulkExport()"><i class="bi bi-download me-1"></i>Export</button>
      <button class="btn btn-sm btn-outline-danger" onclick="bulkDelete()"><i class="bi bi-trash me-1"></i>Delete</button>
    </div>
  </div>
`);
```

### 7. Settings & Preferences Pages

**Organization:** grouped by category (Profile, Security, Notifications, Billing, Team). **Layout:** left sidebar categories + right content panel on desktop; stacked cards on mobile. **Auto-save** toggle switches immediately. Explicit save button for complex forms. **Confirmation** for destructive settings (delete account, remove user).

```html
<div class="row">
  <div class="col-md-3 d-none d-md-block">
    <div class="card">
      <div class="list-group list-group-flush">
        <a href="#profile" class="list-group-item list-group-item-action active">
          <i class="bi bi-person me-2"></i>Profile</a>
        <a href="#security" class="list-group-item list-group-item-action">
          <i class="bi bi-shield-lock me-2"></i>Security</a>
        <a href="#notifications" class="list-group-item list-group-item-action">
          <i class="bi bi-bell me-2"></i>Notifications</a>
        <a href="#billing" class="list-group-item list-group-item-action">
          <i class="bi bi-credit-card me-2"></i>Billing</a>
        <a href="#team" class="list-group-item list-group-item-action">
          <i class="bi bi-people me-2"></i>Team</a>
      </div>
    </div>
  </div>
  <div class="col-md-9">
    <div class="card" id="profile">
      <div class="card-header"><h3 class="card-title">Profile Settings</h3></div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label required">Full Name</label>
            <input type="text" class="form-control" id="fullName" required>
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label required">Email</label>
            <input type="email" class="form-control" id="email" required>
          </div>
        </div>
      </div>
      <div class="card-footer text-end">
        <button class="btn btn-primary" onclick="saveProfile()">
          <i class="bi bi-check me-1"></i>Save Changes</button>
      </div>
    </div>
  </div>
</div>
```

### 8. Multi-Tenant UI Considerations

- **Tenant context:** always show current tenant/franchise name in the header or top bar
- **Tenant switching:** dropdown in top bar for users with multi-tenant access
- **Scoped data:** every list, dashboard, and report filtered to the current tenant — always
- **Branding:** support tenant logo and primary color customization where possible
- **Permission gates:** hide or disable features based on tenant plan tier
- **Reference:** multi-tenant-saas-architecture and modular-saas-architecture skills

```html
<!-- Tenant selector in topbar -->
<div class="nav-item dropdown">
  <a href="#" class="nav-link d-flex lh-1 text-reset p-0" data-bs-toggle="dropdown">
    <span class="avatar avatar-sm me-2"
      style="background-image: url('/api/tenant-logo.php')"></span>
    <div class="d-none d-xl-block ps-2">
      <div id="tenantName">Acme Corp</div>
      <div class="mt-1 small text-muted" id="tenantPlan">Pro Plan</div>
    </div>
  </a>
  <div class="dropdown-menu dropdown-menu-end">
    <a class="dropdown-item active" href="#" onclick="switchTenant(1)">Acme Corp</a>
    <a class="dropdown-item" href="#" onclick="switchTenant(2)">Beta Inc</a>
    <div class="dropdown-divider"></div>
    <a class="dropdown-item" href="/settings/tenants">Manage Organizations</a>
  </div>
</div>
```

### 9. Feedback & Micro-Interactions

**Loading states:** skeleton screens, not just spinners. **Success:** green toast (auto-dismiss 5s). **Error:** red toast with retry. **Confirmations:** SweetAlert2 for all destructive actions — never native `confirm()`. **Timing:** 150ms for micro-interactions, 300ms for page transitions. **Optimistic UI:** update immediately, roll back on API failure. **Hover states:** subtle background change on clickable rows.

#### SweetAlert2 Patterns for CRUD

```javascript
// Create / Update success
Swal.fire({ icon: 'success', title: 'Saved!', timer: 2000, showConfirmButton: false });

// Delete confirmation
async function confirmDelete(id, label) {
  const result = await Swal.fire({
    icon: 'warning', title: `Delete ${escapeHtml(label)}?`,
    text: 'This action cannot be undone.',
    showCancelButton: true, confirmButtonText: 'Delete', confirmButtonColor: '#d63939'
  });
  if (!result.isConfirmed) return false;
  const res = await fetch(`./api/items.php?id=${id}`, { method: 'DELETE' });
  const data = await res.json();
  if (data.success) {
    Swal.fire({ icon: 'success', title: 'Deleted!', timer: 1500, showConfirmButton: false });
    return true;
  }
  Swal.fire({ icon: 'error', title: 'Failed', text: data.message || 'Please try again.' });
  return false;
}

// Loading overlay for long operations
function showLoading(message = 'Processing...') {
  Swal.fire({ title: message, allowOutsideClick: false, didOpen: () => Swal.showLoading() });
}
```

#### Hover States & Transitions

```css
.table-hover tbody tr { cursor: pointer; transition: background-color 150ms ease; }
.card-hover:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.08);
  transition: all 150ms ease; }
```

### 10. Performance Perception

**Skeleton screens:** show content shape while loading. Never leave pages blank. **Debounce search:** 300ms delay prevents excessive API calls. **Lazy-load** images and heavy components below the fold. **Optimistic updates:** update UI immediately, roll back on API failure. **Progress bars** for known-length operations (uploads, imports). **Prefetch** likely-next-page data. **Infinite scroll or pagination** — never load everything.

#### Skeleton Loading Pattern

```html
<div class="card placeholder-glow" id="skeletonCard">
  <div class="card-body">
    <div class="row align-items-center">
      <div class="col-auto"><div class="avatar placeholder"></div></div>
      <div class="col">
        <div class="placeholder col-9 mb-2"></div>
        <div class="placeholder placeholder-xs col-6"></div>
      </div>
    </div>
  </div>
</div>
<script>
async function loadCard() {
  const skeleton = document.getElementById('skeletonCard');
  const res = await fetch('./api/summary.php');
  const data = await res.json();
  skeleton.outerHTML = buildRealCard(data);
}
</script>
```

#### Debounce Search

```javascript
document.getElementById('tableSearch').addEventListener('input', debounce(function() {
  const q = this.value.trim();
  if (q.length >= 2 || q.length === 0) table.search(q).draw();
}, 300));
```

### 11. SaaS Accessibility Baseline

- **WCAG 2.2 AA minimum** for all SaaS features
- **Keyboard navigation** for all interactive elements (Tab, Enter, Escape)
- **Screen reader support:** use `aria-label`, `role`, and semantic HTML
- **Color contrast:** 4.5:1 for normal text, 3:1 for large text and non-text elements
- **Focus indicators:** visible on all interactive elements — never `outline: none` without replacement
- **Skip-to-content link:** at the top of every page

```html
<a href="#main-content" class="visually-hidden-focusable">Skip to main content</a>
<div class="page-body" id="main-content">...</div>
```

### 12. DOs and DONTs

**DO:**

- Show empty states with helpful CTAs
- Use role-based dashboards
- Provide keyboard shortcuts for power users (Ctrl+K search, Ctrl+S save)
- Show loading skeletons instead of blank pages
- Use consistent iconography (Bootstrap Icons `bi-*`) across all modules
- Provide inline help and documentation links
- Support dark mode (or at minimum, respect OS preference via `prefers-color-scheme`)
- Use SweetAlert2 for all confirmations and alerts

**DON'T:**

- Don't show all features at once — use progressive disclosure
- Don't use generic error messages ("Something went wrong") without context or retry
- Don't force long forms without progress indicators
- Don't hide navigation behind unnecessary clicks
- Don't show data from other tenants (ever)
- Don't auto-play videos or animations
- Don't use different patterns for the same action across modules
- Don't use native `alert()`, `confirm()`, or `prompt()` — always SweetAlert2
