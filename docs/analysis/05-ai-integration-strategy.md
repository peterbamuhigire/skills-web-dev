# AI Integration Strategy

**How to build AI into every layer of your product stack**
**April 2026 | Based on current skills + frontier requirements**

---

## The Core Principle

> Every product you build from 2026 onwards should have at least one AI-powered feature.
> Not as a gimmick — as genuine value that users cannot get anywhere else.

Your current skills cover AI orchestration *for Claude Code development workflows*.
What is completely absent is AI *inside your products* — features powered by LLMs that
make your apps smarter, more personal, and worth more money.

---

## AI Layers in a SaaS Product

```
┌─────────────────────────────────────────────┐
│           USER-FACING AI FEATURES           │  ← What users see and pay for
│  Smart search, auto-fill, explanations,     │
│  recommendations, anomaly alerts            │
├─────────────────────────────────────────────┤
│           AI ANALYTICS ENGINE               │  ← Insights from user data
│  Embeddings, clustering, trend detection,   │
│  churn prediction, revenue forecasting      │
├─────────────────────────────────────────────┤
│           RAG / KNOWLEDGE LAYER             │  ← Context injection
│  Vector search, document Q&A,              │
│  policy lookup, semantic search             │
├─────────────────────────────────────────────┤
│           LLM INTEGRATION LAYER             │  ← API calls, prompts, tools
│  Claude/GPT/Gemini/DeepSeek routing,       │
│  prompt management, caching, fallbacks      │
├─────────────────────────────────────────────┤
│           AI INFRASTRUCTURE                 │  ← Cost and reliability
│  Model routing, prompt caching, rate limits,│
│  token tracking, budget controls            │
└─────────────────────────────────────────────┘
```

---

## API Ecosystem You Must Master

### Tier 1 — Primary Models
| Provider | Best For | Key Differentiator |
|----------|----------|-------------------|
| **Anthropic Claude** | Complex reasoning, documents, code | Best context window, tool use |
| **OpenAI GPT-4o** | Multimodal, established ecosystem | Widest third-party support |
| **Google Gemini** | Long documents, Google Workspace | Native Google integrations |
| **DeepSeek** | Cost-efficient coding/reasoning | Chinese market, low cost |

### Tier 2 — Specialised Models
| Provider | Best For |
|----------|----------|
| **Whisper (OpenAI)** | Speech-to-text in mobile apps |
| **ElevenLabs** | Text-to-speech for voice features |
| **Stability AI** | Image generation |
| **Cohere** | Embeddings, enterprise RAG |
| **Mistral** | European privacy compliance |

### Key Principle: Never Hard-Code a Single Provider
Build a model router from day one. Route by: capability, cost, latency, and compliance region.

---

## Skills You Need to Build

### 1. `ai-llm-integration` (Priority 1)
**Core topics:**
- Anthropic SDK (Python + TypeScript + PHP)
- OpenAI SDK integration
- Streaming responses to web and mobile UI
- Tool use / function calling patterns
- Prompt templates and versioning
- Conversation history management
- Output parsing and validation
- Error handling (rate limits, context overflow, model errors)
- Prompt caching (Anthropic 90% cost reduction)
- Multi-provider fallback routing

**Source material:** *AI Engineering* (Chip Huyen 2024), Anthropic docs

### 2. `ai-analytics-saas` (Priority 9)
**Core topics:**
- Embedding user behaviour data
- Semantic clustering of support tickets
- Anomaly detection for financial data
- Churn prediction signals
- Natural language query of business data (Text-to-SQL)
- Automated insight generation (weekly summaries)
- Dashboard co-pilot patterns
- Privacy-safe analytics (no PII in prompts)

**Source material:** *AI Engineering*, *Designing ML Systems* (Chip Huyen)

### 3. `ai-prompt-engineering` (Priority 3 sub-skill)
**Core topics:**
- System prompt architecture
- Few-shot examples for consistency
- Chain-of-thought for complex tasks
- Self-consistency and verification
- Constitutional AI principles in prompts
- Prompt injection prevention
- A/B testing prompts in production
- Prompt version control

