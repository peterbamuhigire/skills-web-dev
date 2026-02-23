# Web Implementation Reference (Bootstrap 5 / Tabler + PHP)

Healthcare web patterns on the `webapp-gui-design` stack: Tabler, Bootstrap 5, PHP, SweetAlert2, DataTables.

---

## 1. Page Structure Template

Clone `seeder-page.php` as base. Extend with healthcare regions.

```php
<?php
$page_title = "Patient Vitals";
$active_module = "clinical";
$active_submenu = "vitals";
$require_patient_context = true;
include 'includes/header.php';      // Facility/ward selector, user menu, alerts
include 'includes/sidebar.php';     // Healthcare nav (Section 2)
include 'includes/patient-bar.php'; // Patient context strip
?>
<div class="page-wrapper">
    <?php if ($facility_alert): ?>
    <div class="alert alert-danger alert-facility fixed-top mb-0 rounded-0 text-center"
         role="alert" aria-live="assertive" style="z-index: 1060;">
        <svg class="icon me-1"><use xlink:href="#icon-alert-triangle"/></svg>
        <strong>FACILITY ALERT:</strong> <?= htmlspecialchars($facility_alert) ?>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    <?php endif; ?>
    <div class="page-body">
        <div class="container-xl">
            <div class="page-header d-print-none mb-3">
                <div class="row align-items-center">
                    <div class="col-auto"><h2 class="page-title"><?= $page_title ?></h2></div>
                    <div class="col-auto ms-auto"><!-- Page actions --></div>
                </div>
            </div>
            <div class="row row-deck row-cards"><!-- Content --></div>
        </div>
    </div>
</div>
<?php include 'includes/footer.php'; ?>
```

### Required Includes

| Include | Purpose | Healthcare Extensions |
|---------|---------|----------------------|
| `header.php` | Top bar, CSS, meta | Facility selector, ward/shift dropdown, notification bell |
| `sidebar.php` | Left nav | Healthcare module groups, badge counters |
| `patient-bar.php` | Patient context strip | Persistent bar below header when patient selected |
| `footer.php` | Scripts, closing | Session timeout timer, audit logger, clinical JS |

### Patient Context Bar

Persistent strip showing active patient. Visible on all clinical pages.

```html
<div class="patient-context-bar bg-primary-lt border-bottom py-2 px-3"
     id="patient-context" role="banner" aria-label="Active patient">
  <div class="container-xl">
    <div class="d-flex align-items-center">
      <span class="avatar avatar-sm me-2"
            style="background-image: url(<?= $patient['photo_url'] ?>)"></span>
      <div>
        <strong><?= htmlspecialchars($patient['name']) ?></strong>
        <span class="text-muted mx-1">|</span>
        <span class="font-monospace"><?= $patient['mrn'] ?></span>
        <span class="text-muted mx-1">|</span>
        <?= $patient['gender'] ?>, <?= $patient['age'] ?>y
        <span class="text-muted mx-1">|</span> Blood: <?= $patient['blood_type'] ?>
      </div>
      <?php if ($patient['allergies']): ?>
      <span class="badge bg-danger ms-2">
        Allergies: <?= htmlspecialchars(implode(', ', $patient['allergies'])) ?>
      </span>
      <?php endif; ?>
      <div class="ms-auto">
        <a href="/patients/<?= $patient['id'] ?>" class="btn btn-sm btn-outline-primary">Full Profile</a>
        <button class="btn btn-sm btn-ghost-secondary ms-1" onclick="clearPatientContext()">
          <svg class="icon icon-sm"><use xlink:href="#icon-x"/></svg>
        </button>
      </div>
    </div>
  </div>
</div>
```

---

## 2. Healthcare Navigation Sidebar

### Module Map

