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

### 1. Frontend Design

**Focus:** Creating distinctive, production-grade user interfaces

**When to use:**

- Building web components, pages, or applications
- Creating landing pages or dashboards
- Designing React/Vue/HTML components
- Styling and beautifying web UIs

**Key capabilities:**

- Bold aesthetic direction and creative design
- Advanced typography and color theory
- CSS animations and micro-interactions
- Avoids generic "AI slop" aesthetics
- Context-specific visual design

**Skill location:** `frontend-design/SKILL.md`

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

### 3. Writing Plans

**Focus:** Comprehensive implementation planning

**When to use:**

- Before starting multi-step feature implementation
- Planning complex technical tasks
- Creating test-driven development workflows
- Documenting implementation strategy

**Key capabilities:**

- Bite-sized task breakdown (2-5 minute steps)
- TDD workflow (test, verify fail, implement, verify pass, commit)
- Exact file paths and commands
- Complete code examples
- Testing instructions
- DRY, YAGNI, and best practice adherence

**Skill location:** `writing-plans/SKILL.md`

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

**Focus:** Professional web app UIs using commercial templates (Tabler/Bootstrap 5)

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
- Bootstrap Icons only (bi-*)
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

### 8. Report Export (PDF + Print)

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

**Skill location:** `pdf-export/SKILL.md`

## Installation

### Option 1: Use Skills Directly

Skills can be referenced in your Claude Code session using the skill invocation syntax.

```bash
# In your Claude Code session
/skill path/to/skills/frontend-design
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
ln -s ~/claude-skills/frontend-design ./skills/frontend-design
```

## Usage

### Loading a Skill in Claude Code

When working on a task that aligns with a specific skill, invoke it:

```bash
# Example: Using frontend design skill
/skill frontend-design
```

Claude will load the skill instructions and apply that expertise to your task.

### Skill Invocation Examples

**Creating a distinctive landing page:**

```
User: "Create a landing page for a fintech startup"
Claude: [Loads frontend-design skill]
[Applies bold aesthetic choices, advanced animations, creative typography]
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
Claude: [Loads writing-plans skill]
[Creates comprehensive plan with TDD workflow, exact steps, testing strategy]
```

### Combining Skills

Skills can work together for comprehensive solutions:

```
1. Use writing-plans to create implementation strategy
2. Use multi-tenant-saas-architecture for backend patterns
3. Use frontend-design for UI components
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

✅ **Explicitly mention in prompt:** "Using frontend-design, create..."
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
├── frontend-design/              # UI/UX design skill
│   ├── SKILL.md
│   └── LICENSE.txt
├── multi-tenant-saas-architecture/  # SaaS architecture skill
│   └── SKILL.md
├── writing-plans/                # Implementation planning skill
│   └── SKILL.md
├── update-claude-documentation/  # Documentation maintenance skill
│   └── SKILL.md
├── dual-auth-rbac/               # Dual authentication + RBAC skill
│   ├── SKILL.md
│   └── references/
│       └── schema.sql
├── webapp-gui-design/            # Web app GUI design skill
│   └── SKILL.md
├── skills/
│   └── skill-writing/            # Skill creator (meta-skill)
│       └── SKILL.md
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
  - Frontend Design skill
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
