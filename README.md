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
| **Android** | `android-development`, `jetpack-compose-ui`, `android-data-persistence`, `android-tdd`, `android-biometric-login`, `android-pdf-export` | Kotlin, Compose, Room, Hilt |
| **iOS** | `ios-development`, `swiftui-design`, `ios-data-persistence`, `ios-project-setup`, `ios-tdd`, `ios-biometric-login`, `ios-pdf-export`, `ios-bluetooth-printing` | Swift 6, SwiftUI, SwiftData |
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
iOS app:          ios-development + swiftui-design + ios-data-persistence + ios-tdd
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
| iOS 26 Programming | Sahar | `ios-development`, `ios-project-setup`, `app-store-review` |
| SwiftUI Cookbook 3rd Ed | Catalan | `swiftui-design`, `ios-data-persistence` |
| UI Design for iOS | Cahill | `swiftui-design` |
| Better UI Components 3.0 | Kuleszo | `practical-ui-design` |
| UX for AI | Nudelman | `ux-for-ai` |

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

- **60+ skills** across 10 categories
- **~25,000 lines** of curated patterns and code examples
- **20+ books** synthesised into actionable guidance
- **3 platforms**: Web (PHP), Android (Kotlin), iOS (Swift)
- **Full SDLC coverage**: Planning through post-deployment evaluation

## Maintained By

**Peter Bamuhigire** — [BIRDC](https://github.com/BIRDC)

Built with Claude Code for use with Claude Code.
