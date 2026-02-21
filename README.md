# Claude Code Skills Collection

A curated collection of specialized skills for Claude Code that bring expert-level knowledge and patterns to your development workflow. Use these skills to maintain consistency across projects, accelerate development, and ensure best practices.

## Table of Contents

- [Overview](#overview)
- [Available Skills](#available-skills)
- [Installation](#installation)
- [Usage](#usage)
- [Skill Development](#skill-development)
- [Contributing](#contributing)
- [License](#license)

## Overview

This repository contains domain-specific skills that can be loaded into Claude Code to enhance its capabilities. Each skill is a self-contained module providing:

- Specialized domain knowledge
- Battle-tested architectural patterns
- Code generation templates
- Best practice guidelines
- Testing strategies

### What are Claude Code Skills?

Skills are specialized instruction sets that guide Claude Code in specific domains. When you load a skill, Claude gains deep expertise in that area and can help with:

- Architecture and design decisions
- Code generation following best practices
- Implementation planning
- Testing strategies
- Security and compliance considerations

## Available Skills

### Full Skill Index

- ai-assisted-development
- ai-error-handling
- ai-error-prevention
- android-custom-icons
- android-biometric-login
- android-pdf-export
- android-data-persistence
- android-development
- android-report-tables
- android-reports
- android-saas-planning
- android-tdd
- api-error-handling
- api-pagination
- custom-sub-agents
- doc-architect
- dual-auth-rbac
- feature-planning
- gis-mapping
- google-play-store-review
- image-compression
- implementation-status-auditor
- plan-implementation
- inventory-management
- jetpack-compose-ui
- manual-guide
- markdown-lint-cleanup
- modular-saas-architecture
- mobile-rbac
- multi-tenant-saas-architecture
- mysql-best-practices
- orchestration-best-practices
- photo-management
- php-modern-standards
- pos-restaurant-ui-standard
- pos-sales-ui-design
- project-requirements
- report-print-pdf
- saas-seeder
- sdlc-design
- sdlc-planning
- sdlc-testing
- sdlc-user-deploy
- skill-safety-audit
- skill-writing
- spec-architect
- update-claude-documentation
- vibe-security-skill
- webapp-gui-design

### 1. Android Development

**Focus:** Android development standards for AI agent implementation

**When to use:**

- Building new Android applications or features
- Reviewing Android code for quality and standards compliance
- Generating Kotlin/Compose code via AI agents
- Setting up Android project structure
- Implementing security, testing, or performance patterns
- Integrating with REST APIs from Android clients

**Key capabilities:**

- Kotlin 100% with Jetpack Compose UI
- MVVM + Clean Architecture (data, domain, presentation layers)
- Hilt dependency injection with proper scoping
- Comprehensive security (EncryptedSharedPreferences, cert pinning, biometrics)
- Material 3 design system with reusable components
- Complete screen patterns (list, form, detail with pull-to-refresh)
- Standard charting via Vico (Compose-first)
- Testing standards (ViewModel, UseCase, Compose UI tests with Turbine/MockK)
- Gradle KTS build configuration with version catalog
- Retrofit API integration with typed error handling
- Firebase analytics and performance monitoring
- AI agent quality checklist for generated code

**Skill location:** `android-development/SKILL.md`

**Reference files:** `references/` (12 topic-specific guides covering project structure, Kotlin conventions, architecture, DI, security, UI, screens, testing, build config, API integration, analytics, and AI guidelines)

---

### 1b. Android Test-Driven Development (TDD)

**Focus:** TDD methodology for Android apps with Red-Green-Refactor cycle

**When to use:**

- Building Android features with test-first methodology
- Setting up test infrastructure for Android projects
- Reviewing test quality and coverage patterns
- Onboarding teams to TDD practices for Android
- Integrating CI/CD test pipelines for Android

**Key capabilities:**

- Red-Green-Refactor cycle enforcement
- Test pyramid strategy (70% unit, 20% integration, 10% UI)
- Layer-specific testing: Domain, ViewModel, Repository, Database, Network, UI
- Coroutine and Flow testing with Turbine
- LiveData testing with InstantTaskExecutorRule
- MockWebServer for API layer testing
- Room in-memory database testing
- Espresso and Compose UI testing
- Test data factories and parameterized tests
- Hilt testing configuration
- GitHub Actions CI pipeline setup
- JaCoCo code coverage integration
- Team adoption strategy and legacy code handling

**Skill location:** `android-tdd/SKILL.md`

**Reference files:** `references/` (5 deep-dive guides: TDD workflow, testing by layer, advanced techniques, tools & CI, team adoption)

---

### 1c. Jetpack Compose UI

**Focus:** Beautiful, sleek, minimalistic Compose UI standard across all apps

**When to use:**

- Building any Compose UI screen or component
- Ensuring consistent design language across apps
- Reviewing Compose code for visual quality and performance
- Implementing animations, transitions, and loading states
- Setting up theming, navigation, and Material 3 patterns

**Key capabilities:**

- Design philosophy: minimalism, consistency, whitespace, content-first hierarchy
- Material 3 theming with dynamic color support and dark theme
- Spacing system (4dp grid), typography hierarchy, shape language
- State hoisting and unidirectional data flow enforcement
- Screen templates: List, Detail, Form (with complete code)
- Shimmer/skeleton loading, pull-to-refresh, pagination
- Micro-interactions: press effects, counter animations, staggered lists
- AnimatedVisibility, Crossfade, AnimatedContent transitions
- Navigation setup with bottom nav, arguments, and screen transitions
- Performance: stability, remember, derivedStateOf, lazy list optimization
- Component library: buttons, cards, text fields, chips, bottom sheets, dialogs

**Skill location:** `jetpack-compose-ui/SKILL.md`

**Reference files:** `references/` (5 deep-dive guides: design philosophy, composable patterns, layouts & components, animation & polish, navigation & performance)

---

### 1d. Android Data Persistence

**Focus:** Room database, DataStore, file storage, and API-backed cloud sync

**When to use:**

- Implementing any local data storage in Android apps
- Setting up Room database with entities, DAOs, and migrations
- Building offline-first features with API sync
- Choosing between DataStore, SharedPreferences, Room, or file storage
- Implementing Repository pattern for data layer
- Caching API responses locally

**Key capabilities:**

- Storage decision guide (DataStore vs Room vs Files vs API sync)
- Room essentials: entities, DAOs, database setup, TypeConverters, Hilt modules
- Room advanced: one-to-many/many-to-many relations, migrations, auto-migrations
- DataStore for preferences (replacing SharedPreferences)
- EncryptedSharedPreferences for sensitive data
- Internal/external file storage patterns
- Repository pattern: Room as cache + custom API backend sync
- Three sync strategies: cache-first, network-first, offline queue
- Offline queue with WorkManager for write operations
- Data layer mapping: DTO -> Entity -> Domain model separation
- Network connectivity awareness
- Paging 3 integration with Room
- Migration testing patterns

**Skill location:** `android-data-persistence/SKILL.md`

**Reference files:** `references/` (4 deep-dive guides: Room essentials, Room advanced, local storage, API sync patterns)

---

### 1e. Android Custom PNG Icons

**Focus:** Enforce custom PNG icons (no icon libraries) with placeholder usage and `PROJECT_ICONS.md` tracking

**When to use:**

- Any Android UI generation (Compose or XML)
- Whenever icons are needed in screens, components, or navigation
- When you want a clear list of required PNGs to source

**Key capabilities:**

- Standard icon directory and naming rules
- Compose and XML usage patterns with placeholders
- Mandatory `PROJECT_ICONS.md` maintenance

**Skill location:** `android-custom-icons/SKILL.md`

---

### 1f. Android Report Tables (25+ Rows)

**Focus:** Require table layouts for any report that can exceed 25 rows

**When to use:**

- Any Android report or analytics list with potential for >25 rows
- Inventory, finance, audit, and transactional reports

**Key capabilities:**

- Mandatory rule for table-first rendering
- Pagination guidance and mobile column limits

**Skill location:** `android-report-tables/SKILL.md`

---

### 1g. Google Play Store Review Readiness

**Focus:** Play Store policy compliance and first-time approval readiness

**When to use:**

- Preparing an Android release for Play Console submission
- Validating policy compliance, data safety, and permissions
- Checking ads, IAP, subscriptions, and store listing accuracy
- Writing reviewer notes and running pre-submission checks

**Key capabilities:**

- Policy compliance checklist for restricted content and deceptive UX
- Data Safety form alignment with SDKs and permissions
- Permission discipline and runtime request patterns
- Target SDK and background work hygiene
- Store listing accuracy checks for screenshots and claims
- Monetization compliance for subscriptions and trials
- Review notes template and pre-submission test list

**Skill location:** `google-play-store-review/SKILL.md`

**Reference files:** `references/review-checklist.md`

---

### 2. Multi-Tenant SaaS Architecture

**Focus:** Production-grade multi-tenant platform patterns

**When to use:**

- Designing multi-tenant SaaS platforms
- Implementing authentication and authorization
- Ensuring strict tenant isolation
- Building admin panels and customer portals
- Implementing audit trails and compliance features

**Key capabilities:**

- Zero-trust security architecture
- Three-panel separation (Tenant App, Admin Panel, Customer Portal)
- Comprehensive permission models
- Data isolation patterns
- Audit and compliance frameworks
- API design principles
- Operational safeguards

**Skill location:** `multi-tenant-saas-architecture/SKILL.md`

---

### 2. Modular SAAS Architecture

**Focus:** Building SAAS platforms with pluggable business modules

**When to use:**

- Designing SAAS with optional features/modules (Advanced Inventory, Restaurant, Pharmacy)
- Implementing per-tenant module enable/disable functionality
- Building module marketplaces with billing integration
- Ensuring modules can be added/removed without breaking the system
- Creating independent modules with clean interfaces

**Key capabilities:**

- Module independence patterns (self-contained modules)
- Graceful degradation when modules are disabled
- Per-tenant module subscriptions and billing
- Dynamic navigation based on enabled modules
- Module registry and dependency management
- Database design for modular systems
- Testing strategies for module isolation
- Event-driven module communication

**Skill location:** `modular-saas-architecture/SKILL.md`

---

### 3. Feature Planning

**Focus:** Complete feature development from specification to implementation

**When to use:**

- Planning new features from requirements to code
- Creating structured specifications with user stories
- Breaking down features into detailed implementation plans
- Test-driven development workflows
- Multi-step feature development

**Key capabilities:**

- **Phase 1 - Specification:** User stories, acceptance criteria, technical constraints, data modeling
- **Phase 2 - Implementation:** Bite-sized task breakdown (2-5 minute steps), TDD workflow, exact file paths
- Complete code examples and testing instructions
- DRY, YAGNI, and best practice adherence
- Token cost analysis and architecture decision framework

**Skill location:** `feature-planning/SKILL.md`

---

### 4. Update Claude Documentation

**Focus:** Efficiently update project documentation files

**When to use:**

- Adding new features or removing existing ones
- Changing project architecture or design patterns
- Updating dependencies or tech stack
- Modifying API endpoints or database schema
- Restructuring project directories
- Changing development workflows

**Key capabilities:**

- Systematic documentation update workflow
- Documentation dependency mapping
- Cross-reference verification
- Time-saving batch update techniques
- Consistency checking across all docs
- Handles: README.md, PROJECT_BRIEF.md, TECH_STACK.md, ARCHITECTURE.md, docs/API.md, docs/DATABASE.md, CLAUDE.md

**Skill location:** `update-claude-documentation/SKILL.md`

---

### 5. Dual Auth RBAC

**Focus:** Dual authentication (Session + JWT) with role-based access control

**When to use:**

- Building multi-tenant SaaS with web + API access
- Implementing authentication for web UI + mobile apps
- Need role-based permissions with tenant isolation
- Require token revocation capability
- Support multiple device sessions per user

**Key capabilities:**

- Session-based auth for web UI (stateful)
- JWT-based auth for API/mobile (stateless)
- RBAC with franchise/tenant-scoped permissions
- Password security (Argon2ID + salt + pepper)
- Token refresh and revocation
- Multi-tenant isolation
- Account protection (lockout, rate limiting)
- Language-agnostic patterns (PHP, Node, Python, Go)

**Skill location:** `dual-auth-rbac/SKILL.md`

---

### 6. Web App GUI Design

**Focus:** Professional web app UIs using commercial templates (with optional bespoke aesthetics)

**When to use:**

- Building CRUD interfaces, admin panels, dashboards
- Data management UIs needing professional look
- Need consistent component patterns fast
- Web applications (NOT marketing sites)

**Key capabilities:**

- Tabler (Bootstrap 5.3.0) base framework
- Mandatory SweetAlert2 for all dialogs (NO native alert/confirm)
- DataTables with Bootstrap 5 integration
- Modular architecture (includes/head.php, topbar.php, footer.php, foot.php)
- Bootstrap Icons only (bi-\*)
- Flatpickr auto-applied date pickers
- Select2 for enhanced selects
- Clone seeder-page.php template pattern
- Mobile-first responsive design
- Complete utility functions (formatCurrency, formatDate, escapeHtml, debounce)

**Skill location:** `webapp-gui-design/SKILL.md`

---

### 7. Skill Creator

**Focus:** Creating effective skills that extend Claude's capabilities

**When to use:**

- Creating a new skill from scratch
- Updating existing skills to follow best practices
- Understanding skill structure and design patterns
- Learning progressive disclosure and resource organization

**Key capabilities:**

- Skill creation process (understand, plan, initialize, edit, package, iterate)
- Progressive disclosure design (metadata → SKILL.md → bundled resources)
- Resource organization (scripts/, references/, assets/)
- Description field as triggering mechanism
- Best practices for concise, effective skills
- Validation and packaging workflows

**Skill location:** `skills/skill-writing/SKILL.md`

**Note:** This is the authoritative guide for creating new skills. Consult this skill before adding new skills to the repository.

---

### 8. Skill Safety Audit

**Focus:** Scan skills for unsafe or malicious instructions before acceptance

**When to use:**

- Any new skill added to the repository
- Any third-party skill update or import
- Any skill with new setup steps or external dependencies

**Key capabilities:**

- Detects unsafe install commands and remote scripts
- Flags credential harvesting or secret handling
- Verifies alignment with project security policies
- Standard audit workflow and required reporting

**Skill location:** `skill-safety-audit/SKILL.md`

---

### 9. API Error Handling

**Focus:** Comprehensive error response system for PHP REST APIs

**When to use:**

- Building PHP REST APIs requiring consistent error formatting
- Need specific error message extraction from database exceptions
- Handling validation errors with field-level detail
- Integrating frontend error display with SweetAlert2
- Implementing business rule enforcement via database triggers
- Require request tracking for debugging

**Key capabilities:**

- Standardized JSON response envelope (success/error structure)
- HTTP status code mapping (400, 401, 403, 404, 409, 422, 429, 500, 503)
- PDOException parsing and message extraction:
  - SQLSTATE 45000 (user-defined exceptions from triggers)
  - SQLSTATE 23000 (integrity constraints - duplicates, foreign keys)
  - Deadlock detection and handling
- ApiResponse helper class with static methods for all response types
- ExceptionHandler converting all exceptions to standardized API responses
- Custom exception classes (ValidationException, AuthenticationException, etc.)
- API bootstrap file with helper functions
- Frontend ApiClient with automatic SweetAlert2 error display
- Validation error field highlighting
- Request ID tracking for error tracing
- Security considerations (no stack traces in production)

**Skill location:** `api-error-handling/SKILL.md`

**Reference files:** `references/ApiResponse.php`, `references/ExceptionHandler.php`, `references/CustomExceptions.php`, `references/bootstrap.php`

**Examples:** `examples/InvoicesEndpoint.php`, `examples/ApiClient.js`

---

### 10. PHP Modern Standards

**Focus:** Modern PHP development for maintainable, testable, object-oriented code

**When to use:**

- Writing PHP 8+ applications
- Implementing object-oriented architecture
- Ensuring code security and type safety
- Building testable, maintainable systems
- Optimizing PHP performance with generators and SPL
- Following Laravel conventions
- Implementing SOLID principles and design patterns

**Key capabilities:**

- Strict typing and modern type system (union types, intersection types, readonly, never)
- PSR standards compliance (PSR-1, PSR-2, PSR-12, PSR-4)
- Modern PHP 8+ features (enums, attributes, match expressions, named arguments, nullsafe operator)
- Constructor property promotion and readonly classes
- Object-oriented design patterns (SOLID principles, dependency injection, interfaces)
- Comprehensive security patterns (SQL injection prevention, XSS protection, CSRF defense, secure password handling)
- Input validation and sanitization best practices
- Performance optimization (generators for large datasets, SPL data structures, memory management)
- Laravel-specific patterns (Eloquent models, controllers, form requests, repositories, actions)
- Testing patterns and TDD workflows
- Session security and file upload handling
- Command injection prevention and security headers

**Skill location:** `php-modern-standards/SKILL.md`

**Reference files:** `references/security-patterns.md` (comprehensive security guide with examples)

**Examples:** `examples/modern-php-patterns.php` (enums, value objects, repositories, generators), `examples/laravel-patterns.php` (Laravel best practices)

---

### 11. MySQL Best Practices

**Focus:** MySQL 8.x best practices for high-performance SaaS

**When to use:**

- Designing MySQL database schemas for multi-tenant SaaS platforms
- Optimizing slow queries and table structures
- Implementing multi-tenant data isolation patterns
- Building transactional financial systems
- Ensuring data integrity with triggers and foreign keys
- Scaling for high concurrency (Africa-wide platforms)
- Securing databases with encryption and proper user privileges

**Key capabilities:**

- Character set and collation (UTF8MB4 for global support)
- Storage engine best practices (InnoDB with ROW_FORMAT=DYNAMIC)
- Table design: auto-increment primary keys, appropriate data type sizing
- Normalization strategies (1NF, 2NF, 3NF) and strategic denormalization
- Indexing strategy: ESR principle (Equality, Sort, Range) for composite indexes
- Foreign key configuration with appropriate ON DELETE/UPDATE strategies
- Stored procedures with transaction safety and error handling
- Triggers for audit trails, data consistency, and prevention
- Concurrency: transaction isolation levels, row-level locking, deadlock prevention
- Security: user privileges, TDE/SSL encryption, SQL injection prevention, multi-tenant isolation
- Performance optimization: query optimization, covering indexes, statistics, slow query logging
- Partitioning strategies: HASH (tenant), RANGE (date), LIST (region)
- Backup and recovery: binary logging, point-in-time recovery
- Monitoring: connection pools, fragmentation, buffer pool stats
- Complete implementation checklists

**Skill location:** `mysql-best-practices/SKILL.md`

**Reference files:** `references/stored-procedures.sql`, `references/triggers.sql`, `references/partitioning.sql`

**Examples:** `examples/saas-schema.sql` (complete multi-tenant schema)

---

### 12. Report Export (PDF + Print)

**Focus:** Clean, consistent report exports for PDF and browser printing

**When to use:**

- Generating PDF reports using mPDF
- Printing HTML reports from the browser print dialog
- Standardizing header/footer and typography across reports
- Ensuring repeating table headers across pages
- Enforcing date/number formatting rules

**Key capabilities:**

- Shared HTML layout for PDF and print
- Compact header with logo/org details/report title
- Pagination-friendly tables (repeating thead)
- Footer with printed-by/printed-on metadata
- DejaVu Sans for small-font clarity

**Skill location:** `report-print-pdf/SKILL.md`

---

### 13. POS & Sales Entry UI Design

**Focus:** POS, checkout, and sales entry UI patterns for web apps

**When to use:**

- Designing POS or sales entry screens
- Defining component patterns and layouts for sales workflows
- Creating invoice/receipt UI and print standards (80mm, A4)
- Enforcing API-first UI interactions

**Key capabilities:**

- 8-to-80 usability philosophy
- 3-level visual hierarchy and large touch targets
- Progressive disclosure for multi-step flows
- Attention-grabber focus cues at key milestones (invoice, product search, payment)
- API-first interaction rules
- Invoice/receipt output standards and templates

**Skill location:** `pos-sales-ui-design/SKILL.md`

---

### 14. Photo Management

**Focus:** Standardized photo upload, preview, storage, and deletion

**When to use:**

- Building any photo upload flow (DPC, assets, products, staff)
- Implementing image galleries with delete actions
- Enforcing upload limits and auto-upload UX
- Ensuring all uploads are compressed via image-compression skill

**Key capabilities:**

- Client-side compression requirement
- Minimal auto-upload UX
- Permission-gated delete actions
- Tenant-safe storage and deletion

**Skill location:** `photo-management/SKILL.md`

---

### 15. Doc Architect

**Focus:** Automated Triple-Layer AGENTS.md documentation

**When to use:**

- Standardizing project documentation
- Generating AGENTS.md files (Root, Data, Planning)
- Creating structured documentation baselines for new projects

**Key capabilities:**

- Workspace scanning to identify tech stack and directories
- Template-driven generation for Root/Data/Planning AGENTS.md
- Reusable domain constraints via logic library

**Skill location:** `doc-architect/SKILL.md`

---

### 16. Manual Guide

**Focus:** End-user manuals and reference guides (not AI agent docs)

**When to use:**

- Documenting a feature for users
- Writing a user manual for a module
- Syncing reference guides

**Key capabilities:**

- Contextual discovery from plans, schema, code, and docs

---

### 17. Inventory Management

**Focus:** Implementation-grade stock and inventory controls for multi-location distribution networks

**When to use:**

- Building product master data with multi-warehouse support
- Designing costing, stock-on-hand, and BOM flows
- Integrating POS/receiving transactions into inventory valuations
- Enforcing bookkeeping rules (FIFO, shrinkage allowances, journal entries)
- Adding new inventory reports or dashboards

**Key capabilities:**

- Tenant-aware product catalog with category hierarchy, units, and conversion factors
- Movement tracking for purchases, sales, transfers, adjustments, and returns
- BOM/routing sequencing with inventory reservation and validation
- Shrinkage periodic close, FIFO cost roll-up, and stock valuation calculations
- Reporting patterns (aging, variances, stock take, adjustments) plus required SQL safeguards (franchise_id filtering, group-by with MAX)
- Storyboard for bringing inventory updates to downstream users (finance, operations, compliance)

**Skill location:** `inventory-management/SKILL.md`

**Reference files:** `inventory-management/references/inventory-playbook.md`

- Dual-workflow guide structure (overview, steps, technical reference, edge cases)
- Professional instructional tone with workflow comparisons

**Skill location:** `manual-guide/SKILL.md`

---

### 18. Custom Sub-Agents

**Focus:** Analyzing codebases, planning, creating, organizing, and documenting custom AI sub-agents for VS Code integration

**When to use:**

- Analyzing codebases to determine sub-agent needs and architecture
- Planning sub-agent implementation and integration strategies
- Creating new AI agents or code assistants
- Organizing agent code, config, and documentation
- Ensuring compatibility with GitHub Copilot and Claude in VS Code
- Building self-contained agent modules
- Establishing agent development standards
- Deciding between sub-agents vs single LLM approaches

**Key capabilities:**

- Codebase analysis framework for identifying sub-agent opportunities
- Decision criteria for sub-agents vs single LLM usage
- Complete folder structure per agent (code, config, docs, tests)
- VS Code integration requirements (chat.customAgentInSubagent.enabled)
- Self-contained agent organization (agent.js, config.json, README.md)
- Comprehensive documentation templates
- Testing and validation frameworks
- Multi-language support (Node.js, Python, PHP, TypeScript)
- Reference guide with detailed examples
- Context window optimization strategies
- Cross-agent integration and communication patterns

**Skill location:** `custom-sub-agents/SKILL.md`

---

### 19. SaaS Seeder

**Focus:** Bootstrap a new SaaS repo from the seeder template

**When to use:**

- Preparing a new SaaS repository from the template
- Creating the database and seeding auth/RBAC baseline
- Importing existing schema dumps before feature development

**Key capabilities:**

- Prompt for MySQL credentials and database name
- Create database and import database/schema SQL dumps
- Run auth/RBAC migration and seed baseline roles
- Seed demo franchise and default super user
- Verify first login readiness

**Skill location:** `saas-seeder/SKILL.md`

**Alias:** seeder-script

---

### 20. Vibe Security Skill

**Focus:** Secure coding practices for web applications

**When to use:**

- Working on any web application (frontend, backend, APIs)
- Implementing authentication, authorization, or data access
- Handling user input, file uploads, redirects, or third-party integrations

**Key capabilities:**

- Defense-in-depth security checklist
- Access control and IDOR prevention
- XSS, CSRF, SSRF, SQLi, XXE, and upload hardening
- Secure headers and safe error handling
- Secret management and data exposure prevention

**Skill location:** `vibe-security-skill/SKILL.md`

---

### 21. GIS Mapping (Leaflet-First)

**Focus:** Leaflet-first GIS mapping, location selection, and geofencing patterns

**When to use:**

- Adding interactive maps to web applications
- Capturing customer/asset/farm locations in GIS-enabled workflows
- Enforcing geo-fencing and boundary validation
- Building map views with filters, legends, and clustering

**Key capabilities:**

- Leaflet-first setup with proper tile provider attribution
- Marker and polygon selection patterns
- Client + server geo-fence validation (point-in-polygon)
- Performance guidance (clustering, bounding boxes, debouncing)

**Skill location:** `gis-mapping/SKILL.md`

**Sub-skill:** `gis-mapping/geofencing.md`

---

### 22. Markdown Lint Cleanup

**Focus:** Remove markdown lint warnings and normalize documentation formatting

**When to use:**

- After editing documentation files
- When markdown lint warnings appear
- Before publishing or sharing docs

**Key capabilities:**

- Enforces proper headings (no bold-only headings)
- Adds blank lines around lists and fences
- Adds language tags to code fences
- Standardizes markdown spacing with minimal content changes

**Skill location:** `markdown-lint-cleanup/SKILL.md`

## Installation

### Option 1: Use Skills Directly

Skills can be referenced in your Claude Code session using the skill invocation syntax.

```bash
# In your Claude Code session
/skill path/to/skills/webapp-gui-design
```

### Option 2: Clone Repository

Clone this repository to a central location and reference skills as needed:

```bash
git clone <your-repo-url> ~/claude-skills
cd ~/claude-skills
```

### Option 3: Symlink to Projects

Create symlinks in your projects to access skills:

```bash
# In your project directory
ln -s ~/claude-skills/webapp-gui-design ./skills/webapp-gui-design
```

## Usage

### Loading a Skill in Claude Code

When working on a task that aligns with a specific skill, invoke it:

```bash
# Example: Using web app GUI design skill
/skill webapp-gui-design
```

Claude will load the skill instructions and apply that expertise to your task.

**Security baseline (required for web apps):**

For any web application work, always load `vibe-security-skill` alongside the primary skill to ensure secure coding practices are applied.

### Skill Invocation Examples

**Creating a distinctive landing page:**

```text
User: "Create a dashboard UI for a fintech startup with a bold aesthetic"
Claude: [Loads webapp-gui-design skill]
[Applies optional frontend design direction within the web app]
```

**Implementing multi-tenant permissions:**

```text
User: "Help me design the permission model for our SaaS platform"
Claude: [Loads multi-tenant-saas-architecture skill]
[Applies three-panel architecture, zero-trust patterns, audit trails]
```

**Planning a complex feature:**

```text
User: "I need to implement user authentication with OAuth"
Claude: [Loads feature-planning skill]
[Creates spec with user stories, then detailed implementation plan with TDD workflow]
```

### Combining Skills

Skills can work together for comprehensive solutions:

```text
1. Use vibe-security-skill to establish the security baseline
2. Use feature-planning to create specification and implementation strategy
3. Use multi-tenant-saas-architecture for backend patterns
4. Use webapp-gui-design for UI components
```

## Skill Development

### Creating a New Skill

**IMPORTANT:** Before creating a new skill, consult the **Skill Creator** skill (`skills/skill-writing/SKILL.md`) for comprehensive guidance on skill creation best practices, structure, and workflow.

Each skill follows a standard structure:

```text
skill-name/
├── SKILL.md             # Main skill instructions (max 500 lines)
├── scripts/             # Optional: Executable code for deterministic tasks
├── references/          # Optional: Documentation loaded as needed
└── assets/              # Optional: Files used in output (templates, images)
```

**Key principles from Skill Creator:**

- Description field acts as triggering mechanism (include all "when to use" info)
- Progressive disclosure: metadata → SKILL.md → bundled resources
- Assume Claude is already smart (only add context Claude doesn't have)
- No extraneous documentation (no README.md, CHANGELOG.md, etc.)
- Keep SKILL.md under 500 lines
- Use imperative/infinitive form

### Skill File Format

Skills use YAML frontmatter followed by markdown content:

```markdown
---
name: skill-name
description: Brief description of what this skill does and when to use it
---

# Skill Name

## Overview

Detailed explanation of the skill's purpose and capabilities.

## When to Use

Clear guidelines on when to invoke this skill.

## Key Patterns

Detailed patterns, code examples, and best practices.

## Examples

Practical examples of using the skill.
```

### Documentation Standards (MANDATORY)

**CRITICAL:** ALL markdown files (.md) created in skills and projects MUST follow strict standards:

✅ **500-line hard limit for ALL .md files** - No exceptions

- SKILL.md: Max 500 lines
- Plan docs: Max 500 lines per file
- Specs: Max 500 lines per file
- Manuals: Max 500 lines per page
- Reference docs: Max 500 lines each
- Any other .md: Max 500 lines

✅ **Two-tier structure** (Required)

- **Tier 1:** High-level TOC/index (200-300 lines)
- **Tier 2:** Deep dive topics (max 500 lines each)

✅ **Smart subdirectory grouping**

- Module-based, type-based, or workflow-based
- Logical organization improves AI comprehension

✅ **Regular grooming** - Improves session bootstrapping and reduces token costs

📖 **See `skills/doc-standards.md` for complete requirements**

### Skills Checklist

#### Structure Requirements

✅ **One SKILL.md per skill** (required, max 500 lines)
✅ **Keep skills one level deep** in /skills/ directory
✅ **Subdirectories for details:** references/, documentation/, examples/ (each file max 500 lines)
✅ **Self-contained:** No dependencies between skills

**Example structure:**

```text
skills/skill-name/
├── SKILL.md             # Main patterns (max 500 lines)
├── references/          # Database schemas, data models (max 500 lines each)
├── documentation/       # Detailed guides (max 500 lines each)
└── examples/            # Code examples, templates
```

#### SKILL.md Essentials

✅ **500-line hard limit for ALL .md files** (enforced strictly)
✅ **Scannable by AI:** Clear headings, bullet points, specific commands
✅ **Focus on core patterns** applicable to 75-90% of use cases
✅ **Avoid generic tasks** AI already knows (basic CRUD, standard patterns)
✅ **Move details to subdirectories** (schemas, verbose guides, examples)
✅ **Frontmatter with name + description** (description acts as trigger)
✅ **Reference subdirectory files** in SKILL.md (so Claude knows they exist)
✅ **Applies to ALL docs created by skills** (plans, specs, manuals, guides)

#### Usage with Claude Code CLI

✅ **Explicitly mention in prompt:** "Using webapp-gui-design, create..."
✅ **Only mentioned skills get loaded** (saves tokens/credits)
✅ **Multiple skills work:** "Using skills/skill-1 and skill-2..."
✅ **Document in CLAUDE.md** which skill to use for what task

#### When Skills Are Worth Creating

✅ **Repeatable patterns** across multiple projects
✅ **Company/domain-specific knowledge** (multi-tenant patterns, industry requirements)
✅ **Complex workflows** (deployment procedures, testing patterns)
✅ **Code you re-explain often** (specific configs, isolation strategies)

#### When NOT to Create Skills

❌ **Generic programming help** (Claude handles natively)
❌ **One-off features** or experimental ideas
❌ **Frequently changing code** (too volatile for a skill)
❌ **Code style/linting rules** (use actual linters instead)

#### Common Mistakes to Avoid

❌ **Don't load all skills globally** (wastes tokens)
❌ **Don't stuff CLAUDE.md** with unrelated instructions
❌ **Don't create skills for generic tasks**
❌ **Don't nest skills** more than one level deep

### Best Practices for Skill Design

1. **Clear Scope:** Each skill should have a well-defined domain
2. **Actionable Guidance:** Provide concrete patterns, not abstract concepts
3. **Code Examples:** Include complete, working code samples
4. **Context-Aware:** Help Claude understand when to apply the skill
5. **Best Practices:** Encode proven patterns and anti-patterns
6. **Maintainable:** Keep skills focused and easy to update
7. **Token-Efficient:** Only load when explicitly needed

### Adding Your Skill

**Recommended workflow** (from Skill Creator):

1. **Understand**: Gather concrete examples of how the skill will be used
2. **Plan**: Identify reusable contents (scripts, references, assets)
3. **Initialize**: Run `scripts/init_skill.py <skill-name>` (if available)
4. **Implement**: Create bundled resources and write SKILL.md
5. **Package**: Run `scripts/package_skill.py <path/to/skill>` (if available)
6. **Audit**: Run `skill-safety-audit` on the new/updated skill
7. **Document**: Update README.md, PROJECT_BRIEF.md, and CLAUDE.md
8. **Commit**: Git commit and push

**Manual workflow** (if scripts unavailable):

1. Create directory: `your-skill-name/`
2. Write `SKILL.md` with frontmatter (name, description) and body (<500 lines)
3. Add bundled resources: scripts/, references/, assets/ (as needed)
4. Run `skill-safety-audit` on the new/updated skill
5. Update README.md, PROJECT_BRIEF.md, CLAUDE.md
6. Commit and push

**See `skills/skill-writing/SKILL.md` for complete guidance.**

---

## 🤖 AI-Assisted Development Skills (New in v3.1)

**Purpose:** Skills that enhance Claude Code's ability to help you develop software by enforcing patterns, preventing errors, and optimizing AI-assisted workflows.

### AI-Assisted Development

**Focus:** Orchestrating multiple AI agents in software development workflows

**When to use:**

- Coordinating multiple AI agents on a single project
- Planning complex features with AI assistance
- Setting up multi-agent development pipelines
- Optimizing AI-assisted development processes

**Key capabilities:**

- 5 orchestration strategies (Sequential, Parallel, Conditional, Looping, Retry)
- 3 AI-specific patterns (Agent Handoff, Fan-Out/Fan-In, Human-in-the-Loop)
- Real-world examples from MADUUKA and BRIGHTSOMA applications
- 30-75% faster development through parallelization
- Complete references for strategies, patterns, and practical examples

**Skill location:** `ai-assisted-development/SKILL.md`

---

### AI Error Prevention

**Focus:** Error prevention strategies for AI-assisted development (Trust But Verify)

**When to use:**

- Working with Claude to generate code (use always!)
- Want to minimize wasted tokens on wrong solutions
- Need to catch Claude's mistakes early
- Developing production-ready code with AI

**Key capabilities:**

- **7 prevention strategies:** Verification-First, Test-Driven Validation, Specification Matching, Incrementalism, Dual Approach, Fallback Code, Documentation Validation
- **Common failure modes:** Hallucination, Incomplete Solutions, Misunderstanding, Lazy Solutions, Wrong Patterns
- **App-specific checklists:** MADUUKA, MEDIC8, BRIGHTSOMA, DDA, CROWNPOINT
- **Token savings:** 50-75% reduction in wasted tokens through early error detection
- Prevents errors BEFORE they happen by changing HOW you interact with Claude

**Skill location:** `ai-error-prevention/SKILL.md`

---

### Orchestration Best Practices

**Focus:** The 10 Commandments of Orchestration for multi-step workflows

**When to use:**

- Generating code for multi-step workflows
- Agent coordination tasks
- Complex process implementation
- System design with multiple components

**Key capabilities:**

- **The 10 rules:** Define steps, identify dependencies, validate inputs, handle errors, validate outputs, log progress, document thoroughly, test comprehensively, have fallbacks, consider parallelization
- Complete code examples showing good vs bad patterns
- Verification checklist for all generated code
- Anti-patterns guide to avoid common mistakes
- Ensures consistent code structure across all AI-generated code

**Skill location:** `orchestration-best-practices/SKILL.md`

---

### AI Error Handling

**Focus:** 5-layer validation stack for AI-generated code

**When to use:**

- Validating AI-generated code before production
- Ensuring code correctness and security
- Building production-ready code with AI
- Need systematic verification approach

**Key capabilities:**

- **5 validation layers:** Syntax, Requirements, Testing, Security, Documentation
- Quality scoring system (0-100 with 80% acceptance threshold)
- Validation loop with max 3 iterations
- Automated recovery strategies for each failure type
- Integration with ai-error-prevention for complete workflow

**Skill location:** `ai-error-handling/SKILL.md`

---

### Reference Guides

#### Prompting Patterns Reference

**Focus:** 10 essential patterns for better AI instructions

**Key capabilities:**

- Clear Task + Context + Constraints, Chain-of-Thought, Few-Shot Learning, Role-Based, Structured Output, etc.
- Reduces clarification questions by 50%
- Improves first-time-right code by 60%
- 4x faster implementation with better prompts

**File:** `prompting-patterns-reference.md`

---

#### Orchestration Patterns Reference

**Focus:** Comprehensive guide for coordinating multiple agents/tasks

**Key capabilities:**

- 5 orchestration types with real-world examples
- 4 core patterns (Map-Reduce, Pipeline, Fan-Out/Fan-In, Circuit Breaker)
- Decision trees and complexity vs performance analysis
- 30-50% faster execution through smart orchestration

**File:** `orchestration-patterns-reference.md`

---

#### Encoding Patterns into Skills

**Focus:** How to create skills that automatically enforce patterns

**Key capabilities:**

- Formula: Rules + Examples + Checklists + Decision Trees
- Pattern encoding templates
- Skill effectiveness and iteration strategies
- Makes Claude automatically follow your patterns

**File:** `encoding-patterns-into-skills.md`

---

### How AI Skills Work Together

```
REQUEST PREPARATION (ai-error-prevention)
├─ Use prompting patterns
├─ Break into small steps
└─ Clear task + context + constraints
    ↓
CLAUDE GENERATES CODE
    ↓
IMMEDIATE VERIFICATION (ai-error-prevention)
├─ Verification-First strategy
├─ Test-Driven Validation
└─ Specification Matching
    ↓
STRUCTURE CHECK (orchestration-best-practices)
├─ Steps clearly defined?
├─ Dependencies identified?
└─ Error handling present?
    ↓
VALIDATION (ai-error-handling)
├─ 5-layer validation stack
└─ Quality threshold >= 80/100
    ↓
ACCEPTANCE OR ITERATION
└─ All checks passed? → USE CODE ✓
```

**Result:** Production-ready code, 50-75% fewer wasted tokens, higher quality output

---

## Contributing

We welcome contributions! To add or improve skills:

### Adding a New Skill

1. Fork this repository
2. Create a new branch: `git checkout -b skill/your-skill-name`
3. Create skill directory and files
4. Update README.md and PROJECT_BRIEF.md
5. Submit a pull request

### Improving Existing Skills

1. Fork and create a feature branch
2. Make improvements with clear documentation
3. Test the skill with Claude Code
4. Submit a pull request with examples

### Contribution Guidelines

- **Quality over quantity:** Each skill should provide real value
- **Clear documentation:** Include usage examples and guidance
- **Test thoroughly:** Verify skill behavior with Claude Code
- **Maintain consistency:** Follow existing skill structure
- **Provide context:** Explain when and why to use the skill

## Repository Structure

```text
skills/
├── android-development/             # Android dev standards
│   ├── SKILL.md
│   └── references/                  # 12 topic-specific guides
├── android-tdd/                     # Android TDD methodology
│   ├── SKILL.md
│   └── references/                  # 5 deep-dive guides
├── jetpack-compose-ui/              # Compose UI standards
│   ├── SKILL.md
│   └── references/                  # 5 deep-dive guides
├── android-data-persistence/        # Data persistence & sync
│   ├── SKILL.md
│   └── references/                  # 4 deep-dive guides
├── google-play-store-review/        # Play Store review readiness
│   ├── SKILL.md
│   └── references/
├── multi-tenant-saas-architecture/  # SaaS architecture skill
│   └── SKILL.md
├── feature-planning/             # Complete feature planning skill (spec + implementation)
│   ├── SKILL.md
│   ├── references/               # Educational guides
│   ├── templates/                # Spec templates
│   ├── protocols/                # Naming conventions
│   └── spec-references/          # Spec examples
├── update-claude-documentation/  # Documentation maintenance skill
│   └── SKILL.md
├── doc-architect/                # Triple-Layer AGENTS.md generator
│   └── SKILL.md
├── manual-guide/                # End-user manuals and reference guides
│   └── SKILL.md
├── dual-auth-rbac/               # Dual authentication + RBAC skill
│   ├── SKILL.md
│   └── references/
│       └── schema.sql
├── webapp-gui-design/            # Web app GUI design skill
│   └── SKILL.md
├── report-print-pdf/             # Report export via PDF + print + auto-print
│   └── SKILL.md
├── pos-sales-ui-design/          # POS & sales entry UI design
│   ├── SKILL.md
│   └── references/
│       └── universal-sales-ui-design.md
├── photo-management/             # Photo upload & gallery patterns
│   └── SKILL.md
├── skill-safety-audit/            # Skill safety scanning and audit
│   └── SKILL.md
├── markdown-lint-cleanup/          # Markdown lint cleanup and formatting
│   └── SKILL.md
├── skills/
│   └── skill-writing/            # Skill creator (meta-skill)
│       └── SKILL.md
├── api-error-handling/           # API error handling skill
│   ├── SKILL.md
│   ├── references/
│   │   ├── ApiResponse.php
│   │   ├── ExceptionHandler.php
│   │   ├── CustomExceptions.php
│   │   └── bootstrap.php
│   └── examples/
│       ├── InvoicesEndpoint.php
│       └── ApiClient.js
├── mysql-best-practices/         # MySQL best practices skill
│   ├── SKILL.md
│   ├── references/
│   │   ├── stored-procedures.sql
│   │   ├── triggers.sql
│   │   └── partitioning.sql
│   └── examples/
│       └── saas-schema.sql
├── PROJECT_BRIEF.md              # Quick project overview
├── README.md                     # This file
└── CLAUDE.md                     # Claude Code specific guide
```

## SDLC Documentation Skills (New in v3.2)

**Purpose:** Generate standardized SDLC documentation across all 4 phases. Each skill covers one SDLC category with detailed templates tailored to the tech stack (PHP 8+, MySQL 8.x, Kotlin/Compose, multi-tenant SaaS).

### SDLC Planning

**Focus:** Planning & Management documentation (7 document types)

**When to use:** Starting a new project, establishing governance, creating the planning baseline before development.

**Documents:** Project Vision & Scope, Software Development Plan (SDP), Configuration Management Plan (SCMP), Quality Assurance Plan, Risk Management Plan, Software Requirements Specification (SRS), Feasibility Study Report

**Skill location:** `sdlc-planning/SKILL.md` + `templates/` (7 template files)

---

### SDLC Design

**Focus:** Design & Development documentation (6 document types)

**When to use:** Translating requirements into technical architecture, guiding development teams.

**Documents:** System Design Document (SDD), Technical Specification, Interface Control Document (ICD), Database Design Document, Code Documentation Standards, API Documentation

**Skill location:** `sdlc-design/SKILL.md` + `templates/` (6 template files)

---

### SDLC Testing

**Focus:** Testing & Quality documentation (5 document types)

**When to use:** Establishing testing strategy, creating test documentation, conducting quality validation.

**Documents:** Software Test Plan (STP), Test Case Specifications, Validation & Verification Plan (SVVP), Validation Test Report (SVTR), Peer Review/Inspection Report

**Skill location:** `sdlc-testing/SKILL.md` + `templates/` (5 template files)

---

### SDLC User & Deployment

**Focus:** User & Deployment documentation (6 document types)

**When to use:** Preparing software for end-users, system administrators, and operations teams.

**Documents:** Software User Manual (SUM), Operations/Deployment Manual, Training Materials, Release Notes, Maintenance Manual, README File

**Skill location:** `sdlc-user-deploy/SKILL.md` + `templates/` (6 template files)

---

### How SDLC Skills Work Together

```
sdlc-planning (Vision, SRS, SDP, QA Plan, Risk Plan, SCMP, Feasibility)
    |
    v  [Requirements approved]
sdlc-design (SDD, Tech Spec, ICD, DB Design, API Docs, Code Docs)
    |
    v  [Architecture defined]
sdlc-testing (Test Plan, Test Cases, V&V Plan, Test Report, Peer Reviews)
    |
    v  [Quality validated]
sdlc-user-deploy (User Manual, Ops Manual, Training, Release Notes, Maintenance, README)
```

**Total:** 24 document templates across 4 skills, all tailored to the multi-tenant SaaS tech stack.

---

### Implementation Status Auditor

**Focus:** Comprehensive project audit producing both status report and completion blueprint

**When to use:**

- Auditing a project to see what's been accomplished
- Identifying gaps between plans and implementation
- Generating a structured completion roadmap
- Cross-referencing database schema against requirements
- Validating cross-platform/API integration integrity

**Key capabilities:**

- **5 audit pillars:** Schema audit, Implementation gap analysis, Cross-platform integrity, Technical risk assessment, Completion blueprint
- **Structured output:** 7+ files in `docs/implementation/review-{date}/` directory
- **Feature classification:** Complete, Partial, Phantom (zero footprint), Undocumented
- **Cross-skill integration:** Maps every gap to a specific skill for resolution
- **Iterative drilling:** Deep dive into modules, API payloads, test coverage
- **Re-audit comparison:** Track progress between audit runs

**Skill location:** `implementation-status-auditor/SKILL.md`

**Reference files:** `references/audit-checklist.md`, `references/gap-analysis-patterns.md`, `references/drill-down-templates.md`

---

### Plan Implementation — Autonomous Executor

**Focus:** Execute feature plans autonomously from start to finish with TDD and validation

**When to use:**

- Implementing plans created by `feature-planning` skill
- User says "implement the plan", "execute the plan", or "build this"
- Autonomous end-to-end code generation with testing
- Any multi-task implementation requiring structured execution

**Key capabilities:**

- **Autonomous execution:** No stopping, no permission-seeking, continuous implementation
- **TDD enforcement:** RED (failing test) → GREEN (minimum code) → VALIDATE → REFACTOR → NEXT
- **5-layer validation:** Syntax, Requirements, Tests, Security, Documentation on every task
- **10 Commandments:** Enforces orchestration best practices on all execution
- **Error recovery:** 3-attempt autonomous fix, escalation ladder, output truncation recovery
- **Progress tracking:** Real-time logging, plan status updates, completion reports
- **Cross-skill integration:** References 14 skills for domain-specific patterns
- **Feedback loop:** Triggers `implementation-status-auditor` for post-execution verification

**Skill location:** `plan-implementation/SKILL.md`

**Reference files:** `references/execution-loop-detail.md`, `references/error-recovery-patterns.md`, `references/progress-tracking.md`

---

## Roadmap

### Planned Skills

- **Microservices:** Service mesh, event-driven architecture

### Version History

- **v1.0.0** (January 2026)
  - Initial release
  - Web App GUI Design skill
  - Multi-Tenant SaaS Architecture skill
  - Writing Plans skill

## License

Individual skills may have their own licenses. Check each skill directory for specific licensing information.

This repository structure and documentation: MIT License

## Support

For questions, issues, or suggestions:

- Open an issue on GitHub
- Review existing skills for examples
- Check [CLAUDE.md](CLAUDE.md) for Claude Code specific guidance

## Acknowledgments

These skills are built from real-world project experience and industry best practices. Special thanks to the Claude Code community for feedback and contributions.

---

**Maintained by:** Peter Bamuhigire
**Version:** 1.0.0
**Last Updated:** January 2026
**Status:** Active Development
