# Software Configuration Management Plan (SCMP) — Template & Guide

**Back to:** [SDLC Planning Skill](../SKILL.md)

## Purpose

Defines **how changes to software, documents, and configurations are managed** throughout the project lifecycle. Ensures reproducibility, traceability, and controlled change processes.

## Audience

DevOps engineers, development leads, release managers, QA team.

## When to Create

After the SDP is drafted. The SCMP operationalizes the source control and deployment strategy outlined in the SDP.

---

## Template

```markdown
# [Project Name] — Software Configuration Management Plan

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**References:** [Link to SDP], [Link to QA Plan]

---

## 1. Introduction

### 1.1 Purpose
This document defines how configuration items (code, documents, configurations,
databases, environments) are identified, controlled, versioned, and audited
throughout the project lifecycle.

### 1.2 Scope
Covers all software artifacts, infrastructure configurations, and documentation
for [Project Name] across development, staging, and production environments.

## 2. Configuration Items (CI) Inventory

### 2.1 CI Categories

| Category | Examples | Storage | Versioning |
|----------|----------|---------|------------|
| Source Code (PHP) | Controllers, models, services | GitHub repo | Git |
| Source Code (Kotlin) | ViewModels, composables, repos | GitHub repo | Git |
| Database Schema | Tables, stored procedures, triggers | `database/schema/` | Git + migration scripts |
| Database Migrations | Production migration scripts | `database/migrations-production/` | Git (idempotent) |
| Configuration Files | `.env`, `php.ini`, Apache config | Per environment | Template in Git, values in env |
| Documentation | Plans, specs, manuals, CLAUDE.md | `docs/` | Git |
| Build Artifacts | APK/AAB, compiled PHP packages | CI/CD pipeline | Versioned by build number |
| Infrastructure | Server configs, SSL certs, DNS | Server + docs | Documented in Git |
| Third-Party Libs | Composer packages, Gradle deps | `composer.json`, `build.gradle` | Lock files in Git |
| Test Data | Fixtures, seed scripts | `database/seeds/` | Git |

### 2.2 CI Identification Scheme

| CI Type | ID Format | Example |
|---------|-----------|---------|
| Source file | Path-based | `app/Controllers/UserController.php` |
| Database object | `DB-[TYPE]-[NAME]` | `DB-TABLE-users`, `DB-SP-sp_get_dashboard` |
| Document | `DOC-[CATEGORY]-[NAME]` | `DOC-PLAN-sdp`, `DOC-SRS-v1.0` |
| Config | `CFG-[ENV]-[NAME]` | `CFG-PROD-env`, `CFG-DEV-apache` |

## 3. Version Control Strategy

### 3.1 Repository Structure
| Repository | Contents | Platform |
|-----------|----------|----------|
| `[project-name]-backend` | PHP API, database, web UI | GitHub |
| `[project-name]-android` | Kotlin/Compose app | GitHub |
| `[project-name]-docs` | Planning & governance docs (optional) | GitHub |

### 3.2 Branching Model

| Branch | Purpose | Lifetime | Protection |
|--------|---------|----------|------------|
| `main` | Production-ready code | Permanent | PR required, 2 reviewers |
| `develop` | Integration branch | Permanent | PR required, 1 reviewer |
| `feature/[ID]-[name]` | New feature development | Temporary | Deleted after merge |
| `bugfix/[ID]-[name]` | Bug fixes | Temporary | Deleted after merge |
| `hotfix/[ID]-[name]` | Critical prod fixes | Temporary | Merged to main + develop |
| `release/[version]` | Release preparation | Temporary | Freeze: only bug fixes |

### 3.3 Commit Message Format
```
type(scope): brief description

[Optional body: what and why, not how]

[Optional footer: issue references]
```

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`
**Scope:** Module or component name (e.g., `auth`, `inventory`, `dashboard`)

### 3.4 Tagging & Releases
- **Format:** Semantic versioning `vMAJOR.MINOR.PATCH` (e.g., `v1.2.3`)
- **When to tag:** After merge to `main` and successful production deployment
- **Android:** Also uses `versionCode` (integer) for Play Store

