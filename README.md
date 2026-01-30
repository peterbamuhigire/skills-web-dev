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

### 1. Multi-Tenant SaaS Architecture

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

### 2. Feature Planning

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

### 3. Update Claude Documentation

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

### 4. Dual Auth RBAC

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

### 5. Web App GUI Design

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

### 6. Skill Creator

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

### 7. API Error Handling

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

### 8. MySQL Best Practices

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

### 9. Report Export (PDF + Print)

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

### 10. POS & Sales Entry UI Design

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

### 11. Photo Management

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

### 12. Doc Architect

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

### 13. Manual Guide

**Focus:** End-user manuals and reference guides (not AI agent docs)

**When to use:**

- Documenting a feature for users
- Writing a user manual for a module
- Syncing reference guides

**Key capabilities:**

- Contextual discovery from plans, schema, code, and docs
- Dual-workflow guide structure (overview, steps, technical reference, edge cases)
- Professional instructional tone with workflow comparisons

**Skill location:** `manual-guide/SKILL.md`

---

### 14. Custom Sub-Agents

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

### Skill Invocation Examples

**Creating a distinctive landing page:**

```
User: "Create a dashboard UI for a fintech startup with a bold aesthetic"
Claude: [Loads webapp-gui-design skill]
[Applies optional frontend design direction within the web app]
```

**Implementing multi-tenant permissions:**

```
User: "Help me design the permission model for our SaaS platform"
Claude: [Loads multi-tenant-saas-architecture skill]
[Applies three-panel architecture, zero-trust patterns, audit trails]
```

**Planning a complex feature:**

```
User: "I need to implement user authentication with OAuth"
Claude: [Loads feature-planning skill]
[Creates spec with user stories, then detailed implementation plan with TDD workflow]
```

### Combining Skills

Skills can work together for comprehensive solutions:

```
1. Use feature-planning to create specification and implementation strategy
2. Use multi-tenant-saas-architecture for backend patterns
3. Use webapp-gui-design for UI components
```

## Skill Development

### Creating a New Skill

**IMPORTANT:** Before creating a new skill, consult the **Skill Creator** skill (`skills/skill-writing/SKILL.md`) for comprehensive guidance on skill creation best practices, structure, and workflow.

Each skill follows a standard structure:

```
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

### Skills Checklist

#### Structure Requirements

✅ **One SKILL.md per skill** (required, max 500 lines)
✅ **Keep skills one level deep** in /skills/ directory
✅ **Subdirectories for details:** references/, documentation/, examples/
✅ **Self-contained:** No dependencies between skills

**Example structure:**

```
skills/skill-name/
├── SKILL.md             # Main patterns (under 500 lines)
├── references/          # Database schemas, data models
├── documentation/       # Detailed guides (feature-flags.md, monitoring.md)
└── examples/            # Code examples, templates
```

#### SKILL.md Essentials

✅ **500-line hard limit** (enforced strictly)
✅ **Scannable by AI:** Clear headings, bullet points, specific commands
✅ **Focus on core patterns** applicable to 75-90% of use cases
✅ **Avoid generic tasks** AI already knows (basic CRUD, standard patterns)
✅ **Move details to subdirectories** (schemas, verbose guides, examples)
✅ **Frontmatter with name + description** (description acts as trigger)
✅ **Reference subdirectory files** in SKILL.md (so Claude knows they exist)

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
6. **Document**: Update README.md, PROJECT_BRIEF.md, and CLAUDE.md
7. **Commit**: Git commit and push

**Manual workflow** (if scripts unavailable):

1. Create directory: `your-skill-name/`
2. Write `SKILL.md` with frontmatter (name, description) and body (<500 lines)
3. Add bundled resources: scripts/, references/, assets/ (as needed)
4. Update README.md, PROJECT_BRIEF.md, CLAUDE.md
5. Commit and push

**See `skills/skill-writing/SKILL.md` for complete guidance.**

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

```
skills/
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

## Roadmap

### Planned Skills

- **API Design Patterns:** RESTful, GraphQL, and gRPC patterns
- **Database Design:** Schema design, migrations, optimization
- **Testing Strategies:** Unit, integration, E2E testing patterns
- **DevOps & CI/CD:** Deployment pipelines and infrastructure
- **Security Hardening:** OWASP, penetration testing, security audits
- **Performance Optimization:** Profiling, caching, load balancing
- **Mobile Development:** iOS, Android, React Native patterns
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
