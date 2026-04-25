## Best Practices

**DO:**
✅ Clone seeder-page.php
✅ Use SweetAlert2
✅ Bootstrap Icons only
✅ Escape HTML
✅ Fetch API
✅ CSRF tokens
✅ Cache-bust shared JS updates with `?v=YYYYMMDD`
✅ Trace data shape end-to-end when debugging `not a function`

**DON'T:**
❌ Native alert/confirm
❌ Mix icon sets
❌ Create from scratch
❌ Inline handlers
❌ Skip auth checks

✅ Auto-trigger `window.print()` in `*-print.php` views so the dialog appears as soon as the DOM is ready, keeping `no-print` controls only for reprints.

## Frontend Design Standards

This skill guides the construction of distinctive, production-grade frontend interfaces that avoid generic “AI slop” aesthetics. Implement real working code with exceptional attention to detail and creative choices. When the user provides frontend requirements—be it a component, page, application, or interface—treat the ask as a chance to craft something unforgettable rather than a safe, templated layout. Refer to the complete terms in LICENSE.txt when invoking this aesthetic directive.

When the request is for dashboards, admin panels, SaaS apps, tools, settings pages, or data interfaces, follow the Interface Design workflow in [skills/webapp-gui-design/sections/09-interface-design.md](skills/webapp-gui-design/sections/09-interface-design.md) before proposing a direction or writing UI code.

## Executive UI Mode (C-Suite)

When the UI is for executives or owners, enforce these rules:

- Dashboard-first: show 4-6 KPIs at the top, then approvals, then reports.
- At-a-glance: large numbers, short labels, one-line trend context.
- Minimalism: remove secondary controls by default; hide advanced filters behind a toggle.
- Actionability: pair insights with clear next actions (Approve, Decline, Contact).
- Speed: prioritize first paint and cached summaries over deep tables.
- Device-agnostic: identical workflows across desktop and mobile.
- Readability: high contrast, large base font, plain language labels.
- Dark mode: offer optional dark mode for extended viewing.
- Brand control: use the product primary color for key highlights only.

**Dynapharm brand note:** primary color is deep red. Use it sparingly for primary actions and critical highlights, never for large background fills.

### Design Thinking

Before coding, understand the context and commit to a bold aesthetic direction:

- **Purpose:** What problem does this interface solve? Who uses it?
- **Tone:** Pick an extreme (brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc.). Use those flavors for inspiration and design something true to the chosen aesthetic.
- **Constraints:** Technical requirements such as framework, performance, or accessibility.
- **Differentiation:** What makes this unforgettable? What is the single thing someone will remember?

**CRITICAL:** Choose a clear conceptual direction and execute it with precision. Both bold maximalism and refined minimalism work—the key is intentionality, not intensity. Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is production-grade, visually striking, cohesive, and meticulously refined.

### Frontend Aesthetics Guidelines

Focus on:

- **Typography:** Choose beautiful, unique, and expressive fonts. Avoid generic families (Arial, Inter, Roboto, system stacks); opt for distinctive pairings where a characterful display font meets a refined body font.
- **Color & Theme:** Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents create more impact than timid, evenly-distributed palettes.
- **Motion:** Deliver animations for high-impact moments (staggered reveals, hero transitions, hover surprises). Favor CSS-only solutions for static HTML and use Motion libraries for React when appropriate. Staggered delays and scroll-triggered reveals beat scattershot micro-interactions.
- **Spatial Composition:** Exploit asymmetry, overlap, diagonal flow, generous negative space, or controlled density. Break the grid when it reinforces the concept.
- **Backgrounds & Visual Details:** Build atmosphere with gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, or grain overlays.

NEVER ship generic AI-generated aesthetics: avoid overused fonts (Inter, Roboto, Arial, system), cliché palettes (especially purple-on-white gradients), predictable layouts, and cookie-cutter component patterns. Every design should feel tailored to its context.

Interpret creatively, pick unexpected choices, and rotate through light/dark themes, different fonts, and varied aesthetics. DON’T repeat the same set of design decisions across outputs (e.g., no repeated Space Grotesk + monochrome combos).

**IMPORTANT:** Match the implementation complexity to the aesthetic vision. Maximalist concepts demand elaborate code (animations, layered effects); minimalist ideas require restraint, pixel-perfect spacing, and subtle refinements. Claude can deliver extraordinary creative work—commit fully to a distinctive vision.

## Visual Design Fundamentals

Grounded in Paduraru (2024) *Roots of UI/UX Design* and Panzarella (2022) *UI/UX Web Design Simply Explained.*

### The 8pt Spacing System

All element dimensions and spacing values must be multiples of 8: 8, 16, 24, 32, 40, 48px. Most screen sizes are divisible by 8. This creates inherent consistency and speeds up developer implementation.

For text baseline grid: use 4px increments.

