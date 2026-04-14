# Phase 09: Advanced AI & RAG Depth

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deepen the existing AI ecosystem from foundational integration to production-grade RAG implementation, and add multimodal AI capability. By the end of this phase, the engine can build AI products that retrieve, reason over, and generate content from private knowledge bases — reliably, measurably, and cost-effectively.

**Architecture:** One new skill directory (`multimodal-ai`). Three existing skills receive deep implementation enhancements: `ai-rag-patterns` (production RAG pipeline depth), `ai-evaluation` (RAGAS framework, drift detection), and `ai-agents-tools` (multi-agent orchestration with guardrails). No new directories for the enhancements — all content goes into existing references.

**Tech Stack:** LlamaIndex, LangChain.js, RAGAS, pgvector HNSW indexes, Pinecone, Qdrant, OpenAI Embeddings API, Cohere Rerank, Claude Vision API, Whisper (speech-to-text), document extraction (LlamaParse, Unstructured.io).

---

## Dual-Compatibility Contract

Every `SKILL.md` must include:
```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Frontmatter:
```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

Platform Notes only. Validate after every write:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Task 1: Create `multimodal-ai` skill

**Files:**
- Create: `multimodal-ai/SKILL.md`
- Create: `multimodal-ai/references/vision-and-document-ai.md`
- Create: `multimodal-ai/references/speech-ai.md`
- Create: `multimodal-ai/references/multimodal-rag.md`

**Step 1:** Write `multimodal-ai/SKILL.md` covering:

- Modality decision table: text (LLM API), image (Vision API or on-device), audio (Whisper), document (LlamaParse + text LLM), video (frame extraction + Vision), structured data (LLM + tool use)
- Vision APIs: Claude Vision (`image/jpeg` base64 or URL), GPT-4o Vision, Gemini Vision — capability comparison, cost per image, resolution limits
- Document extraction: LlamaParse for PDF with tables and charts, Unstructured.io for mixed format batches, raw PDFPlumber for simple text PDFs
- Speech-to-text: Whisper API (OpenAI) for transcription, language detection, timestamp output — use cases (meeting notes, voice search, audio document indexing)
- Text-to-speech: ElevenLabs for voice cloning and natural speech, OpenAI TTS for cost-efficient simple output — streaming audio response
- Multimodal embeddings: CLIP (image + text in same vector space), use cases (image search, visual product similarity)
- Cost management: vision token cost = image_tokens + text_tokens, image resizing to reduce cost, caching responses for repeated images

Anti-Patterns: sending full-resolution images to Vision API when a thumbnail suffices, not batching document extraction, synchronous Whisper transcription for long audio (use async), storing base64 images in the database instead of object storage URLs.

**Step 2:** Write `references/vision-and-document-ai.md` — Node.js examples for Claude Vision API (base64 + URL), PDF extraction with LlamaParse, table data extraction prompt templates, structured JSON output from documents.

**Step 3:** Write `references/speech-ai.md` — Whisper API integration (file upload, streaming), ElevenLabs streaming TTS in a Next.js server action, WebAudio API for browser-side playback, transcription storage and indexing pipeline.

**Step 4:** Write `references/multimodal-rag.md` — RAG pipeline that accepts documents containing text, tables, and images: extract text + image alt-text, chunk, embed, store in pgvector with modality metadata, retrieve and assemble context for LLM prompt.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py multimodal-ai
git add multimodal-ai/
git commit -m "feat: add multimodal-ai skill (Vision, Whisper, TTS, document extraction, multimodal RAG)"
```

---

## Task 2: Deepen `ai-rag-patterns`

**Files:**
- Modify: `ai-rag-patterns/SKILL.md` (add implementation depth section, stay ≤ 500 lines)
- Create: `ai-rag-patterns/references/advanced-rag-techniques.md`
- Create: `ai-rag-patterns/references/multi-tenant-rag.md`
- Create: `ai-rag-patterns/references/rag-cost-management.md`

**Step 1:** Read `ai-rag-patterns/SKILL.md` in full before editing.

**Step 2:** Add **Production RAG Implementation** section to SKILL.md referencing the new reference files:
- Naive RAG → Advanced RAG → Modular RAG progression (conceptual, link to reference)
- Query transformation: HyDE (embed a hypothetical answer, search with that), multi-query (generate 3 variants, merge results)
- Contextual compression: summarise retrieved chunks to reduce tokens before injecting into LLM prompt
- Self-RAG: LLM decides whether to retrieve, retrieves, then critiques the retrieval quality before generating
- Hybrid search: vector similarity (semantic) + BM25 keyword search, Reciprocal Rank Fusion to merge results

**Step 3:** Write `references/advanced-rag-techniques.md` — LlamaIndex and LangChain.js code examples for: HyDE, multi-query retriever, contextual compression, self-RAG critic loop, hybrid search with RRF. Include benchmark: which technique improves faithfulness/relevance for which use case.

**Step 4:** Write `references/multi-tenant-rag.md` — tenant embedding isolation patterns: namespace per tenant (Pinecone), collection per tenant (Qdrant), metadata filter per tenant (pgvector). Cross-tenant leakage prevention, tenant-level index update on document change, embedding cost attribution per tenant.

**Step 5:** Write `references/rag-cost-management.md` — embedding cost table (OpenAI vs. Cohere vs. open-source), caching embedded queries (semantic deduplication), chunk size optimisation (smaller = more precise but more API calls), lazy embedding (embed at query time only if not cached).

**Step 6:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py ai-rag-patterns
git add ai-rag-patterns/
git commit -m "feat: deepen ai-rag-patterns — advanced RAG techniques, multi-tenant, cost management"
```

