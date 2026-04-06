# Claude Code Skills Collection

Production-grade skills library for [Claude Code](https://claude.com/claude-code) — 60+ skills covering full-stack SaaS development, cross-platform mobile, UI/UX design, security, and SDLC documentation. Distilled from 20+ authoritative books and real-world project experience.

## What Are Skills?

Skills are markdown instruction files that give Claude Code deep expertise in specific domains. Load a skill and Claude follows its patterns, code standards, and architectural decisions — producing consistent, production-quality output across projects.

```
User: "Use the ios-development skill to build a login screen"
Claude: Loads ios-development → follows MVVM + @Observable + async/await patterns → generates Swift code
```

## Skill Categories

### Platform Development

| Platform | Skills | Stack |
|----------|--------|-------|
| **Web Backend** | `php-modern-standards`, `php-security`, `mysql-best-practices` | PHP 8+, MySQL 8.x, Redis |
| **Web Frontend** | `webapp-gui-design`, `form-ux-design`, `image-compression` | Bootstrap 5/Tabler, JS |
| **JavaScript** | `javascript-modern`, `javascript-advanced`, `javascript-patterns`, `javascript-php-integration` | ES6+, Modules, Design Patterns |
| **TypeScript** | `typescript-mastery` | Full type system, generics, React, strict mode, tsconfig |
| **Android** | `android-development`, `jetpack-compose-ui`, `android-data-persistence`, `android-tdd`, `android-biometric-login`, `android-pdf-export` | Kotlin, Compose, Room, Hilt |
| **iOS** | `ios-development`, `ios-architecture-advanced`, `ios-at-scale`, `ios-production-patterns`, `ios-debugging-mastery`, `ios-ai-ml`, `ios-swift-design-patterns`, `ios-networking-advanced`, `ios-uikit-advanced`, `ios-monetization`, `ios-push-notifications`, `ios-swift-recipes`, `ios-stability-solutions`, `swiftui-design`, `swiftui-pro-patterns`, `ios-data-persistence`, `ios-tdd`, `ios-project-setup`, `ios-biometric-login`, `ios-pdf-export`, `ios-bluetooth-printing`, `ios-rbac` | Swift 6, SwiftUI, SwiftData, CoreML |
| **Cross-Platform** | `mobile-saas-planning`, `mobile-custom-icons`, `mobile-reports`, `mobile-report-tables`, `api-pagination` | Shared patterns for Android + iOS |

### Architecture & Backend

| Skill | Purpose |
|-------|---------|
| `multi-tenant-saas-architecture` | Three-panel separation, tenant isolation, audit trails |
| `modular-saas-architecture` | Pluggable business modules (enable/disable per tenant) |
| `dual-auth-rbac` | Session + JWT authentication with role-based access |
| `mobile-rbac` / `ios-rbac` | Permission gates for mobile UI (Android + iOS) |
| `saas-accounting-system` | Double-entry accounting engine for SaaS apps |
| `inventory-management` | Stock movement, BOMs, valuation, multi-location |
| `api-error-handling` | Standardised PHP REST API error responses |
| `saas-seeder` | Bootstrap new SaaS projects from template |

### Database (7 Skills)

| Skill | Purpose |
|-------|---------|
| `mysql-best-practices` | MySQL 8.x production patterns: indexing, EXPLAIN, transactions, security, HA, benchmarking |
| `mysql-data-modeling` | Universal entity patterns: Party model, product hierarchy, order/invoice lifecycle (Silverston) |
| `mysql-query-performance` | EXPLAIN ANALYZE, covering indexes, optimizer hints, histogram stats, Performance Schema |
| `mysql-administration` | GTID replication, InnoDB Cluster, XtraBackup, PITR, ProxySQL, zero-downtime schema changes |
| `mysql-advanced-sql` | Window functions, recursive CTEs, JSON_TABLE, dynamic pivoting, stored procedures, triggers |
| `database-internals` | B-tree, WAL/MVCC, buffer pool, lock types, LSM vs B-tree tradeoffs, CAP theorem applied |
| `database-reliability` | SLOs, expand-contract migrations, backup verification, incident runbooks, chaos engineering |

### JavaScript (4 Skills)

| Skill | Purpose |
|-------|---------|
| `javascript-modern` | ES6+ mastery: modules, async/await, Proxy, generators, WeakMap, AbortController, production fetch wrapper |
| `javascript-advanced` | Closures, prototype chain, OOP with #private fields, functional patterns, event loop, memory management |
| `javascript-patterns` | 10 design patterns: Module, Observer, Factory, Strategy, Command, Repository, Mediator, State Machine |
| `javascript-php-integration` | JS-in-own-files architecture rule, data-* bridge, CSRF flow, $pageScript per-page loading |
| `typescript-mastery` | Full TypeScript: fundamentals, generics, conditional/mapped/template-literal types, utility types, React patterns, strict mode, production tsconfig (Pocock + Wellman + Abella) |

### UI/UX Design (21 Skills)

**Cognitive Foundations**
- `ux-psychology` — Dual-process thinking, memory, attention, Gestalt, biases (Hodent, Kahneman)
- `laws-of-ux` — All 30 Yablonski Laws (Fitts, Hick, Miller, Jakob, Tesler, Doherty)
- `cognitive-ux-framework` — Six Minds model (Whalen)

**Design Craft**
- `practical-ui-design` — Colour (HSB palettes), typography (type scales), layout (8pt grid), dark mode (Dannaway)
- `ux-principles-101` — 101 actionable principles: accessibility, forms, search, empty states, error recovery (Grant)
- `data-visualization` — Chart selection, decluttering, storytelling with data (Knaflic)
- `interaction-design-patterns` — 45+ proven patterns (Tidwell)

**Methodology**
- `web-usability-krug` — Krug's 3 Laws, Billboard Design 101, DIY testing
- `lean-ux-validation` — Hypothesis-driven validation before building (Klein)
- `habit-forming-products` — Hook Model for engagement (Eyal)
- `ux-for-ai` — AI interface design: trust, transparency, premium feel

**Domain-Specific**
- `healthcare-ui-design` — Clinical-grade UI (HIPAA, FDA compliance)
- `pos-sales-ui-design` / `pos-restaurant-ui-standard` — POS and checkout interfaces
- `form-ux-design` — Cross-platform form patterns (web + Android + iOS)

### Security

| Skill | Scope |
|-------|-------|
| `vibe-security-skill` | Secure coding baseline for web apps |
| `php-security` | PHP-specific (sessions, XSS, CSRF, file uploads) |
| `code-safety-scanner` | 14-point safety audit (security, stability, payments) |
| `web-app-security-audit` | 8-layer security audit for PHP/JS/HTML apps |
| `skill-safety-audit` | Scan skills for unsafe instructions |

### SDLC Documentation (ISO-Compliant)

| Phase | Skill | Documents Generated |
|-------|-------|-------------------|
| Planning | `sdlc-planning` | Vision, SDP, SRS, QA Plan, Risk Plan |
| Design | `sdlc-design` | SDD, Tech Spec, ICD, DB Design, API Docs |
| Testing | `sdlc-testing` | Test Plan, Test Cases, V&V (ISO 29119-3) |
| Deployment | `sdlc-user-deploy` | User Manual, Ops Manual, Release Notes |
| Maintenance | `sdlc-maintenance` | SMP, MR/PR workflow (ISO 14764:2022) |
| Evaluation | `sdlc-post-deployment` | PDER, operational metrics |

### Store Submission

| Store | Skill |
|-------|-------|
| Google Play | `google-play-store-review` |
| Apple App Store | `app-store-review` |

### Document Production

| Skill | Purpose |
|-------|---------|
| `professional-word-output` | Pandoc + python-docx pipeline; heading flow rules, typography spec, table design, pre-delivery checklist |

### Content & Writing

| Skill | Purpose |
|-------|---------|
| `blog-idea-generator` | Generate 15-25 targeted blog ideas |
| `blog-writer` | SEO-optimised bilingual articles with photography |
| `content-writing` | Headlines, ledes, readability, persuasive structure |
| `east-african-english` | British English, East African professional tone |
| `language-standards` | Multi-language: English, French, Kiswahili |

### AI & Orchestration

| Skill | Purpose |
|-------|---------|
| `ai-assisted-development` | Orchestrate multiple AI agents |
| `ai-error-handling` | 5-layer validation for AI output |
| `ai-error-prevention` | "Trust but verify" workflow |
| `orchestration-best-practices` | Multi-step workflow coordination |
| `feature-planning` | Spec + implementation plan generation |
| `plan-implementation` | Autonomous TDD plan executor |

## How to Use

### In Claude Code

Skills are loaded automatically when referenced in conversation or invoked explicitly:

```
> Use the android-development skill to review this code
> /ios-development  (slash command invocation)
```

### In Your Project

Reference skills from any project by adding to your project's `CLAUDE.md`:

```markdown
Load these skills from ~/.claude/skills/:
- android-development
- api-pagination
- practical-ui-design
```

### Combining Skills

Skills are designed to work together. Common combinations:

```
Web SaaS app:     webapp-gui-design + form-ux-design + practical-ui-design + vibe-security-skill
Android app:      android-development + jetpack-compose-ui + android-data-persistence + android-tdd
iOS app (standard):     ios-development + swiftui-design + ios-data-persistence + ios-tdd
iOS app (advanced):     ios-architecture-advanced + ios-production-patterns + ios-swift-design-patterns
iOS app (commercial):   ios-monetization + ios-push-notifications + ios-networking-advanced
iOS app (scale/teams):  ios-at-scale + ios-debugging-mastery
iOS app (UIKit):        ios-uikit-advanced + ios-production-patterns
iOS AI features:        ios-ai-ml + ios-development
Mobile planning:  mobile-saas-planning + feature-planning + dual-auth-rbac
Any UI work:      ux-psychology + practical-ui-design + interaction-design-patterns
```

## Book Sources

Skills are synthesised from authoritative sources, not improvised:

| Book | Author | Skills Informed |
|------|--------|----------------|
| Don't Make Me Think | Krug | `web-usability-krug` |
| Laws of UX | Yablonski | `laws-of-ux` |
| Hooked | Eyal | `habit-forming-products` |
| UX for Lean Startups | Klein | `lean-ux-validation` |
| Designing with the Mind in Mind | Hodent | `ux-psychology` |
| Design for How People Think | Whalen | `cognitive-ux-framework` |
| Designing Interfaces | Tidwell et al. | `interaction-design-patterns` |
| Practical UI | Dannaway | `practical-ui-design` |
| 101 UX Principles | Grant | `ux-principles-101` |
| Storytelling with Data | Knaflic | `data-visualization` |
| Pro SwiftUI | Hudson | `swiftui-pro-patterns` |
| Advanced iOS App Architecture (4th Ed.) | Cacheaux & Berlin | `ios-architecture-advanced` |
| iOS Development at Scale | Vennaro | `ios-at-scale` |
| iOS 18 Programming for Beginners | Sahar | `ios-at-scale`, `ios-development` |
| Advanced Apple Debugging & Reverse Engineering | Selander | `ios-debugging-mastery` |
| Practical AI with Swift | Geldard & Manning | `ios-ai-ml` |
| Swift Design Patterns | Hudson | `ios-swift-design-patterns` |
| Learning Mobile App Development | Iversen & Eierman | `ios-production-patterns` |
| Ultimate iOS App Development Guide | Chopada | `ios-production-patterns`, `ios-development` |
| UI Design for iOS App Development | Cahill | `ios-production-patterns`, `swiftui-design` |
| SwiftUI Cookbook 3rd Ed | Catalan | `swiftui-design`, `ios-data-persistence` |
| Better UI Components 3.0 | Kuleszo | `practical-ui-design` |
| UX for AI | Nudelman | `ux-for-ai` |
| The Data Model Resource Book Vol 1 & 2 | Silverston | `mysql-data-modeling` |
| MySQL 8 Query Performance Tuning | Krogh | `mysql-query-performance` |
| Efficient MySQL Performance | Schoen | `mysql-query-performance` |
| Mastering MySQL Administration | — | `mysql-administration` |
| MySQL 8 Cookbook | Velos | `mysql-advanced-sql` |
| Leveling Up with SQL | Simon | `mysql-advanced-sql` |
| Advanced MySQL 8 | — | `mysql-best-practices` |
| Database Internals | Petrov | `database-internals` |
| Database Reliability Engineering | Campbell & Majors | `database-reliability` |
| The Golden Book of JavaScript | — | `javascript-modern` |
| JavaScript: The Advanced Concepts | Turner | `javascript-modern` |
| JavaScript: Understanding the Weird Parts (Closures & Prototypes) | — | `javascript-advanced` |
| JavaScript Unleashed | — | `javascript-advanced` |
| JavaScript Design Patterns | Jones | `javascript-patterns` |
| Mastering JavaScript Design Patterns | Shah | `javascript-patterns` |

## Skill Structure

Each skill follows this format:

```yaml
---
name: skill-name
description: "When to use this skill (triggers, symptoms, contexts)"
---

# Skill Content
## Overview — core principle in 1-2 sentences
## When to Use / When NOT to Use
## Patterns with code examples
## Anti-patterns to avoid
## Checklist
```

All skills are under 500 lines. Heavy reference material goes in `references/` subdirectories.

## Repository Stats

- **85+ skills** across 13 categories
- **~37,000 lines** of curated patterns and code examples
- **36+ books** synthesised into actionable guidance
- **4 platforms**: Web (PHP+JS), Android (Kotlin), iOS (Swift), Cross-Platform
- **Full SDLC coverage**: Planning through post-deployment evaluation

## Maintained By

**Peter Bamuhigire** — [BIRDC](https://github.com/BIRDC)

Built with Claude Code for use with Claude Code.
