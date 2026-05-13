> Consolidated from skills/ai-agent-memory/SKILL.md into ai-agent-runtime-architecture on 2026-05-13. Load this through skills/ai-agent-runtime-architecture/SKILL.md, not as an active skill entrypoint.

# AI Agent Memory
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing what an agent remembers across turns, across sessions, and across conversations.
- Implementing **short-term** turn buffers (the last N exchanges), **working** episode memory (this task's scratchpad), and **long-term** semantic memory (facts the agent has learned about this tenant over time).
- Ensuring memory is **per-tenant isolated** — agent never recalls one tenant's facts in another tenant's session.
- Wiring memory into the **forget-on-erase** cascade so a GDPR Article 17 request deletes derived memory too.
- Deciding what is too dangerous to remember (passwords, PII, anything not explicitly tagged for retention).

## Do Not Use When

- The task is the customer's knowledge-base ingestion (uploaded docs) — `ai-rag-multi-tenant`.
- The task is the platform's general data erasure cascade — `saas-tenant-data-portability-and-erasure`. This skill is the *AI-specific* leaf that the cascade traverses.
- The task is short-term conversation state for a single-shot chatbot (no agent, no long horizon) — that's just a session.

## Required Inputs

- Tenancy model and per-tenant isolation pattern (`ai-tenant-isolation-patterns`).
- Data classification (`saas-tenant-data-portability-and-erasure`).
- Erasure cascade map.
- Prompt registry + agent runtime (`ai-on-saas-architecture`, `ai-agent-runtime-architecture`).
- Vector store for semantic memory if used.

## Workflow

1. Read this `SKILL.md`.
2. Define **three memory tiers** (§1): short-term, working, long-term. See `references/memory-tiers.md`.
3. Pick **what is and is not eligible for long-term storage** (§2).
4. Implement **per-tenant isolation** (§3) — every read is tenant-scoped.
5. Implement **forget-on-erase cascade** (§4). See `references/forget-on-erase-cascade.md`.
6. Implement **cross-conversation guard** (§5) — memory of one conversation cannot leak into a different conversation.
7. Implement **memory-write gating** (§6) — agent doesn't auto-write everything to long-term; user controls.
8. Apply anti-patterns (§7).

## Quality Standards

- Memory has **three explicit tiers** with separate stores, separate TTLs, separate query interfaces.
- Every memory row carries `tenant_id`, `user_id` (where relevant), `source`, `confidence`, `expires_at`, `consented_at`.
- Long-term memory writes are **gated** — either by user consent ("Should I remember this?") or by a deterministic rule (entity resolution: "this is a customer record", not "this is a fact").
- Long-term memory reads are tenant-scoped at the query boundary; **no** index spans tenants without an enforced filter.
- An erasure request for a user removes their memory rows in all three tiers within the platform-wide SLA (default 30 days).
- An erasure request for a tenant cascades through embeddings, vector stores, and any fine-tunes / adapters trained on that tenant's data.
- "Forget this fact" is a first-class user action with a confirmation.
- No memory contains plaintext credentials, full payment numbers, government IDs, or PII categories the data classification marks `do-not-store-in-memory`.

## Anti-Patterns

- Long-term memory implemented as a global vector index with `tenant_id` as one of many filters — the filter is a defence in depth, not the only defence.
- Memory rows persisted with no consent timestamp, no source, no confidence. Compliance later cannot defend the retention.
- Agent decides what to remember; the user has no visibility and no control.
- Memory wiped on tenant erasure, but the fine-tune trained on that tenant's chats remains in production.
- Short-term buffer that grows unboundedly. Each turn re-embeds; cost explodes.
- "Conversation history" stored forever as default. GDPR exposure.
- Memory of one user surfacing in another user's session (same tenant, different person).

## Outputs

- Three-tier memory store schema.
- Memory-eligibility rubric (what is / isn't memorable).
- Per-tenant isolation enforcement at query layer.
- Forget-on-erase cascade integration.
- User-facing memory UI ("things I know about you" + delete).
- Audit log of memory writes / reads.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Three-tier memory schema | Markdown | `docs/ai/agent-memory.md` |
| Compliance | Erasure cascade map | Diagram | `docs/compliance/agent-memory-erasure.md` |
| Release evidence | Cross-tenant leak test report | CI report | `tests/ai/agent_memory_isolation_test.py` |
| UX | "What I remember" user surface spec | Markdown | `docs/ux/agent-memory-user-control.md` |

## References

- `references/memory-tiers.md` — short / working / long schemas + lifecycle.
- `references/forget-on-erase-cascade.md` — GDPR cascade through memory tiers.
- Companion: `ai-rag-multi-tenant`, `ai-tenant-isolation-patterns`, `ai-on-saas-architecture`, `saas-tenant-data-portability-and-erasure`, `ai-agent-runtime-architecture`, `dpia-generator`.

<!-- dual-compat-end -->

## §1 Three Tiers

| Tier | Scope | Storage | TTL | Use case |
|---|---|---|---|---|
| **Short-term** | Current turn window | In-memory / Redis | Per conversation, ~24h | Resolve pronouns, maintain immediate context |
| **Working** | Current task / episode | DB row tied to `agent_tasks.id` | Until task completes + 7 days | Plan scratchpad, intermediate observations, retry context |
| **Long-term** | Cross-conversation, per tenant | Vector store + DB | 365 days default, configurable | "User prefers SI units", "customer ACME's billing contact is Ben" |

Each tier has its own client API. The agent does not see them as one. Mixing tiers in one query creates leakage paths.

Full schemas in `references/memory-tiers.md`.

## §2 What is Memorable

Long-term memory is for **stable, durable facts**, not for raw conversation. Memorise:

- **Entity attributes**: "ACME's preferred currency is USD", "Ben's role at ACME is procurement lead".
- **User preferences**: "this user prefers concise answers", "this user wants reports in PDF".
- **Workflow shortcuts**: "for monthly close, run reports in this order".
- **Corrections**: "the user said our default tax assumption was wrong: it's 18% not 20%".

Do **not** memorise:

- Raw chat transcripts (those go in conversation history with a shorter TTL).
- Authentication credentials, payment numbers, government IDs.
- Inferences with low confidence (e.g., "user is in finance" inferred from one message).
- Anything the user did not consent to remember.

Confidence threshold for long-term write: ≥ 0.8. Writes below threshold go to working memory only.

## §3 Per-Tenant Isolation

Default: one **logical store per tenant**.

Vector store options:
- **Silo**: dedicated index per tenant (highest isolation, highest cost).
- **Pool with mandatory filter**: one index, `tenant_id` filter enforced at the query API layer that the agent cannot bypass.

If pool: the query is wrapped — the agent's "search memory" tool does NOT accept `tenant_id` as an arg. The runtime injects it from `ctx.tenant_id`. The agent cannot ask for another tenant's memory because the tool surface doesn't permit it.

```python
def search_memory(args: dict, ctx: ToolContext) -> dict:
    # ctx.tenant_id is set by the runtime, not by the agent
    results = vector_store.query(
        embedding=embed(args["query"]),
        filter={"tenant_id": ctx.tenant_id},  # not user-controllable
        top_k=args.get("top_k", 5),
    )
    return {"status": "ok", "memories": [serialize(r) for r in results]}
```

Tests: every release runs a cross-tenant probe — given tenant A's memory and tenant B's session, confirm no overlap.

## §4 Forget-on-Erase Cascade

When a user invokes erasure (GDPR Art 17 / CCPA), the cascade:

1. Working memory: delete `agent_memory_working` rows where `user_id = U`.
2. Long-term memory:
   - Delete rows in `agent_memory_long` where `subject_user_id = U`.
   - Delete vector embeddings keyed to those rows.
3. Conversation history: delete `agent_conversations` and `agent_messages` for the user.
4. Audit / trace: redact PII (do not delete; immutable audit log required by SOC2). Replace user identifiers with tombstones.
5. Fine-tunes / adapters trained on user data: see `ai-tenant-isolation-patterns` — if any model was tuned on this user's data, mark for retraining without the user.

Full procedure in `references/forget-on-erase-cascade.md`.

## §5 Cross-Conversation Guard

Within the same tenant, memory of conversation A should not surface in conversation B by default. The guard:

- Long-term memory is **tagged with `scope: 'global' | 'conversation' | 'task'`**.
- Default new long-term writes are `scope: 'task'`. Promotion to broader scope is explicit ("remember this across our conversations").
- Cross-conversation surfacing requires a user-visible audit ("From your prior conversation on April 12...").

This prevents the "agent appears to know things it shouldn't" UX failure that erodes trust.

## §6 Memory-Write Gating

Three modes per tenant:

| Mode | Behaviour | Default for |
|---|---|---|
| `off` | No long-term memory writes | Free tier |
| `prompt` | Agent proposes "I'd like to remember X. OK?" → user approves | Pro tier |
| `auto` | Agent writes high-confidence entity attributes automatically; surfaces a "Memory" view for review/edit | Enterprise tier (opt-in) |

`auto` mode still excludes credentials, IDs, low-confidence inferences. Audit trail every write.

## §7 Anti-Patterns

- One global vector index with tenant_id as one of many filter fields. One day someone forgets the filter and leaks.
- Storing raw chat as long-term memory. GDPR exposure, retrieval pollution.
- "Auto" memory mode without a user-visible memory view. Users discover what's remembered only when it surfaces wrongly.
- Memory shared across the customer's org without scoping. User A's preferences applied to user B's session.
- Erasure that deletes the user but leaves vector embeddings (foreign keys, anyone?).
- Memory writes with no confidence score — every later retrieval treats them as ground truth.


