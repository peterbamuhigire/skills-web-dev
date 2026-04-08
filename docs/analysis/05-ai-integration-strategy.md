# AI Integration Strategy

**How AI is now integrated across every layer of your product stack**
**April 2026 (Updated) | 28 AI skills built — ecosystem is complete**

---

## The Core Achievement

Since the first audit identified AI/LLM integration as the single biggest gap,
**28 AI skills have been built** covering every layer from API integration to cost billing
to safety to evaluation. The gap has been closed.

The next phase is **applying this ecosystem to products** — not building more foundational skills.

---

## The Dual-Database Architecture for AI Apps

Every AI-powered SaaS you build will use two data stores simultaneously. This is the
standard production pattern — not a special case.

```
Your SaaS Product
        │
        ├──► MySQL 8 (Primary)
        │       Users, tenants, orders, accounting,
        │       RBAC, reports, all transactional data
        │
        └──► Vector Store (AI-specific)
                Document embeddings, semantic search index,
                knowledge base chunks, recommendation vectors
                
Options for vector store:
  • pgvector on PostgreSQL — one server, SQL interface
  • Pinecone — managed service, simple REST API
  • Qdrant — self-hosted, open source, excellent performance
  • Supabase — PostgreSQL + pgvector + auth + realtime managed
```

**No migration needed.** MySQL stays. You add a vector connection alongside it.
A typical Node.js/PHP app has `$mysqlConnection` and `$pineconeClient` as separate objects.

### The Embedding Pipeline (How Data Gets In)

```
New document saved to MySQL
        │
        ▼
Chunk the text (500–1000 tokens per chunk)
        │
        ▼
Send each chunk to embedding API
(OpenAI text-embedding-3-small: $0.02 / 1M tokens)
        │
        ▼
Store vector + metadata in vector DB
{ vector: [0.12, -0.45, ...1536 dimensions],
  metadata: { tenant_id, doc_id, chunk_index } }
        │
        ▼
At query time: embed the query → search vector DB
→ retrieve top-K chunks → inject into LLM prompt
```

---

## AI Ecosystem Map (Current State)

```
┌─────────────────────────────────────────────┐
│       USER-FACING AI FEATURES               │
│  ai-ux-patterns, ai-slop-prevention         │
│  ai-opportunity-canvas, ai-feature-spec     │
├─────────────────────────────────────────────┤
│       AI ANALYTICS ENGINE                   │
│  ai-analytics-saas, ai-analytics-dashboards │
│  ai-predictive-analytics, ai-nlp-analytics  │
│  ai-analytics-strategy                      │
├─────────────────────────────────────────────┤
│       RAG / KNOWLEDGE LAYER                 │
│  ai-rag-patterns, vector-databases (TODO)   │
│  ai-web-apps                                │
├─────────────────────────────────────────────┤
│       LLM INTEGRATION LAYER                 │
│  ai-llm-integration, ai-prompt-engineering  │
│  ai-agents-tools, openai-agents-sdk         │
│  deepseek-integration                       │
├─────────────────────────────────────────────┤
│       COST & SAFETY INFRASTRUCTURE          │
│  ai-cost-modeling, ai-metering-billing      │
│  ai-saas-billing, ai-security, llm-security │
│  ai-error-handling, ai-error-prevention     │
│  ai-evaluation                              │
└─────────────────────────────────────────────┘
```

---

## API Ecosystem (Covered by Skills)

### Tier 1 — Primary Models
| Provider | Skill | Best For |
|----------|-------|----------|
| Anthropic Claude | ai-llm-integration | Complex reasoning, documents, code |
| OpenAI GPT-4o | ai-llm-integration, openai-agents-sdk | Multimodal, widest ecosystem |
| DeepSeek V3/R1 | deepseek-integration | Cost-efficient coding, local deployment |
| Google Gemini | ai-llm-integration | Long documents, Google Workspace |

### Tier 2 — Specialised (Covered in ai-llm-integration)
- Whisper (speech-to-text), ElevenLabs (TTS), Cohere (embeddings)

### Key Principle: Never Hard-Code a Single Provider
`ai-architecture-patterns` defines the model router pattern. Route by:
capability, cost, latency, and compliance region.

