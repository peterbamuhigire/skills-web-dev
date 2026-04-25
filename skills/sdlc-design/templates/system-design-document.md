# System Design Document (SDD) -- Template & Guide

**Back to:** [SDLC Design Skill](../SKILL.md)

## Purpose

Defines the **overall architecture**, system components, module interactions, and deployment topology. This is the master technical blueprint that all other design documents reference.

## Audience

System architects, senior developers, tech leads, DevOps engineers.

## When to Create

- After the SRS is approved and before implementation begins
- When onboarding new architects or senior developers to the project
- When conducting architecture reviews or audits

## Typical Length

20-40 pages. Split into `01-sdd/` subdirectory files if exceeding 500 lines.

---

## Template

```markdown
# [Project Name] -- System Design Document

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**SRS Reference:** [Link to SRS document]

---

## 1. Introduction

### 1.1 Purpose
[State the purpose of this SDD. Example: "This document describes the software
architecture and design of [Project Name], a multi-tenant SaaS platform for
[domain]. It translates the requirements in SRS v[X] into technical architecture."]

### 1.2 Scope
[What this document covers and does not cover. Reference the SRS for requirements.]

### 1.3 Definitions & Acronyms

| Term | Definition |
|------|-----------|
| SDD | System Design Document |
| SRS | Software Requirements Specification |
| MVVM | Model-View-ViewModel |
| RBAC | Role-Based Access Control |
| franchise_id | Tenant isolation identifier for row-level multi-tenancy |

### 1.4 Design Goals

| Goal | Measurable Target |
|------|-------------------|
| Scalability | Support 500+ concurrent users per franchise |
| Performance | Page load < 2s, API response < 500ms (p95) |
| Availability | 99.5% uptime (excludes scheduled maintenance) |
| Security | Zero cross-tenant data leakage, full audit trail |
| Maintainability | New module deployable in < 2 weeks |

### 1.5 References
- Software Requirements Specification v[X]
- Project Vision & Scope Document
- mysql-best-practices skill (database standards)
- multi-tenant-saas-architecture skill (tenant isolation patterns)
- dual-auth-rbac skill (authentication/authorization patterns)

---

## 2. Architectural Overview

### 2.1 System Context Diagram

[How the system fits in its environment -- users, external systems, boundaries.]

+-------------------+       +-------------------+
|  Franchise Admin  |       |    End User       |
|  (Web Browser)    |       |  (Mobile App)     |
+--------+----------+       +--------+----------+
         |                           |
         | HTTPS (Session)           | HTTPS (JWT)
         v                           v
+------------------------------------------------+
|           [Project Name] Platform              |
|  +----------+  +-----------+  +--------------+ |
|  | /public/ |  |/adminpanel|  |/memberpanel/ | |
|  | (Admin)  |  |(SuperAdmin|  |(End User)    | |
|  +----------+  +-----------+  +--------------+ |
|  +--------------------------------------------+|
|  |         PHP REST API Layer                 ||
|  +--------------------------------------------+|
|  +--------------------------------------------+|
|  |         MySQL 8.x Database                 ||
|  +--------------------------------------------+|
+------------------------------------------------+
         |                  |
         v                  v
+----------------+  +------------------+
| Payment Gateway|  | SMS/Email Service|
| (M-Pesa, etc.) |  | (Notifications)  |
+----------------+  +------------------+

### 2.2 High-Level Architecture

[Major components and their relationships.]

+----------------------------------------------------------+
|                    PRESENTATION LAYER                     |
| +------------+ +---------------+ +---------------------+ |
| | Web UI     | | Admin Panel   | | Android App         | |
| | Tabler/BS5 | | Tabler/BS5    | | Compose + MVVM      | |
| | SweetAlert2| | DataTables    | | Material 3          | |
| +------+-----+ +-------+-------+ +---------+-----------+ |
|        |                |                   |             |
+----------------------------------------------------------+
         |                |                   |
+----------------------------------------------------------+
|                    APPLICATION LAYER                      |
| +----------------------------------------------------+   |
| | PHP Controllers (REST API endpoints)               |   |
| | - Authentication (session + JWT dual auth)         |   |
| | - Business Logic Services                          |   |
| | - Middleware (auth, RBAC, tenant scoping, CORS)    |   |
| | - Validation & Sanitization                        |   |
| +----------------------------------------------------+   |
+----------------------------------------------------------+
         |
+----------------------------------------------------------+
|                    DATA LAYER                             |
| +----------------------------------------------------+   |
| | MySQL 8.x (utf8mb4_general_ci)                     |   |
| | - Row-level tenant isolation (franchise_id)        |   |
| | - Stored procedures (sp_action_entity)             |   |
| | - Triggers (audit trails, cascading updates)       |   |
| | - Views (reporting, dashboards)                    |   |
| +----------------------------------------------------+   |
+----------------------------------------------------------+

### 2.3 Architecture Style & Patterns

| Pattern | Application | Reference |
|---------|------------|-----------|
| Layered Architecture | Web backend: Controller > Service > Repository > DB | php-modern-standards |
| MVVM + Clean Architecture | Android: UI > ViewModel > UseCase > Repository > API/Room | android-development |
| REST API | All client-server communication | api-error-handling |
| Row-Level Multi-Tenancy | franchise_id in every tenant-scoped query | multi-tenant-saas-architecture |
| Dual Authentication | Session (web) + JWT (mobile) running in parallel | dual-auth-rbac |
| Repository Pattern | Data access abstraction in Android and PHP | android-data-persistence |
| Observer Pattern | LiveData/StateFlow in Android ViewModels | android-development |

---

## 3. Component Design

### 3.1 Backend Components (PHP)

| Component | Responsibility | Key Classes/Files |
|-----------|---------------|-------------------|
| Controllers | Route handling, request validation, response formatting | `/api/[module]/[action].php` |
| Services | Business logic encapsulation | `/includes/services/[Module]Service.php` |
| Middleware | Auth, RBAC, tenant scoping, CORS, rate limiting | `/includes/middleware/` |
| Helpers | Utility functions (date formatting, sanitization) | `/includes/helpers/` |
| Models | Data transfer objects and entity representations | `/includes/models/` |
| Config | Environment-specific configuration | `/includes/config/` |

### 3.2 Mobile Components (Android -- Kotlin)

| Layer | Responsibility | Key Packages |
|-------|---------------|--------------|
| Presentation | Compose UI, ViewModels, state management | `ui/`, `viewmodel/` |
| Domain | Use cases, business rules, entity interfaces | `domain/usecase/`, `domain/model/` |
| Data | Repository implementations, API services, Room DAOs | `data/repository/`, `data/remote/`, `data/local/` |
| DI | Hilt dependency injection modules | `di/` |
| Core | Base classes, extensions, utilities | `core/` |

### 3.3 Web Frontend Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Page Templates | HTML structure, server-side rendering | PHP + Tabler template |
| JavaScript Modules | AJAX calls, form handling, dynamic UI | Vanilla JS / jQuery |
| DataTables | Paginated, searchable data grids | DataTables.js |
| Alerts & Modals | User feedback, confirmations | SweetAlert2 |
| Date Pickers | Date/time input | Flatpickr |
| Charts | Dashboard visualizations | Chart.js / ApexCharts |

### 3.4 Database Layer

| Component | Responsibility | Naming Convention |
|-----------|---------------|-------------------|
| Tables | Data storage with tenant isolation | `snake_case`, singular or plural per project |
| Stored Procedures | Complex business logic in SQL | `sp_action_entity` |
| Triggers | Audit trails, cascading updates, validation | `tr_table_timing_event` |
| Views | Reporting, dashboard aggregations | `vw_purpose` |
| Indexes | Query performance optimization | `idx_table_columns` |

See: Database Design Document for complete schema details.
See: mysql-best-practices skill for standards.

---

## 4. Module Decomposition

[Define each business module. Repeat this block per module.]

### Module: [Module Name]

| Attribute | Value |
|-----------|-------|
| Responsibility | [What this module does] |
| Owner | [Team/developer responsible] |
| Dependencies | [Other modules it depends on] |
| Data Owned | [Tables this module owns] |
| API Endpoints | [Endpoint group, e.g., /api/inventory/*] |
| Panels | [Which panels: /public/, /adminpanel/, /memberpanel/] |

**Interfaces Provided:**
- [API endpoint group it exposes]
- [Events/hooks it publishes]

**Interfaces Consumed:**
- [APIs from other modules it calls]
- [Shared services it uses (auth, notifications)]

---

## 5. Multi-Tenant Architecture

### 5.1 Tenant Isolation Strategy
- **Method:** Row-level isolation via `franchise_id` column
- **Enforcement:** Every SQL query on tenant-scoped tables MUST include
  `WHERE franchise_id = ?` (parameterized, never from client input)
- **Source of truth:** `franchise_id` derived from authenticated session/JWT token
- **Validation:** Middleware extracts franchise_id; controllers never accept it as input

### 5.2 Three-Panel Separation

| Panel | URL Path | Users | Auth Method |
|-------|----------|-------|-------------|
| Franchise Admin | `/public/` | Franchise owners, managers | Session |
| Super Admin | `/adminpanel/` | Platform operators | Session |
| End User | `/memberpanel/` | Customers, members | Session |
| Mobile API | `/api/` | Mobile app users | JWT |

### 5.3 Session Prefix System
Each panel uses a distinct session prefix to prevent session collisions:
- `/public/` sessions: `pub_`
- `/adminpanel/` sessions: `adm_`
- `/memberpanel/` sessions: `mem_`

---

## 6. Security Architecture

### 6.1 Authentication Flows
- **Web:** PHP session-based auth with CSRF tokens (see dual-auth-rbac skill)
- **Mobile:** JWT with access/refresh token rotation (see dual-auth-rbac skill)
- **Password:** bcrypt hashing, minimum 8 characters, breach detection

### 6.2 Authorization Model
- **RBAC:** Role > Permission mapping with explicit allow/deny
- **Enforcement:** Middleware checks permission before controller executes
- **Tenant scoping:** Users can only access data within their franchise_id

### 6.3 Encryption
- **In transit:** TLS 1.2+ for all connections
- **At rest:** EncryptedSharedPreferences on Android, AES-256 for sensitive DB fields
- **Tokens:** JWT signed with RS256, stored in EncryptedSharedPreferences

### 6.4 Audit Logging
- **What:** All create/update/delete operations logged
- **Fields:** user_id, franchise_id, action, entity, entity_id, old_value, new_value, timestamp, ip_address
- **Retention:** Minimum 2 years
- **Access:** Super admin only, immutable (append-only)

---

## 7. Deployment Architecture

### 7.1 Environment Topology

| Environment | OS | Server | Database | Purpose |
|------------|-----|--------|----------|---------|
| Development | Windows 11 | WAMP (Apache + PHP 8.x) | MySQL 8.x local | Developer workstations |
| Staging | Ubuntu VPS | Apache/Nginx + PHP 8.x | MySQL 8.x | QA testing, client demos |
| Production | Debian VPS | Apache/Nginx + PHP 8.x | MySQL 8.x | Live traffic |

### 7.2 Cross-Platform Considerations
- File paths: Use forward slashes; avoid case-sensitivity issues
- Line endings: LF (not CRLF) in repository
- Collation: `utf8mb4_general_ci` across all environments
- Timezone: UTC in database, localized in presentation layer

### 7.3 Scaling Strategy
- **Vertical:** Increase VPS resources (CPU, RAM) for single-tenant growth
- **Horizontal:** Read replicas for reporting queries
- **Caching:** OpCache for PHP, query cache for frequent reads
- **CDN:** Static assets served via CDN (CSS, JS, images)

---

## 8. Technology Stack Matrix

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend Language | PHP | 8.x | Server-side logic, REST API |
| Database | MySQL | 8.x | Primary data store |
| Web UI Framework | Tabler + Bootstrap | 5.x | Admin panel templates |
| Mobile Language | Kotlin | 1.9+ | Android app development |
| Mobile UI | Jetpack Compose | Latest BOM | Declarative UI |
| Mobile Architecture | MVVM + Clean Architecture | -- | Separation of concerns |
| Mobile DI | Hilt (Dagger) | Latest | Dependency injection |
| Mobile HTTP | Retrofit + OkHttp | Latest | API communication |
| Mobile Local DB | Room | Latest | Offline data persistence |
| JS Libraries | SweetAlert2, DataTables, Flatpickr | Latest | UI interactions |

---

## 9. Design Decisions Log (ADR Format)

### ADR-001: Row-Level Multi-Tenancy

| Attribute | Value |
|-----------|-------|
| **Decision** | Use row-level isolation with `franchise_id` column |
| **Context** | Need to isolate tenant data in a shared database |
| **Alternatives** | Separate databases per tenant; schema-per-tenant |
| **Rationale** | Simpler deployment, lower cost, easier maintenance for target market (African SaaS). Separate DBs don't scale economically for 100+ small franchises. |
| **Consequences** | Every query must include franchise_id filter. Requires middleware enforcement. |

### ADR-002: Dual Authentication

| Attribute | Value |
|-----------|-------|
| **Decision** | Session-based auth for web, JWT for mobile, running in parallel |
| **Context** | Web and mobile clients have different auth needs |
| **Alternatives** | JWT-only for all clients; session-only with mobile adapter |
| **Rationale** | Sessions work best for server-rendered web pages with CSRF protection. JWT works best for stateless mobile API calls. Dual approach is optimal for both. |
| **Consequences** | Auth middleware must handle both token types. Login endpoints return appropriate token type. |

[Add project-specific ADRs as decisions are made.]
```

