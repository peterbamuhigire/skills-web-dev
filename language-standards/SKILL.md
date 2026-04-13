---
name: language-standards
description: Language and tone standards for all written content across 3 languages
  — English (British, East African), French (Francophone African), and Kiswahili (East
  African standard). Enforces authentic, culturally appropriate, professional communication...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Language Standards — Multi-Language Tone & Grammar

<!-- dual-compat-start -->
## Use When

- Language and tone standards for all written content across 3 languages — English (British, East African), French (Francophone African), and Kiswahili (East African standard). Enforces authentic, culturally appropriate, professional communication...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `language-standards` or would be better handled by a more specific companion skill.
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
