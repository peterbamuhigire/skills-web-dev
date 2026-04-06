# New Skills Roadmap — 34 Skills to Build

**Priority-ordered creation plan | April 2026**

---

## Phase 1 — Critical Frontier (Build in 2026 Q2–Q3)

These are blockers. Without them, you cannot build world-class products today.

### 1. `ai-llm-integration`
**What:** Production LLM integration — Claude, GPT, Gemini, DeepSeek
**Covers:** SDK setup, streaming, tool use, prompt templates, caching, error handling, cost control
**Source:** *AI Engineering* (Huyen 2024) + Anthropic docs + OpenAI Cookbook
**Creates:** The foundation for every AI feature in every product

### 2. `react-nextjs`
**What:** React 19 + Next.js 15 App Router patterns
**Covers:** Server Components, streaming, layouts, error boundaries, data fetching, deployment
**Source:** *Fluent React* (Kumar), Next.js official docs, TkDodo's React Query guide
**Creates:** Full web frontend capability for SaaS

### 3. `typescript-modern`
**What:** TypeScript strict mode patterns for frontend and backend
**Covers:** Type narrowing, generics, utility types, branded types, Zod validation
**Source:** *Learning TypeScript* (Goldberg), *Programming TypeScript* (Cherny)
**Creates:** Type-safe development across the full stack

### 4. `cloud-architecture`
**What:** AWS/GCP core services for SaaS deployment
**Covers:** Compute, storage, RDS, CDN, IAM, auto-scaling, cost optimisation
**Source:** AWS Well-Architected Framework, *Docker Deep Dive* (Poulton)
**Creates:** Ability to deploy and scale production SaaS

### 5. `stripe-payments`
**What:** Stripe integration for SaaS billing
**Covers:** Products, prices, subscriptions, webhooks, dunning, customer portal, tax
**Source:** Stripe documentation (stripe.com/docs/billing)
**Creates:** Revenue collection infrastructure

### 6. `cicd-pipelines`
**What:** GitHub Actions CI/CD for web + mobile
**Covers:** Automated testing, build + deploy pipelines, secrets management, environments
**Source:** *Continuous Delivery* (Humble & Farley), GitHub Actions docs
**Creates:** Fast, safe software delivery

---

## Phase 2 — High Value (Build in 2026 Q4)

### 7. `realtime-systems`
**What:** WebSockets, SSE, live data in web and mobile
**Covers:** WebSocket server/client, SSE streaming, Supabase Realtime, Redis pub/sub
**Source:** *Designing Data-Intensive Applications* (Kleppmann, Ch11), socket.io docs

### 8. `api-design-first`
**What:** OpenAPI 3.1 specification-first REST API design
**Covers:** Schema design, versioning, authentication, rate limiting, documentation generation
**Source:** *The Design of Web APIs* (Lauret), OpenAPI Initiative docs

### 9. `ai-analytics-saas`
**What:** AI-powered analytics features inside SaaS products
**Covers:** Embedding user data, anomaly detection, churn signals, text-to-SQL, NL summaries
**Source:** *AI Engineering* (Huyen), *Designing ML Systems* (Huyen)

### 10. `postgresql-patterns`
**What:** PostgreSQL for modern SaaS (especially AI-adjacent features)
**Covers:** vs MySQL guide, JSONB, full-text search, window functions, migrations
**Source:** *PostgreSQL: Up and Running* (Obe & Hsu)

### 11. `nodejs-typescript-backend`
**What:** Node.js production patterns with TypeScript
**Covers:** Fastify/Hono setup, Prisma ORM, BullMQ jobs, Redis caching, health checks
**Source:** *Node.js Design Patterns* (Casciaro & Mammino, 3rd ed)

### 12. `vector-databases`
**What:** Embeddings, vector search, RAG infrastructure
**Covers:** pgvector, Pinecone/Qdrant, chunking, hybrid search, re-ranking
**Source:** pgvector docs, *AI-Powered Search* (Grainger), Supabase Vector docs

---

## Phase 3 — Depth Expansion (Build in 2027 Q1–Q2)

### 13. `graphql-patterns`
**What:** GraphQL schema design and resolver patterns
**Covers:** Schema-first design, Apollo Server, N+1 prevention, subscriptions, federation
**Source:** *Learning GraphQL* (Porcello & Banks), Apollo docs

### 14. `observability-monitoring`
**What:** Production visibility for SaaS
**Covers:** Structured logging, OpenTelemetry tracing, Sentry errors, Grafana dashboards
**Source:** *Observability Engineering* (Majors, Fong-Jones, Miranda)

### 15. `pwa-offline-first`
**What:** Progressive Web Apps with offline capabilities
**Covers:** Service Workers, IndexedDB, background sync, PWA manifest, install flows
**Source:** *Building Progressive Web Apps* (Ater), Workbox docs

### 16. `android-ai-ml`
**What:** Android AI/ML features
**Covers:** ML Kit, TensorFlow Lite, MediaPipe, Gemini Nano (on-device), streaming AI in Compose
**Source:** Android ML Kit docs, TFLite guide