## 4. Change Control Process

### 4.1 Change Request Flow

```
Developer submits PR
    |
    v
Code Review (1-2 reviewers)
    |
    v
Automated CI checks (lint, tests, build)
    |
    v
Reviewer approves / requests changes
    |
    v
Merge to target branch
    |
    v
Deployment (automated or manual per environment)
```

### 4.2 Change Categories

| Category | Approval Required | Examples |
|----------|------------------|---------|
| Standard | 1 reviewer | Feature additions, bug fixes, refactoring |
| Significant | 2 reviewers + PM | Database schema changes, API breaking changes |
| Emergency | 1 reviewer (retroactive) | Hotfix for production outage |
| Configuration | DevOps + PM | Environment variable changes, server config |

### 4.3 Database Change Control
- **Schema changes** require migration script in `database/migrations-production/`
- **All migrations MUST be idempotent** (safe to run multiple times)
- **Stored procedure changes** require review by tech lead
- **No direct production DB edits** — all changes through migration scripts
- **Reference:** `mysql-best-practices` skill for migration checklist

## 5. Build Management

### 5.1 PHP Backend
| Aspect | Approach |
|--------|----------|
| Build tool | Manual deployment (no compilation) |
| Dependency mgmt | Composer (`composer.json` + `composer.lock`) |
| Syntax check | `php -l` on all changed files before deployment |
| Config | `.env` file per environment (not in Git) |

### 5.2 Android App
| Aspect | Approach |
|--------|----------|
| Build tool | Gradle with Kotlin DSL |
| Build variants | `dev`, `staging`, `prod` (flavor-based API URLs) |
| Signing | Keystore (never committed to Git) |
| Artifact | Debug APK (dev), Signed AAB (prod/Play Store) |
| ProGuard | Enabled for release builds |

### 5.3 CI/CD Pipeline
| Stage | Trigger | Actions | Artifact |
|-------|---------|---------|----------|
| Lint | Push to any branch | PHP syntax, Kotlin lint, markdown lint | Report |
| Test | PR opened/updated | Unit tests, integration tests | Test report |
| Build | PR to `develop` | Full build (PHP check + Gradle build) | Build artifact |
| Deploy Staging | Merge to `develop` | Deploy to Ubuntu staging | Deployed app |
| Deploy Prod | Merge to `main` | Deploy to Debian production | Release |

## 6. Release Management

### 6.1 Release Process
1. Create `release/vX.Y.Z` branch from `develop`
2. Freeze: only bug fixes, no new features
3. Run full regression test suite
4. Update version numbers, changelog
5. Merge to `main` and tag `vX.Y.Z`
6. Deploy to production
7. Merge `release` branch back to `develop`
8. Delete `release` branch

### 6.2 Versioning Scheme
| Component | Format | Example |
|-----------|--------|---------|
| Backend | `vMAJOR.MINOR.PATCH` | `v2.1.0` |
| Android | `vMAJOR.MINOR.PATCH` + `versionCode` | `v1.3.0 (build 15)` |
| Database | Migration sequence number | `migration-2026-02-20-001.sql` |
| API | URL path version (if needed) | `/api/v1/`, `/api/v2/` |

## 7. Environment Configuration

### 7.1 Environment Matrix

| Setting | Development | Staging | Production |
|---------|------------|---------|------------|
| OS | Windows 11 | Ubuntu VPS | Debian VPS |
| DEBUG | true | true | false |
| DB Host | localhost | staging-db | prod-db |
| HTTPS | No | Yes | Yes |
| Error Display | On | On | Off (logged) |
| Mail | Mailtrap/log | Test SMTP | Production SMTP |

### 7.2 Secrets Management
- **Never commit:** `.env`, keystores, API keys, passwords
- **Git-ignored:** `.env`, `*.keystore`, `*.jks`, `google-services.json`
- **Template provided:** `.env.example` with placeholder values
- **Android secrets:** `local.properties` for API keys (git-ignored)
- **Encrypted storage:** EncryptedSharedPreferences for mobile tokens

