---
name: content-writing
description: Use when writing or reviewing website copy, articles, headlines, ledes, persuasive content, readability, or scannable structure.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Content Writing Skill
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.


## Required Inputs

| Input | Required | Use |
|---|---|---|
| Decision, audience, and deliverable | yes | Bound the business outcome |
| Source evidence, constraints, and owner | yes | Ground recommendations and accountability |
| Approved budget, customer data, or production artefacts | conditional | Support high-impact execution |

## Capability and permission contract

Default to read-only analysis and drafting. Do not publish, send, price, promise, alter customer records, commit budget, or modify production artefacts without explicit authority and a named approver. Minimise confidential data, preserve provenance, and keep reversible copies.

## Degraded mode

If evidence, stakeholder decisions, specialist tooling, or authoritative commercial data are unavailable, deliver a labelled draft, checklist, or decision memo. State what was not verified and do not claim approval, publication, financial accuracy, or customer acceptance.

## Decision rules

| Condition | Action | Stop condition |
|---|---|---|
| Output creates a commercial, customer, or delivery commitment | Obtain named approval before release | Authority or terms are unclear |
| Evidence supports a reversible draft | Produce it with assumptions and owner | Required evidence conflicts |
| Tooling or data is incomplete | Specify validation | A final executable artefact is expected |

## Domain Anti-Patterns

- Inventing customer evidence, prices, benchmarks, or approvals. Fix: cite the source or mark the gap.
- Publishing or sending a draft without authority. Fix: retain draft status and name the approver.
- Hiding assumptions inside polished prose. Fix: expose them beside each affected decision.
- Polishing presentation while the decision remains unclear. Fix: resolve audience, owner, and acceptance criteria.
- Treating unavailable tooling as passed validation. Fix: record the unassessed check.


<!-- dual-compat-start -->
## Use When

- Copywriting and content creation standards for website pages, blog posts, and all written copy. Covers headlines, ledes, readability, niche vocabulary, scannable formatting, and persuasive structure. Cross-cutting skill — apply whenever...

## Workflow

- For premium products, websites, proposals, or sales assets, write content that proves authority, qualifies buyers, supports SEO/GEO and digital PR, explains value in business terms, and leads to a concrete next action.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Page copy review | Markdown doc covering headline, lede, body, and CTA per page against the content-writing standard | `docs/content/page-copy-review-checkout.md` |

## References

- [English output standard](../../../docs/continuous-improvement/english-output-standard-2026-09-02.md) for collocation, register, precise vocabulary, idiom restraint, and anti-slop revision.

- Use the `references/` directory for deep detail after reading the core workflow below.
- Pair with `premium-software-product-execution` when copy must support premium pricing, buyer trust, service packaging, sales follow-up, or website-as-marketing-asset requirements.
<!-- dual-compat-end -->
Professional copywriting standards for website copy, blog posts, articles, and all written content. This is a cross-cutting skill — apply these principles whenever creating or editing text for any page.

## The Reader-First Rule

Every word exists for the reader, not the writer. Before writing anything, answer:
- **Who** is the reader? What do they already know?
- **What** are they looking for? What problem brought them here?
- **Why** should they care? What benefit do they gain?
- **What proof** would make them believe us?
- **What action** should a qualified buyer take next?

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

## Quality Standards

Copy must be accurate, audience-specific, readable aloud, supported by named proof, and free of claims the source material cannot substantiate.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Reader-ready copy or copy review | Page owner, editor, or campaign team | The headline names a credible benefit, the body supplies proof, and the CTA states the next action without inventing claims |
