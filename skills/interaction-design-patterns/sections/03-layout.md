# Layout Patterns

From Tidwell, *Designing Interfaces*, 3rd ed., Chapter 4: Layout of Screen Elements — and Chapter 5: Visual Style and Aesthetics.

> "A clean layout follows the principles of visual information hierarchy, visual flow, alignment through a grid, and adherence to Gestalt principles." — Tidwell.

---

## Visual Hierarchy — What Makes Things Look Important

Visual hierarchy gives users instant clues about importance and what to do next. Five tools create it:

| Tool | How to Use |
|------|-----------|
| **Size** | Larger = more important. Headlines bigger than body text. Primary CTA bigger than secondary. |
| **Position** | Top and left read first (F-pattern). Upper-right draws the eye after the primary focal point. Bottom = footer, least important. |
| **Density** | Tight grouping signals related content. Generous whitespace signals importance — isolation draws the eye. |
| **Background/Contrast** | A coloured background or high-contrast treatment draws attention. Same background for everything implies equal importance. |
| **Rhythm** | Consistent spacing between list items, cards, and grid elements creates an invisible reading metronome that reduces cognitive load. |

**The squint test:** Blur your eyes and look at the layout. Can you still perceive hierarchy? What reads first? What reads last? If everything is equally loud, nothing stands out.

---

## Layout Patterns

### Visual Framework
*"Give me stable landmarks so I always know where I am."*

The Visual Framework is the persistent structural skeleton of the application: header, sidebar, footer, and primary content area. It appears on every page unchanged.
- Header contains: logo, global navigation, search, user menu
- Sidebar contains: section navigation, relevant filters/tools
- Content area: changes on every page; gets the most space
- Footer: utility links, legal, secondary navigation
- The framework must be **visually stable** — users build their spatial memory of the app from it
- Sidebars: use the same background colour as the main content — separate with a border, not a contrasting colour. Different colours fragment visual space.

**Design rule:** Never move the navigation between pages. Users rely on spatial memory. Rearranging controls — even helpfully — forces re-learning.

---

### Center Stage
*"Give the most important content the most space."*

The content the user came to see should occupy the dominant visual area of the screen. Navigation, toolbars, and sidebars are supporting cast.
- Primary content area gets 60–75% of horizontal width on desktop
- Navigation never competes visually with the main content
- On mobile: full width, navigation collapses to bottom bar or hamburger
- The dominant element on every screen should be immediately obvious — one clear focal point

**Anti-pattern:** Navigation that is the same visual weight as the content. When the sidebar and content area look equally important, users don't know where to look first.

---

### Grid of Equals
*"Show me a collection of items of similar importance."*

When displaying a group of items with no hierarchy between them (products, team members, categories), a regular grid communicates equality.
- Cards in a grid should be visually identical in treatment: same border, same shadow depth, same padding scale
- Content *inside* cards can vary, but the container should be consistent
- Grid spacing: equal gutters horizontally and vertically
- Responsive: adapt column count (4 → 3 → 2 → 1) as screen width narrows
- Avoid mixing card sizes unless you're intentionally creating a featured-item hierarchy

**When to use:** Product listings, image galleries, team directories, category menus.
**When NOT to use:** Items with a clear priority ranking — use a list with visual emphasis on top items instead.

---

### Titled Sections
*"Help me understand the structure of this complex page."*

For pages with multiple distinct content groups, use clear section headers to label each group and help users scan to the section they need.
- Section header: larger, heavier weight, clearly distinct from body text
- Provide visual separation between sections: whitespace, divider line, or background colour change
- Sections should be scannable: users should be able to understand the page's structure by reading only the section headers
- Maximum 5–6 titled sections on a single scroll — more than that, consider splitting into tabs or pages

---

### Module Tabs
*"Show me different views of the same content."*

Tabs allow users to switch between related views without leaving the page context. Use for: different aspects of the same record (Details / History / Notes), or different content sets in the same container.
- Only 3–7 tabs per group — more than that, use a dropdown or sidebar navigation
- Active tab is clearly distinguished (filled, underlined, or colour-contrasted)
- Tab content loads immediately on click — no page reload
- The URL should reflect the active tab (deep links)
- Tabs work horizontally for short labels; use a sidebar list for long labels or many tabs
- Do NOT use tabs when the user needs to compare content across tabs simultaneously

