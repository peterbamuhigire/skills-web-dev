# Skills Catalog Consolidation Report

Date: 2026-05-13

## Executive Summary

The repository currently has too many skill entrypoints for reliable routing. I found 356 `SKILL.md` files recursively under the repository, with 337 under `skills/`, 17 duplicate finance doctrine skills under `doctrine/skills/`, and 2 meta-initialisation skills outside `skills/`.

The catalog can be reduced to a practical target of about 150-170 active skills, safely below the requested maximum of 200, without losing capability. The right move is not to delete knowledge. It is to keep fewer routing entrypoints and move narrower topics into orchestrated `references/`, `sections/`, `templates/`, and `scripts/` inside the retained parent skills.

Immediate issues:

- 3 skills are skipped by the loader due to invalid frontmatter:
  - `skills/fixed-assets-and-depreciation/SKILL.md`
  - `skills/multicurrency-and-fx/SKILL.md`
  - `skills/finance/finance-module-audit/SKILL.md`
- 17 finance skills are duplicated between `doctrine/skills/*` and `skills/finance/*`.
- `00-meta-initialization/new-project/SKILL.md` has 636 lines, above the repository's 500-line `SKILL.md` limit.
- Many skills are narrower than the loader should see. They should become reference modules inside a broader routing skill.

Recommended end state:

- Active skills: 150-170.
- Hard cap: 200.
- Finance doctrine remains canonical in the `doctrine/` submodule.
- Archive/deep material: normal markdown files, not `SKILL.md`, so the loader does not count or route to them directly.
- Add `docs/skill-aliases.yml` or `docs/skill-routing-index.md` to map old skill names to new parent skills.

## Counting Basis

Observed inventory:

| Area | Current count | Notes |
|---|---:|---|
| All recursive `SKILL.md` files | 356 | Includes `skills/`, `doctrine/skills/`, and meta folders. |
| `skills/**/SKILL.md` | 337 | Main active catalog. |
| `doctrine/skills/**/SKILL.md` | 17 | Canonical finance doctrine submodule skills currently duplicated by `skills/finance/*`. |
| `00-meta-initialization/**/SKILL.md` | 2 | Outside the standard `skills/<name>/SKILL.md` convention. |
| Duplicate names | 17 | All finance doctrine duplicates. |
| Loader-invalid skills | 3 | Must be fixed before migration. |
| `SKILL.md` files over 500 lines | 1 | `00-meta-initialization/new-project`. |

## Consolidation Principles

Use these rules to decide whether something remains a skill:

1. A skill should be a routing entrypoint for a real task family.
2. A skill should not exist only because a topic is important.
3. A narrow standard, checklist, framework, or domain note belongs in `references/`.
4. A code generator, validator, or mechanical operation belongs in `scripts/`.
5. A reusable output shape belongs in `templates/`.
6. A retired skill must not keep a `SKILL.md` file, or it still counts as active.
7. Keep compatibility through aliases in docs, not through hundreds of redirect skills.
8. Descriptions must be short, valid YAML, and loader-friendly.

Recommended retained skill shape:

```text
skills/<parent-skill>/
  SKILL.md
  references/
    <old-skill-slug>.md
    routing.md
    decision-tables.md
  templates/
  scripts/
```

## Immediate Validation Fixes

These should be done before any consolidation work.

### `fixed-assets-and-depreciation`

Problem: frontmatter description contains an unquoted colon.

Fix:

```yaml
description: >-
  Use when designing or reviewing fixed asset accounting under IAS 16/IFRS for SMEs:
  asset register, capitalization, directly attributable costs, depreciation, disposals,
  revaluation policy, custody, and asset-register-to-GL reconciliation.
```

### `multicurrency-and-fx`

Problem: frontmatter description contains an unquoted colon.

Fix:

```yaml
description: >-
  Use when implementing IAS 21 multicurrency accounting: functional currency,
  presentation currency, transaction currency, exchange-rate tables, settlement,
  realised and unrealised forex gains or losses, revaluation, and currency-safe ledger design.
```

### `finance-module-audit`

Problem: description exceeds the loader limit of 1024 characters.

