---
name: ai-slop-prevention
description: Detect and eliminate AI-generated UI anti-patterns ('AI slop') across
  typography, colour, layout, visual effects, and motion. Cross-cutting quality gate
  — load alongside any frontend/UI skill to ensure distinctive, production-grade interfaces...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Slop Prevention Skill
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Detect and eliminate AI-generated UI anti-patterns ('AI slop') across typography, colour, layout, visual effects, and motion. Cross-cutting quality gate — load alongside any frontend/UI skill to ensure distinctive, production-grade interfaces...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-slop-prevention` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | AI slop check report | Markdown doc flagging generic typography, colour, layout, and motion anti-patterns in AI-generated UI | `docs/ux/ai-slop-check-checkout.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Purpose

AI coding tools produce recognisable visual fingerprints — generic, uninspired interfaces immediately identifiable as machine-generated. This skill is the quality gate that catches and eliminates those patterns.

**Cross-cutting skill.** Load alongside any platform or design skill (webapp-gui-design, jetpack-compose-ui, swiftui-design, practical-ui-design, healthcare-ui-design, pos-sales-ui-design).

## The AI Slop Test

After generating any UI, ask: **"If I told someone AI made this, would they believe me immediately?"**

If yes — it's slop. Redesign.

---

## 1. Typography Anti-Patterns

### DON'T

| Pattern | Why It's Slop |
|---|---|
| Default to Inter, Roboto, Arial, Open Sans | Invisible, generic — screams "I didn't choose a font" |
| System font stack as aesthetic choice | Lazy, not intentional |
| Monospace for "technical" feel | Overused AI crutch for developer tools |
| Large rounded icons above every heading | Template pattern, immediately recognisable |
| Same font size everywhere | No hierarchy, no visual interest |
| Title Case For Every Heading | Looks generated, harder to scan |

### DO

- Choose a distinctive typeface that matches brand personality
- Create real typographic hierarchy: display (2-3x body), heading, body, caption
- Use weight contrast (Regular + Bold) not size alone
- Decrease letter-spacing for large display text
- Consider serif or slab-serif for personality — not everything needs sans-serif
- Use sentence case for all UI text

---

## 2. Colour Anti-Patterns

### DON'T

