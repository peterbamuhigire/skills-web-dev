# Recommendations

## Update History

- **2026-04-12 original:** recommended 6 new skills + system-level improvements
- **2026-04-15 reassessment:** all 6 recommended skills completed (plus 10 more in adjacent families); new priority is enforcement and normalisation, not more new skills
- **2026-04-15 follow-up pass:** cross-skill output contracts codified (`skill-composition-standards`), first batch of 5 older skills normalised to 19/20

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
| Standardise skill interfaces (cross-skill output contracts) | **DONE** — `skill-composition-standards` skill codifies the house-style template and I/O contract declaration; 14 canonical artifact templates published |
| Add a validation spine | PARTIAL — individual validation skills exist (`skill-safety-audit`, `code-safety-scanner`, `api-testing-verification`, etc.) but no unified spine |
| Normalise older skills against new baseline | **FIRST BATCH DONE** — 5 high-traffic skills (multi-tenant-saas-architecture, frontend-performance, api-design-first, ai-web-apps, vibe-security-skill) at 19/20 on the house-style checklist; rollout continues |
| Create a repository capability matrix | NOT DONE |
| Forward-testing for key skills | NOT DONE |

## Adjacent Work Completed Since April 12 (beyond the original recommendations)

- **Python family** (6 skills): entire analytics / documents / ML / pipelines stack
- **Kubernetes family** (3 skills): fundamentals, production, SaaS delivery
- **TypeScript production family** (2 new): effective TS, full-stack TS
- **GIS depth** (3 new): PostGIS, Google/Mapbox, ArcGIS + real-estate
- **SaaS business** (2 new): sales organisation, subscription mastery

Plus the `engineering-management-system` baseline skill (not on the April 12 list) covering team operating rhythm, prioritisation, delegation, coaching — meaningfully expanding the delivery-side baseline.

## New Recommendations (2026-04-15, follow-up pass)

The focus has shifted from "add missing capability" to "unify and enforce what exists". The two highest-priority architectural items from the morning pass are now materially addressed. Remaining items in priority order:

### 1. Cross-skill output contracts — DONE (2026-04-15 follow-up)

Codified by `skill-composition-standards`. Every SKILL.md now declares Inputs and Outputs tables. Fourteen canonical artifact templates published under `skill-composition-standards/references/`. Baseline contract register fixes the output set for every baseline skill type. `world-class-engineering` links to it as the enforcement authority.

### 2. Normalise older specialist skills — FIRST BATCH DONE; ROLLOUT CONTINUES

First batch (5 skills) complete and validator-green at 19/20. Next batches, proposed:

- **Batch 2 (operational):** `observability-monitoring`, `reliability-engineering`, `deployment-release-engineering`, `advanced-testing-strategy`, `distributed-systems-patterns` — confirm each produces its declared artifact set in the template format.
- **Batch 3 (platform):** `nextjs-app-router`, `ios-development`, `android-development`, `nodejs-development`, `php-modern-standards` — high-traffic stack baselines.
- **Batch 4 (data):** `postgresql-fundamentals`, `mysql-best-practices`, `mysql-data-modeling`, `postgresql-administration`, `database-reliability` — normalise the data family.
- **Batch 5 (UI/UX):** `grid-systems`, `practical-ui-design`, `interaction-design-patterns`, `ux-writing`, `design-audit`.

Batch cadence: 5 skills per pass, parallel agent dispatch, validator run, score log entry, commit.

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

## Priority Order (updated)

- [x] Cross-skill output contracts (architectural lever) — **done** via `skill-composition-standards`
- [~] Normalise older specialist skills — **first batch of 5 done; rolling**
- [ ] Capability matrix
- [ ] Validation spine
- [ ] Book-verbatim normalisation pass on new families
- [ ] Forward-testing harness for baseline
- [ ] Performance-profiling skill (if appetite remains)
- [ ] CI enforcement of contract gate (parse Inputs/Outputs tables, warn on orphan claims)

---

## Historical: 2026-04-12 Recommendations (preserved)

See earlier versions of this file in git history for the full original recommendation set. The April 12 recommendations covered:

- 6 new skills (observability, reliability, testing, deployment, distributed systems, performance)
- Baseline improvements to the 5 existing baseline skills
- 5 system-level improvements (interfaces, validation spine, normalisation, capability matrix, forward-testing)

Of those, 5 of 6 new skills are fully complete, the 6th is partially addressed, and the system-level improvements remain open — now elevated to the top of the 2026-04-15 priority order.
