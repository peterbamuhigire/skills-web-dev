---
name: javascript-advanced
description: "Advanced JavaScript internals: closures, prototype chain, OOP with classes, functional programming patterns, memory management, event loop mechanics, and performance optimization. Use when implementing complex JavaScript features, debugging closure bugs, designing class hierarchies, applying functional patterns, or diagnosing performance issues."
---

# JavaScript Advanced Internals

## 1. Closures — The Non-Obvious Parts

A closure is a function paired with a reference to the **lexical environment** in which it was created, stored in the hidden `[[Environment]]` internal slot. Every function creates a closure — not just nested ones. Closures capture **variables**, not values.

### The Classic Loop Bug

```javascript
// BUG: var creates one shared binding across all iterations
for (var i = 1; i <= 3; i++) {
    setTimeout(() => console.log(i), 1000); // prints: 4 4 4
}

// FIX: let creates a new binding per iteration
for (let i = 1; i <= 3; i++) {
    setTimeout(() => console.log(i), 1000); // prints: 1 2 3
}

// Pre-ES2015 fix: IIFE captures value into a new scope variable
for (var i = 1; i <= 3; i++) {
    ((counter) => setTimeout(() => console.log(counter), 1000))(i);
}
```

### Memoization with Closure

```javascript
function memoize(fn) {
    const cache = new Map();
    return function(...args) {
        const key = JSON.stringify(args);
        if (cache.has(key)) return cache.get(key);
        const result = fn.apply(this, args);
        cache.set(key, result);
        return result;
    };
}
```

### Partial Application and Module Pattern

```javascript
function partial(fn, ...presetArgs) {
    return (...laterArgs) => fn(...presetArgs, ...laterArgs);
}
const addTax = partial((rate, amount) => amount * (1 + rate), 0.16);
addTax(100); // 116

// IIFE module — private state via closure
const bank = (function () {
    const accounts = []; // private
    function openAccount(data) { accounts.push(data); }
    function deposit(num, amount) { /* ... */ }
    return { openAccount, deposit };
})();
```

### Stale Closure Fix — AbortController Pattern

```javascript
class DataTable {
    #controller = new AbortController();

    init(btn) {
        const sig = { signal: this.#controller.signal };
        window.addEventListener('resize', this.#onResize, sig);
        btn.addEventListener('click', this.#onClick, sig);
    }

    destroy() { this.#controller.abort(); } // removes ALL listeners at once
}
```

---

## 2. Prototype Chain

- `[[Prototype]]` — internal slot on every object; the actual chain link
- `.prototype` — property on **function objects**; becomes `[[Prototype]]` of instances created with `new`

```javascript
function Car(name) { this.name = name; }
Car.prototype.start = function () { console.log('starting ' + this.name); };
const honda = new Car('honda');
Object.getPrototypeOf(honda) === Car.prototype; // true
Object.getPrototypeOf(Object.prototype);        // null — chain ends here
```

### Object.create() and Null Prototype

```javascript
// Prototype-based inheritance without `new`
const methods = { greet() { return `Hi, ${this.name}`; } };
const user = Object.create(methods);
user.name = 'Alice';

// Null prototype — safe lookup map, immune to prototype pollution
const safeMap = Object.create(null); // no toString, no hasOwnProperty inherited
Object.prototype.isAdmin = true;
safeMap.isAdmin; // undefined — safe

// hasOwnProperty vs in
const obj = { a: 1 };
'toString' in obj;              // true (inherited)
Object.hasOwn(obj, 'toString'); // false (own only — modern, safe API)
```

**`instanceof` can lie** across iframes/vm contexts — different realms have different `Function.prototype`. Use `Array.isArray()` or `Object.prototype.toString.call(val)` for reliable type checks.

---

## 3. ES6 Classes

Classes are **syntactic sugar over prototype chains**. `typeof MyClass === 'function'`. The `extends` keyword sets up two prototype chains: `Student.prototype → Person.prototype` and `Student → Person` (constructor chain).

```javascript
class EventEmitter {
    #listeners = new Map(); // true private — SyntaxError if accessed outside

    on(event, fn) {
        if (!this.#listeners.has(event)) this.#listeners.set(event, []);
        this.#listeners.get(event).push(fn);
        return () => this.off(event, fn); // returns unsubscribe fn
    }
    emit(event, ...args) { this.#listeners.get(event)?.forEach(fn => fn(...args)); }
    off(event, fn) {
        const fns = this.#listeners.get(event);
        if (fns) this.#listeners.set(event, fns.filter(f => f !== fn));
    }
}

// Mixins — multiple inheritance workaround
const Serializable = (Base) => class extends Base {
    toJSON() { return JSON.stringify(this); }
    static fromJSON(json) { return Object.assign(new this(), JSON.parse(json)); }
};
const Validatable = (Base) => class extends Base {
    validate() { return Object.keys(this).every(k => this[k] !== null); }
};

class User extends Serializable(Validatable(EventEmitter)) {
    constructor(name) { super(); this.name = name; }
}
```

