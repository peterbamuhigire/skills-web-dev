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
| Bonus | postgresql-patterns | ✅ Built as 6 postgresql-* skills incl. pgvector |
| Bonus | vector-databases | ✅ Covered by postgresql-ai-platform (pgvector RAG) |
| Bonus | nodejs-typescript-backend | ✅ Built as nodejs-development (Fastify + Prisma + BullMQ) |

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

### ~~3. `postgresql-patterns`~~ ✅ DONE
Built as 6 dedicated skills: postgresql-fundamentals through postgresql-ai-platform (pgvector).

### ~~4. `vector-databases`~~ ✅ DONE
Covered by postgresql-ai-platform: pgvector, embeddings, RAG pipeline, HNSW indexes.

### 3. `kubernetes-platform`
**What:** Production-grade Kubernetes cluster management
**Covers:** Cluster setup, Helm, namespaces, RBAC, resource quotas, pod security, workload scaling, HPA/VPA, self-managed VPS-first then cloud-managed
**Source:** *Kubernetes in Action* (Luksa), *Production Kubernetes* (Rosso et al.)
**Creates:** Ability to own and operate production K8s environments end-to-end
**Stack alignment:** Debian/Ubuntu nodes, Helm charts, ArgoCD for GitOps

### 4. `infrastructure-as-code`
**What:** IaC for consistent, repeatable infrastructure
**Covers:** Terraform (providers, state, modules, workspaces), Ansible (playbooks, roles, idempotency), GitOps (ArgoCD, Flux), drift detection
**Source:** *Terraform: Up & Running* (Brikman, 3rd ed.), *Infrastructure as Code* (Morris, O'Reilly)
**Creates:** Version-controlled, reviewable, auditable infrastructure — no more snowflake servers
**Stack alignment:** Terraform for cloud resources, Ansible for Debian/Ubuntu server config

### 5. `cicd-pipelines`
**What:** GitHub Actions CI/CD for web + mobile
**Covers:** Automated testing, build/deploy pipelines, secrets, environments, Fastlane iOS
**Source:** *Continuous Delivery* (Humble & Farley), GitHub Actions documentation
**Creates:** Fast, repeatable, safe delivery on every commit

### ~~4. `nodejs-typescript-backend`~~ ✅ DONE
Built as `nodejs-development` — covers Fastify, Prisma, BullMQ, plus 10 reference files
(async patterns, streams, design patterns, scaling, realtime, testing, MongoDB).

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

### 9. `observability-platform`
**What:** Production visibility for SaaS and infrastructure
**Covers:** Structured JSON logging, Prometheus metrics, Grafana dashboards, OpenTelemetry tracing, SigNoz (self-hosted all-in-one), Sentry error tracking, SLO/SLI/error budget tracking
**Source:** *Observability Engineering* (Majors, Fong-Jones, Miranda); SigNoz docs; Google SRE Book
**Creates:** Full-stack visibility — from application errors to infrastructure health to SLO compliance
**Stack alignment:** SigNoz primary (open-source, self-hosted); PHP + Node.js + Android + iOS instrumentation examples

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

## Existing Skills to Enhance (No New Directory)

These enhancements happen in parallel with new skill creation — add sections to existing SKILL.md files only:

| Skill | Enhancement |
|-------|-------------|
| `cicd-devsecops` | Vault lifecycle, ISO 27001, PCI-DSS controls, Falco/OPA container runtime security |
| `database-reliability` | Platform SRE — SLO/SLI, error budgets, blameless postmortems |
| `microservices-architecture-models` | Reverse proxy ops (Nginx/HAProxy), API gateway ops (Kong/Traefik) |
| `web-app-security-audit` | Network security layer — firewall, WAF, zero-trust, VPN design |
| `cicd-pipeline-design` | FinOps / cost governance — resource quotas, utilisation targets, budget guardrails |
| `cicd-jenkins-debian` | Linux hardening — sysctl, cgroups, auditd, network stack tuning |
| `microservices-communication` | Workflow automation engines — n8n, Temporal, Airflow patterns |

---

## Summary Timeline

| Period | New Skills | Enhancements | Theme |
|--------|-----------|--------------|-------|
| 2026 Q2–Q3 | cloud-architecture, kubernetes-platform, infrastructure-as-code, stripe-payments, cicd-pipelines | cicd-devsecops, database-reliability | Infrastructure |
| 2026 Q4 | android-ai-ml, subscription-billing, observability-platform, pwa-offline-first, e2e-testing | microservices-architecture-models, web-app-security-audit | Platform depth |
| 2027 Q1–Q2 | product-led-growth, event-driven-architecture, graphql-patterns, saas-growth-metrics | cicd-pipeline-design, cicd-jenkins-debian, microservices-communication | Competitive moats |
| Ongoing | — | webapp-gui-design, pos-restaurant-ui-standard, inventory-management stubs | Library maintenance |
| 2028–2030 | multimodal-ai, edge-computing, react-native-advanced, accessibility-wcag, ar-vr-interfaces | — | Future-proofing |

**Total new skills remaining: 22** — current library: 176 skills.
**Total enhancements remaining: 7** — no new directories, just deeper existing skills.

---

*Next: [07-wealth-accumulation-engine.md](07-wealth-accumulation-engine.md)*
