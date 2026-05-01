# Production RAG Implementation

Depth that goes beyond the naive retrieve-and-stuff pattern in the core deep
dive. Load this file when a RAG system has to pass evaluation gates, survive
multi-tenant isolation review, or hit a token-cost budget under load.

Pairs with [skill-deep-dive.md](skill-deep-dive.md) — that file covers pipeline,
chunking, hybrid search, re-ranking, and multi-tenant schema. This file covers
the progression from draft to production and the patterns that decide whether
the system ships.

## Included Sections

- RAG Maturity Model — Naive → Advanced → Modular
- Query Transformation — HyDE, Multi-Query, Step-Back
- Contextual Compression — Shrink retrieved chunks before prompting
- Self-RAG — Decide whether to retrieve; critique retrieval
- RAGAS Evaluation — Four named metrics with production thresholds
- Embedding Pipeline — Batching, upserts, re-embedding triggers
- Cost Management Decision Tree — Concrete $/1M-token figures
- Failure Mode Playbook — Empty, irrelevant, hallucinated, stale

---

## RAG Maturity Model

Three stages. Do not skip — most production failures come from promoting a
naive system straight to load without passing through the intermediate stage.

### Stage 1 — Naive RAG

Minimum viable pipeline. Ship this first to prove the data flow, then measure
before adding complexity.

```
Query → Embed → Top-K Retrieval → Prompt Template → LLM → Answer
```

**Signals you are stuck at naive:** retrieval recall below 0.6 on a golden
set, frequent "I don't know" answers when data is present, hallucinations
when the retrieved context is thin.

**Move on when:** faithfulness drops below 0.8 or context precision drops
below 0.5. Naive retrieval will not recover.

### Stage 2 — Advanced RAG

Pre- and post-retrieval techniques layered onto the naive pipeline. This is
where most production systems land.

```
Query → Pre-Retrieval (transform) → Hybrid Retrieval → Post-Retrieval
         (rerank, compress) → Prompt Template → LLM → Answer
```

**What gets added:**
- Query transformation (HyDE, multi-query, step-back)
- Hybrid search with Reciprocal Rank Fusion
- Cross-encoder re-ranking
- Contextual compression before prompt build

**Signals you are ready for modular:** the system is reliable but can't
answer multi-hop questions, can't self-correct, or has too many unused
retrievals driving cost.

### Stage 3 — Modular RAG

Retrieval becomes a skill the agent calls when useful — not a mandatory
preamble on every query.

```
Query → Router → { Retrieve | Search Web | Answer Directly | Ask Clarification }
                  ↓
                  Self-Critique → Retry with transformed query if faithfulness < 0.7
                  ↓
                  Memory of past turns → prune or expand retrieval next turn
```

**When to stop:** modular RAG adds latency and cost. Only promote here when
the product needs multi-hop reasoning, agent loops, or tool use.

---

## Query Transformation

Pre-retrieval techniques that improve the match between short user queries
and longer document chunks.

### HyDE — Hypothetical Document Embeddings

Generate a hypothetical answer, embed that, retrieve against it. The
hypothetical answer is closer in embedding space to real document chunks than
the raw query is.

```python
async def hyde_retrieve(query: str, k: int = 5) -> list[Chunk]:
    hypothetical = await llm.complete(
        f"Write a short passage that would answer: {query}"
    )
    query_embedding = await embedder.embed(hypothetical.text)
    return await vector_db.search(query_embedding, top_k=k)
```

**Use when:** queries are short (< 10 tokens) and chunks are long-form prose.
**Avoid when:** queries already contain the exact terminology used in docs
(invoice numbers, SKUs) — HyDE adds latency without improving recall.

### Multi-Query Expansion

LLM generates N query variants, retrieve for each, merge results. Covers
paraphrase variation and synonym gaps in embedding space.

```python
async def multi_query_retrieve(query: str, k: int = 5, variants: int = 3):
    variant_prompt = (
        f"Rewrite the question in {variants} different ways, one per line. "
        f"Question: {query}"
    )
    rewrites = (await llm.complete(variant_prompt)).text.splitlines()
    all_chunks: dict[str, Chunk] = {}
    for rewrite in [query, *rewrites]:
        for chunk in await retrieve(rewrite, k):
            all_chunks[chunk.id] = chunk  # dedupe
    return list(all_chunks.values())
```

**Use when:** user base varies in vocabulary (technical vs lay users on the
same product), or recall is the bottleneck and cost is acceptable.

### Step-Back Prompting

Rephrase specific questions as general principles, retrieve against the
general form, then answer the specific question with that context.

```python
async def step_back_retrieve(query: str, k: int = 5) -> list[Chunk]:
    principle = await llm.complete(
        f"What is the general principle behind this question: {query}?"
    )
    return await retrieve(principle.text, k)
```

