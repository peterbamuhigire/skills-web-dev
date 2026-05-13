# Hypothesis and Validation Thresholds

Discovery fails when assumptions stay implicit and "validation" means "we asked some people and they liked it." This reference encodes the discipline that converts opinions into falsifiable hypotheses with thresholds set *before* fieldwork, behavioural signal that counts, and MVP shapes that test the riskiest assumption fastest.

## The Assumption Ledger

For each branch in the impact map, list every belief that must be true for the branch to deliver the outcome. Capture three classes:

| Class | What it asserts | Typical failure mode |
|-------|----------------|----------------------|
| Customer | The actor has the problem, in the form we describe, often enough to act. | Problem is real but rare, or felt by a different actor. |
| Problem | The actor currently uses an inadequate workaround that has measurable cost. | Workaround is "good enough" — no switch energy. |
| Solution | Our proposed deliverable changes the actor's behaviour as predicted. | Actor adopts but reverts; or adopts a different feature than expected. |

Each assumption is written as: *We believe that [actor] [behaviour] because [trigger], and our deliverable will cause [measurable change].*

A taken-for-granted assumption — one nobody on the team can articulate because "that's just how it is" — is the highest-risk class. Force the ledger to surface them by asking, for each branch, *what would have to be true that no one has bothered to question?*

## Ranking Rule

Score each assumption on two axes, 1-5:

- **Impact-if-wrong**: how much of the roadmap collapses if this is false.
- **Evidence-against**: how strong existing disconfirming evidence is (5 = none, 1 = strong disconfirmation already exists).

Rank by `impact-if-wrong * evidence-against`. Top three become this cycle's targets. Anything below the cut is parked in the ledger; do not test it now.

## Setting Thresholds Before Fieldwork

Write the persevere/pivot/kill thresholds *before* recruiting any participant. The threshold has four parts:

1. **Method** — how the signal is collected (interview behaviour, prototype task, landing-page conversion, log analysis, pre-order commitment).
2. **Sample** — minimum number of valid observations.
3. **Signal** — the specific behaviour or quote class that counts.
4. **Cut** — the count or rate that triggers each decision.

Template: *We will run [method] with [sample]. We will count [signal]. If [cut-persevere] we proceed; if [cut-pivot] we re-frame; if [cut-kill] we stop.*

## Stated vs. Behavioural Signal

Treat as weak (stated) signal: opinions, feature requests, "I would use that", ratings of hypotheticals, enthusiastic emails with exclamation points but no real-world evidence.

Treat as strong (behavioural) signal: descriptions of what they did the last time the situation arose, artefacts they show you, money already spent on workarounds, time blocks on calendars, hires they made, complaints they escalated, files they keep, the spreadsheet they built.

A validated hypothesis includes the customer confirming the problem, believing it can be resolved, having tried to resolve it themselves, and ideally having paid (in time, money, or political capital) for an inadequate fix. Threshold counts only behavioural signal. Stated signal is logged but does not move the cut.

## Falsification Discipline

A hypothesis you cannot lose is not a hypothesis. Before fieldwork, write the *one observation* that would force you to abandon the hypothesis. If you cannot write it, the hypothesis is too vague — sharpen it.

Examples:

- Vague: "Users want faster onboarding." (Cannot be falsified.)
- Sharp: "At least 3 of 5 interviewed first-week users describe abandoning at the verification step because of SMS delay; if 2 or fewer describe this, the verification step is not the bottleneck."

## Sample Size Rules of Thumb

Lean Customer Development convention, used as defaults unless a specific risk forces a larger sample:

- Within **5 interviews** you should meet at least one genuinely excited prospect. If not, the hypothesis is most likely already invalidated and the cycle should stop early — do not "push through" looking for the right person.
- Within **10 interviews** patterns should be visible. Use the next interviews to challenge the pattern by deliberately asking the opposite question or recruiting a counter-segment.
- **15–20 interviews** is the working ceiling for a single hypothesis cycle. The signal that you are done is that surprises stop arriving — every new interview confirms what previous ones told you.

If the conversation does not surface a pattern by the tenth interview, the hypothesis is probably mis-framed; pivot the framing rather than running more interviews.

## MVP as a Validation Instrument

The MVP is not a stripped-down product — it is the *minimum* artefact that resolves the *highest-risk* assumption on the ledger. Pick the MVP shape from the question being asked:

| Shape | What it tests | Use when |
|-------|---------------|----------|
| Pre-Order MVP | Commitment, willingness to pay, letter-of-intent, pilot agreement | The unknown is whether anyone will actually transact, not whether the build is feasible. |
| Audience-Building MVP | Whether you can reach the actor at scale | Distribution risk dominates the build risk. |
| Concierge MVP | Whether the workflow you propose actually solves the problem when delivered manually | The solution shape is unclear. |
| Wizard-of-Oz MVP | Whether the customer-facing experience works, before automating | UX is the risk; backend is well-understood. |
| Single Use Case MVP | Whether a narrow slice produces the impact predicted | The map has many branches and you need to know which one bites. |

Two cardinal sizing rules:

- If the MVP would take more than a few weeks, it is not minimum.
- If the MVP cannot be described in two sentences, it is not minimum.

A Pre-Order MVP is the strongest behavioural signal short of a paid customer because pulling out a credit card or signing a letter of intent has high friction. Almost every hypothesis benefits from one form of pre-commitment test, even if the eventual product is built another way.

## Decision Gates

Use these gates rather than ad-hoc judgement at the end of a cycle:

- **Persevere**: behavioural cut met; the actor described the problem in the predicted form, used a costly workaround, and committed something (time, money, agreement) to an MVP. Continue building toward the deliverable.
- **Pivot**: the problem is real but mis-framed — wrong actor, wrong trigger, wrong workaround cost, or wrong deliverable. Re-write the hypothesis in the ledger, refresh thresholds, run another short cycle.
- **Kill**: behavioural cut not met within the planned sample. Park the branch in the impact map under "tried and failed" with the date and signal so it is not unconsciously revived next quarter.

A "we ran out of time" outcome is not a gate — it is a process failure to schedule.

## Closing the Loop with Existing Customers

When the segment under hypothesis is an existing customer base, share back what you heard before designing the next iteration. The act of summarising the problems back, naming the workarounds, and pointing at proposed changes is itself a validation move: customers correct mis-framings faster than they correct prototypes. It also strengthens trust for the next research cycle.

## Anti-Patterns at the Threshold Stage

- Setting thresholds *after* fieldwork — known as "moving the goalposts to confirmation".
- Running more interviews because the data was disappointing rather than pivoting the hypothesis.
- Building the MVP first and then "validating" it with users who have nothing to compare it to.
- Counting feature requests as validation of the underlying problem.
- Treating "they would use it" as equivalent to "they did".

## Source Grounding

- Alvarez's stated-vs-behavioural distinction and the validated-hypothesis criteria (customer confirms problem, believes it can be solved, has tried to solve it, has paid in some form).
- The 5/10/15-20 interview cadence and the "stop hearing surprises" stopping rule.
- The MVP-types catalogue: Pre-Order, Audience-Building, Concierge, Wizard of Oz, Single Use Case, Other People's Product.
- "Minimum" as smallest investment that resolves the riskiest assumption, not stripped-down product.
- Taken-for-granted assumptions as the highest-risk class to surface deliberately.
- Closing the loop with existing customers by summarising back what was heard.