### 17. `subscription-billing`
**What:** Full subscription lifecycle management
**Covers:** Dunning, metered billing, upgrade/downgrade flows, revenue recognition, multi-currency
**Source:** *Subscribed* (Tzuo), Stripe Billing docs

### 18. `product-led-growth`
**What:** PLG tactics for SaaS products
**Covers:** Freemium design, activation flows, in-app upgrade prompts, viral loops, NPS
**Source:** *Product-Led Growth* (Wes Bush), *Escaping the Build Trap* (Perri, already in library)

---

## Phase 4 — Competitive Moats (Build in 2027 Q3–Q4)

### 19. `event-driven-architecture`
**What:** Event sourcing, CQRS, message queues for SaaS
**Covers:** Domain events, event store, projections, RabbitMQ/SQS, saga patterns
**Source:** *Building Event-Driven Microservices* (Bellemare)

### 20. `microservices-patterns`
**What:** Service decomposition for growing SaaS
**Covers:** Service boundaries, inter-service auth, distributed transactions, service mesh basics
**Source:** *Building Microservices* (Sam Newman, 2nd ed)

### 21. `accessibility-wcag`
**What:** WCAG 2.2 AA compliance implementation
**Covers:** Semantic HTML, ARIA, keyboard navigation, screen readers, colour contrast, testing
**Source:** WCAG 2.2 specification, *Accessibility for Everyone* (Laura Kalbag)

### 22. `web-performance-advanced`
**What:** Beyond Core Web Vitals — server-side performance
**Covers:** TTFB reduction, edge caching, HTTP/3, resource hints, bundle splitting
**Source:** *High Performance Web Sites* (Souders), web.dev performance guide

### 23. `mobile-payments`
**What:** In-app purchases + payment methods on mobile
**Covers:** StoreKit 2 (already in ios-monetization), Google Play Billing, Stripe mobile SDKs
**Source:** Extends existing ios-monetization, Google Play Billing docs

### 24. `saas-growth-metrics`
**What:** Instrument and act on SaaS growth metrics
**Covers:** Funnel analytics, cohort analysis, feature usage tracking, A/B testing implementation
**Source:** *Hacking Growth* (Ellis & Brown), Mixpanel/PostHog docs

---

## Phase 5 — 2028–2030 Frontier

### 25. `ai-agents-production`
**What:** Autonomous AI agents in SaaS products
**Covers:** Agent loops, tool orchestration, memory patterns, human-in-the-loop, safety
**Source:** Anthropic agents docs, *AI Engineering* advanced chapters

### 26. `edge-computing`
**What:** Edge functions and distributed execution
**Covers:** Cloudflare Workers, Vercel Edge, Deno Deploy, edge databases (D1, Turso)
**Source:** Cloudflare Workers docs, *Edge Computing* patterns

### 27. `multimodal-ai`
**What:** Vision, audio, and document AI in products
**Covers:** Image analysis (Claude Vision, GPT-4V), audio transcription, document extraction
**Source:** Claude Vision docs, Whisper API docs

### 28. `react-native-advanced`
**What:** React Native for production cross-platform apps
**Covers:** New Architecture (JSI/Fabric), native modules, Expo EAS, performance profiling
**Source:** *Fullstack React Native*, React Native New Architecture docs

### 29. `web3-basics` (optional, watch-and-wait)
**What:** Blockchain integration for specific use cases
**Covers:** Wallet connect, token gating, NFTs as certificates, smart contract reading
**Note:** Only if clients request it — don't over-invest speculatively

### 30. `ar-vr-interfaces` (2028+)
**What:** Augmented/Virtual reality UI for mobile
**Covers:** ARKit, ARCore, Apple Vision Pro, spatial UI patterns
**Source:** ARKit docs, Apple Vision Pro Human Interface Guidelines

---

## Phase 6 — Skills Library Maintenance

### 31. Complete `webapp-gui-design`
Full React + Tailwind design system guide. Currently 27 lines.

### 32. Complete `pos-restaurant-ui-standard`
Complete restaurant POS patterns. Currently 39 lines.

### 33. Complete `inventory-management`
Full inventory management patterns including barcode, batch operations. Currently 40 lines.

### 34. Create `ai-prompt-engineering`
Standalone prompt engineering skill extracted from ai-llm-integration depth.

---

## Summary Timeline

| Year | Skills to Create | Theme |
|------|-----------------|-------|
| 2026 Q2-Q3 | 1–6 | Close critical gaps |
| 2026 Q4 | 7–12 | High-value additions |
| 2027 Q1-Q2 | 13–18 | Depth + PLG |
| 2027 Q3-Q4 | 19–24 | Competitive moats |
| 2028–2030 | 25–30 | Frontier technologies |
| Ongoing | 31–34 | Complete stubs + maintenance |

**Total: 34 new skills** — growing the library from 131 to 165 skills.

---

*Next: [07-wealth-accumulation-engine.md](07-wealth-accumulation-engine.md)*
