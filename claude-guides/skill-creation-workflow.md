# Skill Creation Workflow

This guide covers the complete workflow for adding new skills or modifying existing ones.

## When to Create a New Skill

### Create Skills For

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

## Adding a New Skill

### Step 1: Review Existing Skills

Before creating a new skill:

1. **Read current skills thoroughly:** Understand format and structure
2. **Check for overlaps:** Ensure you're not duplicating existing skills
3. **Identify gaps:** Confirm this skill fills a genuine need

### Step 2: Create Skill Directory

```bash
# Create directory
mkdir skills/new-skill-name

# Follow naming conventions:
# - Use kebab-case
# - Be descriptive but concise
# - Examples: multi-tenant-saas-architecture, webapp-gui-design
```

### Step 3: Write SKILL.md

Create the core skill file:

```bash
cat > skills/new-skill-name/SKILL.md << 'EOF'
---
name: new-skill-name
description: What this skill does and when to use it
---

# Skill Name

## Overview

[What this skill provides and when to use it]

## Core Patterns

[The most common patterns - 75-90% of use cases]

## Quick Reference

[Tables, checklists, commands]

## Examples

[Working code samples]

## Common Pitfalls

[What to avoid and why]

## See Also

[Links to references/ or documentation/ subdirectories]
EOF
```

**CRITICAL Requirements:**

- **500-line hard limit** (strictly enforced)
- Valid YAML frontmatter with name + description
- Description mentions when/how to use (acts as trigger)
- Core patterns focused on broadly applicable patterns (75-90% of use cases)
- Avoid generic tasks AI already knows
- Reference supporting files in body

### Step 4: Add Supporting Content

If your skill needs detailed content (>500 lines total):

```bash
# Create subdirectories
mkdir -p skills/new-skill-name/references
mkdir -p skills/new-skill-name/documentation
mkdir -p skills/new-skill-name/examples

# Add detailed content
# references/ - Database schemas, data models (max 500 lines each)
# documentation/ - Detailed guides (max 500 lines each)
# examples/ - Code examples, templates, implementations
```

**Structure Example:**

```
skills/new-skill-name/
├── SKILL.md                    # Core patterns (max 500 lines)
├── references/
│   ├── database-schema.sql     # Database schema
│   └── api-endpoints.md        # API specifications
├── documentation/
│   ├── advanced-patterns.md    # Deep dive guides
│   └── troubleshooting.md      # Error handling
└── examples/
    ├── example-1.php
    └── example-2.js
```

### Step 5: Update Documentation

Update the main repository documentation:

**README.md:**
```markdown
### [Skill Category]

- **new-skill-name:** Brief description of what it does
```

**PROJECT_BRIEF.md:**
```markdown
## Skills

- **new-skill-name:** When to use it and what it provides
```

### Step 6: Test the Skill

Before committing:

1. **Load the skill** in a test Claude Code session
2. **Apply it to a realistic scenario**
3. **Verify the output** matches intended patterns
4. **Check for edge cases**
5. **Validate examples** actually work

### Step 7: Commit

```bash
# Add files
git add skills/new-skill-name/ README.md PROJECT_BRIEF.md

# Commit with clear message
git commit -m "feat: add new-skill-name for [purpose]"
```

## Modifying Existing Skills

### Step 1: Read Current Skill Thoroughly

Before making changes:

1. **Understand its purpose and patterns**
2. **Review real-world usage** (if available)
3. **Identify the specific issue** or improvement needed

### Step 2: Make Targeted Improvements

**DO:**
- Fix errors or outdated patterns
- Add missing examples
- Clarify ambiguous sections
- Improve organization
- Add cross-references

**DON'T:**
- Completely rewrite unless absolutely necessary
- Change the core purpose or scope
- Remove working examples
- Break backward compatibility

### Step 3: Maintain Backward Compatibility

Existing users depend on these patterns:

- Keep existing sections intact (unless removing errors)
- Add new patterns rather than replacing working ones
- Document breaking changes if absolutely necessary
- Update examples to match changes

### Step 4: Update Documentation

If changes are significant:

- Update skill description in README.md
- Add changelog entry if skill has one
- Update PROJECT_BRIEF.md if purpose changed
- Update cross-references in other skills

### Step 5: Test the Modification

Ensure the skill still provides value:

1. **Apply the modified skill** to test scenarios
2. **Verify examples still work**
3. **Check that improvements achieve their goal**
4. **Test edge cases**

### Step 6: Commit Changes

```bash
# Add modified files
git add skills/skill-name/ README.md

# Commit with descriptive message
git commit -m "improve: enhance skill-name with [addition/fix]"
```

## Skill File Format

### SKILL.md Structure

