# XSS Deep Dive for PHP

Defensive reference for preventing Cross-Site Scripting in PHP applications.
Covers the three XSS types, context-aware output encoding, template engines, CSP, and anti-patterns.

## What XSS is

Cross-Site Scripting is the execution of attacker-supplied content as HTML or JavaScript inside a victim's browser. Once executed, the injected script runs with the victim's origin and privileges, so it can read cookies that are not `HttpOnly`, read the DOM, submit forms on the user's behalf, make same-origin API calls, keylog inputs, or deface the page. XSS is the single most common web vulnerability class and is almost always caused by treating user-controlled data as code at render time.

## The three types

| Type | Where the payload lives | Example |
|---|---|---|
| Reflected | In the current HTTP request; echoed straight back in the response | `search.php?q=<script>...</script>` shown in search results |
| Stored | Persisted in a database/file/cache; served to other users later | A comment containing `<img onerror=...>` shown on a product page |
| DOM-based | Entirely client-side; JavaScript reads attacker data and writes it into the DOM unsafely | `document.location.hash` fed into `innerHTML` |

Reflected and stored XSS are server-side rendering problems. DOM-based XSS is a client-side JavaScript problem and is invisible to server logs.

## Why "filter inputs" is the wrong mental model

XSS is an OUTPUT problem, not an input problem. The same string is safe in a JSON API response, dangerous in an HTML body, dangerous in a JavaScript string literal, and dangerous in a URL attribute — and the rules for making it safe are different in each context. If you try to sanitise at input time you have to guess every future use of the data. Instead, store data raw and apply the correct encoder at the exact moment you render it into a specific output context.

## Output contexts and their encoders

| Context | PHP encoder |
|---|---|
| HTML body / element content | `htmlspecialchars($x, ENT_QUOTES \| ENT_HTML5, 'UTF-8')` |
| HTML attribute (must be quoted) | Same as above; always use double quotes around the attribute |
| JavaScript string literal inside `<script>` | `json_encode($x, JSON_HEX_TAG \| JSON_HEX_AMP \| JSON_HEX_APOS \| JSON_HEX_QUOT \| JSON_UNESCAPED_UNICODE)` |
| URL attribute (`href`, `src`) | Validate scheme is `http`/`https`, then encode individual query pieces with `rawurlencode` |
| CSS value | Avoid entirely; if unavoidable, strict allow-list of tokens |
| Event handler attribute (`onclick`, etc.) | Avoid entirely; bind via `addEventListener` in JavaScript |

### Safe echo in HTML body

```php
<?php
function e(string $s): string {
    return htmlspecialchars($s, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}
?>
<p>Hello, <?= e($name) ?></p>
<input type="text" name="email" value="<?= e($email) ?>">
```

### Safe JSON data handed to JavaScript

```php
<script>
  const user = <?= json_encode(
      $user,
      JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_UNESCAPED_UNICODE
  ) ?>;
  console.log(user.name);
</script>
```

The `JSON_HEX_*` flags escape `<`, `&`, `'`, and `"` so the JSON literal cannot break out of a `<script>` block or an attribute containing JSON.

### Safe URL attribute

```php
<?php
$scheme = parse_url($url, PHP_URL_SCHEME);
if (!in_array($scheme, ['http', 'https'], true)) {
    $url = '#'; // Reject javascript:, data:, vbscript:, file:, etc.
}
?>
<a href="<?= htmlspecialchars($url, ENT_QUOTES | ENT_HTML5, 'UTF-8') ?>">Link</a>
```

Rejecting unknown schemes is critical — `javascript:alert(1)` passes naive URL validation but executes when clicked.

### Building a URL with user-supplied query params

```php
$href = '/search?q=' . rawurlencode($query)
      . '&page=' . rawurlencode((string)$page);
echo '<a href="' . htmlspecialchars($href, ENT_QUOTES | ENT_HTML5, 'UTF-8') . '">Next</a>';
```

## Template engines — autoescape is the default

Modern template engines autoescape HTML. Rely on it and do not disable it.

- **Twig** escapes HTML by default. For other contexts use explicit filters: `{{ x|e('js') }}`, `{{ x|e('css') }}`, `{{ x|e('url') }}`, `{{ x|e('html_attr') }}`. Never set `autoescape: false` globally.
- **Blade** escapes with `{{ $x }}`. The raw syntax `{!! $x !!}` does not escape and is a red flag in any code review.
- **Plates, Latte, Smarty 3+** — all autoescape by default; follow the engine's context-specific filter documentation.

If a codebase uses raw `echo` without a helper, add an `e()` helper everywhere and grep for unescaped output.

## Rich text, WYSIWYG, and HTML email

You cannot escape rich HTML — it must *be* HTML. You must parse it and rebuild it from an allow-list.

- Use **HTMLPurifier**, the battle-tested allow-list parser. Do not try to write your own filter.
- Never use regex-based blocklists to strip `<script>`. They always miss `<IMG SRC=x onerror=...>`, SVG vectors, HTML comments, and encoding tricks.
- Configure HTMLPurifier with only the tags and attributes you actually need.
- Sanitise once at the point of rendering (or once at storage AND re-validate at render). Never trust previously stored HTML blindly — a library upgrade may change what is considered safe.

