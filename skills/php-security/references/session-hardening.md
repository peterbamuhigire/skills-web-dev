# PHP Session Hardening Reference

Deep-dive reference for all PHP session-related php.ini directives and session security patterns.

**Parent skill:** php-security

## Session php.ini Directives

### Cookie Configuration

| Directive | Secure Value | Default | Purpose |
|-----------|-------------|---------|---------|
| `session.cookie_httponly` | `1` | `0` | Prevent JavaScript access to session cookie |
| `session.cookie_secure` | `1` | `0` | Only send cookie over HTTPS |
| `session.cookie_samesite` | `Strict` | `""` | Prevent CSRF via cross-origin requests |
| `session.cookie_lifetime` | `0` | `0` | Session cookie (deleted when browser closes) |
| `session.cookie_path` | `/` | `/` | Cookie scope -- restrict if app is in subdirectory |
| `session.cookie_domain` | `""` | `""` | Leave empty for current domain only |
| `session.name` | Custom name | `PHPSESSID` | Change default session name to reduce fingerprinting |

### Session ID Configuration

| Directive | Secure Value | Default | Purpose |
|-----------|-------------|---------|---------|
| `session.use_cookies` | `1` | `1` | Use cookies for session ID transport |
| `session.use_only_cookies` | `1` | `1` | NEVER accept session ID from URL |
| `session.use_trans_sid` | `0` | `0` | Disable transparent session ID in URLs |
| `session.use_strict_mode` | `1` | `0` | Reject uninitialized session IDs |
| `session.sid_length` | `48` | `32` | Session ID length (more = harder to guess) |
| `session.sid_bits_per_character` | `6` | `4` | Entropy per character (6 = a-z, A-Z, 0-9, -, ,) |

### Session Lifetime & Garbage Collection

| Directive | Secure Value | Default | Purpose |
|-----------|-------------|---------|---------|
| `session.gc_maxlifetime` | `1800` | `1440` | Max session lifetime in seconds (30 min) |
| `session.gc_probability` | `1` | `1` | GC trigger probability numerator |
| `session.gc_divisor` | `100` | `100` | GC trigger probability denominator (1% chance) |

### Session Storage

| Directive | Secure Value | Default | Purpose |
|-----------|-------------|---------|---------|
| `session.save_handler` | `files` | `files` | Session storage backend |
| `session.save_path` | `/var/lib/php/sessions` | `""` | Session file location (restrict permissions) |
| `session.serialize_handler` | `php_serialize` | `php` | Serialization format (php_serialize is safer) |

## Session Attack Vectors

### 1. Session Fixation

**Attack:** Attacker sets a known session ID before victim authenticates.

```
Attacker -> Victim: "Click this link: https://app.com/?PHPSESSID=known-id"
Victim -> Server: Authenticates with PHPSESSID=known-id
Attacker -> Server: Uses PHPSESSID=known-id (now authenticated!)
```

**Prevention:**

```php
// ALWAYS regenerate session ID after authentication
session_start();

if (authenticateUser($username, $password)) {
    // Destroy old session, create new one
    session_regenerate_id(true);

    $_SESSION['user_id'] = $user->id;
    $_SESSION['authenticated'] = true;
    $_SESSION['ip'] = $_SERVER['REMOTE_ADDR'];
    $_SESSION['user_agent'] = $_SERVER['HTTP_USER_AGENT'];
}
```

**Also regenerate on:**
- Login (authentication state change)
- Privilege escalation (admin mode)
- Role switch
- Password change
- Any security-sensitive action

### 2. Session Hijacking

**Attack:** Attacker steals an active session ID and uses it.

**Vectors:**
- XSS attack reads `document.cookie`
- Network sniffing (without HTTPS)
- Session ID in URL (leaked via Referer header)
- Shared hosting session file access

**Prevention Stack:**

