# OWASP Top 10 2025 - Vulnerability Mapping

## Overview

This document maps common web application vulnerabilities to the OWASP Top 10 2025 categories, helping developers understand which security controls to apply for each vulnerability type.

**OWASP Top 10 2025:**
- A01:2025 - Broken Access Control
- A02:2025 - Security Misconfiguration
- A03:2025 - Software Supply Chain Failures
- A04:2025 - Cryptographic Failures
- A05:2025 - Injection
- A06:2025 - Insecure Design
- A07:2025 - Authentication Failures
- A08:2025 - Software or Data Integrity Failures
- A09:2025 - Security Logging and Alerting Failures
- A10:2025 - Mishandling of Exceptional Conditions

---

## A01:2025 - Broken Access Control

### What It Covers

Failures that allow users to act outside their intended permissions, accessing or modifying data they shouldn't.

### Common Vulnerabilities

**1. Insecure Direct Object Reference (IDOR)**
```
User accessing other users' data by manipulating IDs:
GET /api/users/124/profile (accessing another user's profile)
```

**2. Missing Authorization Checks**
```
API endpoints that check authentication but not authorization:
- User is logged in ✓
- User owns the resource? ✗
```

**3. Privilege Escalation**
- Horizontal: User A accessing User B's resources
- Vertical: Regular user accessing admin functionality

**4. Multi-Tenant Data Leakage**
```
Queries not scoped to current organization:
SELECT * FROM invoices WHERE id = ?
// Missing: AND org_id = ?
```

### Prevention

- ✅ Verify resource ownership on EVERY data access
- ✅ Use UUIDs instead of sequential IDs
- ✅ Implement role-based access control (RBAC)
- ✅ Scope all queries to current user/org
- ✅ Return 404 (not 403) for unauthorized access
- ✅ Test authorization with different user roles

### Related References

- `access-control.md` - Complete authorization patterns
- `server-side-security.md` - Server-side checks

---

## A02:2025 - Security Misconfiguration

### What It Covers

Insecure default configurations, incomplete setups, open cloud storage, misconfigured HTTP headers, and verbose error messages.

### Common Vulnerabilities

**1. Missing Security Headers**
```
Missing:
- Strict-Transport-Security
- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
```

**2. Exposed Sensitive Information**
- Debug mode enabled in production
- Stack traces visible to users
- Directory listing enabled
- .env files accessible
- Source maps exposed

**3. Default Credentials**
- Admin/admin still active
- Default database passwords
- Unchanged API keys

**4. Unnecessary Features Enabled**
- WebDAV enabled
- Directory browsing allowed
- Unused HTTP methods (TRACE, OPTIONS)

### Prevention

- ✅ Disable debug mode in production
- ✅ Set all security headers
- ✅ Remove default accounts
- ✅ Disable directory listing
- ✅ Hide server version information
- ✅ Configure CSP policy
- ✅ Regular security audits

### Related References

- `client-side-security.md` - Security headers
- SKILL.md - Security headers checklist

---

## A03:2025 - Software Supply Chain Failures

### What It Covers

Vulnerabilities in dependencies, compromised packages, and untrusted code execution.

### Common Vulnerabilities

**1. Vulnerable Dependencies**
- Outdated npm/composer packages
- Known CVEs in libraries
- Unmaintained dependencies

**2. Dependency Confusion**
- Attacker publishes malicious package with same name
- Build system pulls from wrong registry

**3. Compromised Packages**
- Malicious code in dependencies
- Supply chain attacks (e.g., event-stream, ua-parser-js)

**4. No Integrity Checks**
- No lock files (package-lock.json, composer.lock)
- No subresource integrity for CDN resources

### Prevention

- ✅ Use lock files (package-lock.json, composer.lock)
- ✅ Run `npm audit` / `composer audit` regularly
- ✅ Use Dependabot or Renovate for updates
- ✅ Verify package signatures
- ✅ Use private registries for internal packages
- ✅ Implement subresource integrity (SRI) for CDN
- ✅ Regular dependency updates
- ✅ Review dependency changes in PRs

