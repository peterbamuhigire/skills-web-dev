# SaaS Seeder Architecture Standards

Core architectural concepts and patterns.

## Three-Tier Panel Structure

**THIS IS THE CORE ARCHITECTURAL CONCEPT:**

### 1. `/public/` (root) - Franchise Admin Panel (THE MAIN WORKSPACE)

- Single franchise management workspace
- Files: `dashboard.php`, `skeleton.php` (template)
- User types: `owner`, `staff`
- Purpose: Daily franchise operations

**Key Principle:** `/public/` root is NOT a redirect router - it's the franchise admin workspace!

### 2. `/public/adminpanel/` - Super Admin Panel

- System-wide management
- Multi-franchise oversight
- User type: `super_admin`
- Purpose: Platform operator managing multiple franchises

### 3. `/public/memberpanel/` - End User Portal

- Self-service for end users
- User types: `member`, `student`, `customer`, `patient` (customizable)
- Purpose: End user self-service features

## Session Prefix System

**CRITICAL:** All session variables use a prefix for multi-tenant isolation.

```php
// Define prefix per SaaS app
define('SESSION_PREFIX', 'saas_app_'); // Change per SaaS

// ALWAYS use helpers
setSession('user_id', 123);        // Sets $_SESSION['saas_app_user_id']
$userId = getSession('user_id');   // Gets $_SESSION['saas_app_user_id']
hasSession('user_id');             // Checks if exists
```

**Why?**
- Multiple SaaS apps on same domain won't collide
- Clear namespace per application
- Prevents accidental session variable conflicts

**Customize per SaaS:**
```php
define('SESSION_PREFIX', 'school_');     // School SaaS
define('SESSION_PREFIX', 'restaurant_'); // Restaurant SaaS
define('SESSION_PREFIX', 'clinic_');     // Medical SaaS
```

## Password Hashing

**Algorithm:** Argon2ID + Salt + Pepper (NOT bcrypt)

```
Hash Flow:
1. Random salt (32 bytes)
2. HMAC-SHA256(password, pepper) + salt
3. Argon2ID hash
4. Store: salt(32 chars) + hash
```

**CRITICAL: Admin User Creation**
- NEVER use manual password_hash() or migration defaults
- ALWAYS use dedicated tool like `super-user-dev.php`
- Uses PasswordHelper with correct Argon2ID matching login

## Multi-Tenant Isolation

### User Types & Franchise Requirements

```
super_admin - Platform operators (franchise_id CAN be NULL)
owner       - Franchise owners (franchise_id REQUIRED, NOT NULL)
staff       - Franchise staff (franchise_id REQUIRED, NOT NULL)
member      - End users: student, customer, patient (franchise_id REQUIRED, NOT NULL)
```

### Database-Level Isolation

**ALL franchise-scoped queries MUST filter by franchise_id:**

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

**Database Schema Requirements:**
- All franchise-scoped tables have `franchise_id BIGINT UNSIGNED NOT NULL`
- Foreign key to `tbl_franchises`
- Index on `franchise_id`
- Composite indexes include `franchise_id` as first column
- Collation: `utf8mb4_unicode_ci`

### Permission Codes

- Uppercase with underscores
- Format: `RESOURCE_ACTION`
- Examples: `INVOICE_CREATE`, `STUDENT_DELETE`, `REPORT_VIEW`

## File Structure Convention

```
public/
├── index.php           # Landing page with nav buttons (NOT a router)
├── sign-in.php         # Login with SweetAlert
├── dashboard.php       # Franchise admin dashboard
├── skeleton.php        # Page template
├── adminpanel/         # Super admin panel
│   ├── index.php
│   └── includes/       # Admin-specific includes
├── memberpanel/        # End user portal
│   ├── index.php
│   └── includes/       # Member-specific includes
├── includes/           # Shared includes for /public/ root
├── assets/             # Shared CSS/JS
└── uploads/            # File uploads
```

## Security Standards

### HTTPS Auto-Detection

Critical for localhost development:
```php
// Only set secure cookie if using HTTPS
$isHttps = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
           || $_SERVER['SERVER_PORT'] == 443;
ini_set('session.cookie_secure', $isHttps ? '1' : '0');

// Without this, sessions won't persist on localhost HTTP
```

### Before Production

- [ ] Remove `super-user-dev.php` or restrict access
- [ ] Change `SESSION_PREFIX` from `saas_app_`
- [ ] Set strong `PASSWORD_PEPPER` (64+ chars)
- [ ] Set strong `COOKIE_ENCRYPTION_KEY` (32+ chars)
- [ ] Set `APP_ENV=production`
- [ ] Enable HTTPS (session cookies require it)
- [ ] Review all queries for franchise_id filtering
- [ ] Set proper file permissions on `.env` (600)

## Required Environment Variables

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=saas_seeder
DB_USER=root
DB_PASSWORD=

COOKIE_DOMAIN=localhost
COOKIE_ENCRYPTION_KEY=your-32-char-key  # 32+ chars
PASSWORD_PEPPER=your-64-char-pepper      # 64+ chars recommended

APP_ENV=development
JWT_SECRET_KEY=
```

## Seeding Rules

### Franchise Data

**ALWAYS filter by franchise_id:**
```php
// CORRECT
$stmt = $db->prepare("SELECT * FROM students WHERE franchise_id = ?");
$stmt->execute([getSession('franchise_id')]);

// WRONG - data leakage!
$stmt = $db->prepare("SELECT * FROM students");
```

### Creating New Pages

Use `skeleton.php` as template:
```php
<?php
require_once __DIR__ . '/../src/config/auth.php';
requireAuth();

$pageTitle = 'Students';
$panel = 'admin';
$franchiseId = getSession('franchise_id');
?>
<!doctype html>
<html lang="en">
<head>
    <?php include __DIR__ . "/includes/head.php"; ?>
</head>
<body>
    <?php include __DIR__ . "/includes/topbar.php"; ?>
    <!-- Your content here -->
    <?php include __DIR__ . "/includes/footer.php"; ?>
</body>
</html>
```

## Common Customizations

### 1. Rename Branding

Replace "SaaS Seeder" throughout:
- `public/index.php` - Landing page title
- `public/includes/topbar.php` - Navbar brand
- README.md - Documentation

### 2. Extend Franchises Table

Add custom fields:
```sql
ALTER TABLE tbl_franchises
  ADD COLUMN school_type ENUM('primary','secondary','university'),
  ADD COLUMN student_capacity INT,
  ADD COLUMN academic_year VARCHAR(20);
```

### 3. Add Custom User Types

Edit database enum:
```sql
ALTER TABLE tbl_users MODIFY user_type ENUM(
  'super_admin',
  'owner',
  'staff',
  'student',    -- For school SaaS
  'customer',   -- For restaurant SaaS
  'patient'     -- For medical SaaS
) NOT NULL DEFAULT 'staff';
```
