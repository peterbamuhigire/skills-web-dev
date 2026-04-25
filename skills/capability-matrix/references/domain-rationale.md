# Domain Rationale

One paragraph per matrix row, explaining *why* the picks are what they are. Lets Claude justify a skill choice when asked, and helps maintainers update the row intelligently.

## Web/SaaS

The default web row, deliberately generic. Foundation pulls `system-architecture-design` (decomposition, ADRs) and `database-design-engineering` (schema/tenancy/indexing) because nearly every web project gets these wrong first. Implementation lists `php-modern-standards` and `nodejs-development` as the two most-used backends in this repository's projects. Validation includes both `vibe-security-skill` (threat modeling) and `web-app-security-audit` (configuration/auth review) because web is high-attack-surface. Performance is added because frontend perceived latency dominates user perception.

## Multi-tenant SaaS

Specialised version of Web/SaaS. Foundation upgrades to `multi-tenant-saas-architecture` (tenant isolation, three-panel separation) and adds `saas-erp-system-design` because configurable workflows are common. Implementation includes `dual-auth-rbac` and `modular-saas-architecture` because RBAC and pluggable modules are near-universal in this domain. Companions include billing skills because multi-tenant SaaS almost always means subscription revenue.

## iOS

Foundation is the iOS development standard plus advanced architecture (DI containers, navigation patterns). Implementation covers UI, persistence, and networking — the three areas that define an iOS feature's shape. Validation includes app-store-review because TestFlight + App Store gates are unique to iOS. Companions list common cross-cutting features (PDF export, biometric login, RBAC, monetization) that most production iOS apps need.

## Android

Mirror of iOS but Android-flavoured. `jetpack-compose-ui` replaces SwiftUI; `android-room` is called out separately because Room is the data-layer choice for almost all modern Android. Validation includes Play Store review; Companions cover the same cross-cutting needs. `mobile-custom-icons` appears here (and not iOS) because Android's icon handling has more friction.

## KMP / Compose Multiplatform

Lean row by design — the value of KMP is sharing logic across platforms, so the iOS and Android rows do most of the work. Foundation is `kmp-development`, Implementation is the multiplatform UI skill, Validation is `kmp-tdd`. Companions point at the platform rows because anything platform-specific defers to them.

## API / HTTP

Foundation is `api-design-first` (spec-first, OpenAPI) plus `system-architecture-design` for service decomposition. Implementation lists the same two backends as Web/SaaS. Validation centres on `api-testing-verification` (the canonical Correctness contributor for APIs) plus security skills, with `graphql-security` for GraphQL surfaces. Companions cover patterns most APIs eventually need (pagination, error handling, real-time).

## Database (relational)

Foundation pulls `database-design-engineering` and `mysql-data-modeling` because Silverston-style universal patterns inform almost every schema. Implementation covers both engines (MySQL and PostgreSQL fundamentals). Validation lists the performance-tuning skills per engine plus `database-reliability`. Companions cover deeper administration and internals for when the work needs DBA-level depth.

## Frontend (React / Next)

Foundation is `nextjs-app-router` (the modern Next pattern) plus architecture for service-boundary decisions in full-stack Next apps. Implementation covers React fundamentals, patterns, and Tailwind. Validation centres on performance (the biggest frontend risk) and design audit. Companions are large because UI work draws from many cross-cutting skills (grid systems, type design, interaction patterns, motion, responsive, microcopy, AI slop prevention).

## AI Feature

Foundation has three rows because AI features need three distinct architectural inputs: app architecture, feature spec, and integration patterns (token ledger, module gate, budget guard). Implementation pairs the LLM integration skill with prompt engineering. Validation includes `ai-evaluation` (output quality), `llm-security` (OWASP for LLMs), `ai-error-handling` (validation/fallbacks), and `ai-security` (PII, prompt injection). Companions include UX patterns specific to AI surfaces and cost modelling.

## LLM Integration

Narrower than AI Feature — this row is for direct API integration work (Claude, DeepSeek, OpenAI agents). Foundation is the integration skill; Implementation lists provider-specific skills. Validation overlaps with AI Feature on security and evaluation. Companions cover RAG, agent tools, and microservices-style AI integration.

## Python Service

Foundation is the modern Python standards (uv, ruff, mypy, Pydantic v2). Implementation is the SaaS sidecar pattern (FastAPI + Redis worker) which is how Python plugs into the PHP+mobile stack. Validation is `advanced-testing-strategy`. Companions list the Python specialisations (analytics, document gen, ML, pipelines) — exactly one of these usually applies per service.

## TypeScript Stack

Foundation is `typescript-mastery` (type system depth) plus `typescript-effective` (production idioms, strict tsconfig). Implementation is the full-stack skill (Fastify + tRPC + Prisma) and design patterns for when GoF patterns apply. Validation centres on API contract testing. Companions point at adjacent rows (Node, React) for when the work spans more than pure TypeScript.

## Kubernetes

Foundation is fundamentals plus architecture, because K8s is wrong for many problems and the architectural choice should be deliberate. Implementation is `kubernetes-production` (Helm, autoscaling, secrets). Validation centres on observability, reliability, and network security — the three production K8s pain points. Companions add SaaS delivery patterns and CI/CD integration.

## GIS

Foundation is the Leaflet client and PostGIS backend. Implementation is the integration skill for Google Maps / Mapbox / MapLibre when Leaflet is insufficient. Validation includes performance (maps are perf-sensitive). Companions add ArcGIS Enterprise admin and emphasise database design because spatial schema choices matter.

## ERP / Business System

Foundation pairs the ERP design skill with multi-tenant architecture. Implementation lists the modular SaaS framework, inventory management, and accounting system because most ERP modules use these. Validation adds testing strategy because ERP workflows are integration-heavy. Companions cover form UX, manual generation, and SDLC documentation — all heavy needs in ERP work.

## CI/CD pipeline

Foundation is the pipeline design skill (artifact promotion, branch strategy, release gates). Implementation lists GitHub Actions and Jenkins patterns. Validation includes DevSecOps (security gates) and deployment release engineering (rollout, rollback). Companions add cloud architecture and K8s fundamentals because pipelines usually target one of those.

## Observability / SRE

Foundation is the observability skill (logs/metrics/traces, SLOs, alerts). Implementation pairs reliability engineering with distributed systems patterns because real SRE work is cross-service. Validation lists testing and release engineering — both of which are how SRE evidence shows up in practice. Companions include security-hardening and database reliability for full-stack SRE.
