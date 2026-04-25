# Release Notes Template

**Back to:** [SKILL.md](../SKILL.md)
**Related:** [google-play-store-review](../../google-play-store-review/SKILL.md) (Play Store "What's New") | [update-claude-documentation](../../update-claude-documentation/SKILL.md) (project doc updates)

## Purpose

Communicate what changed in each software version to all stakeholders. Release notes serve as the single source of truth for what shipped, what broke, and how to upgrade.

**Audience:** All stakeholders -- end users, admins, developers, management

---

## Template

### 1. Release Notes Format

```markdown
# Release Notes -- v{VERSION}

| Field | Value |
|-------|-------|
| Version | {MAJOR.MINOR.PATCH} |
| Release Date | {YYYY-MM-DD} |
| Release Type | {Major / Minor / Patch / Hotfix} |
| Platform | {Web / Android / Backend API / All} |
| Android versionCode | {integer, if applicable} |
```

### 2. Version Numbering Strategy

**Semantic Versioning (MAJOR.MINOR.PATCH)**

| Component | Increment When | Example |
|-----------|---------------|---------|
| MAJOR | Breaking changes, major feature overhauls | 1.0.0 to 2.0.0 |
| MINOR | New features, non-breaking enhancements | 1.0.0 to 1.1.0 |
| PATCH | Bug fixes, security patches, minor tweaks | 1.0.0 to 1.0.1 |
| HOTFIX | Emergency production fix (treated as patch) | 1.0.1 to 1.0.2 |

**Platform Versioning:**

| Platform | Version Format | Notes |
|----------|---------------|-------|
| Web application | v1.2.3 | Semantic versioning |
| Backend API | v1.2.3 (with API version prefix, e.g., /api/v1/) | API version may differ |
| Android app | v1.2.3 (display) + versionCode 10203 (integer) | versionCode always increments |

**Android versionCode formula:** `MAJOR * 10000 + MINOR * 100 + PATCH`
Example: v1.2.3 = 10203, v2.0.0 = 20000

### 3. Release Notes Template (Full)

```markdown
# Release Notes -- v{VERSION}

**Release Date:** {YYYY-MM-DD}
**Type:** {Major | Minor | Patch | Hotfix}
**Platform:** {Web | Android | API | All}

## Highlights

{1-3 sentence summary of the most important changes in this release.
Lead with the user-facing impact, not the technical implementation.}

## New Features

- **{Feature Name}** -- {Brief description of what it does and why it matters}
  ({Module: e.g., Sales, Inventory, Reports})
- **{Feature Name}** -- {Description} ({Module})

## Improvements

- **{Improvement}** -- {What changed and how it benefits users} ({Module})
- **{Improvement}** -- {Description} ({Module})

## Bug Fixes

- **{Bug Title}** -- {What was broken and how it is now fixed}
  ({Module}) [#{issue-number}]
- **{Bug Title}** -- {Description} ({Module}) [#{issue-number}]

## Security Updates

- {Security improvement description -- specific enough to inform,
  vague enough to not expose attack vectors}

## Breaking Changes

- **{Change}** -- {What broke, why it was necessary, and migration steps}
  - **Before:** {old behavior or API signature}
  - **After:** {new behavior or API signature}
  - **Migration:** {Step-by-step instructions to adapt}

## API Changes

- **{Endpoint}** -- {What changed: new parameters, deprecated fields,
  response format changes}
  - Method: {GET/POST/PUT/DELETE}
  - Change type: {Added / Modified / Deprecated / Removed}

## Database Migrations

- `{YYYY-MM-DD-description.sql}` -- {What it does}
  - Reversible: {Yes / No}
  - Estimated run time: {seconds/minutes for large tables}
  - Data impact: {Adds column / Modifies data / Creates table}

## Known Issues

- {Issue description} -- {Workaround if available} [#{issue-number}]

## Upgrade Instructions

### Web Application
1. Back up database: `mysqldump --single-transaction {db} > pre-upgrade.sql`
2. Pull latest code: `git pull origin v{VERSION}`
3. Install dependencies: `composer install --no-dev --optimize-autoloader`
4. Run migration: `mysql -u {user} -p {db} < database/migrations/{file}.sql`
5. Clear caches: `{cache clear command}`
6. Verify: Access login page, check dashboard, test one CRUD operation

### Android Application
1. Upload signed APK/AAB to Play Console
2. Set staged rollout to 1%
3. Monitor crash-free rate in Play Console (target: >99.5%)
4. Gradually increase rollout (see Operations Manual for schedule)

## Rollback Procedure

### Web Application
1. Restore database: `mysql -u {user} -p {db} < pre-upgrade.sql`
2. Revert code: `git checkout v{PREVIOUS_VERSION}`
3. Restart web server: `sudo systemctl restart apache2`
4. Verify rollback: Run smoke tests

### Android Application
1. Halt staged rollout in Play Console
2. If severe: upload previous APK as a new versionCode (increment)
3. Communicate via in-app notification
```

