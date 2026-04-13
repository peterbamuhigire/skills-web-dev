---
name: jetpack-compose-ui
description: Jetpack Compose UI standards for beautiful, sleek, minimalistic Android
  apps. Enforces Material 3 design, unidirectional data flow, state hoisting, consistent
  theming, smooth animations, and performance patterns. Use when building or reviewing...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Jetpack Compose UI Standards

<!-- dual-compat-start -->
## Use When

- Jetpack Compose UI standards for beautiful, sleek, minimalistic Android apps. Enforces Material 3 design, unidirectional data flow, state hoisting, consistent theming, smooth animations, and performance patterns. Use when building or reviewing...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `jetpack-compose-ui` or would be better handled by a more specific companion skill.
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

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Design Philosophy

**Goal:** Every screen should feel beautiful, sleek, fast, and effortless to use.

### Core Design Principles

1. **Minimalism over decoration** - Remove anything that doesn't serve the user
2. **Consistency over novelty** - Same patterns across every app screen
3. **Whitespace is a feature** - Generous spacing creates visual breathing room
4. **Speed is UX** - If it feels slow, it's broken regardless of how it looks
5. **Content-first hierarchy** - Important information is immediately visible
6. **Touch-friendly targets** - Minimum 48dp for all interactive elements
7. **Adaptive by default** - Every screen MUST work on phones AND tablets
8. **Colour and first impressions** — Users form visual judgments in ~90 seconds; colour is the first impression. The brain processes images 60,000× faster than text — use visuals and colour to communicate primary meaning instantly.

### Enterprise Mobile UX Principles

**Mobile is NOT a scaled-down desktop app.** Design from the ground up for mobile users, not as a replica:

- **Task-oriented design** - Mobile users have specific goals and limited time. Minimize steps/taps to task completion. Focus on one primary action per screen.
- **Value over features** - Include only functionality that delivers genuine user value. Eliminate features that require users to rework on desktop later or provide insufficient context for decisions.
- **UX before UI aesthetics** - Prioritize (1) backend connectivity, (2) offline support, (3) performance, (4) reliability, then UI polish. Users tolerate degraded visuals if the app works and is responsive.
- **Offline-first mentality** - Design flows that work without connectivity. Sync back when online. Users won't use an app that breaks without internet.

### Task Completion Efficiency (Enterprise)

For enterprise mobile apps, measure success by business impact, not UI novelty:

- **Minimize interaction steps** - Every tap/swipe is friction. Test with actual users and eliminate unnecessary screens.
- **Show decision-enabling data** - Always provide enough context (but not overload). E.g., for field agents: appointment count + status, not monthly analysis.
- **Reduce cognitive load** - Make correct actions obvious. Use clear labels, consistent patterns, and logical groupings.
- **Measure KPIs, not vanity metrics** - Define what success looks like (reduced wait times, faster task completion, fewer support requests). Avoid metrics like "time in app" or "login count."

### Visual Standards

| Element              | Standard                                              |
| -------------------- | ----------------------------------------------------- |
| **Corner radius**    | 12-16dp for cards, 8dp for inputs, 24dp for FABs      |
| **Card elevation**   | 0-2dp (subtle shadows, never heavy)                   |
| **Content padding**  | 16dp horizontal, 8-16dp vertical between items        |
| **Screen padding**   | 16dp compact, 24dp medium, 32dp expanded              |
| **Touch targets**    | Minimum 48dp height/width                             |
| **Icon size**        | 24dp standard, 20dp in buttons, 48dp for empty states |
| **Typography scale** | Use Material 3 type scale exclusively                 |

**Colour rules (Paduraru):**
- Never pure black for text: use `Color(0xFF1A1A1A)` or Material 3 `MaterialTheme.colorScheme.onBackground`
- Never pure white on dark backgrounds: use `Color(0xFFF5F5F5)` or Material 3 `MaterialTheme.colorScheme.background`
- Body text line height = font size × 1.6 (e.g., 16sp font → 26sp line height)

**Icon Policy (Required):** Use custom PNG icons with `painterResource(R.drawable.<name>)`. Maintain `PROJECT_ICONS.md` per `android-custom-icons`.

**Report Table Policy (Required):** Any report that can exceed 25 rows must render as a table (see `android-report-tables`).

**Compact Number Formatting (Required):** KPI cards, summary tiles, and stat chips MUST use `CurrencyFormatter.formatStat()` for monetary values. Values >= 1,000,000 display as compact (e.g. "32.45M"). Values < 1,000,000 display as full format ("999,999.00"). Table rows and list items MUST use `CurrencyFormatter.format()` (always full format). Chart axis labels use `CurrencyFormatter.formatCompact()` (e.g. "1.2M", "12.3K").

## Additional Guidance

Extended guidance for `jetpack-compose-ui` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Quick Reference`
- `Core Compose Principles`
- `Composable Function Signature`
- `Screen Architecture Pattern`
- `Responsive & Adaptive Design (MANDATORY)`
- `Theming (Consistent Across Apps)`
- `Essential UI Patterns`
- `Pull-to-Refresh (MANDATORY)`
- `Performance Essentials`
- `Animation Standards`
- `Patterns & Anti-Patterns`
- `Integration with Other Skills`
- Additional deep-dive sections continue in the reference file.
