# WAHH Attack Patterns — Defender's Taxonomy

Purpose: translate the Web Application Hacker's Handbook attacker methodology into a
defender-oriented catalogue so PHP/JS/HTML developers recognise red flags in their own code.

## How WAHH organises web attacks

The core premise of WAHH is uncomfortable but liberating for defenders: the client is
completely untrusted. Every byte that arrives at the server — URL, path, query string,
header, cookie, body field, file upload, JSON key, JSON value — is attacker-controlled and
must be treated as hostile until proven otherwise. A web application is secure only to the
degree it validates each input on the server, authorises each action on the server, and
encodes each output at the point of use.

WAHH teaches attackers to work in phases: map the application, understand its technology,
identify every parameter, then systematically test each parameter against every known class
of flaw. Defenders use the same phases in reverse — map your own surface first, then verify
each parameter is guarded against the flaw classes it could enable.

## Attack surface mapping (defender's view)

Before testing individual flaws, build a complete inventory of what an attacker can reach:

- Every URL route (including admin, internal, debug, dev-only, legacy, test)
- Every HTTP method each route accepts (GET, POST, PUT, PATCH, DELETE, OPTIONS)
- Every parameter each route reads (query, body, path, header, cookie)
- Every authentication zone (public, authenticated, admin, super-admin, API, webhook)
- Every file-serving path (downloads, uploads, static, report exports)
- Every third-party integration callback (OAuth, payment, SMS, webhook receivers)
- Every client-side feature that makes requests (SPA routes, XHR calls, WebSocket, SSE)
- Every technology fingerprint the app leaks (Server header, X-Powered-By, cookie names,
  HTML comments, error signatures, JS bundle filenames)

An attacker will build this same inventory using tools like Burp Suite's spider, content
discovery wordlists, sitemap.xml, robots.txt, and JS bundle parsing. If you do not know
what endpoints your app exposes, an attacker will.

**Reduce the surface:**

- Delete endpoints no longer used (feature flags turned off = still reachable)
- Block debug routes at the web server level in production (not just in the application)
- Never ship `phpinfo()`, `/test.php`, `/info.php`, `.git/`, `.env`, `.DS_Store`, `composer.lock`
- Strip `Server`, `X-Powered-By`, `X-AspNet-Version` headers
- Remove HTML comments that reveal framework, developer names, or TODOs
- Gate dev-only features on `APP_ENV === 'production'` checks AND web server rules

## Core attack categories — the WAHH taxonomy

| Category | What it targets | Covered in |
|----------|----------------|------------|
| Input-based flaws | Any parameter that reaches backend logic | `input-validation-patterns.md` |
| Authentication flaws | Login, reset, remember-me, MFA | `auth-session-flaws.md` |
| Session management | Session IDs, cookies, timeouts | `auth-session-flaws.md` |
| Access control | Authorisation, horizontal/vertical escalation | `access-control-flaws.md` |
| Injection | SQL, OS command, LDAP, XPath, XXE, SMTP | This file |
| Application logic | Business rule bypass, race conditions | `business-logic-flaws.md` |
| Client-side | XSS, CSRF, clickjacking, DOM-based | This file + `auth-session-flaws.md` |
| Path traversal / file upload | File-system reach, RCE via uploads | This file |
| Information disclosure | Stack traces, debug endpoints, source exposure | This file |

## SQL injection — defender's guide

**How attackers probe:**

- Single quote, double quote, backslash, semicolon in every parameter
- Error-based: look for SQL fragments in error responses (`unterminated string`, `syntax
  error near`, `mysqli_fetch_array`)
- UNION-based: append `UNION SELECT NULL,NULL,NULL--` and iterate column count
- Blind boolean: `AND 1=1` vs `AND 1=2` and diff the response
- Blind time-based: `AND SLEEP(5)--`, `WAITFOR DELAY`, `pg_sleep`
- Second-order: inject on one endpoint (e.g. signup), trigger on another (profile view)

**Red flags in PHP code:**

```php
// DANGEROUS — string concatenation
$sql = "SELECT * FROM users WHERE email = '" . $_POST['email'] . "'";
$result = mysqli_query($conn, $sql);

// DANGEROUS — sprintf does not escape
$sql = sprintf("SELECT * FROM orders WHERE id = %s", $_GET['id']);

// DANGEROUS — addslashes/mysql_real_escape_string used for numeric context
$sql = "SELECT * FROM items WHERE qty > " . addslashes($_GET['qty']);

// DANGEROUS — dynamic table/column names from user input
$sql = "SELECT * FROM " . $_GET['table'];
```

**Defence — always use prepared statements with parameter binding:**

