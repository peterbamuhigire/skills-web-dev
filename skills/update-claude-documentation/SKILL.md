---
name: update-project-documentation
description: "Use when you need to systematically update project documentation (README.md, PROJECT_BRIEF.md, TECH_STACK.md, ARCHITECTURE.md, docs/API.md, docs/DATABASE.md, CLAUDE.md, docs/plans/NEXT_FEATURES.md) after code changes, at end-of-session, or when closing for the day. Ensures all docs tell one cohesive story across audiences."
user-invocable: true
triggers:
  - update project documentation
  - update docs
  - close for the day
  - end of session docs
  - sync documentation
  - refresh project docs
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Update Claude Documentation

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Updating project documentation (README.md, PROJECT_BRIEF.md, TECH_STACK.md, ARCHITECTURE.md, docs/API.md, docs/DATABASE.md, CLAUDE.md, docs/plans/NEXT_FEATURES.md) after significant code or architecture changes
- Closing a work session and need to preserve context for the next session
- Adding, removing, or modifying features that affect multiple documentation files
- Restructuring project directories or changing development workflows

## Do Not Use When

- Making typo-only fixes (edit the file directly)
- Updating code comments (not documentation scope)
- Working on WIP features not yet merged to the main branch

## Required Inputs

- The type of change made (feature, architecture, tech stack, API, database)
- Which files or modules were affected
- Whether the change is breaking or non-breaking

## Workflow

1. Read this `SKILL.md`, then load only the `references/` files relevant to the current change type
2. Identify all affected documentation files using the Change-to-File mapping below
3. Read current state of all affected files before editing
4. Update files in specific-to-general order: technical specs first, then architecture, then user-facing docs
5. Verify cross-file consistency (terminology, versions, paths, component names)
6. Update `docs/plans/NEXT_FEATURES.md` — mandatory at every session end

## Quality Standards

- All markdown files must stay under the 500-line hard limit
- CLAUDE.md must stay under 10k characters as a navigation hub, not a content dump
- Keep outputs execution-oriented and concise
- Prefer deterministic, reviewable steps over vague advice

## Anti-Patterns

- Updating only one file when multiple files reference the same concept
- Using inconsistent terminology across files (pick one term and use it everywhere)
- Bloating CLAUDE.md with detailed guides that belong in `docs/` subdirectories
- Updating general docs before specific docs (always go specific-to-general)

## Outputs

