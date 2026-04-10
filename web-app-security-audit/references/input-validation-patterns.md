# Input Validation and Output Encoding Patterns

Purpose: a defender's reference for validating untrusted input and encoding output correctly in PHP/JS/HTML web apps.
Covers the trust boundary lifecycle, allow-list strategies, contextual output encoding, CSP and anti-patterns.

## 1. The Two-Phase Approach

Input handling has two distinct phases, and conflating them is the root cause of most injection bugs.

1. **Validate on the way in.** Check that the data matches the expected syntactic shape — type, length, character set, range. Reject anything that does not. Validation is context-free; an integer is an integer regardless of where it will later be used.
2. **Encode on the way out.** At the moment you emit the value into an output context (HTML body, HTML attribute, URL, SQL, shell, JSON, LDAP, JavaScript string), apply the encoding rules for that specific context. Encoding is context-dependent; the same value needs different treatment in each sink.

Validation rejects bad data; encoding prevents good data from being interpreted as code. You need both. "I sanitized it" is almost always an anti-pattern because it implies stripping dangerous characters without context — and the same character is dangerous in one sink and innocuous in another.

## 2. The Input Validation Lifecycle

Every piece of untrusted input passes through the same stages:

1. **Trust boundary crossing.** The data enters from the network: HTTP request body, query string, header, cookie, uploaded file.
2. **Canonicalization.** Decode once to a normal form: URL decode, Unicode normalize, strip BOM. Do this exactly once, then validate.
3. **Syntactic validation.** Is it the right shape? Integer in range? Email pattern? ISO date?
4. **Business rule check.** Is it allowed in this state? Does the user own it? Is the order status compatible with this action?
5. **Use.** Pass through the application — to a repository, a service, another system.
6. **Output encoding.** When it finally reaches a sink (template, SQL, shell, HTTP response), encode for that sink.

Skipping step 2 leads to bypasses via encoding tricks. Skipping step 3 means garbage reaches the business layer. Skipping step 6 leads to XSS and injection.

## 3. Validation Strategies

### Allow-List (Positive Validation)

Define the exact shape of permitted input and reject everything else. This is the only reliable strategy.

```php
// Allow-list: digits only, 1 to 10 characters
if (!preg_match('/\A[0-9]{1,10}\z/', $input)) {
    throw new InvalidArgumentException('Invalid id');
}
```

Use anchors `\A` and `\z` (not `^` and `$`) to prevent newline bypasses. Bound the length. Declare the character class explicitly.

### Block-List (Negative Validation)

"Reject anything containing `<script>`." Always incomplete, always bypassable. Attackers have thirty years of tricks: `<ScRiPt>`, `<script\x00>`, `<scr<script>ipt>`, case toggling, Unicode lookalikes, HTML entities, malformed tags.

Block-lists are acceptable only as a secondary defence on top of an allow-list, never as the primary control.

### Type Coercion and Strict Parsing

PHP is a weakly typed language by default, but the filter extension gives you strict parsers:

```php
$id = filter_var($input, FILTER_VALIDATE_INT, [
    'options' => ['min_range' => 1, 'max_range' => PHP_INT_MAX],
]);
if ($id === false) {
    throw new InvalidArgumentException('Invalid id');
}
```

`intval()` and `(int)` cast silently and return `0` for non-numeric input — catastrophic for authorization decisions. Always use `filter_var` with `FILTER_VALIDATE_INT` or equivalent, which returns `false` on invalid input.

## 4. Canonicalization Pitfalls

Validation happens against a single canonical form. If an attacker can make the validator see one form and the sink see another, the validation is bypassed.

- **URL encoding.** `%2e%2e%2f` is `../`. Decode once before matching.
- **Double URL encoding.** `%252e` decodes to `%2e`, then to `.`. Decode only once; never re-decode.
- **Unicode normalization.** NFC, NFD, NFKC, NFKD can map different byte sequences to visually identical strings. Normalize to NFC for all text input.
- **Case folding.** Turkish dotted-I (İ, ı) breaks naive uppercasing. Compare case-insensitively only using well-defined collations.
- **Null bytes.** `user\x00.php` may be truncated by C libraries but not by PHP. Reject `\0` everywhere.
- **Overlong UTF-8.** `\xC0\xAE` is an invalid but sometimes accepted encoding of `.`. Validate UTF-8 strictness.

Canonicalize once, then validate against the canonical form. Never validate first and then decode.

## 5. Input Categories and Defences

### Integers

```php
$quantity = filter_var(
    $_POST['quantity'] ?? null,
    FILTER_VALIDATE_INT,
    ['options' => ['min_range' => 1, 'max_range' => 1000]],
);
if ($quantity === false || $quantity === null) {
    return $this->badRequest('quantity must be 1..1000');
}
```