```php
// PDO with named parameters
$stmt = $pdo->prepare('SELECT id, email FROM users WHERE tenant_id = :tid AND email = :email');
$stmt->execute([':tid' => $tenantId, ':email' => $email]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

// mysqli with type-safe bind_param
$stmt = $mysqli->prepare('INSERT INTO orders (tenant_id, user_id, total) VALUES (?, ?, ?)');
$stmt->bind_param('iid', $tenantId, $userId, $total);
$stmt->execute();
```

**For dynamic identifiers (table, column, ORDER BY) — use an allow-list:**

```php
$sortableColumns = ['created_at', 'total', 'customer_name'];
$sortColumn = in_array($_GET['sort'] ?? '', $sortableColumns, true)
    ? $_GET['sort']
    : 'created_at';
$sql = "SELECT * FROM orders ORDER BY `$sortColumn` DESC";
```

**Layered defences:**

- Database user for the web app has only DML on its schema — no DDL, no `FILE`, no `SUPER`
- Separate DB users per environment and per application tier
- Disable MySQL `LOAD_FILE`, `INTO OUTFILE` via privilege, not just config
- Web Application Firewall as a second line (never the only line)
- Stored procedures are not a defence on their own — they can still be injectable

## OS command injection

**How attackers probe:** shell metacharacters in any field that reaches a shell — filename,
hostname, IP, ping target, image filter, PDF generator option. Probes include `;`, `&`, `|`,
`` ` ``, `$()`, `<(...)`, newline, `%0a`, `%26`, and bracket variants.

**Red flags in PHP:**

```php
// DANGEROUS
exec("convert " . $_FILES['img']['tmp_name'] . " output.png");
system("ping -c 4 " . $_POST['host']);
shell_exec("git log " . $_GET['branch']);
`ls /var/uploads/{$user}`;
passthru("wkhtmltopdf {$url} report.pdf");
```

**Defence — avoid the shell entirely:**

- Use language APIs (GD/Imagick for images, DOMPDF/mPDF for PDFs, `gethostbyname` for DNS)
- If you must fork a process, use `proc_open` with an array argv (no shell interpolation)
- If you must use the shell, wrap every argument in `escapeshellarg()` — but prefer argv
- Enforce an allow-list of permitted values when the input is a mode/option
- Never pass untrusted data into `eval`, `create_function`, `assert` (these are RCE vectors)

```php
// Safer — no shell, no interpolation
$descriptors = [0 => ['pipe','r'], 1 => ['pipe','w'], 2 => ['pipe','w']];
$proc = proc_open(['convert', $srcPath, '-resize', '800x', $dstPath], $descriptors, $pipes);
```

## XXE — XML External Entities

**How attackers probe:** any endpoint that parses XML (SOAP, SAML, Office documents, SVG,
RSS, XML APIs) can be fed a DOCTYPE with an external entity pointing to `file:///etc/passwd`,
`http://169.254.169.254/latest/meta-data/`, or an attacker-controlled URL to exfiltrate data
or trigger SSRF.

**Defence in PHP:**

```php
// PHP 8+: libxml is safe by default, but be explicit
$doc = new DOMDocument();
$doc->loadXML($xml, LIBXML_NONET | LIBXML_NOENT);  // LIBXML_NONET blocks external fetches

// SimpleXML
$sxe = simplexml_load_string($xml, 'SimpleXMLElement', LIBXML_NONET);

// For PHP < 8: disable external entity loading globally
libxml_disable_entity_loader(true);  // deprecated in 8+, not needed
```

Reject XML with DOCTYPE declarations at all unless your application genuinely needs them.
For SVG uploads, strip `<!DOCTYPE>`, `<script>`, `xlink:href="javascript:..."`, and foreign
content before storage.

## Server-Side Request Forgery (SSRF)

**How attackers probe:** any parameter that causes the backend to fetch a URL — webhook
configuration, profile avatar by URL, URL preview generator, file import from URL, PDF
render of remote page, "check my site" style features. Targets include:

- Cloud metadata: `169.254.169.254` (AWS/GCP/Azure), `metadata.google.internal`
- Internal services: `127.0.0.1:6379` (Redis), `localhost:9200` (Elasticsearch)
- Private CIDRs: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
- Link-local: `169.254.0.0/16`, `::1`, `fe80::/10`
- DNS rebinding (TTL=0 resolving first to public, then to private)

**Defence:**

```php
function isSafeFetchUrl(string $url): bool {
    $parts = parse_url($url);
    if (!$parts || !in_array($parts['scheme'] ?? '', ['http', 'https'], true)) return false;

    $host = $parts['host'] ?? '';
    $ip = filter_var($host, FILTER_VALIDATE_IP) ? $host : gethostbyname($host);

    // Block private, loopback, link-local, multicast, reserved
    if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4
        | FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
        return false;
    }
    return true;
}
```

Additional hardening:

