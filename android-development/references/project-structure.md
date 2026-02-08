# Project Structure Standards

Standard Android project layout for scalable, maintainable applications.

**References:**
- [Now in Android](https://github.com/android/nowinandroid) - production multi-module layout with convention plugins
- [Architecture Samples](https://github.com/android/architecture-samples) - single-module layered layout with product flavors (mock/prod)

## Directory Layout

```
project-root/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/company/           # Java sources (legacy only)
│   │   │   ├── kotlin/com/company/        # Primary Kotlin sources
│   │   │   │   ├── core/                  # Core business logic
│   │   │   │   │   ├── di/                # Dependency injection modules
│   │   │   │   │   ├── models/            # Data models / domain entities
│   │   │   │   │   ├── repositories/      # Repository interfaces
│   │   │   │   │   ├── usecases/          # Business use cases
│   │   │   │   │   └── utils/             # Core utilities
│   │   │   │   ├── data/
│   │   │   │   │   ├── local/             # Room database, DAOs
│   │   │   │   │   ├── remote/            # Retrofit API services
│   │   │   │   │   └── datasources/       # Data source implementations
│   │   │   │   ├── presentation/
│   │   │   │   │   ├── components/        # Reusable UI components
│   │   │   │   │   ├── screens/           # Screen composables
│   │   │   │   │   ├── viewmodels/        # ViewModels
│   │   │   │   │   └── navigation/        # Navigation graphs
│   │   │   │   ├── theme/                 # Design system tokens
│   │   │   │   └── MainActivity.kt
│   │   │   ├── res/                       # Resources
│   │   │   └── AndroidManifest.xml
│   │   ├── debug/                         # Debug-only config
│   │   ├── release/                       # Release-only config
│   │   ├── test/                          # Unit tests
│   │   └── androidTest/                   # Instrumentation tests
│   └── build.gradle.kts
├── buildSrc/                              # Convention plugins
├── gradle/
│   └── libs.versions.toml                 # Version catalog
├── build.gradle.kts                       # Root build file
└── settings.gradle.kts
```

## Package Organization Rules

### By Feature (Preferred for Large Apps)

```
com.company.app/
  feature/
    auth/
      data/          # Auth-specific data sources
      domain/        # Auth use cases
      presentation/  # Auth screens + ViewModels
    profile/
      data/
      domain/
      presentation/
    orders/
      data/
      domain/
      presentation/
  core/              # Shared across features
    di/
    models/
    network/
    utils/
```

### By Layer (Simpler Apps)

```
com.company.app/
  core/
    di/
    models/
    repositories/
    usecases/
    utils/
  data/
    local/
    remote/
    datasources/
  presentation/
    components/
    screens/
    viewmodels/
    navigation/
  theme/
```

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Screen | `{Feature}Screen.kt` | `UserProfileScreen.kt` |
| ViewModel | `{Feature}ViewModel.kt` | `UserProfileViewModel.kt` |
| Repository Interface | `{Entity}Repository.kt` | `UserRepository.kt` |
| Repository Impl | `{Entity}RepositoryImpl.kt` | `UserRepositoryImpl.kt` |
| Use Case | `{Action}{Entity}UseCase.kt` | `GetUserUseCase.kt` |
| API Service | `{Feature}ApiService.kt` | `UserApiService.kt` |
| DAO | `{Entity}Dao.kt` | `UserDao.kt` |
| Database | `{App}Database.kt` | `SaasDatabase.kt` |
| DI Module | `{Scope}Module.kt` | `AppModule.kt`, `NetworkModule.kt` |
| UI State | `{Feature}UiState.kt` | `UserProfileUiState.kt` |
| Component | `Standard{Name}.kt` | `StandardButton.kt` |

## Module Organization (Multi-Module)

For larger apps, split into Gradle modules:

```
:app                    # Application module
:core:common            # Shared utilities
:core:network           # Networking (Retrofit, OkHttp)
:core:database          # Room database
:core:ui                # Design system, shared components
:feature:auth           # Authentication feature
:feature:profile        # Profile feature
:feature:orders         # Orders feature
```

### Module Dependencies

- `:app` depends on all `:feature:*` modules
- `:feature:*` depends on `:core:*` modules
- `:core:*` modules are independent of each other
- No circular dependencies between features

## Resource Organization

```
res/
├── drawable/           # Vector drawables, icons
├── layout/             # XML layouts (if using Views)
├── mipmap/             # App launcher icons
├── values/
│   ├── colors.xml      # Color resources
│   ├── strings.xml     # String resources
│   ├── dimens.xml      # Dimension resources
│   └── themes.xml      # Theme definitions
├── values-night/       # Dark theme overrides
├── xml/
│   └── network_security_config.xml
└── raw/                # Raw files (certificates, etc.)
```

## Key Rules

1. **One class per file** - except closely related sealed classes/enums
2. **No God classes** - split large ViewModels by feature
3. **Keep `MainActivity.kt` thin** - only navigation setup
4. **Tests mirror source** - `test/` matches `main/` package structure
5. **Resources use prefixes** - `ic_` for icons, `bg_` for backgrounds, `btn_` for buttons
