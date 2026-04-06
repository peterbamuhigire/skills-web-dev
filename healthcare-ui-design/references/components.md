# Healthcare UI Component Library

## Component Design Principles

1. **States matter.** Every component needs: default, hover, focus, active, disabled, loading, error, success.
2. **Accessible by default.** Every component ships with ARIA labels, keyboard support, focus rings.
3. **Context-aware sizing.** Components come in clinical (dense) and patient-facing (spacious) variants.
4. **Never color alone.** Every status component uses color + icon + text.

---

## Buttons

### Variants

```css
/* Primary — main action on screen */
.btn-primary {
  background: #2563EB;
  color: #FFFFFF;
  height: 48px;           /* 56px for aging/accessibility */
  padding: 0 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  min-width: 120px;
}

/* Secondary — alternative action */
.btn-secondary {
  background: #FFFFFF;
  color: #2563EB;
  border: 2px solid #2563EB;
}

/* Danger — destructive clinical action */
.btn-danger {
  background: #DC2626;
  color: #FFFFFF;
  /* Use only for: discontinue medication, delete record, emergency stop */
}

/* Ghost — tertiary action */
.btn-ghost {
  background: transparent;
  color: #374151;
  border: 1px solid #E5E7EB;
}
```

### Button Rules

- Full-width on mobile for primary actions
- Sentence case labels: "Book appointment" not "BOOK APPOINTMENT"
- Loading state: spinner replaces label, button disabled
- Never two danger buttons side by side
- Confirmation: danger actions require a confirmation dialog showing specifics

### Clinical Action Buttons

```
[Mark Taken]    — green fill (positive action, medication)
[Skip Dose]     — ghost (neutral)
[Discontinue]   — danger (irreversible)
[Sign Order]    — primary (commit action)
[Review]        — secondary (precedes Sign)
```

---

## Form Inputs

### Text Input

```css
.input {
  height: 48px;              /* 40px desktop, 56px aging */
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  padding: 0 16px;
  font-size: 16px;           /* minimum for patient-facing */
  color: #111827;
}
.input:focus {
  border-color: #2563EB;
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);   /* focus ring */
}
.input.error {
  border-color: #DC2626;
  background: #FEF2F2;
}
```

### Label Rules

- Always above input, never placeholder-as-label
- Required fields: asterisk (*) + "Required" text in small label (not red alone)
- Error message below input: specific ("Enter a valid date of birth") not generic ("Invalid")
- Success state: green tick + "Saved" for clinical forms with autosave

### Clinical-Specific Inputs

**Vitals Entry:** Large numeric input, 28px+ digits, previous reading shown for comparison, auto-flag out-of-range values inline.

**Medication Search:** Autocomplete with generic + brand names; interaction warning appears as user types.

**Date of Birth Picker:** Three separate fields (DD / MM / YYYY) — not a calendar date picker. Patients with motor impairments cannot click tiny calendar cells.

**Pain Scale (0–10):** Slider control, not typed input. Visual faces/emoji scale optional for patient-facing.

**Symptom Checklist:** Large checkboxes (48×48px touch area), symptom names in 16px+, grouped by body system.

---

## Cards

### Patient Card (Clinical List)

```
┌──────────────────────────────────────────┐
│ ●  James Smith           Room 4A         │  ← colored dot = acuity
│    55yr M  |  MRN: 001234               │
│    BP: 140/90 ⚠  |  Last seen: 1h ago   │
│    ⚠ Allergy: Penicillin                │
│                        [View Record]    │
└──────────────────────────────────────────┘
```

- Acuity color: red = urgent, amber = caution, green = stable
- Touch area: entire card (not just the button)
- Hover state (desktop): subtle shadow lift, cursor pointer
- Selected state: left border `4px solid #2563EB`

### Medication Card (Patient Mobile)

```
┌──────────────────────────────────────────┐
│ 💊 Metformin 500mg                        │
│    Twice daily — with meals              │
│    Next dose: 2 hours                    │
│                                          │
│    [✓ Mark Taken]  [Skip]  [Snooze]      │
└──────────────────────────────────────────┘
```

### Health Metric Card (Dashboard)

```
┌──────────────────────┐
│ Blood Pressure       │
│                      │
│   140 / 90           │  ← large, readable
│   mmHg               │
│                      │
│ ⚠ Above target range │  ← amber + icon + text
│ Target: <130/80      │
│                      │
│ ↑ from 135/85        │  ← trend arrow + prev value
└──────────────────────┘
```

---

## Alert & Notification Components

### Clinical Alert Banner (Inline)

```
┌─ ⛔ CRITICAL ──────────────────────────────────────────┐
│  Potassium 6.8 mEq/L — James Smith (Room 4A)          │
│  Reference range: 3.5–5.0  |  Received: 2 mins ago   │
│  [Review Now]  [Acknowledge]                          │
└───────────────────────────────────────────────────────┘
```

- Critical: red border-left, red icon, full-width, cannot be scrolled past without acknowledging
- Warning: amber
- Info: blue
- Never auto-dismiss critical alerts

### Toast Notification (Non-Critical)

```
✓  Appointment confirmed for 15 Jan 2:30pm     [Dismiss]
```

