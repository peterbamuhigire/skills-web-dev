# validation-contract — Design Spec

- **Date:** 2026-04-16
- **Author:** Peter Bamuhigire (with Claude Opus 4.6)
- **Status:** Approved for implementation
- **Companion to:** `skill-composition-standards`, `world-class-engineering`

## 1. Purpose

The repository contains roughly 170 skills. Many touch validation in some form — security, testing, performance, observability, accessibility, release management — but there is no single contract that says *what evidence a feature must produce before it ships*. The result is that "validation" lives implicitly across baseline skills and gets re-stated in inconsistent ways inside specialist skills.

`validation-contract` closes this gap by codifying the **third repository-wide contract**, alongside the two already established by `skill-composition-standards`:

1. **House-style contract** — every skill follows the same shape (`skill-composition-standards`, Standard 1).
2. **Inputs/Outputs contract** — every skill declares the artifacts it consumes and produces (`skill-composition-standards`, Standard 2).
3. **Evidence contract** — every specialist skill declares which validation categories its artifacts contribute to, and the repository defines a canonical Release Evidence Bundle that aggregates that evidence at ship time (this skill).

The skill is **contract-style**: normative, not content-heavy. It does not re-explain how to do security or testing — it defines what evidence those skills must point at, and the canonical fillable artifact a reviewer produces before declaring a release done.

## 2. Non-goals

- Not a replacement for `world-class-engineering`. That skill keeps its production-readiness bar; this skill makes the *evidence* of meeting that bar a first-class artifact.
- Not a replacement for any category-specific validation skill (`vibe-security-skill`, `design-audit`, `frontend-performance`, etc.). They remain the source of truth for *how* to validate within their category.
- Not an enforcement engine. Strictness is **normative but unenforced** — the language is binding, but mechanical enforcement is the job of item 5 (CI contract-gate hook), to land separately.

## 3. The 7 evidence categories

Every specialist skill in the repository, when applicable, contributes evidence to one or more of:

| # | Category | What the evidence proves | Indicative contributing skills |
|---|----------|--------------------------|-------------------------------|
| 1 | **Correctness** | Behaviour matches spec; tests cover risk surface; contracts hold | `advanced-testing-strategy`, `api-testing-verification`, `android-tdd`, `ios-tdd`, `kmp-tdd` |
| 2 | **Security** | Threat model exists; scans clean; secrets handled; auth/authorisation verified | `vibe-security-skill`, `php-security`, `ios-app-security`, `web-app-security-audit`, `llm-security`, `cicd-devsecops` |
| 3 | **Data safety** | Schema integrity; migration safety; backup, retention, and PII handling | `database-design-engineering`, `postgresql-administration`, `mysql-administration`, `dpia-generator`, `uganda-dppa-compliance` |
| 4 | **Performance** | Budgets met; load profile understood; query plans acceptable | `frontend-performance`, `mysql-query-performance`, `postgresql-performance` |
| 5 | **Operability** | SLOs defined; runbook exists; observability wired; rollback plan ready | `observability-monitoring`, `reliability-engineering`, `database-reliability` |
| 6 | **UX quality** | Accessibility pass; design audit; content/UX-writing review; AI slop check | `design-audit`, `ux-writing`, `ai-slop-prevention`, `cognitive-ux-framework` |
| 7 | **Release evidence** | Change record; migration plan; rollout/rollback log; post-deploy verification | `deployment-release-engineering`, `sdlc-post-deployment`, `git-collaboration-workflow` |

These seven are deliberately fixed. Adding an eighth requires editing this skill, not silently extending it elsewhere — the closed taxonomy is what makes the contract usable by both reviewers and the future CI hook.

## 4. Declaration mechanic

### 4.1 What a specialist skill adds

