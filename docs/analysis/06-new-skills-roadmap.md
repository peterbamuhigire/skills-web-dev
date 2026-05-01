# New Skills Roadmap — Revised Priority

**Re-prioritised after 2026-05-01 PM spec-closure pass | All Critical/High roadmap items shipped, including the 20-spec backlog from `webdevskills-engine-completion-2026`**

---

## What Has Been Built (No Longer Needed)

The following Phase 1, 2, and 3 skills from prior roadmaps now exist:

| Original Priority | Skill | Status |
|-------------------|-------|--------|
| 1 | ai-llm-integration | ✅ Built (+ 31 more AI skills) |
| 2 | react-nextjs | ✅ Built as react-development + react-patterns + nextjs-app-router |
| 3 | typescript-modern | ✅ 4 skills (mastery, design-patterns, effective, full-stack) |
| 7 | realtime-systems | ✅ Built |
| 8 | api-design-first | ✅ Built |
| 9 | cloud-architecture | ✅ Built |
| 10 | stripe-payments | ✅ Built (+ subscription-billing, saas-accounting-system) |
| 11 | cicd-pipelines | ✅ 4 skills (pipelines, pipeline-design, jenkins-debian, devsecops) |
| 12 | observability-monitoring | ✅ 4 skills (monitoring, reliability, db-reliability, platform) |
| 13 | e2e-testing | ✅ Built (Playwright + Cypress) |
| 14 | pwa-offline-first | ✅ Built (Workbox + IndexedDB; East-Africa connectivity patterns) |
| 15 | infrastructure-as-code | ✅ Built (+ kubernetes 4-skill family) |
| 16 | network-security | ✅ Built |
| 17 | tabler-email-templates | ✅ Built (80 production HTML templates) |
| 18 | design fundamentals | ✅ 11-skill family (every-layout, color-theory, design-by-nature, etc.) |
| 19 | growth/experimentation | ✅ 5 skills (product-discovery, product-led-growth, experiment-engineering, growth-telemetry, saas-growth-metrics) |
| 20 | macOS / Xcode | ✅ 10 skills |
| Bonus | microservices-* | ✅ 5 skills |
| Bonus | postgresql-patterns | ✅ Built (2026-05-01 PM) — Postgres-as-second-DB patterns |
| Bonus | vector-databases | ✅ Built (2026-05-01 PM) — engine selection across pgvector/Qdrant/Pinecone/Weaviate |
| Bonus | rag-implementation | ✅ Built (2026-05-01 PM) — Naive→Advanced→Modular, RAGAS, multi-tenant isolation |
| Bonus | nodejs-typescript-backend | ✅ Built as nodejs-development |

---

## Phase 1 (2026-05-01 PM reset) — Finish Floor + Frontier Skills

These are the post spec-closure priorities. The roadmap below this section is preserved
from prior phases for traceability but most items have shipped.

### 1. Finish the `## Evidence Produced` rollout (URGENT)
Add the section to the 7 reconciled production-readiness skills still missing it
(`rag-implementation`, `kubernetes-platform`, `infrastructure-as-code`,
`observability-platform`, `stripe-payments`, `e2e-testing`, `pwa-offline-first`) plus
the 11 carry-over design / growth / AI / email skills from the 2026-05-01 AM review.
Then promote `MISSING_SECTION_SEVERITY: warning → error` in `contract_gate.py`.

### 2. Promote `enterprise-ux-process` (96 lines) and `demand-forecasting` (35 lines)
Either expand to peer length or merge into adjacent skills. (`kubernetes-platform`
was already reconciled to 447 lines on 2026-05-01 PM, so it drops off this list.)

### 3. Define `## Inputs Contract` / `## Outputs Contract` table schema
In `skill-composition-standards`, then activate the gate's stub checker.

### 4. Book-grounding pass for newly-added families
Python (6), TypeScript (4), GIS (4), Kubernetes (4), Design (11), Growth (5),
Apple-macOS (10) families still ship without full book grounding in their
`references/`. Run the per-skill plan in `docs/superpowers/specs/`.

### 5. New skill: `react-native-advanced`
The cross-platform mobile gap. KMP is covered; RN is not.

### 6. New skill: `compliance-control-mapping`
ISO 27001 / SOC 2 / PCI-DSS / HIPAA control catalogue mapping. Local DPPA + DPIA
already covered. (Note: `cicd-devsecops` now carries ISO 27001 Annex A and
PCI-DSS scope reduction sections, but a dedicated control-catalogue mapping
skill is still warranted.)

### 7. New skill: `rust-systems` (optional, evaluate)
For performance-critical backend services. Track Rust adoption signal through 2026.

### 8. New skill: `edge-runtimes-wasm` (optional)
Cloudflare Workers / Vercel Edge / Fastly Compute@Edge / WASM. Track adoption signal.

### 9. New baseline skill: `growth-experimentation` (optional)
With 5 specialist growth skills now shipped, a baseline-tier skill in the spirit of
`world-class-engineering` would lock in cross-references and decision rules.

### 10. Schedule a quarterly contract-gate sweep
A recurring agent that runs `contract_gate.py` and opens a PR if warnings or errors
return to non-zero. Prevents regression of the kind seen on 2026-05-01 AM.

---

## Phase 1 (legacy — most items shipped) — Critical Infrastructure

### ~~1. `cloud-architecture`~~ ✅ SHIPPED
**What:** AWS/GCP core services for SaaS deployment
**Covers:** Compute, storage, RDS, CDN, IAM, auto-scaling, Docker, cost optimisation
**Source:** AWS Well-Architected Framework (free) + *Docker Deep Dive* (Poulton)
**Creates:** Ability to deploy and scale production SaaS without DevOps help

