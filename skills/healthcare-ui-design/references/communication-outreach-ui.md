# Communication & Patient Outreach UI Patterns

Dual-platform: Web (Bootstrap 5/Tabler + PHP) and Android (Jetpack Compose + Material 3).

---

## 1. Secure Messaging System

**Layout:** Desktop 3-panel (conversations | chat | patient context), tablet 2-panel (conversations 40% | chat 60%), mobile full-screen list or chat with back nav.

**Left:** Conversation list with Open/Recent/All tabs, unread badges, search. **Center:** Message bubbles + delivery status + composer (attach, template, send). **Right (desktop):** Patient name, MRN, allergies, vitals, shared docs.

**Message types:** Text (2000 chars), Image (JPEG/PNG <512KB), Document (PDF <10MB, virus-scanned), Audio (MP3/AAC, 2 min max). **Delivery:** Sent > Delivered > Read (blue double-check + timestamp).

**Rules:** Patient threads use plain language with template suggestions. Provider threads allow clinical shorthand and DICOM links. E2E encryption lock icon in header. PHI warning on external shares. Templates support `{patient_name}`, `{provider_name}`, `{appointment_date}` tokens.

### Web: Three-Panel Chat

```html
<div class="row g-0" style="height:calc(100vh - 60px);">
  <!-- Left: Conversation list (col-lg-3 col-md-4) -->
  <div class="col-lg-3 col-md-4 border-end d-flex flex-column">
    <div class="p-3 border-bottom">
      <input type="text" class="form-control" placeholder="Search conversations...">
    </div>
    <ul class="nav nav-pills nav-fill px-2 py-2">
      <li class="nav-item"><a class="nav-link active" href="#">Open</a></li>
      <li class="nav-item"><a class="nav-link" href="#">Recent</a></li>
      <li class="nav-item"><a class="nav-link" href="#">All</a></li>
    </ul>
    <div class="list-group list-group-flush overflow-auto flex-grow-1">
      <!-- Conversation items with unread badge -->
    </div>
  </div>
  <!-- Center: Active chat (col-lg-6 col-md-8) -->
  <div class="col-lg-6 col-md-8 d-flex flex-column">
    <div class="card-header d-flex align-items-center border-bottom p-3">
      <span class="avatar avatar-sm me-2"></span>
      <div><strong>Jane Doe</strong><br><small class="text-muted">Online</small></div>
      <i class="ti ti-lock ms-2 text-success" title="End-to-end encrypted"></i>
    </div>
    <div class="flex-grow-1 overflow-auto p-3" id="messageArea"></div>
    <div class="border-top p-3"><div class="input-group">
      <button class="btn btn-outline-secondary"><i class="ti ti-paperclip"></i></button>
      <button class="btn btn-outline-secondary"><i class="ti ti-template"></i></button>
      <input type="text" class="form-control" placeholder="Type a message...">
      <button class="btn btn-primary"><i class="ti ti-send"></i></button>
    </div></div>
  </div>
  <!-- Right: Patient context (col-lg-3, desktop only) -->
  <div class="col-lg-3 d-none d-lg-flex flex-column border-start overflow-auto">
    <div class="p-3">
      <div class="card card-sm mb-2"><div class="card-body">
        <strong>Jane Doe</strong>, F, 42 | MRN: 7823
        <div class="text-danger fw-bold mt-1">Allergy: Sulfa</div>
      </div></div>
    </div>
  </div>
</div>
```

### Android: Adaptive Messaging

```kotlin
@Composable
fun SecureMessagingScreen(viewModel: MessagingViewModel = hiltViewModel()) {
    val conversations by viewModel.conversations.collectAsStateWithLifecycle()
    val activeChat by viewModel.activeChat.collectAsStateWithLifecycle()
    val windowSize = currentWindowAdaptiveInfo().windowSizeClass
    when (windowSize.widthSizeClass) {
        WindowWidthSizeClass.Expanded -> TwoPanelMessaging(conversations, activeChat, viewModel)
        else -> if (activeChat != null) ChatDetailScreen(activeChat!!, viewModel)
                else ConversationListScreen(conversations, viewModel)
    }
}

@Composable
fun ChatDetailScreen(chat: ChatDetail, viewModel: MessagingViewModel) {
    val messages by viewModel.messages.collectAsStateWithLifecycle()
    Scaffold(
        topBar = { ChatTopBar(chat.participant, isEncrypted = true) },
        bottomBar = { MessageComposer(onSend = { viewModel.send(it) },
            onAttach = { viewModel.showAttachSheet() }) }
    ) { padding ->
        LazyColumn(Modifier.padding(padding).fillMaxSize(), reverseLayout = true) {
            items(messages, key = { it.id }) { msg ->
                MessageBubble(msg, isOwn = msg.senderId == viewModel.currentUserId)
            }
        }
    }
    // ModalBottomSheet for attachment options (image, document, audio)
}
```

