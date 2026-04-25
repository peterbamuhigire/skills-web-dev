# Scheduling & Telemedicine UI

Reference for appointment scheduling, queue management, pre-visit workflows, telemedicine video consultations, multi-channel communication, and notification systems. Covers **Web (Bootstrap 5/Tabler + PHP)** and **Android (Jetpack Compose + Material 3)**.

---

## 1. Appointment Scheduling

### Provider Search & Discovery

**Filter criteria:** specialty, location, insurance accepted, language, gender, availability window.

Integrate `gis-mapping` skill for map-based provider search with Leaflet markers.

**Provider Card Layout:**

```
┌──────────────────────────────────────────────┐
│ [Photo]  Dr. Jane Kimura, MD                 │
│          Cardiology | Speaks: EN, SW          │
│          Rating: 4.8/5 (142 reviews)         │
│          Accepts: BlueCross, Aetna, Medicare  │
│          Next Available: Feb 24, 10:30 AM     │
│          [Book Now]  [View Profile]           │
└──────────────────────────────────────────────┘
```

**Web:** Tabler card grid with sidebar filter panel. Map view via Leaflet (see `gis-mapping`). Combine DataTable search + Flatpickr date range for availability filtering.

**Android:** `LazyVerticalGrid` of `ElevatedCard` composables. Filter via `ModalBottomSheet`. Map view using `AndroidView` with Leaflet WebView or Google Maps Compose.

### Calendar Views

```
DAY VIEW                           WEEK VIEW
┌────────────────────────┐         ┌─────┬─────┬─────┬─────┬─────┐
│ Mon Feb 24, 2026       │         │ Mon │ Tue │ Wed │ Thu │ Fri │
├────────────────────────┤         ├─────┼─────┼─────┼─────┼─────┤
│ 8:00  [BLUE] New Pt    │         │ ██  │ ░░  │ ██  │ ░░  │ ░░  │
│       John D. - Intake │         │ ██  │ ██  │ ░░  │ ██  │ ░░  │
│ 8:30  ░░ Available ░░  │         │ ░░  │ ██  │ ██  │ ░░  │ ██  │
│ 9:00  [TEAL] Follow-up │         │ ██  │ ░░  │ ██  │ ██  │ ░░  │
│       Mary S. - Cardio │         │ ░░  │ ██  │ ░░  │ ░░  │ ██  │
│ 9:30  [AMBER] Urgent   │         └─────┴─────┴─────┴─────┴─────┘
│       Bob K. - Pain    │         Legend: ██ Booked  ░░ Available
│ 10:00 [PURPLE] Proc.   │                ▓▓ Blocked
│       Kim L. - Biopsy  │
│ 10:30 [GREEN] Telemed  │
│       Pat R. - Video   │
└────────────────────────┘

MONTH VIEW                          PROVIDER SCHEDULE (Multi-Column)
┌───┬───┬───┬───┬───┬───┬───┐     ┌──────────┬──────────┬──────────┐
│Mo │Tu │We │Th │Fr │Sa │Su │     │ Dr.Smith │ Dr.Jones │ Dr.Kim   │
├───┼───┼───┼───┼───┼───┼───┤     ├──────────┼──────────┼──────────┤
│   │   │   │   │   │ 1 │ 2 │     │ 8:00 ██  │ 8:00 ░░  │ 8:00 ██  │
│ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │     │ 8:30 ░░  │ 8:30 ██  │ 8:30 ██  │
│(3)│(5)│(2)│(4)│(1)│   │   │     │ 9:00 ██  │ 9:00 ██  │ 9:00 ░░  │
│10 │11 │...│   │   │   │   │     │ 9:30 ░░  │ 9:30 ░░  │ 9:30 ██  │
└───┴───┴───┴───┴───┴───┴───┘     └──────────┴──────────┴──────────┘
 (n) = appointment count            Facility scheduler view
```

**Web:** FullCalendar.js integration with Tabler card wrapper. Use `eventColor` mapped to appointment type. Flatpickr for date navigation.

**Android:** Custom Compose calendar grid using `LazyVerticalGrid`. Material 3 `DatePicker` for navigation. Color via `MaterialTheme.colorScheme` extensions.

