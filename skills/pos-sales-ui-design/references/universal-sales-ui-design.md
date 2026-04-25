# Universal Sales UI Design System (Reference)

Use this reference when you need detailed component anatomy, tokens, and patterns.

## Design Philosophy (8 to 80)

- Clarity over cleverness
- Visibility over minimalism
- Forgiveness over restriction
- Concrete labels over abstract metaphors

Target personas:

- Young child (large, simple, immediate feedback)
- Senior adult (large fonts, high contrast, explicit labels)
- Busy worker (fast workflow, shortcuts, error prevention)

## Visual Hierarchy (3 Levels)

1. Context Header (Level 1)
   - Sales point, branch, store, price list, date/time
   - Display sizes: 2.0rem title, 1.1rem metadata
2. Current Transaction (Level 2)
   - Selected customer, invoice, agent
   - Highlight in success color with bold values
3. Actions and Details (Level 3)
   - Inputs, helper text, secondary info

## Typography Scale

- Hero: 2.5rem (40px)
- Display: 2.0rem (32px)
- H1: 1.5rem (24px)
- H2: 1.4rem (22.4px)
- H3: 1.2rem (19.2px)
- Large: 1.1rem (17.6px)
- Body: 1.0rem (16px)
- Small: 0.9-0.95rem (14.4-15.2px)

Font weights:

- Normal 400
- Semibold 600
- Bold 700

## Color Palette (Semantics)

- Primary (trust blue): #206bc4
- Success (confirmation): #2fb344
- Warning (caution): #f59f00
- Danger (errors): #d63939
- Text primary: #1e293b
- Text secondary: #475569
- Text muted: #64748b
- Border: #cbd5e1
- Background: #f8f9fa

## Component Anatomy (Essentials)

### Context Header

Purpose: persistent location and status.

- Gradient background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)
- Title 2.0rem, metadata 1.1rem, icons 2.2rem
- Include date/time on the right (desktop)

### Step Label

Purpose: guide multi-step workflows.

- Badge: STEP 1/2/3
- Font: 1.2rem, bold
- Icon + label

### Large Search Input

Purpose: customer/product search.

- Height 48px
- Font 1.1rem
- Clear button always visible
- Debounced API search (300ms)

### Dropdown Results

Purpose: display search results.

- Max height 400px
- Item padding 12x16px
- Name 1.1rem, phone 0.9rem
- Hover background #f8f9fa

### Selected Item Card

Purpose: confirm selection.

- Border 3px success
- Value 1.4rem bold
- Change action visible

### Large Action Button

Purpose: primary action (Start, Pay, Save).

- Height 60px
- Font 1.2rem, bold
- Icon 1.5rem

### Prominent Alerts

Purpose: show constraints and warnings.

- Use icons and bold labels
- Alert types: info, warning, danger, success

### Invoice & Receipt Outputs

Purpose: define consistent, printable outputs for receipts and invoices across 80mm and A4 formats.

**Supported formats:**

- 80mm (thermal printer receipts)
- A4 (formal invoice/receipt)

**Document types:**

- Receipt (pre-payment or post-payment customer copy)
- Invoice (formal tax document with payment history)

## Invoice/Receipt Generation System

### Architecture & Data Flow

Controllers route to the correct template based on format and document type. Keep the workflow API-driven and validate all parameters.

```
Controller -> Database Queries -> Template View
```

Recommended controller logic:

1. Authenticate user (session/SSO).
2. Validate parameters (invoice number/id, format).
3. Fetch invoice, items, and payments scoped to franchise/store.
4. Route to the correct template.

### 80mm Thermal Receipt (Receipt/Invoice)

Design goals: narrow paper, compact text, strong alignment, fast print.

**Typography & layout:**

- Font: Courier New, monospace
- Width: 80mm, auto-height
- Padding: 5mm
- Line height: 1.3
- Franchise name: 13pt bold
- Shop name: 11pt bold
- Section titles: 10pt bold
- Body text: 8–9pt
- Item subtext: 7pt

