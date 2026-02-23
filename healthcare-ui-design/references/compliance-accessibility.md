# Compliance, Accessibility & Security UI Patterns

Cross-platform reference for HIPAA compliance, WCAG 2.2 AA accessibility, and security UI patterns: Web (Bootstrap 5/Tabler + PHP) and Android (Jetpack Compose + Material 3).

---

## 1. HIPAA UI Requirements

### 1.1 Protected Health Information (PHI) Handling

**Never display PHI in:**

- URLs or query parameters (`/patient?ssn=123-45-6789` is a violation)
- Browser tab titles or `<title>` tags (use "Patient Record" not "John Smith - DOB 1985")
- Push notification text (use "You have a new message" not "Lab result: HIV positive")
- Error messages or stack traces shown to users
- Console logs (`console.log(patient)` must be stripped in production)
- Autocomplete suggestions on PHI fields

**Mask sensitive identifiers:**

| Data Type | Display Format | Full Access |
|-----------|---------------|-------------|
| SSN | `***-**-6789` | Behind re-auth click |
| DOB | `**/**/1985` or age only | Role-dependent |
| MRN | Full (operational need) | Always visible to clinical |
| Phone | `(***) ***-4321` | Role-dependent |
| Address | City, State only | Role-dependent |

**Auto-lock and session timeout:**

- Lock screen after 15 minutes inactivity (configurable per facility)
- Show blurred overlay, not blank screen (preserves context awareness)
- Session timeout with state preservation: save draft to server, restore on re-login
- Countdown warning at 2 minutes before timeout

**Minimum Necessary Rule:** Only show PHI needed for the user's current role and task. A receptionist sees demographics, not diagnoses. A lab tech sees orders, not billing.

### 1.2 Audit Trail Requirements

Log every interaction with patient data:

| Event | Fields Logged |
|-------|---------------|
| Record access | user_id, patient_id, timestamp, IP, device, section_viewed |
| Data modification | user_id, field, old_value, new_value, reason, timestamp |
| Export/Print/Download | user_id, patient_id, format, fields_included, timestamp |
| Failed access attempt | user_id, patient_id, reason_denied, timestamp |

**UI requirements:**

- Display "Last accessed by [Name] on [Date]" on sensitive records
- Provide audit log viewer for compliance officers (filterable, exportable)
- Show access history tab on patient profiles (visible to admin roles)

### 1.3 Break-the-Glass Access

Emergency override for restricted patient records:

1. User clicks "Emergency Access" on restricted record
2. Modal requires: documented reason (dropdown + free text), acknowledgment checkbox
3. Access granted for limited window (default 4 hours, configurable)
4. Auto-notify privacy officer immediately
5. Access logged with elevated audit detail
6. Banner persists on record: "Emergency access active - expires [time]"

### 1.4 Platform-Specific HIPAA Controls

**Web (PHP):**

```php
// Secure session configuration
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1);
ini_set('session.cookie_samesite', 'Strict');
ini_set('session.gc_maxlifetime', 900); // 15 min
header('Content-Security-Policy: default-src \'self\'; script-src \'self\'');
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Referrer-Policy: no-referrer'); // Prevent PHI leaking in referrer
```

**Android (Kotlin):**

```kotlin
// Sensitive screen protection
class PatientRecordActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
    }
}

// Encrypted storage for cached PHI
val prefs = EncryptedSharedPreferences.create(
    "phi_cache",
    MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC),
    context,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```

---

## 2. WCAG 2.2 AA Compliance

### 2.1 Color Contrast Requirements

| Element | Minimum Ratio | Test Tool |
|---------|---------------|-----------|
| Normal text (<18px) | 4.5:1 | WebAIM Contrast Checker |
| Large text (18px+ or 14px+ bold) | 3:1 | Browser DevTools |
| Non-text (icons, borders, focus rings) | 3:1 | axe DevTools |
| Clinical status colors vs background | 4.5:1 | Test each status color |

**Critical:** Test ALL clinical status colors (critical red, warning amber, success green, info blue) against both light and dark card backgrounds.

### 2.2 Keyboard Navigation

Every healthcare screen must be fully keyboard-operable:

