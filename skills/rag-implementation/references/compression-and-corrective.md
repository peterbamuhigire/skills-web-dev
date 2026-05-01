# Contextual Compression and Corrective RAG

Deep dive supporting `SKILL.md` §4 and §5.

## Small-to-big retrieval

Decouple retrieval and synthesis chunks (the LlamaIndex pattern quoted in §4).

- Index small chunks (sentences, 1–2 paragraphs) with an embedding optimised for retrieval signal.
- Each small chunk carries a pointer to its parent chunk (a 1–2 page section).
- At retrieval, rank with the small chunks. At synthesis, replace each retrieved small chunk with its parent.

This raises retrieval precision (small chunks are noise-free) without starving the generator of context.

## Compression approaches compared

| Approach | When to use | Cost shape |
|---|---|---|
| LLM extraction (cheap LLM picks relevant sentences) | Long source documents, generation budget tight | Adds one LLM call per retrieved chunk; offset by smaller answer-LLM context |
| Embedding similarity filter | Cheap rerank; want a fast cut | Free at query time; tune threshold on the golden set |
| Cross-encoder rerank | High-precision retrieval needed | Highest latency contribution; biggest precision gain |

Threshold tuning. Sweep the embedding-similarity threshold on the golden set. Pick the value that maximises faithfulness without dropping context recall below the agreed floor.

## Corrective RAG control flow

```text
need_retrieval = llm_yes_no(query, "Does answering this require retrieval?")
if not need_retrieval:
    return generate(query)

candidates = retrieve(query)
relevant = [c for c in candidates if llm_yes_no(query, c, "Is this chunk relevant?")]

if not relevant:
    return fallback(query)   # web search, decline, escalate

answer = generate(query, relevant)
score  = llm_grade_faithfulness(answer, relevant)
if score < threshold:
    return fallback_or_retry(query)

return answer
```

Each step is a separate LLM call. Bound the total by:

- Routing the relevance check through a smaller, cheaper model.
- Caching the retrieved-chunks block when adjacent turns reuse it (see Anthropic prompt caching).
- Skipping the self-grading step on cached / repeat queries.

## Fallback design

A `no_relevant_context` outcome is not a failure — it is a feature. Decide once, per product, what the fallback is:

- Decline to answer with a templated explanation.
- Escalate to human support, attaching the query and the empty-retrieval signal.
- Hand off to a web search tool (only if the product allows out-of-corpus content).

Log every fallback. Spikes in fallback rate are the first indicator of corpus drift.
