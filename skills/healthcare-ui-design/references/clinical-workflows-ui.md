# Clinical Workflows UI Patterns (Reference)

Use this reference for vital signs entry/display, medication administration, care plans, clinical notes, and order entry. Covers web (Bootstrap 5/Tabler + PHP) and Android (Jetpack Compose + Material 3).

## 1. Vital Signs Entry and Display

### Entry Form Pattern

| Vital | Input Type | Unit | Range |
|-------|-----------|------|-------|
| Temperature | Decimal + C/F toggle | C / F | 30.0-45.0C |
| Blood Pressure | Two fields (systolic/diastolic) | mmHg | 50-300 / 20-200 |
| Heart Rate | Integer | bpm | 20-250 |
| SpO2 | Integer | % | 50-100 |
| Respiratory Rate | Integer | /min | 4-60 |
| Pain Scale | Slider or number picker | 0-10 | 0-10 |
| Weight | Decimal | kg / lb | 0.5-500 |
| Height | Decimal | cm / ft-in | 20-300 |

**BMI Auto-Calculation:** When both weight and height are present, display BMI inline: `BMI = weight(kg) / height(m)^2`. Color-code: <18.5 underweight (amber), 18.5-24.9 normal (green), 25-29.9 overweight (amber), >=30 obese (red).

**Entry Source Selector:** Three-option toggle above the form: `[ Manual Entry ] [ Wearable Device ] [ Medical Equipment ]`. When Wearable or Equipment is selected, show device ID field and auto-populate supported vitals.

**Timestamp:** Auto-fill current datetime. Provide override for delayed charting with datetime picker and mandatory "Reason for late entry" text field.

### Clinical Thresholds Table (Configurable Per Facility)

| Vital | Normal (Green) | Warning (Amber) | Critical (Red) |
|-------|---------------|-----------------|----------------|
| HR | 60-100 bpm | <50 or >110 bpm | <40 or >130 bpm |
| SpO2 | >=95% | 90-94% | <90% |
| Temp | 36.1-37.2 C | 37.3-38.5 C | >38.5 C or <35 C |
| BP Systolic | <120 | 120-129 | >=130 |
| BP Diastolic | <80 | 80-89 | >=90 |
| BP Crisis | -- | -- | >180 / >120 |
| RR | 12-20 /min | <10 or >24 /min | <8 or >30 /min |
| Pain | 0-3 | 4-6 | 7-10 |

### Display Patterns

**Grid Cards (Primary View):**

```
+--------------+--------------+--------------+
| HR: 72 bpm   | SpO2: 98%    | Temp: 37.1C  |
| [Normal]     | [Normal]     | [Normal]     |
| -> stable    | -> stable    | -> stable    |
+--------------+--------------+--------------+
| BP: 120/80   | RR: 16 /min  | Pain: 3/10   |
| mmHg [Normal]| [Normal]     | [Mild]       |
| -> stable    | -> stable    | -> down      |
+--------------+--------------+--------------+
```

Each card shows: value (large, bold), unit, status badge (color-coded), trend arrow. Tap/hover reveals timestamp, source, and recording provider.

**Trend Graphs:** Line charts per vital over selectable periods (24h, 7d, 30d). Shade normal range band in light green. Plot warning/critical thresholds as dashed lines. Mark data points with source icon (hand=manual, watch=wearable, monitor=equipment).

**Body Chart:** Anatomical silhouette with tappable regions. Color-code: green (no issues), amber (monitoring), red (active concern). Tapping a region shows associated vitals, diagnoses, and notes.

### Web: Vitals Entry (Tabler + Chart.js)

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Record Vital Signs</h3>
    <div class="btn-group ms-auto" role="group">
      <input type="radio" class="btn-check" name="source" id="src-manual" checked>
      <label class="btn btn-outline-primary btn-sm" for="src-manual">Manual</label>
      <input type="radio" class="btn-check" name="source" id="src-wearable">
      <label class="btn btn-outline-primary btn-sm" for="src-wearable">Wearable</label>
      <input type="radio" class="btn-check" name="source" id="src-equipment">
      <label class="btn btn-outline-primary btn-sm" for="src-equipment">Equipment</label>
    </div>
  </div>
  <div class="card-body">
    <div class="row g-3">
      <div class="col-md-4">
        <label class="form-label">Temperature</label>
        <div class="input-group">
          <input type="number" class="form-control" step="0.1" min="30" max="45">
          <select class="form-select" style="max-width:70px">
            <option value="C">C</option><option value="F">F</option>
          </select>
        </div>
      </div>
      <div class="col-md-4">
        <label class="form-label">Blood Pressure (mmHg)</label>
        <div class="input-group">
          <input type="number" class="form-control" placeholder="120">
          <span class="input-group-text">/</span>
          <input type="number" class="form-control" placeholder="80">
        </div>
      </div>
      <!-- HR, SpO2, RR, Pain, Weight, Height: same col-md-4 input pattern -->
    </div>
  </div>
