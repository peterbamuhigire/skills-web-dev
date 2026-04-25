# Implementation Patterns - Mobile RBAC

## Complete Code Templates

### 1. PermissionManager (Full Implementation)

```kotlin
package com.example.app.data.local.prefs

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PermissionManager @Inject constructor(
    @ApplicationContext context: Context
) {
    private val prefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "app_permissions",
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    private val _permissionsFlow = MutableStateFlow(getPermissions())
    val permissionsFlow: StateFlow<Set<String>> = _permissionsFlow.asStateFlow()

    private val _modulesFlow = MutableStateFlow(getModules())
    val modulesFlow: StateFlow<Set<String>> = _modulesFlow.asStateFlow()

    // ═══ Storage ═══

    fun savePermissions(permissions: Set<String>) {
        prefs.edit().putStringSet(KEY_PERMISSIONS, permissions).apply()
        _permissionsFlow.value = permissions
    }

    fun saveModules(modules: Set<String>) {
        prefs.edit().putStringSet(KEY_MODULES, modules).apply()
        _modulesFlow.value = modules
    }

    fun saveRoles(roles: Set<String>) {
        prefs.edit().putStringSet(KEY_ROLES, roles).apply()
    }

    fun saveUserType(userType: String) {
        prefs.edit().putString(KEY_USER_TYPE, userType).apply()
    }

    fun saveLastRefreshed(timestamp: Long) {
        prefs.edit().putLong(KEY_LAST_REFRESHED, timestamp).apply()
    }

    // ═══ Retrieval ═══

    fun getPermissions(): Set<String> =
        prefs.getStringSet(KEY_PERMISSIONS, emptySet()) ?: emptySet()

    fun getModules(): Set<String> =
        prefs.getStringSet(KEY_MODULES, emptySet()) ?: emptySet()

    fun getRoles(): Set<String> =
        prefs.getStringSet(KEY_ROLES, emptySet()) ?: emptySet()

    fun getUserType(): String =
        prefs.getString(KEY_USER_TYPE, "") ?: ""

    fun getLastRefreshed(): Long =
        prefs.getLong(KEY_LAST_REFRESHED, 0L)

    // ═══ Permission Checks ═══

    fun hasPermission(code: String): Boolean {
        val userType = getUserType()
        if (userType == "super_admin" || userType == "owner") return true
        return code in getPermissions()
    }

    fun hasAnyPermission(codes: Collection<String>): Boolean {
        val userType = getUserType()
        if (userType == "super_admin" || userType == "owner") return true
        val perms = getPermissions()
        return codes.any { it in perms }
    }

    fun hasAllPermissions(codes: Collection<String>): Boolean {
        val userType = getUserType()
        if (userType == "super_admin" || userType == "owner") return true
        val perms = getPermissions()
        return codes.all { it in perms }
    }

    fun hasModule(code: String): Boolean = code in getModules()

    fun isOwner(): Boolean = getUserType() == "owner"

    fun isSuperAdmin(): Boolean = getUserType() == "super_admin"

    fun isStale(): Boolean {
        val elapsed = System.currentTimeMillis() - getLastRefreshed()
        return elapsed > STALE_THRESHOLD_MS
    }

    // ═══ Lifecycle ═══

    fun clear() {
        prefs.edit().clear().apply()
        _permissionsFlow.value = emptySet()
        _modulesFlow.value = emptySet()
    }

    companion object {
        private const val KEY_PERMISSIONS = "user_permissions"
        private const val KEY_MODULES = "user_modules"
        private const val KEY_ROLES = "user_roles"
        private const val KEY_USER_TYPE = "user_type"
        private const val KEY_LAST_REFRESHED = "permissions_updated"
        const val STALE_THRESHOLD_MS = 15 * 60 * 1000L // 15 minutes
    }
}
```

### 2. PermissionGate Composable

