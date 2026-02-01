---
name: saas-seeder
description: "Bootstrap a new SaaS from the SaaS Seeder Template: setup database, configure environment, create super admin user, and verify three-tier panel structure. Use when initializing a new multi-tenant SaaS project from this template."
---

# SaaS Seeder Template Bootstrap

Bootstrap a new multi-tenant SaaS project using the SaaS Seeder Template with proper three-tier panel architecture, Argon2ID authentication, and franchise isolation.

## When to Use

Use when the user says:
- "Using the seeder-script skill, prepare this repository for [SaaS name]"
- "Bootstrap a new SaaS from this template"
- "Initialize the SaaS Seeder Template"
- "Setup database for new SaaS project"

## Critical Architecture Standards

### Three-Tier Panel Structure

**This is the CORE architectural concept:**

1. **`/public/adminpanel/`** - Super Admin Panel
   - System-wide management
   - Multi-franchise oversight
   - User type: `super_admin`

2. **`/public/` (root)** - Franchise Admin Panel
   - Single franchise management (THE MAIN WORKSPACE)
   - Files: `dashboard.php`, `skeleton.php` (template)
   - User types: `owner`, `staff`

3. **`/public/memberpanel/`** - End User Portal
   - Self-service for end users
   - User types: `member`, `student`, `customer`, `patient`

**Key Principle:** `/public/` root is NOT a redirect router - it's the franchise admin workspace!

### Session Prefix System

**All session variables use a prefix:**
```php
define('SESSION_PREFIX', 'saas_app_'); // Change per SaaS

// ALWAYS use helpers
setSession('user_id', 123);        // Sets $_SESSION['saas_app_user_id']
$userId = getSession('user_id');   // Gets $_SESSION['saas_app_user_id']
hasSession('user_id');             // Checks if exists
```

### Password Hashing

**Uses Argon2ID (NOT bcrypt):**
```
Algorithm: Argon2ID + salt + pepper
Hash: salt(32 chars) + Argon2ID(HMAC-SHA256(password, pepper) + salt)
```

**CRITICAL:** Use `super-user-dev.php` to create admin users, NOT migration defaults!

## Required Files And Paths

- `docs/seeder-template/migration.sql` - Core auth/RBAC schema
- `docs/seeder-template/fix-collation-and-create-franchises.sql` - Collation fixes + franchises table
- `public/` - Web root
- `public/super-user-dev.php` - Super admin creator (DEV ONLY)
- `public/dashboard.php` - Franchise admin dashboard
- `public/skeleton.php` - Page template
- `.env` - Environment configuration

## Standard Workflow

### 1. Environment Setup

Ask user for:
- Database credentials (host, port, name, user, password)
- Cookie domain (e.g., `localhost` or production domain)
- Cookie encryption key (32+ random chars)
- Password pepper (64+ random chars)
- App environment (`development` or `production`)

Create/update `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=saas_seeder
DB_USER=root
DB_PASSWORD=

COOKIE_DOMAIN=localhost
COOKIE_ENCRYPTION_KEY=your-32-char-key
PASSWORD_PEPPER=your-64-char-pepper

APP_ENV=development
JWT_SECRET_KEY=
```

### 2. Install Dependencies

```bash
composer install
```

### 3. Database Setup

```bash
# Windows PowerShell
.\setup-database.ps1

# Or manual:
mysql -u root -p < docs/seeder-template/migration.sql
```

### 4. Fix Collations (If Needed)

```bash
# Windows PowerShell
.\fix-database.ps1

# Or manual:
mysql -u root -p saas_seeder < docs/seeder-template/fix-collation-and-create-franchises.sql
```

This script:
- Fixes collation mismatches (utf8mb4_unicode_ci)
- Creates `tbl_franchises` table
- Creates default "system" franchise
- Updates stored procedures

### 5. Create Super Admin

**DO NOT use migration defaults!** Use the dev tool:

1. Start server: `php -S localhost:8000 -t public/`
2. Visit: `http://localhost:8000/super-user-dev.php`
3. Fill form with admin details
4. Click "Create Super Admin"

The tool uses correct Argon2ID hashing that matches login.

### 6. Verify Setup

Test login:
1. Visit: `http://localhost:8000/sign-in.php`
2. Login with created admin credentials
3. Should see beautiful landing page with two buttons:
   - "Super Admin Panel" → `/adminpanel/`
   - "Franchise Dashboard" → `/dashboard.php`
   - "Page Template (Skeleton)" → `/skeleton.php`

### 7. First-Time Configuration

**Update session prefix (IMPORTANT):**

Edit `src/config/session.php`:
```php
// Change from default
define('SESSION_PREFIX', 'saas_app_');

// To your SaaS-specific prefix
define('SESSION_PREFIX', 'school_');     // School SaaS
define('SESSION_PREFIX', 'restaurant_'); // Restaurant SaaS
define('SESSION_PREFIX', 'clinic_');     // Medical SaaS
```

**Customize user types (if needed):**

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

## Seeding Rules

### User Types

