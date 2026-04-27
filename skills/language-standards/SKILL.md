---
name: language-standards
description: "Use when writing or reviewing user-facing content in English (British, East African), French (Francophone African), or Kiswahili (East African standard). Enforces culturally authentic, professionally courteous tone and correct grammar across all three languages. Covers spelling conventions, date/number formats, CTAs, courteous phrasing, and country-specific tone adjustments."
user-invocable: true
triggers:
  - language standards
  - tone review
  - multilingual copy
  - British English style
  - East African English
  - French copy review
  - Kiswahili content
  - content localization
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Language Standards — Multi-Language Tone & Grammar

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Writing or reviewing website copy, headings, CTAs, descriptions, or microcopy in English, French, or Kiswahili
- Auditing existing content for tone consistency and cultural appropriateness across supported languages
- Localising content for East African or Francophone African markets
- Ensuring British English spelling and formal East African professional tone in all English content

## Do Not Use When

- Writing purely internal technical documentation not seen by end users
- The content is in a language not covered here (English, French, Kiswahili only)
- Writing marketing copy that intentionally departs from formal tone (confirm with stakeholders first)

## Required Inputs

- Target language(s) for the content
- Content type (website copy, CTA buttons, notifications, email, documentation)
- Target audience context (country, formality level, domain)

## Workflow

1. Read this `SKILL.md` for core principles and English standards
2. Load `references/skill-deep-dive.md` for detailed rules on spelling, dates, country-specific tone, French, and Kiswahili
3. Apply the six core principles (clear, formal, no hype, professionally indirect, measured confidence, culturally authentic)
4. Review all content against the language-specific rules for the target language
5. Verify consistent verb tense within each section and consistent terminology across pages

## Quality Standards

- British English spelling throughout (colour, organisation, licence as noun)
- Simple present or past tense preferred over progressive forms
- Consistent verb tense within each section — no mixing past and present
- Courteous, formally indirect phrasing that respects East African communication norms
- No slang, exaggeration, or excessive marketing language

## Anti-Patterns

- Using American English spelling in a British English context
- Switching between formal and informal tone within the same page
- Direct imperative commands without courteous softening
- Machine-translating English copy into French or Kiswahili without cultural adaptation
- Ignoring country-specific tone differences (Uganda vs Kenya vs Tanzania)

## Outputs

- Reviewed or written content that meets the language standards for the target language
- Multilingual copy audit documenting tone, style, and grammar findings per page

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Multilingual copy audit | Markdown doc reviewing tone and style consistency across English, French, and other supported languages per page | `docs/content/multilingual-audit.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
All website copy, headings, CTAs, descriptions, and microcopy must follow this style guide for their respective language. Cross-cutting standard — applied throughout every content-writing step.

## Core Principles (All Languages)

1. **Clear and direct.** Sentences are straightforward, grammatically careful, logically structured.
2. **Formal and respectful.** Politeness is essential. Communication shows courtesy and humility.
3. **No excessive marketing language.** Avoid drama, exaggeration, slang.
4. **Professionally indirect.** Soften directives with courteous phrasing.
5. **Measured confidence.** Confident without arrogance.
6. **Culturally authentic.** Respect regional norms, preferences, sensitivities.

---

# ENGLISH (en) — British English, East African Professional Standard

## Core Characteristics

1. **British English spelling** throughout.
2. **East African tone** — formal, respectful, professionally courteous (Uganda, Kenya, Tanzania blend).
3. **Measured and confident** without arrogance or dramatic language.
4. **Logical sentence structure** — no fragments or telegram-style copy.
5. **Progressive tense preference** — use simple present or past over continuous tenses. "The company plans to expand" not "The company is planning to expand." Simple tenses are more direct and authoritative.
6. **Consistent verb tense** — do not switch tenses within a section. If you begin in present, stay present throughout that block. Mixing past and present within the same thought signals uncertainty.

## Additional Guidance

Extended guidance for `language-standards` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `British English Spelling`
- `Dates and Numbers`
- `Tone by East African Country Context`
- `Courteous Phrases (English)`
- `Vocabulary Standards (English)`
- `Redundant Phrases (All Languages)`
- `The "Because" Principle (All Languages)`
- `English CTAs and Button Text`
- `Core Characteristics`
- `French Spelling and Grammar`
- `French Dates and Numbers`
- `Formal Registers and Politeness`
- Additional deep-dive sections continue in the reference file.