> Consolidated from skills/ai-tenant-isolation-patterns/SKILL.md into ai-security on 2026-05-13. Load this through skills/ai-security/SKILL.md, not as an active skill entrypoint.

# AI Tenant Isolation Patterns
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Choosing per-tenant vs pooled storage for vector indexes, fine-tunes, prompt variants, eval datasets, conversation logs.
- Hardening an existing AI feature that shares a single vector index across all tenants with only a `tenant_id` metadata filter.
- Designing a leakage test suite — does retrieval ever return another tenant's chunks? Does a prompt cache leak across tenants? Does a fine-tune memorise tenant-specific PII?
- Onboarding an enterprise tenant who requires their AI assets in a dedicated namespace / index / region.

## Do Not Use When

- The task is transactional data isolation (rows in a Postgres table) — use `multi-tenant-saas-architecture`.
- The task is overall AI architecture — use `ai-on-saas-architecture` first; this skill is a specialist.
- The task is RAG ingestion / retrieval mechanics — use `ai-rag-multi-tenant`.

## Required Inputs

- Per-tenant data sensitivity classification (public, internal, confidential, regulated).
- Tenant count and growth rate (drives silo vs pool feasibility).
- Vector store choice (pgvector, Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Vespa).
- Regulatory commitments per tenant (residency, sovereignty, sector — HIPAA / GxP / financial).
- Plan tiers and their isolation guarantees (Free = pool; Enterprise = silo).

## Workflow

1. Read this `SKILL.md`.
2. Inventory **AI asset classes** (§1): vector index, prompt variant, fine-tune, conversation log, eval dataset, retrieval cache, embedding queue, citation store.
3. For each asset class apply the **silo / namespace / pool decision** (§2).
4. Implement **defence in depth** (§3) — multiple isolation layers so one bug doesn't cause leakage.
5. Add **cryptographic partitioning** (§4) where the platform must prove isolation to enterprise buyers.
6. Write the **data-bleed test suite** (§5) and add it to CI.
7. Wire the **isolation kill-switches** (§6) — quarantining a tenant's AI assets in incident response.
8. Apply anti-patterns (§7).

## Quality Standards

- Every AI request resolves the tenant's namespace / partition / index from `tenant_ai_binding` — never from the request payload.
- Retrieval filters are enforced at **both** the query layer and the storage layer.
- Per-tenant encryption keys for confidential / regulated tiers (BYOK pattern).
- A data-bleed test suite runs in CI and against staging weekly with synthetic per-tenant marker tokens.
- Tenant isolation incidents have a documented playbook with named owners and < 30-minute time-to-quarantine.

## Anti-Patterns

- One shared vector index with only a `WHERE tenant_id = ?` filter and no validation — a bug returns chunks from another tenant.
- Prompt template caching keyed by prompt id only — tenant-specific variables in the template leak across cache hits.
- Per-tenant fine-tune that memorised PII — the model emits another tenant's customer names months later.
- Shared embedding queue with no tenant-scoped DLQ — failed messages from tenant A get inspected by tenant B's support engineer.
- Tenant id passed in the request payload and trusted at the storage layer — IDOR via parameter tampering.

## Outputs

- AI asset class inventory + isolation pattern (silo / namespace / pool) per class.
- Defence-in-depth diagram for every AI feature.
- Encryption key strategy per tier.
- Data-bleed test suite (in repo, in CI).
- Quarantine playbook.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | AI asset isolation matrix | Markdown table | `docs/ai/ai-asset-isolation-matrix.md` |
| Release evidence | Data-bleed test suite | Code + report | `tests/ai/data-bleed/` |
| Compliance | Per-tenant key strategy | Markdown doc | `docs/ai/byok-strategy.md` |
| Operability | Quarantine playbook | Markdown runbook | `docs/runbooks/ai-tenant-quarantine.md` |

## References

- `references/vector-store-partitioning-tradeoffs.md` — pgvector / Pinecone / Qdrant / Weaviate / OpenSearch tradeoffs and the per-tenant patterns each supports.
- `references/data-bleed-test-suite.md` — full test taxonomy + sample tests.
- Companion: `ai-on-saas-architecture`, `ai-model-gateway`, `ai-rag-multi-tenant`, `ai-prompt-injection-and-tenant-safety`, `multi-tenant-saas-architecture`, `saas-deployment-models`.

<!-- dual-compat-end -->

## §1 AI Asset Classes Requiring Isolation

| Asset class | Storage shape | Default isolation | Risk if shared |
|---|---|---|---|
| Vector index (chunks + embeddings) | high-dim vectors + metadata | namespace per tenant | retrieval returns another tenant's chunks |
| Prompt variants (per-tenant overrides) | text + variables | row-level on `tenant_prompt_pins` | tenant A sees tenant B's branded prompt |
| Fine-tunes / adapters | model weights | per tenant (silo) for enterprise; shared base + LoRA per tenant otherwise | model memorises tenant PII |
| Conversation / chat history | rows | row-level + per-tenant encryption key | another tenant's reply surfaced via shared cache |
| Eval datasets (goldens) | rows / files | per tenant (silo always for goldens) | per-tenant signal collapses |
| Retrieval cache | k-v | tenant-prefixed key | cross-tenant cache poisoning |
| Embedding job queue | queue / topic | per-tenant partition or routing key | poisoned messages cross tenants |
| Citation / grounding store | rows | tenant scoped | broken provenance audits |

