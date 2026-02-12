# Authentication & Cryptography - Detailed Guide

## Password Security

### Password Requirements

**Good Requirements:**
- Minimum 8 characters (12+ recommended)
- No maximum length (or very high, e.g., 128 chars)
- Allow all characters including special chars, spaces, unicode
- Don't require specific character types (research shows this weakens passwords)
- Check against leaked password databases (haveibeenpwned)

**Bad Requirements:**
- Requiring specific character types (upper, lower, number, special)
- Maximum length under 64 characters
- Disallowing certain special characters
- Frequent forced password changes

### Password Hashing

**Correct Algorithms:**
```php
// Argon2id (best, PHP 7.3+)
$hash = password_hash($password, PASSWORD_ARGON2ID, [
    'memory_cost' => 65536,  // 64 MB
    'time_cost' => 4,        // 4 iterations
    'threads' => 3           // 3 parallel threads
]);

// bcrypt (good alternative)
$hash = password_hash($password, PASSWORD_BCRYPT, [
    'cost' => 12  // Work factor
]);

// Verification
if (password_verify($password, $hash)) {
    // Login successful

    // Check if hash needs rehashing (parameters changed)
    if (password_needs_rehash($hash, PASSWORD_ARGON2ID)) {
        $newHash = password_hash($password, PASSWORD_ARGON2ID);
        // Update database with new hash
    }
}
```

**Never Use:**
- MD5
- SHA-1
- Plain SHA-256 without salt and iterations
- Custom encryption schemes

### Rate Limiting on Authentication

**Per Username:**
```php
// 5 failed attempts locks for 15 minutes
$attempts = Cache::get("login_attempts:$username", 0);

if ($attempts >= 5) {
    $lockoutTime = Cache::get("login_lockout:$username");
    if ($lockoutTime && time() < $lockoutTime) {
        throw new AuthException('Account temporarily locked. Try again in ' .
            ceil(($lockoutTime - time()) / 60) . ' minutes.');
    }
}

// Increment attempts on failure
if (!$authenticated) {
    $attempts++;
    Cache::put("login_attempts:$username", $attempts, 900); // 15 min

    if ($attempts >= 5) {
        Cache::put("login_lockout:$username", time() + 900, 900);
    }
}

// Clear attempts on success
if ($authenticated) {
    Cache::forget("login_attempts:$username");
    Cache::forget("login_lockout:$username");
}
```

**Per IP Address:**
```php
// 20 login requests per minute per IP
$ip = request()->ip();
$requests = Cache::get("login_rate_limit:$ip", 0);

if ($requests >= 20) {
    throw new AuthException('Too many login attempts. Try again later.');
}

Cache::increment("login_rate_limit:$ip", 1);
Cache::put("login_rate_limit:$ip", $requests + 1, 60); // 1 min
```

**CAPTCHA After Failed Attempts:**
```php
$attempts = Cache::get("login_attempts:$username", 0);

if ($attempts >= 3) {
    // Require CAPTCHA
    if (!$request->captcha_verified) {
        throw new AuthException('Please complete the CAPTCHA');
    }
}
```

### Multi-Factor Authentication (MFA)

**TOTP (Time-based One-Time Password):**
```php
use OTPHP\TOTP;

// Setup
$totp = TOTP::create();
$totp->setLabel($user->email);
$totp->setIssuer('MyApp');

// Save secret to database
$user->update(['mfa_secret' => $totp->getSecret()]);

// Generate QR code for user to scan
$qrCode = $totp->getQrCodeUri();

// Verification
$totp = TOTP::create($user->mfa_secret);
if (!$totp->verify($request->code, null, 1)) { // 1 = 30s window
    throw new AuthException('Invalid verification code');
}
```

**Backup Codes:**
```php
// Generate backup codes
function generateBackupCodes($count = 10) {
    $codes = [];
    for ($i = 0; $i < $count; $i++) {
        $codes[] = strtoupper(substr(bin2hex(random_bytes(4)), 0, 8));
    }
    return $codes;
}

// Hash and store
$backupCodes = generateBackupCodes();
$hashedCodes = array_map(fn($code) => hash('sha256', $code), $backupCodes);
$user->update(['backup_codes' => json_encode($hashedCodes)]);

// Verification
$hashedInput = hash('sha256', $request->backup_code);
$backupCodes = json_decode($user->backup_codes, true);

if (in_array($hashedInput, $backupCodes)) {
    // Remove used code
    $backupCodes = array_diff($backupCodes, [$hashedInput]);
    $user->update(['backup_codes' => json_encode(array_values($backupCodes))]);
    // Allow login
}
```

