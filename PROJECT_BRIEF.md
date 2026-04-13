# Skills Collection - Project Brief

## Overview

A curated collection of reusable Claude Code and Codex skills designed to accelerate development across multiple projects. The repository now includes a shared engineering and management baseline so skills work together as a system for building production-grade web apps, mobile apps, SaaS platforms, ERP systems, APIs, data architectures, and the delivery workflows around them.

## Purpose

Provide consistent, battle-tested patterns and workflows that can be integrated into any Claude Code project, reducing repeated architectural decisions and raising the quality bar across implementation, review, and planning work.

The same repository is now also structured to work as a Codex skills and instruction system without duplicating the skills or relocating them into a different directory layout.

## Strategic Direction

The repository is being shaped around six goals:

- define a shared world-class engineering bar instead of isolated skill-specific advice
- define world-class software development and management, not just implementation detail
- make architecture, data design, security, UX, and delivery workflow reusable across stacks
- convert book knowledge into operational workflows and decision rules
- upgrade skills from reference material into production-grade execution guides
- support end-to-end system generation for web, mobile, SaaS, ERP, backend, and database work

## Core System Skills

- `world-class-engineering` - shared release gates and engineering standards
- `system-architecture-design` - decomposition, contracts, ADRs, failure design, scaling tradeoffs
- `database-design-engineering` - schema design, tenancy, migrations, indexing, retention strategy
- `saas-erp-system-design` - ERP-grade workflow modeling, controls, approvals, and auditability
- `git-collaboration-workflow` - Git delivery discipline for branches, review, conflicts, and release
- `observability-monitoring` - logs, metrics, traces, alerts, SLOs, dashboards, and audit telemetry
- `reliability-engineering` - retries, timeouts, degradation, incident readiness, and recovery-aware design
- `advanced-testing-strategy` - risk-based testing depth and release evidence across systems
- `deployment-release-engineering` - rollout strategy, rollback design, migration-safe shipping, and post-deploy verification
- `distributed-systems-patterns` - consistency, messaging, outbox, saga, idempotency, and cross-service boundaries
- `engineering-management-system` - prioritization, delegation, communication, coaching, and team operating rhythm

## Core Workflow

Default loading order for complex engineering work:

1. `world-class-engineering`
2. `system-architecture-design`, `database-design-engineering`, or `saas-erp-system-design` as needed
3. platform or framework skills
4. security, performance, UX, observability, testing, and release companion skills
5. reliability, distributed-systems, and management skills when system complexity or team scale requires them

## High-Value Existing Skills

### Multi-Tenant SaaS Architecture

- Domain: backend architecture
- Purpose: production-grade tenant isolation and audit-aware SaaS structure
- Use cases: SaaS platforms, tenant-scoped permissions, isolation design

### Modular SaaS Architecture

- Domain: backend architecture and feature management
- Purpose: pluggable business modules enabled or disabled per tenant
- Use cases: modular feature systems, vertical add-ons, per-tenant subscriptions

### API Design First

- Domain: backend and contract design
- Purpose: OpenAPI-first API design with versioning, security, and evolution safety
- Use cases: REST APIs, public APIs, internal service contracts

### Android Development

- Domain: Android engineering
- Purpose: production-grade Kotlin and Compose standards with testing, security, and release discipline
- Use cases: new Android apps, feature development, code reviews

### iOS Development

- Domain: iOS engineering
- Purpose: production-grade Swift and SwiftUI standards with security, testing, and performance rules
- Use cases: new iOS apps, feature development, code reviews

### Vibe Security Skill

- Domain: web application security
- Purpose: secure coding baseline for web-connected applications
- Use cases: web apps, APIs, auth flows, file uploads, security reviews

### Skill Writing

- Domain: meta-skill
- Purpose: create repository-native Claude Code skills with validation-safe frontmatter and strong execution logic
- Use cases: creating new skills, upgrading weak skills, enforcing repository standards

## Repository Shape

The repository is organized as a flat collection of skill folders, each with a `SKILL.md` file and optional `references/`, `scripts/`, or `assets/` directories.

This flat layout is intentional and is the compatibility shape for both Claude Code and Codex.

Examples:

- `world-class-engineering/`
- `system-architecture-design/`
- `database-design-engineering/`
- `saas-erp-system-design/`
- `android-development/`
- `ios-development/`
- `api-design-first/`
- `modular-saas-architecture/`

## Best Practices

- keep each skill focused on one reusable problem space
- keep `SKILL.md` concise and move depth into `references/`
- encode judgment, decision rules, and release gates rather than generic tutorials
- align engineering skills with the shared `world-class-engineering` baseline
- update top-level docs when a new skill changes repository capabilities materially

## Target Audience

- developers using Claude Code across multiple projects
- teams that want shared architecture and implementation standards
- solo builders creating multiple production systems
- agencies and product teams shipping client or internal platforms

## Version

- Current version: 1.2.0
- Last updated: April 2026
- Maintained by: Peter Bamuhigire
