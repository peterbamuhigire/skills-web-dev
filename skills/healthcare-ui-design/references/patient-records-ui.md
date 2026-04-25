# Patient Records UI Patterns (Reference)

Dual-platform patterns for patient lookup, profiles, history, records, documents, and risk scoring.
Web: Bootstrap 5/Tabler + PHP. Android: Jetpack Compose + Material 3.

## 1. Patient Lookup List

**Search:** Full name, partial name, MRN, phone, DOB, room number. Debounced 300ms, min 2 chars.
Display differentiating data (age, MRN last 4) to prevent misidentification. Store last 10 lookups per session.

**Filters** (collapsible sidebar web / bottom sheet Android): Care Program, Medical Condition, Appointment Status (Scheduled|Checked-In|In-Progress|Completed|No-Show), Provider, Ward/Department.

**Tabs:** `[ All ] [ Current ] [ New ] [ Discharged ] [ High Priority(3) ]` -- server-side filtered.

**Favorites:** Star icon per item, persisted in `user_patient_favorites`. Starred section above results.

**List item anatomy:**
```
[Avatar] Jane Doe, F, 42  | MRN: 7823 | [Allergy: Penicillin]
Dr. Smith (Primary) | Next: Feb 25, 10:00 AM | Risk: [HIGH pill]
```
Avatar: initials fallback, color-coded by gender. Allergy: red=severe, amber=moderate, hidden=none.

### Web: DataTables + Tabler Card

```html
<div class="card">
  <div class="card-header d-flex align-items-center">
    <h3 class="card-title">Patient Lookup</h3>
    <div class="ms-auto d-flex gap-2">
      <input type="text" class="form-control" id="patientSearch"
             placeholder="Name, MRN, phone, DOB..." style="min-width:300px;">
      <button class="btn btn-outline-secondary" data-bs-toggle="collapse"
              data-bs-target="#filterPanel"><i class="ti ti-filter"></i> Filters</button>
    </div>
  </div>
  <div class="collapse" id="filterPanel">
    <div class="card-body bg-light border-bottom"><!-- Filter dropdowns --></div>
  </div>
  <ul class="nav nav-tabs card-header-tabs px-3" role="tablist">
    <li class="nav-item"><a class="nav-link active" href="#">All</a></li>
    <li class="nav-item"><a class="nav-link" href="#">Current</a></li>
    <li class="nav-item"><a class="nav-link" href="#">Discharged</a></li>
    <li class="nav-item"><a class="nav-link" href="#">High Priority
      <span class="badge bg-danger ms-1">3</span></a></li>
  </ul>
  <table class="table table-hover" id="patientTable">
    <thead><tr><th></th><th>Patient</th><th>MRN</th><th>Provider</th><th>Next Appt</th><th>Risk</th></tr></thead>
  </table>
</div>
```
```javascript
// Debounced search (300ms)
let t; document.getElementById('patientSearch').addEventListener('input', function() {
  clearTimeout(t); t = setTimeout(() => { $('#patientTable').DataTable().search(this.value).draw(); }, 300);
});
```

### Android: LazyColumn + Sticky Headers + Pull-to-Refresh

