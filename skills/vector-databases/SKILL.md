---
name: vector-databases
description: Use when adding semantic similarity search alongside a relational source-of-truth — choosing between pgvector / Qdrant / Pinecone / Weaviate / Chroma, generating embeddings in production, chunking, multi-tenant isolation, hybrid search with RRF, cross-encoder reranking, freshness, and embedding cost management.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Vector Databases — Semantic Search Beside the Source of Truth
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Adding semantic similarity search to an application whose source of truth lives in MySQL or PostgreSQL.
- Choosing between pgvector, Qdrant, Pinecone, Weaviate, and Chroma for a specific workload.
- Designing the bridge that keeps embeddings synchronised with relational rows.
- Implementing hybrid search (vector + BM25) with Reciprocal Rank Fusion and cross-encoder reranking.
- Enforcing multi-tenant isolation in a vector store and reasoning about pre-filter vs post-filter recall.
- Controlling embedding-API spend on a real corpus.

## Do Not Use When

- Building the RAG application logic, prompt construction, or end-to-end answer evaluation — use `ai-rag-patterns` and `rag-implementation`.
- Re-teaching pgvector DDL — `postgresql-patterns` §5 owns that.
- Training a custom embedding model from scratch.

## Required Inputs

- Source-of-truth data model (tables, primary keys, tenant column) and the corpus that needs to be searchable.
- Tenancy model (single-tenant, pooled-with-tenant-id, silo-per-tenant).
- Latency budget (p95 query) and freshness budget (max time from row update to embedding visible).
- Embedding-API budget (USD/month) and an estimate of tokens-per-document and write rate.
- Existing stack: PostgreSQL or MySQL, whether Kubernetes is available, whether managed services are acceptable.

## Workflow

1. Read this `SKILL.md` first; load the matching reference file only when a task needs that depth.
2. Pick the engine using the §9 decision matrix and the `references/engine-selection.md` rubric — do not start coding until the engine is chosen.
3. Design the relational ↔ vector bridge (§5) before any embedding code is written; the upsert lifecycle, deletion path, and staleness metric are non-negotiable.
4. Implement the embedding pipeline (§3) with batching, exponential-backoff retry with jitter, tokeniser, and cost telemetry.
5. Implement multi-tenant isolation (§6) with pre-filter semantics and a tenant-leakage test.
6. Add hybrid search and reranking (§7, §8) only when vector-only retrieval evaluation justifies the added latency.
7. Wire the four production signals (§10) into `observability-monitoring` before declaring the feature ready.

## Quality Standards

- Every vector query in a multi-tenant system carries a tenant filter; cross-tenant leakage is a security incident.
- Embedding API calls always batch, always retry with jitter, always tokenise before sending.
- Source rows and vector chunks are reconcilable: every chunk carries `source_id`, `tenant_id`, `chunk_index`, `updated_at`.
- Index rebuilds are atomic (alias/namespace swap or `CREATE INDEX CONCURRENTLY`); a rollback path exists.
- Cost telemetry is visible per day; embedding spend dominates total cost and is the primary lever to manage.
- Numbers cited from vendors (pricing, dimensions, model names) are re-verified at the vendor docs before shipping.

## Anti-Patterns

- Replacing the relational source of truth with a vector database. The vector store is a derived index of meaning, allowed to be eventually consistent.
- Post-filtering tenant boundaries (ANN first, drop out-of-tenant after). Recall collapses on selective tenants and leakage risk rises.
- Choosing the embedding model by benchmark only, ignoring per-1M-token cost on the actual corpus volume.
- Re-embedding every row on every job run. Hash the source text and skip when unchanged.
- Skipping the reranker stage when the corpus has homonyms, technical terms, or paraphrase-heavy queries — and skipping it when latency does not need it.
- Treating Chroma as a production engine. It is excellent for local development and prototyping; it is not the engine default for production workloads.
- Citing benchmark or pricing numbers from training data. Vendor specs change; re-verify at the docs.

## Outputs

