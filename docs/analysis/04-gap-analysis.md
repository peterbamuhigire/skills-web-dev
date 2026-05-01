# Gap Analysis — What Is Still Missing & How to Fill It

**April 2026 (Updated) | Gaps 1–3 from first audit now closed. New priority order below.**

---

## Gaps Closed Since First Audit ✅

| Gap | Was | Now |
|-----|-----|-----|
| AI/LLM Integration | Critical — zero skills | 28 skills, enterprise-grade |
| React/Next.js/TypeScript | Critical — 27-line stub | 6 dedicated skills |
| Real-time systems | High — nothing | realtime-systems skill added |
| API Design | Partial | api-design-first added |
| Microservices | None | 5 new skills |

---

## THE POLYGLOT PERSISTENCE PATTERN (Read This First)

> **AI-powered SaaS products use TWO databases simultaneously. This is normal and expected.**

### Why Two Databases

MySQL and vector databases solve different problems:

| Concern | MySQL | Vector DB (pgvector / Pinecone) |
|---------|-------|---------------------------------|
| Users, orders, invoices | ✅ Perfect | ❌ Wrong tool |
| Transactions, accounting | ✅ Perfect | ❌ Wrong tool |
| RBAC, permissions | ✅ Perfect | ❌ Wrong tool |
| "Find similar documents" | ❌ Cannot do this | ✅ Perfect |
| Semantic search ("find records about X") | ❌ Keyword only | ✅ Meaning-aware |
| RAG context retrieval | ❌ Cannot rank by relevance | ✅ Core use case |
| Recommendation engine | ❌ Limited | ✅ Native |

### The Architecture

```
┌─────────────────────────────────────────────────┐
│               Your SaaS App                      │
├──────────────────┬──────────────────────────────┤
│   MySQL 8        │   Vector Store                │
│   (Primary DB)   │   (AI-specific)               │
│                  │                               │
│ • Users          │ • Document embeddings         │
│ • Tenants        │ • Product description vectors │
│ • Orders         │ • Support ticket clusters     │
│ • Accounting     │ • Knowledge base chunks       │
│ • RBAC           │ • Semantic search index       │
│ • Reports        │ • Recommendation vectors      │
└──────────────────┴──────────────────────────────┘
         ↑                      ↑
    Same app, two connections. Normal.
```

### When to Use Which Vector Option

| Option | When to Use | Cost | Complexity |
|--------|-------------|------|------------|
| **pgvector** (PostgreSQL extension) | You want one DB server for both | Low (self-host) | Medium |
| **Supabase** | You want managed PostgreSQL + vector + auth | Low–Medium | Low |
| **Pinecone** | MySQL stays, add vector as a service | Medium | Low |
| **Qdrant** | Self-hosted, open source, no PostgreSQL | Low | Medium |
| **Weaviate** | Multi-modal (text + images) | Medium | High |

**Recommended starting point:** Pinecone (managed, simple API) or Qdrant (self-hosted, free).
You keep MySQL. You add a vector service alongside it. No migration required.

---

## GAP 1: Cloud Architecture & Deployment (CRITICAL)

**Severity:** Critical | **Impact:** Cannot deploy or scale SaaS without this

**What's missing:**
- AWS/GCP core services (EC2, S3, RDS, Lambda, IAM)
- Docker and Docker Compose
- GitHub Actions CI/CD pipelines
- Staging/production environment management
- SSL/TLS automation, CDN, auto-scaling
- Zero-downtime deployments

**Books to buy / find:**

| Resource | Format | Why |
|----------|--------|-----|
| *Docker Deep Dive* — Nigel Poulton | Book (~$35) | Best concise Docker book, ~220 pages |
| *Continuous Delivery* — Humble & Farley | Book (~$50) | Foundational CI/CD theory |
| AWS Well-Architected Framework | Free PDF (aws.amazon.com) | Official AWS patterns |
| *The DevOps Handbook* — Kim, Humble, Debois, Willis | Book (~$40) | Culture + practices |
| *Kubernetes: Up and Running* — Burns, Beda, Hightower | Book (~$55) | If you need container orchestration |

**Start with:** *Docker Deep Dive* + AWS Well-Architected Framework (free).

**Skills to create:** `cloud-architecture`, `cicd-pipelines`, `kubernetes-platform`, `infrastructure-as-code`

---

## GAP 2: Payment Systems & Subscription Billing (CRITICAL)

