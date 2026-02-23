# Dashboards & Analytics UI

Cross-platform healthcare dashboard and analytics patterns for Web (Bootstrap 5/Tabler + PHP) and Android (Jetpack Compose + Material 3). Covers role-based dashboards, KPI metric cards, bed occupancy, data visualization, risk scores, real-time alerts, and report generation.

---

## 1. Dashboard Architecture

### 1.1 Role-Based Dashboards

Each role sees a tailored default layout. Never build one-size-fits-all.

| Role | Primary Widgets | Priority |
|------|----------------|----------|
| **Clinician** | Today's patients, pending tasks, unread messages, recent lab results | Speed -- scan in under 5s |
| **Nurse Station** | Ward overview, bed status grid, vital alerts, medication due, handoff notes | Task flow -- zero missed actions |
| **Admin** | Facility KPIs, revenue trends, bed occupancy %, staff utilization, satisfaction | Analytics -- drill-down capability |
| **Patient** | Upcoming appointments, medications, health goals, messages, lab results | Clarity -- plain language, large targets |

### 1.2 Customizable Widget System

- **Drag-and-drop placement**: Users reorder widgets within a grid layout
- **Widget catalog**: Modal picker to add/remove widgets per preference
- **Layout save/restore**: Persist per-user in `user_dashboard_config` table (JSON column)
- **Refresh intervals**: Per-widget poll interval (30s vitals, 5min KPIs, configurable)
- **Default layouts**: Curated per role; user customization overlays the default

### 1.3 Dashboard Wireframes

```
Web (Tabler): Sidebar + 3-col KPI row + chart/alert split + bed grid
┌──────┬──────────────────────────────────────┐
│ Nav  │ [KPI] [KPI] [KPI] / [KPI] [KPI] [KPI]│
│ Side │ [Chart — Line/Bar] [Alert Feed Panel]  │
│ bar  │ [Bed Occupancy Grid — full width]      │
└──────┴──────────────────────────────────────┘

Android (Compose): TopAppBar + 2-col KPI grid + chart + alert feed
┌──────────────────────────┐
│ TopAppBar: Dashboard      │
├──────────────────────────┤
│ [KPI] [KPI] / [KPI] [KPI]│
│ [Line Chart — Trends]     │
│ [Alert Feed — LazyColumn] │
├──────────────────────────┤
│ BottomNav: Home|Patients  │
└──────────────────────────┘
```

---

## 2. KPI Metric Cards

### 2.1 Card Anatomy

```
┌──────────────────────────┐
│ [Icon]  Metric Label     │
│ 1,247                    │
│ +12% arrow-up vs last mo │
│ progressbar 78%          │
└──────────────────────────┘
```

Components: icon (semantic color), label, large value, trend indicator, optional progress bar or sparkline.

### 2.2 Healthcare KPIs

| KPI | Unit | Good Trend | Threshold Example |
|-----|------|------------|-------------------|
| Patient Volume | count/day | Context-dependent | > 50/day = high |
| Average Wait Time | minutes | Down is good | < 15 green, < 30 amber, > 30 red |
| Bed Occupancy Rate | % | 75-85% optimal | < 70 under, > 90 critical |
| Average Length of Stay | days | Down is good | Varies by department |
| Readmission Rate | % | Down is good | < 5% green, < 10% amber, > 10% red |
| Patient Satisfaction | score/5 | Up is good | > 4.2 green, > 3.5 amber, < 3.5 red |
| Revenue per Dept | currency | Up is good | vs. budget target |
| Staff-to-Patient Ratio | ratio | Context-dependent | Meets regulatory minimums |
| Prescription Fill Rate | % | Up is good | > 95% green |
| Lab Turnaround Time | hours | Down is good | < 2h green, < 4h amber, > 4h red |

### 2.3 Color Coding and Trend Arrows

- **Green** (`--clinical-success`): Target met or exceeded
- **Amber** (`--clinical-warning`): Approaching threshold
- **Red** (`--clinical-critical`): Below target / critical
- Trend arrows: up = improving, right = stable, down = declining
- **Context matters**: For wait time and readmission rate, down is good (green). For satisfaction, down is bad (red). Always pair arrow direction with color.

