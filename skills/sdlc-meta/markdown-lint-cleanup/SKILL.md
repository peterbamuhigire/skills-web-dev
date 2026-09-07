---
name: markdown-lint-cleanup
description: Use when fixing Markdown lint failures, heading structure, list spacing, code-fence languages, or local formatting consistency without changing document meaning.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Markdown Lint Cleanup
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Fix markdown lint warnings by enforcing headings, blank lines around lists, and language-tagged code fences for clean documentation.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Markdown lint cleanup record | Markdown doc tracking lint warnings fixed (headings, blank lines around lists, language-tagged fences) per pass | `docs/lint/markdown-cleanup-2026-04-16.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Overview

Use this skill to clean markdown files so they pass lint checks with zero warnings. It focuses on consistent headings, spacing, and fenced code block language tags.

## When to Use

- Markdown lint warnings appear (MD022, MD032, MD036, MD040, MD031)
- Documentation updates need a clean lint pass
- Large docs need formatting normalization without content changes

## Core Rules (Required)

1. **Headings must be proper headings**
   - Replace bold-only headings with `##`, `###`, etc.
2. **Blank lines around lists**
   - Add a blank line before and after lists
3. **Blank lines around fenced code blocks**
   - Surround code fences with blank lines
4. **Language tags on fenced code blocks**
   - Use `bash`, `php`, `sql`, or `text` as appropriate

## Common Fixes

### MD036: Emphasis used instead of a heading

**Replace**:

**Section Title**

**With**:

## Section Title

### MD032: Blanks around lists

Ensure blank lines before and after lists:

Text paragraph.

- Item one
- Item two

Next paragraph.

### MD022: Blanks around headings

Add a blank line before and after headings:

Paragraph text.

#### Heading

- List item

### MD040: Fenced code language

Add a language identifier:

```text
Example output line
```

### MD031: Blanks around fences

Ensure fences are separated from other text:

Paragraph text.

```bash
php scripts/verify_uom_system.php
```

## File Safety

- Do not change meaning or content structure
- Only adjust formatting to satisfy lint rules
- Preserve links and references exactly

## Recommended Workflow

1. Identify lint warnings and their line numbers
2. Apply targeted fixes (headings, spacing, code fence languages)
3. Re-check lint until clean

## Output Expectations

- No markdown lint warnings
- No content meaning changes
- Consistent formatting across documents

## Decision Rules

| Condition | Action |
|---|---|
| Fix is mechanical and meaning-preserving | Apply narrowly |
| Rule conflicts with repository style | Follow repository configuration |
| Fix alters meaning | Stop and report separately |

## Capability Contract

Read and search are required. Editing and lint execution require authorisation.

## Degraded Mode

Fallback: without execution, return the patch and name the lint command still required.

## Domain Anti-Patterns

- Rewording prose during formatting cleanup.
- Renumbering headings without checking links.
- Guessing a code-fence language.
- Formatting vendored files unintentionally.
- Claiming a clean run without evidence.
## Inputs
| Artefact | Required? | Purpose |
|---|---|---|
| Markdown scope, lint rules, repository conventions, and protected content | yes | Bound safe cleanup |
## Outputs
- Produce cleaned Markdown, lint results, and a note of intentionally retained exceptions.
