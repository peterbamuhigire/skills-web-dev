# Tools, Libraries & CI Setup for Android TDD

## Essential Dependencies

### build.gradle.kts (Module Level)

```kotlin
dependencies {
    // --- Unit Testing ---
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.mockito.kotlin:mockito-kotlin:5.2.1")
    testImplementation("org.mockito:mockito-inline:5.2.0")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("app.cash.turbine:turbine:1.0.0") // Flow testing
    testImplementation("com.google.truth:truth:1.1.5") // Better assertions

    // --- Integration Testing ---
    testImplementation("androidx.arch.core:core-testing:2.2.0")
    testImplementation("androidx.room:room-testing:2.6.1")
    testImplementation("com.squareup.okhttp3:mockwebserver:4.12.0")

    // --- Android Instrumented Testing ---
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test:runner:1.5.2")
    androidTestImplementation("androidx.test:rules:1.5.0")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.test.espresso:espresso-contrib:3.5.1")
    androidTestImplementation("androidx.test.espresso:espresso-intents:3.5.1")

    // --- Compose Testing ---
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.4")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.5.4")

    // --- Hilt Testing ---
    testImplementation("com.google.dagger:hilt-android-testing:2.50")
    kaptTest("com.google.dagger:hilt-compiler:2.50")
    androidTestImplementation("com.google.dagger:hilt-android-testing:2.50")
    kaptAndroidTest("com.google.dagger:hilt-compiler:2.50")
}
```

## Library Purposes

| Library | Purpose | Test Type |
|---------|---------|-----------|
| **JUnit 4** | Test runner and assertions | Unit |
| **Mockito-Kotlin** | Mocking dependencies | Unit |
| **Coroutines Test** | Testing suspend functions and Flows | Unit |
| **Turbine** | Flow assertion library (cleaner than raw collection) | Unit |
| **Truth** | Fluent assertions (Google) | Unit |
| **Core Testing** | InstantTaskExecutorRule for LiveData | Unit |
| **Room Testing** | In-memory database for DAO tests | Integration |
| **MockWebServer** | Fake HTTP server for API tests | Integration |
| **Espresso** | View-based UI testing | UI |
| **Compose Test** | Compose UI testing | UI |
| **Hilt Testing** | Dependency injection in tests | All |

## Test Configuration

### build.gradle.kts Settings

```kotlin
android {
    testOptions {
        unitTests {
            isIncludeAndroidResources = true // For Robolectric
            isReturnDefaultValues = true     // Avoid Android stub errors
        }
        animationsDisabled = true // Faster UI tests
    }
}
```

### Test Runner (for instrumented tests)

```kotlin
android {
    defaultConfig {
        testInstrumentationRunner = "com.example.app.HiltTestRunner"
    }
}
```

```kotlin
class HiltTestRunner : AndroidJUnitRunner() {
    override fun newApplication(
        cl: ClassLoader?,
        className: String?,
        context: android.content.Context?
    ): Application {
        return super.newApplication(cl, HiltTestApplication::class.java.name, context)
    }
}
```

## Continuous Integration

### GitHub Actions

```yaml
name: Android TDD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ hashFiles('**/*.gradle*') }}
      - name: Run Unit Tests
        run: ./gradlew testDebugUnitTest
      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: unit-test-results
          path: app/build/reports/tests/

  instrumented-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - name: Run Instrumented Tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 30
          script: ./gradlew connectedDebugAndroidTest

  coverage:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - name: Generate Coverage Report
        run: ./gradlew jacocoTestReport
      - name: Upload Coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: app/build/reports/jacoco/
```

### CI Rules

- All unit tests must pass before merge
- Coverage threshold: warn below 60%, fail below 40%
- Instrumented tests run on PRs to main only (slower)
- Test reports archived as build artifacts

## Code Coverage with JaCoCo

### build.gradle.kts

```kotlin
plugins {
    id("jacoco")
}

tasks.withType<Test> {
    finalizedBy("jacocoTestReport")
}

tasks.register<JacocoReport>("jacocoTestReport") {
    dependsOn("testDebugUnitTest")

    reports {
        xml.required.set(true)
        html.required.set(true)
    }

    val fileFilter = listOf(
        "**/R.class", "**/R$*.class",
        "**/BuildConfig.*", "**/Manifest*.*",
        "**/*Test*.*", "**/*Fake*.*",
        "**/di/**", "**/hilt_aggregated_deps/**"
    )

    classDirectories.setFrom(
        fileTree("$buildDir/tmp/kotlin-classes/debug") {
            exclude(fileFilter)
        }
    )
    sourceDirectories.setFrom("$projectDir/src/main/java")
    executionData.setFrom("$buildDir/jacoco/testDebugUnitTest.exec")
}
```

## Running Tests Locally

```bash
# All unit tests
./gradlew test

# Specific module
./gradlew :app:testDebugUnitTest

# Single test class
./gradlew test --tests "com.example.UserViewModelTest"

# Single test method
./gradlew test --tests "com.example.UserViewModelTest.fetchUsers_success"

# With coverage
./gradlew testDebugUnitTest jacocoTestReport

# Instrumented tests (requires emulator/device)
./gradlew connectedAndroidTest
```

## IDE Integration (Android Studio)

- **Run test:** Click green arrow next to test method
- **Run all in class:** Click green arrow next to class name
- **Debug test:** Right-click > Debug
- **Coverage:** Right-click > Run with Coverage
- **Keyboard shortcut:** Ctrl+Shift+F10 (run current test)

## Recommended Plugins

| Plugin | Purpose |
|--------|---------|
| **JUnit** | Built-in test runner |
| **Coverage** | Built-in code coverage |
| **Kotest** | Alternative test framework (optional) |
| **Test Recorder** | Record Espresso tests from UI interactions |
