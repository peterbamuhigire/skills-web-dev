# SaaS Seeder Troubleshooting Guide

Common issues and their solutions.

## Session Not Persisting

**Issue:** Login successful but redirects back to login.

**Solution:** Session cookie secure flag. Already handled:
```php
// Automatically disabled on HTTP (localhost)
$isHttps = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
           || $_SERVER['SERVER_PORT'] == 443;
ini_set('session.cookie_secure', $isHttps ? '1' : '0');
```

**Without this fix, sessions won't persist on localhost HTTP.**

## Password Mismatch

**Issue:** Can't login after creating user.

**Solution:** Use `super-user-dev.php` NOT manual password_hash():
```php
// CORRECT (super-user-dev.php does this)
$passwordHelper = new PasswordHelper();
$hash = $passwordHelper->hashPassword($password);

// WRONG - won't match login!
$hash = password_hash($password, PASSWORD_BCRYPT);
```

**The template uses Argon2ID, NOT bcrypt.**

## Collation Errors

**Issue:** "Illegal mix of collations" errors.

**Solution:** Run `fix-database.ps1`:
```bash
.\fix-database.ps1
```

This fixes:
- Collation mismatches to utf8mb4_unicode_ci
- Stored procedure collation issues
- VARCHAR comparison problems

## Missing Franchises Table

**Issue:** "Table 'tbl_franchises' doesn't exist".

**Solution:** Run fix script (includes franchises table creation):
```bash
.\fix-database.ps1
```

Or manual:
```bash
mysql -u root -p saas_seeder < docs/seeder-template/fix-collation-and-create-franchises.sql
```

## Cross-Franchise Data Leakage

**Issue:** Users seeing data from other franchises.

**Solution:** Always filter by franchise_id:
```php
// CORRECT
$stmt = $db->prepare("
    SELECT * FROM students
    WHERE franchise_id = ? AND id = ?
");
$stmt->execute([getSession('franchise_id'), $studentId]);

// WRONG - data leakage!
$stmt = $db->prepare("SELECT * FROM students WHERE id = ?");
$stmt->execute([$studentId]);
```

## Super Admin Can't Access Franchise Data

**Issue:** Super admin gets "Access Denied" when trying to view franchise data.

**Solution:** This is expected behavior. Super admins should:
1. Use `/adminpanel/` for system-wide management
2. To view specific franchise data, use impersonation feature (with audit logging)
3. Or temporarily set a franchise_id in session for testing

## Session Variables Not Working

**Issue:** `$_SESSION['user_id']` is empty but user is logged in.

**Solution:** Use session prefix helpers:
```php
// WRONG - Direct access doesn't work with prefix system
$userId = $_SESSION['user_id'];

// CORRECT - Use helpers
$userId = getSession('user_id');
```

## Panel Structure Confusion

**Issue:** Not sure where to put new pages.

**Solution:** Follow three-tier structure:
- **Franchise admin pages** → `/public/` root (dashboard.php, students.php, etc.)
- **Super admin pages** → `/public/adminpanel/`
- **End user pages** → `/public/memberpanel/`

## Database Connection Fails

**Issue:** "Access denied for user" or "Unknown database".

**Solution:** Check `.env` file:
```env
DB_HOST=localhost      # Check host
DB_PORT=3306          # Check port
DB_NAME=saas_seeder   # Database must exist
DB_USER=root          # Check username
DB_PASSWORD=          # Check password
```

Create database if missing:
```sql
CREATE DATABASE saas_seeder
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

## Composer Install Fails

**Issue:** Dependencies not installing.

**Solution:**
1. Check PHP version: `php -v` (need 8.0+)
2. Update composer: `composer self-update`
3. Clear cache: `composer clear-cache`
4. Retry: `composer install`

## File Paths Breaking

**Issue:** "Failed to open stream" errors.

**Solution:** Always use `__DIR__`:
```php
// CORRECT
require_once __DIR__ . '/../src/config/auth.php';
include __DIR__ . "/includes/head.php";

// WRONG - Breaks in different panels
require_once '../src/config/auth.php';
include "./includes/head.php";
```

## Permissions Not Working

**Issue:** User has permission but still gets "Access Denied".

**Solution:**
1. Check permission code matches exactly (case-sensitive)
2. Verify user type (super_admin bypasses all checks)
3. Check franchise_id matches
4. Clear permission cache if using caching
5. Verify permission is assigned to user's role

## Setup Scripts Don't Run

**Issue:** PowerShell scripts fail to execute.

**Solution:**
```powershell
# Enable script execution (run as administrator)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run script
.\setup-database.ps1
```

Or use manual commands from script content.
