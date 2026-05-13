# Per-Tenant Ingestion Pipeline — Reference

The data-plane design for ingesting a tenant's documents into their KB partition.

## Pipeline stages

```
1. Source connector  → emits SourceItem events {tenant_id, source_id, item_id, fetch_hint}
2. Change detector   → compares against last_seen_hash; drops unchanged
3. Fetcher           → fetches the item (HTTP / SDK / S3 GET)
4. Parser            → extracts text + structure (PDF/HTML/Office/Markdown)
5. Chunker           → tier-specific; emits chunks with offsets + section context
6. Embedder          → batches calls to embedding model; tier-specific model
7. Indexer           → upserts vectors into tenant's namespace
8. Audit + cost      → emits ai.kb.ingest events
```

Each stage is an independent worker reading from a per-tenant queue and writing to the next.

## Tenant-aware queues

Per-tenant Redis lists or per-tenant routing keys in your broker:

```
ingest:fetch:t8421
ingest:parse:t8421
ingest:chunk:t8421
ingest:embed:t8421
ingest:index:t8421
```

A dispatcher round-robins across active tenants → shared worker pool, weighted by tier. One tenant's 1M-page backfill cannot drown a paying tenant's 50-page update.

## Idempotency

Key for each stored chunk:
```
(tenant_id, source_id, item_id, content_sha256, chunk_index)
```

Re-running the pipeline emits no duplicates. The indexer's upsert key matches.

## Change detection

Per source type:
- S3 / object storage: `Etag` + `LastModified`.
- HTML: `Last-Modified` / `ETag` headers; fall back to content hash.
- Notion / Drive: webhook deltas or `versionId`.
- DB-backed integration: timestamp watermark.

A `tenant_sources_state` table:

```sql
CREATE TABLE tenant_sources_state (
    tenant_id   BIGINT NOT NULL,
    source_id   VARCHAR(64) NOT NULL,
    item_id     VARCHAR(256) NOT NULL,
    content_sha256 CHAR(64),
    last_seen   DATETIME NOT NULL,
    bytes       BIGINT,
    PRIMARY KEY (tenant_id, source_id, item_id)
);
```

## Parser registry

Map extension/MIME → parser. Each parser:
- Returns `Document` with `text`, `sections[]`, `tables[]` (optional), `links[]`.
- Records parser version on each chunk.
- Errors are tenant-scoped; failure doesn't block other items.

Parsers to support out of the box: PDF (text + OCR fallback), HTML, Markdown, DOCX/XLSX/PPTX, plain text, code (preserves indentation), CSV/TSV.

## Chunker

Tier-specific (`SKILL.md` §3). Output:

```json
{
  "tenant_id": 8421,
  "source_id": "drive-A",
  "item_id": "doc_91",
  "chunk_index": 0,
  "text": "...",
  "tokens": 624,
  "section_path": ["Refund Policy", "Section 2"],
  "page": 4,
  "char_start": 1820,
  "char_end": 4988,
  "chunker_version": "semantic-v3"
}
```

## Embedder

Batched, model selected from `tenant_ai_binding.embedding_model_tier`. Records:
- Embedding model version on the chunk (for re-embed migration).
- USD cost per chunk for the cost ledger.

Backoff: provider rate limits hit → exponential backoff per tenant, not globally.

## Indexer

Upsert into the tenant's vector store partition. After the upsert, perform an **isolation assertion**: read back one chunk; confirm `tenant_id` metadata matches. Mismatch → roll back and alert.

## Cost & audit

Each ingestion run writes:

```sql
CREATE TABLE kb_ingest_runs (
    run_id       CHAR(26) PRIMARY KEY,
    tenant_id    BIGINT NOT NULL,
    source_id    VARCHAR(64) NOT NULL,
    items        INT NOT NULL,
    chunks       INT NOT NULL,
    tokens_embed BIGINT NOT NULL,
    usd_cost     DECIMAL(10,6) NOT NULL,
    started_at   DATETIME NOT NULL,
    finished_at  DATETIME NOT NULL,
    status       ENUM('ok','partial','failed') NOT NULL,
    errors_json  JSON
);
```

`ai.kb.ingest.completed` event is emitted; consumed by the cost ledger and the tenant's usage panel.

## Backfill / re-embed orchestration

```python
def re_embed_tenant(tenant_id, new_model):
    # 1. Provision parallel namespace
    new_ns = kb.provision_namespace(tenant_id, version="v2")
    # 2. Stream chunks from current namespace
    for chunk in kb.iter_chunks(tenant_id):
        new_vec = embedder.embed(chunk.text, model=new_model)
        kb.upsert(new_ns, chunk.id, new_vec, chunk.metadata)
    # 3. Side-by-side eval
    eval_result = eval_harness.run(
        feature="rag.answer", tenant=tenant_id,
        binding_override={"kb_partition_id": new_ns.id, "embedding_model": new_model}
    )
    if eval_result.is_regression():
        kb.delete_namespace(new_ns.id); raise
    # 4. Promote
    binding.update(tenant_id, kb_partition_id=new_ns.id, embedding_model=new_model)
    # 5. Schedule cleanup of old namespace in 30 days
```

## Failure handling

- Per-tenant DLQ for failed items; back-office can re-drive after fix.
- Persistent failures over a threshold pause the tenant's ingestion and alert.
- The pipeline never silently drops items; every drop is logged with reason.