### Appointment Type Color Coding

| Type | Color | Hex | Icon |
|------|-------|-----|------|
| New Patient | Blue | `#2563EB` | `user-plus` |
| Follow-up | Teal | `#0F766E` | `refresh` |
| Urgent | Amber | `#D97706` | `alert-triangle` |
| Procedure | Purple | `#7C3AED` | `scissors` |
| Telemedicine | Green | `#059669` | `video` |

### Booking Flow (3 Steps)

```
Step 1                    Step 2                    Step 3
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Select Provider  │     │ Patient Info      │     │ Confirmation     │
│ ┌──────────────┐ │     │ Name: [........] │     │ Date: Feb 24     │
│ │ Dr. Smith    │ │     │ DOB:  [........] │     │ Time: 10:30 AM   │
│ │ Cardiology   │ │     │ Reason: [......] │     │ Dr: Smith        │
│ └──────────────┘ │     │ Insurance:       │     │ Loc: Main Clinic │
│ Date: [Feb 24 ]  │     │ [BlueCross v]    │     │ [Map Link]       │
│ Time: [10:30  v]  │     │ Upload card: [+] │     │ Reminders:       │
│                  │     │                  │     │ [x]SMS [x]Email  │
│ [Next ->]        │     │ [<- Back] [Next] │     │ [ ]Push          │
└──────────────────┘     └──────────────────┘     │ [Add to Calendar]│
                                                  │ [Confirm Booking]│
                                                  └──────────────────┘
```

### Rescheduling & Cancellation

- Require reason selection (dropdown: conflict, illness, provider request, other)
- Show alternative available slots immediately
- Enforce cancellation policy window (e.g., 24h before)
- Display fee warning if inside cancellation window
- Log all changes to appointment audit trail

---

## 2. Appointment Queue / Waiting Room

### Status Progression

```
Scheduled --> Checked-in --> In Exam Room --> With Provider --> Checkout
  [Gray]       [Blue]        [Teal]          [Green]         [Purple]
```

### Queue Display

```
┌──────────────────────────────────────────────────────────────────┐
│ Today's Queue - Main Clinic                    Feb 24, 2026     │
├────────┬──────────┬───────────┬──────────┬───────────┬──────────┤
│ Patient│ Sched.   │ Status    │ Wait     │ Provider  │ Actions  │
├────────┼──────────┼───────────┼──────────┼───────────┼──────────┤
│ John D.│ 9:00 AM  │ [With Dr] │ --       │ Dr.Smith  │          │
│ Mary S.│ 9:30 AM  │ [In Room] │ 12 min   │ Dr.Smith  │ [Move]   │
│ Bob K. │ 10:00 AM │ [CheckedIn│ 25 min ! │ Dr.Jones  │ [Room]   │
│ Kim L. │ 10:30 AM │ [Sched]   │ --       │ Dr.Jones  │ [CheckIn]│
│ Pat R. │ 11:00 AM │ [Sched]   │ --       │ Dr.Kim    │ [NoShow] │
└────────┴──────────┴───────────┴──────────┴───────────┴──────────┘
  ! = Wait exceeds threshold (>20 min = amber, >40 min = red)
```

**Quick actions:** Check-in, Move to room, Mark no-show, Reschedule.

**Web:** DataTable with real-time updates (AJAX polling every 30s or WebSocket). Status badges as colored Tabler `badge` components. Countdown timer JS for wait column.

**Android:** `LazyColumn` with `AssistChip` status indicators. `SwipeRefresh` for pull-to-refresh. `WorkManager` for background status sync.

```kotlin
@Composable
fun QueueStatusChip(status: AppointmentStatus) {
    val (color, label) = when (status) {
        AppointmentStatus.SCHEDULED -> Pair(Color.Gray, "Scheduled")
        AppointmentStatus.CHECKED_IN -> Pair(ClinicalBlue, "Checked In")
        AppointmentStatus.IN_ROOM -> Pair(ClinicalTeal, "In Room")
        AppointmentStatus.WITH_PROVIDER -> Pair(ClinicalGreen, "With Provider")
        AppointmentStatus.CHECKOUT -> Pair(ClinicalPurple, "Checkout")
    }
    AssistChip(
        onClick = {},
        label = { Text(label, color = Color.White) },
        colors = AssistChipDefaults.assistChipColors(containerColor = color)
    )
}
```