Specialist skills add a `## Evidence Produced` section to their `SKILL.md`, placed between the existing `## Outputs` and `## References` sections:

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Threat model | Markdown doc per `skill-composition-standards/references/threat-model.md` | `docs/security/threat-model-checkout.md` |
| Operability | Runbook | Markdown doc per `skill-composition-standards/references/runbook.md` | `docs/runbooks/payment-failures.md` |
```

### 4.2 Rules

- A specialist skill that produces validation evidence **MUST** declare at least one row.
- Each row's `Category` value **MUST** be one of the seven canonical names (case-sensitive).
- Each row's `Format` field **MUST** reference an existing template (e.g., one of the 14 canonical artifact templates in `skill-composition-standards/references/`) or define its own format inline in the same SKILL.md.
- A specialist skill **MAY** contribute to multiple categories — most security skills will hit Security and at least one of {Data safety, Operability}.
- Baseline skills, process skills (e.g., `superpowers:brainstorming`, `superpowers:test-driven-development`), and pure index/orchestration skills **MUST NOT** declare. They define frame, not artifacts.

### 4.3 Identifying skill type

A skill is "specialist" for the purposes of this contract if:

- It produces concrete project artifacts (code patterns, schemas, configs, documents), **and**
- It is loaded for a specific domain or platform problem rather than as a baseline frame.

Skills exempt from declaring (non-exhaustive): `world-class-engineering`, `skill-composition-standards`, `validation-contract` itself, `system-architecture-design`, `engineering-management-system`, `git-collaboration-workflow` (process), `feature-planning` (process), `spec-architect` (process), all `superpowers:*` skills.

When a skill straddles the line, the default is **declare**. False positives in the declaration table are cheaper than silent omissions.

## 5. The Release Evidence Bundle

### 5.1 Purpose

When a feature or release is ready to ship, the reviewer produces a single fillable document — the **Release Evidence Bundle** — that links to the concrete artifacts satisfying each of the 7 categories. This document is the canonical answer to *"how do we know this is ready?"*

### 5.2 Template

Stored in `validation-contract/references/release-evidence-bundle-template.md`:

```markdown
# Release Evidence Bundle — <feature or release name>

- **Date:** YYYY-MM-DD
- **Owner:** <name>
- **Scope:** <one-line description of what is shipping>
- **Risk tier:** <low | medium | high>

## 1. Correctness
- Test plan: <link or "N/A — reason">
- Latest CI run: <link>
- Contract tests (API/data): <link or "N/A — reason">

## 2. Security
- Threat model: <link or "N/A — reason">
- Scan output (SAST/DAST/dependency): <link or "N/A — reason">
- Secrets handling note: <link or "N/A — reason">

## 3. Data safety
- Migration plan: <link or "N/A — no schema changes">
- Backup verification: <link or "N/A — reason">
- PII / retention note: <link or "N/A — reason">

## 4. Performance
- Performance budget evidence: <link or "N/A — non-performance-sensitive">
- Load profile / query plan review: <link or "N/A — reason">

## 5. Operability
- SLO record: <link or "N/A — reason">
- Runbook: <link or "N/A — reason">
- Observability wiring (logs/metrics/traces): <link or "N/A — reason">
- Rollback plan: <link or "N/A — reason">

## 6. UX quality
- Design audit: <link or "N/A — no UI surface">
- Accessibility pass: <link or "N/A — no UI surface">
- Content / UX-writing review: <link or "N/A — no user-facing copy">
- AI slop check: <link or "N/A — no AI-generated UI">

## 7. Release evidence
- Change record (PR / commit range): <link>
- Rollout plan: <link or "N/A — reason">
- Post-deploy verification: <link or "N/A — reason">
```

### 5.3 N/A semantics

- `N/A` is permitted **only with a reason on the same line**.
- An empty cell is not acceptable; the reviewer must either link evidence or write `N/A — <reason>`.
- The CI hook (item 5) will eventually parse this bundle and fail when an N/A is missing its reason.

### 5.4 Risk tier guidance

- **Low risk** (internal tools, documentation, non-user-facing scripts): typical bundle has 3–4 categories live, the rest justified `N/A`.
- **Medium risk** (user-facing feature, single-tenant): all 7 categories addressed; some may be `N/A` with reason.
- **High risk** (multi-tenant data, payments, auth, external API surface, AI features): all 7 categories live, no `N/A` permitted on Correctness, Security, Data safety, Operability, or Release evidence.

## 6. Integration with existing skills

This skill is integrated into the repository through three layers of edits, **all executed as part of this skill's implementation plan** (not deferred):

### 6.1 Baseline skills — minimal cross-reference

- `world-class-engineering` — adds a closing line: *"For ship readiness, see `validation-contract` for the canonical release evidence bundle."*
- `skill-composition-standards` — under *Standard 2 — Input/Output contracts*, adds a one-paragraph cross-reference noting `validation-contract` as the third contract dimension.
- `CLAUDE.md` (repository root) — lists `validation-contract` alongside `skill-composition-standards` under "Key Baseline Skills".
- `README.md` and `PROJECT_BRIEF.md` — single-line additions describing the new skill.

### 6.2 Directly-validating specialist skills — add Evidence Produced section

The following 16 skills get their `## Evidence Produced` table added in this skill's implementation pass, because they are the canonical contributors per category. Platform-specific variants (e.g., `android-tdd`, `ios-tdd`, `php-security`, `ios-app-security`, `mysql-administration`) are deferred to item 1 to keep this skill's blast radius bounded:

