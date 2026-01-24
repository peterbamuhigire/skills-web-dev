---
name: update-claude-documentation
description: "Efficiently update project documentation files (README.md, PROJECT_BRIEF.md, TECH_STACK.md, ARCHITECTURE.md, docs/API.md, docs/DATABASE.md, CLAUDE.md) when significant changes occur. Use when adding features, changing architecture, updating dependencies, or modifying project structure. Ensures consistency across all documentation."
---

# Update Claude Documentation

## Overview

Systematic approach to updating project documentation when significant changes occur. Ensures all documentation files remain consistent, accurate, and synchronized.

**Core Principle:** Documentation should tell a cohesive story. Each file serves a specific audience, but all must reflect the same reality.

## When to Use

Invoke when:
- ✅ Adding/removing features
- ✅ Changing architecture or design patterns
- ✅ Updating dependencies or tech stack
- ✅ Modifying API endpoints or database schema
- ✅ Restructuring project directories
- ✅ Changing development workflows

Don't use for:
- ❌ Fixing typos (do directly)
- ❌ Minor code comments
- ❌ WIP features not yet merged

## Documentation File Ecosystem

### File Purposes

| File | Audience | Purpose | Update When |
|------|----------|---------|-------------|
| PROJECT_BRIEF.md | Stakeholders, new devs | 30-sec overview | Scope/purpose changes |
| README.md | Developers | Setup, usage guide | Setup/usage changes |
| TECH_STACK.md | Developers, DevOps | Tech inventory | Dependencies change |
| ARCHITECTURE.md | Senior devs, architects | System design | Design changes |
| docs/API.md | API consumers | API reference | API changes |
| docs/DATABASE.md | Backend devs, DBAs | Schema docs | DB schema changes |
| CLAUDE.md | Claude Code | Dev patterns | Pattern/workflow changes |

### Change Type → Affected Files

```
New Feature
  ├→ PROJECT_BRIEF.md (if significant)
  ├→ README.md (usage)
  ├→ ARCHITECTURE.md (if adds components)
  ├→ docs/API.md (if adds endpoints)
  ├→ docs/DATABASE.md (if adds tables)
  └→ CLAUDE.md (if changes patterns)

Tech Stack Change
  ├→ TECH_STACK.md (always)
  ├→ README.md (setup)
  ├→ ARCHITECTURE.md (if affects design)
  └→ CLAUDE.md (if affects workflows)

Architecture Change
  ├→ ARCHITECTURE.md (always)
  ├→ README.md (overview)
  ├→ PROJECT_BRIEF.md (if major)
  └→ CLAUDE.md (patterns)

API/Database Change
  ├→ docs/API.md or docs/DATABASE.md (always)
  ├→ ARCHITECTURE.md (if changes contracts)
  └→ CLAUDE.md (if affects patterns)
```

## Efficient Update Workflow

### Phase 1: Understand the Change (2-5 min)

**Create change summary:**
```markdown
Type: [Feature/Architecture/Tech Stack/API/Database]
What: [One sentence description]
Impact: [Who/what is affected]
Breaking: [Yes/No - what breaks]
```

### Phase 2: Map to Files (1-2 min)

**Quick Decision Matrix:**

| Changed | Update (in order) |
|---------|-------------------|
| API endpoints | API.md → CLAUDE.md → README.md |
| Database | DATABASE.md → ARCHITECTURE.md → CLAUDE.md |
| Dependencies | TECH_STACK.md → README.md → CLAUDE.md |
| Architecture | ARCHITECTURE.md → README.md → CLAUDE.md → BRIEF.md |
| Features | README.md → API.md (if needed) → CLAUDE.md → BRIEF.md |

### Phase 3: Read Current State (Parallel, 2-3 min)

Read all affected files **in parallel** to understand current state.

### Phase 4: Update Systematically (Sequential, 10-20 min)

**Update order (specific → general):**
```
1. Technical Specs (API.md, DATABASE.md)
2. Architecture (ARCHITECTURE.md, TECH_STACK.md)
3. AI Instructions (CLAUDE.md)
4. User Guides (README.md)
5. Overview (PROJECT_BRIEF.md)
```

**Per-file checklist:**
- [ ] Update primary section
- [ ] Update related sections
- [ ] Update examples/code snippets
- [ ] Add migration notes if breaking
- [ ] Verify consistency with previous updates

### Phase 5: Verify Consistency (2-3 min)

Check across all files:
- [ ] **Terminology** - Same terms everywhere?
- [ ] **Versions** - Consistent version numbers?
- [ ] **Paths** - Same file structure?
- [ ] **Names** - Components named consistently?
- [ ] **Features** - Same capabilities described?

### Phase 6: Final Review (1 min)

- [ ] New dev can understand from README?
- [ ] CLAUDE.md has enough context?
- [ ] Breaking changes clearly marked?
- [ ] Examples actually work?
- [ ] Nothing contradictory?

**Total Time:** 15-30 minutes

## Update Patterns

### Pattern 1: New Feature

```markdown
# 1. docs/API.md (if API endpoints)
### POST /api/auth/login
[Full endpoint spec]

# 2. ARCHITECTURE.md (if new components)
### Authentication Service
**Components:** AuthController, AuthService, AuthMiddleware
**Flow:** [Description]

# 3. CLAUDE.md (dev patterns)
## Authentication Patterns
- Hash passwords with bcrypt (12 rounds)
- JWT tokens expire in 24 hours
- Use AuthMiddleware on protected routes

# 4. README.md (usage)
## Features
- **User Authentication**: Secure login/logout with JWT
### Example
[Working code example]
```

