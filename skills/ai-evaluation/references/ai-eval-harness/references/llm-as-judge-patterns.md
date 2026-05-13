# LLM-as-Judge Patterns — Reference

Open-ended outputs (essays, summaries, support answers) cannot be evaluated with exact match. A stronger LLM acting as a judge is the scalable option — but only if calibrated.

## Choosing the judge model

- Use a **different family** than the candidate when possible (avoid same-model bias).
- Use a **larger / stronger** model than the candidate.
- Pin the judge version in the manifest; never let it auto-upgrade.

## Rubric design

Keep rubrics short, ordinal, and aligned to the metric.

```
SCORE the candidate answer on FAITHFULNESS to the provided source.

  1 = contradicts the source
  2 = adds claims not supported by the source
  3 = supported but partially incomplete
  4 = fully supported and complete

Output a single integer 1–4 followed by a one-line rationale.
```

Why 1–4: forces a decision, no fence-sitting at 5/10 = lukewarm 7. Easier to calibrate to humans.

## Prompt template

```
You are an evaluator.
Task: <one sentence describing what good looks like>
Inputs:
  <source / question / context>
Candidate answer:
  <candidate>
Reference answer (if any):
  <reference>
Rubric:
  <rubric>
Return JSON: {"score": <int>, "reason": "<one line>"}
```

JSON-mode mandatory; downstream code parses cleanly.

## Calibration

Before trusting a judge:

1. Pick 100 candidate outputs spanning the score range.
2. Have ≥ 2 humans score them blindly using the same rubric.
3. Compute inter-rater agreement (Cohen's kappa) human-vs-human.
4. Run the judge; compute kappa judge-vs-human.
5. Accept the judge if kappa(judge, human-mean) ≥ 0.7 AND kappa is close to human-human.
6. If not, refine the rubric, try a different judge, or fall back to human scoring on goldens.

Recalibrate quarterly and whenever the judge model is upgraded.

## Multi-criteria judging

Don't mash 5 metrics into one score. Run the judge once per metric or use a structured output:

```json
{"correctness": 4, "faithfulness": 3, "format": 4, "tone": 3,
 "reason": "Correct but cites para 4 vague."}
```

Easier to dashboard; easier to threshold per-metric.

## Pairwise vs absolute

- **Absolute (1–4)** is good for tracking drift over time and for thresholds.
- **Pairwise (A vs B vs Tie)** is better for A/B prompt evals — sensitivity is higher.
- For pairwise, randomise A/B order to avoid position bias.

## Cost control

Judge calls cost money too. Strategies:
- Cache scores keyed by `(candidate_text_hash, judge_model, rubric_version, reference_hash)`.
- Sample production at 1–5%, not 100%.
- Use a cheaper judge for routine sampling; reserve the strong judge for goldens.
- Batch judge calls (Anthropic / OpenAI batch APIs) for offline runs.

## Failure modes

- **Position bias** in pairwise — fix with order randomisation.
- **Verbosity bias** — longer answers score higher. Mitigate by including length tolerance in rubric or normalising.
- **Self-preference** — judge favours its own model's style. Mitigate by using a different family.
- **Sycophancy** — judge agrees with the candidate's reasoning when it shouldn't. Mitigate by providing source / reference and asking for grounded justification.

## Audit

Persist every judge call: candidate id, judge model, rubric version, score, reason, ts. Required for:
- Re-running with a new judge.
- Debugging regressions.
- Disputes when a prompt change is rejected.
