---
name: kmp-compose-multiplatform
description: Compose Multiplatform for shared UI across Android, iOS, Desktop (JVM),
  and Web (wasmJs). Covers targets configuration, shared composables, desktop windowing,
  wasmJs browser targets, navigation, platform-specific UI hooks, CI/CD for multi-target
  builds, and performance optimisation. Companion to kmp-development (business logic)
  and android-development (Android-only UI).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Compose Multiplatform Standards
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Compose Multiplatform for shared UI across Android, iOS, Desktop (JVM), and Web (wasmJs). Covers targets configuration, shared composables, desktop windowing, wasmJs browser targets, navigation, platform-specific UI hooks, CI/CD for multi-target builds, and performance optimisation. Companion to kmp-development (business logic) and android-development (Android-only UI).
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `kmp-compose-multiplatform` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Multiplatform UI parity audit | Markdown doc covering Android, iOS, Desktop (JVM), and Web (wasmJs) parity per shared screen | `docs/kmp/ui-parity-audit.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## When to Use Compose Multiplatform vs Native UI

| Approach | When to Choose |
|---|---|
| **Compose Multiplatform (this skill)** | Design system consistency > platform feel; internal tools; desktop+mobile parity needed |
| **Native UI (kmp-development)** | App Store/Play Store quality expected; platform-specific UX; iOS gestures critical |

Compose Multiplatform shares UI code across Android, iOS, Desktop, and Web. It is **not** a replacement for SwiftUI when platform-native feel matters.

## Targets Configuration

```kotlin
// shared/build.gradle.kts (or composeApp/build.gradle.kts)
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.composeMultiplatform)
    alias(libs.plugins.composeCompiler)
}

kotlin {
    androidTarget()

    listOf(iosX64(), iosArm64(), iosSimulatorArm64()).forEach {
        it.binaries.framework {
            baseName = "ComposeApp"
            isStatic = true
        }
    }

    jvm("desktop")          // Desktop target

    @OptIn(ExperimentalWasmDsl::class)
    wasmJs {
        moduleName = "composeApp"
        browser {
            commonWebpackConfig {
                outputFileName = "composeApp.js"
            }
        }
        binaries.executable()
    }

    sourceSets {
        val desktopMain by getting

        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            implementation(compose.components.resources)
            implementation(compose.components.uiToolingPreview)
            implementation(libs.navigation.compose)
            implementation(libs.koin.compose)
        }
        androidMain.dependencies {
            implementation(compose.preview)
            implementation(libs.androidx.activity.compose)
        }
        desktopMain.dependencies {
            implementation(compose.desktop.currentOs)
            implementation(libs.kotlinx.coroutines.swing)
        }
    }
}

compose.desktop {
    application {
        mainClass = "com.example.app.MainKt"
        nativeDistributions {
            targetFormats(TargetFormat.Dmg, TargetFormat.Msi, TargetFormat.Deb)
            packageName = "com.example.app"
            packageVersion = "1.0.0"
        }
    }
}
```

## Source Set Structure

```text
composeApp/src/
  commonMain/           # Shared composables, ViewModels, navigation
    kotlin/
    composeResources/   # Shared images, fonts, strings
  androidMain/          # Android entry point (Activity)
  iosMain/              # iOS entry point (UIViewController wrapper)
  desktopMain/          # Desktop entry point (main fun)
  wasmJsMain/           # Browser entry point (main fun)
```

## Entry Points Per Platform

```kotlin
// androidMain — Activity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { App() }
    }
}

// desktopMain — main function
fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "MyApp",
        state = rememberWindowState(width = 1200.dp, height = 800.dp)
    ) {
        App()
    }
}

// wasmJsMain — browser
@OptIn(ExperimentalComposeUiApi::class)
fun main() {
    ComposeViewport(document.body!!) { App() }
}
```

## Shared App Composable

```kotlin
// commonMain
@Composable
fun App() {
    MaterialTheme {
        val navController = rememberNavController()
        NavHost(navController, startDestination = "home") {
            composable("home") { HomeScreen(navController) }
            composable("detail/{id}") { backStack ->
                DetailScreen(backStack.arguments?.getString("id") ?: "")
            }
        }
    }
}
```

## Platform-Specific UI Hooks (expect/actual for UI)

Use `expect`/`actual` only when you need platform-specific UI behaviour.

```kotlin
// commonMain
@Composable
expect fun PlatformSpecificContent()

expect fun openUrl(url: String)

// androidMain
@Composable
actual fun PlatformSpecificContent() {
    // Android-only widget
}

actual fun openUrl(url: String) {
    // Use Android Intent
}

// desktopMain
@Composable
actual fun PlatformSpecificContent() {
    // Desktop-specific panel
}

actual fun openUrl(url: String) {
    Desktop.getDesktop().browse(URI(url))
}

// wasmJsMain
@Composable
actual fun PlatformSpecificContent() { /* no-op or web specific */ }

