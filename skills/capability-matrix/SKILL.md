---
name: capability-matrix
description: Use when starting a new project, scoping a feature, or deciding which skill stack to load — provides the canonical Foundation → Implementation → Validation → Companions skill set per technology domain. The lookup table that turns "I'm building X" into "load these skills, in this order".
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Capability Matrix
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Starting a new project and choosing the initial skill stack.
- Scoping a feature in an existing codebase and deciding which skills should load alongside the platform skill.
- Reviewing a PR or design and asking *"what should have been loaded for this work?"*.
- Onboarding to a new domain (mobile, AI, K8s, GIS) and wanting the canonical recommended set rather than discovering skills one by one.

## Do Not Use When

- The work is purely conceptual (writing prose, planning, brainstorming) and no implementation is imminent. Skills are loaded for execution; the matrix is a tool for execution work.
- The domain is genuinely novel (no row applies). Flag the gap and ask the user to clarify; do not guess by stretching an unrelated row.
- A specialist skill's own `Use When` already covers the situation completely. The matrix is for stack composition, not single-skill triggering.

## Required Inputs

- The technology domain or domains in scope (web, mobile, API, AI, etc.).
- A clear sense of whether the work is greenfield or brownfield (changes which Foundation skills apply).
- Awareness that Validation entries here are pulled from `validation-contract`'s seven evidence categories.

## Workflow

- Identify the matrix row(s) that match the work.
- Load every skill in the row's Foundation column first, then Implementation, then Validation.
- Add Companions as the work demands per `references/companion-rules.md`.
- If two rows could apply (e.g., AI feature inside a multi-tenant SaaS), load both rows and dedupe.

## Quality Standards

- Treat the matrix as the *minimum* starting set, not the cap. Add more skills if the work warrants.
- Never load a skill from the matrix without also reading its `Use When` to confirm the situation actually matches.
- Flag missing rows. The matrix is not exhaustive; an unknown domain is a signal to ask, not to improvise.

## Anti-Patterns

- Loading every skill in a row without reading their `Use When` triggers — the matrix recommends, the skill triggers gate.
- Treating Validation column entries as the *only* validation needed — `validation-contract` defines the full evidence requirement; the matrix lists the canonical contributors per domain.
- Inventing a new row inline rather than updating this skill. The matrix is the single source of truth.

## Outputs

- A loaded skill stack tailored to the domain, ordered Foundation → Implementation → Validation → Companions.
- A clear statement when the matrix has no row for the work, prompting the user to clarify the domain.

## References

- [references/domain-rationale.md](references/domain-rationale.md): per-row rationale for the skill picks.
- [references/companion-rules.md](references/companion-rules.md): when each Companion category kicks in (UX, content, security baseline, release).
<!-- dual-compat-end -->

## How to use the matrix

1. **Identify the domain.** Ask: "what is this project / feature primarily?" Match it to one row. If two rows apply (a common case — e.g., "AI feature in a SaaS"), load both rows and dedupe the skill list.
2. **Load Foundation → Implementation → Validation in order.** Foundation skills set up the architecture, contracts, and data shape decisions before framework-level work begins. Implementation skills handle the platform-specific build. Validation skills carry the ship-readiness gates.
3. **Add Companions as the work demands.** Companions are cross-cutting skills that often apply but not always — see `references/companion-rules.md` for the trigger rules.

## The matrix