Fix: shorten description to the trigger and move the long auto-run policy into `references/finance-audit-trigger.md`.

```yaml
description: >-
  Use when auditing any software, SRS, proposal, POS, ERP, SaaS, mobile app, or workflow
  that touches money, billing, payments, tax, payroll, banking, mobile money, inventory,
  statutory compliance, financial reports, or accounting records.
```

## High-Impact Consolidation Map

### 1. Finance And Accounting

Current issue: 29 finance/accounting skills in `skills/`, plus 17 duplicate `doctrine/skills` entrypoints. This creates double routing, drift risk, and loader noise. The finance doctrine is a submodule and should remain the canonical accounting source of truth.

Target: 10-12 active finance skills.

Canonical decision:

- Keep the finance doctrine submodule as the canonical source for IFRS, controls, reconciliation, close, migration, reporting, and finance UX doctrine.
- Remove or de-activate duplicate `skills/finance/*` entrypoints that repeat the same doctrine skills.
- Keep only thin orchestration skills outside the submodule where they add cross-repository behaviour: finance trigger routing, accounting engine implementation, SaaS integration, and controller-grade audit orchestration.
- Do not keep the same skill name active in both places.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `accounting-finance-controller` | Controller-grade routing, doctrine loading, finance quality gate. |
| `accounting-engine` | Ledger posting, subledger tagging, immutability, reversals, idempotency. |
| `finance/finance-module-audit` or `doctrine/skills/finance-module-audit` | Standards scorecard, finance audit trigger, remediation master plan. Prefer moving this into the doctrine submodule if it is doctrine-owned. |
| `doctrine/skills/ifrs-standards-suite` | `ias-agriculture`, `ias-government-grants`, `ias-impairment`, `ias-income-tax-deferred-tax`, `ias-provisions-contingencies`, `ifrs-financial-instruments`, `ifrs-for-smes-equivalents`, `ifrs-leases`, `ifrs-revenue-recognition`, `fixed-assets-and-depreciation`, `multicurrency-and-fx`. |
| `doctrine/skills/reconciliation-and-cash-control` | `bank-and-mobile-money-reconciliation`, POS cash drawer, card settlements, clearing accounts. |
| `doctrine/skills/reporting-close-and-audit-pack` | `audit-ready-reporting-pack`, `month-end-and-year-end-close-playbook`, statutory packs, retained earnings close. |
| `doctrine/skills/controls-and-governance` | `internal-controls-library`, approval thresholds, audit trails, maker-checker, fraud indicators. |
| `doctrine/skills/management-accounting` | `management-accounting-dimensions`, budgeting, variance, grants, allocations, contribution margin. |
| `doctrine/skills/migration-and-opening-balances` | `opening-balances-and-migration-playbook`, cutover, legacy mapping, suspense, sign-off. |
| `doctrine/skills/inventory-payroll-pos` | `inventory-costing`, `inventory-management`, `payroll-postings-uganda`, `pos-restaurant-ui-standard`, `pos-sales-ui-design`. |
| `doctrine/skills/finance-ux-ui` | `finance-ui-pattern-library`, `finance-ux-for-non-accountants`. |
| `saas-accounting-system` | Keep only if it remains SaaS-specific; otherwise fold into `accounting-engine` plus SaaS references. |

Expected reduction: about 46 finance-related entrypoints, counting doctrine duplicates, to about 12.

### 2. AI And Agentic Systems

Current issue: about 78 AI-related skills. The `ai-agent-*` family alone is too granular for direct routing.