actual fun openUrl(url: String) {
    window.open(url, "_blank")
}
```

## Shared Resources

Compose Multiplatform has a unified resource system. Place all shared assets in `commonMain/composeResources/`:

```text
composeResources/
  drawable/           # SVG/XML vector drawables
  font/               # TTF/OTF fonts
  values/
    strings.xml       # Localised strings
```

```kotlin
// Access resources in composables
import composeapp.composeresources.*

@Composable
fun Logo() {
    Image(
        painter = painterResource(Res.drawable.logo),
        contentDescription = "Logo"
    )
}

val label = stringResource(Res.string.welcome_message)
```

## Desktop Window Management

```kotlin
// desktopMain
fun main() = application {
    val windowState = rememberWindowState(
        placement = WindowPlacement.Maximized
    )
    Window(
        onCloseRequest = ::exitApplication,
        state = windowState,
        title = "MyApp",
        icon = BitmapPainter(useResource("icon.png", ::loadImageBitmap))
    ) {
        MenuBar {
            Menu("File") {
                Item("Open", onClick = { /* ... */ })
                Separator()
                Item("Exit", onClick = ::exitApplication)
            }
        }
        App()
    }
}
```

## Web (wasmJs) Considerations

```kotlin
// wasmJsMain
@OptIn(ExperimentalComposeUiApi::class)
fun main() {
    ComposeViewport(document.getElementById("root")!!) {
        App()
    }
}
```

**wasmJs limitations:**
- No file system access — use web APIs via `external` declarations
- No system fonts — bundle fonts in `composeResources/font/`
- HTTP calls must use CORS-allowed origins
- Use `kotlinx.browser` for DOM interop where needed

## DI with Koin in Compose Multiplatform

```kotlin
// commonMain
val appModule = module {
    viewModel { HomeViewModel(get()) }
    viewModel { DetailViewModel(get()) }
}

@Composable
fun App() {
    KoinApplication(application = {
        modules(appModule, sharedModule)
    }) {
        MaterialTheme {
            NavHost(/* ... */)
        }
    }
}

// In composables
@Composable
fun HomeScreen() {
    val viewModel: HomeViewModel = koinViewModel()
    // ...
}
```

## CI/CD for Multi-Target KMP

### GitHub Actions Matrix

```yaml
# .github/workflows/build.yml
name: Build & Test

on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            task: testDebugUnitTest        # Android JVM
          - os: macos-latest
            task: iosSimulatorArm64Test    # iOS simulator
          - os: ubuntu-latest
            task: desktopTest             # Desktop JVM
          - os: ubuntu-latest
            task: wasmJsBrowserTest       # Web/WASM

    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
      - uses: gradle/actions/setup-gradle@v3
      - run: ./gradlew ${{ matrix.task }}
```

### Platform-Specific Release Tasks

```bash
# Android APK/AAB
./gradlew assembleRelease
./gradlew bundleRelease

# Desktop distributable
./gradlew packageDmg          # macOS
./gradlew packageMsi          # Windows
./gradlew packageDeb          # Linux

# Web bundle
./gradlew wasmJsBrowserProductionWebpack
```

## Performance Optimisation

### Stable Classes

Mark ViewModel state as `@Stable` or use `@Immutable` to prevent unnecessary recompositions:

```kotlin
@Immutable
data class UiState(
    val items: List<Item> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)
```

### Lazy Layouts

```kotlin
// Prefer LazyColumn/LazyGrid over Column with forEach
LazyColumn {
    items(items, key = { it.id }) { item ->
        ItemCard(item)
    }
}
```

### Remember and derivedStateOf

```kotlin
val filteredItems by remember(query) {
    derivedStateOf { allItems.filter { it.name.contains(query) } }
}
```

### Image Loading (Coil / Kamel)

```kotlin
// commonMain — use Kamel for multiplatform async image loading
implementation(libs.kamel.image)

@Composable
fun AsyncImage(url: String) {
    KamelImage(
        resource = asyncPainterResource(url),
        contentDescription = null,
        contentScale = ContentScale.Crop
    )
}
```

## Mandatory Rules

1. **Shared composables in `commonMain`** — never platform-specific in shared UI
2. **Resources in `composeResources/`** — never raw platform asset folders
3. **All targets in CI** — run tests on Android JVM, iOS simulator, desktop, wasmJs
4. **`@Immutable`/`@Stable` on all state classes** — prevents recomposition thrashing
5. **Koin for DI** — do not use Hilt in shared compose code
6. **`key = {}` in lazy layouts** — always supply a stable key
7. **Bundle fonts** — do not rely on system fonts (especially for wasmJs)

## Anti-Patterns

- Importing Android-specific APIs in `commonMain` composables
- Using `Column { forEach }` for long lists (use LazyColumn)
- Missing `key` in `items {}` — causes full recomposition on list updates
- Hardcoding pixel sizes — use `dp` and `sp` everywhere
- Platform entry point logic in `commonMain` — keep it in platform source sets
- Skipping wasmJs in CI — web target fails silently on missing APIs