- Position: top-right desktop, bottom mobile
- Auto-dismiss: 4–5 seconds (success), persistent (errors)
- Stacking: max 3 visible, queue the rest

### Allergy Banner (Persistent)

```
⚠ ALLERGIES: Penicillin  |  NSAIDs  |  Latex
```

- Amber background (#FEF3C7), dark text (#92400E)
- Always visible on any prescribing or medication screen
- Never dismissible during clinical workflow

---

## Navigation Components

### Tab Bar (Mobile / Tablet Portrait)

```
[🏠 Home] [📅 Appts] [💬 Messages] [📋 Records] [👤 Profile]
```

- Active: filled icon + colored label
- Inactive: outline icon + grey label
- Badge: red dot with number for unread/urgent items
- Minimum tap area: 48px height per tab

### Sidebar (Desktop / Tablet Landscape)

```
┌─────────────────────┐
│ ≡  MediSoft         │  ← logo + collapse toggle
│                     │
│ 👥 Patients    ⌘1   │
│ 📅 Schedule    ⌘2   │
│ 📋 Orders      ⌘3   │
│ 🧪 Results     ⌘4   │
│ 💬 Messages  3 ⌘5   │  ← badge count
│ 📊 Reports     ⌘6   │
│                     │
│ ─────────────────── │
│ ⚙  Settings        │
│ ?  Help             │
│ Dr Smith            │  ← current user
└─────────────────────┘
```

### Breadcrumb (Desktop)

```
Patients > James Smith > Medications > Metformin
```

- Each segment clickable
- Current page: non-clickable, slightly muted
- Max depth: 4 levels before collapsing middle: `Patients > ... > Metformin`

---

## Data Tables (Clinical Lists)

```css
/* Table structure for clinical density */
.clinical-table th {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6B7280;
  padding: 12px 16px;
  border-bottom: 2px solid #E5E7EB;
}
.clinical-table td {
  font-size: 14px;
  padding: 12px 16px;
  border-bottom: 1px solid #F3F4F6;
}
.clinical-table tr:hover {
  background: #F9FAFB;
}
.clinical-table tr.critical {
  background: #FEF2F2;
  border-left: 4px solid #EF4444;
}
```

- Minimum row height: 48px (touch), 40px (mouse-only)
- Sortable columns: show sort indicator (↑↓) on hover; active: filled arrow
- Filterable: filter chips above table, not buried in settings
- Empty state: helpful illustration + action ("No results found. [Book appointment]")

---

## Modal Dialogs

### Standard Modal

```
┌─────────────────────────────────────────┐
│  Confirm Medication Order           ✕   │
│─────────────────────────────────────────│
│  You are about to order:               │
│                                        │
│  Metformin 500mg — Twice daily         │
│  Patient: James Smith (MRN: 001234)    │
│  Duration: 90 days                     │
│                                        │
│  ⚠ Interaction: Alcohol (moderate)     │
│                                        │
│  [Cancel]              [Sign Order]    │
└─────────────────────────────────────────┘
```

- Width: 500px desktop, 90vw tablet, 100vw mobile (full-screen)
- Always show what action is being confirmed with specifics
- Cancel always present and clearly labeled
- Primary action right-aligned
- Backdrop: semi-transparent dark overlay; click-to-dismiss only for non-critical modals
- Never auto-close a confirmation modal

### Sizes

| Size | Width | Use |
|------|-------|-----|
| Small | 400px | Simple confirmations |
| Medium | 500–600px | Forms, order details |
| Large | 800px | Complex workflows |
| Full-screen | 100% | Multi-step clinical flows |

---

## Progress & Loading States

### Skeleton Screen (Loading)

```
┌─────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░         ← name  │
│ ▓▓▓▓▓▓▓░░   ▓▓▓░          ← meta │
│                                     │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░  ← data │
└─────────────────────────────────────┘
```

- Animated shimmer effect (left-to-right gradient)
- Never show blank white screen while loading
- Show skeleton that matches the expected layout exactly

### Progress Bar (Multi-Step)

```
Step 2 of 4: Select appointment time
●─────●─────○─────○
```

- Completed steps: filled circle
- Current step: filled + slightly larger
- Future steps: outline only
- Label shows current step name

### Empty States

Every empty state needs: illustration (optional), heading, explanation, action button.

```
[Medical chart illustration]

No lab results yet

Your test results will appear here
once they've been processed.

[Book a Test]
```

---

## Form Design Patterns

From Fruto Design Healthcare Pattern Library:

### Progressive Disclosure

For complex clinical intake forms:
- Show only the fields needed for current context
- Reveal additional fields based on previous answers
- Medical history: only show "Diabetes details" if "Diabetes" is checked

### Inline Validation

- Validate on blur (when user leaves field), not on each keystroke
- Show success (✓) immediately for confirmed-valid fields
- Never clear valid data when showing errors

### Autosave

```
Saved 2 minutes ago  [Interrupt & Resume Later]
```

- Save every 30 seconds in background
- Visible save timestamp bottom of form
- Resume banner when user returns: "You were completing intake for James Smith. [Continue]"

### Smart Defaults

- Pre-fill: known patient data (DOB, allergies) from record
- Default values: most common dosage, most common duration, most common route
- Smart suggestions: "Did you mean Metformin 500mg?" when "met" typed