- **Correctness:** `advanced-testing-strategy`, `api-testing-verification`
- **Security:** `vibe-security-skill`, `web-app-security-audit`, `llm-security`, `cicd-devsecops`
- **Data safety:** `database-design-engineering`, `dpia-generator`
- **Performance:** `frontend-performance`
- **Operability:** `observability-monitoring`, `reliability-engineering`
- **UX quality:** `design-audit`, `ux-writing`, `ai-slop-prevention`
- **Release evidence:** `deployment-release-engineering`, `sdlc-post-deployment`

### 6.3 Remaining ~150 specialist skills — deferred to normalisation rollout (item 1)

The full sweep of `## Evidence Produced` tables across the rest of the catalogue is item 1 (normalisation rollout). This bounds item 2's blast radius and keeps each spec/plan focused.

## 7. File structure

```
validation-contract/
├── SKILL.md                                     # ~400 lines, contract spec
└── references/
    ├── evidence-categories.md                   # ~250 lines: per-category definition, examples, common artifacts
    ├── declaration-form.md                      # ~150 lines: how to write the Evidence Produced table; worked examples
    ├── release-evidence-bundle-template.md      # the canonical fillable artifact
    └── integration-rollout.md                   # the edits made to other skills (audit trail)
```

## 8. SKILL.md frontmatter

```yaml
---
name: validation-contract
description: Use when authoring or normalising a specialist skill, or preparing to ship a feature/release — defines the seven evidence categories every specialist skill must declare against and provides the canonical Release Evidence Bundle template. The contract spine that turns scattered validation skills into a coherent ship-readiness check.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---
```

## 9. SKILL.md outline

1. Use When / Do Not Use When (per house style)
2. Required Inputs (per house style)
3. Workflow (per house style)
4. Quality Standards (per house style)
5. Anti-Patterns (per house style)
6. Outputs (per house style)
7. References (per house style)
8. **The three repository-wide contracts** — narrative locating this skill alongside `skill-composition-standards`
9. **The seven evidence categories** — table + per-category one-paragraph definition
10. **Declaration mechanic** — the `## Evidence Produced` table form and rules
11. **The Release Evidence Bundle** — purpose, template summary, N/A semantics, risk tier guidance
12. **Specialist vs exempt skills** — the rule for who declares
13. **Integration with existing skills** — the three-layer rollout
14. **Strictness** — normative but unenforced; how item 5 will mechanise it later

## 10. Strictness

- The contract uses **MUST**, **MAY**, **MUST NOT** in the RFC 2119 sense.
- Mechanical enforcement is **out of scope** for this skill. It lands as item 5 (CI contract-gate hook), which will:
  - parse `## Evidence Produced` tables and warn on missing/invalid categories
  - parse Release Evidence Bundles and warn on empty cells or unjustified N/A
- Authoring this skill with binding language now means item 5 is a parser/CI integration only, not a policy debate.

## 11. Validation of this skill

- Validator: `python -X utf8 skill-writing/scripts/quick_validate.py validation-contract`
- Manual check: confirm `## Evidence Produced` exists in each of the ~15 directly-validating specialist skills after edit pass.
- Manual check: confirm baseline skills (`world-class-engineering`, `skill-composition-standards`) cross-reference correctly.
- Manual check: README, PROJECT_BRIEF, CLAUDE.md updated.

## 12. Out of scope (deferred to other items)

- **Item 1 (normalisation rollout):** adds `## Evidence Produced` to the remaining ~155 specialist skills.
- **Item 3 (capability matrix):** the validation column of the matrix becomes populatable once this skill exists.
- **Item 5 (CI contract-gate hook):** mechanical enforcement of both Inputs/Outputs and Evidence Produced declarations.
- **Item 4 (book-verbatim grounding):** unrelated content work in reference files for Python / Kubernetes / TypeScript / GIS skills.

## 13. Acceptance criteria for the implementation plan

The implementation pass (next step, via `writing-plans`) is complete when:

1. `validation-contract/` directory exists with `SKILL.md` and the four reference files.
2. Validator passes on `validation-contract`.
3. The 16 directly-validating specialist skills (listed in section 6.2) carry `## Evidence Produced` tables that cite the right categories and existing templates.
4. `world-class-engineering` and `skill-composition-standards` cross-reference `validation-contract`.
5. `CLAUDE.md`, `README.md`, `PROJECT_BRIEF.md` updated.
6. A single commit (or coherent commit series) lands all of the above with a message that names the contract addition explicitly.
