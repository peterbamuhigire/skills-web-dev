---
name: ux-content-strategy
description: Use when planning, governing, or upgrading product content as a system - voice charts, content-first design, UI text patterns, form completion gates, error taxonomy, content measurement, decision communication, lifecycle narrative, and content operations. Higher-level orchestration above tactical microcopy and form mechanics.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# UX Content Strategy
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Defining or refreshing product voice, tone-shift rules, and content principles for a product or feature family.
- Designing a flow where content drives layout (onboarding, recovery, churn-risk, premium upgrades, complex forms).
- Establishing a content measurement framework tied to completion, comprehension, error reduction, conversion, trust, and support deflection.
- Communicating a content decision to skeptical stakeholders or capturing agreement after debate.
- Planning a 30 / 60 / 90-day content operation across multiple surfaces, locales, or teams.

## Do Not Use When

- The task is a single string of microcopy with an established voice and clear pattern - use `ux-writing` directly.
- The task is form layout, field grouping, input types, or validation mechanics - use `form-ux-design` directly.
- The request is a one-line stakeholder reply that needs no decision rationale capture.

## Required Inputs

- Product purpose, audience segments, and the user state(s) the content must serve (first use, mastery, error, churn-risk, win-back).
- Existing voice or content guidance, brand constraints, regulatory or legal copy requirements, locale list.
- The surface(s) involved (screen, form, email, notification, system message) and the metric the content is expected to move.
- Stakeholder map: who decides, who reviews, who has veto.

## Workflow

- Read this `SKILL.md` first. Pull only the references you need for the current decision.
- Decide whether the task is **strategic** (voice, measurement, lifecycle) or **tactical** (a string, a field, an error). If tactical, hand off to `ux-writing` or `form-ux-design`.
- For any new flow: write the **content brief before the wireframe**. Layout decisions follow content, not the reverse. See `references/content-first-design-workflow.md`.
- For any new product or sub-product without a voice chart: build one before approving copy. See `references/voice-chart-construction.md`.
- For any UI text decision: pick the pattern from `references/ui-text-patterns-library.md`, not from instinct.
- For any error: classify (system / user / environment), then apply the recovery formula in `references/error-state-taxonomy-and-recovery.md`.
- For any form: apply input reduction and engagement gates from `references/form-completion-gates.md` before writing labels.
- Set the metric and baseline using `references/content-measurement-framework.md` before content ships, or the change is unmeasurable.
- Communicate the decision using the framing in `references/design-decision-communication.md` and capture explicit agreement.
- For lifecycle content (onboarding through win-back), apply the narrative arc and peak/end placement in `references/product-narrative-arcs.md`.

## Quality Standards

- Every content decision names: the user state it serves, the metric it moves, the voice principle it enforces, and the alternative it rejected.
- Voice attributes are observable in the copy. If a stakeholder cannot point to the word that proves "warm" or "expert," the chart is decorative.
- Tone shifts by user state, not by writer mood. Same product, different moments, predictable shift.
- Errors tell the user what happened, why, and the next move - in that order, in user language, without blame.
- No content ships without a measurement plan: baseline, target, time window, sampling rule.
- Stakeholder agreements are recorded in writing with the date, the alternatives considered, and the trade-off accepted.

## Anti-Patterns

- Writing copy onto a finished wireframe and calling it content design.
- Voice charts that list adjectives nobody can disprove ("friendly," "professional," "human").
- Apologetic system errors that hide cause and offer no next step.
- Form labels rewritten in isolation while the field still asks for data the business does not need now.
- "We measured engagement" used as a substitute for completion, comprehension, error rate, or trust signals.
- Carrying a content debate by seniority instead of by evidence, then re-litigating it three sprints later.
- Treating onboarding as the only narrative moment and ignoring recovery, mastery, and win-back.

## Outputs