### Session Management

**Secure Session Configuration:**
```php
// php.ini or session config
session.cookie_httponly = 1    // Prevent JavaScript access
session.cookie_secure = 1      // HTTPS only
session.cookie_samesite = Strict  // CSRF protection
session.use_strict_mode = 1    // Reject uninitialized session IDs
session.use_only_cookies = 1   // Don't accept session IDs from URL
session.sid_length = 48        // Long session ID
session.gc_maxlifetime = 7200  // 2 hour lifetime

// In code
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1);
ini_set('session.cookie_samesite', 'Strict');
```

**Session Regeneration:**
```php
// After login - prevent session fixation
session_regenerate_id(true);

// After privilege escalation
if ($user->elevateToAdmin()) {
    session_regenerate_id(true);
}

// After password change
if ($user->updatePassword($newPassword)) {
    session_regenerate_id(true);
}
```

**Session Invalidation:**
```php
// Logout
session_destroy();
setcookie(session_name(), '', time() - 3600, '/');

// Logout all other sessions
// Store session ID in database
$user->sessions()->where('id', '!=', session_id())->delete();
```

### JWT (JSON Web Tokens)

**Secure JWT Implementation:**
```php
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

// Generate token
$payload = [
    'iss' => 'https://myapp.com',        // Issuer
    'sub' => $user->id,                  // Subject (user ID)
    'iat' => time(),                     // Issued at
    'exp' => time() + 3600,              // Expiration (1 hour)
    'jti' => bin2hex(random_bytes(16)),  // JWT ID (prevent replay)
];

$token = JWT::encode($payload, env('JWT_SECRET'), 'HS256');

// Verify token
try {
    $decoded = JWT::decode($token, new Key(env('JWT_SECRET'), 'HS256'));

    // Additional checks
    if ($decoded->exp < time()) {
        throw new Exception('Token expired');
    }

    // Check if token is revoked (store jti in cache/db when revoking)
    if (Cache::has("revoked_token:{$decoded->jti}")) {
        throw new Exception('Token revoked');
    }

} catch (Exception $e) {
    throw new AuthException('Invalid token');
}
```