- Use an egress proxy with an allow-list of destinations for outbound fetches
- Never follow redirects automatically (`CURLOPT_FOLLOWLOCATION = false`) — re-validate each
- Set short timeouts and response size limits
- Use a dedicated DNS resolver that refuses private ranges
- Do not expose the response body verbatim — metadata services return valuable secrets

## File upload vulnerabilities

**How attackers probe:**

- Double extensions: `shell.php.jpg`, `shell.pHp5`, `shell.phtml`
- MIME spoofing: PNG header + PHP payload, correct `Content-Type: image/png`
- Null byte in older PHP: `shell.php\x00.jpg`
- SVG with embedded `<script>` (executes when viewed in browser)
- ZIP/archive bombs, path traversal in ZIP entries (`../../etc/cron.d/rootme`)
- Polyglot files (valid JPEG + valid PHP)
- EXIF metadata containing HTML/JS for stored XSS via image viewer

**Defence checklist:**

1. **Store outside web root** — never serve by direct path
2. **Randomise filename** — `bin2hex(random_bytes(16))` + extension derived from content
3. **Validate by content (magic bytes)**, not by `$_FILES['name']` extension or MIME
4. **Re-encode images** via GD/Imagick to strip hidden payloads
5. **Enforce size limits** at web server (`client_max_body_size`) AND in PHP
6. **Scan with ClamAV** for all file types
7. **Serve via a controller** that sets `Content-Disposition: attachment` and a safe MIME
8. **Never execute** — web server must not interpret `.php` in the upload directory

```php
// Content-based validation
$allowed = [
    'image/jpeg' => 'jpg',
    'image/png'  => 'png',
    'image/webp' => 'webp',
    'application/pdf' => 'pdf',
];
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime  = finfo_file($finfo, $_FILES['file']['tmp_name']);
if (!isset($allowed[$mime])) {
    throw new Exception('Unsupported file type');
}
$ext = $allowed[$mime];
$safeName = bin2hex(random_bytes(16)) . '.' . $ext;
$dest = '/var/app-storage/uploads/' . $safeName;
move_uploaded_file($_FILES['file']['tmp_name'], $dest);
```

Web server config (nginx example): deny PHP execution in upload directory.

```nginx
location ^~ /uploads/ {
    location ~ \.php$ { deny all; return 403; }
}
```

## Path traversal

**How attackers probe:**

- `../../etc/passwd`, URL-encoded `..%2f..%2f`, double-encoded `%252e%252e%252f`
- Unicode variants, overlong UTF-8, Windows separators `..\..\windows\win.ini`
- Absolute paths: `/etc/passwd`, `C:\boot.ini`
- PHP wrapper abuse: `php://filter/convert.base64-encode/resource=config.php`

**Red flags:**

```php
include "templates/" . $_GET['page'] . ".php";  // LFI / RCE
readfile("/var/reports/" . $_GET['file']);       // arbitrary file read
```

**Defence — never build a path from user input:**

- Accept an opaque ID (integer or UUID) and look up the file path in a database
- If you must use a name, allow-list it against an enum of permitted values
- If you must accept a path, call `realpath()` and verify the result starts with your
  intended base directory

```php
$base = realpath('/var/app-storage/reports') . DIRECTORY_SEPARATOR;
$requested = realpath($base . basename($_GET['file'] ?? ''));
if ($requested === false || !str_starts_with($requested, $base)) {
    http_response_code(404); exit;
}
readfile($requested);
```

## Cross-site scripting (XSS) — defender's overview

Three categories:

- **Reflected:** payload in the request (query/body) is echoed into the response without
  encoding. Single request = execution.
- **Stored:** payload saved to DB/file and served later to other users. Higher impact —
  affects every viewer.
- **DOM-based:** the client-side JavaScript reads from `location`, `document.referrer`,
  `postMessage`, `localStorage` and writes to the DOM without encoding.

**Red flags in PHP:**

```php
echo $_GET['q'];                                    // reflected
echo '<input value="' . $user['name'] . '">';       // attribute context, no encoding
echo "<script>var u = '" . $username . "';</script>"; // JS string context
```

**Red flags in JavaScript:**

```js
element.innerHTML = userInput;           // HTML sink
eval(userInput);                          // eval = JS execution
document.write(location.hash);            // URL fragment sink
new Function(userInput)();                // equivalent to eval
location = userInput;                     // open redirect + javascript: scheme
```

**Defence — contextual output encoding at the point of use:**

| Context | PHP function | Example |
|---------|--------------|---------|
| HTML text | `htmlspecialchars($x, ENT_QUOTES \| ENT_SUBSTITUTE, 'UTF-8')` | `<p><?=h($x)?></p>` |
| HTML attribute (quoted) | same, always quote attributes | `<input value="<?=h($x)?>">` |
| JavaScript string literal | `json_encode($x, JSON_HEX_TAG \| JSON_HEX_AMP \| JSON_HEX_APOS \| JSON_HEX_QUOT)` | `<script>var u = <?=json_encode($u)?>;</script>` |
| URL parameter | `rawurlencode($x)` | `?id=<?=rawurlencode($id)?>` |
| CSS value | strict allow-list only; prefer CSS custom properties set from `data-*` |

