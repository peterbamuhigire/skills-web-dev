# capability-matrix — Design Spec

- **Date:** 2026-04-16
- **Author:** Peter Bamuhigire (with Claude Opus 4.6)
- **Status:** Approved for implementation
- **Companion to:** `validation-contract`, `skill-composition-standards`, `world-class-engineering`

## 1. Purpose

The repository now has ~170 skills. Choosing the right stack for a given project — Foundation, Implementation, Validation, and Companions — is the single most error-prone step at the start of any work. `CLAUDE.md` partially addresses this with five "X Baseline" prose sections (Python, TypeScript, Kubernetes, GIS, UI/UX), but those sections are fragmented, miss several common domains (mobile, AI, ERP), and intermix prose principles with concrete skill lists.

`capability-matrix` consolidates per-domain skill stacks into a single hand-curated lookup table. Claude loads the matrix when starting a project or scoping a feature, identifies the relevant domain row, and pulls Foundation → Implementation → Validation → Companions from a single source of truth.

## 2. Non-goals

- Not a replacement for `world-class-engineering` (production-readiness bar) or `validation-contract` (evidence categories). The matrix tells Claude *which skills* to load; those baselines tell Claude *how to use* them.
- Not auto-generated. Editorial judgment about the canonical recommendation per domain is the matrix's value. Auto-aggregating frontmatter would surface every skill, defeating curation.
- Not exhaustive of every possible niche. Verticals (Healthcare, POS, Payments) get one-line addenda, not their own rows.

## 3. Shape

### 3.1 File structure

```
capability-matrix/
├── SKILL.md                              # ~300 lines: matrix table + how-to-use
└── references/
    ├── domain-rationale.md               # ~200 lines: why each row picks the skills it does
    └── companion-rules.md                # ~80 lines: when UX, content, security, release companions kick in
```

Mirrors `validation-contract` shape.

### 3.2 Frontmatter

```yaml
---
name: capability-matrix
description: Use when starting a new project, scoping a feature, or deciding which skill stack to load — provides the canonical Foundation → Implementation → Validation → Companions skill set per technology domain. The lookup table that turns "I'm building X" into "load these skills, in this order".
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---
```

### 3.3 The matrix

Four columns, 17 rows. Each cell holds 1–4 skill names. Columns:

- **Foundation** — architecture, data, contracts (e.g., `system-architecture-design`, `database-design-engineering`).
- **Implementation** — platform/framework skills (e.g., `nextjs-app-router`, `android-development`).
- **Validation** — `validation-contract` contributors that apply (e.g., `vibe-security-skill`, `frontend-performance`).
- **Companions** — non-validation cross-cutting skills (e.g., `ux-writing`, `git-collaboration-workflow`).

The 17 rows:

1. Web/SaaS
2. Multi-tenant SaaS
3. iOS
4. Android
5. KMP/Compose Multiplatform
6. API/HTTP
7. Database (relational)
8. Frontend (React/Next)
9. AI Feature
10. LLM Integration
11. Python Service
12. TypeScript Stack
13. Kubernetes
14. GIS
15. ERP/Business System
16. CI/CD pipeline
17. Observability/SRE

### 3.4 SKILL.md outline

1. House-style 8 sections (Use When → References) inside dual-compat block.
2. **How to use the matrix** — three lookup steps: identify domain → load Foundation+Implementation+Validation → add Companions as the work demands.
3. **The matrix** — the 17-row 4-column table.
4. **Domain disambiguation** — short paragraph for cases where two rows could apply (e.g., "AI feature in a SaaS" → load both AI Feature and Multi-tenant SaaS rows, dedupe).
5. **Vertical addenda** — one paragraph listing common verticals and their add-on skills:
   - Healthcare → add `healthcare-ui-design`
   - POS / Restaurant → add `pos-sales-ui-design`, `pos-restaurant-ui-standard`
   - Payments → add `stripe-payments`, `subscription-billing`
   - Auth surface → add `dual-auth-rbac`, `mobile-rbac`, `ios-rbac`
   - East-African / Uganda compliance → add `uganda-dppa-compliance`, `dpia-generator`, `language-standards`
6. **Evidence-contract note** — one paragraph reminding readers that every row's Validation column maps to one or more `validation-contract` evidence categories.
7. **Companion Skills** (the standard section).

