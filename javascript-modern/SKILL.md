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

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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

- Use the `references/` directory for deep detail after reading the core workflow below.
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

## Additional Guidance

Extended guidance for `javascript-modern` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Async/Await — The Right Patterns`
- `3. Production-Grade Fetch Wrapper`
- `4. Destructuring — Beyond the Basics`
- `5. Optional Chaining and Nullish Coalescing`
- `6. Generators for Pagination / Lazy Data`
- `7. WeakMap for Private Data and DOM Metadata`
- `8. Proxy for Validation and Reactivity`
- `9. Error Handling Strategy`
- `10. Event Delegation (Performance Pattern)`
- `11. Debounce and Throttle`
- `12. LocalStorage with Expiry`
- `13. `const` / `let` and Arrow Function `this``
- Additional deep-dive sections continue in the reference file.
