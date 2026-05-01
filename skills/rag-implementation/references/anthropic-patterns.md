# Anthropic Claude Patterns for RAG

Deep dive supporting `SKILL.md` §10.

## Contextual Retrieval pipeline

Indexing time, per chunk:

1. Take the chunk and its parent document.
2. Ask Claude: "Given this document, write a 50–100 token context that situates this chunk in the document for retrieval purposes. Do not summarise; locate."
3. Prepend the generated context to the chunk before embedding.
4. Prepend the same context to the chunk before BM25 indexing.

Hybrid retrieval. Run both contextual-embedding search and contextual-BM25 search. Combine with Reciprocal Rank Fusion. Optionally rerank.

The published failure-rate reductions (anthropic.com/news/contextual-retrieval, fetched 2026-05-01):

- Contextual Embeddings alone: 35% reduction (5.7% to 3.7%).
- Contextual Embeddings + Contextual BM25: 49% reduction (5.7% to 2.9%).
- The above + reranking: 67% reduction (5.7% to 1.9%).

The one-time generation cost is "$1.02 per million document tokens" (verbatim, fetched 2026-05-01) when prompt caching is used.

## Prompt caching for retrieved chunks

Verbatim shape (platform.claude.com/docs/en/docs/build-with-claude/prompt-caching, fetched 2026-05-01):

```json
{
  "type": "text",
  "text": "Your content here",
  "cache_control": {"type": "ephemeral"}
}
```

TTL options:

- Default ephemeral: 5 minutes.
- Extended: `{"type": "ephemeral", "ttl": "1h"}`.

Cost shape:

- Cache reads: 10% of base input token price.
- 5-minute writes: 25% more than base input tokens.
- 1-hour writes: 2× base input tokens.

Caching applies to content blocks in tools, system, and `messages.content` (text, images, documents, tool use, tool results). Up to 4 explicit breakpoints allowed.

## Cache-breakpoint placement for RAG

Order the prompt from most-stable to most-volatile. Place the breakpoint after each stable block:

1. System prompt — stable across the product. Cache.
2. Tool definitions — stable. Cache.
3. Retrieved-chunks block — stable across a multi-turn conversation about the same documents. Cache.
4. Conversation history — append new turns after the cached blocks.
5. Current user turn — never cache.

Multi-turn conversation about the same document. The first turn pays full input-token cost on the chunks; subsequent turns pay 10% on the same block, as long as you stay within the TTL. Use 1-hour TTL when sessions span longer than 5 minutes.

Single-shot queries, repeated. Full-pipeline cache (a key-value cache keyed on the normalised query) outperforms prompt caching here. Use prompt caching when the conversation is long; full-pipeline cache when traffic is FAQ-shaped.

## Citations API

Claude can return structured citations linking each part of the response to specific input documents. Treat as concept-only in this skill. Verify the exact request and response shape against current docs (docs.anthropic.com / platform.claude.com) before writing dependent code. Do not invent JSON shapes.

When the Citations API is available and verified, prefer it over hand-rolled citation prompting — model-native citations are tied to actual input spans, not to LLM-generated references.