Bounds are mandatory. `PHP_INT_MAX` is rarely a real business limit.

### Floats and Money

`FILTER_VALIDATE_FLOAT` is locale-aware; watch comma vs dot as decimal separator. **Never use float for money.** Use BCMath (`bcadd`, `bcmul`) or store as integer cents. Financial rounding must be explicit: define currency precision, round once at commit.

### Strings

```php
$name = $_POST['name'] ?? '';
if (!mb_check_encoding($name, 'UTF-8')) {
    return $this->badRequest('Invalid encoding');
}
$name = \Normalizer::normalize($name, \Normalizer::FORM_C);
if (mb_strlen($name) === 0 || mb_strlen($name) > 100) {
    return $this->badRequest('Name length 1..100');
}
if (strpos($name, "\0") !== false) {
    return $this->badRequest('Null byte rejected');
}
```

Always check encoding, length, and null bytes. Normalize Unicode before comparing or storing.

### Email

```php
$email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);
if ($email === false) {
    return $this->badRequest('Invalid email');
}
```

Note: `FILTER_VALIDATE_EMAIL` accepts some rarely seen but legitimate forms (quoted local parts, plus addressing). It rejects the obviously broken. Additionally cap length and, if delivering mail, verify deliverability via a bounce or token.

### URL

```php
$url = filter_var($_POST['url'] ?? '', FILTER_VALIDATE_URL);
if ($url === false) {
    return $this->badRequest('Invalid url');
}
$parts = parse_url($url);
if (!in_array($parts['scheme'] ?? '', ['http', 'https'], true)) {
    return $this->badRequest('Only http/https allowed');
}
```

Always allow-list the scheme. Block `javascript:`, `data:`, `file:`, `ftp:`, custom schemes. If the URL will be fetched server-side (image proxy, webhook), add SSRF protection: resolve the hostname, reject loopback (`127.0.0.0/8`, `::1`), reject link-local, reject private ranges (`10/8`, `172.16/12`, `192.168/16`).

### Dates

```php
$dt = DateTimeImmutable::createFromFormat('!Y-m-d', $_POST['date'] ?? '');
$errors = DateTimeImmutable::getLastErrors();
if ($dt === false || ($errors['warning_count'] ?? 0) > 0 || ($errors['error_count'] ?? 0) > 0) {
    return $this->badRequest('Invalid date');
}
```

Use `createFromFormat` with the leading `!` to zero out unset fields. Reject any warnings (these catch e.g. 2025-02-30 auto-rolling to March). Prefer ISO 8601 in storage and transport.

### Phone Numbers

Use a library (for PHP, `giggsey/libphonenumber-for-php`). Parse in a default region, normalize to E.164 for storage, render in the user's preferred format. Do not regex phone numbers.

### JSON

```php
try {
    $data = json_decode(
        $raw,
        true,
        512, // depth limit
        JSON_THROW_ON_ERROR,
    );
} catch (\JsonException) {
    return $this->badRequest('Invalid JSON');
}
```

Always set a depth limit to prevent stack exhaustion. Validate against a JSON schema if the structure is non-trivial. Reject if the payload exceeds a size cap, checked before parsing.

### XML

XML is a security hazard. Disable external entities before parsing:

```php
$prev = libxml_disable_entity_loader(true); // PHP <8.0
$dom = new DOMDocument();
$dom->loadXML($raw, LIBXML_NONET | LIBXML_DTDLOAD | LIBXML_NOENT);
// PHP 8+: libxml_disable_entity_loader is a no-op; the default is already safe.
```

Prefer JSON over XML for new APIs. If you must parse XML, disable DTDs, external entities and network access.

### File Uploads

- Check size before reading.
- Determine MIME type from **magic bytes** (`finfo_file`), not the `Content-Type` header and not the extension.
- Allow-list both MIME and extension, then pick the safer of the two.
- Store outside the web root; serve via a handler that sets `Content-Disposition` and a locked `Content-Type`.
- Rename to a random UUID; never trust the supplied filename.
- Scan with ClamAV or equivalent for user-to-user file exchange.
- Images: re-encode through a library (Imagick, Intervention) — this strips any embedded payload.

## 6. Output Encoding by Context

The sink determines the encoding. Mixing up contexts produces XSS.

### HTML Body

```php
echo htmlspecialchars($value, ENT_QUOTES | ENT_HTML5 | ENT_SUBSTITUTE, 'UTF-8');
```

