---
name: kmp-development
description: Kotlin Multiplatform shared module development standards for sharing
  business logic across Android and iOS while keeping native UI. Covers project structure
  (shared/composeApp/iosApp), source sets, targets, expect/actual, DI (Koin)...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Kotlin Multiplatform Development Standards

<!-- dual-compat-start -->
## Use When

- Kotlin Multiplatform shared module development standards for sharing business logic across Android and iOS while keeping native UI. Covers project structure (shared/composeApp/iosApp), source sets, targets, expect/actual, DI (Koin)...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `kmp-development` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Strategy: Shared Logic, Native UI

KMP shares business logic (domain, data, networking) across platforms. Each
platform keeps its native UI framework: Jetpack Compose for Android, SwiftUI
for iOS. This preserves the best user experience on each platform while
eliminating business logic duplication.

## Module-to-Skill Mapping

| Module | Governs | Skill |
|---|---|---|
| `shared/` | Business logic, data, networking | **This skill** (kmp-development) |
| `composeApp/` | Android UI, platform integration | android-development |
| `iosApp/` | iOS UI, platform integration | ios-development |

## Project Structure

Every KMP project has three modules:

```text
project-root/
  shared/                    # Shared Kotlin module (this skill governs)
    src/
      commonMain/            # Shared code (domain, data, use cases)
        kotlin/
        resources/
      androidMain/           # Android-specific implementations
        kotlin/
        AndroidManifest.xml
      iosMain/               # iOS-specific implementations
        kotlin/
      commonTest/            # Shared tests
      androidUnitTest/       # Android-specific tests
      iosTest/               # iOS-specific tests
    build.gradle.kts         # KMP Gradle config
  composeApp/                # Android app (follow android-development skill)
    src/main/
    build.gradle.kts
  iosApp/                    # iOS Xcode project (follow ios-development skill)
    iosApp/
    iosApp.xcodeproj
  build.gradle.kts           # Root build file
  gradle/libs.versions.toml  # Version catalog
```

## Technology Stack

| Concern | Library | Notes |
|---|---|---|
| Language | Kotlin | 100% Kotlin in shared module |
| Build | Gradle KTS + Version Catalogs | Mandatory |
| Networking | Ktor Client | Replaces Retrofit in shared code |
| Database (primary) | SQLDelight | Mature KMP-native, typesafe SQL |
| Database (alternative) | Room KMP | Familiar to Android devs, newer |
| Key-Value Storage | DataStore / Multiplatform Settings | Platform-agnostic preferences |
| Object Storage | KStore | kotlinx.serialization + okio |
| DI | Koin | Lightweight, no reflection on iOS |
| Serialization | kotlinx.serialization | JSON, Protobuf, CBOR |
| Async | Coroutines + Flow | Shared across all platforms |
| Swift Interop | SKIE (TouchLab) | Sealed classes, Flows in Swift |
| Framework Publishing | KMMBridge | XCFramework + SPM/CocoaPods |
| Environment Check | KDoctor | Validates dev environment setup |

## Source Sets and Targets

### Targets Configuration

```kotlin
// shared/build.gradle.kts
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
}

kotlin {
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = JavaVersion.VERSION_17.toString()
            }
        }
    }

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "Shared"
            isStatic = true
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.json)
            implementation(libs.koin.core)
        }
        androidMain.dependencies {
            implementation(libs.ktor.client.okhttp)
            implementation(libs.koin.android)
        }
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }
        commonTest.dependencies {
            implementation(kotlin("test"))
            implementation(libs.kotlinx.coroutines.test)
            implementation(libs.turbine)
            implementation(libs.koin.test)
        }
    }
}
```

### Source Set Hierarchy

```text
commonMain          <- Shared business logic (domain, data, use cases)
  androidMain       <- Android-specific implementations (Kotlin/JVM)
  iosMain           <- iOS-specific implementations (Kotlin/Native)
    iosArm64Main    <- iPhone devices
    iosX64Main      <- Intel simulators
    iosSimulatorArm64Main  <- Apple Silicon simulators
```

Dependencies in `commonMain` automatically propagate to all platform source
sets. Only add platform-specific dependencies in `androidMain`/`iosMain`.

## Architecture: Clean Architecture in Shared Module