### ~~2. `stripe-payments`~~ ✅ SHIPPED
**What:** Stripe integration for SaaS billing — the revenue layer
**Covers:** Products, prices, subscriptions, webhooks, dunning, customer portal, tax
**Source:** Stripe documentation (stripe.com/docs/billing)
**Creates:** Revenue collection infrastructure for every SaaS product

### ~~3. `postgresql-patterns`~~ ✅ DONE
Built as 6 dedicated skills: postgresql-fundamentals through postgresql-ai-platform (pgvector).

### ~~4. `vector-databases`~~ ✅ DONE
Covered by postgresql-ai-platform: pgvector, embeddings, RAG pipeline, HNSW indexes.

### ~~3. `kubernetes-platform`~~ ✅ SHIPPED (reconciled 2026-05-01 PM, 135 → 447 lines)

### ~~4. `infrastructure-as-code`~~ ✅ SHIPPED (reconciled 2026-05-01 PM)
### ~~5. `cicd-pipelines`~~ ✅ SHIPPED (reconciled 2026-05-01 PM)

### ~~4. `nodejs-typescript-backend`~~ ✅ DONE
Built as `nodejs-development` — covers Fastify, Prisma, BullMQ, plus 10 reference files
(async patterns, streams, design patterns, scaling, realtime, testing, MongoDB).

---

## Phase 2 — Platform Depth (SHIPPED 2026-05-01 PM)

All five Phase 2 skills shipped via the 20-spec closure in commit `b5a6251`:

- ~~7. `android-ai-ml`~~ ✅ SHIPPED (reconciled to spec — ML Kit, TFLite, MediaPipe, Gemini Nano)
- ~~8. `subscription-billing`~~ ✅ SHIPPED (reconciled to spec — dunning, metered billing, upgrade/downgrade, revenue recognition)
- ~~9. `observability-platform`~~ ✅ SHIPPED (reconciled to spec — SigNoz/Prometheus/Grafana/OpenTelemetry/Jaeger/Sentry)
- ~~10. `pwa-offline-first`~~ ✅ SHIPPED (reconciled to spec — Workbox, Service Workers, IndexedDB, East-Africa connectivity patterns)
- ~~11. `e2e-testing`~~ ✅ SHIPPED (reconciled to spec — Playwright + Cypress, POM, network mocking, visual regression, quarantine + flake budgets)

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

## Existing Skills Enhanced (SHIPPED 2026-05-01 PM)

All seven enhancements shipped in commit `b5a6251`:

| Skill | Enhancement | Status |
|-------|-------------|--------|
| `cicd-devsecops` | Vault PKI lifecycle, ISO 27001 Annex A, PCI-DSS scope reduction, Falco/Gatekeeper/Trivy runtime defence | ✅ |
| `database-reliability` | Platform SRE — SLO/SLI definitions, error budgets, blameless postmortem template, escalation matrix, game-day playbook | ✅ |
| `microservices-architecture-models` | Reverse proxy ops (Nginx/HAProxy) + API gateway ops (Kong/Traefik) + decision matrix | ✅ |
| `web-app-security-audit` | Network security layer — firewall, WAF, segmentation, zero-trust, VPN | ✅ |
| `cicd-pipeline-design` | FinOps Foundation framework — resource quotas, utilisation targets, cost allocation, budget guardrails | ✅ |
| `cicd-jenkins-debian` | Linux hardening — sysctl, cgroups, auditd, network stack tuning | ✅ |
| `microservices-communication` | Workflow automation engines — n8n / Temporal / Airflow + retry-policy table | ✅ |

---

## Summary Timeline

| Period | New Skills | Enhancements | Theme |
|--------|-----------|--------------|-------|
| 2026 Q2–Q3 | cloud-architecture, kubernetes-platform, infrastructure-as-code, stripe-payments, cicd-pipelines | cicd-devsecops, database-reliability | Infrastructure |
| 2026 Q4 | android-ai-ml, subscription-billing, observability-platform, pwa-offline-first, e2e-testing | microservices-architecture-models, web-app-security-audit | Platform depth |
| 2027 Q1–Q2 | product-led-growth, event-driven-architecture, graphql-patterns, saas-growth-metrics | cicd-pipeline-design, cicd-jenkins-debian, microservices-communication | Competitive moats |
| Ongoing | — | webapp-gui-design, pos-restaurant-ui-standard, inventory-management stubs | Library maintenance |
| 2028–2030 | multimodal-ai, edge-computing, react-native-advanced, accessibility-wcag, ar-vr-interfaces | — | Future-proofing |

**Current library:** 248 skills (was 245 on 2026-05-01 AM; +3 from spec closure).
**Remaining new-skill candidates (post 2026-05-01 PM):** 4 — `react-native-advanced`,
`compliance-control-mapping`, `rust-systems` (optional), `edge-runtimes-wasm` (optional);
plus optional `growth-experimentation` baseline.
**Remaining mechanical work:** finish `## Evidence Produced` rollout (~16 skills),
promote `MISSING_SECTION_SEVERITY` to `error`, define I/O contract table schema,
schedule quarterly contract-gate sweep, promote `enterprise-ux-process` and
`demand-forecasting`, book-grounding pass for Python/K8s/TS/GIS families.

---

*Next: [07-wealth-accumulation-engine.md](07-wealth-accumulation-engine.md)*
