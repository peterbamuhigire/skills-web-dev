# Access Control Security - Detailed Guide

## Overview

Access control vulnerabilities occur when users can access resources or perform actions beyond their intended permissions. This is one of the most common and critical vulnerabilities in web applications.

## Core Requirements

For **every data point and action** that requires authentication:

1. **User-Level Authorization**
   - Each user must only access/modify their own data
   - No user should access data from other users or organizations
   - Always verify ownership at the data layer, not just the route level

2. **Use UUIDs Instead of Sequential IDs**
   - Use UUIDv4 or similar non-guessable identifiers
   - Exception: Only use sequential IDs if explicitly requested by user
   - Prevents enumeration attacks

3. **Account Lifecycle Handling**
   - When a user is removed from an organization: immediately revoke all access tokens and sessions
   - When an account is deleted/deactivated: invalidate all active sessions and API keys
   - Implement token revocation lists or short-lived tokens with refresh mechanisms

## Authorization Checks Checklist

- [ ] Verify user owns the resource on every request (don't trust client-side data)
- [ ] Check organization membership for multi-tenant apps
- [ ] Validate role permissions for role-based actions
- [ ] Re-validate permissions after any privilege change
- [ ] Check parent resource ownership (e.g., if accessing a comment, verify user owns the parent post)

## Common Pitfalls to Avoid

### IDOR (Insecure Direct Object Reference)

Always verify the requesting user has permission to access the requested resource ID.

**Example Attack:**
```
GET /api/users/123/profile  → Your profile
GET /api/users/124/profile  → Someone else's profile (VULNERABLE!)
```

**Fix:**
```php
function getResource($resourceId, $currentUser) {
    $resource = database->find($resourceId);

    if ($resource === null) {
        return 404;  // Don't reveal if resource exists
    }

    if ($resource->owner_id !== $currentUser->id) {
        if (!$currentUser->hasOrgAccess($resource->org_id)) {
            return 404;  // Return 404, not 403, to prevent enumeration
        }
    }

    return $resource;
}
```

### Horizontal Privilege Escalation

User A accessing User B's resources with the same privilege level.

**Prevention:**
- Always check resource ownership: `WHERE owner_id = ? AND id = ?`
- For multi-tenant: `WHERE org_id = ? AND id = ?`
- Never trust client-provided user IDs

### Vertical Privilege Escalation

Regular user accessing admin functionality.

**Prevention:**
- Check role on every admin endpoint
- Verify role server-side (never trust client claims)
- Use middleware/guards for role checking
- Re-check after role changes

### Mass Assignment Vulnerabilities

**Vulnerable Code:**
```php
// User can set any field, including 'is_admin'
$user->update($request->all());
```

**Secure Code:**
```php
// Explicitly whitelist allowed fields
$user->update($request->only(['name', 'email', 'bio']));

// Or use validation with specific rules
$validated = $request->validate([
    'name' => 'required|string|max:255',
    'email' => 'required|email',
    'bio' => 'nullable|string|max:500',
]);
$user->update($validated);
```

## Multi-Tenant Isolation Patterns

### Database-Level Isolation

**Every query must include tenant filter:**

```sql
-- WRONG: Global query
SELECT * FROM invoices WHERE id = ?

-- CORRECT: Tenant-scoped query
SELECT * FROM invoices WHERE org_id = ? AND id = ?
```

### Application-Level Enforcement

```php
// Base repository with automatic tenant scoping
abstract class TenantScopedRepository {
    protected function query() {
        return DB::table($this->table)
            ->where('org_id', Auth::user()->org_id);
    }
}

// Usage
class InvoiceRepository extends TenantScopedRepository {
    public function find($id) {
        return $this->query()->where('id', $id)->first();
    }

    public function all() {
        return $this->query()->get();
    }
}
```

### Middleware for Tenant Context

```php
class SetTenantContext {
    public function handle($request, $next) {
        if (Auth::check()) {
            // Set tenant context for all queries
            TenantScope::setTenant(Auth::user()->org_id);
        }

        return $next($request);
    }
}
```

## Role-Based Access Control (RBAC)

### Permission Checking Pattern

```php
class PermissionMiddleware {
    public function handle($request, $next, $permission) {
        if (!Auth::user()->hasPermission($permission)) {
            abort(403, 'Insufficient permissions');
        }

        return $next($request);
    }
}

// Route definition
Route::delete('/users/{id}', [UserController::class, 'destroy'])
    ->middleware('permission:users.delete');
```

### Hierarchical Permissions

```php
class User {
    public function hasPermission($permission) {
        // Admin has all permissions
        if ($this->role === 'admin') {
            return true;
        }

        // Check specific permission
        return $this->permissions->contains('name', $permission);
    }

    public function hasAnyPermission($permissions) {
        foreach ($permissions as $permission) {
            if ($this->hasPermission($permission)) {
                return true;
            }
        }
        return false;
    }
}
```

## API Key Security

### Key Generation

```php
// Generate secure random API key
$apiKey = bin2hex(random_bytes(32)); // 64 character hex string

// Hash before storing in database
$hashedKey = hash('sha256', $apiKey);

// Store in database
DB::table('api_keys')->insert([
    'user_id' => $userId,
    'key_hash' => $hashedKey,
    'name' => $request->name,
    'last_used' => null,
    'expires_at' => now()->addYear(),
]);

// Return to user ONCE (they must store it)
return response()->json([
    'api_key' => $apiKey,
    'message' => 'Store this key securely. You will not see it again.',
]);
```

### Key Validation

```php
// Validate API key from request
$providedKey = $request->bearerToken();
$hashedKey = hash('sha256', $providedKey);

$apiKey = DB::table('api_keys')
    ->where('key_hash', $hashedKey)
    ->where('expires_at', '>', now())
    ->first();

if (!$apiKey) {
    abort(401, 'Invalid API key');
}

// Update last used timestamp
DB::table('api_keys')
    ->where('id', $apiKey->id)
    ->update(['last_used' => now()]);
```

## Session Management

### Secure Session Configuration

```php
// config/session.php
return [
    'lifetime' => 120,              // 2 hours
    'expire_on_close' => true,      // Expire when browser closes
    'secure' => true,               // Only send over HTTPS
    'http_only' => true,            // Not accessible via JavaScript
    'same_site' => 'strict',        // CSRF protection
];
```

### Session Regeneration

```php
// After login - prevent session fixation
Auth::login($user);
session()->regenerate();

// After privilege escalation
if ($user->elevateToAdmin()) {
    session()->regenerate();
}

// After password change - invalidate all other sessions
Auth::logoutOtherDevices($currentPassword);
```

## Testing Access Control

### Manual Testing Checklist

```bash
# Test horizontal escalation (user accessing other user's data)
curl -H "Authorization: Bearer user1_token" \
     https://api.example.com/users/user2_id/profile

# Test vertical escalation (user accessing admin endpoint)
curl -H "Authorization: Bearer user_token" \
     https://api.example.com/admin/users

# Test IDOR with sequential IDs
curl -H "Authorization: Bearer token" \
     https://api.example.com/invoices/1
curl -H "Authorization: Bearer token" \
     https://api.example.com/invoices/2
curl -H "Authorization: Bearer token" \
     https://api.example.com/invoices/3

# Test multi-tenant isolation
curl -H "Authorization: Bearer org1_token" \
     https://api.example.com/api/data?org_id=org2
```

### Automated Testing

```php
// PHPUnit test for authorization
public function test_user_cannot_access_other_users_profile() {
    $user1 = User::factory()->create();
    $user2 = User::factory()->create();

    $response = $this->actingAs($user1)
        ->get("/api/users/{$user2->id}/profile");

    $response->assertStatus(404); // Not 403 (prevents enumeration)
}

public function test_multi_tenant_isolation() {
    $org1 = Organization::factory()->create();
    $org2 = Organization::factory()->create();

    $user = User::factory()->create(['org_id' => $org1->id]);
    $invoice = Invoice::factory()->create(['org_id' => $org2->id]);

    $response = $this->actingAs($user)
        ->get("/api/invoices/{$invoice->id}");

    $response->assertStatus(404);
}
```

## Defense in Depth

Implement multiple layers of access control:

1. **Route-level middleware** - Require authentication
2. **Controller-level authorization** - Check permissions
3. **Service-level checks** - Verify ownership
4. **Database-level constraints** - Foreign keys, tenant scoping
5. **Audit logging** - Track all access attempts

**Never rely on a single layer.** If one layer fails, others should catch the breach.

## Common Framework Patterns

### Laravel

```php
// Policy-based authorization
Gate::define('update-post', function ($user, $post) {
    return $user->id === $post->user_id;
});

// In controller
public function update(Request $request, Post $post) {
    $this->authorize('update-post', $post);
    // ...
}
```

### Express.js

```javascript
// Ownership verification middleware
const verifyOwnership = (resourceLoader) => {
  return async (req, res, next) => {
    const resource = await resourceLoader(req.params.id);

    if (!resource) {
      return res.status(404).json({ error: 'Not found' });
    }

    if (resource.userId !== req.user.id) {
      return res.status(404).json({ error: 'Not found' });
    }

    req.resource = resource;
    next();
  };
};

// Usage
app.get('/posts/:id',
  authenticate,
  verifyOwnership(loadPost),
  (req, res) => {
    res.json(req.resource);
  }
);
```

## Summary

Access control is not optional—it's fundamental to application security. Every endpoint that handles user data must verify authorization. Use defense in depth, test thoroughly, and always return 404 (not 403) for unauthorized access to prevent enumeration.
