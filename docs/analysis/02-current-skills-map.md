# Current Skills Map — Complete Inventory

**248 skills across 26 domains | 2026-05-01 (Post Spec-Closure)**

> **Note:** The per-domain detail below was written when the library was at 176 skills.
> The cluster-by-cluster narrative remains accurate for the older domains, but the
> following domains have been added or materially expanded since. Counts reflect the
> 2026-05-01 PM inventory after closing the 20-spec backlog (commit `b5a6251`).

## Delta since 2026-05-01 AM (+3 skills, 17 reconciled or enhanced)

| Skill | Type | Domain |
|---|---|---|
| `postgresql-patterns` | NEW | Database |
| `vector-databases` | NEW | AI Data Layer |
| `rag-implementation` | NEW | AI Data Layer |
| `cloud-architecture` | Reconciled | Cloud |
| `kubernetes-platform` | Reconciled (135 → 447 lines) | Kubernetes |
| `infrastructure-as-code` | Reconciled | Cloud / IaC |
| `cicd-pipelines` | Reconciled | CI/CD |
| `observability-platform` | Reconciled | Observability |
| `stripe-payments` | Reconciled | Payments |
| `subscription-billing` | Reconciled | Payments |
| `android-ai-ml` | Reconciled | Android |
| `e2e-testing` | Reconciled | Testing |
| `pwa-offline-first` | Reconciled | PWA |
| `cicd-devsecops` | Enhanced (Vault PKI, ISO 27001, PCI-DSS, Falco/Gatekeeper/Trivy) | CI/CD |
| `database-reliability` | Enhanced (SLO/SLI, error budgets, postmortems, escalation, game days) | Observability |
| `microservices-architecture-models` | Enhanced (HAProxy/Kong/Traefik ops + decision matrix) | Microservices |
| `web-app-security-audit` | Enhanced (network-layer audit) | Security |
| `cicd-pipeline-design` | Enhanced (FinOps Foundation framework) | CI/CD |
| `cicd-jenkins-debian` | Enhanced (Linux hardening + perf tuning) | CI/CD |
| `microservices-communication` | Enhanced (n8n/Temporal/Airflow + retry-policy table) | Microservices |

~40 new `references/` files added across these skills. All 20 validate clean and stay under the 500-line ceiling (max 493 lines on `cicd-jenkins-debian`).

## Delta since 2026-04-16 (+72 skills total)

| Domain | Was | Now | New Skills |
|---|---:|---:|---|
| AI / LLM | 28 | 32 | `ai-agentic-ui`, `ai-output-design`, `deepseek-integration`, `openai-agents-sdk` |
| AI Data Layer (RAG + Vector + Postgres) | 1 | 4 | `postgresql-patterns`, `vector-databases`, `rag-implementation` (joining `ai-rag-patterns`) |
| Apple macOS / Xcode | 0 | 10 | `macos-appkit-interop`, `macos-app-sandbox-security`, `macos-git-libgit2`, `xcode-cloud-testflight`, `xcode-instruments-performance`, `xcode-project-engineering`, `swift-concurrency-macos`, `swiftui-pro-patterns`, `ios-bluetooth-printing` (+1 misc) |
| Design fundamentals | 0 | 11 | `every-layout`, `color-theory`, `design-by-nature`, `grid-systems`, `motion-design`, `interaction-design-patterns`, `practical-ui-design`, `cognitive-ux-framework`, `enterprise-ux-process`, `frontend-performance`, `habit-forming-products` |
| Growth / experimentation | 0 | 5 | `product-discovery`, `product-led-growth`, `experiment-engineering`, `growth-telemetry-pipeline`, `saas-growth-metrics` |
| Platform tier | 3 | 8 | `pwa-offline-first`, `e2e-testing`, `kubernetes-platform`, `observability-platform`, `infrastructure-as-code`, `network-security`, `orchestration-best-practices` |
| Email infrastructure | 0 | 1 | `tabler-email-templates` (80 production HTML templates) |
| Document generation | 1 | 3 | `professional-word-output`, `excel-spreadsheets` |
| SaaS business / pricing | 5 | 8 | `software-business-models`, `software-pricing-strategy`, `saas-accounting-system` |
| Reporting / forecasting | 2 | 3 | `demand-forecasting` (stub-marked) |
| Compliance (regional) | 0 | 3 | `uganda-dppa-compliance`, `dpia-generator`, `east-african-english` |
| Content / blogging | 0 | 3 | `blog-writer`, `blog-idea-generator`, `content-writing` |
| Misc | — | — | `code-safety-scanner`, `ai-slop-prevention`, `image-compression`, `photo-management`, `feature-planning`, `competitive-analysis-pm`, `technology-grant-writing` |

