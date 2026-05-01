# README File Template

**Back to:** [SKILL.md](../SKILL.md)
**Related:** [update-claude-documentation](../../update-claude-documentation/SKILL.md) (ongoing README maintenance) | [saas-seeder](../../saas-seeder/SKILL.md) (project bootstrap)

## Purpose

Provide the standard introductory document for a software project. The README is the first thing anyone sees when they discover the project -- it must answer "What is this?", "How do I set it up?", and "How do I contribute?" within 5 minutes of reading.

**Audience:** New developers, contributors, evaluators, anyone discovering the project

---

## Template

### Project README (Root)

```markdown
# {Project Name}

{One-line description: what it does and who it is for.}

## Overview

{Product Name} is a {multi-tenant SaaS platform / web application / mobile app}
for {target market, e.g., African businesses}. It provides {key capabilities:
e.g., inventory management, point-of-sale, customer management, and reporting}
through a web dashboard and native Android application.

**Key Features:**
- {Feature 1: e.g., Multi-franchise management with data isolation}
- {Feature 2: e.g., Real-time sales tracking and reporting}
- {Feature 3: e.g., Offline-capable Android companion app}
- {Feature 4: e.g., Role-based access control with granular permissions}

**Architecture:** Three-panel web application with REST API backend and
native Android client. Multi-tenant with row-level data isolation.

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | PHP (strict typing, PSR-12) | 8.x |
| Database | MySQL (utf8mb4_general_ci) | 8.x |
| Web UI | Tabler (Bootstrap 5), SweetAlert2, DataTables, Flatpickr | Latest |
| Mobile | Kotlin + Jetpack Compose (MVVM + Clean Architecture, Hilt DI) | Latest |
| Auth (Web) | PHP Sessions + Argon2ID hashing | -- |
| Auth (Mobile) | JWT (access + refresh tokens) | -- |
| Testing | PHPUnit (PHP), JUnit 5 + MockK (Android) | Latest |

## Architecture

```
┌────────────────────────────────────────────────┐
│                   CLIENTS                       │
│  Browser ──> /public/      (Franchise Admin)   │
│  Browser ──> /adminpanel/  (Super Admin)       │
│  Browser ──> /memberpanel/ (End User Portal)   │
│  Android ──> /api/         (REST API + JWT)    │
└──────────────────┬─────────────────────────────┘
                   │ HTTPS
