# Local Storage: DataStore, SharedPreferences, Files

## DataStore (Recommended for Key-Value Storage)

DataStore replaces SharedPreferences with a safer, async API built on Kotlin coroutines and Flow.

### Gradle Dependency

```kotlin
implementation("androidx.datastore:datastore-preferences:1.0.0")
```

### Setup

```kotlin
// Create DataStore instance (top-level extension)
val Context.dataStore by preferencesDataStore(name = "app_settings")
```

### Define Keys

```kotlin
object PrefsKeys {
    val AUTH_TOKEN = stringPreferencesKey("auth_token")
    val REFRESH_TOKEN = stringPreferencesKey("refresh_token")
    val USER_ID = stringPreferencesKey("user_id")
    val DARK_MODE = booleanPreferencesKey("dark_mode")
    val SORT_ORDER = stringPreferencesKey("sort_order")
    val LANGUAGE = stringPreferencesKey("language")
    val ONBOARDING_COMPLETE = booleanPreferencesKey("onboarding_complete")
    val LAST_SYNC = longPreferencesKey("last_sync_timestamp")
}
```

### Reading Values

```kotlin
class SettingsRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    val darkMode: Flow<Boolean> = context.dataStore.data
        .catch { emit(emptyPreferences()) }
        .map { prefs -> prefs[PrefsKeys.DARK_MODE] ?: false }

    val sortOrder: Flow<String> = context.dataStore.data
        .catch { emit(emptyPreferences()) }
        .map { prefs -> prefs[PrefsKeys.SORT_ORDER] ?: "name_asc" }

    val authToken: Flow<String?> = context.dataStore.data
        .catch { emit(emptyPreferences()) }
        .map { prefs -> prefs[PrefsKeys.AUTH_TOKEN] }

    val isLoggedIn: Flow<Boolean> = context.dataStore.data
        .catch { emit(emptyPreferences()) }
        .map { prefs -> prefs[PrefsKeys.AUTH_TOKEN] != null }
}
```

### Writing Values

```kotlin
class SettingsRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    suspend fun setDarkMode(enabled: Boolean) {
        context.dataStore.edit { prefs ->
            prefs[PrefsKeys.DARK_MODE] = enabled
        }
    }

    suspend fun saveAuthTokens(authToken: String, refreshToken: String) {
        context.dataStore.edit { prefs ->
            prefs[PrefsKeys.AUTH_TOKEN] = authToken
            prefs[PrefsKeys.REFRESH_TOKEN] = refreshToken
        }
    }

    suspend fun clearSession() {
        context.dataStore.edit { prefs ->
            prefs.remove(PrefsKeys.AUTH_TOKEN)
            prefs.remove(PrefsKeys.REFRESH_TOKEN)
            prefs.remove(PrefsKeys.USER_ID)
        }
    }

    suspend fun updateLastSync() {
        context.dataStore.edit { prefs ->
            prefs[PrefsKeys.LAST_SYNC] = System.currentTimeMillis()
        }
    }
}
```

### ViewModel Usage

```kotlin
@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val settingsRepository: SettingsRepository
) : ViewModel() {

    val darkMode = settingsRepository.darkMode
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), false)

    fun toggleDarkMode() {
        viewModelScope.launch {
            settingsRepository.setDarkMode(!darkMode.value)
        }
    }
}
```

### Hilt Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DataStoreModule {
    @Provides
    @Singleton
    fun provideSettingsRepository(
        @ApplicationContext context: Context
    ): SettingsRepository = SettingsRepository(context)
}
```

## SharedPreferences (Legacy)

Use only when maintaining existing code. New features should use DataStore.

### Reading

```kotlin
val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
val darkMode = prefs.getBoolean("dark_mode", false)
val username = prefs.getString("username", "") ?: ""
val score = prefs.getInt("score", 0)
```

### Writing

```kotlin
prefs.edit()
    .putBoolean("dark_mode", true)
    .putString("username", "Peter")
    .putInt("score", 100)
    .apply()  // Async (preferred)
