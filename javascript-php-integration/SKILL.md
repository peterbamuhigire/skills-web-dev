---
name: javascript-php-integration
description: 'JavaScript integration patterns for PHP+JavaScript SaaS apps. Enforces
  JS-in-own-files architecture: data passing via data attributes/meta tags, AJAX to
  PHP API endpoints, CSRF protection, file organization, script loading strategy.
  Use when...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# JavaScript + PHP Integration

<!-- dual-compat-start -->
## Use When

- JavaScript integration patterns for PHP+JavaScript SaaS apps. Enforces JS-in-own-files architecture: data passing via data attributes/meta tags, AJAX to PHP API endpoints, CSRF protection, file organization, script loading strategy. Use when...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `javascript-php-integration` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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
| Correctness | JS-in-own-files boundary register | Markdown doc covering data passing via data-attributes, JSON islands, and PHP-emitted state | `docs/web/js-php-boundary.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
> **JavaScript belongs in `.js` files. PHP emits HTML and data — never JavaScript logic.**
>
> Allowed in PHP: `<script src="...">`, `<div data-config='<?= json_encode($data) ?>'>`, `<meta name="csrf-token" content="<?= $token ?>">`.
> Never in PHP: `<script>var x = <?php echo $x; ?></script>` (except truly trivial one-liners like page redirects).

---

## 1. File Organisation

```
assets/
└── js/
    ├── core/               # Shared infrastructure
    │   ├── api.js          # Fetch wrapper, error handling
    │   ├── auth.js         # CSRF token, session management
    │   ├── event-bus.js    # Global event system
    │   └── utils.js        # formatCurrency, formatDate, debounce, etc.
    ├── modules/            # Feature-specific JS (one per page/feature)
    │   ├── customers.js    # Customer list page
    │   ├── invoice-form.js # Invoice creation form
    │   ├── dashboard.js    # Dashboard charts and stats
    │   └── reports.js      # Report generation
    ├── components/         # Reusable UI components
    │   ├── confirm-dialog.js
    │   ├── data-table.js
    │   └── file-uploader.js
    └── vendors/            # Third-party libraries (local copies)
        ├── datatables.min.js
        └── chart.min.js
```

**Rule:** One module per page/feature. Core files are loaded in the layout. Modules are loaded per page.

---

## 2. Passing PHP Data to JavaScript

PHP passes data to JS via HTML — never via inline script blocks.

```php
<!-- Method 1: data attribute on container element (preferred) -->
<div id="page-data"
     data-config='<?= json_encode([
         'apiBase'        => '/api',
         'currencySymbol' => $settings->currency_symbol,
         'dateFormat'     => $settings->date_format,
         'tenantId'       => $tenant->id,
     ], JSON_HEX_APOS | JSON_HEX_TAG) ?>'>
</div>

<!-- Method 2: CSRF token in meta tag (for all AJAX calls) -->
<meta name="csrf-token" content="<?= htmlspecialchars($csrfToken) ?>">

<!-- Method 3: Per-page data on the page's own container -->
<div id="customers-table"
     data-filters='<?= json_encode($activeFilters, JSON_HEX_APOS) ?>'
     data-permissions='<?= json_encode($userPermissions, JSON_HEX_APOS) ?>'>
</div>
```

```javascript
// assets/js/core/config.js — Read all page config once at startup
const AppConfig = (() => {
    const el = document.getElementById('page-data');
    if (!el) return {};
    try {
        return JSON.parse(el.dataset.config);
    } catch {
        console.error('Invalid page config JSON');
        return {};
    }
})();

export const { apiBase, currencySymbol, dateFormat, tenantId } = AppConfig;
```

**Why `JSON_HEX_APOS | JSON_HEX_TAG`:** Prevents HTML injection when the JSON is placed inside an HTML attribute. Always use these flags.

---

## 3. CSRF Protection for AJAX

```javascript
// assets/js/core/auth.js
export function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content ?? '';
}
```

```javascript
// assets/js/core/api.js
import { getCsrfToken } from './auth.js';

export async function apiPost(endpoint, data) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw await response.json();
    return response.json();
}

