# Healthcare Desktop UI Patterns (Clinician Workstations)

## Desktop Context

Desktop is the primary platform for physicians, specialists, lab technicians, admin, and billing staff. These users are expert operators who spend 8+ hours in the system. Design for speed, density, and precision — not simplicity.

**Key difference from mobile/tablet:** Clinicians will memorize the interface. Efficiency over discoverability.

---

## Layout Architecture

### Three-Panel EHR Layout (Standard)
```
┌────────────┬──────────────────────────────┬───────────────┐
│ Left Nav   │        Main Content           │  Right Rail   │
│ 220px      │        ~60% width             │  280px        │
│            │                               │               │
│ Patients   │  ┌─────────────────────────┐ │  ● Critical   │
│ Schedule   │  │ Patient Header (sticky) │ │    Labs (2)   │
│ Orders     │  │ Smith J | 55M | MRN 001 │ │               │
│ Results    │  │ ⚠ Penicillin Allergy    │ │  Messages (3) │
│ Reports    │  └─────────────────────────┘ │               │
│ Messages   │                               │  ─────────── │
│ Admin      │  [Summary][Meds][Labs][Notes] │  Today's      │
│            │                               │  Tasks        │
│ ─────────  │  [Tab content here]          │               │
│ ? Help     │                               │               │
│ ⚙ Settings │                               │               │
└────────────┴──────────────────────────────┴───────────────┘
```

### Left Sidebar Navigation
- Width: 220px expanded, 64px icon-only collapsed
- Groups: Patient Care | Workflow | Reports | Admin
- Active item: filled left-border (`4px solid primary`) + subtle bg
- Keyboard shortcuts shown next to label: `Patients ⌘1`
- Notification badges on: Orders (pending), Messages (unread), Results (to review)
- Bottom of sidebar: current user name + role, settings, help

### Patient Header (Sticky — Always Visible)
```
┌──────────────────────────────────────────────────────────┐
│ JAMES SMITH  |  55 yr M  |  DOB: 12 Mar 1968  |  MRN: 001│
│ ⚠ ALLERGY: Penicillin  |  ⚠ ALLERGY: NSAIDs             │
│ Active Meds: 4  |  Last Visit: 3 Jan 2026                │
└──────────────────────────────────────────────────────────┘
```
- Always visible when viewing any patient record
- Allergy banner: amber background, red text, not dismissible
- Minimum height: 56px, adjust for multiple allergies

---

## Key Desktop Screens

### Clinical Dashboard (Physician View)
```
┌──────────────────────────────────────────────────────────┐
│ Good morning, Dr Smith  —  Monday 6 Jan 2026             │
│                                                          │
│  My Patients Today (12)     Pending Actions (5)         │
│  ┌─────────────────────┐    ┌────────────────────────┐  │
│  │ ● Jones, A  9:00am  │    │ Review Lab: Smith J    │  │
│  │ ○ Brown, K  9:30am  │    │ Sign Order: Lee M      │  │
│  │ ○ Davis, L 10:00am  │    │ Callback: Patel R      │  │
│  │ [View All]          │    │ [View All]             │  │
│  └─────────────────────┘    └────────────────────────┘  │
│                                                          │
│  Critical Alerts (1)        Messages (3 unread)         │
│  ┌─────────────────────┐    ┌────────────────────────┐  │
│  │ ⛔ K 6.8 mEq/L      │    │ [Inbox snippet here]   │  │
│  │    Davis, Linda      │    │                        │  │
│  │    [Review Now]      │    │ [Open Inbox]           │  │
│  └─────────────────────┘    └────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Lab Results Review Screen
```
─────────────────────────────────────────────────────────
Test Name      | Result  | Ref Range  | Status   | Trend
─────────────────────────────────────────────────────────
Potassium      | 6.8 ⛔   | 3.5–5.0   | CRITICAL | ↑↑
Sodium         | 138     | 135–145    | Normal   | →
Creatinine     | 145     | 60–110     | ⚠ High   | ↑
Haemoglobin    | 132     | 130–170    | Normal   | →
─────────────────────────────────────────────────────────
```
- Critical values: red row highlight + ⛔ icon + "CRITICAL" text label
- High/Low (non-critical): amber + ⚠ icon + "High"/"Low"
- Normal: green ✓ (subtle, not distracting)
- Trend: sparkline in last column (last 5 readings)
- One-click from result → Message Patient | Order Follow-up | Add Note

### Medication Ordering
```
Search: [metform_________________ ▼]  ← Smart autocomplete

