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

## User Input

The user provides:

1. **Article title** (or topic idea)
2. **Brief summary** (2-5 sentences describing what the article should cover)
3. **Photos** uploaded to `photo-bank/` (at least 3: 1 featured/hero + 2 in-article)

From this simple prompt, generate the complete article pipeline below.

---

## Blog Content Directory: `docs/blogs/`

Every website project uses `docs/blogs/` as the standard blog content directory:

```
docs/blogs/
  topics.md              ← Topic index (generated by blog-idea-generator)
  {slug}.md              ← English article draft
  {slug}.fr.md           ← French article draft
  {slug}.sw.md           ← Kiswahili article draft (if enabled)
```

**Workflow:**
1. **Draft** — Articles are written and saved as markdown in `docs/blogs/{slug}.md` (EN) and `docs/blogs/{slug}.fr.md` (FR)
2. **Edit** — The user edits and refines the markdown files directly. Multiple rounds of revision happen here.
3. **Publish** — On instruction ("build this post", "publish this article"), create the Astro page from the markdown file at `src/pages/{lang}/blog/{slug}.astro`
4. **Update** — If the user edits the markdown file after publishing, rebuild the Astro page from the updated markdown on instruction.

The markdown files are the source of truth. Astro pages are generated from them, not the other way around.

---

## Article Content Pipeline

### Step 0: Read Idea Summary (if available)

If `docs/blogs/topics.md` exists and contains a summary for this article's topic:

1. Read the full 200-word hybrid summary for this topic
2. Extract and use as planning inputs:
   - **Audience** — target reader segment
   - **Buyer Stage** — awareness, consideration, or decision
   - **Format** — content format (how-to, case study, list, etc.) → read `blog-idea-generator/references/content-formats.md` for the structural template
   - **Angle** — the specific twist that differentiates this article
   - **Key Points** — section headings or core coverage areas
   - **CTA Goal** — what action the reader should take
   - **SEO Keywords** — primary and secondary targets
   - **Tier** — SEO driver, authority builder, or thought leadership
3. The idea summary is a starting point, not a straitjacket — adapt based on research in Step 1

If no idea summary exists, proceed directly to Step 1.

### Step 1: Research and Plan

1. Read the company profile to understand the author's expertise and experience. **Build a voice profile** (see `references/human-voice-standards.md` — Voice DNA Extraction): analyse the author's sentence patterns, vocabulary, opinions, register from their docs. Extract 5-10 characteristic sentences as tone anchors.
2. Identify the target audience segment for this article (see `references/content-strategy.md`)
3. Identify the reader types this article must serve: Scanner, Deep Diver, Sceptic, Action-Taker (see `references/reader-experience.md`)
4. Determine which buyer journey stage the article targets: Awareness, Consideration, or Decision
5. Identify 2-3 target SEO keywords from the topic (see Keyword Strategy below)
6. Choose the content organisation pattern (see `references/writing-craft.md`)
7. Choose an opening hook technique (question, startling fact, story, current event, bold assertion, poster child, scene-setter, significant detail, profile lead — see `references/writing-craft.md`)
8. Map the 5 touchpoints: pre-touch (title/meta), first touch (hero/opening), core touch (body), last touch (conclusion/CTA), in-touch (related articles/newsletter)
9. Produce an outline with 5-8 section headings (h2s)
10. Identify which stories from the author's experience to include (see `references/storytelling.md`)
11. Present the outline to the user for approval before writing

### Step 2: Process Article Photos

1. Scan `photo-bank/` for photos the user uploaded for this article
2. Measure dimensions of each photo
3. Copy to `src/assets/images/` following the photo-manager pipeline
4. Assign roles: **featured** (hero), **landscape** (in-article), **portrait** (in-article)
5. Update `_catalog.json` with article photo entries
6. Minimum: 1 featured + 1 landscape + 1 portrait = 3 photos. Maximum: 1 featured + 4 in-article = 5 photos.
7. If fewer than 3 photos are available, note what is needed and proceed with available images

### Step 3: Write English Article

Save to `docs/blogs/{slug}.md`:

```markdown
---
title: "Article Title in Title Case"
slug: "article-slug-here"
date: "YYYY-MM-DD"
author: "Author Name"
category: "Category Name"
description: "SEO meta description — under 155 characters, includes primary keyword and location."
keywords: ["primary keyword", "secondary keyword", "tertiary keyword"]
featured_image: "filename-of-hero-image.jpg"
images: ["landscape-image.jpg", "portrait-image.jpg"]
read_time: "X min read"
---

Article body here...
```