export async function apiGet(endpoint, params = {}) {
    const url = new URL(endpoint, window.location.origin);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    const response = await fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    if (!response.ok) throw await response.json();
    return response.json();
}
```

**`X-Requested-With: XMLHttpRequest`** — PHP checks this to block direct browser URL access to API endpoints. Always include it on every AJAX call.

---

## 4. PHP API Endpoint Structure

```php
<?php
// api/customers.php
header('Content-Type: application/json');

// Verify AJAX — block direct URL access
if (empty($_SERVER['HTTP_X_REQUESTED_WITH'])) {
    http_response_code(403);
    exit(json_encode(['error' => 'Direct access forbidden']));
}

// Verify CSRF on state-changing requests
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $token = $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
    if (!hash_equals($_SESSION['csrf_token'], $token)) {
        http_response_code(403);
        exit(json_encode(['error' => 'Invalid CSRF token']));
    }
}

// Route the action
$action = $_GET['action'] ?? '';
switch ($action) {
    case 'list':
        echo json_encode(['data' => $customerService->getAll()]);
        break;
    case 'save':
        $body = json_decode(file_get_contents('php://input'), true);
        $result = $customerService->save($body);
        echo json_encode(['data' => $result]);
        break;
    default:
        http_response_code(400);
        echo json_encode(['error' => 'Unknown action']);
}
```

**Checklist for every PHP endpoint:**
- `Content-Type: application/json` header first
- Check `HTTP_X_REQUESTED_WITH` before anything else
- Verify CSRF token on POST/PUT/DELETE
- Use `hash_equals()` for CSRF comparison (timing-safe)
- Return consistent `{ data: ... }` or `{ error: ... }` shape

---

## 5. Script Loading Strategy

```php
<!-- layout.php: load core scripts once in every page -->
<script src="/assets/js/vendors/jquery.min.js"></script>
<script src="/assets/js/core/config.js" type="module"></script>
<script src="/assets/js/core/api.js" type="module"></script>
<script src="/assets/js/core/event-bus.js" type="module"></script>

<!-- Individual PHP pages declare which module they need -->
<?php $pageScript = 'modules/customers.js'; ?>

<!-- Layout footer picks it up -->
<?php if (!empty($pageScript)): ?>
<script src="/assets/js/<?= htmlspecialchars($pageScript) ?>" type="module"></script>
<?php endif; ?>
```

**Rules:**
- `type="module"` on all app JS — enables ES module imports and defers by default
- Vendor scripts (jQuery, DataTables) load before modules
- Each page sets `$pageScript` — the layout includes it
- Never load all modules on every page

---

## 6. DataTables + PHP Integration

```javascript
// assets/js/modules/customers.js
import { apiGet } from '../core/api.js';
import { EventBus } from '../core/event-bus.js';
import { getCsrfToken } from '../core/auth.js';

const el = document.getElementById('customers-table');
const permissions = JSON.parse(el?.dataset.permissions ?? '{}');

const table = new DataTable('#customers-table', {
    ajax: {
        url: '/api/customers?action=list',
        type: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': getCsrfToken()
        },
        dataSrc: 'data'
    },
    columns: [
        { data: 'id' },
        { data: 'name' },
        { data: 'email' },
        {
            data: 'id',
            render: (id) => permissions.canEdit
                ? `<button data-action="edit" data-id="${id}">Edit</button>`
                : ''
        }
    ]
});

// Event delegation — works for dynamically-rendered rows
el.addEventListener('click', e => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    if (btn.dataset.action === 'edit') {
        EventBus.emit('customer:edit', { id: btn.dataset.id });
    }
    if (btn.dataset.action === 'delete') {
        EventBus.emit('customer:delete', { id: btn.dataset.id });
    }
});
```

---

## 7. Form Submission via AJAX

```javascript
// assets/js/modules/customer-form.js
import { apiPost } from '../core/api.js';
import { EventBus } from '../core/event-bus.js';

