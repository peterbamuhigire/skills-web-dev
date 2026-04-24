---
name: experiment-engineering
description: Use when designing trustworthy product experiments — counterfactual logging,
  trigger design (exposure/action/hybrid), experiment-type selection (A/A, A/B, holdout,
  fake door, reverse, switchback), fairness checklist, sample-ratio-mismatch detection,
  and guardrail-metric pairing. The engineering discipline of running experiments that
  actually measure what you think they measure. Based on Okonkwo, *Growth Engineering*
  (Wiley, 2025).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Experiment Engineering

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing trustworthy product experiments — counterfactual logging, trigger design (exposure/action/hybrid), experiment-type selection (A/A, A/B, holdout, fake door, reverse, switchback), fairness checklist, sample-ratio-mismatch detection, and guardrail-metric pairing.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `experiment-engineering` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: experiment spec, trigger design, scorecard, or fairness-check report.

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

- Experiment spec (hypothesis, trigger definition, success metric, guardrail metrics, MDE, sample size, run-time).
- Counterfactual logging schema.
- Fairness-check report and SRM diagnosis.
- Scorecard: winners, losers, inconclusive, with remediation.

## References

- `references/experiment-spec-template.md` — pre-registration template.
- `references/trigger-patterns.md` — exposure/action/hybrid trigger patterns with pseudo-code.
- `references/experiment-types.md` — the six designs, when to use, when not to use.
- `references/fairness-and-srm.md` — SRM chi-squared, peeking, multiple comparisons.
<!-- dual-compat-end -->

## Why Experiments Fail Silently

The most common failure mode is dilution. If you log every page visitor as "treated" when only 5% actually saw the upsell card, the treatment effect dissolves into the noise of the 95% who never encountered it. The experiment reads "inconclusive," the feature ships nothing, and the team concludes the idea did not work. The idea may have worked; the measurement was wrong.

Dilution is invisible. The dashboards look fine, p-values compute, sample size was met. The only defence is a clean trigger — the precise moment a user becomes eligible for the treatment — combined with counterfactual logging that records both the variant assignment and the realised exposure.

## Triggers: The Clean Causal Line

A **trigger** is the precise moment a user becomes eligible to see the treatment. It is the moment from which the treatment and control groups diverge in experience. Everything before the trigger is shared; everything after is measured.

Three trigger patterns, each with a different correct use:

- **Exposure-based** — fired when the feature is rendered on screen. Use when the feature is visible-by-default (banners, hero tiles, inline cards that do not require navigation).
- **Action-based** — fired when the user takes the specific action that reveals the feature. Use when the feature sits behind navigation (clicks a tab, opens settings, taps an overflow menu).
- **Hybrid** — rendered-but-only-counts-if-visible. Use when visibility depends on scroll depth or viewport (below-the-fold modules, lazy-loaded sections).

Rule: log the trigger event server-side with the experiment ID, variant, user ID, and timestamp. A client-only trigger is not trustworthy because ad-blockers, bot traffic, and failed JavaScript drop events unequally across variants, which in turn creates spurious effect estimates.

See `references/trigger-patterns.md` for pseudo-code per pattern.

## Counterfactual Logging

For every triggered user, record both what they *saw* (the variant actually rendered) and what they *could have seen* (the counterfactual — what the other variant would have produced). This enables offline causal analysis beyond the primary metric.

Two implementation shapes:

- When the counterfactual is cheap — the experiment service computes both variant outputs and returns them with a `shown_variant` field. A ranker can produce both ranked lists at small marginal cost.
- When the counterfactual is expensive — the service records the decision inputs (features, weights, seed) so the counterfactual can be reconstructed later in an offline job.

Counterfactual logs let you answer questions the primary metric does not: did the treatment reorder the same items users would have clicked, or did it surface items users never would have seen?

## Experiment-Type Taxonomy

Six designs. Pick one before writing the spec.