See [`2026-05-01-post-spec-closure.md`](2026-05-01-post-spec-closure.md) for the latest heat map and residual list, and [`2026-05-01-thorough-review.md`](2026-05-01-thorough-review.md) for the morning review.

| Domain | Was | Now | New Skills |
|---|---:|---:|---|
| AI / LLM | 28 | 32 | `ai-agentic-ui`, `ai-output-design`, `deepseek-integration`, `openai-agents-sdk` |
| Apple macOS / Xcode | 0 | 10 | `macos-appkit-interop`, `macos-app-sandbox-security`, `macos-git-libgit2`, `xcode-cloud-testflight`, `xcode-instruments-performance`, `xcode-project-engineering`, `swift-concurrency-macos`, `swiftui-pro-patterns`, `ios-bluetooth-printing` (+1 misc) |
| Design fundamentals | 0 | 11 | `every-layout`, `color-theory`, `design-by-nature`, `grid-systems`, `motion-design`, `interaction-design-patterns`, `practical-ui-design`, `cognitive-ux-framework`, `enterprise-ux-process`, `frontend-performance`, `habit-forming-products` |
| Growth / experimentation | 0 | 5 | `product-discovery`, `product-led-growth`, `experiment-engineering`, `growth-telemetry-pipeline`, `saas-growth-metrics` |
| Platform tier | 3 | 8 | `pwa-offline-first`, `e2e-testing`, `kubernetes-platform`, `observability-platform`, `infrastructure-as-code`, `network-security`, `orchestration-best-practices` |
| Email infrastructure | 0 | 1 | `tabler-email-templates` (80 production HTML templates) |
| Document generation | 1 | 3 | `professional-word-output`, `excel-spreadsheets` |
| SaaS business / pricing | 5 | 8 | `software-business-models`, `software-pricing-strategy`, `saas-accounting-system` |
| Reporting / forecasting | 2 | 3 | `demand-forecasting` (stub-marked) |
| Compliance (regional) | 0 | 3 | `uganda-dppa-compliance`, `dpia-generator`, `east-african-english` |
| Content / blogging | 0 | 3 | `blog-writer`, `blog-idea-generator`, `content-writing` |
| Misc | — | — | `code-safety-scanner`, `ai-slop-prevention`, `image-compression`, `photo-management`, `feature-planning`, `competitive-analysis-pm`, `technology-grant-writing` |

See [`2026-05-01-thorough-review.md`](2026-05-01-thorough-review.md) for the per-domain heat map and regression list.

---

## Original Per-Domain Inventory (April 2026 baseline — preserved below)


---

## iOS Development — 23 Skills (World-Class)

| Skill | Lines | Coverage |
|-------|-------|----------|
| ios-development | ~500 | Core Swift/SwiftUI, MVVM, async/await, lifecycle |
| ios-architecture-advanced | 456 | Scoped DI, MVVM/Redux/Elements, model-driven navigation |
| ios-at-scale | 426 | RIBLETS, Buck/Bazel, trunk-based dev, CI at scale |
| swiftui-design | 498 | NavigationStack, Material 3, adaptive layouts |
| swiftui-pro-patterns | 466 | Layout internals, identity, animation, custom layouts |
| ios-networking-advanced | ~500 | Actor-based client, 401 refresh, cert pinning, multipart |
| ios-data-persistence | 491 | SwiftData, Keychain, offline-first, repository pattern |
| ios-push-notifications | 387 | APNs, rich push, service extensions, silent push |
| ios-biometric-login | 495 | Face ID/Touch ID, LocalAuthentication, Keychain |
| ios-bluetooth-printing | 450 | CoreBluetooth, ESC/POS thermal printing |
| ios-pdf-export | 442 | UIGraphicsPDFRenderer, table layouts, multipage |
| ios-debugging-mastery | 406 | LLDB, Python scripting, watchpoints, DTrace |
| ios-monetization | 430 | StoreKit 2, subscriptions, paywall ViewModel, JWS |
| ios-ai-ml | 497 | CoreML, Vision, NaturalLanguage, CreateML |
| ios-project-setup | 499 | SPM, xcconfig, build schemes, environment config |
| ios-tdd | 509 | Red-Green-Refactor, Swift Testing, test pyramid |
| ios-swift-design-patterns | 465 | Observable MVVM, POP, delegation, keypath adapter |
| ios-uikit-advanced | 508 | Diffable DS, compositional layout, custom transitions |
| ios-production-patterns | 461 | VC lifecycle, Core Data migration, UIKit gotchas |
| ios-stability-solutions | 495 | Crash prevention, optional safety, SOLID, TDD safety |
| ios-swift-recipes | 497 | Numeric, date, Codable, hashing, string validation |
| ios-rbac | 481 | Permission gating, backend resolution, encrypted storage |
| app-store-review | 450 | App Store compliance, privacy labels, review readiness |