### Tools

```bash
# PHP
composer audit

# Node.js
npm audit
npm audit fix

# Check for outdated packages
npm outdated
```

---

## A04:2025 - Cryptographic Failures

### What It Covers

Failures related to cryptography that lead to exposure of sensitive data.

### Common Vulnerabilities

**1. Plain Text Password Storage**
```php
// WRONG
CREATE TABLE users (password VARCHAR(255));
INSERT INTO users VALUES ('password123');

// CORRECT
$hash = password_hash($password, PASSWORD_ARGON2ID);
```

**2. Weak Hashing Algorithms**
- MD5, SHA-1 for passwords
- No salt
- Insufficient iteration count

**3. Insecure Communication**
- HTTP instead of HTTPS
- Missing HSTS header
- Self-signed certificates without validation

**4. Exposed Secrets**
- API keys in frontend code
- Credentials in git history
- Unencrypted sensitive data in database

**5. Weak Encryption**
- ECB mode (no IV)
- Weak keys
- Hardcoded encryption keys

### Prevention

- ✅ Use Argon2id or bcrypt for passwords
- ✅ Enforce HTTPS everywhere
- ✅ Enable HSTS
- ✅ Encrypt sensitive data at rest (AES-256-GCM)
- ✅ Use secure random number generators
- ✅ Store secrets in environment variables
- ✅ Rotate keys periodically
- ✅ Timing-safe comparisons for hashes

### Related References

- `authentication-security.md` - Password hashing, encryption
- SKILL.md - Cryptographic best practices

---

## A05:2025 - Injection

### What It Covers

Untrusted data sent to an interpreter as part of a command or query.

### Common Vulnerabilities

**1. SQL Injection**
```php
// WRONG
$query = "SELECT * FROM users WHERE id = " . $_GET['id'];

// CORRECT
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$_GET['id']]);
```

**2. Cross-Site Scripting (XSS)**
```php
// WRONG
echo "<h1>Welcome " . $_GET['name'] . "</h1>";

// CORRECT
echo "<h1>Welcome " . htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8') . "</h1>";
```

**3. Command Injection**
```php
// WRONG
system("ping -c 4 " . $_GET['host']);

// CORRECT
$host = escapeshellarg($_GET['host']);
exec("ping -c 4 $host");
```

**4. LDAP Injection**
**5. XML Injection (XXE)**
**6. Template Injection**

### Prevention

- ✅ Use parameterized queries
- ✅ Output encoding (context-specific)
- ✅ Input validation
- ✅ ORM for database access
- ✅ Disable external entities in XML parsers
- ✅ Content Security Policy (CSP)

### Related References

- `server-side-security.md` - SQL injection, XXE, command injection
- `client-side-security.md` - XSS prevention

---

## A06:2025 - Insecure Design

### What It Covers

Missing or ineffective control design, business logic flaws.

### Common Vulnerabilities

**1. No Rate Limiting**
- Brute force attacks on login
- Account enumeration
- API abuse

**2. Missing Authorization Logic**
- Features built without considering access control
- No ownership checks in design

**3. Business Logic Flaws**
- Negative quantity orders
- Race conditions in payment processing
- Price manipulation

**4. No Security Requirements**
- Security not considered in design phase
- No threat modeling

### Prevention

- ✅ Threat modeling before development
- ✅ Security requirements in user stories
- ✅ Rate limiting on sensitive endpoints
- ✅ Input validation for business rules
- ✅ Test business logic thoroughly
- ✅ Principle of least privilege
- ✅ Defense in depth

### Example: Secure Design Pattern

```
Feature: Delete User Account

Security Requirements:
- Only account owner can delete
- Require recent authentication
- Require password confirmation
- Soft delete (90-day retention)
- Notify via email
- Invalidate all sessions
- Rate limit: 1 attempt per hour
```