**JWT Best Practices:**
- Use HS256 or RS256 algorithm
- Never store sensitive data in payload (it's visible)
- Set short expiration times (15 min - 1 hour)
- Implement refresh tokens for long-lived sessions
- Store JTI in revocation list when logging out
- Include claims: iss, sub, iat, exp, jti

### Password Reset

**Secure Password Reset Flow:**
```php
// Step 1: Generate reset token
$token = bin2hex(random_bytes(32));
$hashedToken = hash('sha256', $token);

DB::table('password_resets')->insert([
    'email' => $user->email,
    'token' => $hashedToken,
    'created_at' => now(),
]);

// Send email with token (not hashed)
Mail::to($user)->send(new PasswordResetEmail($token));

// Step 2: Verify token
$hashedToken = hash('sha256', $request->token);
$reset = DB::table('password_resets')
    ->where('token', $hashedToken)
    ->where('created_at', '>', now()->subHours(1)) // 1 hour expiry
    ->first();

if (!$reset) {
    throw new AuthException('Invalid or expired reset token');
}

// Step 3: Update password
$user = User::where('email', $reset->email)->first();
$user->update(['password' => bcrypt($request->password)]);

// Step 4: Clean up
DB::table('password_resets')->where('email', $user->email)->delete();

// Step 5: Invalidate all sessions
$user->sessions()->delete();

// Step 6: Send notification
Mail::to($user)->send(new PasswordChangedEmail());
```

**Password Reset Checklist:**
- [ ] Token is cryptographically random (not predictable)
- [ ] Token is hashed before storing in database
- [ ] Token expires after 1 hour
- [ ] Only one valid token per user (delete old tokens)
- [ ] Invalidate token after use
- [ ] Rate limit reset requests
- [ ] Don't reveal whether email exists (same message for all)
- [ ] Invalidate all sessions after password change
- [ ] Send notification email after password change

### OAuth 2.0

**Secure OAuth Implementation:**
```php
// Redirect to OAuth provider
$state = bin2hex(random_bytes(16));
session(['oauth_state' => $state]);

$params = [
    'client_id' => env('OAUTH_CLIENT_ID'),
    'redirect_uri' => url('/oauth/callback'),
    'response_type' => 'code',
    'scope' => 'user:email',
    'state' => $state,
];

return redirect('https://provider.com/oauth/authorize?' . http_build_query($params));

// Handle callback
if ($request->state !== session('oauth_state')) {
    throw new AuthException('Invalid state parameter');
}

// Exchange code for token
$response = Http::post('https://provider.com/oauth/token', [
    'client_id' => env('OAUTH_CLIENT_ID'),
    'client_secret' => env('OAUTH_CLIENT_SECRET'),
    'code' => $request->code,
    'redirect_uri' => url('/oauth/callback'),
    'grant_type' => 'authorization_code',
]);

$accessToken = $response->json()['access_token'];

// Fetch user data
$user = Http::withToken($accessToken)
    ->get('https://provider.com/api/user')
    ->json();
```

**OAuth Security Checklist:**
- [ ] Verify state parameter to prevent CSRF
- [ ] Use HTTPS for redirect URI
- [ ] Validate redirect URI server-side
- [ ] Don't expose client secret in frontend
- [ ] Store tokens securely (encrypted if in database)
- [ ] Implement token refresh
- [ ] Use PKCE for mobile/SPA applications

---

## Cryptographic Failures

### Encryption

**Symmetric Encryption (AES-256-GCM):**
```php
// Encrypt
function encrypt($data, $key) {
    $iv = random_bytes(16);
    $tag = '';

    $ciphertext = openssl_encrypt(
        $data,
        'aes-256-gcm',
        $key,
        OPENSSL_RAW_DATA,
        $iv,
        $tag
    );

    // Return IV + tag + ciphertext
    return base64_encode($iv . $tag . $ciphertext);
}

// Decrypt
function decrypt($encrypted, $key) {
    $data = base64_decode($encrypted);
    $iv = substr($data, 0, 16);
    $tag = substr($data, 16, 16);
    $ciphertext = substr($data, 32);

    $plaintext = openssl_decrypt(
        $ciphertext,
        'aes-256-gcm',
        $key,
        OPENSSL_RAW_DATA,
        $iv,
        $tag
    );

    if ($plaintext === false) {
        throw new Exception('Decryption failed');
    }

    return $plaintext;
}
```

**Key Management:**
```php
// Generate secure key
$key = random_bytes(32); // 256 bits

// Store in environment variable
// .env
ENCRYPTION_KEY=base64:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

// Access in code
$key = base64_decode(substr(env('ENCRYPTION_KEY'), 7));

// Rotate keys periodically
// Keep old keys for decrypting existing data
```

### Hashing

**Secure Hashing:**
```php
// For passwords - use password_hash()

// For data integrity
$hash = hash('sha256', $data);

// With HMAC (keyed hash)
$hmac = hash_hmac('sha256', $data, $key);

// Verify HMAC
if (!hash_equals($hmac, $providedHmac)) {
    throw new Exception('Invalid signature');
}
```

**Timing-Safe Comparison:**
```php
// WRONG - vulnerable to timing attacks
if ($hash === $providedHash) { }

// CORRECT - constant-time comparison
if (hash_equals($hash, $providedHash)) { }
```

### Random Number Generation

**Cryptographically Secure:**
```php
// PHP
$random = random_bytes(32);
$randomInt = random_int(1, 100);

// JavaScript (browser)
const random = crypto.getRandomValues(new Uint8Array(32));

// Node.js
const crypto = require('crypto');
const random = crypto.randomBytes(32);
```

**Never Use:**
```php
// INSECURE
rand()
mt_rand()
uniqid()
Math.random() // JavaScript
```

### SSL/TLS

**Enforce HTTPS:**
```php
// Redirect HTTP to HTTPS
if (!request()->secure()) {
    return redirect()->secure(request()->getRequestUri());
}

// Or in Apache
<VirtualHost *:80>
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
</VirtualHost>

// Or in Nginx
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

**HSTS Header:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Certificate Validation:**
```php
// Verify SSL certificates in HTTP requests
$response = Http::withOptions([
    'verify' => true,  // Verify SSL certificate
])->get('https://api.example.com');

// Never disable verification in production
// WRONG:
'verify' => false  // Vulnerable to MITM attacks
```

---

## Summary

Authentication and cryptography require careful implementation:
1. **Hash passwords** with Argon2id or bcrypt
2. **Implement rate limiting** on login endpoints
3. **Regenerate sessions** after login and privilege changes
4. **Use secure random** for tokens and keys
5. **Enforce HTTPS** everywhere
6. **Implement MFA** for sensitive accounts
7. **Secure JWT tokens** with short expiration and revocation
8. **Encrypt sensitive data** with AES-256-GCM
9. **Use timing-safe comparisons** for hashes
10. **Validate SSL certificates** in API requests