```text
shared/src/commonMain/kotlin/com/example/app/
  domain/
    model/           # Domain entities (data classes)
    repository/      # Repository interfaces
    usecase/         # Business use cases
  data/
    repository/      # Repository implementations
    remote/          # Network data sources (Ktor)
    local/           # Local data sources (SQLDelight/Room)
    mapper/          # DTO <-> Domain mappers
  di/
    SharedModule.kt  # Koin module definitions
  platform/
    Platform.kt      # expect declarations for platform code
```

### Layer Rules

- **Domain layer** is pure Kotlin, no platform dependencies, no framework imports
- **Data layer** uses KMP libraries (Ktor, SQLDelight) via interfaces
- **Platform-specific code** uses expect/actual only when KMP libraries
  do not cover the use case

## Expect/Actual Pattern

Use expect/actual for platform-specific functionality that cannot be handled
by KMP libraries.

```kotlin
// commonMain - declare the contract
expect class PlatformContext

expect fun getPlatformName(): String

// androidMain - Android implementation
actual typealias PlatformContext = android.content.Context

actual fun getPlatformName(): String = "Android ${Build.VERSION.SDK_INT}"

// iosMain - iOS implementation
actual class PlatformContext

actual fun getPlatformName(): String =
    UIDevice.currentDevice.systemName() + " " +
    UIDevice.currentDevice.systemVersion
```

### When to Use expect/actual

- Platform APIs with no KMP library equivalent (e.g., Bluetooth, biometrics)
- Platform-specific SDK wrappers (e.g., Bugsnag, Firebase)
- Context/environment access (Android Context, iOS NSUserDefaults)

### When NOT to Use expect/actual

- Networking: use Ktor instead
- Database: use SQLDelight or Room KMP instead
- Preferences: use DataStore or Multiplatform Settings instead
- Serialization: use kotlinx.serialization instead

## Dependency Injection with Koin

```kotlin
// shared/src/commonMain/.../di/SharedModule.kt
val sharedModule = module {
    // Data sources
    single<RemoteDataSource> { KtorRemoteDataSource(get()) }
    single<LocalDataSource> { SQLDelightLocalDataSource(get()) }

    // Repositories
    single<UserRepository> { UserRepositoryImpl(get(), get()) }

    // Use cases
    factory { GetUsersUseCase(get()) }
    factory { RefreshUsersUseCase(get()) }
}

// Platform-specific modules
// androidMain
val androidPlatformModule = module {
    single { provideAndroidContext() }
    single<SqlDriver> { AndroidSqliteDriver(AppDatabase.Schema, get(), "app.db") }
    single<HttpClient> { HttpClient(OkHttp) { installDefaults() } }
}

// iosMain
val iosPlatformModule = module {
    single<SqlDriver> { NativeSqliteDriver(AppDatabase.Schema, "app.db") }
    single<HttpClient> { HttpClient(Darwin) { installDefaults() } }
}
```

### Koin Initialization

```kotlin
// Android (in Application class)
startKoin {
    androidContext(this@App)
    modules(sharedModule, androidPlatformModule)
}

// iOS (in Swift, via helper)
// shared/src/iosMain/.../di/KoinHelper.kt
fun initKoin() {
    startKoin {
        modules(sharedModule, iosPlatformModule)
    }
}
```

## Networking with Ktor

```kotlin
// commonMain
internal fun createHttpClient(engine: HttpClientEngine): HttpClient {
    return HttpClient(engine) {
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
            })
        }
        install(Logging) {
            logger = Logger.DEFAULT
            level = LogLevel.HEADERS
        }
        defaultRequest {
            contentType(ContentType.Application.Json)
        }
    }
}

// Data source using Ktor
class KtorUserRemoteDataSource(
    private val client: HttpClient,
    private val baseUrl: String,
) : UserRemoteDataSource {

    override suspend fun getUsers(): Result<List<UserDto>> = runCatching {
        client.get("${baseUrl}/users").body()
    }
}
```

### Environment Configuration

Use the same three-environment pattern as native skills:

| Environment | Base URL | Notes |
|---|---|---|
| Development | `http://{LAN_IP}:{port}/api/` | Local WAMP backend |
| Staging | `https://staging.{domain}/api/` | QA/TestFlight |
| Production | `https://{domain}/api/` | App Store/Play Store |

Define base URLs via expect/actual or build config, never hardcoded.

## Database with SQLDelight

```kotlin
// shared/build.gradle.kts
plugins {
    alias(libs.plugins.sqldelight)
}

sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.app.db")
        }
    }
}
```

