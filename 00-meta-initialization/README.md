# Meta-Initialization: Methodology Selection & Project Setup

This skill is the **entry point** for the SDLC-Docs-Engine. Run this skill FIRST before generating any documentation.

## Purpose

Analyze your project, recommend the appropriate documentation methodology (Waterfall, Agile, or Hybrid), and generate a customized documentation roadmap.

## Quick Start

```bash
# Run this skill first
Run skill: 00-meta-initialization

# Follow the prompts to select methodology

# Review generated files:
# - projects/<ProjectName>/_context/methodology.md
# - projects/<ProjectName>/_context/doc_roadmap.md
# - projects/<ProjectName>/_context/project_profile.md

# Execute first skill in roadmap (shown in output)
```

## What This Skill Does

1. **Scans** your project directory for indicators (package.json, README.md, git history)
2. **Detects** project characteristics (regulated, startup, enterprise, etc.)
3. **Recommends** the best methodology (Waterfall, Agile, or Hybrid)
4. **Generates** a customized documentation roadmap
5. **Initializes** project context directory
6. **Shows** next steps to begin documentation

## Outputs

### Primary Outputs

- **`projects/<ProjectName>/_context/methodology.md`**: Selected methodology with rationale
- **`projects/<ProjectName>/_context/doc_roadmap.md`**: Documentation execution plan
- **`projects/<ProjectName>/_context/project_profile.md`**: Project characteristics summary

### Console Output

```
==================================================
SDLC-Docs-Engine: Methodology Selection
==================================================

Scanning project directory...
✓ Project type detected: PHP/Laravel
✓ Framework: Laravel 10.x
✓ Database: MySQL
✓ Version control: Git
✓ CI/CD: GitHub Actions

Analyzing project characteristics...
✓ Regulatory requirements: None detected
✓ Team size: Small (inferred from git contributors)
✓ Development pace: Moderate (8 commits/week average)
✓ Project maturity: Brownfield (existing codebase)

==================================================
RECOMMENDATION: Agile (Confidence: 78%)
==================================================

Reasons:
1. No regulatory constraints detected
2. Moderate development pace suggests iterative approach
3. Existing codebase benefits from incremental documentation
4. No fixed-scope contract indicators

Recommended Pipeline:
→ 01-strategic-vision/01-prd-generation (Lightweight PRD)
→ 02-requirements-engineering/agile/01-user-story-generation
→ 03-design-documentation/01-high-level-design (HLD only)
→ 07-agile-artifacts/01-sprint-planning

==================================================
Do you want to:
[1] Accept recommendation (Agile) ← Recommended
[2] Choose Waterfall instead
[3] Choose Hybrid approach
[4] Show detailed comparison
[5] Skip methodology selection

Your choice: _
```

## When to Use

✅ **USE when:**
- Starting documentation for a new project
- Migrating from v2.x to v3.0
- Switching methodologies mid-project
- Setting up documentation standards for a team

❌ **DO NOT USE when:**
- You've already run this and have `methodology.md`
- Just updating existing docs (use specific phase skills)

## Resources

- **[SKILL.md](SKILL.md)**: Complete skill documentation
- **[templates/methodology.md.template](templates/methodology.md.template)**: Methodology selection template
- **[templates/doc_roadmap.md.template](templates/doc_roadmap.md.template)**: Documentation roadmap template
- **[references/methodology-decision-tree.md](references/methodology-decision-tree.md)**: Detailed decision criteria

## Examples

See `templates/` for complete examples:
- Waterfall selection for medical device project
- Agile selection for startup MVP
- Hybrid selection for enterprise SaaS

---

**Last Updated:** 2026-02-07
