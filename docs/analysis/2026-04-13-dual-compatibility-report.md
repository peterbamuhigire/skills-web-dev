# Dual Compatibility Report

Date: 2026-04-13

## Scope

Upgrade this repository into a dual-compatible skills system that works in both Claude Code and Codex without moving the skill directories or breaking existing Claude Code workflows.

## What Was Wrong

### Structural Gaps

- The repository already used portable `SKILL.md` files, but Codex had no root `AGENTS.md` describing how to route tasks across the catalog.
- Some top-level docs described the repository as Claude-only, which hid the portability that already existed in the folder layout.

### Skill Design Gaps

- Skills were inconsistent in structure. Many lacked an explicit `Use When`, `Do Not Use When`, `Required Inputs`, `Workflow`, `Outputs`, or `References` contract.
- A few skills had malformed frontmatter for validator purposes because they used unsupported keys such as `compatibility`.
- Several skills embedded optional platform assumptions as hard requirements instead of compatibility notes.

### Platform-Coupling Gaps

- Repeated `Required Plugins` sections treated the Superpowers plugin as mandatory, which is reasonable in some Claude Code workflows but blocks Codex from using the same skill cleanly.
- Some wording across the repository referred only to Claude Code even when the skill content itself was portable.

## What Was Improved

### Repository-Level Compatibility

- Added root `AGENTS.md` with repository purpose, baseline skills, routing rules, working model, and quality expectations for Codex.
- Updated `README.md`, `CLAUDE.md`, and `PROJECT_BRIEF.md` to describe the repository as a dual-compatible Claude Code and Codex skills catalog.

### Skill-Level Compatibility

- Standardized every `SKILL.md` with a portable execution contract:
  - `Use When`
  - `Do Not Use When`
  - `Required Inputs`
  - `Workflow`
  - `Quality Standards`
  - `Anti-Patterns`
  - `Outputs`
  - `References`
- Added portable metadata to every skill frontmatter:
  - `metadata.portable: true`
  - `metadata.compatible_with: [claude-code, codex]`
- Converted unsupported `compatibility` frontmatter keys into supported `metadata.compatibility_notes`.
- Replaced hard `Required Plugins` blockers with `Platform Notes` so optional helpers remain documented without preventing Codex execution.

### Maintenance Support

- Added `skill-writing/scripts/upgrade_dual_compat.py` to make the dual-compatibility normalization repeatable instead of a one-off manual rewrite.

## What Was Added

- Root `AGENTS.md`
- This compatibility report
- `skill-writing/scripts/upgrade_dual_compat.py`
- Portable execution sections injected into all skill entry points

## Why The Changes Matter

- Codex now has explicit repository routing and a uniform contract for every skill.
- Claude Code keeps the same flat repository layout and the same skill invocation style.
- The portable contract reduces ambiguity for both tools without duplicating the underlying skill logic.
- Optional platform features remain documented, but no longer block use on a different agent platform.
- Validator-safe frontmatter and consistent structure make future maintenance less fragile.

## Validation Summary

- Skills discovered: 193
- Skills with portable contract injected: 193
- Skills with plugin notes converted to platform notes: 58
- Validator result: all skills passed `python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>`
- Line-count guard: no `SKILL.md` exceeds 500 lines after the upgrade

## Residual Recommendations

- Gradually modernize older skill bodies that still contain tool- or project-specific assumptions, especially the longest legacy reference-heavy skills.
- Add nested `AGENTS.md` files only for genuinely complex subdomains, not preemptively.
- Continue moving oversized conceptual material into `references/` when a skill body starts to drift toward textbook format.