- An engine selection memo grounded in the §9 matrix and the project's tenancy, hosting, and stack constraints.
- A bridge design covering the upsert lifecycle, deletion handling, and the staleness metric.
- Embedding pipeline code with batching, retry, idempotency, and cost telemetry hooks.
- Tenant-isolation test (pre-filter recall + cross-tenant leakage check) that runs in CI.
- Hybrid-search and reranking configuration justified by an evaluation result, not by reflex.
- Observability dashboards covering write latency, query latency (vector vs rerank stage split), recall@k, and freshness staleness.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Retrieval evaluation report | Markdown with recall@k and p95 latency on a fixed eval set | `docs/ai/vector-eval-2026-05.md` |
| Data safety | Multi-tenant isolation test report | Markdown describing pre-filter pattern and a leakage test result | `docs/ai/vector-tenancy.md` |
| Cost | Embedding spend baseline | CSV or table of tokens-per-day and USD-per-day | `docs/ai/embedding-cost-baseline.csv` |
| Operability | Bridge runbook | Markdown covering reindex, ghost-chunk reaping, and rollback | `docs/runbooks/vector-bridge.md` |

## References

- `references/embeddings-and-models.md` — §2, §3 depth: dimensions, normalisation, model trade-offs, batch sizing, tokenisation.
- `references/chunking-and-bridge.md` — §4, §5 depth: chunking strategies, parent-child, the relational ↔ vector bridge lifecycle.
- `references/hybrid-and-rerank.md` — §6, §7, §8 depth: pre-filter vs post-filter, RRF fusion, cross-encoder pipeline.
- `references/engine-selection.md` — §9 depth: per-engine notes for Pinecone, Qdrant, Weaviate, Chroma, pgvector with quoted vendor concepts.
- `references/production-and-cost.md` — §10, §11 depth: index lifecycle, freshness, monitoring, cost levers.
<!-- dual-compat-end -->

## Overview

A vector database stores fixed-length numerical vectors and answers "find the k vectors closest to this one" in sub-linear time. In production it sits **beside** the relational source of truth, not in front of it. MySQL or PostgreSQL holds orders, users, and authorisation; the vector store holds embeddings of derived text and is keyed back to the relational primary key. The vector store is allowed to be eventually consistent because it can always be rebuilt from the source of truth by re-embedding.

The cost dominance to remember: across every realistic option, **embedding generation is the dominant cost, not the vector store itself**. Optimise embedding spend first.

---

## §1 The Polyglot Framing

The relational database holds the source of truth: orders, users, RBAC, audit trail. The vector store holds derived indexes of meaning. The architecture diagram from `polyglot-persistence` is the canonical figure: writes go to the relational DB, an event or worker generates embeddings asynchronously, the vector store is keyed back to the relational primary key. Worst case, the vector store is dropped and rebuilt from the relational DB.

Do not propose replacing the relational DB with a vector store. Vector stores have weak transactional guarantees, no foreign keys, and no row-level constraints. They are an index, not a system of record.

---

## §2 Embeddings 101

An embedding is a fixed-length numerical vector that encodes the meaning of a piece of text (or image, or audio). Texts with similar meanings have vectors that are close to each other under a chosen distance metric — typically **cosine similarity** for L2-normalised vectors.

For L2-normalised vectors (||v|| = 1), cosine similarity equals the dot product, and ranking by cosine equals ranking by Euclidean. Several vendors return L2-normalised vectors; verify normalisation behaviour at the vendor docs before assuming it.

Common model families (re-verify model names, dimensions, and pricing at the vendor docs before publishing — these change quickly):

| Model family | Provider | Dimensions (typical) | Notes |
|---|---|---|---|
| text-embedding-3-small | OpenAI | 1536 (resizable) | Sensible default for general English text |
| text-embedding-3-large | OpenAI | 3072 (resizable) | Higher quality, higher cost |
| Cohere embed-v3 | Cohere | 1024 typical | Strong multi-language support |
| Voyage embeddings | Voyage AI | varies | Strong on retrieval benchmarks per vendor claims |
| BGE / E5 | Open-source (HuggingFace) | 384 / 768 / 1024 | Self-hosted; free at inference time |

Choose by: language coverage, retrieval quality on a held-out evaluation set drawn from your corpus, per-1M-token cost at projected volume, and whether self-hosting is acceptable.

Depth: `references/embeddings-and-models.md`.

---

## §3 Embedding Generation in Production

The reference loop. Treat as pseudocode and verify SDK shapes against the current SDK before use.

