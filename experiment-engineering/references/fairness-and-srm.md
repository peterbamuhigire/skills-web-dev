# Fairness and Sample Ratio Mismatch

Before calling a result, run the fairness checks. Before trusting any metric, run the SRM check.

## Sample Ratio Mismatch (SRM)

You assigned 50/50. The logs say 48/52 with 100k users per arm. Is that a broken platform or a normal coin-flip wobble?

Chi-squared test:

- Expected per arm at 50/50 and N=200,000 total: 100,000.
- Observed: 96,000 and 104,000 (to be concrete — the 48/52 proportions on 200k).
- Chi-squared statistic: `sum((observed - expected)^2 / expected)` = `(4000^2 / 100000) + (4000^2 / 100000)` = `160 + 160` = `320`.
- Degrees of freedom: 1.
- Critical value at α=0.01: 6.63.
- `320 >> 6.63`, so p < 0.001. **SRM detected. Stop the experiment and investigate.**

Classic SRM causes in order of frequency:

1. Bot traffic hitting one variant more — usually the heavier/slower variant bots abandon, skewing toward the lighter variant.
2. Redirect loops stripping the assignment cookie for one variant only.
3. CDN caching one variant more aggressively.
4. Server-side assignment race conditions under load spikes.
5. Different page weights causing different abandonment rates pre-trigger.

Run the SRM check daily during the experiment. SRM detected mid-run invalidates everything collected so far; do not try to salvage the result.

## Peeking Illustration

Peeking at daily reads inflates false-positive rate. A test declared at α=0.05 that is peeked once per day for 14 days has a true false-positive rate closer to 20-30% depending on sample accumulation.

Defences:

- Pre-declare the sample size and only analyse at that sample size.
- If you must read early, use a sequential test (mSPRT, group sequential bounds, or Bayesian with pre-declared decision thresholds).
- Lock the test duration; do not "extend until significant."

## Multiple Comparisons Rules of Thumb

Testing one primary metric at α=0.05 → false-positive rate 5%.
Testing 10 metrics at α=0.05 with no correction → family-wise error rate ≈ 40%.

Corrections:

- **Bonferroni** — divide α by the number of tests. Conservative; use when false positives are expensive (ship/kill decisions on production features).
- **Benjamini-Hochberg (FDR)** — controls the expected proportion of false discoveries. Use when exploring many metrics to generate hypotheses for future tests.

Rule: one primary metric per experiment gets the uncorrected α. Every additional metric is either a guardrail (pre-declared threshold, not a p-value) or a secondary metric (Bonferroni or FDR corrected).

## Fairness Checklist (Expanded)

- **Same audience** — verify segment composition is within 1% absolute between variants on: country, device type, login status, tenure bucket.
- **Same time window** — both variants received traffic across the same clock hours and days of week; a test that ran Monday-only on one arm is invalid.
- **Same metric definition** — no PR merged during the test that changed the event, the aggregation, or the filter conditions.
- **Same backend version** — no staged rollout of an unrelated change overlapped with the experiment window.
- **No peeking** — no decisions made on early reads; the scorecard is produced only after the pre-declared sample size is reached.
- **Guardrails pre-declared** — latency, error rate, crash rate, revenue per session, support ticket volume; thresholds are written in the spec before launch.

If any fairness item fails, the result is not callable — rerun the experiment with the fairness issue fixed.