- **Tab** reaches every interactive element in logical order (top-to-bottom, left-to-right)
- **Focus indicators** are always visible: `outline: 2px solid var(--clinical-primary); outline-offset: 2px;`
- **Skip-to-content** link on every page (first focusable element)
- **Escape** closes all modals, dropdowns, and overlays
- **Enter/Space** activates buttons and toggles
- **Arrow keys** navigate within components (tabs, menus, date pickers)

**Web implementation:**

```html
<!-- Skip link — first element in <body> -->
<a href="#main-content" class="visually-hidden-focusable">
  Skip to main content
</a>

<!-- Focus indicator — never use outline: none -->
<style>
:focus-visible {
  outline: 2px solid var(--clinical-primary);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}
</style>
```

### 2.3 Screen Reader Support

**Web ARIA patterns:**

```html
<!-- Vital signs with live updates -->
<div role="region" aria-label="Vital Signs Monitor" aria-live="polite">
  <dl>
    <dt>Heart Rate</dt>
    <dd aria-label="Heart rate 72 beats per minute, normal">
      <span class="vital-value">72</span> <span class="vital-unit">bpm</span>
      <span class="badge badge-success">Normal</span>
    </dd>
  </dl>
</div>

<!-- Critical alert — assertive announcement -->
<div role="alert" aria-live="assertive">
  Critical: Blood pressure reading 180/120 — immediate attention required
</div>

<!-- Table with proper scope headers -->
<table aria-label="Patient Medications">
  <thead>
    <tr><th scope="col">Medication</th><th scope="col">Dosage</th><th scope="col">Frequency</th><th scope="col">Status</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Metformin</th><td>500mg</td><td>Twice daily</td><td><span aria-label="Active">Active</span></td></tr>
  </tbody>
</table>

<!-- ARIA landmarks -->
<header role="banner">...</header>
<nav role="navigation" aria-label="Main">...</nav>
<main role="main" id="main-content">...</main>
<aside role="complementary" aria-label="Patient summary">...</aside>
```

**Android Compose semantics:**

```kotlin
@Composable
fun VitalSignCard(label: String, value: String, unit: String, status: VitalStatus) {
    Card(
        modifier = Modifier.semantics(mergeDescendants = true) {
            contentDescription = "$label $value $unit, ${status.label}"
            stateDescription = status.label
            if (status == VitalStatus.CRITICAL) liveRegion = LiveRegionMode.Assertive
        }
    ) {
        Text(text = label, style = MaterialTheme.typography.labelMedium)
        Text(text = "$value $unit", style = MaterialTheme.typography.headlineMedium)
        StatusBadge(status = status)
    }
}

@Composable
fun CriticalAlert(message: String) {
    Card(
        colors = CardDefaults.cardColors(containerColor = ClinicalColors.CriticalLight),
        modifier = Modifier.semantics {
            liveRegion = LiveRegionMode.Assertive
            contentDescription = "Critical alert: $message"
        }
    ) { Text(text = message, color = ClinicalColors.Critical) }
}
```

### 2.4 Touch Target & Form Accessibility

**Touch targets:**

| Context | Web Minimum | Android Minimum | Healthcare Recommended |
|---------|-------------|-----------------|----------------------|
| Standard interactive | 44x44px | 48x48dp | 48px / 48dp |
| Primary clinical action | 48x48px | 56x56dp | 56px / 56dp |
| Gap between targets | 8px | 8dp | 8px / 8dp |

**Forms -- mandatory patterns:**

```html
<!-- ALWAYS visible labels, NEVER placeholder-only -->
<div class="mb-3">
  <label for="allergies" class="form-label">
    Known Allergies <span class="text-danger" aria-hidden="true">*</span>
    <span class="visually-hidden">(required)</span>
  </label>
  <textarea id="allergies" class="form-control" required
    aria-describedby="allergies-help allergies-error"></textarea>
  <div id="allergies-help" class="form-text">List all known drug and food allergies</div>
  <div id="allergies-error" class="invalid-feedback" role="alert">Required for patient safety</div>
</div>

<!-- Group related fields with fieldset/legend -->
<fieldset>
  <legend>Emergency Contact</legend>
  <label for="ec-name" class="form-label">Full Name</label>
  <input type="text" id="ec-name" class="form-control mb-3">
  <label for="ec-phone" class="form-label">Phone Number</label>
  <input type="tel" id="ec-phone" class="form-control">
</fieldset>
```