```php
final class SessionSecurity
{
    public static function init(): void
    {
        // 1. Cookie-only transport (no URL leakage)
        ini_set('session.use_only_cookies', '1');
        ini_set('session.use_trans_sid', '0');

        // 2. HttpOnly prevents XSS cookie theft
        ini_set('session.cookie_httponly', '1');

        // 3. Secure flag prevents network sniffing
        $isHttps = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
                   || ($_SERVER['SERVER_PORT'] ?? 0) == 443;
        ini_set('session.cookie_secure', $isHttps ? '1' : '0');

        // 4. SameSite prevents CSRF-based session use
        ini_set('session.cookie_samesite', 'Strict');

        // 5. Strict mode rejects unknown session IDs
        ini_set('session.use_strict_mode', '1');

        session_start();

        // 6. Fingerprint binding
        self::validateFingerprint();

        // 7. Idle timeout
        self::checkIdleTimeout();
    }

    private static function validateFingerprint(): void
    {
        $fingerprint = hash('sha256',
            ($_SERVER['HTTP_USER_AGENT'] ?? '') .
            ($_SERVER['HTTP_ACCEPT_LANGUAGE'] ?? '')
        );

        if (!isset($_SESSION['_fingerprint'])) {
            $_SESSION['_fingerprint'] = $fingerprint;
            return;
        }

        if (!hash_equals($_SESSION['_fingerprint'], $fingerprint)) {
            self::destroyAndRestart();
        }
    }

    private static function checkIdleTimeout(int $maxIdle = 1800): void
    {
        if (isset($_SESSION['_last_activity'])) {
            if (time() - $_SESSION['_last_activity'] > $maxIdle) {
                self::destroyAndRestart();
                return;
            }
        }
        $_SESSION['_last_activity'] = time();
    }

    private static function destroyAndRestart(): void
    {
        $_SESSION = [];
        if (ini_get('session.use_cookies')) {
            $p = session_get_cookie_params();
            setcookie(session_name(), '', time() - 42000, $p['path'], $p['domain'], $p['secure'], $p['httponly']);
        }
        session_destroy();
        session_start();
        session_regenerate_id(true);
    }
}
```

### 3. Session Sidejacking

**Attack:** Attacker intercepts session cookie over unencrypted connection.

**Prevention:**
- Force HTTPS on all authenticated pages
- Set `session.cookie_secure = 1`
- Enable HSTS header
- Redirect all HTTP to HTTPS

### 4. Session Prediction

**Attack:** Attacker guesses session IDs by analyzing patterns.

**Prevention:**
- Use PHP 7.1+ default session ID generation (cryptographically secure)
- Increase session ID length: `session.sid_length = 48`
- Increase entropy: `session.sid_bits_per_character = 6`
- Never use custom session ID generators unless you understand CSPRNG

## Shared Hosting Considerations

On shared hosting, `/tmp` is readable by all users:

```php
// Set dedicated session directory with restricted permissions
$sessionPath = '/home/youruser/sessions';
if (!is_dir($sessionPath)) {
    mkdir($sessionPath, 0700, true);
}
ini_set('session.save_path', $sessionPath);

// Or use database session handler
ini_set('session.save_handler', 'user');
session_set_save_handler(new DatabaseSessionHandler($pdo), true);
```

### Database Session Handler

```php
final class DatabaseSessionHandler implements \SessionHandlerInterface
{
    public function __construct(private \PDO $pdo) {}

    public function open(string $path, string $name): bool { return true; }
    public function close(): bool { return true; }

    public function read(string $id): string|false
    {
        $stmt = $this->pdo->prepare(
            'SELECT data FROM sessions WHERE id = :id AND expires_at > NOW()'
        );
        $stmt->execute(['id' => $id]);
        $row = $stmt->fetch(\PDO::FETCH_ASSOC);
        return $row ? $row['data'] : '';
    }

    public function write(string $id, string $data): bool
    {
        $stmt = $this->pdo->prepare(
            'REPLACE INTO sessions (id, data, expires_at) VALUES (:id, :data, DATE_ADD(NOW(), INTERVAL 30 MINUTE))'
        );
        return $stmt->execute(['id' => $id, 'data' => $data]);
    }

    public function destroy(string $id): bool
    {
        $stmt = $this->pdo->prepare('DELETE FROM sessions WHERE id = :id');
        return $stmt->execute(['id' => $id]);
    }

    public function gc(int $max_lifetime): int|false
    {
        $stmt = $this->pdo->prepare('DELETE FROM sessions WHERE expires_at < NOW()');
        $stmt->execute();
        return $stmt->rowCount();
    }
}
```