| Module | Icon | Sub-items | Badge |
|--------|------|-----------|-------|
| **Dashboard** | `icon-home` | (none) | -- |
| **Patients** | `icon-users` | Lookup, Register, My Patients | -- |
| **Clinical** | `icon-stethoscope` | Vitals, Medications, Orders, Notes | -- |
| **Schedule** | `icon-calendar` | Appointments, Calendar, Queue | Queue (waiting) |
| **Communication** | `icon-message` | Messages, Campaigns, Health Bot | Messages (unread) |
| **Labs & Imaging** | `icon-flask` | Orders, Results, Pending | -- |
| **Billing** | `icon-credit-card` | Invoices, Payments, Insurance | -- |
| **Reports** | `icon-chart-bar` | Clinical, Financial, Operational | -- |
| **Admin** | `icon-settings` | Users, Roles, Facility, Audit Logs | -- |

### Sidebar Pattern (one module shown -- repeat for each)

```html
<aside class="navbar navbar-vertical navbar-expand-lg" data-bs-theme="dark">
  <div class="navbar-brand"><img src="/img/logo-health.svg" alt="Logo" height="32"></div>
  <div class="collapse navbar-collapse">
    <ul class="navbar-nav">
      <!-- Dashboard (no sub-items) -->
      <li class="nav-item">
        <a class="nav-link" href="/dashboard">
          <span class="nav-link-icon"><svg class="icon"><use xlink:href="#icon-home"/></svg></span>
          <span class="nav-link-title">Dashboard</span>
        </a>
      </li>
      <!-- Module with sub-items (repeat pattern for each module above) -->
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#nav-patients"
           data-bs-toggle="collapse" aria-expanded="false">
          <span class="nav-link-icon"><svg class="icon"><use xlink:href="#icon-users"/></svg></span>
          <span class="nav-link-title">Patients</span>
        </a>
        <div class="collapse" id="nav-patients">
          <ul class="nav nav-sm flex-column">
            <li class="nav-item"><a class="nav-link" href="/patients/lookup">Lookup</a></li>
            <li class="nav-item"><a class="nav-link" href="/patients/register">Register</a></li>
            <li class="nav-item"><a class="nav-link" href="/patients/mine">My Patients</a></li>
          </ul>
        </div>
      </li>
      <!-- Module with badge (Communication example) -->
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#nav-comms"
           data-bs-toggle="collapse" aria-expanded="false">
          <span class="nav-link-icon"><svg class="icon"><use xlink:href="#icon-message"/></svg></span>
          <span class="nav-link-title">Communication</span>
          <span class="badge bg-info ms-auto" id="unread-count">0</span>
        </a>
        <div class="collapse" id="nav-comms">
          <ul class="nav nav-sm flex-column">
            <li class="nav-item"><a class="nav-link" href="/comms/messages">Messages</a></li>
            <li class="nav-item"><a class="nav-link" href="/comms/campaigns">Campaigns</a></li>
            <li class="nav-item"><a class="nav-link" href="/comms/healthbot">Health Bot</a></li>
          </ul>
        </div>
      </li>
      <!-- Repeat for: Clinical, Schedule, Labs, Billing, Reports, Admin -->
    </ul>
  </div>
</aside>
```

**Rules:** Active module gets `active` class + `border-start: 3px solid var(--clinical-primary)`. Badge counts update via polling/WebSocket. Collapse state persisted in `sessionStorage`. Icons from Tabler SVG sprite.

---

## 3. Healthcare Component Patterns

### Patient Card

```html
<div class="card card-patient" role="region" aria-label="Patient summary">
  <div class="card-body">
    <div class="d-flex align-items-center">
      <span class="avatar avatar-lg me-3" style="background-image: url(patient.jpg)"
            role="img" aria-label="Patient photo"></span>
      <div>
        <h3 class="mb-0">John Doe <span class="badge bg-danger ms-1">Allergy: Penicillin</span></h3>
        <div class="text-muted">
          M, 45y | <span class="font-monospace">MRN: 1234567</span> | Blood: O+ | Dr. Smith
        </div>
      </div>
      <div class="ms-auto text-end">
        <span class="badge bg-warning">Moderate Risk</span>
        <div class="text-muted small mt-1">Last Visit: 2026-02-20</div>
      </div>
    </div>
  </div>
</div>
```

### Vital Signs Grid

Use `row-cols-2 row-cols-md-3 row-cols-lg-6` for responsive 6-up layout. One tile shown; repeat for SpO2, Temp, BP, RR, Pain. Background class from `getVitalStatus()` (Section 4).

