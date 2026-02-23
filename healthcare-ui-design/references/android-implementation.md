# Android Implementation Reference

Kotlin + Jetpack Compose + Material 3 + MVVM patterns for healthcare apps.
Companion to the main `healthcare-ui-design` skill. Follow `android-development` and `jetpack-compose-ui` skills as baseline.

## 1. Project Architecture

Follow `android-development` skill: MVVM + Clean Architecture + Hilt DI.

```
com.app.healthcare/
├── ui/
│   ├── theme/          # HealthcareTheme, Colors, Typography
│   ├── components/     # Reusable healthcare composables
│   ├── screens/
│   │   ├── dashboard/  # Home dashboard
│   │   ├── patients/   # Patient list, detail, search
│   │   ├── vitals/     # Vital signs entry and display
│   │   ├── medications/# Medication list, administration
│   │   ├── schedule/   # Appointments, calendar
│   │   ├── messaging/  # Secure chat
│   │   └── portal/     # Patient portal screens
│   └── navigation/     # NavHost, bottom nav, routes
├── domain/
│   ├── model/          # Patient, VitalSign, Medication, Appointment
│   └── usecase/        # Business logic
├── data/
│   ├── remote/         # API DTOs, Retrofit services
│   ├── local/          # Room entities, DAOs
│   └── repository/     # Repository implementations
└── util/               # Extensions, constants, formatters
```

Each screen folder contains `Screen.kt`, `ViewModel.kt`, and `UiState.kt`. Domain models are separate from Room entities and API DTOs -- map at the repository boundary.

## 2. Healthcare Theme Setup

### HealthcareColors.kt

```kotlin
object HealthcareColors {
    val Primary = Color(0xFF2563EB);      val PrimaryLight = Color(0xFFDBEAFE)
    val Secondary = Color(0xFF0F766E);    val SecondaryLight = Color(0xFFCCFBF1)
    val Surface = Color(0xFFF8FAFC);      val Background = Color(0xFFF1F5F9)
    val Border = Color(0xFFE2E8F0)
    val Critical = Color(0xFFDC2626);     val CriticalLight = Color(0xFFFEF2F2)
    val Warning = Color(0xFFD97706);      val WarningLight = Color(0xFFFFFBEB)
    val Success = Color(0xFF059669);      val SuccessLight = Color(0xFFECFDF5)
    val Info = Color(0xFF0284C7);         val InfoLight = Color(0xFFF0F9FF)
    val TextPrimary = Color(0xFF0F172A);  val TextSecondary = Color(0xFF334155)
    val TextMuted = Color(0xFF64748B);    val TextInverse = Color(0xFFFFFFFF)
    val Medication = Color(0xFF7C3AED);   val MedicationLight = Color(0xFFF5F3FF)
    val AllergyBg = Color(0xFFFEF2F2);   val AllergyBorder = Color(0xFFDC2626)
}
```

### HealthcareTheme.kt

```kotlin
private val HealthcareColorScheme = lightColorScheme(
    primary = HealthcareColors.Primary, onPrimary = HealthcareColors.TextInverse,
    secondary = HealthcareColors.Secondary, onSecondary = HealthcareColors.TextInverse,
    surface = HealthcareColors.Surface, onSurface = HealthcareColors.TextPrimary,
    background = HealthcareColors.Background, onBackground = HealthcareColors.TextPrimary,
    error = HealthcareColors.Critical, onError = HealthcareColors.TextInverse,
    surfaceVariant = HealthcareColors.Background, outline = HealthcareColors.Border,
)

@Composable
fun HealthcareTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = HealthcareColorScheme, typography = HealthcareTypography, content = content)
}
```

### HealthcareTypography.kt

Full type scale is in `design-tokens.md`. Clinical-specific extensions:

