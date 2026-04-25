---
name: color-theory
description: Use when choosing or auditing colours for any web, app, or brand surface — provides the Flux Academy process (brief → primary hue → harmony → palette → 60/30/10 → contrast review), the six harmonies (monochromatic / analogous / complementary / split-complementary / triadic / tetradic), HSL/OKLCH scale generation, and WCAG contrast tactics. Use this when you need a defensible palette decision, not just a swatch.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Colour Theory — Choosing Colours That Work

Sources: Flux Academy, *The Complete Guide for Choosing Colors* (Ran Segall et al.); WCAG 2.1; CSS Color 4 (OKLCH).

## Use when

- Picking a brand or website palette from a brief (with or without existing brand colours).
- Auditing an existing palette for accessibility, ratio balance, or visual coherence.
- Generating a tonal scale (50–900) from a single brand colour.
- Resolving a contrast failure without abandoning the brand colour.
- Deciding which colour harmony fits a brief (calm / playful / premium / punchy CTA).

## Do not use when

- The user wants a design-system audit (load `design-system` / `design-audit`).
- The task is purely typography or layout (load `practical-ui-design` / `every-layout`).
- The user wants generative palettes from a photograph alone (point them at coolors.co / Canva, then return here for refinement).

## Prerequisites

- The brief: who is the audience, what mood, what do they need to do, what constraints.
- Any existing brand assets: logo, photography, prior collateral, style guide.
- The output medium (screen / print / both) — affects model choice (sRGB vs OKLCH vs CMYK).

## Required inputs

- A mood word or three (e.g. "premium / minimal / trustworthy"; "playful / bold / accessible"; "wellness / calm / organic").
- Audience snapshot (rough demographic + cultural context).
- Either an existing brand hex code, or hero imagery to sample from, or neither.
- Accessibility target (WCAG 2.1 AA at minimum; AAA for content-heavy / regulated sites).

## Outputs

- A documented primary hue (in HSL and hex; OKLCH if project supports CSS Color 4).
- A 10-step tonal scale per brand colour (50, 100, 200, 300, 400, 500-base, 600, 700, 800, 900).
- A 10-step neutrals scale, slightly tinted toward the primary.
- A harmony-justified accent (1 colour, optional 1 secondary support colour).
- A 60/30/10 usage ratio plan (which colour goes where).
- WCAG contrast verification per text/background pairing.
- Semantic colours (success, warning, error, info) that sit inside the brand palette.

## Non-negotiables

1. **Primary hue first, palette second.** All colour palettes begin with one single colour. Pick it from the brief and audience, not from a generator.
2. **Tone matters more than hue for legibility.** Two different hues at the same lightness can have terrible contrast. Lock body text and background lightness early.
3. **Brand colour is rarely body-text-on-white safe.** Reserve raw brand colour for chrome, headings, and CTAs. Use a darker shade (700–800) for body-weight brand text.
4. **Build base first, accents last.** Lay out the page in primary + neutrals. Add accent colours only at the end of the design process.
5. **Colour is never the only signal.** Errors carry icons + text; links underline; status uses shape and label, not just hue.
6. **Match the harmony to the brief.** Don't pick "rainbow" because it looks fun; match the harmony to the message.

## Decision rules

### Picking the harmony

| Brief signal | Default harmony | Why |
|---|---|---|
| Premium / minimal / SaaS / clinical | Monochromatic, or analogous + 1 neutral | Calm, focused, photography carries weight |
| Calm, organic, wellness, food, nature | Analogous | Harmony without monotony |
| SaaS with strong CTA / conversion-focused | Split-complementary | Punchy contrast without aggression |
| Sports, alarms, posters | Complementary | Maximum visual punch, intentional vibration |
| Playful, creative agency, kids, editorial | Triadic | Bold, varied, signals creativity |
| Entertainment, festivals, magazines | Tetradic with strong neutrals | Rich variety, needs strong dominance discipline |

### Choosing colour model

| Need | Use | Why |
|---|---|---|
| Match an existing brand hex | HEX / RGB | Ground truth |
| Hand-tune tints / shades / tones | HSL | Lightness is intuitive (caveat: not perceptually uniform) |
| Match Figma's colour picker | HSB / HSV | Designer-friendly |
| Generate a perceptually uniform 10-step scale | OKLCH | Equal L truly looks equal-bright |
| Print output | CMYK | Required by print profiles |

For modern web projects, generate scales in OKLCH then export hex for production CSS.

### Resolving a contrast failure

1. **Lower body text lightness** before changing hue. Move from `purple-500` to `purple-700` for body weight on white.
2. **Raise background lightness** if dropping text further would lose hue identity.
3. **Add a scrim** on imagery: `rgba(0,0,0,0.4-0.6)` to guarantee 4.5:1 for white text.
4. **Move to a different shade on the same scale** — never re-pick the hue for an accessibility fix.
5. **Use a darker version for AA, the brand mid-tone for visuals.** Document both in the design system.

## Workflow

