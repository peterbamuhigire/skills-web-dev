# The Complete Guide for Choosing Colors — Flux Academy

Reference notes from the Flux Academy guide by Ran Segall and team.

## 1. Color theory fundamentals

### Hue, tint, shade, tone (book)

- **Hue** — the pure color (position on the color wheel, 0-360 degrees in HSL/HSB).
- **Tint** — hue + white. Lighter, softer, more pastel. Raise lightness toward 100%.
- **Shade** — hue + black. Darker, heavier, more grounded. Drop lightness toward 0%.
- **Tone** — hue + gray. Reduce saturation while keeping lightness mid-range. Useful for muted, sophisticated palettes.

| Operation | HSL move | Example: base `hsl(265, 70%, 55%)` |
|-----------|----------|------------------------------------|
| Pure hue  | keep S, L mid (~50-60%) | `hsl(265, 70%, 55%)` |
| Tint      | raise L toward 90-95%, optionally drop S a touch | `hsl(265, 60%, 92%)` |
| Shade     | drop L toward 10-20%, keep S | `hsl(265, 70%, 18%)` |
| Tone      | drop S toward 15-30%, keep L | `hsl(265, 20%, 55%)` |

### Color models (agent reference)

The book itself does not discuss RGB/HSL/HSB/LCH/OKLCH. For coding work:

- **HEX / RGB** — what the brand guide will give you. Use as ground truth.
- **HSL** — best for hand-tuning shades and tints because Lightness is intuitive. Caveat: equal-L colors do not look equally bright (yellow at L=50% looks far brighter than blue at L=50%).
- **HSB / HSV** — designer-friendly (matches Figma's color picker). B=brightness != L=lightness.
- **OKLCH** (CSS Color 4) — perceptually uniform. Preferred for generating shade scales programmatically because equal-L truly looks equal-bright. `oklch(L% C H)` where L is 0-100%, C is chroma (~0-0.4), H is hue 0-360. Example: `oklch(60% 0.18 295)` for a vivid purple.
- **LCH** — older perceptual model, similar use case.

For new projects targeting modern browsers, generate scales in OKLCH then export hex.

### Color psychology (book)

The book is explicit that **psychological reactions are situational and culture-bound**. Red can read as passion/love or as danger/warning depending on context. Takeaway:

- Do not pick a hue from a generic "blue = trust" cheat sheet. Pick it against the brief.
- The same hue can do opposite jobs depending on saturation and the surrounding palette: a desaturated dusty red is "warm and grounded"; a saturated fire-engine red is "alert".

| Hue family | Common positive read | Common negative / context-flip |
|---|---|---|
| Red | passion, love, urgency, appetite | danger, anger, warning |
| Orange | warmth, energy, friendly, playful | cheap, garish at full saturation |
| Yellow | optimism, attention, joy | caution, anxiety, hard to read on white |
| Green | nature, growth, health, money, "go" | sickness (yellow-green), boredom |
| Blue | trust, calm, professional, stability | cold, corporate, sad |
| Purple | luxury, creativity, spirituality, premium | artificial, juvenile (lavender) |
| Pink | playful, romantic, modern feminine | infantile if overused |
| Black | luxury, authority, modernity | death, oppression |
| White | clean, simple, premium minimal | sterile, empty |
| Gray | neutral, balanced, sophisticated | dull, corporate-default |

Rule of thumb: **interpret the hue inside the brief, not in the abstract.**

---

## 2. Color harmonies (book)

### Monochromatic
A single hue at multiple tints/shades/tones. Same H in HSL; vary S and L.
- **Use when:** brand needs to feel calm, focused, premium, minimal; when you want zero risk of color clash; when imagery (photos, illustrations) carries the visual weight.
- **Watch out:** can feel flat without strong typography or imagery contrast.

### Analogous
Hues that sit next to each other on the wheel — typically within ~30 degrees. Three colors is standard.
- **Use when:** harmony and warmth without monotony; nature/lifestyle/wellness/food brands.
- **Watch out:** low contrast between the colors — pick one to dominate (60%) and the others as secondary/accent. Always test text legibility because adjacent hues do not separate type from background well.

### Complementary
Two hues directly opposite on the wheel (180 degrees apart). Works where high contrast is required.
- **Use when:** strong CTAs, sports/energetic brands, posters, anywhere you need a single accent to pop off the dominant color.
- **Watch out:** pure complementaries vibrate uncomfortably at high saturation when adjacent. Desaturate one side, or separate them with neutrals/whitespace.

### Split-complementary
Base hue + the two hues adjacent to its complement (instead of the complement itself). Same logic as complementary but softer because the accent has two notes.
- **Use when:** you want complementary contrast but with less visual aggression. Good default for most websites that need a punchy accent.

### Triadic
Three hues evenly spaced around the wheel (120 degrees apart). Red/yellow/blue and the secondary set orange/green/purple.
- **Use when:** playful, creative, kid-friendly, bold editorial. Good for illustration-heavy sites.
- **Watch out:** all three at full saturation is overwhelming. Pick one dominant; mute the other two or use them only as small accents.

### Tetradic / Square / Rectangle
Four hues arranged as a rectangle or square on the wheel. Two complementary pairs.
- **Use when:** rich, varied palettes — entertainment, kids, fashion, festivals.
- **Watch out:** hardest to balance. Pick one dominant, one supporting, two accents. Otherwise it reads as chaotic.

### Decision shortcut

| Brief signal | Default harmony |
|---|---|
| Premium / minimal / SaaS | Monochromatic, or analogous + 1 neutral |
| Calm, organic, wellness | Analogous |
| Punchy CTA, conversion-focused | Split-complementary or complementary |
| Playful, creative agency | Triadic |
| Editorial / lifestyle / multi-section magazine | Tetradic with strong neutrals |

---

## 3. The book's process for choosing colors

### Step 1 — Define the brief

1. **Client has brand guidelines.** Read them thoroughly. Identify exact color codes and forbidden combinations. Look for technical constraints.
2. **Client has no branding.** Bigger challenge. The book warns "free reign can be fun but leaves a lot of room for error." Interview about: what they are trying to achieve, target audience, how they want their website interpreted.

### Step 2 — Ask the four diagnostic questions (book)

1. **What constraints do I have?** (existing palette, technical limits, formats forbidden)
2. **Is this all the guidance I have?** (push for more; check existing materials and how they use color)
3. **What do I want the viewer to feel?** Provoke them? Interest? Calm? Entertain?
4. **What do I want the viewer to do?** Take an action? Read a story? Determines where color is loud (CTA areas) versus quiet (long-form content).

### Step 3 — Pick the primary hue

"All color palettes begin with one single color." Choose from:
- The mood / tone / associations you want the visitor to feel.
- Color psychology, considered situationally.

In the book's worked example, the designer starts from a black-and-white reference photograph (a girl holding balloons) and tints it purple. **Pick imagery first that conveys the mood, then sample / tint a hue that matches that mood, then build the palette around that hue.**

### Step 4 — Decide how many colors and which harmony

Recommended generators:
- **coolors.co** — fast palette generation, lock and shuffle.
- **Canva color generator** — palette from a photo upload.
- **colormind.io** — ML-driven palette suggestions.
- **mycolor.space** — gradient palettes.

### Step 5 — Apply usage ratios (60/30/10)
### Step 6 — Review against brief

---

## 4. Building palettes — structure, ratios, shade counts

### The 60/30/10 rule (book)

> "You use the primary color 60% of the time, the secondary for 30%, and the accent color for only 10%."

A **guideline, not a strict rule**. Purpose: "vary and balance a page" so no single color dominates uncomfortably and no accent is too anemic. 60/30/10 does not have to be exactly three colors — it is a dominance gauge for primary versus accents.

### Recommended palette structure for a website

1. **Background / surface (60%)** — usually a neutral (white, off-white, near-black). Carries body copy area.
2. **Primary brand color (~30%)** — the main hue. Used for headers, hero panels, primary buttons, brand chrome.
3. **Secondary** — supports the primary; could be a darker/lighter version, or the analogous neighbor.
4. **Accent (~10%)** — the punch. Used for CTAs, highlights, badges. Often the complementary or split-complementary color.
5. **Neutrals scale (5-10 grays)** — for borders, text, subtle backgrounds. A tinted gray (gray with a hint of the brand hue) feels more cohesive than pure neutral gray.
6. **Semantic colors** — success (green), warning (amber), error (red), info (blue). Tune them so they sit inside the brand palette.

### Shades per color

- **Brand colors:** generate a 10-step scale (50, 100, 200, ..., 900) like Tailwind. Use OKLCH with a fixed hue, varying L from ~97% down to ~15%, with C peaking around L=50-60%.
- **Neutrals:** also a 10-step scale, hue locked to a slight tint of the brand hue.
- **Accent:** at minimum the base + a hover (slightly darker, e.g. L drop of ~8%) + a disabled (drop S, raise L).

### Concrete example scale (from `hsl(265, 70%, 55%)` purple)

| Token | HSL | Hex (approx) |
|---|---|---|
| purple-50 | hsl(265, 70%, 97%) | #f5f1ff |
| purple-100 | hsl(265, 70%, 92%) | #e5d9ff |
| purple-200 | hsl(265, 70%, 84%) | #cdb3ff |
| purple-300 | hsl(265, 70%, 74%) | #b08aff |
| purple-400 | hsl(265, 70%, 65%) | #9560ff |
| purple-500 | hsl(265, 70%, 55%) | #7a3ee0 (base) |
| purple-600 | hsl(265, 72%, 45%) | #5e22c2 |
| purple-700 | hsl(265, 75%, 35%) | #441a96 |
| purple-800 | hsl(265, 80%, 25%) | #2f126b |
| purple-900 | hsl(265, 85%, 15%) | #1c0944 |

---

## 5. Contrast and accessibility

### What the book says

- "The higher the contrast between two colors, the more each color will stand out from one another."
- Contrast is not just about hue — **tone matters more for legibility**. Two different hues at the same lightness can have terrible contrast.
- "High contrast will mean the text is more legible. Low contrast, and you'll have an abundance of people who couldn't read the message."
- Recommends `colourcontrast.cc`.

### WCAG specifics (agent reference)

- **WCAG 2.1 AA — body text:** 4.5:1.
- **WCAG 2.1 AA — large text (18pt+ or 14pt+ bold):** 3:1.
- **WCAG 2.1 AAA — body text:** 7:1. Recommended for content-heavy sites and anything legal/medical.
- **Non-text UI (icons, focus rings, form borders):** 3:1 against adjacent colors.

### Brand color contrast tradeoffs

The book hints at this when it says "some color combinations are functional but they don't look very appealing. If that is the case, maybe a shade below or above might improve how it's interpreted."

1. **Brand color rarely passes AA on white as body text.** A vivid `hsl(265, 70%, 55%)` purple is around 5:1 on white — borderline. Lime/yellow brand colors usually fail. Solution: never use the raw brand color for body copy. Reserve it for headings, buttons (with white text), and accents. Use a darkened shade (e.g. `purple-700` or `purple-800`) for body-weight brand text on white.
2. **Buttons:** check both background-vs-page contrast and text-on-button contrast.
3. **Text on imagery:** add a scrim — usually `rgba(0,0,0,0.4-0.6)` over photos for white text. Or place text in a solid panel.
4. **Disabled states:** WCAG exempts disabled controls from contrast minimums, but users still need to perceive them. Aim for 3:1.
5. **Color is never the only signal.** Errors must have an icon or label. Links must underline.

### Practical contrast workflow

1. Lock body text color and background early. Verify ratio is ≥4.5:1.
2. Generate the brand scale. Identify which step is the "minimum AA on white" step (usually 600-700) and which is the "AA on dark surface" step (usually 200-300). Document them.
3. Test every button state: default, hover, active, disabled, focused. The focus ring needs 3:1 against both the button and the page.
4. Test in dark mode if relevant — flip the neutrals scale, retest.

---

## 6. Common mistakes the book calls out

1. **Skipping the brief.**
2. **Treating free reign as a gift.**
3. **Ignoring brand guidelines.** "A beautiful website is great, but if it doesn't match the brand guidelines, then it's not very helpful for your client."
4. **Choosing colors that are functional but ugly.** Passing contrast is not enough.
5. **Choosing colors that look great but fail legibility.**
6. **Color that distracts instead of guiding.** The job of color is to support the viewer's action.
7. **Treating 60/30/10 as a rigid rule.**
8. **Building accents first.** "Build the base with simplicity in mind and develop the accents to create the color pops later in the design process."
9. **Color from a generator without context.**
10. **Universal psychology assumptions.**

### The book's review checklist

- **Is it functional?** Text legible, color guides rather than distracts.
- **Is it appealing?** Functional but ugly is still wrong.
- **Is it consistent with brand guidelines?** Hex codes match.
- **Have I answered the brief?**

---

## 7. Specific examples from the book

### The example walkthrough

1. **Reference image.** A black-and-white photograph of a young girl in a dress reaching up toward a cluster of balloons. Mood: dreamy, hopeful, slightly nostalgic, slightly surreal.
2. **Pick a primary hue against the mood.** The designer chooses **purple** — reinforces dream/imagination/premium creativity.
3. **Tint the imagery with the hue.** The same photograph is duotone-tinted purple/violet so the brand color now lives inside the photography. **Bring the photo into the palette** instead of pasting a stock photo onto a purple page.
4. **Build the palette around the primary.**
   - Deep navy-purple background (`~hsl(255-265, 70%, 20%)`) for the hero.
   - Vivid mid-purple (`~hsl(270, 70%, 50%)`) as main brand color.
   - Magenta / hot-pink accent (`~hsl(330, 80%, 55%)`) for buttons, badges, "READ MORE" links, gradient endpoints — split-complementary, used at the 10% slot.
   - Off-white (`~hsl(0, 0%, 98%)`) for content cards and body backgrounds — the 60% surface.
   - Near-black or deep purple-black for body text.
5. **Gradients.** Primary→accent gradients (purple→magenta) on hero panels and CTA tiles, energy without introducing a new color family.
6. **Apply 60/30/10.**

### The reusable algorithm

1. From the brief, pick a **mood word** (dreamy, urgent, calm, playful, premium, technical, organic, luxurious).
2. Identify or generate **hero imagery** that carries that mood.
3. Sample or pick a **primary hue** that reinforces the mood. Set it at moderate saturation (60-75%) and lightness (45-60%) for HSL.
4. Tint the hero imagery toward the primary hue (duotone or color overlay).
5. Choose a harmony (default: split-complementary if you need a CTA accent; monochromatic if minimal/premium).
6. Generate a 10-step scale of the primary + a 10-step neutral scale (slightly tinted toward the primary).
7. Pick one **accent color** at the harmony partner, used only on CTAs, highlights, and gradient endpoints.
8. Apply 60/30/10 — neutrals dominate, primary structures the page, accent points to actions.
9. Verify WCAG AA on every text/background pair. Adjust shade (move up or down on the scale) to fix any failures while keeping the hue.
10. Run the book's review checklist: functional, appealing, brand-consistent, brief-answered.

---

## Quick reference card for AI coding agents

When picking colors for a client website with no brand guide:

1. **Get the brief.** Mood word + viewer action + audience.
2. **Pick the primary hue** in HSL: `hsl(H, 65-75%, 50-60%)`.
3. **Choose harmony:**
   - Minimal/premium → monochromatic
   - Wellness/organic → analogous
   - SaaS with strong CTA → split-complementary
   - Creative/playful → triadic
4. **Generate scales** in OKLCH (or HSL if the project doesn't support OKLCH yet): 10 steps for primary, 10 for neutrals tinted toward the primary, 3-5 for the accent.
5. **Apply 60/30/10:** neutrals 60%, primary 30%, accent 10%.
6. **Verify WCAG AA** (4.5:1 body, 3:1 large/UI). Move shades up/down the scale, never re-pick the hue.
7. **Reserve raw brand color for chrome and CTAs**, never body text on white.
8. **Tint imagery** toward the primary hue when possible.
9. **Build base first, accents last.** No accent in non-CTA areas.
10. **Final review checklist:** functional, appealing, brand-consistent, brief-answered.

When the client has brand guidelines: take the exact hex codes as ground truth, generate the missing scales and neutrals around them, and apply steps 5-10 unchanged.