```yaml
---
name: skill-name
description: "When to use this skill and what it does (acts as trigger)"
---

# Skill Title

## Overview

Brief introduction to what this skill provides and when to use it.

## Core Patterns

The most common patterns (75-90% of use cases). Avoid edge cases or niche scenarios.

### Pattern 1: [Name]

[Description and example]

### Pattern 2: [Name]

[Description and example]

## Quick Reference

Tables, checklists, or command lists for quick lookup.

## Examples

Working code samples that demonstrate the patterns.

## Common Pitfalls

What to avoid and why.

## See Also

Links to:
- `references/` - Deep dive content
- `documentation/` - Detailed guides
- `examples/` - Code samples
- Related skills
```

### Frontmatter Requirements

**Required fields:**
```yaml
---
name: skill-name        # Must match directory name
description: "..."      # Clear trigger for when to use
---
```

**Description best practices:**
- Mention when to use: "Use when adding features..."
- Mention what it does: "Provides multi-tenant isolation patterns..."
- Be specific: "For MySQL 8.x database design" not "For databases"
- Acts as trigger for Claude to load the skill

## Validation Checklist

Before committing a new or modified skill:

- [ ] Frontmatter is valid YAML
- [ ] Description clearly states when to use
- [ ] SKILL.md is under 500 lines (strict)
- [ ] Examples are complete and working
- [ ] Patterns are specific and actionable
- [ ] Anti-patterns are documented
- [ ] Markdown formatting is correct
- [ ] File structure follows conventions
- [ ] Documentation is updated
- [ ] Supporting files referenced in SKILL.md
- [ ] Tested in real scenario
- [ ] No generic tasks AI already knows
- [ ] Focused on 75-90% use cases

## Quality Standards

Every skill should be:

1. **Token-efficient** - Only loaded when explicitly needed
2. **Focused** - Under 500 lines, single domain
3. **Self-contained** - No dependencies on other skills
4. **Actionable** - Provides concrete patterns, not theory
5. **Maintained** - Updated when patterns change
6. **Referenced** - Listed in project CLAUDE.md with usage guidance

## Common Mistakes to Avoid

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

❌ **Don't exceed 500 lines in SKILL.md**

```
# BAD: Everything in one file
skills/huge-skill/SKILL.md (1,200 lines)

# GOOD: Core patterns + references
skills/skill-name/SKILL.md (450 lines)
skills/skill-name/references/advanced.md (500 lines)
skills/skill-name/references/troubleshooting.md (350 lines)
```

❌ **Don't forget to reference supporting files**

```
# BAD: Files exist but not mentioned
skills/my-skill/SKILL.md (no mention of scripts/)
skills/my-skill/scripts/deploy.sh (orphaned)

# GOOD: Files referenced in SKILL.md
"See scripts/deploy.sh for deployment automation"
```

## Skill Lifecycle

```
Created → Tested → Released → Maintained → Enhanced/Deprecated
```

- **Created:** New skill added
- **Tested:** Verified in real scenarios
- **Released:** Available in main branch
- **Maintained:** Updated as needed
- **Enhanced:** Improved based on usage
- **Deprecated:** Replaced by better approach (don't delete, document)

## Cross-Project Setup Patterns

### Pattern 1: Shared Skills Repository

For cross-project standards:

```bash
# 1. Create shared skills repo
skills-repo/
├── pdf-printing-standards/
├── multi-tenant-patterns/
└── african-market-payments/

# 2. Use git submodule in each app
cd my-app
git submodule add <skills-repo-url> skills

# 3. Reference in project's CLAUDE.md
```

**Project CLAUDE.md:**
```markdown
## Available Skills

- **pdf-printing-standards**: Use for any PDF generation
- **multi-tenant-patterns**: Use for tenant isolation features
```

### Pattern 2: System-Specific Skills

For individual systems:

```bash
# Create skill per major system
skills/
├── maduuka-erp/          # ERP-specific patterns
├── medic8/               # Healthcare patterns
├── kesilex/              # Legal system patterns
└── brightsoma/           # Education patterns

# Include actual data in references/
skills/maduuka-erp/
├── SKILL.md
├── references/
│   ├── database-schema.sql    # Actual schema
│   ├── api-endpoints.md       # Actual API docs
│   └── business-rules.md      # Actual business logic
└── scripts/
    └── deploy.sh              # Actual deployment script
```

## Version Control

### Commit Messages

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

## Regular Maintenance

### Review Schedule

Periodically review skills for:

- Outdated patterns or technologies
- Improved best practices
- User feedback
- Real-world applicability

### Grooming Checklist

- [ ] Remove outdated information
- [ ] Update examples to current patterns
- [ ] Verify all examples work
- [ ] Check line counts (all <500)
- [ ] Consolidate duplicate content
- [ ] Add missing examples
- [ ] Update cross-references
- [ ] Improve clarity

**Grooming Frequency:**
- After major project: Review related skills
- Quarterly: Review all skills
- Before project handoff: Complete audit
- When skills feel "heavy": Immediate refactor
