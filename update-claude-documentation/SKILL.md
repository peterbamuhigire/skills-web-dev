---
name: update-claude-documentation
description: "Update project documentation files (README.md, PROJECT_BRIEF.md, TECH_STACK.md, ARCHITECTURE.md, docs/API.md, docs/DATABASE.md, CLAUDE.md) when significant changes occur. Use for feature additions, architecture changes, dependency updates, API/database modifications. Ensures consistency across all docs."
---

# Update Claude Documentation

Update project documentation systematically after significant changes. Keep all files consistent and accurate.

**Core Principle:** Documentation tells one cohesive story. Each file serves a specific audience but must reflect the same reality.

## When to Use

✅ Adding/removing features
✅ Architecture or design pattern changes
✅ Dependency or tech stack updates
✅ API endpoints or database schema changes
✅ Project directory restructuring
✅ Development workflow changes

❌ Typo fixes (do directly)
❌ Code comments
❌ WIP features not yet merged

## Documentation Files

| File | Audience | Purpose |
|------|----------|---------|
| PROJECT_BRIEF.md | Stakeholders, new devs | 30-sec overview |
| README.md | Developers | Setup, usage guide |
| TECH_STACK.md | Developers, DevOps | Tech inventory |
| ARCHITECTURE.md | Senior devs, architects | System design |
| docs/API.md | API consumers | API reference |
| docs/DATABASE.md | Backend devs, DBAs | Schema docs |
| CLAUDE.md | Claude Code | Dev patterns |

## Change → File Mapping

**New Feature:**
- README.md (usage)
- docs/API.md (if adds endpoints)
- docs/DATABASE.md (if adds tables)
- ARCHITECTURE.md (if adds components)
- CLAUDE.md (if changes patterns)
- PROJECT_BRIEF.md (if significant)

**Tech Stack Change:**
- TECH_STACK.md (always)
- README.md (setup instructions)
- ARCHITECTURE.md (if affects design)
- CLAUDE.md (if affects workflows)

**Architecture Change:**
- ARCHITECTURE.md (always)
- README.md (overview section)
- CLAUDE.md (patterns)
- PROJECT_BRIEF.md (if major)

**API/Database Change:**
- docs/API.md or docs/DATABASE.md (always)
- ARCHITECTURE.md (if changes contracts)
- CLAUDE.md (if affects patterns)
- README.md (if affects usage)

## Update Workflow

### 1. Understand Change (2-5 min)

Document:
- Type: Feature/Architecture/Tech Stack/API/Database
- What: One sentence description
- Impact: Who/what affected
- Breaking: Yes/No (what breaks)

### 2. Map to Files (1-2 min)

Order: Specific → General
1. Technical Specs (API.md, DATABASE.md)
2. Architecture (ARCHITECTURE.md, TECH_STACK.md)
3. AI Instructions (CLAUDE.md)
4. User Guides (README.md)
5. Overview (PROJECT_BRIEF.md)

### 3. Read Current State (2-3 min)

Read all affected files in parallel.

### 4. Update Systematically (10-20 min)

**Per-file checklist:**
- [ ] Update primary section
- [ ] Update related sections
- [ ] Update examples/code snippets
- [ ] Add migration notes if breaking

### 5. Verify Consistency (2-3 min)

Check across all files:
- [ ] Terminology consistent
- [ ] Version numbers match
- [ ] File paths consistent
- [ ] Component names consistent
- [ ] Features described consistently

### 6. Final Review (1 min)

- [ ] New dev can understand from README
- [ ] CLAUDE.md has context
- [ ] Breaking changes marked
- [ ] Examples work
- [ ] No contradictions

**Total:** 15-30 minutes

## Common Mistakes

❌ **Updating only one file**
```markdown
# Updated README but forgot CLAUDE.md
# Result: AI doesn't know new pattern
```

❌ **Inconsistent terminology**
```markdown
# README.md: "Authentication Service"
# ARCHITECTURE.md: "Auth Module"
# CLAUDE.md: "Login System"
# Pick ONE term everywhere
```

❌ **Forgetting breaking changes**
```markdown
# Renamed API endpoint but README examples still use old path
# Add migration notes EVERYWHERE affected
```

❌ **General → Specific order**
```markdown
# BAD: Update BRIEF first, then API.md
# GOOD: Update API.md first (precise), then BRIEF (summary)
```

## Quick Reference

**Update Order:**
```
API/DB Specs → Architecture → CLAUDE → README → BRIEF
```

**Consistency Checks:**
```
Terminology, Versions, Paths, Names, Features
```

**Time Budget:**
```
Small change: 5-10 min
Medium change: 15-30 min
Major refactor: 45-60 min
```

## Summary

**Process:** Understand → Map → Read → Update → Verify → Review

**Key Rules:**
1. Update specific docs first, general last
2. Read all affected files before editing
3. Keep terminology consistent
4. Mark breaking changes everywhere
5. Test examples before committing
6. One reality, multiple perspectives

**Remember:** Documentation debt compounds fast. Update immediately when making changes.