---

## What Each AI Skill Does

### Integration Foundation
- **ai-llm-integration** — Direct API calls, streaming, tool use, caching, multi-provider
- **ai-prompt-engineering** — Templates, CoT, versioning, defensive prompting
- **ai-agents-tools** — ReAct loop, tool definitions, multi-agent orchestration

### Product & Analytics
- **ai-opportunity-canvas** — Discover which AI features to build first
- **ai-feature-spec** — Design one AI feature end-to-end
- **ai-analytics-saas** — NL2SQL, embeddings, anomaly detection inside SaaS
- **ai-analytics-dashboards** — KPI cards, AI Insights panel, role-based views
- **ai-predictive-analytics** — LLM-based predictions without ML infrastructure
- **ai-nlp-analytics** — Sentiment, classification, NER, multi-language

### Architecture & Cost
- **ai-architecture-patterns** — Module gate, budget guard, provider abstraction
- **ai-app-architecture** — AI-powered app stack design
- **ai-cost-modeling** — Token economics, per-user/tenant cost calculator
- **ai-metering-billing** — Token ledger schema, middleware, invoice generation
- **ai-saas-billing** — Module gating (off by default), quota management

### Safety & Quality
- **ai-security** — Prompt injection, PII scrubbing, DPPA compliance
- **llm-security** — OWASP LLM Top 10, trust boundaries
- **ai-error-handling** — 5-layer validation stack, quality scoring
- **ai-error-prevention** — Verify-first, TDD for AI output
- **ai-evaluation** — Golden test sets, AI-as-judge, drift detection

---

## AI in Mobile Apps

### iOS — Already Well-Covered
`ios-ai-ml` covers: CoreML, Vision, NaturalLanguage, CreateML.
**Still needed:** On-device LLM inference via Apple Intelligence APIs (iOS 18+),
streaming Claude/GPT responses in SwiftUI, privacy-preserving on-device processing.
**Action:** Extend `ios-ai-ml` when Apple Intelligence APIs stabilise.

### Android — Gap
`android-ai-ml` skill does not exist yet.
**Needs:** ML Kit, TensorFlow Lite, MediaPipe, Gemini Nano (on-device, Android 14+),
streaming AI responses in Compose UI.
**Action:** Create `android-ai-ml` — this is GAP 5 in the gap analysis.

---

## AI Safety — Non-Negotiable Requirements

Every AI feature must implement (covered across `ai-security`, `ai-error-handling`):

1. **Output validation** — validate structure, check for hallucinations where possible
2. **User transparency** — mark AI-generated content clearly
3. **Graceful degradation** — if AI fails, core feature still works
4. **Cost limits** — per-user, per-day token budgets (ai-saas-billing)
5. **PII guards** — strip/mask personal data before sending to external APIs
6. **Audit logs** — log all AI calls for debugging and compliance
7. **Human override** — critical AI decisions must be reviewable

---

## AI Features That Justify Premium Pricing

These justify higher tier pricing per `ai-saas-billing` module gating:

| Feature | Skill to Build With | Tier |
|---------|---------------------|------|
| Document Q&A | ai-rag-patterns + ai-llm-integration | Premium |
| Smart data entry | ai-llm-integration | Paid |
| Automated reports with narrative | ai-predictive-analytics | Premium |
| Anomaly alerts with explanation | ai-analytics-saas | Premium |
| Natural language search | ai-analytics-saas | Paid/Premium |
| AI assistant / co-pilot | ai-agents-tools | Highest |
| Predictive analytics dashboard | ai-analytics-dashboards | Premium |

---

## Next Actions — AI Is Now Feature Work, Not Skill Building

1. **Pick one SaaS product** and apply the ai-opportunity-canvas skill to identify AI features
2. **Use ai-feature-spec** to design the first AI feature end-to-end
3. **Build it with ai-llm-integration** — streaming response in the UI
4. **Apply ai-cost-modeling** — price the feature into a tier
5. **Create `vector-databases` skill** — the one remaining AI infrastructure gap
6. **Create `android-ai-ml` skill** — close the mobile AI parity gap

---

*Next: [06-new-skills-roadmap.md](06-new-skills-roadmap.md)*
