# Software Requirements Specification (SRS) — Template & Guide

**Back to:** [SDLC Planning Skill](../SKILL.md)

## Purpose

The **complete blueprint** of all functional and non-functional requirements for the full system. This is the definitive reference for what the software must do and how well it must perform.

## Audience

Developers, QA engineers, stakeholders, architects, project managers.

## When to Create

After requirements are gathered (via `project-requirements` skill or stakeholder interviews) and the Vision & Scope is approved. This document expands raw requirements into a structured, traceable specification.

## Relationship to Other Skills

- **`project-requirements`** gathers raw requirements via guided interview. Feed its output into this SRS template.
- **`android-saas-planning`** generates an SRS specifically for Android apps. This template covers the **full system** (backend + web + mobile).
- **`feature-planning`** creates specs for individual features. This SRS covers the entire system at a higher level.

## Typical Length

30-60 pages. **Split into sub-files** for large projects:
```
docs/planning/
├── 03-software-requirements-spec.md    # Index (this template)
├── 03-srs/
│   ├── functional-requirements.md      # All FR-* requirements
│   ├── non-functional-requirements.md  # All NFR-* requirements
│   └── traceability-matrix.md          # Requirements traceability
```

---

## Template

```markdown
# [Project Name] — Software Requirements Specification

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**References:** [Vision & Scope], [project-requirements output]

---

## 1. Introduction

### 1.1 Purpose
This SRS defines all functional and non-functional requirements for [Project Name],
a multi-tenant SaaS platform for [domain/industry].

### 1.2 Scope
[Brief description of the system being specified.]

### 1.3 Definitions & Acronyms

| Term | Definition |
|------|-----------|
| Franchise | A tenant in the multi-tenant system |
| franchise_id | Row-level tenant isolation identifier present in all data tables |
| RBAC | Role-Based Access Control |
| JWT | JSON Web Token (used for mobile API authentication) |
| SPA | Single Page Application |
| [Domain term] | [Definition] |

### 1.4 References
| Document | Purpose |
|----------|---------|
| Project Vision & Scope | High-level scope and objectives |
| project-requirements output | Raw requirements from interview |
| Risk Management Plan | Risks that inform NFRs |

## 2. Overall Description

### 2.1 Product Perspective
[Where this system fits in the larger ecosystem. New system? Replacement?
Integration with existing systems?]

### 2.2 Product Functions (High-Level)
| Module | Description | Priority |
|--------|------------|----------|
| Authentication | Session (web) + JWT (mobile), RBAC | P0 |
| User Management | User CRUD, roles, permissions | P0 |
| [Module 3] | [Description] | P0 |
| [Module 4] | [Description] | P1 |
| [Module 5] | [Description] | P2 |

### 2.3 User Classes & Characteristics

| User Class | Access Panel | Key Capabilities | franchise_id Scoped? |
|-----------|-------------|------------------|---------------------|
| Super Admin | System admin panel | Global config, tenant management | No (sees all) |
| Franchise Owner | Franchise admin panel | Full franchise management | Yes |
| Staff | Franchise admin panel | Assigned module access | Yes |
| End User | Member portal or mobile app | Self-service features | Yes |

### 2.4 Operating Environment
| Component | Environment |
|-----------|------------|
| Backend | PHP 8.2+ on Apache (WAMP dev, Linux prod) |
| Database | MySQL 8.x with utf8mb4_general_ci |
| Web UI | Modern browsers (Chrome, Firefox, Safari, Edge) |
| Mobile | Android 10+ (API 29+), Kotlin + Jetpack Compose |

### 2.5 Design Constraints
- Multi-tenant with row-level isolation (franchise_id in every query)
- Dual auth: Session for web, JWT for mobile
- PHP strict typing with PSR standards
- TDD methodology (tests before implementation)
- 500-line limit on all documentation files

### 2.6 Assumptions
- [List assumptions made during requirements gathering]

## 3. Functional Requirements

### Requirement ID Convention
Format: `FR-[MODULE]-[NUMBER]`
Example: `FR-AUTH-001`, `FR-INV-003`, `FR-RPT-012`

### 3.1 Authentication Module (FR-AUTH)

| ID | Requirement | Priority | Acceptance Criteria |
|----|------------|----------|-------------------|
| FR-AUTH-001 | System shall support web login via email/password with session-based auth | P0 | User can log in via web, session is created, RBAC enforced |
| FR-AUTH-002 | System shall support mobile login via JWT with refresh token rotation | P0 | Mobile user gets access + refresh token, refresh rotates token, old token invalidated |
| FR-AUTH-003 | System shall enforce RBAC with explicit allow/deny permissions | P0 | Users see only features their role permits, denied features return 403 |
| FR-AUTH-004 | System shall detect token breach (reuse of revoked refresh token) | P0 | Revoked token reuse revokes all tokens for that user, returns 401 |
| FR-AUTH-005 | System shall support password reset via email | P1 | User receives reset link, can set new password, old sessions invalidated |

### 3.2 [Module Name] (FR-[MOD])

| ID | Requirement | Priority | Acceptance Criteria |
|----|------------|----------|-------------------|
| FR-[MOD]-001 | [Requirement description] | [P0/P1/P2] | [Specific, testable criteria] |

[Repeat for each module. Group requirements logically.]

## 4. Non-Functional Requirements

### Requirement ID Convention
Format: `NFR-[CATEGORY]-[NUMBER]`

### 4.1 Performance (NFR-PERF)

| ID | Requirement | Target | Measurement |
|----|------------|--------|-------------|
| NFR-PERF-001 | API response time (p95) | < 500ms | APM monitoring |
| NFR-PERF-002 | Web page load time | < 2 seconds | Lighthouse score |
| NFR-PERF-003 | Android app cold start | < 3 seconds | Android Profiler |
| NFR-PERF-004 | Database query time (simple) | < 100ms | MySQL slow query log |
| NFR-PERF-005 | Concurrent users supported | 200+ per server | Load testing |

### 4.2 Security (NFR-SEC)

| ID | Requirement | Target | Verification |
|----|------------|--------|-------------|
| NFR-SEC-001 | All SQL queries use prepared statements | 100% compliance | Code review + static analysis |
| NFR-SEC-002 | All user input validated server-side | 100% of inputs | Security testing |
| NFR-SEC-003 | Sensitive data encrypted at rest | All PII, tokens | Audit |
| NFR-SEC-004 | HTTPS enforced on staging and production | No HTTP allowed | SSL check |
| NFR-SEC-005 | Session timeout after inactivity | 30 min (web), configurable | Testing |

### 4.3 Availability (NFR-AVL)

| ID | Requirement | Target |
|----|------------|--------|
| NFR-AVL-001 | System uptime | 99.5% (excluding planned maintenance) |
| NFR-AVL-002 | Planned maintenance window | < 2 hours/month, off-peak |
| NFR-AVL-003 | Recovery Time Objective (RTO) | < 4 hours |
| NFR-AVL-004 | Recovery Point Objective (RPO) | < 1 hour (max data loss) |

### 4.4 Scalability (NFR-SCL)

| ID | Requirement | Target |
|----|------------|--------|
| NFR-SCL-001 | Support tenant count | 100+ tenants on single instance |
| NFR-SCL-002 | Support data volume | 1M+ rows per major table |
| NFR-SCL-003 | Horizontal scaling capability | Add app servers behind load balancer |

### 4.5 Usability (NFR-USB)

| ID | Requirement | Target |
|----|------------|--------|
| NFR-USB-001 | New user task completion (primary flow) | < 5 minutes without training |
| NFR-USB-002 | Web accessibility compliance | WCAG 2.1 AA |
| NFR-USB-003 | Android accessibility | TalkBack compatible, 48dp touch targets |
| NFR-USB-004 | Mobile UI responsiveness | All screens work on 5" to 7" displays |

### 4.6 Multi-Tenancy (NFR-MT)

| ID | Requirement | Target | Verification |
|----|------------|--------|-------------|
| NFR-MT-001 | Tenant data isolation | Zero cross-tenant data leakage | Automated isolation tests |
| NFR-MT-002 | franchise_id in all data tables | 100% of data tables | Schema audit |
| NFR-MT-003 | franchise_id in all data queries | 100% of queries | Code review + testing |
| NFR-MT-004 | Tenant-scoped configuration | Each tenant configures independently | Testing |

### 4.7 Offline Capability (NFR-OFF) — Android Only

| ID | Requirement | Target |
|----|------------|--------|
| NFR-OFF-001 | Dashboard viewable offline | Cached data from last sync |
| NFR-OFF-002 | Network state indicator | User sees online/offline badge |
| NFR-OFF-003 | Auto-sync on reconnection | Queued operations sync within 30 seconds |
| NFR-OFF-004 | Conflict resolution | Last-write-wins with server authority |

## 5. Interface Requirements

### 5.1 User Interfaces

| Platform | Technology | Standards |
|----------|-----------|-----------|
| Web Admin | Tabler/Bootstrap 5, DataTables, SweetAlert2, Flatpickr | Responsive, WCAG 2.1 AA |
| Android | Jetpack Compose, Material 3 | Material Design 3 guidelines |

### 5.2 API Interfaces

| Interface | Protocol | Auth | Format |
|-----------|----------|------|--------|
| Web API | REST/HTTP | Session + CSRF | JSON |
| Mobile API | REST/HTTPS | JWT Bearer token | JSON |
| Webhook (optional) | HTTPS POST | API key / signature | JSON |

### 5.3 External Interfaces

| System | Protocol | Purpose |
|--------|----------|---------|
| [Payment gateway] | REST API | Payment processing |
| [SMS provider] | REST API | OTP, notifications |
| [Email service] | SMTP / API | Transactional email |

## 6. Data Requirements

### 6.1 Data Model Overview
[List core entities with their relationships. Reference database design docs for details.]

| Entity | Key Fields | Relationships |
|--------|-----------|---------------|
| franchises | id, name, code, settings | Parent of all tenant data |
| users | id, franchise_id, email, role | Belongs to franchise |
| [Entity] | [Fields] | [Relationships] |

### 6.2 Data Retention
| Data Type | Retention Period | Action After |
|-----------|-----------------|-------------|
| Transactional data | 7 years | Archive |
| Audit logs | 3 years | Archive |
| User sessions | 30 days | Purge |
| Deleted records | 90 days (soft delete) | Hard delete |

### 6.3 Data Privacy
- PII fields identified and documented
- Data encryption at rest for sensitive fields
- User data export capability (GDPR compliance)
- User data deletion capability (right to be forgotten)

## 7. Traceability Matrix

| Requirement ID | Design Component | Test Case | Status |
|---------------|-----------------|-----------|--------|
| FR-AUTH-001 | LoginController, SessionManager | TC-AUTH-001 | [ ] |
| FR-AUTH-002 | MobileAuthController, JWTManager | TC-AUTH-002 | [ ] |
| NFR-PERF-001 | All API endpoints | TC-PERF-001 | [ ] |
| NFR-MT-001 | All data access layers | TC-MT-001 | [ ] |

[Complete traceability matrix in `03-srs/traceability-matrix.md` for large projects.]

## 8. Appendices

### Appendix A: Data Dictionary
[Field-level definitions for key entities. Move to sub-file if large.]

### Appendix B: Glossary
[Complete domain glossary.]
```

