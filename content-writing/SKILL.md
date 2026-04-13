---
name: content-writing
description: Copywriting and content creation standards for website pages, blog posts,
  and all written copy. Covers headlines, ledes, readability, niche vocabulary, scannable
  formatting, and persuasive structure. Cross-cutting skill — apply whenever...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Content Writing Skill

<!-- dual-compat-start -->
## Use When

- Copywriting and content creation standards for website pages, blog posts, and all written copy. Covers headlines, ledes, readability, niche vocabulary, scannable formatting, and persuasive structure. Cross-cutting skill — apply whenever...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `content-writing` or would be better handled by a more specific companion skill.
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
Professional copywriting standards for website copy, blog posts, articles, and all written content. This is a cross-cutting skill — apply these principles whenever creating or editing text for any page.

## The Reader-First Rule

Every word exists for the reader, not the writer. Before writing anything, answer:
- **Who** is the reader? What do they already know?
- **What** are they looking for? What problem brought them here?
- **Why** should they care? What benefit do they gain?

Write for the reader all the time. That is what separates content that converts from content that gets ignored.

---

## Headlines & Titles

The headline is the most important element. Five times as many people read the headline as read the body. If the headline fails, everything below it is wasted.

### Headline Rules

1. **Promise a benefit.** Headlines that promise benefits outperform those that don't.
2. **Give news.** Readers seek new information — new products, new methods, new insights.
3. **Select your reader.** Flag down the people you want. If writing for banana farmers, put "banana farmers" in the headline.
4. **Be specific.** "How to Increase Banana Yield by 40%" beats "Tips for Better Farming."
5. **Long headlines that say something outpull short headlines that say nothing.** Never sacrifice clarity for brevity.
6. **Write the headline AFTER the content.** Only then do you know the full scope and best angle.
7. **Telegraph in simple language.** Readers do not stop to decipher obscure headlines.

### Headline Formulas That Work

- **How to [achieve desired result]**: "How to Store Bananas for Maximum Shelf Life"
- **[Number] Ways/Reasons/Steps**: "7 Steps to Higher-Quality Matooke Flour"
- **Question that mirrors the reader's problem**: "Is Your Banana Crop Vulnerable to Fusarium Wilt?"
- **News/announcement**: "New Banana Cultivar Resists Black Sigatoka Disease"
- **Direct benefit**: "Reduce Post-Harvest Losses by Half with These Storage Methods"

### What to Avoid in Headlines

- Clever wordplay the reader won't get
- Headlines that could apply to any topic (too generic)
- ALL CAPS for entire headlines (harder to read)
- Clickbait that the content cannot deliver on

---

## Additional Guidance

Extended guidance for `content-writing` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `The Lede (Opening)`
- `Readability`
- `Niche Vocabulary (Thematic Depth)`
- `Scannable Formatting`
- `The "So What?" Test`
- `Attribution as Authority`
- `Unique Value Proposition`
- `Features vs Benefits`
- `Structure Templates`
- `Keeping Eyes Moving`
- `Writing Styles`
- `Takeaways`
- Additional deep-dive sections continue in the reference file.