```html
<div class="row row-cols-2 row-cols-md-3 row-cols-lg-6 g-2" aria-label="Vital signs">
  <div class="col">
    <div class="card vital-card bg-success-lt">
      <div class="card-body p-2 text-center">
        <div class="text-muted small">Heart Rate</div>
        <div class="h2 mb-0 font-monospace vital-value" aria-label="72 bpm, normal">72</div>
        <div class="small text-success">bpm - Normal</div>
      </div>
    </div>
  </div>
  <!-- Repeat: SpO2, Temperature, Blood Pressure, Respiratory Rate, Pain Scale -->
</div>
```

### Clinical Alert Banner

```html
<div class="alert alert-danger alert-dismissible border-danger" role="alert" aria-live="assertive">
  <div class="d-flex align-items-start">
    <svg class="icon alert-icon me-2 mt-1"><use xlink:href="#icon-shield-exclamation"/></svg>
    <div class="flex-fill">
      <h4 class="alert-title mb-1">Drug Interaction Alert</h4>
      <div class="text-muted">Warfarin + Aspirin: Increased bleeding risk. Requires physician review.</div>
    </div>
    <button class="btn btn-danger btn-sm ms-3" data-action="acknowledge-alert"
            data-alert-id="123">Acknowledge</button>
  </div>
</div>
```

### Medication Checklist

```html
<div class="list-group list-group-flush" aria-label="Medication schedule">
  <div class="list-group-item">
    <div class="row align-items-center">
      <div class="col-auto"><span class="badge bg-purple">Oral</span></div>
      <div class="col">
        <div class="fw-bold">Amoxicillin 500mg</div>
        <div class="text-muted small">3x daily - Next due: 14:00</div>
      </div>
      <div class="col-auto">
        <span class="badge bg-success-lt text-success me-2">Last: 08:00</span>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal"
                data-bs-target="#administerModal" data-med-id="456">Administer</button>
      </div>
    </div>
  </div>
  <div class="list-group-item">
    <div class="row align-items-center">
      <div class="col-auto"><span class="badge bg-blue">IV</span></div>
      <div class="col">
        <div class="fw-bold">Normal Saline 0.9% 1000mL</div>
        <div class="text-muted small">Continuous - Rate: 125mL/hr</div>
      </div>
      <div class="col-auto">
        <span class="badge bg-info-lt text-info me-2">Running</span>
        <button class="btn btn-outline-secondary btn-sm">Adjust Rate</button>
      </div>
    </div>
  </div>
</div>
```

---

## 4. JavaScript Patterns

### Debounced Patient Search