```php
require_once 'HTMLPurifier.auto.php';

$config = HTMLPurifier_Config::createDefault();
$config->set('HTML.Allowed', 'p,br,strong,em,ul,ol,li,a[href|title],h2,h3,blockquote');
$config->set('HTML.TargetBlank', true);
$config->set('URI.AllowedSchemes', ['http' => true, 'https' => true, 'mailto' => true]);
$purifier = new HTMLPurifier($config);

$cleanHtml = $purifier->purify($userHtml);
```

## DOM-based XSS prevention in JavaScript

DOM-based XSS happens inside the browser — the server never sees the payload. Rules for the front-end:

- Use `element.textContent = value` (safe — inserts as text).
- Avoid `element.innerHTML = value`. If you must, sanitise with **DOMPurify**.
- Never use `document.write`, `eval`, `new Function(str)`, `setTimeout("string")`, or `setInterval("string")`.
- Treat `location.hash`, `location.search`, `location.href`, `document.referrer`, `window.name`, and `postMessage` payloads as hostile input.
- Validate URL schemes before assigning to `location` or to an `href` set by script.

```javascript
// Unsafe
el.innerHTML = location.hash.slice(1);

// Safe
el.textContent = location.hash.slice(1);
```

## Content Security Policy as a second line of defence

CSP is not a replacement for output encoding. It is a blast-radius reducer that blocks the payload if encoding fails.

```text
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-Rk9PQkFS';
  style-src 'self';
  object-src 'none';
  base-uri 'self';
  frame-ancestors 'none';
  form-action 'self'
```

- Generate a fresh nonce per request with `bin2hex(random_bytes(16))` and embed it on every `<script>` tag you emit.
- Start in `Content-Security-Policy-Report-Only` mode, monitor reports, then enforce.
- For larger sites use `'strict-dynamic'` together with a nonce to let approved scripts load their own dependencies.
- `object-src 'none'` kills Flash/PDF XSS vectors. `base-uri 'self'` prevents `<base href>` injection.

```php
$nonce = bin2hex(random_bytes(16));
header("Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-$nonce'; object-src 'none'; base-uri 'self'");
?>
<script nonce="<?= $nonce ?>">
  // trusted inline code
</script>
```

## HttpOnly cookies limit the blast radius

Even if XSS fires, an `HttpOnly` session cookie cannot be read by JavaScript, so session-theft attacks fail. Combine with `Secure` (HTTPS only) and `SameSite=Lax` or `Strict`.

```php
session_set_cookie_params([
    'lifetime' => 0,
    'path'     => '/',
    'domain'   => '',
    'secure'   => true,
    'httponly' => true,
    'samesite' => 'Lax',
]);
```

## XSS in error messages and logs

- In production, set `display_errors = Off` in `php.ini`. Stack traces that include user input can echo `<script>` payloads straight to the browser.
- Log files rendered in an admin HTML viewer must be escaped on display. Never let a log line turn into executable markup in the admin panel.
- Emails generated from user input — also HTML-escape unless you are running through HTMLPurifier.

## Mutation XSS (mXSS)

Some vectors are safe according to the HTML spec but become unsafe after the browser re-serialises the DOM inside `innerHTML`. DOMPurify and HTMLPurifier both have mitigations, but you should still keep user HTML out of locations where it will be re-serialised (e.g. do not copy a sanitised blob into `innerHTML` of another element without re-sanitising).

## Defender's checklist

- [ ] Template engine autoescape is enabled globally
- [ ] No raw `echo $_GET[...]`/`echo $_POST[...]`/`echo $_COOKIE[...]`
- [ ] JSON data inlined into scripts uses `json_encode` with the four `JSON_HEX_*` flags
- [ ] No user-controlled data inside `onclick=` / `onload=` / other event handler attributes
- [ ] `href` and `src` attributes validate scheme against an allow-list
- [ ] Content Security Policy deployed, starting in report-only mode
- [ ] Session cookies set `HttpOnly`, `Secure`, `SameSite`
- [ ] Rich text / WYSIWYG content is parsed by HTMLPurifier with a strict allow-list
- [ ] `display_errors = Off` in production; log viewers re-escape log lines
- [ ] Client-side code prefers `textContent` over `innerHTML`
- [ ] DOMPurify wraps any unavoidable `innerHTML` usage

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| `strip_tags($x)` as XSS defence | Misses attribute vectors like `<a href="javascript:...">`; mangles valid text |
| `addslashes` before echo | `addslashes` is a SQL artefact; it does nothing to HTML |
| `htmlentities` without `ENT_QUOTES` | Attribute-based injection still possible because single quotes are not escaped |
| Regex blocklist that removes `<script>` | Defeated by `<img onerror>`, SVG, `<iframe srcdoc>`, casing tricks, HTML entity encoding |
| `FILTER_SANITIZE_STRING` | Deprecated in PHP 8.1; was never a reliable XSS defence |
| Disabling template autoescape "for performance" | Opens every rendered page to XSS; the cost is trivial compared to the risk |
| Sanitising at input only | Misses data added via imports, admin panels, or API endpoints |

## Cross-references

- `php-security/SKILL.md` — overall PHP security posture
- `php-security/references/injection-attack-patterns.md` — sibling reference on injection classes
- `php-security/references/security-code-patterns.md` — reusable PHP helpers
- `php-security/references/session-hardening.md` — HttpOnly/Secure cookie setup
- `vibe-security-skill` — cross-stack secure coding
- `llm-security` — prompt injection is structurally similar to output-context confusion