---

## Task 3: Deepen `ai-evaluation`

**Files:**
- Modify: `ai-evaluation/SKILL.md` (add RAGAS and drift sections, stay ≤ 500 lines)
- Create: `ai-evaluation/references/ragas-framework.md`
- Create: `ai-evaluation/references/production-drift-detection.md`

**Step 1:** Read `ai-evaluation/SKILL.md` in full before editing.

**Step 2:** Add to SKILL.md:
- RAGAS metrics: faithfulness (does answer match retrieved context?), answer relevance (does answer address the question?), context precision (are retrieved chunks relevant?), context recall (are all relevant chunks retrieved?)
- Evaluation pipeline: generate golden dataset (question + ground-truth answer pairs), run RAG pipeline, score with RAGAS, set pass/fail thresholds, block deployment if thresholds not met

**Step 3:** Write `references/ragas-framework.md` — RAGAS Python setup, golden dataset format, metric calculation, CI integration (fail build if faithfulness < 0.8), comparison across RAG versions.

**Step 4:** Write `references/production-drift-detection.md` — monitoring LLM output quality in production: log quality signals (user thumbs up/down, task completion rate), sliding window score tracking, alert when score drops > 10% week-over-week, root cause investigation checklist.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py ai-evaluation
git add ai-evaluation/
git commit -m "feat: deepen ai-evaluation — RAGAS framework, production drift detection"
```

---

## Task 4: Deepen `ai-agents-tools`

**Files:**
- Modify: `ai-agents-tools/SKILL.md` (add orchestration and guardrails, stay ≤ 500 lines)
- Create: `ai-agents-tools/references/multi-agent-orchestration.md`
- Create: `ai-agents-tools/references/agent-guardrails.md`

**Step 1:** Read `ai-agents-tools/SKILL.md` in full before editing.

**Step 2:** Add to SKILL.md:
- Multi-agent patterns: orchestrator + specialist agents, parallel execution (fan-out/fan-in), sequential pipelines, debate pattern (two agents argue, third arbitrates)
- Guardrails: input guardrail (validate before sending to LLM), output guardrail (validate before returning to user), hard stop conditions, human approval gates for irreversible actions

**Step 3:** Write `references/multi-agent-orchestration.md` — LangGraph and OpenAI Agents SDK orchestration examples: research agent (search + summarise), code generation + review agent pair, customer support triage agent routing to specialist agents.

**Step 4:** Write `references/agent-guardrails.md` — input validation (PII scrub, prompt injection detection), output validation (schema check, content policy check, factual consistency check), cost guardrail (abort if token budget exceeded), Anthropic and OpenAI guardrail patterns.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py ai-agents-tools
git add ai-agents-tools/
git commit -m "feat: deepen ai-agents-tools — multi-agent orchestration, input/output guardrails"
```

---

## Success Gate

- [ ] `multimodal-ai` passes validator, ≤ 500 lines, portable metadata present
- [ ] `ai-rag-patterns` still passes validator after enhancement, references RAGAS
- [ ] `ai-evaluation` still passes validator after enhancement
- [ ] `ai-agents-tools` still passes validator after enhancement
- [ ] No `Required Plugins` blockers in any skill

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | *AI Engineering* — Chip Huyen (O'Reilly, 2025) | Book | ~$60 | RAG depth, evaluation, AI systems design |
| 2 | *Hands-On Large Language Models* — Alammar & Grootendorst | Book | ~$60 | Visual RAG and embeddings explanations |
| 3 | *AI-Powered Search* — Trey Grainger (Manning) | Book | ~$55 | Hybrid vector + keyword search depth |
| 4 | RAGAS documentation | Free (docs.ragas.io) | Free | RAG evaluation framework |
| 5 | LlamaIndex documentation | Free (docs.llamaindex.ai) | Free | Advanced RAG technique implementations |
| 6 | LangChain RAG guide | Free (python.langchain.com/docs/tutorials/rag) | Free | HyDE, multi-query, compression patterns |
| 7 | Anthropic Cookbook | Free (github.com/anthropics/anthropic-cookbook) | Free | Claude-specific RAG and agent patterns |
| 8 | LlamaParse documentation | Free (docs.llamaindex.ai/en/stable/llama_cloud/llama_parse) | Free | Document extraction for multimodal RAG |

**Read first:** *AI Engineering* (Huyen) — the single most important book for this phase. Buy it before starting Task 2.

---

*Next → `phase-10-frontier-thought-leadership.md`*
