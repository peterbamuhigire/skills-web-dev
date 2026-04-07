---
name: ai-rag-patterns
description: Use when building features that answer questions from private data, documents, policies, or time-sensitive information — RAG architecture, chunking strategies, hybrid search, re-ranking, vector databases, evaluation, agentic RAG, multimodal RAG, and production deployment
---

# RAG Patterns — Retrieval-Augmented Generation

## Overview

RAG solves the core LLM limitation: they only know what they were trained on. Use RAG to inject private data (invoices, menus, policies, reports) into every AI response.

**Core principle:** RAG = look up a database + LLM synthesises the results. The LLM never needs to "know" your data.

---

## When to Use RAG

| Condition | Action |
|---|---|
| Knowledge base < 200K tokens (~500 pages) | Include everything in context — no RAG needed |
| Knowledge base > 200K tokens | Use RAG |
| Data changes frequently (menus, prices, stock) | RAG (update documents, not model) |
| Data is private/confidential | RAG (keeps data out of training pipelines) |
| Need source citations | RAG (chunks are traceable to source) |
| Model needs brand voice / domain jargon | Fine-tune instead |

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

**Default: start with RAG.** Fine-tune only when RAG + prompt engineering cannot deliver the required tone or vocabulary.

---

## Pipeline Architecture

```
INGESTION (run once + on document updates)
──────────────────────────────────────────
Documents → Loader → Cleaner → Chunker → Embedding Model → Vector DB + Metadata

QUERY (runs per user request)
──────────────────────────────
User Query → Query Rewriter (multi-turn) ─────────────┐
           → Keyword Search (BM25) ─────────────────┐  │
           → Embed Query → Vector Search ────────── │──┘
                                                    ↓
                                       RRF Hybrid Merge → Top 20 Chunks
                                                    ↓
                                        Cross-Encoder Reranker → Top 5
                                                    ↓
                                  Prompt Builder (query + chunks + citations)
                                                    ↓
                                                LLM API → Response
```

---

## Chunking Strategies

Chunking is the most critical tuning decision — wrong chunk size destroys retrieval quality.