**Source material:** Anthropic prompt engineering guide, *Prompt Engineering Guide* (DAIR.AI)

### 4. `vector-databases` (Priority 13)
**Core topics:**
- Embedding generation (text-embedding-3-small, Cohere embed)
- pgvector for PostgreSQL
- Pinecone / Qdrant / Weaviate patterns
- Chunking strategies for documents
- Metadata filtering
- Hybrid search (vector + keyword)
- RAG pipeline architecture
- Re-ranking results

---

## AI in Mobile Apps

### iOS AI Features (Extend `ios-ai-ml`)
Current: CoreML, Vision, NaturalLanguage, CreateML.
**Add:**
- On-device LLM inference (Apple Intelligence APIs, iOS 18+)
- Streaming Claude/GPT responses in SwiftUI
- AI-powered camera features (Vision + LLM description)
- Voice interfaces (Whisper + ElevenLabs)
- Offline AI with Core ML models
- Privacy-preserving on-device processing

### Android AI Features
**Create `android-ai-ml`:**
- ML Kit (Google's on-device ML)
- TensorFlow Lite integration
- MediaPipe for real-time vision
- Gemini Nano (on-device, Android 14+)
- Streaming AI responses in Compose UI
- Voice interfaces

---

## AI Safety in Production

Every AI feature must have:
1. **Output validation** — LLMs hallucinate. Validate structure, check facts where possible.
2. **User transparency** — Mark AI-generated content clearly. Don't mislead users.
3. **Graceful degradation** — If AI fails, the core feature still works.
4. **Cost limits** — Set per-user, per-day token budgets. Prevent cost bombs.
5. **PII guards** — Strip or mask personal data before sending to external APIs.
6. **Audit logs** — Log all AI calls for debugging and compliance.
7. **Human override** — Critical AI decisions must be reviewable/overridable.

---

## AI Features That Justify Premium Pricing

These are features users will pay extra for:

| Feature | Monetisation Model | Implementation |
|---------|-------------------|----------------|
| Document Q&A | Per-query or premium tier | RAG + LLM |
| Smart data entry | Included in paid plan | LLM extraction from documents |
| Automated reports with narrative | Premium feature | LLM summarisation |
| Anomaly alerts with explanation | Premium tier | ML + LLM explanation |
| Natural language search | Premium or included | Embeddings + semantic search |
| AI assistant / co-pilot | Highest tier | Full LLM integration |
| Predictive analytics | Analytics tier | Embeddings + ML models |

---

## Recommended Reading — AI Integration

| Book / Resource | Priority | Why |
|----------------|----------|-----|
| *AI Engineering* — Chip Huyen (2024) | P1 | Best modern LLM integration book |
| Anthropic Cookbook (github) | P1 | Production Claude patterns |
| *Designing ML Systems* — Chip Huyen | P2 | Production ML at scale |
| *Building LLM Apps* — Valentina Alto | P2 | End-to-end LLM app development |
| *Prompt Engineering Guide* (DAIR.AI) | P2 | Prompting science and patterns |
| *AI-Powered Search* — Trey Grainger | P3 | Semantic and hybrid search |
| *The Deep Learning Book* — Goodfellow | P4 | Foundations (optional depth) |

---

## Implementation Order

1. **Build `ai-llm-integration` skill** — covers the API integration layer
2. **Add AI feature to one existing product** — prove the pattern works
3. **Build `ai-prompt-engineering` skill** — production prompt management
4. **Build `vector-databases` skill** — unlock RAG and semantic search
5. **Build `ai-analytics-saas` skill** — AI insights in every SaaS dashboard
6. **Extend `ios-ai-ml`** — on-device + cloud AI for iOS
7. **Create `android-ai-ml`** — parity for Android

---

*Next: [06-new-skills-roadmap.md](06-new-skills-roadmap.md)*