```sql
-- shared/src/commonMain/sqldelight/com/example/app/db/User.sq
CREATE TABLE User (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

selectAll:
SELECT * FROM User;

insertUser:
INSERT OR REPLACE INTO User(id, name, email) VALUES (?, ?, ?);
```

### Platform Drivers

```kotlin
// commonMain
expect class DriverFactory {
    fun createDriver(): SqlDriver
}

// androidMain
actual class DriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver =
        AndroidSqliteDriver(AppDatabase.Schema, context, "app.db")
}

// iosMain
actual class DriverFactory {
    actual fun createDriver(): SqlDriver =
        NativeSqliteDriver(AppDatabase.Schema, "app.db")
}
```

## Modularization

For larger projects, split the shared module into domain-specific modules:

```text
shared/
  core/           # Base utilities, networking client, DI setup
  feature-auth/   # Authentication domain
  feature-users/  # Users domain
  umbrella/       # Umbrella module that re-exports all to iOS
```

### Umbrella Framework for iOS

When using multiple shared modules, create an umbrella module that
re-exports all frameworks as a single iOS framework:

```kotlin
// umbrella/build.gradle.kts
kotlin {
    listOf(iosX64(), iosArm64(), iosSimulatorArm64()).forEach {
        it.binaries.framework {
            baseName = "Shared"
            isStatic = true
            export(project(":shared:core"))
            export(project(":shared:feature-auth"))
            export(project(":shared:feature-users"))
        }
    }
    sourceSets {
        commonMain.dependencies {
            api(project(":shared:core"))
            api(project(":shared:feature-auth"))
            api(project(":shared:feature-users"))
        }
    }
}
```

## Native Library Integration

### Android Dependencies in KMP

Add Android-specific dependencies directly in `androidMain`:

```kotlin
sourceSets {
    androidMain.dependencies {
        api(libs.bugsnag.android)
        implementation(libs.androidx.startup.runtime)
    }
}
```

### iOS Dependencies via CocoaPods

```kotlin
// shared/build.gradle.kts
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.cocoaPods)
}

kotlin {
    cocoapods {
        version = "1.0"
        summary = "Shared KMP module"
        homepage = "https://example.com"
        name = "Shared"
        ios.deploymentTarget = "16.0"
        framework {
            baseName = "Shared"
            isStatic = false
        }
        pod("Bugsnag") { version = "~> 6.28" }
    }
}
```

## Tooling

### SKIE (Swift-Kotlin Interface Enhancer)

Improves Swift interop: sealed classes become Swift enums with exhaustive
switch, Kotlin Flows become Swift async sequences.

```kotlin
// shared/build.gradle.kts
plugins {
    id("co.touchlab.skie") version "0.8.0"
}
```

### KMMBridge

Publishes KMP frameworks as XCFrameworks for SPM or CocoaPods consumption:

```kotlin
plugins {
    id("co.touchlab.kmmbridge") version "0.5.0"
}

kmmbridge {
    mavenPublishArtifacts()
    spm()
}
```

### KDoctor

Run before starting development to validate environment:

```bash
kdoctor
```

Checks: OS version, JDK, Android Studio, Xcode, CocoaPods, Gradle.

## Mandatory Rules

1. **Domain layer is pure Kotlin** -- no Android/iOS imports in domain/
2. **Use KMP libraries first** -- only fall back to expect/actual when no
   library covers the use case
3. **Koin for DI in shared module** -- Hilt stays in composeApp/ only
4. **Ktor for networking** -- Retrofit stays in composeApp/ only if needed
5. **Three environments** -- dev, staging, production (matching native skills)
6. **Version catalogs mandatory** -- all dependencies in libs.versions.toml
7. **Static framework for iOS** -- `isStatic = true` unless CocoaPods requires
   dynamic
8. **SKIE recommended** -- install for better Swift interop unless project has
   constraints

## Anti-Patterns

- Putting UI code in the shared module (use Compose/SwiftUI in app modules)
- Using Android Context in commonMain (use expect/actual or Koin injection)
- Hardcoding base URLs (use build config or expect/actual)
- Using Hilt in the shared module (Hilt is Android-only; use Koin)
- Skipping the umbrella module when multiple shared modules exist
- Using Retrofit in shared code (Retrofit is JVM-only; use Ktor)
- Force-unwrapping in iOS integration code