- Updated documentation files that reflect the current state of the codebase
- End-of-session completion document at `docs/plans/YYYY-MM-DD-[feature-name]-completion.md`
- Updated `docs/plans/NEXT_FEATURES.md` with completed work and revised priorities

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Documentation update record | Markdown doc tracking changes made across all affected documentation files | `docs/updates/doc-update-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Update project documentation systematically after significant changes. Keep all files consistent and accurate.

**Core Principle:** Documentation tells one cohesive story. Each file serves a specific audience but must reflect the same reality.

**Deployment Context:** Project runs across Windows dev, Ubuntu staging, and Debian production (all MySQL 8.x). Documentation must reflect this 3-environment setup. When updating CLAUDE.md or TECH_STACK.md, always include the deployment environment table and cross-platform rules.

**Style Rule:** Be precise and concise. Do not add verbose or unnecessary text to any documentation file.

**Documentation Standards (MANDATORY):** ALL markdown files (.md) must follow strict formatting rules:
- **500-line hard limit** - no exceptions
- **Two-tier structure**: High-level TOC docs + Deep dive topic docs
- **Smart subdirectory grouping** for related documentation
- **See `doc-standards.md` for complete requirements**

**Modularize Instructions (Token Economy):** Avoid packing everything into a single CLAUDE.md. Prefer multiple focused docs (e.g., docs/setup.md, docs/api.md, docs/workflows.md) and reference them only when needed to reduce context bloat.

**CLAUDE.md as Navigation Hub (CRITICAL):** Keep CLAUDE.md under 10k characters as a quick-reference hub with links to detailed documentation. Move verbose sections (detailed workflows, extensive examples, module-specific guides) to appropriate `docs/` subdirectories. CLAUDE.md should provide essential patterns and pointers, not duplicate comprehensive content that exists elsewhere. This reduces AI context window usage by 80%+ and makes information easier to maintain.

**Docs Organization Rule (Required):** All documentation markdown now lives under `docs/` plus a semantic subdirectory (overview, architecture, pharmacy, localization, etc.). Do not add new files directly to the repo root—move existing root markdown into the appropriate `docs/<module>` folder before editing, then update `docs/agents/AGENTS.md` and always update `docs/plans/AGENTS.md` when plans are added or their status changes. The canonical landing doc is now `docs/overview/README.md`, and the root `README.md` should only point people into `docs/`.

**Claude-Ready Module Headers (Required):** Updating documentation now includes refreshing `CLAUDE.md` and the hero portion of each touched skill (`*/SKILL.md`). Claude relies on the YAML `name`/`description` pair and the opening markdown (hero title, quick summary, when-to-use bullets) for each skill, so keep that block aligned with the module-header template in `references/module-header-template.md`. The template spells out the claude-friendly structure with a checklist for ensuring the front-matter description triggers the right use cases and the leading sections stay concise yet informative.

## When to Use

✅ Adding/removing features
✅ Architecture or design pattern changes
✅ Dependency or tech stack updates
✅ API endpoints or database schema changes
✅ Project directory restructuring
✅ Development workflow changes
✅ **End of work session** - User says "update project documentation", "update docs", or "close for the day"

❌ Typo fixes (do directly)
❌ Code comments
❌ WIP features not yet merged

## End-of-Session Documentation (CRITICAL)

**When user says "update project documentation", "update docs", or "close for the day":**

**MANDATORY Steps:**

1. **Create completion document** - `docs/plans/YYYY-MM-DD-[feature-name]-completion.md`
   - Detailed technical report
   - All features and bug fixes
   - Code examples and patterns
   - Key learnings

2. **Update docs/plans/INDEX.md**
   - Move completed work to "Completed Plans"
   - Add completion date
   - Update status

3. **Update docs/plans/NEXT_FEATURES.md** (MANDATORY)
   - Mark completed features in "Recently Completed"
   - Update priority levels
   - Adjust effort estimates
   - Update recommended next steps

4. **Update MEMORY.md**
   - Critical patterns discovered
   - Common mistakes to avoid
   - API response structures
   - Key file references

5. **Create end-of-day summary** (Optional but recommended)
   - `docs/YYYY-MM-DD-END-OF-DAY-SUMMARY.md`
   - Quick reference for accomplishments
   - Next session priorities

**This workflow ensures:**
- Continuity between sessions
- Knowledge preservation
- Clear priorities for next session
- Reduced context loss

## Documentation Files

| File                       | Audience                | Purpose                     | Update Frequency      |
| -------------------------- | ----------------------- | --------------------------- | --------------------- |
| PROJECT_BRIEF.md           | Stakeholders, new devs  | 30-sec overview             | Major changes         |
| README.md                  | Developers              | Setup, usage guide          | Feature additions     |
| TECH_STACK.md              | Developers, DevOps      | Tech inventory              | Stack changes         |
| ARCHITECTURE.md            | Senior devs, architects | System design               | Architecture changes  |
| docs/API.md                | API consumers           | API reference               | API changes           |
| docs/DATABASE.md           | Backend devs, DBAs      | Schema docs                 | Schema changes        |
| CLAUDE.md                  | Claude Code             | Dev patterns                | Pattern changes       |
| docs/plans/NEXT_FEATURES.md| Team, Claude Code       | **Priority roadmap**        | **Every session**     |
| docs/plans/INDEX.md        | Team, Claude Code       | Plans index                 | Plan status changes   |
| MEMORY.md                  | Claude Code             | Session memory, learnings   | End of each session   |

## Change → File Mapping

**New Feature:**

- README.md (usage)
- docs/API.md (if adds endpoints)
- docs/DATABASE.md (if adds tables)
- ARCHITECTURE.md (if adds components)
- CLAUDE.md (if changes patterns)
- PROJECT_BRIEF.md (if significant)
- **docs/plans/NEXT_FEATURES.md (MANDATORY - mark as completed, update priorities)**
- docs/plans/INDEX.md (update status)
- MEMORY.md (capture key learnings)
- Each affected `*/SKILL.md` front-matter and hero section should follow the module-header template above so Claude sees the change immediately and can re-trigger the skill with the new context.

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
6. **Priority Roadmap (docs/plans/NEXT_FEATURES.md)** - MANDATORY every session

### 3. Read Current State (2-3 min)

Read all affected files in parallel.

### 3.a. Review Module Headers (1-2 min)

Open every impacted `*/SKILL.md` and verify the hero `name`/`description` plus the opening sections line up with the Claude-friendly template. Capture the new feature/behavior in the quick summary and `## When to Use` bullets before editing the downstream docs.

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

### 6. Update NEXT_FEATURES.md (MANDATORY - 5 min)

**CRITICAL:** This MUST be done at the end of every work session, even if no other docs changed.

**When user says "update project documentation" or "close for the day":**

1. **Mark completed work:**
   - Move completed features from "Active" to "Recently Completed"
   - Add completion date
   - Add brief summary of what was delivered

2. **Update priorities:**
   - Adjust priority levels based on new information
   - Add newly identified features
   - Remove obsolete features

3. **Update effort estimates:**
   - Revise estimates based on recent work velocity
   - Add new estimates for newly identified work

4. **Update recommended next steps:**
   - Reflect current project state
   - Consider dependencies and urgency
   - Update "Recommended Next Session Plan"

**Template structure:**
```markdown
## 🔴 CRITICAL PRIORITY
[Feature name] - Why critical, effort estimate, start point

## 🟠 HIGH PRIORITY
[Feature name] - Why high priority, effort estimate, start point

## 🟡 MEDIUM PRIORITY
[Feature name] - Why medium priority, effort estimate, start point

## ✅ Recently Completed
[Feature name] - Completion date, brief summary
```

**Location:** `docs/plans/NEXT_FEATURES.md`

### 7. Final Review (1 min)

- [ ] New dev can understand from README
- [ ] CLAUDE.md has context
- [ ] Breaking changes marked
- [ ] Examples work
- [ ] No contradictions
- [ ] **NEXT_FEATURES.md updated with session changes**

**Total:** 20-35 minutes (includes NEXT_FEATURES.md update)

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

❌ **Bloated CLAUDE.md with duplicate content**

```markdown
# BAD: 40k+ character CLAUDE.md with detailed implementation guides

# GOOD: 6k character CLAUDE.md hub linking to docs/coding/UI_DEVELOPMENT_GUIDE.md

# Result: 84% reduction in AI context usage, easier maintenance
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