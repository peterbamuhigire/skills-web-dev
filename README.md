# Claude Code Skills Collection

Production-grade skills library for Claude Code covering software architecture, web apps, mobile apps, SaaS, ERP, AI systems, security, UX, databases, and SDLC documentation.

The repository is designed to help Claude Code produce systems that are secure, scalable, maintainable, performance-conscious, and user-centered. It is not just a bag of examples. It is a layered engineering system.

## What Skills Are

Skills are markdown instruction packages that encode reusable engineering judgment:

- when to use a pattern
- how to execute it
- what to avoid
- what quality gates must be met before calling the result production-ready

## Core Baseline

For serious implementation work, start with the repository baseline before loading stack-specific skills:

- `world-class-engineering`
- `system-architecture-design`
- `database-design-engineering`
- `saas-erp-system-design`
- `git-collaboration-workflow`

These skills establish the shared bar for architecture, data modeling, workflow design, release discipline, security, performance, UX, testing, and operability.

## Recommended Load Order

For high-stakes engineering work, load in this order:

```text
world-class-engineering
-> architecture or data baseline skill
-> platform or framework skill
-> security, UX, performance, and validation companion skills
```

Typical baseline choices:

- `system-architecture-design` for module boundaries, contracts, ADRs, failure design
- `database-design-engineering` for schema shape, tenancy, indexing, retention, migration safety
- `saas-erp-system-design` for configurable business workflows, approvals, controls, auditability
- `git-collaboration-workflow` for branch, review, merge, and release discipline

## Skill Categories

### Core System Skills

| Skill | Purpose |
|-------|---------|
| `world-class-engineering` | Shared production-grade engineering bar and release gates |
| `system-architecture-design` | Decomposition, contracts, ADRs, failure design, scaling tradeoffs |
| `database-design-engineering` | Cross-engine data architecture, tenancy, indexing, migration safety, retention |
| `saas-erp-system-design` | Configurable SaaS and ERP workflow design, controls, auditability, extensions |
| `git-collaboration-workflow` | Branch, commit, PR, merge, conflict, and release discipline |

### Architecture And Backend

| Skill | Purpose |
|-------|---------|
| `multi-tenant-saas-architecture` | Tenant isolation, audit trails, SaaS backend patterns |
| `modular-saas-architecture` | Pluggable business modules and per-tenant enablement |
| `dual-auth-rbac` | Session and JWT authentication with role-based access control |
| `api-design-first` | OpenAPI-first REST design, versioning, auth, caching, rate limiting |
| `api-error-handling` | Standardized API errors and response formatting |
| `saas-accounting-system` | Double-entry accounting engine patterns |
| `inventory-management` | Inventory, stock movement, valuation, and multi-location patterns |

### Database

| Skill | Purpose |
|-------|---------|
| `mysql-best-practices` | MySQL production patterns for schema, performance, security, HA |
| `mysql-data-modeling` | Universal entity patterns and business data models |
| `mysql-query-performance` | Query tuning, plans, indexes, and diagnosis |
| `mysql-administration` | Replication, backup, recovery, and operational safety |
| `database-internals` | Storage engine tradeoffs and core internals |
| `database-reliability` | SLOs, migrations, backup verification, incident runbooks |

### Web, Mobile, And Frontend

| Area | Key Skills |
|------|------------|
| Web frontend | `webapp-gui-design`, `form-ux-design`, `responsive-design`, `frontend-performance` |
| Web backend | `php-modern-standards`, `php-security`, `nodejs-development`, `nextjs-app-router` |
| Android | `android-development`, `android-data-persistence`, `android-tdd`, `jetpack-compose-ui` |
| iOS | `ios-development`, `ios-data-persistence`, `ios-tdd`, `swiftui-design` |
| Cross-platform planning | `mobile-saas-planning`, `mobile-reports`, `mobile-report-tables`, `mobile-rbac` |

### Security

| Skill | Scope |
|-------|-------|
| `vibe-security-skill` | Secure coding baseline for web-connected systems |
| `web-app-security-audit` | Structured security review for web apps |
| `php-security` | PHP-specific security patterns |
| `ai-security` | LLM and AI integration security controls |
| `llm-security` | Prompt injection, trust boundaries, output validation |
| `skill-safety-audit` | Safety checks for skills themselves |

### UX, Product Writing, And Design

| Skill | Purpose |
|-------|---------|
| `laws-of-ux` | Named UX laws and design implications |
| `ux-writing` | Microcopy, empty states, errors, loading, confirmations |
| `ux-psychology` | Cognitive foundations for product design |
| `practical-ui-design` | Visual design systems, layout, typography, color |
| `interaction-design-patterns` | Reusable interaction patterns |
| `design-audit` | Structured UI quality review |

### AI And Orchestration

| Skill | Purpose |
|-------|---------|
| `ai-web-apps` | AI-enabled web app patterns, budgets, streaming, tool use |
| `ai-assisted-development` | Multi-agent development workflows |
| `ai-error-handling` | Validation stacks for AI output |
| `ai-error-prevention` | Trust-but-verify workflows |
| `orchestration-best-practices` | Multi-step AI workflow coordination |
| `ai-rag-patterns` | Retrieval-augmented generation patterns |

## Recommended Skill Stacks

- Web application: `world-class-engineering` + `system-architecture-design` + `api-design-first` + `database-design-engineering` + `vibe-security-skill`
- SaaS or ERP platform: `world-class-engineering` + `saas-erp-system-design` + `modular-saas-architecture` + `multi-tenant-saas-architecture` + `database-design-engineering`
- Mobile-backed product: `world-class-engineering` + `system-architecture-design` + `android-development` or `ios-development` + security and persistence skills
- AI-enabled application: `world-class-engineering` + `system-architecture-design` + `ai-web-apps` + `ai-security` + `frontend-performance`

## How To Use

### In Claude Code

Reference skills directly in the prompt:

```text
Use the android-development skill to review this feature.
Use world-class-engineering and system-architecture-design before proposing the backend design.
```

### In Other Projects

Reference the skills from your project-level `CLAUDE.md`:

```markdown
Load these skills from ~/.claude/skills:
- world-class-engineering
- system-architecture-design
- database-design-engineering
- api-design-first
```

## Skill Structure

Each skill should follow this shape:

```yaml
---
name: skill-name
description: Use when ...
---
```

Then include:

- scope and activation clues
- workflow or decision rules
- standards and anti-patterns
- references to deeper files in `references/`

## Repository Standards

- Every markdown file must remain under 500 lines.
- `SKILL.md` should contain execution logic, not textbook-length explanation.
- Deep detail belongs in `references/`.
- Engineering skills should align with `world-class-engineering`.
- New skills should update the top-level repository docs when they materially change the system.

## Repository Stats

- 85+ skills across architecture, web, mobile, AI, security, UX, data, and SDLC
- full-stack coverage for web apps, mobile apps, SaaS, ERP, APIs, and data systems
- layered baseline for architecture, data design, delivery workflow, and production quality

## Maintained By

Peter Bamuhigire

Built with Claude Code for Claude Code.
