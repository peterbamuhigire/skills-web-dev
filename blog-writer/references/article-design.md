# Article Design Reference — Blog Writer Skill

Every blog article must be visually distinctive, match the tone of its content, and feel like a natural extension of the website's brand. Use the **frontend-design plugin** throughout article page creation for high-quality design decisions.

---

## Image Requirements

### Featured Image (Required)
Every article has a featured/hero image displayed at the top, like a WordPress featured image.

- **Source:** User uploads article photos to `photo-bank/` before writing
- **Processing:** Copy to `src/assets/images/` using the photo-manager pipeline. Measure dimensions.
- **Minimum size:** 1200px wide for landscape, 800px wide for portrait
- **Display:** Full-width or contained within the article max-width, with rounded corners or edge-to-edge depending on article style
- **Alt text:** Descriptive, relevant to article content
- **Loading:** `loading="eager"` (above the fold)

### In-Article Images (2-4 Required)
Every article must include at least 2 images within the body, and may include up to 4:

| Requirement | Specification |
|-------------|--------------|
| Minimum count | 2 images |
| Maximum count | 4 images |
| Orientation mix | At least 1 landscape AND at least 1 portrait |
| Placement | Distributed through the article body, not clustered |
| Sizing | Landscape: full-width or 2/3 width. Portrait: 1/2 width with text wrap or centred. |
| Captions | Optional but recommended — adds context and accessibility |
| Loading | `loading="lazy"` for all in-article images |
| Alt text | Required on every image |

### Image Placement Rules
- **First in-article image** should appear after the first major section (after the first h2)
- **Second image** should appear roughly midway through the article
- **Additional images** (if 3-4) should be evenly distributed
- **Never place two images back-to-back** without text between them
- **Landscape images** work well as full-width section breaks
- **Portrait images** work well floated alongside text or centred with a caption

### Photo Selection Guidance
When selecting from available photos in `photo-bank/`:
- Choose images that relate to the article topic
- Mix photo types: contextual shots, Peter working, technology in use, African business settings
- Prefer photos showing real people and real environments over stock-looking images
- If insufficient photos exist, note what is needed in `_catalog.json` placeholders_needed

---

## Design Variety System

**No two articles should look exactly the same.** Achieve variety through these dimensions while staying within the website's design system:

### Layout Variations

Choose one layout style per article. Cycle through them:

**Style A — Full-Width Hero**
- Hero image spans full viewport width, edge-to-edge
- Title overlaid on the image with dark gradient overlay
- Author and date below the image
- Article body in a centred max-width column

**Style B — Contained Hero**
- Hero image contained within the content max-width
- Rounded corners (rounded-2xl)
- Title above or below the image
- Byline with author avatar alongside

**Style C — Split Hero**
- Two-column layout: image on one side, title/meta on the other
- Reverses on mobile (image on top, text below)
- Creates a magazine-style opening

**Style D — Minimal Hero**
- No large hero image at the top
- Category badge and title as the primary visual
- Featured image appears as the first in-article image instead
- Clean, text-forward design

### Colour Accent Variations
Each article can use a subtle colour accent drawn from the design system palette:

- **Navy accent** — for technology and technical topics
- **Gold accent** — for business strategy and leadership topics
- **Warm accent** — for personal stories and cultural topics
- **Neutral accent** — for how-to guides and practical topics

Apply the accent to: category badge, blockquote borders, pull quotes, and heading underlines.

### Typography Variations
While body text stays consistent (the website's body font), vary:

- **Pull quote styling** — large italic text, left-aligned with a vertical rule vs centred with quotation marks
- **Heading decoration** — some articles use an underline accent on h2, others use a side border
- **Dropcap** — optional large first letter on the opening paragraph (use sparingly, perhaps every 3rd article)

### Image Treatment Variations
- **Rounded corners** vs **sharp edges**
- **Full-width bleed** vs **contained with shadow**
- **With caption** vs **without caption**
- **Float left/right** vs **centred block**

---

## Article Page Components

### Required Components Per Article Page

1. **Article Hero** — featured image + title + category + read time + author + date
2. **Article Body** — the content with h2/h3 headings, paragraphs, lists, blockquotes, images
3. **Author Bio** — brief about-the-author section at the end (pulls from company-profile.md)
4. **Related Articles** — links to other articles if they exist (skip if this is the first article)
5. **CTA Section** — the standard CTASection component matching the rest of the website
6. **Share Links** — optional social sharing links (LinkedIn, Twitter/X)

### Reading Experience Enhancements

- **Estimated read time** — calculate from word count (average 200 words/minute for English, 180 for French)
- **Progress bar** — optional subtle reading progress indicator at the top of the page
- **Back to blog** — navigation link back to the blog index at the top and bottom
- **Smooth scroll** — heading anchor links for navigation within the article
- **Table of contents** — optional for articles with 5+ h2 sections, displayed as a sidebar on desktop or collapsible on mobile

---

## Matching Article Design to Content Tone

The article's visual treatment should reinforce its content tone:

| Article Tone | Design Choices |
|-------------|---------------|
| **Technical / How-to** | Clean, structured. Numbered steps. Code blocks if relevant. Contained hero. Minimal decoration. |
| **Strategic / Business** | Confident, spacious. Pull quotes. Gold accents. Full-width hero with professional imagery. |
| **Personal / Story-driven** | Warm, intimate. Portrait photos. Dropcap opening. Soft rounded corners. Closer line spacing. |
| **Opinion / Thought Leadership** | Bold, distinctive. Split hero. Strong heading typography. Emphasis on blockquotes. |
| **Practical / Guide** | Clear, scannable. Table of contents. Many h2s. Lists and tables. Contained hero. |

---

## Brand Consistency Rules

While varying the design between articles, these elements must remain **identical across all articles**:

- **Body font and size** — same as the rest of the website
- **Max content width** — consistent with the website's content column (max-w-3xl)
- **CTA Section** — same component, same messaging
- **Footer** — same as every other page
- **Header/Navigation** — same as every other page
- **Colour palette** — only use colours defined in the design system
- **Spacing rhythm** — section padding matches the rest of the website
- **Mobile behaviour** — same responsive patterns

---

## Blog Index Card Design

When updating the blog index page with a new article:

### Card Structure
- Featured image (as card thumbnail, cropped to consistent aspect ratio)
- Category badge
- Article title (linked)
- Meta description or first ~100 characters of the article
- Date and read time
- "Read More" or equivalent CTA

### Card Grid
- Desktop: 2 columns
- Mobile: 1 column, stacked
- Cards should have consistent height within each row (use `aspect-ratio` on images)
- Hover effect: subtle shadow lift or image zoom

### Index Page Progression
- First article: remove "Coming Soon" cards and `noindex` meta tag
- 2-3 articles: show all in chronological order (newest first)
- 4+ articles: consider adding category filters
- 6+ articles: add pagination or "Load More" button

---

## Astro Image Component Usage

Always use Astro's `<Image>` component for optimised delivery:

```astro
import { Image } from 'astro:assets';
import heroImg from '@/assets/images/article-hero.jpg';

<Image
  src={heroImg}
  alt="Descriptive alt text"
  width={1200}
  height={675}
  loading="eager"
  class="rounded-2xl w-full"
/>
```

- Hero images: `loading="eager"`, explicit width/height
- In-article images: `loading="lazy"`, explicit width/height
- All images: descriptive `alt` text, appropriate CSS classes
- Astro automatically generates WebP/AVIF formats and responsive srcsets
