# Skill Routing Index

Source: `docs/skills-trimminhg.md`

Date: 2026-05-17

This index records the intended consolidation routing without moving or deleting
skill directories. It exists so old skill slugs can be mapped to retained parent
skills while the catalog is reduced below the active-skill cap.

## Active Skill Policy

- Active skill roots are `skills/` and `00-meta-initialization/`.
- Active skill means a file named `SKILL.md` under an active root.
- Target active catalog size is 150-170 skills, with a hard cap of 200.
- Reference material must not be named `SKILL.md`.
- Inactive aliases retain their original content as `ALIAS.md` in the same
  directory and route through `docs/skill-aliases.yml`.
- Redirect skills count as active skills and should be temporary if used.
- Finance doctrine is canonical in the external `chwezi-accounting-doctrine`
  engine. Local `doctrine/skills/` files are retained reference material only.

Current guardrail baseline after the 2026-06-21 external-engine split:

| Metric | Value |
|---|---:|
| Active `SKILL.md` files | 179 |
| Guardrail hard cap | 200 |
| Duplicate frontmatter names | 0 |
| Inactive alias files retained | 47 |

## 2026-06-13 Consulting Delivery Additions

The GIZ 7000012724 skills enhancement added three active global skills because
they are cross-engine operating controls rather than proposal-, business-plan-,
social-, or SRS-specific domain skills.

| Trigger | Route |
|---|---|
| Multi-workstream bid or consulting delivery control room, RACI, RAID, deliverables register, decision log, evidence register | `skills/product-business/consulting-delivery-control-room` |
| Word/PDF/Excel, application register, scoring matrix, budget, dashboard, price schedule, report, or annex generation readiness | `skills/product-business/document-spreadsheet-tooling-readiness` |
| High-stakes bid red-team, evaluator simulation, compliance knockout scan, evidence audit, spreadsheet review, delivery feasibility, final release gate | `skills/sdlc-meta/world-class-bid-red-team-and-delivery-qc` |

## Finance Doctrine Canonicality

Finance, accounting, tax, inventory, payroll, banking, mobile money, POS,
statutory compliance, and accounting-record work routes first to the external
`chwezi-accounting-doctrine` engine for doctrine-owned rules. Duplicate finance
entrypoints under `skills/finance-accounting/finance/*` are compatibility
aliases only until their durable material is absorbed into retained references
or a small number of orchestration wrappers.

Root-level finance implementation skills may remain active when they add behavior
outside doctrine:

