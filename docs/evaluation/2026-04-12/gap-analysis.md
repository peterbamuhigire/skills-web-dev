# Gap Analysis

## Update History

- **2026-04-12 original assessment:** five high-priority capability gaps flagged
- **2026-04-15 reassessment:** all five original gaps closed; remaining gaps are integration and normalisation concerns, not missing capability

The body below is the 2026-04-15 reassessment. The 2026-04-12 gap list is preserved at the end.

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

## Remaining Gaps (2026-04-15)

The remaining gaps are integration and enforcement concerns, not missing capability.

### Gap 1: Cross-Skill Output Contracts Still Implicit

Despite strong individual skills, there is no repository-wide rule about what a baseline skill must produce for downstream skills. Example of the kind of contract still missing:

- Architecture skill output must include: context map, critical-flow table, ADR set, dependency diagram.
- Database skill output must include: entity model, access patterns, index plan, migration plan.
- API skill output must include: OpenAPI contract, auth model, error model, observability notes.
- Release skill output must include: test evidence, rollout plan, rollback plan, monitoring plan.

Without this, the skills still behave like linked documents rather than a guaranteed-composable system. This is the single biggest remaining architectural gap.

### Gap 2: Older Specialist Skills Not Yet Normalised

New skills (Python, Kubernetes, TypeScript production, GIS, SaaS business, and the 6 new baseline skills) follow a consistent high-rigour template — decision rules, thresholds, anti-patterns, references to deep-dive files.

Many older specialist skills pre-date that template and still read as:

- example-heavy tactical notes
- stack-specific guidance without decision logic
- partially outdated conventions

Until these are normalised against the new baseline style, the repository's floor lags its ceiling.

### Gap 3: Capability Matrix Absent

No single document maps capability -> baseline skill -> specialist skills -> validation skill -> remaining depth. Without it, operators cannot see at a glance whether a domain is fully supported and where to add depth.

### Gap 4: Validation Spine Not Yet Unified

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

Status: **still open**. Highest priority architectural improvement remaining.

### Bottleneck 2 (was #2 in April 12): Missing operability layer

Status: **CLOSED**. `observability-monitoring`, `reliability-engineering`, `advanced-testing-strategy`, `deployment-release-engineering`, `distributed-systems-patterns`, and the Kubernetes production family now provide this layer.

### Bottleneck 3 (was #3 in April 12): Review and validation depth fragmented

Status: **partially open**. Individual validation skills exist and are strong; repository-wide validation spine still not unified.

### Bottleneck 4 (was #4 in April 12): Legacy and new standards coexist unevenly

Status: **still open**. The gap between new-style and older-style skills is in fact wider now — the new skills raised the ceiling, and older skills have not been brought up. Next-phase normalisation pass addresses this.

### Bottleneck 5 (was #5 in April 12): World-class target stated more than enforced

Status: **partially open**. The target is better matched by capability now (all 5 first-order gaps closed), but consistency and enforcement remain the remaining distance.

## Priority of Remaining Work

1. **Introduce cross-skill output contracts** in `world-class-engineering` so every baseline skill must produce a defined artifact set that downstream skills can consume. (Architectural lever — unblocks the biggest remaining bottleneck.)
2. **Normalise high-traffic older specialist skills** against the new baseline template (decision rules, thresholds, anti-patterns, reference splits).
3. **Build a repository capability matrix** at `README.md` or `docs/capability-matrix.md` mapping domain -> baseline -> specialists -> validation -> gaps.
4. **Formalise the validation spine** — a single skill or document that codifies "what proves production-readiness" across correctness, safety, operability, UX.
5. **Book-verbatim pass** on the Python / Kubernetes / TypeScript / GIS / SaaS new-family reference files, now that PDF/EPUB extraction tooling is available.

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