┌──────────────────▼─────────────────────────────┐
│        PHP 8.x Application (Apache)            │
│   Session auth (web) | JWT auth (mobile/API)   │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│     MySQL 8.x (row-level isolation via          │
│     franchise_id on every tenant table)         │
└────────────────────────────────────────────────┘
```

## Getting Started

### Prerequisites

- **PHP** 8.x with extensions: mysql, mbstring, xml, curl, zip, gd, intl
- **MySQL** 8.x
- **Composer** (PHP dependency manager)
- **Git**
- **Apache** 2.4+ (with mod_rewrite enabled)
- **For Android development:** Android Studio (latest), JDK 17

### Installation (Development - Windows/WAMP)

1. **Clone the repository:**
   git clone {repository-url}
   cd {project-name}

2. **Install PHP dependencies:**
   composer install

3. **Create the database:**
   mysql -u root -p
   CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   EXIT;

4. **Apply database schema:**
   mysql -u root -p {db_name} < database/schema/core-schema.sql
   mysql -u root -p {db_name} < database/schema/seed-data.sql

5. **Configure environment:**
   cp .env.example .env
   # Edit .env with your local database credentials and keys
   # See Configuration section below for all variables

6. **Create super admin user:**
   # Navigate to http://localhost/{project-name}/public/super-user-dev.php
   # Fill in admin details and submit

7. **Verify installation:**
   # Navigate to http://localhost/{project-name}/public/sign-in.php
   # Log in with the super admin credentials you just created
   # Expected: Dashboard loads with navigation to all panels

### Configuration (.env)

| Variable | Description | Dev Default |
|----------|-------------|-------------|
| APP_ENV | Environment | development |
| APP_URL | Base URL | http://localhost/{project} |
| DB_HOST | Database host | localhost |
| DB_NAME | Database name | {project}_dev |
| DB_USER | Database user | root |
| DB_PASS | Database password | {your-password} |
| SESSION_PREFIX | Session key prefix | {project}_ |
| PASSWORD_PEPPER | Argon2ID pepper (64+ chars) | {generate-random} |
| JWT_SECRET | JWT signing key | {generate-random} |

> **WARNING:** Never commit .env files. The .env.example file contains
> placeholder values only. Generate strong random values for all secrets.

### Running Tests

# PHP tests
composer test           # Run PHPUnit/Pest tests
composer stan           # Run PHPStan static analysis
composer cs-fix         # Fix code style (PSR-12)
composer quality        # Run all checks

# Android tests (from android/ directory)
./gradlew test          # Unit tests
./gradlew connectedAndroidTest  # Instrumented tests

## Project Structure

{project-name}/
├── public/                  # Web root (Franchise Admin panel)
│   ├── index.php           # Landing page
│   ├── sign-in.php         # Authentication
│   ├── dashboard.php       # Main dashboard
│   ├── skeleton.php        # Page template (clone for new pages)
│   ├── adminpanel/         # Super Admin panel
│   ├── memberpanel/        # End User portal
│   ├── api/                # REST API endpoints (JWT auth)
│   └── assets/             # CSS, JS, images
├── src/                     # PHP source code
│   ├── config/             # Configuration (auth, session, database)
│   ├── Auth/               # Authentication services
│   ├── Services/           # Business logic services
│   └── Helpers/            # Utility functions
├── database/
│   ├── schema/             # Database schema files
│   ├── migrations/         # Migration files (YYYY-MM-DD-description.sql)
│   └── migrations-production/  # Production-only migrations (non-destructive)
├── docs/                    # Project documentation
│   ├── planning/           # SDLC planning documents
│   ├── design/             # SDLC design documents
│   └── plans/              # Feature plans and INDEX.md
├── tests/                   # Test files
├── uploads/                 # User-uploaded files
├── manuals/                 # End-user manual files
├── .env.example            # Environment template
├── composer.json           # PHP dependencies
├── CLAUDE.md               # AI development guide
└── README.md               # This file

## Multi-Tenant Architecture

This application uses **row-level tenant isolation**:
- Every tenant-scoped table has a `franchise_id` column
- Every query includes `WHERE franchise_id = ?`
- The three-panel structure separates concerns:
  - `/public/` -- Franchise Admin (primary workspace)
  - `/adminpanel/` -- Super Admin (system-wide management)
  - `/memberpanel/` -- End User (self-service portal)

## API Documentation

API endpoints are available at `/api/v1/`. Authentication uses JWT tokens.

**Quick reference:**
- `POST /api/v1/auth/login` -- Get access + refresh tokens
- `POST /api/v1/auth/refresh` -- Refresh access token
- `GET /api/v1/{resource}` -- List resources (paginated)
- `POST /api/v1/{resource}` -- Create resource

See `docs/design/05-api-documentation.md` for complete API reference.

## Deployment

| Environment | OS | URL |
|-------------|-----|-----|
| Development | Windows 11 (WAMP) | http://localhost/{project} |
| Staging | Ubuntu 22.04 LTS | https://staging.{domain} |
| Production | Debian 12 | https://{domain} |

See `docs/user-deploy/02-operations-deployment-manual.md` for full deployment guide.

## Contributing

### Branch Naming
- `feature/{description}` -- New features
- `fix/{description}` -- Bug fixes
- `hotfix/{description}` -- Emergency production fixes

### Commit Conventions
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `refactor:` Code restructuring
- `test:` Adding/updating tests

### Pull Request Process
1. Create feature branch from `main`
2. Write tests first (TDD: Red-Green-Refactor)
3. Run `composer quality` before committing
4. Open PR with description of changes
5. Await code review and CI checks
6. Merge after approval

## License

{License type, e.g., Proprietary / MIT / Apache 2.0}

## Support

- **Bug reports:** {issue tracker URL or email}
- **Feature requests:** {process description}
- **Documentation:** See `docs/` directory
- **Contact:** {support email or channel}
```

---

## README Variants

### Module README (Subdirectory)

For subdirectories that benefit from their own README:

