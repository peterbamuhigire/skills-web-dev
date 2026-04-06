# Quality & Compliance Audit

**April 2026 | Standards: doc-standards.md (500-line hard limit)**

---

## Over-Limit Files (Must Fix)

### 1. modular-saas-architecture — 1,003 lines (CRITICAL)
**Problem:** More than double the 500-line limit. This is the worst offender.
**Impact:** Degrades AI comprehension, wastes tokens, violates stated standards.
**Fix:** Split into 3 files:
- `modular-saas-architecture/SKILL.md` — Module anatomy, when to use (≤500 lines)
- `modular-saas-architecture/references/module-patterns.md` — Deep patterns
- `modular-saas-architecture/references/module-examples.md` — Full examples

### 2. multi-tenant-saas-architecture — 760 lines (HIGH)
**Problem:** 52% over limit.
**Fix:** Split into 2 files:
- `multi-tenant-saas-architecture/SKILL.md` — Three-tier model, isolation patterns (≤500)
- `multi-tenant-saas-architecture/references/deep-dive.md` — Advanced patterns

### 3. mysql-data-modeling — 600 lines (MEDIUM)
**Problem:** 20% over limit.
**Fix:** Move deep entity examples to `references/party-model-deep-dive.md`

---

## Stub Skills (Must Complete or Deprecate)

### 1. webapp-gui-design — 27 lines (CRITICAL)
**Status:** The web frontend skill is 27 lines. This is the most important gap in
the entire repository given that web is the primary delivery platform for SaaS.
**Action:** Complete with full React/Next.js + Tailwind design patterns.
(Or supersede with a new `react-nextjs` skill and mark this as deprecated.)

### 2. pos-restaurant-ui-standard — 39 lines (HIGH)
**Status:** Exists in CLAUDE.md directory listing as a complete skill but is almost empty.
**Action:** Either write complete restaurant POS UI patterns or merge into `pos-sales-ui-design`.

### 3. inventory-management — 40 lines (HIGH)
**Status:** References other skills but provides no actual inventory patterns.
**Action:** Write complete inventory management patterns (warehouse, stock levels,
reorder triggers, barcode scanning, batch operations) or deprecate.

---

## Deprecated Skills (Should Be Marked Clearly)

| Skill | Status | Superseded By |
|-------|--------|---------------|
| android-reports | Marked superseded | mobile-reports |
| android-saas-planning | Partially superseded | mobile-saas-planning |
| android-report-tables | Partially superseded | mobile-report-tables |
| android-custom-icons | Partially superseded | mobile-custom-icons |

**Action:** Add `DEPRECATED: Use [skill-name] instead` as the first line of each deprecated skill.

---

## Skill Overlaps (Consider Consolidating)

### Auth/RBAC Overlap
Three RBAC skills with significant overlap:
- `dual-auth-rbac` — Web/PHP sessions + JWT
- `ios-rbac` — iOS-specific permission gating
- `mobile-rbac` — Cross-platform (Android + iOS) permission gating

**Recommendation:** Keep all three — they serve genuinely different stacks.
Add cross-references so Claude picks the right one automatically.

### Planning Overlaps
- `mobile-saas-planning` — Planning a mobile-first SaaS
- `android-saas-planning` — Android-specific planning
- `feature-planning` — Individual feature planning
- `project-requirements` — Requirements gathering

**Recommendation:** Keep all. They operate at different scopes.
Add a `planning-skill-guide.md` reference that explains when to use which.

### Report/Table Overlaps
- `mobile-reports` — Supersedes `android-reports`
- `mobile-report-tables` — Cross-platform table UI
- `android-report-tables` — Android-specific

**Recommendation:** Deprecate `android-reports`. The others cover distinct concerns.

---

## Quality Issues in Specific Skills

### Skills With Thin Coverage (< 200 lines)
These exist but provide minimal guidance:
| Skill | Lines | Issue |
|-------|-------|-------|
| android-custom-icons | 96 | Very thin — enforcement rules only, no examples |
| google-play-store-review | 84 | Minimal guidance |
| skill-safety-audit | 121 | Limited remediation guidance |
| laws-of-ux | 124 | Quick reference only — no application guidance |
| gis-mapping | 199 | Leaflet focus, missing advanced features |
| image-compression | 109 | Thin on format selection guidance |

These are acceptable if they are truly just checklists/references, but should be noted.

---

## Compliance Summary

| Category | Count | Percentage |
|----------|-------|------------|
| Fully compliant (< 500 lines) | 128 | 97.7% |
| Over-limit (> 500 lines) | 3 | 2.3% |
| Stub / incomplete | 3 | 2.3% |
| Deprecated (not yet marked) | 4 | 3.1% |
| Thin coverage (< 200 lines) | 6 | 4.6% |

---

## Immediate Action Priority

1. **Refactor modular-saas-architecture** (1,003 → ≤500 lines)
2. **Refactor multi-tenant-saas-architecture** (760 → ≤500 lines)
3. **Complete webapp-gui-design** or supersede with react-nextjs skill
4. **Complete pos-restaurant-ui-standard** or merge into pos-sales-ui-design
5. **Mark deprecated skills clearly** in their SKILL.md frontmatter
6. **Refactor mysql-data-modeling** (600 → ≤500 lines)

---

*Next: [04-gap-analysis.md](04-gap-analysis.md)*