</div>
<!-- Trend chart: Chart.js line with annotation plugin for normal-range shading -->
<script>
new Chart(document.getElementById('vitals-trend').getContext('2d'), {
  type: 'line',
  data: { labels: timestamps, datasets: [{ label: 'HR', data: hrValues,
    borderColor: '#2563EB', fill: false }]},
  options: { plugins: { annotation: { annotations: { normalBand: {
    type: 'box', yMin: 60, yMax: 100,
    backgroundColor: 'rgba(5,150,105,0.08)', borderWidth: 0 }}}}}
});
</script>
```

### Android: Vitals Composables

```kotlin
@Composable
fun VitalSignCard(label: String, value: String, unit: String,
    status: VitalStatus, trend: TrendDirection, modifier: Modifier = Modifier) {
    val statusColor = when (status) {
        VitalStatus.NORMAL -> Color(0xFF059669)
        VitalStatus.WARNING -> Color(0xFFD97706)
        VitalStatus.CRITICAL -> Color(0xFFDC2626)
    }
    Card(modifier = modifier, colors = CardDefaults.cardColors(
        containerColor = statusColor.copy(alpha = 0.08f)),
        border = BorderStroke(1.dp, statusColor.copy(alpha = 0.3f))) {
        Column(Modifier.padding(12.dp)) {
            Text(label, style = MaterialTheme.typography.labelMedium)
            Row(verticalAlignment = Alignment.Bottom) {
                Text(value, style = MaterialTheme.typography.headlineMedium,
                     fontWeight = FontWeight.Bold)
                Spacer(Modifier.width(4.dp))
                Text(unit, style = MaterialTheme.typography.bodySmall)
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                StatusBadge(status); Spacer(Modifier.width(4.dp)); TrendArrow(trend)
            }
        }
    }
}