```javascript
function debounce(fn, delay) {
    let timer;
    return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}
const patientSearch = debounce(async (query) => {
    if (query.length < 2) return;
    const res = await fetch(`/api/patients/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) return;
    renderPatientList((await res.json()).data);
}, 300);
document.getElementById('patient-search').addEventListener('input', e => patientSearch(e.target.value.trim()));
```

### Vital Sign Threshold Validation

```javascript
const VITAL_THRESHOLDS = {
    heart_rate:  { crit_lo: 40, warn_lo: 50, norm_lo: 60, norm_hi: 100, warn_hi: 110, crit_hi: 130 },
    spo2:        { crit_lo: 0,  warn_lo: 0,  norm_lo: 95, norm_hi: 100, warn_hi: 94,  crit_hi: 89 },
    temperature: { crit_lo: 34, warn_lo: 35, norm_lo: 36.1, norm_hi: 37.2, warn_hi: 38.5, crit_hi: 40 },
    resp_rate:   { crit_lo: 6,  warn_lo: 8,  norm_lo: 12, norm_hi: 20,  warn_hi: 24,  crit_hi: 30 },
    systolic_bp: { crit_lo: 70, warn_lo: 80, norm_lo: 90, norm_hi: 140, warn_hi: 160, crit_hi: 180 },
    pain_scale:  { crit_lo: 0,  warn_lo: 0,  norm_lo: 0,  norm_hi: 3,   warn_hi: 6,   crit_hi: 8 }
};
function getVitalStatus(type, value) {
    const t = VITAL_THRESHOLDS[type];
    if (!t) return { status: 'unknown', cssClass: 'text-muted', bgClass: '' };
    if (value <= t.crit_lo || value >= t.crit_hi)
        return { status: 'Critical', cssClass: 'text-danger', bgClass: 'bg-danger-lt' };
    if (value <= t.warn_lo || value >= t.warn_hi)
        return { status: 'Warning', cssClass: 'text-warning', bgClass: 'bg-warning-lt' };
    if (value >= t.norm_lo && value <= t.norm_hi)
        return { status: 'Normal', cssClass: 'text-success', bgClass: 'bg-success-lt' };
    return { status: 'Warning', cssClass: 'text-warning', bgClass: 'bg-warning-lt' };
}
```

### Medication Administration Confirmation (SweetAlert2)

```javascript
function confirmMedicationAdmin(medId, patientId, medName, patientName, mrn) {
    Swal.fire({
        title: 'Confirm Medication Administration',
        html: `<div class="text-start">
            <p>Administering <strong>${medName}</strong> to
            <strong>${patientName} (MRN: ${mrn})</strong></p>
            <div class="alert alert-warning mt-2">
                <strong>5 Rights Check:</strong> Verify Patient, Medication, Dose, Time, Route
            </div></div>`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Confirm Administration',
        confirmButtonColor: '#059669',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/api/medications/administer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content },
                body: JSON.stringify({ medication_id: medId, patient_id: patientId })
            }).then(r => r.json()).then(data => {
                data.success ? Swal.fire('Recorded', 'Administration logged.', 'success')
                             : Swal.fire('Error', data.message, 'error');
            });
        }
    });
}
```

### Session Timeout with Warning

```javascript
const SESSION_TIMEOUT = 15 * 60 * 1000;
const WARNING_AT = 13 * 60 * 1000;
let timeoutTimer, warningTimer;
function resetSessionTimers() {
    clearTimeout(timeoutTimer);
    clearTimeout(warningTimer);
    warningTimer = setTimeout(() => {
        Swal.fire({
            title: 'Session Expiring',
            text: 'Your session expires in 2 minutes due to inactivity.',
            icon: 'warning', showCancelButton: true,
            confirmButtonText: 'Stay Logged In', cancelButtonText: 'Log Out'
        }).then(r => r.isConfirmed
            ? (fetch('/api/session/refresh', { method: 'POST' }), resetSessionTimers())
            : (window.location.href = '/logout'));
    }, WARNING_AT);
    timeoutTimer = setTimeout(() => { window.location.href = '/logout?reason=timeout'; }, SESSION_TIMEOUT);
}
['click','keypress','scroll','mousemove'].forEach(e =>
    document.addEventListener(e, debounce(resetSessionTimers, 1000)));
