# Security Standards

Comprehensive security patterns for Android applications.

## Local Development Networking (WAMP)

- On local Windows/Ubuntu dev machines, the Android emulator must reach the backend via the host machine's static LAN IP, not `localhost`.
- Ensure firewall rules allow inbound access to the WAMP HTTP port.

## Encrypted Storage

```kotlin
@Singleton
class SecurityManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPreferences by lazy {
        EncryptedSharedPreferences.create(
            context,
            "secure_preferences",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun saveSecure(key: String, value: String) {
        encryptedPreferences.edit().putString(key, value).apply()
    }

    fun getSecure(key: String): String? {
        return encryptedPreferences.getString(key, null)
    }

    fun removeSecure(key: String) {
        encryptedPreferences.edit().remove(key).apply()
    }

    fun clearAll() {
        encryptedPreferences.edit().clear().apply()
    }
}
```

### Storage Rules

- **Always** use `EncryptedSharedPreferences` for tokens, keys, PII
- **Never** store secrets in plain `SharedPreferences`
- **Never** hardcode API keys, tokens, or passwords in source code
- Use `BuildConfig` fields for environment-specific values
- Clear sensitive data on logout

## Biometric Authentication

```kotlin
@Singleton
class BiometricManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    fun isBiometricAvailable(): Boolean {
        val manager = androidx.biometric.BiometricManager.from(context)
        return manager.canAuthenticate(
            androidx.biometric.BiometricManager.Authenticators.BIOMETRIC_STRONG
        ) == androidx.biometric.BiometricManager.BIOMETRIC_SUCCESS
    }

    suspend fun authenticate(
        activity: FragmentActivity,
        title: String = "Authentication Required",
        subtitle: String = "Use biometric to continue"
    ): Boolean = suspendCancellableCoroutine { continuation ->
        val executor = ContextCompat.getMainExecutor(context)

        val callback = object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(
                result: BiometricPrompt.AuthenticationResult
            ) {
                if (continuation.isActive) continuation.resume(true)
            }

            override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                if (continuation.isActive) continuation.resume(false)
            }

            override fun onAuthenticationFailed() {
                // Don't resume - user can retry
            }
        }

        val biometricPrompt = BiometricPrompt(activity, executor, callback)

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(title)
            .setSubtitle(subtitle)
            .setNegativeButtonText("Cancel")
            .setAllowedAuthenticators(
                androidx.biometric.BiometricManager.Authenticators.BIOMETRIC_STRONG
            )
            .build()

        biometricPrompt.authenticate(promptInfo)
    }
}
```

## Network Security

### Certificate Pinning

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkSecurityModule {

    @Provides
    @Singleton
    fun provideCertificatePinner(): CertificatePinner {
        return CertificatePinner.Builder()
            .add("api.company.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            .add("api.company.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")
            .build()
    }
}
```

### Network Security Config

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Disallow cleartext (HTTP) traffic -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Debug overrides (only in debug builds) -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>

    <!-- Pin specific domains -->
    <domain-config>
        <domain includeSubdomains="true">api.company.com</domain>
        <pin-set expiration="2025-12-31">
            <pin digest="SHA-256">PRIMARY_PIN_HERE</pin>
            <pin digest="SHA-256">BACKUP_PIN_HERE</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

Reference in `AndroidManifest.xml`:

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ... >
```

### Auth Interceptor

```kotlin
@Singleton
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        val token = tokenManager.getToken()
            ?: return chain.proceed(originalRequest)

        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .header("X-App-Version", BuildConfig.VERSION_NAME)
            .header("X-Platform", "Android")
            .build()

        val response = chain.proceed(authenticatedRequest)

        // Handle token refresh on 401
        if (response.code == 401) {
            response.close()
            val newToken = tokenManager.refreshToken()
            if (newToken != null) {
                val retryRequest = originalRequest.newBuilder()
                    .header("Authorization", "Bearer $newToken")
                    .build()
                return chain.proceed(retryRequest)
            }
        }

        return response
    }
}
```

## Token Management

```kotlin
@Singleton
class TokenManager @Inject constructor(
    private val securityManager: SecurityManager
) {
    companion object {
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_TOKEN_EXPIRY = "token_expiry"
    }

    fun saveTokens(accessToken: String, refreshToken: String, expiresIn: Long) {
        securityManager.saveSecure(KEY_ACCESS_TOKEN, accessToken)
        securityManager.saveSecure(KEY_REFRESH_TOKEN, refreshToken)
        securityManager.saveSecure(
            KEY_TOKEN_EXPIRY,
            (System.currentTimeMillis() + expiresIn * 1000).toString()
        )
    }

    fun getToken(): String? {
        val expiry = securityManager.getSecure(KEY_TOKEN_EXPIRY)?.toLongOrNull() ?: 0
        if (System.currentTimeMillis() >= expiry) return null
        return securityManager.getSecure(KEY_ACCESS_TOKEN)
    }

    fun getRefreshToken(): String? =
        securityManager.getSecure(KEY_REFRESH_TOKEN)

    fun clearTokens() {
        securityManager.removeSecure(KEY_ACCESS_TOKEN)
        securityManager.removeSecure(KEY_REFRESH_TOKEN)
        securityManager.removeSecure(KEY_TOKEN_EXPIRY)
    }

    suspend fun refreshToken(): String? {
        // Implement token refresh via API
        return null
    }
}
```

## Security Checklist

- Encrypted storage for all sensitive data
- Certificate pinning for API domains
- No cleartext HTTP traffic
- Biometric auth for sensitive operations
- Token rotation and secure refresh
- ProGuard/R8 obfuscation in release
- No logging of sensitive data in release
- Input validation and sanitization
- Root/jailbreak detection (if required)
- Secure WebView configuration (if used)
