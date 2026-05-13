> Consolidated from skills/ai-rag-multi-tenant/SKILL.md into ai-rag-patterns on 2026-05-13. Load this through skills/ai-rag-patterns/SKILL.md, not as an active skill entrypoint.

# AI RAG Multi-Tenant
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building the per-tenant knowledge-base service for a SaaS RAG feature.
- Designing the ingestion pipeline that handles per-tenant sources, change detection, chunking, embedding, indexing, and erasure.
- Choosing chunking and embedding strategy per plan tier.
- Hardening retrieval against cross-tenant leakage with assertions and tests.
- Implementing citation UX that lets the user verify provenance per tenant.

## Do Not Use When

- The task is general RAG without multi-tenancy — `ai-rag-patterns`.
- The task is the vector-store choice axis — `ai-tenant-isolation-patterns/references/vector-store-partitioning-tradeoffs.md`.
- The task is the citation UX surface alone — `ai-hallucination-slo-and-grounding/references/grounding-and-citation-ux.md`.

## Required Inputs

- Tenant deployment model (`saas-deployment-models`).
- Vector store choice (see `ai-tenant-isolation-patterns`).
- Plan tiers and entitlements for KB size, embedding tier, retrieval depth.
- Source types per tenant (uploaded files, URL crawls, third-party integrations).

## Workflow

1. Read this `SKILL.md`.
2. Define the **KB service contract** (§1) — per-tenant API.
3. Design the **per-tenant ingestion pipeline** (§2): sources → chunker → embedder → index.
4. Choose **chunking strategy per tier** (§3).
5. Choose **embedding model per tier** (§4).
6. Design **retrieval security** (§5) — defence in depth.
7. Implement **citation grounding** (§6) for the answer path.
8. Wire **erasure** (§7) into the platform-wide erasure cascade.
9. Wire **operations** (§8) — backfills, re-embed, drift.
10. Apply anti-patterns (§9).

## Quality Standards

- The KB service refuses to operate without `tenant_id`. No anonymous methods.
- Every chunk carries `tenant_id` in metadata and the storage layer enforces the filter.
- Ingestion is idempotent per `(tenant_id, source_id, chunk_id)`.
- Per-tenant ingestion concurrency is bounded — one large reindex never starves others.
- Citation links resolve to the tenant's authoritative source, not the cached chunk.
- Erasure removes embeddings + source metadata + cached responses for a tenant in < 24h.

## Anti-Patterns

- Single collection + `tenant_id` filter as the only isolation. One bug = cross-tenant retrieval.
- Shared embedding queue with no tenant routing — a poisoned message lands in the wrong tenant.
- Same chunking parameters for all tiers — Free tier costs as much as Pro.
- Same embedding model for all tiers — overpays for free users, underpowers paid users.
- Retrieval cache keyed by query text only — cross-tenant cache hits.
- Citations that link to the cached chunk text, not the live source.
- No re-embed path when the embedding model upgrades.

## Outputs

- KB service API (per-tenant).
- Ingestion pipeline diagram + components.
- Chunking + embedding strategy per tier.
- Retrieval pipeline with defence-in-depth assertions.
- Citation UX contract.
- Erasure cascade integration.
- Re-embed / backfill runbook.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | KB service API | OpenAPI / Markdown | `docs/ai/kb-service.md` |
| Architecture | Ingestion pipeline | Diagram + Markdown | `docs/ai/kb-ingestion.md` |
| Release evidence | Tier strategy table | Markdown | `docs/ai/kb-tier-strategy.md` |
| Operability | Re-embed runbook | Runbook | `docs/runbooks/kb-re-embed.md` |

## References

- `references/per-tenant-ingestion-pipeline.md` — full ingestion design.
- `references/retrieval-security-patterns.md` — defence-in-depth at the query path.
- Companion: `ai-rag-patterns`, `ai-tenant-isolation-patterns`, `ai-on-saas-architecture`, `ai-hallucination-slo-and-grounding`, `ai-model-gateway`, `saas-tenant-data-portability-and-erasure`, `saas-rate-limiting-and-quotas`.

<!-- dual-compat-end -->

## §1 KB Service Contract

The KB service is a control-plane service. API (v1):

```
# Sources
POST   /kb/tenants/{tenant_id}/sources             create source (file upload, URL, integration)
GET    /kb/tenants/{tenant_id}/sources
DELETE /kb/tenants/{tenant_id}/sources/{id}

# Ingestion
POST   /kb/tenants/{tenant_id}/sources/{id}/ingest   trigger ingestion run
GET    /kb/tenants/{tenant_id}/ingestion/{run_id}    status

# Retrieval
POST   /kb/tenants/{tenant_id}/search                {query, top_k, filters?} → chunks[]

# Operations
DELETE /kb/tenants/{tenant_id}                       purge all (erasure)
POST   /kb/tenants/{tenant_id}/reembed               re-embed with current model
```

Tenant id is in the path; never in the body. The service refuses to operate without it.

## §2 Per-Tenant Ingestion Pipeline

```
Source connector ──> Change detector ──> Fetcher ──> Parser ──> Chunker ──> Embedder ──> Indexer
       │                   │                │           │           │             │           │
       └─ S3 / Notion       │            (HTTP/SDK)  (HTML/PDF)   (tier-       (tier-      (write
          / Drive /         └─ deltas only           /Office)     specific)   specific)    to vector
          web / app                                                                         store with
                                                                                            tenant_id)
```