| Pattern | Why It's Slop |
|---|---|
| Cyan-on-dark theme | The #1 AI colour fingerprint of 2024-2025 |
| Purple-to-blue gradients | Second most common AI palette |
| Neon accents on dark backgrounds | Looks like every AI demo |
| Gradient text on headings/metrics | Decorative without purpose |
| Gray text on coloured backgrounds | Washed-out, fails contrast |
| Pure black (#000) or pure white (#fff) | Harsh, unrefined — real designers tint neutrals |
| Dark mode with glowing accents as default | AI's favourite "futuristic" look |
| Rainbow/multi-hue palettes without system | Looks random, not designed |

### DO

- **Tint all neutrals**: Add 2-5% of brand hue to greys (never pure grey)
- Use **OKLCH** colour space for perceptually uniform palettes
- Follow the **60-30-10 rule**: 60% neutral, 30% secondary, 10% accent
- Design light mode first — dark mode is a separate palette, not an inversion
- Use colour semantically (red=error, amber=warning, green=success, blue=info)
- Pair every colour indicator with an icon (never rely on colour alone)
- Desaturate brand colours 10-20% for dark mode (saturated colours vibrate on dark)

---

## 3. Layout Anti-Patterns

### DON'T

| Pattern | Why It's Slop |
|---|---|
| Everything in cards | Cards are a crutch — not every element needs a container |
| Cards nested inside cards | Visual noise, unclear hierarchy |
| Identical card grids (icon + heading + text repeated) | The most recognisable AI layout pattern |
| Hero metric template (big number + small label + stats) | Used in every AI dashboard |
| Everything centred | Lazy alignment — real layouts use intentional asymmetry |
| Same spacing everywhere | No rhythm, no grouping, flat hierarchy |
| Three-column feature grid with icons | Every AI landing page looks like this |
| Sidebar + main content + right panel by default | Generic dashboard template |

### DO

- Use **varied spacing** to create visual rhythm (tight grouping + generous separation)
- Break the grid intentionally — asymmetric layouts feel designed
- Use whitespace as a design element, not just padding
- Choose layout tools purposefully: Flexbox for 1D, CSS Grid for 2D
- Let content determine the layout, not a template
- Apply the **Squint Test**: blur your eyes — groups should still be distinguishable
- Use visual hierarchy through multiple dimensions (size, weight, colour, position, space)

---

## 4. Visual Effects Anti-Patterns

### DON'T

| Pattern | Why It's Slop |
|---|---|
| Glassmorphism everywhere | Decorative blur, glass cards, glow borders — peak AI aesthetic |
| Rounded rectangles with thick coloured side border | Common AI card decoration |
| Sparklines as decoration | Used without real data context |
| Excessive drop shadows on everything | Looks like a template, not a design |
| Gradient backgrounds behind every section | Visual noise, no purpose |
| Neumorphism (soft raised/recessed look) | Fails contrast, dated trend |
| Decorative SVG blobs and waves | AI's favourite background filler |
| Excessive modals for simple actions | Poor UX disguised as "clean" design |

### DO

- Use shadows purposefully: subtle lift for cards, deeper for elevated overlays
- Tint shadows with brand hue (never pure black shadows)
- Use borders sparingly — whitespace separates better than lines
- If using background effects, ensure they serve hierarchy (not decoration)
- Prefer real content over placeholder decorations
- Use depth (elevation) semantically: higher = more important/closer to user

---

## 5. Motion Anti-Patterns

### DON'T

| Pattern | Why It's Slop |
|---|---|
| Bounce or elastic easing | Feels dated and tacky — the calling card of AI demos |
| Animating everything on page load | Animation fatigue, slows perceived performance |
| Animating layout properties (width, height, top, left) | Jank, poor performance |
| Slow fade-ins on scroll (> 500ms) | Feels sluggish, not smooth |
| Parallax scrolling effects | Overused, causes motion sickness |
| Spinning loaders for every state | Lazy loading pattern |

### DO

- Use **transform + opacity only** (GPU-accelerated, jank-free)
- Follow timing rules: 100-150ms (feedback), 200-300ms (state), 300-500ms (layout)
- Use exponential easing: `ease-out-quart`, `ease-out-quint` (not `ease` or `linear`)
- Exit animations at ~75% of enter duration
- **Always respect `prefers-reduced-motion`** (35%+ of adults over 40 are affected)
- Animate with purpose: guide attention, show relationships, provide feedback

---

## 6. Content & Copy Anti-Patterns

### DON'T

| Pattern | Why It's Slop |
|---|---|
| Lorem ipsum in shipped UI | Obviously placeholder |
| "Welcome to [App]" as hero text | Generic, says nothing |
| "Submit" on form buttons | Vague — what are they submitting? |
| "Click here" link text | Inaccessible, non-descriptive |
| Corporate jargon ("leverage", "synergy", "robust") | AI vocabulary fingerprint |
| Emoji-heavy section headers | Looks like AI marketing copy |
| "Loading..." for every wait state | No context, no personality |

### DO

- Button text = **verb + noun** ("Save changes", "Delete message", "Create account")
- Error messages: what happened + why + how to fix
- Empty states: acknowledge + explain value + provide action
- Use specific loading text ("Saving your draft..." not "Loading...")
- Write in active voice, plain language, short sentences
- Keep vocabulary consistent (pick one term per concept across the whole UI)

---

## 7. The Quality Gate Checklist

Before shipping any AI-generated interface, verify **every item**:

### Visual Identity

- [ ] Typeface is intentionally chosen (not Inter/Roboto/system default)
- [ ] Colour palette uses tinted neutrals (no pure grey, black, or white)
- [ ] Palette is NOT cyan-on-dark or purple-to-blue gradient
- [ ] Dark mode is independently designed (not inverted light mode)

### Layout & Composition

- [ ] Not everything is wrapped in cards
- [ ] Spacing varies to create rhythm and grouping
- [ ] Layout doesn't match the "icon + heading + text" card grid template
- [ ] At least one intentional asymmetry or grid break

### Effects & Polish

- [ ] No glassmorphism, decorative blur, or glow borders
- [ ] Shadows are subtle and purposeful (tinted, not pure black)
- [ ] No gradient text on headings or metrics
- [ ] No decorative SVG blobs or waves

### Motion

- [ ] No bounce or elastic easing
- [ ] Animations use transform + opacity only
- [ ] `prefers-reduced-motion` is handled
- [ ] Timing follows the 100/300/500 rule

### Content

- [ ] No "Submit", "Click here", or "Loading..." text
- [ ] Button labels use verb + noun
- [ ] Error messages explain what, why, and how to fix
- [ ] No corporate AI vocabulary ("leverage", "robust", "seamlessly")

### Accessibility

- [ ] Text contrast >= 4.5:1 (body), >= 3:1 (large text, UI components)
- [ ] Colour is never the sole indicator (always paired with icon or text)
- [ ] Touch targets >= 44x44px (48x48px preferred)
- [ ] Keyboard navigation works (focus visible, logical tab order)

---

## 8. Remediation Patterns

When slop is detected, apply these fixes:

| Problem | Fix |
|---|---|
| Generic font | Choose a font with personality (serif, geometric, humanist) |
| Cyan/purple palette | Derive palette from brand hue using OKLCH; tint neutrals |
| Card grid monotony | Mix card sizes, use list views, add featured items, break the grid |
| Glassmorphism | Replace with subtle elevation (shadow) or surface tinting |
| Bounce animations | Switch to `ease-out-quart` or `cubic-bezier(0.25, 1, 0.5, 1)` |
| Everything centred | Left-align content; use asymmetric hero layouts |
| Same spacing everywhere | Apply semantic spacing tokens with varied scale |
| Gradient text | Use solid colour with weight/size for emphasis instead |

---

## Integration with Other Skills

This skill is a **cross-cutting quality gate**. Reference it from:

- `practical-ui-design` — apply after colour/typography/layout choices
- `webapp-gui-design` — check before shipping any web interface
- `jetpack-compose-ui` / `swiftui-design` — validate mobile UI decisions
- `healthcare-ui-design` — ensure clinical UIs are distinctive yet professional
- `pos-sales-ui-design` — verify POS screens avoid template looks
- `motion-design` — validate animation choices
- `design-audit` — include AI slop check in audit reports

---

*Source: Impeccable — Design fluency for AI harnesses (Bakaus, 2025). Anti-patterns observed across AI-generated interfaces 2024-2025.*