---

## A07:2025 - Authentication Failures

### What It Covers

Failures in confirming user identity, session management, and authentication.

### Common Vulnerabilities

**1. No Rate Limiting on Login**
```
Allows brute force attacks:
- Unlimited login attempts
- No account lockout
```

**2. Weak Passwords Allowed**
- No minimum length
- No complexity requirements
- Common passwords accepted

**3. Session Fixation**
```php
// WRONG - Don't regenerate session on login
session_start();

// CORRECT
session_start();
session_regenerate_id(true); // After login
```

**4. Credential Stuffing**
- No protection against leaked passwords
- No MFA

**5. Insecure Password Reset**
- Predictable reset tokens
- No token expiration
- Token in URL (logged)

### Prevention

- ✅ Implement rate limiting (5 attempts, 15 min lockout)
- ✅ Enforce strong passwords (min 8 chars, check haveibeenpwned)
- ✅ Regenerate session ID after login
- ✅ Implement MFA
- ✅ Secure password reset flow
- ✅ Monitor for credential stuffing
- ✅ Account lockout after failed attempts

### Related References

- `authentication-security.md` - Complete authentication patterns
- SKILL.md - Rate limiting, password security

---

## A08:2025 - Software or Data Integrity Failures

### What It Covers

Failures to protect against integrity violations of code and data.

### Common Vulnerabilities

**1. Unverified Webhook Signatures**
```php
// WRONG - Trust any POST to webhook
Route::post('/webhook/stripe', function($request) {
    $event = $request->body;
    grantAccess($event['customer']); // DANGEROUS
});

// CORRECT - Verify signature
$signature = $request->header('Stripe-Signature');
$event = \Stripe\Webhook::constructEvent(
    $request->rawBody,
    $signature,
    env('STRIPE_WEBHOOK_SECRET')
);
```

**2. No Code Signing**
- Unsigned releases
- No checksum verification

**3. Insecure Deserialization**
```php
// WRONG
$data = unserialize($_POST['data']);

// CORRECT
$data = json_decode($_POST['data'], true);
```

**4. No Integrity Checks**
- Auto-updates without signature verification
- No CDN resource integrity

### Prevention

- ✅ Verify webhook signatures
- ✅ Use subresource integrity (SRI) for CDN
- ✅ Sign code releases
- ✅ Use JSON instead of native serialization
- ✅ Verify update integrity

### Example: SRI for CDN

```html
<script
  src="https://cdn.example.com/script.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/ux..."
  crossorigin="anonymous">
</script>
```

---

## A09:2025 - Security Logging and Alerting Failures

### What It Covers

Insufficient logging, monitoring, and alerting of security events.

### Common Vulnerabilities

**1. No Logging**
- No login attempt logs
- No access logs for sensitive data
- No audit trail

**2. Insufficient Log Data**
```php
// WRONG
Log::info('Login failed');

// CORRECT
Log::warning('Login failed', [
    'username' => $username,
    'ip' => request()->ip(),
    'user_agent' => request()->userAgent(),
    'timestamp' => now(),
]);
```

**3. Logs Not Monitored**
- Logs collected but never reviewed
- No alerts for suspicious activity

**4. Logs Contain Sensitive Data**
```php
// WRONG
Log::info('User logged in', ['password' => $password]);

// CORRECT
Log::info('User logged in', ['user_id' => $user->id]);
```

### Prevention

- ✅ Log all authentication events
- ✅ Log authorization failures
- ✅ Log data access (sensitive records)
- ✅ Set up alerts for suspicious activity
- ✅ Don't log sensitive data (passwords, credit cards)
- ✅ Centralized logging (ELK, Splunk)
- ✅ Log retention policy

### What to Log

**Always Log:**
- Authentication success/failure
- Authorization failures
- Input validation failures
- Data modification (who, what, when)
- Privilege escalation attempts
- Application errors

