---
name: design-audit
description: Comprehensive UI/UX quality audit covering visual hierarchy, accessibility,
  AI slop detection, typography, colour, layout, interaction states, responsive behaviour,
  performance, and microcopy. Produces severity-rated findings with actionable...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Design Audit Skill

<!-- dual-compat-start -->
## Use When

- Comprehensive UI/UX quality audit covering visual hierarchy, accessibility, AI slop detection, typography, colour, layout, interaction states, responsive behaviour, performance, and microcopy. Produces severity-rated findings with actionable...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `design-audit` or would be better handled by a more specific companion skill.
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
| UX quality | Design audit report | Markdown doc covering visual hierarchy, typography, spacing, colour, and accessibility findings | `docs/ux/design-audit-checkout.md` |
| UX quality | Accessibility pass report | Markdown doc summarising WCAG conformance | `docs/ux/a11y-checkout.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Plugins (Load Alongside)

| Companion Skill | When to Load |
|---|---|
| `ai-slop-prevention` | Detailed AI anti-pattern reference |
| `practical-ui-design` | Visual system rules to audit against |
| `motion-design` | Animation quality standards |
| `ux-writing` | Microcopy quality standards |
| `responsive-design` | Responsive behaviour standards |
| `frontend-performance` | Performance measurement targets |
| `laws-of-ux` | UX law compliance |
| `ux-principles-101` | Accessibility and usability principles |

---

## 1. Audit Process

### Step 1: Gather Context

Before auditing, understand:

- **Who are the users?** (age, tech literacy, use context)
- **What's the purpose?** (task completion, information display, commerce)
- **What platform?** (web, Android, iOS, cross-platform)
- **What design system?** (if any — tokens, components, patterns)
- **What's the brand personality?** (professional, playful, clinical)

### Step 2: Systematic Scan

Evaluate across all 10 dimensions (Section 2). Score each dimension.

### Step 3: Produce Report

Follow the report structure (Section 3). Prioritise findings by severity.

---

## 2. The 10 Audit Dimensions

### Dimension 1: AI Slop Detection

**The first check.** Does this interface look machine-generated?

| Check | Look For |
|---|---|
| Typography | Inter/Roboto defaults, no hierarchy, title case everywhere |
| Colour | Cyan-on-dark, purple gradients, gradient text, pure black/white |
| Layout | Everything in cards, identical card grids, everything centred |
| Effects | Glassmorphism, decorative blur, glow borders, SVG blobs |
| Motion | Bounce/elastic easing, animation fatigue |
| Content | "Submit" buttons, "Loading..." text, corporate AI jargon |

**Verdict**: PASS (distinctive, intentional) / BORDERLINE (some generic choices) / FAIL (immediately recognisable as AI-generated)

### Dimension 2: Visual Hierarchy

| Check | Standard |
|---|---|
| Squint test | Most important element visible when blurred |
| Size hierarchy | Clear primary > secondary > tertiary sizing |
| Weight contrast | Bold for headings, regular for body (not medium/light) |
| Colour emphasis | Brand colour reserved for interactive elements |
| Whitespace | Generous spacing separates sections; tight spacing groups related items |
| Focal point | Each screen has one clear entry point for the eye |

### Dimension 3: Accessibility

| Check | Standard | Severity |
|---|---|---|
| Text contrast | >= 4.5:1 (body), >= 3:1 (large text) | Critical |
| UI component contrast | >= 3:1 against background | Critical |
| Touch targets | >= 44x44px (48x48px preferred) | Critical |
| Keyboard navigation | Logical tab order, visible focus ring | Critical |
| Screen reader | Semantic HTML, ARIA labels, meaningful alt text | Critical |
| Colour independence | Never colour alone as indicator | High |
| Zoom support | Usable at 200% zoom | High |
| Reduced motion | `prefers-reduced-motion` respected | High |
| Focus management | Focus moves logically after interactions | Medium |

### Dimension 4: Typography

| Check | Standard |
|---|---|
| Font choice | Intentional, not default (matches brand personality) |
| Type scale | Consistent scale (Major Third or project-appropriate) |
| Body size | >= 16px (18px preferred) |
| Line height | 1.5-2.0 for body; decreasing for larger sizes |
| Line length | 40-80 characters (66 ideal) |
| Weight usage | Regular + Bold only (avoid thin/light/medium) |
| Alignment | Left-aligned body text (no justified, centre only for 1-2 lines) |
| Letter spacing | Decreased for large display text |

### Dimension 5: Colour

| Check | Standard |
|---|---|
| Tinted neutrals | No pure grey (#808080), black (#000), or white (#fff) |
| Palette structure | Primary + neutral + semantic + surface tokens |
| 60-30-10 rule | 60% neutral, 30% secondary, 10% accent |
| Semantic colour | Red=error, amber=warning, green=success, blue=info |
| Dark mode | Independently designed (not inverted), desaturated brand colours |
| Brand colour usage | Reserved for interactive elements only |
| System colour pairing | Always paired with icon (not colour alone) |

### Dimension 6: Layout & Spacing

| Check | Standard |
|---|---|
| Spacing system | Consistent token scale (4pt or 8pt based) |
| Spacing variation | Rhythm through varied spacing (not uniform everywhere) |
| Alignment consistency | Few alignment axes per screen |
| Content max-width | Text constrained to 40-80 character line length |
| Grid usage | Appropriate tool: Flexbox for 1D, Grid for 2D |
| Responsive | Mobile-first, content-driven breakpoints |
| Container queries | Used for reusable components |

### Dimension 7: Interaction States

Every interactive element must have these states defined:

| State | Visual Treatment |
|---|---|
| Default | Base appearance |
| Hover | Subtle shift (colour, shadow, or position) |
| Focus | Visible ring (`focus-visible` for keyboard only) |
| Active/Pressed | Distinct from hover (scale or colour change) |
| Disabled | Reduced opacity OR removed with explanation |
| Loading | Inline indicator with specific status text |
| Error | Red styling + icon + descriptive message |
| Success | Green styling + icon + confirmation message |

### Dimension 8: Motion & Animation

| Check | Standard |
|---|---|
| Purpose | Every animation serves a function (feedback, guide, connect) |
| Timing | Follows 100/300/500 rule for category |
| Easing | Exponential curves (ease-out-quart/quint), no bounce/elastic |
| GPU-only | Transform + opacity only (no layout property animation) |
| Reduced motion | `prefers-reduced-motion` alternative provided |
| Performance | 60fps on mid-range devices |
| Restraint | Not everything animates (no animation fatigue) |

### Dimension 9: Content & Microcopy

| Check | Standard |
|---|---|
| Button labels | Verb + noun (no "Submit", "OK", "Yes/No") |
| Error messages | What happened + why + how to fix |
| Empty states | Acknowledge + explain value + action |
| Loading text | Names the operation ("Saving your draft...") |
| Link text | Descriptive (no "Click here", "Learn more") |
| Vocabulary | Consistent terms throughout |
| Tone | Matches moment (serious for errors, warm for onboarding) |

### Dimension 10: Performance

| Check | Standard |
|---|---|
| LCP | < 2.5s on mid-range mobile |
| INP | < 200ms |
| CLS | < 0.1 |
| Initial load | < 650 KB compressed total |
| Images | WebP/AVIF, srcset, lazy loading, explicit dimensions |
| Fonts | `font-display: swap`, preloaded, subset |

---

## 3. Report Structure

### Header

```
# Design Audit Report
**Date:** [Date]
**Auditor:** Claude (AI-assisted)
**Target:** [Screen/feature name]
**Platform:** [Web/Android/iOS]
**Context:** [Brief description of purpose and users]
```

### AI Slop Verdict

```
## AI Slop Verdict: [PASS / BORDERLINE / FAIL]
[1-2 sentence summary of why]
```

### Executive Summary

```
## Executive Summary
- **Overall Score:** [X/100]
- **Critical Issues:** [count]
- **High Issues:** [count]
- **Medium Issues:** [count]
- **Low Issues:** [count]
- **What's Working:** [1-3 bullet points of strengths]
- **Top Priority:** [The single most impactful fix]
```

### Findings by Severity

```
## Critical (Must Fix Before Ship)
### [Finding Title]
- **Dimension:** [Which of the 10 dimensions]
- **Location:** [Where in the interface]
- **Issue:** [What's wrong]
- **Impact:** [Who is affected and how]
- **Fix:** [Specific actionable fix]
- **Standard:** [Which standard it violates]

## High (Fix Within Sprint)
[Same structure]

## Medium (Fix Within Quarter)
[Same structure]

## Low (Nice to Have)
[Same structure]
```

### Severity Definitions

| Severity | Meaning |
|---|---|
| **Critical** | Blocks users, fails accessibility law, data loss risk |
| **High** | Significant UX degradation, frequent user confusion |
| **Medium** | Noticeable quality issue, occasional friction |
| **Low** | Minor polish, edge case, aesthetic preference |

### Positive Findings

```
## What's Working Well
[List patterns and decisions that are effective and should be maintained]
```

### Recommendations

```
## Prioritised Recommendations
1. [Highest impact fix] — addresses [N] critical/high issues
2. [Second priority] — addresses [N] issues
3. [Third priority] — addresses [N] issues
```

---

## 4. Scoring Guide

| Score | Meaning |
|---|---|
| 90-100 | Production-ready. Minor polish only. |
| 75-89 | Good foundation. Fix high-priority issues before shipping. |
| 60-74 | Significant issues. Needs focused remediation sprint. |
| 40-59 | Major redesign areas. Multiple dimensions failing. |
| < 40 | Fundamental problems. Start with structure and hierarchy. |

### Dimension Weights

| Dimension | Weight | Rationale |
|---|---|---|
| Accessibility | 20% | Legal requirement, blocks users |
| Visual Hierarchy | 15% | Foundation of usability |
| Interaction States | 12% | Functional completeness |
| Content & Microcopy | 12% | User comprehension |
| Typography | 10% | Readability |
| Colour | 8% | Communication and mood |
| Layout & Spacing | 8% | Structure and scannability |
| Performance | 6% | Speed and responsiveness |
| Motion | 5% | Polish and feedback |
| AI Slop | 4% | Distinctiveness (binary pass/fail) |

---

## 5. Quick Audit Checklist (10-Minute Version)

For rapid checks when a full audit isn't needed:

- [ ] **AI Slop**: Does this look machine-generated? (fonts, colours, layout)
- [ ] **Hierarchy**: Squint test passes — primary element is clear
- [ ] **Contrast**: Body text >= 4.5:1, UI components >= 3:1
- [ ] **Touch targets**: >= 44x44px on touch devices
- [ ] **Keyboard**: Tab through the page — focus visible, logical order
- [ ] **States**: Hover, focus, active, error, loading all defined
- [ ] **Buttons**: All use verb + noun labels
- [ ] **Errors**: All show what, why, how to fix
- [ ] **Empty states**: No blank screens
- [ ] **Responsive**: Works on mobile without horizontal scroll
- [ ] **Performance**: Loads in < 3s on mobile
- [ ] **Motion**: No bounce easing, reduced motion handled

---

*Sources: Impeccable audit and critique skills (Bakaus, 2025); WCAG 2.2 AA; Nielsen Norman Group heuristic evaluation framework.*
