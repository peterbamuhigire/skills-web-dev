# New Skills Roadmap — Revised Priority

**Re-prioritised after AI, iOS, and web frontend enhancements | April 2026**

---

## What Has Been Built (No Longer Needed)

The following Phase 1 and Phase 2 skills from the original roadmap now exist:

| Original Priority | Skill | Status |
|-------------------|-------|--------|
| 1 | ai-llm-integration | ✅ Built (+ 27 more AI skills) |
| 2 | react-nextjs | ✅ Built as react-development + react-patterns |
| 3 | typescript-modern | ✅ Built as typescript-mastery + typescript-design-patterns |
| 7 | realtime-systems | ✅ Built |
| 8 | api-design-first | ✅ Built |
| Bonus | microservices-* | ✅ 5 skills built |

---

## Phase 1 — Critical Infrastructure (Build in 2026 Q2–Q3)

### 1. `cloud-architecture`
**What:** AWS/GCP core services for SaaS deployment
**Covers:** Compute, storage, RDS, CDN, IAM, auto-scaling, Docker, cost optimisation
**Source:** AWS Well-Architected Framework (free) + *Docker Deep Dive* (Poulton)
**Creates:** Ability to deploy and scale production SaaS without DevOps help

### 2. `stripe-payments`
**What:** Stripe integration for SaaS billing — the revenue layer
**Covers:** Products, prices, subscriptions, webhooks, dunning, customer portal, tax
**Source:** Stripe documentation (stripe.com/docs/billing)
**Creates:** Revenue collection infrastructure for every SaaS product

### 3. `postgresql-patterns`
**What:** PostgreSQL core patterns — additive to MySQL, not a replacement
**Covers:** Syntax differences from MySQL, JSONB, full-text search, migrations
**Source:** *PostgreSQL: Up and Running* (Obe & Hsu)
**Note:** You stay on MySQL for existing products. This skill unlocks Supabase,
pgvector, and PostgreSQL-native client projects.

### 4. `vector-databases`
**What:** Embeddings, vector search, and RAG storage infrastructure
**Covers:** pgvector for PostgreSQL, Pinecone/Qdrant/Weaviate, chunking, hybrid search
**Source:** pgvector docs, Supabase Vector docs, *AI-Powered Search* (Grainger)
**Creates:** The missing storage layer for RAG pipelines (ai-rag-patterns theory already exists)

### 5. `cicd-pipelines`
**What:** GitHub Actions CI/CD for web + mobile
**Covers:** Automated testing, build/deploy pipelines, secrets, environments, Fastlane iOS
**Source:** *Continuous Delivery* (Humble & Farley), GitHub Actions documentation
**Creates:** Fast, repeatable, safe delivery on every commit

### 6. `nodejs-typescript-backend`
**What:** Node.js production server with TypeScript
**Covers:** Fastify/Hono, Prisma ORM, BullMQ, Redis caching, health checks, Zod validation
**Source:** *Node.js Design Patterns* (Casciaro & Mammino, 3rd ed)
**Creates:** Modern server-side option alongside PHP

---

## Phase 2 — Platform Depth (Build in 2026 Q4)

### 7. `android-ai-ml`
**What:** Android AI and ML integration
**Covers:** ML Kit, TensorFlow Lite, MediaPipe, Gemini Nano (on-device), Compose streaming
**Source:** Android ML Kit docs, TFLite Android guide
**Creates:** Parity with ios-ai-ml for Android projects

### 8. `subscription-billing`
**What:** Full subscription lifecycle management beyond basic Stripe setup
**Covers:** Dunning, metered billing, upgrade/downgrade flows, multi-currency, revenue recognition
**Source:** *Subscribed* (Tzuo), Stripe Billing deep docs
**Creates:** Complete billing lifecycle for SaaS products

### 9. `observability-monitoring`
**What:** Production visibility for SaaS
**Covers:** Structured JSON logging, Sentry error tracking, OpenTelemetry, Grafana, SLOs
**Source:** *Observability Engineering* (Majors, Fong-Jones, Miranda)
**Creates:** Ability to diagnose and fix production issues fast

