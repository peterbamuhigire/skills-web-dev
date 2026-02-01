# SaaS Seeder Bootstrap Workflow

Complete workflow for setting up a new SaaS project from the template.

## Environment Setup

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

## Install Dependencies

```bash
composer install
```

## Database Setup

```bash
# Windows PowerShell
.\setup-database.ps1

# Or manual:
mysql -u root -p < docs/seeder-template/migration.sql
```

## Fix Collations (If Needed)

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

## Create Super Admin

**DO NOT use migration defaults!** Use the dev tool:

1. Start server: `php -S localhost:8000 -t public/`
2. Visit: `http://localhost:8000/super-user-dev.php`
3. Fill form with admin details
4. Click "Create Super Admin"

The tool uses correct Argon2ID hashing that matches login.

## Verify Setup

Test login:
1. Visit: `http://localhost:8000/sign-in.php`
2. Login with created admin credentials
3. Should see beautiful landing page with buttons:
   - "Super Admin Panel" → `/adminpanel/`
   - "Franchise Dashboard" → `/dashboard.php`
   - "Page Template (Skeleton)" → `/skeleton.php`

## Project Customization

After basic setup, customize for your SaaS:

### Update Session Prefix

Edit `src/config/session.php`:
```php
// Change from default
define('SESSION_PREFIX', 'saas_app_');

// To your SaaS-specific prefix
define('SESSION_PREFIX', 'school_');     // School SaaS
define('SESSION_PREFIX', 'restaurant_'); // Restaurant SaaS
define('SESSION_PREFIX', 'clinic_');     // Medical SaaS
```

### Customize User Types

Based on requirements, update database enum:
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

### Update Branding

Replace "SaaS Seeder" throughout:
- `public/index.php` - Landing page title
- `public/includes/topbar.php` - Navbar brand
- README.md - Documentation

### Apply Custom Schema

Run project-specific schema:
```bash
mysql -u root -p saas_seeder < database/schema/core-schema.sql

# If seed data exists
mysql -u root -p saas_seeder < database/schema/seed-data.sql
```

### Update Documentation

- Replace README.md with project-specific content
- Create project-specific CLAUDE.md
- Remove template docs, keep relevant ones
- Reference `docs/project-requirements/` for project details