@Composable
fun VitalsEntryForm(onSubmit: (VitalsRecord) -> Unit) {
    var temperature by remember { mutableStateOf("") }
    var systolic by remember { mutableStateOf("") }
    var diastolic by remember { mutableStateOf("") }
    var source by remember { mutableStateOf(EntrySource.MANUAL) }
    Column(Modifier.verticalScroll(rememberScrollState())) {
        SourceSelector(selected = source, onSelect = { source = it })
        OutlinedTextField(value = temperature, onValueChange = { temperature = it },
            label = { Text("Temperature") }, suffix = { Text("C") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(value = systolic, onValueChange = { systolic = it },
                label = { Text("Systolic") }, modifier = Modifier.weight(1f))
            Text("/", Modifier.align(Alignment.CenterVertically))
            OutlinedTextField(value = diastolic, onValueChange = { diastolic = it },
                label = { Text("Diastolic") }, modifier = Modifier.weight(1f))
        }
        // HR, SpO2, RR, Pain, Weight, Height: same OutlinedTextField pattern
    }
}
```

## 2. Medication Administration

### 5 Rights Verification UI

Sequential verification steps -- UI must enforce completion order:

1. **Right Patient:** Display photo + full name + MRN + DOB. Barcode scan for wristband. Green checkmark on confirmation.
2. **Right Medication:** Drug name + form (tablet/liquid/injection) + strength. Barcode scan option. Auto cross-check against allergy list.
3. **Right Dose:** Prescribed dose + calculated dose with formula: `Dose = [dose/kg] x [weight] = [result] [unit]`. Flag if outside safe range.
4. **Right Time:** Scheduled vs current time. Amber if +/-15min, red if +/-30min. Require reason if outside window.
5. **Right Route:** Visual icon selector (Oral/IV/IM/SC/Topical/Inhaled). Must match prescribed route. Mismatch blocks progression.

**Override Flow:** Block on verification failure. Override requires supervisor PIN + mandatory reason text. Log all overrides in audit trail.

### Medication List View

Three sections: **Current** (drug + next-due time + Administer button), **PRN** (as-needed meds with last-given time + Give button), **Held/Discontinued** (drug + reason). Each section visually separated.

**Drug Interaction Alerts:** Inline amber banner when active medications interact. Show severity (mild/moderate/severe) and recommendation. **Allergy Cross-Check:** Red blocking alert if prescribed drug matches or is in same class as documented allergy. Requires pharmacist/physician override.

### Web: Step Wizard (Tabler)

```html
<div class="card">
  <div class="card-header"><h3>Medication Administration</h3></div>
  <div class="card-body">
    <div class="steps steps-green steps-counter">
      <a href="#step-patient" class="step-item active">Right Patient</a>
      <a href="#step-med" class="step-item">Right Medication</a>
      <a href="#step-dose" class="step-item">Right Dose</a>
      <a href="#step-time" class="step-item">Right Time</a>
      <a href="#step-route" class="step-item">Right Route</a>
    </div>
    <!-- Step content panels rendered dynamically per active step -->
  </div>
</div>
```

### Android: Stepper Composable

```kotlin
@Composable
fun MedAdminStepper(medication: Medication, patient: Patient) {
    var currentStep by remember { mutableIntStateOf(0) }
    val steps = listOf("Patient", "Medication", "Dose", "Time", "Route")
    val verified = remember { mutableStateListOf(false, false, false, false, false) }
    Column {
        StepIndicator(steps = steps, current = currentStep, verified = verified)
        when (currentStep) {
            0 -> PatientVerification(patient) { verified[0] = true; currentStep++ }
            1 -> MedicationVerification(medication, patient.allergies) {
                verified[1] = true; currentStep++ }
            2 -> DoseVerification(medication, patient.weight) {
                verified[2] = true; currentStep++ }
            3 -> TimeVerification(medication.scheduledTime) {
                verified[3] = true; currentStep++ }
            4 -> RouteVerification(medication.prescribedRoute) { verified[4] = true }
        }
        if (verified.all { it }) {
            Button(onClick = { /* confirm and log */ },
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF059669))) {
                Icon(Icons.Default.Check, null); Text("Confirm Administration")
            }
        }
    }
}
```

## 3. Care Plan Builder

### POGI Framework

Each care plan item follows Problem-Objective-Goal-Intervention:

```
+---------------------------------------------------------------+
| PROBLEM: Uncontrolled Type 2 Diabetes (E11.65)                |
| OBJECTIVE: Reduce HbA1c from 9.2% to <7.0% within 6 months  |
| GOAL: Patient self-manages glucose with <2 hypos/month       |
| INTERVENTION:                                                 |
|   - Endocrinology consult (Dr. Lee) -- Due: Mar 15           |
|   - Dietitian referral -- Due: Mar 10                        |
|   - Daily glucose log review by nurse -- Ongoing             |
| STATUS: [====------] 40% -- At Risk (amber)                  |
+---------------------------------------------------------------+
```

**Status Colors:** On Track (green, >=70%), At Risk (amber, 40-69%), Behind (red, <40%).

**AI-Assisted Templates:** On new diagnosis, suggest matching care plan templates as selectable cards with name, duration, and intervention count.

**Progress Tracking:** Timeline view with milestones showing date, responsible provider, completion status. Notes and attachments at each milestone.

### Web: Draggable Cards (SortableJS)

```html
<div id="care-plan-items" class="sortable-list">
  <div class="card mb-2 care-plan-item" data-id="1">
    <div class="card-body d-flex align-items-center">
      <span class="drag-handle cursor-grab me-2">&#9776;</span>
      <div class="flex-fill">
        <strong>Problem:</strong> Uncontrolled Diabetes
        <div class="progress mt-2" style="height:8px">
          <div class="progress-bar bg-warning" style="width:40%"></div>
        </div>
      </div>
      <span class="badge bg-warning">At Risk</span>
    </div>
  </div>
