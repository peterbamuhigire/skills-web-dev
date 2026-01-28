---
name: manual-guide
description: "Generate end-user manuals and reference guides for ERP modules. Use when the user asks to document a feature, write a user manual, or sync a reference guide. This skill is explicitly separate from doc-architect (which manages AI guidance docs like AGENTS.md)."
---

# Manual Guide (End-User Documentation)

Create **end-user manuals** and **reference guides**. This is **not** for AI instruction documents. Do **not** edit or generate AGENTS.md or other AI guidance files when this skill is used.

## Trigger Phrases

Activate when the user asks to:

- "Document feature [X]"
- "Write manual for [Module]"
- "Sync reference guide"

## Contextual Discovery (Intelligence Phase)

Before writing a single word, analyze these four pillars:

1. **Plans**: Scan `docs/plans/**/*.md` to understand business intent and user stories.
2. **Schema**: Scan `database/schema/*.sql` to identify constraints, triggers, and auto-generated fields.
3. **Codebase**: Read implementation in `src/` or `app/` to see actual UI behavior and data flow.
4. **Documentation**: Check `docs/*` for style guides or technical debt notes.

## Output Structure (Dual-Workflow)

Every guide must include:

1. **Conceptual Overview**
   - Why the feature exists
   - How it works from a business perspective

2. **Procedural Steps**
   - Numbered steps for the happy path
   - Use bold for UI elements (**buttons**, **menus**, **fields**)

3. **Technical Reference**
   - Tables for auto-generated fields, required inputs, and background triggers

4. **Edge Cases**
   - Derived from schema constraints and validation rules

## Tone & Style

- Professional, instructional, literal-minded
- Use tables to compare workflows (e.g., POS vs Direct Sales)
- Avoid implementation details that are irrelevant to end users

## Manual Delivery Requirements (Required)

- Manuals must be created in `/manuals/` using subdirectories for major areas.
- Create a core page: `/public/user-manuals.php` based on the standard template (e.g., `skeleton.php`).
- The core page should dynamically include manual files, e.g. `user-manuals.php?manual=pos-system`.
- When asked to design a manual:
  1.  Check if `/public/user-manuals.php` exists.
  2.  Check if `/manuals/` exists and contains subdirectories.
  3.  If no folders exist, study the codebase and create **up to 10** top-level manual sections.
  4.  Create `/manuals/AGENTS.md` describing the directory purpose and what each subfolder should contain.
  5.  Create the manual PHP file for the requested module in its subfolder.

## Manual UI Expectations (Web)

- Make manuals **enjoyable** and **interactive**, not static help pages.
- Use a clean, high-contrast layout with subtle depth (glassmorphism-like panels).
- Provide a top progress indicator and section anchors.
- Provide a fast live search/omnibox (Cmd/Ctrl+K) with visual previews when feasible.
- Use highlighted UI callouts (dim rest of page on hover/focus of a term).
- Ensure mobile readability and fast load time.

## Manual PDF Expectations

- Produce a clean, print-ready manual for export.
- Support a dark-mode style variant where feasible.
- Use high-quality typography (sans for headings, monospace for field names).
- Include visual anchors (clean UI illustrations rather than heavy screenshots).
- Optional QR code links for video walkthroughs or live demos.

## Tool Permissions

- Allowed: `read_file`, `list_dir`, `grep_search`, `file_search`, `create_file`, `apply_patch`
- Use edits only for manuals and `/public/user-manuals.php` scaffolding

## Output Formatting

- Manuals should be created as PHP files in `/manuals/<section>/` and included dynamically by `user-manuals.php`
