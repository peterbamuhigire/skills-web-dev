# Gap Analysis

## Update History

- **2026-04-12 original assessment:** five high-priority capability gaps flagged
- **2026-04-15 reassessment:** all five original gaps closed; remaining gaps were integration and normalisation concerns
- **2026-04-15 follow-up pass:** the two most load-bearing remaining gaps — cross-skill output contracts and un-normalised specialist skills — both closed structurally (contracts) and materially (first batch of 5 high-traffic skills normalised)

The body below is the 2026-04-15 reassessment as updated by the follow-up pass. The 2026-04-12 gap list is preserved at the end.

## Status of April 12 Gaps (all closed)

| April 12 Gap | Status | Closed by |
|---|---|---|
| Observability and Monitoring | CLOSED | `observability-monitoring` |
| Reliability and SRE | CLOSED | `reliability-engineering` |
| Advanced Testing Strategy | CLOSED | `advanced-testing-strategy` |
| Deployment and Release Engineering | CLOSED | `deployment-release-engineering` |
| Distributed Systems Discipline | CLOSED | `distributed-systems-patterns` + microservices-fundamentals, microservices-communication, microservices-resilience, microservices-ai-integration, microservices-architecture-models |

Each of these is now a first-class baseline skill. The "operability layer" the April 12 report called the biggest architectural bottleneck is structurally filled.

## New Capability Added Since 2026-04-12 (beyond closing original gaps)

- **Python (6 skills):** `python-modern-standards`, `python-saas-integration`, `python-data-analytics`, `python-document-generation`, `python-ml-predictive`, `python-data-pipelines`. Covers Python as sidecar / worker alongside PHP SaaS for analytics, branded document output, predictive ML, ETL, OCR.
- **Kubernetes (3 skills):** `kubernetes-fundamentals`, `kubernetes-production`, `kubernetes-saas-delivery`. From "no K8s coverage at all" to complete family covering mental model, production hardening, multi-tenant GitOps delivery.
- **TypeScript production (2 new):** `typescript-effective` (production idioms), `typescript-full-stack` (tRPC, Prisma, Fastify, Zod, turborepo).
- **GIS depth (3 new):** `gis-postgis-backend`, `gis-maps-integration`, `gis-enterprise-domain` — adds server-side spatial, Google Maps / Mapbox / MapLibre, ArcGIS admin + real-estate patterns.
- **SaaS business (2 new):** `saas-sales-organization`, `saas-subscription-mastery` — sales org design and subscription business strategy.

The repository grew from roughly 180 skills to 209, and the baseline layer grew from 5 to 11.

## Remaining Gaps (2026-04-15, follow-up pass)

### Gap 1: Cross-Skill Output Contracts — CLOSED (structural)

Codified by the new `skill-composition-standards` skill. Every SKILL.md must now declare:

- an **Inputs** table naming the upstream skill and artifact it depends on
- an **Outputs** table naming the downstream consumer and the template format it must produce in

14 canonical artifact templates were written under `skill-composition-standards/references/`: context-map, ADR, critical-flow, entity-model, access-patterns, migration-plan, OpenAPI contract, error-model, threat-model, SLO, release-plan, rollback-plan, runbook, test-plan. Each has a rules section and common-failures section so downstream skills can rely on the shape.

`world-class-engineering` now links to this skill as the enforcement spine. The 20-point house-style checklist enforces contract declaration during skill review.

Structural closure. Repository coverage of the contracts still depends on the normalisation pass below, because older skills declared none.

### Gap 2: Older Specialist Skills Not Yet Normalised — FIRST BATCH CLOSED (5 skills)

First normalisation batch complete. All 5 high-traffic specialist skills moved from ~7–8/20 on the house-style checklist to **19/20**:

| Skill | Before | After | Notes |
|---|---:|---:|---|
| `multi-tenant-saas-architecture` | 8/20 | 19/20 | Contracts declared, 5 decision tables, 9 concrete anti-patterns |
| `frontend-performance` | 8/20 | 19/20 | Performance-budget contract, 4 references split from 382-line SKILL |
| `api-design-first` | 7/20 | 19/20 | OpenAPI contract + error-model as formal outputs, 4 decision tables |
| `ai-web-apps` | 6/20 | 19/20 | AI module gate + token ledger as formal outputs, 10 anti-patterns |
| `vibe-security-skill` | 8/20 | 19/20 | Threat-model + abuse-case + auth matrix + secret-plan as outputs |

