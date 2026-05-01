# Vector Engine Selection — Deep Dive

Companion to `SKILL.md` §9.

## Decision rubric

Walk the rubric in order. Stop at the first match.

1. **Already running PostgreSQL and the workload fits a single DB process?** Use `pgvector`. Tenant isolation via RLS is the strongest guarantee available. SQL joins between source rows and vector results are a real win.
2. **Multi-modal (text + image) is a real requirement, not a nice-to-have?** Use `Weaviate`. Native multi-modal modules. GraphQL API.
3. **Self-hosting on Kubernetes is acceptable and the team wants an open-source dedicated engine?** Use `Qdrant`. Apache 2.0, mature HNSW, payload indexes for tenant filters, snapshot-based backups.
4. **Managed-only requirement (no self-host capacity, no PostgreSQL appetite)?** Use `Pinecone`. Namespaces map cleanly to tenants. Managed serverless model.
5. **Local development or prototyping only?** Use `Chroma`. Not the engine default for production.

## Per-engine notes

### Pinecone

Concepts (verified at `docs.pinecone.io/guides/get-started/overview`, fetched 2026-05-01):

- **Indexes** — dense, sparse, or both. Sparse indexes power BM25-style keyword retrieval natively.
- **Namespaces** — the multi-tenant primitive. "Use namespaces to partition data for faster queries and multitenant isolation between customers."
- **Metadata filtering** — for non-tenant axes (doc type, date, source).
- **Upsert/query API** — point IDs are client-supplied; deterministic IDs from `(source_id, chunk_index)` give idempotent upserts.

Strengths: zero-ops, hybrid search built-in, namespace isolation, predictable latency.
Weaknesses: proprietary, vendor lock-in, cost scales with vector count and query volume.

### Qdrant

Concepts (verified at `qdrant.tech/documentation/concepts/collections/`, fetched 2026-05-01):

- **Collections of points.** Each point = `{ id, vector, payload }`.
- **Payload indexes.** Required for fast filtering on payload fields. Without an index, payload filters are linear scans.
- **Named vectors.** Multiple vector fields per point (e.g., dense + sparse, or two embedding models).
- **HNSW under the hood** with configurable distance metric.

Distance options: Dot, Cosine, Euclid, Manhattan. The docs note: "Cosine similarity is implemented as dot-product over normalized vectors. Vectors are automatically normalized during upload."

Strengths: open-source (Apache 2.0), strong self-host story, hybrid search, snapshots, runs on Kubernetes well.
Weaknesses: ops burden vs managed, no built-in RBAC story (handle at the application layer).

### Weaviate

Concepts (verified at `docs.weaviate.io/weaviate/concepts`, fetched 2026-05-01): inverted indexes, ANN indexing via HNSW with configurable distance metrics, vector quantisation for storage compression, and "filtered vector search combining HNSW with inverted indexes for high-recall, rapid queries". Modules (vectorisers) and multi-modal capabilities are referenced in the broader Weaviate docs; verify class shapes before shipping code.

Strengths: native multi-modal, GraphQL, modules ecosystem.
Weaknesses: heavier than Qdrant or pgvector for text-only workloads; the schema/class abstraction is opinionated.

### Chroma

Verbatim getting-started snippet (`docs.trychroma.com/docs/overview/getting-started`, fetched 2026-05-01):

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

The docs note: "Chroma will embed this for you" — Chroma calls the embedding API itself by default.

Strengths: simplest API in the comparison, excellent for local development, zero setup.
Weaknesses: not the engine default for production. Hybrid search is limited. Multi-tenant primitives are coarse.

### pgvector

See `postgresql-patterns` §5 for SQL syntax. The use cases:

- Team is already operating PostgreSQL.
- The workload fits a single DB process.
- Tenant isolation via RLS is required.
- Cross-table joins between source rows and vector results are valuable.

Strengths: one DB process, RLS-enforced tenant isolation, ACID, transactional writes alongside source rows, mature ops story.
Weaknesses: scaling is bound by the PostgreSQL instance; very large indexes (tens of millions of vectors) push toward dedicated engines; hybrid search via tsvector requires more code than dedicated engines provide.

## Cost model summary

Across all five engines, embedding generation dominates total cost, not the vector store. The vector store cost differences matter only at scale. Optimise embedding cost first (hash-and-skip, right-size the model, reduce dimensions); revisit engine cost only when a representative load test shows the engine itself is the bottleneck.

## Sources

- Pinecone — `docs.pinecone.io/guides/get-started/overview`.
- Qdrant — `qdrant.tech/documentation/concepts/collections/`.
- Weaviate — `docs.weaviate.io/weaviate/concepts`.
- Chroma — `docs.trychroma.com/docs/overview/getting-started`.
- pgvector — `github.com/pgvector/pgvector` (cited via `postgresql-patterns`).
