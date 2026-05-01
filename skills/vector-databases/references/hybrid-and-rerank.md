# Multi-Tenant Isolation, Hybrid Search, and Reranking — Deep Dive

Companion to `SKILL.md` §6, §7, §8.

## Multi-tenant isolation

Cross-tenant retrieval leakage is a security incident. Treat it as such in tests, alerts, and incident review.

### Pre-filter vs post-filter

- **Pre-filter.** The metadata filter is applied before the ANN search. The index is restricted to candidate points that match the filter, and ANN runs over those. Recall is preserved.
- **Post-filter.** The ANN search runs over the whole index; matches that fail the filter are dropped from the result set. If the filter is selective (e.g., a single tenant out of thousands), the top-k of the ANN search is unlikely to include enough in-tenant matches and recall collapses.

For tenant boundaries, always pre-filter. For non-isolation filters (date range, document type) post-filter is acceptable when the filter is non-selective.

### Pinecone

Pinecone docs (`docs.pinecone.io/guides/get-started/overview`, fetched 2026-05-01): "Use namespaces to partition data for faster queries and multitenant isolation between customers."

```python
index.query(
    namespace=f"tenant-{tenant_id}",
    vector=query_embedding,
    top_k=10,
    filter={"doc_type": {"$eq": "article"}},
    include_metadata=True,
)
```

Namespace is the primary tenant primitive; metadata filters are secondary (use them for non-tenant axes).

### Qdrant

Two patterns from `qdrant.tech/documentation/concepts/collections/` (fetched 2026-05-01):

- Single collection with a `tenant_id` payload field and a payload index on it. Best for many small tenants.
- A collection per tenant. Best for few large tenants.

```python
from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333")

client.create_collection(
    collection_name="docs",
    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
)

client.create_payload_index(
    collection_name="docs",
    field_name="tenant_id",
    field_schema="keyword",
)
```

Distance options: Dot, Cosine, Euclid, Manhattan. Per the docs: "Cosine similarity is implemented as dot-product over normalized vectors. Vectors are automatically normalized during upload."

### pgvector

Tenant filter is a SQL `WHERE tenant_id = $tenant`, optionally enforced by row-level security:

```sql
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON document_chunks
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

This is the strongest tenant-isolation guarantee of the five engines because it is enforced by the database, not the application.

### Tenant-leakage test

Add to CI: insert documents for tenant A and tenant B, run a query bound to tenant A, assert that no document with `tenant_id = B` appears in the results. Run it before every release.

## Hybrid search and Reciprocal Rank Fusion

Vector search captures semantic similarity but loses on exact-match keywords. BM25 (the keyword baseline) wins on those. Hybrid runs both and fuses the rankings.

### When each wins

| Query type | Vector wins | Keyword wins |
|---|---|---|
| Paraphrase ("how do I cancel a subscription") | Yes | No |
| Exact SKU ("PRD-2024-RED-XL") | No | Yes |
| Error code ("ERR_TIMEOUT_5042") | No | Yes |
| Conceptual ("strategies for high churn") | Yes | No |
| Person name | No | Yes |
| Multilingual | Yes | No |

### Reciprocal Rank Fusion

RRF does not require score calibration between the two systems:

```
RRF_score(d) = Σ_i  1 / (k + rank_i(d))
```

`rank_i(d)` is `d`'s rank in retrieval system `i`. `k` is a small constant, typically 60. Each system contributes a bounded amount per result, regardless of the system's raw score scale.

Reference implementation:

```python
def rrf_merge(rank_lists: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranked in rank_lists:
        for rank, doc_id in enumerate(ranked):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])
```

### Anthropic's Contextual Retrieval result

From `anthropic.com/news/contextual-retrieval` (fetched 2026-05-01):

- Contextual Embeddings alone "reduced the top-20-chunk retrieval failure rate by 35% (5.7% → 3.7%)".
- Contextual-embedding + contextual-BM25 combined "reduced the top-20-chunk retrieval failure rate by 49% (5.7% → 2.9%)".
- With reranking added, "reduced the top-20-chunk retrieval failure rate by 67% (5.7% → 1.9%)".

Hybrid + context beats vector-only. Implementation belongs in `rag-implementation`; this skill records the result.

## Reranking — the two-stage pipeline

### Why bi-encoders need a reranker

The embedding models that produced the index are bi-encoders: query and document are encoded independently and their interaction is reduced to a single dot product. Cross-encoders score (query, document) jointly and capture interaction features that a dot product cannot. Cross-encoders are far more accurate per item and far too slow to run over the whole corpus.

The pipeline:

1. **Retrieve.** Pull top-100 candidates by vector similarity (or hybrid).
2. **Rerank.** Score each candidate against the exact query with a cross-encoder; keep top-10.

### Reranker options

- **Cohere Rerank** (`cohere.com/rerank`). Managed API, multi-language.
- **BGE reranker.** Open-source on HuggingFace. Self-host on CPU (small models) or GPU (larger).
- **Voyage rerank.** Managed API.

### Latency and cost

Reranking adds latency, typically 100–500 ms for a shortlist of 100 — verify against your reranker. Cost: per-token API for managed rerankers; GPU/CPU for self-hosted. Cache identical (query, doc) pairs.

### When to skip reranking

- Latency budget below 200 ms p95 and no GPU available.
- Corpus is small (under a few thousand chunks) and vector-only recall is already saturated.
- Evaluation shows no measurable lift over hybrid alone.

## Sources

- Pinecone — `docs.pinecone.io/guides/get-started/overview`.
- Qdrant — `qdrant.tech/documentation/concepts/collections/`.
- Anthropic Contextual Retrieval — `anthropic.com/news/contextual-retrieval`.
- AI-Powered Search, Trey Grainger, Manning, 2024 — canonical reference for hybrid search architecture (concept level only).
- Reciprocal Rank Fusion: Cormack, Clarke, Büttcher 2009 — concept named; verify the SIGIR proceedings reference before any direct quotation.
