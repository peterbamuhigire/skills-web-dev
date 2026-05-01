# Production Patterns and Cost Management — Deep Dive

Companion to `SKILL.md` §10 and §11.

## Index lifecycle

Vector indexes — HNSW especially — are not free to maintain on heavy-write workloads. Insert and delete operations modify the graph; rebalance work is amortised but not zero. On corpora that are written more than they are queried, the index pays for itself slowly.

The standard pattern is **bulk-load a fresh index off-line, switch reads atomically, keep the old one for rollback**:

- **Pinecone.** Create a new index or namespace, bulk-upsert, switch the application's index/namespace pointer atomically, drop the old after a soak period.
- **Qdrant.** Create a new collection, bulk-upsert, alias swap (Qdrant supports collection aliases), drop the old.
- **pgvector.** Use `CREATE INDEX CONCURRENTLY` for online builds. For full rebuilds, build into a side table and `ALTER TABLE ... RENAME` atomically inside a transaction.
- **Weaviate.** Versioned classes with a switch in the application layer.

Always keep the old index until the new one has been verified in production by retrieval evaluation and a tenant-leakage test.

## Freshness vs recall

New writes that have not yet been embedded are invisible to retrieval. The lag is "freshness staleness". Reduce it by streaming the embedding pipeline (event-driven) rather than batch nightly.

The metric:

```
staleness_seconds = NOW() - vector_updated_at
```

Track it as a percentile (p50, p95, p99). Alert when p95 exceeds the freshness budget agreed with the product owner. Typical SaaS budgets: 30 seconds for in-app search, 5 minutes for analytics, 1 hour for nightly reports.

## Monitoring signals

Wire these into `observability-monitoring`:

| Signal | Purpose | Alert threshold (typical) |
|---|---|---|
| Embedding-write latency p95 | Pipeline health | > 5 s sustained |
| Embedding-write error rate | Provider outage | > 1% over 5 min |
| Query latency p95 (vector stage) | Retrieval health | > budget × 1.5 |
| Query latency p95 (rerank stage) | Reranker health | > budget × 1.5 |
| Recall@k on held-out eval | Drift detection | < baseline by 5 pp |
| Index-rebuild duration | Operational sanity | > 2× last rebuild |
| Freshness staleness p95 | Bridge health | > freshness budget |
| Tokens-per-day | Cost control | > daily budget |
| Dollars-per-day | Cost control | > daily budget |

Recall@k drift is the canary for embedding-model deprecation, corpus drift, or a silent change in chunking. Run it at least nightly against a held-out evaluation set.

## Cost management

Embedding generation is the dominant cost across every realistic option. The vector store itself is secondary. Optimise embedding spend first.

### Cost levers, ordered by impact

1. **Re-embed only what changed.** Hash the source text per chunk; skip the API call when the hash is unchanged. On a corpus that changes 1% per day, this lever is roughly 100x.
2. **Right-size the model.** `text-embedding-3-small` is materially cheaper than `-large`. Move up only if your evaluation set shows the lift justifies the multiplier.
3. **Reduce dimensions.** OpenAI 3-* embeddings support output truncation to a smaller dimension; storage and query speed improve roughly linearly. Verify retrieval-quality impact at the chosen dimension on your evaluation set before committing.
4. **Cache reranker calls.** Identical (query, doc) pairs are common in interactive applications; cache for hours to days.
5. **Batch aggressively.** Per-request overhead is non-trivial. Larger batches reduce dollars-per-token at the margin.
6. **Negotiate volume pricing** above some monthly threshold — vendor-specific.

### Vector-store cost models

- **Pinecone** — metered on storage (vector count) and query volume. Predictable; visible in dashboard.
- **Qdrant Cloud** — metered on instance size; self-host is fixed (compute + storage).
- **Weaviate Cloud** — similar metered model; self-host is fixed.
- **Chroma** — local is free; managed is metered.
- **pgvector** — folded into PostgreSQL hosting; effectively zero marginal cost beyond what you already pay for PostgreSQL.

### Cost telemetry

Emit per embedding batch:

- `tokens_in` — sum of input tokens.
- `model` — for per-model attribution.
- `dollars_estimated` — `tokens_in × price_per_token` from a configured price table.
- `tenant_id` — for per-tenant cost attribution if multi-tenant.

Aggregate in the observability platform; report daily and monthly. A daily dashboard panel and a budget-threshold alert are the minimum.

## Disaster recovery

The vector store can be lost. Design for it:

- The relational DB is the source of truth.
- The bridge (see `chunking-and-bridge.md`) supports a "rebuild from scratch" path.
- The rebuild has a known runtime (measure it during a quiet period; document it in the runbook).
- The rebuild can be run into a side index without taking the live system down.

If the vector store is lost and the rebuild cannot complete inside the agreed RTO, degrade gracefully — fall back to keyword-only search or a "search temporarily unavailable" UX. Do not serve stale or partial vector results without disclosure.

## Sources

- `polyglot-persistence` — cost-model summary and observability signals.
- `observability-monitoring` — wiring the signals.
- `reliability-engineering` — DR planning and degradation paths.