</div>
<script>new Sortable(document.getElementById('care-plan-items'), {handle:'.drag-handle'});</script>
```

### Android: Reorderable LazyColumn

```kotlin
@Composable
fun CarePlanCard(item: CarePlanItem) {
    val statusColor = when (item.status) {
        PlanStatus.ON_TRACK -> Color(0xFF059669)
        PlanStatus.AT_RISK -> Color(0xFFD97706)
        PlanStatus.BEHIND -> Color(0xFFDC2626)
    }
    Card(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)) {
        Column(Modifier.padding(16.dp)) {
            Text(item.problem, style = MaterialTheme.typography.titleSmall)
            Text("Objective: ${item.objective}", style = MaterialTheme.typography.bodySmall)
            LinearProgressIndicator(progress = { item.progressPercent / 100f },
                color = statusColor, modifier = Modifier.fillMaxWidth().padding(top = 8.dp))
            Text("${item.progressPercent}% - ${item.status.label}",
                color = statusColor, style = MaterialTheme.typography.labelSmall)
        }
    }
}
```

## 4. Clinical Notes / Documentation

### SOAP Note Template

```
+------------------------------------------------------+
| SOAP Note - Visit: 2026-02-23 09:30                 |
+------------------------------------------------------+
| S (Subjective)                                       |
|   Chief Complaint: [text]  HPI: [rich text]          |
|   ROS: [checklist: General, HEENT, CV, Resp, GI...] |
| O (Objective)                                        |
|   Vitals: [auto-populated]  PE: [findings/system]    |
| A (Assessment)                                       |
|   Diagnosis: [ICD-10 search + multi-select]          |
| P (Plan)                                             |
|   Orders: [CPOE link]  Referrals: [specialty search] |
|   Follow-up: [date picker + interval selector]       |
+------------------------------------------------------+
| Auto-saved 30s ago | v3 | [View History] | [Sign]   |
+------------------------------------------------------+
```

**Quick Templates:** Dropdown pre-fills SOAP for common visit types (Annual Physical, Follow-up, Urgent, Post-Op). Editable after selection.

**Voice-to-Text:** Microphone button per text section. Speech-to-text API integration. Transcribed text editable before save.

**Auto-Save:** Draft saved every 30 seconds with "Saved" indicator. Version history via "View History" link.

**E-Signature:** "Sign" captures provider name, credentials (MD/DO/NP/PA), timestamp, IP. Signed notes become read-only; amendments create addendums.

### Web: Accordion SOAP Sections

```html
<div class="card">
  <div class="card-header d-flex justify-content-between">
    <h3>Clinical Note</h3>
    <select class="form-select w-auto" id="note-template">
      <option value="">-- Template --</option>
      <option value="annual">Annual Physical</option>
      <option value="followup">Follow-Up</option>
    </select>
  </div>
  <div class="card-body">
    <div class="accordion" id="soap-sections">
      <div class="accordion-item">
        <h2 class="accordion-header">
          <button class="accordion-button" data-bs-toggle="collapse"
                  data-bs-target="#subjective">Subjective</button>
        </h2>
        <div id="subjective" class="accordion-collapse collapse show">
          <div class="accordion-body">
            <input type="text" class="form-control mb-3" placeholder="Chief Complaint">
            <div id="hpi-editor"></div> <!-- TinyMCE/Quill for HPI -->
          </div>
        </div>
      </div>
      <!-- Objective, Assessment, Plan: same accordion-item pattern -->
    </div>
  </div>
  <div class="card-footer d-flex justify-content-between">
    <small class="text-muted">Auto-saved 30s ago | v3</small>
    <button class="btn btn-primary">Sign Note</button>
  </div>