```

### EncryptedSharedPreferences (Sensitive Data)

**CRITICAL: Samsung/Knox Crash Prevention** — Always wrap EncryptedSharedPreferences initialization in try-catch with fallback to regular SharedPreferences. Samsung devices with Knox can throw `KeyStoreException` during `MasterKey` creation, crashing the app before any UI renders (during Hilt DI init). Do NOT use the deprecated `MasterKeys.getOrCreate()` API — use `MasterKey.Builder()`.

```kotlin
// Gradle
implementation("androidx.security:security-crypto:1.1.0-alpha06")

// Usage — ALWAYS use try-catch with fallback
val prefs: SharedPreferences = try {
    val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
} catch (e: Exception) {
    Log.e("SecurePrefs", "EncryptedSharedPreferences init failed, falling back", e)
    context.getSharedPreferences("secure_prefs", Context.MODE_PRIVATE)
}

// Same API as regular SharedPreferences
prefs.edit().putString("api_key", "secret123").apply()
```

## File Storage

### Internal Storage (Private to App)

```kotlin
class FileRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    // Write text file
    suspend fun saveTextFile(fileName: String, content: String) {
        withContext(Dispatchers.IO) {
            context.openFileOutput(fileName, Context.MODE_PRIVATE).use { stream ->
                stream.write(content.toByteArray())
            }
        }
    }

    // Read text file
    suspend fun readTextFile(fileName: String): String? {
        return withContext(Dispatchers.IO) {
            try {
                context.openFileInput(fileName).use { stream ->
                    stream.bufferedReader().readText()
                }
            } catch (e: FileNotFoundException) {
                null
            }
        }
    }

    // Delete file
    fun deleteFile(fileName: String): Boolean = context.deleteFile(fileName)

    // List files
    fun listFiles(): Array<String> = context.fileList()

    // Get file path
    fun getFilePath(fileName: String): File = File(context.filesDir, fileName)
}
```

### External Storage (Scoped Storage)

```kotlin
class MediaRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    // Save image to app-specific external directory
    suspend fun saveImage(bitmap: Bitmap, fileName: String): File? {
        return withContext(Dispatchers.IO) {
            val dir = context.getExternalFilesDir(Environment.DIRECTORY_PICTURES) ?: return@withContext null
            val file = File(dir, fileName)
            FileOutputStream(file).use { stream ->
                bitmap.compress(Bitmap.CompressFormat.JPEG, 85, stream)
            }
            file
        }
    }

    // Save document to app-specific external directory
    suspend fun saveDocument(content: ByteArray, fileName: String): File? {
        return withContext(Dispatchers.IO) {
            val dir = context.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS) ?: return@withContext null
            val file = File(dir, fileName)
            file.writeBytes(content)
            file
        }
    }

    // Check external storage availability
    fun isExternalStorageWritable(): Boolean =
        Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED
}
```

### Cache Directory

```kotlin
// Internal cache (automatically cleaned by system when space is low)
val cacheFile = File(context.cacheDir, "temp_data.json")
cacheFile.writeText(jsonData)

// External cache
val externalCacheFile = File(context.externalCacheDir, "temp_image.jpg")
```

## Storage Comparison

| Feature | DataStore | SharedPreferences | Files | Room |
|---------|-----------|-------------------|-------|------|
| **Data type** | Key-value | Key-value | Raw bytes | Structured |
| **API** | Flow (async) | Sync or apply() | Streams | Flow/Suspend |
| **Thread safety** | Built-in | Not safe | Manual | Built-in |
| **Type safety** | Keys typed | Cast required | None | Compile-time |
| **Encryption** | Via security lib | EncryptedSP | Manual | SQLCipher |
| **Size limit** | Small (KB) | Small (KB) | Any | Any |
| **Best for** | Settings | Legacy settings | Media/docs | App data |

## When to Use What

```
User preferences, flags, tokens → DataStore
├── Theme, language, sort order
├── Auth tokens (use EncryptedSharedPreferences for sensitive tokens)
└── Onboarding state, feature flags

Structured app data → Room
├── Products, orders, users
├── Cached API responses
└── Offline-first data

Raw files → File storage
├── Downloaded images/PDFs
├── User-captured photos
├── Exported reports
└── Temp/cache files

Sensitive credentials → EncryptedSharedPreferences
├── API keys
├── Biometric tokens
└── Encryption keys
```