`ENT_QUOTES` escapes both single and double quotes. `ENT_SUBSTITUTE` replaces invalid code units with U+FFFD instead of returning an empty string (which is silent failure).

### HTML Attribute

Same as body, but **always quote the attribute with double quotes**:

```php
echo '<input value="' . htmlspecialchars($value, ENT_QUOTES | ENT_HTML5, 'UTF-8') . '">';
```

Never emit unquoted attributes. `value=<?= $x ?>` breaks with any space or quote.

### JavaScript String

Do not hand-escape JS strings. Use `json_encode` to emit a JSON literal:

```php
<script>
  const cfg = <?= json_encode($config, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT) ?>;
</script>
```

The `JSON_HEX_*` flags prevent `</script>` breakout and attribute escaping issues. Even better: put data in a `data-*` attribute and read it from JavaScript, eliminating server-side string splicing entirely.

### URL Component

```php
$href = '/search?q=' . rawurlencode($query);
```

`rawurlencode` (RFC 3986) is safer than `urlencode` (which encodes spaces as `+`, legal only in form bodies).

### CSS

Avoid dynamic CSS values entirely. If unavoidable, allow-list the permitted values (hex colour, `px` size in range) and reject anything else. `expression()`, `url(javascript:...)` and `@import` have historically all been XSS vectors.

### SQL

SQL does not use "encoding" — it uses **parameterized queries**. Placeholders, not string concatenation, not quoting helpers:

```php
$stmt = $pdo->prepare('SELECT * FROM users WHERE email = :email');
$stmt->execute(['email' => $email]);
```

Identifiers (table names, column names) cannot be parameterized; allow-list them instead.

## 7. Template Engine Escaping

Twig, Blade, and similar engines autoescape by default. The autoescape is for the **HTML body** context. If you render user input into an attribute, a JS string, or a URL, you still need the right helper (`|e('html_attr')`, `|e('js')`, `|e('url')`).

Never concatenate HTML in PHP. Use the template. "I'm only writing one line" is where XSS is born.

Check the configuration: some projects disable autoescape for historical reasons. Search for `autoescape: false` or `{!! $x !!}` (raw Blade output) and eliminate it.

## 8. DOM-Based XSS in JavaScript

Many XSS bugs live in the client, not the server. The dangerous sinks in the browser are:

- `element.innerHTML = userValue`
- `element.outerHTML = userValue`
- `document.write(userValue)`
- `eval(userValue)`
- `new Function(userValue)`
- `setTimeout(userValue)` / `setInterval(userValue)` with a string argument
- `location = userValue` / `location.href = userValue` (open redirect / javascript: URL)

### Defences

- Use `textContent` instead of `innerHTML` when assigning text.
- Use `setAttribute` instead of string concatenation into HTML.
- When HTML must be rendered from untrusted input, sanitize with DOMPurify before insertion.
- Never pass strings to `setTimeout`/`setInterval`; pass a function reference.
- Validate redirect targets against an allow-list of origins.

## 9. Content Security Policy

CSP is a backup defence — not a substitute for input validation. When XSS slips through, a tight CSP prevents the payload from executing.

A reasonable starting policy:

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-RANDOM' 'strict-dynamic';
  style-src 'self' 'nonce-RANDOM';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self';
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
  object-src 'none';
  upgrade-insecure-requests;
```

Key practices:

- Generate a fresh nonce per response. Emit it on every `<script>` and `<style>` tag.
- Prefer `'strict-dynamic'` to an allow-list of script hosts — trusted scripts can load their own dependencies without maintaining a list.
- Deploy in `Content-Security-Policy-Report-Only` first. Fix all legitimate violations. Then switch to enforcement.
- Send reports to a collection endpoint to catch regressions.
- `frame-ancestors 'none'` replaces `X-Frame-Options`.

## 10. Header Injection

Sending a carriage return / line feed in an HTTP header value can inject a second header, or split the response, or insert a cookie. Defence is simple: reject `\r` and `\n` in any value you set via header setters.

```php
function safeHeader(string $name, string $value): void
{
    if (preg_match('/[\r\n]/', $name . $value)) {
        throw new InvalidArgumentException('Header injection attempt');
    }
    header("$name: $value");
}
```

Modern PHP `header()` blocks this, but do not rely on it — validate.

## 11. Mass Assignment

A user posts `is_admin=1` or `tenant_id=999` to a profile update endpoint. If the backend blindly binds all request fields to the model, privilege escalation is one HTTP request away.

```php
// DANGEROUS
$user->fill($_POST);
$user->save();