</div>
```

### Android: Expandable SOAP Form

```kotlin
@Composable
fun SoapNoteForm(note: SoapNote, onSign: (SoapNote) -> Unit) {
    val expanded = remember { mutableStateMapOf("subjective" to true, "objective" to true,
        "assessment" to false, "plan" to false) }
    LazyColumn(Modifier.padding(16.dp)) {
        item {
            SoapSection("Subjective", expanded["subjective"] == true,
                { expanded["subjective"] = !(expanded["subjective"] ?: false) }) {
                OutlinedTextField(note.chiefComplaint, { note.chiefComplaint = it },
                    label = { Text("Chief Complaint") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(note.hpi, { note.hpi = it },
                    label = { Text("HPI") }, minLines = 4, modifier = Modifier.fillMaxWidth())
            }
        }
        // Objective, Assessment, Plan: same SoapSection composable
        item {
            Button(onClick = { onSign(note) }, Modifier.fillMaxWidth()) {
                Icon(Icons.Default.Draw, null); Spacer(Modifier.width(8.dp)); Text("Sign Note")
            }
        }
    }
}
```

## 5. Order Entry (CPOE)

### Order Types

| Order Type | Required Fields |
|-----------|----------------|
| **Lab** | Test name, urgency (Routine/Stat/ASAP), specimen type, clinical indication |
| **Imaging** | Modality (X-ray/CT/MRI/US), body part, indication, contrast Y/N |
| **Medication** | Drug, dose, route, frequency, duration, diagnosis |
| **Referral** | Specialty, preferred provider, reason, urgency, supporting docs |

### Clinical Decision Support (CDS)

Alerts fire automatically during order entry:

- **Duplicate Detection:** "Active CBC order exists (2h ago). Continue?" -- amber warning
- **Drug Interaction:** "Warfarin + Aspirin: increased bleeding risk." -- red block if severe
- **Dose Validation:** "Amoxicillin 2000mg exceeds max dose (1000mg) for 70kg." -- red block
- **Allergy Alert:** "Allergic to Penicillin. Amoxicillin is penicillin-class." -- red block, override required

### Web: Modal Order Form

```html
<div class="modal modal-lg" id="order-modal"><div class="modal-dialog"><div class="modal-content">
  <div class="modal-header">
    <h5>New Order</h5>
    <div class="btn-group">
      <button class="btn btn-outline-primary active" data-type="lab">Lab</button>
      <button class="btn btn-outline-primary" data-type="imaging">Imaging</button>
      <button class="btn btn-outline-primary" data-type="medication">Medication</button>
      <button class="btn btn-outline-primary" data-type="referral">Referral</button>
    </div>
  </div>
  <div class="modal-body">
    <input type="text" class="form-control mb-3" placeholder="Search labs, meds, imaging...">
    <div id="order-results" class="list-group mt-1"></div>
    <div id="order-fields"></div> <!-- Dynamic fields per type -->
    <div id="cds-alerts"></div>   <!-- CDS alert banners -->
  </div>
  <div class="modal-footer">
    <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
    <button class="btn btn-primary">Place Order</button>
  </div>
</div></div></div>
```

### Android: Bottom Sheet Order Form

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OrderEntryBottomSheet(patient: Patient, onDismiss: () -> Unit, onSubmit: (Order) -> Unit) {
    var selectedType by remember { mutableStateOf(OrderType.LAB) }
    var searchQuery by remember { mutableStateOf("") }
    var cdsAlerts by remember { mutableStateOf(emptyList<CdsAlert>()) }
    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(Modifier.padding(16.dp)) {
            Text("New Order", style = MaterialTheme.typography.titleLarge)
            SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) {
                OrderType.entries.forEachIndexed { index, type ->
                    SegmentedButton(selected = selectedType == type,
                        onClick = { selectedType = type },
                        shape = SegmentedButtonDefaults.itemShape(index, OrderType.entries.size)
                    ) { Text(type.label) }
                }
            }
            OutlinedTextField(searchQuery, { searchQuery = it },
                label = { Text("Search ${selectedType.label}") },
                leadingIcon = { Icon(Icons.Default.Search, null) },
                modifier = Modifier.fillMaxWidth())
            cdsAlerts.forEach { CdsAlertBanner(it) }
            Spacer(Modifier.height(16.dp))
            Button({ /* validate and submit */ }, Modifier.fillMaxWidth()) { Text("Place Order") }
        }
    }
}

@Composable
fun CdsAlertBanner(alert: CdsAlert) {
    val (bgColor, icon) = when (alert.severity) {
        CdsSeverity.BLOCKING -> Color(0xFFDC2626).copy(0.1f) to Icons.Default.Block
        CdsSeverity.WARNING -> Color(0xFFD97706).copy(0.1f) to Icons.Default.Warning
        CdsSeverity.INFO -> Color(0xFF0284C7).copy(0.1f) to Icons.Default.Info
    }
    Surface(color = bgColor, shape = RoundedCornerShape(8.dp),
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, null); Spacer(Modifier.width(8.dp))
            Column {
                Text(alert.title, fontWeight = FontWeight.Bold)
                Text(alert.message, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
```

## Cross-Workflow Rules

- **Audit Logging:** Every clinical action (vital entry, med admin, note signing, order placement) must log user ID, timestamp, patient MRN, and action type.
- **Confirmation Dialogs:** All medication, order, and signature actions require explicit confirmation. Never auto-submit.
- **Allergy Visibility:** Patient allergy banner must remain visible across all workflow screens.
- **Offline Support:** Vital signs entry and clinical notes must support offline drafting with sync-on-reconnect.
- **Session Timeout:** 15-minute inactivity timeout. Save drafts before logout. Re-authenticate to resume.
- **Accessibility:** Keyboard navigation for all forms. Color-coded statuses must include text labels. Touch targets minimum 48x48dp (Android).