```kotlin
@Composable
fun PatientListScreen(viewModel: PatientListViewModel = hiltViewModel()) {
    val patients by viewModel.patients.collectAsStateWithLifecycle()
    val searchQuery by viewModel.searchQuery.collectAsStateWithLifecycle()
    var showFilters by remember { mutableStateOf(false) }
    PullToRefreshBox(state = rememberPullToRefreshState(), onRefresh = { viewModel.refresh() }) {
        Column(Modifier.fillMaxSize()) {
            SearchBar(query = searchQuery, onQueryChange = { viewModel.updateSearch(it) },
                placeholder = "Name, MRN, phone, DOB...",
                trailingIcon = { IconButton(onClick = { showFilters = true }) {
                    Icon(Icons.Default.FilterList, "Filters") } })
            ClassificationTabRow(viewModel)
            LazyColumn {
                patients.groupBy { it.ward }.forEach { (ward, wardPatients) ->
                    stickyHeader { WardHeader(ward) }
                    items(wardPatients, key = { it.mrn }) { patient ->
                        PatientListItem(patient, onStarClick = { viewModel.toggleFavorite(it) })
                    }
                }
            }
        }
    }
    if (showFilters) FilterBottomSheet(onDismiss = { showFilters = false })
}

@Composable
fun PatientListItem(patient: Patient, onStarClick: (Patient) -> Unit) {
    Card(Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 4.dp)) {
        Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            PatientAvatar(patient.name, patient.photoUrl, patient.gender)
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("${patient.name}, ${patient.genderShort}, ${patient.age}",
                         style = MaterialTheme.typography.titleSmall)
                    Spacer(Modifier.width(8.dp))
                    Text("MRN: ${patient.mrn}", style = MaterialTheme.typography.bodySmall)
                }
                if (patient.allergies.isNotEmpty()) AllergyBadge(patient.allergies)
                Row { Text(patient.primaryProvider, style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.weight(1f)); RiskLevelChip(patient.riskLevel) }
            }
            IconButton(onClick = { onStarClick(patient) }) {
                Icon(if (patient.isFavorite) Icons.Filled.Star else Icons.Outlined.StarBorder,
                     tint = if (patient.isFavorite) Color(0xFFF59F00) else Color.Gray,
                     contentDescription = "Favorite") }
        }
    }
}
```

## 2. Patient Profile / Summary

```
+------------------------------------------------------------------+
| [Photo]  Jane Doe           DOB: 1984-03-15 | Age: 42 | F       |
|          MRN: 7823          Blood: O+  | Lang: English           |
+------------------------------------------------------------------+
| !! ALLERGY: Penicillin (SEVERE) | Sulfa (Moderate)            !! |
+------------------------------------------------------------------+
| [Last Visit]  [Active Meds]  [Open Orders]  [Risk Score]        |
|  Feb 20, 2026   5 medications   2 pending      72 (HIGH)        |
+------------------------------------------------------------------+
| Overview | Vitals | Records | Meds | Labs | Documents | Billing  |
+------------------------------------------------------------------+
```

**Rules:** Allergy banner ALWAYS visible, never scrolls off. Red (`bg-danger`) = severe, amber (`bg-warning`) = moderate. Quick-stat cards are clickable to navigate to detail tabs.

### Web: Tabler Card + Tabs

```html
<div class="card mb-3">
  <div class="card-body">
    <div class="row align-items-center">
      <div class="col-auto"><span class="avatar avatar-lg" style="background-image:url(photo.jpg)"></span></div>
      <div class="col"><h2 class="mb-0">Jane Doe</h2>
        <div class="text-muted">DOB: 1984-03-15 | Age: 42 | Female | MRN: 7823 | Blood: O+ | English</div></div>
    </div>
  </div>
  <div class="card-footer bg-danger text-white fw-bold p-2 text-center">
    ALLERGY: Penicillin (SEVERE) | Sulfa (Moderate)</div>
</div>
<!-- Quick Stats: row row-cards with col-sm-6 col-lg-3 for Last Visit, Active Meds, Open Orders, Risk Score -->
<div class="card"><div class="card-header">
  <ul class="nav nav-tabs card-header-tabs">
    <li class="nav-item"><a class="nav-link active" href="#overview">Overview</a></li>
    <li class="nav-item"><a class="nav-link" href="#vitals">Vitals</a></li>
    <li class="nav-item"><a class="nav-link" href="#records">Records</a></li>
    <li class="nav-item"><a class="nav-link" href="#meds">Medications</a></li>
    <li class="nav-item"><a class="nav-link" href="#labs">Lab Results</a></li>
    <li class="nav-item"><a class="nav-link" href="#docs">Documents</a></li>
    <li class="nav-item"><a class="nav-link" href="#billing">Billing</a></li>
  </ul></div>
  <div class="card-body tab-content"><!-- Tab panes --></div>
</div>
```

