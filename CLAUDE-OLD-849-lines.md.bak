# Claude Code Guide - Skills Repository

This document provides specific guidance for Claude Code when working with this skills collection.

## Repository Context

**Purpose:** Shared skills library for use across multiple projects
**Type:** Reference/Knowledge Repository
**Usage Pattern:** Skills are loaded into Claude Code sessions in other projects

## How Claude Should Work With This Repository.

### When Asked to Use Skills

If a user mentions they want to use a skill from this collection:

1. **Understand the context:** Determine which project the user is working on
2. **Recommend the appropriate skill:** Based on their task requirements
3. **Explain how to load it:** Provide clear instructions for skill invocation
4. **Apply the skill's patterns:** Once loaded, follow the skill's guidelines precisely

If a user says "seeder-script", treat it as the saas-seeder skill.

### Security Baseline (Required for Web Apps)

For any web application work (frontend, backend, APIs), always load and apply the **Vibe Security Skill** alongside the primary skill. Security principles are non-optional and must be enforced in every relevant change.

### When Adding New Skills

If asked to create a new skill:

1. **Review existing skills:** Understand the format and structure
2. **Create skill directory:** `skill-name/` with appropriate naming
3. **Write SKILL.md:** Follow the frontmatter + markdown format
4. **Add documentation:** Update README.md and PROJECT_BRIEF.md
5. **Ensure completeness:** Include examples, patterns, and clear guidance

### When Modifying Existing Skills

If improving or fixing a skill:

1. **Read the current skill thoroughly:** Understand its purpose and patterns
2. **Make targeted improvements:** Don't completely rewrite unless necessary
3. **Maintain backward compatibility:** Existing users depend on these patterns
4. **Update documentation:** Reflect changes in README if significant
5. **Test the modification:** Ensure it still provides value

## Skill Invocation Pattern

When users invoke a skill, Claude should:

```markdown
1. Load the skill content
2. Acknowledge the skill is active
3. Apply the skill's patterns and guidelines
4. Reference the skill's best practices
5. Generate outputs consistent with the skill
```

Example:

```
User: "Use the webapp-gui-design skill to create a dashboard UI"

Claude: "I'm using the webapp-gui-design skill to create a polished dashboard UI.

[Applies established template patterns and optional bespoke aesthetics per skill guidelines]
```

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

### When Reading Skills

1. **Parse frontmatter:** Extract name and description
2. **Understand the full context:** Read the entire skill before applying
3. **Note key sections:** Overview, patterns, examples, anti-patterns
4. **Apply holistically:** Don't cherry-pick; use the full skill guidance

### When Creating Skills

1. **Follow the template:** Match existing skill structure
2. **Be comprehensive:** Include all necessary guidance
3. **Provide examples:** Real, working code samples
4. **Define scope clearly:** When to use and when not to use
5. **Include anti-patterns:** Show what to avoid

## Documentation Standards (MANDATORY)

**CRITICAL:** ALL markdown files (.md) created in this repository MUST follow strict standards:

✅ **500-line hard limit for ALL .md files** - No exceptions
- SKILL.md files: Max 500 lines
- Plan documents: Max 500 lines per file
- Specifications: Max 500 lines per file
- Manuals: Max 500 lines per page
- Reference docs: Max 500 lines per file
- Any other .md file: Max 500 lines

✅ **Two-tier documentation structure** (Required)
- **Tier 1:** High-level table of contents / index docs (200-300 lines)
- **Tier 2:** Deep dive topic-specific docs (max 500 lines each)

✅ **Smart subdirectory grouping** (Required)
- Group related docs in logical subdirectories
- Module-based: `docs/inventory/`, `docs/sales/`
- Type-based: `docs/coding/`, `docs/testing/`
- Workflow-based: `docs/buy-matooke/`, `docs/manufacturing/`

✅ **Regular documentation grooming**
- Improves session bootstrapping
- Reduces token consumption
- Better AI comprehension
- Easier knowledge transfer

📖 **See `skills/doc-standards.md` for complete requirements and examples**

## Skills Best Practices & Checklist

### Structure Requirements

**CRITICAL:** Always follow these structure rules:

✅ **One SKILL.md per skill** (required)

- Each skill is a single SKILL.md file
- No splitting across multiple files

✅ **Keep skills one level deep** in /skills/ directory

- Skills live at `skills/skill-name/SKILL.md`
- Never nest skills deeper (no `skills/category/skill-name/`)

✅ **Subdirectories for detailed content:**

```
skills/skill-name/
├── SKILL.md             # Core patterns (max 500 lines, strictly enforced)
├── references/          # Database schemas, data models (max 500 lines each)
├── documentation/       # Detailed guides (max 500 lines each)
└── examples/            # Code examples, templates, implementations
```

✅ **Skills are self-contained**