- Voice chart with tone-shift table, content principles, and worked examples per user state.
- Content brief(s) preceding wireframes, with success metric, voice principle, user state, and copy boundary.
- UI text decisions traceable to a pattern in the library.
- Error taxonomy with recovery copy formulas and escalation paths.
- Content measurement plan: metric, baseline, target, instrumentation, review cadence.
- Decision log entries (decision -> reason -> evidence -> alternatives -> trade-off -> agreement).
- Lifecycle narrative map with peak/end moments identified per persona.
- 30 / 60 / 90-day content operations plan when scope warrants.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | UX content strategy and voice chart | Markdown with voice principles, UI patterns, and audience rules | `docs/ux/content-strategy.md` |
| Correctness | UI text QA checklist | Markdown checklist covering buttons, labels, errors, empty states, and confirmations | `docs/ux/ui-text-qa.md` |
| Performance | Form completion gate | Markdown or CSV with friction, validation timing, and completion metrics | `docs/ux/form-completion-gate.md` |
| Release evidence | Content measurement plan | Markdown plan with metrics, owners, review cadence, and change log | `docs/ux/content-measurement.md` |

## References

- `references/voice-chart-construction.md` - deriving voice attributes and the tone-shift table.
- `references/content-first-design-workflow.md` - content brief template and the content-first protocol.
- `references/ui-text-patterns-library.md` - rules for label, button, error, empty, loading, confirm, notification.
- `references/form-completion-gates.md` - input reduction logic, gradual engagement, inline validation copy.
- `references/error-state-taxonomy-and-recovery.md` - error categories, recovery formulas, escalation copy.
- `references/content-measurement-framework.md` - metrics tied to content goals, baseline-to-target.
- `references/design-decision-communication.md` - rationale framing, objection handling, agreement capture.
- `references/product-narrative-arcs.md` - lifecycle stories, peak/end moments, persona-aware narrative.
- Use `ux-writing` for tactical microcopy execution once strategy is set.
- Use `form-ux-design` for form mechanics, field selection, and validation behavior.
<!-- dual-compat-end -->

Derived from Metts and Welfle (2020) *Strategic Writing for UX*, Wroblewski (2008) *Web Form Design: Filling in the Blanks*, Greever (2020) *Articulating Design Decisions*, 2nd ed., and Parrish (2020) *Storytelling in Design*.

## When To Invoke Companion Skills

| Situation | Skill |
|---|---|
| Voice exists, you need a single button or empty state string | `ux-writing` |
| Form layout, field count, input type, validation behavior | `form-ux-design` |
| New product, new sub-product, or voice drift across teams | this skill, then `ux-writing` |
| Error rate or completion rate is the target metric | this skill, then `form-ux-design` and `ux-writing` |
| Stakeholder has rejected copy three times | this skill - see `design-decision-communication.md` |

## Decision Gates

- **Voice gate:** No copy ships for a new product surface until the voice chart and at least one tone-shift row exist.
- **Content-first gate:** No high-stakes flow goes to visual design until a content brief is approved.
- **Measurement gate:** No content change is "done" until baseline, target, and review date are recorded.
- **Decision gate:** No revisited debate is reopened without new evidence; the decision log is the source of truth.
- **Narrative gate:** No lifecycle program ships without identifying its peak and end moments per persona.

## Operating Cadence

## Inputs

| Artifact | Produced by | Required? | Why |
|---|---|---|---|
| Product purpose, audience, and critical flows | Product brief or research | required | Anchors voice and content priorities |
| Current interface copy and performance evidence | Repository and analytics | optional | Reveals drift and measurable failure points |

## Capability contract

Read and search current product copy and approved research first. Editing requires authorisation; do not publish copy or alter production content without explicit approval.

## Degraded mode

If product copy, research, or metrics are unavailable, return a provisional brief, list needed evidence, and avoid claiming that decisions are validated.

- Weekly: review content tickets against voice and pattern library; flag drift.
- Monthly: review measurement dashboard against targets; retire content that fails to move its metric.
- Quarterly: refresh voice chart only if evidence shows the audience or product purpose has shifted; otherwise leave it alone.
- Per release: confirm error taxonomy coverage for new failure modes introduced by the release.
