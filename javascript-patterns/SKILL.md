---
name: javascript-patterns
description: "JavaScript design patterns for SaaS apps: Module, Observer, Factory, Strategy, Command, Mediator, Repository, and State patterns with practical web app examples. Use when structuring JavaScript code, implementing event-driven UI, decoupling components, managing application state, or applying SOLID principles to frontend code."
---

# JavaScript Design Patterns for PHP+SaaS Frontend

Production-grade patterns for structuring JavaScript in PHP-backed SaaS applications.

**Core principle:** Every feature is a module. Components communicate through events, not
direct references. Data access lives in repositories, not scattered `fetch` calls.

✅ Vanilla JS ✅ PHP SaaS ✅ ES2020+ ✅ No framework | ❌ React/Vue ❌ Node.js server-side

---

## Pattern 1 — Module (IIFE + Closure)

Each feature = one module. Private state lives in the closure; only the public API is exposed.

```javascript
// assets/js/modules/invoice-form.js
const InvoiceForm = (() => {
    // Private
    let lineItems = [];

    function calculateTotals() {
        const subtotal = lineItems.reduce((sum, i) => sum + i.qty * i.price, 0);
        const tax = subtotal * 0.16;
        return { subtotal, tax, total: subtotal + tax };
    }

    function updateUI(totals) {
        document.getElementById('subtotal').textContent = formatCurrency(totals.subtotal);
        document.getElementById('tax').textContent    = formatCurrency(totals.tax);
        document.getElementById('total').textContent  = formatCurrency(totals.total);
    }

    // Public API
    return {
        addItem(item)    { lineItems.push(item); updateUI(calculateTotals()); },
        removeItem(idx)  { lineItems.splice(idx, 1); updateUI(calculateTotals()); },
        getItems()       { return [...lineItems]; } // copy, not reference
    };
})();
```

**Rule:** Never leak private functions. Return only what callers need.
**ES module variant:** Replace the IIFE with `export` when bundling with Vite/esbuild.

---

## Pattern 2 — Observer / EventBus (PubSub)

Decouples UI components — no direct references between modules.

```javascript
// assets/js/core/event-bus.js
const EventBus = (() => {
    const subscribers = {};

    return {
        on(event, callback) {
            (subscribers[event] ??= []).push(callback);
            return () => this.off(event, callback); // returns unsubscribe fn
        },
        off(event, callback) {
            subscribers[event] = subscribers[event]?.filter(cb => cb !== callback);
        },
        emit(event, data) {
            subscribers[event]?.forEach(cb => {
                try { cb(data); }
                catch (e) { console.error(`EventBus [${event}]:`, e); }
            });
        }
    };
})();

// Multiple components react to one event — zero coupling
EventBus.on('cart:updated', ({ items, total }) => updateCartBadge(items.length));
EventBus.on('cart:updated', ({ total })        => updateOrderSummary(total));
EventBus.emit('cart:updated', { items, total });
```

**Memory leak prevention:** Store the unsubscribe function and call it on component teardown.

```javascript
const unsub = EventBus.on('user:loggedOut', cleanup);
// Later: unsub();
```

**Named event conventions for SaaS:**
`entity:action` — `invoice:saved`, `customer:deleted`, `payment:failed`

---

## Pattern 3 — Factory

Create objects without specifying exact class. Centralises construction logic.

```javascript
// assets/js/factories/modal-factory.js
const ModalFactory = {
    create(type, config) {
        const types = {
            confirm : ConfirmModal,
            form    : FormModal,
            alert   : AlertModal,
            image   : ImageModal,
        };
        const ModalClass = types[type];
        if (!ModalClass) throw new Error(`Unknown modal type: ${type}`);
        return new ModalClass(config);
    }
};

// Usage — caller never imports individual modal classes
const modal = ModalFactory.create('confirm', {
    title     : 'Delete Record',
    message   : 'This cannot be undone.',
    onConfirm : () => deleteRecord(id),
});
modal.show();
```

**SaaS uses:** modal factory, chart factory (bar/line/pie), export handler (CSV/PDF/Excel),
notification factory (toast/banner/inline).

---

