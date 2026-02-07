# Documentation Standards (MANDATORY)

**CRITICAL:** These standards apply to ALL markdown files in the project: CLAUDE.md, SKILL.md files, plan documents, specifications, manuals, guides, and any other .md files.

## Core Rules (Non-Negotiable)

### Rule 1: 500-Line Hard Limit

**Every .md file MUST NOT exceed 500 lines.**

This is a **hard limit**, not a suggestion. Files that exceed 500 lines **MUST** be broken down.

**Why 500 lines?**
- Faster AI parsing and context loading
- Reduced token consumption (lower costs)
- Easier maintenance and updates
- Better navigability and discoverability
- Improved session bootstrapping

**Enforcement:**
- Check line count before committing: `wc -l file.md`
- If >500 lines, immediately refactor into smaller files
- No exceptions

### Rule 2: Two-Tier Documentation Structure

Use a hierarchical organization pattern:

**Tier 1: High-Level Table of Contents (TOC)**
- Overview document with navigation
- Max 200-300 lines
- Links to Tier 2 docs
- Quick reference sections
- Essential patterns only

**Tier 2: Deep Dive Documents**
- Focused topic-specific docs
- Max 500 lines each
- Detailed implementation guides
- Complete code examples
- Troubleshooting and edge cases

**Example Structure:**

```
docs/
├── README.md                    # Tier 1: Main TOC (250 lines)
├── coding/
│   ├── README.md               # Tier 1: Coding TOC (200 lines)
│   ├── ui-patterns.md          # Tier 2: UI deep dive (450 lines)
│   ├── api-patterns.md         # Tier 2: API deep dive (480 lines)
│   └── database-patterns.md    # Tier 2: DB deep dive (500 lines)
├── modules/
│   ├── inventory/
│   │   ├── README.md           # Tier 1: Inventory TOC (180 lines)
│   │   ├── stock-entries.md    # Tier 2: Stock entry guide (450 lines)
│   │   └── batch-tracking.md   # Tier 2: Batch tracking (420 lines)
│   └── sales/
│       ├── README.md           # Tier 1: Sales TOC (220 lines)
│       ├── pos-workflow.md     # Tier 2: POS deep dive (500 lines)
│       └── invoicing.md        # Tier 2: Invoicing guide (480 lines)
```

### Rule 3: Smart Subdirectory Grouping

Group related documentation in logical subdirectories:

**By Module/Domain:**
```
docs/inventory/
docs/sales/
docs/accounting/
docs/hr/
```

**By Type:**
```
docs/coding/        # Development guides
docs/testing/       # Testing documentation
docs/deployment/    # Deployment guides
docs/api/          # API documentation
```

**By Workflow:**
```
docs/buy-matooke/  # Complete matooke procurement workflow
docs/manufacturing/ # Manufacturing processes
docs/payroll/      # Payroll workflows
```

## Documentation Types & Limits

| Document Type              | Max Lines | Structure                          |
|----------------------------|-----------|-------------------------------------|
| CLAUDE.md                  | 500       | TOC with links to docs/            |
| SKILL.md                   | 500       | Core patterns + links to references|
| Plan documents             | 500       | Overview + links to plan sections  |
| Specifications             | 500       | Spec only, or TOC + linked sections|
| Manuals                    | 500       | Per-page or TOC + linked pages     |
| API docs                   | 500       | Per endpoint group, or TOC         |
| Database docs              | 500       | Per module, or TOC + table groups  |
| Feature guides             | 500       | Per feature, or TOC + sections     |

## Breaking Down Large Documents

### Pattern 1: Topic-Based Split

**Before (850 lines):**
```
docs/INVENTORY_GUIDE.md  # 850 lines - TOO LONG
```

**After:**
```
docs/inventory/
├── README.md            # 200 lines: TOC + overview
├── stock-entries.md     # 350 lines: Stock entry workflows
├── batch-tracking.md    # 400 lines: Batch and expiry management
└── reports.md           # 300 lines: Inventory reports
```

### Pattern 2: Workflow-Based Split

**Before (920 lines):**
```
docs/SALES_WORKFLOWS.md  # 920 lines - TOO LONG
```

**After:**
```
docs/sales/
├── README.md            # 180 lines: TOC + overview
├── pos-workflow.md      # 480 lines: POS complete workflow
├── invoice-workflow.md  # 420 lines: Manual invoicing
├── quotations.md        # 360 lines: Quotation management
└── returns.md           # 280 lines: Sales returns
```

### Pattern 3: Reference-Based Split

**Before (1200 lines):**
```
ARCHITECTURE.md          # 1200 lines - TOO LONG
```

**After:**
```
ARCHITECTURE.md          # 300 lines: High-level overview + TOC
docs/architecture/
├── service-layer.md     # 400 lines: Service layer patterns
├── data-access.md       # 350 lines: Database access patterns
├── api-design.md        # 450 lines: API architecture
└── security.md          # 500 lines: Security architecture
```

## Grooming Documents for Better Context

**Regular Grooming Benefits:**
- Faster session bootstrapping
- Reduced token consumption
- Better AI comprehension
- Easier knowledge transfer
- Improved team onboarding

**Grooming Checklist:**
- [ ] Remove outdated information
- [ ] Consolidate duplicate content
- [ ] Update examples to current patterns
- [ ] Verify all links work
- [ ] Check line counts (all <500)
- [ ] Ensure TOC docs link to deep dives
- [ ] Add missing deep dive docs
- [ ] Remove verbose explanations
- [ ] Use tables for comparisons
- [ ] Use code blocks for examples