---

## 3. Pre-Visit Preparation

### Pre-Visit Questionnaire

- Digital form sent via SMS/email link (token-authenticated, HIPAA-compliant)
- Captures: chief complaint, symptom duration, current medications, allergies updates
- Auto-saves progress, mobile-optimized responsive layout
- Submission triggers status update on provider dashboard

### Required Documents Checklist

| Document | Status | Action |
|----------|--------|--------|
| Insurance Card (front/back) | Uploaded | [View] |
| Photo ID | Pending | [Upload] |
| Consent Forms | Signed | [View] |
| Prior Auth Letter | N/A | -- |

### Pre-Visit Summary for Providers

```
┌─────────────────────────────────────────────┐
│ PRE-VISIT SUMMARY: John Doe, M, 45y        │
│ MRN: 1234567 | Allergies: Penicillin        │
├─────────────────────────────────────────────┤
│ [v] History Highlights                      │
│     - Hypertension (dx 2020), Type 2 DM     │
│     - Coronary stent placed Jan 2025         │
│ [v] Current Medications                     │
│     - Metformin 500mg BID                    │
│     - Lisinopril 10mg QD                     │
│     - Aspirin 81mg QD                        │
│ [v] Recent Labs (Feb 10, 2026)              │
│     - HbA1c: 7.2% (↑ from 6.8)             │
│     - LDL: 110 mg/dL [Warning]              │
│ [>] Chief Complaint (from questionnaire)     │
│     "Increased fatigue, 3 weeks duration"    │
│ [>] Open Orders & Pending Results            │
│ [>] Last Vitals (Feb 10): BP 138/88, HR 78  │
└─────────────────────────────────────────────┘
  [v] = expanded  [>] = collapsed
```

**Web:** Collapsible Tabler accordion cards beside the schedule view. PHP renders server-side with AJAX expand/collapse.

**Android:** `ExpandableCard` composable with `AnimatedVisibility` for section toggle. Lazy-load sections from API.

---

## 4. Telemedicine Video Consultation

### Pre-Call Tech Check

Verify before connecting: camera, microphone, speaker, network speed. Show pass/fail indicators. Provide troubleshooting links for failures. Minimum bandwidth requirement: 1.5 Mbps.

### Video Call Interface

```
┌─────────────────────────────────────────────────────────────────┐
│ Telemedicine Session - Dr. Smith & John Doe        [00:12:34]  │
├──────────────────────────────────────────┬──────────────────────┤
│                                          │ Patient: John Doe    │
│                                          │ MRN: 1234567         │
│       MAIN VIDEO (Provider/Patient)      │ Allergies: Penicillin│
│                                          ├──────────────────────┤
│                                          │ Vitals (last):       │
│              ┌──────────┐                │ BP: 138/88 HR: 78    │
│              │ Self-View│                │ SpO2: 97%            │
│              │ (small)  │                ├──────────────────────┤
│              └──────────┘                │ Medications:         │
│                                          │ - Metformin 500mg    │
├──────────────────────────────────────────┤ - Lisinopril 10mg    │
│ [Mute] [Video] [Share] [Chat] [Rx] [End]│ - Aspirin 81mg       │
├──────────────────────────────────────────┼──────────────────────┤
│ TRANSCRIPT (AI-powered, real-time)       │ Notes:               │
│ Dr: "How has your fatigue been?"         │ [........................]│
│ Pt: "Worse in the mornings, better by"   │ [........................]│
│ Dr: "Any chest pain or shortness of—"    │ [Save Note]          │
│ >> KEY: HbA1c 7.2% flagged in context    │                      │
└──────────────────────────────────────────┴──────────────────────┘
```

### In-Call Actions

| Action | Web | Android |
|--------|-----|---------|
| Mute/Unmute | WebRTC `audioTrack.enabled` toggle | CameraX audio toggle |
| Video On/Off | WebRTC `videoTrack.enabled` toggle | CameraX video toggle |
| Screen Share | `getDisplayMedia()` API | MediaProjection API |
| Chat | WebSocket sidebar panel | `ModalBottomSheet` overlay |
| Share Rx | Open prescription modal | Navigate to Rx composable |
| End Call | `RTCPeerConnection.close()` | Release CameraX + WebRTC |

