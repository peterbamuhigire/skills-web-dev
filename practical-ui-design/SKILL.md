---
name: practical-ui-design
description: Rules-based visual UI design system covering colour (HSB palettes, light/dark
  mode), typography (type scales, line height), layout (spacing tokens, 12-column
  grid), copywriting, buttons, and forms. Load alongside any platform skill...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Practical UI Design Skill

<!-- dual-compat-start -->
## Use When

- Rules-based visual UI design system covering colour (HSB palettes, light/dark mode), typography (type scales, line height), layout (spacing tokens, 12-column grid), copywriting, buttons, and forms. Load alongside any platform skill...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `practical-ui-design` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Plugins (Load Alongside)

| Companion Skill | When to Load |
|---|---|
| `webapp-gui-design` | Web app dashboards, admin panels, SaaS UIs |
| `jetpack-compose-ui` | Android native (Kotlin/Compose) |
| `form-ux-design` | Deep form patterns (this skill covers quick reference only) |
| `healthcare-ui-design` | Clinical-grade interfaces with strict accessibility |
| `pos-sales-ui-design` | Point-of-sale and retail entry screens |
| `ux-psychology` | Cognitive science foundations behind these rules |
| `laws-of-ux` | Named-law quick reference (Fitts, Hick, Miller, etc.) |
| `ai-slop-prevention` | Quality gate to catch generic AI-generated UI patterns |
| `motion-design` | Animation timing, easing, and micro-interaction standards |
| `ux-writing` | Microcopy standards for buttons, errors, empty states |
| `responsive-design` | Mobile-first, container queries, pointer detection |
| `frontend-performance` | Core Web Vitals, image and rendering optimisation |
| `design-audit` | Comprehensive UI quality audit with severity ratings |

**Usage:** This skill provides the *visual system* (colour, type, spacing, components). Platform skills provide *implementation code*. Load both.

---

## 1. Colour System (HSB-Based)

### 1.1 Why HSB, Not RGB/HEX

Use HSB (Hue 0-360, Saturation 0-100, Brightness 0-100) for all design decisions. HSB maps to how humans perceive colour: pick a hue, adjust richness with saturation, adjust lightness with brightness. Convert to HEX/RGB only at implementation time.

### 1.2 OKLCH Alternative

For perceptually uniform colour manipulation, consider **OKLCH** (`oklch(L C H)`) instead of HSB. OKLCH ensures equal perceived brightness across hues (unlike HSB where blue looks darker than yellow at the same B value). Use OKLCH for generating palettes, ensuring consistent visual weight. Convert final values to HEX/RGB for implementation. **Tint all neutrals** — add 2-5% of brand hue to greys; never use pure grey.

### 1.3 Start with Black and White

Design the interface without colour first. Focus on spacing, size, layout, and contrast. Colour is added last, purposefully.

