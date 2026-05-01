# php.ini Security Checklist

Complete security audit checklist for PHP configuration. Use during deployment or security review.

**Parent skill:** php-security

## Critical Settings (Must Fix)

| Directive | Secure Value | Risk if Wrong |
|-----------|-------------|---------------|
| `display_errors` | `Off` | Stack traces leak file paths, DB credentials, internal logic |
| `display_startup_errors` | `Off` | PHP module info leaked to attackers |
| `expose_php` | `Off` | `X-Powered-By: PHP/8.x` header reveals version for targeted exploits |
| `allow_url_include` | `Off` | Remote File Inclusion (RFI) — attacker includes malicious PHP from URL |
| `allow_url_fopen` | `Off` (if possible) | SSRF risk — PHP can fetch attacker-controlled URLs |
| `register_globals` | `Off` | Removed in PHP 5.4 but verify on legacy systems |
| `session.use_only_cookies` | `1` | Session ID in URL leaks via Referer header, browser history, logs |
| `session.use_strict_mode` | `1` | Accepts attacker-supplied session IDs (session fixation) |
| `session.cookie_httponly` | `1` | XSS can steal session cookie via document.cookie |
| `open_basedir` | Set to app root | PHP can read ANY file on server (e.g., /etc/passwd) |

## High Priority Settings

| Directive | Secure Value | Purpose |
|-----------|-------------|---------|
| `log_errors` | `On` | Capture errors server-side for debugging |
| `error_log` | `/var/log/php/error.log` | Dedicated error log location |
| `error_reporting` | `E_ALL` | Report all errors (log them, don't display) |
| `session.cookie_secure` | `1` | Only send session cookie over HTTPS |
| `session.cookie_samesite` | `Strict` | Prevent CSRF-based session abuse |
| `session.use_trans_sid` | `0` | Never embed session ID in HTML links |
| `session.gc_maxlifetime` | `1800` | Session expires after 30 min idle |
| `session.sid_length` | `48` | Longer session IDs are harder to guess |
| `session.sid_bits_per_character` | `6` | Maximum entropy per character |
| `max_execution_time` | `30` | Prevent DoS via long-running scripts |
| `max_input_time` | `60` | Limit input parsing time |
| `memory_limit` | `128M` | Prevent memory exhaustion attacks |

## File Upload Settings

| Directive | Secure Value | Purpose |
|-----------|-------------|---------|
| `file_uploads` | `On` (if needed) | Disable entirely if no uploads required |
| `upload_max_filesize` | `5M` | Limit individual file size |
| `max_file_uploads` | `5` | Limit files per request |
| `post_max_size` | `10M` | Must be >= upload_max_filesize |
| `upload_tmp_dir` | Dedicated path | Don't use shared /tmp on shared hosting |

## Dangerous Functions to Disable

```ini
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source,eval
```

**Note:** Only disable functions your application doesn't need. Web apps rarely need exec/shell functions.

| Function | Risk |
|----------|------|
| `exec()` | Execute system commands |
| `passthru()` | Execute and output raw result |
| `shell_exec()` | Execute via shell |
| `system()` | Execute and output |
| `proc_open()` | Open process with pipes |
| `popen()` | Open process pipe |
| `eval()` | Execute arbitrary PHP code |
| `assert()` | Can execute code in older PHP |
| `parse_ini_file()` | Read server config files |
| `show_source()` | Display PHP source code |
| `phpinfo()` | Expose full server configuration |

## Complete Secure php.ini Template

```ini
; ============================================
; PHP SECURITY CONFIGURATION
; Apply to production php.ini
; ============================================

; --- Error Handling ---
display_errors = Off
display_startup_errors = Off
log_errors = On
error_log = /var/log/php/error.log
error_reporting = E_ALL
html_errors = Off

; --- PHP Information ---
expose_php = Off

; --- Resource Limits ---
max_execution_time = 30
max_input_time = 60
memory_limit = 128M
post_max_size = 10M

; --- File Uploads ---
file_uploads = On
upload_max_filesize = 5M
max_file_uploads = 5
upload_tmp_dir = /var/lib/php/uploads

; --- File Access ---
open_basedir = /var/www/app:/var/lib/php
allow_url_fopen = Off
allow_url_include = Off

; --- Session Security ---
session.use_cookies = 1
session.use_only_cookies = 1
session.use_trans_sid = 0
session.use_strict_mode = 1
session.cookie_httponly = 1
session.cookie_samesite = Strict
; session.cookie_secure = 1  ; Enable for HTTPS sites
session.cookie_lifetime = 0
session.name = __Host-SESSID
session.sid_length = 48
session.sid_bits_per_character = 6
session.gc_maxlifetime = 1800
session.gc_probability = 1
session.gc_divisor = 100
session.save_path = /var/lib/php/sessions
session.serialize_handler = php_serialize
session.cache_limiter = nocache

; --- Disable Dangerous Functions ---
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,show_source,phpinfo

; --- Misc Security ---
default_charset = "UTF-8"
```

## Audit Workflow

### Step 1: Review Current Configuration

```bash
# Show loaded php.ini location
php --ini

# Show specific directives
php -i | grep display_errors
php -i | grep expose_php
php -i | grep open_basedir
php -i | grep session
php -i | grep disable_functions
php -i | grep allow_url
```

### Step 2: Check Against This Checklist

Run through each table above. For every directive:
1. Check current value
2. Compare to secure value
3. Document any deviations with business justification
4. Apply fix or document accepted risk

### Step 3: Verify Changes

```bash
# After editing php.ini, restart PHP
sudo systemctl restart php8.2-fpm  # or php-fpm, apache2

# Verify changes took effect
php -r "echo ini_get('display_errors');"  # Should be empty/Off
php -r "echo ini_get('expose_php');"      # Should be empty/Off
php -r "echo ini_get('session.use_strict_mode');"  # Should be 1
```

### Step 4: Test Application

After hardening, verify your application still works:
- [ ] Login/logout flow works
- [ ] File uploads function correctly
- [ ] Session timeout enforced
- [ ] Error logging captures errors
- [ ] No errors displayed to users
- [ ] All features functional

## Environment-Specific Notes

### Development (Windows/localhost)

```ini
; Allow error display for debugging
display_errors = On
error_reporting = E_ALL
; session.cookie_secure = 0  ; HTTP on localhost
```

### Staging (Ubuntu)

```ini
; Match production settings
display_errors = Off
; Test with session.cookie_secure = 1 if HTTPS configured
```

### Production (Debian)

```ini
; Full lockdown as per template above
; ALL security directives enabled
; disable_functions configured
; open_basedir restricted
```

## Quick Audit Summary

Use this shortened checklist for rapid audits:

- [ ] `display_errors = Off`
- [ ] `expose_php = Off`
- [ ] `allow_url_include = Off`
- [ ] `open_basedir` is set
- [ ] `session.use_only_cookies = 1`
- [ ] `session.use_strict_mode = 1`
- [ ] `session.cookie_httponly = 1`
- [ ] `disable_functions` configured
- [ ] `error_log` set to writable path
- [ ] `upload_max_filesize` reasonable
- [ ] File permissions: php.ini is 644, owned by root
- [ ] Session save_path has restricted permissions (700)