- **A/A test** — same variant on both arms. Use to calibrate the platform, estimate baseline variance, and detect broken randomisation *before* any A/B runs. Non-negotiable before the first real experiment on a new platform. A platform that fails its own A/A test cannot be trusted to evaluate real treatments.
- **A/B test** — one change, two arms. Use for simple feature changes. The default.
- **Holdout group** — permanently withhold the feature from a small slice (typically 1-5%) indefinitely to measure long-term cumulative effect. Use when treatment effects compound over time (retention, habit formation, long-term revenue).
- **Fake door** — ship a button or entry point for a feature that does not exist yet; log clicks as a demand signal. Use to test demand before committing engineering time. Example: an "Invite a Friend" button that only logs and shows a "coming soon" modal. *Never leave fake doors in production for more than 14 days without explanatory copy* — leaving them indefinitely breaks user trust.
- **Reverse experiment** — remove a feature from the treatment group (opposite of A/B) to prove it still adds value. Use when a feature has been live for months and the team is unsure whether it still contributes. The reverse experiment is the only honest answer to "do we still need this?"
- **Switchback** — alternate treatment and control over time (e.g., every 30 minutes) across the whole audience. Use in marketplaces and supply-constrained systems where user-level randomisation leaks through shared supply (Uber driver pricing, ride-matching algorithms, inventory allocation).

See `references/experiment-types.md` for one worked-example scenario per design.

## Fairness Checklist

Before calling a result, confirm every item:

- Same audience — no segment drift between variants.
- Same time window — no weekend-vs-weekday split across arms.
- Same metric definition — no code change to event logging mid-experiment.
- Same backend version — no staged rollout overlapping with the test window.
- Pre-declared minimum detectable effect and sample size — no peeking.
- Pre-declared guardrail metrics — latency, error rate, crash rate, revenue-per-session, support ticket volume.

A result that fails any item is not a result; it is a coincidence that happens to be statistically significant.

## Sample Ratio Mismatch (SRM)

If you assigned users 50/50 and the logs show 48/52 with 100k users per arm, the experiment platform is broken — stop the experiment and investigate. Run a chi-squared test on assignment counts; if p < 0.01, do not trust any metric from the run.

Classic SRM causes:

- Bot traffic disproportionately hitting one variant (treatment arm has a heavier page weight that bots abandon).
- Redirect loops stripping the assignment cookie for one variant only.
- Caching skew (CDN caches the control variant more aggressively).
- Server-side assignment race conditions under load.

SRM is a platform health check, not a metric debate. See `references/fairness-and-srm.md` for a worked chi-squared example.

## Statistical Pitfalls

- **Peeking** — checking results before reaching the pre-declared sample size inflates the false-positive rate. A test with α=0.05 peeked at daily over two weeks has a true false-positive rate closer to 30%, not 5%.
- **Multiple comparisons** — testing 10 metrics at α=0.05 gives roughly a 40% chance of at least one spurious win. Apply Bonferroni or Benjamini-Hochberg correction when reporting more than one metric.
- **Novelty effect** — early lift fades as users habituate to a visual change. Wait for stabilisation before reading the result; typically the first 3-5 days are unreliable for UI changes.
- **Survivorship** — metrics computed on users who stayed through the entire window look artificially strong. Always compute retention-adjusted metrics alongside window-end metrics.

## Experiment Lifecycle

1. Propose hypothesis.
2. Pre-register the spec (see `references/experiment-spec-template.md`).
3. Run A/A validation if the platform is new or recently changed.
4. Implement the treatment with counterfactual logging and server-side triggers.
5. Launch to the declared audience slice.
6. Monitor guardrails daily; halt if any guardrail breaches its threshold.
7. Reach the pre-declared sample size.
8. Freeze the variant, collect the final window, analyse.
9. Produce the scorecard: primary metric result, guardrail results, segment breakdowns, fairness-check status.
10. Ship, kill, or iterate. Archive the spec and scorecard in the experiment registry either way.

## Anti-Patterns (Expanded)

- Logging every page visitor as treated when only some saw the feature — dilution.
- Calling wins at p=0.05 without reviewing guardrail metrics — latency regressions often pay for the conversion lift in refunds and support load.
- Never running an A/A test on a new experiment platform — unknowable baseline error rate.
- Treating the PM's gut feeling that "it's working" as rollout signal before sample size is hit — political rollout, not evidence-based rollout.
- Leaving fake doors live without disclosure — trust erosion compounds silently.
- Running switchbacks on user-level-randomised features — no effect on the variance problem, wastes a scarce experiment slot.

## Companion Skills

- `saas-growth-metrics` — the metrics the experiments improve.
- `growth-telemetry-pipeline` — the instrumentation that feeds trigger and counterfactual events.
- `observability-monitoring` — guardrail dashboards (latency, error rate, crash rate).
- `product-led-growth` — the motions that generate candidate experiments.
- `python-data-analytics` — offline scorecards, cohort slicing, counterfactual analysis.

## Sources

- *Growth Engineering* — Joseph Okonkwo (Wiley, 2025).
- Kohavi, Tang, Xu — *Trustworthy Online Controlled Experiments* (Cambridge).
