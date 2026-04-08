# Quality & Compliance Audit

**April 2026 (Updated) | Standards: doc-standards.md (500-line hard limit)**

---

## Over-Limit Files — Status: All Fixed ✅

The three over-limit violations from the first audit have been resolved:

| Skill | Before | After | Status |
|-------|--------|-------|--------|
| modular-saas-architecture | 1,003 lines | 293 lines | ✅ Fixed |
| multi-tenant-saas-architecture | 760 lines | 268 lines | ✅ Fixed |
| mysql-data-modeling | 600 lines | 359 lines | ✅ Fixed |

No new over-limit files detected. Compliance rate: **100% within hard limit**.

---

## Stub Skills (Must Complete or Deprecate)

These three stubs remain unchanged from the first audit. All are blocking business value.

### 1. webapp-gui-design — 27 lines (CRITICAL)
**Status:** Still 27 lines. React, Next.js, Tailwind, and TypeScript skills now exist,
making this stub even more embarrassing by contrast.
**Action:** Either write a comprehensive React + Tailwind + component architecture guide,
or deprecate and point to `react-development`, `nextjs-app-router`, and `tailwind-css`.

### 2. pos-restaurant-ui-standard — 39 lines (HIGH)
**Status:** Still 39 lines. Blocking the restaurant POS vertical SaaS opportunity.
**Action:** Write complete patterns for: order entry, kitchen display, receipt printing,
table management, modifier selection, split billing, and staff management flows.

### 3. inventory-management — 40 lines (HIGH)
**Status:** Still 40 lines. Blocking pharmacy, logistics, and warehouse SaaS verticals.
**Action:** Write complete patterns for: stock levels, reorder triggers, barcode scanning,
batch operations, supplier management, stock-take, and FIFO/LIFO tracking.

---

## Deprecated Skills (Not Yet Marked)

| Skill | Status | Superseded By |
|-------|--------|---------------|
| android-reports | Unmarked | mobile-reports |
| android-saas-planning | Unmarked | mobile-saas-planning |
| android-report-tables | Unmarked | mobile-report-tables |
| android-custom-icons | Unmarked | mobile-custom-icons |

**Action:** Add `DEPRECATED: Use [skill-name] instead` as the first line of each.

---

## Skill Overlaps (Acceptable)

### Auth/RBAC — 3 skills serve different stacks
- `dual-auth-rbac` — Web/PHP sessions + JWT
- `ios-rbac` — iOS-specific (PermissionGate ViewModifier)
- `mobile-rbac` — Cross-platform Android + iOS

Keep all three. Add cross-references in each.

### AI Billing/Metering — 3 skills serve different scopes
- `ai-cost-modeling` — Strategy: token economics and margin modeling
- `ai-metering-billing` — Implementation: ledger schema and metering middleware
- `ai-saas-billing` — Product: module gating and tenant quota management

Keep all three. They are genuinely different levels of abstraction.

### Planning Skills — 4 skills at different scopes
- `mobile-saas-planning` — App-level planning
- `feature-planning` — Individual feature spec
- `project-requirements` — Requirements gathering
- `sdlc-planning` — Full SDLC phase

Keep all four. Scopes do not overlap.

---

## Thin Coverage Skills (< 200 lines)

These exist but provide minimal guidance. Acceptable as checklists/references.

| Skill | Lines | Verdict |
|-------|-------|---------|
| google-play-store-review | ~84 | Acceptable as checklist |
| android-custom-icons | ~96 | Acceptable as enforcement rules |
| skill-safety-audit | ~121 | Acceptable as meta-skill |
| laws-of-ux | ~124 | Acceptable as quick reference |
| image-compression | ~109 | Consider expanding or merging |
| gis-mapping | ~199 | Acceptable, Leaflet focus |

---

## Compliance Summary

| Category | Count | Percentage |
|----------|-------|------------|
| Fully compliant (< 500 lines) | 174 | 100% |
| Over-limit (> 500 lines) | 0 | 0% |
| Stub / incomplete | 3 | 1.7% |
| Deprecated (not yet marked) | 4 | 2.3% |
| Thin coverage (< 200 lines) | 6 | 3.4% |

---

## Immediate Action Priority

1. **Deprecate 4 android-\* skills** — add DEPRECATED line to each
2. **Complete webapp-gui-design** or write deprecation pointing to React skills
3. **Complete pos-restaurant-ui-standard** — POS vertical is blocked
4. **Complete inventory-management** — pharmacy/logistics verticals are blocked
5. **Review image-compression** — expand or merge into frontend-performance

---

*Next: [04-gap-analysis.md](04-gap-analysis.md)*