```kotlin
object ClinicalTextStyles {
    val VitalValue = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 24.sp, fontWeight = FontWeight.W700, lineHeight = 28.sp)
    val PatientName = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.W600, lineHeight = 24.sp)
    val MrnDisplay = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 14.sp, fontWeight = FontWeight.W500, letterSpacing = 0.8.sp)
}
```

## 3. Core Healthcare Composables

### PatientCard

```kotlin
@Composable
fun PatientCard(patient: Patient, onTap: () -> Unit, modifier: Modifier = Modifier) {
    Card(
        onClick = onTap, modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            PatientAvatar(patient.photoUrl, size = 48.dp)
            Spacer(Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(patient.fullName, style = MaterialTheme.typography.titleMedium)
                Text("${patient.gender}, ${patient.age}y | MRN: ${patient.mrn}",
                     style = MaterialTheme.typography.bodySmall, color = HealthcareColors.TextMuted)
            }
            RiskBadge(patient.riskLevel)
        }
        if (patient.allergies.isNotEmpty()) { AllergyBanner(patient.allergies) }
    }
}
```

### AllergyBanner (ALWAYS Visible -- Never Hide)

Allergy visibility is a patient safety requirement. Never hide, collapse, or scroll off-screen.

```kotlin
@Composable
fun AllergyBanner(allergies: List<String>, modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        color = HealthcareColors.AllergyBg, border = BorderStroke(1.dp, HealthcareColors.AllergyBorder)
    ) {
        Row(Modifier.padding(horizontal = 16.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Warning, contentDescription = "Allergy", tint = HealthcareColors.Critical)
            Spacer(Modifier.width(8.dp))
            Text("Allergies: ${allergies.joinToString(", ")}",
                 style = MaterialTheme.typography.labelMedium, color = HealthcareColors.Critical,
                 modifier = Modifier.semantics { stateDescription = "Patient has allergies" })
        }
    }
}
```

### VitalSignCard

```kotlin
enum class VitalStatus(val label: String) { NORMAL("Normal"), WARNING("Warning"), CRITICAL("Critical") }
enum class VitalTrend { UP, DOWN, STABLE }

@Composable
fun VitalSignCard(label: String, value: String, unit: String, status: VitalStatus, trend: VitalTrend? = null) {
    val statusColor = when (status) {
        VitalStatus.NORMAL -> HealthcareColors.Success
        VitalStatus.WARNING -> HealthcareColors.Warning
        VitalStatus.CRITICAL -> HealthcareColors.Critical
    }
    Card(colors = CardDefaults.cardColors(containerColor = statusColor.copy(alpha = 0.1f))) {
        Column(Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text(label, style = MaterialTheme.typography.labelSmall, color = HealthcareColors.TextMuted)
            Row(verticalAlignment = Alignment.Bottom) {
                Text(value, style = MaterialTheme.typography.headlineMedium.copy(
                    fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold), color = statusColor)
                trend?.let { TrendArrow(it) }
            }
            Text("$unit - ${status.label}", style = MaterialTheme.typography.labelSmall)
        }
    }
}

@Composable
fun TrendArrow(trend: VitalTrend) {
    val (icon, color) = when (trend) {
        VitalTrend.UP -> Icons.Default.TrendingUp to HealthcareColors.Critical
        VitalTrend.DOWN -> Icons.Default.TrendingDown to HealthcareColors.Success
        VitalTrend.STABLE -> Icons.Default.TrendingFlat to HealthcareColors.TextMuted
    }
    Icon(icon, contentDescription = trend.name, tint = color, modifier = Modifier.size(20.dp))
}
```

### ClinicalAlert