```kotlin
package com.example.app.presentation.common.components

import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import com.example.app.data.local.prefs.PermissionManager

@Composable
fun PermissionGate(
    permissionManager: PermissionManager,
    permission: String,
    hide: Boolean = true,
    modifier: Modifier = Modifier,
    deniedContent: @Composable (() -> Unit)? = null,
    content: @Composable () -> Unit
) {
    // Collect to trigger recomposition when permissions change
    val permissions by permissionManager.permissionsFlow.collectAsState()
    val hasPermission = permissionManager.hasPermission(permission)

    if (hasPermission) {
        Box(modifier = modifier) { content() }
    } else if (!hide && deniedContent != null) {
        Box(modifier = modifier) { deniedContent() }
    }
}

@Composable
fun PermissionGateAny(
    permissionManager: PermissionManager,
    permissions: List<String>,
    hide: Boolean = true,
    modifier: Modifier = Modifier,
    deniedContent: @Composable (() -> Unit)? = null,
    content: @Composable () -> Unit
) {
    val perms by permissionManager.permissionsFlow.collectAsState()
    val hasAny = permissionManager.hasAnyPermission(permissions)

    if (hasAny) {
        Box(modifier = modifier) { content() }
    } else if (!hide && deniedContent != null) {
        Box(modifier = modifier) { deniedContent() }
    }
}

@Composable
fun ModuleGate(
    permissionManager: PermissionManager,
    module: String,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    val modules by permissionManager.modulesFlow.collectAsState()
    if (module in modules) {
        Box(modifier = modifier) { content() }
    }
}
```

### 3. PermissionButton Composable

```kotlin
package com.example.app.presentation.common.components

import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.annotation.DrawableRes
import androidx.compose.ui.unit.dp
import com.example.app.data.local.prefs.PermissionManager

@Composable
fun PermissionButton(
    permissionManager: PermissionManager,
    permission: String,
    onClick: () -> Unit,
    text: String,
    modifier: Modifier = Modifier,
    @DrawableRes iconRes: Int? = null,
    deniedMessage: String = "Restricted",
    colors: ButtonColors = ButtonDefaults.buttonColors()
) {
    val hasPermission = permissionManager.hasPermission(permission)

    Button(
        onClick = if (hasPermission) onClick else { {} },
        enabled = hasPermission,
        modifier = modifier,
        colors = if (!hasPermission) {
            ButtonDefaults.buttonColors(
                disabledContainerColor = MaterialTheme.colorScheme.surfaceVariant,
                disabledContentColor = MaterialTheme.colorScheme.onSurfaceVariant
            )
        } else colors
    ) {
        if (iconRes != null) {
            Icon(painterResource(iconRes), contentDescription = null, modifier = Modifier.size(18.dp))
            Spacer(Modifier.width(8.dp))
        }
        Text(if (hasPermission) text else deniedMessage)
    }
}
```

### 4. PermissionDeniedScreen

```kotlin
package com.example.app.presentation.common.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.res.painterResource

@Composable
fun PermissionDeniedScreen(
    permission: String,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            painterResource(R.drawable.lock),
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.height(16.dp))
        Text(
            "Access Restricted",
            style = MaterialTheme.typography.headlineSmall
        )
        Spacer(Modifier.height(8.dp))
        Text(
            "You need the \"$permission\" permission to access this page. " +
                "Contact your administrator.",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.height(24.dp))
        OutlinedButton(onClick = onBack) {
            Text("Go Back")
        }
    }
}
```

### 5. Permission Repository

```kotlin
package com.example.app.data.repository

import com.example.app.data.local.prefs.PermissionManager
import com.example.app.data.remote.api.UserApiService
import com.example.app.domain.repository.PermissionRepository
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PermissionRepositoryImpl @Inject constructor(
    private val api: UserApiService,
    private val permissionManager: PermissionManager
) : PermissionRepository {

    override suspend fun refreshPermissions(): Result<Unit> {
        return try {
            val response = api.getPermissions()
            if (response.isSuccessful) {
                val data = response.body()?.data
                    ?: return Result.failure(Exception("Empty permissions response"))

                permissionManager.savePermissions(data.permissions.toSet())
                permissionManager.saveModules(
                    data.modules.filter { it.isEnabled }.map { it.code }.toSet()
                )
                permissionManager.saveRoles(data.roles.map { it.code }.toSet())
                permissionManager.saveUserType(data.userType)
                permissionManager.saveLastRefreshed(System.currentTimeMillis())
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun hasPermission(code: String): Boolean =
        permissionManager.hasPermission(code)

    override fun hasModule(code: String): Boolean =
        permissionManager.hasModule(code)

    override fun isStale(): Boolean =
        permissionManager.isStale()

    override fun clearPermissions() =
        permissionManager.clear()
}
```

### 6. Permission Constants Object