---

## 2. Multi-Provider Communication

Group threads linked to patient records. @mention autocomplete for team members. Priority flags: Normal, Important (amber), Urgent (red + sound). Case discussion threads branch from main chat. **Handoff notes:** Patient ID (auto-filled), Condition Summary, Active Issues (bullets), Pending Items (checklist), Notes (free text).

### Web: Thread-Based Team Chat

```html
<div class="card">
  <div class="card-header d-flex align-items-center">
    <span class="avatar-list avatar-list-stacked me-2">
      <span class="avatar avatar-xs">DS</span><span class="avatar avatar-xs">MJ</span>
      <span class="avatar avatar-xs">+3</span>
    </span>
    <h3 class="card-title mb-0">Care Team: Jane Doe (MRN 7823)</h3>
    <span class="badge bg-red ms-auto">Urgent</span>
  </div>
  <div class="card-body overflow-auto" style="max-height:400px;">
    <div class="mb-2">
      <strong>Dr. Smith</strong> <small class="text-muted">10:15</small>
      <p><span class="badge bg-blue-lt">@nurse.johnson</span> Please check BP every 2h.</p>
    </div>
  </div>
  <div class="card-footer">
    <div class="input-group">
      <span class="input-group-text">@</span>
      <input type="text" class="form-control" placeholder="Message care team...">
      <button class="btn btn-warning"><i class="ti ti-flag"></i></button>
      <button class="btn btn-primary"><i class="ti ti-send"></i></button>
    </div>
  </div>
</div>
```

### Android: Group Chat with Mention Chips

```kotlin
@Composable
fun CareTeamChat(viewModel: CareTeamViewModel = hiltViewModel()) {
    val members by viewModel.members.collectAsStateWithLifecycle()
    val messages by viewModel.messages.collectAsStateWithLifecycle()
    Scaffold(
        topBar = { TopAppBar(title = { Text("Care Team: ${viewModel.patientName}") },
            actions = { PriorityFlagButton(viewModel.priority, onChange = { viewModel.setPriority(it) }) }) },
        bottomBar = { MentionComposer(members, onSend = { viewModel.send(it) }) }
    ) { padding ->
        LazyColumn(Modifier.padding(padding), reverseLayout = true) {
            items(messages, key = { it.id }) { CareTeamMessageBubble(it) }
        }
    }
}

// MentionComposer: OutlinedTextField that triggers LazyRow of SuggestionChips
// when user types "@". Chip tap inserts "@name " into text field.
```

---

## 3. Patient Outreach Campaigns

**Dashboard:** Active/inactive campaign list with toggle, performance metrics (sent, delivered, opened, responded), stat cards at top.

**Builder steps:** 1) Audience filters (age, condition, last visit, risk level, insurance) 2) Template editor with `{patient_name}`, `{provider_name}`, `{appointment_date}` tokens 3) Channel selection (email, SMS, push, portal) 4) Schedule (now/delayed/recurring) 5) Review + confirm.

**Anti-spam:** Show patient's active subscriptions, frequency cap (default 3/week), one-tap unsubscribe, outbound audit log.

### Web: Campaign Dashboard

```html
<div class="row row-cards mb-3">
  <div class="col-sm-6 col-lg-3">
    <div class="card card-sm"><div class="card-body">
      <div class="text-muted">Active Campaigns</div><div class="h1 mb-0">4</div>
    </div></div>
  </div>
  <div class="col-sm-6 col-lg-3">
    <div class="card card-sm"><div class="card-body">
      <div class="text-muted">Total Sent (Month)</div><div class="h1 mb-0">3,240</div>
    </div></div>
  </div>
</div>
<div class="card">
  <div class="card-header d-flex">
    <h3 class="card-title">Campaigns</h3>
    <button class="btn btn-primary ms-auto"><i class="ti ti-plus"></i> New Campaign</button>
  </div>
  <table class="table table-hover" id="campaignTable">
    <thead><tr><th>Name</th><th>Status</th><th>Sent</th><th>Delivered</th>
      <th>Opened</th><th>Responded</th><th>Actions</th></tr></thead>
  </table>
</div>
```

### Android: Campaign Cards

