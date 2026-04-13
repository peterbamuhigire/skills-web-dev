---
name: javascript-modern
description: 'Modern JavaScript (ES6+) patterns for PHP+JavaScript SaaS apps: modules,
  async/await, destructuring, Proxy/Reflect, generators, WeakMap/WeakSet, optional
  chaining, error handling, and performance patterns. Use when writing JavaScript
  for web...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# javascript-modern

<!-- dual-compat-start -->
## Use When

- Modern JavaScript (ES6+) patterns for PHP+JavaScript SaaS apps: modules, async/await, destructuring, Proxy/Reflect, generators, WeakMap/WeakSet, optional chaining, error handling, and performance patterns. Use when writing JavaScript for web...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `javascript-modern` or would be better handled by a more specific companion skill.
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

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Expert-level ES6+ patterns for PHP+JavaScript SaaS developers. Assumes fluency with variables, loops, and functions.

## Architecture Rule (Non-Negotiable)

JavaScript belongs in its own `.js` files. PHP only emits a `<script src="...">` tag or passes config via a single JSON data attribute. No `<?php echo $var ?>` scattered through JS files.

```php
<!-- PHP emits one data attribute — no inline JS -->
<div id="app-config"
     data-config='<?= json_encode($config, JSON_HEX_APOS) ?>'
     data-user='<?= json_encode(['id' => $user->id, 'role' => $user->role]) ?>'>
</div>
```

```javascript
// assets/js/app.js — reads config cleanly from its own file
const config = JSON.parse(document.getElementById('app-config').dataset.config);
const user   = JSON.parse(document.getElementById('app-config').dataset.user);
```

---

## 1. Module Pattern (IIFE + ES Modules)

```javascript
// assets/js/modules/user-table.js
const UserTable = (() => {
    let tableInstance = null;           // private — unreachable from outside

    function init(config) { tableInstance = new DataTable('#users-table', config); }
    function refresh()    { tableInstance?.ajax.reload(); }

    return { init, refresh };           // public API only
})();

export default UserTable;

// Named exports for shared utilities: assets/js/core/utils.js
export function debounce(fn, delay) { /* ... */ }
export function throttle(fn, limit) { /* ... */ }
```

---

## 2. Async/Await — The Right Patterns

### Sequential vs Parallel (critical performance distinction)

```javascript
// WRONG — runs in series (~2000ms total)
async function loadDashboard(userId) {
    const profile  = await fetchProfile(userId);   // waits 800ms
    const settings = await fetchSettings(userId);  // THEN waits 1200ms
}

// CORRECT — runs in parallel (~1200ms total)
async function loadDashboard(userId) {
    const [profile, settings] = await Promise.all([
        fetchProfile(userId),
        fetchSettings(userId)
    ]);
    renderDashboard(profile, settings);
}
```

### Promise Combinators — Choosing the Right Tool

| Method | Fulfills when | Rejects when | Use case |
|---|---|---|---|
| `Promise.all()` | All fulfill | Any rejects | Dashboard load — need everything |
| `Promise.allSettled()` | All settle | Never | Batch uploads — need all outcomes |
| `Promise.race()` | First settles | First rejects | Timeout pattern |
| `Promise.any()` | First fulfills | All reject | Redundant CDNs — fastest wins |

```javascript
// Promise.race for timeout
function fetchWithTimeout(url, ms) {
    const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
    );
    return Promise.race([fetch(url), timeoutPromise]);
}

// Promise.allSettled for batch operations
async function uploadFiles(files) {
    const results = await Promise.allSettled(files.map(uploadSingleFile));
    const failed  = results.filter(r => r.status === 'rejected');
    const success = results.filter(r => r.status === 'fulfilled');
    return { success, failed };
}
```

### Async IIFE for top-level await compatibility

```javascript
(async () => {
    const data = await apiRequest('/api/init');
    App.init(data);
})();
```

---

## 3. Production-Grade Fetch Wrapper

```javascript
// assets/js/core/api.js
class APIError extends Error {
    constructor(message, status) {
        super(message);
        this.status = status;
        this.name = 'APIError';
    }
}

async function apiRequest(url, options = {}) {
    const defaults = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content
        }
    };

    const merged   = { ...defaults, ...options,
        headers: { ...defaults.headers, ...(options.headers ?? {}) }
    };
    const response = await fetch(url, merged);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: response.statusText }));
        throw new APIError(error.message, response.status);
    }
    return response.json();
}

export { apiRequest, APIError };
```

---

## 4. Destructuring — Beyond the Basics

```javascript
// Rename while destructuring (API response key differs from local name)
const { user_id: id, created_at: createdAt } = apiResponse;

// Default values — only applied when value is undefined, not when it's 0 or ''
// This is why the old pattern (val || default) is wrong
const { name = 'Unknown', role = 'guest', notifications = 0 } = user;
// notifications = 0 is respected; (notifications || 10) would wrongly give 10

// Nested destructuring for API responses
const { address: { city, country = 'UG' } } = user;

// Array destructuring with skip
const [first, , third] = arr;
const [winner, runnerUp, ...others] = leaderboard;

// Swap variables without temp
[a, b] = [b, a];

// Function parameter destructuring with safe default for entire object
function makeRequest({ url, method = 'GET', timeout = 8000, headers = {} } = {}) {
    // Safe even when called with no arguments
}
```

