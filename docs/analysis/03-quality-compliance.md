# Quality & Compliance Audit

**May 2026 (Updated) | Standards: doc-standards.md (500-line hard limit) | Skills: 245**

---

## Over-Limit Files — Status: All Fixed ✅

| Skill | Before | After | Status |
|-------|--------|-------|--------|
| modular-saas-architecture | 1,003 lines | 293 lines | ✅ Fixed |
| multi-tenant-saas-architecture | 760 lines | 268 lines | ✅ Fixed |
| mysql-data-modeling | 600 lines | 359 lines | ✅ Fixed |

No new over-limit files detected. Compliance rate: **100% within hard limit**.

---

## Contract-Gate Status — Regression to Fix ⚠️

**Last clean run:** 2026-04-16 → `210 scanned | 0 errors | 0 warnings | 10 exempt`
**Current run (2026-05-01):** `226 scanned | 0 errors | 17 warnings | 10 exempt`

The 17 newly-added skills missing the canonical `## Evidence Produced` section:

| Skill | Family | Severity |
|---|---|---|
| `pwa-offline-first` | Platform tier | High — closes a flagged gap; should set the example |
| `e2e-testing` | Testing | High — production-readiness skill |
| `kubernetes-platform` | K8s | High — production-readiness; also 135-line stub |
| `observability-platform` | SRE | High — production-readiness skill |
| `infrastructure-as-code` | Cloud | High — production-readiness skill |
| `tabler-email-templates` | Email | Medium |
| `ai-agentic-ui` | AI | Medium |
| `ai-output-design` | AI | Medium |
| `experiment-engineering` | Growth | Medium |
| `growth-telemetry-pipeline` | Growth | Medium |
| `product-discovery` | Growth | Medium |
| `product-led-growth` | Growth | Medium |
| `saas-growth-metrics` | Growth | Medium |
| `color-theory` | Design | Low — qualitative skill, may need new evidence category |
| `every-layout` | Design | Low — same |
| `design-by-nature` | Design | Low — same |
| `enterprise-ux-process` | Design | Low — also 96-line stub |

**Action:** Add `## Evidence Produced` to each, then promote
`MISSING_SECTION_SEVERITY` from `warning` to `error` in `contract_gate.py`.

---

## Stub Skills

The three blockers from prior audits are closed (`webapp-gui-design`,
`pos-restaurant-ui-standard`, `inventory-management` are all rewritten). New stubs
identified on 2026-05-01:

### 1. demand-forecasting — 35 lines (LOW, marked)
**Status:** Moved into `skills/` and explicitly stub-marked on 2026-05-01.
**Action:** Add `references/forecast-methods.md`, `references/backtesting-evidence.md`,
`references/sql-templates.md`. Skill remains usable as a baseline workflow.

### 2. kubernetes-platform — 135 lines (MEDIUM)
**Status:** Half the length of the existing 3-skill K8s family
(`kubernetes-fundamentals`, `kubernetes-production`, `kubernetes-saas-delivery`).
**Action:** Decide: merge content into one of the three peer skills, OR expand to
match (cluster topology, node pools, multi-region, zero-downtime upgrades).

### 3. enterprise-ux-process — 96 lines (MEDIUM)
**Status:** Markedly thinner than peers like `ux-principles-101`, `ux-psychology`,
`web-usability-krug`, `cognitive-ux-framework`.
**Action:** Promote to peer length or fold into `cognitive-ux-framework`.

---

## Repository-Root Pollution — Cleared 2026-05-01 ✅

The catalog migration left orphan directories at the repo root. Cleaned:

- `cicd-devsecops/` — empty, deleted (canonical lives in `skills/cicd-devsecops/`)
- `cicd-jenkins-debian/` — empty, deleted
- `cicd-pipeline-design/` — empty, deleted
- `demand-forecasting/` → moved to `skills/demand-forecasting/`

Note: a few non-skill helpers still live at root (`00-meta-initialization/`,
`professional-word-output/`, `saas-accounting-system/`, `code-safety-scanner.skill`,
`blog-posts/`, `claude-guides/`, `scripts/`). Some of these are skills that are
loaded directly by the harness; verify whether they should live under `skills/` or stay
at root. `code-safety-scanner.skill` (a single file, not a directory) is the most
unusual and should probably be moved into `skills/code-safety-scanner/SKILL.md`.

