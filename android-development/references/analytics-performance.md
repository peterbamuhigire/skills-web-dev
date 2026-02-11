# Analytics & Performance Standards

Firebase analytics, crash reporting, and performance optimization patterns.

## Local Development Networking (WAMP)

- On local Windows/Ubuntu dev machines, the Android emulator must reach the backend via the host machine's static LAN IP, not `localhost`.
- Ensure firewall rules allow inbound access to the WAMP HTTP port.

## Analytics Manager

```kotlin
@Singleton
class AnalyticsManager @Inject constructor(
    private val firebaseAnalytics: FirebaseAnalytics,
    private val crashlytics: FirebaseCrashlytics
) {
    // Screen tracking
    fun trackScreenView(screenName: String, screenClass: String? = null) {
        firebaseAnalytics.logEvent(FirebaseAnalytics.Event.SCREEN_VIEW) {
            param(FirebaseAnalytics.Param.SCREEN_NAME, screenName)
            screenClass?.let {
                param(FirebaseAnalytics.Param.SCREEN_CLASS, it)
            }
        }
        crashlytics.setCustomKey("last_screen", screenName)
    }

    // Custom event tracking
    fun trackEvent(
        eventName: String,
        parameters: Map<String, Any> = emptyMap()
    ) {
        firebaseAnalytics.logEvent(eventName) {
            parameters.forEach { (key, value) ->
                when (value) {
                    is String -> param(key, value)
                    is Long -> param(key, value)
                    is Double -> param(key, value)
                    is Int -> param(key, value.toLong())
                    else -> param(key, value.toString())
                }
            }
        }
    }

    // User properties
    fun setUserProperty(property: String, value: String?) {
        firebaseAnalytics.setUserProperty(property, value)
    }

    fun setUserId(userId: String?) {
        firebaseAnalytics.setUserId(userId)
        crashlytics.setUserId(userId ?: "")
    }

    // Error tracking
    fun logError(error: Throwable, context: Map<String, String> = emptyMap()) {
        context.forEach { (key, value) ->
            crashlytics.setCustomKey(key, value)
        }
        crashlytics.recordException(error)
    }

    fun logMessage(message: String) {
        crashlytics.log(message)
    }
}
```

## Screen Analytics Composable

```kotlin
@Composable
fun TrackScreen(
    screenName: String,
    analyticsManager: AnalyticsManager = hiltViewModel<AnalyticsViewModel>().analyticsManager
) {
    DisposableEffect(screenName) {
        analyticsManager.trackScreenView(screenName)
        onDispose { }
    }
}

// Usage in any screen
@Composable
fun UserProfileScreen(/* ... */) {
    TrackScreen("UserProfile")
    // ... screen content
}
```

## Standard Analytics Events

```kotlin
object AnalyticsEvents {
    // Authentication
    const val LOGIN = "login"
    const val LOGOUT = "logout"
    const val SIGNUP = "sign_up"

    // Content
    const val VIEW_ITEM = "view_item"
    const val SEARCH = "search"

    // Commerce
    const val ADD_TO_CART = "add_to_cart"
    const val PURCHASE = "purchase"
    const val CHECKOUT_BEGIN = "begin_checkout"

    // Engagement
    const val SHARE = "share"
    const val SELECT_CONTENT = "select_content"
}

// Example usage
analyticsManager.trackEvent(AnalyticsEvents.PURCHASE, mapOf(
    "order_id" to orderId,
    "total" to total,
    "item_count" to items.size
))
```

## Performance Monitoring

### StrictMode (Debug Only)

```kotlin
@Singleton
class PerformanceMonitor @Inject constructor(
    @ApplicationContext private val context: Context
) {
    fun initialize() {
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .penaltyDeathOnNetwork() // Crash on network on main thread
                    .build()
            )

            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .build()
            )
        }
    }
}
```

### Firebase Performance Traces

```kotlin
// Manual trace for critical operations
suspend fun <T> tracedOperation(
    traceName: String,
    block: suspend () -> T
): T {
    val trace = Firebase.performance.newTrace(traceName)
    trace.start()
    return try {
        val result = block()
        trace.putAttribute("status", "success")
        result
    } catch (e: Exception) {
        trace.putAttribute("status", "error")
        trace.putAttribute("error_type", e::class.simpleName ?: "unknown")
        throw e
    } finally {
        trace.stop()
    }
}

// Usage
val user = tracedOperation("load_user_profile") {
    userRepository.getUser(userId)
}
```

## Compose Performance Optimization

### Stable Keys in Lists

```kotlin
// Always provide stable keys
LazyColumn {
    items(
        items = orders,
        key = { order -> order.id } // Stable key for recomposition
    ) { order ->
        OrderCard(order = order)
    }
}
```

### derivedStateOf for Expensive Calculations

```kotlin
@Composable
fun OrderSummary(items: List<OrderItem>) {
    // Only recalculates when items actually change
    val total by remember(items) {
        derivedStateOf {
            items.sumOf { it.price * it.quantity }
        }
    }

    Text("Total: $${"%.2f".format(total)}")
}
```

### Avoid Unnecessary Recomposition

```kotlin
// Bad: lambda recreated every recomposition
LazyColumn {
    items(orders) { order ->
        OrderCard(onClick = { viewModel.selectOrder(order.id) }) // new lambda each time
    }
}

// Good: stable reference
LazyColumn {
    items(orders, key = { it.id }) { order ->
        val orderId = order.id
        OrderCard(onClick = remember(orderId) { { viewModel.selectOrder(orderId) } })
    }
}
```

### Image Loading with Coil

```kotlin
@Composable
fun UserAvatar(
    imageUrl: String?,
    modifier: Modifier = Modifier,
    size: Dp = 48.dp
) {
    AsyncImage(
        model = ImageRequest.Builder(LocalContext.current)
            .data(imageUrl)
            .crossfade(true)
            .size(coil.size.Size.ORIGINAL) // or specific size
            .build(),
        contentDescription = "User avatar",
        modifier = modifier
            .size(size)
            .clip(CircleShape),
        contentScale = ContentScale.Crop,
        placeholder = painterResource(R.drawable.ic_avatar_placeholder),
        error = painterResource(R.drawable.ic_avatar_placeholder)
    )
}
```

## Memory Management

```kotlin
// Check memory in debug builds
fun logMemoryUsage(tag: String = "Memory") {
    if (BuildConfig.DEBUG) {
        val runtime = Runtime.getRuntime()
        val usedMem = (runtime.totalMemory() - runtime.freeMemory()) / 1024 / 1024
        val maxMem = runtime.maxMemory() / 1024 / 1024
        Log.d(tag, "Used: ${usedMem}MB / Max: ${maxMem}MB")
    }
}
```

## Performance Checklist

- StrictMode enabled in debug builds
- Stable keys in all `LazyColumn`/`LazyRow` items
- `derivedStateOf` for expensive computed values
- `collectAsStateWithLifecycle()` for lifecycle-aware collection
- Coil for image loading with proper caching
- ProGuard + resource shrinking in release
- No main-thread blocking operations
- Firebase Performance traces for critical paths
- Memory leak detection (LeakCanary in debug)
- App startup time tracking
