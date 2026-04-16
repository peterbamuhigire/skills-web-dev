---
name: form-ux-design
description: Cross-platform form UX/UI patterns for web (Bootstrap 5/Tabler), Android
  (Jetpack Compose), and iOS (SwiftUI). Covers field anatomy, validation, error states,
  multi-step wizards, accessibility, touch-friendly inputs, and submission workflows.
  Use...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Form UX/UI Design

<!-- dual-compat-start -->
## Use When

- Cross-platform form UX/UI patterns for web (Bootstrap 5/Tabler), Android (Jetpack Compose), and iOS (SwiftUI). Covers field anatomy, validation, error states, multi-step wizards, accessibility, touch-friendly inputs, and submission workflows. Use...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `form-ux-design` or would be better handled by a more specific companion skill.
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
| UX quality | Form UX audit | Markdown doc covering field grouping, validation, error states, and submit affordances per platform | `docs/ux/form-audit-checkout.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Cross-cutting form design patterns for **web** (Bootstrap 5 / Tabler + PHP), **Android** (Jetpack Compose + Material 3), and **iOS** (SwiftUI). Apply this skill whenever you build, review, or refactor any form.

## Quick Reference

| Topic | Reference File | Scope |
|-------|---------------|-------|
| Web form components | `references/web-form-components.md` | Bootstrap/Tabler inputs, selects, checkboxes, radios, switches, textareas, file uploads |
| Android form components | `references/android-form-components.md` | Compose TextField, ExposedDropdownMenu, Checkbox, RadioButton, Switch, Slider |
| iOS form components | `references/ios-form-components.md` | SwiftUI TextField, Picker, Toggle, DatePicker, Stepper |
| Validation patterns | `references/form-validation.md` | Validation logic, error states, async validation, submission workflows (all platforms) |
| Accessibility | `references/form-accessibility.md` | WCAG form requirements, ARIA, screen readers, keyboard nav, touch targets (all platforms) |

---

## 1. Form Design Philosophy

Five rules that govern every form decision:

**Three dimensions of every form** (most to least influential):
1. **Words** — what you say and how you say it. Users can work around bad layout; they cannot work around bad wording.
2. **Layout** — how things are visually presented
3. **Flow** — how the user moves through the form

**A form is a conversation.** Order, tone, appropriateness, and effort all matter to humans. Design accordingly.

**"Start with nothing. Then only add what's needed to communicate with the user."** — Every pixel must serve a purpose. Be ruthless.

**Collect only what you need.** Every additional question reduces completion rate and data quality. Never add questions "just in case."

### Rule 1 — Labels Above Inputs (ALWAYS)

Labels above inputs on ALL screen sizes. NEVER use placeholder text as the label — it disappears on focus, makes fields look pre-filled, is not reliably announced by screen readers, and corrupts data when left in the field. NEVER use float labels — they have all the same problems as placeholder-as-label plus broken animation on long labels.

Mark **optional** fields with "(optional)" appended to the label. Do NOT mark required fields with red asterisks — they are abstract, visually noisy, inaccessible, and often labelled with jargon like "mandatory."

### Rule 2 -- Single Column by Default

One column for forms. Two-column layout only for naturally paired fields (first name / last name, city / state). Mobile is always single column regardless.

### Rule 3 -- Progressive Disclosure

Show only what is needed now. Reveal advanced fields conditionally (toggles, dependency rules). Break long forms (more than 7 fields) into logical steps.

### Rule 4 -- Instant Feedback

Validate on blur (not on keystroke). Show errors inline below the field. Display success indicators (green border or checkmark) for completed fields that passed validation.

**Error message must do three things** (Enders):
1. Convey that an error has occurred
2. State exactly what the error is and where
3. Tell the user how to fix it — in plain, non-accusatory language

Never use vague messages ("Invalid input"). Never use the word "error" alone — be specific. For long forms: provide an error summary at the top of the page with anchor links to each error. Pair all error colours with an icon — never rely on colour alone.

### Rule 5 -- Minimal Friction

Use smart defaults, autocomplete attributes, and auto-formatting (phone, currency). Reduce keystrokes. Never ask for information you already have or can derive.

---

## Additional Guidance

Extended guidance for `form-ux-design` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Field Anatomy`
- `3. Field States`
- `4. Essential Code Examples`
- `5. Multi-Step Form Pattern (Wizard)`
- `5b. Gateway Screen (Before Long Forms)`
- `5c. Confirmation Screen (After Submission)`
- `5d. Specific Field Rules (from Enders)`
- `6. Form Submission Workflow`
- `7. Touch Target and Spacing Rules`
- `8. Form DOs and DON'Ts`
- `9. Common Form Types -- Quick Patterns`
- `10. Integration with Existing Skills`
