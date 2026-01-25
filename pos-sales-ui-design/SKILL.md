---
name: pos-sales-ui-design
description: Design POS, checkout, and sales entry web UIs that are simple, accessible, and fast for all ages while integrating all backend actions strictly through APIs. Use for creating or reviewing UI patterns, layouts, components, and workflows for web-based sales recording systems.
---

# POS & Sales Entry UI Design Skill

## Overview
Design sales entry screens that an 8-year-old and an 80-year-old can both use confidently. Prioritize clarity, large touch targets, visible context, and fast workflows. Ensure all backend activity is API-driven (no direct DB assumptions).

## Summary
- Build POS and sales entry screens with a strict 3-level hierarchy and large touch targets.
- Use progressive disclosure and fast feedback for customer, invoice, and cart workflows.
- Treat all backend actions as API-driven (search, pricing, tax, payment, printing).
- Apply invoice/receipt output standards for 80mm and A4 formats with consistent totals and payment history.

## Quick Reference
Use this skill when you need to:
- Design POS, checkout, or sales entry screens for any web-based sales system.
- Create component specs, layout patterns, or interaction rules for sales UIs.
- Review existing sales UIs for accessibility and usability.
- Define API-first UI workflows (search, add to cart, payment, save).

## Core Workflow
1. Identify the sales flow type: POS (walk-in) vs sales encoding (invoice-first).
2. Define persistent context (branch, store, sales point, price list, date/time).
3. Map the 3-step workflow (Customer -> Invoice/Details -> Action/Payment).
4. Choose components and layout patterns appropriate to device size.
5. Define interaction rules (search debounce, confirmations, optimistic UI).
6. Enforce accessibility and touch target standards.
7. Bind all actions to API endpoints with robust error handling.

## Core Instructions
### 1) Use the 8-to-80 philosophy
- Prefer clarity over cleverness.
- Keep important context always visible.
- Make errors recoverable (undo, cancel, confirmations).
- Use familiar labels and explicit actions.

### 2) Enforce persistent context
Always show where/when/who/what constraints:
- Sales point name, branch, store, price list.
- Date/time and invoice number.
- Selected customer and agent.

### 3) Apply a 3-level visual hierarchy
- Level 1: Context header (largest, always visible).
- Level 2: Current transaction (selected customer, invoice).
- Level 3: Actions/details (inputs, buttons, hints).

### 4) Use large touch targets
- Minimum 48x48px for all interactive elements.
- Inputs 42-48px height; primary action buttons 60px height.

### 5) Progressive disclosure
- Start with a simple search or selection.
- Reveal details only after selection.
- Lock downstream steps until prerequisites are complete.

### 6) Immediate visual feedback
- Show feedback within 100ms (loading, success, error).
- Use icons + text (never color alone).

## API-First Rule (Required)
All backend activity MUST go through APIs.
- Use API calls for search, selection, cart updates, pricing, tax, and payment.
- Never assume direct database access or server-side session state.
- Keep UI optimistic where possible and reconcile with API responses.
- Standardize error handling for network, validation, and business logic errors.

## Key Patterns
### Component Essentials
- Context Header (sales point, branch, store, price list, date/time).
- Step Label (STEP 1/2/3 badges with clear action text).
- Large Search Input with debounced API search (300ms).
- Dropdown Results with large list items.
- Selected Item Card with change/reset action.
- Large Primary Action Button (Start/Pay/Save).
- Prominent Alerts for date windows or constraints.

### Layout Patterns
- Header-Content-Footer structure.
- 3-column step grid on desktop; stacked on mobile.
- Use consistent spacing scale based on 4px increments.

### Interaction Rules
- Debounce search (300ms) to reduce API load.
- Confirm destructive changes (change customer, clear cart).
- Show keyboard shortcuts for power users (F2/F3/F9).
- Use optimistic UI updates with rollback on failure.

## Accessibility Checklist
- WCAG 2.1 AA contrast minimums.
- Visible focus indicators for all controls.
- Labels always visible (do not rely on placeholders).
- Support keyboard navigation for all interactions.
- Never rely on color alone to convey meaning.

## Common Pitfalls
- Hiding essential context (branch/store/prices) below the fold.
- Using small buttons or dense tables that are not touch-friendly.
- Skipping confirmation on destructive actions.
- Triggering API searches on every keystroke without debounce.
- Coupling UI to direct database access instead of APIs.

## Examples
### Debounced customer search (API-first)
Use API calls only and debounce input:

```javascript
let searchTimeout;
customerInput.addEventListener("input", (e) => {
	clearTimeout(searchTimeout);
	const query = e.target.value.trim();
	if (query.length < 2) return hideResults();
	searchTimeout = setTimeout(() => searchCustomersApi(query), 300);
});
```

### Confirmation before clearing work
```javascript
if (cart.length > 0) {
	showConfirm("Change customer? This will clear your cart.")
		.then((confirmed) => confirmed && resetCustomer());
}
```

## Reference Files
- See references/universal-sales-ui-design.md for detailed component anatomy, design tokens, color palette, and layout examples.
