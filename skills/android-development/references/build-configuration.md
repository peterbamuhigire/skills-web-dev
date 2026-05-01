# Build Configuration Standards

Gradle Kotlin DSL configuration for Android projects, with Android Studio setup and build-speed defaults aimed at the fastest safe local development loop.

## Fastest Safe Setup Path

When creating or modernizing an Android project, apply these in order:

1. Update Android Studio, SDK tools, the Gradle wrapper, and AGP to a mutually compatible set already approved by the repo.
2. Use **Kotlin DSL**, **version catalogs**, and **KSP** from day one.
3. Turn off legacy compatibility flags you do not need, especially `android.enableJetifier`.
4. Keep local development focused on the `debug` variant; do not build `staging` and `release` on every change.
5. Enable the **configuration cache** once the project and plugins are clean.
6. Use Android Studio **Build Analyzer** before changing heap sizes or Gradle flags.

## Android Studio / Gradle Performance Baseline

Put these settings in place before profiling:

- Prefer **KSP over kapt**. If a library supports KSP, migrate immediately.
- Use **static dependency versions** only. Never use `+`, `latest.release`, or floating plugin versions.
- Put `google()` and `mavenCentral()` before `gradlePluginPortal()` in plugin repositories unless a plugin truly requires otherwise.
- Keep debug-only values **static**. Dynamic versioning and manifest/resource generation belong in release-oriented variants only.
- Avoid unnecessary dev resources. Restrict extra locales and densities in the dev flavor where appropriate.
- Use **non-transitive R classes** and **non-constant R classes**. Treat the AGP 8+ defaults as the standard.
- Convert large PNG inventories to **WebP** when feasible; otherwise avoid build-time image work in debug.
- Move expensive custom Gradle logic into **cacheable tasks** instead of executing it during configuration.
- Modularize large apps so Gradle can recompile less code and parallelize more effectively.

## Recommended gradle.properties Baseline

```properties
# Gradle core
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn
org.gradle.parallel=true
org.gradle.caching=true

# AndroidX
android.useAndroidX=true
android.enableJetifier=false

# JVM
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8 -XX:+UseParallelGC -XX:MaxMetaspaceSize=1g
```

Rules:

- Increase heap size only when Build Analyzer shows GC overhead is a real bottleneck.
- Keep `-XX:MaxMetaspaceSize` and `-XX:+HeapDumpOnOutOfMemoryError` explicit when overriding `org.gradle.jvmargs`.
- If configuration cache causes plugin issues, fix the plugin/build logic first; fall back to disabling it only when blocked.

## Recommended settings.gradle.kts Repositories

```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
```

Rules:

- Put the repositories most likely to satisfy requests first.
- Do not scatter repositories across module build files.
- Prefer centralized repository declaration in `settings.gradle.kts`.

## Three Build Variants (Mandatory)

Every Android project MUST define exactly 3 build variants: **debug** (dev), **staging**, and **release** (prod). This is a hard requirement for all apps.

### Variant Summary

| Variant | APK Prefix | API Server | Minified | Signing | Install |
|---------|-----------|------------|----------|---------|---------|
| debug | `{App}-dev` | Local dev server | No | Debug keystore | Emulator (default) |
| staging | `{App}-staging` | User-provided staging URL | Yes (R8) | Debug keystore | Emulator (on request) |
| release | `{App}-prod` | User-provided production URL | Yes (R8) | Release keystore | Device (manual) |

### User Must Specify

Before setting up build variants, the user MUST provide:

1. **Staging API URL** (for example `https://staging.example.com/api/`)
2. **Production API URL** (for example `https://app.example.com/api/`)

The debug URL is always the local dev server (emulator uses `http://10.0.2.2/...` to reach the host machine).

### Build & Install Workflow

**Default local development loop:**

```bash
./gradlew installDebug
```

Use `assembleDebug` instead of `installDebug` when the user only needs an APK or when no emulator/device is attached.

**When the user explicitly asks to build all deliverables, prepare QA artifacts, or verify release outputs:**

```bash
./gradlew assembleDebug assembleStaging assembleRelease
```

**If the user explicitly asks to test staging:**

