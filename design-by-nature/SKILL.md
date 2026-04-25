---
name: design-by-nature
description: Use when designing logos, brand systems, illustration systems, motion, or layout grids that need to feel inevitable rather than arbitrary — applies Maggie Macnab's universal forms (branch, meander, spiral, helix, packing, radial), five archetypal shapes (circle, line, triangle, square, spiral), three symmetries (translation, reflection, rotation), and proportion (golden ratio / Fibonacci) to align form with message so users read intent pre-cognitively. Use to choose grid type, logo skeleton, motion archetype, or icon family from the brief.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Design by Nature — Universal Forms in Digital Design

Source: Maggie Macnab, *Design by Nature: Using Universal Forms and Principles in Design* (New Riders).

## Use when

- Designing a logo or brand mark from a brief.
- Choosing a layout grid (rectangular, hexagonal, golden-ratio, radial) for a product or marketing surface.
- Planning an illustration system — picking the visual DNA (curve types, corner types) that scales from spot to hero.
- Designing motion archetypes — what kind of movement signals what kind of meaning.
- Designing iconography — matching icon shape to function archetype.
- Reviewing why a design "feels off" without an obvious technical fault.

## Do not use when

- The task is implementation-only (load `every-layout`, `tailwind-css`, etc.).
- The task is colour selection (load `color-theory`).
- The task is purely UX flow / wireframing (load `interaction-design-patterns`, `ux-principles-101`).

## Prerequisites