---

## Deprecated Skills — Status: Resolved ✅

The four `android-*` skills flagged in the prior audit
(`android-reports`, `android-saas-planning`, `android-report-tables`,
`android-custom-icons`) are no longer present in `skills/`. The `mobile-*` versions
are canonical.

---

## Skill Overlaps (Acceptable)

### Auth/RBAC — 3 skills serve different stacks
- `dual-auth-rbac` — Web/PHP sessions + JWT
- `ios-rbac` — iOS-specific (PermissionGate ViewModifier)
- `mobile-rbac` — Cross-platform Android + iOS

Keep all three.

### AI Billing/Metering — 3 skills serve different scopes
- `ai-cost-modeling` — Strategy: token economics and margin modeling
- `ai-metering-billing` — Implementation: ledger schema and metering middleware
- `ai-saas-billing` — Product: module gating and tenant quota management

Keep all three.

### Planning Skills — 4 skills at different scopes
- `mobile-saas-planning` — App-level planning
- `feature-planning` — Individual feature spec
- `project-requirements` — Requirements gathering
- `sdlc-planning` — Full SDLC phase

Keep all four.

### Kubernetes — 4 skills (review)
- `kubernetes-fundamentals`, `kubernetes-production`, `kubernetes-saas-delivery`,
  `kubernetes-platform`. The fourth duplicates content from the first three at
  half the depth. Recommend consolidation.

### Design fundamentals — 11 skills (acceptable, sweep)
The new design family (`every-layout`, `color-theory`, `design-by-nature`,
`grid-systems`, `motion-design`, `interaction-design-patterns`, `practical-ui-design`,
`cognitive-ux-framework`, `enterprise-ux-process`, `frontend-performance`,
`habit-forming-products`) overlaps with existing `ux-*` skills. None are clear
duplicates but a sweep is warranted to confirm scope boundaries are documented.

---

## Thin Coverage Skills (< 200 lines)

| Skill | Lines | Verdict |
|-------|-------|---------|
| `enterprise-ux-process` | 96 | **Promote or merge** |
| `kubernetes-platform` | 135 | **Consolidate** |
| `product-discovery` | 129 | Acceptable as decision framework |
| `tabler-email-templates` | 177 | Acceptable as catalog index |
| `ai-agentic-ui` | 184 | Acceptable as pattern library |
| `experiment-engineering` | 178 | Acceptable as decision-rule skill |
| `growth-telemetry-pipeline` | 167 | Acceptable as architectural pattern |
| `color-theory` | 167 | Acceptable as reference skill |
| `every-layout` | 186 | Acceptable as reference skill |
| `design-by-nature` | 186 | Acceptable as reference skill |
| `demand-forecasting` | 35 | **Stub-marked, expand** |

---

## Compliance Summary

| Category | Count | Percentage |
|----------|-------|------------|
| Fully compliant (< 500 lines) | 245 | 100% |
| Over-limit (> 500 lines) | 0 | 0% |
| Stub / incomplete | 3 | 1.2% |
| Deprecated (not yet marked) | 0 | 0% |
| Thin coverage (< 200 lines) | 11 | 4.5% |
| Missing `## Evidence Produced` | 17 | 7.5% (regression) |

---

## Immediate Action Priority

1. **Add `## Evidence Produced` to the 17 flagged skills**, then promote
   `MISSING_SECTION_SEVERITY: warning → error` in `contract_gate.py`.
2. **Decide on `kubernetes-platform`** — merge into the existing K8s trio or expand.
3. **Promote `enterprise-ux-process`** to peer length, or fold into `cognitive-ux-framework`.
4. **Expand `demand-forecasting`** with the three reference files listed in its stub banner.
5. **Move `code-safety-scanner.skill`** into a proper `skills/code-safety-scanner/SKILL.md`
   directory if it is intended to be a real skill.

---

*Next: [04-gap-analysis.md](04-gap-analysis.md)*