```python
from openai import OpenAI
import time, random

client = OpenAI()

def embed_batch(texts: list[str], model: str = "text-embedding-3-small"):
    for attempt in range(5):
        try:
            resp = client.embeddings.create(model=model, input=texts)
            return [e.embedding for e in resp.data]
        except RateLimitError:
            time.sleep((2 ** attempt) + random.random())
    raise RuntimeError("embedding retries exhausted")
```

Required patterns:

- **Batch.** Per-request overhead dominates without batching. Typical batches are 100–512 inputs depending on total tokens per request.
- **Retry with exponential backoff and jitter.** Rate limits are common; never retry without jitter.
- **Tokenise before sending.** Vendors charge per token and enforce per-input token limits. Use `tiktoken` for OpenAI; the equivalent for other vendors per their docs.
- **Idempotency keys** when supported, so duplicate retries do not double-charge.
- **Cost telemetry.** Track tokens-per-request and dollars-per-day in `observability-monitoring`.

Depth: `references/embeddings-and-models.md`.

---

## §4 Chunking Strategies

The chunking decision dominates retrieval quality more than the choice of vector store.

| Strategy | How | Wins on | Loses on |
|---|---|---|---|
| Fixed-size by tokens | e.g. 800-token chunks, 100-token overlap | Most documents; fast to implement | Cuts mid-sentence; loses heading context |
| Semantic / heading-bounded | Split at H1/H2 (Markdown), paragraph (HTML), sentence (NLTK/spaCy) | Structured docs (knowledge bases, manuals) | Highly variable chunk sizes |
| Hierarchical / parent-child | Embed small chunks for retrieval; return parent to LLM | Long-form documents needing context | Storage and bookkeeping overhead |
| Sentence-window | Embed each sentence; return sentence + N neighbours | High-precision QA on dense prose | Index size grows linearly |

The LangChain RAG tutorial (`docs.langchain.com/oss/python/langchain/rag`, fetched 2026-05-01) uses fixed-size chunks of 1000 characters with 200-character overlap as the starting baseline, producing 66 splits from a sample blog post. The default is reasonable; the tuning is corpus-specific.

LlamaIndex's production-RAG guidance (`developers.llamaindex.ai/python/framework/optimizing/production_rag/`, fetched 2026-05-01) recommends decoupling retrieval and synthesis chunks: "The optimal chunk representation for retrieval might be different than the optimal consideration used for synthesis." Embed document summaries or sentence windows for retrieval, then synthesise from a different (larger) chunk.

Depth: `references/chunking-and-bridge.md`.

---

## §5 The Relational ↔ Vector Bridge

This is the engineering heart of the polyglot pattern. The bridge is the application code that, when a domain object changes in the relational DB, recomputes its embedding and writes it to the vector store keyed back to the relational primary key.

Minimum viable bridge:

1. Domain event published (or app-level write hook) — `article.updated(id=42)`.
2. Consumer fetches the row from the relational DB by id.
3. Consumer chunks and embeds the relevant text.
4. Consumer upserts each chunk into the vector store with payload `{ source_id: 42, tenant_id, chunk_index, updated_at }`.
5. Old chunks for `source_id = 42` are deleted before new ones are written, OR replaced atomically by `chunk_index`.

Failure modes to design for:

- **Ghost retrieval.** Source row deleted but vector chunks remain. Serve a tombstone flag and reap on schedule, or use cascade deletes via a worker subscription.
- **Embedding API outage.** Queue with retry; do not block the relational write.
- **Drift between source `updated_at` and vector `updated_at`.** Expose `staleness = NOW() - vector_updated_at` as an observability signal.

Depth: `references/chunking-and-bridge.md`.

---

## §6 Metadata Filtering and Multi-Tenant Isolation

Every vector query in a multi-tenant system carries a tenant filter. Cross-tenant retrieval leakage is a security incident, not a quality incident.

**Pinecone** (concept from `docs.pinecone.io/guides/get-started/overview`, fetched 2026-05-01): "Use namespaces to partition data for faster queries and multitenant isolation between customers." Namespace per tenant is the recommended pattern; metadata filtering is the secondary tool.

