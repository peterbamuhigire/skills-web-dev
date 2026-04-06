# Gap Analysis — What Is Missing & How to Fill It

**April 2026 | Each gap includes: severity, impact, and the best reading material to generate a skill.**

---

## GAP 1: AI/LLM Integration (CRITICAL)

**Severity:** Critical | **Business Impact:** Existential — every product needs this by 2026

**What's missing:**
- Using Claude/GPT/Gemini/DeepSeek APIs in web and mobile apps
- RAG (Retrieval-Augmented Generation) architecture
- Prompt engineering for production systems
- Streaming responses in UI
- Function calling / tool use
- AI cost management and caching
- Embeddings and semantic search
- Guardrails and output validation
- Multi-model routing (best model per task)
- AI agent patterns in SaaS features

**Best reading material to generate this skill:**
- **Primary:** *AI Engineering* — Chip Huyen (2024) — the definitive 2024 book on LLM integration
- **Primary:** Anthropic documentation (docs.anthropic.com) — Claude API, tool use, prompt caching
- **Primary:** OpenAI Cookbook (github.com/openai/openai-cookbook) — production patterns
- **Secondary:** *Building LLM-Powered Applications* — Valentina Alto
- **Secondary:** *Prompt Engineering Guide* (promptingguide.ai)
- **Reference:** Anthropic Claude SDK docs, LangChain docs, LlamaIndex docs

**Skill to create:** `ai-llm-integration` + `ai-analytics-saas` + `ai-prompt-engineering`

---

## GAP 2: React / Next.js / TypeScript Web Frontend (CRITICAL)

**Severity:** Critical | **Business Impact:** Cannot build modern web SaaS without this

**What's missing:**
- React 19 component patterns, hooks, Server Components
- Next.js 15 App Router — layouts, loading states, error boundaries
- TypeScript strict mode patterns for React
- Tailwind CSS design system integration
- State management (Zustand, Jotai, React Query)
- Form handling (React Hook Form + Zod)
- Client-side data fetching patterns
- SSR/SSG/ISR tradeoffs for SaaS
- React Testing Library + Vitest
- Next.js deployment (Vercel, self-hosted)

**Best reading material:**
- **Primary:** *Fluent React* — Tejas Kumar (2023) — deep React internals and patterns
- **Primary:** Next.js official docs (nextjs.org/docs) — App Router
- **Primary:** *Learning TypeScript* — Josh Goldberg (2022)
- **Secondary:** *React Design Patterns* — Carlos Santana Roldán
- **Secondary:** *TypeScript Deep Dive* — Basarat Ali Syed (free online)
- **Reference:** TkDodo's React Query blog series, Kent C. Dodds' EpicReact

**Skills to create:** `react-nextjs`, `typescript-modern`, `react-state-management` (already exists as marketplace skill)

---

## GAP 3: Cloud Architecture & Deployment (CRITICAL)

**Severity:** Critical | **Business Impact:** Cannot deploy, scale, or charge for SaaS professionally

