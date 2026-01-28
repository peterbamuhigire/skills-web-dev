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

## Tool Permissions

- Allowed: `read_file`, `list_dir`, `grep_search`, `file_search`
- Disallowed: any file editing tools (manuals are produced as output only)

## Output Formatting

- Provide the manual as a **clean, ready-to-copy Markdown block**
- Do not include tool names or internal file paths in the narrative