### Android: Collapsing Toolbar + TabRow + HorizontalPager

```kotlin
@Composable
fun PatientProfileScreen(patientId: String, vm: PatientProfileViewModel = hiltViewModel()) {
    val patient by vm.patient.collectAsStateWithLifecycle()
    val pagerState = rememberPagerState(pageCount = { 7 })
    val tabs = listOf("Overview","Vitals","Records","Meds","Labs","Documents","Billing")
    val scope = rememberCoroutineScope()
    Scaffold(topBar = { CollapsingToolbarLayout(patient) }) { padding ->
        Column(Modifier.padding(padding)) {
            patient?.allergies?.let { AllergyBanner(it) }
            QuickStatRow(patient)
            ScrollableTabRow(selectedTabIndex = pagerState.currentPage) {
                tabs.forEachIndexed { i, title -> Tab(selected = pagerState.currentPage == i,
                    onClick = { scope.launch { pagerState.animateScrollToPage(i) } },
                    text = { Text(title) }) }
            }
            HorizontalPager(state = pagerState) { page -> when (page) {
                0 -> OverviewTab(patient); 1 -> VitalsTab(patientId)
                2 -> RecordsTab(patientId); 3 -> MedicationsTab(patientId)
                4 -> LabResultsTab(patientId); 5 -> DocumentsTab(patientId)
                6 -> BillingTab(patientId)
            }}
        }
    }
}

@Composable
fun AllergyBanner(allergies: List<Allergy>) {
    val hasSevere = allergies.any { it.severity == Severity.SEVERE }
    Surface(color = if (hasSevere) MaterialTheme.colorScheme.error else Color(0xFFF59F00),
            modifier = Modifier.fillMaxWidth()) {
        Text("ALLERGY: " + allergies.joinToString(" | ") { "${it.name} (${it.severity})" },
             color = Color.White, fontWeight = FontWeight.Bold,
             modifier = Modifier.padding(8.dp), textAlign = TextAlign.Center)
    }
}
```

## 3. Medical History Timeline

Chronological vertical timeline (newest first). Year-based grouping with filter dropdown.

**Event types with color-coded icons:**

| Type | Color | Icon | Type | Color | Icon |
|------|-------|------|------|-------|------|
| Visit | `#206bc4` Blue | Stethoscope | Procedure | `#f76707` Orange | Scalpel |
| Lab | `#0ca678` Teal | Flask | Medication | `#f59f00` Amber | Pill |
| Imaging | `#ae3ec9` Purple | Camera | Discharge | `#2fb344` Green | Door-open |

```
2026 ----+
  Feb 20 o---- [Visit] Dr. Smith - Annual checkup
         |     BP 120/80, Weight 165 lbs. [Expand]
  Feb 10 o---- [Lab] CBC Panel - Results normal
         |     Hemoglobin 14.2, WBC 7.5k. [View Report]
  Jan 15 o---- [Medication] Lisinopril 10mg started
2025 ----+
  Dec 01 o---- [Procedure] Knee arthroscopy (right)
```

### Web: CSS Timeline

```html
<div class="timeline">
  <div class="timeline-year">2026</div>
  <div class="timeline-event">
    <div class="timeline-dot bg-blue"></div>
    <div class="timeline-content"><div class="card card-sm"><div class="card-body">
      <div class="d-flex justify-content-between">
        <span class="badge bg-blue-lt">Visit</span>
        <small class="text-muted">Feb 20, 2026</small></div>
      <h4 class="mt-2 mb-1">Dr. Smith - Annual Checkup</h4>
      <p class="text-muted mb-0">BP 120/80, Weight 165 lbs.</p>
      <a href="#" class="btn btn-sm btn-outline-primary mt-2"
         data-bs-toggle="collapse" data-bs-target="#evt-1">Expand</a>
    </div></div></div>
  </div>
</div>
<!-- CSS: .timeline{position:relative;padding-left:32px}
     .timeline::before{content:'';position:absolute;left:12px;top:0;bottom:0;width:2px;background:var(--tblr-border-color)}
     .timeline-dot{position:absolute;left:6px;width:14px;height:14px;border-radius:50%;border:2px solid #fff}
     .timeline-event{position:relative;margin-bottom:16px}
     .timeline-year{font-weight:700;font-size:1.2rem;margin:16px 0 8px -20px} -->
```

