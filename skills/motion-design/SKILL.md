---
name: motion-design
description: Animation and micro-interaction standards for web, Android, and iOS.
  Covers timing rules (100/300/500), easing curves, GPU-accelerated animation, staggered
  entrances, state transitions, loading states, and mandatory prefers-reduced-motion...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Motion Design Skill
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Animation and micro-interaction standards for web, Android, and iOS. Covers timing rules (100/300/500), easing curves, GPU-accelerated animation, staggered entrances, state transitions, loading states, and mandatory prefers-reduced-motion...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `motion-design` or would be better handled by a more specific companion skill.
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
| UX quality | Motion audit | Markdown doc covering timing rules, easing curves, reduce-motion support, and per-platform parity | `docs/ux/motion-audit-checkout.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Plugins (Load Alongside)

| Companion Skill | When to Load |
|---|---|
| `practical-ui-design` | Visual system (colour, type, spacing) |
| `jetpack-compose-ui` | Android Compose animation APIs |
| `swiftui-design` | SwiftUI animation/transition APIs |
| `webapp-gui-design` | Web app CSS/JS animation |
| `ai-slop-prevention` | Validate animations aren't AI slop |
| `frontend-performance` | Measure animation frame rates |

---

## 1. Duration Rules (The 100/300/500 Rule)

| Category | Duration | Use For |
|---|---|---|
| **Feedback** | 100-150ms | Button press, toggle, checkbox, hover |
| **State change** | 200-300ms | Accordion, tab switch, dropdown, modal appear |
| **Layout shift** | 300-500ms | Page transition, panel expand, reorder |
| **Entrance** | 500-800ms | Hero content, first-time reveal, onboarding |

### Exit Animations

Exit duration = **~75% of enter duration**. Users care less about things leaving than arriving.

### Key Principles

- Anything under 100ms feels instant (no animation needed)
- Anything over 400ms feels slow for micro-interactions
- Total staggered sequence should not exceed 800ms
- **80ms threshold**: if an operation takes < 80ms, skip the loading animation entirely
- Treat timing as a scale: derive related delays and durations from a base value, then cap the total sequence so the interface still feels responsive.

---

## 2. Easing Curves

### Recommended Curves

| Curve | CSS Value | When to Use |
|---|---|---|
| **ease-out-quart** | `cubic-bezier(0.25, 1, 0.5, 1)` | Default for most entrances and micro-interactions |
| **ease-out-quint** | `cubic-bezier(0.22, 1, 0.36, 1)` | Snappy feedback (toggles, checkboxes) |
| **ease-out-expo** | `cubic-bezier(0.16, 1, 0.3, 1)` | Dramatic entrances, hero content |
| **ease-in-quart** | `cubic-bezier(0.5, 0, 0.75, 0)` | Exit animations |
| **ease-in-out** | `cubic-bezier(0.4, 0, 0.2, 1)` | Toggles, state changes, position swaps |

### NEVER Use

| Curve | Why |
|---|---|
| `bounce` / `elastic` | Dated, tacky — the #1 AI animation fingerprint |
| `linear` | Mechanical, unnatural (except for continuous rotation) |
| `ease` (CSS default) | Too gentle, feels mushy |
| Custom springs with visible oscillation | Distracting, unprofessional |

---

## 3. What to Animate (GPU-Accelerated Only)

### ONLY Animate

| Property | Use For |
|---|---|
| `transform: translate()` | Position changes, slide in/out |
| `transform: scale()` | Grow/shrink, emphasis |
| `transform: rotate()` | Spin, flip, tilt |
| `opacity` | Fade in/out, reveal/hide |

These run on the GPU compositor — no layout recalculation, no jank.

### NEVER Animate

| Property | Why |
|---|---|
| `width`, `height` | Triggers layout recalculation every frame |
| `top`, `left`, `right`, `bottom` | Triggers layout recalculation every frame |
| `margin`, `padding` | Triggers layout recalculation every frame |
| `border-width`, `border-radius` | Triggers paint every frame |
| `font-size` | Triggers layout + paint + composite |
| `box-shadow` (animated) | Expensive paint operation |

**Alternative**: Use `transform: scale()` instead of animating width/height. Use `transform: translate()` instead of animating position.

---

## 4. Animation Categories

### 4.1 Entrance Animations

- Fade in: `opacity: 0 → 1` (200-300ms, ease-out-quart)
- Slide up: `translate(0, 16px) → translate(0, 0)` + fade (300-500ms)
- Scale in: `scale(0.95) → scale(1)` + fade (200-300ms)
- **Stagger children**: 50-80ms delay between items, cap total at 800ms

### 4.2 Micro-Interactions (Feedback)

- Button press: `scale(0.97)` on `:active` (100ms, ease-out-quint)
- Toggle: position swap (150ms, ease-in-out)
- Checkbox: check mark draw (200ms, ease-out-quart)
- Hover: subtle lift or colour shift (150ms, ease-out)

### 4.3 State Transitions

- Tab switch: cross-fade content (200ms)
- Accordion: height with `max-height` or CSS grid trick (250-300ms)
- Modal appear: backdrop fade + content scale from 0.95 (250ms, ease-out-quart)
- Modal exit: content fade + scale to 0.97 (180ms, ease-in-quart)

### 4.4 Navigation & Flow

- Page transition: fade + subtle slide in direction of navigation (300ms)
- Shared element: morph position/size between views (400ms, ease-out-expo)
- Back navigation: reverse the enter animation direction

### 4.5 Loading & Feedback

- Skeleton screens: shimmer gradient animation (1.5s, infinite, ease-in-out)
- Progress bars: width transition (300ms, ease-out)
- Success: check mark draw + subtle scale bounce to 1.0 (400ms)
- Error: horizontal shake `translate(-4px) → translate(4px)` x2 (300ms)

### 4.6 Delight Moments

- Celebration: confetti, particle burst (use sparingly)
- Achievement: scale up + glow + settle (500ms)
- Easter eggs: only after repeated interaction, never blocking

---

## 5. Staggered Animations (CSS)

```css
/* Set index via inline style or CSS custom property */
.stagger-item {
  --i: 0; /* set per element: style="--i: 0", style="--i: 1", etc. */
  animation: fadeSlideUp 300ms ease-out both;
  animation-delay: calc(var(--i) * 60ms);
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Rules:**
- 40-80ms between items (60ms is sweet spot)
- Cap total stagger time at 800ms (for 10+ items, reduce per-item delay)
- First item appears immediately (no delay)
- Formula: `delay = min(index * 60ms, 480ms)` keeps long lists from becoming slow.

---

## 6. Reduced Motion (MANDATORY)

**35%+ of adults over 40 experience vestibular sensitivity.** This is not optional.

### CSS Implementation

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### What to Do Instead

| Normal | Reduced Motion |
|---|---|
| Slide + fade entrance | Instant appear (or very fast fade, 100ms) |
| Position transitions | Instant position change |
| Parallax scrolling | Static positioning |
| Auto-playing video/animation | Paused with play button |
| Continuous rotation/pulse | Static state |

### What to Keep

- Opacity transitions (under 200ms) — generally safe
- Colour transitions — no motion involved
- Essential progress indicators — use non-motion alternatives (progress bar fill)

---

## 7. Perceived Performance

### Preemptive Start

Start animations before data arrives. Show optimistic UI immediately, update when data loads.

### Early Visual Completion

Animate to ~90% quickly, slow the last 10%. Progress feels faster even if total time is the same.

### Active vs Passive Waiting

- **Active**: User-initiated (button click → action). Keep under 400ms or show inline progress.
- **Passive**: System-initiated (page load, sync). Use skeleton screens, not spinners.

### Optimistic Updates

Apply state changes immediately in the UI. Roll back only if the server rejects.

```
User taps "Like" → Heart fills instantly → API call fires in background
                                          → If fails, revert heart + show error
```

---

## 8. Platform-Specific Notes

### Web (CSS/JS)

- Prefer CSS animations/transitions over JS when possible
- Use `will-change` sparingly (only on elements about to animate)
- Use Web Animations API for complex JS-driven sequences
- Use `requestAnimationFrame` for frame-synced updates
- For JS-driven motion, calculate from elapsed time, not assumed frame count; compare decimals with a small tolerance when snapping to an end state.

### Android (Jetpack Compose)

- Use `animateFloatAsState`, `animateContentSize`, `AnimatedVisibility`
- `Animatable` for interruptible animations
- `spring()` for physics-based (use stiffness, not bounce)
- Check `LocalReducedMotion.current` (Compose 1.7+)

### iOS (SwiftUI)

- Use `.animation()` modifier or `withAnimation {}`
- `.spring(duration:bounce:)` — keep bounce at 0 for professional feel
- `matchedGeometryEffect` for shared element transitions
- Check `UIAccessibility.isReduceMotionEnabled`

---

## 9. Quality Checklist

Before shipping animations:

- [ ] All animations use transform + opacity only (no layout properties)
- [ ] Timing follows the 100/300/500 rule for the animation category
- [ ] Easing uses exponential curves (ease-out-quart/quint), not bounce/elastic
- [ ] Stagger delays are 40-80ms with total capped at 800ms
- [ ] `prefers-reduced-motion` provides meaningful alternative
- [ ] Animations run at 60fps on mid-range devices
- [ ] Exit animations are ~75% of enter duration
- [ ] No animation fatigue (not everything animates)
- [ ] Animations serve purpose (guide attention, show relationships, provide feedback)
- [ ] Tested on real devices (not just DevTools)

---

*Sources: Impeccable motion-design reference (Bakaus, 2025); Material Design Motion guidelines; Apple Human Interface Guidelines — Motion.*