Properties:
- **Tenant-aware queues**: each tenant has its own ingestion queue with per-tenant concurrency cap.
- **Idempotent**: re-running emits no duplicates. Key: `(tenant_id, source_id, content_hash, chunk_index)`.
- **Per-tenant rate**: a free tenant cannot block a paying one.
- **Failure isolated**: one tenant's parser error doesn't poison the shared dead-letter.
- **Audit**: every run records `(tenant_id, run_id, source_id, pages, chunks, embed_calls, cost, duration, errors)`.

See `references/per-tenant-ingestion-pipeline.md`.

## §3 Chunking Strategy per Tier

| Tier | Chunk size | Overlap | Strategy |
|---|---|---|---|
| Free | 800 tokens | 100 | naive fixed |
| Starter | 600 tokens | 150 | sentence-aware |
| Pro | 400–800 dynamic | 150 | semantic + heading-aware |
| Business | 400–800 + section titles | 200 | semantic + heading + table-aware |
| Enterprise | tuned per tenant | tuned | tuned + structured (code/tables/forms detected) |

Why differentiated: chunking quality drives retrieval quality drives faithfulness. Pay tiers earn a smarter chunker.

Implementation note: chunking strategy id is recorded on the chunk; mixing strategies in the same index is allowed if retrieval-aware.

## §4 Embedding Model per Tier

| Tier | Embedding model | Dimensions | Cost class |
|---|---|---|---|
| Free | small / open-source | 384 | low |
| Starter | mid commercial | 768 | low-mid |
| Pro | flagship commercial | 1024–1536 | mid |
| Business | flagship commercial + reranker (e.g., Cohere Rerank) | 1024–1536 | high |
| Enterprise | flagship + reranker + optional domain-tuned | varies | highest |

Re-embedding when the model upgrades is a major operation — see §8.

## §5 Retrieval Security (Defence in Depth)

Every retrieval enforces tenant scope at multiple layers:

1. **Auth scope**: caller's JWT has `tenant_id = X`.
2. **Path**: API path is `/kb/tenants/X/search`. Mismatch with JWT → 403.
3. **Engine filter**: query against namespace/collection `kb_t{X}` (not metadata filter alone).
4. **Metadata filter**: additionally `WHERE tenant_id = X` in the query payload — defence redundancy.
5. **Result assertion**: every returned chunk's `tenant_id` checked against X; mismatch → drop chunk, alert.
6. **Cache key**: retrieval cache keyed `t{X}:hash(query, params)`. Cross-tenant cache impossible.

See `references/retrieval-security-patterns.md`.

## §6 Citation Grounding

The answer path post-processes model output:

1. Model returns text + `citations[{id, chunk_id, supports}]`.
2. Post-processor verifies:
   - Every `chunk_id` is in the retrieved set for THIS request.
   - The `supports` substring is paraphrased from the chunk text (lexical/semantic overlap > threshold).
   - Every numeric `[n]` in the answer maps to a citation.
3. Failures → rewrite (drop unsupported claims) or abstain.
4. The UI renders citations linking to the **live source** (not the cached chunk), so the user sees the up-to-date document.

Source pointer schema per chunk:
```json
{
  "source_url": "https://docs.acme.com/refunds#section-2",
  "source_title": "Refund Policy",
  "source_doc_id": "doc_91",
  "source_section": "Section 2",
  "source_last_modified": "2026-03-10T..."
}
```

## §7 Erasure

When `saas-tenant-data-portability-and-erasure` runs the cascade for a tenant, the KB service receives `DELETE /kb/tenants/{tenant_id}`. It must:

1. Drop the vector store namespace/index for the tenant.
2. Delete source documents and parsed chunks from object storage.
3. Delete chunk metadata rows.
4. Delete retrieval cache entries (`SCAN MATCH t{tenant_id}:*`).
5. Delete conversation/RAG-trace rows associated with the tenant.
6. Confirm to the erasure orchestrator with proof (counts purged).

Backups: per the platform retention policy. Document the window.

## §8 Operations

### Backfill

When the embedding model upgrades (better quality, more dimensions):

1. Provision a parallel namespace `kb_t{X}_v2`.
2. Re-embed all chunks for tenant X with the new model into v2.
3. Run side-by-side eval on the tenant's goldens; promote v2 if metrics improve.
4. Switch reads to v2; keep v1 for 30 days for rollback; then purge.

### Tenant-scoped throttling

A bulk re-embed for one tenant must not affect other tenants' QPS. Per-tenant ingestion concurrency caps enforce this.

### Drift detection

Monitor:
- Retrieval recall on goldens, per tenant.
- Average citation-density per answer.
- Ratio of abstained answers.
- Cost per ingested page.

Alert on > 2-sigma shifts.

## §9 Anti-Patterns

- Source upload directly to the vector store from feature code — bypasses tenant routing and audit.
- Same chunker for free and enterprise — cost optimisation only; quality suffers.
- Embedding cache keyed by text only — same text from different tenants returns same cache entry (acceptable IF embedding model is identical AND tenant scope is enforced at retrieval). Be deliberate.
- Re-embed on every ingestion — wasteful; embed only changed chunks.
- Retrieval that returns "no results" silently — should abstain or escalate.
- Citation rendered as the chunk text snippet — must link to live source.
- Erasure deletes vectors but leaves cached responses.

## §10 Read Next

- `ai-tenant-isolation-patterns` — vector store partitioning + tests.
- `ai-rag-patterns` — general RAG techniques.
- `ai-hallucination-slo-and-grounding` — sets the citation/abstain bar.
- `ai-on-saas-architecture` — KB service positioning.
- `saas-tenant-data-portability-and-erasure` — receives the erasure call.
- `saas-rate-limiting-and-quotas` — per-tenant ingestion cap.