### 10. `pwa-offline-first`
**What:** Progressive Web Apps with offline capabilities
**Covers:** Workbox, Service Workers, IndexedDB (Dexie.js), background sync, PWA manifest
**Source:** Workbox docs, *Building Progressive Web Apps* (Ater)
**Creates:** Web apps that work in East Africa's variable connectivity

### 11. `e2e-testing`
**What:** End-to-end testing with Playwright
**Covers:** Page Object Model, network mocking, visual regression, CI integration
**Source:** Playwright documentation, *Testing JavaScript Applications* (da Costa)
**Creates:** Delivery confidence without slowing down

---

## Phase 3 — Competitive Moats (Build in 2027 Q1–Q2)

### 12. `product-led-growth`
**What:** PLG tactics for SaaS products
**Covers:** Freemium design, activation flows, in-app upgrade prompts, viral loops, NPS
**Source:** *Product-Led Growth* (Wes Bush), *Escaping the Build Trap* (Perri — in library)

### 13. `event-driven-architecture`
**What:** Event sourcing, CQRS, message queues for scaling SaaS
**Covers:** Domain events, event store, projections, RabbitMQ/SQS, saga patterns
**Source:** *Building Event-Driven Microservices* (Bellemare)

### 14. `graphql-patterns`
**What:** GraphQL schema design and resolver patterns (graphql-security already exists)
**Covers:** Schema-first design, Apollo Server, N+1 prevention, federation
**Source:** *Learning GraphQL* (Porcello & Banks), Apollo docs

### 15. `saas-growth-metrics`
**What:** Instrument and act on product growth metrics
**Covers:** Funnel analytics, cohort analysis, feature usage, A/B testing implementation
**Source:** *Hacking Growth* (Ellis & Brown), PostHog docs

---

## Phase 4 — Stubs to Complete (Ongoing)

### 16. Complete `webapp-gui-design`
Full React + Tailwind component architecture guide. Currently 27 lines.
With react-development, nextjs-app-router, and tailwind-css existing, this should
be a practical reference pointing at those skills plus adding SaaS-specific patterns.

### 17. Complete `pos-restaurant-ui-standard`
Complete restaurant POS UI patterns. Currently 39 lines.
Needed for the restaurant POS vertical SaaS opportunity.

### 18. Complete `inventory-management`
Full inventory management patterns. Currently 40 lines.
Needed for pharmacy, logistics, and warehouse verticals.

---

## Phase 5 — 2028–2030 Frontier

### 19. `multimodal-ai`
Vision, audio, and document AI in products. Claude Vision, Whisper, document extraction.

### 20. `edge-computing`
Cloudflare Workers, Vercel Edge, D1 database, edge caching patterns.

### 21. `react-native-advanced`
New Architecture (JSI/Fabric), Expo EAS, native modules, performance profiling.

### 22. `accessibility-wcag`
WCAG 2.2 AA compliance implementation. Semantic HTML, ARIA, keyboard, screen readers.

### 23. `ar-vr-interfaces`
ARKit, ARCore, Apple Vision Pro, spatial UI patterns (2028+).

---

## Summary Timeline

| Period | Skills to Build | Theme |
|--------|----------------|-------|
| 2026 Q2–Q3 | 1–6 (cloud, payments, DB, CI/CD, Node) | Infrastructure |
| 2026 Q4 | 7–11 (Android AI, billing, observability, PWA, E2E) | Platform depth |
| 2027 Q1–Q2 | 12–15 (PLG, events, GraphQL, metrics) | Competitive moats |
| Ongoing | 16–18 (3 stubs) | Library maintenance |
| 2028–2030 | 19–23 (frontier) | Future-proofing |

**Total remaining: 23 skills** — growing from 174 to ~197 skills.

---

*Next: [07-wealth-accumulation-engine.md](07-wealth-accumulation-engine.md)*