**Use when:** user asks detail-level questions against policy or concept
documents ("Can I get a refund on my June invoice?" → step back to "refund
policy").

---

## Contextual Compression

Summarise retrieved chunks with a cheap model before injecting them into the
expensive generation prompt. Cuts input tokens 50–80% with small accuracy
loss.

```python
async def compress_chunks(query: str, chunks: list[Chunk]) -> list[Chunk]:
    tasks = [
        cheap_llm.complete(
            f"Extract only the sentences from this passage that help answer "
            f"the question. Preserve wording.\n\n"
            f"Question: {query}\n\nPassage: {c.text}"
        )
        for c in chunks
    ]
    summaries = await asyncio.gather(*tasks)
    return [
        Chunk(id=c.id, text=s.text, metadata=c.metadata)
        for c, s in zip(chunks, summaries) if s.text.strip()
    ]
```

**Use when:** chunks are long (> 500 tokens each) and the generation model is
expensive (GPT-4, Claude Opus). Compression with GPT-4o-mini or Haiku
recovers most of its own cost through reduced input tokens to the generator.

**Avoid when:** chunks are already tight (FAQs, titles, short policy
clauses) — compression adds a round-trip for no gain.

---

## Self-RAG

LLM decides whether retrieval is necessary at all, and critiques its own
retrieval quality before answering.

```python
async def self_rag(query: str) -> str:
    decision = await llm.complete(
        f"Does answering this require looking up private data? "
        f"Reply only YES or NO.\n\nQuestion: {query}"
    )
    if decision.text.strip().upper() == "NO":
        return await llm.complete(query).text

    chunks = await retrieve(query, k=5)
    critique = await llm.complete(
        f"Rate relevance of the following to the question (HIGH/MED/LOW).\n\n"
        f"Question: {query}\n\nContext:\n{format_chunks(chunks)}"
    )
    if critique.text.strip().upper() == "LOW":
        chunks = await multi_query_retrieve(query, k=5)

    return await llm.complete(build_prompt(query, chunks)).text
```

**Use when:** the product mixes general chit-chat with private-data
questions (chatbot with small-talk on top of SaaS data). Skips retrieval on
about 40% of queries in practice, cutting cost.

**Avoid when:** every query must be grounded (legal, compliance, medical
assistants) — the NO branch removes the safety net.

---

## RAGAS Evaluation Framework

Four named metrics, each computed by a judge LLM on a golden set. Track all
four weekly in production.

| Metric | Question | Formula Hint | Prod Threshold | Prod-Fail Threshold |
|--------|----------|--------------|----------------|---------------------|
| Faithfulness | Does the answer follow from the context? | Claims-in-answer ∩ context / claims-in-answer | ≥ 0.85 | < 0.7 → human review flag |
| Answer Relevance | Does the answer address the question? | Cosine-sim of generated question from answer, vs original query | ≥ 0.8 | < 0.6 → retry with step-back |
| Context Precision | Are the retrieved chunks relevant? | Relevant chunks at top-K / K | ≥ 0.7 | < 0.5 → add re-ranker |
| Context Recall | Did we retrieve all relevant chunks? | Relevant chunks retrieved / total relevant in corpus | ≥ 0.8 | < 0.6 → switch to hybrid search |

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness, answer_relevancy,
    context_precision, context_recall,
)

# golden = HuggingFace Dataset with columns: question, ground_truth, answer, contexts
results = evaluate(
    dataset=golden,
    metrics=[faithfulness, answer_relevancy,
             context_precision, context_recall],
)
print(results.to_pandas().describe())
```

**Gate this in CI.** A scheduled job runs RAGAS nightly against a golden set
of ≥ 50 curated Q/A pairs. If any metric falls below its Prod-Fail
threshold, the nightly build fails and the model version is pinned to the
last passing snapshot.

---

## Embedding Pipeline

Practical cost and latency patterns for the embedding side of the system.

### Batching

Embedding APIs charge per token, not per call, but batch calls amortise
HTTPS overhead. Batch up to the provider's max — OpenAI accepts 2048 inputs
per request.

```python
async def embed_corpus(texts: list[str], batch_size: int = 512):
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        vectors = await embedder.embed_batch(batch)
        await vector_db.upsert(
            [(hash(t), v, {"text": t}) for t, v in zip(batch, vectors)]
        )