## Pattern 4 — Strategy

Swap algorithms at runtime without if/else chains.

```javascript
// Validation strategies (composable, testable)
const validators = {
    required  : v => v.trim() !== ''                          || 'This field is required',
    email     : v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)    || 'Invalid email address',
    minLength : n => v => v.length >= n                        || `Minimum ${n} characters`,
    numeric   : v => !isNaN(v)                                 || 'Must be a number',
    positive  : v => Number(v) > 0                             || 'Must be greater than zero',
};

class FormValidator {
    #rules = new Map();

    addRule(field, ...strategies) {
        this.#rules.set(field, strategies);
        return this; // fluent
    }

    validate(formData) {
        const errors = {};
        for (const [field, strategies] of this.#rules) {
            for (const strategy of strategies) {
                const result = strategy(formData[field] ?? '');
                if (result !== true) { errors[field] = result; break; }
            }
        }
        return errors; // empty = valid
    }
}

// Usage
const validator = new FormValidator()
    .addRule('email',    validators.required, validators.email)
    .addRule('password', validators.required, validators.minLength(8))
    .addRule('amount',   validators.required, validators.numeric, validators.positive);

const errors = validator.validate(Object.fromEntries(new FormData(form)));
if (Object.keys(errors).length === 0) submitForm();
```

**Other SaaS uses:** export format strategies (CSV/PDF/JSON), sort strategies,
payment gateway strategies, chart rendering strategies.

---

## Pattern 5 — Command (+ Undo/Redo)

Encapsulate operations as objects. Enables undo/redo and audit logging.

```javascript
class CommandHistory {
    #history = [];
    #future  = [];

    execute(command) {
        command.execute();
        this.#history.push(command);
        this.#future = []; // clear redo stack on new action
        EventBus.emit('command:executed', { name: command.constructor.name });
    }

    undo() {
        const cmd = this.#history.pop();
        if (cmd) { cmd.undo(); this.#future.push(cmd); }
    }

    redo() {
        const cmd = this.#future.pop();
        if (cmd) { cmd.execute(); this.#history.push(cmd); }
    }

    get canUndo() { return this.#history.length > 0; }
    get canRedo() { return this.#future.length > 0; }
}

// A command implementation
class AddLineItemCommand {
    constructor(invoice, item) { this.invoice = invoice; this.item = item; }
    execute() { this.invoice.addItem(this.item); }
    undo()    { this.invoice.removeLastItem(); }
}

// Usage
const history = new CommandHistory();
history.execute(new AddLineItemCommand(invoice, { sku: 'SVC-01', qty: 2, price: 500 }));
// Ctrl+Z
document.addEventListener('keydown', e => {
    if (e.ctrlKey && e.key === 'z') history.undo();
    if (e.ctrlKey && e.key === 'y') history.redo();
});
```

---

## Pattern 6 — Repository (Frontend Data Layer)

Separates data fetching from UI logic. AJAX calls are swappable and testable.

```javascript
// assets/js/repositories/customer-repository.js
const CustomerRepository = (() => {
    const cache = new Map();

    async function apiRequest(url, options = {}) {
        const res = await fetch(url, {
            headers: { 'Content-Type': 'application/json',
                        'X-CSRF-Token': document.querySelector('meta[name=csrf-token]')?.content },
            ...options
        });
        if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
        return res.json();
    }

    return {
        async findAll(params = {}) {
            const query = new URLSearchParams(params).toString();
            const key   = `all:${query}`;
            if (cache.has(key)) return cache.get(key);
            const data = await apiRequest(`/api/customers?${query}`);
            cache.set(key, data);
            return data;
        },

        async findById(id) {
            if (cache.has(id)) return cache.get(id);
            const data = await apiRequest(`/api/customers/${id}`);
            cache.set(id, data);
            return data;
        },

        async save(customer) {
            const method = customer.id ? 'PUT' : 'POST';
            const url    = customer.id ? `/api/customers/${customer.id}` : '/api/customers';
            const data   = await apiRequest(url, { method, body: JSON.stringify(customer) });
            cache.clear(); // invalidate on mutation
            EventBus.emit('customer:saved', data);
            return data;
        },

        async delete(id) {
            await apiRequest(`/api/customers/${id}`, { method: 'DELETE' });
            cache.delete(id);
            cache.forEach((_, k) => { if (k.startsWith('all:')) cache.delete(k); });
            EventBus.emit('customer:deleted', { id });
        }
    };
})();
```

