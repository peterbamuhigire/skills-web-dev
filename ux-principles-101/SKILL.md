---
name: ux-principles-101
description: 101 actionable UX principles covering accessibility (WCAG), controls,
  forms, navigation, search, empty states, onboarding, error recovery, progress indicators,
  copywriting, user journeys, and ethical design. Cross-cutting skill — load alongside...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# UX Principles 101
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- 101 actionable UX principles covering accessibility (WCAG), controls, forms, navigation, search, empty states, onboarding, error recovery, progress indicators, copywriting, user journeys, and ethical design. Cross-cutting skill — load alongside...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ux-principles-101` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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
| UX quality | 101 UX principles checklist run | Markdown doc covering applicable principles per surface (accessibility, controls, forms, navigation) | `docs/ux/principles-checklist.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
> Cross-cutting skill. Load alongside any platform or domain skill to enforce UX quality.

## Plugins (Load Alongside)

| Skill | When to combine |
|---|---|
| `webapp-gui-design` | Web app UI implementation |
| `jetpack-compose-ui` | Android Compose screens |
| `form-ux-design` | Deep form patterns |
| `pos-sales-ui-design` | Point-of-sale interfaces |
| `healthcare-ui-design` | Clinical-grade UI |
| `ux-psychology` | Cognitive science foundations |
| `laws-of-ux` | Named-law quick reference (Fitts, Hick, Miller) |
| `interaction-design-patterns` | Tidwell's 45+ structural patterns |
| `web-usability-krug` | Krug's usability laws and billboard design |
| `lean-ux-validation` | Hypothesis-driven validation |
| `vibe-security-skill` | Security baseline (mandatory for web apps) |

---

## 1. Accessibility (WCAG Essentials)

Sources: Grant Ch.59-69, Maioli Ch.6 (POUR + Universal Design)

### Contrast & Colour

- **4.5:1 minimum** contrast ratio (WCAG 2.0 §1.4.3); aim for **7:1** on mobile
- **3:1 minimum** for large text (18px+) and non-text UI components
- Never use colour alone to convey information — 8% of men are colour-blind
- Colour is a great *secondary* indicator alongside text, icons, or patterns

### Keyboard & Focus

- Logical **tab order** via `tabindex`; test by tabbing through every form and menu
- **Skip-to-content** link at page top (CSS-hidden for sighted users)
- Never remove `:focus` outlines — restyle them if needed, but keep them visible
- Allow **ESC** to close modals, drawers, and overlays

### Zoom & Responsive

- Never disable device zoom (`maximum-scale=1.0, user-scalable=no` is forbidden)
- Support **200% zoom** without horizontal scroll or content loss
- Mobile-first responsive design is a given, not optional

### Labels & Icons

- Every icon **must** have a visible text label — icons alone cause frustration
- Use consistent icon style across the product; never mix disparate sets
- Don't embed text inside icons (breaks translation and screen readers)
- Don't use obsolete metaphors (floppy disk for "save", rotary phone)

### Touch Targets

- Finger-sized: max **5 tappable items** across screen width
- **2mm padding** between adjacent touch targets to prevent mis-taps
- Use native control elements (already the right size)

### Links & Copy

- Links must make sense **out of context** ("Download report" not "click here")
- Underline links or style them clearly — hover-only fails on touch screens
- Don't make non-links look like links or non-buttons look like buttons

### POUR Principles (Maioli)

- **Perceivable:** Content available to all senses (alt text, captions, contrast)
- **Operable:** Keyboard navigable, sufficient time, no seizure triggers
- **Understandable:** Readable, predictable, input assistance
- **Robust:** Works with current and future assistive technologies

### Universal Design — 7 Principles (Maioli)

1. Equitable use
2. Flexibility in use
3. Simple and intuitive
4. Perceptible information
5. Tolerance for error
6. Low physical effort
7. Size and space for approach and use

### Quick Accessibility Checklist (Maioli)

- Validate HTML for semantic correctness
- Test keyboard-only navigation end to end
- Use SVG over icon fonts (better screen-reader support)
- Maintain heading hierarchy (h1 > h2 > h3, no skipping)
- Avoid justified text (uneven word spacing harms dyslexic readers)
- Respect `prefers-reduced-motion` for all animations
- Don't auto-play audio or video

---

## Additional Guidance

Extended guidance for `ux-principles-101` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Controls & Buttons`
- `3. Forms & Input`
- `4. Navigation & Content`
- `5. Search UX`
- `6. Empty States & Onboarding`
- `7. Progress & Feedback`
- `8. Error Recovery`
- `9. User Journeys`
- `10. Copywriting for UI`
- `11. Ethical Design`
- `12. Heuristic Evaluation Quick Reference`
- `13. UX Quality Checklist`
- Additional deep-dive sections continue in the reference file.