### 4. Release Notes by Audience

**Guidance:** Create audience-specific views of the same release.

```markdown
## Audience-Specific Views

### End-User View (Simplified)
Strip technical details. Focus on what users will notice.

**Template:**
# What's New in v{VERSION}

**{Product Name}** has been updated! Here is what changed:

**New:**
- {Feature described in plain language, e.g., "You can now export invoices as PDF"}

**Improved:**
- {Improvement in user terms, e.g., "Dashboard loads faster"}

**Fixed:**
- {Bug fix in user terms, e.g., "Date filter now works correctly on reports"}

**Need Help?** Contact support at {email} or use the in-app **?** button.

---

### Admin View (Technical)
Include migration steps, configuration changes, and security updates.
Use the full release notes template above.

---

### Developer View (Code-Focused)
Focus on API changes, breaking changes, and dependency updates.

**Template:**
# Developer Release Notes -- v{VERSION}

**Breaking Changes:**
- {API endpoint/behavior change with before/after code examples}

**API Changes:**
- `POST /api/v1/{resource}` -- Added `{field}` parameter (optional, string)
- `GET /api/v1/{resource}` -- Response now includes `{field}` in payload

**Dependencies Updated:**
- {package}: {old_version} -> {new_version}

**Migration Required:**
- Run `{migration_file}` before deploying (non-destructive, adds column)
```

### 5. Internal Release Checklist

```markdown
## Internal Release Checklist

### Pre-Release
- [ ] Code freeze applied to release branch
- [ ] All tests pass on staging (unit, integration, E2E)
- [ ] QA sign-off obtained
- [ ] Database migration tested on staging (with production-sized data)
- [ ] Release notes drafted and reviewed
- [ ] Rollback procedure verified on staging
- [ ] Stakeholders notified of release window

### Release Execution
- [ ] Database backup taken (production)
- [ ] Code deployed to production
- [ ] Database migration executed
- [ ] Smoke tests passed (login, dashboard, CRUD, reports)
- [ ] Error logs clean for 15 minutes post-deploy
- [ ] Mobile app uploaded to Play Store (if applicable)

### Post-Release
- [ ] Release notes published (changelog page, email, in-app)
- [ ] Monitoring dashboard reviewed (error rates, response times)
- [ ] Team notified of successful release
- [ ] Known issues documented (if any)
- [ ] Rollback window observed (4 hours before declaring success)
```

### 6. Release Communication Plan

```markdown
## Release Communication Plan

| Channel | Audience | When | Content |
|---------|----------|------|---------|
| In-app notification | All web users | On deploy | Highlights + link to full notes |
| Push notification | Android users | Major releases only | 1-line summary |
| Email | Franchise admins | All releases | Admin-view release notes |
| Changelog page | All users | On deploy | Cumulative release history |
| Internal Slack/chat | Dev team | Pre and post deploy | Technical release notes |

### In-App Notification Template
**Title:** {Product Name} Updated to v{VERSION}
**Body:** {1-2 sentence highlight}. [View full release notes]({link})
**Dismiss:** User can close; does not show again for this version.

### Email Template (Admin)
**Subject:** {Product Name} v{VERSION} Released -- {1-line highlight}
**Body:** {Admin-view release notes with upgrade instructions if self-hosted}
```

