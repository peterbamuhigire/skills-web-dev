# Skill Routing Index

Source: `docs/skills-trimminhg.md`

Date: 2026-05-17

This index records the intended consolidation routing without moving or deleting
skill directories. It exists so old skill slugs can be mapped to retained parent
skills while the catalog is reduced below the active-skill cap.

## Active Skill Policy

- Active skill roots are `skills/`, `doctrine/skills/`, and `00-meta-initialization/`.
- Active skill means a file named `SKILL.md` under an active root.
- Target active catalog size is 150-170 skills, with a hard cap of 200.
- Reference material must not be named `SKILL.md`.
- Inactive aliases retain their original content as `ALIAS.md` in the same
  directory and route through `docs/skill-aliases.yml`.
- Redirect skills count as active skills and should be temporary if used.
- Finance doctrine is canonical in the `doctrine/` submodule.

Current guardrail baseline after the 2026-05-17 cleanup:

| Metric | Value |
|---|---:|
| Active `SKILL.md` files | 173 |
| Guardrail hard cap | 200 |
| Duplicate frontmatter names | 0 |
| Inactive alias files retained | 47 |

## Finance Doctrine Canonicality

Finance, accounting, tax, inventory, payroll, banking, mobile money, POS,
statutory compliance, and accounting-record work routes first to
`doctrine/skills/*` for doctrine-owned rules. Duplicate finance entrypoints under
`skills/finance-accounting/finance/*` are compatibility aliases only until their durable material is
absorbed into doctrine references or a small number of orchestration wrappers.

Root-level finance implementation skills may remain active when they add behavior
outside doctrine:

| Active skill | Role |
|---|---|
| `skills/finance-accounting/accounting-engine` | Posting engine, ledger integrity, reversals, idempotency, implementation contracts. |
| `skills/finance-accounting/accounting-finance-controller` | Controller-grade routing, quality gates, finance audit orchestration. |
| `skills/saas/saas-accounting-system` | SaaS-specific accounting product architecture, if still distinct from `accounting-engine`. |
| `doctrine/skills/*` | Canonical accounting doctrine, controls, reporting, close, migration, reconciliation, and finance UX. |

## Finance Alias Map

| Old or narrow slug | Target active skill | Status |
|---|---|---|
| `skills/finance-accounting/finance/audit-ready-reporting-pack` | `doctrine/skills/audit-ready-reporting-pack` | Inactive alias |
| `skills/finance-accounting/finance/bank-and-mobile-money-reconciliation` | `doctrine/skills/bank-and-mobile-money-reconciliation` | Inactive alias |
| `skills/finance-accounting/finance/finance-module-audit` | `doctrine/skills/finance-module-audit` | Inactive alias |
| `skills/finance-accounting/finance/finance-ui-pattern-library` | `doctrine/skills/finance-ui-pattern-library` | Inactive alias |
| `skills/finance-accounting/finance/finance-ux-for-non-accountants` | `doctrine/skills/finance-ux-for-non-accountants` | Inactive alias |
| `skills/finance-accounting/finance/ias-agriculture` | `doctrine/skills/ias-agriculture` | Inactive alias |
| `skills/finance-accounting/finance/ias-government-grants` | `doctrine/skills/ias-government-grants` | Inactive alias |
| `skills/finance-accounting/finance/ias-impairment` | `doctrine/skills/ias-impairment` | Inactive alias |
| `skills/finance-accounting/finance/ias-income-tax-deferred-tax` | `doctrine/skills/ias-income-tax-deferred-tax` | Inactive alias |
| `skills/finance-accounting/finance/ias-provisions-contingencies` | `doctrine/skills/ias-provisions-contingencies` | Inactive alias |
| `skills/finance-accounting/finance/ifrs-financial-instruments` | `doctrine/skills/ifrs-financial-instruments` | Inactive alias |
| `skills/finance-accounting/finance/ifrs-for-smes-equivalents` | `doctrine/skills/ifrs-for-smes-equivalents` | Inactive alias |
| `skills/finance-accounting/finance/ifrs-leases` | `doctrine/skills/ifrs-leases` | Inactive alias |
| `skills/finance-accounting/finance/ifrs-revenue-recognition` | `doctrine/skills/ifrs-revenue-recognition` | Inactive alias |
| `skills/finance-accounting/finance/internal-controls-library` | `doctrine/skills/internal-controls-library` | Inactive alias |
| `skills/finance-accounting/finance/management-accounting-dimensions` | `doctrine/skills/management-accounting-dimensions` | Inactive alias |
| `skills/finance-accounting/finance/month-end-and-year-end-close-playbook` | `doctrine/skills/month-end-and-year-end-close-playbook` | Inactive alias |
| `skills/finance-accounting/finance/opening-balances-and-migration-playbook` | `doctrine/skills/opening-balances-and-migration-playbook` | Inactive alias |
| `skills/finance-accounting/fixed-assets-and-depreciation` | `doctrine/skills/fixed-assets-and-depreciation` | Inactive alias |
| `fixed-assets-and-depreciation`, `multicurrency-and-fx` | `doctrine/skills/ifrs-standards-suite` | Planned absorbed reference |
| `inventory-costing`, `inventory-management`, `payroll-postings-uganda`, `pos-restaurant-ui-standard`, `pos-sales-ui-design` | `doctrine/skills/inventory-payroll-pos` | Planned absorbed references |
| POS cash drawer, card settlements, clearing accounts | `doctrine/skills/reconciliation-and-cash-control` | Planned absorbed references |