### 60-30-10 Colour Rule

Professional colour proportion for any interface:
- **60%** — dominant neutral (background, surfaces)
- **30%** — secondary colour (cards, sidebars, secondary actions)
- **10%** — accent/primary (CTAs, highlights, primary actions)

More than 10% accent colour on a page overwhelms the design and the accent loses its ability to direct attention.

### Typography Rules

- **Never pure black (#000000)** on white: causes eye strain and overstimulates the retina. Use `#1A1A1A` or `#333333`.
- **Never pure white (#FFFFFF)** on pure black: causes "halation" — letters appear to bleed/glow, especially for users with astigmatism. Use `#F5F5F5` on `#1A1A1A`.
- **Body text line height** = font-size × 1.6. At 16px: 26px line height.
- **Sans-serif is the default** for UI. Serif for editorial/content contexts only.
- **Maximum 3 font sizes per section** — more creates noise and destroys hierarchy.
- **Sentence case throughout** — fastest to read in English. UPPERCASE is harder to read and reads as shouting.

### Dual-Layer Shadows

A single drop shadow is flat and artificial. Professional shadows use two layers:
1. **Core shadow** — narrow, dark, close to the object (the contact shadow)
2. **Cast shadow** — wider, lighter, behind the object (the ambient shadow)

Shadow size is proportional to object size. In dark mode: NEVER use white shadows — they create stark, tiring contrast. Use a darker shade of the element's colour with a lighter tint from the background.

### Button States (All 6 Required)

Every button variant must have all six states designed:
1. **Default** — interactive, enabled
2. **Hover** — visual feedback on cursor entry
3. **Active/Pressed** — visible confirmation of click
4. **Progress** — action is processing (spinner/loading)
5. **Focus** — keyboard navigation highlight
6. **Disabled** — non-interactive, visually distinct (never just grey opacity)

Designing only the default state is incomplete.

### Hero Sections

Always reveal a portion of the next section below the fold. Never cover the entire viewport with a hero. A full-bleed hero with no visible content below kills curiosity and scroll intent.

---

## Dominance, Rhythm, and Proximity

### Dominance

Every layout must have one clearly dominant element — the first thing the eye notices. Without it, users have no indication of where to start and get overwhelmed.

Three tools to create dominance:
- **Size** — larger elements are noticed first
- **Contrast** — a small element with strong contrast dominates over larger low-contrast elements
- **Negative space** — surrounding any element with generous whitespace places it centre-stage

### Rhythm (Spacing Consistency)

When the interval between elements is always the same, the brain learns the rule and moves through the page on autopilot. Consistent spacing between list items, cards, and grid elements creates an invisible reading metronome. Rhythm dramatically reduces reading fatigue.

### Proximity as Grouping

Elements close together are perceived as belonging together. Use proximity to:
- Create card groupings without borders
- Signal that a label belongs to its input field
- Separate navigation levels (primary vs secondary)

---

## Mental Model Alignment

**The implementation model vs the mental model (Cooper):**

The most common design error is building interfaces that follow how the technology works rather than how the user thinks. The user has no interest in how the system works — they want to reach their goal in the simplest way possible.

Always ask: "How would my user *think* about this?" Design the interface to match that mental model, not the database structure or API response shape.

Examples:
- Group event dates as "Today / This Week / This Weekend" — not by timestamp
- Treat airport name and city name as interchangeable (JFK = New York)
- Pre-select "round trip" and "economy" for flight searches — most users choose these

---

## Common Mistakes

❌ `alert('Success!');` → ✅ `Swal.fire('Success!', '', 'success');`
❌ `<div>${data.name}</div>` → ✅ `<div>${escapeHtml(data.name)}</div>`
❌ `<i class="fa fa-plus">` → ✅ `<i class="bi bi-plus">`
❌ Assuming arrays from APIs → ✅ `Array.isArray(x) ? x : x.key || []`

## Checklist

- [ ] Cloned seeder-page.php
- [ ] Auth check
- [ ] Includes loaded
- [ ] Bootstrap Icons only
- [ ] SweetAlert2 for dialogs
- [ ] DataTables configured
- [ ] Fetch API
- [ ] HTML escaped
- [ ] Responsive
- [ ] CSRF tokens
- [ ] **Dropdowns tested in browser** (not empty, search works, console clean)
- [ ] **Console logging added** for dynamic dropdowns (✅ success, ❌ errors)
- [ ] **Error handling** implemented (graceful failures, user-friendly messages)

## Summary

**Principles:**

1. Clone seeder-page.php
2. Tabler/Bootstrap 5
3. SweetAlert2, DataTables, Flatpickr
4. Modular includes
5. Mobile-first

**Stack:**
Tabler, Bootstrap Icons, SweetAlert2, DataTables, Flatpickr, Select2

**Remember:** Professional UIs = Consistent patterns + Commercial templates.