### 2.4 Web: Tabler KPI Card with Sparkline

```html
<div class="col-sm-6 col-lg-3">
  <div class="card">
    <div class="card-body">
      <div class="d-flex align-items-center mb-2">
        <span class="badge bg-success-lt p-2 me-2">
          <i class="ti ti-heartbeat icon"></i>
        </span>
        <span class="text-secondary">Bed Occupancy</span>
      </div>
      <div class="d-flex align-items-baseline">
        <h1 class="mb-0 me-2">82%</h1>
        <span class="text-success d-inline-flex align-items-center lh-1">
          <i class="ti ti-trending-up me-1"></i> +3%
        </span>
      </div>
      <canvas id="sparkline-occupancy" height="30" class="mt-2"></canvas>
      <div class="progress progress-sm mt-2">
        <div class="progress-bar bg-success" style="width: 82%"></div>
      </div>
    </div>
  </div>
</div>
```

```javascript
// Chart.js sparkline — minimal config, no axes
new Chart(document.getElementById('sparkline-occupancy'), {
  type: 'line',
  data: {
    labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
    datasets: [{ data: [76,78,80,79,82,85,82], borderColor: '#059669',
                 borderWidth: 2, fill: false, pointRadius: 0, tension: 0.4 }]
  },
  options: {
    plugins: { legend: { display: false } },
    scales: { x: { display: false }, y: { display: false } },
    responsive: true, maintainAspectRatio: false
  }
});
```

### 2.5 Android: KPI Card Composable

```kotlin
@Composable
fun KpiCard(
    icon: ImageVector, label: String, value: String,
    trend: String, isPositiveTrend: Boolean,
    progress: Float? = null, sparklineData: List<Float> = emptyList(),
    modifier: Modifier = Modifier
) {
    val trendColor = if (isPositiveTrend) ClinicalSuccess else ClinicalCritical
    Card(modifier = modifier.fillMaxWidth(),
         colors = CardDefaults.cardColors(containerColor = ClinicalSurface)) {
        Column(Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(icon, label, tint = ClinicalPrimary, modifier = Modifier.size(24.dp))
                Spacer(Modifier.width(8.dp))
                Text(label, style = MaterialTheme.typography.bodyMedium, color = ClinicalTextSecondary)
            }
            Spacer(Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.Bottom) {
                Text(value, style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
                Spacer(Modifier.width(8.dp))
                Text(trend, color = trendColor, style = MaterialTheme.typography.bodySmall)
            }
            if (sparklineData.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                SparklineChart(sparklineData, trendColor, Modifier.fillMaxWidth().height(30.dp))
            }
            progress?.let {
                Spacer(Modifier.height(8.dp))
                LinearProgressIndicator(progress = { it },
                    modifier = Modifier.fillMaxWidth().height(4.dp).clip(RoundedCornerShape(2.dp)),
                    color = trendColor, trackColor = ClinicalBorder)
            }
        }
    }
}
```

---

## 3. Bed Occupancy Management

### 3.1 Visual Ward Layout

```
Ward 3A — 20 Beds (16 Occupied, 2 Available, 1 Cleaning, 1 Maintenance)
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│3A-01 │ │3A-02 │ │3A-03 │ │3A-04 │ │3A-05 │
│ Blue │ │ Blue │ │Green │ │ Blue │ │ Red  │
│J.Doe │ │M.Lee │ │      │ │R.Kim │ │Clean │
└──────┘ └──────┘ └──────┘ └──────┘ └──────┘
```

| Status | Color | Hex | Meaning |
|--------|-------|-----|---------|
| Available | Green | `#059669` | Ready for admission |
| Occupied | Blue | `#2563EB` | Patient assigned |
| Needs Cleaning | Red | `#DC2626` | Post-discharge, not ready |
| Maintenance | Gray | `#64748B` | Out of service |

### 3.2 Occupancy Metrics and Projection