**What's missing:**
- AWS/GCP core services (EC2/Compute, S3/Storage, RDS, Lambda/Functions)
- Docker containers and Docker Compose
- CI/CD pipelines (GitHub Actions)
- Environment management (staging/production)
- SSL/TLS automation (Let's Encrypt)
- CDN configuration (CloudFront, Cloudflare)
- Auto-scaling and load balancing
- Infrastructure as Code (Terraform basics)
- Cost monitoring and optimisation
- Zero-downtime deployments

**Best reading material:**
- **Primary:** *AWS Certified Developer Study Guide* — Nick Garner + AWS Well-Architected Framework
- **Primary:** *Docker Deep Dive* — Nigel Poulton (concise, practical)
- **Primary:** *Continuous Delivery* — Jez Humble & David Farley
- **Secondary:** *Accelerate* — Forsgren, Humble, Kim (metrics for delivery performance)
- **Secondary:** *Cloud Native Patterns* — Cornelia Davis
- **Reference:** GitHub Actions documentation, Terraform getting started guide

**Skill to create:** `cloud-architecture`, `cicd-pipelines`, `docker-deployment`

---

## GAP 4: Real-Time Systems (HIGH)

**Severity:** High | **Business Impact:** Live dashboards, collaboration, notifications — expected in 2026 SaaS

**What's missing:**
- WebSockets (server + client patterns)
- Server-Sent Events for one-way streaming
- Real-time database sync (Supabase Realtime, Firebase)
- Live collaboration patterns (OT/CRDT basics)
- Presence indicators, typing indicators
- Real-time notifications architecture
- Pub/sub patterns (Redis, Pusher)
- Rate limiting real-time connections
- Mobile WebSocket clients (iOS + Android)

**Best reading material:**
- **Primary:** *Designing Data-Intensive Applications* — Martin Kleppmann — Chapter 11 (streams)
- **Primary:** *WebSocket* — Andrew Lombardi
- **Secondary:** Supabase Realtime docs, Ably documentation
- **Reference:** socket.io documentation, Pusher channels docs

**Skill to create:** `realtime-systems`

---

## GAP 5: Payment Systems & Subscription Billing (HIGH)

**Severity:** High | **Business Impact:** Direct revenue impact — no billing = no SaaS

**What's missing:**
- Stripe integration (PHP + Node.js + mobile)
- Subscription lifecycle management
- Webhook handling and idempotency
- Dunning management (failed payment recovery)
- Metered billing and usage-based pricing
- Multi-currency support
- Tax handling (VAT, GST, sales tax)
- Mobile in-app purchases linking to Stripe
- Refunds and disputes
- Revenue recognition accounting entries

**Best reading material:**
- **Primary:** Stripe documentation (stripe.com/docs) — Billing, Webhooks, Connect
- **Primary:** *Subscribed* — Tien Tzuo (the subscription economy bible)
- **Secondary:** Stripe developer blog, PaddleHQ documentation
- **Reference:** *Mastering Software Product Management* (already in library) — pricing chapters

**Skill to create:** `stripe-payments`, `subscription-billing`

---

## GAP 6: GraphQL & API-First Design (HIGH)

**Severity:** High | **Business Impact:** Modern API clients and partner integrations require this

**What's missing:**
- GraphQL schema design and resolvers
- Apollo Server / Hasura patterns
- REST API versioning strategies
- OpenAPI 3.1 specification-first design
- API authentication (OAuth2, API keys, JWT scopes)
- Rate limiting and throttling
- API documentation generation
- Webhook design and delivery guarantees
- API monetisation patterns

**Best reading material:**
- **Primary:** *The Design of Web APIs* — Arnaud Lauret (2019)
- **Primary:** *Learning GraphQL* — Eve Porcello & Alex Banks
- **Secondary:** *REST API Design Rulebook* — Mark Masse
- **Reference:** OpenAPI Initiative docs, Apollo GraphQL docs

**Skill to create:** `api-design-first`, `graphql-patterns`

---

## GAP 7: PostgreSQL & Vector Databases (HIGH)

**Severity:** High | **Business Impact:** AI features require vector search; many modern stacks use PostgreSQL

**What's missing:**
- PostgreSQL vs MySQL decision guide
- pgvector for AI similarity search
- Full-text search (PostgreSQL tsvector)
- JSONB patterns for flexible schemas
- PostgreSQL-specific optimisations
- Vector database options (Pinecone, Weaviate, Qdrant)
- Embedding storage and retrieval patterns
- Semantic search implementation

**Best reading material:**
- **Primary:** *PostgreSQL: Up and Running* — Regina Obe & Leo Hsu
- **Primary:** pgvector documentation + Supabase Vector docs
- **Secondary:** *The Art of PostgreSQL* — Dimitri Fontaine
- **Reference:** Neon.tech blog, Supabase blog on vector search

**Skill to create:** `postgresql-patterns`, `vector-databases`

---

## GAP 8: Node.js / TypeScript Backend (MEDIUM-HIGH)

**Severity:** Medium-High | **Business Impact:** Many AI/real-time features are easier in Node.js

**What's missing:**
- Node.js production patterns (Express, Fastify, Hono)
- TypeScript backend with strict typing
- Dependency injection in TypeScript (tsyringe, InversifyJS)
- ORM patterns (Prisma, Drizzle)
- Background jobs (BullMQ, Agenda)
- Caching strategies (Redis, in-memory)
- Health checks and observability
- API middleware patterns

**Best reading material:**
- **Primary:** *Node.js Design Patterns* — Mario Casciaro & Luciano Mammino (3rd ed)
- **Primary:** *Programming TypeScript* — Boris Cherny
- **Secondary:** Fastify docs, Hono docs (modern alternatives to Express)
- **Reference:** Prisma docs, BullMQ docs

**Skill to create:** `nodejs-typescript-backend`

---

## GAP 9: Testing at Scale (MEDIUM)

**Severity:** Medium | **Business Impact:** Without this, speed of delivery degrades over time

**What's missing:**
- End-to-end testing (Playwright, Cypress)
- API testing automation (Postman/Newman, REST-assured)
- Visual regression testing (Percy, Chromatic)
- Load testing (k6, Artillery)
- Contract testing (Pact)
- Test data factories and fixtures
- CI-integrated test reporting

**Best reading material:**
- **Primary:** *Testing JavaScript Applications* — Lucas da Costa
- **Primary:** Playwright documentation
- **Secondary:** *The Art of Unit Testing* — Roy Osherove
- **Reference:** k6 documentation, Pact documentation

**Skill to create:** `e2e-testing`, `load-testing`

---

## GAP 10: Observability & Monitoring (MEDIUM)

**Severity:** Medium | **Business Impact:** You cannot fix what you cannot see in production

**What's missing:**
- Structured logging patterns (JSON logs, log levels)
- Distributed tracing (OpenTelemetry)
- Error tracking (Sentry integration)
- Performance monitoring (APM)
- Uptime monitoring and alerting
- SLO/SLA definition and measurement
- Custom metrics and dashboards (Grafana, Datadog)
- Log aggregation (CloudWatch, Loki)

**Best reading material:**
- **Primary:** *Observability Engineering* — Charity Majors, Liz Fong-Jones, George Miranda
- **Primary:** OpenTelemetry documentation
- **Secondary:** Sentry documentation, Grafana documentation
- **Reference:** *Site Reliability Engineering* — Google (free online)

**Skill to create:** `observability-monitoring`

---

## GAP 11: Offline-First & Progressive Web Apps (MEDIUM)

**Severity:** Medium | **Business Impact:** East Africa connectivity patterns require offline support

**What's missing:**
- Service Worker patterns for web
- IndexedDB patterns and libraries (Dexie.js)
- Background sync strategies
- Conflict resolution for offline data
- PWA manifest, install prompts
- Cache-first vs network-first strategies
- Push notifications for PWA

**Best reading material:**
- **Primary:** *Building Progressive Web Apps* — Tal Ater
- **Secondary:** Workbox documentation (Google)
- **Reference:** web.dev PWA guide

**Skill to create:** `pwa-offline-first`

---

## Summary: Skills to Create by Priority

| Priority | Skill | Gap It Fills |
|----------|-------|--------------|
| 1 | `ai-llm-integration` | AI/LLM in every product |
| 2 | `react-nextjs` | Modern web frontend |
| 3 | `typescript-modern` | Type safety everywhere |
| 4 | `cloud-architecture` | Deployable SaaS |
| 5 | `stripe-payments` | Revenue collection |
| 6 | `realtime-systems` | Live data features |
| 7 | `api-design-first` | Professional APIs |
| 8 | `cicd-pipelines` | Automated delivery |
| 9 | `ai-analytics-saas` | AI-differentiated SaaS |
| 10 | `postgresql-patterns` | AI-ready databases |
| 11 | `nodejs-typescript-backend` | Modern backend option |
| 12 | `graphql-patterns` | Flexible API design |
| 13 | `vector-databases` | Semantic search |
| 14 | `observability-monitoring` | Production health |
| 15 | `pwa-offline-first` | East Africa resilience |

*Full roadmap: [06-new-skills-roadmap.md](06-new-skills-roadmap.md)*