**Structural rules:**

- Use dashed borders for section breaks.
- Use dotted borders between item rows.
- Use double borders around totals.
- Always show invoice number, date/time, customer, and tax ID.

**CSS essentials:**

```css
@page { size: 80mm auto; margin: 0; }
body {
   width: 80mm;
   font-family: 'Courier New', Courier, monospace;
   font-size: 9pt;
   padding: 5mm;
}
.receipt-header { border-bottom: 2px dashed #333; }
.items-table td { border-bottom: 1px dotted #ccc; }
.totals { border-top: 2px solid #333; border-bottom: 2px solid #333; }
```

**Auto-print:**

```javascript
window.onload = function() { window.print(); };
```

### A4 Receipt/Invoice

Design goals: professional appearance, clear table grid, file-ready output.

**Typography & layout:**

- Font: Arial, sans-serif
- Page size: A4
- Container width: 190mm
- Margins: 10mm
- Franchise name: 14pt bold
- Shop name: 10pt semibold
- Table headers: 8pt bold
- Table body: 8pt

**CSS essentials:**

```css
@page { size: A4; margin: 10mm; }
.container { width: 190mm; margin: 0 auto; }
.items-table th, .items-table td {
   border: 1px solid #000;
   padding: 2px 4px;
}
.items-table th { background-color: #f0f0f0; }
```

### PDF Export (Styled)

When generating PDF via TCPDF or similar, use a branded header, alternating row colors, and semantic total colors.

**Color scheme (example):**

- Header background: #667eea
- Invoice number box: #f0f8ff
- Date box: #fff8dc
- Table header: #667eea
- Alternating rows: #f8f9fa / #ffffff
- Total row: #28a745
- Balance due: #dc3545

### Data Model (Reference)

**Invoice:**

- invoice_number, invoice_date, total_amount
- customer name + phone
- franchise name + tax ID
- shop/DPC name + address + phone

**Line items:**

- name, product_code
- unit_price, total_quantity, total_price
- bv_points/total_bv (if applicable)

**Payments:**

- payment_date, payment_method, amount, reference_number

### Logic Patterns

**Customer name fallback:**

- If customer name missing, fallback to distributor ID/name.

**Balance calculation:**

- Sum all payments, subtract from total.
- If balance <= 0.01, show PAID IN FULL (or Balance: NIL).

**No payments:**

- Show a clear “NO PAYMENT” block instead of an empty table.

### Security & Validation

- Require authentication for all print/export controllers.
- Scope queries by franchise/store.
- Validate invoice numbers/IDs and format parameters.
- Escape all output (e.g., htmlspecialchars).

## Layout Patterns

- Header-Content-Footer layout
- Desktop 3-column steps (33/42/25)
- Tablet 2 columns, mobile stacked
- Spacing scale in 4px increments

## Interaction Rules

- Debounce search calls (300ms)
- Confirm destructive actions
- Optimistic UI updates with API rollback
- Keyboard shortcuts (F2 search customer, F3 search product, F9 pay)

## Accessibility Standards

- WCAG 2.1 AA contrast minimum
- Focus outlines for all interactive elements
- Touch targets min 48x48px
- Labels visible and explicit

## Design Tokens (Copy/Paste)

```css
:root {
  --font-size-display: 2rem;
  --font-size-h2: 1.4rem;
  --font-size-large: 1.1rem;
  --font-size-body: 1rem;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --color-primary: #206bc4;
  --color-success: #2fb344;
  --color-warning: #f59f00;
  --color-danger: #d63939;
  --color-text-primary: #1e293b;
  --color-text-muted: #64748b;
  --color-border: #cbd5e1;
  --color-bg-light: #f8f9fa;

  --input-height-lg: 48px;
  --button-height-xl: 60px;
  --border-width-thick: 3px;
  --border-radius-lg: 10px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --gradient-header: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}
```