```bash
./gradlew installStaging
```

Never install release to an emulator unless explicitly asked. Release builds typically require a real signing key.

## Dev Flavor Resource Trimming

Use a lightweight dev flavor when the app carries many locales or density-specific assets:

```kotlin
android {
    flavorDimensions += "env"
    productFlavors {
        create("dev") {
            dimension = "env"
            resourceConfigurations += listOf("en", "xxhdpi")
        }
    }
}
```

This keeps local builds smaller and faster without weakening production variants.

## Local Development Networking (WAMP)

- On local Windows or Ubuntu dev machines, the Android emulator must reach the backend via `10.0.2.2` (emulator alias for host localhost) or the host machine's static LAN IP.
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

        // Keep debug values static for fast iteration.
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
            buildConfigField("String", "API_BASE_URL", "\"https://app.example.com/api/\"")
        }
        create("staging") {
            initWith(getByName("release"))
            signingConfig = signingConfigs.getByName("debug")
            buildConfigField("String", "API_BASE_URL", "\"https://staging.example.com/api/\"")
        }
    }

    androidResources {
        nonTransitiveRClass = true
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

androidComponents {
    onVariants { variant ->
        val apkPrefix = when (variant.buildType) {
            "debug" -> "MyApp-dev"
            "staging" -> "MyApp-staging"
            "release" -> "MyApp-prod"
            else -> "MyApp"
        }

        variant.outputs.forEach { output ->
            output.outputFileName.set("$apkPrefix-${variant.versionName.orNull ?: "0.0.0"}.apk")
        }
    }
}
```

### Key Points

- **staging `initWith(release)`**: inherits R8 minification and resource shrinking from release.
- **staging `signingConfig = debug`**: allows installation on emulator or device without the release keystore.
- **APK naming**: consistent `{AppName}-{dev|staging|prod}-{version}.apk` format via the Android Components Variant API.
- **BuildConfig fields**: each variant has its own `API_BASE_URL`. Code uses `BuildConfig.API_BASE_URL` everywhere.
- **Static debug values**: keep debug values stable. Do not generate dynamic values that force full rebuilds every run.
- **KSP only**: prefer symbol processing everywhere. Add `kapt` only when a dependency has no viable KSP path.
- **Non-transitive R**: faster multi-module builds and less resource churn.

## ProGuard Rules (Mandatory for Staging + Release)

```proguard
# proguard-rules.pro

# Retrofit
-keepattributes Signature
-keepattributes *Annotation*
-keep class retrofit2.** { *; }
-keepclasseswithmembers class * {
    @retrofit2.http.* <methods>;
}

# Moshi codegen only
-keep class com.squareup.moshi.** { *; }
-keep @com.squareup.moshi.JsonQualifier interface *
-keepclassmembers @com.squareup.moshi.JsonClass class * extends java.lang.Enum {
    <fields>;
}
-keepnames @com.squareup.moshi.JsonClass class *
-if @com.squareup.moshi.JsonClass class *
-keep class <1>JsonAdapter { <init>(...); }

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }

# Google Tink / EncryptedSharedPreferences
-dontwarn com.google.errorprone.annotations.**
-dontwarn com.google.api.client.http.**
-dontwarn com.google.api.client.http.javanet.**
-dontwarn org.joda.time.Instant
-keep class com.google.crypto.tink.** { *; }

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
-keep @androidx.room.Dao class *

# Kotlin coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
-keepclassmembers class kotlinx.coroutines.** {
    volatile <fields>;
}

# Kotlin metadata
-keepattributes RuntimeVisibleAnnotations

# Hilt
-keep class dagger.hilt.** { *; }
-keep class * extends dagger.hilt.android.internal.managers.ViewComponentManager$FragmentContextWrapper { *; }

# Strip debug logging from staging and release builds
-assumenosideeffects class android.util.Log {
    public static int v(...);
    public static int d(...);
    public static int i(...);
}
-assumenosideeffects class kotlin.io.ConsoleKt {
    public static void println(...);
}

