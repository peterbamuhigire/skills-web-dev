# Grounding & Citation UX — Reference

How to show grounding so the user can verify, not just trust.

## Principles

1. **Show, don't claim.** A confidence percent without sources is theatre.
2. **One click to verify.** Source preview must be one interaction away.
3. **Default to provenance.** Every factual sentence shows where it came from.
4. **Honest absence.** When the system has no source, say so.
5. **Accessibility-first.** Citations must be keyboard-navigable and screen-reader-friendly.

## Patterns

### Inline numbered citations

```
The refund window is 30 days from purchase [1]. Refunds are issued to the original payment method [2].

[1] Refund Policy → Section 2 (updated 2026-03-10)
[2] Refund Policy → Section 4
```

- Numbers are clickable.
- Hover/focus reveals a tooltip with source title, snippet, updated date.
- Click opens the source in a side panel at the cited section.

### Source-pill cluster (chat UIs)

After the answer, a row of source pills:

```
Sources: [Refund Policy ↗] [Shipping FAQ ↗] [Order #88421 ↗]
```

Each pill is the document title; click opens preview.

### Confidence + sources (combined)

```
Answer (high confidence, 3 sources)
The refund window is 30 days...

Sources: ...
```

Confidence is derived from grounding signals; never a model-emitted self-rating.

### Abstain affordance

When the system cannot ground:

```
I couldn't find a definitive answer in your knowledge base.
Suggestions:
  • Try rephrasing your question.
  • Browse [Refunds] [Shipping] [Account].
  • Or [talk to a human ↗] (response in < 5 min).
```

### Partial grounding

When some claims are grounded and some are not:

```
The refund window is 30 days [1]. ⚠️ The replacement-shipment timeline isn't in your knowledge base — generic guidance only.
```

Ungrounded claims must be marked.

## Anti-patterns

- Confidence shown as 87% with no source links.
- Footnotes that are not interactive — users can't verify.
- Source pills that link to the doc's homepage, not the section.
- "I'm not sure" with no escape hatch (no related docs, no human handoff).
- Citations rendered but the cited text doesn't actually support the claim — worse than no citations.

## Implementation

The model is asked to produce structured output with claim → chunk_id mappings:

```json
{
  "answer": "The refund window is 30 days [1]. Refunds go to the original method [2].",
  "citations": [
    {"id": 1, "chunk_id": "ch_001", "score": 0.91, "supports": "refund window is 30 days"},
    {"id": 2, "chunk_id": "ch_007", "score": 0.84, "supports": "original payment method"}
  ]
}
```

Post-processor verifies:
- Every cited chunk_id is in the retrieved set.
- The `supports` excerpt is paraphrased from the chunk text (lexical or semantic overlap > threshold).
- Every numeric marker `[n]` in `answer` has a matching citation.

Failures → either rewrite or abstain.

## Accessibility

- Citation markers are `<button>`/`<a>` with `aria-describedby` pointing to a hidden source description.
- Source previews are keyboard accessible (Enter to open, Escape to close).
- High-contrast modes maintain ≥ 4.5:1 contrast on markers.
- Screen reader: "Reference 1: Refund Policy, Section 2".

## Telemetry

Track:
- Citation click-through rate (target ≥ 20% for verifiable workflows).
- Abstain rate.
- "This wasn't right" flag rate per cited source.
- Latency to first citation render in streaming.