**Rule:** UI modules call the repository. They never call `fetch` directly.
**Testing:** Swap the repository with a mock that returns fixture data.

---

## Pattern 7 — Mediator

Central coordinator for complex component interactions. Prevents spaghetti event wiring.

```javascript
// Page-level mediator — coordinates all components on a dashboard
const DashboardMediator = (() => {
    const components = {};

    return {
        register(name, component) {
            components[name] = component;
        },

        notify(sender, event, data) {
            switch (`${sender}:${event}`) {
                case 'dateFilter:changed':
                    components.chart?.update(data.range);
                    components.table?.reload(data.range);
                    components.summary?.refresh(data.range);
                    break;
                case 'table:rowSelected':
                    components.detailPanel?.load(data.id);
                    break;
                case 'detailPanel:saved':
                    components.table?.reload();
                    components.summary?.refresh();
                    break;
            }
        }
    };
})();

// Component usage
DashboardMediator.register('dateFilter', DateFilterComponent);
DashboardMediator.register('chart', ChartComponent);

// Inside DateFilterComponent:
// DashboardMediator.notify('dateFilter', 'changed', { range: { from, to } });
```

**Rule:** Use Mediator when 3+ components need to react to one action.
Use EventBus when the sender should not know its audience.

---

## Pattern 8 — State Machine

Replace boolean flag spaghetti with explicit, documented states.

```javascript
const FormStates = { IDLE: 'idle', VALIDATING: 'validating',
                     SUBMITTING: 'submitting', SUCCESS: 'success', ERROR: 'error' };

const transitions = {
    [FormStates.IDLE]       : { submit: FormStates.VALIDATING },
    [FormStates.VALIDATING] : { valid: FormStates.SUBMITTING, invalid: FormStates.ERROR },
    [FormStates.SUBMITTING] : { success: FormStates.SUCCESS,  failure: FormStates.ERROR },
    [FormStates.ERROR]      : { reset: FormStates.IDLE },
    [FormStates.SUCCESS]    : { reset: FormStates.IDLE },
};

class FormStateMachine {
    #state = FormStates.IDLE;

    get state() { return this.#state; }

    transition(event) {
        const next = transitions[this.#state]?.[event];
        if (!next) throw new Error(`Invalid: ${event} from ${this.#state}`);
        this.#state = next;
        this.#render();
        EventBus.emit('form:stateChanged', { state: this.#state });
        return this;
    }

    #render() {
        const is = s => this.#state === s;
        submitBtn.disabled   = !is(FormStates.IDLE) && !is(FormStates.ERROR);
        spinner.hidden       = !is(FormStates.SUBMITTING);
        errorMsg.hidden      = !is(FormStates.ERROR);
        successMsg.hidden    = !is(FormStates.SUCCESS);
    }
}

// Usage
const fsm = new FormStateMachine();
form.addEventListener('submit', async e => {
    e.preventDefault();
    fsm.transition('submit');
    const errors = validator.validate(Object.fromEntries(new FormData(form)));
    if (Object.keys(errors).length) { fsm.transition('invalid'); return; }
    fsm.transition('valid');
    try {
        await CustomerRepository.save(formData);
        fsm.transition('success');
    } catch { fsm.transition('failure'); }
});
```

---

## Pattern 9 — Singleton (Careful Use)

For truly global shared services. Use sparingly — one per genuine global concern.

```javascript
class NotificationManager {
    static #instance = null;
    static getInstance() { return (this.#instance ??= new NotificationManager()); }

    #queue = [];

    show(message, type = 'info', duration = 4000) {
        const toast = this.#createToast(message, type);
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), duration);
    }

    #createToast(message, type) {
        const el = document.createElement('div');
        el.className = `toast toast--${type}`;
        el.textContent = message;
        return el;
    }
}