### 7.3 .env Template
```env
# Application
APP_NAME=ProjectName
APP_ENV=development|staging|production
APP_DEBUG=true|false
APP_URL=http://localhost

# Database
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=project_db
DB_USERNAME=root
DB_PASSWORD=

# JWT
JWT_SECRET=your-jwt-secret-here
JWT_EXPIRY=3600
JWT_REFRESH_EXPIRY=604800

# External Services
SMS_API_KEY=
PAYMENT_GATEWAY_KEY=
```

## 8. Database Migration Strategy

### 8.1 Migration File Naming
Format: `migration-YYYY-MM-DD-NNN-description.sql`
Example: `migration-2026-02-20-001-add-pos-sessions-table.sql`

### 8.2 Migration Rules
- Every migration MUST be idempotent (use `IF NOT EXISTS`, `IF EXISTS`)
- Include rollback section (commented out, for reference)
- Test on staging before production
- Back up production database before running migrations
- Log migration execution: `INSERT INTO migration_log (...)`

### 8.3 Stored Procedure Changes
- Store in `database/schema/stored-procedures/`
- Use `DROP PROCEDURE IF EXISTS` + `CREATE PROCEDURE` pattern
- Version procedures in Git alongside code changes

## 9. Audit Trail

### 9.1 What Gets Logged
| Event | Log Location | Retention |
|-------|-------------|-----------|
| Code changes | Git history | Permanent |
| Deployments | CI/CD logs + deployment log | 12 months |
| DB migrations | `migration_log` table | Permanent |
| Config changes | Git history + change log | Permanent |
| Access changes | Application audit table | Per compliance req |

### 9.2 Change Log
Maintain `CHANGELOG.md` in repository root, updated with each release.
Format: [Keep a Changelog](https://keepachangelog.com/) convention.

## 10. Tools & Infrastructure

| Tool | Purpose | URL/Location |
|------|---------|-------------|
| Git | Version control | Installed locally |
| GitHub | Repository hosting, PRs, Issues | github.com/[org] |
| GitHub Actions | CI/CD pipeline | `.github/workflows/` |
| Composer | PHP dependency management | `composer.json` |
| Gradle | Android build system | `build.gradle.kts` |
| MySQL Workbench | Database management | Local tool |
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No branching strategy | Merge conflicts, broken production | Define and enforce branching model |
| Direct production DB edits | Untracked changes, no rollback | All changes through migration scripts |
| Secrets in Git | Security breach | Use `.env` files, add to `.gitignore` |
| No idempotent migrations | Migrations fail on re-run | Always use `IF NOT EXISTS` / `IF EXISTS` |
| Skipping staging deployment | Bugs reach production | Always deploy to staging first |
| No build artifacts versioning | Cannot reproduce specific releases | Tag releases with semantic versioning |
| Missing `.env.example` | New developers cannot set up environment | Maintain template with placeholder values |

## Quality Checklist

- [ ] All configuration item categories identified and inventoried
- [ ] Branching model defined with protection rules
- [ ] Commit message format documented and enforced
- [ ] Change control process covers standard, significant, and emergency changes
- [ ] Database migration strategy is idempotent and documented
- [ ] All 3 environments documented with their differences
- [ ] Secrets management plan ensures no secrets in Git
- [ ] `.env.example` provided with placeholder values
- [ ] CI/CD pipeline stages defined with triggers and artifacts
- [ ] Release process is step-by-step with versioning scheme
- [ ] Audit trail covers code, deployments, migrations, and configs
- [ ] Tools and infrastructure listed with their purposes
- [ ] Document stays under 500 lines

---

**Back to:** [SDLC Planning Skill](../SKILL.md)
**Previous:** [Software Development Plan](software-development-plan.md)
**Next:** [Quality Assurance Plan](quality-assurance-plan.md)
