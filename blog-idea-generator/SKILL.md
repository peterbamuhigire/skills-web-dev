---
name: blog-idea-generator
description: Generate 15-25 targeted blog post ideas with 200-word summaries for any client website. Reads website content, assesses available information, adaptively selects from 20 ideation methods, and conducts a guided interview. Each idea includes a narrative brief + structured specs. Use when the user says "generate blog ideas", "what should I blog about", "blog topic ideas", "content ideas", or wants to populate docs/blogs/topics.md.
---

# Blog Idea Generator

Generate 15-25 targeted blog post ideas, each presented as a 200-word hybrid summary with narrative brief + structured specs. The system adapts its ideation methods to the specific client and available information.

**Read `references/ideation-frameworks.md`** for the full 20-method library and selection logic.
**Read `references/content-formats.md`** for 20 content formats with structural templates.
**Read `sales-copywriting/references/headline-mastery.md`** for headline formulas and 4 U's scoring.

---

## Step 1: Gather Context

### Read client docs (mandatory)

Read every available file to build a complete picture:

1. `docs/en/company-profile.md` (and all enabled language versions)
2. `docs/en/services.md` — service offerings, target customers
3. `docs/en/pages.md` — existing website pages and content
4. `docs/sector-brief.md` — industry context (if present)
5. `docs/style-brief.md` — brand voice and tone
6. `docs/blogs/topics.md` — existing topics (avoid duplicates)
7. `src/pages/en/blog/` — existing articles (avoid overlap)
8. All other `docs/en/` files — testimonials, FAQ, portfolio, about-story

Extract and note:
- What the business does (core services, products)
- Who they serve (audience segments, industries, company sizes)
- Where they operate (geographic focus, markets)
- What makes them different (competitive advantage, methodology)
- What expertise the author has (experience, credentials, stories)
- What problems customers face (pain points, challenges)
- What content already exists (published articles, covered topics)

### Guided interview (3-5 questions)

After reading docs, ask targeted questions to fill gaps. Ask one at a time. Skip questions already answered by docs.