### 3.5 References

- `references/domain-rationale.md` — one paragraph per row explaining *why* those particular skills were picked. Lets Claude answer "why did you load X?" and helps future maintainers update intelligently.
- `references/companion-rules.md` — decision rules for when each Companion category kicks in:
  - UX — anything user-facing → auto-load `grid-systems`, `practical-ui-design`, `interaction-design-patterns`.
  - Content — anything with copy → auto-load `content-writing`, `ux-writing`, `language-standards`.
  - Security baseline — always for web/API → auto-load `vibe-security-skill`.
  - Release — anything shipping to production → auto-load `deployment-release-engineering`.

## 4. CLAUDE.md migration

The matrix absorbs the per-domain baselines currently scattered through `CLAUDE.md`. CLAUDE.md keeps the global ordering principle and the critical rules but loses the five "X Baseline" sub-sections.

**Removed from CLAUDE.md** (each migrates into a matrix row or addendum):

- `## UI/UX Baseline` → Frontend row + Companions column + `companion-rules.md`
- `## Python Baseline` → Python Service row
- `## TypeScript Baseline` → TypeScript Stack row
- `## Kubernetes Baseline` → Kubernetes row
- `## GIS Baseline` → GIS row
- `## SaaS Business Skills (non-engineering)` → Multi-tenant SaaS row's Companions, plus a vertical addendum

**Added to CLAUDE.md** under "Key Baseline Skills":

```
- `capability-matrix` - per-domain Foundation → Implementation → Validation → Companions skill stacks; load when starting any new project or feature
```

`README.md` and `PROJECT_BRIEF.md` get the same single-line addition in their baseline-skill listings.

## 5. Integration with `validation-contract`

The Validation column of every matrix row pulls skills that are themselves declared `validation-contract` contributors. The cross-reference is explicit at the bottom of `SKILL.md`:

> Validation entries in this matrix are drawn from `validation-contract`'s seven evidence categories. The matrix tells you *which* validation skills apply per domain; `validation-contract` defines *what evidence* those skills must produce at ship time.

## 6. Strictness

The matrix is **advisory, not binding**. Claude should:

- Treat the matrix as the default starting set. Loading a domain's row is the *minimum* — Claude can add more skills if the work demands.
- Treat omissions as gaps to flag, not silent skips. If the matrix has no row for the work at hand, say so and ask the user to clarify the domain rather than guessing.

## 7. File structure on disk

```
capability-matrix/
├── SKILL.md
└── references/
    ├── domain-rationale.md
    └── companion-rules.md
```

## 8. Acceptance criteria

1. `capability-matrix/` directory exists with `SKILL.md` and the two reference files.
2. Validator passes (`python -X utf8 skill-writing/scripts/quick_validate.py capability-matrix`, exit 0).
3. The matrix table contains 17 domain rows, each with at least one entry in Foundation, Implementation, and Validation. Companions may be empty for niche rows.
4. Vertical addenda paragraph names at minimum 5 verticals.
5. `CLAUDE.md` no longer contains the five "X Baseline" sub-sections (UI/UX, Python, TypeScript, Kubernetes, GIS) or "SaaS Business Skills"; instead it has a single pointer line under Key Baseline Skills.
6. `README.md` and `PROJECT_BRIEF.md` mention `capability-matrix` in their baseline-skill listings.
7. Cross-reference to `validation-contract` present at the bottom of `capability-matrix/SKILL.md`.
8. All edits land in a coherent commit series. Suggested split:
   - Commit 1: create the new skill (3 files).
   - Commit 2: migrate `CLAUDE.md` and update `README.md` / `PROJECT_BRIEF.md`.

## 9. Out of scope

- **Item 1 (normalisation rollout)** — adding `## Evidence Produced` to the remaining ~150 specialist skills. Independent track.
- **Item 5 (CI contract-gate hook)** — mechanical enforcement. Independent track.
- **Item 4 (book-verbatim grounding)** — content work in reference files for Python / Kubernetes / TypeScript / GIS skills. Independent track.
- **Project-archetype matrix** (greenfield SaaS, brownfield refactor, etc.) — could be added later as a second skill or as a section inside `capability-matrix`. Not in scope for this pass.
- **Problem-type rows** (auth, billing, observability wiring) — out of scope; recommended for separate handling if it ever becomes painful.
