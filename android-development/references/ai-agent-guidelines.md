# AI Agent Implementation Guidelines

Standards for AI agents generating Android code.

## Standard Implementation Request Template

When requesting Android implementation from an AI agent, use this structure:

```
PROJECT: [Project Name]
FEATURE: [Feature Name]

REQUIREMENTS:
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

TECH STACK:
- Minimum SDK: 28 (Android 9.0)
- Target SDK: 34
- Language: Kotlin 100%
- UI: Jetpack Compose
- Architecture: MVVM with Clean Architecture
- DI: Hilt

DELIVERABLES:
- [ ] Feature implementation (all layers)
- [ ] Unit tests (ViewModel + Use Case)
- [ ] UI tests (key screens)
- [ ] Error handling (all states)
- [ ] Analytics tracking

SPECIAL INSTRUCTIONS:
[Any additional context]
```

## AI Output Quality Checklist

### Architecture Compliance

- [ ] Clean Architecture layers separated (data, domain, presentation)
- [ ] ViewModel uses `StateFlow`, not `mutableStateOf` or `LiveData`
- [ ] Use Cases have single `invoke` operator function
- [ ] Repository interface in domain, implementation in data
- [ ] No Android imports in domain layer

### Compose Standards

- [ ] All composables accept `Modifier` parameter
- [ ] Side effects use `LaunchedEffect` / `DisposableEffect`
- [ ] Flow collected with `collectAsStateWithLifecycle()`
- [ ] Stable keys provided for lazy list items
- [ ] Private sub-composables for screen content

### State Management

- [ ] UI state modeled with sealed interface or data class
- [ ] Loading, error, empty, and success states handled
- [ ] Side effects via `Channel` for one-time events
- [ ] Back handler for unsaved form changes

### Security

- [ ] Sensitive data uses `EncryptedSharedPreferences`
- [ ] No hardcoded secrets in source code
- [ ] Certificate pinning configured
- [ ] Auth tokens managed via `TokenManager`
- [ ] No logging of sensitive data in release

### Error Handling

- [ ] `safeApiCall` wrapper for all network operations
- [ ] Typed exception hierarchy used
- [ ] User-friendly error messages (not stack traces)
- [ ] Retry mechanism for recoverable errors
- [ ] Offline fallback where appropriate

### Testing

- [ ] ViewModel tests with Turbine for Flow
- [ ] Use Case tests with MockK
- [ ] Repository tests with mock API responses
- [ ] `MainDispatcherRule` for coroutine tests
- [ ] Error path tests included

### Performance

- [ ] No main-thread blocking operations
- [ ] Image loading via Coil (not manual)
- [ ] `derivedStateOf` for expensive calculations
- [ ] Proper pagination for large lists

## Layer-by-Layer Implementation Order

When implementing a feature, follow this order:

### 1. Domain Layer (First)

```
1. Define domain model (data class)
2. Define repository interface
3. Create use case(s)
```

### 2. Data Layer

```
1. Create DTO with mapping to domain
2. Create API service interface
3. Create Room entity + DAO (if caching)
4. Implement repository
```

### 3. Presentation Layer

```
1. Define UI state sealed interface/data class
2. Create ViewModel
3. Create screen composable
4. Wire up navigation
```

### 4. DI Layer

```
1. Add API service to NetworkModule
2. Bind repository in RepositoryModule
3. Add DAO to DatabaseModule (if needed)
```

### 5. Tests

```
1. Use Case unit tests
2. Repository unit tests
3. ViewModel unit tests
4. Screen UI tests
```

## Common AI Mistakes to Avoid

### Architecture

- Putting business logic in composables instead of use cases
- Skipping the domain layer (calling API directly from ViewModel)
- Using `mutableStateOf` in ViewModel instead of `StateFlow`
- Missing the mapper between DTO and domain model

### Compose

- Forgetting `Modifier` parameter on composables
- Using `remember { mutableStateOf() }` for ViewModel state
- Side effects outside `LaunchedEffect`
- Missing `key` in `LazyColumn` items
- Not handling all UI states (loading, error, empty)

### Kotlin

- Using Java patterns (e.g., `static` instead of `companion object`)
- Callback-based async instead of coroutines
- Not using `sealed interface` for state modeling
- Forgetting null safety patterns

### Testing

- Not injecting test dispatchers
- Testing implementation details instead of behavior
- Missing error path tests
- Not using Turbine for Flow assertions

## File Generation Checklist

For each new feature, AI should generate:

```
feature/
├── data/
│   ├── dto/{Feature}Dto.kt
│   ├── remote/{Feature}ApiService.kt
│   └── repository/{Feature}RepositoryImpl.kt
├── domain/
│   ├── model/{Feature}.kt
│   ├── repository/{Feature}Repository.kt
│   └── usecase/Get{Feature}UseCase.kt
├── presentation/
│   ├── {Feature}Screen.kt
│   ├── {Feature}ViewModel.kt
│   └── {Feature}UiState.kt
└── di/
    └── {Feature}Module.kt (if feature-scoped)
```