---

## Section-by-Section Guidance

### Functional Requirements
- Every requirement must be **testable** (specific acceptance criteria)
- Use the `FR-[MODULE]-[NUMBER]` format consistently
- Group by module for readability
- Include priority (P0/P1/P2) to guide implementation order
- Cross-reference `project-requirements` output for completeness

### Non-Functional Requirements
- Every NFR must have a **measurable target** (not "fast" but "< 500ms")
- Include the **measurement method** (how will you verify this?)
- Always include NFR-MT (multi-tenancy) for SaaS projects
- Include NFR-OFF (offline) only if Android app has offline requirements

### Traceability Matrix
- Links requirements to design components and test cases
- Ensures nothing is built without a requirement
- Ensures nothing is required without a test
- Start with the matrix structure; fill in as design and testing progress

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Ambiguous requirements ("system should be fast") | Untestable, subjective | Use specific numeric targets with measurement methods |
| Missing non-functional requirements | Performance, security, scalability issues discovered late | Always include all 7 NFR categories |
| No requirement IDs | Cannot trace, cannot reference, cannot track | Use `FR-MOD-NNN` and `NFR-CAT-NNN` format |
| No traceability matrix | Requirements get lost between spec and implementation | Build matrix from the start, update continuously |
| No multi-tenancy requirements | Data leakage risks | Always include NFR-MT for multi-tenant systems |
| Requirements without acceptance criteria | Developers interpret differently, QA cannot test | Every FR must have specific, testable acceptance criteria |
| One massive SRS file (1000+ lines) | Exceeds 500-line limit, hard to navigate | Split into index + sub-files (functional, non-functional, traceability) |
| Copy-paste from project-requirements without refinement | Raw interview output is not structured enough | Refine, number, and add acceptance criteria |

## Quality Checklist

- [ ] All functional requirements have unique IDs (FR-MOD-NNN format)
- [ ] All functional requirements have priority (P0/P1/P2)
- [ ] All functional requirements have specific acceptance criteria
- [ ] All non-functional requirements have measurable targets
- [ ] Performance NFRs include API, web, and Android targets
- [ ] Security NFRs reference OWASP and vibe-security-skill
- [ ] Multi-tenancy NFRs address franchise_id isolation
- [ ] Offline NFRs included if Android app has offline requirements
- [ ] Interface requirements cover web, mobile, and external APIs
- [ ] Data requirements include retention and privacy policies
- [ ] Traceability matrix structure is in place (even if partially filled)
- [ ] User classes match those defined in Vision & Scope
- [ ] Operating environment matches SDP's tech stack
- [ ] Definitions and glossary are complete
- [ ] Document stays under 500 lines (split into sub-files if needed)
- [ ] Cross-references to project-requirements output and Vision & Scope included

---

**Back to:** [SDLC Planning Skill](../SKILL.md)
**Previous:** [Risk Management Plan](risk-management-plan.md)
**Next:** [Feasibility Study Report](feasibility-study-report.md)