**Assessment:** Exceptional. One of the most complete iOS skill sets achievable.
Remaining gaps: Objective-C interop, VoIP/CallKit, on-device LLM fine-tuning.

---

## AI/LLM Ecosystem — 28 Skills (Comprehensive)

| Skill | Coverage |
|-------|----------|
| ai-llm-integration | OpenAI/Claude/Gemini/DeepSeek APIs, streaming, tool use, caching |
| ai-prompt-engineering | System prompts, CoT, few-shot, versioning, defensive patterns |
| ai-rag-patterns | Chunking, hybrid search, re-ranking, contextual retrieval |
| ai-agents-tools | ReAct loop, tool categories, multi-agent, human approval gates |
| ai-architecture-patterns | Module gate, budget guard, token ledger, provider abstraction |
| ai-app-architecture | AI-powered app stack, component design, module gating |
| ai-analytics-strategy | Analytics maturity, KDD, CRISP-DM, responsible AI, ROI |
| ai-analytics-dashboards | KPI cards, AI Insights panel, role-based dashboards, export |
| ai-analytics-saas | NL2SQL, embeddings, semantic search, anomaly detection |
| ai-predictive-analytics | Risk scoring, demand forecasting, domain prompt templates |
| ai-nlp-analytics | Sentiment, classification, entity extraction, multi-language |
| ai-opportunity-canvas | Discover and rank AI use cases, AI Opportunity Register |
| ai-feature-spec | Single AI feature blueprint: model, prompt, schema, fallback, UX |
| ai-integration-section | AI Integration section for SRS/PRD/HLD documents |
| ai-ux-patterns | Loading states, streaming, confidence, HITL, usage display |
| ai-cost-modeling | Token economics, cost/user, cost/tenant, margin modeling |
| ai-metering-billing | Token ledger, metering middleware, per-tenant billing |
| ai-saas-billing | Module gating (off by default), per-tenant metering, quotas |
| ai-error-handling | 5-layer validation stack, quality scoring, recovery strategies |
| ai-error-prevention | Verify-first, TDD, specification matching, fallback code |
| ai-evaluation | Golden test sets, AI-as-judge, production monitoring, drift |
| ai-security | Prompt injection, PII scrubbing, output validation, DPPA |
| ai-assisted-development | Multi-agent orchestration, 5 strategies, HITL |
| ai-slop-prevention | Detect/eliminate AI-generated UI anti-patterns |
| ai-web-apps | Vercel AI SDK, streaming, RAG, LangChain.js |
| llm-security | OWASP LLM Top 10, trust boundaries, injection defence |
| openai-agents-sdk | OpenAI Agents SDK: Agent, Runner, Tools, Handoff, Guardrails |
| deepseek-integration | DeepSeek V3/R1, Ollama local, cost comparison, Python/JS/PHP |

**Assessment:** Enterprise-grade. Covers integration → analytics → products →
cost control → safety → evaluation.

---

## Web Frontend — 14 Skills (Strong)

| Skill | Coverage |
|-------|----------|
| react-development | Hooks, state management, performance, testing, TypeScript, forms |
| react-patterns | HOC, Compound Components, Control Props, Render Props, State Reducer |
| nextjs-app-router | RSC, App Router, data fetching, auth, deployment |
| tailwind-css | Utility-first, responsive, dark mode, @apply, components |
| typescript-mastery | Types, generics, conditional/mapped types, branding, React, tsconfig |
| typescript-design-patterns | All 23 GoF patterns in TypeScript with code examples |
| javascript-modern | ES6+, async/await, modules, Proxy/Reflect, AbortController |
| javascript-advanced | Closures, prototype chain, OOP, functional patterns, event loop |
| javascript-patterns | Module, Observer, Factory, Strategy, Command, Repository |
| javascript-php-integration | JS-in-files architecture, data-* bridge, CSRF, AJAX |
| practical-ui-design | HSB colour, typography scales, 8pt grid, dark mode |
| responsive-design | Mobile-first, container queries, pointer/hover, safe areas |
| frontend-performance | Core Web Vitals, LCP/INP/CLS, image/JS/font optimisation |
| webapp-gui-design | **STUB — 27 lines, provides no actual guidance** |