## 2026-05-17 Inactive Alias Routes

These old entrypoints no longer expose active `SKILL.md` files. Their original
content remains in-place as `ALIAS.md`, and agents should route to the retained
target instead.

| Inactive alias | Retained target |
|---|---|
| `skills/finance-accounting/chart-of-accounts-templates` | `doctrine/skills/ledger-posting-engine-core` |
| `skills/sdlc-meta/capability-matrix` | `skills/product-business/product-discovery` |
| `skills/sdlc-meta/continuous-improvement-system` | `skills/sdlc-meta/world-class-engineering` |
| `skills/sdlc-meta/custom-sub-agents` | `skills/ai/ai-agent-multi-agent-coordination` |
| `skills/backend-databases/database-internals` | `skills/backend-databases/database-design-engineering` |
| `skills/finance-accounting/demand-forecasting` | `skills/languages/python-ml-predictive` |
| `skills/security/dual-auth-rbac` | `skills/security/vibe-security-skill` |
| `skills/sdlc-meta/engineering-management-system` | `skills/sdlc-meta/world-class-engineering` |
| `skills/sdlc-meta/engineering-strategy` | `skills/sdlc-meta/world-class-engineering` |
| `skills/product-business/experiment-engineering` | `skills/ai/ai-feature-rollout-and-experimentation` |
| `skills/product-business/growth-telemetry-pipeline` | `skills/languages/python-data-analytics` |
| `skills/finance-accounting/inventory-costing` | `doctrine/skills/inventory-costing-and-stock-accounting` |
| `skills/finance-accounting/inventory-management` | `doctrine/skills/inventory-costing-and-stock-accounting` |
| `skills/architecture/microservices-ai-integration` | `skills/ai/ai-app-architecture` |
| `skills/mobile-cross/mobile-reports` | `skills/product-business/professional-word-output` |
| `skills/product-business/premium-product-positioning` | `skills/product-business/premium-software-product-execution` |
| `skills/finance-accounting/payroll-postings-uganda` | `doctrine/skills/payroll-and-statutory-postings-east-africa` |
| `skills/frontend-ux/pos-restaurant-ui-standard` | `doctrine/skills/finance-ui-pattern-library` |
| `skills/frontend-ux/pos-sales-ui-design` | `doctrine/skills/finance-ui-pattern-library` |
| `skills/backend-databases/postgresql-ai-platform` | `skills/ai/ai-rag-patterns` |
| `skills/ai/rag-implementation` | `skills/ai/ai-rag-patterns` |
| `skills/saas/saas-control-plane-engineering` | `skills/saas/saas-architecture-strategy` |
| `skills/saas/saas-deployment-models` | `skills/saas/saas-architecture-strategy` |
| `skills/saas/saas-subscription-mastery` | `skills/saas/subscription-billing` |
| `skills/saas/saas-tenant-onboarding-automation` | `skills/product-business/product-led-growth` |
| `skills/security/uganda-dppa-compliance` | `skills/security/dpia-generator` |
| `skills/ai/ux-for-ai` | `skills/ai/ai-agent-ux` |
| `skills/frontend-ux/ux-principles-101` | `skills/frontend-ux/practical-ui-design` |
| `skills/backend-databases/vector-databases` | `skills/ai/ai-rag-patterns` |

