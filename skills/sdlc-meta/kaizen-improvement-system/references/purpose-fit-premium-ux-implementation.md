# Purpose-fit premium UX implementation

Parent skill: [Kaizen Improvement System](../SKILL.md).

Use this reference when a web implementation must feel distinctive, premium, and client-specific
while remaining clear, accessible, responsive, and operable. The implementation job is not to
reproduce a reference site's look. It is to preserve the user principle and express the product's
own visual thesis in real code, content, data, and states.

## Source boundary and currentness

The method is informed by three Eleken practitioner articles accessed 2026-09-08:

- [18 UX Improvements That Move Product Metrics](https://www.eleken.co/blog-posts/ux-improvements)
- [16 Best Dashboard Design Examples](https://www.eleken.co/blog-posts/dashboard-design-examples-that-catch-the-eye)
- [Compelling Design Takes More Than “Making It Like Stripe”](https://www.eleken.co/blog-posts/making-it-like-stripe)

These are Tier 5 creative inputs. Do not treat their examples, numbers, or recommendations as
platform standards. Verify current accessibility and browser behaviour against authoritative
sources. This reference uses [WAI-ARIA's dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/),
[WCAG 2.2 error identification](https://www.w3.org/WAI/WCAG22/Understanding/error-identification),
and [MDN's reduced-motion reference](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion)
as implementation evidence sources, all reviewed 2026-09-08.

The official model-currentness review also ran on 2026-09-08. `gpt-6-astra` and `gpt-5.6-luna`
remain the authorised topology; the installed policy helper returned root-policy drift and actual
runtime/account entitlement was not exposed, so availability is `NOT_ASSESSED`. Do not change the
model selection silently.

## Implementation contract

Before building a premium slice, record:

| Field | Implementation evidence |
|---|---|
| Client fit | Product, audience, job, environment, stakes, content/data truth |
| Design thesis | One sentence for hierarchy and feeling |
| Signature choice | One distinctive choice and its purpose, with reference treatments rejected |
| Source of truth | Token, component, content, and state owners |
| Critical states | Empty, loading, error, recovery, success, permission, interruption, long content |
| Target matrix | Wide/narrow viewport, keyboard, touch, reduced motion, locale, slow network |
| Proof | Running slice or render, tests, accessibility result, performance evidence, reviewer, rollback |

The slice is incomplete when it only has a hero screenshot, placeholder data, or a happy path.

## Pattern translation for web delivery

### Reduce entry friction without losing trust

- Prefer import or upload when the user already has the information, but keep an editable review
  state and a manual fallback when appropriate.
- Group fields by the actor's mental model and domain language, not by backend table order.
- Split a long form only at meaningful decisions; otherwise keep related independent decisions in a
  scannable page with clear sections.
- Make validation text-based and actionable. The W3C error-identification guidance is a release
  reference; colour alone is not an error explanation.
- Autofocus only when it helps the first desktop action and does not create an unwanted mobile
  keyboard jump; test the actual target devices.

### Make navigation and dashboard decisions visible

- Expose high-frequency filters, active-filter chips, search, and primary actions at the point of
  work. Persist scope in the URL or state model when the product needs a reproducible view.
- Classify a dashboard by the decision it serves. Implement the hierarchy as signal -> explanation
  -> action/detail, not as a uniform grid of cards.
- Give each chart a data contract: measure, unit, period, comparison, empty state, stale/partial
  state, accessible summary, and drill-down action.
- Use colour as one cue among labels, ordering, shape, or text. Keep the brand accent purposeful;
  do not turn every status into a competing accent.
- Allow personalisation when roles genuinely differ, but preserve a reliable default and shared
  definitions so customisation does not destroy team meaning.

### Preserve context with the right surface

Use the simplest surface that matches content depth:

| Situation | Implementation |
|---|---|
| Quick inspect or small edit | Dialog, side panel, or inline expansion with focus management |
| Deep, linkable, or multi-step work | Page with stable route, back path, and independent states |
| Independent decisions | One page if it remains scannable and recoverable |
| Dependent or high-risk decisions | Guided flow with step count, saved state, review, and confirmation |

When using a modal, implement the WAI-ARIA pattern: move focus inside, keep keyboard focus within
the dialog, support Escape, provide an accessible name, and return focus to the invoker or a
logical successor. Test the background as inert; a visual dimmer is not enough.

### Make waits and progress honest

- Replace a dead spinner with truthful stage messages only when the system exposes real stages.
- Use determinate progress when the total is known; otherwise describe the wait and expose cancel,
  retry, or safe continuation.
- Model queued, active, partial, success, failure, timeout, and duplicate-submit outcomes in the
  state machine and tests.
- Use a live-region strategy appropriate to the message frequency and importance; avoid flooding
  assistive technology with rotating decorative copy.
- Honour `prefers-reduced-motion` for non-essential animation and provide an equivalent readable
  state. Verify the actual browser matrix rather than relying on a generic support claim.

### Finish the authored system

Premium implementation is the final coherent system, not an expensive-looking colour layer. Check:

- type pairing, scale, line length, and real-content wrapping;
- spacing rhythm, container behaviour, data density, and responsive reflow;
- focus, hover, active, disabled, selected, validation, and permission states;
- meaningful empty/loading/error/recovery copy and retry/undo behaviour;
- icon semantics, image alternatives, motion timing, reduced-motion fallback, and input latency;
- bundle, image, font, and rendering budgets for the critical path;
- whether the signature choice is still legible and useful at narrow widths and in a neutral theme.

Run a concrete demo loop: implement one real slice, compare it to the thesis, review with real
content, make one deliberate variation, check the gates, and keep the version with the strongest
fit. Do not let an automated metric choose the aesthetic decision; use measurement to reveal harm
or validate the task outcome.

## Decision rules

| Finding | Implement | Avoid |
|---|---|---|
| Existing document or structured data is available | Upload/import plus editable confirmation | Opaque extraction that becomes final without review |
| Filter changes are frequent | Visible controls and removable scope chips | Repeated hidden-panel clicks |
| Dashboard has one dominant decision | Signal-first hierarchy with drill-down | Equal-weight widget wall |
| Detail is shallow | Dialog/panel with focus return | Route change that discards context |
| Process stages are known | Stepper and truthful determinate progress | Fake progress or spinner-only wait |
| Reference style is recognisable | Keep the principle, implement a new thesis | Copying layout, gradients, icons, or copy |
| Visual flourish harms access/performance | Reduce, defer, or remove it | Calling it premium because it is expensive to build |

## Minimum acceptance evidence

```text
client_fit_and_job:
design_thesis:
signature_choice_and_rejected_reference:
implemented_slice:
state_matrix:
responsive_and_input_matrix:
accessibility_result:
performance_result:
real_content_review:
rollback_or_revert:
reviewer_and_reaudit_date:
```

For a dashboard, add the metric/data contract and a comprehension or task-time measure. For a
modal, add keyboard focus entry, containment, Escape, accessible name, and focus return evidence.
For a long-running action, add duplicate-submit, retry, cancellation, and interruption evidence.
Missing evidence remains `NOT_ASSESSED` and blocks a production-ready claim.

## Anti-patterns

- **Reference screenshot as specification.** Fix: extract the job and write the client-specific
  thesis, tokens, content contract, and state matrix.
- **Dashboard as decoration.** Fix: require a signal, explanation, action, data definition, and
  empty/stale/partial state for every visual.
- **Modal without focus recovery.** Fix: use the current WAI-ARIA dialog acceptance sequence and
  test keyboard and assistive technology behaviour.
- **Loading theatre.** Fix: expose actual stages or honest wait/cancel/retry behaviour.
- **One accent everywhere.** Fix: reserve the accent for purposeful hierarchy and pair it with
  labels or other cues for meaning.
- **Placeholder-content approval.** Fix: use representative long, short, empty, translated, and
  error content before calling the slice finished.
- **Premium polish that misses the job.** Fix: stop the visual pass and return to requirements,
  content, or information architecture.

## Worked example

Suppose a multi-tenant operations app needs a “today” view. The implementation record can state:
the tenant administrator must identify the most urgent unresolved items, the thesis is “quiet
control room with one clear next action”, and the signature choice is a narrow attention rail
paired with plain-language status summaries. The code then implements visible scope chips, a
signal-first overview, a side-panel detail view with focus return, truthful loading and partial
data states, narrow-layout reflow, keyboard paths, and a reduced-motion variant. A copied neon
gradient or a generic card grid is rejected even if it looks fashionable. The proof is the running
slice plus state, accessibility, performance, and reviewer evidence.
