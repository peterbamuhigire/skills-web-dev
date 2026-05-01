# Evaluation with RAGAS

Deep dive supporting `SKILL.md` §6.

## Golden set design

Aim for 50–500 questions. Cover:

- Each major topic in the corpus (representative coverage).
- Each query class supported (factoid, comparison, summarisation, multi-hop).
- Known edge cases (recent updates, deprecated content, sensitive topics).
- Cross-tenant probes — queries that should retrieve nothing in the current tenant.

Each entry contains: query, ideal answer (free-text), ideal supporting chunk IDs, and a label for query class. The chunk IDs let you compute context recall directly.

## CI gate

Run RAGAS on every PR build. Fail when:

- Faithfulness drops more than 5 percentage points relative to the main-branch baseline.
- Context precision drops more than 5 percentage points.
- Any cross-tenant probe returns a non-empty result. This is severity-1; block release.

Tune the 5 pp threshold to your noise floor. Run the baseline three times to estimate variance; do not set the gate inside the noise band.

## Threshold tuning workflow

1. Run RAGAS on the golden set against `main` 5 times.
2. Compute mean and standard deviation per metric.
3. Set the gate at `mean - 2 * stddev` for floor metrics, or `baseline - 5 pp` for delta metrics — whichever is tighter.
4. Re-baseline after intentional changes (new model, new chunking).

## Production sampling loop

- Sample 1–5% of real queries weekly.
- Label asynchronously — human for high-stakes queries, LLM-as-judge for the rest, with a human-spot-check on a sub-sample of LLM judgements.
- Promote interesting cases (new failure modes, novel query classes) into the golden set monthly.
- Retire stale golden-set entries when the corpus or product changes.

## What RAGAS does not catch

- User-perceived helpfulness — you still need a thumbs-up / thumbs-down loop.
- Latency and cost — instrument these separately.
- Tone and refusal correctness — needs its own rubric.
- Prompt-injection robustness — needs adversarial probes (see `failure-modes.md`).