```

### Upsert Semantics

Every chunk needs a stable ID derived from `(document_id, chunk_index)` — not
a random UUID. On re-embed, the upsert overwrites the previous vector rather
than duplicating it.

```python
chunk_id = f"{doc_id}:{chunk_index}"
```

### Re-Embedding Triggers

Trigger a re-embed when any of the following holds:
- Document `updated_at` changed since the chunk's `embedded_at`
- Embedding model version changed
- Chunking strategy changed (chunk_size, overlap)

Track all three in chunk metadata so the trigger is a metadata query, not a
full table scan.

### Cost Reference (2025 pricing)

| Model | $/1M tokens | Dimensions | Notes |
|-------|-------------|------------|-------|
| `text-embedding-3-small` (OpenAI) | $0.02 | 1536 (truncate to 512) | Default choice |
| `text-embedding-3-large` (OpenAI) | $0.13 | 3072 | Only if recall < 0.7 with small |
| `voyage-3-large` (Voyage AI) | $0.18 | 1024 | Best quality if budget allows |
| `all-MiniLM-L6-v2` (local, SBERT) | $0 | 384 | Self-hosted; compute cost only |

A 50,000-document corpus (average 2,000 tokens/doc) = 100M tokens. One-time
embedding at `text-embedding-3-small` = **$2.00**. Cost is almost never the
reason to downgrade the embedder — retrieval quality is.

---

## Cost Management Decision Tree

Concrete dollar figures at each decision point. All based on 2025 public
pricing; update when prices change.

```
Query comes in
├── Classify: is retrieval needed? (Self-RAG gate)
│   ├── NO → generate directly → done (no retrieval cost)
│   └── YES → continue
│
├── Retrieve top-K
│   ├── K=3:  minimal context, fastest, good for narrow queries
│   ├── K=5:  default production value
│   └── K=10: use for multi-hop / agentic RAG only — doubles input tokens
│
├── Re-rank? (cross-encoder adds ~$0.0001 per call)
│   ├── YES if context precision < 0.7 → proceed with top-3 after rerank
│   └── NO if context precision ≥ 0.7 → proceed
│
├── Compress? (adds 1 cheap-LLM round-trip)
│   ├── Chunks total > 3000 tokens → YES (saves ~$0.02 per generation call)
│   └── Chunks total ≤ 3000 tokens → NO (overhead > savings)
│
└── Generate
    ├── Haiku:  $0.25 / $1.25 per 1M input/output  — default
    ├── Sonnet: $3.00 / $15.00 per 1M              — quality bar
    └── Opus:   $15.00 / $75.00 per 1M             — only when Sonnet fails eval
```

**Rule of thumb:** a production RAG query with compression, hybrid search,
re-ranking, and Sonnet generation costs about **$0.01–$0.03 per call**. A
naive RAG query with Haiku is **$0.002–$0.005**. Model choice dominates cost
far more than retrieval choice.

---

## Failure Mode Playbook

Four common failure modes, each with a detection signal and a specific remedy.

### Empty Retrieval

**Signal:** `len(chunks) == 0` or all chunks below similarity threshold.

**Remedy:**
1. Answer from general LLM knowledge with an explicit caveat: *"I don't
   have specific information on this in your knowledge base, but here is what
   is generally true..."*
2. Log the query to a "no-retrieval" table for review — these reveal missing
   documents in the corpus.
3. Do not silently generate a confident-sounding answer — this is the
   primary source of RAG hallucinations.

### Irrelevant Retrieval

**Signal:** RAGAS context precision < 0.5 on the live sample.

**Remedy (in order):**
1. Add re-ranking before prompt build if not already present.
2. Switch to hybrid search (BM25 + vector + RRF) if the corpus has
   domain-specific terminology.
3. Apply HyDE or multi-query expansion if queries are much shorter than
   chunks.
4. Re-chunk if chunk size is above 1000 tokens — long chunks match too many
   queries.

### Hallucination Despite Context

**Signal:** RAGAS faithfulness < 0.7.

**Remedy:**
1. Tighten the system prompt: *"Answer ONLY using the provided context. If
   the answer is not in the context, say 'I don't know'. Do not infer."*
2. Add a post-generation faithfulness check with a judge LLM — flag
   low-faithfulness answers for human review before display.
3. Reduce temperature to 0.2 — lower creativity, tighter grounding.
4. Escalate to a stronger generation model (Haiku → Sonnet → Opus).

### Stale Embeddings

**Signal:** document `updated_at` > chunk `embedded_at` for > 24 hours.

**Remedy:**
1. Re-embedding schedule: daily incremental job that re-embeds any chunk
   whose source document changed.
2. On any document-update webhook, enqueue the chunk-ids for that document
   to a re-embed queue immediately.
3. Track `embedded_at` on every chunk; reject queries against chunks where
   `(now - embedded_at) > TTL` for time-sensitive corpora (stock levels,
   pricing).

---

## Gates Before Shipping

A production RAG system is ready when all of the following hold, measured on
a golden set of at least 50 Q/A pairs:

- Faithfulness ≥ 0.85
- Answer relevance ≥ 0.80
- Context precision ≥ 0.70
- Context recall ≥ 0.80
- P95 end-to-end latency ≤ 3 seconds
- Per-query cost ≤ the product's target margin
- Multi-tenant test harness passes — no cross-tenant leak in 1,000 random
  query probes
- Failure-mode playbook drills documented and tested

Ship nothing that fails any gate. Each gate has a specific remedy above.
