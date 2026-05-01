# Patient Portal UI Patterns

Patient-facing self-service interface patterns for web (Bootstrap 5/Tabler + PHP) and Android (Jetpack Compose + Material 3). Covers authentication, dashboard, lab results, medications, appointments, billing, health tracking, and educational resources.

---

## 1. Design Philosophy

Patient portals serve people who may be elderly, injured, stressed, or unfamiliar with technology. Every decision must favor clarity and comfort.

**Core Principles:**

- **Plain language** — No medical jargon without a parenthetical explanation. "HbA1c (average blood sugar over 3 months)" not just "HbA1c".
- **Large touch targets** — 56px (web) / 56dp (Android) minimum. Patients may have tremors, injuries, or reduced dexterity.
- **High contrast** — Target WCAG AAA (7:1 ratio) for all primary text. AA (4.5:1) absolute minimum.
- **Progressive disclosure** — Show essentials first (next appointment, active meds), reveal details on demand (full history, lab trends).
- **Multi-language support** — All strings externalized. RTL layout support. Date/number formatting per locale.
- **Age-inclusive icons** — Use skeuomorphic icons for familiarity: pill bottle for medications, clipboard for records, calendar for appointments, stethoscope for providers, heart for vitals.

**Patient vs. Clinician Density:**

| Aspect | Clinician View | Patient Portal |
|--------|---------------|----------------|
| Information density | High (scan-optimized) | Low (comprehension-optimized) |
| Font size | 15px / 16sp body | 16px / 18sp body minimum |
| Card spacing | 16px gap | 24px gap |
| Actions per screen | Many (workflow tools) | Few (one primary CTA visible) |
| Language | Clinical terminology | Plain language with tooltips |

---

## 2. Patient Authentication

### Login Options

Offer multiple sign-in methods to accommodate all patients:

1. **Email + password** — Standard, always available
2. **Phone + OTP** — SMS or WhatsApp verification, preferred for elderly
3. **Google / Apple sign-in** — Social login for convenience
4. **Biometric** (Android) — Fingerprint or face unlock via `android-biometric-login` skill

### Web Login (Tabler)

```html
<div class="container-tight py-6">
  <div class="card card-md shadow-sm">
    <div class="card-body">
      <h2 class="text-center mb-4">Welcome to Your Health Portal</h2>
      <form action="/auth/login" method="post" autocomplete="on">
        <div class="mb-3">
          <label class="form-label fs-5">Email or Phone Number</label>
          <input type="text" class="form-control form-control-lg"
                 name="identifier" autocomplete="username" required
                 style="min-height: 56px; font-size: 1.1rem;">
        </div>
        <div class="mb-3">
          <label class="form-label fs-5">Password</label>
          <input type="password" class="form-control form-control-lg"
                 name="password" autocomplete="current-password" required
                 style="min-height: 56px; font-size: 1.1rem;">
        </div>
        <div class="mb-3">
          <a href="/auth/forgot" class="fs-5">Forgot password?</a>
        </div>
        <button type="submit" class="btn btn-primary btn-lg w-100"
                style="min-height: 56px; font-size: 1.1rem;">
          Sign In
        </button>
      </form>
      <div class="hr-text my-4">or</div>
      <div class="d-grid gap-2">
        <a href="/auth/google" class="btn btn-outline-secondary btn-lg">
          Continue with Google
        </a>
        <a href="/auth/otp" class="btn btn-outline-secondary btn-lg">
          Sign in with Phone (OTP)
        </a>
      </div>
    </div>
  </div>
</div>
```

### Android Login (Compose)

```kotlin
@Composable
fun PatientLoginScreen(
    onLogin: (String, String) -> Unit,
    onBiometric: () -> Unit
) {
    var identifier by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(Modifier.height(48.dp))
        Text("Welcome to Your Health Portal",
             style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(32.dp))
        OutlinedTextField(value = identifier,
            onValueChange = { identifier = it },
            label = { Text("Email or Phone Number") },
            modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp),
            textStyle = MaterialTheme.typography.bodyLarge.copy(fontSize = 18.sp))
        Spacer(Modifier.height(16.dp))
        // Password field, biometric button, social sign-in...
        Button(onClick = { onLogin(identifier, password) },
            modifier = Modifier.fillMaxWidth().height(56.dp)
        ) { Text("Sign In", fontSize = 18.sp) }
    }
}
```

### Security Rules

