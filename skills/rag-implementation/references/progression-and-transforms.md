# Progression and Query Transforms

Deep dive supporting `SKILL.md` §2 and §3.

## When to move from Naive to Advanced

Move when any of these is true:

- Multi-hop questions appear in the golden set ("Compare A and B on X").
- Recall@10 below 0.7 on the golden set.
- Users are reformulating queries to get better results.

Add stages in this order: rerank → hybrid (BM25 + vector) → query transformation → contextual compression. Re-evaluate after each. Do not add all four at once; you will not know which moved the metric.

## When to move from Advanced to Modular

Move when any of these is true:

- Two or more corpora with different optimal retrievers.
- Conditional retrieval (some queries should not retrieve at all).
- A routing decision needs to call different generation models for different query classes.

Modular RAG is a runtime-routing system. Do not introduce it before you have a routing decision worth making.

## Choosing a query transform

| Symptom | Transform |
|---|---|
| Ambiguous, short queries | Multi-query expansion |
| Multi-part questions | Decomposition |
| Domain mismatch between query language and corpus language | HyDE |
| Question is too specific; corpus only contains general material | Step-back |

Combinations that help:

- HyDE + rerank — HyDE expands recall, rerank cleans the candidate set.
- Multi-query + Reciprocal Rank Fusion — when paraphrases yield disjoint candidate lists.

Combinations to avoid:

- HyDE + decomposition simultaneously on every query — multiplies LLM calls without measured gain. Route by query class.

## HyDE failure modes

- Hypothetical document confidently fabricates an entity that exists nowhere in the corpus; retrieval returns near-misses with high similarity. Mitigation: rerank with the original query, not the hypothetical.
- Hypothetical is too short; embedding lacks signal. Generate 100–200 tokens, not 30.

## Decomposition prompt shape

```text
You will receive a multi-part question. Output a JSON list of self-contained
sub-questions. Each sub-question must be answerable independently of the
others. Do not invent sub-questions that the original does not imply.

Question: {query}
```

Validate the output is a JSON list before retrieving. Cap at 5 sub-questions to bound cost.