// SAFE
$user->update([
    'display_name' => $_POST['display_name'] ?? null,
    'email' => $_POST['email'] ?? null,
    'phone' => $_POST['phone'] ?? null,
]);
```

Every model should declare an explicit allow-list of writable fields. Privilege fields, tenant fields, and audit fields (`created_by`, `created_at`, `id`) must never appear in the allow-list.

## 12. A PHP Input Validator Class

One place to keep validation rules, with typed returns and structured errors:

```php
<?php
declare(strict_types=1);

final class Validator
{
    /** @var array<string, string> */
    private array $errors = [];

    public function integer(string $field, mixed $value, int $min, int $max): ?int
    {
        $v = filter_var($value, FILTER_VALIDATE_INT, [
            'options' => ['min_range' => $min, 'max_range' => $max],
        ]);
        if ($v === false) {
            $this->errors[$field] = "must be integer in $min..$max";
            return null;
        }
        return $v;
    }

    public function stringLen(string $field, mixed $value, int $min, int $max): ?string
    {
        if (!is_string($value) || !mb_check_encoding($value, 'UTF-8')) {
            $this->errors[$field] = 'must be a UTF-8 string';
            return null;
        }
        $v = \Normalizer::normalize($value, \Normalizer::FORM_C) ?: $value;
        if (mb_strlen($v) < $min || mb_strlen($v) > $max) {
            $this->errors[$field] = "length must be $min..$max";
            return null;
        }
        if (strpos($v, "\0") !== false) {
            $this->errors[$field] = 'null byte rejected';
            return null;
        }
        return $v;
    }

    public function email(string $field, mixed $value): ?string
    {
        $v = filter_var($value, FILTER_VALIDATE_EMAIL);
        return $v === false
            ? $this->fail($field, 'invalid email')
            : $v;
    }

    /** @return array<string,string> */
    public function errors(): array { return $this->errors; }

    public function ok(): bool { return $this->errors === []; }

    private function fail(string $field, string $msg): null
    {
        $this->errors[$field] = $msg;
        return null;
    }
}
```

## 13. Defender's Checklist

- [ ] Every input validated at the trust boundary, before business logic runs.
- [ ] Allow-list validation used — not block-list.
- [ ] Integer bounds explicit, not `PHP_INT_MAX`.
- [ ] Canonicalization done once, then validation.
- [ ] Output encoded per context (HTML body, attribute, JS, URL, CSS).
- [ ] Template autoescape is enabled; raw output (`{!! !!}`) audited.
- [ ] SQL uses prepared statements everywhere; no concatenation.
- [ ] CSP present, nonce-based, and tight.
- [ ] `X-Content-Type-Options: nosniff` set on all responses.
- [ ] JSON decoding sets a depth limit.
- [ ] XML parsing has external entities disabled.
- [ ] File uploads validated by magic bytes; stored outside web root; renamed.
- [ ] Mass assignment prevented by explicit field allow-lists.
- [ ] URL validation includes scheme allow-list and SSRF protection.
- [ ] Money is BCMath or integer cents, never float.

## 14. Anti-Patterns

- **`strip_tags` as XSS defence.** It does not cover attribute injection, encoded payloads, or CSS contexts.
- **`addslashes` or `mysql_real_escape_string` instead of prepared statements.** Both have known bypasses with multi-byte charsets.
- **Concatenating user input into any query, shell command, eval, or HTML string.** The only correct answer is: don't.
- **Block-listing `<script>`.** `<img src=x onerror=alert(1)>`, `<svg onload=...>`, etc.
- **Normalizing to uppercase and then comparing.** Turkish locale: `i`.toUpperCase() is `İ`, not `I`.
- **Trusting the `Content-Type` header on file uploads.** Attackers set whatever they want.
- **Double-decoding.** If you decode once, validate, decode again, the validation was pointless.
- **Client-side validation only.** Client validation is UX; every check must be re-run on the server.
- **"We regex-match the input, so we're safe."** Regexes are easy to get subtly wrong, and bypasses are frequent.
- **Relying on framework defaults without checking.** Templates, autoescape, content type, headers — verify each.
- **Sanitizing instead of validating.** "Remove dangerous characters" is a fiction; different sinks have different dangers.

## Cross-References

- `access-control-flaws.md` — authorization bugs that validation alone cannot fix
- `business-logic-flaws.md` — validation passes, but workflow or state is wrong
- `security-headers-reference.md` — CSP, HSTS, and friends as backup defences
- `audit-checklist-detailed.md` — parent skill's master audit checklist
- `php-security` skill — PHP-specific input handling and session hardening
- `vibe-security-skill` — general secure coding baseline
- OWASP Top 10: A03 Injection, A05 Security Misconfiguration
- OWASP Cheat Sheet Series: Input Validation, Cross-Site Scripting Prevention