const notifications = NotificationManager.getInstance();
// Use across all modules: notifications.show('Saved!', 'success');
```

**Acceptable Singletons:** notification manager, app config, CSRF token provider.
**Avoid Singleton for:** repositories, validators, form modules — those should be instances.

---

## Pattern 10 — Decorator

Extend behaviour without subclassing. Add logging, retry, caching to any function.
Source: *Decoding* ch3 Decorator; *Mastering* ch8 metaprogramming.

```javascript
// Add timing + logging to any async function
function withLogging(fn, label) {
    return async function(...args) {
        console.time(label);
        try {
            return await fn.apply(this, args);
        } finally {
            console.timeEnd(label);
        }
    };
}

// Add automatic retry with exponential back-off
function withRetry(fn, maxAttempts = 3, baseDelay = 1000) {
    return async function(...args) {
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try { return await fn.apply(this, args); }
            catch (e) {
                if (attempt === maxAttempts) throw e;
                await new Promise(r => setTimeout(r, baseDelay * attempt));
            }
        }
    };
}

// Add response caching to any repository method
function withCache(fn, ttlMs = 30_000) {
    const cache = new Map();
    return async function(...args) {
        const key = JSON.stringify(args);
        const hit = cache.get(key);
        if (hit && Date.now() - hit.ts < ttlMs) return hit.data;
        const data = await fn.apply(this, args);
        cache.set(key, { data, ts: Date.now() });
        return data;
    };
}

// Compose decorators
CustomerRepository.findAll = withLogging(
    withRetry(
        withCache(CustomerRepository.findAll.bind(CustomerRepository))
    ),
    'CustomerRepository.findAll'
);
```

---

## Pattern 11 — Async Performance Patterns

Source: *Decoding* ch5 asynchronous performance design patterns.

```javascript
// Debounce: fire once after user stops typing
function debounce(fn, delay = 300) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// Throttle: fire at most once per interval
function throttle(fn, interval = 200) {
    let lastCall = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastCall >= interval) { lastCall = now; fn.apply(this, args); }
    };
}

// Batch parallel API calls (avoids sequential waterfall)
async function batchFetch(ids, fetcher, batchSize = 5) {
    const results = [];
    for (let i = 0; i < ids.length; i += batchSize) {
        const batch = await Promise.all(ids.slice(i, i + batchSize).map(fetcher));
        results.push(...batch);
    }
    return results;
}

// Usage
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', debounce(async e => {
    const results = await CustomerRepository.findAll({ q: e.target.value });
    renderResults(results);
}, 350));
```

---

## Pattern Selection Guide

| Scenario | Pattern |
|---|---|
| Organising feature code, private state | Module |
| Components react to shared events | Observer / EventBus |
| Create different object types without if/else | Factory |
| Swappable algorithms: sort, validate, export | Strategy |
| Undo/redo, audit trail | Command |
| All AJAX and data access | Repository |
| 3+ components coordinate on one action | Mediator |
| Form/wizard multi-step flow, submit states | State Machine |
| Global shared service (one instance only) | Singleton |
| Add logging/retry/cache to any function | Decorator |
| Search input, resize, scroll handlers | Debounce/Throttle |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|---|---|
| `document.getElementById` scattered across modules | Repository or Module pattern |
| `if (isLoading) else if (isError) else if (isSuccess)` | State Machine |
| `window.someData` passed between scripts | EventBus or Module API |
| `fetch()` called directly inside click handlers | Repository pattern |
| One god object doing everything | Mediator + separate Modules |
| Unbounded `on()` subscriptions | Store and call unsubscribe functions |

---

## File Organisation Convention

```
assets/js/
├── core/
│   ├── event-bus.js        # EventBus singleton
│   └── command-history.js  # CommandHistory
├── modules/
│   ├── invoice-form.js     # Module pattern per feature
│   └── customer-list.js
├── repositories/
│   ├── customer-repository.js
│   └── invoice-repository.js
├── factories/
│   └── modal-factory.js
└── pages/
    └── dashboard.js        # Page mediator + bootstrap
```

Each file is a self-contained module. Pages wire them together through the Mediator.