All 5 validator-green. Remaining work: roll the same normalisation over the rest of the specialist layer in batches. Each batch gets an entry in the ScoredNormalisation log.

Until that rollout is complete, specialist skills outside the first batch still vary in quality. The floor has moved, but not yet uniformly.

### Gap 3: Capability Matrix Absent (unchanged)

No single document maps capability -> baseline skill -> specialist skills -> validation skill -> remaining depth. Without it, operators cannot see at a glance whether a domain is fully supported and where to add depth.

### Gap 4: Validation Spine Not Yet Unified (unchanged)

Individual skills cover validation per domain (advanced-testing-strategy, skill-safety-audit, code-safety-scanner, vibe-security-skill, web-app-security-audit, etc.), but there is no repository-wide validation spine asking, for any substantial output:

- what proves correctness?
- what proves safety?
- what proves operability?
- what proves user quality?

### Gap 5: Book-Verbatim Grounding Inconsistent

The Python, Kubernetes, GIS, and TypeScript reference files were written when the system lacked PDF/EPUB extraction tooling. Content is canonical-knowledge-aligned rather than source-book-verbatim. Now that the Python toolkit is installed and the admin script is available for system binaries, future reference writing should be book-verbatim for book-sourced skills.

### Gap 6: Enforcement Remains Advisory

The baseline layer is now 11 skills strong, but nothing automatically blocks a downstream skill from shipping output that ignores observability, reliability, tests, or rollout plans. Enforcement is still a discipline choice by the operator.

## System Bottlenecks (2026-04-15)

### Bottleneck 1 (was #1 in April 12): Cross-skill output contract

Status: **CLOSED structurally**. `skill-composition-standards` codifies the contract. 5 high-traffic skills already produce contracts in the new format. Rollout to the rest of the specialist layer is in progress.

### Bottleneck 2 (was #2 in April 12): Missing operability layer

Status: **CLOSED**. `observability-monitoring`, `reliability-engineering`, `advanced-testing-strategy`, `deployment-release-engineering`, `distributed-systems-patterns`, and the Kubernetes production family now provide this layer.

### Bottleneck 3 (was #3 in April 12): Review and validation depth fragmented

Status: **partially open**. Individual validation skills exist and are strong; repository-wide validation spine still not unified.

### Bottleneck 4 (was #4 in April 12): Legacy and new standards coexist unevenly

Status: **partially closed**. First batch of 5 high-traffic skills now sit at 19/20 on the house-style checklist; the normalisation playbook and 20-point checklist are codified so subsequent batches can be rolled out deterministically. Remaining specialist skills outside batch 1 still need the same pass.

### Bottleneck 5 (was #5 in April 12): World-class target stated more than enforced

Status: **partially open**. The target is better matched by capability now (all 5 first-order gaps closed), but consistency and enforcement remain the remaining distance.

## Priority of Remaining Work

1. **Roll the normalisation playbook** over the rest of the specialist layer in batches of 5–8 skills. Each batch validated, scored, logged. (Floor-raising — the contract spine is live; the mass of skills still needs to adopt it.)
2. **Build a repository capability matrix** at `README.md` or `docs/capability-matrix.md` mapping domain -> baseline -> specialists -> validation -> gaps.
3. **Formalise the validation spine** — a single skill or document that codifies "what proves production-readiness" across correctness, safety, operability, UX.
4. **Book-verbatim pass** on the Python / Kubernetes / TypeScript / GIS / SaaS new-family reference files, now that PDF/EPUB extraction tooling is available.
5. **CI enforcement** of the contract gate — parse Inputs/Outputs tables and warn when a claimed upstream artifact is not declared by any upstream skill.

---

## Historical: 2026-04-12 Gap Analysis (preserved)

The April 12 assessment identified five missing capability areas as the primary gap to world-class:

1. Observability and Monitoring
2. Reliability and SRE
3. Advanced Testing Strategy
4. Deployment and Release Engineering
5. Distributed Systems Discipline

Plus four weak areas:
- uneven skill maturity
- weak baseline enforcement
- inconsistent cross-skill contracts
- production operations underrepresented

And five bottlenecks:
1. no mandatory output interface between layers
2. missing operability layer
3. review and validation depth fragmented
4. legacy and new standards coexist unevenly
5. world-class target stated more strongly than enforced

As of 2026-04-15, all five missing capabilities have been added. Three of the five bottlenecks remain fully or partially open. The primary lever for the next improvement is formalising cross-skill output contracts.