---

## Section-by-Section Guidance

| Section | Key Guidance |
|---------|-------------|
| Introduction | Always reference the specific SRS version. Define every acronym. |
| System Context | Show ALL external actors and systems. Include data flow direction. |
| High-Level Architecture | Show layers, not individual files. Group by responsibility. |
| Component Design | List components per layer. Include naming conventions. |
| Module Decomposition | One block per business module. Document ownership and interfaces. |
| Multi-Tenant | Document franchise_id strategy explicitly. Never assume it is obvious. |
| Security | Reference `dual-auth-rbac` and `vibe-security-skill`. Cover all four areas. |
| Deployment | Include all three environments with specific OS and server details. |
| ADR Log | Add decisions as they are made. Never delete old ADRs; mark superseded. |

## Example Excerpt: ERP Module Decomposition

```markdown
### Module: Inventory Management

| Attribute | Value |
|-----------|-------|
| Responsibility | Track stock levels, movements, valuations across locations |
| Owner | Backend Team |
| Dependencies | Products module, Locations module, Auth module |
| Data Owned | stock_movements, stock_levels, warehouses, stock_adjustments |
| API Endpoints | /api/inventory/* |
| Panels | /public/ (franchise admin), /adminpanel/ (reports only) |

**Interfaces Provided:**
- GET /api/inventory/stock-levels.php?product_id=X
- POST /api/inventory/stock-adjustment.php
- Triggers: stock level update on invoice creation

**Interfaces Consumed:**
- Products API: product details and pricing
- Auth middleware: franchise_id extraction, permission checks
```

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| No component boundaries | Everything depends on everything | Define clear module ownership |
| Missing tenant isolation section | Data leakage risk | Always document franchise_id strategy |
| God classes (1000+ line services) | Untestable, unmaintainable | One service per business capability |
| No deployment diagram | DevOps can't set up environments | Include all 3 environments |
| Vague design goals ("fast", "secure") | Unmeasurable | Use numeric targets (< 500ms, 99.5%) |
| No ADR log | Design decisions are lost | Record every significant decision |

## Quality Checklist

- [ ] All architecture diagrams present (system context, high-level, deployment)
- [ ] Tech stack matrix includes specific version numbers
- [ ] Every module has a decomposition block with interfaces
- [ ] Multi-tenant isolation strategy explicitly documented
- [ ] Security architecture covers auth, authorization, encryption, audit
- [ ] Deployment covers all 3 environments (dev, staging, prod)
- [ ] Cross-platform considerations documented
- [ ] ADR log started with foundational decisions
- [ ] Cross-references to SRS requirement IDs where applicable
- [ ] No sections left as "[TODO]" -- all filled or marked "N/A" with justification

---

**Back to:** [SDLC Design Skill](../SKILL.md) | **Related:** [Technical Specification](technical-specification.md) | [Database Design](database-design-document.md)