resetSessionTimers();
```

---

## 5. DataTables for Patient Lists

```javascript
$('#patient-table').DataTable({
    processing: true, serverSide: true,
    ajax: { url: '/api/patients/list', type: 'POST', headers: { 'X-CSRF-Token': csrfToken } },
    columns: [
        { data: 'name', render: (d, t, r) => `
            <div class="d-flex align-items-center">
              <span class="avatar avatar-sm me-2"
                    style="background-image: url(${r.photo_url || '/img/default-avatar.png'})"></span>
              <div><div class="fw-bold">${d}</div>
              <div class="text-muted small">${r.gender}, ${r.age}y</div></div>
            </div>` },
        { data: 'mrn', className: 'font-monospace' },
        { data: 'blood_type' },
        { data: 'risk_level', render: d => {
            const c = { high:'danger', moderate:'warning', low:'success' };
            return `<span class="badge bg-${c[d]||'secondary'}">${d}</span>`;
        }},
        { data: 'allergies', render: d => d?.length
            ? d.map(a => `<span class="badge bg-danger-lt text-danger">${a}</span>`).join(' ')
            : '<span class="text-muted">None</span>' },
        { data: 'next_appointment', render: d => d ? dayjs(d).format('MMM D, HH:mm') : '-' },
        { data: 'id', orderable: false, render: id => `
            <a href="/patients/${id}" class="btn btn-sm btn-outline-primary">View</a>
            <a href="/clinical/vitals?pid=${id}" class="btn btn-sm btn-outline-secondary">Vitals</a>` }
    ],
    order: [[3, 'desc']],
    language: { search: 'Search patients:', emptyTable: 'No patients found' },
    responsive: true, pageLength: 25
});
```

---

## 6. Print and PDF Patterns

Follow the `report-print-pdf` skill. Key healthcare templates use mPDF.

```php
$mpdf = new \Mpdf\Mpdf(['mode' => 'utf-8', 'format' => 'A4']);
$mpdf->SetTitle("Patient Summary - {$patient['name']}");
$mpdf->SetAuthor($current_user['name']);
$html = view('reports/partials/clinical-letterhead', [
    'facility' => $facility, 'report_title' => 'Patient Summary', 'patient' => $patient
]);
$html .= view('reports/patient-summary-body', [
    'patient' => $patient, 'diagnoses' => $diagnoses, 'medications' => $active_meds,
    'allergies' => $allergies, 'vitals' => $latest_vitals, 'care_team' => $care_team
]);
$mpdf->WriteHTML($html);
$mpdf->Output("patient-summary-{$patient['mrn']}.pdf", 'D');
```

### Document Templates

| Document | Key Sections | Special Rules |
|----------|-------------|---------------|
| **Patient Summary** | Demographics, Diagnoses, Medications, Allergies, Vitals, Care Team | Allergy warnings in red |
| **Discharge Summary** | Admission reason, Course, Discharge Dx, Follow-up, Medications | Attending signature required |
| **Lab Report** | Order info, Results table with reference ranges, Flag column | Abnormal values bold + red |
| **Prescription** | Provider, Patient, Rx details, Instructions, Signature line | Legal formatting required |

---

## 7. HIPAA Web Security Checklist

Reference `vibe-security-skill` for base web security; extend with these HIPAA controls.

### HTTP Headers

```php
header("Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'");
header("X-Content-Type-Options: nosniff");
header("X-Frame-Options: DENY");
header("X-XSS-Protection: 1; mode=block");
header("Strict-Transport-Security: max-age=31536000; includeSubDomains");
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Pragma: no-cache");
header("Referrer-Policy: strict-origin-when-cross-origin");
```

### Session Security

```php
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1);
ini_set('session.cookie_samesite', 'Strict');
ini_set('session.gc_maxlifetime', 900);  // 15 min
ini_set('session.use_strict_mode', 1);
ini_set('session.use_only_cookies', 1);
```

### Compliance Checklist

| Requirement | Implementation |
|-------------|----------------|
| CSRF protection | Token in meta tag, validated on all POST/PUT/DELETE |
| Auto-logout | 15-min timeout with 2-min warning modal (see Section 4) |
| PHI autocomplete | `autocomplete="off"` on all PHI input fields |
| No PHI caching | `Cache-Control: no-store` on patient data pages |
| Clickjacking | `X-Frame-Options: DENY` |
| Audit logging | Log every API call: user ID, timestamp, IP, endpoint, patient ID |
| PHI in URLs | Never include patient names or full MRNs in URLs |
| Browser storage | Never store PHI in localStorage or sessionStorage |
| Copy audit | Audit log on copy events for PHI elements |
| Print audit | Log all print/export with document type and patient ID |

### Audit Logger

```javascript
function logAccess(action, resourceType, resourceId, details = {}) {
    navigator.sendBeacon('/api/audit/log', JSON.stringify({
        action,            // 'view', 'edit', 'print', 'export', 'search'
        resource_type: resourceType,
        resource_id: resourceId,
        details,
        timestamp: new Date().toISOString(),
        page_url: window.location.pathname
    }));
}
// Auto-log on patient context pages
if (document.getElementById('patient-context')) {
    const pid = document.getElementById('patient-context').dataset.patientId;
    logAccess('view', 'patient', pid, { section: document.title });
}
```
