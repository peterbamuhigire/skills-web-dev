# Markdown Portability Reference

This reference contains the formatting appendix moved out of [../doc-standards.md](../doc-standards.md). Use it when a skill or project document needs explicit GitHub/Pandoc portability rules.

## Markdown Formatting Conventions (Portability Rules)

These rules ensure SKILL.md files render identically on GitHub and when processed by Pandoc into `.docx`. Violations can silently corrupt output documents. *(Source: The Markdown Guide, Matt Cone, 2023)*

### Rule 4: Heading Spacing

Always put a **blank line before and after every heading**, and a **space between `#` and the heading text**. Without the blank line, Pandoc may attach the heading to the preceding paragraph.

```markdown
<!-- CORRECT -->

## Section Name

Content starts here.

<!-- WRONG — may corrupt Pandoc output -->
## Section Name
Content starts here.
```

### Rule 5: List Delimiter — Always Use `-`

Use `-` (dash) for all unordered lists. Do **not** mix `-`, `*`, and `+` within the same document. Do **not** use emoji characters (✅, ❌) as list markers — they are not valid Markdown list elements and will render as plain text in Pandoc output.

```markdown
<!-- CORRECT -->
- Item one
- Item two

<!-- WRONG -->
* Item one
✅ Item two
```

### Rule 6: Inline Styles — Three-Way Convention

Use the three-way inline style convention consistently throughout all documentation:

| Purpose | Style | Syntax | Example |
|---------|-------|--------|---------|
| UI elements, field names, button labels | **Bold** | `**...**` | Click **Save** |
| First use of a term, emphasis | *Italic* | `*...*` | *Shall* means mandatory |
| File paths, commands, code, identifiers | `Monospace` | `` `...` `` | Run `build-doc.sh` |

Never use underscores for bold or italic (`__bold__`, `_italic_`) — underscores inside technical terms (e.g., `_context_`) cause parse ambiguity.

### Rule 7: Code Block Language Tags

Always specify the language on fenced code blocks:

```markdown
<!-- CORRECT -->
```bash
mkdir -p projects/MyProject/_context
```

```yaml
name: my-skill
version: 1.0.0
```

<!-- WRONG — renders as unstyled monospace, loses syntax context for AI -->
```
mkdir -p projects/MyProject/_context
```
```

Supported language tags: `bash`, `python`, `yaml`, `json`, `markdown`, `mermaid`, `sql`, `php`, `javascript`.

### Rule 8: Horizontal Rule Blank Lines

Always put a blank line **before and after** a `---` horizontal rule. Without the preceding blank line, Pandoc interprets the text above as a setext-style heading:

```markdown
<!-- CORRECT -->

---

## Next Section

<!-- WRONG — "Previous content" becomes a heading -->
Previous content
---
## Next Section
```

### Rule 9: Blockquotes for Guardrails and Standards Citations

Use `>` blockquotes for: anti-hallucination guards, critical warnings, IEEE/ISO citations that must stand out from instruction text. Use plain bold text only for in-line emphasis within prose.

```markdown
<!-- CORRECT — critical guardrail stands out, is parseable by AI -->
> **CRITICAL:** Do not fabricate requirements. Flag all gaps with `[CONTEXT-GAP]`.

<!-- WRONG — buried in prose, easy to miss -->
**CRITICAL:** Do not fabricate requirements. Flag all gaps with `[CONTEXT-GAP]`.
```

### Rule 10: Verification Checklists — Use Task List Syntax

Use `- [ ]` / `- [x]` task list syntax for all verification checklists so they render as interactive checkboxes on GitHub and Pandoc outputs:

```markdown
<!-- CORRECT -->
- [ ] All `_context/` files are populated (no bare `TODO` placeholders)
- [ ] Output file exists in the correct directory
- [x] Manifest.md updated

<!-- WRONG — renders as plain bullets, not checkboxes -->
- All `_context/` files are populated
- Output file exists
```

**Last Updated:** 2026-03-15
**Status:** MANDATORY - Strictly Enforced