- `super_admin` - Platform operators (franchise_id CAN be NULL)
- `owner` - Franchise owners (franchise_id REQUIRED)
- `staff` - Franchise staff with permissions (franchise_id REQUIRED)
- Custom types - End users (franchise_id REQUIRED)

### Franchise Data

**ALWAYS filter by franchise_id:**
```php
// CORRECT
$stmt = $db->prepare("SELECT * FROM students WHERE franchise_id = ?");
$stmt->execute([getSession('franchise_id')]);

// WRONG - data leakage!
$stmt = $db->prepare("SELECT * FROM students");
```

### Permission Codes

- Uppercase with underscores
- Format: `RESOURCE_ACTION`
- Examples: `INVOICE_CREATE`, `STUDENT_DELETE`, `REPORT_VIEW`

## Common Customizations

### 1. Rename Branding

Replace "SaaS Seeder" throughout:
- `public/index.php` - Landing page title
- `public/includes/topbar.php` - Navbar brand
- README.md - Documentation

### 2. Add Custom Features

Create pages in `/public/` using `skeleton.php` as template:

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

### 3. Extend Franchises Table

Add custom fields to `tbl_franchises`:
```sql
ALTER TABLE tbl_franchises
  ADD COLUMN school_type ENUM('primary','secondary','university'),
  ADD COLUMN student_capacity INT,
  ADD COLUMN academic_year VARCHAR(20);
```

## Security Checklist Before Production

- [ ] Remove `super-user-dev.php` or restrict access
- [ ] Change `SESSION_PREFIX` from `saas_app_`
- [ ] Set strong `PASSWORD_PEPPER` (64+ chars)
- [ ] Set strong `COOKIE_ENCRYPTION_KEY` (32+ chars)
- [ ] Set `APP_ENV=production`
- [ ] Enable HTTPS (session cookies require it)
- [ ] Review all queries for franchise_id filtering
- [ ] Set proper file permissions on `.env` (600)

## Troubleshooting

### Session Not Persisting

**Issue:** Login successful but redirects back to login.

**Solution:** Session cookie secure flag. Already handled:
```php
// Automatically disabled on HTTP (localhost)
$isHttps = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
           || $_SERVER['SERVER_PORT'] == 443;
ini_set('session.cookie_secure', $isHttps ? '1' : '0');
```

### Password Mismatch

**Issue:** Can't login after creating user.

**Solution:** Use `super-user-dev.php` NOT manual password_hash():
```php
// CORRECT (super-user-dev.php does this)
$passwordHelper = new PasswordHelper();
$hash = $passwordHelper->hashPassword($password);

// WRONG - won't match login!
$hash = password_hash($password, PASSWORD_BCRYPT);
```

### Collation Errors

**Issue:** "Illegal mix of collations" errors.

**Solution:** Run `fix-database.ps1`:
```bash
.\fix-database.ps1
```

### Missing Franchises Table

**Issue:** "Table 'tbl_franchises' doesn't exist".

**Solution:** Run fix script (includes franchises table creation).

## File Structure After Setup

```
saas-seeder/
├── public/
│   ├── index.php           # Landing page with nav buttons
│   ├── sign-in.php         # Login with SweetAlert
│   ├── super-user-dev.php  # Super admin creator (REMOVE IN PROD)
│   ├── dashboard.php       # Franchise admin dashboard
│   ├── skeleton.php        # Page template
│   ├── adminpanel/         # Super admin panel
│   ├── memberpanel/        # End user portal
│   └── assets/             # Shared CSS/JS
├── src/
│   ├── config/
│   │   ├── auth.php        # Auth functions + automatic access control
│   │   ├── session.php     # Session prefix helpers
│   │   └── database.php    # Database connection
│   └── Auth/               # Auth services, helpers, DTOs
├── docs/
│   └── seeder-template/
│       ├── migration.sql                            # Core schema
│       └── fix-collation-and-create-franchises.sql  # Fixes
├── .env                    # Environment config
├── composer.json           # Dependencies
├── setup-database.ps1      # Setup script
├── fix-database.ps1        # Fix script
└── CLAUDE.md               # Development guide
```

## Output After Completion

Report to user:
```
✅ SaaS Seeder Template Ready!

Database: [name] created and configured
Franchises: tbl_franchises table created
Super Admin: Create at http://localhost:8000/super-user-dev.php
Login: http://localhost:8000/sign-in.php

Next Steps:
1. Visit super-user-dev.php to create admin user
2. Login and explore three-tier panel structure
3. Customize SESSION_PREFIX in src/config/session.php
4. Start building your franchise management features!

Documentation:
- README.md - Quick start
- docs/PANEL-STRUCTURE.md - Three-tier architecture
- CLAUDE.md - Development guide
```

## References

See:
- `../multi-tenant-saas-architecture/` - Multi-tenant patterns
- `../dual-auth-rbac/` - Authentication & RBAC
- `../../docs/PANEL-STRUCTURE.md` - Complete three-tier guide
- `../../CLAUDE.md` - Development guidelines