**Layered defences:**

- Content Security Policy (see `security-headers-reference.md`) with `script-src` limited
  to hashes/nonces — no `unsafe-inline`
- `HttpOnly` session cookies so XSS cannot exfiltrate the session ID
- Trusted Types API on modern browsers for DOM sink enforcement
- Frameworks that autoescape by default (Twig, Blade) — never disable escaping globally

## Cross-site request forgery (CSRF)

CSRF exploits a browser's willingness to attach cookies to cross-origin requests. An attacker
hosts a page that auto-submits a form to your app; the user's browser sends the request with
the user's session cookie, and your server cannot distinguish it from a legitimate request.

Brief defence summary (full treatment in `auth-session-flaws.md`):

- `SameSite=Lax` or `Strict` on session cookies blocks most cross-site POSTs
- Synchronizer token on every state-changing request
- Origin / Referer header validation for state-changing requests
- Require re-authentication for sensitive actions (password change, email change, payment)

## Information disclosure

Attackers look for anything that reveals internals:

- PHP stack traces from `display_errors=On` — leak file paths, DB names, library versions
- Verbose error messages from frameworks running in debug mode
- `.git/`, `.svn/`, `.env`, `.DS_Store`, `composer.lock`, `package-lock.json` exposed
- Directory listings enabled (`Index of /`)
- Source map files (`app.js.map`) in production
- HTML comments with TODOs, developer names, commented-out credentials
- Timing differences that reveal valid usernames, tenant IDs, file existence
- Verbose `Server`, `X-Powered-By`, `X-AspNet-Version`, `X-Runtime` headers
- `phpinfo()`, `/info.php`, `/test.php` left in production

**Defence in php.ini for production:**

```ini
display_errors = Off
display_startup_errors = Off
log_errors = On
error_log = /var/log/php/error.log
expose_php = Off
```

Web server hardening:

```nginx
server_tokens off;
location ~ /\.(git|svn|env|DS_Store) { deny all; return 404; }
location = /phpinfo.php { deny all; return 404; }
```

## Attack surface minimisation — developer checklist

- [ ] No unused endpoints deployed — delete dead routes
- [ ] No debug modes enabled in production — gated on `APP_ENV`
- [ ] No admin panels reachable from the internet without VPN/IP allow-list or MFA
- [ ] No test endpoints, no seeded test accounts, no default credentials
- [ ] No source maps served publicly (or served only with auth)
- [ ] No framework/version fingerprints in headers, cookies, HTML
- [ ] No sensitive files exposed: `.git`, `.env`, `composer.lock`, backup files
- [ ] No directory listings enabled on any path
- [ ] No `phpinfo()`, no `/test.php`, no `/info.php`
- [ ] Dependencies updated weekly (Composer, npm) — SCA scanning in CI
- [ ] WAF in front of the app as a second line
- [ ] Rate limiting at reverse proxy layer (not just application)

## The WAHH methodology applied to code review

For every endpoint in the application, answer six questions:

1. **What inputs does it accept?** Enumerate query, body, headers, cookies, path params,
   uploaded files. Do not forget `$_SERVER['HTTP_*']` headers that your code reads.
2. **What authentication does it require?** Anonymous, authenticated user, authenticated
   admin, machine-to-machine? Is that check actually enforced on the server?
3. **What authorisation does it enforce?** Does it verify ownership / tenant membership
   / role on every record it touches? (Horizontal access control is the most commonly
   missed.)
4. **What does it do with the inputs?** SQL query, shell command, filesystem path, URL
   fetch, template render, log write, email send, cache key — each sink has its own class
   of flaw.
5. **What does it return?** Is any part of the response under attacker control? Could a
   response include another tenant's data? Could error messages reveal internals?
6. **What side effects occur?** State changes, external calls, background jobs, webhook
   deliveries, audit log entries. Side effects must be idempotent or CSRF-protected.

Map each sink to the flaw category above and verify the defence is in place. A code review
that answers these six questions for every endpoint will catch most web application
vulnerabilities.

## Cross-references

- `input-validation-patterns.md` — deep dive on input validation principles
- `auth-session-flaws.md` — authentication and session management flaws
- `access-control-flaws.md` — horizontal and vertical access control
- `business-logic-flaws.md` — application logic and race conditions
- `security-headers-reference.md` — CSP, HSTS, X-Frame-Options configuration
- `audit-checklist-detailed.md` — full audit checklist tied to this taxonomy
- `../SKILL.md` — entry point for the web app security audit skill
- Related skills: `php-security`, `vibe-security-skill`, `graphql-security`, `llm-security`