```kotlin
@Composable
fun CampaignListScreen(viewModel: CampaignViewModel = hiltViewModel()) {
    val campaigns by viewModel.campaigns.collectAsStateWithLifecycle()
    Scaffold(floatingActionButton = {
        ExtendedFloatingActionButton(onClick = { viewModel.createNew() },
            icon = { Icon(Icons.Default.Add, null) }, text = { Text("New Campaign") })
    }) { padding ->
        LazyColumn(Modifier.padding(padding), contentPadding = PaddingValues(12.dp),
                   verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(campaigns, key = { it.id }) { c ->
                ElevatedCard(Modifier.fillMaxWidth()) { Column(Modifier.padding(16.dp)) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(c.name, style = MaterialTheme.typography.titleMedium)
                        Switch(checked = c.isActive, onCheckedChange = { viewModel.toggleStatus(c) })
                    }
                    Row(Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceEvenly) {
                        MetricColumn("Sent", "${c.sent}"); MetricColumn("Delivered", "${c.delivered}")
                        MetricColumn("Opened", "${c.opened}"); MetricColumn("Responded", "${c.responded}")
                    }
                } }
            }
        }
    }
}
```

---

## 4. Pre-Appointment Screening

Digital questionnaire sent via SMS/email link. Provider sees pre-populated summary during appointment. **Components:** Pill-button symptom selection (multi-select), pain scale slider (0-10), Yes/No segmented buttons, free text (500 chars), symptom search with ICD autocomplete.

### Web: Mobile-Friendly Survey

```html
<form class="card" id="screeningForm">
  <div class="card-header"><h3 class="card-title">Pre-Visit Screening</h3></div>
  <div class="card-body">
    <label class="form-label fw-bold">Select current symptoms:</label>
    <div class="d-flex flex-wrap gap-2 mb-3">
      <input type="checkbox" class="btn-check" id="sym-headache" autocomplete="off">
      <label class="btn btn-outline-primary btn-pill" for="sym-headache">Headache</label>
      <input type="checkbox" class="btn-check" id="sym-fever" autocomplete="off">
      <label class="btn btn-outline-primary btn-pill" for="sym-fever">Fever</label>
      <input type="checkbox" class="btn-check" id="sym-cough" autocomplete="off">
      <label class="btn btn-outline-primary btn-pill" for="sym-cough">Cough</label>
    </div>
    <label class="form-label fw-bold">Pain level (0-10):</label>
    <input type="range" class="form-range" min="0" max="10" step="1" id="painScale">
    <div class="d-flex justify-content-between"><small>0</small><small>5</small><small>10</small></div>
    <label class="form-label fw-bold mt-3">Do you have a fever?</label>
    <div class="btn-group w-100" role="group">
      <input type="radio" class="btn-check" name="fever" id="fever-yes">
      <label class="btn btn-outline-primary" for="fever-yes">Yes</label>
      <input type="radio" class="btn-check" name="fever" id="fever-no">
      <label class="btn btn-outline-primary" for="fever-no">No</label>
    </div>
    <label class="form-label fw-bold mt-3">Additional details:</label>
    <textarea class="form-control" rows="3" maxlength="500"></textarea>
  </div>
  <div class="card-footer"><button type="submit" class="btn btn-primary w-100">Submit</button></div>
</form>
```

### Android: Screening Composable

```kotlin
@Composable
fun PreScreeningForm(viewModel: ScreeningViewModel = hiltViewModel()) {
    val symptoms = listOf("Headache", "Fever", "Cough", "Fatigue", "Nausea", "Chest Pain")
    val selected by viewModel.selectedSymptoms.collectAsStateWithLifecycle()
    val painLevel by viewModel.painLevel.collectAsStateWithLifecycle()
    LazyColumn(Modifier.fillMaxSize().padding(16.dp)) {
        item { // Symptom chips (FlowRow with FilterChip per symptom)
            Text("Select current symptoms:", style = MaterialTheme.typography.titleMedium)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)) {
                symptoms.forEach { s -> FilterChip(selected = s in selected,
                    onClick = { viewModel.toggleSymptom(s) }, label = { Text(s) }) }
            }
        }
        item { // Pain slider 0-10
            Text("Pain level: ${painLevel.toInt()}/10", style = MaterialTheme.typography.titleMedium)
            Slider(value = painLevel, onValueChange = { viewModel.setPain(it) },
                   valueRange = 0f..10f, steps = 9)
        }
        item { // Yes/No segmented button + free text + submit
            Text("Do you have a fever?", style = MaterialTheme.typography.titleMedium)
            SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) {
                SegmentedButton(selected = viewModel.hasFever == true, onClick = { viewModel.setFever(true) },
                    shape = SegmentedButtonDefaults.itemShape(0, 2), label = { Text("Yes") })
                SegmentedButton(selected = viewModel.hasFever == false, onClick = { viewModel.setFever(false) },
                    shape = SegmentedButtonDefaults.itemShape(1, 2), label = { Text("No") })
            }
            OutlinedTextField(value = viewModel.additionalNotes, onValueChange = { viewModel.setNotes(it) },
                label = { Text("Additional details") }, modifier = Modifier.fillMaxWidth(), maxLines = 5)
            Button(onClick = { viewModel.submit() }, modifier = Modifier.fillMaxWidth()) {
                Text("Submit Screening") }
        }
    }
}
```