---

### Accordion
*"Let me expand just the section I need."*

Accordions show a list of section headers; clicking a header expands it to reveal its content, optionally collapsing the previously open section.
- Best for: FAQ pages, settings pages with many categories, mobile navigation
- Keep headers short and scannable — they function as a table of contents
- Show a visual indicator (chevron, +/−) that communicates the expand/collapse action
- Allow multiple sections open simultaneously unless there's a strong reason to restrict to one
- Do NOT use for multi-step forms — accordions have known usability issues with wizard-style flows

**Anti-pattern:** An accordion where all sections start open and collapse. Defeats the purpose — users don't see the collapsed state as the default.

---

### Collapsible Panels
*"Let me hide this content when I don't need it."*

Similar to accordions but typically used for optional or secondary content panels on complex screens — filter panels, detail panels, configuration panels.
- Provide a clear toggle: "Show filters" / "Hide filters"
- Remember the user's preference (collapsed/expanded) between sessions
- Collapsed state should not break the page layout — other content fills the space gracefully
- On mobile: collapsible panels help manage limited screen real estate

---

### Movable Panels
*"Let me arrange my workspace the way I work."*

Some applications benefit from letting users customise panel positions — dashboards, data analysis tools, IDEs.
- Only implement where user customisation genuinely adds value — don't add complexity for its own sake
- Provide a sensible, well-designed default layout for new users
- Persist the user's arrangement between sessions
- Provide a "Reset to default" option
- On mobile: movable panels are not practical — use fixed layouts

---

## Visual Design Principles (Tidwell Chapter 5)

### Visual Credibility
The Stanford Web Credibility Project (2002) found that **visual design appearance is the #1 factor users use to judge website credibility** — above company reputation, content quality, or customer service. Users do not trust interfaces that look amateurish.

**Design rule:** Professional visual quality is not optional. An interface that looks unfinished undermines user trust regardless of functionality.

---

### Color Rules

**Warm vs Cool:** Red/orange/yellow/brown = warm. Blue/green/purple/grey = cool. Match colour temperature to the product's emotional intent.

**Dark vs Light backgrounds:** Light is standard and readable. Dark feels edgier — use with clear intent, not as a default.

**High vs Low contrast:** High contrast = strength, boldness, tension. Low contrast = calm, relaxed. Use contrast levels deliberately.

**Saturated vs Muted:** Pure/vivid colours draw attention but tire the eye when overused. Use one or two saturated accent colours; muted tones for everything else.

**Complementary colour pairs to avoid as text/background combinations:** Blue on red, red on green — they vibrate and fatigue the eye.

**Colour blindness:** 10% of men, 1% of women have some form of colour vision deficiency. Never use colour as the *only* signal — always pair with shape, icon, or text.

---

### Typography Rules

- Body text line height = font-size × 1.6 (e.g., 16px text → 26px line-height)
- Never pure black (#000000) on white — use #1A1A1A or #333333
- Maximum 3 font sizes per page section — more creates noise
- Sentence case for all UI labels — fastest to read, never shouts
- Sans-serif for interface labels, sans-serif or serif for content depending on the product's character
- Build a 4-level text hierarchy: primary, secondary, tertiary, muted — use all four consistently

---

### Visual Styles Reference

| Style | Character | Use When |
|-------|-----------|----------|
| **Skeuomorphic** | Mimics real-world objects (leather, paper, wood) | When users need help mapping digital to physical concepts |
| **Illustrated** | Custom illustrations, distinctive personality | Consumer apps, onboarding, brand-forward products |
| **Flat Design** | No shadows/gradients, bright solid colours | Clean, modern, fast-loading interfaces |
| **Minimalistic** | Extreme whitespace, near-invisible structural elements | Focus-intensive tools, reading apps, premium positioning |
| **Adaptive/Parametric** | System-generated, responds to data or context | Data-heavy applications, AI-driven interfaces |

**Design rule:** Choose a style and commit to it across every element. Mixed visual styles — some flat, some skeuomorphic — signal design incoherence and erode credibility.
