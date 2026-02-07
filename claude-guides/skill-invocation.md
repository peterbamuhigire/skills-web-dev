# Skill Invocation & Usage Guide

This guide covers how to invoke and use skills effectively with Claude Code.

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

[Applies established template patterns and optional bespoke aesthetics per skill guidelines]
```

## How Skills Are Loaded

### Explicit Loading (Required)

✅ **Only explicitly mentioned skills get loaded**

Users must mention the skill in their prompt:

```
"Using webapp-gui-design, create a dashboard..."
"With multi-tenant-saas-architecture skill, implement tenant isolation..."
"Apply the mysql-best-practices skill to design this database..."
```

**Why explicit loading?**
- Saves tokens and costs
- Loads only relevant context
- Faster response times
- Avoids confusion from unrelated patterns

### Multiple Skills

✅ **Multiple skills can be combined**

When tasks require multiple domains:

```
"Using webapp-gui-design and multi-tenant-saas-architecture, create a multi-tenant dashboard..."

"Using feature-planning and mysql-best-practices, design a new inventory module..."

"With pos-sales-ui-design and report-print-pdf, create an invoice with print capability..."
```

### Security Baseline

✅ **Always load vibe-security-skill for web apps**

For any web application work (frontend, backend, APIs), always apply the **vibe-security-skill** alongside the primary skill:

```
"Using webapp-gui-design and vibe-security-skill, create a secure login page..."
```

Security principles are non-optional and must be enforced in every relevant change.

## Working with Skill Files

### SKILL.md Format

Each skill follows this structure:

```yaml
---
name: skill-name
description: When to use this skill
---
# Skill Content
[Detailed guidelines, patterns, examples]
```

### Reading Skills

When Claude reads a skill:

1. **Parse frontmatter:** Extract name and description
2. **Understand the full context:** Read the entire skill before applying
3. **Note key sections:** Overview, patterns, examples, anti-patterns
4. **Apply holistically:** Don't cherry-pick; use the full skill guidance

### Applying Skills

**DO:**
- Read the skill completely before applying
- Follow all patterns and guidelines
- Use provided examples as templates
- Reference anti-patterns to avoid mistakes
- Apply the skill holistically, not partially

**DON'T:**
- Cherry-pick sections
- Ignore anti-patterns
- Skip examples
- Partially apply guidance
- Mix with conflicting patterns

## Usage Workflows

### Workflow 1: User Requests Skill Usage

```
User: "I need help with multi-tenant authentication"

Claude:
1. Recognize this aligns with multi-tenant-saas-architecture skill
2. Reference or load the skill
3. Apply authentication patterns from the skill
4. Provide implementation guidance per skill's best practices
```

### Workflow 2: Cross-Project Usage

```
User in Project A: "Use the webapp-gui-design skill"

Claude:
1. Confirm skill location (this repo or local copy)
2. Load skill content
3. Apply to Project A's context
4. Generate code following skill patterns
```

### Workflow 3: Multiple Skills Combined

```
User: "Using feature-planning and multi-tenant-saas-architecture, design a new module"

Claude:
1. Load both skills
2. Use feature-planning for specification
3. Use multi-tenant-saas-architecture for backend patterns
4. Integrate both approaches seamlessly
```

## Skill Aliases

Some skills have common aliases:

- **"seeder-script"** → Use `saas-seeder` skill
- **"PDF printing"** → Use `report-print-pdf` skill
- **"GUI design"** → Use `webapp-gui-design` skill

## Repository Structure Recognition

Claude should recognize these directories and their purposes:

```
skills/
├── multi-tenant-saas-architecture/  # SaaS backend skill
├── feature-planning/         # Complete feature planning (spec + implementation)
├── update-claude-documentation/  # Documentation maintenance skill
├── doc-architect/            # Triple-Layer AGENTS.md generator
├── manual-guide/             # End-user manual and reference guide skill
├── dual-auth-rbac/           # Dual auth + RBAC security skill
├── webapp-gui-design/        # Web app GUI design skill
├── pos-sales-ui-design/      # POS & sales entry UI design
├── report-print-pdf/         # Report export via PDF + print + auto-print
├── api-error-handling/       # API error handling with SweetAlert2
├── mysql-best-practices/     # MySQL 8.x best practices for SaaS
├── saas-seeder/               # SaaS bootstrap and seeding workflow
├── gis-mapping/              # OpenStreetMap GIS mapping + geofencing
├── vibe-security-skill/       # Secure coding for web apps
├── skills/
│   └── skill-writing/        # Skill creator (meta-skill)
├── PROJECT_BRIEF.md          # Quick overview
├── README.md                 # Full documentation
└── CLAUDE.md                 # This file
```

## Skill Categories

### Design Skills

**webapp-gui-design**
- When: Creating web app UIs, dashboards, forms
- Provides: UI patterns, optional bespoke aesthetics
- Combine with: vibe-security-skill

**pos-sales-ui-design**
- When: Creating POS systems, sales entry, invoices
- Provides: POS UI patterns, invoice/receipt standards
- Combine with: report-print-pdf

### Architecture Skills

**multi-tenant-saas-architecture**
- When: Building multi-tenant SaaS applications
- Provides: Backend patterns, security, tenant isolation
- Combine with: mysql-best-practices, dual-auth-rbac

### Security Skills

**dual-auth-rbac**
- When: Implementing authentication and authorization
- Provides: Dual auth (Session + JWT), RBAC, multi-tenant isolation
- Combine with: multi-tenant-saas-architecture

**vibe-security-skill**
- When: ANY web application work
- Provides: Secure coding baseline, input validation, output escaping
- Combine with: ALL web-related skills

### Database Skills

**mysql-best-practices**
- When: ANY database-related work
- Provides: Schema design, migrations, stored procedures, indexing
- **MANDATORY** for all database work
- Combine with: multi-tenant-saas-architecture

### Process Skills

**feature-planning**
- When: Planning new features or modules
- Provides: Complete planning from spec to implementation, TDD workflows
- Combine with: Relevant implementation skills

**update-claude-documentation**
- When: Maintaining project documentation
- Provides: Documentation standards, consistency checking
- Standalone skill

**doc-architect**
- When: Generating AGENTS.md documentation
- Provides: Triple-Layer documentation generation
- Standalone skill

## Skill-Specific Guidelines

### mysql-best-practices (MANDATORY)

**ALWAYS use for:**
- Database migrations (adding/dropping tables, columns)
- Schema design and modifications
- Creating/updating stored procedures, triggers, views
- Adding indexes or foreign keys
- Query optimization
- Multi-tenant isolation patterns

**Migration Checklist (MANDATORY):**

**Pre-Migration:**
1. Grep entire codebase for table/column references
2. Check all stored procedures, triggers, views
3. Backup database

**Post-Migration:**
4. Verify no orphaned references in code
5. Test all affected endpoints
6. Export updated schema
7. Document rollback procedure

**Failure to follow causes production failures.**

### vibe-security-skill (Baseline for Web)

**ALWAYS use for:**
- Frontend development
- Backend API development
- Form creation
- User input handling
- Database queries
- Authentication/authorization

**Security principles enforced:**
- Input validation
- Output escaping
- SQL injection prevention
- XSS protection
- CSRF protection
- Authentication security
- Authorization checks

## Error Handling

### If a Skill is Unclear

```
User: "Use [skill-name]"

