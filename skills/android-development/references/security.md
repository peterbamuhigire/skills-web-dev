# Security Standards

Comprehensive security patterns for Android applications.

## Local Development Networking (WAMP)

- On local Windows/Ubuntu dev machines, the Android emulator must reach the backend via the host machine's static LAN IP, not `localhost`.
- Ensure firewall rules allow inbound access to the WAMP HTTP port.

## Encrypted Storage

**CRITICAL: Samsung/Knox Crash Prevention** — Always wrap EncryptedSharedPreferences initialization in try-catch with fallback to regular SharedPreferences. Samsung devices with Knox can throw `KeyStoreException` during `MasterKey` creation, crashing the app before any UI renders (during Hilt DI init). Do NOT use the deprecated `MasterKeys.getOrCreate()` API — use `MasterKey.Builder()`.

```kotlin
@Singleton
class SecurityManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    // MUST use try-catch — Samsung Knox throws KeyStoreException
    private val encryptedPreferences: SharedPreferences = try {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        EncryptedSharedPreferences.create(
            context,
            "secure_preferences",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    } catch (e: Exception) {
        Log.e("SecurityManager", "EncryptedSharedPreferences init failed, falling back", e)
        context.getSharedPreferences("secure_preferences", Context.MODE_PRIVATE)
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

- **Always** use `EncryptedSharedPreferences` for tokens, keys, PII (with try-catch fallback)
- **Never** store secrets in plain `SharedPreferences` (unless as fallback for Keystore failure)
- **Never** hardcode API keys, tokens, or passwords in source code
- Use `BuildConfig` fields for environment-specific values
- Clear sensitive data on logout
- **Never** use deprecated `MasterKeys.getOrCreate()` — use `MasterKey.Builder()`

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

**CRITICAL: Never use placeholder pins.** Placeholder pins (`AAA...=`, `BBB...=`) will cause `SSLPeerUnverifiedException` at runtime, silently breaking all HTTPS connections on staging/production builds. Extract real pins before enabling.

**Let's Encrypt Warning:** If the server uses Let's Encrypt (most VPS setups), leaf certificate pins rotate every 90 days on auto-renewal. **Always pin the intermediate CA** (stable) alongside the leaf pin. OkHttp accepts if ANY pin matches per host, so the intermediate CA pin survives renewals.

#### How to Extract Real Certificate Pins

Run from Git Bash (or any terminal with openssl):

```bash
# Leaf certificate pin (changes every 90 days with Let's Encrypt)
echo | openssl s_client -connect YOUR_DOMAIN:443 -servername YOUR_DOMAIN 2>/dev/null \
  | openssl x509 -pubkey -noout \
  | openssl pkey -pubin -outform der \
  | openssl dgst -sha256 -binary \
  | openssl enc -base64

# Intermediate CA pin (stable — recommended for pinning)
echo | openssl s_client -connect YOUR_DOMAIN:443 -servername YOUR_DOMAIN -showcerts 2>/dev/null \
  | awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/{ if(/BEGIN/) n++; if(n==2) print }' \
  | openssl x509 -pubkey -noout \
  | openssl pkey -pubin -outform der \
  | openssl dgst -sha256 -binary \
  | openssl enc -base64
```

Verify with: `openssl s_client -connect YOUR_DOMAIN:443 2>/dev/null | openssl x509 -noout -issuer -dates`

#### Implementation Pattern

```kotlin
@Provides
@Singleton
fun provideCertificatePinner(): CertificatePinner =
    CertificatePinner.Builder().apply {
        if (BuildConfig.ENABLE_CERT_PINNING) {
            // Intermediate CA (stable across cert renewals)
            add("staging.example.com", "sha256/<INTERMEDIATE_CA_PIN>")
            add("app.example.com", "sha256/<INTERMEDIATE_CA_PIN>")
            // Leaf certificate pins (change on renewal — backup only)
            add("staging.example.com", "sha256/<STAGING_LEAF_PIN>")
            add("app.example.com", "sha256/<PROD_LEAF_PIN>")
        }
    }.build()
```

#### Build Config Flags

```kotlin
// build.gradle.kts — product flavors
create("dev") {
    buildConfigField("Boolean", "ENABLE_CERT_PINNING", "false")  // No pinning for local dev
}
create("staging") {
    buildConfigField("Boolean", "ENABLE_CERT_PINNING", "true")   // Pin staging server
}
create("prod") {
    buildConfigField("Boolean", "ENABLE_CERT_PINNING", "true")   // Pin production server
}
```

#### Pinning Checklist

- [ ] Extract real pins from BOTH staging and production servers before enabling
- [ ] Pin the intermediate CA (not just the leaf) for Let's Encrypt servers
- [ ] Pin ALL server domains the app connects to (staging + production)
- [ ] Use `ENABLE_CERT_PINNING` BuildConfig flag — disabled for dev, enabled for staging/prod
- [ ] Write a test that asserts no placeholder pins remain in the codebase
- [ ] Document pin extraction date and cert expiry in code comments
```

### Network Security Config

**CRITICAL: The `<base-config>` section is MANDATORY.** Without it, staging/release builds on physical devices (especially Samsung devices with Knox security) may fail to make HTTPS connections — even though the same APK works fine on emulators. The `<base-config>` explicitly declares trust for system CA certificates. If you only have `<debug-overrides>` and `<domain-config>` without `<base-config>`, HTTPS to your staging/production servers will silently fail with "network error" on real devices.

**Symptoms of missing `<base-config>`:**
- App works on emulator (debug build uses cleartext HTTP to 10.0.2.2)
- App shows "network error" on physical devices (staging/release builds use HTTPS)
- Other apps on the same device work fine
- Particularly affects Samsung devices (A05s, S24, etc.)

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- MANDATORY: Trust system CAs for all HTTPS connections -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Debug overrides (only in debug builds) -->
    <debug-overrides>
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>

    <!-- Allow cleartext only for emulator localhost -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">localhost</domain>
    </domain-config>

    <!-- Optional: Pin specific domains -->
    <!--
    <domain-config>
        <domain includeSubdomains="true">api.company.com</domain>
        <pin-set expiration="2026-12-31">
            <pin digest="SHA-256">PRIMARY_PIN_HERE</pin>
            <pin digest="SHA-256">BACKUP_PIN_HERE</pin>
        </pin-set>
    </domain-config>
    -->
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
- Certificate pinning for API domains (extract real pins — NEVER use placeholders)
- No cleartext HTTP traffic
- Biometric auth for sensitive operations
- Token rotation and secure refresh
- ProGuard/R8 obfuscation in release
- No logging of sensitive data in release
- Input validation and sanitization
- Root/jailbreak detection (if required)
- Secure WebView configuration (if used)
