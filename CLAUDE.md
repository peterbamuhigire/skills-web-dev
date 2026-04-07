# Claude Code Guide - Skills Repository

**Quick Reference Hub** - For detailed guides, see `claude-guides/` directory.

## Repository Context

**Purpose:** Shared skills library for use across multiple projects
**Type:** Reference/Knowledge Repository
**Usage Pattern:** Skills are loaded into Claude Code sessions in other projects

## Documentation Standards (MANDATORY)

**CRITICAL:** ALL markdown files (.md) created in this repository MUST follow strict standards:

✅ **500-line hard limit for ALL .md files** - No exceptions
✅ **Two-tier structure:** High-level TOC (Tier 1) + Deep dive docs (Tier 2)
✅ **Smart subdirectory grouping:** Logical organization by module/type/workflow
✅ **Regular grooming:** Improves AI comprehension and reduces token costs

📖 **See `doc-standards.md` for complete requirements**

## How Claude Should Work With This Repository

### When Asked to Use Skills

If a user mentions they want to use a skill from this collection:

1. **Understand the context:** Determine which project the user is working on
2. **Recommend the appropriate skill:** Based on their task requirements
3. **Explain how to load it:** Provide clear instructions for skill invocation
4. **Apply the skill's patterns:** Once loaded, follow the skill's guidelines precisely

**Alias:** If a user says "seeder-script", treat it as the saas-seeder skill.

### When Generating Blog Posts (MANDATORY)

When asked to generate a blog post, article, or any written content piece:

1. **Read these skills** from `C:\wamp64\www\website-skills\` before writing:
   - `blog-idea-generator/SKILL.md` — ideation, topic framing, audience targeting
   - `blog-writer/SKILL.md` — article pipeline, SEO, structure, human voice standards
   - `content-writing/SKILL.md` — headlines, ledes, readability, persuasive structure
   - `east-african-english/SKILL.md` — British English spelling, East African tone
   - `language-standards/SKILL.md` — multi-language tone, grammar, cultural standards

2. **Output:** Save each blog post as a **single `.md` file** in `blog-posts/` directory (this repository root).

3. **Filename format:** `slug-of-the-title.md` (lowercase, hyphenated, descriptive).

4. **Apply these standards from the skills:**
   - British English spelling throughout (organisation, colour, programme, etc.)
   - Formal, respectful East African professional tone
   - Strong headline with clear benefit promise
   - Short opening paragraph (inverted pyramid — most important first)
   - Scannable structure with subheadings, bullets, and short paragraphs
   - No AI-sounding vocabulary (no "delve", "leverage", "robust", "seamlessly")
   - Clear call to action at the close

### Security Baseline (Required for Web Apps)

For any web application work (frontend, backend, APIs), always load and apply the **Vibe Security Skill** alongside the primary skill. Security principles are non-optional.

### When Adding New Skills

If asked to create a new skill:

1. **Review existing skills:** Understand the format and structure
2. **Create skill directory:** `skill-name/` with appropriate naming
3. **Write SKILL.md:** Follow the frontmatter + markdown format (max 500 lines)
4. **Add documentation:** Update README.md and PROJECT_BRIEF.md
5. **Ensure completeness:** Include examples, patterns, and clear guidance

📖 **See `claude-guides/skill-creation-workflow.md` for complete workflow**

### When Modifying Existing Skills

If improving or fixing a skill:

1. **Read the current skill thoroughly:** Understand its purpose and patterns
2. **Make targeted improvements:** Don't completely rewrite unless necessary
3. **Maintain backward compatibility:** Existing users depend on these patterns
4. **Update documentation:** Reflect changes in README if significant
5. **Test the modification:** Ensure it still provides value

## Skill Invocation Pattern

When users invoke a skill, Claude should:

1. Load the skill content
2. Acknowledge the skill is active
3. Apply the skill's patterns and guidelines
4. Reference the skill's best practices
5. Generate outputs consistent with the skill

**Example:**

```
User: "Use the webapp-gui-design skill to create a dashboard UI"