**Writing requirements** (detailed in `references/writing-craft.md`):

- **1,500-2,500 words** — detailed, rich, educational. Every word earns its place.
- **Opening hook** — first paragraph grabs attention. Never open with a definition or generic statement. Consider poster child, scene-setter, significant detail, or profile lead types (see `references/writing-craft.md`).
- **Nut 'graph** — if the opening uses a story or anecdote, follow it (paragraphs 2-4) with a grounding paragraph that states what the article is actually about. Without this, soft openings feel directionless.
- **Pain point formula** — demonstrate understanding of the reader's problem before offering solutions.
- **At least one story** from the author's real experience with specific details (places, outcomes, lessons).
- **Concrete language** — specific numbers, named places, real examples. No vague abstractions.
- **Active voice** — at least 90% of sentences. Passive voice only when the actor is unknown or unimportant.
- **Sentence variety** — average 15-20 words. Mix short (8-10) with medium (25-30). Never exceed 35.
- **One idea per paragraph** — 2-4 sentences each. Topic sentence leads.
- **Scannable** — clear h2 headings, bulleted lists where enumerable, bold for key terms.
- **Internal links** — link to relevant service, portfolio, about, and contact pages.
- **Image placement markers** — indicate where in-article images should appear: `[IMAGE: landscape-image.jpg — caption text]`
- **Full circle ending** — reconnect the conclusion to the opening. If you opened with a poster child, bring them back. If you opened with a scene, return to it transformed. Readers feel closure and reward.
- **CTA conclusion** — end with a clear, natural call to action (not a sales pitch).
- **Clarity** — use "because" not "since", "although" not "while", "can" for ability, "might" for possibility. No ambiguous words for multilingual readers.
- **Conciseness** — cut filler ("in order to" → "to", "due to the fact that" → "because"). Delete weak modifiers (really, very, quite, basically).
- **Linking flow** — every paragraph connects to the previous one with a logical bridge or transition word.

**Human voice requirements** (from `references/human-voice-standards.md`):

