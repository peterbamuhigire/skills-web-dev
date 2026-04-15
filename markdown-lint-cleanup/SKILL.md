---
name: markdown-lint-cleanup
description: Fix markdown lint warnings by enforcing headings, blank lines around
  lists, and language-tagged code fences for clean documentation.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Markdown Lint Cleanup

<!-- dual-compat-start -->
## Use When

- Fix markdown lint warnings by enforcing headings, blank lines around lists, and language-tagged code fences for clean documentation.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `markdown-lint-cleanup` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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