- No dependencies between skills
- Each skill loaded independently
- Subdirectories contain supplementary content

### SKILL.md Essentials

**Every SKILL.md must have:**

✅ **500-line hard limit** (strictly enforced)

- Core patterns and essentials only
- Move detailed content to subdirectories
- If explaining takes >500 lines, restructure

✅ **Scannable by AI:**

- Clear markdown headings (##, ###)
- Bullet points for lists
- Code blocks for examples
- Specific, unambiguous commands

✅ **Focus on broadly applicable patterns** (75-90% of use cases)

- Not edge cases or niche scenarios
- Common patterns most projects need
- Transferable across projects

✅ **Avoid generic tasks AI already knows:**

- No basic CRUD explanations
- No standard REST conventions
- No generic programming concepts
- No code style/linting rules

✅ **Frontmatter with name + description** (required)

```yaml
---
name: skill-name
description: "When to use this skill and what it does (acts as trigger)"
---
```

✅ **Description mentions when/how to use**

- Helps Claude remember when to apply the skill
- Clear triggers: "Use when adding features..." or "Use for multi-tenant..."

✅ **Body under 500 lines** (hard limit)

- Forces focus and clarity
- If longer, split into multiple skills or move details to references/

✅ **Reference supporting files in body**

- If scripts/ exists, mention in skill: "See scripts/deploy.sh for..."
- If references/ exists, mention: "Database schema in references/schema.sql"
- This tells Claude the files exist and are relevant

### Usage with Claude Code CLI

**How skills are loaded:**

✅ **Only explicitly mentioned skills get loaded**

- User must mention skill in prompt: "Using webapp-gui-design, create..."
- This saves tokens and costs
- Don't auto-load all skills

✅ **Multiple skills can be combined**

- "Using skills/skill-1 and skill-2..."
- "Using webapp-gui-design and multi-tenant-saas-architecture..."
- Load only what's needed for the task

✅ **Document skill usage in CLAUDE.md**

- Each project's CLAUDE.md should list which skills to use when
- Example: "For multi-tenant features, use multi-tenant-saas-architecture skill"

❌ **Don't load all skills globally**

- Wastes tokens (expensive)
- Adds irrelevant context
- Confuses Claude with unrelated patterns

### When Skills Are Worth Creating

**Create skills for:**

✅ **Repeatable patterns across multiple projects**

- PDF printing standards used in 5 apps
- Multi-tenant isolation patterns
- Deployment procedures

✅ **Company/domain-specific knowledge**

- African market payment requirements
- Healthcare compliance patterns (HIPAA, local regulations)
- Legal document formatting standards
- Education system-specific workflows

✅ **Complex workflows to remember**

- Complete deployment procedures
- Testing patterns with specific tools
- Migration strategies
- Security audit checklists

✅ **Code you find yourself re-explaining**

- Specific mPDF configurations
- Exact tenant isolation strategies
- API authentication patterns
- Database access control implementation

### When NOT to Create Skills

**Don't create skills for:**

❌ **Generic programming help**

- Claude Code handles this natively
- "How to write a for loop" - not a skill
- "REST API basics" - Claude knows this

❌ **One-off features or experimental ideas**

- Features used in only one project
- Experiments that might not work out
- Temporary workarounds

❌ **Frequently changing code** (too volatile)

- Code that changes weekly
- Experimental APIs
- Unstable third-party integrations

❌ **Code style/linting rules**

- Use ESLint, Prettier, PHPStan instead
- Linters enforce better than docs
- Skills should be about patterns, not syntax

### Common Mistakes to Avoid

❌ **Don't load all skills globally**

```
# BAD: Loading all skills always
"When coding, always use all skills in /skills/"

# GOOD: Load skills explicitly when needed
"Using multi-tenant-saas-architecture, implement tenant isolation"
```

❌ **Don't stuff CLAUDE.md with unrelated instructions**

```
# BAD: CLAUDE.md with everything
CLAUDE.md: 5000 lines covering every possible scenario

# GOOD: CLAUDE.md references skills
CLAUDE.md: "For multi-tenant features, use multi-tenant-saas-architecture skill"
```

❌ **Don't create skills for generic tasks**

```
# BAD: Generic skill
skills/how-to-write-functions/SKILL.md

# GOOD: Specific domain skill
skills/maduuka-erp-patterns/SKILL.md (with actual business rules)
```

❌ **Don't nest skills more than one level deep**

```
# BAD: Nested skills
skills/backend/api/rest/SKILL.md

# GOOD: Flat structure
skills/api-patterns/SKILL.md
```

### Specific Setup Patterns

**For cross-project standards:**

1. Create shared skills repo

```bash
skills-repo/
├── pdf-printing-standards/
├── multi-tenant-patterns/
└── african-market-payments/
```

1. Use git submodule in each app

```bash
cd my-app
git submodule add <skills-repo-url> skills
```

1. Reference in project's CLAUDE.md

```markdown
## Available Skills

- **pdf-printing-standards**: Use for any PDF generation
- **multi-tenant-patterns**: Use for tenant isolation features
```

**For system-specific skills:**

1. Create skill per major system

```
skills/
├── maduuka-erp/          # ERP-specific patterns
├── medic8/               # Healthcare patterns
├── kesilex/              # Legal system patterns
└── brightsoma/           # Education patterns
```

1. Include actual data in references/

```
skills/maduuka-erp/
├── SKILL.md
├── references/
│   ├── database-schema.sql    # Actual schema
│   ├── api-endpoints.md       # Actual API docs
│   └── business-rules.md      # Actual business logic
└── scripts/
    └── deploy.sh              # Actual deployment script
```

### Token Efficiency

**Why explicit loading matters:**

- Claude Code charges per token
- Loading 10 skills = 10,000+ tokens wasted if not needed
- Explicit loading = only pay for what you use

**Example:**

```
# Expensive: Load all skills
Total tokens: 50,000 (10 skills × 5,000 tokens each)
Cost: High

# Efficient: Load only needed skill
Total tokens: 5,000 (1 skill)
Cost: Low
```

### Quality Standards

Every skill should be:

1. **Token-efficient** - Only loaded when explicitly needed
2. **Focused** - Under 500 lines, single domain
3. **Self-contained** - No dependencies on other skills
4. **Actionable** - Provides concrete patterns, not theory
5. **Maintained** - Updated when patterns change
6. **Referenced** - Listed in project CLAUDE.md with usage guidance

## Skill Categories

Skills are organized by domain:

### Design Skills

- **webapp-gui-design:** Web app UI patterns, optional bespoke aesthetics
- **pos-sales-ui-design:** POS and sales entry UI patterns, invoice/receipt standards

### Architecture Skills

- **multi-tenant-saas-architecture:** Backend patterns, security, isolation

### Security Skills

- **dual-auth-rbac:** Dual authentication (Session + JWT), RBAC, multi-tenant isolation

### Database Skills

- **mysql-best-practices:** **MANDATORY for ALL database work** - Schema design, migrations, stored procedures, indexing, performance, multi-tenant isolation

### Process Skills

- **feature-planning:** Complete feature planning from specification to implementation, TDD workflows
- **update-claude-documentation:** Documentation maintenance, consistency checking
- **doc-architect:** Generate Triple-Layer AGENTS.md documentation (Root/Data/Planning)

### Future Categories

- Testing, DevOps, API Design, Performance

## Database Standards (CRITICAL)

**All database-related work MUST reference mysql-best-practices skill:**

### When to Use mysql-best-practices

✅ **ALWAYS use for:**
- Database migrations (adding/dropping tables, columns)
- Schema design and modifications
- Creating/updating stored procedures, triggers, views
- Adding indexes or foreign keys
- Query optimization
- Multi-tenant isolation patterns

### Migration Checklist (MANDATORY)

The mysql-best-practices skill includes a comprehensive migration checklist that MUST be followed:

**Pre-Migration:**
1. Grep entire codebase for table/column references
2. Check all stored procedures, triggers, views
3. Backup database

**Post-Migration:**
4. Verify no orphaned references in code
5. Test all affected endpoints
6. Export updated schema
7. Document rollback procedure

**Failure to follow this checklist causes production failures** (see MEMORY.md for examples).

## Common Workflows

### Workflow 1: User Requests Skill Usage

```
User: "I need help with multi-tenant authentication"

Claude:
1. Recognize this aligns with multi-tenant-saas-architecture skill
2. Reference or load the skill
3. Apply authentication patterns from the skill
4. Provide implementation guidance per skill's best practices
```

### Workflow 2: User Asks to Add Skill

```
User: "Create a skill for API design patterns"

Claude:
1. Review existing skills for format
2. Create api-design-patterns/ directory
3. Write SKILL.md with comprehensive patterns
4. Update README.md with new skill entry
5. Update PROJECT_BRIEF.md
6. Commit with clear message
```

### Workflow 3: Cross-Project Usage

```
User in Project A: "Use the webapp-gui-design skill"

Claude:
1. Confirm skill location (this repo or local copy)
2. Load skill content
3. Apply to Project A's context
4. Generate code following skill patterns
```

## Best Practices for Claude

### DO

✅ **Read skills completely** before applying them
✅ **Follow skill guidelines precisely** - they encode best practices
✅ **Combine skills when appropriate** - they're designed to work together
✅ **Update documentation** when adding/modifying skills
✅ **Maintain consistency** across all skills in format and quality
✅ **Provide clear examples** in skills
✅ **Reference skills explicitly** when using them ("Using webapp-gui-design skill...")

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
feature-planning → Creates spec + implementation strategy
      ↓
multi-tenant-saas-architecture → Provides backend patterns
      ↓
webapp-gui-design → Delivers UI components
      ↓
[testing-skill] → Validates implementation
```

## Version Control

### Commit Messages

When modifying this repository:

```bash
# Adding new skill
git commit -m "feat: add [skill-name] skill for [purpose]"

# Improving existing skill
git commit -m "improve: enhance [skill-name] with [addition]"

# Fixing skill issues
git commit -m "fix: correct [issue] in [skill-name]"

# Updating documentation
git commit -m "docs: update README with [changes]"
```

### Branch Strategy

```
main                    # Stable, tested skills
├── skill/[name]       # New skill development
├── improve/[name]     # Skill improvements
└── docs/[change]      # Documentation updates
```

## Testing Skills

### Manual Testing

Before committing a new or modified skill:

1. **Load the skill** in a test Claude Code session
2. **Apply it to a realistic scenario**
3. **Verify the output** matches intended patterns
4. **Check for edge cases**
5. **Validate examples** actually work

### Validation Checklist

- [ ] Frontmatter is valid YAML
- [ ] Description clearly states when to use
- [ ] Examples are complete and working
- [ ] Patterns are specific and actionable
- [ ] Anti-patterns are documented
- [ ] Markdown formatting is correct
- [ ] File structure follows conventions
- [ ] Documentation is updated

## Common Tasks

### Adding a Skill

```bash
# 1. Create directory
mkdir new-skill-name

# 2. Create SKILL.md
cat > new-skill-name/SKILL.md << 'EOF'
---
name: new-skill-name
description: What this skill does and when to use it
---

# Skill Name

[Content here]
EOF

# 3. Update documentation
# Edit README.md and PROJECT_BRIEF.md

# 4. Commit
git add new-skill-name/ README.md PROJECT_BRIEF.md
git commit -m "feat: add new-skill-name for [purpose]"
```

### Updating a Skill

```bash
# 1. Read current skill
cat skill-name/SKILL.md

# 2. Make improvements
# Edit skill-name/SKILL.md

# 3. Update docs if needed
# Edit README.md if skill description changed

# 4. Commit
git add skill-name/ README.md
git commit -m "improve: enhance skill-name with [addition]"
```

### Reviewing Skills

When reviewing skills (user request or self-review):

1. **Check for accuracy:** Patterns should be current best practices
2. **Verify examples:** Code samples should be complete and correct
3. **Test applicability:** Ensure skill works across scenarios
4. **Validate scope:** Skill should be focused but comprehensive
5. **Update if needed:** Improve based on real-world usage

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

## Maintenance Guidelines

### Regular Reviews

Periodically review skills for:

- Outdated patterns or technologies
- Improved best practices
- User feedback
- Real-world applicability

### Skill Lifecycle

```
Created → Tested → Released → Maintained → Enhanced/Deprecated
```

- **Created:** New skill added
- **Tested:** Verified in real scenarios
- **Released:** Available in main branch
- **Maintained:** Updated as needed
- **Enhanced:** Improved based on usage
- **Deprecated:** Replaced by better approach (don't delete, document)

## Special Considerations

### When Users Fork This Repo

Users may fork to customize skills for their needs. Claude should:

1. Respect their customizations
2. Suggest merging improvements back upstream
3. Maintain compatibility with standard skills

### Cross-Platform Considerations

Skills should work across:

- Different operating systems (Windows, macOS, Linux)
- Different tech stacks (JS, Python, PHP, Go, etc.)
- Different project scales (startup to enterprise)

Keep skills framework-agnostic where possible, or clearly specify requirements.

## Troubleshooting

### Skill Not Loading

1. Check file path
2. Verify YAML frontmatter syntax
3. Confirm markdown formatting
4. Review for parsing errors

### Skill Producing Unexpected Results

1. Re-read skill completely
2. Check if context matches skill's intended use case
3. Verify all skill patterns are being applied
4. Ask user for clarification if ambiguous

### Multiple Applicable Skills

1. Determine primary domain of the task
2. Load the most specific skill first
3. Reference other skills as needed
4. Combine patterns thoughtfully

## Summary

This skills collection is a **living library** of reusable expertise. Claude should:

- ✅ Apply skills precisely and completely
- ✅ Maintain high quality standards
- ✅ Keep documentation in sync
- ✅ Suggest improvements based on usage
- ✅ Help users leverage skills effectively

Skills are designed to make Claude more consistent, powerful, and valuable across projects. Treat them as encoded best practices that improve over time.

---

**For Claude Code Internal Use**
This guide ensures consistent, high-quality interaction with the skills repository.
When in doubt, read the skill thoroughly before applying it.

**Last Updated:** January 2026
**Maintained by:** Peter Bamuhigire
