# Injection Attack Patterns for PHP

Defensive reference covering every injection class a PHP application can face.
Core principle: keep data out of the code channel that an interpreter parses.

## The injection principle

Every injection vulnerability has the same shape: user-controlled data is concatenated into a string that will be parsed by an interpreter (SQL engine, shell, LDAP server, XML parser, HTTP client, template engine, PHP itself). The interpreter cannot tell data from code, so metacharacters in the data become new instructions. The only durable fix is to use an API that keeps data and code in separate channels — parameterised queries, argument arrays, escaping functions tied to a specific context, or eliminating the interpreter call altogether.

## SQL injection

### Mechanism

```php
// DANGEROUS — do not do this
$email = $_POST['email'];
$sql = "SELECT id FROM users WHERE email = '$email'";
$pdo->query($sql);
```

A payload of `' OR '1'='1` turns the WHERE clause into a tautology. More surgical payloads extract data (`UNION SELECT`), modify rows, drop tables, or read filesystem contents via `LOAD_FILE`.

### PDO prepared statements are the answer

```php
$pdo = new PDO(
    'mysql:host=localhost;dbname=app;charset=utf8mb4',
    $user,
    $pass,
    [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_EMULATE_PREPARES   => false,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]
);

$stmt = $pdo->prepare(
    'SELECT id, name FROM users WHERE email = ? AND tenant_id = ?'
);
$stmt->execute([$email, $tenantId]);
$user = $stmt->fetch();
```

- `ATTR_EMULATE_PREPARES = false` forces the driver to use real server-side parameter binding. Emulated prepares have had driver-level bypass issues (see CVE-2012-2143 and character-set edge cases).
- `ATTR_ERRMODE = ERRMODE_EXCEPTION` makes silent failures impossible.
- Use `utf8mb4` everywhere; legacy `latin1` with `SET NAMES` is how multi-byte encoding attacks historically bypassed escaping.

### Named placeholders for readability

```php
$stmt = $pdo->prepare('
    INSERT INTO invoices (tenant_id, customer_id, amount, currency)
    VALUES (:tenant, :customer, :amount, :currency)
');
$stmt->execute([
    ':tenant'   => $tenantId,
    ':customer' => $customerId,
    ':amount'   => $amount,
    ':currency' => $currency,
]);
```

### Identifier injection (tables and columns)

Prepared statements cannot parameterise identifiers. Use an allow-list.

```php
$allowedSortColumns = ['created_at', 'amount', 'customer_name'];
$allowedDirections  = ['ASC', 'DESC'];

$sortColumn = in_array($_GET['sort'] ?? '', $allowedSortColumns, true)
    ? $_GET['sort']
    : 'created_at';

$sortDir = in_array(strtoupper($_GET['dir'] ?? ''), $allowedDirections, true)
    ? strtoupper($_GET['dir'])
    : 'DESC';

$sql = "SELECT * FROM invoices WHERE tenant_id = ? ORDER BY $sortColumn $sortDir LIMIT 50";
$stmt = $pdo->prepare($sql);
$stmt->execute([$tenantId]);
```

### LIKE operator metacharacter escape

`%` and `_` are wildcards inside LIKE patterns — escape them if the user supplies a literal search term.

```php
$escaped = addcslashes($search, '%_\\');
$stmt = $pdo->prepare('SELECT id FROM products WHERE name LIKE ? LIMIT 20');
$stmt->execute(['%' . $escaped . '%']);
```

### Stored procedures are not a silver bullet

If the procedure body itself concatenates parameters into dynamic SQL (`PREPARE ... FROM CONCAT(...)`), SQL injection still exists. Prepared statements at the application layer remain the correct defence.

### ORMs

Doctrine, Eloquent, Cycle, and similar libraries generate parameterised SQL by default. The danger is the raw-SQL escape hatch — `DB::select('SELECT ... ' . $x)`, `$qb->where("name = '$x'")`. Grep for those.

## NoSQL injection (MongoDB)

PHP's Mongo driver accepts nested arrays as query documents. A JSON body that provides `{"email": {"$ne": null}}` becomes a PHP array `['email' => ['$ne' => null]]` and matches every row.

```php
// DANGEROUS — blindly trusting the request body
$user = $collection->findOne(['email' => $_POST['email'], 'password' => $_POST['password']]);

// SAFE — force scalar strings
$email    = is_string($_POST['email'] ?? null) ? $_POST['email'] : '';
$password = is_string($_POST['password'] ?? null) ? $_POST['password'] : '';
$user = $collection->findOne([
    'email'    => (string)$email,
    'password' => (string)$password,
]);
```

Never forward `$_POST` arrays into a NoSQL query without type-casting each field.

## OS command injection

### Dangerous functions

`exec`, `system`, `shell_exec`, `passthru`, `popen`, `proc_open`, backticks (`` `cmd` ``), and `pcntl_exec`.

### First rule: avoid the shell entirely