---

## 5. Health Bot / Post-Discharge Monitoring

Automated check-ins at Day 1 (pain/wound/meds), Day 3 (symptom changes), Day 7 (recovery), Day 14 (follow-up). Escalation triggers: pain > 7, new symptoms, no improvement, fever. **UI:** Chat bubbles with bot avatar, quick-reply buttons, escalation to human provider on threshold, summary report for care team. Log unanswered/failed attempts.

### Web: Floating Chat Widget

```html
<div id="healthBot" class="position-fixed bottom-0 end-0 m-3" style="width:360px;z-index:1050;">
  <div class="card shadow-lg">
    <div class="card-header bg-primary text-white d-flex align-items-center">
      <span class="avatar avatar-sm bg-white text-primary me-2">Bot</span>
      <strong>Recovery Check-In</strong>
      <button class="btn-close btn-close-white ms-auto"></button>
    </div>
    <div class="card-body overflow-auto" style="height:350px;" id="botMessages">
      <div class="mb-2"><div class="bg-light rounded p-2 d-inline-block">
        How is your pain today?</div></div>
    </div>
    <div class="card-footer">
      <div class="d-flex flex-wrap gap-2">
        <button class="btn btn-sm btn-outline-success quick-reply">0-3 Mild</button>
        <button class="btn btn-sm btn-outline-warning quick-reply">4-6 Moderate</button>
        <button class="btn btn-sm btn-outline-danger quick-reply">7+ Severe</button>
      </div>
    </div>
  </div>
</div>
```

### Android: Bot Chat Composable

```kotlin
@Composable
fun HealthBotScreen(viewModel: HealthBotViewModel = hiltViewModel()) {
    val messages by viewModel.botMessages.collectAsStateWithLifecycle()
    val quickReplies by viewModel.quickReplies.collectAsStateWithLifecycle()
    Scaffold(topBar = { TopAppBar(title = { Text("Recovery Check-In") },
        navigationIcon = { BotAvatar() }) }) { padding ->
        Column(Modifier.padding(padding).fillMaxSize()) {
            LazyColumn(Modifier.weight(1f).padding(horizontal = 12.dp), reverseLayout = true) {
                items(messages, key = { it.id }) { BotMessageBubble(it) }
            }
            if (quickReplies.isNotEmpty()) {
                FlowRow(Modifier.padding(12.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    quickReplies.forEach { r ->
                        OutlinedButton(onClick = { viewModel.selectReply(r) }) { Text(r.label) }
                    }
                }
            }
        }
    }
}
```

---

## 6. Notification System Architecture

**Types:** Clinical (lab results, vital alerts, med reminders -- High/Critical -- in-app, push, SMS), Administrative (appt reminders, billing -- Normal -- in-app, push, email), Communication (messages, care team -- Normal/High -- in-app, push). **Priority:** Critical bypasses DND + requires ack. High respects DND. Normal respects quiet hours (10PM-7AM). Preferences stored per channel per type in `notification_preferences`.

### Web: Notification Dropdown

```html
<div class="nav-item dropdown">
  <a href="#" class="nav-link" data-bs-toggle="dropdown">
    <i class="ti ti-bell"></i><span class="badge bg-danger badge-notification">5</span>
  </a>
  <div class="dropdown-menu dropdown-menu-end" style="width:380px;max-height:450px;overflow:auto;">
    <div class="px-3 py-2 d-flex justify-content-between align-items-center border-bottom">
      <strong>Notifications</strong>
      <div class="btn-group btn-group-sm">
        <button class="btn btn-outline-secondary active">All</button>
        <button class="btn btn-outline-secondary">Clinical</button>
        <button class="btn btn-outline-secondary">Admin</button>
      </div>
    </div>
    <a href="#" class="dropdown-item d-flex align-items-start py-2">
      <span class="avatar avatar-sm bg-danger-lt me-2"><i class="ti ti-flask"></i></span>
      <div><div class="fw-bold">Lab Results Ready</div>
        <small class="text-muted">Jane Doe - CBC Panel</small>
        <small class="d-block text-muted">2 min ago</small></div>
    </a>
  </div>
</div>
```

