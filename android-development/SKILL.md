---
name: android-development
description: "Android development standards for AI agent implementation. Kotlin-first, Jetpack Compose UI, MVVM + Clean Architecture, Hilt DI, comprehensive security, testing, and performance patterns. Use when building or reviewing Android applications, generating Kotlin code, or setting up Android project structure."
---

# Android Development Standards

Production-grade Android development standards for AI-assisted implementation. Kotlin-first with Jetpack Compose, following modern Android best practices.

**Core Stack:** Kotlin 100% | Jetpack Compose | MVVM + Clean Architecture | Hilt DI
**Min SDK:** 28 (Android 9.0) | **Target SDK:** 34
**Reference App:** [Now in Android](https://github.com/android/nowinandroid) - Google's official sample demonstrating these standards in a production-quality codebase

## When to Use

- Building new Android applications or features
- Reviewing Android code for quality and standards compliance
- Generating Kotlin/Compose code via AI agents
- Setting up Android project structure
- Implementing security, testing, or performance patterns
- Integrating with REST APIs from Android clients

## Quick Reference

| Topic | Reference File | Covers |
|-------|---------------|--------|
| **Project Structure** | `references/project-structure.md` | Directory layout, module organization |
| **Kotlin Conventions** | `references/kotlin-conventions.md` | Coding style, Compose patterns |
| **Architecture** | `references/architecture-patterns.md` | MVVM, Clean Architecture layers |
| **Dependency Injection** | `references/dependency-injection.md` | Hilt modules, scoping, ViewModel injection |
| **Security** | `references/security.md` | Encrypted storage, biometrics, network security |
| **UI Design System** | `references/ui-design-system.md` | Tokens, components, Material 3 |
| **Screen Patterns** | `references/screen-patterns.md` | Complete screen templates, state handling |
| **Testing** | `references/testing.md` | Unit, UI, instrumentation tests |
| **Build Configuration** | `references/build-configuration.md` | Gradle KTS, dependencies, build types |
| **API Integration** | `references/api-integration.md` | Retrofit, error handling, repository pattern |
| **Analytics & Performance** | `references/analytics-performance.md` | Firebase, monitoring, optimization |
| **AI Agent Guidelines** | `references/ai-agent-guidelines.md` | Prompt templates, quality checklists |

## Architecture Overview

```
Presentation Layer (Compose + ViewModels)
         |
    Domain Layer (Use Cases + Repository Interfaces)
         |
    Data Layer (Repository Impl + API + Room)
```

### Layer Rules

1. **Presentation** depends on Domain only
2. **Domain** has no Android dependencies (pure Kotlin)
3. **Data** implements Domain interfaces, handles API/DB

### Package Structure

```
com.company.app/
  core/          # Shared: DI, models, repositories, utils
  data/          # Room DB, API services, data sources
  presentation/  # Screens, ViewModels, components, navigation
  theme/         # Design system tokens
```

## Key Standards Summary

### Kotlin

- 100% Kotlin, no Java for new code
- Coroutines + Flow for async (never callbacks)
- Sealed classes for UI state modeling
- Extension functions for utility code

### Compose

- Stateless composables preferred (state hoisted to ViewModel)
- `LaunchedEffect` for side effects, never in composition
- `collectAsStateWithLifecycle()` for Flow collection
- Stable keys for `LazyColumn`/`LazyRow` items

### Security

- `EncryptedSharedPreferences` for sensitive data
- Certificate pinning for API calls
- Biometric authentication for sensitive operations
- No hardcoded secrets, use `BuildConfig` fields
- ProGuard/R8 for release builds

### Testing

- Unit tests for ViewModels and Use Cases (MockK)
- Compose UI tests for screens (ComposeTestRule)
- Turbine for Flow testing
- Hilt test rules for DI in tests

### Performance

- StrictMode in debug builds
- Stable keys in lazy lists
- `derivedStateOf` for expensive calculations
- Image loading via Coil with caching
- ProGuard + resource shrinking in release

## Anti-Patterns

- Putting business logic in Composables
- Using `mutableStateOf` in ViewModels instead of `StateFlow`
- Hardcoding colors/dimensions instead of design tokens
- Skipping error states in UI
- Network calls on main thread
- Missing `key` parameter in `LazyColumn` items
- God ViewModels (split by feature, not by screen)
- Ignoring lifecycle (use `collectAsStateWithLifecycle`)

## Integration with Other Skills

```
feature-planning           -> spec + implementation strategy
  |
android-development        -> Kotlin/Compose implementation
  |
api-error-handling         -> Backend API error patterns
  |
mysql-best-practices       -> Database schema (backend)
  |
vibe-security-skill        -> Security review
```

**Always apply `vibe-security-skill`** alongside this skill for web-connected Android apps.

## Reference Implementation

**Now in Android** ([github.com/android/nowinandroid](https://github.com/android/nowinandroid)) is Google's official fully-functional reference app. Use it as the canonical example of:

- Multi-module architecture with convention plugins
- Jetpack Compose UI with Material 3
- Offline-first with Room + network sync
- Hilt dependency injection across modules
- Kotlin coroutines + Flow for reactive data
- Comprehensive testing (unit, UI, screenshot)
- Build configuration with version catalogs and Gradle KTS

When in doubt about how to structure something, check how Now in Android does it.