- **Session timeout:** 15 minutes of inactivity. Show countdown at 13 min. Save form state before logout so patient does not lose work.
- **2FA for sensitive actions:** Viewing full medical records, downloading data, changing contact info.
- **Password recovery:** Email or SMS verification. Never reveal whether an account exists.
- **First-time onboarding:** Guided 3-step setup: verify identity, complete profile, set communication preferences.
- **Remember device:** Allow trusted device enrollment to skip 2FA for 30 days (configurable).

---

## 3. Patient Home / Dashboard

### Layout

```
+-------------------------------------------+
| Welcome, [First Name]     [Notifications] |
+-------------------------------------------+
| +---------------+ +---------------------+ |
| | Next Appt     | | Active Medications  | |
| | Dr. Smith     | | 3 active, 1 refill  | |
| | Feb 28, 2pm   | | due                 | |
| +---------------+ +---------------------+ |
| +---------------+ +---------------------+ |
| | Recent Labs   | | Health Goals        | |
| | 2 new         | | Steps: 6,200/10,000 | |
| | results       | | ####------ 62%      | |
| +---------------+ +---------------------+ |
| +-------------------------------------+   |
| | Messages (1 unread from Dr. Smith)  |   |
| +-------------------------------------+   |
+-------------------------------------------+
```

### Web Implementation

```html
<div class="page-header mb-3">
  <h2 class="page-title">Welcome, <?= htmlspecialchars($patient->first_name) ?></h2>
  <a href="/notifications" class="btn btn-outline-primary position-relative">
    Notifications
    <?php if ($unreadCount > 0): ?>
      <span class="badge bg-red badge-notification"><?= $unreadCount ?></span>
    <?php endif; ?>
  </a>
</div>
<div class="row row-cols-1 row-cols-md-2 g-4">
  <div class="col">
    <div class="card shadow-sm" style="min-height: 140px;">
      <div class="card-body">
        <h3 class="card-title fs-4">Next Appointment</h3>
        <p class="fs-5 mb-1"><?= $nextAppt->provider_name ?></p>
        <p class="text-muted fs-5"><?= formatDate($nextAppt->datetime) ?></p>
        <a href="/appointments" class="btn btn-primary mt-2">View Details</a>
      </div>
    </div>
  </div>
  <!-- Repeat for Medications, Labs, Goals, Messages -->
</div>
```

### Android Implementation

```kotlin
@Composable
fun PatientDashboard(state: DashboardState) {
    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(vertical = 16.dp)
    ) {
        item { WelcomeHeader(state.firstName, state.unreadCount) }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                DashboardCard(
                    title = "Next Appointment",
                    subtitle = state.nextAppt.providerName,
                    detail = state.nextAppt.formattedDate,
                    modifier = Modifier.weight(1f)
                )
                DashboardCard(
                    title = "Active Medications",
                    subtitle = "${state.activeMedCount} active",
                    detail = "${state.refillDueCount} refill due",
                    modifier = Modifier.weight(1f)
                )
            }
        }
        // Labs row, Health Goals row, Messages card
    }
}
```

**Rules:** Pull-to-refresh on Android. Auto-refresh every 60s on web. Cards are tappable/clickable to navigate to detail. Unread badge uses `clinical-critical` color.

---

## 4. Lab Results Access

### List View Columns

| Column | Display | Notes |
|--------|---------|-------|
| Test Name | Plain name + tooltip with clinical name | "Blood Sugar (Glucose, Fasting)" |
| Date | Formatted per locale | "Feb 20, 2026" |
| Status | Badge: Pending (blue), Completed (green) | Icon + text, never color alone |
| Provider | Ordering physician name | Tappable to message |

### Result Detail Display

```
+-------------------------------------------+
| Blood Sugar (Glucose, Fasting)            |
| Collected: Feb 20, 2026                   |
+-------------------------------------------+
| Your Result:  95 mg/dL     [NORMAL]       |
| Normal Range: 70 - 100 mg/dL             |
+-------------------------------------------+
| What This Means:                          |
| Your blood sugar level is within the      |
| normal range. This suggests your body is  |
| processing sugar well.                    |
+-------------------------------------------+
| Trend (last 12 months):                   |
| 110 |        *                             |
| 100 |  *        *   *                      |
|  90 |     *        *   *  *               |
|  80 +--+--+--+--+--+--+--+--             |
|      Mar May Jul Sep Nov Jan Feb          |
+-------------------------------------------+
| [Download PDF]  [Share with Provider]     |
+-------------------------------------------+
```

