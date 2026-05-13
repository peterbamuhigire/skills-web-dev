# Vector Store Partitioning Tradeoffs — Reference

How each major vector store supports per-tenant isolation, with the tradeoffs.

## Pattern axes

- **Logical isolation**: namespaces / collections / partitions inside one instance.
- **Physical isolation**: separate instance per tenant.
- **Metadata-filter only**: one collection, `tenant_id` filter at query time.

## Per-engine map

### pgvector (Postgres)

- **Logical**: `tenant_id` column + composite index, or one schema per tenant.
- **Physical**: one Postgres database per tenant (silo deployment).
- **Best for**: small-to-mid tenant counts; teams already running Postgres; where transactional data and vectors share lifecycle.
- **Watch**: HNSW index size; per-tenant deletes are cheap; cross-tenant queries cheap but easy to write — guard via RLS.
- **Recommended**: enable Postgres Row Level Security with `tenant_id` policy. Even if a query forgets the filter, RLS catches it.

### Pinecone

- **Namespaces** are first-class per-index; use one namespace per tenant.
- Limits: total namespaces per index can be large but check tier. Pinecone serverless has different limits.
- **Strong** at namespace-scoped queries.
- **Weak** for moving a tenant out (export → reimport).

### Qdrant

- **Collections** per tenant for clear isolation; or single collection with payload filter.
- Recent versions support **multi-tenant collections** with payload-based partitioning that the engine optimises.
- **Best for** mid scale with clear per-tenant volumes.

### Weaviate

- **Multi-tenancy mode** (v1.20+) — first-class tenant abstraction inside a class. Each tenant has its own shard. Strong isolation; supports per-tenant offload / hot/cold.
- **Recommended** when you need 1k+ tenants and want logical-with-physical-tendencies.

### Milvus

- **Partitions** inside a collection (limited count) or **databases** for stronger isolation.
- Multi-tenant strategies vary by version; recent versions add partition-key based routing.

### OpenSearch / Elasticsearch (with vector field)

- **Indexes per tenant** (silo-on-shared-cluster) or single index + filter.
- Per-tenant indexes scale poorly past ~1000 tenants (shard count explosion); use index aliases + ILM.

### Vespa

- **Tenants** as a content cluster concept; mature multi-tenant support.

## Decision matrix

| Tenants count | Sensitivity | Recommended engine + pattern |
|---|---|---|
| < 50, low | low | pgvector single collection + tenant_id filter + RLS |
| < 50, mid-high | mid | pgvector schema-per-tenant or Weaviate multi-tenancy |
| 50–500, mid | mid | Weaviate multi-tenancy, or Qdrant collection-per-tenant |
| 500–5000, mid | mid | Pinecone namespaces, Weaviate multi-tenancy |
| > 5000, mixed | mixed | Pinecone namespaces or Weaviate; consider sharding by region |
| Any, regulated tenant | high | dedicated index/instance per tenant; per-region; BYOK on at-rest store |

## Migration paths

- Start single index with `tenant_id` filter → migrate to namespaces once you have > ~20 paying tenants OR your first enterprise.
- Start namespaces → migrate enterprise tenants to dedicated indexes when contract requires.
- Plan the **export/import** path early — a per-tenant export of vectors + metadata is the unit you move between patterns.

## Cost tradeoffs

- Per-tenant indexes: highest fixed cost, simplest reasoning, easiest deletion (drop index).
- Namespaces: shared infrastructure cost, low marginal per-tenant cost, namespace cap to watch.
- Single index + filter: lowest cost, weakest isolation, highest test burden.

## Always do, regardless of engine

- `tenant_id` in metadata of every vector and required on every query.
- Per-tenant ingestion concurrency limit (one tenant's bulk reindex doesn't starve others).
- Per-tenant retrieval timeout.
- Validate retrieved chunks' `tenant_id` against the request tenant in feature code as a final assertion.
- Backups segmented per tenant (or restorable per tenant).