Display above ward grid: Total Beds, Occupied %, Available Count, Expected Discharges Today, Pending Admissions. Include a 7-day projected occupancy line chart with a horizontal threshold at 90% (critical capacity).

### 3.3 Web: CSS Grid Ward Layout

```html
<div class="ward-grid" style="display:grid; grid-template-columns:repeat(5,1fr); gap:8px;">
  <div class="bed-cell bg-primary-lt text-center p-2 rounded"
       data-bs-toggle="tooltip" title="John Doe — Admitted 2026-02-20 — Cardiology">
    <div class="fw-bold">3A-01</div><small>J. Doe</small>
  </div>
  <div class="bed-cell bg-success-lt text-center p-2 rounded">
    <div class="fw-bold">3A-03</div><small>Available</small>
  </div>
  <!-- Repeat per bed -->
</div>
```

### 3.4 Android: Bed Grid Composable

```kotlin
@Composable
fun WardBedGrid(beds: List<BedInfo>, onBedClick: (BedInfo) -> Unit) {
    LazyVerticalGrid(columns = GridCells.Fixed(4), contentPadding = PaddingValues(8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)) {
        items(beds, key = { it.bedId }) { bed -> BedCell(bed, onClick = { onBedClick(bed) }) }
    }
}

@Composable
fun BedCell(bed: BedInfo, onClick: () -> Unit) {
    val bgColor = when (bed.status) {
        BedStatus.AVAILABLE -> ClinicalSuccess.copy(alpha = 0.15f)
        BedStatus.OCCUPIED -> ClinicalPrimary.copy(alpha = 0.15f)
        BedStatus.CLEANING -> ClinicalCritical.copy(alpha = 0.15f)
        BedStatus.MAINTENANCE -> ClinicalTextMuted.copy(alpha = 0.15f)
    }
    Card(onClick = onClick, colors = CardDefaults.cardColors(containerColor = bgColor)) {
        Column(Modifier.padding(8.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text(bed.bedNumber, fontWeight = FontWeight.Bold)
            Text(bed.patientName ?: bed.status.label,
                 style = MaterialTheme.typography.bodySmall, color = ClinicalTextSecondary)
        }
    }
}
```

---

## 4. Data Visualization Patterns

### 4.1 Chart Type Selection Guide

| Chart Type | Use For | Healthcare Example |
|------------|---------|-------------------|
| **Line** | Trends over time | Vital sign trends, patient volume, revenue |
| **Bar (Vertical)** | Time-series comparison | Monthly admissions, quarterly revenue |
| **Bar (Horizontal)** | Category comparison | Department comparison, top diagnoses |
| **Pie/Donut** | Part-of-whole (max 6 + Other) | Insurance mix, disease distribution |
| **Heatmap** | Density/correlation | Appointment slots by hour/day |
| **Gauge** | Single KPI progress | Occupancy %, satisfaction score |
| **Funnel** | Sequential stage drop-off | Admission to follow-up journey |

### 4.2 Clinical Chart Rules

1. **Always include**: axis labels with units, legend, data point tooltips
2. **Threshold lines**: Horizontal dashed lines for clinical normal ranges
3. **Color accessibility**: Patterns/textures alongside colors; data tables as fallback
4. **Max 6 slices** on pie/donut; group remainder as "Other"
5. **Adjacent legend** -- never overlap labels on the chart
6. **Responsive**: Charts resize with viewport; touch-friendly tooltips on mobile
7. **Libraries**: Web uses Chart.js or ApexCharts with Tabler; Android uses Vico or Compose Canvas

### 4.3 Web: Chart.js Line with Clinical Thresholds

```javascript
new Chart(document.getElementById('vitalTrend'), {
  type: 'line',
  data: {
    labels: timeLabels,
    datasets: [{ label: 'Heart Rate (bpm)', data: heartRateData,
                 borderColor: '#2563EB', tension: 0.3, fill: false }]
  },
  options: {
    plugins: { annotation: { annotations: {
      highThreshold: { type: 'line', yMin: 100, yMax: 100,
        borderColor: '#DC2626', borderDash: [6,4], label: { content: 'High', display: true } },
      lowThreshold: { type: 'line', yMin: 60, yMax: 60,
        borderColor: '#D97706', borderDash: [6,4], label: { content: 'Low', display: true } }
    }}},
    scales: {
      y: { title: { display: true, text: 'BPM' } },
      x: { title: { display: true, text: 'Time' } }
    }
  }
});
```

