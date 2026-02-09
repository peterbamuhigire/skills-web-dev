# Dependency Injection Standards

Hilt (Dagger) dependency injection with proper scoping for Android apps.

## Local Development Networking (WAMP)

- On local Windows/Ubuntu dev machines, the Android emulator must reach the backend via the host machine's static LAN IP, not `localhost`.
- Ensure firewall rules allow inbound access to the WAMP HTTP port.

## Setup

Application class must be annotated:

```kotlin
@HiltAndroidApp
class SaasApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // Initialize global dependencies
    }
}
```

Activities must be annotated:

```kotlin
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { AppNavGraph() }
    }
}
```

## Module Organization

### App Module (Singletons)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideSecurityManager(
        @ApplicationContext context: Context
    ): SecurityManager = SecurityManager(context)

    @Provides
    @Singleton
    fun provideTokenManager(
        securityManager: SecurityManager
    ): TokenManager = TokenManager(securityManager)
}
```

### Network Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG)
                HttpLoggingInterceptor.Level.BODY
            else
                HttpLoggingInterceptor.Level.NONE
        }
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        loggingInterceptor: HttpLoggingInterceptor,
        certificatePinner: CertificatePinner
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .certificatePinner(certificatePinner)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideUserApiService(retrofit: Retrofit): UserApiService {
        return retrofit.create(UserApiService::class.java)
    }
}
```

### Database Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context
    ): SaasDatabase {
        return Room.databaseBuilder(
            context,
            SaasDatabase::class.java,
            "saas_database"
        )
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideUserDao(database: SaasDatabase): UserDao {
        return database.userDao()
    }
}
```

### Repository Module (Binds Pattern)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository

    @Binds
    @Singleton
    abstract fun bindOrderRepository(
        impl: OrderRepositoryImpl
    ): OrderRepository
}
```

### Dispatcher Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {

    @IoDispatcher
    @Provides
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @MainDispatcher
    @Provides
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main

    @DefaultDispatcher
    @Provides
    fun provideDefaultDispatcher(): CoroutineDispatcher = Dispatchers.Default
}

// Qualifier annotations
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class DefaultDispatcher
```

## ViewModel Injection

### Standard (Recommended)

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase,
    private val updateUserUseCase: UpdateUserUseCase,
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    private val userId: String = checkNotNull(savedStateHandle["userId"])
}

// In Composable
@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel()
) { /* ... */ }
```

### With Assisted Injection (Dynamic Parameters)

```kotlin
@HiltViewModel(assistedFactory = UserViewModel.Factory::class)
class UserViewModel @AssistedInject constructor(
    @Assisted private val userId: String,
    private val userRepository: UserRepository
) : ViewModel() {

    @AssistedFactory
    interface Factory {
        fun create(userId: String): UserViewModel
    }
}
```

## Scoping Guidelines

| Scope                     | Component                   | Lifecycle              | Use For                          |
| ------------------------- | --------------------------- | ---------------------- | -------------------------------- |
| `@Singleton`              | `SingletonComponent`        | App lifetime           | OkHttp, Retrofit, Room, Managers |
| `@ActivityScoped`         | `ActivityComponent`         | Activity lifetime      | Rarely needed                    |
| `@ViewModelScoped`        | `ViewModelComponent`        | ViewModel lifetime     | Shared within ViewModel          |
| `@ActivityRetainedScoped` | `ActivityRetainedComponent` | Survives config change | Rarely needed                    |
| Unscoped                  | N/A                         | New instance each time | Use Cases, Mappers               |

### Scoping Rules

- **Singleton** for expensive objects (HTTP clients, databases)
- **Unscoped** for lightweight objects (use cases, mappers)
- **Never scope ViewModels manually** - Hilt handles this via `@HiltViewModel`
- **Avoid `@ActivityScoped`** unless truly needed

## Testing with Hilt

```kotlin
@HiltAndroidTest
class UserProfileTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Module
    @InstallIn(SingletonComponent::class)
    object TestModule {
        @Provides
        @Singleton
        fun provideFakeUserRepository(): UserRepository = FakeUserRepository()
    }

    @Before
    fun setup() {
        hiltRule.inject()
    }
}
```

## Anti-Patterns

- Manual instantiation (`val repo = UserRepositoryImpl(...)`)
- Injecting `Context` into ViewModels (use `@ApplicationContext` in data layer)
- Over-scoping (making everything `@Singleton`)
- Circular dependencies between modules
- Injecting concrete classes instead of interfaces