- **Zero AI vocabulary** — never use Tier 1 blacklist words (delve, tapestry, landscape, leverage, navigate, foster, realm, etc.). Check every sentence.
- **Zero AI phrases** — never open with "In today's...", "Have you ever wondered...", "It's important to note...". See full blacklist.
- **Burstiness mandatory** — every 500-word section must contain 3+ sentences under 8 words and 1+ sentence over 25 words.
- **Take positions** — at least 3 clear opinions per article. "I recommend" not "One might consider".
- **Client language** — mine vocabulary from docs/ files and use the client's own words.
- **Strategic contractions** — 2-4 per 500 words (don't, can't, it's). Never in headlines.
- **Sensory detail in stories** — what it looked like, felt like, sounded like. Not just what happened.
- **Write then cut** — draft 30% more than needed, then cut ruthlessly in revision.
- **Max 2 em dashes per article**. Vary paragraph lengths (1 sentence, then 4, then 2).

### Step 4: Write French Article

Save to `docs/blogs/{slug}.fr.md` with identical frontmatter structure.

**This is adaptation, not translation.** The French article must:

- Restructure paragraphs for natural French flow
- Use francophone African examples (Dakar, Abidjan, Douala) where English uses anglophone ones
- Feel like it was written in French first
- Use formal register throughout (vous, never tu)
- Follow West African francophone business conventions (see voice guides below)
- **1,800-3,000 words** — French naturally expands 20-30% from English
- Accents mandatory on every character (é, è, ê, ç, à, ù, ô, î)

### Quality Gate: Verify Against Idea Summary

If this article was generated from an idea summary (Step 0), verify alignment before proceeding to design:

- [ ] **Audience match** — article addresses the specified reader segment
- [ ] **Format compliance** — article follows the structural template for the specified format
- [ ] **Key points covered** — all key points from the summary are addressed in the article
- [ ] **Angle delivered** — the unique angle is evident, not generic
- [ ] **SEO keywords placed** — primary keyword in title, first 100 words, at least one h2, and conclusion
- [ ] **CTA goal achieved** — conclusion drives the specified action
- [ ] **Tier alignment** — Tier 1 articles prioritise SEO; Tier 2 prioritise depth; Tier 3 prioritise voice

If any check fails, revise the article before proceeding.

### Step 5: Design and Build Astro Pages

**Invoke the `frontend-design` plugin** for article page design.

1. Count existing articles to determine which layout variation to use (cycle through A, B, C, D)
2. Select colour accent based on article category/tone
3. Create `src/pages/en/blog/{slug}.astro` and `src/pages/fr/blog/{slug}.astro`
4. Include: Article JSON-LD schema, featured image, in-article images, author bio, CTA
5. Pass the featured image as the OG image: `<BaseLayout ... ogImage={heroImg.src}>` — each article must use its own featured image for Open Graph, not the default site OG image
6. Use `heroImg.src` in the JSON-LD `image` field: `"image": \`\${siteUrl}\${heroImg.src}\``
7. The featured image must be landscape orientation (wider than tall) for optimal OG display
8. Add prose styles to `global.css` if not already present

See `references/article-design.md` for layout variations, image treatment, and design variety system.

### Step 6: Update Blog Index

Update `src/pages/en/blog.astro` and `src/pages/fr/blog.astro`:

- Add the new article card with featured image thumbnail, title, category, date, read time, excerpt
- If this is the **first real article**: remove "Coming Soon" cards and remove `noindex` meta tag
- Keep the newsletter section
- Order articles newest-first

### Step 7: SEO Verification

Verify every SEO requirement (see full SEO checklist below):

- [ ] Title tag under 60 chars with primary keyword
- [ ] Meta description under 155 chars with primary keyword + location
- [ ] Article JSON-LD schema (headline, author, datePublished, publisher, description, image)
- [ ] Primary keyword in first 100 words, at least one h2, and conclusion
- [ ] Internal links to service/portfolio/contact pages
- [ ] Featured image has descriptive alt text with keyword
- [ ] Canonical URL correct
- [ ] Hreflang links between EN and FR versions

### Step 8: Build and Verify

Run `npm run build` and confirm:
- No build errors
- Article pages render correctly in both languages
- All images load and are optimised
- Blog index shows the new article

---

## English Voice

Write as the author would write for a business audience — the register of a senior professional writing a LinkedIn article or industry blog. Not academic, not casual.

**Read `references/storytelling.md`** for authentic human touch and cultural markers.

- **Simple and clear.** Short sentences. One idea per paragraph. No jargon without explanation.
- **British spelling.** organisation, programme, centre, colour, specialise.
- **Warm but professional.** Polite, measured, confident. Not stiff, not chatty.
- **First person where natural.** "In my experience" and "I have found" — the author has authority.
- **Practical focus.** Every article should leave the reader with something they can use.
- **Real examples.** Reference actual business contexts and projects from the company profile.

| Use | Avoid |
|-----|-------|
| practical, effective, significant | cutting-edge, game-changing, revolutionary |
| I have found that | It is widely acknowledged that |
| In our experience | Research conclusively demonstrates |
| This approach works because | This paradigm shift enables |
| I recommend | One might consider |
| This works | This can potentially |
| Two approaches matter | There are several approaches |

**Contraction calibration:** Use contractions sparingly for natural rhythm (don't, can't, it's — 2-4 per 500 words). Zero contractions sounds like AI or academia. Too many sounds casual.

**Commit, don't hedge:** Say what you think. "This is the best approach for SMEs" not "This could arguably be considered a viable approach." Readers trust writers who commit.

**Read `references/editorial-standards.md`** for punctuation, capitalisation, numbers, and grammar rules.

---

## French Voice

Write as a bilingual professional would for francophone African business readers — Dakar boardrooms and Abidjan tech meetups, not Parisian literary prose.

- **Formal but accessible.** Vous throughout. Professional register. Not stiff or bureaucratic.
- **Concrete vocabulary.** "entreprise" not "firme", "mettre en place" not "implémenter", "formation" not "enseignement".
- **No anglicisms where French words exist.** Say "logiciel" not "software", "numérique" not "digital", "réseau" not "network". Technical terms (ERP, API, SaaS) stay in English.
- **Accents mandatory.** Every é, è, ê, ç, à, ù must be correct. Gender agreement verified.

---

## SEO Requirements (Every Article)

### On-Page SEO Checklist

1. **Title tag** — `{Article Title} — {Author Name}` (under 60 chars). Must contain primary keyword. Don't write cute-only headlines — combine creative hook with search-practical keywords: "The Three-Hour Problem: Fixing Slow Reconciliation in Multi-Branch Retail". See `references/writing-craft.md` headline rules.
2. **Meta description** — under 155 chars. Must include primary keyword + geographic location.
3. **URL slug** — lowercase, hyphenated, keyword-rich: `/en/blog/erp-implementation-mistakes/`
4. **Heading hierarchy** — one h1 (article title), 4-7 h2s (main sections), h3s for subsections.
5. **Keyword placement:**
   - Primary keyword in the title (h1)
   - Primary keyword in the first 100 words
   - Primary keyword in at least one h2
   - Primary keyword in the conclusion
   - Secondary keywords distributed naturally through body text
   - **Never keyword-stuff.** Every instance must read naturally.
6. **Alt text** — every image has descriptive alt text. Include the primary keyword in the featured image alt.
7. **Internal links** — at least 3 per article: one to a service page, one to about/portfolio, one to contact.
8. **External links** — link to authoritative sources when citing facts or data (opens in new tab).

### Structured Data (Article JSON-LD)

Every article page must include:

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "url": "https://site.com/en/about/"
  },
  "datePublished": "2026-03-01",
  "dateModified": "2026-03-01",
  "publisher": {
    "@type": "Organization",
    "name": "Company Name",
    "url": "https://site.com"
  },
  "description": "Meta description",
  "image": "https://site.com/path/to/featured-image.jpg",
  "inLanguage": "en-GB",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://site.com/en/blog/article-slug/"
  }
}
```

### Technical SEO

- **Canonical URL** — automatic from BaseLayout
- **Hreflang** — links between all language versions (automatic from BaseLayout)
- **Open Graph** — title, description, featured image via `ogImage={heroImg.src}` prop on BaseLayout (each article uses its own featured image, not the default site OG image)
- **Sitemap** — remove `noindex` after first real article so blog pages are indexed
- **Page speed** — all images optimised via Astro `<Image>`, lazy loading on in-article images

### Keyword Research Per Article

Every article targets at least one keyword cluster. Research what the target audience searches for:

- Use the primary service terms from the company profile
- Append geographic modifiers (city, country, region)
- Prefer long-tail phrases (higher intent, less competition)
- Include the primary keyword and 2-3 secondary keywords naturally

---

## Article Quality Standards

| Element | Standard |
|---------|----------|
| Word count | 1,500-2,500 words (EN) / 1,800-3,000 words (FR) |
| Paragraphs | 2-4 sentences each, max 5. One idea per paragraph. |
| Headings | h2 for main sections (4-7 per article), h3 for subsections |
| Lists | Use where content is naturally enumerable (max 9 items per list) |
| Images | 1 featured + 2-4 in-article (at least 1 landscape + 1 portrait) |
| Stories | At least 1 concrete story from the author's experience |
| Internal links | At least 3 (service, about/portfolio, contact) |
| CTA | Natural call to action in the conclusion |
| Read time | Calculate at 200 words/min (EN) or 180 words/min (FR) |

---

## Publishing Checklist

### Quality Gates (from `references/reader-experience.md`)
- [ ] **8-Second Test** — title, hero image, and first paragraph make you want to keep reading
- [ ] **Scanner Test** — headings, bold text, and first sentence of each section convey the key points
- [ ] **So-What Test** — every major claim is followed by what the reader can do with it
- [ ] **Ambiguity Test** — no word could mean two things to a non-native English speaker
- [ ] **Touchpoint Test** — every transition feels natural and the conclusion has a clear "what's next"

### Content Quality
- [ ] Article is detailed, educating, and provides genuine value
- [ ] At least one authentic story with specific details (places, outcomes)
- [ ] Concrete language throughout — no vague abstractions
- [ ] Active voice in 90%+ of sentences
- [ ] Opening hook captures attention (not a definition or generic statement)
- [ ] Conclusion has a clear, natural CTA
- [ ] No filler phrases (in order to, due to the fact that, it is important to note)
- [ ] No weak modifiers (really, very, quite, basically, actually)
- [ ] Every paragraph connects to the previous one with a logical bridge

### Human Voice (from `references/human-voice-standards.md`)
- [ ] Zero Tier 1 AI blacklist words (delve, tapestry, landscape, leverage, realm, navigate, foster, etc.)
- [ ] Zero banned AI phrases ("In today's...", "It's important to note...", "Game-changer", etc.)
- [ ] Burstiness present — 3+ short sentences (<8 words) per 500-word section
- [ ] At least 3 clear opinions the author stands behind
- [ ] Paragraph lengths vary (1, 2, 3, 4 sentences — not all the same)
- [ ] Max 2 em dashes in the entire article
- [ ] No "Furthermore/Moreover/Additionally" as paragraph openers
- [ ] Stories contain at least one sensory or physical detail
- [ ] 2-4 contractions per 500 words (natural rhythm, not zero)

### Language
- [ ] English: British spelling, East African professional tone, warm but measured
- [ ] French: formal francophone African register, vous throughout, accents correct
- [ ] French article feels native — not a translation

### Images
- [ ] Featured image present, minimum 1200px wide, `loading="eager"`
- [ ] At least 2 in-article images (1 landscape + 1 portrait)
- [ ] All images have descriptive alt text
- [ ] All images use Astro `<Image>` component
- [ ] Images distributed through article body, not clustered

### Design
- [ ] Layout variation differs from the previous article
- [ ] Design matches article tone and website brand
- [ ] Mobile-responsive at 375px, 768px, 1280px
- [ ] Author bio section present
- [ ] `frontend-design` plugin used for design decisions

### SEO
- [ ] Title tag under 60 chars with primary keyword
- [ ] Meta description under 155 chars with keyword + location
- [ ] Primary keyword in first 100 words, one h2, and conclusion
- [ ] Article JSON-LD schema with all required fields including image (`heroImg.src`)
- [ ] OG image uses article's featured image via `ogImage={heroImg.src}` (not default site OG)
- [ ] Featured image is landscape orientation for optimal OG/social sharing display
- [ ] Internal links to at least 3 other pages
- [ ] Featured image alt text includes primary keyword
- [ ] Hreflang tags present

### Technical
- [ ] `npm run build` passes with no errors
- [ ] Blog index updated with new article card
- [ ] `noindex` removed from blog pages (if first real article)
- [ ] All images tracked in `_catalog.json`

## References

| File | When to Read |
|------|-------------|
| `references/writing-craft.md` | During outlining and writing — 7-step process, lead types (9 techniques), article arc (nut 'graph, full circle), sentence craft, headline SEO formula, clarity, conciseness |
| `references/content-strategy.md` | During planning — audience segments, buyer journey, SEO strategy, pillar content, touchpoints |
| `references/reader-experience.md` | During planning and review — touchpoint mapping, reader types, quality gates, tone calibration |
| `references/storytelling.md` | During writing — authentic stories, cultural markers, the human touch |
| `references/editorial-standards.md` | During proofing — punctuation, capitalisation, numbers, grammar, British spelling |
| `references/article-design.md` | During page building — layout variations, image placement, design variety |
| `references/ideation-and-research.md` | During planning — ideation techniques (clustering, spin, 9 value-adding angles, W5 discovery), research methods (2X rule, evidence types), competitor analysis framework, headline generation |
| `references/content-distribution.md` | After drafting — plan distribution across 9 channels (email, LinkedIn, Quora, communities, SlideShare, YouTube, guest posting); apply the 20/80 rule; build the repurposing plan for each article |
| `docs/blogs/topics.md` | When suggesting topics — curated list with keyword targets (project-specific, generated by blog-idea-generator skill) |

Cross-cutting skills that apply throughout:
- `language-standards` — language and tone standards for all languages
- `east-african-english` — detailed English voice guide (if present in project)
- `brand-alignment` — visual and messaging consistency with the overall website brand
- `seo` — multi-language SEO, hreflang, language-specific sitemaps (ensures articles are SEO-ready)
- `sales-copywriting` — headline formulas, fascination bullets, closing techniques (always active for all articles)

---

## Blog Index Page Structure

The blog index page (`/en/blog/`, `/fr/blog/`) is one of the most visited pages. Don't just show a grid of latest posts. Structure it for discovery:

1. **Blog focus statement** (1-2 sentences at the top) — tell readers what you blog about
2. **Featured posts row** — 2-3 hand-picked posts (most popular, posts with lead magnets)
3. **Newsletter signup** — prominently placed for visitors impressed by your content
4. **Topic categories** — list several post categories so readers can jump to topics of interest
5. **Latest posts grid** — chronological listing below the curated sections

### Heading Substance Test

After writing a blog post, scroll through reading only the section headings. If a reader could learn everything from the headings alone, the article lacks substance — you've written "X obvious things about Y" formatted beautifully but without depth.

**Fix:** Don't just repeat what everyone else says. Add your own perspective, look at the topic from an unexpected angle, add a twist in the headings while keeping them clear, inject personality and humour.

### Blog Taxonomy Rules

If the site has blog categories and tags:
- All categories should contain approximately equal numbers of posts
- If one category is twice as large as the rest, split it into two
- Do not assign too many categories or tags to a single post
- Remove tags or categories used only once or twice
- Show categories early on the page (near the top), not hidden at the bottom in small grey text
- Each category and tag page should have a title and short description