```kotlin
package com.example.app.domain.model

object Permission {
    // Group constants by module for readability
    // Dashboard
    const val DASHBOARD_VIEW = "DASHBOARD_VIEW"

    // POS
    const val POS_VIEW_PRODUCTS = "POS_VIEW_PRODUCTS"
    const val POS_CREATE_SALE = "POS_CREATE_SALE"
    const val POS_CREDIT_SALE = "POS_CREDIT_SALE"
    const val POS_VIEW_RECEIPTS = "POS_VIEW_RECEIPTS"

    // Inventory
    const val INVENTORY_VIEW = "INVENTORY_VIEW"
    const val INVENTORY_PO_VIEW = "INVENTORY_PO_VIEW"
    const val INVENTORY_PO_CREATE = "INVENTORY_PO_CREATE"
    const val INVENTORY_PO_APPROVE = "INVENTORY_PO_APPROVE"
    const val INVENTORY_PO_RECEIVE = "INVENTORY_PO_RECEIVE"
    // ... etc
}

object Module {
    const val POS = "POS"
    const val INVENTORY = "INVENTORY"
    const val CUSTOMERS = "CUSTOMERS"
    // ... etc
}
```

### 7. Module-Gated Bottom Navigation

```kotlin
// In MainScaffold.kt
@Composable
fun MainScaffold(
    permissionManager: PermissionManager,
    // ... other params
) {
    val modules by permissionManager.modulesFlow.collectAsState()

    val items = remember(modules) {
        buildList {
            add(BottomNavItem.Dashboard) // Always visible
            if (Module.POS in modules) add(BottomNavItem.POS)
            if (Module.INVENTORY in modules) add(BottomNavItem.Inventory)
            if (Module.CUSTOMERS in modules) add(BottomNavItem.Customers)
            add(BottomNavItem.Settings) // Always visible
        }
    }

    Scaffold(
        bottomBar = {
            NavigationBar {
                items.forEach { item ->
                    NavigationBarItem(
                        selected = currentRoute == item.route,
                        onClick = { navigate(item.route) },
                        icon = { Icon(item.icon, item.label) },
                        label = { Text(item.label) }
                    )
                }
            }
        }
    ) { padding ->
        // NavHost with padding
    }
}
```

### 8. Login Integration

```kotlin
// In LoginViewModel
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val loginUseCase: LoginUseCase,
    private val refreshPermissionsUseCase: RefreshPermissionsUseCase
) : ViewModel() {

    fun login(username: String, password: String) {
        viewModelScope.launch {
            _uiState.value = LoginUiState.Loading
            val result = loginUseCase(username, password)
            if (result.isSuccess) {
                // Fetch permissions immediately after login
                refreshPermissionsUseCase()
                _uiState.value = LoginUiState.Success
            } else {
                _uiState.value = LoginUiState.Error(result.exceptionOrNull()?.message ?: "Login failed")
            }
        }
    }
}
```

### 9. Logout Integration

```kotlin
// In AuthRepositoryImpl or LogoutUseCase
class LogoutUseCase @Inject constructor(
    private val authRepository: AuthRepository,
    private val permissionManager: PermissionManager
) {
    suspend operator fun invoke() {
        authRepository.logout()
        permissionManager.clear() // Clear all cached permissions
    }
}
```

### 10. 403 Response Handler

```kotlin
// In OkHttp Interceptor or Repository
class PermissionDeniedInterceptor @Inject constructor(
    private val permissionManager: PermissionManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val response = chain.proceed(chain.request())
        if (response.code == 403) {
            // Trigger background permission refresh
            // The UI will re-evaluate via StateFlow observation
            runBlocking {
                try {
                    // This will update permissionsFlow, triggering UI recomposition
                    permissionRepository.refreshPermissions()
                } catch (_: Exception) { }
            }
        }
        return response
    }
}
```

## Testing Patterns

### Unit Test: PermissionManager

```kotlin
@Test
fun `hasPermission returns true for owner`() {
    permissionManager.saveUserType("owner")
    permissionManager.savePermissions(emptySet()) // No explicit permissions
    assertTrue(permissionManager.hasPermission("ANY_PERMISSION"))
}

@Test
fun `hasPermission returns false when not in set`() {
    permissionManager.saveUserType("staff")
    permissionManager.savePermissions(setOf("DASHBOARD_VIEW"))
    assertFalse(permissionManager.hasPermission("POS_CREATE_SALE"))
}
```

### Compose Test: PermissionGate

```kotlin
@Test
fun `PermissionGate hides content when permission denied`() {
    permissionManager.saveUserType("staff")
    permissionManager.savePermissions(emptySet())

    composeTestRule.setContent {
        PermissionGate(permissionManager, "POS_CREATE_SALE") {
            Text("Charge", modifier = Modifier.testTag("charge_button"))
        }
    }

    composeTestRule.onNodeWithTag("charge_button").assertDoesNotExist()
}
```
