# Chunking and the Relational ↔ Vector Bridge — Deep Dive

Companion to `SKILL.md` §4 and §5.

## Chunking strategies in depth

### Fixed-size by tokens

Default starting point. Pick a chunk size that comfortably fits inside your model's context window when the LLM sees the retrieved chunks. 800 tokens with 100-token overlap is a sane baseline for general English text. The LangChain RAG tutorial (`docs.langchain.com/oss/python/langchain/rag`, fetched 2026-05-01) uses 1000 characters with 200-character overlap and produces 66 splits from a sample blog post.

Wins on: heterogeneous documents, fast bring-up, low storage overhead.
Loses on: documents with strong section structure (manuals, knowledge bases), dialogue, code.

### Semantic / heading-bounded

Split at structural boundaries: H1/H2 in Markdown, paragraph in HTML, sentence boundaries from spaCy or NLTK. Chunk size becomes variable. Pre-process: discard chunks below a minimum token count (say 50) by merging into the next; cap chunks above a maximum by recursive splitting.

Wins on: structured documents (technical manuals, policies, knowledge bases).
Loses on: free-form prose with weak structure.

### Hierarchical / parent-child

Embed small chunks (paragraphs or sentences) for retrieval; on a hit, return the larger parent chunk (section or page) to the LLM. Storage roughly doubles, but retrieval precision improves and synthesis context is preserved.

LlamaIndex's production-RAG guidance (`developers.llamaindex.ai/python/framework/optimizing/production_rag/`, fetched 2026-05-01): "The optimal chunk representation for retrieval might be different than the optimal consideration used for synthesis." Embed document summaries or sentence windows for retrieval, then synthesise from a different (larger) chunk.

### Sentence-window

Embed each sentence; on a hit, return the sentence plus N neighbouring sentences. High precision on dense prose (legal, medical, scientific). Index size grows linearly in sentences — verify the storage and embedding-cost impact at corpus scale.

## The relational ↔ vector bridge

The bridge is the application code that keeps embeddings synchronised with the relational source of truth.

### Lifecycle

1. **Source change captured.** Either via a domain event (`article.updated(id=42)`) emitted by the application after the relational write, or via a CDC stream from the database.
2. **Worker consumes the event.** The worker fetches the latest row from the relational DB by primary key. Do not embed from the event payload alone — the event is a trigger, not a source of truth.
3. **Chunk and embed.** Apply the chunking strategy. Compute a content hash per chunk; skip chunks whose hash has not changed since the last run.
4. **Upsert to the vector store.** Each chunk carries the payload `{ source_id, tenant_id, chunk_index, updated_at, content_hash }`. The vector point ID is deterministic from `(source_id, chunk_index)` so re-runs are idempotent.
5. **Reconcile chunk count.** If the new chunking produced fewer chunks than last time, delete the surplus chunks for `source_id`. The simplest pattern is delete-then-insert per `source_id`; the more efficient pattern is upsert-by-`chunk_index` with a final delete of indices above the new count.

### Failure modes

- **Ghost retrieval.** The relational row is deleted but its vector chunks remain. Retrieval returns content for a record that no longer exists. Mitigation: emit a `source.deleted` event and delete by `source_id`, OR mark a tombstone column on the source and have the bridge worker reap on schedule.
- **Embedding API outage.** The bridge worker cannot reach the embedding provider. Mitigation: queue the events with a durable queue (RabbitMQ, SQS, Postgres-backed); never block the relational write on the embedding API.
- **Drift.** The vector store's `updated_at` lags the relational `updated_at`. Mitigation: emit `staleness = NOW() - vector_updated_at` as a percentile metric, alert when p95 exceeds the freshness budget.
- **Mixed-model corpus.** A model migration that is rolled out partially leaves the corpus split across two embedding models. Queries embedded with one cannot rank documents embedded with the other. Mitigation: full re-embed in a side index, atomic switch.

### Reindex from scratch

The bridge must support a "rebuild the entire vector store from the relational DB" path. This is the disaster-recovery story: if the vector store is lost or corrupted, the relational DB plus the embedding pipeline can rebuild it.

Pattern: a CLI or admin endpoint that iterates the source table by primary key in batches, calls the bridge's per-row embed function, and writes to a fresh side index. Switch reads to the new index atomically (alias swap, namespace swap, or `ALTER TABLE ... RENAME` for pgvector).

## Sources

- LangChain RAG tutorial — `docs.langchain.com/oss/python/langchain/rag`.
- LlamaIndex production-RAG — `developers.llamaindex.ai/python/framework/optimizing/production_rag/`.