**Assessment:** Modern web stack fully covered. Critical issue: webapp-gui-design is a stub.

---

## Node.js Backend — 1 Skill (Strong)

| Skill | Coverage |
|-------|----------|
| nodejs-development | Reactor pattern, ESM/CJS, async/await, EventEmitter, streams, HTTP |

**References (10 deep-dive files):**
- `async-patterns.md` — callbacks, Promises, TaskQueue, producer-consumer
- `streams.md` — backpressure, Transform, merge, fork, mux/demux
- `design-patterns.md` — Factory, Builder, Proxy, Middleware, Decorator, DI
- `scaling.md` — cluster, worker_threads, AMQP, Redis Streams
- `fastify.md` — server setup, plugins (fp()), hooks, JWT, TypeBox, Swagger, testing
- `prisma.md` — schema, migrations, CRUD, relations, transactions, TS types, seeding
- `bullmq.md` — queues, workers, retries, cron, FlowProducer, Bull Board, Redis
- `mongodb-mongoose.md` — schema design, validation, relationships
- `realtime.md` — WebSockets, SSE, Socket.IO, multi-tenant isolation
- `testing.md` — Mocha/Chai, Sinon, Supertest, c8 coverage

**Sources:** *Node.js Design Patterns* (Casciaro & Mammino), *Accelerating Server-Side Development
with Fastify* (Spigolon), *Node.js Recipes* (Gackenheimer), *Fullstack Node.js* (Murray),
*Next.js 13 + Prisma* (Lim), BullMQ docs/guides.

---

## MySQL / Database — 7 Skills (Expert)

| Skill | Coverage |
|-------|----------|
| mysql-best-practices | Schema design, indexing, InnoDB, security, tuning, HA, benchmarking |
| mysql-data-modeling | Party model, product hierarchy, order/invoice, double-entry accounting |
| mysql-query-performance | EXPLAIN ANALYZE, index design, optimizer hints, Performance Schema |
| mysql-advanced-sql | Window functions, CTEs, JSON_TABLE, dynamic pivoting, stored procedures |
| mysql-administration | GTID replication, InnoDB Cluster, XtraBackup, ProxySQL, PITR |
| database-internals | B-tree, WAL, MVCC, buffer pool, LSM trees, CAP tradeoffs |
| database-reliability | SLOs, expand-contract migrations, backup verification, chaos engineering |

**Assessment:** Expert-level. A genuine competitive differentiator.

---

## PostgreSQL — 7 Skills (Expert)

| Skill | Coverage |
|-------|----------|
| postgresql-fundamentals | Tools, roles, data types, object model, server config, extensions |
| postgresql-advanced-sql | CTEs, recursive, window functions, JSONB, arrays, full-text search |
| postgresql-server-programming | PL/pgSQL, functions, procedures, triggers, event triggers, extensions |
| postgresql-performance | EXPLAIN ANALYZE, B-tree/GIN/GiST/BRIN/partial indexes, MVCC, VACUUM |
| postgresql-administration | pg_dump, WAL/PITR, streaming/logical replication, monitoring, cloud PaaS |
| postgresql-ai-platform | pgvector, embeddings, RAG pipeline, AI fault lines, sovereign data platform |
| postgresql-patterns | **NEW (2026-05-01)** — Postgres-as-second-DB patterns: JSONB, FTS, pgvector, RLS, PgBouncer, MySQL→PG translations |

**Assessment:** Complete PostgreSQL stack from fundamentals through pgvector RAG and
explicit MySQL-coexistence patterns. Enables Supabase projects, vector search, and
hybrid MySQL+Postgres SaaS architectures.

---

## AI Data Layer — 4 Skills (Cohort Complete, Post Spec-Closure)

| Skill | Coverage |
|-------|----------|
| ai-rag-patterns | Architectural RAG patterns: chunking, hybrid search, re-ranking, contextual retrieval |
| postgresql-patterns | **NEW** — Postgres + pgvector + JSONB + FTS as a second DB alongside MySQL |
| vector-databases | **NEW** — Engine selection (pgvector / Qdrant / Pinecone / Weaviate), embedding model choice, chunking strategy, hybrid search, reranking |
| rag-implementation | **NEW** — Naive → Advanced → Modular RAG progression, query transforms (HyDE, multi-query), corrective RAG, RAGAS evaluation, multi-tenant isolation, cost levers |