---

## 3. Color-Blind Safe Design

**Rule:** Never use color alone to convey clinical meaning.

Every color indicator must be paired with at least one of: icon, text label, pattern, or shape.

### 3.1 Status Indicator Pattern

| Status | Color | Icon | Text Label | All Three Together |
|--------|-------|------|------------|-------------------|
| Critical | `#DC2626` | Warning triangle | "Critical" | Red triangle + "Critical" text |
| Warning | `#D97706` | Exclamation circle | "Warning" | Amber circle + "Warning" text |
| Normal | `#059669` | Checkmark | "Normal" | Green check + "Normal" text |
| Info | `#0284C7` | Info circle | "Pending" | Blue info + "Pending" text |

### 3.2 Chart Accessibility

For clinical charts (vitals over time, lab trends):

- Use different line patterns: solid, dashed, dotted, dash-dot
- Add distinct markers: circle, square, triangle, diamond
- Include data labels at key points
- Provide tabular data alternative

### 3.3 Safe Color Pairs

Instead of red/green (indistinguishable for 8% of males):

| Use Case | Recommended Pair | Avoid |
|----------|-----------------|-------|
| Good/Bad | Blue `#2563EB` + Orange `#D97706` | Red + Green |
| High contrast | Dark blue `#1E40AF` + Yellow `#CA8A04` | Red + Green |
| Status range | Blue/Amber/Dark gray | Red/Yellow/Green alone |

Test all palettes with Deuteranopia, Protanopia, and Tritanopia simulators (Chrome DevTools > Rendering > Emulate vision deficiencies).

---

## 4. Role-Based Access Control UI

### 4.1 UI Visibility Rules

| Strategy | When to Use |
|----------|-------------|
| **Hide** nav items/menu entries | User's role has zero access to the feature |
| **Disable** (gray out) buttons/actions | User can see but needs higher permission to act |
| **Show explanation** on unauthorized attempt | User clicks disabled action or navigates via URL |

Never rely on UI hiding alone for security. Server-side permission checks are mandatory.

### 4.2 Healthcare Role Hierarchy

| Role | Scope | Typical Access |
|------|-------|----------------|
| Super Admin | System-wide | Full platform configuration |
| Facility Admin | Facility | User management, facility settings, reports |
| Physician | Assigned patients | Records, orders, prescriptions, referrals |
| Nurse | Assigned ward/unit | Vitals, medication admin, notes, assessments |
| Lab Technician | Lab module | Lab orders, results entry, specimen tracking |
| Pharmacist | Pharmacy module | Medication orders, dispensing, interactions |
| Receptionist | Front desk | Scheduling, check-in, demographics, billing |
| Patient | Own records | View records, appointments, messages, payments |

### 4.3 Platform Integration

**Web:** Use `dual-auth-rbac` skill for server-side checks + UI filtering:

```php
// Server-side: always check before rendering
if ($auth->hasPermission('view_patient_records')) {
    include 'partials/patient-records-nav.php';
}
// Client-side disabled state for visible but restricted actions
<button class="btn btn-primary" <?= !$auth->hasPermission('prescribe') ? 'disabled aria-disabled="true" title="Requires physician role"' : '' ?>>
  Write Prescription
</button>
```

**Android:** Use `mobile-rbac` skill PermissionGate composable:

```kotlin
PermissionGate(permission = "view_patient_records") {
    PatientRecordsScreen()
}

// Disabled button for visible but restricted actions
PermissionButton(
    permission = "prescribe",
    onClick = { navController.navigate("prescribe/$patientId") },
    disabledMessage = "Requires physician role"
) {
    Text("Write Prescription")
}
```

---

## 5. Data Privacy UI Patterns

### 5.1 Consent Management

Provide granular, revocable consent toggles:

```
Consent Settings
-------------------------------------------------
[ON]  Share records with my care team
[OFF] Share anonymized data with research
[OFF] Share records with insurance provider
[ON]  Receive appointment reminders via SMS
[OFF] Allow third-party health app access
-------------------------------------------------
Last updated: Feb 15, 2026 | Version 3
[View full consent agreement] [Download my consent history]
```

**Requirements:**

- Each toggle has a plain-language explanation (not legal jargon)
- Revocable at any time from patient settings
- All consent changes are version-tracked with timestamps
- Consent state is checked server-side before any data sharing