## §2 Silo / Namespace / Pool Decision

Three patterns, in order of strength:

1. **Silo (per-tenant index / instance / weights).** Strongest. Operationally heavy. Use for enterprise + regulated tenants and for fine-tunes.
2. **Namespace (single instance, hard partition).** Most vector DBs (Pinecone namespaces, Qdrant collections per tenant, Weaviate tenants). Strong logical separation, shared infra. Default for vectors.
3. **Pool with tenant filter.** Single index, `tenant_id` in metadata, filter at query time. Lowest cost. Acceptable only for low-sensitivity tiers and when defence in depth is in place.

### Decision rules

| Condition | Pattern |
|---|---|
| Regulated data (HIPAA, GxP, financial) | silo |
| Sovereignty / residency required | silo per region |
| > 10k tenants and shared free tier | pool with tenant filter at low tier; namespace at paid tier |
| Enterprise contract demands proof of isolation | silo or namespace + BYOK |
| Eval dataset | always silo (signal preservation, not security) |
| Fine-tune ≥ 50k examples and revenue justifies | silo per tenant |
| Fine-tune < 50k examples | shared base + LoRA adapter per tenant |

## §3 Defence in Depth

Never rely on one isolation layer. Stack at least three:

1. **Network**: per-region endpoints; private link for enterprise.
2. **Storage partition**: namespace or silo (§2).
3. **Query-time filter**: tenant predicate enforced by the data-access library — feature code can't bypass.
4. **Token-level filter**: `tenant_id` is part of the embedding metadata, the API key scope, and the JWT — a mismatch is a hard fail.
5. **Output validation**: every retrieved chunk's `tenant_id` is asserted against the request's tenant id before being used in a prompt. Fail loud, alert on mismatch.

A single bug in any layer cannot cause leakage if other layers hold.

## §4 Cryptographic Partitioning (BYOK and per-tenant KEK)

For confidential and regulated tiers, the platform proves isolation by encrypting per-tenant data with a tenant-specific KEK (Key Encryption Key). The KEK can be:

- Platform-managed (default tier).
- Customer-managed via KMS (Enterprise — AWS KMS / GCP KMS / Azure Key Vault).
- HYOK / BYOK with platform never seeing the key in plaintext (regulated).

Apply to:
- Conversation logs (envelope encryption per row).
- Embeddings of confidential documents (encrypt the *source*; embeddings themselves are derivable but irreversible; some sectors still require encrypted vectors using deterministic CSE — rare).
- Fine-tune training data at rest.
- AI audit log payloads in S3.

When the tenant revokes the KEK, the platform loses the ability to decrypt — and the data is effectively erased.

## §5 Data-Bleed Test Suite

A standing test suite that proves isolation. Runs in CI and weekly against staging.

**Test taxonomy:**

1. **Marker-token retrieval test.** Seed every tenant's KB with a unique, non-guessable marker token in one chunk. Issue queries from tenant A that should retrieve only A's marker; assert no other tenant's marker ever appears.
2. **Forced-id IDOR.** Send a request with tenant A's auth but tenant B's `kb_partition_id` in the payload — must reject.
3. **Cache poisoning.** Pre-populate a retrieval cache with tenant A's response keyed without the tenant prefix — issue tenant B's request; assert no hit.
4. **Prompt cache leak.** Render tenant A's prompt with tenant-specific variables, then render tenant B's; assert no variable leaks.
5. **Fine-tune memorisation.** For fine-tuned tenants, prompt the model with adversarial cues for memorised PII; assert no other tenant's PII emerges.
6. **Embedding queue redirection.** Push a message with mismatched tenant id; assert it is rejected, not processed under the wrong tenant.
7. **Audit log query scope.** Query the AI audit log as tenant A; assert no tenant B rows.

See `references/data-bleed-test-suite.md` for sample code.

## §6 Quarantine Playbook

When a leakage incident is suspected:

1. **Kill-switch** the suspected tenants' AI (`tenant_ai_binding.ai_enabled = false`) and the involved feature globally if scope is unclear.
2. **Freeze** the vector namespace / index — mark read-only.
3. **Snapshot** the AI audit log + traces for the incident window.
4. **Replay** representative requests in a sandbox; reproduce.
5. **Notify** affected tenants per the breach notification SLA (often 72h for GDPR; less for some contracts).
6. **Remediate** the isolation gap; add a regression test to the data-bleed suite.
7. **Post-mortem** with the AI control-plane team and security.

## §7 Anti-Patterns

- Trusting the tenant id from the request payload at the storage layer.
- One global retrieval cache keyed only by query text.
- Per-tenant fine-tune that includes raw PII in the training set.
- "Multi-tenant" vector DB used in single-collection mode with metadata filtering as the only protection.
- No data-bleed tests because "we filter by tenant_id everywhere".
- BYOK marketed but key actually held by the platform — a contractual misrepresentation.
- Eval datasets pooled across tenants — produces a flat, lying scorecard.

## §8 Read Next

- `ai-on-saas-architecture` — the unifying view.
- `ai-rag-multi-tenant` — RAG-specific patterns building on this.
- `ai-prompt-injection-and-tenant-safety` — the adversarial complement.
- `ai-model-gateway` — enforces tenant scope at the gateway boundary.
- `multi-tenant-saas-architecture` — transactional data isolation.