```python
index.query(
    namespace=f"tenant-{tenant_id}",
    vector=query_embedding,
    top_k=10,
    filter={"doc_type": {"$eq": "article"}},
    include_metadata=True,
)
```

**Qdrant** (`qdrant.tech/documentation/concepts/collections/`, fetched 2026-05-01): collections hold points (vector + payload). Multi-tenant pattern: a single collection with a `tenant_id` payload field and a payload index on it (best for many small tenants), or a collection per tenant (best for few large tenants).

```python
from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333")

client.create_collection(
    collection_name="{collection_name}",
    vectors_config=models.VectorParams(size=100, distance=models.Distance.COSINE),
)
```

Distance options per Qdrant docs: Dot, Cosine, Euclid, Manhattan. The docs note: "Cosine similarity is implemented as dot-product over normalized vectors. Vectors are automatically normalized during upload."

**pgvector** (per `postgresql-patterns` §5): tenant filter is a SQL `WHERE tenant_id = $tenant`. Supabase RLS enforces it at the database layer; this is the strongest guarantee of the five engines.

**Pre-filter vs post-filter.** Pre-filter applies the metadata filter before the ANN search — most relevant matches inside the filter; recall preserved. Post-filter does the ANN search first, then drops out-of-tenant results — recall collapses if the filter is selective. Pinecone and Qdrant pre-filter natively. Verify behaviour at index-type and version edges before relying on recall numbers.

Depth: `references/hybrid-and-rerank.md`.

---

## §7 Hybrid Search

Vector search captures semantic similarity but loses on exact keywords (product codes, technical terms, named entities). BM25 wins on those. Hybrid search runs both and fuses the rankings.

**Reciprocal Rank Fusion (RRF)** is the standard fusion technique because it does not require score calibration between systems:

```
RRF_score(d) = Σ_i  1 / (k + rank_i(d))
```

where `rank_i(d)` is document `d`'s rank in retrieval system `i`, and `k` is a small constant (typically 60).

When keyword wins: exact-match SKUs, error codes, person names, identifiers, regex-style queries. When vector wins: paraphrase, conceptual questions, fuzzy intent, multilingual.

Anthropic's Contextual Retrieval (`anthropic.com/news/contextual-retrieval`, fetched 2026-05-01) reports: "Contextual Embeddings alone … reduced the top-20-chunk retrieval failure rate by 35% (5.7% → 3.7%)" and the combined contextual-embedding + contextual-BM25 approach "reduced the top-20-chunk retrieval failure rate by 49% (5.7% → 2.9%)". Implementation detail belongs in `rag-implementation`; this skill records the result — hybrid + context beats vector-only.

Depth: `references/hybrid-and-rerank.md`.

---

## §8 Re-ranking

The two-stage pipeline:

1. **Retrieve.** Pull top-100 candidates by vector similarity (or hybrid).
2. **Rerank.** Score each candidate against the exact query with a cross-encoder; keep top-10.

Bi-encoders (the embedding models that produced the index) compress query and document independently and lose interaction information. Cross-encoders score (query, document) jointly — far more accurate per item but far too slow over the whole corpus. Run the cheap retriever first, the expensive reranker on a shortlist.

Reranker options:

- Cohere Rerank (managed API; `cohere.com/rerank`).
- BGE reranker (open-source on HuggingFace; self-host on CPU/GPU).
- Voyage rerank (managed API).

Anthropic's Contextual Retrieval blog (fetched 2026-05-01): "with reranking added … reduced the top-20-chunk retrieval failure rate by 67% (5.7% → 1.9%)".

Reranking adds latency (typically 100–500 ms for a shortlist of 100; verify against your reranker, do not invent numbers). Cost: per-token API for managed; GPU/CPU for self-hosted.

Depth: `references/hybrid-and-rerank.md`.

---

## §9 Vector Store Comparison

Decision matrix. Re-verify pricing and limits at vendor docs before publishing.

