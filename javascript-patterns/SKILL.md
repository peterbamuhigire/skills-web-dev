---
name: javascript-patterns
description: 'JavaScript design patterns for SaaS apps: Module, Observer, Factory,
  Strategy, Command, Mediator, Repository, and State patterns with practical web app
  examples. Use when structuring JavaScript code, implementing event-driven UI, decoupling...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# JavaScript Design Patterns for PHP+SaaS Frontend
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- JavaScript design patterns for SaaS apps: Module, Observer, Factory, Strategy, Command, Mediator, Repository, and State patterns with practical web app examples. Use when structuring JavaScript code, implementing event-driven UI, decoupling...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `javascript-patterns` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Pattern usage decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering Module / Observer / Factory / Strategy / Mediator pattern picks | `docs/web/js-patterns-adr.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
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

**Rule:** Never leak private functions. Return only what callers need. Replace the IIFE with `export` when bundling.

---

## Additional Guidance

Extended guidance for `javascript-patterns` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Pattern 2 — Observer / EventBus (PubSub)`
- `Pattern 3 — Factory`
- `Pattern 4 — Strategy`
- `Pattern 5 — Command (+ Undo/Redo)`
- `Pattern 6 — Repository (Frontend Data Layer)`
- `Pattern 7 — Mediator`
- `Pattern 8 — State Machine`
- `Pattern 9 — Singleton (Careful Use)`
- `Pattern 10 — Decorator`
- `Pattern 11 — Async Performance Patterns`
- `Pattern Selection Guide`
- `Anti-Patterns to Avoid`
- Additional deep-dive sections continue in the reference file.