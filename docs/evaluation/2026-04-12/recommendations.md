# Recommendations

## Update History

- **2026-04-12 original:** recommended 6 new skills + system-level improvements
- **2026-04-15 reassessment:** all 6 recommended skills completed (plus 10 more in adjacent families); new priority is enforcement and normalisation, not more new skills

## Status of April 12 Recommendations

### New skills recommended (6)

| April 12 Recommendation | Status | Delivered as |
|---|---|---|
| 1. Observability and Monitoring | DONE | `observability-monitoring` |
| 2. Reliability Engineering | DONE | `reliability-engineering` |
| 3. Advanced Testing Strategy | DONE | `advanced-testing-strategy` |
| 4. Deployment and Release Engineering | DONE | `deployment-release-engineering` |
| 5. Distributed Systems Patterns | DONE | `distributed-systems-patterns` + microservices-* family (5 skills) |
| 6. Performance Profiling | PARTIALLY DONE | Addressed inside `frontend-performance`, `mysql-query-performance`, `postgresql-performance`, `python-data-analytics/references/performance-and-polars.md`; no stand-alone skill |

### Baseline improvements recommended

| Recommendation | Status |
|---|---|
| Strengthen world-class-engineering with explicit output artifacts | PARTIAL — baseline expanded to 11 skills but formal output-artifact contracts not yet introduced |
| system-architecture-design distributed systems guidance | DONE via `distributed-systems-patterns` + microservices family |
| database-design-engineering replication / CDC / hot-path patterns | PARTIAL — covered in `python-data-pipelines/references/etl-external-apis.md` and postgresql-* family but not yet folded back into database-design-engineering |
| saas-erp-system-design cross-module workflow + policy engines | STILL OPEN — not prioritised this cycle |
| git-collaboration-workflow CI/release coupling | PARTIAL — addressed in `cicd-pipeline-design`, `cicd-pipelines`, `deployment-release-engineering` |

### System-level improvements recommended

| Recommendation | Status |
|---|---|
| Standardise skill interfaces (cross-skill output contracts) | NOT DONE — highest-priority remaining item |
| Add a validation spine | PARTIAL — individual validation skills exist (`skill-safety-audit`, `code-safety-scanner`, `api-testing-verification`, etc.) but no unified spine |
| Normalise older skills against new baseline | NOT DONE — still the biggest consistency gap |
| Create a repository capability matrix | NOT DONE |
| Forward-testing for key skills | NOT DONE |

## Adjacent Work Completed Since April 12 (beyond the original recommendations)

- **Python family** (6 skills): entire analytics / documents / ML / pipelines stack
- **Kubernetes family** (3 skills): fundamentals, production, SaaS delivery
- **TypeScript production family** (2 new): effective TS, full-stack TS
- **GIS depth** (3 new): PostGIS, Google/Mapbox, ArcGIS + real-estate
- **SaaS business** (2 new): sales organisation, subscription mastery

Plus the `engineering-management-system` baseline skill (not on the April 12 list) covering team operating rhythm, prioritisation, delegation, coaching — meaningfully expanding the delivery-side baseline.

## New Recommendations (2026-04-15)

The focus shifts from "add missing capability" to "unify and enforce what exists". In priority order:

### 1. Introduce cross-skill output contracts (HIGHEST PRIORITY)

Codify in `world-class-engineering` the mandatory output artifacts every baseline skill must produce:

- architecture output: context map + critical-flow table + ADR set + dependency diagram + failure modes
- database output: entity model + access patterns + index plan + migration plan + retention + tenancy
- API output: OpenAPI contract + auth model + error model + observability notes + idempotency keys
- release output: test evidence + rollout plan + rollback plan + monitoring plan + runbook
- observability output: SLOs + alerts + dashboards + runbook per service
- security output: threat model + abuse cases + auth/authz matrix + secret handling

Each downstream skill declares what upstream artifacts it consumes. That makes the repository a composable system rather than a library.

### 2. Normalise older specialist skills against the new baseline

Target the top 20 most-loaded older specialist skills. For each:

- add "When this skill applies" section if missing
- add decision-rule tables with concrete thresholds
- extract deep content into `references/` files
- add anti-patterns section
- add explicit cross-references to adjacent skills

This closes the ceiling-floor gap.

### 3. Build a capability matrix

Single document at `docs/capability-matrix.md` with columns: capability | baseline skill | specialist skills | validation skill | remaining depth | next-step priority. Operators can see at a glance where a domain is fully supported and where gaps remain.

### 4. Formalise a validation spine

One skill, `validation-spine` or similar, that every substantial engineering output must map onto:

- what proves correctness? (tests, contracts, invariants)
- what proves safety? (threat model, abuse cases, least privilege)
- what proves operability? (SLOs, alerts, rollback, runbook)
- what proves user quality? (UX review, a11y audit, performance budgets)

### 5. Book-verbatim normalisation pass on new reference files

The Python, Kubernetes, TypeScript, GIS, and SaaS business reference files were authored when the agent sandbox lacked PDF/EPUB extraction tooling. Now that the Python toolkit is installed (PyMuPDF, pdfplumber, ebooklib, BeautifulSoup) and the admin script exists for system binaries (poppler, tesseract, ghostscript, pandoc), re-run book extraction for the reference files we flagged in each agent's "Gaps" note, to lift content from canonical-aligned to book-sourced.

### 6. Forward-test the baseline

For each of the 11 baseline skills, write 3–5 representative evaluation prompts and a rubric. Run them periodically (or at least on baseline-skill changes) and grade the output. This is the enforcement mechanism baseline-strength has been missing.

### 7. Consider a dedicated performance-profiling skill

The April 12 recommendation #6 was partially addressed by scattered content. A stand-alone `performance-profiling` skill covering backend profiling, DB hot-path analysis, memory / CPU diagnosis, capacity planning, and regression detection would complete the six-recommendation set and close the last pure-capability gap.

## Priority Order

Recommended implementation order for the 2026-04-15 cycle:

1. Cross-skill output contracts (architectural lever)
2. Normalise top 20 older specialist skills
3. Capability matrix
4. Validation spine
5. Book-verbatim normalisation pass on new families
6. Forward-testing harness for baseline
7. Performance-profiling skill (if appetite remains)

---

## Historical: 2026-04-12 Recommendations (preserved)

See earlier versions of this file in git history for the full original recommendation set. The April 12 recommendations covered:

- 6 new skills (observability, reliability, testing, deployment, distributed systems, performance)
- Baseline improvements to the 5 existing baseline skills
- 5 system-level improvements (interfaces, validation spine, normalisation, capability matrix, forward-testing)

Of those, 5 of 6 new skills are fully complete, the 6th is partially addressed, and the system-level improvements remain open — now elevated to the top of the 2026-04-15 priority order.