Target: 24-30 active AI skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `ai-app-architecture` | `ai-architecture-patterns`, `ai-on-saas-architecture`, high-level AI system boundaries. |
| `ai-llm-integration` | `deepseek-integration`, provider adapters, request/response contracts. |
| `ai-model-gateway` | Model routing, fallback, quotas, provider observability. |
| `ai-prompt-engineering` | Prompt design, prompt libraries, defensive prompting, output constraints. |
| `ai-rag-patterns` | `rag-implementation`, `ai-rag-multi-tenant`, `vector-databases`, retrieval freshness, chunking, hybrid search. |
| `ai-evaluation` | `ai-eval-harness`, eval suites, regression gates. |
| `ai-observability-and-debugging` | `ai-hallucination-slo-and-grounding`, traces, replay, prompt/version capture. |
| `ai-security` | `llm-security`, `ai-prompt-injection-and-tenant-safety`, tenant isolation, data exfiltration controls. |
| `ai-analytics` | `ai-analytics-dashboards`, `ai-analytics-saas`, `ai-analytics-strategy`, `ai-nlp-analytics`, `ai-predictive-analytics`. |
| `ai-cost-and-metering` | `ai-cost-modeling`, `ai-cost-per-tenant-attribution`, `ai-metering-billing`, `ai-usage-metering-and-billing`. |
| `ai-output-design` | `ai-slop-prevention`, output quality gates, structured output rules. |
| `ai-web-apps` | AI web implementation patterns. |
| `openai-agents-sdk` | Keep provider/framework-specific. |
| `ai-assisted-development` | Keep as coding-workflow skill. |
| `ai-feature-spec` | Keep for AI feature requirements. |
| `ai-feature-rollout-and-experimentation` | Keep for experiments and staged launches. |
| `ai-economic-value-engine` | Keep if it produces ROI/value artifacts. |
| `ai-opportunity-canvas` | Keep if it is used before feature selection. |
| `ai-entitlements-and-feature-gating` | Merge with SaaS entitlements unless AI-specific enforcement remains materially different. |

Agentic systems should collapse into a smaller suite:

| Keep active skill | Absorb these as references |
|---|---|
| `ai-agent-runtime-architecture` | `ai-agent-async-and-long-running-tasks`, `ai-agent-memory`, state machines, resumability. |
| `ai-agent-tooling-and-hitl` | `ai-agent-tool-catalogue-and-action-gating`, `ai-agents-tools`, `ai-agent-action-approval-and-hitl`. |
| `ai-agent-governance-and-limits` | `ai-agent-cost-and-step-budgets`, `ai-agent-reversibility-and-blast-radius`, policy gates. |
| `ai-agent-observability-evaluation` | `ai-agent-eval`, `ai-agent-task-success-tracking`, `ai-agent-observability-and-replay`, `ai-agent-evidence-automation`. |
| `ai-agent-commercial-operations` | `ai-agent-pricing-engine`, `ai-agent-attempted-vs-completed-billing`, `ai-agent-revenue-recognition`, `ai-agent-abandonment-and-refund-policy`. |
| `ai-agent-sla-and-customer-commitments` | `ai-agent-sla-and-commitments`, `ai-agent-sla-credit-automation`, `ai-agent-customer-sla-dashboard`. |
| `ai-agent-compliance-controls` | `ai-agent-soc2-controls`, `ai-agent-iso27001-controls`, `ai-agent-hipaa-security-controls`, `ai-agent-control-testing-and-attestation`, `ai-agent-audit-log-integrity`. |
| `ai-agent-safety-and-red-team` | Safety testing, abuse cases, adversarial tasks. |
| `ai-agent-ux` | `ai-agentic-ui`, `ai-agent-mobile-and-web-ux-patterns`, `ux-for-ai` if AI-specific UX is kept outside general UX. |
| `ai-agent-multi-agent-coordination` | Keep only if it has distinct orchestration protocols; otherwise fold into runtime architecture. |

Expected reduction: about 78 AI skills to about 26.

### 3. Mobile

Current issue: 44 mobile-related skills, with iOS especially over-split.

