# Healthcare Tablet UI Patterns

## Tablet Context in Healthcare

Tablets are used in fundamentally different contexts to phones. Design for each:

| Context | Orientation | Distance | Input | Who |
|---------|-------------|----------|-------|-----|
| Bedside nursing | Portrait | 40cm | Fingers, gloves | Nurse |
| Ward rounding | Landscape | 40–60cm | Fingers, stylus | Doctor |
| Reception/intake | Landscape | 50–70cm | Fingers, keyboard | Admin |
| Physio session | Portrait | 30cm | Fingers | Allied health |
| Patient self-check-in kiosk | Landscape | 60–80cm | Fingers | Patient |

---

## Layout Strategy

### Portrait Mode (Bedside)
- Single-column layout with clear visual hierarchy
- Critical info in top 60% of screen (visible without scrolling)
- Action buttons bottom 40% — thumb reach in one hand
- No sidebar nav — bottom tabs (same as mobile)
- Information density: medium (more than phone, less than desktop)

### Landscape Mode (Rounding / Intake)
```
┌────────────────┬─────────────────────────────────┐
│  Patient List  │         Patient Detail          │
│  280px         │         ~70% width              │
│                │                                 │
│  ◉ Smith, J    │  James Smith | DOB: 12/03/1968  │
│    Room 4A     │  MRN: 00124567                  │
│  ○ Doe, M      │  ─────────────────────────────  │
│    Room 5B     │  [Summary] [Meds] [Notes] [Labs]│
│  ○ Lee, K      │                                 │
│    Room 6C     │  Vitals: BP 140/90 ⚠ High       │
│                │  HR: 78 ✓  SpO2: 97% ✓          │
└────────────────┴─────────────────────────────────┘
```

### Sidebar Navigation (Landscape)
- Width: 240–280px persistent
- Icon + label (not icon-only — context matters for clinical staff)
- Collapsible to 64px icon-only for maximum content space
- Active state: filled background on nav item, color change
- Keyboard shortcut labels shown in sidebar (⌘1, ⌘2, etc.)

---

## Key Tablet Screens

### Nurse Station Dashboard (Portrait)
```
┌─────────────────────────────────────┐
│ Ward 4A  —  12 Patients             │
│ ┌───────────────────────────────┐   │
│ │ ● Smith, James  Room 4A       │   │  ← Red dot = needs attention
│ │   BP 140/90 ⚠  Due: meds 10am│   │
│ └───────────────────────────────┘   │
│ ┌───────────────────────────────┐   │
│ │ ○ Doe, Mary  Room 5B          │   │
│ │   Stable  Next check: 2pm     │   │
│ └───────────────────────────────┘   │
│              [ + Add Note ]         │
└─────────────────────────────────────┘
```

### Vitals Entry (Portrait — one metric per screen)
```
┌─────────────────────────────────────┐
│  Blood Pressure          2 of 5     │  ← Progress indicator
│  James Smith  |  Room 4A            │  ← Patient always visible
│                                     │
│         ┌──────┐ / ┌──────┐         │
│         │ 140  │   │  90  │         │  ← Large input fields
│         └──────┘   └──────┘         │
│         Systolic      Diastolic     │
│                                     │
│  Previous: 135/85  (2 hours ago)   │  ← Context for comparison
│                                     │
│         ⚠  Above normal range       │  ← Auto-flag, amber
│                                     │
│  [← Back]              [Next →]     │
└─────────────────────────────────────┘
```

### Patient Intake Form (Landscape)
```
┌──────────────────────┬──────────────────────────────┐
│ Questions            │ Patient Context              │
│                      │                              │
│ Chief Complaint      │ James Smith                  │
│ ┌──────────────────┐ │ 55 yr male                   │
│ │ [text area]      │ │ Last visit: 6 months ago     │
│ └──────────────────┘ │ Allergies: Penicillin ⚠      │
│                      │ Current meds: 3              │
│ Pain Scale (0–10)    │                              │
│ ○─────────────── 6   │ [View full history]          │
│                      │                              │
│ Duration             │                              │
│ [2] [days ▾]         │                              │
│                      │                              │
│ [Save & Continue]    │                              │
└──────────────────────┴──────────────────────────────┘
```

### Patient Self-Check-In Kiosk (Landscape, Standing)
- Text minimum: **22px** (viewing at arm's length)
- Touch targets: **64×64px** minimum
- Maximum 3 screens total
- Simple flow: Name/DOB → Confirm appointment → Confirm insurance → Done
- Large confirmation screen: "You're checked in! Take a seat. Dr Smith will call you."
- No complex clinical data — just logistics

---

## Tablet Orientation Transitions

When user rotates device mid-task:
- State must be preserved — no data loss on rotation
- Layout reflows but content does not disappear
- If currently editing a form: rotation completes, user stays on same field
- Long-press landscape controls (like modals) must resize correctly

## Tablet Touch Standards

| Element | Portrait Min | Landscape Min |
|---------|-------------|--------------|
| Buttons | 48×48px | 48×44px |
| List row tap area | 56px height | 48px height |
| Data table row | 48px height | 40px height |
| Form inputs | 48px height | 44px height |
| Gloved use | 60×60px | 56×56px |

## Tablet Typography

| Use | Size | Weight |
|-----|------|--------|
| Patient name (primary) | 20–22px | 700 Bold |
| Section headings | 16–18px | 600 SemiBold |
| Body / clinical data | 14–16px | 400 Regular |
| Labels / metadata | 13–14px | 400 Regular |
| Data table cells | 14px | 400 Regular |
| Alert text | 14px | 600 SemiBold |

## Keyboard Support (Tablet with Bluetooth KB)

- Tab through all form fields in logical order
- Enter submits current step
- Escape cancels modals
- Arrow keys navigate lists
- Ctrl+S / Cmd+S saves current form
- Display keyboard shortcut hints on long-press or in `?` help overlay

---

## Styling Notes

- Cards: `border-radius: 12px`, `box-shadow: 0 2px 8px rgba(0,0,0,0.08)`
- Panel dividers: 1px line `#E5E7EB` (subtle, not heavy grid lines)
- Alternating row shading in patient lists: `#F9FAFB` alternate rows
- Active/selected patient row: left-border `4px solid #3A7BD5` + light blue fill
