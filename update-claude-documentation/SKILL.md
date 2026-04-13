---
name: update-claude-documentation
description: Update project documentation files (README.md, PROJECT_BRIEF.md, TECH_STACK.md,
  ARCHITECTURE.md, docs/API.md, docs/DATABASE.md, CLAUDE.md, docs/plans/NEXT_FEATURES.md)
  when significant changes occur. MANDATORY at end of each work session to...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Claude Code: use Superpowers or similar helpers when they are available and materially useful.
- Codex: apply this skill normally; do not treat optional plugins as a prerequisite.

# Update Claude Documentation

<!-- dual-compat-start -->
## Use When

- Update project documentation files (README.md, PROJECT_BRIEF.md, TECH_STACK.md, ARCHITECTURE.md, docs/API.md, docs/DATABASE.md, CLAUDE.md, docs/plans/NEXT_FEATURES.md) when significant changes occur. MANDATORY at end of each work session to...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `update-claude-documentation` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

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
- **See `skills/doc-standards.md` for complete requirements**

**Modularize Instructions (Token Economy):** Avoid packing everything into a single CLAUDE.md. Prefer multiple focused docs (e.g., docs/setup.md, docs/api.md, docs/workflows.md) and reference them only when needed to reduce context bloat.

**CLAUDE.md as Navigation Hub (CRITICAL):** Keep CLAUDE.md under 10k characters as a quick-reference hub with links to detailed documentation. Move verbose sections (detailed workflows, extensive examples, module-specific guides) to appropriate `docs/` subdirectories. CLAUDE.md should provide essential patterns and pointers, not duplicate comprehensive content that exists elsewhere. This reduces AI context window usage by 80%+ and makes information easier to maintain.

**Docs Organization Rule (Required):** All documentation markdown now lives under `docs/` plus a semantic subdirectory (overview, architecture, pharmacy, localization, etc.). Do not add new files directly to the repo root—move existing root markdown into the appropriate `docs/<module>` folder before editing, then update `docs/agents/AGENTS.md` and always update `docs/plans/AGENTS.md` when plans are added or their status changes. The canonical landing doc is now `docs/overview/README.md`, and the root `README.md` should only point people into `docs/`.

**Claude-Ready Module Headers (Required):** Updating documentation now includes refreshing `CLAUDE.md` and the hero portion of each touched skill (`skills/*/SKILL.md`). Claude relies on the YAML `name`/`description` pair and the opening markdown (hero title, quick summary, when-to-use bullets) for each skill, so keep that block aligned with the module-header template in `references/module-header-template.md`. The template spells out the claude-friendly structure with a checklist for ensuring the front-matter description triggers the right use cases and the leading sections stay concise yet informative.

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
- Each affected `skills/*/SKILL.md` front-matter and hero section should follow the module-header template above so Claude sees the change immediately and can re-trigger the skill with the new context.

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

Open every impacted `skills/*/SKILL.md` and verify the hero `name`/`description` plus the opening sections line up with the Claude-friendly template. Capture the new feature/behavior in the quick summary and `## When to Use` bullets before editing the downstream docs.

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