Claude: "I've reviewed the [skill-name] skill. Before proceeding, I need clarification:
- [Specific question about context]
- [Specific question about approach]

This will help me apply the skill's patterns most effectively."
```

### If Skills Conflict

```
Situation: Two skills suggest different approaches

Claude: "I notice the [skill-1] and [skill-2] skills have different
recommendations for [topic]. For your use case, I recommend [skill-1]
because [reason]. Would you like me to proceed with that approach?"
```

### If a Skill is Missing

```
User: "Use the [non-existent-skill] skill"

Claude: "I don't see a [non-existent-skill] skill in the collection.
The closest match is [similar-skill], which covers [domain].

Would you like me to:
1. Use [similar-skill] skill
2. Create a new [non-existent-skill] skill
3. Work without a specific skill
```

### Skill Not Loading

**Troubleshooting steps:**

1. Check file path: `skills/skill-name/SKILL.md`
2. Verify YAML frontmatter syntax
3. Confirm markdown formatting
4. Review for parsing errors

### Skill Producing Unexpected Results

**Troubleshooting steps:**

1. Re-read skill completely
2. Check if context matches skill's intended use case
3. Verify all skill patterns are being applied
4. Ask user for clarification if ambiguous

### Multiple Applicable Skills

**Resolution:**

1. Determine primary domain of the task
2. Load the most specific skill first
3. Reference other skills as needed
4. Combine patterns thoughtfully

## Integration Points

### With Other Projects

Skills from this repository are used in:

- Individual development projects
- Client work
- SaaS platforms
- Mobile applications
- Web applications

### Cross-Skill Integration

Skills complement each other:

```
feature-planning → Creates spec + implementation strategy
      ↓
multi-tenant-saas-architecture → Provides backend patterns
      ↓
mysql-best-practices → Database design
      ↓
webapp-gui-design → Delivers UI components
      ↓
vibe-security-skill → Ensures security
      ↓
[testing-skill] → Validates implementation
```

## Token Efficiency Best Practices

### Load Only What You Need

❌ **Expensive:**
```
Total tokens: 50,000 (10 skills × 5,000 tokens each)
Cost: High
```

✅ **Efficient:**
```
Total tokens: 5,000 (1 skill)
Cost: Low
```

### Combine Related Skills Only

```
# GOOD: Related skills for the task
"Using webapp-gui-design and vibe-security-skill, create a login page"

# BAD: Unrelated skills
"Using webapp-gui-design, mysql-best-practices, gis-mapping, and pos-sales-ui-design, create a login page"
```

## Cross-Platform Considerations

Skills work across:

- Different operating systems (Windows, macOS, Linux)
- Different tech stacks (JS, Python, PHP, Go, etc.)
- Different project scales (startup to enterprise)

Keep skills framework-agnostic where possible, or clearly specify requirements.

## When Users Fork This Repo

Users may fork to customize skills for their needs. Claude should:

1. Respect their customizations
2. Suggest merging improvements back upstream
3. Maintain compatibility with standard skills

## Summary

Effective skill usage:

1. **Load explicitly** - Only mention needed skills
2. **Combine thoughtfully** - Related skills only
3. **Apply completely** - Use full skill guidance
4. **Reference clearly** - Acknowledge which skill you're using
5. **Maintain security baseline** - Always apply vibe-security-skill for web work
6. **Use mysql-best-practices** - Mandatory for all database work

Skills make Claude more consistent, powerful, and valuable across projects.