**Color coding:** Normal = `clinical-success` green, Abnormal = `clinical-warning` amber, Critical = `clinical-critical` red. Always pair with text label and icon.

### Web: DataTables with expandable rows and Chart.js for trend lines.

### Android: LazyColumn with expandable cards, inline chart composable using a lightweight charting library.

### Filter options: date range (Flatpickr on web, DatePicker on Android), test name search, status toggle.

---

## 5. Medication Management

### Current Medications List

Each medication card shows:

- **Drug name** (bold, large) + generic name in parentheses
- **Dosage and frequency** — "500mg, twice daily with meals"
- **Prescribing doctor** — tappable to message
- **Refill status badge:** Active (green), Refill Due (amber), Expired (red)
- **Visual pill identifier** — shape and color thumbnail if available

### Medication Ordering (3-Step Flow)

```
Step 1: Select Prescription
+-------------------------------------------+
| Choose a prescription to refill:          |
| (*) Metformin 500mg - Dr. Smith           |
|     Last filled: Jan 15, 2026             |
| ( ) Lisinopril 10mg - Dr. Johnson        |
|     Last filled: Feb 1, 2026              |
| --- OR ---                                |
| [Upload New Prescription] (photo/file)    |
+-------------------------------------------+
| [Next ->]                                 |

Step 2: Delivery Preferences
+-------------------------------------------+
| Quantity: [30 tablets v]                   |
| Delivery: (*) Pickup at pharmacy          |
|           ( ) Home delivery (+$5.00)      |
| Preferred pharmacy: [City Pharmacy v]     |
+-------------------------------------------+
| [<- Back]                [Next ->]        |

Step 3: Review and Pay
+-------------------------------------------+
| Metformin 500mg x 30 tablets              |
| Pickup at City Pharmacy                   |
| Cost: $12.00 (You save $8.00 vs retail)   |
+-------------------------------------------+
| [<- Back]         [Confirm and Pay]       |
```

### Web: Card list with refill action buttons. SweetAlert2 for confirmations. Multi-step form with progress indicator.

### Android: LazyColumn with action buttons. Stepper composable for the 3-step flow. WorkManager for medication reminder scheduling.

### Medication Reminders

Configurable push notifications (time, frequency, snooze). Android: AlarmManager for exact timing, WorkManager for daily scheduling. Web: Browser notification API with service worker fallback.

---

## 6. Appointment Self-Service

### Book New Appointment Flow

**Step 1: Find a Provider**

- Search by: specialty, provider name, location, insurance accepted
- Show: provider photo, name, specialty, next available slot, rating
- Filter: distance, availability (today, this week, next available)

**Step 2: Select Date and Time**

- Calendar view with available slots highlighted
- Time slots in 15/30-min increments, grouped by morning/afternoon/evening
- Web: Flatpickr inline calendar with slot buttons
- Android: Custom date picker composable with time slot chips

**Step 3: Confirm Details**

- Reason for visit (text field, optional category dropdown)
- Reminder preference: SMS, email, push notification, or all
- Insurance verification prompt
- Cancellation policy notice

### My Appointments

| Column | Display |
|--------|---------|
| Date/Time | Formatted, with "Today" / "Tomorrow" relative labels |
| Provider | Name + specialty |
| Location | Clinic name + address (tappable for maps) |
| Status | Upcoming (blue), Completed (green), Cancelled (gray) |
| Actions | Reschedule, Cancel, Check-in (if within 24h) |

### Digital Check-In (up to 24h before appointment)

1. Confirm personal information (name, DOB, address, phone)
2. Update insurance (photo upload of card)
3. Intake questionnaire (reason for visit, symptoms)
4. Sign consent forms (digital signature). Show estimated wait time on arrival day.

---

## 7. Billing and Payments

### Invoice List

```
+-------------------------------------------+
| Your Bills                  [Filter v]    |
+-------------------------------------------+
| Feb 15, 2026 | Dr. Smith - Office Visit   |
| Amount: $45.00    Status: [PENDING]       |
| Insurance covered: $120.00                |
| [Pay Now]                                 |
+-------------------------------------------+
| Jan 20, 2026 | Lab Work - Blood Panel     |
| Amount: $0.00     Status: [PAID]          |
| Insurance covered: $85.00                 |
| [View Receipt]                            |
+-------------------------------------------+
```

### Invoice Detail

- Itemized charges with CPT code descriptions in plain language
- Insurance adjustment breakdown
- Patient responsibility clearly highlighted (large font, primary color)
- Payment due date with overdue visual indicator

