---
name: ai-rag-patterns
description: Use when building features that need to answer questions from private company data, documents, policies, or time-sensitive information — RAG architecture, chunking, retrieval algorithms, vector databases, and hybrid search
---

# RAG Patterns — Retrieval-Augmented Generation

## Overview

RAG solves the core limitation of LLMs: they only know what they were trained on. Use RAG to inject your client's private data (invoices, menus, policies, reports) into every AI response.

**Core principle:** RAG = look up a database + LLM summarises the results. The LLM never needs to "know" your data — it just synthesises what you retrieve.

---

## When to Use RAG

| Condition | Action |
|---|---|
| Knowledge base < 200K tokens (~500 pages) | Include everything in context — no RAG needed |
| Knowledge base > 200K tokens | Use RAG |
| Data changes frequently (menus, prices, stock) | RAG (update documents, not model) |
| Data is private/confidential | RAG (keeps data out of training pipelines) |
| Need source citations | RAG (chunks are traceable to source) |
| Model needs brand voice / jargon | Fine-tune instead |

---

## RAG vs Fine-Tuning

| Factor | RAG | Fine-Tuning |
|---|---|---|
| Up-to-date content | ✅ Yes (add docs anytime) | ❌ Stale until retrained |
| Hallucinations | ✅ Lower (document-grounded) | ❌ Higher |
| Source citations | ✅ Yes | ❌ No |
| Brand voice control | ❌ Weak | ✅ Strong |
| Domain jargon | ❌ Weak | ✅ Strong |
| Up-front cost | ✅ Lower | ❌ High |
| Data needed | Unstructured documents | Labelled input-output pairs |

**Default: start with RAG.** Only fine-tune for brand voice/jargon when RAG + prompt engineering cannot solve it.

---

## RAG Architecture

```
INGESTION PIPELINE (run once + on document updates)
────────────────────────────────────────────────────
Documents → Loader → Text Splitter → Chunker
                                        ↓
                               Embedding Model
                                        ↓
                               Vector Database (store)

QUERY PIPELINE (runs per user request)
───────────────────────────────────────
User Query → Keyword Search (BM25) ──────┐
           → Embed Query → Vector Search ─┤ Hybrid Merge (RRF)
                                          ↓
                                    Top K Chunks
                                          ↓
                              Prompt Builder (query + chunks)
                                          ↓
                                       LLM API
                                          ↓
                              Citation Resolver → Response
```

---

## Chunking Strategy

Chunking is the most important tuning decision in RAG. Wrong chunk size destroys retrieval quality.

| Chunk Size | Retrieval | Context |
|---|---|---|
| Too small (< 100 tokens) | Diverse but fragment context | Too little per chunk |
| Too large (> 1000 tokens) | Fewer, richer chunks | Fewer fit in context window |
| **Good range: 200–500 tokens** | Balanced | 3–5 chunks fit easily |

**Rules:**
- Chunk by semantic boundary (heading, paragraph) not character count when possible
- Add overlap (50–100 tokens) between chunks to avoid losing information at boundaries
- Store metadata with each chunk: `document_id`, `title`, `section`, `page_number`, `created_at`

### Contextual Retrieval (Anthropic pattern — major quality boost)
Add a 50–100 token context summary to every chunk before embedding.

```
Prompt to generate context per chunk:
"Please give a short succinct context to situate this chunk within the overall
document for the purpose of improving search retrieval:
Document title: {title}
Chunk: {chunk_text}
Context (under 100 words):"
```

Store: `{generated_context}\n\n{chunk_text}` as the embedded unit.

---

## Retrieval Algorithms

### Term-Based (BM25 / Elasticsearch)
```
Pros: Fast, no embeddings, handles product codes/SKUs/exact terms
Cons: Misses synonyms and semantic meaning
```
Start here. Works out of the box with Elasticsearch/MySQL FULLTEXT.

### Embedding-Based (Vector Search)
```
Pros: Semantic matching ("cheap" finds "affordable", "low cost")
Cons: Misses exact product codes; requires embedding model + vector DB
```
Vector DBs: **Qdrant** (best OSS), Chroma (dev), Pinecone (managed), Weaviate, FAISS.

### Hybrid Search (Recommended for Production)
Combine both algorithms using Reciprocal Rank Fusion (RRF).

