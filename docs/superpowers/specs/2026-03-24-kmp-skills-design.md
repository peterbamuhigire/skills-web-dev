# KMP Skills Design Spec

## Summary

Add Kotlin Multiplatform (KMP) support to the skills repository through two new
skills and targeted updates to three existing skills.

**Strategy:** Shared logic, native UI. KMP shares business logic (domain, data,
networking) while Android keeps Jetpack Compose and iOS keeps SwiftUI for UI.

## New Skills

### 1. kmp-development

Governs the `shared/` module in KMP projects. Covers:

- Project structure: shared, composeApp, iosApp modules
- Source sets: commonMain, androidMain, iosMain
- Targets: androidTarget, iosX64, iosArm64, iosSimulatorArm64
- expect/actual mechanism for platform-specific code
- Dependency injection: Koin (recommended for KMP)
- Modularization: umbrella frameworks, multiple shared modules
- Libraries: Ktor (networking), SQLDelight/Room KMP (database), DataStore,
  Multiplatform Settings
- Native library integration: CocoaPods for iOS, standard Gradle for Android
- Tooling: SKIE (Swift interop), KMMBridge (framework publishing), KDoctor
- Build configuration: Gradle KTS with version catalogs

**Module-to-skill mapping:**
- `shared/` -> kmp-development (this skill)
- `composeApp/` -> android-development skill
- `iosApp/` -> ios-development skill

### 2. kmp-tdd

Cross-platform testing for the shared module. Covers:

- Test source sets: commonTest, androidUnitTest, iosTest
- Test framework: kotlin.test + Kotest
- Flow testing: Turbine
- Mocking: Mokkery (inspired by MockK, KMP-compatible)
- Test doubles: fakes, stubs, mocks -- when to use each
- Unit tests: use cases, repositories, ViewModels in commonTest
- Integration tests: Ktor MockEngine, SQLDelight in-memory drivers
- DI in tests: Koin test modules (testPlatformModule)
- Coverage: Kover (JVM/Android only, no native yet)
- Running tests: `./gradlew :shared:allTests`
- Red-Green-Refactor cycle adapted for multiplatform

## Existing Skill Updates

### android-development

Add a "KMP Projects" section (3-5 lines) stating: if this is a KMP project, the
`composeApp/` module follows this skill while `shared/` follows kmp-development.

### ios-development

Add a "KMP Projects" section (3-5 lines) stating: if this is a KMP project, the
`iosApp/` module follows this skill while `shared/` follows kmp-development.

### mobile-saas-planning

Add KMP as a third project type option alongside pure-Android and pure-iOS.
When KMP is selected, planning docs account for shared module architecture in
SDS, shared networking in API Contract, and cross-platform test strategy.

## Architecture Decision Records

- **DI choice: Koin** -- most popular in KMP community, no reflection on iOS,
  lightweight DSL, integrates well with existing Android Hilt patterns at the
  app level
- **Database choice: SQLDelight primary, Room KMP secondary** -- SQLDelight is
  the mature KMP-native option; Room KMP is newer but familiar to Android devs
- **Networking: Ktor** -- the standard KMP HTTP client, replaces Retrofit in
  shared module
- **Mocking: Mokkery** -- MockK-inspired but fully KMP-compatible across all
  targets
- **No Compose Multiplatform** -- native UI preserved; existing Compose/SwiftUI
  skills remain authoritative for their respective platforms