### 1. Fixed-Size (Baseline)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
```

Best for: homogeneous documents (FAQs, support tickets). Overlap prevents context loss at boundaries.

### 2. Sentence Window (Balanced Precision + Context)

```python
from llama_index.core.node_parser import SentenceWindowNodeParser
parser = SentenceWindowNodeParser.from_defaults(
    window_size=5,
    window_metadata_key="window",
    original_text_metadata_key="original_sentence"
)
```

Retrieves at sentence level, expands to surrounding window for context when sending to LLM.

### 3. Hierarchical (Structured Documents)

```python
from llama_index.core.node_parser import HierarchicalNodeParser
parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[512, 256, 128])
# Use with AutoMergingRetriever — merges small child chunks to parent when needed
```

Best for: technical docs, legal documents, manuals with nested structure.

### 4. Semantic Splitter (Best Quality)

```python
from llama_index.core.node_parser import SemanticSplitterNodeParser
parser = SemanticSplitterNodeParser(
    buffer_size=1,
    breakpoint_percentile_threshold=95,
    embed_model=embed_model
)
```

Uses embeddings to detect semantic breakpoints. Produces far fewer, richer chunks (e.g., 624 vs 12,453 for the same document). Best for long documents with distinct topic shifts. Improves latency because fewer chunks need evaluation.

### 5. Contextual Retrieval (Anthropic Pattern — Major Quality Boost)

Prepend a 50–100 token context summary to every chunk before embedding:

```
"Give a short context to situate this chunk for search retrieval:
Document: {title}
Chunk: {chunk_text}
Context (under 100 words):"
```

Store and embed: `{generated_context}\n\n{chunk_text}` as the indexed unit.

**Rule of thumb:** Target 200–500 tokens per chunk. Add 50–100 token overlap. Prefer semantic boundaries (paragraphs, headings) over character counts.

---

## Embedding Model Selection

| Model | Dimensions | Best For |
|---|---|---|
| `text-embedding-3-small` (OpenAI) | 1536 | General purpose, cost-optimised |
| `text-embedding-ada-002` (OpenAI) | 1536 | Strong general quality |
| `all-MiniLM-L6-v2` (SBERT) | 384 | Fast, offline, good accuracy |
| `SciBERT` | 768 | Scientific / medical literature |
| `LegalBERT` | 768 | Legal documents, case law |
| CLIP | 512 | Text + image cross-modal search |

**Critical:** Use the same embedding model for both indexing and querying. Mixing models completely breaks retrieval.

---

## Vector Database Selection

| Database | Type | Hybrid Search | Metadata Filter | Best For |
|---|---|---|---|---|
| **Qdrant** | Self-hosted/Cloud | ✅ | ✅ | Production OSS — best overall |
| **pgvector** | PostgreSQL extension | ✅ | ✅ | Already using PostgreSQL |
| **Pinecone** | Cloud managed | Limited | ✅ | Fully managed, minimal ops |
| **Chroma** | Self-hosted | ❌ | ✅ | Dev / prototyping |
| **FAISS** | In-memory library | ❌ | ❌ | Offline, privacy-sensitive |
| **Weaviate** | Self-hosted/Cloud | ✅ | ✅ | Graph-like queries |

**Recommendation:** Qdrant for self-hosted production. Pinecone for fully managed. Chroma or FAISS for development.

---

## Retrieval Algorithms

### BM25 (Keyword / Sparse)

```
Pros: Fast, no embeddings, handles product codes / SKUs / exact terms
Cons: Misses synonyms and semantic meaning
```

Start here. Works with Elasticsearch or MySQL FULLTEXT.

### Vector Search (Semantic / Dense)

```
Pros: Semantic matching ("cheap" → "affordable", "low cost")
Cons: Misses exact product codes; requires embedding model + vector DB
```

### Hybrid Search — Production Standard

Combine BM25 + vector using Reciprocal Rank Fusion (RRF):

```
Score(doc) = Σ 1/(k + rank_i(doc))   where k = 60
```

```php
function hybridRetrieve(string $query, int $tenantId, int $topK = 5): array {
    $keywordResults = $this->bm25Search($query, $tenantId, $topK * 2);
    $vectorResults  = $this->vectorSearch($this->embed($query), $tenantId, $topK * 2);

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

Real-world: 42% improvement in relevant retrieval; 2.5s → 800ms latency reduction.

---

## Re-Ranking

After hybrid retrieval, re-rank with a cross-encoder for significantly better precision. Bi-encoder retrieval is fast but imprecise. Cross-encoders compare query+document together — far more accurate.

**Pipeline:** BM25 + Vector → RRF merge (top 20) → Cross-Encoder → top 5 → LLM

```python
# Option A: Cohere Rerank (managed)
import cohere
co = cohere.Client(api_key)
results = co.rerank(
    model="rerank-english-v3.0",
    query=query,
    documents=retrieved_chunks,
    top_n=5
)

# Option B: Local cross-encoder (SentenceTransformers)
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
scores   = reranker.predict([(query, doc) for doc in retrieved_chunks])
ranked   = sorted(zip(scores, retrieved_chunks), reverse=True)[:5]
```

---

## Full RAG Query Algorithm

```
1. Receive user question
2. If multi-turn: rewrite last message to be self-contained (see below)
3. BM25 keyword search → top 10 candidates
4. Embed query → vector search → top 10 semantic candidates
5. RRF merge → top 20 chunks
6. Cross-encoder rerank → top 5 chunks
7. Filter any chunk below similarity threshold (e.g., 0.75)
8. Retrieve metadata: source URL, document title, page number
9. Build prompt:
   Context:
   [CHUNK 1] Source: {doc_title}, p.{page}
   {chunk_text_1}
   [CHUNK 2] ...
   Question: {user_question}
   Answer ONLY from provided context. Cite the source document for each fact.
   If the answer is not in the context, say: "I don't have that information."
10. Call LLM API (temperature 0.2–0.3 for factual tasks)
11. Resolve citation URLs → return answer + source list
```

---

## Query Rewriting (Multi-Turn)

```
"Given this conversation history, rewrite the last message as a self-contained question:
History: {history}
Last message: 'What about the chicken one?'
Rewritten: 'What is the pricing of the chicken burger?'"
```

---

## RAG Schema (Multi-Tenant)

```sql
CREATE TABLE documents (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  tenant_id  INT NOT NULL,
  title      VARCHAR(255),
  source_url VARCHAR(512),
  doc_type   VARCHAR(50),        -- 'menu', 'policy', 'invoice', 'report'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW() ON UPDATE NOW(),
  INDEX idx_tenant (tenant_id)
);

CREATE TABLE document_chunks (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  document_id  BIGINT NOT NULL,
  tenant_id    INT NOT NULL,
  chunk_index  INT NOT NULL,
  chunk_text   TEXT NOT NULL,
  context_text TEXT,             -- contextual retrieval prefix (Anthropic pattern)
  token_count  INT,
  created_at   TIMESTAMP DEFAULT NOW(),
  FULLTEXT INDEX ft_chunk (chunk_text),
  INDEX idx_tenant_doc (tenant_id, document_id),
  FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
-- Store dense embeddings in Qdrant/pgvector externally, referencing chunk.id
```

---

## Evaluation Framework

Evaluate both retrieval and response quality separately. Never deploy without baselines.

### Retrieval Metrics

| Metric | Measures | Target |
|---|---|---|
| **Hit Rate** | Is the correct doc in top-K retrieved? | > 0.80 |
| **MRR** (Mean Reciprocal Rank) | How high is the first correct doc ranked? | > 0.70 |
| **Precision@K** | % of retrieved docs that are relevant | > 0.60 |

### Response Metrics

| Metric | Measures | Tool |
|---|---|---|
| **Faithfulness** | Answer stays within retrieved context? | RAGAS |
| **Answer Relevancy** | Answer addresses the actual question? | RAGAS |
| **Context Recall** | Retrieved context sufficient for the answer? | RAGAS |
| **BLEU / ROUGE** | N-gram overlap with reference answers | NLTK |

```python
# RAGAS evaluation (framework-agnostic)
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall

results = evaluate(
    dataset=test_dataset,  # fields: question, answer, contexts, ground_truth
    metrics=[faithfulness, answer_relevancy, context_recall]
)
```

Set baselines before any chunking or retrieval changes. Schedule periodic regression evaluations.

---

## Production Patterns

### PII Masking Before Indexing

```python
import re

def mask_pii(text: str) -> str:
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', '[EMAIL]', text)
    return text
```

### Confidence Thresholding

```python
MIN_SIMILARITY = 0.75
filtered = [(score, doc) for score, doc in results if score >= MIN_SIMILARITY]
if not filtered:
    return "I couldn't find relevant information. Please rephrase or contact support."
```

### Caching Strategy

- Cache embeddings — identical text never re-embedded (Redis + TTL)
- Cache retrieval results — same query within same session returns cached top-K
- Cache LLM responses — identical query+context pairs
- Use prefix KV caching for repeated system prompts (Anthropic and OpenAI both support this)

### Monitoring Stack

- **Prometheus + Grafana** — query latency, error rates, token consumption, cache hit rate
- **LangSmith / LangChain tracing** — full pipeline visibility per request
- **RAGAS** — scheduled batch evaluation for quality regression detection
- **Alert thresholds:** p95 latency > 2s, error rate > 1%, faithfulness < 0.7

### Scalability

- Parallelise retrieval: `ThreadPoolExecutor` for concurrent BM25 + vector queries
- Migrate local FAISS → Pinecone or Qdrant when data exceeds local hardware
- FAISS HNSW index for approximate nearest-neighbours at large scale
- Horizontal scaling via Kubernetes HPA on CPU/memory metrics

---

## Agentic RAG

For queries requiring multiple retrieval steps, tool calls, or self-correction.

### RouterRetriever (LlamaIndex)

```python
from llama_index.core.retrievers import RouterRetriever, LLMSingleSelector

retriever = RouterRetriever(
    selector=LLMSingleSelector.from_defaults(llm=llm),
    retriever_tools=[vector_tool, summary_tool, sql_tool]
)
# LLM selects the correct retriever based on query type automatically
```

### Self-Correcting RAG

```
1. Retrieve → Generate draft answer
2. LLM-as-judge: "Is this answer grounded in the provided context? Yes/No"
3. If No → re-query with expanded or reformulated terms → regenerate
4. Max 3 correction iterations before returning "I don't have that information"
```

### Multi-Step Retrieval Pattern

```
User query
    ↓
Router: classify query (summarisation vs. specific fact vs. calculation)
    ↓ specific fact
    → Vector retriever → top results
    → Confidence check: if below threshold → expand query + retry
    → Fallback: web search tool
    ↓
Generate grounded answer with citations
```

---

## Multimodal RAG

For documents containing images, charts, diagrams, or mixed media.

```python
# LlamaIndex CLIP-based multimodal index (text + images in shared embedding space)
from llama_index.core.indices import MultiModalVectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore

text_store  = QdrantVectorStore(client=client, collection_name="text")
image_store = QdrantVectorStore(client=client, collection_name="images")

storage_context = StorageContext.from_defaults(
    vector_store=text_store, image_store=image_store
)
index = MultiModalVectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)
# Text query can retrieve relevant images — CLIP creates shared embedding space
retriever = index.as_retriever(similarity_top_k=3, image_similarity_top_k=1)
```

Use cases: product search by image, medical reports with X-rays, technical manuals with diagrams.

---

## Edge Cases

| Case | Response |
|---|---|
| Zero chunks retrieved | "I couldn't find relevant information. Please rephrase or contact support." |
| All chunks below similarity threshold | Same as zero — do not send low-quality context to LLM |
| Query needs calculation | Route to calculator tool, then generate |
| Query needs current web data | Route to web search tool |
| Query is out of domain | Catch at router before RAG runs |
| Multi-turn ambiguous reference | Rewrite query to self-contained form first |

---

## Cost Optimisation

- Use cheaper embedding model (`text-embedding-3-small`) vs. generation model (GPT-4o)
- Cache embeddings — identical documents never re-embedded
- Cache retrieval results — same query within session
- Prefix KV caching for repeated system prompts (saves ~60% on long system prompts)
- Mini-RAG: for single-document Q&A, prepend entire document — no retriever needed
- Knowledge distillation + quantisation for edge/offline deployment

---

## Sources

Josyula et al. — *Mastering Retrieval-Augmented Generation* (BPB, 2024);
Smith, J. — *RAG Generative AI: A Practical Guide* (2024);
Aki D. — *LLM, Transformer, RAG AI* (2024);
Brener, J. — *Mastering RAG for AI Agents* (2024);
Chip Huyen — *AI Engineering* (2025) Ch.6
