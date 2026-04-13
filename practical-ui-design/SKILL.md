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

## Additional Guidance

Extended guidance for `practical-ui-design` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Typography Rules`
- `3. Layout and Spacing`
- `4. Copywriting for UI`
- `5. Buttons`
- `6. Forms (Quick Reference)`
- `7. Component Patterns (Kuleszo)`
- `8. Dark Mode Rules`
- `9. Anti-Patterns`
- `10. Design Checklist`
