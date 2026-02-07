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
├── multi-tenant-saas-architecture/  # SaaS backend patterns
├── feature-planning/                # Complete feature planning (spec + implementation)
├── ai-assisted-development/         # AI agent orchestration for development workflows
├── update-claude-documentation/     # Documentation maintenance
├── doc-architect/                   # Triple-Layer AGENTS.md generator
├── manual-guide/                    # End-user manuals and guides
├── dual-auth-rbac/                  # Dual auth + RBAC security
├── webapp-gui-design/               # Web app GUI design
├── pos-sales-ui-design/             # POS & sales entry UI
├── report-print-pdf/                # Report export (PDF + print)
├── api-error-handling/              # API error handling
├── mysql-best-practices/            # MySQL 8.x best practices
├── saas-seeder/                     # SaaS bootstrap and seeding
├── gis-mapping/                     # OpenStreetMap GIS + geofencing
├── vibe-security-skill/             # Secure coding for web apps
├── skill-writing/                   # Skill creator (meta-skill)
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
**Last Updated:** 2026-02-07
**Line Count:** ~250 lines (compliant with doc-standards.md)