If PHP has a native API for the task (image resizing, file hashing, archive extraction), use it. `file_get_contents`, `imagecopyresampled`, `ZipArchive`, `hash_file`, `openssl_*` all avoid shell execution and escape rules.

### If you must shell out

```php
// DANGEROUS
system('convert ' . $filename . ' -resize 800x output.jpg');

// SAFER — escape, allow-list, and avoid shell interpretation
$allowedExt = ['jpg', 'jpeg', 'png'];
$ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
if (!in_array($ext, $allowedExt, true)) {
    throw new RuntimeException('Unsupported file type');
}

// Use proc_open with argv array — no shell interpolation at all
$descriptors = [1 => ['pipe', 'w'], 2 => ['pipe', 'w']];
$process = proc_open(
    ['/usr/bin/convert', $filename, '-resize', '800x', $outputPath],
    $descriptors,
    $pipes
);
```

Passing an argv array to `proc_open` bypasses `/bin/sh` entirely, so shell metacharacters (`;`, `&&`, `|`, `` ` ``, `$()`) in the arguments cannot chain commands.

If you cannot use argv form, use `escapeshellarg` on every value, still validate against an allow-list, and never pass entire user input as the command name.

```php
$safeFilename = escapeshellarg($filename);
$cmd = "/usr/bin/convert $safeFilename -resize 800x " . escapeshellarg($outputPath);
$output = shell_exec($cmd);
```

## LDAP injection

LDAP filter syntax has its own metacharacters (`*`, `(`, `)`, `\`, `NUL`). Escape with `ldap_escape`.

```php
$username = ldap_escape($_POST['username'], '', LDAP_ESCAPE_FILTER);
$filter = "(&(objectClass=user)(uid=$username))";
$result = ldap_search($link, 'ou=users,dc=example,dc=com', $filter);

// For DN strings use LDAP_ESCAPE_DN
$rdn = ldap_escape($_POST['cn'], '', LDAP_ESCAPE_DN);
```

## XPath injection

PHP's DOMXPath has no built-in parameterisation. Either hard-code the XPath, or sanitise with a strict allow-list, or prefer JSON/SQL for data exchange.

## XXE — XML External Entity

Modern PHP (libxml ≥ 2.9, PHP ≥ 8.0) disables external entity loading by default. Still, write defensively:

```php
$xml = file_get_contents('php://input');

// Disable network fetches; reject entities with LIBXML_NONET and LIBXML_NOENT=0
libxml_use_internal_errors(true);
$doc = new DOMDocument();
$doc->loadXML($xml, LIBXML_NONET | LIBXML_DTDLOAD | LIBXML_DTDATTR);

// Never set LIBXML_NOENT — that enables entity substitution
```

For older PHP, call `libxml_disable_entity_loader(true)` before any parse. Do not use `simplexml_load_string` on untrusted input without the same flags.

## Template injection (SSTI)

If users supply template source code and the engine renders it with full function access, they get arbitrary PHP execution (Twig `{{ ['id']|filter('system') }}`, Smarty `{php}` blocks, Blade `@php`).

- Never let users edit template source code.
- If you must support user-supplied fragments, use the Twig sandbox extension with an explicit allow-list of tags, filters, methods, and properties.
- Disable dangerous globals (`_self`, raw PHP execution) in whatever engine you use.

## Header injection and CRLF

```php
// DANGEROUS
header('Location: ' . $_GET['next']);
```

PHP's `header()` has blocked `\n` since 5.1.2, but an attacker can still point the victim at a malicious site (open redirect). Defend with an allow-list of destinations or by storing an opaque token that maps to a server-side URL.

```php
$allowed = ['/dashboard', '/billing', '/settings'];
$next = in_array($_GET['next'] ?? '', $allowed, true) ? $_GET['next'] : '/dashboard';
header('Location: ' . $next, true, 302);
exit;
```

## Mail header injection

User input in the To/Cc/Bcc/Subject/From fields can introduce new headers (via embedded `\r\n`) and hijack the message.

```php
// DANGEROUS — raw mail() with user-controlled headers
mail($to, $subject, $body, "From: $userEmail\r\n");
```

Use PHPMailer, Symfony Mailer, or Laminas Mail. They validate headers, enforce encoding, and set addresses through API methods that cannot be tricked into injecting new headers.

```php
use Symfony\Component\Mime\Email;
use Symfony\Component\Mailer\Mailer;

$email = (new Email())
    ->from('noreply@example.com')
    ->to($recipient)
    ->subject($subject)
    ->text($body);

$mailer->send($email);
```

## SSRF — Server-Side Request Forgery

SSRF is URL injection against an HTTP client. The interpreter is cURL or the stream wrapper. Attack targets include cloud metadata services (`169.254.169.254`), internal admin endpoints, and localhost-only services.

Defence layers:

1. Scheme allow-list (`http`, `https` only).
2. Host allow-list, or a blocklist of private/link-local CIDRs: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16`, `::1/128`, `fc00::/7`, `fe80::/10`.
3. Resolve DNS yourself, check the resolved IP, then connect to that IP directly (TOCTOU-safe).
4. Disable redirects, or re-validate the resolved URL after each redirect.

```php
function assertSafeOutboundUrl(string $url): string {
    $parts = parse_url($url);
    if (!in_array($parts['scheme'] ?? '', ['http', 'https'], true)) {
        throw new RuntimeException('Scheme not allowed');
    }
    $host = $parts['host'] ?? '';
    $ip = filter_var($host, FILTER_VALIDATE_IP)
        ? $host
        : gethostbyname($host);

    if (isPrivateIp($ip)) {
        throw new RuntimeException('Private IP blocked');
    }
    return $url;
}

function isPrivateIp(string $ip): bool {
    return !filter_var(
        $ip,
        FILTER_VALIDATE_IP,
        FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE
    );
}
```

Pass `CURLOPT_FOLLOWLOCATION => false` and handle redirects yourself so every hop is re-validated.

## Path traversal

The filesystem is the interpreter, `../` is the metacharacter.

```php
// DANGEROUS
include '/var/app/templates/' . $_GET['page'] . '.php';
```

Defence: canonicalise with `realpath` and enforce a prefix check.

```php
$baseDir = realpath('/var/app/templates');
$target  = realpath($baseDir . '/' . $_GET['page'] . '.php');

if ($target === false || !str_starts_with($target, $baseDir . DIRECTORY_SEPARATOR)) {
    http_response_code(404);
    exit;
}

include $target;
```

Better: never let the user name the file. Map an opaque ID to a server-side filename:

```php
$pages = [
    'home'    => 'home.php',
    'about'   => 'about.php',
    'pricing' => 'pricing.php',
];
$page = $pages[$_GET['page'] ?? 'home'] ?? 'home.php';
include __DIR__ . '/pages/' . $page;
```

## Code injection

PHP has two ways to execute arbitrary code from a string: `eval()` and file inclusion (`include`/`require` with dynamic paths).

- **`eval($userInput)` has no safe form.** There is no escaping function that can make it safe. Delete every `eval` in the codebase.
- **`include $userInput`** — if the user can influence the path (even indirectly via configuration), they can execute arbitrary PHP. Combined with file upload, they get remote code execution. Use an allow-list map as shown above.
- **`create_function`** is deprecated and removed in PHP 8.0; its removal was driven entirely by injection risk. Use closures instead.
- **`unserialize($userInput)`** — object injection. Magic methods (`__wakeup`, `__destruct`, `__toString`) can be chained to reach dangerous sinks. Never unserialise untrusted data; use `json_decode` instead.

## Defender's audit checklist

- [ ] Every SQL query uses prepared statements with bound parameters
- [ ] `PDO::ATTR_EMULATE_PREPARES = false` and `ERRMODE_EXCEPTION` set
- [ ] Database connection uses `utf8mb4`, not `latin1` + `SET NAMES`
- [ ] `LIKE` patterns escape `%`, `_`, `\`
- [ ] `ORDER BY` / table / column names validated against allow-lists
- [ ] No `exec`/`system`/`shell_exec`/`passthru`/backticks with user data
- [ ] `proc_open` argv form preferred over shell strings
- [ ] No `eval`, no `create_function`, no `unserialize` on user data
- [ ] No dynamic `include`/`require` with user-controlled paths
- [ ] `ldap_escape` used on every LDAP filter and DN fragment
- [ ] XML parsers set `LIBXML_NONET`; `LIBXML_NOENT` not set
- [ ] Mail sent via PHPMailer/Symfony Mailer, not raw `mail()` with header strings
- [ ] Outbound HTTP calls validate scheme, host, and resolved IP against private ranges
- [ ] File operations use an allow-list ID map, not user-supplied paths
- [ ] Template engines do not render user-supplied template source

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| `mysql_real_escape_string` as primary defence | Deprecated API; wrong tool; broke under multi-byte charset tricks |
| String concatenation "because ORM is too slow" | Performance gain is negligible; risk is total |
| Disabling emulated prepares "for the statement cache" | The cache gain is trivial and emulated prepares are a proven bypass vector |
| Trusting "framework magic" without reading the docs | Some query builders have raw-SQL shortcuts that look safe but aren't |
| `escapeshellcmd` as the only defence | It escapes the whole command string, not per-argument; still allows argument injection |
| Blocklisting known-bad SQL keywords | Defeated by comment obfuscation, encoding, and case variation |
| Sanitising at input instead of at the interpreter boundary | Data changes meaning in different contexts; you must encode per sink |
| Calling `unserialize` on cookies or request bodies | PHP object injection leads to remote code execution via magic methods |

## Cross-references

- `php-security/SKILL.md` — overall PHP security posture
- `php-security/references/xss-deep-dive.md` — sibling reference on output encoding
- `php-security/references/input-output-security.md` — input validation patterns
- `php-security/references/security-code-patterns.md` — reusable PHP helpers
- `mysql-best-practices` — prepared statements and query design
- `llm-security` — prompt injection is structurally a template injection class
- `api-design-first` — where to enforce validation at API boundaries