**Severity:** Critical | **Impact:** No billing = no SaaS

**What's missing:**
- Stripe integration (PHP + Node.js)
- Subscription lifecycle: create, upgrade, downgrade, cancel, pause
- Webhook handling and idempotency
- Dunning management (failed payment recovery)
- Metered billing and usage-based pricing
- Multi-currency and tax handling (VAT, GST)

**Books to buy / find:**

| Resource | Format | Why |
|----------|--------|-----|
| Stripe Documentation — stripe.com/docs | Free (online) | The authoritative source — read Billing + Webhooks |
| *Subscribed* — Tien Tzuo | Book (~$25) | The subscription economy bible — WHY subscription matters |
| Stripe Developer Blog — stripe.dev | Free (online) | Production patterns, edge cases |
| *Mastering Software Product Management* | Already in library | Pricing strategy chapters |

**Start with:** Stripe docs Billing section — it's excellent and free.

**Skills to create:** `stripe-payments`, `subscription-billing`

---

## GAP 3: PostgreSQL & pgvector (HIGH — AI-enabling)

**Severity:** High | **Impact:** Needed for pgvector RAG pipelines and Supabase projects

**Important:** You do NOT migrate from MySQL. You add PostgreSQL knowledge for
AI vector search and Supabase projects. MySQL remains your primary transactional DB.

**What's missing:**
- PostgreSQL syntax differences from MySQL (key gotchas)
- JSONB — flexible schema for AI metadata storage
- Full-text search (tsvector/tsquery) vs MySQL FULLTEXT
- pgvector: storing/querying 1536-dimension embeddings
- HNSW indexes for fast approximate nearest-neighbour search
- Supabase: PostgreSQL + auth + realtime + vector in one service
- Connection pooling with PgBouncer (important at scale)

**Books to buy / find:**