1. **Define the brief.** Mood word, audience, viewer action. If client has a brand guide, use the exact hex codes as ground truth and skip to step 4.
2. **Ask the four diagnostic questions.** What constraints? Is this all the guidance? What feel? What action?
3. **Pick the primary hue.** From mood + audience. If imagery exists, sample from it; consider tinting the imagery toward the brand hue (duotone) so it lives inside the palette.
4. **Choose the harmony.** Use the harmony decision table.
5. **Generate scales.** 10 steps for primary, 10 for neutrals tinted toward primary, 3–5 for the accent (base, hover, active, disabled).
6. **Plan the 60/30/10 distribution.**
   - Background / surface (60%): a neutral.
   - Primary brand colour (30%): headers, hero panels, primary buttons, brand chrome.
   - Accent (10%): CTAs, highlights, badges, gradient endpoints.
7. **Add semantic colours** that sit inside the palette: success (green), warning (amber), error (red), info (blue) — tuned so they don't read as Bootstrap defaults.
8. **WCAG verification.** Check every text-on-background pair against AA (4.5:1 body, 3:1 large/UI). Document the "minimum AA on white" step (usually 600–700) and the "AA on dark" step (usually 200–300).
9. **Test the page.** Apply, look at the result. Run the review checklist.
10. **Iterate.** Move shades up/down the scale to fix issues; never re-pick the hue mid-build.

## The Flux 60/30/10 rule (clarified)

> "You use the primary color 60% of the time, the secondary for 30%, and the accent color for only 10%."

It is a **dominance gauge**, not a literal three-colour rule:

- A site with primary + 5 neutrals + 1 accent still applies 60/30/10 by *visual weight*: neutrals dominate (60%), primary structures (30%), accent points (10%).
- Increase neutrals if the page is content-heavy (long-form reading, dashboards).
- Increase primary if the page is brand-led (hero, marketing).
- Never let accent exceed ~10% of visual area, or it stops attracting the eye.

## Worked example — generating a palette from a single hue

Given primary `hsl(265, 70%, 55%)` (purple) for a "creative agency, premium, dreamy" brief:

| Token | HSL | Hex | Role |
|---|---|---|---|
| purple-50 | hsl(265, 70%, 97%) | #f5f1ff | tinted background |
| purple-100 | hsl(265, 70%, 92%) | #e5d9ff | hover surface |
| purple-200 | hsl(265, 70%, 84%) | #cdb3ff | borders, dividers |
| purple-300 | hsl(265, 70%, 74%) | #b08aff | disabled/secondary text on light |
| purple-400 | hsl(265, 70%, 65%) | #9560ff | accent hover |
| purple-500 | hsl(265, 70%, 55%) | #7a3ee0 | brand mid-tone (chrome) |
| purple-600 | hsl(265, 72%, 45%) | #5e22c2 | primary button |
| purple-700 | hsl(265, 75%, 35%) | #441a96 | body text on white (AA) |
| purple-800 | hsl(265, 80%, 25%) | #2f126b | headings on white |
| purple-900 | hsl(265, 85%, 15%) | #1c0944 | hero background |

Accent (split-complementary partner of purple): magenta `hsl(330, 80%, 55%)` for CTAs and gradient endpoints.
Neutrals: `hsl(265, 8%, L%)` for L = 97, 92, 84, 74, 60, 45, 30, 18, 10 — slight purple tint for cohesion.

## Anti-patterns

- **Picking the hue from a generator without the brief.** Generators are starting points. Always validate against mood + audience.
- **Treating "blue = trust, red = danger" as universal.** Psychology is situational and cultural. Same hue at different saturations does opposite jobs.
- **Using brand colour as body text on white.** Almost always fails WCAG AA. Reserve raw brand for chrome and CTAs.
- **Building accents first.** Loud accents in non-CTA areas pull attention away from conversion.
- **Treating 60/30/10 as exact percentages.** It's a balance gauge, not a measurement.
- **Re-picking the hue to fix a contrast failure.** Move shade, don't move hue — preserves brand identity.
- **Equal-saturation triadic.** All three at full saturation is overwhelming. Pick one dominant; mute the other two.
- **Pure-neutral grey on a coloured site.** A grey tinted toward the primary feels cohesive; pure grey reads as "design-system default".
- **No documented "minimum AA" step.** Without it, designers will pick the brand mid-tone for body text and ship inaccessible UI.

## Read next

- `practical-ui-design` — typography, spacing, and how colours land in real UI.
- `design-system` — tokenising the palette into CSS custom properties, Figma styles, and theme switching.
- `accessibility-audit` — WCAG verification beyond colour (focus, motion, ARIA).
- `every-layout` — applying colour to layout primitives (Box.invert, etc.).
- `design-by-nature` — colour selection that aligns with natural form archetypes (corners vs curves, warm vs cool ↔ message).

## References

- `references/flux-process.md` — the full Flux Academy walkthrough with the worked example (purple-balloons → magenta-accent palette) and the imagery-first algorithm.
- `references/harmonies.md` — deep notes on each harmony (monochromatic, analogous, complementary, split-complementary, triadic, tetradic) with when-to-use, watch-outs, and HSL examples.
- `references/scales-and-models.md` — generating 10-step scales in HSL and OKLCH; choosing between RGB, HSL, HSB, OKLCH, LCH, CMYK; programmatic palette generators.
- `references/wcag-contrast.md` — WCAG 2.1 contrast ratios, the "minimum AA shade" workflow, scrims, focus rings, dark mode flipping.
- `references/common-mistakes.md` — the Flux mistake list with concrete before/after fixes.