---

## 5. Optional Chaining and Nullish Coalescing

```javascript
// Safe deep access — short-circuits at first null/undefined
const city  = user?.address?.city ?? 'Unknown';
const count = response?.data?.items?.length ?? 0;

// Safe method call — no "cannot read property of undefined"
modal?.hide();
table?.ajax?.reload();

// Optional index access
const first = items?.[0]?.name;

// Nullish coalescing vs OR — critical difference
const count1 = userCount ?? 10;   // 0 is valid — returns 0
const count2 = userCount || 10;   // 0 is falsy — wrongly returns 10
```

---

## 6. Generators for Pagination / Lazy Data

Generators are functions that can pause (`yield`) and resume. They implement the iterator protocol — the engine behind `for...of`, spread, and `Array.from`.

```javascript
// assets/js/modules/paginator.js
async function* fetchPages(endpoint) {
    let page = 1;
    while (true) {
        const data = await apiRequest(`${endpoint}?page=${page}`);
        if (!data.items.length) return;
        yield data.items;
        if (!data.hasNextPage) return;
        page++;
    }
}

// Usage — reads like synchronous code
for await (const items of fetchPages('/api/records')) {
    renderItems(items);
}

// Generator for infinite sequences (e.g., auto-incrementing IDs)
function* idSequence(prefix = 'row') {
    let n = 0;
    while (true) yield `${prefix}-${++n}`;
}
const nextId = idSequence('item');
nextId.next().value; // 'item-1'
nextId.next().value; // 'item-2'
```

Key rules: `function*` declares a generator. Calling it returns a generator object (does NOT run the body). Each `.next()` call runs to the next `yield` and pauses.

---

## 7. WeakMap for Private Data and DOM Metadata

WeakMap keys must be objects. When the key is garbage collected the entry disappears — no memory leaks.

```javascript
// Private class state — not reachable from outside
const _private = new WeakMap();

class Modal {
    constructor(element) {
        _private.set(this, { element, isOpen: false });
    }
    open() {
        const data = _private.get(this);
        data.isOpen = true;
        data.element.classList.add('show');
    }
    isOpen() { return _private.get(this).isOpen; }
}

// Attach metadata to DOM nodes without polluting the node object
const elementMeta = new WeakMap();
const registerTable = (el, cfg) => elementMeta.set(el, { cfg, rows: 0 });
const getTableMeta  = el => elementMeta.get(el);
```

Use `WeakSet` to tag objects ("has this record been processed?") without preventing GC.

---

## 8. Proxy for Validation and Reactivity

A Proxy wraps a target and intercepts operations via traps. Always use `Reflect` to forward the default behaviour — it handles inherited setters and edge cases correctly.

```javascript
// Validation proxy
function createValidatedUser(data) {
    return new Proxy(data, {
        set(target, prop, value, receiver) {
            if (prop === 'age'   && (typeof value !== 'number' || value < 0))
                throw new TypeError('age must be a non-negative number');
            if (prop === 'email' && !value.includes('@'))
                throw new TypeError('invalid email format');
            return Reflect.set(target, prop, value, receiver);  // always use Reflect, not target[prop]=value
        }
    });
}

// Reactivity proxy — Vue 3's core mechanism in miniature
function makeReactive(target, onChange) {
    return new Proxy(target, {
        set(obj, prop, value, receiver) {
            const result = Reflect.set(obj, prop, value, receiver);
            onChange(prop, value);
            return result;
        }
    });
}

const formData = makeReactive({}, (field, value) => {
    validateField(field, value);
    updatePreview(field, value);
});
```

---

## 9. Error Handling Strategy

```javascript
// assets/js/core/errors.js
class ValidationError extends Error {
    constructor(field, msg) { super(msg); this.name = 'ValidationError'; this.field = field; }
}
class NetworkError extends Error {
    constructor(status, msg) { super(msg); this.name = 'NetworkError'; this.status = status; }
}
class AuthError extends Error {
    constructor(msg = 'Session expired') { super(msg); this.name = 'AuthError'; }
}
export { ValidationError, NetworkError, AuthError };

// Centralised handler — call from every catch block
function handleError(error) {
    if (error instanceof ValidationError)                        showFieldError(error.field, error.message);
    else if (error instanceof AuthError)                         window.location.href = '/login';
    else if (error instanceof NetworkError && error.status===429) showToast('Too many requests', 'warning');
    else if (error instanceof NetworkError && error.status>=500)  showToast('Server error', 'error');
    else { showToast(error.message || 'Something went wrong', 'error'); console.error('[Unhandled]', error); }
}

// Global safety net for unhandled rejections
window.addEventListener('unhandledrejection', event => {
    handleError(event.reason);
    event.preventDefault();
});
```