### 4.4 Android: Compose Canvas Sparkline

```kotlin
@Composable
fun SparklineChart(data: List<Float>, color: Color, modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        if (data.size < 2) return@Canvas
        val maxVal = data.max(); val minVal = data.min()
        val range = (maxVal - minVal).coerceAtLeast(1f)
        val stepX = size.width / (data.size - 1)
        val path = Path().apply {
            data.forEachIndexed { i, v ->
                val x = i * stepX
                val y = size.height - ((v - minVal) / range) * size.height
                if (i == 0) moveTo(x, y) else lineTo(x, y)
            }
        }
        drawPath(path, color, style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round))
    }
}
```

---

## 5. Risk Score and Population Health

### 5.1 Patient Risk Stratification

- **Histogram/bell curve**: Risk score distribution across patient population
- **High-risk list**: Table sorted by score descending, with score breakdown tooltip
- **Stacked bar**: Contribution of risk factors per patient (age, comorbidities, utilization)

### 5.2 Population Health Metrics

| Metric | Visualization | Details |
|--------|--------------|---------|
| Chronic disease prevalence | Horizontal bar | Grouped by condition (diabetes, HTN, COPD) |
| Preventive care completion | Progress bars | Screenings, vaccinations, wellness checks |
| Age/gender distribution | Population pyramid | Stacked horizontal bars, M left, F right |
| RUB distribution | Donut chart | Resource Utilization Band segments |
| ACG/HCC risk detail | Expandable panel | Score components with weight contribution |

### 5.3 Web Implementation

Use DataTables with expandable rows for risk factor breakdown. Chart.js donut overlays inside expanded rows show weight contribution visually.

### 5.4 Android: Expandable Risk List

```kotlin
@Composable
fun RiskPatientList(patients: List<RiskPatient>) {
    LazyColumn {
        items(patients, key = { it.patientId }) { patient ->
            var expanded by remember { mutableStateOf(false) }
            Card(onClick = { expanded = !expanded },
                 modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)) {
                Column(Modifier.padding(12.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        RiskScoreBadge(score = patient.riskScore)
                        Spacer(Modifier.width(12.dp))
                        Column(Modifier.weight(1f)) {
                            Text(patient.name, fontWeight = FontWeight.SemiBold)
                            Text("MRN: ${patient.mrn}",
                                 style = MaterialTheme.typography.bodySmall, color = ClinicalTextMuted)
                        }
                        Icon(if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                             contentDescription = "Toggle details")
                    }
                    AnimatedVisibility(visible = expanded) {
                        Column(Modifier.padding(top = 8.dp)) {
                            patient.riskFactors.forEach { factor ->
                                RiskFactorRow(name = factor.name, weight = factor.weight)
                            }
                        }
                    }
                }
            }
        }
    }
}
```

---

## 6. Real-Time Alerts and Monitoring

### 6.1 Alert Feed Design

Chronological list panel with priority sorting: Critical first, then Warning, then Info.

```
┌──────────────────────────────────────┐
│ Alerts (3 unread)            Filter  │
├──────────────────────────────────────┤
│ [!] CRITICAL 14:32                   │
│ Bed 3A-07: SpO2 dropped to 88%      │
│ [Acknowledge] [Assign] [Escalate]    │
├──────────────────────────────────────┤
│ [!] WARNING 14:15                    │
│ Lab: Potassium 5.8 mEq/L — Room 204 │
│ [Acknowledge] [Dismiss]              │
├──────────────────────────────────────┤
│ [i] INFO 13:50                       │
│ Discharge orders signed — Bed 2B-12  │
│ [Dismiss]                            │
└──────────────────────────────────────┘
```