---

## 4. `this` Binding — All 4 Rules

| Rule | Trigger | `this` value |
|---|---|---|
| Implicit | `obj.method()` | `obj` |
| Explicit | `.call(ctx)` / `.apply(ctx)` / `.bind(ctx)` | `ctx` |
| `new` | `new Fn()` | Newly created instance |
| Default | bare `fn()` non-strict | `globalThis`; strict: `undefined` |
| Arrow | Any call | Lexical — from enclosing scope |

```javascript
class FormHandler {
    constructor(btn) {
        // WRONG: passes reference — `this` becomes the DOM element
        btn.addEventListener('click', this.handleClick);

        // CORRECT option 1: arrow preserves lexical `this`
        btn.addEventListener('click', () => this.handleClick());

        // CORRECT option 2: bind
        btn.addEventListener('click', this.handleClick.bind(this));
    }
    handleClick() { this.sendRequest(); }
    sendRequest() { console.log('sending...'); }
}

// Method borrowing with explicit binding
function greet(msg) { return `${msg}, ${this.name}`; }
greet.call({ name: 'Alice' }, 'Hello'); // 'Hello, Alice'
```

---

## 5. Event Loop

JavaScript is single-threaded. Long synchronous tasks block the UI entirely.

- **Task queue** (macrotasks): `setTimeout`, `setInterval`, DOM events — one per tick
- **Microtask queue**: Promise callbacks, `queueMicrotask()` — **all** drain before next task

```javascript
console.log('start');
setTimeout(() => console.log('setTimeout'), 0);
Promise.resolve().then(() => console.log('then 1')).then(() => console.log('then 2'));
console.log('end');
// Output: start → end → then 1 → then 2 → setTimeout
```

### Chunked Processing — Avoid Blocking UI

```javascript
async function processInChunks(items, processFn, chunkSize = 100) {
    for (let i = 0; i < items.length; i += chunkSize) {
        items.slice(i, i + chunkSize).forEach(processFn);
        await new Promise(resolve => setTimeout(resolve, 0)); // yield to UI
    }
}
```

Use `requestAnimationFrame` for DOM/animation writes — runs before the browser paints, guaranteeing smooth 60fps. Never use `setTimeout` for animations.

---

## 6. Memory Management

| Leak Source | Fix |
|---|---|
| Forgotten event listeners | `AbortController` (see §1) |
| `setInterval` without clear | Store ID, call `clearInterval` in teardown |
| Detached DOM nodes still referenced | Null references on removal |
| Closure over large data | Set the variable to `null` when done |
| Implicit globals (`result = value`) | `'use strict'` + always declare |

```javascript
// WeakRef — optional reference, does not prevent GC
const cache = new Map();
function getCached(key, factory) {
    const existing = cache.get(key)?.deref();
    if (existing) return existing;
    const value = factory();
    cache.set(key, new WeakRef(value));
    return value;
}
```

**Detecting leaks in Chrome DevTools:** Memory tab → take heap snapshot before and after suspected operation → compare → filter "Objects allocated between snapshots" → look for detached DOM trees.

---

## 7. Functional Programming Patterns

```javascript
// Pure function — no side effects, same input = same output
const addItem = (arr, item) => [...arr, item]; // returns new array

// Compose (right-to-left) and pipe (left-to-right)
const compose = (...fns) => x => fns.reduceRight((v, f) => f(v), x);
const pipe    = (...fns) => x => fns.reduce((v, f) => f(v), x);

const processUsers = pipe(
    users => users.filter(u => u.active),
    users => users.map(u => ({ ...u, displayName: `${u.first} ${u.last}` })),
    users => users.sort((a, b) => a.displayName.localeCompare(b.displayName))
);

// Currying for configuration
const curry = fn => function curried(...args) {
    return args.length >= fn.length
        ? fn(...args)
        : (...more) => curried(...args, ...more);
};
const request = curry((method, base, path, body) =>
    fetch(base + path, { method, body: JSON.stringify(body) }));
const post = request('POST', 'https://api.example.com');
post('/users', { name: 'Alice' });
```

---

## 8. Iterators and Generators

```javascript
// Custom iterable — implement [Symbol.iterator]
class Range {
    constructor(start, end) { this.start = start; this.end = end; }
    [Symbol.iterator]() {
        let cur = this.start, end = this.end;
        return {
            next() { return cur <= end ? { value: cur++, done: false } : { done: true }; },
            [Symbol.iterator]() { return this; }
        };
    }
}
[...new Range(1, 5)]; // [1, 2, 3, 4, 5]

// Generator — cleaner iterator syntax, supports lazy/infinite sequences
function* odds(max) { for (let i = 1; i <= max; i += 2) yield i; }

// Generator as class iterator method
class Student {
    constructor(name, age, courses) { this.name = name; this.age = age; this.courses = courses; }
    *[Symbol.iterator]() {
        for (const key of Object.getOwnPropertyNames(this)) yield `${key} => ${this[key]}`;
    }
}

// Generators can consume values via next(value)
function* accumulator() {
    let total = 0;
    while (true) { const n = yield total; total += n ?? 0; }
}
const acc = accumulator();
acc.next();     // { value: 0, done: false }
acc.next(10);   // { value: 10, done: false }
acc.next(5);    // { value: 15, done: false }
```