```kotlin
enum class AlertLevel { CRITICAL, WARNING, INFO, SUCCESS }

@Composable
fun ClinicalAlert(
    level: AlertLevel, title: String, message: String,
    onAcknowledge: (() -> Unit)? = null, onDismiss: (() -> Unit)? = null
) {
    val (bgColor, icon) = when (level) {
        AlertLevel.CRITICAL -> HealthcareColors.Critical to Icons.Default.GppBad
        AlertLevel.WARNING -> HealthcareColors.Warning to Icons.Default.Warning
        AlertLevel.INFO -> HealthcareColors.Info to Icons.Default.Info
        AlertLevel.SUCCESS -> HealthcareColors.Success to Icons.Default.CheckCircle
    }
    Surface(
        modifier = Modifier.fillMaxWidth().semantics { liveRegion = LiveRegionMode.Assertive },
        color = bgColor.copy(alpha = 0.1f), border = BorderStroke(1.dp, bgColor)
    ) {
        Row(Modifier.padding(16.dp)) {
            Icon(icon, contentDescription = level.name, tint = bgColor)
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.titleSmall, color = bgColor)
                Spacer(Modifier.height(4.dp))
                Text(message, style = MaterialTheme.typography.bodySmall)
            }
            onAcknowledge?.let {
                Button(onClick = it, colors = ButtonDefaults.buttonColors(containerColor = bgColor)) {
                    Text("Acknowledge")
                }
            }
            onDismiss?.let {
                IconButton(onClick = it) { Icon(Icons.Default.Close, contentDescription = "Dismiss") }
            }
        }
    }
}
```

## 4. Navigation Structure

```kotlin
sealed class HealthcareRoute(val route: String) {
    object Dashboard : HealthcareRoute("dashboard")
    object PatientList : HealthcareRoute("patients")
    object PatientDetail : HealthcareRoute("patients/{patientId}")
    object VitalsEntry : HealthcareRoute("patients/{patientId}/vitals/entry")
    object MedicationAdmin : HealthcareRoute("patients/{patientId}/medications/admin")
    object Scheduling : HealthcareRoute("scheduling")
    object Messages : HealthcareRoute("messages")
    object Profile : HealthcareRoute("profile")
}

val bottomNavItems = listOf(
    BottomNavItem("Home", Icons.Default.Home, HealthcareRoute.Dashboard.route),
    BottomNavItem("Patients", Icons.Default.People, HealthcareRoute.PatientList.route),
    BottomNavItem("Schedule", Icons.Default.CalendarMonth, HealthcareRoute.Scheduling.route),
    BottomNavItem("Messages", Icons.Default.Chat, HealthcareRoute.Messages.route),
    BottomNavItem("Profile", Icons.Default.Person, HealthcareRoute.Profile.route),
)

@Composable
fun HealthcareNavHost(navController: NavHostController) {
    NavHost(navController = navController, startDestination = HealthcareRoute.Dashboard.route) {
        composable(HealthcareRoute.Dashboard.route) { DashboardScreen(navController) }
        composable(HealthcareRoute.PatientList.route) { PatientListScreen(navController) }
        composable(HealthcareRoute.PatientDetail.route,
            arguments = listOf(navArgument("patientId") { type = NavType.StringType })
        ) { entry -> PatientDetailScreen(entry.arguments?.getString("patientId") ?: "", navController) }
        composable(HealthcareRoute.Scheduling.route) { SchedulingScreen(navController) }
        composable(HealthcareRoute.Messages.route) { MessagesScreen(navController) }
        composable(HealthcareRoute.Profile.route) { ProfileScreen(navController) }
    }
}
```

## 5. Accessibility for Healthcare (Compose)

### Semantics on Clinical Data

```kotlin
Text("Heart Rate: 72 bpm", modifier = Modifier.semantics {
    contentDescription = "Heart rate is 72 beats per minute, normal range"
    stateDescription = "Normal"
})
```

### Critical Alert Announcements

```kotlin
val context = LocalContext.current
LaunchedEffect(criticalAlert) {
    criticalAlert?.let {
        val manager = context.getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        if (manager.isEnabled) {
            val event = AccessibilityEvent.obtain(AccessibilityEvent.TYPE_ANNOUNCEMENT)
                .apply { text.add(it.message) }
            manager.sendAccessibilityEvent(event)
        }
    }
}
```

