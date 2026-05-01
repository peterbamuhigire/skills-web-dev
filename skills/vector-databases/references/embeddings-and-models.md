# Embeddings and Embedding Generation — Deep Dive

Companion to `SKILL.md` §2 and §3.

## Why cosine similarity is the standard

For an L2-normalised vector `v`, `||v|| = 1`. Cosine similarity between two unit vectors equals the dot product, and the Euclidean distance is monotonic with cosine, so all three rank documents identically. This is why most retrieval systems standardise on cosine over normalised vectors: ranking is invariant to the choice of metric and the dot product is the cheapest computation.

Several vendors normalise on upload (Qdrant explicitly states this for cosine collections; OpenAI's `text-embedding-3-*` returns normalised vectors). Verify per-vendor before assuming.

## Choosing dimensions

Higher dimensions can encode more nuance but cost more storage and compute per query. For most retrieval tasks 768–1536 dimensions are sufficient. OpenAI's `text-embedding-3-*` family supports output truncation: ask for the first N dimensions of a 3072-dim vector and storage and query speed improve roughly linearly. Truncated embeddings retain most of the retrieval quality on standard benchmarks per OpenAI's reporting; verify on your own evaluation set.

## Choosing a model

Decide on these axes:

- **Language coverage.** OpenAI 3-* and Cohere embed-v3 are strong on multilingual; BGE/E5 vary by checkpoint.
- **Per-1M-token cost** at projected volume. The cost of `-large` over `-small` is rarely justified by retrieval lift alone.
- **Hosted vs self-hosted.** Self-hosted (BGE, E5) is free at inference time but you pay GPU/CPU. Hosted is per-token but zero ops.
- **Evaluation on your corpus.** Build a small held-out evaluation set (50–200 queries with known relevant chunks) and rank candidate models by recall@k and MRR.

## Production embedding pipeline

The minimum viable loop:

```python
from openai import OpenAI
import time, random
import hashlib

client = OpenAI()

def embed_batch(texts: list[str], model: str = "text-embedding-3-small"):
    for attempt in range(5):
        try:
            resp = client.embeddings.create(model=model, input=texts)
            return [e.embedding for e in resp.data]
        except RateLimitError:
            time.sleep((2 ** attempt) + random.random())
    raise RuntimeError("embedding retries exhausted")

def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

Required behaviour:

- **Batch.** Vendors accept many inputs per request. Per-request overhead dominates without batching. Typical batch sizes: 100–512 inputs depending on total tokens per request and the vendor's per-request token cap.
- **Retry with exponential backoff and jitter.** Rate limits are the common failure mode. Always add jitter; deterministic retry creates thundering-herd recovery.
- **Tokenise before sending.** Use `tiktoken` for OpenAI; vendor-specific tokenisers for others. You need the token count for cost telemetry and to stay under per-input limits.
- **Idempotency keys** when the SDK supports them, so duplicate retries do not double-charge.
- **Hash and skip.** Compute `content_hash(text)` and store it alongside the chunk. On the next run, compare hashes and only re-embed changed chunks. This is the single largest cost lever.
- **Cost telemetry.** Emit `tokens_in` and `dollars_estimated` per batch into `observability-monitoring`. Aggregate by day; alert on a threshold that is a fraction of monthly budget.

## Anti-patterns

- Calling the embedding API one input at a time inside a loop.
- Retrying without jitter and without a cap.
- Re-embedding the entire corpus on every nightly job.
- Mixing models. Once a corpus is embedded with one model, queries must use the same model. Migrating models requires a full re-embed and a switch-over plan.

## Sources

- OpenAI Embeddings guide — `platform.openai.com/docs/guides/embeddings` (concept-level only; re-verify model names and pricing).
- OpenAI Cookbook — `github.com/openai/openai-cookbook` for batching and tokenisation patterns.
- Cohere embed docs — `docs.cohere.com/docs/embeddings`.
- Voyage AI docs — `docs.voyageai.com`.