**Required table:**

```sql
CREATE TABLE sessions (
    id VARCHAR(128) NOT NULL PRIMARY KEY,
    data TEXT NOT NULL,
    expires_at DATETIME NOT NULL,
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Session Management Patterns

### Login Flow

```php
// 1. Start session
SecureSession::start();

// 2. Validate credentials
$user = authenticateUser($username, $password);
if (!$user) {
    logFailedAttempt($username, $_SERVER['REMOTE_ADDR']);
    // Return error
}

// 3. Regenerate session ID (prevent fixation)
session_regenerate_id(true);

// 4. Store minimal session data
$_SESSION['user_id'] = $user->id;
$_SESSION['franchise_id'] = $user->franchise_id;
$_SESSION['user_type'] = $user->user_type;
$_SESSION['last_activity'] = time();
$_SESSION['fingerprint'] = hash('sha256', $_SERVER['HTTP_USER_AGENT'] ?? '');

// 5. Log successful login
logSuccessfulLogin($user->id, $_SERVER['REMOTE_ADDR']);
```

### Logout Flow

```php
// 1. Clear all session data
$_SESSION = [];

// 2. Delete session cookie
if (ini_get('session.use_cookies')) {
    $params = session_get_cookie_params();
    setcookie(
        session_name(), '', time() - 42000,
        $params['path'], $params['domain'],
        $params['secure'], $params['httponly']
    );
}

// 3. Destroy session on server
session_destroy();

// 4. Redirect to login
header('Location: /login');
exit;
```

### Idle Timeout Check (Middleware)

```php
function checkSessionValidity(): bool
{
    if (!isset($_SESSION['user_id'])) {
        return false;
    }

    // Check idle timeout (30 minutes)
    if (isset($_SESSION['last_activity']) && time() - $_SESSION['last_activity'] > 1800) {
        SecureSession::destroy();
        return false;
    }

    // Check absolute timeout (8 hours)
    if (isset($_SESSION['created_at']) && time() - $_SESSION['created_at'] > 28800) {
        SecureSession::destroy();
        return false;
    }

    // Validate fingerprint
    $fingerprint = hash('sha256', $_SERVER['HTTP_USER_AGENT'] ?? '');
    if (!hash_equals($_SESSION['fingerprint'] ?? '', $fingerprint)) {
        SecureSession::destroy();
        return false;
    }

    // Update last activity
    $_SESSION['last_activity'] = time();
    return true;
}
```

## Complete Secure php.ini Template

```ini
; === SESSION SECURITY ===

; Cookie transport only
session.use_cookies = 1
session.use_only_cookies = 1
session.use_trans_sid = 0

; Cookie security
session.cookie_httponly = 1
session.cookie_samesite = Strict
; session.cookie_secure = 1  ; Uncomment for HTTPS-only sites
session.cookie_lifetime = 0
session.name = __Host-SESSID

; Session ID strength
session.sid_length = 48
session.sid_bits_per_character = 6
session.use_strict_mode = 1

; Lifetime and GC
session.gc_maxlifetime = 1800
session.gc_probability = 1
session.gc_divisor = 100

; Storage
session.save_handler = files
session.save_path = "/var/lib/php/sessions"
session.serialize_handler = php_serialize

; Caching
session.cache_limiter = nocache
session.cache_expire = 180
```

## Quick Reference

| Threat | Primary Defense | Secondary Defense |
|--------|----------------|-------------------|
| Session Fixation | `session_regenerate_id(true)` on auth | `session.use_strict_mode = 1` |
| Session Hijacking | HttpOnly + Secure cookies | Fingerprint binding |
| Session Sidejacking | HTTPS + `cookie_secure = 1` | HSTS header |
| Session Prediction | PHP 7.1+ defaults | `sid_length = 48` |
| URL Leakage | `use_only_cookies = 1` | `use_trans_sid = 0` |
| XSS Cookie Theft | `cookie_httponly = 1` | Content-Security-Policy |
| Shared Hosting | Custom save_path | Database session handler |
| Idle Sessions | Timeout check in middleware | `gc_maxlifetime` |