| Active skill | Role |
|---|---|
| `skills/finance-accounting/accounting-engine` | Posting engine, ledger integrity, reversals, idempotency, implementation contracts. |
| `skills/finance-accounting/accounting-finance-controller` | Controller-grade routing, quality gates, finance audit orchestration. |
| `skills/saas/saas-accounting-system` | SaaS-specific accounting product architecture, if still distinct from `accounting-engine`. |
| `doctrine/skills/*` | Retained accounting doctrine reference material; not active in this local engine. |

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
| AI evaluation | `ai-evaluation` | `ai-eval-suite`, eval suites, regression gates |
| AI security | `ai-security` | `llm-security`, `ai-prompt-injection-and-tenant-safety` |
| AI analytics | `ai-analytics` | `ai-analytics-dashboards`, `ai-analytics-saas`, `ai-analytics-strategy`, `ai-nlp-analytics`, `ai-predictive-analytics` |
| AI cost and billing | `ai-cost-and-metering` | `ai-cost-modeling`, `ai-cost-per-tenant-attribution`, `ai-metering-billing`, `ai-usage-metering-and-billing` |
| Agent runtime | `ai-agent-runtime-architecture` | `ai-agent-async-and-long-running-tasks`, `ai-agent-memory` |
| Agent tools and HITL | `ai-agent-tooling-and-hitl` | `ai-agent-tool-catalogue-and-action-gating`, `ai-agents-tools`, `ai-agent-action-approval-and-hitl` |
| Agent governance | `ai-agent-governance-and-limits` | `ai-agent-cost-and-step-budgets`, `ai-agent-reversibility-and-blast-radius` |
| Coding-agent environment optimisation | `coding-agent-optimization` | Device-specific Codex and Claude Code context, model, subagent, permission, and token tuning |
| Agent evidence | `ai-agent-observability-evaluation` | `ai-agent-eval`, `ai-agent-task-success-tracking`, `ai-agent-observability-and-replay`, `ai-agent-evidence-automation` |
| Agent commercial ops | `ai-agent-commercial-operations` | `ai-agent-pricing-engine`, `ai-agent-attempted-vs-completed-billing`, `ai-agent-revenue-recognition`, `ai-agent-abandonment-and-refund-policy` |
| Agent compliance | `ai-agent-compliance-controls` | `ai-agent-soc2-controls`, `ai-agent-iso27001-controls`, `ai-agent-hipaa-security-controls`, `ai-agent-control-testing-and-attestation`, `ai-agent-audit-log-integrity` |
| Android | `android-development` | `android-ai-ml`, `android-biometric-login`, `android-pdf-export` |
| Android persistence | `android-data-persistence` | `android-room` |
| Android UI | `android-ui-ux-design` | `jetpack-compose-ui` |
| iOS core | `ios-development` | `ios-project-setup`, `ios-swift-recipes` |
| iOS architecture | `ios-architecture` | `ios-architecture-advanced`, `ios-at-scale`, `ios-production-patterns` |
| iOS AI/ML | `ios-ai-ml` | Foundation Models, Core AI, Core ML, Vision, NaturalLanguage, on-device evaluation |
| iOS persistence | `ios-data-persistence` | `ios-swiftdata`, semantic indexing, AI local context caches |
| iOS UI | `ios-ui-ux-design` | `swiftui-design`, `swiftui-pro-patterns`, `ios-uikit-advanced` |
| iOS capabilities | `ios-platform-capabilities` | `ios-biometric-login`, `ios-bluetooth-printing`, `ios-push-notifications`, `ios-pdf-export`, `ios-networking-advanced`, App Intents, Siri, Spotlight semantic indexing |
| iOS quality/release | `ios-quality-and-release` | Swift Testing, Device Hub, Xcode Cloud, TestFlight, App Store release evidence |
| iOS security/RBAC | `ios-security-and-rbac` | Keychain, App Attest, Trust Insights, App Intents authorization, AI tool security |
| iOS monetization | `ios-monetization` | StoreKit 2, App Store Server API, subscriptions, Unity StoreKit plugin |
| Mobile operations | `mobile-platform-operations` | `mobile-custom-icons`, `mobile-rbac`, `mobile-saas-planning`, `google-play-store-review`, Apple TestFlight/Xcode Cloud operations |
| SaaS managed visual assets | `saas-managed-visual-assets` | Authentication background pools, light/dark logos, favicons, secure admin lifecycle, fallback, and audit |
| Full-coverage SaaS seeding | `full-coverage-saas-seeding` | Synthetic tenant demonstrations, phased application-boundary journeys, schema-compatibility gates, controlled reference/configuration exceptions, temporal refresh, replay, reset, isolation, reconciliation, and evidence |
| Frontend CSS | `tailwind-css` | `responsive-design`, `every-layout`, `grid-systems` |
| UX foundations | `ux-foundations` | `ux-principles-101`, `ux-psychology`, `laws-of-ux`, `web-usability-krug`, `cognitive-ux-framework` |
| UX content | `ux-content-strategy` | `ux-writing` |
| Frontend architecture | `frontend-architecture` | Component boundaries, tokens, state/content contracts, design-system implementation, frontend quality and migration decisions |
| ERP POS sales operations | `pos-sales-operations-engineering` | Tenant default customer, three POS surfaces, product-to-finished-stock identity, manufacturing timing, canonical posting, permissions, idempotency, and reconciliation |
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
| Enterprise Java and JVM | `java-enterprise-development` | Java, Spring, Jakarta EE, Hibernate, jOOQ, Maven, Gradle, Quarkus, Micronaut, Helidon, GraalVM, WebLogic, Oracle JDBC/UCP, JVM diagnostics and modernisation |
| Python executable and desktop-suite distribution | `python-modern-standards` | PyInstaller, auto-py-to-exe, Nuitka, frozen applications, multi-executable suites, portable ZIPs, Inno Setup installers, signing, and Windows packaging CI |
| Security | `vibe-security-skill` | `dual-auth-rbac`, selected stack security references |
| GraphQL | `graphql-patterns` | `graphql-security` |
| CI/CD | `cicd-pipelines` | `cicd-pipeline-design`, `cicd-devsecops`, `cicd-jenkins-debian` |
| Kubernetes | `kubernetes-platform` | `kubernetes-fundamentals`, `kubernetes-production`, `kubernetes-saas-delivery` |
| Product discovery | `product-discovery` | `feature-planning`, `competitive-analysis-pm` |
| Content | `content-writing` | `blog-writer`, `blog-idea-generator`, `east-african-english` |
| SDLC docs | `sdlc-documentation` | `sdlc-design`, `sdlc-maintenance`, `sdlc-planning`, `sdlc-post-deployment`, `sdlc-testing`, `sdlc-user-deploy` |
| GIS | `gis-platform-engineering` | `gis-mapping`, `gis-maps-integration`, `gis-postgis-backend` |