# Keep DTOs
-keep class com.company.appname.**.dto.** { *; }
```

### R8 Missing Classes

When R8 reports missing classes, check `app/build/outputs/mapping/{variant}/missing_rules.txt` for the exact `-dontwarn` rules needed. Common culprits: Google Tink, errorprone annotations, and Joda Time.

## Dependencies (Organized by Category)

```kotlin
dependencies {
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
    ksp(libs.moshi.codegen)

    // Room
    implementation(libs.room.runtime)
    implementation(libs.room.ktx)
    ksp(libs.room.compiler)

    // Security
    implementation(libs.security.crypto)

    // Image loading
    implementation(libs.coil.compose)
    implementation(libs.coil.network.okhttp)

    // Charts
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
2. **Default local loop is debug only** — use `./gradlew installDebug` or `assembleDebug` unless the user asks for more.
3. **Build all 3 APKs only when needed** — `./gradlew assembleDebug assembleStaging assembleRelease` for QA, CI, or release verification.
4. **Install dev to emulator by default** — `./gradlew installDebug`
5. **Install staging only when user explicitly requests it** — `./gradlew installStaging`
6. **User provides staging + prod URLs** — never guess or hardcode server URLs
7. **APK naming**: `{AppName}-dev-{ver}.apk`, `{AppName}-staging-{ver}.apk`, `{AppName}-prod-{ver}.apk`
8. **Never commit signing keys** — use `local.properties` or CI secrets
9. **Enable R8/ProGuard** for staging and release builds
10. **Shrink resources** in staging and release builds
11. **Strip debug logs** (Log.v/d/i + println) from staging and release via ProGuard rules
12. **Use version catalog** for all projects (`gradle/libs.versions.toml`)
13. **Pin dependency versions** — no dynamic versions (`+`)
14. **Prefer KSP over kapt** — treat kapt as legacy and justify every remaining use
15. **Disable Jetifier** unless dependency analysis proves it is still required
16. **Enable configuration cache** when the plugin set is compatible
17. **Keep debug build config static** — no dynamic versioning or manifest/resource churn in the debug path
18. **Network security config MUST have `<base-config>`** — without it, staging and release HTTPS can fail on physical devices. See `security.md` for details.
19. **Extract real certificate pins before enabling cert pinning** — never use placeholder pins. Use `ENABLE_CERT_PINNING` as a build flag (`false` for dev, `true` for staging and prod).
20. **Pin ALL server domains** — both staging and production.

## Build Speed Troubleshooting Order

When builds feel slow, optimize in this order:

1. **Check Build Analyzer** in Android Studio. Do not guess first.
2. **Eliminate kapt** and unsupported annotation processors where possible.
3. **Remove configuration-phase work** from Gradle scripts and move it into lazy, cacheable tasks.
4. **Verify configuration cache reuse** on repeated builds.
5. **Disable Jetifier** if safe.
6. **Trim dev resources** and confirm debug values are static.
7. **Increase JVM heap** only if GC overhead is actually high.
8. **Experiment with `UseParallelGC`** only after measuring the baseline.
9. **Modularize** when repeated work is caused by large monolithic modules.

## Critical R8 / Moshi Rules

**Never use `moshi-kotlin` (reflection adapter) with R8-minified builds.** `KotlinJsonAdapterFactory` relies on Kotlin reflection metadata that R8 strips, causing runtime crashes on staging and release APKs that appear fine in debug.

**Instead:** use `moshi-codegen` (KSP) only. Every DTO data class must have `@JsonClass(generateAdapter = true)`. The Moshi builder should be:

```kotlin
Moshi.Builder().build()
```

**Never:**

```kotlin
Moshi.Builder()
    .addLast(KotlinJsonAdapterFactory())
    .build()
```

## Image URL Construction Rule

Never hardcode server URLs (for example `http://10.0.2.2/DMS_web/`) in image loading or anywhere else. Always derive from `BuildConfig.API_BASE_URL`:

```kotlin
fun buildImageUrl(relativePath: String): String {
    val baseUrl = BuildConfig.API_BASE_URL
    val rootUrl = baseUrl.replace("/api/", "/")
    return rootUrl + relativePath.trimStart('/')
}
```

Place this utility in a shared location and import it wherever images are loaded. Hardcoded URLs often work in debug and then fail in staging or production.
