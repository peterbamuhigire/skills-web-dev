# Software Development Plan (SDP) — Template & Guide

**Back to:** [SDLC Planning Skill](../SKILL.md)

## Purpose

Defines the **management and technical approach** for how the project will be developed. Covers methodology, team structure, environment setup, coding standards, scheduling, and communication.

## Audience

Project managers, development leads, QA team, DevOps engineers.

## When to Create

After the Project Vision & Scope is approved and the SRS is drafted or in progress.

---

## Template

```markdown
# [Project Name] — Software Development Plan

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**References:** [Link to Project Vision & Scope], [Link to SRS]

---

## 1. Project Overview

### 1.1 Purpose
[Brief description referencing the Vision & Scope document.]

### 1.2 Scope
[What this plan covers — development lifecycle from design through deployment.]

### 1.3 Referenced Documents
| Document | Location |
|----------|----------|
| Project Vision & Scope | docs/planning/02-project-vision-scope.md |
| Software Requirements Spec | docs/planning/03-software-requirements-spec.md |
| Risk Management Plan | docs/planning/07-risk-management-plan.md |

## 2. Development Methodology

### 2.1 Approach
[Describe the methodology. For this stack:]

**Primary:** Phase-Gated Delivery with TDD (Red-Green-Refactor)
**Iteration Model:** 2-week sprints within each phase gate
**Quality Gate:** Each phase requires sign-off before proceeding

### 2.2 Phase Gates

| Gate | Entry Criteria | Exit Criteria | Approver |
|------|---------------|---------------|----------|
| G0: Planning | Project approved | All planning docs complete | Sponsor |
| G1: Design | Planning approved | SDD, DB design, API design complete | Tech Lead |
| G2: Development | Design approved | Code complete, unit tests pass | Dev Lead |
| G3: Testing | Dev complete | All test cases pass, defects resolved | QA Lead |
| G4: Deployment | Testing approved | Production deployment successful | PM + Sponsor |

### 2.3 TDD Workflow

1. **Red:** Write a failing test that defines expected behavior
2. **Green:** Write minimal code to make the test pass
3. **Refactor:** Improve code quality while keeping tests green
4. **Commit:** Commit after each green cycle

## 3. Team Structure & Roles

| Role | Name | Responsibilities |
|------|------|-----------------|
| Project Sponsor | [Name] | Funding, strategic direction, gate approvals |
| Project Manager | [Name] | Schedule, resources, risk management, communication |
| Technical Lead | [Name] | Architecture, code reviews, technical decisions |
| Backend Developer | [Name] | PHP API development, database, business logic |
| Frontend Developer | [Name] | Web UI (Tabler/Bootstrap 5), JavaScript |
| Android Developer | [Name] | Kotlin/Compose app development |
| QA Engineer | [Name] | Test planning, execution, defect management |
| DevOps | [Name] | CI/CD, server management, deployments |

## 4. Technical Architecture Summary

[High-level architecture — reference SDD for details.]

### 4.1 System Layers

| Layer | Technology | Responsibility |
|-------|-----------|---------------|
| Presentation (Web) | Tabler/Bootstrap 5, SweetAlert2, DataTables | Web UI |
| Presentation (Mobile) | Kotlin + Jetpack Compose, Material 3 | Android UI |
| API | PHP 8+ (strict typing, PSR-4) | REST endpoints |
| Business Logic | PHP service classes | Domain rules, validation |
| Data Access | PHP + MySQL 8.x (PDO, prepared statements) | CRUD, stored procedures |
| Auth | Session (web) + JWT (mobile), RBAC | Authentication & authorization |
| Infrastructure | WAMP (dev), Ubuntu/Debian (prod) | Hosting, deployment |

### 4.2 Multi-Tenancy
Row-level isolation via `franchise_id` in every table and every query. No exceptions.

## 5. Development Environment Setup

| Environment | OS | Web Server | Database | PHP | Purpose |
|------------|-----|------------|----------|-----|---------|
| Development | Windows 11 | WAMP (Apache) | MySQL 8.4.x | 8.x | Local dev |
| Staging | Ubuntu VPS | Apache/Nginx | MySQL 8.x | 8.x | Integration testing |
| Production | Debian VPS | Apache/Nginx | MySQL 8.x | 8.x | Live system |

### 5.1 Cross-Platform Considerations
- Use forward-slash paths in code (works on both Windows and Linux)
- Case-sensitive file names (Linux is case-sensitive, Windows is not)
- Database collation: `utf8mb4_general_ci` across all environments
- Line endings: LF (configure `.gitattributes`)
- Environment variables: `.env` file (never committed to Git)

## 6. Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend Language | PHP (strict typing) | 8.2+ |
| Database | MySQL | 8.x |
| Web UI Framework | Tabler + Bootstrap | 5.x |
| JS Libraries | SweetAlert2, DataTables, Flatpickr | Latest stable |
| Mobile Language | Kotlin | 2.0+ |
| Mobile UI | Jetpack Compose + Material 3 | BOM 2024.06+ |
| Mobile DI | Dagger Hilt | 2.51+ |
| Mobile Networking | Retrofit + OkHttp + Moshi | 2.11+ / 4.12+ |
| Mobile DB | Room | 2.6+ |
| CI/CD | GitHub Actions | — |
| Version Control | Git + GitHub | — |

## 7. Coding Standards & Conventions

### 7.1 PHP Standards
- **Reference:** `php-modern-standards` skill
- PSR-12 coding style, PSR-4 autoloading
- Strict typing: `declare(strict_types=1);` in every file
- Type hints on all parameters and return types
- No raw SQL without prepared statements

### 7.2 Kotlin/Android Standards
- **Reference:** `android-development` skill
- MVVM + Clean Architecture with Hilt DI
- Coroutines + Flow for async operations
- EncryptedSharedPreferences for sensitive data
- Samsung Knox crash prevention for EncryptedSharedPreferences init

### 7.3 Database Standards
- **Reference:** `mysql-best-practices` skill
- All tables include `franchise_id`, `created_at`, `updated_at`
- Stored procedures for complex business logic
- Indexes on all foreign keys and frequently queried columns
- Production migrations in `database/migrations-production/` (idempotent)

## 8. Source Control Strategy

### 8.1 Branching Model
| Branch | Purpose | Merges To |
|--------|---------|-----------|
| `main` | Production-ready code | — |
| `develop` | Integration branch | `main` (via release) |
| `feature/*` | New features | `develop` |
| `bugfix/*` | Bug fixes | `develop` |
| `hotfix/*` | Critical production fixes | `main` + `develop` |
| `release/*` | Release preparation | `main` + `develop` |

### 8.2 Commit Conventions
Format: `type: brief description`
Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`

### 8.3 Code Review
- All merges to `develop` require PR with at least 1 reviewer
- All merges to `main` require 2 reviewers
- No self-merging to `main`

## 9. Build & Deployment Pipeline

### 9.1 CI Pipeline (GitHub Actions)
| Stage | Trigger | Actions |
|-------|---------|---------|
| Lint | Every push | PHP syntax check, Kotlin lint |
| Test | Every PR | Unit tests, integration tests |
| Build | PR to develop | Build artifacts |
| Deploy Staging | Merge to develop | Deploy to Ubuntu staging |
| Deploy Prod | Merge to main | Deploy to Debian production |

### 9.2 Android Build
- Gradle build with dev/staging/prod flavors
- Signed APK/AAB for Play Store releases
- ProGuard/R8 for release builds

## 10. Sprint/Phase Planning

| Phase | Duration | Key Deliverables |
|-------|----------|-----------------|
| Phase 1 | Weeks 1-4 | Auth, user management, tenant setup |
| Phase 2 | Weeks 5-8 | Core modules (P0 features) |
| Phase 3 | Weeks 9-12 | Secondary modules (P1 features) |
| Phase 4 | Weeks 13-16 | Android companion app (Phase 1 bootstrap) |
| Phase 5 | Weeks 17-20 | QA, performance, beta launch |
| Phase 6 | Weeks 21-24 | Production launch, monitoring |

## 11. Communication Plan

| Meeting | Frequency | Participants | Purpose |
|---------|-----------|-------------|---------|
| Daily Standup | Daily (15 min) | Dev team | Blockers, progress |
| Sprint Planning | Bi-weekly | PM, Dev, QA | Sprint scope |
| Sprint Review | Bi-weekly | All + stakeholders | Demo deliverables |
| Sprint Retro | Bi-weekly | Dev team | Process improvement |
| Phase Gate Review | Per phase | PM, Sponsor, Leads | Go/No-Go decision |

## 12. Schedule & Milestones

| Milestone | Target Date | Dependencies | Status |
|-----------|-------------|-------------|--------|
| Planning Complete | YYYY-MM-DD | None | [ ] |
| Design Complete | YYYY-MM-DD | Planning | [ ] |
| Backend MVP | YYYY-MM-DD | Design | [ ] |
| Frontend MVP | YYYY-MM-DD | Backend MVP | [ ] |
| Android Phase 1 | YYYY-MM-DD | Backend MVP | [ ] |
| Beta Launch | YYYY-MM-DD | Frontend + Android | [ ] |
| Production Launch | YYYY-MM-DD | Beta | [ ] |
```

---

## Section-by-Section Guidance

### Methodology
Be explicit about TDD. State that tests are written before implementation. This is not optional.

### Team Structure
Even for solo developers, list the roles. One person may fill multiple roles. This clarifies responsibilities.

### Environment Setup
Document exact differences between dev/staging/prod. This prevents "works on my machine" issues.

### Source Control
The branching model should match team size. Small teams can use GitHub Flow (main + feature branches). Larger teams benefit from GitFlow.

### Communication
Adjust meeting cadence to team size. Solo/duo teams need less ceremony. Define escalation paths.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No methodology defined | Everyone codes differently | Choose and document a methodology |
| Skipping TDD ("we'll test later") | Bugs compound, refactoring is risky | Write tests first, always |
| No branching strategy | Merge conflicts, broken main | Define and enforce branching model |
| Missing environment docs | Deployment failures | Document every environment difference |
| No phase gates | Quality issues reach production | Define gate criteria and enforce them |
| Unrealistic timelines (no buffer) | Missed deadlines, team burnout | Add 20-30% contingency buffer |

## Quality Checklist

- [ ] Methodology and TDD workflow clearly described
- [ ] Team roles defined (even if one person fills multiple roles)
- [ ] All 3 environments (dev/staging/prod) documented with differences
- [ ] Technology stack lists specific version numbers
- [ ] Coding standards reference relevant skills
- [ ] Branching model matches team size and workflow
- [ ] CI/CD pipeline stages defined with triggers
- [ ] Phase planning has realistic timelines with contingency
- [ ] Communication plan includes escalation procedures
- [ ] Cross-platform considerations documented (Windows to Linux)
- [ ] Database migration strategy referenced (idempotent scripts)
- [ ] Document stays under 500 lines

---

**Back to:** [SDLC Planning Skill](../SKILL.md)
**Previous:** [Project Vision & Scope](project-vision-scope.md)
**Next:** [Configuration Management Plan](configuration-management-plan.md)
