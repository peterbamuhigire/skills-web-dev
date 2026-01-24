# Skills Collection - Project Brief

## Overview

A curated collection of reusable Claude Code skills designed to accelerate development across multiple projects. Each skill provides specialized expertise in specific domains, from frontend design to multi-tenant architecture.

## Purpose

Provide consistent, battle-tested patterns and workflows that can be seamlessly integrated into any project using Claude Code, eliminating repetitive architectural decisions and ensuring best practices.

## Current Skills

### 1. Frontend Design

**Domain:** UI/UX Development
**Purpose:** Create distinctive, production-grade frontend interfaces that avoid generic AI aesthetics
**Use Cases:** Web components, landing pages, dashboards, React components, HTML/CSS layouts
**Key Features:** Bold aesthetic choices, creative typography, advanced animations, context-specific design

### 2. Multi-Tenant SaaS Architecture

**Domain:** Backend Architecture
**Purpose:** Production-grade multi-tenant SaaS platform patterns with security and isolation
**Use Cases:** Building SaaS platforms, implementing permissions, ensuring tenant isolation
**Key Features:** Zero-trust security, three-panel architecture, comprehensive audit trails, scalable patterns

### 3. Writing Plans

**Domain:** Development Workflow
**Purpose:** Create comprehensive, executable implementation plans for multi-step tasks
**Use Cases:** Feature planning, technical specifications, TDD workflows
**Key Features:** Bite-sized tasks, exact file paths, complete code examples, test-driven approach

### 4. Update Claude Documentation

**Domain:** Documentation Maintenance
**Purpose:** Efficiently update project documentation when significant changes occur
**Use Cases:** Feature additions, architecture changes, tech stack updates, API modifications
**Key Features:** Documentation dependency mapping, systematic update workflow, cross-reference verification, consistency checking

### 5. Dual Auth RBAC

**Domain:** Security & Authentication
**Purpose:** Dual authentication system (Session + JWT) with role-based access control
**Use Cases:** Multi-tenant SaaS, web + API authentication, mobile apps, tenant-scoped permissions
**Key Features:** Session + JWT auth, RBAC, Argon2ID passwords, token revocation, multi-tenant isolation, cross-platform

### 6. Web App GUI Design

**Domain:** Frontend Development (Web Applications)
**Purpose:** Professional web app UIs using commercial templates with established component patterns
**Use Cases:** CRUD interfaces, admin panels, dashboards, data management UIs
**Key Features:** Tabler (Bootstrap 5), mandatory SweetAlert2, DataTables, modular architecture (includes), Flatpickr, Select2, seeder-page.php template pattern, Bootstrap Icons only

### 7. Skill Creator

**Domain:** Meta-Skill (Skill Development)
**Purpose:** Guide for creating effective skills with progressive disclosure and proper structure
**Use Cases:** Creating new skills, updating existing skills, understanding skill best practices
**Key Features:** Skill creation process (understand, plan, initialize, edit, package, iterate), progressive disclosure (metadata → SKILL.md → bundled resources), resource organization (scripts/, references/, assets/), description field as trigger, no extraneous files

### 8. API Error Handling

**Domain:** Backend Development (REST APIs)
**Purpose:** Comprehensive, standardized error response system for PHP REST APIs with SweetAlert2 integration
**Use Cases:** Building REST APIs, consistent error formatting, PDOException parsing, validation error handling, frontend error display
**Key Features:** Standardized JSON envelopes (success/error), HTTP status code mapping, PDOException message extraction (SQLSTATE 45000, 23000, deadlocks), ApiResponse helper, ExceptionHandler with specific error parsing, custom exception classes, SweetAlert2 integration, business rule extraction, request ID tracking

### 9. Report Export (PDF + Print)

**Domain:** Reporting
**Purpose:** Clean, consistent report exports for PDF and browser printing
**Use Cases:** Financial PDFs, inventory reports, audit exports, browser printouts
**Key Features:** Shared HTML template for PDF/print, compact header/footer, repeating table headers, DejaVu Sans typography, strict date/number formatting

## Repository Structure

```
skills/
├── frontend-design/
│   └── SKILL.md
├── multi-tenant-saas-architecture/
│   ├── SKILL.md
│   ├── references/
│   │   ├── database-schema.md
│   │   └── permission-model.md
│   └── documentation/
│       └── migration.md
├── writing-plans/
│   └── SKILL.md
├── update-claude-documentation/
│   └── SKILL.md
├── dual-auth-rbac/
│   ├── SKILL.md
│   └── references/
│       └── schema.sql
├── webapp-gui-design/
│   └── SKILL.md
├── pdf-export/
│   └── SKILL.md
├── api-error-handling/
│   ├── SKILL.md
│   ├── references/
│   │   ├── ApiResponse.php
│   │   ├── ExceptionHandler.php
│   │   ├── CustomExceptions.php
│   │   └── bootstrap.php
│   └── examples/
│       ├── InvoicesEndpoint.php
│       └── ApiClient.js
├── skills/
│   └── skill-writing/
│       └── SKILL.md
├── PROJECT_BRIEF.md
├── README.md
└── CLAUDE.md
```

## Tech Stack

- Framework Agnostic (skills apply across tech stacks)
- Focus: Patterns, Architecture, Best Practices
- Compatible with: JavaScript/TypeScript, Python, PHP, Go, etc.

## Target Audience

- Developers using Claude Code across multiple projects
- Teams wanting consistent architectural patterns
- Solo developers building multiple products
- Agencies managing client projects

## Best Practices

**Structure:**

- One SKILL.md per skill (500-line hard limit, strictly enforced)
- Keep skills one level deep in /skills/
- Use subdirectories: references/, documentation/, examples/
- Move detailed content to subdirectories
- Skills are self-contained (no dependencies)

**Content:**

- Scannable by AI: clear headings, bullet points, specific commands
- Focus on core patterns (75-90% of use cases)
- Avoid generic tasks AI already knows
- Move verbose content to subdirectories

**Usage:**

- Explicitly mention skills in prompts: "Using skill-name..."
- Only mentioned skills get loaded (saves tokens)
- Multiple skills: "Using skill-1 and skill-2..."
- Document skill usage in CLAUDE.md

**Create Skills For:**

- Repeatable patterns across projects
- Domain-specific knowledge
- Complex workflows you re-explain often

**Don't Create Skills For:**

- Generic programming tasks
- One-off features
- Frequently changing code
- Code style rules (use linters)

## Maintenance Status

**Active Development** - New skills are continuously added based on project needs

## Quick Links

- [Full Documentation](README.md)
- [Claude Code Guide](CLAUDE.md)
- [Contributing Guidelines](README.md#contributing)

## Version

Current Version: 1.0.0
Last Updated: January 2026
Maintained By: Peter Bamuhigire