---

## 9. Symbol — Practical Uses

```javascript
// Unique keys — no collision risk between libraries
const _id = Symbol('id');
const obj = { [_id]: 42, name: 'visible' };
Object.keys(obj);                  // ['name'] — symbols hidden from enumeration
Object.getOwnPropertySymbols(obj); // [Symbol(id)]

// Symbol.toPrimitive — control type coercion
const money = {
    amount: 100, currency: 'USD',
    [Symbol.toPrimitive](hint) {
        return hint === 'number' ? this.amount : `${this.amount} ${this.currency}`;
    }
};
+money;     // 100
`${money}`; // "100 USD"

// Symbol.toStringTag — custom type tag
class APIResponse {
    get [Symbol.toStringTag]() { return 'APIResponse'; }
}
Object.prototype.toString.call(new APIResponse()); // "[object APIResponse]"

// Symbol.for — shared across modules/realms (global registry)
const key = Symbol.for('app.userId');
Symbol.for('app.userId') === key; // true
Symbol.keyFor(key);               // 'app.userId'
```

---

## 10. Metaprogramming with Proxy and Reflect

```javascript
// Reflect forwards traps correctly — preserves receiver for getters/setters
function createValidator(target, schema) {
    return new Proxy(target, {
        set(obj, prop, value, receiver) {
            const rule = schema[prop];
            if (rule && !rule(value)) throw new TypeError(`Invalid ${prop}: ${value}`);
            return Reflect.set(obj, prop, value, receiver);
        }
    });
}

const user = createValidator({}, {
    age:   v => typeof v === 'number' && v >= 0,
    email: v => typeof v === 'string' && v.includes('@')
});
user.age = 25;     // ok
user.age = 'old';  // TypeError
```

Use `Reflect` over direct object operations: returns booleans instead of throwing, maintains correct `receiver`, and is consistent with all Proxy trap signatures.

---

## 11. Performance Patterns

```javascript
// Avoid layout thrashing — batch reads THEN writes
const heights = elements.map(el => el.offsetHeight);          // all reads
elements.forEach((el, i) => el.style.height = heights[i] * 2 + 'px'); // all writes

// DocumentFragment — single reflow for many DOM insertions
function renderList(items) {
    const frag = document.createDocumentFragment();
    items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item.name;
        frag.appendChild(li);
    });
    document.querySelector('ul').appendChild(frag);
}

// IntersectionObserver — lazy loading (far better than scroll events)
const io = new IntersectionObserver(entries => {
    entries.filter(e => e.isIntersecting).forEach(e => {
        e.target.src = e.target.dataset.src;
        io.unobserve(e.target);
    });
}, { rootMargin: '200px' });
document.querySelectorAll('img[data-src]').forEach(img => io.observe(img));
```

**JIT shape consistency:** V8 compiles hot functions to native code using assumed object shapes. Passing inconsistently shaped objects causes deoptimisation — the engine falls back to slower bytecode. Always create objects with the same property layout.

---

## 12. Scope Internals

**Temporal Dead Zone (TDZ):** `let`, `const`, and `class` are hoisted but stay uninitialized until their declaration executes. Accessing them before that throws `ReferenceError`.

**Non-simple parameter scope:** Functions with default params or rest params have a hidden intermediate scope between the outer scope and the function body. A `var` inside the function body with the same name as a parameter creates a *separate binding*.

```javascript
function example(arr = ['default'], getArr = () => arr) {
    var arr = [1, 2, 3];   // separate binding in function-body scope
    console.log(arr);      // [1, 2, 3]
    console.log(getArr()); // ['default'] — closes over parameter-scope's arr
}
```

---

## 13. Anti-Patterns

| Anti-Pattern | Consequence | Fix |
|---|---|---|
| `var` in loops with closures | All callbacks share one binding | Use `let` |
| Implicit type coercion | `"5" + 3 = "53"`, `[] == false` is `true` | Explicit conversion |
| Mutating function arguments | Caller's data changes silently | Spread/clone first |
| Prototype pollution via `Object.prototype` | Affects every object | `Object.create(null)` for lookup maps |
| Forgetting `new` with constructor functions | `this` binds to global | Use `class` (enforces `new`) |
| Inconsistent object shapes | JIT deoptimisation | Always initialise same properties in constructor |
| Sequential `await` for independent ops | 3× slower than needed | `await Promise.all([a(), b(), c()])` |
| `async` executor function in `new Promise` | Silent unhandled rejection | Never mark executor as `async` |
| Detached event listeners / intervals | Memory leak, zombie behaviour | `AbortController` + explicit `clearInterval` |