### Android: Canvas Timeline Connector

```kotlin
@Composable
fun MedicalTimeline(events: List<TimelineEvent>) {
    LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
        events.groupBy { it.date.year }.forEach { (year, yearEvents) ->
            item { Text("$year", style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold, modifier = Modifier.padding(vertical = 8.dp)) }
            itemsIndexed(yearEvents) { i, event -> TimelineItem(event, i == yearEvents.lastIndex) }
        }
    }
}

@Composable
fun TimelineItem(event: TimelineEvent, isLast: Boolean) {
    val color = when (event.type) {
        EventType.VISIT -> Color(0xFF206BC4); EventType.LAB -> Color(0xFF0CA678)
        EventType.IMAGING -> Color(0xFFAE3EC9); EventType.PROCEDURE -> Color(0xFFF76707)
        EventType.MEDICATION -> Color(0xFFF59F00); EventType.DISCHARGE -> Color(0xFF2FB344)
    }
    Row(Modifier.fillMaxWidth()) {
        Box(Modifier.width(32.dp).height(IntrinsicSize.Min)) {
            Canvas(Modifier.fillMaxSize()) {
                drawCircle(color, 7.dp.toPx(), Offset(size.width / 2, 20.dp.toPx()))
                if (!isLast) drawLine(Color.LightGray, Offset(size.width / 2, 34.dp.toPx()),
                    Offset(size.width / 2, size.height), 2.dp.toPx())
            }
        }
        ElevatedCard(Modifier.weight(1f).padding(bottom = 8.dp)) {
            Column(Modifier.padding(12.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    SuggestionChip(onClick = {}, label = { Text(event.type.label) },
                        colors = SuggestionChipDefaults.suggestionChipColors(
                            containerColor = color.copy(alpha = 0.1f)))
                    Text(event.date.format(), style = MaterialTheme.typography.labelSmall) }
                Text(event.title, style = MaterialTheme.typography.titleSmall,
                     modifier = Modifier.padding(top = 4.dp))
                Text(event.summary, style = MaterialTheme.typography.bodySmall,
                     color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}
```

## 4. Patient Record Cards

Card-based modular layout: Diagnoses (ICD codes, active/resolved), Insurance (provider, policy, coverage, co-pay), Emergency Contacts (name, relationship, phone, priority), Care Team (primary, specialists, nurses).

**Grid:** Web 3-col lg / 2-col md / 1-col sm. Android `GridCells.Adaptive(300.dp)`.

```
+-------------------+-------------------+-------------------+
| DIAGNOSES         | INSURANCE         | EMERGENCY CONTACTS|
| E11.9 T2 Diabetes | BlueCross PPO    | John Doe (Spouse) |
| Active, 2023-06   | BC-445521        | (555) 123-4567    |
+-------------------+-------------------+-------------------+
```

### Web

```html
<div class="row row-cards">
  <div class="col-lg-4 col-md-6"><div class="card">
    <div class="card-header"><h3 class="card-title">Diagnoses</h3></div>
    <div class="list-group list-group-flush">
      <div class="list-group-item d-flex justify-content-between">
        <div><strong>E11.9</strong> Type 2 Diabetes</div>
        <span class="badge bg-green">Active</span>
      </div>
    </div>
  </div></div>
  <div class="col-lg-4 col-md-6"><div class="card">
    <div class="card-header"><h3 class="card-title">Insurance</h3></div>
    <div class="card-body"><dl class="row mb-0">
      <dt class="col-5">Provider</dt><dd class="col-7">BlueCross PPO</dd>
      <dt class="col-5">Policy #</dt><dd class="col-7">BC-445521</dd>
      <dt class="col-5">Coverage</dt><dd class="col-7">01/2026 - 12/2026</dd>
      <dt class="col-5">Co-pay</dt><dd class="col-7">$30</dd>
    </dl></div>
  </div></div>
  <!-- Emergency Contacts, Care Team cards follow same pattern -->
</div>
```