**Core questions (ask what's missing):**

1. **Audience specifics** — "Who is your ideal reader? (Job title, company size, industry, location)"
2. **Top pain points** — "What are the top 3 problems your customers face that your business solves?"
3. **Content goals** — "What should readers DO after reading? (Contact you, book a demo, understand a concept?)"
4. **Competitor landscape** — "Name 2-3 competitors. What topics do they cover?"
5. **Unique knowledge** — "What do you know that competitors don't? What's your unfair advantage?"
6. **Customer questions** — "What questions do customers ask most before buying?"
7. **Content gaps** — "Topics you've wanted to write about but haven't?"
8. **Context/audience** — any additional context the user provides (specific themes, campaigns, seasonal needs)

If the user provides additional context (audience details, campaign goals, seasonal focus), incorporate it into the assessment.

---

## Step 2: Assess Available Information

Score each dimension to determine which ideation methods will work best:

| Dimension | Rich (3) | Moderate (2) | Sparse (1) |
|-----------|----------|--------------|------------|
| **Client docs** | Detailed company-profile, services, testimonials, stories | Basic company-profile and services | Minimal — just a business name and description |
| **Competitor visibility** | Named competitors with active blogs | Competitors named but blogs unknown | No competitor info |
| **Audience specificity** | Named segments with pain points | General audience description | Vague ("businesses") |
| **Industry dynamism** | Active news cycle, regulations, trends | Moderate change rate | Stable/static industry |
| **Existing content** | 5+ published articles to spin off | 1-4 articles | No existing content |
| **Customer interaction** | Direct customer questions available | Some FAQ data | No customer feedback |

---

## Step 3: Select Ideation Methods

Based on the assessment, select 5-7 methods from the 20-method library. **Always include Methods 1 and 2** as foundation.

### Selection Matrix

| Method | Best When | Min Score |
|--------|-----------|-----------|
| 1. Category Drilldown | Always | — (always include) |
| 2. Buyer Awareness Stages | Always | — (always include) |
| 3. Pain Point Mining | Client docs ≥ 2 or customer interaction ≥ 2 | — |
| 4. Competitor Gap Analysis | Competitor visibility ≥ 2 | Competitor 2+ |
| 5. Customer Question Mapping | Customer interaction ≥ 2 | Customer 2+ |
| 6. They Ask, You Answer | Customer interaction = 3 | Customer 3 |
| 7. Amazon/Review Mining | Product-based business | Client docs 2+ |
| 8. Spin-Off Posts | Existing content ≥ 2 | Content 2+ |
| 9. Media Mashup | Brand voice is informal/creative | Client docs 2+ |
| 10. Highlight Good/Bad | Industry has notable examples | Industry 2+ |
| 11. How-To/Tutorial Mining | Product/service has teachable processes | Client docs 2+ |
| 12. Success/Failure Stories | Client has real project stories | Client docs 3 |
| 13. Holiday/Event Mapping | Content calendar needs seasonal hooks | Any |
| 14. Newsjacking/Trends | Industry dynamism = 3 | Industry 3 |
| 15. Use Any Object | Need creative/lateral ideas | Any (creative fallback) |
| 16. Curated Roundups | Industry has notable resources | Industry 2+ |
| 17. Prediction Posts | Industry dynamism ≥ 2 | Industry 2+ |
| 18. Jargon/Glossary | Technical niche with newcomer audience | Audience 2+ |
| 19. Contrarian/Negative | Audience is sophisticated | Audience 3 |
| 20. Topic-Category Matrix | Need high volume quickly | Any (volume fallback) |

Announce: "Based on available information, I'm using methods: [list]. Here's why: [brief rationale]."

---

## Step 4: Generate Ideas

Run selected methods sequentially. Aim for 25-35 raw ideas, then filter to the best 15-25.

For each method, consult `references/ideation-frameworks.md` for detailed instructions and examples.

### Quality Filters

Remove any idea that fails:

| Filter | Test |
|--------|------|
| **High-value goal** | Does this help the reader make/save money, reduce risk, save time, or gain advantage? |
| **Unique angle** | Does this require knowledge that isn't commonly available? |
| **So-what test** | Would the target reader care enough to click? |
| **Longevity** | Will this still be relevant in 12 months? |
| **No overlap** | Not already published or in existing docs/blogs/topics.md? |
| **Searchable** | Would someone type this into a search engine? |

### Tier Classification

| Tier | Purpose | Target Count |
|------|---------|-------------|
| **Tier 1: SEO drivers** | Attract organic traffic via long-tail keywords | 6-8 ideas |
| **Tier 2: Authority builders** | Establish expertise with deep guides and analysis | 5-7 ideas |
| **Tier 3: Thought leadership** | Build brand with opinions, predictions, stories | 4-5 ideas |

---

## Step 5: Create 200-Word Hybrid Summaries

For each approved idea, produce a summary in this exact format:

```markdown
### [Number]. [Working Title]

[3-4 sentence narrative brief: What this article is about, who it serves,
why it matters now, and the unique angle that makes it worth reading. This
paragraph should make someone want to write — and read — this article. It
captures the creative direction and emotional tone.]

- **Audience:** [specific reader segment — job title, industry, company size]
- **Buyer Stage:** [Awareness / Consideration / Decision]
- **Format:** [How-to / Case study / List / Opinion / Guide / Story / Comparison / Interview / Roundup / FAQ]
- **Angle:** [the specific twist that differentiates from competitors — 1 sentence]
- **Key Points:**
  1. [what the article must cover — specific enough to outline from]
  2. [second key point]
  3. [third key point]
  4. [fourth key point — optional]
  5. [fifth key point — optional]
- **CTA Goal:** [what action the reader should take after reading]
- **SEO Keywords:** [primary keyword], [secondary keyword]
- **Tier:** [1: SEO driver / 2: Authority builder / 3: Thought leadership]
- **Est. Words:** [1,500-2,500]
```

### Summary Quality Rules

- The narrative must read like a creative brief — not a dry description
- Key points must be specific enough to outline section headings from
- Keywords must be realistic long-tail phrases someone would search
- The angle must be genuinely different from what a Google search would surface
- Every title must pass the 4 U's test (see `sales-copywriting/references/headline-mastery.md`): Useful, Unique, Urgent, Ultra-specific — score 3+ on at least 3 dimensions

---

## Step 6: Present and Refine

### Present to the User

Show ideas grouped by tier with full summaries. After presenting, ask:
- Which ideas excite you most?
- Any ideas to remove or modify?
- Any topics you expected but don't see?
- Any specific campaigns or seasonal needs to address?

Refine based on feedback. The user's input overrides the assessment.

---

## Step 7: Save Output

Save the final approved list to `docs/blogs/topics.md`:

```markdown
# Blog Topic Ideas — [Client Name]

Generated: YYYY-MM-DD
Methods used: [list of methods applied]
Target audience: [summary]
Content categories: [list]

## Tier 1: SEO Drivers

### 1. [Title]
[Full 200-word hybrid summary as above]

## Tier 2: Authority Builders
...

## Tier 3: Thought Leadership
...

## Content Calendar Suggestion

| Month | Article 1 (Tier) | Article 2 (Tier) |
|-------|-------------------|-------------------|
| Month 1 | [title] (T1) | [title] (T2) |
...
```

If the file already exists, merge new ideas — don't overwrite existing topics. Mark previously written topics as `[PUBLISHED]`.

---

## Quality Checklist

Before finalising:

- [ ] At least 15 ideas across all 3 tiers
- [ ] Each idea has a complete 200-word hybrid summary
- [ ] No duplicate angles (each idea is distinct)
- [ ] At least 2 ideas per buyer awareness stage
- [ ] Ideas span at least 3 content categories
- [ ] Every title passes the 4 U's test (3+ dimensions at 3+)
- [ ] No overlap with existing published articles
- [ ] Mix of content formats (not all lists, not all how-tos)
- [ ] At least 3 ideas that showcase the author's unique expertise
- [ ] At least 2 ideas based on real customer questions (if data available)
- [ ] Content calendar covers at least 6 months at 2 articles/month
- [ ] All SEO keywords are realistic long-tail phrases
- [ ] Narrative briefs are compelling — they make you want to write the article

After writing, verify line count is under 500: wc -l blog-idea-generator/SKILL.md