## Eleven-engine control plane

Use `skills/sdlc-meta/engine-control-plane` when the work concerns cross-engine
routing, agent roles, thin commands, lifecycle hooks, evidence contracts,
handoffs, bounded recovery, or adapter design. The registry lives at
`docs/engine-control-plane.json`; its validator is
`scripts/validate_engine_control_plane.py`.

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

## Game development family

Route complete game initiatives through `skills/game-development/game-development-orchestration/SKILL.md`, then load only the required specialists:

| Intent | Skill |
|---|---|
| Inception, risky assumptions, hypotheses, prototype choice, experiment gates, pivot or stop decisions | `lean-game-product-development` |
| Player fantasy, loop, touch controls, sessions, onboarding, accessibility, progression or economy | `mobile-game-design` |
| Unity C# project, scenes, prefabs, input, saves, Android/iOS build | `unity-mobile-game-development` |
| Godot scenes, nodes, resources, signals, scripts or mobile export | `godot-mobile-game-development` |
| Combat, quests, inventory, progression or world/save state | `gameplay-systems-architecture` |
| NPC behaviour, behaviour/state trees, perception, navigation, crowds, reservations or AI profiling | `game-ai-behaviour-and-navigation` |
| Coordinate spaces, transforms, vectors, quaternions, curves, probability, fixed-step simulation or numerical stability | `game-math-and-simulation` |
| Render pipeline, shaders, materials, lighting, shadows, visibility, post-processing or graphics API diagnosis | `real-time-game-graphics` |
| Concepts, models, UVs, textures, rigs, animation, LODs, colliders or imports | `game-3d-asset-pipeline` |
| Blender source files, rig controls, shape keys, export presets, FBX/glTF, clean re-import or Blender automation | `blender-game-asset-production` |
| Music, ambience, Foley, voice, buses, spatial/adaptive audio or audio rights | `game-audio-implementation` |
| Frame pacing, CPU/GPU, memory, loading, battery, heat or device budgets | `mobile-game-performance` |
| QA, playtesting, balance, accessibility/localisation regression, alpha/beta/RC | `game-testing-polish` |
| Signing, stores, privacy, ratings, IAP, rollout, rollback, support or live events | `mobile-game-release-liveops` |
| iOS/iPadOS/macOS game services, Metal diagnosis, controllers, haptics, cloud saves, Mac windowing, signing or notarisation | `apple-game-platform-delivery` |
| Multiplayer authority, replication, RPCs, prediction, matchmaking, sessions, reconnect, backend state or protocol evolution | `online-multiplayer-and-game-backend` |
| Reproducible Unity/Godot/Unreal builds, manifests, symbols, signing boundaries, promotion, certification or rollback | `game-build-release-engineering` |
| Game trust boundaries, anti-cheat, tampering, economy fraud, bots, abuse investigation, enforcement or appeals | `game-security-anti-cheat-and-abuse` |
| Unreal Engine C++, Blueprints, Gameplay Framework, assets, automation, packaging or Unreal profiling | `unreal-game-development` |
| Sprites, atlases, tile sets, 2D rigs/animation, UI art, particles, VFX or resolution variants | `game-2d-art-animation-and-vfx-pipeline` |
| Levels, worlds, encounters, missions, procedural generation, streaming or content throughput | `level-world-and-content-production` |
| Interactive story, characters, dialogue, quests, choices, story state, environmental narrative or setup/payoff | `game-narrative-and-interactive-story-design` |
| Game telemetry, metrics, experiments, remote config, economy sources/sinks, live events or data quality | `game-data-analytics-and-live-economy` |
| Game discovery, estimation, staffing/RACI, SOW, greenlight, milestones, outsourcing, launch command or case evidence | `game-studio-delivery-and-commercial-operations` |
| Accessible gameplay, remapping, sensory alternatives, localisation, cultural review, moderation or player safety | `game-accessibility-localisation-and-player-safety` |

For historical, cultural, market, legal or version-sensitive claims, pair this family with the external Digital Research Skills Engine. For interface appearance, pair it with `design-system-skills`. For native store operations, reuse the existing Android/iOS/mobile-platform skills.

- Update this file when a retained parent skill changes.
- Add the same mapping to `docs/skill-aliases.yml` when a route needs to be machine-readable.
- Do not remove old directories as part of registry maintenance.
- Run `python -X utf8 scripts/skill_catalog_guardrails.py --report-only` after registry updates.