```
Score(doc) = Σ 1/(k + rank_i(doc))   where k = 60
```

Run keyword search and vector search in parallel → merge rankings → take top K.

```php
function hybridRetrieve(string $query, int $tenantId, int $topK = 5): array {
    // Parallel retrieval
    $keywordResults = $this->bm25Search($query, $tenantId, $topK * 2);
    $vectorResults = $this->vectorSearch($this->embed($query), $tenantId, $topK * 2);

    // RRF merge
    $scores = [];
    foreach ($keywordResults as $rank => $doc) {
        $scores[$doc['id']] = ($scores[$doc['id']] ?? 0) + 1 / (60 + $rank + 1);
    }
    foreach ($vectorResults as $rank => $doc) {
        $scores[$doc['id']] = ($scores[$doc['id']] ?? 0) + 1 / (60 + $rank + 1);
    }
    arsort($scores);
    return array_slice(array_keys($scores), 0, $topK);
}
```

---

## Full RAG Query Algorithm

```
1. Receive user question
2. Keyword search (BM25) → top 10 candidates
3. Embed user question
4. Vector search → top 10 semantic candidates
5. RRF merge → top 5 chunks
6. Retrieve metadata (source URL, document title, page)
7. Build prompt:
   ---
   Context:
   [CHUNK 1] Source: {doc_title}, p.{page}
   {chunk_text_1}

   [CHUNK 2] Source: {doc_title}, p.{page}
   {chunk_text_2}
   ---
   Question: {user_question}

   Answer using ONLY the provided context.
   If the answer is not in the context, say: "I don't have that information."
   Cite the source document for each fact you state.
   ---
8. Call LLM API
9. Resolve citation URLs
10. Return answer + source list
```

---

## RAG Schema (Multi-Tenant)

```sql
CREATE TABLE documents (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  tenant_id     INT NOT NULL,
  title         VARCHAR(255),
  source_url    VARCHAR(512),
  doc_type      VARCHAR(50),        -- 'menu', 'policy', 'invoice', 'report'
  created_at    TIMESTAMP DEFAULT NOW(),
  updated_at    TIMESTAMP DEFAULT NOW() ON UPDATE NOW(),
  INDEX idx_tenant (tenant_id)
);

CREATE TABLE document_chunks (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  document_id   BIGINT NOT NULL,
  tenant_id     INT NOT NULL,
  chunk_index   INT NOT NULL,
  chunk_text    TEXT NOT NULL,
  context_text  TEXT,              -- Anthropic contextual retrieval prefix
  embedding     JSON,              -- or use pgvector / Qdrant externally
  token_count   INT,
  created_at    TIMESTAMP DEFAULT NOW(),
  FULLTEXT INDEX ft_chunk (chunk_text),
  INDEX idx_tenant_doc (tenant_id, document_id),
  FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
```

---

## Query Rewriting

For multi-turn conversations, rewrite the last message to be self-contained.

```
User turn 1: "Tell me about our beef burger pricing."
User turn 2: "What about the chicken one?"

Rewrite prompt:
"Given this conversation history, rewrite the last user message to be
self-contained without needing the history:
History: {history}
Last message: 'What about the chicken one?'
Rewritten:"
→ "What is the pricing of the chicken burger?"
```

---

## Edge Cases to Handle

| Case | Response |
|---|---|
| Zero chunks retrieved | "I couldn't find relevant information. Please rephrase or contact support." |
| All chunks below relevance threshold | Same as zero |
| Query needs calculation | Route to calculator tool before RAG |
| Query needs current web data | Route to web search tool |
| Query is out of domain | Catch at router before RAG runs |

---

## Cost Optimisation

- Use a **cheaper embedding model** (text-embedding-3-small) vs the generation model (GPT-4o)
- **Cache embeddings** — identical queries don't need re-embedding
- **Cache retrieval results** — same query within same session
- Use **prefix KV caching** for repeated system prompts (OpenAI, Anthropic both support this)
- Mini-RAG: for single-document Q&A, prepend entire document — no retriever needed

---

## Sources
Chip Huyen — *AI Engineering* (2025) Ch.6; David Spuler — *Generative AI Applications* (2024) Ch.15; Andrea De Mauro — *AI Applications Made Easy* (2024) Ch.4