### Android

```kotlin
@Composable
fun PatientRecordCards(patient: Patient) {
    LazyVerticalGrid(columns = GridCells.Adaptive(300.dp), contentPadding = PaddingValues(12.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        item { DiagnosesCard(patient.diagnoses) }
        item { InsuranceCard(patient.insurance) }
        item { EmergencyContactsCard(patient.emergencyContacts) }
        item { CareTeamCard(patient.careTeam) }
    }
}

@Composable
fun DiagnosesCard(diagnoses: List<Diagnosis>) {
    ElevatedCard(Modifier.fillMaxWidth()) { Column {
        Text("Diagnoses", style = MaterialTheme.typography.titleMedium,
             modifier = Modifier.padding(16.dp))
        HorizontalDivider()
        diagnoses.forEach { dx -> ListItem(
            headlineContent = { Text("${dx.icdCode} ${dx.name}") },
            supportingContent = { Text("Diagnosed: ${dx.dateFormatted}") },
            trailingContent = { SuggestionChip(onClick = {},
                label = { Text(if (dx.isActive) "Active" else "Resolved") },
                colors = SuggestionChipDefaults.suggestionChipColors(containerColor =
                    (if (dx.isActive) Color(0xFF2FB344) else Color.Gray).copy(alpha = 0.12f))) }) }
    }}
}
```

## 5. Document Management

**Categories:** Clinical Notes | Lab Results | Imaging | Consent Forms | Referrals.
Each row: type icon, filename, category, date, uploader, size. Version history per row. Inline preview panel.
Upload: drag-drop (web) or camera/file picker (Android). Max 25MB. Accepted: PDF, JPG, PNG, DICOM.

### Web

```html
<!-- Drag-drop upload zone: dashed border card, ti-cloud-upload icon, hidden file input -->
<div class="card mb-3"><div class="card-body text-center p-4"
     style="border:2px dashed var(--tblr-border-color);border-radius:8px;">
  <i class="ti ti-cloud-upload" style="font-size:2rem;"></i>
  <p class="mb-1">Drag files here or <a href="#">browse</a></p>
  <small class="text-muted">PDF, JPG, PNG, DICOM. Max 25MB.</small>
  <input type="file" id="fileInput" multiple accept=".pdf,.jpg,.png,.dcm" hidden>
</div></div>
<!-- Category pill tabs: All | Clinical Notes | Lab Results | Imaging | Consent Forms | Referrals -->
<!-- Table: Type icon | Document | Category | Date | Uploaded By | Size | Actions -->
```

### Android

```kotlin
@Composable
fun DocumentsTab(patientId: String, vm: DocumentsViewModel = hiltViewModel()) {
    val docs by vm.documents.collectAsStateWithLifecycle()
    val launcher = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenMultipleDocuments()) { uris -> vm.uploadDocuments(uris) }
    Column(Modifier.fillMaxSize()) {
        LazyRow(contentPadding = PaddingValues(horizontal = 12.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            items(DocumentCategory.entries) { cat -> FilterChip(selected = vm.selectedCategory == cat,
                onClick = { vm.filterByCategory(cat) }, label = { Text(cat.label) }) }
        }
        OutlinedButton(onClick = { launcher.launch(arrayOf("application/pdf","image/*")) },
            modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp)) {
            Icon(Icons.Default.CloudUpload, null); Spacer(Modifier.width(8.dp)); Text("Upload") }
        LazyColumn { items(docs, key = { it.id }) { doc ->
            DocumentListItem(doc, onPreview = { vm.preview(doc) },
                onVersionHistory = { vm.showVersions(doc) }) } }
    }
}
```