## Broad Routing Groups

| Domain | Target active skill | Absorbed or routed slugs |
|---|---|---|
| AI architecture | `ai-app-architecture` | `ai-architecture-patterns`, `ai-on-saas-architecture` |
| LLM integration | `ai-llm-integration` | `deepseek-integration`, provider adapters |
| RAG | `ai-rag-patterns` | `rag-implementation`, `ai-rag-multi-tenant`, `vector-databases` |
| AI evaluation | `ai-evaluation` | `ai-eval-harness`, eval suites, regression gates |
| AI security | `ai-security` | `llm-security`, `ai-prompt-injection-and-tenant-safety` |
| AI analytics | `ai-analytics` | `ai-analytics-dashboards`, `ai-analytics-saas`, `ai-analytics-strategy`, `ai-nlp-analytics`, `ai-predictive-analytics` |
| AI cost and billing | `ai-cost-and-metering` | `ai-cost-modeling`, `ai-cost-per-tenant-attribution`, `ai-metering-billing`, `ai-usage-metering-and-billing` |
| Agent runtime | `ai-agent-runtime-architecture` | `ai-agent-async-and-long-running-tasks`, `ai-agent-memory` |
| Agent tools and HITL | `ai-agent-tooling-and-hitl` | `ai-agent-tool-catalogue-and-action-gating`, `ai-agents-tools`, `ai-agent-action-approval-and-hitl` |
| Agent governance | `ai-agent-governance-and-limits` | `ai-agent-cost-and-step-budgets`, `ai-agent-reversibility-and-blast-radius` |
| Agent evidence | `ai-agent-observability-evaluation` | `ai-agent-eval`, `ai-agent-task-success-tracking`, `ai-agent-observability-and-replay`, `ai-agent-evidence-automation` |
| Agent commercial ops | `ai-agent-commercial-operations` | `ai-agent-pricing-engine`, `ai-agent-attempted-vs-completed-billing`, `ai-agent-revenue-recognition`, `ai-agent-abandonment-and-refund-policy` |
| Agent compliance | `ai-agent-compliance-controls` | `ai-agent-soc2-controls`, `ai-agent-iso27001-controls`, `ai-agent-hipaa-security-controls`, `ai-agent-control-testing-and-attestation`, `ai-agent-audit-log-integrity` |
| Android | `android-development` | `android-ai-ml`, `android-biometric-login`, `android-pdf-export` |
| Android persistence | `android-data-persistence` | `android-room` |
| Android UI | `android-ui-ux-design` | `jetpack-compose-ui` |
| iOS core | `ios-development` | `ios-project-setup`, `ios-swift-recipes` |
| iOS architecture | `ios-architecture` | `ios-architecture-advanced`, `ios-at-scale`, `ios-production-patterns` |
| iOS persistence | `ios-data-persistence` | `ios-swiftdata` |
| iOS UI | `ios-ui-ux-design` | `swiftui-design`, `swiftui-pro-patterns`, `ios-uikit-advanced` |
| iOS capabilities | `ios-platform-capabilities` | `ios-biometric-login`, `ios-bluetooth-printing`, `ios-push-notifications`, `ios-pdf-export`, `ios-networking-advanced` |
| Mobile operations | `mobile-platform-operations` | `mobile-custom-icons`, `mobile-rbac`, `mobile-saas-planning`, `google-play-store-review` |
| Frontend CSS | `tailwind-css` | `responsive-design`, `every-layout`, `grid-systems` |
| UX foundations | `ux-foundations` | `ux-principles-101`, `ux-psychology`, `laws-of-ux`, `web-usability-krug`, `cognitive-ux-framework` |
| UX content | `ux-content-strategy` | `ux-writing` |
| Design audit | `design-audit` | `lean-ux-validation`, heuristic review workflows |
| Database PostgreSQL | `postgresql-engineering` | `postgresql-fundamentals`, `postgresql-patterns`, `postgresql-advanced-sql`, `postgresql-server-programming` |
| PostgreSQL operations | `postgresql-operations` | `postgresql-administration`, `postgresql-performance` |
| MySQL engineering | `mysql-engineering` | `mysql-best-practices`, `mysql-data-modeling`, `mysql-advanced-sql` |
| MySQL operations | `mysql-operations` | `mysql-administration`, `mysql-query-performance` |
| Microservices | `microservices-architecture` | `microservices-fundamentals`, `microservices-architecture-models`, `microservices-communication`, `microservices-resilience` |
| APIs | `api-design-first` | `api-error-handling`, `api-pagination`, `api-testing-verification` |
| JavaScript | `javascript-modern` | `javascript-advanced`, `javascript-patterns` |
| TypeScript | `typescript-effective` | `typescript-mastery`, `typescript-design-patterns` |
| C# and .NET | `csharp-dotnet-development` | `csharp`, `dotnet`, `aspnet-core`, `ef-core`, `dotnet-maui`, `dotnet-ai` |
| Security | `vibe-security-skill` | `dual-auth-rbac`, selected stack security references |
| GraphQL | `graphql-patterns` | `graphql-security` |
| CI/CD | `cicd-pipelines` | `cicd-pipeline-design`, `cicd-devsecops`, `cicd-jenkins-debian` |
| Kubernetes | `kubernetes-platform` | `kubernetes-fundamentals`, `kubernetes-production`, `kubernetes-saas-delivery` |
| Product discovery | `product-discovery` | `feature-planning`, `competitive-analysis-pm` |
| Content | `content-writing` | `blog-writer`, `blog-idea-generator`, `east-african-english` |
| SDLC docs | `sdlc-documentation` | `sdlc-design`, `sdlc-maintenance`, `sdlc-planning`, `sdlc-post-deployment`, `sdlc-testing`, `sdlc-user-deploy` |
| GIS | `gis-platform-engineering` | `gis-mapping`, `gis-maps-integration`, `gis-postgis-backend` |

## Quality Guardrails (always-on, cross-cutting)

These two skills under `skills/sdlc-meta/` apply to every artefact type the catalogue
produces (website, web/mobile app, business plan, SRS/spec, proposal, blog/article,
social post, marketing copy, document, image/video, codebase). They are not routed by
domain — they sit above domain skills.

| Skill | Role | When it fires |
|---|---|---|
| `skills/sdlc-meta/anti-ai-slop` | Real-time production guardrail | Continuously while generating ANY output, and at the pre-ship gate. Load first; overrides stylistic preferences. |
| `skills/sdlc-meta/ai-slop-audit` | Detection / scoring auditor | After EACH major iteration of work (logs a verdict; blocks progression on grade F), as the final gate, and auto-runs when the user asks to analyse/review/evaluate/audit/critique/de-slop ANY project, app, website, plan, spec, document, image, or codebase, or asks "does this look AI-generated?". |

## Registry Maintenance

- Update this file when a retained parent skill changes.
- Add the same mapping to `docs/skill-aliases.yml` when a route needs to be machine-readable.
- Do not remove old directories as part of registry maintenance.
- Run `python -X utf8 scripts/skill_catalog_guardrails.py --report-only` after registry updates.
