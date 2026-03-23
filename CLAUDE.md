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
├── ios-development/                 # iOS dev standards (Swift, SwiftUI, MVVM, async/await, @Observable)
├── ios-tdd/                         # iOS TDD (Red-Green-Refactor, Swift Testing, XCTest, protocol mocks)
├── ios-data-persistence/            # SwiftData, Keychain, offline-first, repository pattern for iOS
├── ios-project-setup/               # Xcode setup, xcconfig schemes, code signing, TestFlight, App Store
├── ios-biometric-login/             # Face ID/Touch ID gate via LocalAuthentication + Keychain
├── ios-pdf-export/                  # Native PDF export using UIGraphicsPDFRenderer + share sheet
├── ios-rbac/                        # RBAC for iOS (PermissionGate ViewModifier, module-gated TabView)
├── ios-bluetooth-printing/          # CoreBluetooth ESC/POS thermal printer communication
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
├── ai-assisted-development/         # AI agent orchestration for development workflows
├── ai-error-prevention/             # Error prevention for AI-assisted development (trust but verify)
├── orchestration-best-practices/    # The 10 commandments of orchestration
├── ai-error-handling/               # 5-layer validation stack for AI output
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
├── api-error-handling/              # API error handling
├── api-pagination/                 # Offset pagination (PHP + Android + iOS infinite scroll)
├── mysql-best-practices/            # MySQL 8.x (schema, indexing, queries, security, transactions, tuning, HA)
├── php-modern-standards/            # PHP 8+ (strict typing, SOLID, generators, OPcache, testing, Fibers, security)
├── php-security/                    # PHP security patterns (sessions, XSS, CSRF, file uploads, php.ini)
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
├── ux-psychology/                   # Cognitive science foundations (dual-process, memory, attention, biases, dark patterns, design laws)
├── laws-of-ux/                      # Named-law quick reference: all 30 Yablonski Laws of UX (Fitts, Hick, Miller, Jakob, Tesler, Postel, Doherty, Zeigarnik, Peak-End, Gestalt)
├── ux-for-ai/                       # AI interface design (trust, transparency, premium vs slop, human oversight)
├── lean-ux-validation/              # Hypothesis-driven UX (validate before build, 5-user research, metrics)
├── interaction-design-patterns/     # Tidwell's 45+ patterns: behavioral, navigation, layout, actions, data display
├── web-usability-krug/              # Krug's 3 Laws, Billboard Design 101, navigation, goodwill reservoir, mobile, accessibility (Don't Make Me Think)
├── swiftui-pro-patterns/            # Advanced SwiftUI: layout internals, identity, animation, custom layouts, environment/preferences, performance (Pro SwiftUI, Hudson)
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
**Last Updated:** 2026-02-20
**Line Count:** ~250 lines (compliant with doc-standards.md)