| Resource | Format | Why |
|----------|--------|-----|
| *PostgreSQL: Up and Running* — Regina Obe & Leo Hsu (O'Reilly, 3rd ed) | Book (~$50) | Best practical intro — covers core + advanced in 250 pages |
| *The Art of PostgreSQL* — Dimitri Fontaine | Book (~$40, leanpub.com) | Intermediate — SQL patterns, window functions, JSONB |
| pgvector README — github.com/pgvector/pgvector | Free (GitHub) | The definitive pgvector reference — read the entire README |
| Supabase Vector documentation — supabase.com/docs/guides/ai | Free (online) | Practical pgvector + Supabase patterns |
| Neon.tech blog on vector search | Free (online) | Real production patterns with pgvector |

**Start with:** *PostgreSQL: Up and Running* + pgvector README (free).

**Skills to create:** `postgresql-patterns`, with pgvector as a dedicated section

---

## GAP 4: Vector Databases & Embeddings (HIGH — AI-enabling)

**Severity:** High | **Impact:** RAG pipelines need a retrieval layer — this is it

**What this is:** You generate embeddings (numerical vectors representing meaning) from text
using an API (OpenAI `text-embedding-3-small`, Cohere embed, etc.), then store and query
them in a vector database to find semantically similar content.

**The RAG pipeline (requires this gap filled):**
```
User query
    → embed query (OpenAI API)
    → search vector DB for similar chunks
    → retrieve top-K chunks
    → inject chunks into LLM prompt as context
    → LLM generates answer grounded in your data
```

**What's missing:**
- Generating embeddings (OpenAI, Cohere, open-source models)
- Chunking strategies: fixed-size vs semantic vs hierarchical
- Metadata filtering: filter by tenant_id, date, document_type
- Hybrid search: combine vector similarity with keyword (BM25) search
- Re-ranking: reorder results with a cross-encoder before LLM prompt
- Vector DB options: Pinecone, Qdrant, Weaviate, Chroma (local dev)
- Production patterns: index updates, staleness, cost management

**Books to buy / find:**

| Resource | Format | Why |
|----------|--------|-----|
| *AI Engineering* — Chip Huyen (O'Reilly, 2025) | Book (~$60) | **The definitive book** — RAG chapter is the best available explanation. Buy this first. |
| *Hands-On Large Language Models* — Jay Alammar & Maarten Grootendorst (O'Reilly, 2024) | Book (~$60) | Visual, accessible — embeddings and RAG explained with diagrams |
| *AI-Powered Search* — Trey Grainger (Manning, 2024) | Book (~$55) | Hybrid search (vector + keyword) in depth |
| Pinecone documentation — docs.pinecone.io | Free (online) | Best-in-class managed vector DB docs, with code examples |
| Qdrant documentation — qdrant.tech/documentation | Free (online) | Best self-hosted option, excellent docs |
| LlamaIndex documentation — docs.llamaindex.ai | Free (online) | Practical RAG framework; shows real chunking/retrieval patterns |

**Start with:** *AI Engineering* (Chip Huyen) + Pinecone docs.
*AI Engineering* is the single most important book for this entire domain.

**Skills to create:** `vector-databases` (covers Pinecone, Qdrant, pgvector, chunking, hybrid search)

---

## GAP 5: AI RAG Patterns (Deep Implementation) (HIGH)

**Severity:** High | **Impact:** Your ai-rag-patterns skill has the theory; it needs the implementation depth

**Note:** The existing `ai-rag-patterns` skill covers RAG architecture at a conceptual level.
This gap is about the *production implementation* — the code, the failure modes, the cost patterns.

**What's still missing:**
- Naive RAG → Advanced RAG → Modular RAG progression
- Query transformation: HyDE (Hypothetical Document Embeddings), multi-query
- Contextual compression: reduce token cost by summarising retrieved chunks
- Self-RAG: LLM decides when to retrieve and whether result is relevant
- Evaluation metrics: faithfulness, answer relevance, context relevance (RAGAS framework)
- Multi-tenant RAG: isolate tenant embeddings, prevent cross-tenant retrieval
- Cost management: embedding costs, retrieval latency, LLM context costs
- Failure modes: empty retrieval, irrelevant retrieval, hallucination despite context

**Books to buy / find:**

| Resource | Format | Why |
|----------|--------|-----|
| *AI Engineering* — Chip Huyen (O'Reilly, 2025) | Book (~$60) | RAG chapter + evaluation — most complete treatment |
| *Building LLM Apps* — Valentina Alto (Packt, 2023) | Book (~$40) | End-to-end implementation with LangChain |
| RAGAS documentation — docs.ragas.io | Free (online) | RAG evaluation framework — measure your RAG quality |
| LangChain RAG guide — python.langchain.com | Free (online) | Practical patterns: multi-query, compression, self-query |
| Anthropic Cookbook — github.com/anthropics/anthropic-cookbook | Free (GitHub) | Claude-specific RAG patterns, contextual retrieval |

**Start with:** *AI Engineering* then LangChain RAG guide for the code.

**Action:** Extend existing `ai-rag-patterns` skill with implementation depth,
or create `rag-implementation` as a companion skill.

---

## GAP 6: Node.js / TypeScript Backend (PARTIALLY CLOSED ✅)

**Severity:** ~~High~~ → **Medium** | **Closed:** 2026-04-09

**What's now covered** by `nodejs-development` skill (built from 4 books):
- Module system (CJS vs ESM), event loop, reactor pattern
- Async patterns: callbacks, Promises, async/await, EventEmitter
- Streams: pipeline(), Transform, backpressure, mux/demux
- Design patterns: Factory, Builder, Proxy, Middleware, Strategy, Decorator, DI
- HTTP server/client, static file serving, Express middleware
- Error handling, cluster scaling, worker_threads, WebSockets, SSE
- Security: path traversal, AES-256-GCM, bcrypt, env validation
- Testing: Mocha/Chai, Sinon, Supertest, c8 coverage
- Deployment: pm2, cluster, Nginx, Docker, health checks

**Still missing (needs additional resources):**

| Resource | Format | Why |
|----------|--------|-----|
| Fastify documentation — fastify.dev | Free (online) | Preferred over Express; better TypeScript support |
| Prisma documentation — prisma.io/docs | Free (online) | Best TypeScript ORM for Node.js |
| BullMQ documentation — docs.bullmq.io | Free (online) | Background job queues |

**Action:** ✅ Gap fully closed. Three reference files added to `nodejs-development`:
`references/fastify.md`, `references/prisma.md`, `references/bullmq.md`

---

## GAP 7: Android AI/ML (HIGH)

**What's missing:** ML Kit, TensorFlow Lite, MediaPipe, Gemini Nano, Compose streaming

**Materials:**

| Resource | Format | Why |
|----------|--------|-----|
| Android ML Kit Guide — developers.google.com/ml-kit | Free (online) | Official guide — text, face, barcode, language |
| TensorFlow Lite Android — tensorflow.org/lite/android | Free (online) | Custom model inference |
| MediaPipe documentation — developers.google.com/mediapipe | Free (online) | Real-time vision |

**Skill to create:** `android-ai-ml`

---

## GAP 8: E2E Testing (MEDIUM)

**Materials:**

| Resource | Format | Why |
|----------|--------|-----|
| Playwright documentation — playwright.dev | Free (online) | The definitive E2E testing tool |
| *Testing JavaScript Applications* — Lucas da Costa (Manning) | Book (~$50) | Complete JS testing stack |

**Skill to create:** `e2e-testing`

---

## GAP 9: Observability & Monitoring (MEDIUM → HIGH for platform role)

**What's missing:**
- Structured logging (JSON logs, log levels, log correlation)
- Metrics collection and storage (Prometheus, VictoriaMetrics)
- Dashboards and alerting (Grafana, alert rules, PagerDuty/OpsGenie integration)
- Distributed tracing (OpenTelemetry, Jaeger)
- SigNoz — open-source all-in-one (preferred per NSANO JD: self-hosted, avoids vendor lock-in)
- SLO/SLI/SLA design and error budget tracking
- Sentry for application error monitoring (web + mobile)

**Materials:**

| Resource | Format | Why |
|----------|--------|-----|
| *Observability Engineering* — Majors, Fong-Jones, Miranda (O'Reilly) | Book (~$55) | The definitive book on this topic |
| SigNoz documentation — signoz.io/docs | Free (online) | Self-hosted Prometheus + Jaeger + dashboards in one |
| OpenTelemetry documentation — opentelemetry.io | Free (online) | Vendor-neutral instrumentation standard |
| Sentry documentation — docs.sentry.io | Free (online) | Error tracking for web + mobile |
| *Site Reliability Engineering* — Google | Free (sre.google/books) | SLO/SLI/error budget design |

**Skill to create:** `observability-platform`
**Stack alignment:** SigNoz as primary (self-hosted, open-source); PHP + Node.js + Android + iOS instrumentation examples.

---

---

## GAP 10: Infrastructure & Platform Engineering Depth (HIGH)

**Context:** Mapped against the Head of Infrastructure & Platform Engineering role at NSANO.
These are not new skill directories — they are targeted enhancements to existing skills.
The rule: enhance first, create new only when the domain is genuinely absent.

### Skills to Enhance (add sections, not create new directories)

| Enhancement | Target Skill | Section to Add |
|---|---|---|
| Secrets lifecycle — Vault deep-dive, PKI, key rotation, encryption-at-rest | `cicd-devsecops` | Full Vault operations section |
| Compliance — ISO 27001 controls, PCI-DSS requirements, audit evidence checklists | `cicd-devsecops` | Compliance mapping section |
| Container runtime security — Falco, OPA, admission controllers | `cicd-devsecops` | Runtime threat detection & policy |
| Network security — firewall rules, WAF, zero-trust, VPN design | `web-app-security-audit` | Network-layer security section |
| Reverse proxy ops — Nginx/HAProxy config, reload, rate limiting | `microservices-architecture-models` | Ops runbook section |
| API gateway ops — Kong/Traefik routing, plugins, auth | `microservices-architecture-models` | Gateway ops section |
| Workflow automation engines — n8n, Temporal, Airflow async patterns | `microservices-communication` | Async orchestration section |
| SRE practices — SLO/SLI/error budgets, blameless postmortems, escalation | `database-reliability` | Platform SRE section |
| FinOps / cost governance — resource quotas, utilisation targets, budgets | `cicd-pipeline-design` | Cost governance section |
| Linux hardening & performance tuning — sysctl, cgroups, auditd, network stack | `cicd-jenkins-debian` | Linux systems hardening section |

### New Skills to Create (genuinely absent domains)

| New Skill | Why New (Not Enhancement) | Key Books |
|---|---|---|
| `kubernetes-platform` | Zero K8s coverage — cluster management, Helm, RBAC, resource governance, pod security | *Kubernetes in Action* (Luksa); *Production Kubernetes* (Rosso et al.) |
| `infrastructure-as-code` | Zero IaC coverage — Terraform, Ansible, state mgmt, modules, GitOps (ArgoCD/Flux) | *Terraform: Up & Running* (Brikman); *Infrastructure as Code* (Morris) |

**Note:** `observability-platform` (GAP 9 above) covers the third new skill for this domain.

### Stack Alignment for All Three New Skills

- **K8s skill:** Target self-managed clusters on Debian/Ubuntu VPS first (NSANO VPS-first model), cloud-managed second
- **IaC skill:** Terraform for infrastructure, Ansible for server config (Debian/Ubuntu); GitOps via ArgoCD
- **Observability skill:** SigNoz as primary (self-hosted, open-source); PHP + Node.js + Android + iOS instrumentation

### Books to Get (Infrastructure Domain)

| Priority | Book | Covers |
|----------|------|--------|
| 1 | *Kubernetes in Action* — Marko Luksa | K8s core, cluster ops |
| 2 | *Production Kubernetes* — Rosso, Lander, Brand, Harris | Ops-grade K8s, security |
| 3 | *Terraform: Up & Running* — Brikman (3rd ed.) | IaC fundamentals, modules |
| 4 | *Infrastructure as Code* — Kief Morris (O'Reilly, 2nd ed.) | IaC patterns, GitOps |
| 5 | *The Practice of Cloud System Administration* — Limoncelli et al. | SRE + Linux ops |
| 6 | *Linux System Administration Handbook* — Nemeth et al. | Linux hardening |

---

## Priority Book Shopping List

If you were buying books today, in order of ROI:

| Priority | Book | Price | Closes Which Gap |
|----------|------|-------|-----------------|
| 1 | *AI Engineering* — Chip Huyen (O'Reilly 2025) | ~$60 | RAG + Vector DB + AI systems (covers 3 gaps) |
| 2 | *Hands-On Large Language Models* — Alammar & Grootendorst | ~$60 | Embeddings + RAG visually explained |
| 3 | *PostgreSQL: Up and Running* — Obe & Hsu (O'Reilly) | ~$50 | PostgreSQL + pgvector foundation |
| 4 | *Docker Deep Dive* — Nigel Poulton | ~$35 | Cloud + deployment |
| 5 | *Subscribed* — Tien Tzuo | ~$25 | Subscription billing strategy |
| 6 | *Node.js Design Patterns* — Casciaro & Mammino (3rd ed) | ~$45 | Modern Node.js backend |
| 7 | *Observability Engineering* — Majors et al. | ~$55 | Production monitoring |
| 8 | *AI-Powered Search* — Trey Grainger (Manning) | ~$55 | Hybrid vector + keyword search |

**Free resources that replace books:**
- Stripe docs (replaces any Stripe book)
- pgvector README on GitHub (essential, free)
- Pinecone or Qdrant docs (excellent, free)
- Anthropic Cookbook on GitHub (Claude-specific RAG patterns)
- LlamaIndex docs (practical RAG framework)
- Supabase Vector docs (pgvector + managed PostgreSQL)

---

## Summary: Remaining Skills to Create by Priority

| Priority | Skill | Key Resource |
|----------|-------|--------------|
| 1 | `cloud-architecture` | *Docker Deep Dive* + AWS Well-Architected |
| 2 | `kubernetes-platform` | *Kubernetes in Action* + *Production Kubernetes* |
| 3 | `infrastructure-as-code` | *Terraform: Up & Running* + *Infrastructure as Code* |
| 4 | `stripe-payments` | Stripe docs (free) |
| 5 | `cicd-pipelines` | *Continuous Delivery* + GitHub Actions docs |
| 6 | `observability-platform` | *Observability Engineering* + SigNoz docs |
| 7 | `android-ai-ml` | ML Kit docs (free) |
| 8 | `e2e-testing` | Playwright docs (free) |
| 9 | `subscription-billing` | *Subscribed* + Stripe Billing docs |
| 10 | `pwa-offline-first` | Workbox docs (free) |

## Summary: Existing Skills to Enhance (No New Directory)

| Skill | What to Add |
|-------|-------------|
| `cicd-devsecops` | Vault lifecycle, ISO 27001, PCI-DSS controls, container runtime security |
| `database-reliability` | Platform SRE section — SLO/SLI, error budgets, postmortems |
| `microservices-architecture-models` | Reverse proxy ops, API gateway ops (Kong/Traefik) |
| `web-app-security-audit` | Network security layer (firewall, WAF, zero-trust, VPN) |
| `cicd-pipeline-design` | FinOps / cost governance section |
| `cicd-jenkins-debian` | Linux hardening & performance tuning (sysctl, cgroups, auditd) |
| `microservices-communication` | Workflow automation engines (n8n, Temporal, Airflow) |

*Full roadmap: [06-new-skills-roadmap.md](06-new-skills-roadmap.md)*