---

## 10. Event Delegation (Performance Pattern)

Attach one listener to the container instead of per-row listeners. Avoids memory leaks when rows are added/removed dynamically.

```javascript
document.querySelector('#data-table').addEventListener('click', e => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;

    const { action, id } = btn.dataset;
    actions[action]?.(id);
});

const actions = {
    edit:   id => openEditModal(id),
    delete: id => confirmDelete(id),
    view:   id => openViewModal(id),
};
```

---

## 11. Debounce and Throttle

```javascript
// Debounce — wait for a pause in events (search, form validation)
function debounce(fn, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// Throttle — maximum one call per interval (scroll, resize)
function throttle(fn, limit) {
    let lastCall = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastCall >= limit) {
            lastCall = now;
            fn.apply(this, args);
        }
    };
}

// Usage
const searchHandler = debounce(async query => {
    const results = await apiRequest(`/api/search?q=${encodeURIComponent(query)}`);
    renderResults(results);
}, 300);

document.getElementById('search').addEventListener('input', e =>
    searchHandler(e.target.value)
);

const scrollHandler = throttle(() => updateStickyHeader(), 100);
window.addEventListener('scroll', scrollHandler);
```

| Pattern | Core idea | Use case |
|---|---|---|
| Debounce | Execute only after events stop | Search input, form save |
| Throttle | Execute at most once per interval | Scroll, resize, mousemove |

---

## 12. LocalStorage with Expiry

```javascript
// assets/js/core/store.js
const Store = {
    set(key, value, ttlMinutes = 60) {
        localStorage.setItem(key, JSON.stringify(
            { value, expires: Date.now() + ttlMinutes * 60_000 }
        ));
    },
    get(key) {
        try {
            const item = JSON.parse(localStorage.getItem(key));
            if (!item) return null;
            if (Date.now() > item.expires) { localStorage.removeItem(key); return null; }
            return item.value;
        } catch { return null; }  // corrupt data — fail silently
    },
    remove: key => localStorage.removeItem(key),
    clear:  ()  => localStorage.clear()
};
export default Store;
```

---

## 13. `const` / `let` and Arrow Function `this`

```javascript
// const by default. Object contents can still be mutated; the binding cannot.
const user = { name: 'Alice' };
user.name = 'Bob';    // valid
// user = {};         // TypeError

// Arrow functions capture 'this' lexically — no .bind(this) or self = this needed
class DataTable {
    constructor() { this.data = []; }
    fetchAndRender() {
        fetch('/api/data')
            .then(r => r.json())
            .then(items => { this.data = items; this.render(); }); // 'this' is correct
    }
}

// Arrow functions are WRONG for object methods that need dynamic 'this'
const obj = {
    name: 'test',
    sayHi:   () => console.log(this.name),          // 'this' is window — WRONG
    sayHiOk: function() { console.log(this.name); } // correct
};
```

---

## 14. Anti-Patterns Reference

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Inline `<?php echo ?>` in JS | Unmaintainable, no IDE support, XSS risk | Separate `.js` files + data attributes |
| `var` declarations | Function scope, hoisting surprises, closure bugs in loops | `const` / `let` always |
| `value \|\| default` for falsy 0 | 0 is falsy — silently wrong | `value ?? default` |
| `document.write()` | Overwrites entire page | DOM manipulation methods |
| String concat in HTML | XSS risk | `textContent`, or sanitise before `innerHTML` |
| Events attached in loops | Memory leak, slow | Event delegation |
| `eval()` | Security + performance | `JSON.parse()` for data, never eval |
| Global variables | Collisions, hard to debug | ES modules or IIFE |
| Synchronous XHR | Blocks UI thread | `async/await fetch` |
| Sequential `await` for independent ops | Wastes time | `Promise.all([...])` |
| Not handling `unhandledrejection` | Silent failures in production | Global handler |
| Bare `.catch(console.error)` | Swallows error, no user feedback | Typed error handler |

---

## 15. Symbol for Collision-Free Keys

Symbol keys are invisible to `for...in`, `Object.keys()`, and `JSON.stringify()`. Use them when attaching metadata to objects you do not own.

```javascript
const PROCESSED = Symbol('processed');
function process(record) {
    if (record[PROCESSED]) return;  // idempotent — safe to call multiple times
    record[PROCESSED] = true;
}
```

---

## Quick Reference

| Need | Pattern |
|---|---|
| Pass PHP data to JS | Single `data-config` attribute + `JSON.parse` |
| Private class state | `WeakMap` keyed on `this` |
| Validate object writes | `Proxy` with `set` trap + `Reflect.set` |
| Multiple parallel fetches | `Promise.all([...])` |
| Batch ops — need all outcomes | `Promise.allSettled([...])` |

---
> **Note:** Content trimmed to 500-line standard. Move overflow content to `references/` for on-demand loading.