- **Avoid pure black** (#000000) -- high contrast against white causes eye strain. Use a dark grey with a tinge of brand hue instead.
- **Avoid pure white text on dark** -- same eye strain problem in reverse.

### 1.3 One Brand Colour

Choose a single distinctive brand colour. Apply it **only to interactive elements** (buttons, text links, active states). Do not apply brand colour to headings or non-interactive elements -- users will mistake them for links.

- If brand colour has a strong existing meaning (e.g. red = error), use the darkest palette variation for interactive elements, or switch interactive colour to blue.
- If brand colour is too light (e.g. yellow): use darkest variation for button text and links; add a border to buttons for 3:1 contrast.

### 1.4 Monochromatic Palette (1 Hue + 5 Variations)

All you need: **1 brand colour + 5 tonal variations** sharing the same hue.

#### Light Palette (example hue 230)

| Token | HSB | Purpose | Contrast Req. |
|---|---|---|---|
| **Primary** | 230, 70, 80 | Buttons, links, interactive | >= 4.5:1 vs Lightest |
| **Darkest** | 230, 60, 20 | Heading text | >= 4.5:1 vs Lightest |
| **Dark** | 230, 30, 45 | Secondary/body text | >= 4.5:1 vs Lightest |
| **Medium** | 230, 20, 66 | Non-decorative borders, icons | >= 3:1 vs Lightest |
| **Light** | 230, 10, 95 | Decorative borders, dividers | Decorative -- no req. |
| **Lightest** | 230, 2, 98 | Alternate backgrounds | Base surface |
| **White** | 0, 0, 100 | Main background | Base surface |

#### Dark Palette (example hue 166)

| Token | HSB | Purpose | Contrast Req. |
|---|---|---|---|
| **Primary** | 166, 50, 90 | Buttons, links, interactive | >= 4.5:1 vs Dark |
| **White** | 0, 0, 100 | Heading text | >= 4.5:1 vs Dark |
| **Lightest** | 166, 4, 80 | Secondary/body text | >= 4.5:1 vs Dark |
| **Light** | 166, 6, 65 | Non-decorative borders | >= 3:1 vs Dark |
| **Medium** | 166, 8, 33 | Decorative borders | Decorative -- no req. |
| **Dark** | 166, 10, 23 | Alternate backgrounds | Base surface |
| **Darkest** | 166, 12, 15 | Main background | Base surface |

### 1.5 System Colours

| Colour | Meaning | Usage |
|---|---|---|
| **Red** | Error | Negative messages, failures, urgent alerts |
| **Amber** | Warning | Caution, risky actions |
| **Green** | Success | Positive messages, completed actions |
| **Blue** | Info | Neutral informational messages |

- System colour text: >= 4.5:1 contrast. Icons/components only: >= 3:1.
- Always pair system colour with an icon -- never rely on colour alone (colour-blind users).

### 1.6 Contrast Rules (WCAG 2.1 AA)

| Element | Min. Ratio |
|---|---|
| Small text (<= 18px regular, <= 14px bold) | **4.5:1** |
| Large text (> 18px bold or > 24px regular) | **3:1** |
| UI components (fields, radios, checkboxes) | **3:1** |
| Decorative-only elements | No requirement |

**APCA (WCAG 3 draft):** 90 preferred body, 75 minimum body, 60 other text, 45 large text + UI, 30 placeholders, 15 non-text.

---

## 2. Typography Rules

### 2.1 Typeface Selection

- **One sans-serif typeface** for the entire interface (neutral, legible, low cognitive load).
- Optionally add a **second typeface for headings only** (serif, rounded, script) to inject personality.
- Choose popular, well-tested typefaces with multiple weights and high x-height.
- When in doubt, use the platform default system font.

### 2.2 Type Scale (Major Third 1.250)

Start with **18px body** and multiply by 1.250 for each step up:

| Style | Size | Weight |
|---|---|---|
| H1 | 44px | Bold |
| H2 | 36px | Bold |
| H3 | 28px | Bold |
| H4 | 22px | Bold |
| Body | 18px | Regular |
| Small / Caption | 15px | Regular |

- **Body text minimum 18px** -- 14px and 16px are too small for comfortable reading.
- Complex apps/dashboards: use a smaller scale (Major Second 1.125 or Minor Third 1.200).
- Marketing sites: use a larger scale (Perfect Fifth 1.500 or Golden Ratio 1.618).
- Switch to a smaller scale on mobile to prevent excessive wrapping.

### 2.3 Font Weights

Use **Regular + Bold only**. Semi-bold is acceptable if Bold feels too heavy. Avoid light, medium, thin -- they reduce legibility at body sizes.

- **Bold** = headings (emphasis).
- **Regular** = everything else.

### 2.4 Line Height

- Body text (18px): **1.5 to 2** (start at 1.6).
- **Decrease line height as font size increases**: headings at 1.2-1.3, large display at 1.0-1.1.
- Longer lines, darker typefaces, and visually larger typefaces need taller line height.

### 2.5 Line Length

**40-80 characters per line** (66 is ideal). Do not stretch text to fill page width.

### 2.6 Alignment and Spacing

- **Left-align all text** -- consistent anchor point, optimal readability.
- Never justify body text (creates rivers of whitespace, harms dyslexic readers).
- Centre-align only very short blocks (1-2 lines max).
- **Decrease letter spacing for large text** (display sizes).
- Avoid light grey text (fails contrast) and pure black text (eye strain).

---

## 3. Layout and Spacing

### 3.1 The 8pt Grid

All spacing values are multiples of 8:

| Token | Value | Typical Use |
|---|---|---|
| **XS** | 8pt | Innermost text gaps, icon-to-label |
| **S** | 16pt | Internal component padding, gutters (mobile) |
| **M** | 24pt | Card padding, between related fields |
| **L** | 32pt | Column gaps, between field groups, nav link spacing |
| **XL** | 48pt | Section padding (small), large component gaps |
| **XXL** | 80pt | Section padding (desktop), outer margins (desktop) |

For detailed/dense interfaces, allow 4pt increments.

### 3.2 Spacing Principle: Relatedness

- More related elements = closer together.
- Start with small spacing for innermost content, gradually increase outward.
- Use the Squint Test: if you cannot distinguish groups when squinting, increase spacing.

### 3.3 Be Generous with Whitespace

- More whitespace increases comprehension by ~20%.
- When choosing between two spacing tokens, prefer the larger one.
- Tight spacing makes hierarchy and grouping invisible.

### 3.4 The 12-Column Grid

| Property | Desktop | Mobile |
|---|---|---|
| Columns | 12 (flexible %) | 4 (flexible %) |
| Gutters | 32pt (fixed) | 16pt (fixed) |
| Margins | 80pt (fixed) | 16pt (fixed) |

- Smaller elements inside containers do not need to align to the 12-column grid; use spacing tokens instead.
- Content max-width: constrain to maintain 40-80 char line length.

### 3.5 Visual Hierarchy (Priority Order)

1. **Size** -- larger = more important
2. **Colour** -- brighter, richer, warmer, higher contrast
3. **Weight** -- bolder = more important
4. **Proximity** -- surrounded by space = prominent
5. **Position** -- top or first in row = more important
6. **Depth** -- elevated (shadow) = closer to user

**Squint Test:** Blur your eyes. The most important element should still be recognisable. If not, adjust hierarchy.

### 3.6 Depth and Shadows

- Predefined shadow tokens: **Small** (sharp, subtle lift), **Medium**, **Large** (soft, high elevation).
- Light source from top (natural mental model).
- Use darkest palette variation for shadow colour, never pure black.
- White cards on grey backgrounds look elevated without any shadow.

### 3.7 Box Model

Content > Padding > Border > Margin. Spacing starts small at innermost layer and increases outward.

### 3.8 Alignment

- Left-justify content; avoid multiple alignment axes on the same screen.
- Baseline-align text of different sizes sitting on the same horizontal line.
- Border radius tokens: 8pt (small), 16pt (medium), 32pt (large).

---

## 4. Copywriting for UI

### 4.1 Conciseness

- Sentences under **20 words**.
- If a word can be removed without losing meaning, remove it.
- Cut filler: "actually", "basically", "really", "in order to", "would you like to".

### 4.2 Casing and Language

- **Sentence case everywhere** -- only first word and proper nouns capitalised.
- Plain language at a **6th-grade reading level**. Avoid jargon and slang.
- Use contractions naturally (who's, they're, you're).

### 4.3 Structure

- **Front-load** important information (key info at start of sentence/heading).
- **Inverted pyramid**: most important first, supporting info second, background last.
- Break content with **descriptive headings** and **bullet lists**.
- Headings must make sense when read out of context (screen readers extract them).

### 4.4 Numbers and Vocabulary

- Use **numerals** (245, not "two hundred and forty five"). Format with commas: 1,000.
- Very large numbers: combine numerals and words (1 billion, not 1,000,000,000).
- Consistent vocabulary throughout: pick one term and keep it (e.g. "Delete" everywhere, not "Delete" and "Remove").
- Avoid abbreviations; if used, define on first occurrence.

### 4.5 Links and Labels

- Text links must **describe their destination** ("View pricing plans", not "Click here").
- Avoid generic link text: "learn more", "read more", "click here".
- Drop "My" from form labels -- use "Email", not "My email" or "Your email".

### 4.6 Reading Patterns

- **F-pattern**: text-heavy pages (articles, search results). Users scan top, then left edge.
- **Z-pattern**: visual layouts with minimal text (landing pages, hero sections).
- **Gutenberg diagram**: evenly distributed content; primary optical area top-left, terminal area bottom-right (place CTA here).

---

## 5. Buttons

### 5.1 Three Button Weights

| Weight | Style | When to Use |
|---|---|---|
| **Primary** | Solid fill (brand colour) + white text + rounded corners | Most important action per screen/section |
| **Secondary** | Outlined (brand colour border + text) + rounded corners | Alternative or equally important actions |
| **Tertiary** | Text-only (underlined or brand colour, no fill/border) | Least important actions, destructive actions |

- Never use a second solid-fill colour for Secondary (confuses with Primary, especially for colour-blind users).
- Never use light grey fill for Secondary (looks disabled).

### 5.2 Single Primary Per Screen

One Primary button per visible screen area. "If everything is important, nothing is important." Use Secondary for equal-weight alternatives.

### 5.3 Contrast and Sizing

- Button **shape** contrast: >= 3:1 against page background.
- Button **text** contrast: >= 4.5:1 against button fill.
- Target area: minimum **48pt x 48pt** (aligns with 8pt grid).
- Space between adjacent buttons: at least **16pt**.

### 5.4 Alignment and Text

- **Left-align buttons** (desktop). Most important = leftmost.
- **Mobile:** Stack top-to-bottom, most-to-least important; full-width for one-handed use.
- Button text formula: **verb + noun** ("Save changes", "Delete message", "Edit profile"). Avoid vague labels: "OK", "Submit", "Yes".

### 5.5 Destructive Action Friction (Escalating)

| Level | Technique | Example |
|---|---|---|
| **Initial** | Make destructive action a Tertiary button, position away from Primary | Tertiary "Delete" far from Primary "Save" |
| **Light** | Simple confirmation dialog | "Delete message?" / Delete message / Cancel |
| **Medium** | Red button + warning icon in dialog | "Delete article? You won't be able to recover it." |
| **Heavy** | Confirmation checkbox before action enables | "I confirm I want to delete my account" checkbox |
| **Undo** | Allow reversal after action | Toast: "Message deleted. Restore" |

### 5.6 Avoid Disabled Buttons

Disabled buttons provide no feedback, fail contrast, and are not keyboard-accessible. Prefer: enable and validate on submit, remove unavailable actions with explanation, or use a lock icon for premium features.

### 5.7 Icon + Text Pairs

Match icon weight (stroke thickness) to text weight. Match icon size to text size. If mismatch is unavoidable, decrease icon contrast using the Medium colour token.

---

## 6. Forms (Quick Reference)

**For full depth, load the `form-ux-design` skill.**

### 6.1 Layout

- **Single column** -- consistent downward momentum, fewer missed fields.
- Stack checkboxes and radio buttons vertically.
- Exception: short related fields side by side (expiry + CVC).

### 6.2 Labels and Hints

- Labels **on top** of fields (never floating, never placeholder-as-label).
- **4pt** gap between label and its field.
- **32pt** gap between field groups.
- Hints above fields, not below (avoid being covered by autofill/keyboard).

### 6.3 Field Sizing and Input Types

- Match field width to expected input length (4-digit postcode = narrow field).
- **Radio buttons** for <= 10 options (always visible, one-click).
- **Autocomplete** for > 10 options (type-ahead, max ~10 suggestions).
- **Steppers** for small numeric adjustments (48pt min button target).
- **Toggle switch** for immediate-effect binary options; **checkbox** for submit-required binary options.

### 6.4 Validation

- **Validate on submit** -- display error summary at top of form with links to invalid fields.
- Error messages above fields (not below). Red highlight + icon.
- Never rely on colour alone for error indication.
- Exceptions for inline validation: password strength, character limits, username availability.

### 6.5 Required/Optional Marking

- Mark required fields with asterisk (*) and include instructions: "Required fields are marked with an asterisk *".
- Mark optional fields with "(optional)".
- Safest: use the word "required" on required fields.
- Minimise optional fields -- every field must earn its place.

### 6.6 Field Borders

Form field borders need at least **3:1** contrast. Applies to buttons, toggles, steppers, checkboxes, radio buttons.

---

## 7. Component Patterns (Kuleszo)

### 7.1 Search

- Text field + button labelled **"Search"** (not just an icon).
- Show recent searches on focus (reduces repeat typing).
- Autocomplete suggestions as user types; max ~10 results.
- Highlight matching characters in bold.

### 7.2 Modals

- Max width **480px**; centre on viewport.
- Clear close affordance (X button top-right + Escape key).
- Darken background overlay (trap focus inside modal).
- Single Primary action; Secondary for cancel/dismiss.
- Avoid nesting modals -- use progressive disclosure or a new screen instead.

### 7.3 Cards

- Consistent border-radius across all cards in a view.
- Shadow depth signals interactivity: deeper shadow = clickable card.
- Keep card content scannable: image + heading + 1-2 line summary + CTA.
- Ensure similar text length across cards in a row for visual alignment.

### 7.4 Navigation

- Max **7 top-level items** (Miller's Law). Group overflow under "More" or mega-menu.
- Highlight current page/section clearly (bold, underline, or brand colour indicator).
- Mobile: **bottom navigation bar** for primary actions (thumb zone); hamburger menu for secondary.
- Breadcrumbs for deep hierarchies (> 2 levels).

### 7.5 Hero Sections

- **Single CTA** (do not split attention with multiple actions).
- Max 2 sentences of supporting text.
- Ensure text contrast on background images: gradient overlay (darkest variation at 90% opacity from bottom), semi-transparent overlay (50%), blur, or solid text background.
- Place CTA in the terminal area (bottom-right per Gutenberg diagram) or directly below headline.

### 7.6 Dropdowns

- Max **7 visible options** without scrolling.
- For > 15 items: group under section headers.
- For > 30 items: switch to autocomplete/search.
- Always show a default/placeholder selection.

---

## 8. Dark Mode Rules

### 8.1 Not Just Inversion

Dark mode is a distinct palette, not a CSS `invert()`. Colours, contrast ratios, and shadows all need independent tuning.

### 8.2 Colour Adjustments

- **Desaturate** brand and system colours by 10-20% (saturated colours vibrate on dark backgrounds).
- Avoid pure white (#FFFFFF) text on dark backgrounds -- use Lightest token (e.g. HSB hue, 4, 80).
- Shadows are nearly invisible on dark; use **lighter borders or surface elevation** to separate layers.

### 8.3 Hierarchy Preservation

- Same size, weight, and spatial hierarchy as light mode.
- Headings remain largest and boldest; body remains Regular weight.
- Interactive elements still use Primary colour (desaturated version).

### 8.4 Independent Testing

- Test all contrast ratios against the Dark palette independently.
- APCA values change when you swap foreground/background -- re-verify.
- Test with both light and dark system preferences active.

---

## 9. Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Pure black (#000) backgrounds or text | Eye strain from extreme contrast | Dark grey with hue tinge |
| Multiple brand colours on interactive elements | Confuses what is clickable | Single brand colour for interactive |
| Placeholder text as label | Disappears on input, inaccessible contrast | Label above field, always visible |
| Justified body text | Rivers of whitespace, harms dyslexic readers | Left-align |
| Centre-aligned long paragraphs | Inconsistent line start, hard to scan | Left-align; centre only 1-2 lines |
| Trendy effects (glassmorphism, neumorphism) | Fail contrast, short shelf life | Clean, minimal styles |
| Multiple primary buttons per screen | Everything competing = nothing prominent | One Primary per visible area |
| Disabled buttons without explanation | No feedback, inaccessible | Enable + validate, or explain |
| Title Case for UI text | Harder to scan, inconsistent rules | Sentence case |
| Generic link text ("Click here") | Inaccessible, non-descriptive | Describe destination |

---

## 10. Design Checklist

Before shipping any screen, verify:

- [ ] HSB-based colour palette created (light + dark variants)
- [ ] WCAG contrast verified: 4.5:1 small text, 3:1 large text + UI components
- [ ] System colours (red/amber/green/blue) paired with icons, not colour alone
- [ ] Type scale applied (Major Third or project-appropriate scale)
- [ ] Body text >= 18px; line height 1.5-2 for body
- [ ] Line length 40-80 characters
- [ ] 8pt spacing grid used consistently (XS through XXL tokens)
- [ ] 12-column grid for page layout (32pt gutters desktop, 16pt mobile)
- [ ] Single Primary button per visible screen area
- [ ] All touch targets >= 48pt; >= 16pt between buttons
- [ ] Sentence case for all UI text
- [ ] Button text = verb + noun
- [ ] Links describe their destination
- [ ] Forms: single column, labels on top, validate on submit
- [ ] Squint test passes (hierarchy clear when blurred)
- [ ] Dark mode palette tested independently for contrast
- [ ] No pure black or pure white in palette
- [ ] Destructive actions use appropriate friction level

---

*Sources: Practical UI (Dannaway, 2022) -- 104 rules; Better UI Components 3.0 (Kuleszo, 2024) -- component patterns; Fixing Bad UX (Maioli) -- conversion patterns, reading models, microcopy.*