document.getElementById('customer-form')?.addEventListener('submit', async e => {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('[type=submit]');

    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';
    clearErrors(form);

    try {
        const data = Object.fromEntries(new FormData(form));
        const result = await apiPost('/api/customers?action=save', data);
        EventBus.emit('customer:saved', result.data);
        Swal.fire('Saved!', 'Customer saved successfully.', 'success');
    } catch (error) {
        if (error.errors) showFieldErrors(form, error.errors);
        else Swal.fire('Error', error.message ?? 'Save failed', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save';
    }
});

function showFieldErrors(form, errors) {
    Object.entries(errors).forEach(([field, message]) => {
        const input = form.querySelector(`[name="${field}"]`);
        if (!input) return;
        input.classList.add('is-invalid');
        const feedback = input.nextElementSibling;
        if (feedback?.classList.contains('invalid-feedback')) {
            feedback.textContent = message;
        }
    });
}

function clearErrors(form) {
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
}
```

---

## 8. Allowed vs Prohibited in PHP Templates

| Allowed in PHP | Prohibited in PHP |
|---|---|
| `<script src="/assets/js/page.js" type="module">` | `<script>var config = <?php echo json_encode($data); ?></script>` |
| `<meta name="csrf-token" content="<?= $token ?>">` | `<script>if (<?= $role ?> === 'admin') { ... }</script>` |
| `<div data-config='<?= json_encode($cfg, JSON_HEX_APOS) ?>'>` | `onclick="deleteRecord(<?= $id ?>)"` |
| `<div id="chart" data-stats='<?= json_encode($stats) ?>'>` | `<script>$.ajax({ url: '<?= $url ?>' })</script>` |

**Exception:** Simple redirects after server actions are acceptable:
```php
<script>window.location.href = '<?= htmlspecialchars($redirectUrl) ?>';</script>
```

---

## 9. Event Bus Pattern

Decouples modules that need to communicate without direct imports.

```javascript
// assets/js/core/event-bus.js
const listeners = {};

export const EventBus = {
    on(event, callback) {
        (listeners[event] ??= []).push(callback);
    },
    off(event, callback) {
        listeners[event] = (listeners[event] ?? []).filter(cb => cb !== callback);
    },
    emit(event, payload) {
        (listeners[event] ?? []).forEach(cb => cb(payload));
    }
};
```

**Usage pattern:**
```javascript
// customers.js emits
EventBus.emit('customer:saved', { id: 42, name: 'Acme Ltd' });

// dashboard.js listens — no direct import of customers.js needed
EventBus.on('customer:saved', ({ id, name }) => {
    refreshCustomerCount();
});
```

---

## 10. Debugging PHP+JS Integration

- **Network tab:** Inspect AJAX request headers — verify `X-Requested-With` and `X-CSRF-Token` are present
- **PHP side:** `error_log(json_encode($data))` to confirm what the endpoint receives
- **JS side:** `console.log(JSON.parse(document.getElementById('page-data').dataset.config))` to verify data attribute passing
- **CSRF issues:** Check `$_SESSION['csrf_token']` is set before the page renders; regenerate on login
- **404 on AJAX:** Confirm URL includes correct query params (`?action=list`)
- **403 on AJAX:** `HTTP_X_REQUESTED_WITH` is missing or CSRF token mismatch

---

## 11. Pre-Commit Checklist

- [ ] No `<?php ?>` inside `<script>` tags (except redirects)
- [ ] PHP data passed via `data-*` attributes with `json_encode()` and `JSON_HEX_APOS | JSON_HEX_TAG`
- [ ] CSRF token in `<meta name="csrf-token">`, read only by `core/auth.js`
- [ ] All AJAX calls include `X-Requested-With: XMLHttpRequest`
- [ ] All POST AJAX calls include `X-CSRF-Token` header
- [ ] PHP endpoints verify `HTTP_X_REQUESTED_WITH` before responding
- [ ] PHP endpoints verify CSRF on every POST/PUT/DELETE
- [ ] JS files organised: `core/`, `modules/`, `components/`, `vendors/`
- [ ] Page-specific JS loaded per page; core loaded in layout footer
- [ ] Event delegation used for dynamically-added table row buttons
- [ ] `type="module"` on all app script tags
- [ ] No inline `onclick="..."` attributes with PHP-echoed values
