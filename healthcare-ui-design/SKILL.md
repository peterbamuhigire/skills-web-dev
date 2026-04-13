---
name: healthcare-ui-design
description: Design world-class clinical and patient-facing healthcare UIs for web,
  mobile (Android/iOS), and tablet. Covers EMR/EHR dashboards, patient portals, telemedicine,
  medication management, wellness apps, and aging-care interfaces. Enforces HIPAA...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Healthcare UI Design

<!-- dual-compat-start -->
## Use When

- Design world-class clinical and patient-facing healthcare UIs for web, mobile (Android/iOS), and tablet. Covers EMR/EHR dashboards, patient portals, telemedicine, medication management, wellness apps, and aging-care interfaces. Enforces HIPAA...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `healthcare-ui-design` or would be better handled by a more specific companion skill.
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
## Overview

Healthcare UIs must do three things simultaneously: keep patients safe, keep clinicians efficient, and earn trust from both. Every pixel carries clinical weight — wrong colors, buried alerts, or confusing navigation can harm real people. Design for the worst moment a user will ever have in your app.

**References:** See `references/` for deep-dive guides on each topic.

| Topic | Reference File |
|-------|---------------|
| Mobile patterns (iOS/Android) | [references/mobile-patterns.md](references/mobile-patterns.md) |
| Tablet patterns | [references/tablet-patterns.md](references/tablet-patterns.md) |
| Desktop / clinician workstation | [references/desktop-patterns.md](references/desktop-patterns.md) |
| Color system & typography | [references/color-typography.md](references/color-typography.md) |
| Component library | [references/components.md](references/components.md) |

## Platform Strategy

### Which Platform, Which Role

| Platform | Primary Users | Primary Tasks |
|----------|--------------|--------------|
| **Mobile** | Patients, community health workers, field nurses | Appointments, meds, mood tracking, telehealth |
| **Tablet** | Bedside nurses, ward doctors, physios, intake staff | Vitals entry, rounding, patient assessment, EHR review |
| **Desktop** | Physicians, specialists, admin, billing, lab | Full EHR, ordering, reporting, complex scheduling |

Never design a single layout for all three. Each has distinct interaction model, ergonomic constraints, and cognitive load profile.

## Mobile Design (Phones — < 768px)

### Core Principles

- **One-handed by default.** Primary actions sit in the thumb zone (bottom 40% of screen).
- **Bottom navigation** (4–5 tabs max): Home, Messages, Appointments, Records, Profile.
- **Single-column layout.** No side-by-side clinical data — patients read under stress.
- **2–3 tap rule.** Any critical task reachable in ≤ 3 taps from home.
- **Touch targets.** Minimum 48×48px for all interactive elements; 56px for aged or motor-impaired users.

### Mobile Navigation

```
Bottom Tab Bar (always visible):
[Home] [Appointments] [Messages] [Records] [Profile]

Avoid: hamburger menus as primary nav, deep nested stacks (>3 levels)
Use: modal sheets for quick actions, FAB for single primary action
```

### Key Mobile Screens

**Patient Home Dashboard**
- Greeting with patient name (trust signal)
- Next appointment card (most important info first)
- Medication reminders with time badges
- Recent lab results with status indicators (no color alone — add text: "Normal", "High", "Low")
- Quick actions: Book, Message Doctor, Refill

**Telehealth Entry**
- One-tap "Start Consultation" button (minimum 56px height, full-width)
- Pre-call checklist: camera, mic, internet check with visual pass/fail
- No waiting in dark UI — show animated "Connecting…" with estimated wait

**Medication Reminder**
- Large pill illustration + medication name in 20px+ bold
- Dose, timing, and instructions on one screen — no scrolling required
- "Taken" / "Skip" / "Snooze" — clear three-state action
- Red badge only for overdue doses — not for every reminder

**Mood / Symptom Tracker**
- Slider or large emoji-scale for quick entry (not typed input)
- Maximum 3 questions per session — cognitive load is high for unwell users
- Progress bar showing streak (gamification for chronic disease management)

### Mobile Typography

- Body text: minimum **18px** (older patients, low-light scenarios)
- Headings: 26–32px
- Labels / captions: 14px minimum
- Line height: 1.6× font size
- Font: System font (SF Pro / Roboto) — fastest load, OS-native feel

### Mobile Color