```markdown
# {Module Name}

## Purpose
{What this module does and how it fits into the overall system.}

## Key Files
| File | Purpose |
|------|---------|
| {file.php} | {Description} |

## Local Development
{Any module-specific setup steps.}

## Patterns Used
- {Pattern 1: e.g., Repository pattern for data access}
- {Pattern 2: e.g., Service layer for business logic}

## Related Modules
- [{Related Module}](../{related-module}/) -- {Relationship}
```

### Android Project README

Additional sections for the Android project:

```markdown
## Android Setup

### Requirements
- Android Studio {version}+ (Ladybug or newer)
- JDK 17
- Android SDK: compileSdk 35, minSdk 29, targetSdk 35

### Build Variants
| Variant | API URL | Signing |
|---------|---------|---------|
| dev | http://{LAN-IP}:8000/api | Debug key |
| staging | https://staging.{domain}/api | Release key |
| prod | https://{domain}/api | Release key |

### Local API Connection
1. Find your computer's LAN IP: ipconfig (Windows) / ifconfig (Mac/Linux)
2. Update `local.properties`: `api.base.url=http://{LAN-IP}:8000/api/v1/`
3. Ensure phone and computer are on the same WiFi network

### Emulator Setup
1. Create a Pixel 6 emulator with API 34
2. Configure: 4 GB RAM, 2 GB internal storage
3. For local API: use http://10.0.2.2:8000/api/v1/ (emulator loopback)

### Running Tests
./gradlew test                       # Unit tests
./gradlew connectedAndroidTest       # Instrumented tests
./gradlew jacocoTestReport           # Coverage report

### Play Store Deployment
See `docs/user-deploy/02-operations-deployment-manual.md` (Android section)
and the `google-play-store-review` skill for compliance checklist.
```

### API README

For the API subdirectory:

```markdown
# API Reference

## Base URL
- Dev: http://localhost/{project}/api/v1/
- Staging: https://staging.{domain}/api/v1/
- Production: https://{domain}/api/v1/

## Authentication
All endpoints require JWT Bearer token except /auth/login and /auth/refresh.

## Testing
# Get token
curl -X POST {base}/auth/login -d '{"email":"test@example.com","password":"pass"}'

# Use token
curl -H "Authorization: Bearer {token}" {base}/resource

## Full Documentation
See docs/design/05-api-documentation.md
```

---

## Writing Guidelines

- **Start with what, not how** -- describe purpose before installation
- **Assume nothing** -- the reader may have never seen this project
- **Copy-pasteable commands** -- every command works when pasted directly
- **Show expected output** -- so the reader knows it worked
- **Keep it updated** -- stale READMEs erode trust faster than no README
- **Link, do not duplicate** -- reference detailed docs instead of copying content

## Multi-Tenant SaaS Specifics

- Explain the three-panel architecture (public, adminpanel, memberpanel)
- Document the `franchise_id` isolation requirement prominently
- Include environment-specific configuration for all 3 environments
- Dev credentials: include in README with a prominent warning banner
- Never include production credentials anywhere in the repository

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| No installation steps | New devs cannot get started | Write complete step-by-step setup |
| Outdated information | Devs follow wrong steps, waste hours | Update README with each significant change |
| Missing prerequisites | Setup fails with cryptic errors | List every required tool with version |
| No project structure | Devs cannot find anything | Include annotated directory tree |
| Wall of text, no structure | Nobody reads it | Use headers, tables, code blocks |
| Production credentials in README | Security breach | Only dev/example credentials with warnings |

## Quality Checklist

- [ ] One-line description answers "What does this do?"
- [ ] Overview covers what, who, and key capabilities
- [ ] Tech stack table with versions is current
- [ ] Architecture diagram (ASCII) shows system components
- [ ] Prerequisites list every required tool with version
- [ ] Installation steps are copy-pasteable and tested on a clean machine
- [ ] Configuration documents every .env variable
- [ ] Test commands and expected output documented
- [ ] Project structure with file/directory descriptions
- [ ] Multi-tenant architecture explained (franchise_id, three panels)
- [ ] Deployment environments table with URLs
- [ ] Contributing guide with branch naming and commit conventions
- [ ] No production credentials or secrets in the file
- [ ] Links to detailed docs (API, deployment, design) are correct
- [ ] Document stays under 500 lines (split into sub-files if needed)

---

**Back to:** [SKILL.md](../SKILL.md)