**Grooming Frequency:**
- After major features: Always
- Monthly: Review and refactor
- Before project handoff: Complete audit
- When docs feel "heavy": Immediate refactor

## CLAUDE.md Specific Rules

**CRITICAL:** CLAUDE.md must be a **navigation hub**, not a comprehensive guide.

**Max Size:** 500 lines (strictly enforced)

**What Goes in CLAUDE.md:**
- Project overview (2-3 paragraphs)
- Tech stack summary
- Quick reference to key files
- Critical business rules (5-10 rules max)
- Links to detailed guides in docs/
- Common pitfalls (5-10 max)
- Development workflow (brief)

**What Does NOT Go in CLAUDE.md:**
- Detailed implementation guides (→ docs/coding/)
- Complete API documentation (→ docs/API.md)
- Full database schema (→ docs/DATABASE.md)
- Module-specific workflows (→ docs/[module]/)
- Testing procedures (→ docs/testing/)
- Deployment steps (→ docs/deployment/)

**CLAUDE.md Structure:**
```markdown
# CLAUDE.md

## System Overview
[2-3 paragraphs]

## Documentation Map
- Root docs: README.md, PROJECT_BRIEF.md, TECH_STACK.md
- Coding guides: docs/coding/
- Module docs: docs/[module-name]/
- Testing: docs/testing/

## Quick Reference
### Tech Stack
[Brief list with versions]

### Development Commands
[5-10 most common commands]

### Critical Business Rules
[5-10 most critical rules with brief explanation]

## Common Pitfalls
[5-10 common mistakes to avoid]

## Where to Find Details
- UI Development: docs/coding/UI_DEVELOPMENT_GUIDE.md
- API Patterns: docs/API.md
- Database Schema: docs/DATABASE.md
- Module X: docs/module-x/README.md
```

## Plan Documents Specific Rules

**Plans must follow the same 500-line limit.**

**For Simple Plans:**
- Single file: `docs/plans/YYYY-MM-DD-feature-name.md` (max 500 lines)

**For Complex Plans:**
```
docs/plans/
├── YYYY-MM-DD-feature-name.md       # 200 lines: Overview + TOC
└── feature-name/
    ├── 01-database.md               # 450 lines: DB changes
    ├── 02-api.md                    # 480 lines: API implementation
    ├── 03-ui.md                     # 500 lines: UI implementation
    └── 04-testing.md                # 350 lines: Testing strategy
```

## Skill Documents Specific Rules

**SKILL.md files MUST NOT exceed 500 lines.**

**Structure:**
```
skills/skill-name/
├── SKILL.md                  # Max 500 lines: Core patterns
├── references/               # Deep dive content
│   ├── topic-a.md           # Max 500 lines each
│   ├── topic-b.md
│   └── topic-c.md
├── documentation/            # Detailed guides
│   ├── guide-1.md
│   └── guide-2.md
└── examples/                 # Code examples
    └── example.php
```

**SKILL.md Content:**
- Overview (what/when to use)
- Core patterns (most common 80% of use cases)
- Quick reference tables
- Links to references/ for deep dives
- Links to examples/
- Common pitfalls

**What Goes in references/:**
- Database schemas
- API specifications
- Detailed workflows
- Advanced patterns
- Framework-specific guides
- Troubleshooting guides

## Enforcement Workflow

**Before Committing:**
1. Check line count: `wc -l file.md`
2. If >500 lines, refactor immediately
3. Create subdirectory if needed
4. Split into TOC + deep dive docs
5. Update parent TOC with links

**During Code Review:**
- Flag any .md file >500 lines
- Require refactoring before merge
- Verify TOC structure exists
- Check subdirectory organization

**Monthly Audit:**
- Run: `find . -name "*.md" -exec wc -l {} + | sort -rn`
- Identify files >500 lines
- Schedule refactoring sprints
- Update TOC documents

## Benefits Summary

**Token Efficiency:**
- Load only what's needed
- Reduce context window usage by 60-80%
- Lower API costs
- Faster response times

**Maintainability:**
- Easier to update specific topics
- Clear ownership per document
- Reduced merge conflicts
- Better version control diffs

**Discoverability:**
- TOC provides clear navigation
- Topic-based organization
- Easier to find information
- Better for new team members

**AI Comprehension:**
- Focused context per document
- Better pattern recognition
- Improved code generation
- Faster session bootstrapping

## Examples from BIRDC ERP

**Good Example:**
```
docs/manufacturing/
├── README.md                 # 220 lines: Overview + TOC
├── work-orders.md            # 480 lines: Work order workflow
├── recipes.md                # 450 lines: Recipe management
└── production-execution.md   # 500 lines: Production process
```

**Bad Example:**
```
docs/MANUFACTURING_COMPLETE_GUIDE.md  # 1,850 lines - REFACTOR IMMEDIATELY
```

**Refactored:**
Split into the good example above, plus:
```
docs/manufacturing/
├── quality-control.md        # 420 lines: QC procedures
└── reporting.md              # 380 lines: Manufacturing reports
```

## Summary

**Remember:**
1. **500 lines maximum** - No exceptions
2. **Two-tier structure** - TOC + deep dives
3. **Smart grouping** - Logical subdirectories
4. **Regular grooming** - Keep docs fresh
5. **CLAUDE.md as hub** - Not a comprehensive guide
6. **Check before commit** - Enforce the limits

**These standards are MANDATORY for:**
- All new documentation
- All documentation updates
- All skills
- All plans
- All manuals
- All guides

**Non-compliance:**
- Files >500 lines will be rejected in code review
- Must refactor before merge
- No exceptions for "special cases"

**Last Updated:** 2026-02-07
**Status:** MANDATORY - Strictly Enforced