### Post-Call Workflow

1. **Auto-generated visit summary** -- AI transcription produces structured SOAP note draft
2. **Prescription issuance** -- Provider reviews/signs e-prescriptions
3. **Follow-up scheduling** -- Suggest next appointment with pre-filled context
4. **Patient satisfaction** -- 1-5 star rating + optional comment within 24h

### Accessibility Features

| Feature | Implementation |
|---------|---------------|
| Real-time captions | AI speech-to-text overlay, toggleable by patient/provider |
| Large text mode | `font-scale` multiplier (1.5x), affects all UI text |
| Low-bandwidth fallback | Auto-detect < 500kbps, switch to audio-only with profile photo |
| High-contrast mode | WCAG AAA contrast for all video overlay controls |

**Web:** WebRTC via `RTCPeerConnection`, HTML5 `<video>` elements, Tabler sidebar for patient context. Transcript via Web Speech API or HIPAA-compliant transcription service.

```javascript
// Web - Basic WebRTC setup (simplified)
const pc = new RTCPeerConnection(iceConfig);
const localStream = await navigator.mediaDevices.getUserMedia({
    video: { width: 1280, height: 720 },
    audio: { echoCancellation: true, noiseSuppression: true }
});
localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
document.getElementById('localVideo').srcObject = localStream;

pc.ontrack = (event) => {
    document.getElementById('remoteVideo').srcObject = event.streams[0];
};
```

**Android:** CameraX for local preview + WebRTC for transmission. Overlay composables for controls.

```kotlin
@Composable
fun TelemedicineCallScreen(sessionId: String, viewModel: TelemedViewModel) {
    val callState by viewModel.callState.collectAsState()

    Box(modifier = Modifier.fillMaxSize()) {
        // Remote video (full screen)
        AndroidView(factory = { ctx -> SurfaceViewRenderer(ctx).apply {
            viewModel.attachRemoteRenderer(this)
        }}, modifier = Modifier.fillMaxSize())

        // Self-view (picture-in-picture)
        AndroidView(factory = { ctx -> SurfaceViewRenderer(ctx).apply {
            viewModel.attachLocalRenderer(this)
        }}, modifier = Modifier
            .size(120.dp, 160.dp)
            .align(Alignment.BottomStart)
            .padding(16.dp))

        // Controls bar
        TelemedControlBar(
            isMuted = callState.isMuted,
            isVideoOn = callState.isVideoOn,
            onToggleMute = viewModel::toggleMute,
            onToggleVideo = viewModel::toggleVideo,
            onEndCall = viewModel::endCall,
            modifier = Modifier.align(Alignment.BottomCenter)
        )

        // Side panel - patient context
        if (callState.showSidePanel) {
            PatientContextPanel(
                patient = callState.patient,
                modifier = Modifier.align(Alignment.CenterEnd).width(280.dp)
            )
        }
    }
}
```

---

## 5. Multi-Channel Communication

### Supported Channels During Visit

| Channel | Use Case | Fallback |
|---------|----------|----------|
| Video call | Primary telemedicine consult | Audio call |
| Audio call | Low-bandwidth or patient preference | Secure chat |
| Secure chat | Quick questions, async follow-up | Async message |
| Document share | Lab results, imaging, Rx | Secure portal |

### Channel Switching

- Maintain session context when switching (e.g., video to audio)
- Transfer transcript and notes across channels
- Log channel changes in visit record

**Web:** Tabbed communication panel with three tabs: Video | Chat | Documents. WebSocket maintains session state across tab switches.

```html
<!-- Web - Tabler tabbed communication panel -->
<div class="card">
  <div class="card-header">
    <ul class="nav nav-tabs card-header-tabs">
      <li class="nav-item">
        <a class="nav-link active" data-bs-toggle="tab" href="#video-tab">Video</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#chat-tab">Chat</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#docs-tab">Documents</a>
      </li>
    </ul>
  </div>
  <div class="card-body tab-content">
    <div class="tab-pane active" id="video-tab"><!-- WebRTC video --></div>
    <div class="tab-pane" id="chat-tab"><!-- Secure chat messages --></div>
    <div class="tab-pane" id="docs-tab"><!-- Shared documents list --></div>
  </div>
</div>
```

