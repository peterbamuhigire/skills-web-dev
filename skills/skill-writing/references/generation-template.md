# SKILL.md Generation Template

Use this when asking Claude to generate a complete SKILL.md from your requirements.

---

## Input Structure (What You Provide)

```
### Name
[What should this skill be called? Lowercase, hyphens only, max 64 chars]

### Purpose
[What problem does this skill solve?]

### Platform Target
[Claude Code only | Gemini CLI only | Both platforms (cross-platform)]

### When to Use
[List the triggers — when should the agent activate this skill?]

### Key Concepts/Patterns
[Core patterns, rules, or approaches that define this skill]

### Implementation Details
[Steps, configurations, important details]

### Code Examples (if applicable)
[Concrete code showing proper implementation]

### Common Mistakes
[What to avoid and why]

### Bundled Resources (if applicable)
[What files go in scripts/, references/, assets/ — and what each contains]

### Project Context
[Any context specific to your projects]
```

---

## Output Requirements (What You Ask Claude to Generate)

Generate a SKILL.md that:

**1. YAML Frontmatter**
- `name`: lowercase, hyphens only, matches directory name, max 64 chars
- `description`: ≤250 chars (Claude Code truncation limit). Front-load the key use case.
  Include: what it does + specific when-to-use triggers + keywords users naturally say
- For cross-platform: add `compatibility: Designed for Claude Code and Gemini CLI`
- For Claude Code-only features: add `disable-model-invocation`, `context`, etc. as needed
- Only include `license` if the skill has a license

**2. Body Structure**
- **Overview**: 2–3 sentences on core purpose
- **Core Instructions**: step-by-step implementation guidance
- **Key Patterns**: specific patterns and examples
- **Reference Files**: if you mention bundled files, state what goes where and when to read
- **Common Pitfalls**: what NOT to do

**3. Content Quality**
- Assume Claude is smart — only add non-obvious, domain-specific knowledge
- Use imperative language: "Use X", "Follow Y", "Implement Z"
- Under 500 lines — put detailed content in references/
- Code examples only where essential

**4. File References** (if bundled resources exist)
- For each file in scripts/, references/, assets/:
  - What it contains
  - When to use/read it

---

## Example Input

```
### Name
pdf-export

### Purpose
Standardised PDF export using mPDF 8.1.3 across all PHP SaaS projects.

### Platform Target
Both platforms (cross-platform)

### When to Use
- Implementing PDF export for invoices, receipts, reports, certificates
- Configuring PDF page layout and fonts
- Setting up print queue handling

### Key Concepts
- All PDFs use mPDF 8.1.3
- Standard layout: A4, 10mm margins, DejaVuSansMono
- Headers: company logo + date. Footers: page number + "Printed by {username}"
- All PDF classes extend BasePDFGenerator
- CMYK colour mode for production printing

### Common Mistakes
- Using RGB instead of CMYK
- Not embedding fonts
- Missing error handling for large documents

### Bundled Resources
- scripts/pdf_generator.php: BasePDFGenerator class
- references/mpdf_config.md: Exact mPDF configuration parameters
```

---

## Example Output (What Good Looks Like)

```yaml
---
name: pdf-export
description: Standardised mPDF 8.1.3 PDF export for PHP SaaS. Use when implementing
  invoices, receipts, reports, or certificates, or configuring PDF layout and print queues.
compatibility: Designed for Claude Code and Gemini CLI. Requires PHP 8+ and mPDF 8.1.3.
---

# PDF Export

Standard mPDF 8.1.3 configuration for all PHP SaaS PDF output.
All PDF classes extend `BasePDFGenerator` in `scripts/pdf_generator.php`.

## Standard Configuration

- Page: A4, 10mm margins, DejaVuSansMono font
- Colour mode: CMYK (not RGB)
- Headers: company logo + date
- Footers: page number + "Printed by {username}"
- Always embed fonts. Always enable compression.

## Creating a PDF

1. Extend `BasePDFGenerator` — read `scripts/pdf_generator.php` first
2. Call `initPDF()` before adding any content
3. Use CMYK colour values throughout
4. Log errors to `/var/log/pdf-errors.log`
5. For full config reference: see [references/mpdf_config.md](references/mpdf_config.md)

## Common Pitfalls

- Using RGB colours instead of CMYK — breaks production printing
- Not embedding fonts — PDF looks wrong on other machines
- Calling `initPDF()` after adding content — mPDF silently fails
```

---

## Validation Checklist Before Saving

- [ ] `name` is lowercase, hyphens only, matches directory name
- [ ] `description` is ≤250 chars and front-loads the key use case
- [ ] `compatibility` present if cross-platform or has dependencies
- [ ] Body is under 500 lines
- [ ] All referenced files (scripts/, references/) are explicitly listed with what they contain
- [ ] No secrets, credentials, or API keys
- [ ] Imperative language used throughout
- [ ] Frontmatter contains ONLY: name, description, license (if needed), compatibility (if needed), metadata (if needed), allowed-tools (if needed), plus Claude Code-specific fields only if Claude Code-only skill
