# Build Configuration Standards

Gradle Kotlin DSL configuration for Android projects.

## Three Build Variants (Mandatory)

Every Android project MUST define exactly 3 build variants: **debug** (dev), **staging**, and **release** (prod). This is a hard requirement for all apps.

### Variant Summary

| Variant | APK Prefix | API Server | Minified | Signing | Install |
|---------|-----------|------------|----------|---------|---------|
| debug | `{App}-dev` | Local dev server | No | Debug keystore | Emulator (always) |
| staging | `{App}-staging` | User-provided staging URL | Yes (R8) | Debug keystore | Emulator (on request) |
| release | `{App}-prod` | User-provided production URL | Yes (R8) | Release keystore | Device (manual) |

### User Must Specify

Before setting up build variants, the user MUST provide:
1. **Staging API URL** (e.g., `https://staging.example.com/api/`)
2. **Production API URL** (e.g., `https://app.example.com/api/`)

The debug URL is always the local dev server (emulator uses `http://10.0.2.2/...` to reach the host machine).

### Build & Install Workflow

**Every time the user asks to build or says "build the APKs":**

```bash
# Step 1: Build ALL 3 variants (always)
./gradlew assembleDebug assembleStaging assembleRelease

# Step 2: Install dev to emulator (default)
./gradlew installDebug
```

**If the user explicitly asks to test staging:**

```bash
./gradlew installStaging
```

Never install release to emulator unless explicitly asked — release builds typically require a real signing key.

## Local Development Networking (WAMP)

- On local Windows/Ubuntu dev machines, the Android emulator must reach the backend via `10.0.2.2` (emulator alias for host localhost) or the host machine's static LAN IP.
- Ensure firewall rules allow inbound access to the WAMP HTTP port.

## App-Level build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.company.appname"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.company.appname"
        minSdk = 29
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        // Debug (dev) — local server
        buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2/MyApp/api/\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            // USER MUST PROVIDE THIS URL
            buildConfigField("String", "API_BASE_URL", "\"https://app.example.com/api/\"")
        }
        create("staging") {
            initWith(getByName("release"))
            // Use debug signing so it installs on emulator without release keystore
            signingConfig = signingConfigs.getByName("debug")
            // USER MUST PROVIDE THIS URL
            buildConfigField("String", "API_BASE_URL", "\"https://staging.example.com/api/\"")
        }
    }

    // APK naming: {AppName}-{variant}-{version}.apk
    applicationVariants.all {
        val variant = this
        outputs.all {
            val output = this as com.android.build.gradle.internal.api.BaseVariantOutputImpl
            val prefix = when (variant.buildType.name) {
                "debug" -> "MyApp-dev"
                "staging" -> "MyApp-staging"
                "release" -> "MyApp-prod"
                else -> "MyApp"
            }
            output.outputFileName = "$prefix-${variant.versionName}.apk"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}
```

### Key Points

- **staging `initWith(release)`**: Inherits R8 minification and resource shrinking from release.
- **staging `signingConfig = debug`**: Allows installation on emulator/device without the release keystore.
- **APK naming**: Consistent `{AppName}-{dev|staging|prod}-{version}.apk` format via `applicationVariants.all`.
- **BuildConfig fields**: Each variant has its own `API_BASE_URL`. Code uses `BuildConfig.API_BASE_URL` everywhere — never hardcode URLs.

## ProGuard Rules (Mandatory for Staging + Release)

```proguard
# proguard-rules.pro

# ── Strip debug logging from staging and release builds ──
-assumenosideeffects class android.util.Log {
    public static int v(...);
    public static int d(...);
    public static int i(...);
}

# Strip Kotlin println (shouldn't be in production code)
-assumenosideeffects class kotlin.io.ConsoleKt {
    public static void println(...);
}

# ── Keep Retrofit service interfaces ──
-keep,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# ── Moshi ──
-keep class com.squareup.moshi.** { *; }
-keepclassmembers class * {
    @com.squareup.moshi.* <methods>;
    @com.squareup.moshi.* <fields>;
}

# ── Room ──
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *

# ── Keep data classes used in API responses ──
-keep class com.company.appname.**.dto.** { *; }
```

## Dependencies (Organized by Category)

```kotlin
dependencies {
    // Compose BOM
    val composeBom = platform(libs.compose.bom)
    implementation(composeBom)
    androidTestImplementation(composeBom)

    // Compose UI
    implementation(libs.compose.ui)
    implementation(libs.compose.ui.graphics)
    implementation(libs.compose.ui.tooling.preview)
    implementation(libs.compose.material3)
    implementation(libs.compose.material.icons.extended)
    debugImplementation(libs.compose.ui.tooling)
    debugImplementation(libs.compose.ui.test.manifest)

    // AndroidX Core
    implementation(libs.core.ktx)
    implementation(libs.activity.compose)
    implementation(libs.appcompat)

    // Lifecycle
    implementation(libs.lifecycle.runtime.ktx)
    implementation(libs.lifecycle.runtime.compose)
    implementation(libs.lifecycle.viewmodel.compose)

    // Navigation
    implementation(libs.navigation.compose)

    // Hilt
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)
    implementation(libs.hilt.navigation.compose)

    // Networking
    implementation(libs.retrofit)
    implementation(libs.retrofit.moshi)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging)
    implementation(libs.moshi)
    implementation(libs.moshi.kotlin)
    ksp(libs.moshi.codegen)

    // Room
    implementation(libs.room.runtime)
    implementation(libs.room.ktx)
    ksp(libs.room.compiler)

    // Security
    implementation(libs.security.crypto)

    // Image Loading (Coil 3)
    implementation(libs.coil.compose)
    implementation(libs.coil.network.okhttp)

    // Charts (Vico)
    implementation(libs.vico.compose)
    implementation(libs.vico.compose.m3)

    // Testing
    testImplementation(libs.junit5.api)
    testRuntimeOnly(libs.junit5.engine)
    testImplementation(libs.mockk)
    testImplementation(libs.turbine)
    testImplementation(libs.coroutines.test)
    testImplementation(libs.room.testing)
    androidTestImplementation(libs.compose.ui.test.junit4)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.androidx.test.ext)
}

tasks.withType<Test> {
    useJUnitPlatform()
}
```

## Version Catalog (gradle/libs.versions.toml)

Use a version catalog for all projects:

```toml
[versions]
kotlin = "2.1.0"
agp = "8.13.2"
ksp = "2.1.0-1.0.29"
compose-bom = "2025.01.01"
hilt = "2.50"
retrofit = "2.9.0"
room = "2.6.1"
okhttp = "4.12.0"
moshi = "1.15.0"

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }
retrofit = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }
room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
```

## Build Configuration Rules

1. **3 build variants always** — debug (dev), staging, release (prod). No exceptions.
2. **Build all 3 APKs every time** — `./gradlew assembleDebug assembleStaging assembleRelease`
3. **Install dev to emulator by default** — `./gradlew installDebug` after every build
4. **Install staging only when user explicitly requests it** — `./gradlew installStaging`
5. **User provides staging + prod URLs** — never guess or hardcode server URLs
6. **APK naming**: `{AppName}-dev-{ver}.apk`, `{AppName}-staging-{ver}.apk`, `{AppName}-prod-{ver}.apk`
7. **Never commit signing keys** — use `local.properties` or CI secrets
8. **Enable R8/ProGuard** for staging and release builds
9. **Shrink resources** in staging and release builds
10. **Strip debug logs** (Log.v/d/i + println) from staging and release via ProGuard rules
11. **Use version catalog** for all projects (gradle/libs.versions.toml)
12. **Pin dependency versions** — no dynamic versions (`+`)
