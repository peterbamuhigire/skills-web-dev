---
name: blog-writer
description: Generate SEO-optimised, bilingual blog articles with featured images,
  in-article photography, and distinctive per-article design. Articles are drafted
  and edited as markdown in docs/blogs/{slug}.md (EN) and docs/blogs/{slug}.fr.md
  (FR). On...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Blog Writer — Article Generation Skill
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Generate SEO-optimised, bilingual blog articles with featured images, in-article photography, and distinctive per-article design. Articles are drafted and edited as markdown in docs/blogs/{slug}.md (EN) and docs/blogs/{slug}.fr.md (FR). On...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `blog-writer` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Published blog post record | Markdown doc capturing each published post: title, slug, language(s), images, and metadata | `docs/content/blog-publish-log.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Generate detailed, rich, educating, and captivating blog articles with authentic human voice, professional photography, and full SEO optimisation. Each article is a marketing asset — a demonstration of expertise that builds trust and attracts clients through organic search.

**Use the `frontend-design` plugin** throughout article page creation for distinctive, high-quality design.

## Before Writing

Read these files first:

1. `docs/en/company-profile.md` (and all enabled language versions) — author background, services, expertise
2. `src/pages/en/blog.astro` — current blog index structure (check for existing articles)
3. `src/pages/fr/blog.astro` — French blog index (if FR enabled)
4. `src/layouts/BaseLayout.astro` — layout props, structured data, design system
5. `src/styles/global.css` — current styles (add prose styles if missing)
6. Existing articles in `src/pages/{lang}/blog/` — count them to determine layout variation
7. `photo-bank/` — scan for article photos the user has uploaded
8. `src/assets/images/_catalog.json` — current image catalog

Read the reference files as needed during writing:

- `references/human-voice-standards.md` — **READ FIRST** — AI vocabulary/phrase/structure blacklists, human voice techniques, self-check (ensures content sounds 100% human)
- `references/writing-craft.md` — 7-step process, sentence craft, paragraph structure, opening hooks, clarity, conciseness
- `references/content-strategy.md` — audience segments, buyer journey, SEO strategy, R.E.S.U.L.T.S. framework, blog creation checklist, 5-stage keyword mapping
- `seo/references/seo-content-writing.md` — keyword density rules, search intent types, featured snippets, voice search, on-page SEO checklist
- `sales-copywriting/references/headline-mastery.md` — Read for ALL blog headlines (10 formulas + 4 U's scoring)
- `sales-copywriting/references/resistance-and-objections.md` — Read for persuasive and opinion articles
- `references/reader-experience.md` — touchpoint mapping, reader types, quality gates, tone calibration, publishing rhythm
- `references/storytelling.md` — authentic stories, human touch, cultural markers
- `references/editorial-standards.md` — punctuation, capitalisation, numbers, grammar, British spelling
- `references/article-design.md` — image requirements, layout variations, design variety system
- `references/ideation-and-research.md` — ideation techniques, research methods, competitor analysis, headline generation
- `references/content-distribution.md` — Fishbein's 9 growth mechanisms, 20/80 create-vs-distribute rule, repurposing framework (1 post → 6 formats), 9 distribution tactics (email, LinkedIn, Quora, communities, SlideShare, YouTube, guest posting), SlideShare 50M+ visitor strategy, YouTube blog amplifier loop
- `docs/blogs/topics.md` — curated topic suggestions (project-specific, if present)
- `blog-idea-generator/references/content-formats.md` — 20 content formats with structural templates (How-to, Case study, List, Opinion, Guide, Story, Comparison, etc.)
- `sales-copywriting/references/fascination-bullets.md` — 21 bullet point templates for engaging list items and key takeaways
- `sales-copywriting/references/closing-and-guarantees.md` — closing templates for strong article conclusions and CTAs

---

## Additional Guidance

Extended guidance for `blog-writer` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `User Input`
- `Blog Content Directory: `docs/blogs/``
- `Article Content Pipeline`
- `English Voice`
- `French Voice`
- `SEO Requirements (Every Article)`
- `Article Quality Standards`
- `Publishing Checklist`
- `References`
- `Blog Index Page Structure`