**Never Log:**
- Passwords (even hashed)
- Credit card numbers
- Session tokens
- API keys

---

## A10:2025 - Mishandling of Exceptional Conditions

### What It Covers

Improper error handling that can lead to information disclosure or denial of service.

### Common Vulnerabilities

**1. Verbose Error Messages**
```php
// WRONG - Exposes database structure
catch (PDOException $e) {
    echo $e->getMessage(); // "SQLSTATE[42S02]: Table 'db.users' not found"
}

// CORRECT
catch (PDOException $e) {
    Log::error('Database error', ['error' => $e->getMessage()]);
    throw new HttpException(500, 'An error occurred. Please try again.');
}
```

**2. Stack Traces in Production**
```php
// WRONG - Debug mode in production
APP_DEBUG=true

// CORRECT
APP_DEBUG=false
```

**3. No Error Handling**
```php
// WRONG - Unhandled exception crashes app
$user = User::findOrFail($id); // Throws exception if not found

// CORRECT
try {
    $user = User::findOrFail($id);
} catch (ModelNotFoundException $e) {
    return response()->json(['error' => 'User not found'], 404);
}
```

**4. Information Leakage in Errors**
- Revealing file paths
- Database connection strings
- Internal IP addresses

### Prevention

- ✅ Generic error messages for users
- ✅ Detailed logs for developers (server-side only)
- ✅ Disable debug mode in production
- ✅ Custom error pages
- ✅ Catch all exceptions
- ✅ Sanitize error responses

### Error Handling Pattern

```php
try {
    // Application logic
} catch (ValidationException $e) {
    // User input error - safe to show
    return response()->json([
        'error' => 'Validation failed',
        'details' => $e->errors()
    ], 422);
} catch (AuthorizationException $e) {
    // Don't reveal why - prevents enumeration
    return response()->json([
        'error' => 'Not found'
    ], 404);
} catch (Exception $e) {
    // Unexpected error - log and show generic message
    Log::error('Unexpected error', [
        'exception' => $e->getMessage(),
        'trace' => $e->getTraceAsString()
    ]);

    return response()->json([
        'error' => 'An error occurred. Please try again.'
    ], 500);
}
```

---

## Quick Reference: Vulnerability → OWASP Category

| Vulnerability                  | OWASP Category                  |
| ------------------------------ | ------------------------------- |
| IDOR                           | A01 - Broken Access Control     |
| Missing Authorization          | A01 - Broken Access Control     |
| Missing Security Headers       | A02 - Security Misconfiguration |
| Debug Mode in Production       | A02 - Security Misconfiguration |
| Vulnerable Dependencies        | A03 - Supply Chain Failures     |
| Plain Text Passwords           | A04 - Cryptographic Failures    |
| Weak Encryption                | A04 - Cryptographic Failures    |
| SQL Injection                  | A05 - Injection                 |
| XSS                            | A05 - Injection                 |
| Command Injection              | A05 - Injection                 |
| No Rate Limiting               | A06 - Insecure Design           |
| Business Logic Flaws           | A06 - Insecure Design           |
| Weak Password Policy           | A07 - Authentication Failures   |
| Session Fixation               | A07 - Authentication Failures   |
| Unverified Webhooks            | A08 - Data Integrity Failures   |
| Insecure Deserialization       | A08 - Data Integrity Failures   |
| No Audit Logging               | A09 - Logging Failures          |
| Verbose Error Messages         | A10 - Exception Handling        |
| Stack Traces Exposed           | A10 - Exception Handling        |

---

## Summary

The OWASP Top 10 provides a framework for understanding web application security risks. Use this mapping to:
1. Identify which OWASP category a vulnerability falls under
2. Apply appropriate security controls
3. Ensure comprehensive coverage when reviewing code
4. Structure security testing and audits

**Remember:** Security is not a checklist. Understanding the underlying principles behind each OWASP category is essential for building truly secure applications.