## 6. Acuity / Risk Scoring Display

| Level | Background | Text | Meaning |
|-------|------------|------|---------|
| Low | `#d4edda` | `#155724` | Routine care |
| Moderate | `#fff3cd` | `#856404` | Needs monitoring |
| High | `#f8d7da` | `#721c24` | Requires intervention |
| Critical | `#721c24` | `#ffffff` | Immediate attention |

**Trend:** Improving (down arrow, green) | Stable (right arrow, gray) | Worsening (up arrow, red).
**Breakdown card:** Score + level pill + trend + rows: HCC Score, Chronic Count, ER Visits/yr, Med Adherence with delta values.

**Web badges:** `bg-success`=LOW, `bg-warning text-dark`=MODERATE, `bg-danger`=HIGH, `style="background:#721c24;color:#fff"`=CRITICAL.

### Android Risk Composables

```kotlin
@Composable
fun RiskLevelChip(level: RiskLevel) {
    val (bg, fg) = when (level) {
        RiskLevel.LOW -> Color(0xFFD4EDDA) to Color(0xFF155724)
        RiskLevel.MODERATE -> Color(0xFFFFF3CD) to Color(0xFF856404)
        RiskLevel.HIGH -> Color(0xFFF8D7DA) to Color(0xFF721C24)
        RiskLevel.CRITICAL -> Color(0xFF721C24) to Color.White
    }
    SuggestionChip(onClick = {}, label = { Text(level.name, fontWeight = FontWeight.Bold) },
        colors = SuggestionChipDefaults.suggestionChipColors(containerColor = bg, labelColor = fg))
}

@Composable
fun RiskScoreCard(score: RiskScore) {
    ElevatedCard(Modifier.fillMaxWidth().padding(12.dp)) { Column(Modifier.padding(16.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically) {
            Text("Risk Score: ${score.value}", style = MaterialTheme.typography.headlineSmall)
            RiskLevelChip(score.level) }
        TrendIndicator(score.trend)
        HorizontalDivider(Modifier.padding(vertical = 8.dp))
        score.breakdown.forEach { (label, value, delta) ->
            Row(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                Text(label, Modifier.weight(1f)); Text(value, Modifier.width(60.dp)); DeltaText(delta) } }
    }}
}
```

## 7. Search Best Practices

- **Two-patient verification:** Similar names trigger side-by-side comparison before selection
- **Differentiators:** Always show age, MRN last 4, DOB alongside name
- **Barcode/QR:** Web accepts scanner input in text field; Android uses CameraX + ML Kit
- **Audit:** Log every access with user ID, timestamp, patient MRN, access reason

### Debounce Pattern (Android ViewModel)

```kotlin
private val _searchQuery = MutableStateFlow("")
val patients = _searchQuery.debounce(300).filter { it.length >= 2 }
    .flatMapLatest { repository.searchPatients(it) }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
```

### Server-Side DataTables (Web)

```javascript
$('#patientTable').DataTable({ processing: true, serverSide: true,
    ajax: { url: '/api/patients/search', type: 'POST' },
    columns: [{ data:'star', orderable:false }, { data:'name' }, { data:'mrn' },
        { data:'provider' }, { data:'next_appointment' },
        { data:'risk_level', render: riskBadgeRenderer }],
    pageLength: 25, deferRender: true });
```

### Barcode Scanner (Android)

```kotlin
@Composable
fun BarcodeScanButton(onScanned: (String) -> Unit) {
    val launcher = rememberLauncherForActivityResult(ScanContract()) { result ->
        result.contents?.let { onScanned(it) } }
    IconButton(onClick = { launcher.launch(ScanOptions().apply {
        setDesiredBarcodeFormats(ScanOptions.CODE_128, ScanOptions.QR_CODE)
        setPrompt("Scan patient wristband"); setBeepEnabled(true) })
    }) { Icon(Icons.Default.QrCodeScanner, "Scan wristband") }
}
```