Target: 14-18 active mobile skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `android-development` | `android-ai-ml`, `android-biometric-login`, `android-pdf-export`, general Android implementation recipes. |
| `android-data-persistence` | `android-room` as a Room-specific reference. |
| `android-ui-ux-design` | `jetpack-compose-ui` as Compose reference. |
| `android-tdd` | Keep if test workflow is substantial; otherwise fold into `android-development`. |
| `ios-development` | `ios-project-setup`, `ios-swift-recipes`, broad iOS workflow. |
| `ios-architecture` | `ios-architecture-advanced`, `ios-at-scale`, `ios-production-patterns`. |
| `ios-data-persistence` | `ios-swiftdata`. |
| `ios-ui-ux-design` | `swiftui-design`, `swiftui-pro-patterns`, `ios-uikit-advanced`. |
| `ios-platform-capabilities` | `ios-biometric-login`, `ios-bluetooth-printing`, `ios-push-notifications`, `ios-pdf-export`, `ios-networking-advanced`. |
| `ios-quality-and-release` | `ios-tdd`, `ios-debugging-mastery`, `ios-stability-solutions`, `app-store-review`. |
| `ios-security-and-rbac` | `ios-app-security`, `ios-rbac`. |
| `ios-ai-ml` | Keep if ML workflows are rich; otherwise reference under `ios-platform-capabilities`. |
| `ios-monetization` | Keep if it has App Store purchase/subscription specificity; otherwise fold into SaaS/subscription skills. |
| `kmp-development` | `kmp-compose-multiplatform`, `kmp-tdd`. |
| `mobile-reports` | `mobile-report-tables`, `report-print-pdf` mobile rules. |
| `mobile-platform-operations` | `mobile-custom-icons`, `mobile-rbac`, `mobile-saas-planning`, `google-play-store-review`. |

Expected reduction: about 44 mobile skills to about 16.

### 4. Frontend, UI, And UX

Current issue: design principles, web app GUI, CSS layout, UX psychology, UX writing, and premium UI are split into many overlapping entrypoints.

Target: 16-20 active skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `webapp-gui-design` | Main SaaS app UI shell, dashboards, tables, forms, dialogs. |
| `premium-ui-ux-design` | Premium execution bar; cross-links to practical UI and product positioning. |
| `practical-ui-design` | Keep as tactical UI decision skill if distinct from premium UI. |
| `frontend-performance` | Keep. |
| `nextjs-app-router` | Keep. |
| `react-development` | `react-patterns`. |
| `tailwind-css` | `responsive-design`, `every-layout`, `grid-systems`, CSS layout rules. |
| `form-ux-design` | Forms, validation, field grouping, completion gates. |
| `ux-content-strategy` | `ux-writing` as tactical microcopy reference. |
| `ux-foundations` | `ux-principles-101`, `ux-psychology`, `laws-of-ux`, `web-usability-krug`, `cognitive-ux-framework`. |
| `interaction-design-patterns` | Keep as interaction-specific. |
| `design-audit` | `lean-ux-validation`, review workflow, heuristic audit. |
| `enterprise-ux-process` | `experience-mapping`, `service-design-blueprinting`. |
| `healthcare-ui-design` | Keep if healthcare-specific compliance/workflow rules are substantial. |
| `pwa-offline-first` | Keep if implementation-specific. |
| `no-json-in-ui` | Fold into `webapp-gui-design` unless it is frequently triggered as a hard guardrail. |
| `motion-design` | Keep if animation/motion has its own production rules. |
| `color-theory` | Reference under `premium-ui-ux-design`. |
| `design-by-nature` | Reference under `premium-ui-ux-design` or remove as active if mostly conceptual. |

Expected reduction: about 33 frontend/UX skills to about 18.

### 5. Databases, Data, And Analytics

Current issue: engine-specific database skills are split by administration, advanced SQL, modeling, performance, and patterns. That is useful as reference depth, not as separate loader entrypoints for every query.

Target: 11-13 active skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `database-design-engineering` | Keep as baseline. |
| `database-reliability` | Keep. |
| `database-internals` | Keep only if low-level database engine work is common; otherwise reference. |
| `postgresql-engineering` | `postgresql-fundamentals`, `postgresql-patterns`, `postgresql-advanced-sql`, `postgresql-server-programming`. |
| `postgresql-operations` | `postgresql-administration`, `postgresql-performance`. |
| `postgresql-ai-platform` | Keep if pgvector/AI platform work is frequent; otherwise fold into `ai-rag-patterns`. |
| `mysql-engineering` | `mysql-best-practices`, `mysql-data-modeling`, `mysql-advanced-sql`. |
| `mysql-operations` | `mysql-administration`, `mysql-query-performance`. |
| `data-visualization` | Keep. |
| `python-data-analytics` | Keep. |
| `python-data-pipelines` | Keep. |
| `python-ml-predictive` | `demand-forecasting` as reference. |
| `excel-spreadsheets` | Keep if spreadsheet artifact generation is common. |
| `growth-telemetry-pipeline` | Fold into product analytics or observability unless materially distinct. |