### Payment Options

- Card on file (show last 4 digits, card brand icon)
- Add new card (inline form or redirect to payment gateway)
- Bank transfer / ACH
- Payment plan setup for large balances
- One-tap/one-click pay for balances under configurable threshold

### Web: Tabler invoice components. Stripe Elements or payment gateway integration. PDF receipt download.

### Android: Card composable with payment action button. In-app payment sheet (Google Pay supported). Receipt sharing via Android share intent.

### Cost Estimation

For upcoming procedures, show estimated cost breakdown:

- Provider charges (estimated)
- Insurance coverage (estimated based on plan)
- Patient estimated responsibility
- Disclaimer: "This is an estimate. Actual costs may vary."

---

## 8. Health Tracking and Wearable Integration

### Connected Devices

| Platform | Integration | Data Types |
|----------|-------------|-----------|
| Apple Health | HealthKit (iOS companion) | Steps, HR, sleep, blood glucose |
| Google Fit | Health Connect API | Steps, HR, sleep, blood pressure |
| Fitbit | REST API | Steps, HR, sleep, SpO2 |
| Manual Entry | In-app forms | Any metric, patient-reported |

### Data Display

- **Daily view:** Bar/line chart for the day, key metrics as cards
- **Weekly view:** 7-day trend line, daily averages, goal progress
- **Monthly view:** Calendar heatmap, monthly summary statistics

### Goal Setting

Display progress bars with numeric labels: "6,200 / 10,000 steps (62%)". Show weekly average and best day. Allow patients to set and adjust goals per metric.

### Share with Care Team

- Opt-in toggle per data category. Shared data visible to assigned providers only.
- Audit log of who accessed shared health data. Revoke sharing at any time.

### Platform Notes

- **Web:** Chart.js for visualizations. API integration panels for device connection.
- **Android:** Health Connect API integration. Compose charts (Vico). Background sync via WorkManager.

---

## 9. Educational Resources

### Content Linking Strategy

Resources appear contextually, not just in a library:

- **From diagnosis:** "You have been diagnosed with Type 2 Diabetes" links to "Understanding Type 2 Diabetes" guide
- **From prescription:** Medication card links to drug info sheet (side effects, interactions, dietary advice)
- **From appointment:** Pre-visit instructions linked 48h before, post-visit care plan linked after

### Content Display

- **Web:** Card-based content library with search bar. Tabler card grid. Rich HTML content.
- **Android:** LazyColumn card list. WebView for rich content, Compose rich-text for simple articles.

### Preventive Care Recommendations

Based on patient demographics (age, gender, history): annual screenings, vaccination schedule, wellness checkup reminders. Show as a checklist card on the dashboard with completion status.

---

## 10. Accessibility Checklist (Patient Portal Specific)

Beyond standard WCAG 2.2 compliance, patient portals must:

| Requirement | Implementation |
|-------------|----------------|
| Font size minimum 16px/18sp | Apply to all body text, form labels, buttons |
| Touch target minimum 56px/56dp | All interactive elements: buttons, links, cards |
| Contrast ratio 7:1 (AAA) preferred | Primary text on backgrounds |
| Screen reader navigation | Landmark roles, heading hierarchy, aria-labels |
| Keyboard-only operation | Tab order, focus indicators, skip-to-content |
| Error messages in context | Inline validation, not just toast/snackbar |
| Plain language alternatives | Tooltip/popover for medical terms |
| Zoom support to 200% | No content loss, no horizontal scroll |
| Form state preservation | Save draft on timeout, restore on re-login |
| Loading states | Skeleton screens, not spinners (reduce anxiety) |

---

## 11. Anti-Patterns (Do NOT Do)

- **Do not** use infinite scroll for medical records. Use paginated lists with clear page counts so patients know the extent of their history.
- **Do not** auto-play videos or audio on health education pages.
- **Do not** use medical abbreviations without expansion (write "Blood Pressure" not "BP" in patient-facing text).
- **Do not** show raw LOINC/CPT codes to patients.
- **Do not** require patients to calculate anything (show "take 2 pills" not "take 500mg when each pill is 250mg").
- **Do not** use small dismissible banners for critical health alerts (abnormal lab results, medication recalls).
- **Do not** hide the "Contact My Doctor" action behind menus. It should be reachable from every screen.
- **Do not** display financial balances prominently on the home dashboard (causes anxiety). Use a dedicated billing section.
- **Do not** require precise date entry for search filters. Provide presets: "Last 3 months", "Last year", "All time".