### Touch Targets and Focus

Clinical environments involve gloved hands. Minimum 56dp for clinical action buttons (exceeds 48dp Material minimum):

```kotlin
IconButton(onClick = { /* action */ }, modifier = Modifier.size(56.dp)) {
    Icon(Icons.Default.Favorite, contentDescription = "Record vital sign")
}
// Auto-focus critical fields when entering vital signs
val focusRequester = remember { FocusRequester() }
LaunchedEffect(Unit) { focusRequester.requestFocus() }
OutlinedTextField(
    value = systolicValue, onValueChange = { onSystolicChange(it) },
    label = { Text("Systolic (mmHg)") },
    modifier = Modifier.focusRequester(focusRequester),
    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
)
```

## 6. Offline-First Healthcare Patterns

Follow `android-data-persistence` skill for Room setup and sync architecture.

| Action | Online | Offline |
|--------|--------|---------|
| Patient roster | Pull from API | Read from Room cache |
| Vital signs entry | POST to API | Queue in Room, sync later |
| Medication admin | POST to API | Queue in Room, sync later |
| Clinical notes | POST to API | Save locally, sync later |
| Patient photos | Download on demand | Serve from Coil disk cache |

### Offline Mode Banner

```kotlin
@Composable
fun OfflineModeBanner(isOffline: Boolean) {
    AnimatedVisibility(visible = isOffline) {
        Surface(color = HealthcareColors.Warning.copy(alpha = 0.15f), modifier = Modifier.fillMaxWidth()) {
            Row(Modifier.padding(horizontal = 16.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.CloudOff, contentDescription = null, tint = HealthcareColors.Warning)
                Spacer(Modifier.width(8.dp))
                Text("Offline Mode - Data will sync when connected",
                     style = MaterialTheme.typography.labelMedium, color = HealthcareColors.Warning)
            }
        }
    }
}
```

### Data Freshness Indicator

```kotlin
@Composable
fun DataFreshnessLabel(lastSyncTime: Instant?) {
    val text = lastSyncTime?.let {
        val minutes = Duration.between(it, Instant.now()).toMinutes()
        when {
            minutes < 1 -> "Just synced"; minutes < 60 -> "Last synced: ${minutes}min ago"
            else -> "Last synced: ${minutes / 60}h ago"
        }
    } ?: "Never synced"
    Text(text, style = MaterialTheme.typography.labelSmall, color = HealthcareColors.TextMuted)
}
```

### Sync Queue Entity

```kotlin
@Entity(tableName = "sync_queue")
data class SyncQueueItem(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val entityType: String,   // "vital_sign", "medication_admin", "clinical_note"
    val entityId: String,
    val payload: String,      // JSON serialized data
    val createdAt: Long = System.currentTimeMillis(),
    val retryCount: Int = 0,
    val status: String = "pending" // pending, syncing, failed, completed
)
```

## 7. Security for Healthcare Android

### FLAG_SECURE on All PHI Screens

```kotlin
val activity = LocalContext.current as? Activity
DisposableEffect(Unit) {
    activity?.window?.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
    onDispose { activity?.window?.clearFlags(WindowManager.LayoutParams.FLAG_SECURE) }
}
```

### Required Security Measures

| Measure | Implementation |
|---------|---------------|
| Biometric auth | Use `android-biometric-login` skill. Require on app launch. |
| Token storage | `EncryptedSharedPreferences` for JWT, refresh tokens, session data |
| Certificate pinning | OkHttp `CertificatePinner` for all API endpoints |
| App lock | Re-authenticate after 30 seconds in background |
| Screenshot block | `FLAG_SECURE` on every screen displaying PHI |
| Obfuscation | R8/ProGuard enabled for release builds |
| Audit logging | Log every patient record access with user ID, timestamp, MRN |

### App Lock on Background