Expected reduction: about 22 data/database skills to about 12.

### 6. Architecture, Backend, APIs, And Languages

Current issue: backend architecture, API design, GraphQL, microservices, language standards, JavaScript, TypeScript, PHP, Python, and Node are over-split.

Target: 22-28 active skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `system-architecture-design` | Keep baseline. |
| `distributed-systems-patterns` | `event-driven-architecture`, `realtime-systems` as references unless used heavily. |
| `microservices-architecture` | `microservices-fundamentals`, `microservices-architecture-models`, `microservices-communication`, `microservices-resilience`. |
| `microservices-ai-integration` | Fold into `ai-app-architecture` unless it has unique service-mesh/runtime guidance. |
| `api-design-first` | `api-error-handling`, `api-pagination`, `api-testing-verification` as references. |
| `graphql-patterns` | `graphql-security` as reference or companion security section. |
| `nodejs-development` | Keep. |
| `typescript-effective` | `typescript-mastery`, `typescript-design-patterns` as references. |
| `typescript-full-stack` | Keep for full-stack architecture. |
| `javascript-modern` | `javascript-advanced`, `javascript-patterns`. |
| `javascript-php-integration` | Fold into PHP or JS unless frequently used. |
| `php-modern-standards` | Keep. |
| `php-security` | Fold into `web-app-security-audit` or keep as PHP-specific if common. |
| `php-vs-nextjs` | Reference under architecture decision guides. |
| `python-modern-standards` | Keep. |
| `python-saas-integration` | Fold into `python-modern-standards` or SaaS architecture. |
| `modular-saas-architecture` | Keep. |
| `multi-tenant-saas-architecture` | Keep. |
| `saas-architecture-strategy` | Could absorb `saas-deployment-models` and `saas-control-plane-engineering`. |
| `saas-erp-system-design` | Keep if ERP scope is frequent and finance-heavy. |
| `saas-rate-limiting-and-quotas` | Keep or fold into SaaS entitlements/control plane. |
| `saas-sso-scim-enterprise-auth` | Keep enterprise-auth-specific. |
| `saas-tenant-data-portability-and-erasure` | Keep due legal/data lifecycle specificity. |
| `saas-tenant-onboarding-automation` | Fold into SaaS lifecycle if not deep. |
| `saas-seeder` | Keep if it is tied to a real template/tooling workflow. |

Expected reduction: about 40 architecture/backend/language skills to about 25.

### 7. Security And Compliance

Current issue: some security skills are general, while some are stack-specific or AI-specific. Keep specialist skills only where threat models materially differ.

Target: 7-9 active skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `vibe-security-skill` | General web/API/SaaS threat model and security review. |
| `web-app-security-audit` | Keep if it is a concrete audit workflow. |
| `code-safety-scanner` | Keep if it has a scanner workflow. |
| `network-security` | Keep. |
| `linux-security-hardening` | Keep. |
| `llm-security` | Fold into `ai-security` unless used independently outside AI app work. |
| `dual-auth-rbac` | Fold into security or SaaS enterprise auth unless dual-auth has strict domain rules. |
| `dpia-generator` | `uganda-dppa-compliance` can be a jurisdiction reference inside it. |
| `graphql-security` | Reference inside `graphql-patterns` and `vibe-security-skill`. |
| `php-security` | Reference inside `php-modern-standards` and `web-app-security-audit`. |

Expected reduction: about 13 security/compliance skills to about 8.

### 8. DevOps, Reliability, And Platform

Current issue: CI/CD and Kubernetes are over-split.