Results:
  Metformin 500mg Tab    [Select]
  Metformin 850mg Tab    [Select]
  Metformin 1000mg Tab   [Select]

⚠ Interaction: Metformin + Alcohol (moderate)  ← Inline, not modal

─────────────────────────────────────────────────────────
Dosage:  [500] mg    Frequency: [Twice daily ▼]
Route:   [Oral ▼]   Duration:  [90] days
Instructions: [With meals____________________________]
─────────────────────────────────────────────────────────

[Save Draft]  [Review Order]  (→ then Sign)
```
- Two-step sign: never one-click prescribing
- Drug interaction warnings appear as user types, not on submit
- Dosage calculator shows: weight-based suggestion for paediatrics
- On "Review Order": full summary screen before signing

### Patient Record Tabs

**Summary Tab:** Chief complaint, problem list, active medications, allergies, recent vitals, last visit summary — all on one screen, above the fold.

**Medications Tab:** Full medication list with: drug, dose, frequency, prescriber, start date, refills remaining. Actions: [Refill] [Modify] [Discontinue] (each requiring confirmation).

**Notes Tab:** SOAP-structured notes with rich text editor. Previous notes in timeline. Voice-to-text option.

**Orders Tab:** Pending, active, completed orders in separate sections. Order sets for common conditions.

---

## Hospital Management / CRM Dashboard

For admin, scheduling, and operations teams:

```
┌──────────────┬──────────────────────────────────────────┐
│  Left Nav    │   KPI Header                             │
│              │   Patients Today: 142  |  Avg Wait: 18m  │
│  Dashboard   │   Beds Available: 23   |  ER Load: 87%   │
│  Patients    │                                          │
│  Schedule    │  ┌──────────────┐ ┌─────────────────┐    │
│  Staff       │  │ Dept Capacity│ │ Appointments    │    │
│  Billing     │  │ [Bar Chart]  │ │ [Timeline View] │    │
│  Reports     │  └──────────────┘ └─────────────────┘    │
│  Settings    │                                          │
└──────────────┴──────────────────────────────────────────┘
```

- Real-time data refresh every 60 seconds (configurable)
- Color-coded capacity: green <70%, amber 70–90%, red >90%
- Drill-down: click any KPI to see detail list

---

## AI Integration Patterns (Desktop)

From Nutrisense AI SaaS Dashboard and DocNow booking:
- AI suggestions appear as **recommendations**, not instructions: "Consider reviewing potassium levels"
- AI confidence shown: "High confidence" / "Moderate confidence" badges
- Always one-click to dismiss or override AI recommendation
- AI-authored content clearly labeled: "AI-generated draft — review before signing"
- Never auto-submit or auto-sign on behalf of clinician

---

## Desktop Typography

| Use | Size | Weight |
|-----|------|--------|
| Page title / patient name | 20–24px | 700 |
| Section headings | 16–18px | 600 |
| Body / clinical notes | 14px | 400 |
| Data table cells | 13–14px | 400 |
| Labels / metadata | 12–13px | 400 |
| Navigation labels | 13px | 500 |
| Keyboard shortcuts | 11px | 400, monospace |

- Font: Inter, Roboto, or SF Pro — clean, high-legibility at small sizes
- Line height: 1.4–1.5 for body text; 1.2 for dense data tables
- Letter spacing: 0 for body; +0.01em for all-caps labels

## Desktop Keyboard Shortcuts

Always document these in a `?` help overlay:

| Action | Mac | Win/Linux |
|--------|-----|-----------|
| Patient search | ⌘K | Ctrl+K |
| New note | ⌘N | Ctrl+N |
| New order | ⌘O | Ctrl+O |
| Save | ⌘S | Ctrl+S |
| Sign/Confirm | ⌘Enter | Ctrl+Enter |
| Go to patients | ⌘1 | Ctrl+1 |
| Go to schedule | ⌘2 | Ctrl+2 |

## Print Support (Desktop)

- Discharge summaries, lab reports, prescriptions must be print-optimized
- CSS `@media print`: hide nav, right rail; show patient header; black ink only
- Print layout: A4/Letter, 12px min font, clear section breaks
- Electronic prescription: add QR code to printed script for pharmacy verification