Claude: "I'm using the webapp-gui-design skill to create a polished dashboard UI.
[Applies established template patterns per skill guidelines]"
```

📖 **See `claude-guides/skill-invocation.md` for detailed usage patterns**

## Repository Structure

```
skills/
├── android-development/             # Android dev standards (Kotlin, Compose, MVVM, Hilt)
├── android-tdd/                     # Android TDD (Red-Green-Refactor, test pyramid, CI)
├── jetpack-compose-ui/              # Compose UI (beautiful, minimalistic, Material 3)
├── android-data-persistence/        # Room, DataStore, API sync, offline-first
├── android-reports/                 # [Superseded by mobile-reports] Android report patterns
├── android-saas-planning/           # [Superseded by mobile-saas-planning] Android SaaS planning
├── android-biometric-login/         # Biometric auth (fingerprint/face) for Android apps
├── android-custom-icons/            # [Superseded by mobile-custom-icons] Android PNG icons
├── android-pdf-export/              # Native PDF export using PdfDocument API
├── android-report-tables/           # [Superseded by mobile-report-tables] Android report tables
├── kmp-development/                 # KMP shared module (Ktor, SQLDelight, Koin, expect/actual, SKIE)
├── kmp-tdd/                         # KMP TDD (commonTest, Mokkery, Turbine, Ktor MockEngine, Kover)
├── ios-development/                 # iOS dev standards (Swift, SwiftUI, MVVM, async/await, @Observable)
├── ios-tdd/                         # iOS TDD (Red-Green-Refactor, Swift Testing, XCTest, protocol mocks)
├── ios-stability-solutions/         # Crash prevention, optional safety, DI, SOLID, TDD safety net, SDUI, UI crash surface
├── ios-data-persistence/            # SwiftData, Keychain, offline-first, repository pattern for iOS
├── ios-project-setup/               # Xcode setup, xcconfig schemes, code signing, TestFlight, App Store
├── ios-biometric-login/             # Face ID/Touch ID gate via LocalAuthentication + Keychain
├── ios-pdf-export/                  # Native PDF export using UIGraphicsPDFRenderer + share sheet
├── ios-rbac/                        # RBAC for iOS (PermissionGate ViewModifier, module-gated TabView)
├── ios-bluetooth-printing/          # CoreBluetooth ESC/POS thermal printer communication
├── ios-swift-recipes/               # App Store production Swift recipes (data, JSON, UIKit, images, animation, SwiftUI)
├── swiftui-design/                  # SwiftUI UI standards (NavigationStack, theming, animations, charts)
├── healthcare-ui-design/            # Clinical-grade UI for EMR/EHR, telemedicine, patient portals (web + Android)
├── google-play-store-review/        # Play Store review readiness
├── app-store-review/                # Apple App Store compliance, privacy labels, TestFlight, review readiness
├── implementation-status-auditor/   # Project audit + completion blueprint
├── plan-implementation/             # Autonomous plan executor (TDD + 5-layer validation)
├── multi-tenant-saas-architecture/  # SaaS backend patterns
├── modular-saas-architecture/       # Pluggable SaaS modules
├── feature-planning/                # Complete feature planning (spec + implementation)
├── form-ux-design/                  # Cross-platform form UX patterns (web + Android + iOS)
├── nextjs-app-router/               # Next.js App Router: RSC, routing, data fetching, auth, deployment (Jain + Krause)
├── ai-app-architecture/             # AI-powered app stack: architecture styles, component design, module gating, token billing
├── ai-prompt-engineering/           # Production prompt engineering: templates, CoT, few-shot, versioning, defensive patterns
├── ai-rag-patterns/                 # RAG architecture: chunking, hybrid search, contextual retrieval, multi-tenant
├── ai-agents-tools/                 # AI agents: ReAct loop, tool categories, human approval gates, multi-agent patterns
├── llm-security/                    # LLM security: OWASP Top 10, trust boundaries, prompt injection defense, output validation
├── ai-evaluation/                   # AI evaluation: golden test sets, AI-as-judge, production monitoring, drift detection
├── ai-saas-billing/                 # AI SaaS billing: module gating (off by default), per-tenant/user token metering, quotas
├── ai-web-apps/                     # AI-enhanced web apps: Vercel AI SDK, streaming, RAG, LangChain.js (Despoudis)
├── ai-assisted-development/         # AI agent orchestration for development workflows
├── ai-error-prevention/             # Error prevention for AI-assisted development (trust but verify)
├── orchestration-best-practices/    # The 10 commandments of orchestration
├── ai-error-handling/               # 5-layer validation stack for AI output
├── ai-opportunity-canvas/           # Discover and rank AI use cases for any project (AI Opportunity Register)
├── ai-feature-spec/                 # Design a single AI feature end-to-end (model, prompt, schema, fallback, UX)
├── ai-cost-modeling/                # Token economics: cost/user, cost/tenant, provider comparison, margin modeling
├── ai-architecture-patterns/        # AI Module Gate, Budget Guard, Token Ledger, provider abstraction (PHP/Android/iOS)
├── ai-ux-patterns/                  # UX for AI: loading states, streaming, confidence, human-in-the-loop, usage display
├── ai-security/                     # LLM security: prompt injection, PII scrubbing, output validation, DPPA compliance
├── ai-metering-billing/             # Token ledger schema, metering middleware, per-tenant billing, pricing tiers
├── ai-integration-section/          # Generate AI Integration section for SRS/PRD/HLD documents
├── microservices-fundamentals/      # Monolith vs microservices, decomposition patterns, 12-Factor App, bounded contexts, data isolation
├── microservices-architecture-models/ # NGINX MRA three models (Proxy/Router Mesh/Fabric), API gateway, service discovery
├── microservices-resilience/        # Circuit breaker, /health endpoint, load balancing, retry, bulkhead, timeout, slowstart
├── microservices-communication/     # Sync vs async, service discovery, inter-service auth, data isolation, API contracts
├── microservices-ai-integration/    # AI as a microservice, AI gateway, async AI job pipeline, Kubeflow/Seldon Core, metering in distributed systems
├── ai-analytics-strategy/           # Analytics maturity model, KDD, CRISP-DM, data quality, responsible AI, analytics ROI measurement
├── ai-predictive-analytics/         # Predictive models via LLM API — risk scoring, demand forecasting, anomaly detection — domain prompt templates
├── ai-nlp-analytics/                # Text analytics — sentiment, classification, entity extraction, multi-language (English/Luganda/Swahili)
├── ai-analytics-dashboards/         # AI-powered dashboard design — KPI cards, trend charts, AI Insights panel, role-based variants, export
├── ai-analytics-saas/               # AI analytics for SaaS: NL2SQL, embeddings, semantic search, anomaly detection, insight cache
├── realtime-systems/                # WebSockets, SSE, live dashboards, multi-tenant channel isolation, reconnection strategies
├── update-claude-documentation/     # Documentation maintenance
├── doc-architect/                   # Triple-Layer AGENTS.md generator
├── manual-guide/                    # End-user manuals and guides
├── custom-sub-agents/               # Custom AI sub-agent architecture and setup
├── dual-auth-rbac/                  # Dual auth + RBAC security
├── webapp-gui-design/               # Web app GUI design
├── image-compression/               # Client-side image compression patterns
├── inventory-management/            # Inventory management patterns
├── pos-sales-ui-design/             # POS & sales entry UI
├── pos-restaurant-ui-standard/      # Restaurant POS UI standard
├── report-print-pdf/                # Report export (PDF + print)
├── project-requirements/            # SaaS project requirements discovery
├── api-design-first/                # REST conventions, OpenAPI 3 spec-first, versioning, GraphQL decision guide, PHP controller pattern
├── api-error-handling/              # API error handling
├── api-pagination/                 # Offset pagination (PHP + Android + iOS infinite scroll)
├── mysql-best-practices/            # MySQL 8.x (schema, indexing, queries, security, transactions, tuning, HA, benchmarking) + MySQL 8 exclusive features reference
├── mysql-data-modeling/             # Universal entity patterns: Party model, product hierarchy, order/invoice lifecycle, double-entry accounting (Silverston)
├── mysql-query-performance/         # EXPLAIN ANALYZE, index design, optimizer hints, histogram stats, Performance Schema, covering indexes, slow query diagnosis
├── mysql-administration/            # GTID replication, InnoDB Cluster, least-privilege security, XtraBackup, PITR, ProxySQL, zero-downtime schema changes
├── mysql-advanced-sql/              # Window functions, recursive CTEs, JSON_TABLE, dynamic pivoting, gaps/islands, stored procedures, triggers
├── database-internals/              # B-tree mechanics, WAL/redo log, MVCC, buffer pool, lock types, LSM trees, distributed tradeoffs (CAP, read-your-writes)
├── database-reliability/            # Database SLOs, expand-contract migrations, backup verification, incident runbooks, monitoring pyramid, chaos engineering
├── php-modern-standards/            # PHP 8+ (strict typing, SOLID, generators, OPcache, testing, Fibers, security, rate limiting, queues, caching, resilience)
├── php-security/                    # PHP security patterns (sessions, XSS, CSRF, file uploads, php.ini)
├── javascript-modern/               # ES6+ mastery: modules, async/await, Proxy, generators, WeakMap, AbortController, production fetch
├── javascript-advanced/             # Closures, prototype chain, OOP (#private fields), functional patterns, event loop, memory management
├── javascript-patterns/             # 10 design patterns: Module, Observer, Factory, Strategy, Command, Repository, Mediator, State Machine
├── javascript-php-integration/      # JS-in-own-files architecture, data-* bridge, CSRF flow, $pageScript pattern (PHP+JS SaaS rule)
├── typescript-mastery/              # Full TypeScript: types, generics, conditional/mapped types, variance, infer, branding, Option type, exception unions, React, tsconfig (Pocock + Wellman + Cherny)
├── typescript-design-patterns/      # All 23 GoF patterns in TypeScript with code examples and when-to-use (Akintoye)
├── php-vs-nextjs/                   # PHP vs Next.js decision framework — when to use each, hybrid architecture, migration strategy
├── saas-accounting-system/           # Double-entry accounting engine for SaaS
├── saas-seeder/                     # SaaS bootstrap and seeding
├── skill-safety-audit/              # Skill safety audit workflow
├── gis-mapping/                     # OpenStreetMap GIS + geofencing
├── markdown-lint-cleanup/           # Markdown lint cleanup and formatting
├── vibe-security-skill/             # Secure coding for web apps
├── code-safety-scanner/             # 14-point safety scan (security, stability, payments)
├── web-app-security-audit/          # 8-layer security audit for PHP/JS/HTML web apps
├── photo-management/                # Photo upload and gallery patterns
├── mobile-custom-icons/             # Cross-platform custom PNG icons (Android + iOS), placeholder tracking
├── mobile-rbac/                     # RBAC for Android mobile apps (PermissionGate, ModuleGate)
├── mobile-report-tables/            # Cross-platform report tables (Android + iOS) for 25+ row datasets
├── mobile-reports/                  # Cross-platform mobile report design (Android Compose + iOS SwiftUI)
├── mobile-saas-planning/            # Cross-platform SaaS companion app planning (Android + iOS), 7 docs
├── skill-writing/                   # Skill creator (meta-skill)
├── sdlc-planning/                   # SDLC planning & management docs (Vision, SDP, SRS, etc.)
├── sdlc-design/                     # SDLC design & development docs (SDD, Tech Spec, ICD, DB Design, API)
├── sdlc-testing/                    # SDLC testing & quality docs (STP, Test Cases, V&V, Reports)
├── sdlc-user-deploy/                # SDLC user & deployment docs (User Manual, Ops, Training, Release)
├── sdlc-maintenance/                # SDLC maintenance docs (SMP, MR/PR workflow, ISO 14764)
├── sdlc-post-deployment/            # Post-deployment evaluation report (PDER, operational metrics)
├── sdlc-lifecycle.md                # SDLC master lifecycle overview (all 4 phases)
├── spec-architect/                  # Specification architecture skill
├── blog-idea-generator/             # Generate 15-25 targeted blog ideas for client sites
├── blog-writer/                     # SEO-optimised bilingual blog articles with photography
├── content-writing/                 # Copywriting standards (headlines, ledes, readability)
├── east-african-english/            # British English / East African tone standard
├── language-standards/              # Multi-language tone, grammar & cultural standards
├── api-testing-verification/        # API test verification patterns
├── habit-forming-products/          # Hook Model (Trigger→Action→Variable Reward→Investment), internal triggers, ethics, Habit Testing
├── product-discovery/               # 4 product risks, opportunity assessment, customer discovery, prototype spectrum, testing (INSPIRED)
├── product-strategy-vision/         # Product vision principles, strategy, OKRs, roadmap alternatives, product evangelism (INSPIRED + Mastering SPM)
├── competitive-analysis-pm/         # Porter's Five Forces for PMs, win/loss analysis, competitor teardown, positioning map (Mastering SPM)
├── saas-business-metrics/           # MRR/ARR/CAC/LTV/NRR/churn/NPS/Rule of 40/unit economics (SaaS Guide + Mastering SPM)
├── software-pricing-strategy/       # Value-based pricing, 3 principles, pricing models, packaging, negotiation, expansion revenue (Mastering SPM)
├── software-business-models/        # Products vs services vs hybrid, platforms, open source, licensing, startup survival (Business of Software)
├── it-proposal-writing/             # BOD/USP, proposal lifecycle, 5-level failure model, persuasive prose, Proposal Evaluation Questionnaire (Coombs)
├── technology-grant-writing/        # Grant landscape, winning framework, needs assessment, evaluation plan, budget justification (Winning at IT)
├── ux-psychology/                   # Cognitive science foundations (dual-process, memory, attention, biases, dark patterns, design laws)
├── laws-of-ux/                      # Named-law quick reference: all 30 Yablonski Laws of UX (Fitts, Hick, Miller, Jakob, Tesler, Postel, Doherty, Zeigarnik, Peak-End, Gestalt)
├── ux-for-ai/                       # AI interface design (trust, transparency, premium vs slop, human oversight)
├── lean-ux-validation/              # Hypothesis-driven UX (validate before build, 5-user research, metrics)
├── interaction-design-patterns/     # Tidwell's 45+ patterns: behavioral, navigation, layout, actions, data display
├── web-usability-krug/              # Krug's 3 Laws, Billboard Design 101, navigation, goodwill reservoir, mobile, accessibility (Don't Make Me Think)
├── practical-ui-design/             # Rules-based visual design: colour (HSB), typography (scales), layout (8pt grid), buttons, dark mode (Dannaway + Kuleszo)
├── ux-principles-101/               # 101 UX principles: accessibility, forms, search, empty states, error recovery, copywriting, ethics (Grant + Maioli)
├── data-visualization/              # Knaflic's 6-lesson framework: context, chart selection, decluttering, attention, design, storytelling (Storytelling with Data)
├── ai-slop-prevention/              # AI-generated UI anti-pattern detection and elimination (Impeccable, Bakaus 2025)
├── motion-design/                   # Animation timing (100/300/500), easing curves, GPU-only, prefers-reduced-motion
├── ux-writing/                      # Microcopy standards: buttons, errors, empty states, loading, voice/tone, i18n
├── responsive-design/               # Mobile-first, container queries, pointer/hover detection, safe areas, srcset
├── frontend-performance/            # Core Web Vitals (LCP, INP, CLS), image/JS/CSS/font optimisation, budgets
├── design-audit/                    # 10-dimension UI quality audit with severity-rated findings and scoring
├── swiftui-pro-patterns/            # Advanced SwiftUI: layout internals, identity, animation, custom layouts, environment/preferences, performance (Pro SwiftUI, Hudson)
├── ios-architecture-advanced/       # Scoped DI containers, MVVM/Redux/Elements architecture, use case patterns, model-driven navigation, Observer composition
├── ios-at-scale/                    # Modular architecture (RIBLETS/ComponentKit), Buck/Bazel builds, trunk-based dev, CI/CD pipeline, feature flags, perf at scale
├── ios-production-patterns/         # Production gotchas: VC lifecycle, delegate pattern, sensor mgmt, camera, keyboard, Core Data migration, SwiftUI↔UIKit
├── ios-debugging-mastery/           # LLDB mastery, Python scripting for LLDB, watchpoints, DTrace, malloc stack logging, Mach-O analysis, anti-debugging bypass
├── ios-ai-ml/                       # CoreML, Vision (face/barcode/saliency), NaturalLanguage, CreateML training, on-device model updates, privacy-preserving AI
├── ios-swift-design-patterns/       # Swift-idiomatic patterns: Observable MVVM, POP composition, VC containment, delegation conventions, keypath adapter
├── ios-networking-advanced/         # Actor-based NetworkClient, 401 refresh deduplication, exponential backoff, background URLSession, cert pinning, multipart upload
├── ios-uikit-advanced/              # Diffable data sources, compositional layout, custom transitions, UIViewPropertyAnimator, context menus, bottom sheets
├── ios-monetization/                # StoreKit 2: consumables, subscriptions, paywall UI, Transaction.updates loop, receipt JWS, sandbox testing
├── ios-push-notifications/          # APNs: UNUserNotificationCenter, rich push, service extensions, silent push, notification categories, token lifecycle
├── ios-swift-recipes/               # App Store production Swift recipes (data, JSON, UIKit, images, animation, SwiftUI)
├── ios-stability-solutions/         # Crash prevention, optional safety, DI, SOLID, TDD safety net, SDUI, UI crash surface
├── prompting-patterns-reference.md  # Prompting patterns for AI instructions
├── orchestration-patterns-reference.md # Orchestration strategies for multi-agent workflows
├── doc-standards.md                 # Documentation formatting standards (MANDATORY)
├── claude-guides/                   # Deep dive guides (this file's Tier 2)
│   ├── skill-creation-workflow.md   # Creating and modifying skills
│   ├── skill-best-practices.md      # Best practices and quality standards
│   ├── skill-invocation.md          # How to use skills effectively
│   ├── database-standards.md        # Database work requirements (CRITICAL)
│   ├── workflows.md                 # Common workflows
│   └── troubleshooting.md           # Error handling and maintenance
├── PROJECT_BRIEF.md                 # Quick overview
├── README.md                        # Full documentation
└── CLAUDE.md                        # This file
```

## Quick Reference Guide

| Topic                       | Guide File                                  | When to Use                                    |
|-----------------------------|---------------------------------------------|------------------------------------------------|
| **Creating Skills**         | `claude-guides/skill-creation-workflow.md`  | Adding new skills, modifying existing skills   |
| **Best Practices**          | `claude-guides/skill-best-practices.md`     | Quality standards, structure requirements      |
| **Using Skills**            | `claude-guides/skill-invocation.md`         | Loading skills, combining skills, token costs  |
| **Database Work**           | `claude-guides/database-standards.md`       | **MANDATORY for ALL database-related work**    |
| **Common Workflows**        | `claude-guides/workflows.md`                | User requests skill, add skill, cross-project  |
| **Troubleshooting**         | `claude-guides/troubleshooting.md`          | Error handling, maintenance, special cases     |
| **Documentation Standards** | `doc-standards.md`                          | **MANDATORY: 500-line limit, two-tier structure** |

## Critical Rules

### Database Standards (MANDATORY)

**All database-related work MUST reference mysql-best-practices skill and follow the migration checklist.**

✅ **Always use for:**

- Database migrations (tables, columns, indexes)
- Schema design and modifications
- Stored procedures, triggers, views
- Query optimization
- Multi-tenant isolation patterns

📖 **See `claude-guides/database-standards.md` for complete checklist**

### Documentation Standards (MANDATORY)

**All markdown files MUST follow strict formatting:**

- **500-line hard limit** - No exceptions
- **Two-tier structure** - TOC + deep dive docs
- **Smart grouping** - Logical subdirectories

📖 **See `doc-standards.md` for complete requirements**

## Working with Skill Files

### SKILL.md Format

Each skill follows this structure:

```yaml
---
name: skill-name
description: Brief description of what this skill does and when to use it
---
# Skill Content
[Detailed guidelines, patterns, examples]
```

**Requirements:**

- Max 500 lines
- Clear frontmatter (name + description)
- Scannable markdown structure
- Links to references/ for deep dives

### When Reading Skills

1. **Parse frontmatter:** Extract name and description
2. **Understand full context:** Read entire skill before applying
3. **Note key sections:** Overview, patterns, examples, anti-patterns
4. **Apply holistically:** Don't cherry-pick; use full skill guidance

### When Creating Skills

1. **Follow the template:** Match existing skill structure
2. **Be comprehensive:** Include all necessary guidance
3. **Provide examples:** Real, working code samples
4. **Define scope clearly:** When to use and when not to use
5. **Include anti-patterns:** Show what to avoid

## Best Practices for Claude

### DO

✅ **Read skills completely** before applying them
✅ **Follow skill guidelines precisely** - they encode best practices
✅ **Combine skills when appropriate** - they're designed to work together
✅ **Update documentation** when adding/modifying skills
✅ **Maintain consistency** across all skills in format and quality
✅ **Provide clear examples** in skills
✅ **Reference skills explicitly** when using them

### DON'T

❌ **Don't partially apply skills** - use the full guidance
❌ **Don't modify skills without updating docs**
❌ **Don't create duplicate skills** - extend existing ones
❌ **Don't make skills too broad** - keep them focused
❌ **Don't skip examples** - they're critical for understanding
❌ **Don't create skills for one-off tasks** - skills should be reusable
❌ **Don't forget frontmatter** - it's essential for skill recognition

## Skill Quality Standards

Every skill should:

1. **Have clear scope:** Well-defined domain and use cases
2. **Include examples:** Real, working code samples
3. **Provide patterns:** Specific, actionable guidance
4. **Show anti-patterns:** What to avoid and why
5. **Be maintainable:** Easy to update as best practices evolve
6. **Be self-contained:** All necessary context included
7. **Be tested:** Verified to work in real scenarios

## Integration Points

### With Other Projects

Skills from this repository are used in:

- Individual development projects
- Client work
- SaaS platforms
- Mobile applications
- Web applications

### Cross-Skill Integration

Skills should complement each other:

```
feature-planning → spec + implementation strategy
      ↓
multi-tenant-saas-architecture → backend patterns
      ↓
webapp-gui-design → UI components
      ↓
[testing-skill] → validates implementation
```

## Summary

**This is a navigation hub.** For detailed guidance, see:

📖 **claude-guides/skill-creation-workflow.md** - Creating and modifying skills
📖 **claude-guides/skill-best-practices.md** - Best practices and quality standards
📖 **claude-guides/skill-invocation.md** - How to use skills effectively
📖 **claude-guides/database-standards.md** - Database work requirements (CRITICAL)
📖 **claude-guides/workflows.md** - Common workflows
📖 **claude-guides/troubleshooting.md** - Error handling and maintenance
📖 **doc-standards.md** - Documentation formatting standards (MANDATORY)

**For Claude Code Internal Use**

This guide ensures consistent, high-quality interaction with the skills repository. When in doubt, read the skill thoroughly before applying it.

---

**Maintained by:** Peter Bamuhigire
**Last Updated:** 2026-03-30
**Line Count:** ~250 lines (compliant with doc-standards.md)
