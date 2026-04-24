# Verifiability Patterns

Why confidence-percentage UI is wrong for LLMs, what to do instead, and how to check citation quality.

---

## Why Confidence % Is Wrong for LLMs

LLMs generate one token at a time, each with an internal probability distribution. Those probabilities are **about the next token**, not about the truth of the statement.

- A hallucinated fact can be generated with high token probability if the model has seen similar patterns frequently.
- A correct, rare fact can be generated with low token probability.
- Averaging token probabilities across a sentence produces a number that feels like confidence but has no relationship to correctness.

Displaying this number as "87% confident" misleads users. It confers false authority — a polished badge on a wrong answer is worse than no badge.

**Do not:** "Confidence: 87%" on an LLM paragraph.
**Do not:** "High / Medium / Low confidence" derived from token probabilities.
**Do not:** colour-code LLM output red/yellow/green based on perplexity.

---

## What to Do Instead: Inline Sources per Claim

Attribution is the only verifiability signal users can act on.

**Perplexity pattern (superscript):**

```
The DPPA 2019 Act was enacted in Uganda on 25 February 2019[1]
and requires data controllers to notify the PDPO of any breach
immediately[1][2].

Sources:
  [1] ulii.org/ug/legislation/acts/2019/9 - accessed 2026-04-25
  [2] pdpo.go.ug/guidance/breach-notification - accessed 2026-04-25
```

**NotebookLM pattern (chip per claim):**

Every paragraph ends with a chip showing the number of source passages; clicking opens a side panel with the exact passage highlighted.

**Rules:**

- Every factual claim has at least one source.
- Multiple claims share a source marker when appropriate.
- "Source: my own reasoning" is a valid marker for synthesised claims — be explicit about it.

---

## Citation Quality Checks

Attribution is only useful if the source actually supports the claim. LLMs can hallucinate citations too.

**Automated checks:**

- Fetch the cited URL at generation time.
- Run a retrieval similarity score between the claim and the cited passage.
- If similarity is below a threshold, demote the citation to "Source found but may not directly support this claim" and log for review.

**Human-in-the-loop checks:**

- In high-stakes domains, require a reviewer to click through at least one citation per output before marking it approved.
- Log citation-click-through rate per model version as a quality metric.

---

## Hallucination-Risk Signals

Even without confidence numbers, signal elevated risk:

- "No sources available" — output is pure generation. Surface this prominently.
- "Tool use failed, falling back to model knowledge" — output may be stale.
- "Session context only" — output is summarising what the user typed, not external fact.

These are factual metadata, not confidence estimates, and they help users decide how much to trust the output without inviting false precision.

---

## Exceptions: When a Confidence Number IS OK

- **Calibrated non-LLM models.** A computer vision classifier that reports softmax probabilities has mathematically meaningful confidence. Display it.
- **RAG retrieval score.** The similarity score between query and retrieved passage is meaningful for "did we find the right document" — it is distinct from "is the LLM's answer correct".
- **A/B test or forecasting models with real backtests.** If you have evidence the model is calibrated, show it.

In all three cases, the confidence is **about something that has been measured**, not about the LLM's self-assessment of its own prose.