### Android: Notification Channels + Deep Links

```kotlin
object HealthNotificationChannels {
    fun createAll(context: Context) {
        val mgr = context.getSystemService(NotificationManager::class.java)
        mgr.createNotificationChannels(listOf(
            NotificationChannel("clinical_critical", "Critical Alerts",
                NotificationManager.IMPORTANCE_HIGH).apply { setBypassDnd(true); enableVibration(true) },
            NotificationChannel("clinical_results", "Lab Results", NotificationManager.IMPORTANCE_DEFAULT),
            NotificationChannel("admin_reminders", "Reminders", NotificationManager.IMPORTANCE_DEFAULT),
            NotificationChannel("messages", "Messages", NotificationManager.IMPORTANCE_DEFAULT)
        ))
    }
}

fun buildLabNotification(ctx: Context, patient: String, test: String): Notification {
    val intent = NavDeepLinkBuilder(ctx).setGraph(R.navigation.nav_graph)
        .setDestination(R.id.labResultFragment).createPendingIntent()
    return NotificationCompat.Builder(ctx, "clinical_results")
        .setSmallIcon(R.drawable.ic_flask).setContentTitle("Lab Results Ready")
        .setContentText("$patient - $test available").setContentIntent(intent)
        .setAutoCancel(true).build()
}
```

---

## 7. Feedback Collection

Post-visit survey: star rating (1-5), NPS (0-10), provider-specific feedback with anonymous toggle, free-text suggestions (max 500 chars). Triggered after visit completion.

### Web: Survey Modal

```html
<div class="modal fade" id="feedbackModal" tabindex="-1">
  <div class="modal-dialog modal-sm"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title">How was your visit?</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body text-center">
      <div class="mb-3" id="starRating"><!-- 5x ti-star icons, data-value 1-5 --></div>
      <label class="form-label">Recommend us? (0-10)</label>
      <input type="range" class="form-range" min="0" max="10" id="npsScore">
      <div class="form-check text-start mt-3">
        <input class="form-check-input" type="checkbox" id="anonFeedback">
        <label class="form-check-label" for="anonFeedback">Submit anonymously</label>
      </div>
      <textarea class="form-control mt-3" rows="3" placeholder="Suggestions..."></textarea>
    </div>
    <div class="modal-footer">
      <button class="btn btn-primary w-100">Submit Feedback</button></div>
  </div></div>
</div>
```

### Android: Feedback BottomSheet

```kotlin
@Composable
fun FeedbackBottomSheet(onDismiss: () -> Unit, onSubmit: (Feedback) -> Unit) {
    var rating by remember { mutableIntStateOf(0) }
    var nps by remember { mutableFloatStateOf(5f) }
    var anonymous by remember { mutableStateOf(false) }
    var comments by remember { mutableStateOf("") }
    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(Modifier.padding(24.dp).fillMaxWidth()) {
            Text("How was your visit?", style = MaterialTheme.typography.headlineSmall,
                 textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
            Spacer(Modifier.height(16.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                (1..5).forEach { s ->
                    IconButton(onClick = { rating = s }) {
                        Icon(if (s <= rating) Icons.Filled.Star else Icons.Outlined.Star,
                             tint = if (s <= rating) Color(0xFFF59F00) else Color.Gray,
                             contentDescription = "$s stars", modifier = Modifier.size(36.dp))
                    }
                }
            }
            Text("Recommend us? ${nps.toInt()}/10")
            Slider(value = nps, onValueChange = { nps = it }, valueRange = 0f..10f, steps = 9)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = anonymous, onCheckedChange = { anonymous = it })
                Text("Submit anonymously")
            }
            OutlinedTextField(value = comments, onValueChange = { comments = it },
                label = { Text("Suggestions") }, modifier = Modifier.fillMaxWidth(), maxLines = 4)
            Button(onClick = { onSubmit(Feedback(rating, nps.toInt(), anonymous, comments)) },
                   modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) { Text("Submit Feedback") }
        }
    }
}
```

---

## Compliance Reminders

- **PHI encryption:** All message content is PHI. Encrypt at rest and in transit. Never log message body in plain-text server logs.
- **Audit trail:** Log every send/receive, campaign dispatch, notification delivery, and feedback with user ID + timestamp.
- **Session timeout:** Messaging auto-locks after 15 min inactivity. Re-authenticate to resume.
- **External sharing:** PHI warning banner when sharing outside the system.
- **Consent tracking:** Record patient opt-in/opt-out per channel with timestamp and method.