**Assessment:** The AI Data Layer cohort is now content-complete — engine choice,
embedding pipeline, retrieval architecture, evaluation framework, and multi-tenant
isolation are all addressed with explicit decision tables.

---

## Android Development — 7 Skills (Solid)

| Skill | Coverage |
|-------|----------|
| android-development | Kotlin, Compose, MVVM, Clean Arch, Hilt, edge-to-edge |
| jetpack-compose-ui | Material 3, adaptive layouts, unidirectional data flow |
| android-data-persistence | Room, Flow, offline-first, API sync |
| android-pdf-export | PdfDocument API, Canvas-based, multipage |
| android-biometric-login | AndroidX Biometric, CryptoObject |
| android-tdd | Red-Green-Refactor, JUnit, Espresso, Mockk |
| mobile-rbac | Permission gating, EncryptedSharedPreferences, JWT |

**Cross-platform (shared with iOS):** mobile-reports, mobile-report-tables,
mobile-saas-planning, mobile-custom-icons.

**Assessment:** Solid. Gap: Android AI/ML (TensorFlow Lite, ML Kit, Gemini Nano).
*Note: android-reports, android-saas-planning, android-report-tables, android-custom-icons deleted —
superseded by mobile-* equivalents.*

---

## PHP Backend — 4 Skills

| Skill | Coverage |
|-------|----------|
| php-modern-standards | PHP 8+, strict typing, enums, Fibers, generators, OPcache |
| php-security | Sessions, XSS, CSRF, file uploads, php.ini hardening |
| javascript-php-integration | JS-in-files architecture, data-* bridge, CSRF, $pageScript |
| php-vs-nextjs | Decision framework: when PHP, when Next.js, hybrid architecture |

---

## DevOps / Infrastructure — 4 CI/CD + Cloud + IaC + K8s family (World-Class, Post Spec-Closure)

### CI/CD + DevSecOps (4 skills)

| Skill | Coverage |
|-------|----------|
| cicd-pipeline-design | 14-stage CI/CD methodology, DORA metrics, blue-green/canary, branching strategy, **FinOps Foundation framework (NEW 2026-05-01)** |
| cicd-pipelines | **Reconciled (2026-05-01)** — GitHub Actions + GitLab CI templates, environments, secrets, fast-feedback loops |
| cicd-jenkins-debian | Jenkins on Debian/Ubuntu: install, Declarative Jenkinsfile, Docker agents, RBAC, backup, **Linux hardening + perf tuning (NEW 2026-05-01)** |
| cicd-devsecops | Vault basics, OWASP Dependency Check, SonarQube, Trivy, UFW, container hardening, **Vault PKI lifecycle, ISO 27001 Annex A, PCI-DSS scope reduction, Falco/Gatekeeper/Trivy runtime defence (NEW 2026-05-01)** |

### Cloud + IaC (3 skills)

| Skill | Coverage |
|-------|----------|
| cloud-architecture | **Reconciled (2026-05-01)** — AWS/GCP core services, IAM, networking, cost, well-architected pillars |
| infrastructure-as-code | **Reconciled (2026-05-01)** — Terraform (state, modules, workspaces), Ansible, GitOps (ArgoCD/Flux), drift detection |
| network-security | Firewall, WAF, segmentation, zero-trust, VPN |

### Kubernetes (4 skills)

| Skill | Coverage |
|-------|----------|
| kubernetes-fundamentals | Core objects, kubectl, probes, ingress, when K8s is right vs alternatives |
| kubernetes-production | Helm, autoscaling, StatefulSets, external-secrets, observability, RBAC + PSS, NetworkPolicies, Velero, cost control |
| kubernetes-saas-delivery | Multi-tenancy models, namespace isolation, ArgoCD GitOps, progressive delivery, tenant onboarding/offboarding |
| kubernetes-platform | **Reconciled (2026-05-01, 135 → 447 lines)** — cluster topology, node pools, multi-region, zero-downtime upgrades, Helm chart governance |

**Assessment:** Cloud / Containers / IaC / CI/CD is now world-class with explicit
compliance evidence (ISO 27001, PCI-DSS), runtime defence (Falco/Gatekeeper/Trivy),
FinOps cost governance, and Linux hardening built in.

---

## Microservices — 5 Skills