### 6.2 Alert Rules

- **Critical**: Blocks workflow until acknowledged. Audio notification (configurable, visual fallback for muted environments). Never auto-dismiss.
- **Warning**: Prominent banner, dismissible after 3s minimum display.
- **Info**: Auto-dismiss after 10s, always in feed history.
- **Badge**: Dashboard icon shows unread count. Red dot for critical unread.

### 6.3 Web: Server-Sent Events Feed

```javascript
const alertSource = new EventSource('/api/alerts/stream');
alertSource.addEventListener('clinical-alert', function(e) {
  const alert = JSON.parse(e.data);
  prependAlertToFeed(alert);
  if (alert.priority === 'critical') { playAlertSound(); showBlockingModal(alert); }
  updateAlertBadge();
});
```

Use Tabler notification panel styling. Critical alerts: red-bordered cards with pulsing left border.

### 6.4 Android: Alert Feed Composable

```kotlin
@Composable
fun AlertFeed(alerts: List<ClinicalAlert>, onAction: (ClinicalAlert, AlertAction) -> Unit) {
    LazyColumn(Modifier.fillMaxSize()) {
        items(alerts, key = { it.alertId }) { alert ->
            val borderColor = when (alert.priority) {
                AlertPriority.CRITICAL -> ClinicalCritical
                AlertPriority.WARNING -> ClinicalWarning
                AlertPriority.INFO -> ClinicalInfo
            }
            Card(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)
                .border(3.dp, borderColor, RoundedCornerShape(8.dp))) {
                Column(Modifier.padding(12.dp)) {
                    Row {
                        PriorityBadge(alert.priority)
                        Spacer(Modifier.weight(1f))
                        Text(alert.timestamp, style = MaterialTheme.typography.bodySmall,
                             color = ClinicalTextMuted)
                    }
                    Spacer(Modifier.height(4.dp))
                    Text(alert.message, style = MaterialTheme.typography.bodyMedium)
                    Spacer(Modifier.height(8.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        alert.availableActions.forEach { action ->
                            OutlinedButton(onClick = { onAction(alert, action) }) {
                                Text(action.label, style = MaterialTheme.typography.labelSmall)
                            }
                        }
                    }
                }
            }
        }
    }
}
```

---

## 7. Report Generation

### 7.1 Quick Report Builder

Report configuration panel: date range picker (Flatpickr web / DatePicker Android), department multi-select, metric checklist, format selector (PDF, CSV, Excel, Print).

### 7.2 Export Formats

| Format | Web Approach | Android Approach |
|--------|-------------|-----------------|
| **PDF** | mPDF backend (see `report-print-pdf` skill) | PdfDocument API (see `android-pdf-export` skill) |
| **CSV** | PHP `fputcsv` with UTF-8 BOM | Kotlin `FileWriter` to cache, share via Intent |
| **Excel** | PhpSpreadsheet library | Apache POI or CSV fallback |
| **Print** | Print CSS `@media print` (see `report-print-pdf`) | `PrintManager` framework |

### 7.3 Scheduled Reports and Print

- Configure: frequency (daily/weekly/monthly), recipients, template, filters
- Backend cron generates and emails PDF attachments; store in `report_schedules` table
- Print layouts: `@media print` hides nav/alerts/interactive elements; follow `report-print-pdf` skill

---

## Cross-Reference

| Topic | Skill / Reference |
|-------|------------------|
| Design tokens and colors | [`design-tokens.md`](design-tokens.md) |
| Patient records and lookup | [`patient-records-ui.md`](patient-records-ui.md) |
| Vital signs and medications | [`clinical-workflows-ui.md`](clinical-workflows-ui.md) |
| PDF report generation (Web) | `report-print-pdf` skill |
| PDF export (Android) | `android-pdf-export` skill |
| Web component patterns | [`web-implementation.md`](web-implementation.md) |
| Android Compose patterns | [`android-implementation.md`](android-implementation.md) |
| HIPAA and accessibility | [`compliance-accessibility.md`](compliance-accessibility.md) |