- The brief — what the design is for, audience, what feeling it must produce.
- Existing brand context if any (competitors, prior marks, the firm's positioning).

## Required inputs

- The mission or category of the brand/feature ("financial trust", "creative agency", "wellness", "tech-transfer").
- The primary user action or emotional response intended.
- Any existing assets that constrain the design (typography, colour, photographic style).

## Outputs

- A chosen **shape archetype** (circle / line / triangle / square / spiral) with the rationale tied to the brief.
- A chosen **pattern** (branch / meander / spiral / helix / packing / radial) with the rationale.
- A chosen **symmetry** (translation / reflection / rotation / asymmetry).
- A chosen **proportion system** (golden ratio / square / 4:3 / Fibonacci spacing scale).
- A logo concept that satisfies Macnab's three essentials (works in B&W, balanced negative/positive space, embedded story).
- For brand systems: the DNA (one shape + one pattern + one symmetry + one ratio) propagated across logo, type, motion, iconography, illustration.

## Non-negotiables

1. **Match form to message.** Corners mean precision/authority; curves mean flexibility/care. Choose corners for finance/security/legal; curves for wellness/care/hospitality. Mixing is intentional, not aesthetic.
2. **Black-and-white scaling test.** A logo must work in pure black on white at favicon (16px) and at billboard size before colour or effects are added. If it fails, redesign before colourising.
3. **Negative space is information.** Aim for roughly equal positive and negative space. Empty space carries half the meaning in good marks.
4. **Repetition is what makes a brand.** Saturate consistently with the core form across every collateral piece. Inconsistent application destroys recognition.
5. **Story before craft.** Every logo embeds one metaphor that connects mark to mission. A beautiful mark with no story doesn't stick.
6. **Phi is a sounding board, not a straitjacket.** Use the golden ratio to break ties when proportions feel off, not to force every dimension into compliance.
7. **Self-similarity across scale.** The brand DNA must read at favicon, app icon, business card, billboard. If you can't trace the same DNA through every collateral piece, the system isn't designed yet.

## Decision rules

### Shape archetype → meaning

| Shape | Positive read | Where to use |
|---|---|---|
| Circle | wholeness, source, autonomy, friendliness | global brands, communities, holistic services, avatars, pill buttons, soft chrome |
| Line / cross | relationship, precision, joining | precision tools, navigation, dividers, "+" affordances |
| Triangle | aspiration, transformation, direction | mobility, "next" affordances, play buttons, transcendence |
| Square | stability, durability, manifestation | finance, infrastructure, contracts, default UI containers |
| Spiral | creativity, regeneration, expansion | creative agencies, life cycles, growth-oriented services, loading reveals |

### Pattern → meaning

| Pattern | Where it lives in nature | Where to use in design |
|---|---|---|
| Branching (angular bifurcation) | rivers, neurons, lightning, dendrites | tech-transfer, networking, sitemaps, decision trees, dependency graphs |
| Meander (sinuous flow) | streams, brain folds, intestines, labyrinths | travel, leisure, narrative, ambient experiences, decorative borders |
| Spiral (logarithmic / Archimedean) | nautilus, galaxies, rose petals | creative agencies, regeneration, life cycles, radial menus |
| Helix (constant-diameter twist) | DNA, drill bits, screws, woven cloth | medical, security, sync, pairs in cooperation |
| Stacking & packing (hex / square / triangle) | hives, basalt columns, brick walls | finance, real estate, dashboards, modular grids |
| Radial burst | sun, fireworks, sand-dollar | celebration, attention, pie/donut charts, notifications |

### Symmetry → meaning

| Symmetry | Use for |
|---|---|
| Translation (constant interval repeat) | rhythm in lists/tables, "diverse but equal" content rows |
| Reflection (mirror) | settled, balanced, trustworthy logos and hero compositions |
| Rotation (point symmetry) | active, multi-aspect brands, radial menus, activity indicators |
| Asymmetry | contemporary editorial energy; intentional tension; never accidental |

### Grid choice

| Grid | When |
|---|---|
| Rectangular (12-col / 4-col) | institutional, content-dense, default for most products |
| Hexagonal | connectivity, social graphs, lateral diffusion, contribution heatmaps |
| Golden-ratio (1.618fr / 1fr) | editorial, hero, marketing, content+aside layouts where one side dominates |
| Radial | single decision points, polls, navigation hubs |

## Workflow

1. **Read the brief.** Identify the mission, audience, intended feeling.
2. **Decide corners vs curves.** First branching decision — sets the family of shapes and patterns.
3. **Pick the shape archetype.** Use the table; one of the five will fit better than the others.
4. **Pick the pattern.** The pattern carries the *energy* of the brand. Branching for delivery; meandering for ambient; spiral for creation; helix for binding; packing for storage; radial for attention.
5. **Pick the symmetry.** Reflection is the safe default for trust; rotation for dynamism; asymmetry for editorial energy.
6. **Pick the proportion system.** Golden ratio for editorial layouts and type scale; whole-integer ratios (1:1, 4:3, 16:9) for product UI; Fibonacci scale for spacing.
7. **Sketch B&W thumbnails.** Test the shape + pattern + symmetry combination in pure black on white. Multiple roughs.
8. **Embed the story.** What metaphor lives inside the mark? Macnab's Agricultura logo: hand silhouette = "hand-grown," palm negative space = leaf, lifeline = stem.
9. **Test scale.** Render at 16px and at 600px. If the form breaks at either end, redesign.
10. **Propagate the DNA.** Apply the same shape/pattern/symmetry/ratio to type, motion, iconography, illustration. Self-similarity is what makes a brand system, not a brand sticker.

## Type scale on the golden ratio

```css
:root {
  --phi: 1.618;
  --phi-inv: 0.618;
  --fs-base: 1rem;
  --fs-h6: calc(var(--fs-base) * var(--phi-inv) * var(--phi-inv));
  --fs-h5: calc(var(--fs-base) * var(--phi-inv));
  --fs-h4: var(--fs-base);
  --fs-h3: calc(var(--fs-base) * var(--phi));
  --fs-h2: calc(var(--fs-base) * var(--phi) * var(--phi));
  --fs-h1: calc(var(--fs-base) * var(--phi) * var(--phi) * var(--phi));
}

.layout-phi {
  display: grid;
  grid-template-columns: 1.618fr 1fr;
  gap: clamp(1rem, 2vw, 2rem);
}
```

## Motion archetypes

- **Spiral** — creative reveal, regeneration, "loading something new."
- **Helix** — pairing, syncing, binding two streams.
- **Meander** — ambient idle states, soft scroll-linked motion.
- **Branch** — dependency or tree expansions.
- **Radial burst** — success/celebration moments — earned, not constant.
- **Translation** — list-item stagger, conveyor patterns.
- **Rotation** — activity indicators, refresh.
- **Reflection** — paired transitions, before/after wipes.

## Iconography

Match icon shape archetype to function:

- **+ (line/cross)** for add — relationship/joining archetype.
- **○ (circle)** for status/identity/avatar — wholeness archetype.
- **△ (triangle)** for play/direction/next — aspiration/direction archetype.
- **□ (square)** for containers/grids — stability archetype.
- **⟲ (rotation)** for refresh/cycle — rotation symmetry.
- **⤴ (branch)** for fork/share — branching pattern.
- **〰 (meander)** for ambient/trend lines — meander pattern.

Choose one stroke style and one corner radius family across the system. Translation symmetry across the icon set is what reads as "consistent" — because it *is* consistent at the atomic level.

## Anti-patterns

- **Choosing curves for a financial brand because curves "look modern".** Mismatch — finance demands corners. The mark will feel unserious regardless of execution quality.
- **Triangle logo for a wellness brand.** Triangle is aspiration/transformation; wellness needs circle/curve. The mark will feel cold.
- **Multiple unrelated patterns in one brand system** (e.g., spiral logo + hex illustrations + branching motion). The brain reads as noise; the brand is unsigned.
- **Forcing golden ratio onto every dimension.** Macnab is explicit it's a sounding board. A logo that's 1.618:1 but tells no story is still a bad logo.
- **Adding colour and effects before B&W works.** If the form fails in black on white, no amount of gradient saves it.
- **Symmetric logo for a brand whose message is dynamic/editorial.** Reflection reads as settled. Use rotation or asymmetry for "alive".
- **No metaphor.** A typographic mark with no embedded story is a wordmark, not a logo. Wordmarks are fine — but choose them deliberately, not by default.
- **Inconsistent DNA propagation.** Logo curves but illustrations are angular and motion is linear. The system isn't designed.

## Read next

- `practical-ui-design` — translates archetypes into typography, spacing, colour decisions.
- `color-theory` — pair shape archetype with colour harmony from the brief.
- `every-layout` — implement chosen grid (golden ratio, hex tile, rectangular) with primitives.
- `motion-design` — animation timing and curves for chosen motion archetype.
- `practical-ui-design` — visual hierarchy, typographic systems, the everyday craft.

## References

- `references/forms-and-shapes.md` — full notes on the six universal patterns and five archetypal shapes, with where they live in nature and where to use them in digital design.
- `references/symmetry-and-proportion.md` — three symmetries, tessellation, asymmetry, golden ratio, Fibonacci, scale, and self-similarity, with CSS examples.
- `references/process.md` — Macnab's eight-step linear process, the biomimicry six-step spiral, and her lived heuristics (detective work first, capture energy then refine, B&W scaling test).
- `references/logo-checklist.md` — the three essentials checklist + extensions, applied to digital marks (favicon, app icon, social avatar).
- `references/biophilic-application.md` — applying the framework to motion, iconography, illustration systems, brand DNA propagation.