### Pattern 2: Tech Stack Update

```markdown
# 1. TECH_STACK.md
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2.0 | UI framework |

**Recent Changes:**
- 2025-01: Upgraded React 17 → 18

# 2. README.md
## Prerequisites
- Node.js 18.x or higher

# 3. CLAUDE.md
### React 18 Patterns
- Use `useTransition` for non-urgent updates
- Automatic batching enabled
```

### Pattern 3: Architecture Change

```markdown
# 1. ARCHITECTURE.md
## System Architecture
[Diagrams and complete design]

# 2. README.md
## Architecture
Microservices architecture. See ARCHITECTURE.md.

# 3. CLAUDE.md
## Development Patterns
[Service-specific patterns]

# 4. PROJECT_BRIEF.md
## Architecture
Microservices with API Gateway pattern.
```

### Pattern 4: Database Change

```markdown
# 1. docs/DATABASE.md
### Users Table
[Schema definition]

### Relationships
[ERD and relationships]

### Common Queries
[SQL examples]

## Migrations
**Latest:** 002_add_roles.sql
[Migration details]

# 2. ARCHITECTURE.md (if data model changes)
### Data Layer
[Updated data access patterns]

# 3. CLAUDE.md (if affects patterns)
## Database Patterns
[Updated query patterns]
```

### Pattern 5: Breaking Changes

**Must appear in ALL affected docs:**

```markdown
## Breaking Changes

### v2.0.0 - [Change Name]

**Changed:**
- [What changed from → to]

**Migration:**
[How to update]

**Timeline:**
- Deprecated: [Date]
- Removed: [Date]
```

## Time-Saving Techniques

### 1. Batch File Reading
```bash
# Read all affected files in parallel
Read [docs/API.md, CLAUDE.md, README.md]
```

### 2. Diff-Based Updates
```bash
# Update only changed sections, not entire files
Edit FILE.md (old_section) → (new_section)
```

### 3. Consistency Checking
```bash
# Quick grep for inconsistencies
grep -r "authentication\|auth" *.md docs/*.md
grep -r "version" *.md docs/*.md
```

## Common Mistakes

### ❌ Updating in Wrong Order
```markdown
# WRONG: Update README first, then API.md
# README now has wrong endpoint names!

# RIGHT: Update API.md first, then README
```

### ❌ Forgetting Cross-References
```markdown
# Updated ARCHITECTURE.md but forgot CLAUDE.md
# Now they contradict each other!
```

### ❌ Outdated Examples
```markdown
# Changed endpoint /v1/users → /v2/users
# Forgot to update examples in README
# Examples now return 404!
```

### ❌ Version Mismatches
```markdown
# TECH_STACK.md: "React 18.2.0"
# README.md: "React 18.x"
# CLAUDE.md: "React 18.0"
# Which is it?!
```

## Verification Checklist

Before considering update complete:

- [ ] All affected files identified
- [ ] Files updated in correct order
- [ ] Terminology consistent
- [ ] Version numbers match
- [ ] File paths consistent
- [ ] Component names consistent
- [ ] Breaking changes noted everywhere
- [ ] Examples tested
- [ ] No contradictions
- [ ] Cross-references valid

## Examples

### Simple Dependency Update

**Change:** Update express 4.18.0 → 4.19.0 (patch)

**Files:** TECH_STACK.md only (version number)

**Time:** 2 minutes

### Breaking API Change

**Change:** Rename /api/login → /api/auth/login

**Files:**
1. docs/API.md - Endpoint docs
2. README.md - Examples
3. CLAUDE.md - Patterns
4. ARCHITECTURE.md - Structure

**Time:** 15 minutes

### Major Architecture Refactor

**Change:** Monolith → Microservices

**Files:** All (ARCHITECTURE, README, CLAUDE, BRIEF, TECH_STACK)

**Time:** 45-60 minutes

## Advanced Tips

### Auto-Generate Where Possible

```bash
# Generate API docs from OpenAPI spec
npx @redocly/cli build-docs openapi.yaml -o docs/API.md

# Then manually update narrative docs
```

### Documentation-Driven Development

1. Update docs FIRST (describes what will exist)
2. Implement the change
3. Verify docs match implementation

### Template Sections

Keep templates for common updates:

**Feature Template:**
```markdown
## Features
- **[Name]**: [Description]
  - [Capability 1]
  - [Capability 2]

### Example
[Code]
```

**Tech Stack Template:**
```markdown
| Technology | Version | Purpose |
|------------|---------|---------|
| [Name] | [Version] | [Why] |
```

## Summary

### Efficient Process

```
1. Understand (2-5 min) → Change summary
2. Map (1-2 min) → File list
3. Read (2-3 min) → Current state
4. Update (10-20 min) → Specific → General
5. Verify (2-3 min) → Consistency checks
6. Review (1 min) → Sanity check

Total: 15-30 minutes
```

### Key Principles

1. **Understand before writing** - Planning saves rewriting
2. **Update specific → general** - Prevents contradictions
3. **Read parallel, write sequential** - Maximize efficiency
4. **Verify cross-references** - Consistency is critical
5. **Use templates** - Speed up common updates

### When to Skip

Skip updating a file if:
- ✅ Change doesn't affect that audience
- ✅ File already describes generically
- ✅ Internal implementation only
- ❌ NEVER skip breaking changes
- ❌ NEVER skip user-facing changes

**Remember:** Good documentation tells a cohesive story. Every file should agree on the current reality.