| Domain | Foundation | Implementation | Validation | Companions |
|--------|------------|----------------|------------|------------|
| **Web/SaaS** | `system-architecture-design`, `database-design-engineering` | `php-modern-standards`, `nodejs-development` | `vibe-security-skill`, `web-app-security-audit`, `frontend-performance` | `git-collaboration-workflow`, `ux-writing` |
| **Multi-tenant SaaS** | `multi-tenant-saas-architecture`, `database-design-engineering`, `saas-erp-system-design` | `php-modern-standards`, `dual-auth-rbac`, `modular-saas-architecture` | `vibe-security-skill`, `observability-monitoring` | `saas-business-metrics`, `subscription-billing`, `stripe-payments`, `feature-planning` |
| **iOS** | `ios-development`, `ios-architecture-advanced` | `swiftui-design`, `ios-data-persistence`, `ios-networking-advanced` | `ios-tdd`, `ios-app-security`, `app-store-review` | `ios-pdf-export`, `ios-biometric-login`, `ios-rbac`, `ios-monetization` |
| **Android** | `android-development` | `jetpack-compose-ui`, `android-data-persistence`, `android-room` | `android-tdd`, `google-play-store-review` | `android-pdf-export`, `android-biometric-login`, `mobile-rbac`, `mobile-custom-icons` |
| **KMP / Compose Multiplatform** | `kmp-development` | `kmp-compose-multiplatform` | `kmp-tdd` | `ios-development`, `android-development` |
| **API / HTTP** | `api-design-first`, `system-architecture-design` | `nodejs-development`, `php-modern-standards` | `api-testing-verification`, `vibe-security-skill`, `graphql-security` | `api-pagination`, `api-error-handling`, `realtime-systems` |
| **Database (relational)** | `database-design-engineering`, `mysql-data-modeling` | `mysql-best-practices`, `postgresql-fundamentals` | `database-reliability`, `mysql-query-performance`, `postgresql-performance` | `mysql-administration`, `postgresql-administration`, `database-internals` |
| **Frontend (React / Next)** | `nextjs-app-router`, `system-architecture-design` | `react-development`, `react-patterns`, `tailwind-css` | `frontend-performance`, `design-audit` | `grid-systems`, `practical-ui-design`, `interaction-design-patterns`, `motion-design`, `responsive-design`, `ux-writing`, `ai-slop-prevention` |
| **AI Feature** | `ai-app-architecture`, `ai-feature-spec`, `ai-architecture-patterns` | `ai-llm-integration`, `ai-prompt-engineering` | `ai-evaluation`, `llm-security`, `ai-error-handling`, `ai-security` | `ai-ux-patterns`, `ux-for-ai`, `ai-cost-modeling`, `ai-slop-prevention` |
| **LLM Integration** | `ai-llm-integration`, `ai-app-architecture` | `claude-api`, `deepseek-integration`, `openai-agents-sdk` | `llm-security`, `ai-evaluation`, `ai-error-handling` | `ai-prompt-engineering`, `ai-rag-patterns`, `ai-agents-tools`, `microservices-ai-integration` |
| **Python Service** | `python-modern-standards` | `python-saas-integration` | `advanced-testing-strategy` | `python-data-analytics`, `python-document-generation`, `python-ml-predictive`, `python-data-pipelines` |
| **TypeScript Stack** | `typescript-mastery`, `typescript-effective` | `typescript-full-stack`, `typescript-design-patterns` | `api-testing-verification`, `advanced-testing-strategy` | `nodejs-development`, `react-development` |
| **Kubernetes** | `kubernetes-fundamentals`, `system-architecture-design` | `kubernetes-production` | `observability-monitoring`, `reliability-engineering`, `network-security` | `kubernetes-saas-delivery`, `cicd-devsecops`, `cloud-architecture` |
| **GIS** | `gis-mapping`, `gis-postgis-backend` | `gis-maps-integration` | `vibe-security-skill`, `frontend-performance` | `gis-enterprise-domain`, `database-design-engineering` |
| **ERP / Business System** | `saas-erp-system-design`, `multi-tenant-saas-architecture` | `modular-saas-architecture`, `inventory-management`, `saas-accounting-system` | `vibe-security-skill`, `observability-monitoring`, `advanced-testing-strategy` | `form-ux-design`, `manual-guide`, `sdlc-design`, `feature-planning` |
| **CI/CD pipeline** | `cicd-pipeline-design` | `cicd-pipelines`, `cicd-jenkins-debian` | `cicd-devsecops`, `deployment-release-engineering` | `cloud-architecture`, `kubernetes-fundamentals` |
| **Observability / SRE** | `observability-monitoring` | `reliability-engineering`, `distributed-systems-patterns` | `advanced-testing-strategy`, `deployment-release-engineering` | `linux-security-hardening`, `network-security`, `database-reliability` |

## Domain disambiguation

When two rows could apply, load both and dedupe. Common combinations:

- **AI feature inside a SaaS** → AI Feature row + Multi-tenant SaaS row.
- **Mobile app talking to a backend** → iOS or Android row + API/HTTP row.
- **GIS dashboard inside a web app** → GIS row + Frontend (React/Next) row.
- **AI-powered analytics in a SaaS** → AI Feature row + Multi-tenant SaaS row + (if Python-based) Python Service row.
- **K8s-deployed multi-tenant SaaS** → Multi-tenant SaaS row + Kubernetes row + Observability/SRE row.
- **Brownfield refactor of any kind** → relevant domain row + always add `git-collaboration-workflow` and `system-architecture-design`.

## Vertical addenda

Some verticals add a small set of skills on top of whatever rows apply:

- **Healthcare** → add `healthcare-ui-design`.
- **POS / Restaurant** → add `pos-sales-ui-design`, `pos-restaurant-ui-standard`.
- **Payments** → add `stripe-payments`, `subscription-billing`.
- **Auth surface** → add `dual-auth-rbac`, `mobile-rbac`, `ios-rbac` as platform demands.
- **East-African / Uganda compliance** → add `uganda-dppa-compliance`, `dpia-generator`, `language-standards`, `east-african-english`.
- **Reporting / dashboards** → add `data-visualization`, `mobile-reports`, `mobile-report-tables`, `report-print-pdf` as platform demands.
- **Photo / image handling** → add `photo-management`, `image-compression`.
- **Real-time features** → add `realtime-systems`.
- **PDF / document generation** → add `report-print-pdf`, `python-document-generation`, `ios-pdf-export`, `android-pdf-export`, `professional-word-output`, `excel-spreadsheets` as needed.
- **Spec / SDLC docs** → add `spec-architect`, `sdlc-design`, `sdlc-planning`, `sdlc-testing`, `sdlc-user-deploy`, `sdlc-maintenance`, `sdlc-post-deployment`.

## Evidence-contract note

The Validation column in every row pulls skills that are themselves declared `validation-contract` contributors. This matrix tells you *which* validation skills apply per domain; `validation-contract` defines *what evidence* those skills must produce at ship time. Always load `validation-contract` alongside the matrix when shipping is in scope.

## Companion Skills

- `world-class-engineering` — the production-readiness bar that the matrix's recommendations operate within.
- `validation-contract` — defines the seven evidence categories that the Validation column draws from.
- `skill-composition-standards` — house style and Inputs/Outputs contracts; load when authoring new skills that should be added to the matrix.