**Android:** `BottomSheet` with channel options. Shared `ViewModel` preserves context across channel composables.

---

## 6. Notification & Reminder System

### Reminder Schedule

| Timing | Channel | Content |
|--------|---------|---------|
| 48h before | Email | Full details + prep instructions + map/link |
| 24h before | SMS + Push | Date, time, provider, location/join link |
| 2h before | Push | "Your appointment is in 2 hours" + quick actions |
| At time | Push (telemedicine) | "Join now" deep-link to video session |

All timing is configurable per patient preference. Respect do-not-disturb hours.

### Reminder Content Template

```
Your appointment with Dr. Smith is on Feb 24 at 10:30 AM.
Location: Main Clinic, Room 204
Preparation: Please fast for 8 hours before your visit.
[View Details] [Reschedule] [Cancel]
```

### No-Show Follow-Up

- Auto-trigger outreach 15 min after missed appointment
- Sequence: Push notification -> SMS (30 min) -> Email (1h) -> Staff call (2h)
- Offer one-tap reschedule link in all communications
- Log no-show reason if patient responds

**Web:** Email templates (PHP Blade/Twig) + SMS via Twilio/Vonage API. Cron job triggers reminders at scheduled intervals.

```php
// PHP - Reminder scheduling
class AppointmentReminderService {
    public function scheduleReminders(Appointment $appt): void {
        $reminders = [
            ['offset' => '-48 hours', 'channel' => 'email'],
            ['offset' => '-24 hours', 'channel' => 'sms'],
            ['offset' => '-2 hours',  'channel' => 'push'],
        ];
        foreach ($reminders as $r) {
            ReminderQueue::create([
                'appointment_id' => $appt->id,
                'send_at' => Carbon::parse($appt->scheduled_at)->modify($r['offset']),
                'channel' => $r['channel'],
                'status' => 'pending',
            ]);
        }
    }
}
```

**Android:** `WorkManager` for scheduled local notifications. Deep-link to appointment detail or telemedicine join screen.

```kotlin
class AppointmentReminderWorker(
    context: Context, params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val appointmentId = inputData.getLong("appointment_id", -1)
        val appointment = appointmentRepo.getById(appointmentId) ?: return Result.failure()

        notificationManager.showAppointmentReminder(
            title = "Upcoming Appointment",
            body = "Your appointment with ${appointment.providerName} is in 2 hours",
            deepLink = "healthapp://appointments/${appointment.id}"
        )
        return Result.success()
    }
}

// Schedule reminders when appointment is booked
fun scheduleReminders(appointment: Appointment) {
    val intervals = listOf(
        Duration.ofHours(48) to "48h reminder",
        Duration.ofHours(24) to "24h reminder",
        Duration.ofHours(2)  to "2h reminder"
    )
    intervals.forEach { (offset, tag) ->
        val delay = Duration.between(
            Instant.now(),
            appointment.scheduledAt.toInstant().minus(offset)
        )
        if (delay.isNegative) return@forEach
        val request = OneTimeWorkRequestBuilder<AppointmentReminderWorker>()
            .setInitialDelay(delay.toMillis(), TimeUnit.MILLISECONDS)
            .setInputData(workDataOf("appointment_id" to appointment.id))
            .addTag("reminder_${appointment.id}_$tag")
            .build()
        WorkManager.getInstance(context).enqueue(request)
    }
}
```

---

## Cross-Cutting Concerns

- **HIPAA:** All video/audio streams must be encrypted (TLS 1.3 + SRTP for WebRTC). Transcripts are PHI -- store encrypted, log access.
- **Audit:** Log every appointment create/update/cancel, every video session start/end, every document share.
- **Offline (Android):** Cache upcoming appointment list. Queue check-in actions for sync. Show "offline" indicator on telemedicine features.
- **Accessibility:** All calendar interactions keyboard-navigable. Screen reader announcements for status changes (`aria-live`). Touch targets minimum 48dp (Android) / 44px (Web).
