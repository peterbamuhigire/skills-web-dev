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
- Use attention-grabber focus cues, such as making the field glow and bounce at key milestones (e.g., invoice number, product search) to guide new staff.

## Quick Reference
Use this skill when you need to:
- Design POS, checkout, or sales entry screens for any web-based sales system.
- Create component specs, layout patterns, or interaction rules for sales UIs.
- Review existing sales UIs for accessibility and usability.
- Define API-first UI workflows (search, add to cart, payment, save).
- Standardize restaurant POS UI to the approved layout and workflow.

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
- Minimum 56x56px for all interactive elements.
- Inputs 48-56px height; primary action buttons 60px height.

### 5) Progressive disclosure
- Start with a simple search or selection.
- Reveal details only after selection.
- Lock downstream steps until prerequisites are complete.

### 6) Immediate visual feedback
- Show feedback within 100ms (loading, success, error).
- Use icons + text (never color alone).

### 7) Attention-grabber on milestone focus (Required)
- When focus moves to key milestones (invoice number, product search, payment input), briefly animate the field.
- Use a gentle glow + micro-bounce (1–2 seconds) to guide new staff without disrupting workflow.
- Trigger on programmatic focus changes only (avoid constant animation on manual typing).
- Keep effects subtle, accessible, and consistent with brand colors.

## Standard POS UI Baseline (All POS Screens)

These elements are mandatory across all POS screens (retail, pharmacy, restaurant):

- Sticky context header with outlet/server/time/order type
- Search-first layout with auto-focus on load
- Quick access lanes (Recent, Favorites, Popular) where feasible
- Sticky or floating cart panel with dominant Pay CTA
- Large touch targets (>= 56px) and 60px primary actions
- Accessibility and keyboard flow (ARIA labels, focus states, shortcuts)

Use the Restaurant POS standard as the design benchmark for these elements:
- Apply `pos-restaurant-ui-standard` where a full POS overhaul is required
- Borrow the layout and interaction patterns even when the domain is not restaurant

## Restaurant POS Standard (Required)

For restaurant POS screens, apply the standard UI defined in the Restaurant POS redesign plan.

- Use the dedicated skill: `pos-restaurant-ui-standard`
- Canonical plan: docs/plans/restaurant-pos/2026-02-03-restaurant-pos-ui-redesign.md
- Follow the component specs and breakpoints in the plan sections

## API-First Rule (Required)
All backend activity MUST go through APIs.
- Use API calls for search, selection, cart updates, pricing, tax, and payment.
- Never assume direct database access or server-side session state.
- Keep UI optimistic where possible and reconcile with API responses.
- Standardize error handling for network, validation, and business logic errors.

### Invoice Generation Timing (Critical)
**DO NOT** generate invoice headers on page load or context changes.
- Invoice generation should ONLY occur when the user clicks the payment button (PAY/CHARGE/CREDIT).
- Never auto-generate invoices when: selecting a shop, selecting a customer, creating a customer, or adding items to cart.
- This prevents orphaned invoices (empty invoices with 0 0 0 0) when users navigate away without completing a transaction.
- Always check if an invoice exists before payment; generate only if missing.

## Key Patterns
### Component Essentials
- Context Header (sales point, branch, store, price list, date/time).
- Step Label (STEP 1/2/3 badges with clear action text).
- Large Search Input with debounced API search (300ms).
- Dropdown Results with large list items.
- Selected Item Card with change/reset action.
- Large Primary Action Button (Start/Pay/Save).
- Prominent Alerts for date windows or constraints.

### Product Display for Large Inventories (REQUIRED)
**Standard enforced for all POS screens (pharmacy, retail, wholesale - NOT restaurant):**

- **≤ 49 products:** Use card/grid view by default
  - Provide toggle button to switch between card view and table view
  - Save user preference in localStorage
  - Cards are visual, easy to scan for small catalogs

- **> 49 products:** FORCE table view only (no toggle)
  - Use DataTables (https://datatables.net/) for pagination, search, and sorting
  - Display alert: "You have X products. Table view enforced for better performance."
  - Table configuration:
    - Page length: 25 (options: 10, 25, 50, 100, All)
    - Sort by product name (ascending) by default
    - Enable column search in header
    - Make entire row clickable to add product (not just button)
    - Prevent row click when clicking action button (`event.stopPropagation()`)

- **Table columns (standard):**
  - Product Name (40% width)
  - Code/SKU (15%)
  - Price (15%)
  - Stock/Availability (10%) - with color-coded badge
  - Action button (20%) - "Add to Cart" with icon

- **Table UX rules:**
  - Hover effect on rows for visual feedback
  - Cursor pointer on rows
  - Row click adds product (same as clicking Add button)
  - Action button stops event propagation to prevent double-add
  - Stock badge: green (>10), yellow (1-10), red (0)

**Why this matters:**
- Card grids with 100+ products cause scroll fatigue
- Tables are faster to scan with search/filter
- Pharmacies often have 200-500 SKUs
- Table view handles large datasets efficiently

**Restaurant exception:**
- Restaurants keep menus manageable (<50 items typically)
- Visual card view works better for food/drinks
- No need for table view toggle in restaurant POS

### Layout Patterns
- Header-Content-Footer structure.
- 3-column step grid on desktop; stacked on mobile.
- Use consistent spacing scale based on 4px increments.

### Interaction Rules
- Debounce search (300ms) to reduce API load.
- Confirm destructive changes (change customer, clear cart).
- Show keyboard shortcuts for power users (F2/F3/F9).
- Use optimistic UI updates with rollback on failure.
- Apply milestone focus cues after system-driven focus jumps (e.g., distributor -> invoice number; start transaction -> product search).

### Barcode Scanner Support (Required)
- Treat barcode scanners as keyboard input that ends with Enter.
- On Enter, attempt an exact barcode match against product data (`barcode` field).
- If matched, add one unit to cart and clear/refocus the search input.
- Support both grid cards and table rows (use `data-barcode` or row data payloads).
- If no match, show a brief non-blocking warning (SweetAlert2 toast).

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
- **Generating invoices too early** (on page load, shop selection, or customer selection) - this creates orphaned invoices when users navigate away without completing transactions.

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

### Invoice generation on payment only
```javascript
// WRONG: Generating invoice on page load or shop selection
async handleShopSelect(shopId) {
	this.currentShop = shopId;
	await this.generateInvoice(); // ❌ Creates orphaned invoices
}

// CORRECT: Generate invoice only when user clicks pay
async submitPayment() {
	// Only generate invoice if it doesn't exist
	if (!this.invoiceNumber) {
		await this.generateInvoice(); // ✅ Invoice created on payment intent
	}
	// Process payment
	await this.processPayment();
}
```

## Reference Files
- See references/universal-sales-ui-design.md for detailed component anatomy, design tokens, color palette, and layout examples.