| Property | Pinecone | Qdrant | Weaviate | Chroma | pgvector |
|---|---|---|---|---|---|
| Hosting | Managed only | Self-host or cloud | Self-host or cloud | Local-first; managed available | Self-host (PostgreSQL) or Supabase |
| License (server) | Proprietary | Apache 2.0 | BSD-3 | Apache 2.0 | PostgreSQL licence |
| Multi-tenant primitive | Namespaces | Collections / payload partitions | Tenants / collections | Collections | Rows + RLS |
| Multi-modal | Text-first | Text + extension | Native multi-modal modules | Text-first | Text only |
| Hybrid search | Native (sparse + dense) | Native (sparse + dense) | Native | Limited | Vector + tsvector via SQL |
| Best fit | "Relational stays, add a managed vector service" | Self-hosted, open-source, no PG | Multi-modal, GraphQL teams | Local dev; small projects | Team prefers one DB process |
| Engine default? | Yes (managed default) | Yes (self-host default) | Specialist | Dev-only | Yes (when PG already in stack) |

**Engine preferences for this stack:**

- **pgvector** is preferred when the team already operates PostgreSQL (especially via Supabase) and the workload fits a single DB process. RLS gives the strongest tenant-isolation guarantee.
- **Qdrant** is preferred when self-hosting on Kubernetes is acceptable and the team wants an open-source dedicated engine. License is Apache 2.0; HNSW is mature.
- **Pinecone** is preferred when the team explicitly wants a managed service and self-hosting capacity is unavailable.
- **Weaviate** when multi-modal (text + image) is a real requirement.
- **Chroma** for local development and prototyping only — not the engine default for production.

Verbatim Chroma getting-started snippet (`docs.trychroma.com/docs/overview/getting-started`, fetched 2026-05-01):

```python
import chromadb
chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="my_collection")

collection.add(
    ids=["id1", "id2"],
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ]
)

results = collection.query(
    query_texts=["This is a query document about hawaii"],
    n_results=2
)
print(results)
```

The Chroma docs note: "Chroma will embed this for you" — Chroma calls the embedding API itself by default.

Depth: `references/engine-selection.md`.

---

## §10 Production Patterns

**Index lifecycle.** Vector indexes (HNSW especially) are not free to maintain on heavy-write workloads. Pattern: bulk-load a fresh index off-line, switch reads to it atomically (alias or namespace swap), keep the old one for rollback. Vendor-specific tooling: Pinecone collections, Qdrant snapshots, pgvector `CREATE INDEX CONCURRENTLY`.

**Freshness vs recall.** New writes that have not yet been embedded are invisible to retrieval — "freshness lag". Reduce by streaming the embedding pipeline (event-driven) rather than batch nightly. Track `staleness = NOW() - vector_updated_at` as a percentile metric.

Monitoring signals to wire into `observability-monitoring`:

- Embedding-write latency (p50, p95).
- Query latency (p50, p95) — separate vector and rerank stages.
- Recall@k against a held-out evaluation set (RAG-style; details in `rag-implementation`).
- Index-rebuild duration.
- Freshness staleness (time since the source row last changed vs vector last updated).

Depth: `references/production-and-cost.md`.

---

## §11 Cost Management

Embedding generation is the dominant cost. The vector store itself is secondary across every realistic option.

Cost levers, ordered by impact:

1. **Re-embed only what changed.** Hash the source text; skip embedding if the hash is unchanged.
2. **Right-size the model.** `text-embedding-3-small` is materially cheaper than `-large`. Move up only if evaluation justifies it.
3. **Reduce dimensions.** OpenAI 3-* embeddings support output truncation to a smaller dimension; storage and query speed improve roughly linearly. Verify against current vendor docs.
4. **Cache reranker calls.** Identical (query, doc) pairs can be cached.
5. **Negotiate volume pricing** above some threshold — vendor-specific.

Vector-store costs themselves vary by mode (managed metered vs self-host fixed). Embedding-API spend dominates total cost across all five engines on a representative SaaS load.

Depth: `references/production-and-cost.md`.

---

## §12 Cross-References

- `postgresql-patterns` §5 — pgvector SQL syntax (this skill calls into it, does not re-teach it).
- `rag-implementation` — RAG application logic using these primitives.
- `ai-rag-patterns` — conceptual RAG; this skill assumes that material.
- `observability-monitoring` — AI-workload signals (recall@k, staleness).
- `cicd-devsecops` — embedding-API key rotation.
- `kubernetes-platform` — running self-hosted Qdrant or Weaviate on Debian/Ubuntu Kubernetes.