- Primary brand: **calm blue** (#3A7BD5 or equivalent) — do not use aggressive or saturated primaries
- Success: green (#10B981) — with text label
- Warning: amber (#F59E0B) — with text label
- Danger/alert: red (#EF4444) — with text label, never color alone
- Background: white or very light grey (#F9FAFB) — never dark backgrounds for patient-facing

---

## Tablet Design (768px – 1280px)

### Who Uses Tablets in Healthcare

- **Ward nurses** at patient bedside (portrait, one-handed while holding tablet)
- **Rounding physicians** reviewing records on the move (landscape, two-handed)
- **Intake staff** at reception (landscape, stationary, keyboard attached)
- **Physiotherapists / Allied health** during sessions with patient

### Core Principles

- **Both orientations must work.** Portrait for bedside use, landscape for data review.
- **Glance-first layout.** Most important information visible without scrolling in portrait mode.
- **Hybrid navigation.** Bottom tab bar in portrait; sidebar nav in landscape.
- **Touch AND keyboard.** Tablet users frequently have Bluetooth keyboards; support Tab key and keyboard shortcuts.

### Tablet Navigation

```
Portrait:  Bottom navigation (same as mobile)
Landscape: Persistent left sidebar (200px) + content area
           Sidebar collapses to icon-only (64px) when content needs more space
```

### Key Tablet Screens

**Nurse Rounding Dashboard (Landscape)**
- Patient list (left panel, 280px): name, room, acuity color strip, last vitals time
- Patient detail (right panel): vitals chart, medications, notes, tasks
- Quick vitals entry inline — no modal, no navigation away
- "Next Patient" button bottom-right — supports fast ward rounds

**Vitals Entry Form (Portrait)**
- One metric per screen: BP → HR → SpO2 → Temp → Weight
- Large numeric keypad input (no small text fields)
- Previous reading shown for comparison
- Auto-flagging out-of-range values before submission

**Patient Assessment / Intake (Landscape)**
- Two-column form layout: questions left, patient context right
- Progress indicator: "Step 2 of 5"
- Autosave every 30 seconds — interruptions are constant
- "Interrupt & Resume Later" button — saves partial form with timestamp

### Tablet Typography

- Body: 16px minimum (larger than mobile not needed — viewing distance is closer)
- Data tables: 14px with 1.4× line height for density
- Touch targets: same 48×48px minimum
- Consider: increase to 20px body for patient-facing tablet kiosks

---

## Desktop Design (Clinician Workstations — ≥ 1280px)

### Core Principles

- **Density over simplicity.** Clinicians need maximum information on screen — avoid mobile-style empty space.
- **Left sidebar navigation** — persistent, labeled, with keyboard shortcuts shown.
- **Power-user workflows.** Keyboard shortcuts for every critical action. Document them in a help overlay (? key).
- **Multi-panel layouts.** Patient context (left) + current task (center) + reference/alerts (right).
- **Mouse + keyboard.** Hover states, right-click menus, drag-and-drop are valid desktop-only patterns.

### Desktop Navigation

```
┌─────────────┬────────────────────────────┬───────────────┐
│  Left       │       Main Content         │  Right Panel  │
│  Sidebar    │                            │  (Contextual) │
│  200px      │       ~60% width           │  280px        │
│  • Patients │                            │  • Alerts     │
│  • Schedule │                            │  • Messages   │
│  • Orders   │                            │  • Notes      │
│  • Reports  │                            │               │
└─────────────┴────────────────────────────┴───────────────┘
```

### Key Desktop Screens

**EHR Patient Summary**
- Persistent patient header (always visible): name, DOB, MRN, allergies banner, active alerts
- Tabbed record sections: Summary | Medications | Labs | Imaging | Notes | History
- Inline ordering — never navigate away from patient context to place an order
- Timeline view option: chronological clinical events as a swimlane

**Clinical Dashboard (Physician)**
- My Patients panel: acuity-sorted, color-coded by status
- Tasks panel: pending orders, results needing review, messages
- Alerts panel: critical lab values, drug interactions, overdue actions
- Calendar strip for today's appointments

**Medication Ordering**
- Search with smart autocomplete (generic + brand names)
- Drug interaction warnings appear inline as user types — not after submission
- Dosage calculator for weight-based medications
- Two-step confirm: "Review" then "Sign" — separate from initial entry

**Lab Results Review**
- Reference ranges displayed next to every result
- Trend sparkline for each metric (last 5 readings)
- Critical values highlighted: bold + red + icon (three signals, not just color)
- One-click to message patient or order follow-up

### Desktop Typography

- Body / data: 14px (dense clinical workflows benefit from tighter text)
- Navigation labels: 13px
- Patient name / primary headings: 18–22px
- Data table rows: 14px, 1.4× line height, alternating row shading

---

## Color System (All Platforms)

### Trusted Healthcare Palette

| Role | Light Mode | Dark Mode | Usage |
|------|-----------|-----------|-------|
| Primary (trust) | #3A7BD5 | #5B9FE8 | Buttons, links, brand |
| Success | #10B981 | #34D399 | Confirmations, stable |
| Warning | #F59E0B | #FBBF24 | Moderate alerts |
| Danger | #EF4444 | #F87171 | Critical alerts only |
| Background | #F9FAFB | #111827 | Page background |
| Surface | #FFFFFF | #1F2937 | Cards, panels |
| Text primary | #111827 | #F9FAFB | Body text |
| Text secondary | #6B7280 | #9CA3AF | Labels, captions |

**Rules:**
- Never use color as the only indicator — always add text label or icon
- Red is reserved for true emergencies — overusing it creates alert fatigue
- Soft blues and greens reduce patient anxiety; avoid harsh saturated primaries for patient-facing
- Mental health / behavioral apps: consider soft lilac (#C4B5FD) as primary — reduces stigma

### Specialty Palettes

- **Aging care / accessibility apps:** Higher contrast ratios; avoid subtle grey-on-grey
- **Emergency / ICU dashboards:** Darker backgrounds acceptable; high-contrast alert colors
- **Wellness / fitness:** Vibrant greens (#10B981, #059669) and teals (#14B8A6) — suggest vitality

---

## Accessibility (Non-Negotiable)

- **WCAG 2.1 AA minimum** for all healthcare UIs; AAA for patient-facing
- Contrast ratio: 4.5:1 for body text; 3:1 for large text (≥18px)
- All interactive elements keyboard-navigable; visible focus ring (3px outline, 2px offset)
- Screen reader: semantic HTML, ARIA labels, `role="alert"` for dynamic clinical updates
- Touch targets: 48×48px minimum on all touch interfaces
- Never use only color, shape, or sound to convey critical information

---

## Patient Safety Rules (Always Enforced)

1. **Allergies visible before any prescribing screen** — persistent banner, not one-click away
2. **Drug interactions interrupt workflow** for severe interactions — modal, not passive banner
3. **Confirmation dialogs for irreversible actions** — show specifics: "Administer 500mg Paracetamol to Jane Doe. Confirm?"
4. **Two patient identifiers** on every clinical screen (name + DOB or MRN)
5. **Out-of-range vitals** flagged with color + icon + text (three independent signals)
6. **Autosave every 30 seconds** — clinicians are interrupted constantly; partial data must not be lost
7. **Session timeout warning** 2 minutes before auto-logout on shared workstations

---

## Regulatory Compliance

| Regulation | Requirement | UI Implementation |
|-----------|-------------|-------------------|
| HIPAA | Session timeout, access logging | Auto-logout after inactivity; audit log on every record access |
| FDA 21 CFR Part 11 | Electronic signatures | Two-step sign: review screen → sign with credentials |
| WCAG 2.1 AA | Accessibility | Contrast ratios, keyboard nav, screen reader support |
| ISO 62366-1 | Usability engineering | Minimum 2 patient identifiers; usability testing documentation |
| HL7 FHIR | Interoperability | API-first; no direct DB coupling in UI layer |

---

## App Type Quick-Start Guide

| App Type | Primary Platform | Color Lead | Nav Pattern | Key Constraint |
|----------|----------------|------------|------------|----------------|
| Patient portal | Mobile-first | Calm blue | Bottom tabs | No medical jargon |
| EMR/EHR | Desktop-first | Professional blue-grey | Left sidebar | Maximum data density |
| Telehealth | Responsive all | Warm blue | Simple — one CTA | Technology must feel invisible |
| Mental health | Mobile | Soft lilac/purple | Bottom tabs | Gentle language, no red |
| Aging care | Mobile + tablet | High-contrast blue | Large bottom tabs | 18px+ body, 56px+ targets |
| Medication mgmt | Mobile | Blue + green | Bottom tabs | No ambiguity in dose display |
| ICU/Emergency | Desktop + tablet | Dark bg + high contrast | Left sidebar | Speed — every second counts |
| Wellness/fitness | Mobile | Green/teal | Bottom tabs | Gamification + engagement |

---

## Anti-Patterns (Never Do)

- Color alone to indicate severity — always add text/icon
- Medical jargon in patient-facing interfaces without plain-language alternative
- Hover-only controls on touch platforms
- Modal dialogs for non-critical information (kills clinical flow)
- Identical layouts for mobile and desktop (different cognitive contexts)
- Alert fatigue through overuse of red / notification badges
- Forgetting landscape orientation on tablet
- Tiny touch targets (<44px) in a context where users may have gloves, tremors, or stress

---

## Pre-Delivery Checklist

- [ ] Two patient identifiers on every clinical screen
- [ ] Allergies banner visible before any prescribing action
- [ ] Critical alerts use color + icon + text (three signals)
- [ ] All touch targets ≥ 48×48px (≥56px for aging/accessibility)
- [ ] WCAG 2.1 AA contrast ratios verified
- [ ] Keyboard navigation tested (Tab, Enter, Arrow keys only)
- [ ] Screen reader tested (VoiceOver / TalkBack)
- [ ] Session timeout configured and warning shown
- [ ] Audit trail implemented for all data writes
- [ ] Confirmation dialogs on all irreversible actions
- [ ] Interruption recovery: autosave + resume banner
- [ ] Tablet: portrait AND landscape tested
- [ ] Mobile: one-handed reach for all critical actions
- [ ] Desktop: keyboard shortcuts documented in help overlay
