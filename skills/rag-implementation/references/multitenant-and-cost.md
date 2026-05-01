# Multi-tenant Isolation and Cost Levers

Deep dive supporting `SKILL.md` §7 and §8.

## Store-specific isolation patterns

Pinecone — namespaces:

```python
index.upsert(vectors=[...], namespace=tenant_id)
index.query(vector=q, top_k=10, namespace=tenant_id)
```

Namespace is a hard partition. Cross-namespace queries are not possible without explicit code. Make `namespace=tenant_id` the only path; reject any code path that builds the namespace string from user input.

Qdrant — payload filter or collection-per-tenant:

```python
client.search(
    collection_name="docs",
    query_vector=q,
    query_filter=Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]),
    limit=10,
)
```

Collection-per-tenant is a stronger boundary; payload filter is cheaper to operate but relies on every query carrying the filter. If you cannot guarantee that, choose collections.

pgvector + RLS:

```sql
CREATE POLICY tenant_isolation ON chunks
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

Set `app.tenant_id` from the verified auth context per request, never from the query payload.

## Audit log shape

Every retrieval call writes one row:

```text
ts, request_id, user_id, tenant_id, query, transformed_query,
returned_chunk_ids[], scores[], reranker_used, llm_called, cache_hit
```

Retain at least 90 days. Required for incident response and for regression analysis when faithfulness drops.

## Cost levers in operating order

1. Cache identical queries — full pipeline. Free wins on repeated FAQs.
2. Anthropic prompt caching on retrieved chunks — see `anthropic-patterns.md`.
3. Contextual compression — measure on your own corpus.
4. Smaller routing / eval LLM — Haiku-class for is-this-relevant calls; flagship only for final generation.
5. Dimension reduction in embeddings — only if your store supports it cleanly.
6. Re-embed only what changed — emit corpus-change events; never re-embed the whole corpus on schedule.

Measure each lever. The infrastructure cost difference between vector stores is typically smaller than the embedding-API and LLM cost; optimise the API tier first.

## What not to do for cost

- Do not lower top-k below the level the rerank stage needs to be effective. The rerank lift comes from having candidates to rerank.
- Do not switch to a cheaper embedding model without re-running the golden-set evaluation. A 30% cost reduction that costs 10 pp of context precision is a regression, not a win.