Target: 8-10 active skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `deployment-release-engineering` | Keep. |
| `observability-monitoring` | `observability-platform` as reference unless platform build is distinct. |
| `reliability-engineering` | Keep. |
| `cloud-architecture` | Keep. |
| `infrastructure-as-code` | Keep. |
| `docker-development` | Keep. |
| `cicd-pipelines` | `cicd-pipeline-design`, `cicd-devsecops`, `cicd-jenkins-debian`. |
| `kubernetes-platform` | `kubernetes-fundamentals`, `kubernetes-production`, `kubernetes-saas-delivery`. |

Expected reduction: about 15 platform skills to about 8.

### 9. Product, Business, Growth, Pricing, And Content

Current issue: business model, pricing, SaaS metrics, growth, sales, product discovery, premium positioning, and content are split into many adjacent skills.

Target: 16-20 active skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `premium-software-product-execution` | Premium software quality bar and packaging. |
| `premium-product-positioning` | `premium-client-sales` as sales reference if not used independently. |
| `product-discovery` | `feature-planning`, `competitive-analysis-pm`, discovery artifacts. |
| `product-strategy-vision` | Keep. |
| `product-led-growth` | `habit-forming-products`, growth loops. |
| `software-business-models` | Keep. |
| `software-pricing-strategy` | `saas-subscription-mastery` and pricing packaging references. |
| `subscription-billing` | `stripe-payments` if Stripe-only payment mechanics are not frequent enough to remain standalone. |
| `stripe-payments` | Keep if payment implementation happens often. |
| `saas-business-metrics` | `saas-growth-metrics`. |
| `saas-sales-organization` | Keep if sales org design is common. |
| `saas-lifecycle-email-orchestration` | `saas-transactional-email-infrastructure`, `tabler-email-templates` as references, unless email template generation is a frequent output. |
| `saas-admin-backoffice-tooling` | Keep if admin/backoffice design is frequent. |
| `saas-entitlements-and-plan-gating` | Keep; absorb AI-specific entitlement references if needed. |
| `customer-service-excellence` | Keep. |
| `content-writing` | `blog-writer`, `blog-idea-generator`, `east-african-english` style guide. |
| `it-proposal-writing` | `technology-grant-writing` only if grants are a reference mode; keep grant writing if frequent. |
| `professional-word-output` | `manual-guide`, report formatting references. |

Expected reduction: about 28 product/business/content skills to about 18.

### 10. SDLC, Documentation, Testing, And Skill Maintenance

Current issue: SDLC document generation is split by lifecycle phase. That makes sense as reference chapters, but not necessarily as separate skills.

Target: 12-16 active skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `world-class-engineering` | Keep baseline. |
| `advanced-testing-strategy` | `e2e-testing`, `sdlc-testing` as references where appropriate. |
| `project-requirements` | `spec-architect`, parts of `sdlc-planning`. |
| `sdlc-documentation` | `sdlc-design`, `sdlc-maintenance`, `sdlc-planning`, `sdlc-post-deployment`, `sdlc-testing`, `sdlc-user-deploy`. |
| `doc-architect` | Keep if it orchestrates documentation systems beyond SDLC. |
| `update-claude-documentation` | Keep if repository automation depends on it. |
| `skill-writing` | Keep. |
| `skill-composition-standards` | Keep. |
| `skill-safety-audit` | Keep. |
| `validation-contract` | Keep. |
| `implementation-status-auditor` | Keep if audit reports are frequent. |
| `plan-implementation` | Fold into project requirements or implementation status unless materially distinct. |
| `orchestration-best-practices` | Fold into skill composition unless used for agents generally. |
| `capability-matrix` | Fold into product discovery or architecture unless used often. |
| `custom-sub-agents` | Fold into orchestration or AI-agent runtime unless direct subagent authoring is common. |
| `language-standards` | Reference under engineering or docs. |
| `markdown-lint-cleanup` | Keep if tooling/script-backed; otherwise reference under docs. |

Expected reduction: about 24 SDLC/docs/skill-maintenance skills to about 14.

### 11. GIS

Current issue: 4 GIS skills split by domain, mapping, integration, and PostGIS.

Target: 1-2 active skills.

Recommended active skills:

| Keep active skill | Absorb these as references |
|---|---|
| `gis-enterprise-domain` | Enterprise GIS concepts and domain boundaries. |
| `gis-platform-engineering` | `gis-mapping`, `gis-maps-integration`, `gis-postgis-backend`. |

If GIS work is infrequent, keep only `gis-enterprise-domain` and put all implementation detail under references.

### 12. Media, Export, Localisation, And Miscellaneous

Recommended handling:

| Keep active skill | Absorb these as references |
|---|---|
| `image-compression` | Keep if image optimisation is common. |
| `photo-management` | Fold into `image-compression` unless it has a distinct workflow. |
| `report-print-pdf` | Fold into `professional-word-output`, mobile reports, or finance reporting depending on dominant usage. |
| `python-document-generation` | Fold into `professional-word-output` or Python standards unless it has scripts/templates. |
| `east-african-english` | Reference under `content-writing`. |

## Proposed Target Catalog Size

This is the recommended target allocation, not an exact rename list.

| Domain | Current rough count | Target active skills |
|---|---:|---:|
| AI and agentic systems | 78 | 26 |
| Finance and accounting | 46 including duplicates | 12, with doctrine submodule canonical |
| Mobile | 44 | 16 |
| Frontend, UI, UX | 33 | 18 |
| Databases, data, analytics | 22 | 12 |
| Architecture, backend, APIs, languages | 40 | 25 |
| Security and compliance | 13 | 8 |
| DevOps, reliability, platform | 15 | 8 |
| Product, business, growth, content | 28 | 18 |
| SDLC, docs, testing, skill maintenance | 24 | 14 |
| GIS | 4 | 2 |
| Meta/bootstrap | 2 | 1 |
| Media/export/localisation/misc | 13 | 6 |
| Buffer for future high-value skills | 0 | 15 |
| **Total target** | **356 recursive today** | **181 including buffer** |

Without the 15-skill buffer, the practical catalog lands around 166 active skills.

## Migration Plan

### Phase 0: Fix loader failures

1. Fix invalid frontmatter in the three skipped skills.
2. Validate them with:

```powershell
python -X utf8 skills/skill-writing/scripts/quick_validate.py skills/fixed-assets-and-depreciation
python -X utf8 skills/skill-writing/scripts/quick_validate.py skills/multicurrency-and-fx
python -X utf8 skills/skill-writing/scripts/quick_validate.py skills/finance/finance-module-audit
```

3. Split `00-meta-initialization/new-project/SKILL.md` so it is under 500 lines.

### Phase 1: Define the active-skill registry

Create a registry file:

```text
docs/skill-routing-index.md
```

It should define:

- Active skill slug.
- Old slugs absorbed.
- Reference file path for absorbed content.
- Owner domain.
- Validation command.
- Migration status.

Optional machine-readable version:

```text
docs/skill-aliases.yml
```

Example:

```yaml
fixed-assets-and-depreciation:
  active_skill: doctrine/skills/ifrs-standards-suite
  reference: doctrine/skills/ifrs-standards-suite/references/fixed-assets-and-depreciation.md
  status: absorbed
```

### Phase 2: Consolidate one domain at a time

Recommended order:

1. Finance duplicates and invalid skills.
2. AI agentic skills.
3. Mobile, especially iOS.
4. Database engines.
5. SDLC document generators.
6. SaaS/product/business skills.
7. Frontend/UX overlaps.
8. DevOps and Kubernetes.
9. GIS and miscellaneous.

For each cluster:

1. Pick the retained parent skill.
2. Read each source `SKILL.md` fully.
3. Extract durable content into `references/<old-slug>.md`.
4. Update parent `SKILL.md` with routing conditions and direct reference links.
5. Move scripts/templates into the parent skill when still used.
6. Delete or rename old `SKILL.md` files so they are not active entrypoints.
7. Update cross-links and root routing docs.
8. Run validation.

### Phase 3: Add guardrails so the count does not grow again

Add a repository check that fails when active skill count exceeds 200.

Suggested policy:

```text
Active skill = any file named SKILL.md under skills/ plus approved active submodule roots.
Finance doctrine = approved active submodule root at doctrine/skills/.
Reference material must not be named SKILL.md.
```

Validation should check:

- Active skill count <= 200.
- No duplicate `name:` frontmatter values.
- `description` length <= 1024.
- `name` matches directory slug.
- Every updated `SKILL.md` has the acknowledgement line.
- No `SKILL.md` exceeds 500 lines.
- Every absorbed skill is represented in the alias/routing index.

### Phase 4: Run safety and contract audit

For each migrated domain:

```powershell
python -X utf8 skills/skill-writing/scripts/quick_validate.py skills/<parent-skill>
python -X utf8 skills/skill-writing/scripts/contract_gate.py --skill skills/<parent-skill>
```

For finance doctrine parents, validate the submodule path instead:

```powershell
python -X utf8 skills/skill-writing/scripts/quick_validate.py doctrine/skills/<parent-skill>
python -X utf8 skills/skill-writing/scripts/contract_gate.py --skill doctrine/skills/<parent-skill>
```

Then run a repository-level scan:

```powershell
python -X utf8 skills/skill-writing/scripts/contract_gate.py --all
```

## Risks And Decisions

### Do not keep redirect skills unless absolutely necessary

A redirect `SKILL.md` still counts as a skill. If compatibility is needed, keep a small number of temporary redirect skills, but they must fit inside the 200 cap and have an expiry date.

### Avoid hiding specialist routing inside vague mega-skills

Consolidation should not produce generic skills that agents cannot route well. Each retained skill needs a clear decision table:

- When to use the parent.
- Which reference file to load.
- Which companion skills to load.
- What output evidence is expected.

### Finance doctrine canonical source

The current duplicate finance skills are the clearest drift risk. The selected direction is:

- `doctrine/skills/*` is the canonical active finance doctrine catalog.
- `skills/finance/*` duplicates should be removed, renamed out of `SKILL.md`, or reduced to a very small number of orchestration wrappers only when they add behaviour outside doctrine.
- Root skills such as `accounting-engine` and `accounting-finance-controller` may remain active because they orchestrate implementation across finance doctrine, SaaS, architecture, database, security, and UX skills.

This is a deliberate exception to the normal `skills/<skill-name>/SKILL.md` convention because the AGENTS finance trigger explicitly treats `doctrine/` as the finance submodule to load for money, tax, inventory, payroll, banking, mobile money, POS, statutory compliance, and accounting-record work.

### Some high-value specialist skills should stay standalone

Do not over-collapse skills that have unique trigger moments and produce distinct artifacts. Examples:

- `world-class-engineering`
- `system-architecture-design`
- `database-design-engineering`
- `api-design-first`
- `advanced-testing-strategy`
- `deployment-release-engineering`
- `observability-monitoring`
- `vibe-security-skill`
- `accounting-engine`
- `finance-module-audit`
- `ai-rag-patterns`
- `ai-agent-runtime-architecture`
- `ios-development`
- `android-development`
- `webapp-gui-design`
- `premium-ui-ux-design`
- `skill-writing`
- `skill-safety-audit`

## Definition Of Done

The consolidation is complete when:

- Recursive active skill count is below 200.
- The three invalid skipped skills load successfully.
- No duplicate `name:` values exist.
- No active `SKILL.md` exceeds 500 lines.
- Old skill slugs are mapped in `docs/skill-routing-index.md` or `docs/skill-aliases.yml`.
- Each retained parent skill links directly to its absorbed reference files.
- The whole catalog passes quick validation and contract gates.
- Finance doctrine has a single active source of truth in the `doctrine/` submodule.

## Recommended First PR

Keep the first change small and high-confidence:

1. Fix the 3 invalid frontmatter files.
2. Add active skill counter validation.
3. Add `docs/skill-routing-index.md`.
4. Consolidate only finance duplicates first, keeping the doctrine submodule as canonical and de-activating duplicate `skills/finance/*` entrypoints.

Finance is the best first domain because it has obvious duplicate names and current loader errors. Once that pattern is reviewed, repeat it for AI-agent and mobile.