### 7. Android Release Specifics

```markdown
## Android Release Specifics

### Play Store "What's New" Text
- **Limit:** 500 characters
- **Format:** Bullet points, plain language, no markdown

**Template:**
What's New in v{VERSION}:
- {New feature 1 -- user benefit in one line}
- {New feature 2}
- {Improvement -- "Faster loading for {screen}"}
- {Bug fix -- "Fixed {issue} on {screen}"}
- Performance improvements and bug fixes

### Testing Track Progression
| Track | Purpose | Audience | Duration |
|-------|---------|----------|----------|
| Internal testing | Developer verification | Dev team (max 100) | 1-2 days |
| Closed testing | QA and beta testers | Selected users (up to 1000) | 3-5 days |
| Open testing | Broader beta | Any volunteer | 5-7 days (optional) |
| Production | Full release | All users | Staged rollout |

### Staged Rollout Percentages
1% -> 5% -> 20% -> 50% -> 100%
Monitor crash-free rate at each stage. Halt if below 99%.

> **Reference:** See `google-play-store-review` skill for full compliance checklist.
```

### 8. Historical Changelog Format

```markdown
## Historical Changelog

Maintain a cumulative changelog file at `docs/CHANGELOG.md`:

# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]
### Added
- {Feature in progress}

## [1.1.0] -- 2026-03-15
### Added
- PDF export for invoices (Sales module)
### Changed
- Dashboard KPI cards now refresh every 60 seconds
### Fixed
- Date filter on reports page (#42)
### Security
- Updated JWT refresh token rotation logic

## [1.0.1] -- 2026-03-01
### Fixed
- Login redirect loop on mobile browsers (#38)
### Security
- Patched XSS vulnerability in search input (#39)

## [1.0.0] -- 2026-02-15
### Added
- Initial release with Sales, Inventory, and Reports modules
- Android app with offline support
- Multi-tenant architecture with franchise isolation

### Changelog Search Tips
- Search by version: `[1.1.0]`
- Search by date: `2026-03`
- Search by module: `Sales module`
- Search by type: `### Fixed`
- Search by issue: `#42`
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| "Various bug fixes and improvements" | Users and admins have no idea what changed | List each change with description |
| Missing upgrade instructions | Admins break systems during upgrade | Step-by-step upgrade for every release |
| No rollback procedure | Failed upgrades become emergencies | Document rollback before releasing |
| Users surprised by breaking changes | Trust eroded, support tickets spike | Announce breaking changes in advance |
| Release notes only for developers | End-users and admins left in the dark | Create audience-specific views |
| No version numbering strategy | Version numbers are arbitrary and confusing | Use semantic versioning consistently |
| Android "What's New" copy-pasted from full notes | Exceeds 500 chars; too technical for users | Write dedicated Play Store copy |
| Release notes written after the release | Details forgotten, inaccuracies introduced | Draft notes during development, finalize before release |

## Quality Checklist

- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)
- [ ] Release date in ISO format (YYYY-MM-DD)
- [ ] Highlights section summarizes the release in 1-3 sentences
- [ ] Every change categorized (New Feature, Improvement, Bug Fix, Security, Breaking)
- [ ] Bug fixes reference issue numbers
- [ ] Breaking changes include migration instructions
- [ ] API changes specify endpoint, method, and what changed
- [ ] Database migrations list file name, description, and reversibility
- [ ] Upgrade instructions are step-by-step and tested
- [ ] Rollback procedure documented for this specific release
- [ ] Audience-specific views created (end-user, admin, developer)
- [ ] Android Play Store "What's New" text under 500 characters
- [ ] Internal release checklist completed
- [ ] Changelog updated with this version
- [ ] Document stays under 500 lines (split if needed)

---

**Back to:** [SKILL.md](../SKILL.md)
