# Implementation Audit — Pre-Flight Checklist

Complete this checklist before generating the audit report.

## Phase 1: Discovery Checklist

### Project Identity

- [ ] Project name identified
- [ ] Tech stack confirmed (languages, frameworks, databases)
- [ ] Architecture pattern identified (MVC, Clean, Microservices, etc.)
- [ ] Multi-tenant? If yes, isolation model documented
- [ ] Deployment target identified (cloud, on-prem, hybrid)

### Documentation Located

- [ ] CLAUDE.md / AGENTS.md read at project root
- [ ] README.md read for project overview
- [ ] Architecture documents found and read
- [ ] PRD / SRS / requirements documents found
- [ ] API documentation (Swagger/OpenAPI) found
- [ ] Database documentation found
- [ ] Milestone/roadmap documents found
- [ ] NEXT_FEATURES.md or equivalent backlog found

### Database Artifacts Located

- [ ] Schema dump files (`.sql`) found
- [ ] Migration files found and ordered
- [ ] Seed/fixture files found
- [ ] Stored procedures/triggers inventoried
- [ ] ERD diagrams found (if any)
- [ ] Database configuration (charset, collation) verified

### Source Code Mapped

- [ ] Directory tree generated (top 2 levels)
- [ ] Route/endpoint files identified
- [ ] Controller/handler files identified
- [ ] Model/entity files identified
- [ ] Service/use-case files identified
- [ ] Middleware files identified
- [ ] Frontend component structure mapped
- [ ] Configuration files read

### Integration Points Identified

- [ ] Sister projects identified (mobile apps, microservices)
- [ ] External API dependencies documented
- [ ] Webhook endpoints cataloged
- [ ] Authentication flow mapped (session, JWT, OAuth)
- [ ] Shared libraries or packages identified

### Test Infrastructure Assessed

- [ ] Test directory structure mapped
- [ ] Test framework identified
- [ ] Unit tests counted by module
- [ ] Integration tests counted
- [ ] E2E/UI tests counted
- [ ] CI/CD pipeline configuration read
- [ ] Coverage reports found (if any)

## Phase 2: Analysis Checklist

### Schema Audit

- [ ] Every documented entity mapped to a database table
- [ ] Missing tables identified and listed
- [ ] Foreign key completeness verified
- [ ] Index coverage assessed for query patterns
- [ ] Multi-tenant scoping columns verified (tenant_id)
- [ ] Audit columns present (created_at, updated_at, created_by)
- [ ] Soft-delete columns present where required
- [ ] Character set consistency verified (utf8mb4_unicode_ci)
- [ ] Enum/status columns match documented business states
- [ ] Junction tables exist for many-to-many relationships

### Implementation Gap Analysis

- [ ] Feature list extracted from all planning documents
- [ ] Each feature classified: Complete / Partial / Phantom / Undocumented
- [ ] Evidence documented for each classification
- [ ] Module-level completion percentages calculated
- [ ] Dependency chain between incomplete features mapped

### Cross-Platform Integration

- [ ] All documented API endpoints verified in code
- [ ] Authentication endpoints verified for mobile/external access
- [ ] CRUD endpoints verified for each entity
- [ ] Pagination implemented on list endpoints
- [ ] Error response format consistent across endpoints
- [ ] File upload/download endpoints verified
- [ ] Push notification infrastructure verified (if documented)
- [ ] Offline sync mechanisms verified (if documented)

### Risk Assessment

- [ ] Critical blockers identified (prevents next milestone)
- [ ] High technical debt items flagged
- [ ] Security gaps identified (see `vibe-security-skill`)
- [ ] Performance bottlenecks identified
- [ ] Scalability concerns documented
- [ ] Missing error handling patterns flagged

## Phase 3: Output Checklist

### Files Generated

- [ ] `00-executive-summary.md` — Project health score, completion table
- [ ] `01-schema-audit.md` — Table-to-feature mapping, gaps
- [ ] `02-implementation-progress.md` — Module-by-module status
- [ ] `03-integration-status.md` — API and cross-platform analysis
- [ ] `04-technical-risks.md` — Prioritized risk register
- [ ] `05-completion-blueprint.md` — Phased action plan
- [ ] `06-module-details/` — Per-module deep dives (as needed)
- [ ] `07-appendices/` — Supporting data tables

### Quality Checks

- [ ] Every file under 500 lines
- [ ] Executive summary under 40 lines of content
- [ ] All tables render correctly in markdown
- [ ] Every gap has: description, severity, skill, complexity
- [ ] Blueprint tasks are dependency-ordered
- [ ] No vague recommendations (all link to specific skills)
- [ ] Completion percentages are evidence-based, not guesses
