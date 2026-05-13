# Retrieval Security Patterns — Reference

Defence-in-depth at the retrieval path so a single bug cannot leak chunks across tenants.

## Layer 1 — Auth scope

The caller's JWT carries `tenant_id`. The KB service uses ONLY this value; the path is `/kb/tenants/{tenant_id}/search` and the path id must match the JWT id. Mismatch → 403.

```python
def assert_path_tenant_matches_auth(path_tenant_id, jwt_tenant_id):
    if path_tenant_id != jwt_tenant_id:
        raise PermissionError("tenant_id mismatch")
```

## Layer 2 — Engine namespace, not just filter

Whenever the engine supports it (Pinecone namespace, Weaviate tenant, Qdrant collection-per-tenant, Postgres schema-per-tenant), use the **namespace boundary** as the primary partition. A namespace-scoped query cannot return rows from another namespace, by construction.

Per-collection filter (`WHERE tenant_id = ?`) is a **second** line, not the primary.

## Layer 3 — Result-set validation

Every chunk returned has `tenant_id` in metadata. The retrieval client asserts:

```python
for chunk in results:
    if chunk.metadata["tenant_id"] != ctx.tenant_id:
        metrics.incr("retrieval.tenant_mismatch")
        alerts.emit("ai.retrieval.bleed", tenant=ctx.tenant_id,
                    rogue=chunk.metadata["tenant_id"], chunk_id=chunk.id)
        raise PermissionError("retrieval returned wrong-tenant chunk")
```

The alert pages on-call; assume incident and run the quarantine playbook.

## Layer 4 — Tenant-keyed retrieval cache

Cache keys include the tenant id:

```python
key = f"retr:t{tenant_id}:{sha256(query + str(params))}"
```

Never share retrieval-cache entries across tenants, even when query text is identical. The cost of re-embedding the query is small; the cost of a leak is unbounded.

## Layer 5 — Query-rewrite safety

When the query is rewritten by an LLM (e.g., HyDE, query expansion):
- Rewriting runs through the gateway as a normal AI request — tenant-scoped, audited, cost-attributed.
- The rewritten query is used ONLY for retrieval; it is not displayed to the user as the model's "thought".
- Rewriter cannot insert tenant ids or filters into the query.

## Layer 6 — Tool-use guard

If the model is allowed to call a `search_kb` tool:
- Tool implementation hard-codes the `tenant_id` from the calling context.
- Tool **ignores** any tenant_id argument the model passes; logs an attempt as a safety event.

```python
def search_kb_tool(query: str, context):
    # NOTE: tenant_id is from context, NOT from the model
    return kb.search(context.tenant_id, query, top_k=context.entitlements.top_k)
```

## Layer 7 — Logs / traces redaction

Retrieval traces carry chunk ids and scores, not chunk text. Chunk text goes in the audit S3 payload (encrypted with the tenant's KEK), not in spans or logs.

## Layer 8 — Tests

The data-bleed test suite (`ai-tenant-isolation-patterns/references/data-bleed-test-suite.md`) covers retrieval-specific tests:
- Marker token retrieval (cross-tenant marker must not appear).
- Forced kb_partition_id IDOR.
- Cache poisoning.

CI runs these on every PR touching retrieval code.

## Layer 9 — Cross-tenant suggestion features

Some products offer "tenants like yours also asked..." style features. Implement these with **derived statistics only** (aggregated counts, anonymised), never with raw cross-tenant retrieval. Make the feature opt-in and document the data flow in the DPA.

## Layer 10 — Backup-restore correctness

A restore of one tenant's vector store must not write into another tenant's namespace. The backup tool keys backups per tenant; the restore tool refuses to write outside the target tenant's namespace.

## Anti-patterns

- Tenant filter applied at the application layer after the engine returns more results than asked for (`top_k * N`, then filter). Wasted compute and a leak waiting to happen.
- Embedding query reuses cached embedding across tenants. Acceptable only if the embedding model is *identical* across tenants AND retrieval enforces tenant scope. Document this choice.
- Per-feature retrieval cache that escapes the per-tenant boundary. Standardise the cache layer.
- "Trust the engine" — even mature engines have had multi-tenant bugs. Layer your own assertions.