| Skill | Coverage |
|-------|----------|
| microservices-fundamentals | Monolith vs micro, decomposition, 12-Factor App, bounded contexts |
| microservices-architecture-models | NGINX MRA: Proxy/Router Mesh/Fabric, API gateway, discovery, **HAProxy/Kong/Traefik ops + decision matrix (NEW 2026-05-01)** |
| microservices-resilience | Circuit breaker, health endpoints, retry, bulkhead, timeout |
| microservices-communication | Sync vs async, inter-service auth, data isolation, API contracts, **n8n/Temporal/Airflow async orchestration + retry-policy table (NEW 2026-05-01)** |
| microservices-ai-integration | AI as a microservice, async AI jobs, Kubeflow/Seldon, metering |

---

## Security — 11 Skills

dual-auth-rbac, vibe-security-skill, php-security, web-app-security-audit (with
**network-layer audit section (NEW 2026-05-01)**), code-safety-scanner, skill-safety-audit,
graphql-security, llm-security, ai-security, network-security, cicd-devsecops.

## Payments — 3 Skills (Post Spec-Closure)

| Skill | Coverage |
|---|---|
| stripe-payments | **Reconciled (2026-05-01)** — Products, prices, subscriptions, webhooks (idempotency), customer portal, tax, multi-currency |
| subscription-billing | **Reconciled (2026-05-01)** — Dunning, metered billing, upgrade/downgrade flows, revenue recognition |
| saas-accounting-system | Double-entry accounting engine patterns |

## Observability / SRE — 4 Skills (Post Spec-Closure)

| Skill | Coverage |
|---|---|
| observability-monitoring | Logs, metrics, traces, alerts, SLOs, diagnosis-first telemetry |
| reliability-engineering | Retries, timeouts, degradation, incident readiness, recovery-aware design |
| database-reliability | SLOs, expand-contract migrations, backup verification, chaos engineering, **SLO/SLI definitions, error budgets, blameless postmortem template, escalation matrix, game-day playbook (NEW 2026-05-01)** |
| observability-platform | **Reconciled (2026-05-01)** — SigNoz/Prometheus/Grafana/OpenTelemetry/Jaeger/Sentry instrumentation patterns |

## Mobile AI/ML — 2 Skills (Parity Reached)

| Skill | Coverage |
|---|---|
| ios-ai-ml | CoreML, Vision, NaturalLanguage, CreateML |
| android-ai-ml | **Reconciled (2026-05-01)** — ML Kit, TensorFlow Lite, MediaPipe, Gemini Nano, Compose streaming |

## Testing — Reconciliations

| Skill | Coverage |
|---|---|
| e2e-testing | **Reconciled (2026-05-01)** — Playwright + Cypress, Page Object Model, network mocking, visual regression, CI integration, quarantine + flake budgets |

## PWA / Offline-First — 1 Skill (Reconciled)

| Skill | Coverage |
|---|---|
| pwa-offline-first | **Reconciled (2026-05-01)** — Workbox, Service Workers, IndexedDB (Dexie.js), background sync, PWA manifest, East-Africa connectivity patterns |

---

## UI/UX Design — 19 Skills

practical-ui-design, form-ux-design, cognitive-ux-framework, design-audit, laws-of-ux,
lean-ux-validation, ux-principles-101, ux-psychology, ux-writing, healthcare-ui-design,
pos-sales-ui-design, habit-forming-products, ai-slop-prevention, ux-for-ai, motion-design,
interaction-design-patterns, web-usability-krug, data-visualization, responsive-design.

---

## SDLC Documentation — 12 Skills

sdlc-planning, sdlc-design, sdlc-testing, sdlc-user-deploy, sdlc-maintenance,
sdlc-post-deployment, doc-architect, manual-guide, update-claude-documentation,
markdown-lint-cleanup, professional-word-output, spec-architect.

---

## Business / Monetisation — 5 Skills

software-business-models, software-pricing-strategy, technology-grant-writing,
it-proposal-writing, saas-business-metrics.

---

## KMP / Cross-platform — 3 Skills

kmp-development, kmp-tdd, kmp-compose-multiplatform.

---

## API & Real-Time — 5 Skills

api-design-first, api-error-handling, api-pagination, api-testing-verification,
realtime-systems.

---

## Product Management — 5 Skills

product-discovery, product-strategy-vision, competitive-analysis-pm,
feature-planning, project-requirements.

---

*Next: [03-quality-compliance.md](03-quality-compliance.md)*
