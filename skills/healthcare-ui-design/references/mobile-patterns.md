# Healthcare Mobile UI Patterns (iOS & Android)

## Screen Architecture

### Bottom Navigation (Standard)
```
[Home] [Appointments] [Messages] [Records] [Profile]
```
- 4–5 tabs max — more creates decision paralysis
- Active tab: filled icon + label in primary blue
- Badge counters: red dot for unread messages/alerts only
- On iOS: use `UITabBarController`; on Android: `BottomNavigationView`

### Floating Action Button
- Use for single dominant action: "Book Appointment", "Log Symptom"
- Position: bottom-right, 16px from edges
- Do NOT use FAB when there are multiple competing primary actions

### Modal Sheets
- Use for contextual quick actions (reschedule, refill, message)
- Bottom sheet on iOS (`UISheetPresentationController`) and Android
- Always include drag handle + backdrop dismiss
- Full-screen modal only for multi-step flows

---

## Key Screen Designs

### Patient Home Dashboard
```
┌─────────────────────────────┐
│  Good morning, Jane  ─────  │  ← Personalised greeting (trust)
│  ┌─────────────────────┐    │
│  │ Next: Dr Smith      │    │  ← Next appointment card (most important)
│  │ Today 2:30pm        │    │
│  │ [Reschedule] [Join] │    │
│  └─────────────────────┘    │
│  Medications (2 due)        │  ← Badge counter
│  ┌──────┐ ┌──────┐          │
│  │Metf..│ │Lisin.│          │  ← Medication cards
│  │8:00am│ │12pm  │          │
│  └──────┘ └──────┘          │
│  Recent Results             │
│  Blood glucose  5.6 Normal  │  ← Result + status text (not color alone)
└─────────────────────────────┘
```

### Medication Detail Screen
- Drug name: 22px bold at top
- Dose + frequency: 18px body, clearly separated
- Next due: large time display, countdown if < 2 hours
- Instructions: expandable section (collapse by default)
- Actions: [Mark Taken] [Skip] [Snooze] — all ≥48px height
- Interaction warnings: amber banner above actions, not hidden in detail

### Appointment Booking Flow
```
Step 1: Select specialty / doctor
Step 2: Select date (calendar picker, 48px day cells)
Step 3: Select time slot (scrollable list, not tiny grid)
Step 4: Confirm + add notes
Step 5: Confirmation screen with calendar add button
```
- Progress bar at top: "Step 2 of 4"
- Back button always accessible
- Never require account creation before showing availability

### Telehealth Pre-Call Screen
- Pre-call checklist (auto-checked where possible):
  - Camera: ✓ Working
  - Microphone: ✓ Working
  - Internet: ✓ Good connection
- "Join Call" button: full-width, 56px height, green (#10B981)
- Waiting room: animated pulse, doctor name + photo, estimated wait time
- "Leave" button: clearly available but not prominent (reduce accidental exits)

### Lab Results List
```
│ Test Name          │ Result │ Status  │ Date   │
│ HbA1c              │ 6.2%   │ ⚠ High  │ 3 Jan  │  ← amber + text
│ Creatinine         │ 85     │ ✓ Normal│ 3 Jan  │  ← green + text
│ Cholesterol Total  │ 4.8    │ ✓ Normal│ 3 Jan  │
```
- Status always: icon + color + text (three signals)
- Tap row to expand: full reference range, trend chart, doctor note
- "Message Doctor about results" CTA at bottom

---

## Aging Care & Accessibility Mobile Patterns

From Dtail Studio (Wellness Aging Care App):
- Body text: **minimum 18px**, ideally 20px
- Buttons: minimum **56×56px** — users may have tremors or reduced dexterity
- Touch target spacing: **12px minimum** between adjacent targets
- High contrast: text contrast ratio ≥ 7:1 (AAA) not just 4.5:1 (AA)
- Avoid thin fonts (weight < 400) — unreadable in outdoor/bright light
- Simple language: "Your appointment is tomorrow at 2pm" not "Appointment: 14:00 15/01"
- Larger icons (28–32px) not small icon-only controls
- Audio confirmation option for medication taken (accessibility)

---

## Mental Health / Behavioral App Patterns

- Color: soft purple/lilac as primary (#C4B5FD, #8B5CF6) — reduces anxiety, avoids clinical coldness
- Avoid: red anywhere except genuine emergency states (causes anxiety)
- Language: "Log how you're feeling" not "Enter mood rating"
- Gamification that feels supportive, not pressuring: streaks shown, not "You missed 3 days!"
- Crisis button: always one tap away, high-contrast, never buried
- Progress visualization: gentle upward curves, not harsh comparison charts

---

## Women's Health App Patterns

- Privacy-first: data stays on device by default, clear sync disclosure
- Compassionate language: no clinical coldness for reproductive health data
- Cycle tracking: visual calendar with color fills, not data tables
- Insights: conversational ("Your cycle is usually 28 days — today is day 14") not raw numbers
- Onboarding: explain why each data point is requested before asking for it

---

## Touch & Interaction Standards

| Element | Minimum Size | Recommended |
|---------|-------------|-------------|
| Buttons | 48×48px | 56px height |
| List rows | 44px height | 56px for primary content |
| Tab bar icons | 44px tap area | 56px for aging apps |
| Form inputs | 44px height | 48–56px |
| Checkbox/radio | 48×48px touch area | 48×48px |
| Spacing between targets | 8px | 12px |

---

## Performance on Mobile

- Load critical screens (home, appointments) in < 2 seconds on 3G
- Skeleton screens while loading — never blank white screens
- Offline mode for critical reads: medication list, appointment details, emergency contacts
- Cache last-known data with timestamp: "Last updated 3 mins ago"
- Lazy-load images (doctor photos, clinic images)