```kotlin
class HealthcareApp : Application(), DefaultLifecycleObserver {
    private var backgroundTimestamp: Long = 0L
    override fun onStop(owner: LifecycleOwner) { backgroundTimestamp = System.currentTimeMillis() }
    override fun onStart(owner: LifecycleOwner) {
        if (System.currentTimeMillis() - backgroundTimestamp > 30_000) {
            EventBus.post(RequireReAuthEvent)
        }
    }
}
```

## 8. Performance Patterns

### Paginated Patient Lists

Follow `api-pagination` skill. Use Paging 3 for infinite scroll:

```kotlin
@HiltViewModel
class PatientListViewModel @Inject constructor(private val repository: PatientRepository) : ViewModel() {
    val patients: Flow<PagingData<Patient>> = Pager(
        config = PagingConfig(pageSize = 25, prefetchDistance = 5),
        pagingSourceFactory = { repository.patientPagingSource() }
    ).flow.cachedIn(viewModelScope)
}

@Composable
fun PatientListContent(patients: LazyPagingItems<Patient>, onPatientClick: (String) -> Unit) {
    LazyColumn {
        items(count = patients.itemCount, key = patients.itemKey { it.mrn }) { index ->
            patients[index]?.let { PatientCard(patient = it, onTap = { onPatientClick(it.mrn) }) }
        }
        item {
            if (patients.loadState.append is LoadState.Loading) {
                CircularProgressIndicator(Modifier.fillMaxWidth().padding(16.dp))
            }
        }
    }
}
```

### Image Loading with Coil

```kotlin
@Composable
fun PatientAvatar(photoUrl: String?, size: Dp = 48.dp) {
    AsyncImage(
        model = ImageRequest.Builder(LocalContext.current).data(photoUrl).crossfade(true)
            .diskCachePolicy(CachePolicy.ENABLED).memoryCachePolicy(CachePolicy.ENABLED).build(),
        contentDescription = "Patient photo",
        modifier = Modifier.size(size).clip(CircleShape),
        placeholder = painterResource(R.drawable.ic_patient_placeholder),
        error = painterResource(R.drawable.ic_patient_placeholder),
        contentScale = ContentScale.Crop
    )
}
```

### Skeleton Loading Screens

```kotlin
@Composable
fun PatientCardSkeleton(modifier: Modifier = Modifier) {
    val shimmer = rememberInfiniteTransition(label = "shimmer")
    val alpha by shimmer.animateFloat(
        initialValue = 0.3f, targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(1500), RepeatMode.Reverse), label = "alpha"
    )
    Card(modifier = modifier.fillMaxWidth()) {
        Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(Modifier.size(48.dp).clip(CircleShape).background(Color.LightGray.copy(alpha = alpha)))
            Spacer(Modifier.width(12.dp))
            Column {
                Box(Modifier.width(160.dp).height(16.dp).background(Color.LightGray.copy(alpha = alpha)))
                Spacer(Modifier.height(8.dp))
                Box(Modifier.width(120.dp).height(12.dp).background(Color.LightGray.copy(alpha = alpha)))
            }
        }
    }
}
```

### Prefetch Strategy

```kotlin
// Prefetch patient detail when item becomes visible in list
LaunchedEffect(visiblePatientIds) {
    visiblePatientIds.forEach { mrn -> launch { repository.prefetchPatientDetail(mrn) } }
}
```

## Companion Skill Cross-References

| Need | Skill to Load |
|------|---------------|
| Full MVVM + Hilt setup | `android-development` |
| Compose UI patterns | `jetpack-compose-ui` |
| Biometric login | `android-biometric-login` |
| Room + offline sync | `android-data-persistence` |
| Infinite scroll pagination | `api-pagination` |
| RBAC permission gates | `mobile-rbac` |
| PDF export | `android-pdf-export` |
| Custom PNG icons | `android-custom-icons` |
| Report tables (>25 rows) | `android-report-tables` |
| Security baseline | `vibe-security-skill` |