### 5.2 Data Portability

- **Export my health data** -- FHIR R4 format (JSON) or human-readable PDF
- **Request data deletion** -- with clear notice of legal retention periods (e.g., "Records retained 7 years per state law")
- **Data sharing dashboard** -- shows who has access to what, with revoke option

### 5.3 Privacy Notices

- Layered notice: short summary visible, full policy one click away (plain language, 6th grade reading level)
- Web: cookie/tracking consent banner (GDPR/state law) | Android: privacy policy in settings, consent at onboarding

---

## 6. Security UI Patterns

### 6.1 Authentication

- **MFA required** for all clinical users (password + OTP or biometric)
- **Session indicator:** lock icon + "Secure Session" in header
- **Failed login handling:** lockout after 5 consecutive failures, CAPTCHA after 3
- **Password strength:** minimum 12 characters, complexity indicator, healthcare-grade policy

### 6.2 Sensitive Action Verification

Re-authenticate before high-risk actions:

| Action | Verification Method |
|--------|-------------------|
| Prescribing medication | Password or biometric re-entry |
| Accessing restricted record | Break-the-glass flow (Section 1.3) |
| Exporting patient data | Password + reason documentation |
| Overriding a block | Supervisor PIN entry |
| Digital signature | Credentials + displayed signer identity |

### 6.3 Copy/Paste and Screen Capture

**Web:**

```html
<!-- Warn on copy of PHI fields -->
<input type="text" id="ssn-field" class="phi-field"
  oncopy="logPhiCopy('ssn', userId); showCopyWarning();"
  style="user-select: none;" readonly>

<script>
function showCopyWarning() {
  Swal.fire({
    icon: 'warning',
    title: 'PHI Copy Detected',
    text: 'Copying protected health information has been logged.',
    confirmButtonColor: 'var(--clinical-primary)'
  });
}
</script>
```

**Android:**

```kotlin
// Prevent screenshots on sensitive screens
window.setFlags(
    WindowManager.LayoutParams.FLAG_SECURE,
    WindowManager.LayoutParams.FLAG_SECURE
)

// Disable copy on PHI text fields
TextField(
    value = maskedSsn,
    onValueChange = {},
    readOnly = true,
    modifier = Modifier.semantics {
        // Announce that copy is restricted
        contentDescription = "Social Security Number, last four digits, copy restricted"
    },
    visualTransformation = SsnMaskTransformation()
)
```

---

## 7. Per-Screen Compliance Checklist

Use this checklist for **every** healthcare screen built:

### Accessibility

- [ ] Color contrast verified: 4.5:1 for text, 3:1 for non-text elements
- [ ] All color indicators paired with text labels and/or icons
- [ ] Keyboard navigation works completely (Tab, Enter, Escape, arrows)
- [ ] Visible focus indicators on all interactive elements
- [ ] Screen reader announces all content correctly (test with NVDA/TalkBack)
- [ ] Touch targets meet minimum 48dp (Android) / 44px (web)
- [ ] Forms have visible labels, not placeholder-only
- [ ] Error messages programmatically associated with fields (aria-describedby)
- [ ] Loading states announced via `aria-live` regions
- [ ] Skip-to-content link present (web)

### HIPAA & Privacy

- [ ] PHI not exposed in URLs, page titles, or browser tabs
- [ ] PHI not logged to console or included in error messages
- [ ] Sensitive identifiers masked (SSN, DOB per role)
- [ ] Session timeout implemented with state preservation
- [ ] Audit logging for all data access and modifications
- [ ] "Last accessed by" displayed on sensitive records
- [ ] Minimum Necessary Rule applied (role-scoped data)

### Security

- [ ] Role-based visibility applied (hide/disable per permission)
- [ ] Server-side permission check backs up every UI gate
- [ ] Re-authentication required for sensitive actions
- [ ] FLAG_SECURE set on sensitive Android screens
- [ ] CSP headers and secure cookies configured (web)
- [ ] Copy/paste restrictions on PHI fields with logging
- [ ] Break-the-glass flow available for emergency access

---

**Cross-references:** `dual-auth-rbac` for auth patterns | `mobile-rbac` for Android permissions | `vibe-security-skill` for general web security | `design-tokens.md` for clinical color values
