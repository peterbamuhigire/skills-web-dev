# pgvector Deep Reference

All snippets are from the pgvector README at github.com/pgvector/pgvector v0.8.2 unless flagged as synthesis.

## Install on Debian/Ubuntu (PostgreSQL 13+ required)

```sh
sudo apt-get install -y build-essential postgresql-server-dev-all git
cd /tmp
git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

Enable per database:

```sql
CREATE EXTENSION vector;
```

## Storage and dimension limits

Each vector takes `4 * dimensions + 8 bytes`. Each element is a single-precision float. Maximum dimensionality is 16,000. For OpenAI `text-embedding-3-small` (1536 dims), a single row's vector is `4 * 1536 + 8 = 6152` bytes, so 1M embeddings is roughly 6 GB before index overhead.

## Distance operators

| Operator | Distance | Use when |
|---|---|---|
| `<->` | L2 (Euclidean) | Default for unit-norm or arbitrary embeddings |
| `<#>` | Negative inner product | Maximum-similarity ranking on normalised vectors |
| `<=>` | Cosine | Direction-only similarity; standard for OpenAI text embeddings |
| `<+>` | L1 (taxicab) | Sparse or count-based vectors |
| `<~>` | Hamming | Binary vectors |
| `<%>` | Jaccard | Binary set vectors |

For L2-normalised embeddings (OpenAI `text-embedding-3-*`), cosine and inner product produce equivalent rankings.

## Schema for an embeddings table

```sql
CREATE TABLE items (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id BIGINT NOT NULL,
  source_id BIGINT NOT NULL,             -- FK back to MySQL source row
  embedding vector(1536) NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX items_tenant_idx ON items (tenant_id);
CREATE INDEX items_metadata_gin ON items USING GIN (metadata);
```

## HNSW

```sql
CREATE INDEX CONCURRENTLY items_embedding_hnsw
ON items USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

Knobs:

- `m`: graph connectivity. Higher = better recall, more memory and build time. Default 16 is fine for most.
- `ef_construction`: build-time search width. Higher = better index quality, slower build. Default 64.
- `ef_search`: query-time search width. Set per session: `SET hnsw.ef_search = 100;`. Raise to trade latency for recall.

HNSW supports `CREATE INDEX CONCURRENTLY` so you can build it without blocking writes.

## IVFFlat

```sql
CREATE INDEX items_embedding_ivf
ON items USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);
```

Rule of thumb: `lists` approximately rows/1000 for under 1M rows; `sqrt(rows)` for larger sets. Build the index after the data is loaded so centroids reflect real distribution. Tune `probes` per session: `SET ivfflat.probes = 10;`.

## Operator class must match the query operator

`vector_l2_ops` works only with `<->`. `vector_cosine_ops` works only with `<=>`. `vector_ip_ops` works only with `<#>`. If the operator class does not match, the planner falls back to a sequential scan and you will see no error, just slow queries.

## Top-k query with metadata pre-filter

```sql
SELECT id, source_id, 1 - (embedding <=> $1) AS similarity
FROM items
WHERE tenant_id = $2
  AND metadata @> '{"doc_type":"article"}'::jsonb
ORDER BY embedding <=> $1
LIMIT 10;
```

The B-tree on `tenant_id` and the GIN on `metadata` are still required. Vector indexes do not eliminate metadata indexes.

## When to choose an external vector store instead

Use pgvector when the team already runs PostgreSQL and the embedding count fits comfortably in memory (typically up to a few million vectors for HNSW). Move to Pinecone, Qdrant, or Weaviate when you need cross-region replication of the vector index, multi-modal embeddings, or hybrid search with built-in BM25 + dense ranking. See `vector-databases`.
