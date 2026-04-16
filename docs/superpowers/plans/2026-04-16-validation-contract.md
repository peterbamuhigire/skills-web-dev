# validation-contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the `validation-contract` skill and wire it into the existing baseline / specialist catalogue so every specialist skill declares which of seven fixed evidence categories it contributes to, and shipping produces a canonical Release Evidence Bundle.

**Architecture:** Contract-style, normative-but-unenforced baseline skill mirroring `skill-composition-standards`. One `SKILL.md` plus four reference files. Light cross-references in two baseline skills and three repo docs. Sixteen directly-validating specialist skills gain a `## Evidence Produced` table in this pass; the remaining ~150 are deferred to item 1 (normalisation rollout).

**Tech Stack:** Markdown skill files (UTF-8), YAML frontmatter, Python validator at `skill-writing/scripts/quick_validate.py`, Git.

**Spec:** `docs/superpowers/specs/2026-04-16-validation-contract-design.md`

---

## File Structure

**New files (all under `validation-contract/`):**

- `validation-contract/SKILL.md` — contract definition, < 500 lines, house-style compliant
- `validation-contract/references/evidence-categories.md` — 7 category definitions with examples
- `validation-contract/references/declaration-form.md` — `## Evidence Produced` table rules and worked examples
- `validation-contract/references/release-evidence-bundle-template.md` — canonical fillable artifact
- `validation-contract/references/integration-rollout.md` — audit trail of edits made to other skills in this pass

**Modified files:**

- `world-class-engineering/SKILL.md` — closing cross-reference
- `skill-composition-standards/SKILL.md` — paragraph under Standard 2
- `CLAUDE.md` — add `validation-contract` to Key Baseline Skills list
- `README.md` — single-line addition
- `PROJECT_BRIEF.md` — single-line addition
- Sixteen specialist `SKILL.md` files — add `## Evidence Produced` section between `## Outputs` and `## References`:
  - `advanced-testing-strategy/SKILL.md`
  - `api-testing-verification/SKILL.md`
  - `vibe-security-skill/SKILL.md`
  - `web-app-security-audit/SKILL.md`
  - `llm-security/SKILL.md`
  - `cicd-devsecops/SKILL.md`
  - `database-design-engineering/SKILL.md`
  - `dpia-generator/SKILL.md`
  - `frontend-performance/SKILL.md`
  - `observability-monitoring/SKILL.md`
  - `reliability-engineering/SKILL.md`
  - `design-audit/SKILL.md`
  - `ux-writing/SKILL.md`
  - `ai-slop-prevention/SKILL.md`
  - `deployment-release-engineering/SKILL.md`
  - `sdlc-post-deployment/SKILL.md`

**Commits:** one commit per phase (four total), last commit is the final integration commit.

---

## Phase 1 — Create the validation-contract skill

### Task 1: Create `validation-contract/SKILL.md`

**Files:**
- Create: `validation-contract/SKILL.md`

- [ ] **Step 1: Verify the directory does not already exist**

Run: `ls C:/Users/BIRDC/.claude/skills/validation-contract/ 2>/dev/null || echo "does not exist"`
Expected: `does not exist`

- [ ] **Step 2: Write the full SKILL.md**

Use the Write tool to create `C:/Users/BIRDC/.claude/skills/validation-contract/SKILL.md` with the following exact content:

````markdown
---
name: validation-contract
description: Use when authoring or normalising a specialist skill, or preparing to ship a feature or release — defines the seven evidence categories every specialist skill must declare against and provides the canonical Release Evidence Bundle template. The contract spine that turns scattered validation skills into a coherent ship-readiness check.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Validation Contract

<!-- dual-compat-start -->
## Use When

- Authoring a new specialist skill and deciding which validation evidence it should produce.
- Normalising an older specialist skill against the current house style.
- Preparing a feature or release for ship and assembling the Release Evidence Bundle.
- Reviewing a PR that claims a feature is production-ready.

## Do Not Use When

- The work is purely local, experimental, or explicitly throwaway with no path to production.
- The skill being authored is a baseline, process, or pure index skill. Those do not declare evidence.
- The task is unrelated to validation planning or shipping readiness.

## Required Inputs

- The specialist skill or feature being validated, including its intended scope and risk tier.
- Access to the repository's existing validation skills (`advanced-testing-strategy`, `vibe-security-skill`, `observability-monitoring`, etc.) as the source of category-specific "how to validate" content.
- Awareness of the 14 canonical artifact templates in `skill-composition-standards/references/` so evidence rows can cite existing formats.

## Workflow

- Identify whether the skill or feature in scope is specialist (declares evidence) or baseline/process (does not).
- For specialist skills: map each artifact the skill produces to one of the seven evidence categories.
- For releases: produce a Release Evidence Bundle that links concrete artifacts under each of the seven categories, using `N/A — <reason>` only where an entire category legitimately does not apply.
- Cross-check risk tier guidance before permitting any `N/A` in high-risk releases.

## Quality Standards

- Every specialist skill that produces validation evidence declares at least one evidence category with a concrete artifact reference.
- Evidence declarations cite existing artifact templates where possible instead of inventing new formats.
- Release Evidence Bundles never carry empty cells. Every cell links evidence or carries an `N/A — <reason>` line.

## Anti-Patterns

- Declaring every category on every skill "just in case". This kills the signal.
- Writing prose validation notes instead of linking concrete artifacts in a Release Evidence Bundle.
- Permitting unjustified `N/A` on Correctness, Security, Data safety, Operability, or Release evidence in high-risk releases.
- Treating the Release Evidence Bundle as a retrospective summary written after ship. It is produced before ship.

## Outputs

- A specialist skill with a validated `## Evidence Produced` section declaring one or more of the seven categories.
- A Release Evidence Bundle in the project's `docs/` tree linking evidence for every applicable category at ship time.
- Clear `N/A — <reason>` annotations for non-applicable categories, with risk-tier-aware justification.

## References

- [references/evidence-categories.md](references/evidence-categories.md): per-category definition, indicative contributing skills, and common artifact shapes.
- [references/declaration-form.md](references/declaration-form.md): the `## Evidence Produced` table form, rules, and worked examples.
- [references/release-evidence-bundle-template.md](references/release-evidence-bundle-template.md): the canonical fillable Release Evidence Bundle.
- [references/integration-rollout.md](references/integration-rollout.md): audit trail of edits made to other skills during this skill's rollout.
<!-- dual-compat-end -->

## The three repository-wide contracts

The repository is held together by three contracts, each codified in a baseline skill:

1. **House-style contract** — every skill follows the same shape. Source: `skill-composition-standards`, Standard 1.
2. **Inputs/Outputs contract** — every skill declares the artifacts it consumes and produces. Source: `skill-composition-standards`, Standard 2.
3. **Evidence contract** — every specialist skill declares which of seven fixed validation categories its artifacts contribute to, and every release produces a Release Evidence Bundle. Source: this skill.

The three contracts stack. A skill that meets Standard 1 but skips Standard 2 or 3 is not repository-grade.

## The seven evidence categories

| # | Category | What the evidence proves |
|---|----------|--------------------------|
| 1 | **Correctness** | Behaviour matches spec; tests cover risk surface; contracts hold. |
| 2 | **Security** | Threat model exists; scans clean; secrets handled; auth/authorisation verified. |
| 3 | **Data safety** | Schema integrity; migration safety; backup, retention, and PII handling. |
| 4 | **Performance** | Budgets met; load profile understood; query plans acceptable. |
| 5 | **Operability** | SLOs defined; runbook exists; observability wired; rollback plan ready. |
| 6 | **UX quality** | Accessibility pass; design audit; content/UX-writing review; AI slop check. |
| 7 | **Release evidence** | Change record; migration plan; rollout/rollback log; post-deploy verification. |

The taxonomy is closed. Adding an eighth category requires editing this skill, not silently extending it elsewhere. Full definitions and indicative contributing skills live in [references/evidence-categories.md](references/evidence-categories.md).

## Declaration mechanic

Specialist skills add a `## Evidence Produced` section to their `SKILL.md`, between `## Outputs` and `## References`:

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Threat model | Markdown doc per `skill-composition-standards/references/threat-model-template.md` | `docs/security/threat-model-checkout.md` |
| Operability | Runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` | `docs/runbooks/payment-failures.md` |
```

### Rules

- A specialist skill that produces validation evidence **MUST** declare at least one row.
- Each row's `Category` value **MUST** be one of the seven canonical names (case-sensitive).
- Each row's `Format` field **MUST** reference an existing template or define its own format inline in the same `SKILL.md`.
- A specialist skill **MAY** contribute to multiple categories.
- Baseline skills, process skills, and pure index/orchestration skills **MUST NOT** declare.

Worked examples live in [references/declaration-form.md](references/declaration-form.md).

## Specialist vs exempt skills

A skill is "specialist" for the purposes of this contract when it:

- Produces concrete project artifacts (code patterns, schemas, configs, documents).
- Is loaded for a specific domain or platform problem rather than as a baseline frame.

Skills exempt from declaring (non-exhaustive):

- `world-class-engineering`, `skill-composition-standards`, `validation-contract` itself.
- `system-architecture-design`, `engineering-management-system`, `git-collaboration-workflow`.
- `feature-planning`, `spec-architect`.
- All `superpowers:*` skills.

When a skill straddles the line, the default is **declare**. False positives are cheaper than silent omissions.

## The Release Evidence Bundle

When a feature or release is ready to ship, the reviewer produces a single fillable document — the Release Evidence Bundle — that links to the concrete artifacts satisfying each of the seven categories.

- **Template:** [references/release-evidence-bundle-template.md](references/release-evidence-bundle-template.md).
- **`N/A` semantics:** permitted **only with a reason on the same line**. An empty cell is not acceptable.
- **Risk tier guidance:**
  - **Low risk** — internal tools, docs, non-user-facing scripts. Typical bundle has 3-4 categories live.
  - **Medium risk** — user-facing feature, single-tenant. All 7 categories addressed; some may be `N/A` with reason.
  - **High risk** — multi-tenant data, payments, auth, external APIs, AI features. All 7 categories live; no `N/A` permitted on Correctness, Security, Data safety, Operability, or Release evidence.

## Strictness

- The contract uses **MUST**, **MAY**, **MUST NOT** in the RFC 2119 sense.
- Mechanical enforcement is **out of scope** for this skill. It lands separately as a CI contract-gate hook that will:
  - parse `## Evidence Produced` tables and warn on missing or invalid categories.
  - parse Release Evidence Bundles and warn on empty cells or unjustified `N/A`.
- Authoring with binding language now means the CI hook is a parser and CI integration only, not a policy debate.

## Integration with existing skills

The rollout in [references/integration-rollout.md](references/integration-rollout.md) lists every edit made to other skills when this skill was introduced. Future edits that touch this contract should update that file.

## Companion Skills

- `skill-composition-standards` — Standards 1 and 2. Load this before `validation-contract`.
- `world-class-engineering` — repository production-readiness bar. This contract makes the evidence of meeting that bar a first-class artifact.
- Category-specific skills — the source of truth for *how* to validate within each category (see [references/evidence-categories.md](references/evidence-categories.md)).
````

- [ ] **Step 3: Run validator**

Run: `cd C:/Users/BIRDC/.claude/skills && python -X utf8 skill-writing/scripts/quick_validate.py validation-contract`
Expected: exit code 0 with no errors. If errors appear, fix them in `validation-contract/SKILL.md` and re-run until green.

---

### Task 2: Create `references/evidence-categories.md`

**Files:**
- Create: `validation-contract/references/evidence-categories.md`

- [ ] **Step 1: Write the file**

Use the Write tool to create `C:/Users/BIRDC/.claude/skills/validation-contract/references/evidence-categories.md` with the following content:

````markdown
# Evidence Categories

The seven categories are fixed. Each entry below gives the full definition, what artifacts typically satisfy it, which skills contribute, and the common failure mode.

## 1. Correctness

**What the evidence proves:** The feature's observable behaviour matches the specification across the risk surface. Tests cover the paths that matter, contracts hold under change, and regressions would be caught before ship.

**Typical artifacts:**
- Test plan document listing scenarios, risk tier, and coverage strategy.
- Latest CI run link showing unit, integration, and contract tests passing.
- Contract test output for API or data-schema stability.

**Indicative contributing skills:** `advanced-testing-strategy`, `api-testing-verification`, `android-tdd`, `ios-tdd`, `kmp-tdd`.

**Common failure mode:** Test count is high but coverage skews to happy paths; risky boundaries and error paths are untested.

## 2. Security

**What the evidence proves:** The feature's threat surface has been reasoned about, scanned, and hardened. Authentication, authorisation, secrets handling, and input validation are designed rather than assumed.

**Typical artifacts:**
- Threat model document naming actors, assets, and mitigations.
- SAST, DAST, and dependency scan outputs.
- Secrets-handling note explaining where credentials are stored and rotated.

**Indicative contributing skills:** `vibe-security-skill`, `web-app-security-audit`, `php-security`, `ios-app-security`, `llm-security`, `cicd-devsecops`.

**Common failure mode:** Scan report exists but the threat model was never written, so the scan findings are not prioritised against actual risk.

## 3. Data safety

**What the evidence proves:** Data schema changes are safe to deploy, backups are verified, retention policies are in place, and PII is handled per regulation.

**Typical artifacts:**
- Migration plan document with backward-compatibility notes and rollback steps.
- Backup verification log (most recent restore test).
- PII and retention note mapping personal data fields to regulatory basis and retention window.

**Indicative contributing skills:** `database-design-engineering`, `postgresql-administration`, `mysql-administration`, `dpia-generator`, `uganda-dppa-compliance`.

**Common failure mode:** Migration is irreversible (dropped column, destructive type change) with no feature-flag gate, forcing a full release rollback instead of a feature rollback.

## 4. Performance

**What the evidence proves:** The feature meets agreed performance budgets under expected load, and the hot paths have been measured, not assumed.

**Typical artifacts:**
- Performance budget document listing page, API, or job budgets.
- Load test or production-trace evidence showing the budget is met.
- Query plan review for new or changed database queries.

**Indicative contributing skills:** `frontend-performance`, `mysql-query-performance`, `postgresql-performance`.

**Common failure mode:** Local benchmarks exist but no production-shape load was run, and the feature silently degrades a shared endpoint under real traffic.

## 5. Operability

**What the evidence proves:** The feature is safe to run in production. SLOs exist, a human on-call can diagnose problems without calling the author, and rolling back is routine rather than heroic.

**Typical artifacts:**
- SLO record stating the agreed service-level objective and its measurement.
- Runbook covering the top failure modes with diagnosis and remediation steps.
- Observability wiring evidence (logs, metrics, traces present and searchable).
- Rollback plan.

**Indicative contributing skills:** `observability-monitoring`, `reliability-engineering`, `database-reliability`.

**Common failure mode:** Logs are emitted but dashboards and alerts were never wired, so regressions are detected by customers rather than by the team.

## 6. UX quality

**What the evidence proves:** The user-facing surface has been reviewed for usability, accessibility, tone, and visual coherence.

**Typical artifacts:**
- Design audit report against the repository's UX standards.
- Accessibility pass (WCAG conformance check).
- Content / UX-writing review for microcopy.
- AI slop check for features that display AI-generated UI.

**Indicative contributing skills:** `design-audit`, `ux-writing`, `ai-slop-prevention`, `cognitive-ux-framework`.

**Common failure mode:** Visual review is done but accessibility, tone, and AI-slop checks are skipped, and the feature ships with keyboard-trap bugs or generic AI copy.

## 7. Release evidence

**What the evidence proves:** The deployment itself was planned, executed, and verified. If something had gone wrong, the team could have backed out without data loss.

**Typical artifacts:**
- Change record (PR range, tagged commit, release notes).
- Migration and rollout plan.
- Post-deploy verification log.
- Rollback plan and any rollback drill evidence.

**Indicative contributing skills:** `deployment-release-engineering`, `sdlc-post-deployment`, `git-collaboration-workflow`.

**Common failure mode:** Release notes exist but no post-deploy verification was recorded, so a partial outage goes unnoticed until a customer reports it.
````

- [ ] **Step 2: Confirm file created and under the 500-line limit**

Run: `wc -l C:/Users/BIRDC/.claude/skills/validation-contract/references/evidence-categories.md`
Expected: line count > 70 and < 500.

---

### Task 3: Create `references/declaration-form.md`

**Files:**
- Create: `validation-contract/references/declaration-form.md`

- [ ] **Step 1: Write the file**

Use the Write tool to create `C:/Users/BIRDC/.claude/skills/validation-contract/references/declaration-form.md` with:

````markdown
# Declaration Form — `## Evidence Produced`

Every specialist skill that produces validation evidence adds this section to its `SKILL.md`, placed between `## Outputs` and `## References`.

## Canonical form

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Threat model | Markdown doc per `skill-composition-standards/references/threat-model-template.md` | `docs/security/threat-model-checkout.md` |
```

## Column semantics

- **Category** — one of the seven canonical names: `Correctness`, `Security`, `Data safety`, `Performance`, `Operability`, `UX quality`, `Release evidence`. Case-sensitive.
- **Artifact** — the concrete thing the skill produces. Noun phrase, not verb.
- **Format** — either a pointer to an existing template (preferred) or a short inline description. Examples of existing templates: `skill-composition-standards/references/threat-model-template.md`, `skill-composition-standards/references/runbook-template.md`, `skill-composition-standards/references/migration-plan-template.md`.
- **Example** — a realistic path showing where the artifact would live in a project repository.

## Worked example 1 — `advanced-testing-strategy`

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Test plan | Markdown doc per `skill-composition-standards/references/test-plan-template.md` | `docs/testing/test-plan-checkout.md` |
| Correctness | Latest CI run evidence | CI URL or archived log | `https://ci.example.com/run/12345` |
```

## Worked example 2 — `vibe-security-skill`

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Threat model | Markdown doc per `skill-composition-standards/references/threat-model-template.md` | `docs/security/threat-model-checkout.md` |
| Security | Abuse-case catalogue | Markdown doc listing misuse scenarios | `docs/security/abuse-cases-checkout.md` |
```

## Worked example 3 — `observability-monitoring` (multi-category)

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | SLO record | Markdown doc per `skill-composition-standards/references/slo-template.md` | `docs/slo/checkout-service.md` |
| Operability | Runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` | `docs/runbooks/checkout-latency.md` |
| Release evidence | Post-deploy verification log | Markdown doc or CI artifact | `docs/releases/2026-04-16-verify.md` |
```

## Common mistakes

- **Declaring every category.** The signal dies when a skill claims to produce evidence for six categories. Pick the categories where the skill actually produces the artifact.
- **Skipping the Format column.** The template pointer is how reviewers know what a "Threat model" should look like. Free-form artifacts without a format pointer are harder to mechanise.
- **Using a category synonym.** `Safety` is not a category. `Reliability` is not a category. Use the exact canonical names.
- **Vague Example paths.** `docs/file.md` is not a useful example. Use a realistic feature-named path.
````

- [ ] **Step 2: Confirm**

Run: `wc -l C:/Users/BIRDC/.claude/skills/validation-contract/references/declaration-form.md`
Expected: line count > 40 and < 500.

---

### Task 4: Create `references/release-evidence-bundle-template.md`

**Files:**
- Create: `validation-contract/references/release-evidence-bundle-template.md`

- [ ] **Step 1: Write the file**

Use the Write tool to create `C:/Users/BIRDC/.claude/skills/validation-contract/references/release-evidence-bundle-template.md` with:

````markdown
# Release Evidence Bundle — Template

Copy this file into the consuming project as `docs/releases/YYYY-MM-DD-<feature>-evidence.md` and fill every row before declaring the release ready.

---

# Release Evidence Bundle — <feature or release name>

- **Date:** YYYY-MM-DD
- **Owner:** <name>
- **Scope:** <one-line description of what is shipping>
- **Risk tier:** <low | medium | high>

## 1. Correctness

- Test plan: <link or `N/A — reason`>
- Latest CI run: <link>
- Contract tests (API/data): <link or `N/A — reason`>

## 2. Security

- Threat model: <link or `N/A — reason`>
- Scan output (SAST/DAST/dependency): <link or `N/A — reason`>
- Secrets handling note: <link or `N/A — reason`>

## 3. Data safety

- Migration plan: <link or `N/A — no schema changes`>
- Backup verification: <link or `N/A — reason`>
- PII / retention note: <link or `N/A — reason`>

## 4. Performance

- Performance budget evidence: <link or `N/A — non-performance-sensitive`>
- Load profile / query plan review: <link or `N/A — reason`>

## 5. Operability

- SLO record: <link or `N/A — reason`>
- Runbook: <link or `N/A — reason`>
- Observability wiring (logs/metrics/traces): <link or `N/A — reason`>
- Rollback plan: <link or `N/A — reason`>

## 6. UX quality

- Design audit: <link or `N/A — no UI surface`>
- Accessibility pass: <link or `N/A — no UI surface`>
- Content / UX-writing review: <link or `N/A — no user-facing copy`>
- AI slop check: <link or `N/A — no AI-generated UI`>

## 7. Release evidence

- Change record (PR / commit range): <link>
- Rollout plan: <link or `N/A — reason`>
- Post-deploy verification: <link or `N/A — reason`>

---

## N/A semantics

- `N/A` is permitted **only with a reason on the same line**.
- An empty cell is not acceptable.
- At **high risk tier**, `N/A` is never permitted on Correctness, Security, Data safety, Operability, or Release evidence.

## Sign-off

- Owner: <name, date>
- Reviewer: <name, date>
````

- [ ] **Step 2: Confirm**

Run: `wc -l C:/Users/BIRDC/.claude/skills/validation-contract/references/release-evidence-bundle-template.md`
Expected: line count > 40 and < 500.

---

### Task 5: Create `references/integration-rollout.md`

**Files:**
- Create: `validation-contract/references/integration-rollout.md`

- [ ] **Step 1: Write the file**

Use the Write tool to create `C:/Users/BIRDC/.claude/skills/validation-contract/references/integration-rollout.md` with:

````markdown
# Integration Rollout — Audit Trail

This file records every edit made to other skills and repository documents when `validation-contract` was introduced on 2026-04-16. Future edits that touch this contract should append to this file.

## Baseline skills

- `world-class-engineering/SKILL.md` — added a closing line under `## Companion Skills` pointing at `validation-contract` as the canonical release-evidence contract.
- `skill-composition-standards/SKILL.md` — added a paragraph under `## Standard 2 — Input/Output Contracts` naming `validation-contract` as the third contract dimension.

## Repository documents

- `CLAUDE.md` — added `validation-contract` to the Key Baseline Skills section.
- `README.md` — single-line addition in the baseline-skills listing.
- `PROJECT_BRIEF.md` — single-line addition in the baseline-skills listing.

## Specialist skills with `## Evidence Produced` sections added in this pass

Sixteen directly-validating specialist skills gained `## Evidence Produced` sections:

- Correctness: `advanced-testing-strategy`, `api-testing-verification`
- Security: `vibe-security-skill`, `web-app-security-audit`, `llm-security`, `cicd-devsecops`
- Data safety: `database-design-engineering`, `dpia-generator`
- Performance: `frontend-performance`
- Operability: `observability-monitoring`, `reliability-engineering`
- UX quality: `design-audit`, `ux-writing`, `ai-slop-prevention`
- Release evidence: `deployment-release-engineering`, `sdlc-post-deployment`

## Deferred

- Remaining ~150 specialist skills — receive `## Evidence Produced` sections as part of the repository-wide normalisation rollout (tracked separately).
- Mechanical enforcement — tracked separately as a CI contract-gate hook that parses both the Inputs/Outputs tables (from `skill-composition-standards`) and the Evidence Produced tables defined here.
````

- [ ] **Step 2: Confirm**

Run: `wc -l C:/Users/BIRDC/.claude/skills/validation-contract/references/integration-rollout.md`
Expected: line count > 20 and < 500.

---

### Task 6: Validate the new skill end-to-end

- [ ] **Step 1: Run the validator on validation-contract**

Run: `cd C:/Users/BIRDC/.claude/skills && python -X utf8 skill-writing/scripts/quick_validate.py validation-contract`
Expected: exit code 0, no errors.

- [ ] **Step 2: Confirm file structure**

Run: `ls C:/Users/BIRDC/.claude/skills/validation-contract/ && echo "---" && ls C:/Users/BIRDC/.claude/skills/validation-contract/references/`
Expected output (in any order):
```
SKILL.md
references
---
declaration-form.md
evidence-categories.md
integration-rollout.md
release-evidence-bundle-template.md
```

- [ ] **Step 3: Commit Phase 1**

```bash
cd C:/Users/BIRDC/.claude/skills
git add validation-contract/
git commit -m "$(cat <<'EOF'
feat: add validation-contract baseline skill

Third repository-wide contract alongside skill-composition-standards.
Defines seven fixed evidence categories (Correctness, Security, Data
safety, Performance, Operability, UX quality, Release evidence) that
every specialist skill declares against, plus the canonical Release
Evidence Bundle template for shipping.

Normative but unenforced. Mechanical enforcement will land as a
separate CI contract-gate hook.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: commit succeeds, no pre-commit hook failures.

---

## Phase 2 — Baseline integration

### Task 7: Cross-reference in `world-class-engineering/SKILL.md`

**Files:**
- Modify: `world-class-engineering/SKILL.md`

- [ ] **Step 1: Confirm current content of the Companion Skills section**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "Companion Skills" world-class-engineering/SKILL.md`
Expected: one line number of a `## Companion Skills` heading.

- [ ] **Step 2: Add the cross-reference**

Use the Edit tool with:
- `old_string` = `- Load platform and security skills relevant to the stack after this baseline is established.`
- `new_string` = `- Load platform and security skills relevant to the stack after this baseline is established.\n- Load \`validation-contract\` when authoring a specialist skill or assembling a Release Evidence Bundle for ship; it is the canonical source for what evidence ship-readiness requires.`

(Use the literal newline character in the tool, not the escape sequence.)

- [ ] **Step 3: Verify the edit**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "validation-contract" world-class-engineering/SKILL.md`
Expected: one match under Companion Skills.

- [ ] **Step 4: Validate**

Run: `cd C:/Users/BIRDC/.claude/skills && python -X utf8 skill-writing/scripts/quick_validate.py world-class-engineering`
Expected: exit code 0.

---

### Task 8: Cross-reference in `skill-composition-standards/SKILL.md`

**Files:**
- Modify: `skill-composition-standards/SKILL.md`

- [ ] **Step 1: Locate the Standard 2 section**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "Standard 2" skill-composition-standards/SKILL.md`
Expected: at least one line number.

- [ ] **Step 2: Read the current ending of the Standard 2 section to find the exact anchor for insertion**

Run: `cd C:/Users/BIRDC/.claude/skills && sed -n '141,160p' skill-composition-standards/SKILL.md`
Expected: the full text from the `## Standard 2 — Input/Output Contracts` heading down through its first subsection; use the last line of the Standard 2 summary paragraph as the `old_string` anchor in the next step.

- [ ] **Step 3: Insert the third-contract paragraph**

Use the Edit tool to add a paragraph under the Standard 2 summary. The `old_string` is the first sentence under `## Standard 2 — Input/Output Contracts`; the `new_string` is that same sentence followed by a blank line and:

```markdown
Beyond Inputs and Outputs, specialist skills also declare which of seven fixed validation categories their artifacts contribute to. That third contract lives in `validation-contract`; it turns scattered validation skills into a coherent ship-readiness check and produces the canonical Release Evidence Bundle at release time.
```

If the exact sentence cannot be located, add the paragraph immediately before the first `## Inputs` subsection by using that heading as the anchor and prepending the paragraph plus a blank line.

- [ ] **Step 4: Verify and validate**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "validation-contract" skill-composition-standards/SKILL.md && python -X utf8 skill-writing/scripts/quick_validate.py skill-composition-standards`
Expected: one match and validator exit code 0.

---

### Task 9: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Locate the Key Baseline Skills section**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "skill-composition-standards" CLAUDE.md`
Expected: at least one line mentioning `skill-composition-standards - house-style template`.

- [ ] **Step 2: Insert the validation-contract line**

Use the Edit tool with:
- `old_string` = `` - `skill-composition-standards` - house-style template, cross-skill I/O contracts, 14 canonical artifact templates ``
- `new_string` = `` - `skill-composition-standards` - house-style template, cross-skill I/O contracts, 14 canonical artifact templates
- `validation-contract` - seven evidence categories, Release Evidence Bundle, the third repository-wide contract ``

- [ ] **Step 3: Verify**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "validation-contract" CLAUDE.md`
Expected: one match.

---

### Task 10: Update `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Confirm README structure**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "skill-composition-standards" README.md`
Expected: at least one match; note the line and surrounding context so the new line follows the same formatting.

- [ ] **Step 2: Add the line**

Use the Edit tool to insert a single-line mention of `validation-contract` immediately after the `skill-composition-standards` entry in the baseline-skills list. Match the surrounding bullet style exactly.

- [ ] **Step 3: Verify**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "validation-contract" README.md`
Expected: one match.

---

### Task 11: Update `PROJECT_BRIEF.md`

**Files:**
- Modify: `PROJECT_BRIEF.md`

- [ ] **Step 1: Confirm structure**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "skill-composition-standards" PROJECT_BRIEF.md`
Expected: at least one match.

- [ ] **Step 2: Add the line**

Use the Edit tool to insert a single-line mention of `validation-contract` immediately after the `skill-composition-standards` entry, matching the surrounding bullet style exactly.

- [ ] **Step 3: Verify**

Run: `cd C:/Users/BIRDC/.claude/skills && grep -n "validation-contract" PROJECT_BRIEF.md`
Expected: one match.

---

### Task 12: Commit Phase 2

- [ ] **Step 1: Review staged changes**

Run: `cd C:/Users/BIRDC/.claude/skills && git status && git diff --stat`
Expected: five modified files (world-class-engineering/SKILL.md, skill-composition-standards/SKILL.md, CLAUDE.md, README.md, PROJECT_BRIEF.md).

- [ ] **Step 2: Commit**

```bash
cd C:/Users/BIRDC/.claude/skills
git add world-class-engineering/SKILL.md skill-composition-standards/SKILL.md CLAUDE.md README.md PROJECT_BRIEF.md
git commit -m "$(cat <<'EOF'
feat: wire validation-contract into baseline skills and repo docs

Adds cross-references from world-class-engineering and
skill-composition-standards to validation-contract, and lists the new
skill in CLAUDE.md, README.md, and PROJECT_BRIEF.md.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: commit succeeds.

---

## Phase 3 — Specialist declarations

Each task in this phase adds a `## Evidence Produced` section to the target skill's `SKILL.md`, placed between `## Outputs` and `## References`. Use this insertion procedure for every skill:

1. Locate the skill's `## Outputs` and `## References` lines.
2. Confirm there is currently no `## Evidence Produced` section (grep for it; expect zero matches).
3. Insert the section with the category rows specified in the task.
4. Run the validator on the skill.

The table template for every insertion:

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| <CATEGORY> | <ARTIFACT> | <FORMAT> | <EXAMPLE> |
```

### Task 13: Add Evidence Produced to Correctness skills

**Files:**
- Modify: `advanced-testing-strategy/SKILL.md`
- Modify: `api-testing-verification/SKILL.md`

- [ ] **Step 1: Insert in `advanced-testing-strategy/SKILL.md`**

Add between `## Outputs` and `## References`:

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Test plan | Markdown doc per `skill-composition-standards/references/test-plan-template.md` | `docs/testing/test-plan-checkout.md` |
| Correctness | Latest CI run evidence | CI URL or archived log | `https://ci.example.com/run/12345` |
```

- [ ] **Step 2: Insert in `api-testing-verification/SKILL.md`**

Add between `## Outputs` and `## References`:

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | API contract test output | CI log or recorded test report | `docs/testing/api-contract-2026-04-16.md` |
| Correctness | Endpoint verification checklist | Markdown doc listing verified endpoints and methods | `docs/testing/api-verified-endpoints.md` |
```

- [ ] **Step 3: Validate both**

Run: `cd C:/Users/BIRDC/.claude/skills && python -X utf8 skill-writing/scripts/quick_validate.py advanced-testing-strategy && python -X utf8 skill-writing/scripts/quick_validate.py api-testing-verification`
Expected: both exit 0.

---

### Task 14: Add Evidence Produced to Security skills

**Files:**
- Modify: `vibe-security-skill/SKILL.md`
- Modify: `web-app-security-audit/SKILL.md`
- Modify: `llm-security/SKILL.md`
- Modify: `cicd-devsecops/SKILL.md`

- [ ] **Step 1: `vibe-security-skill/SKILL.md`**

Insert between Outputs and References:

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Threat model | Markdown doc per `skill-composition-standards/references/threat-model-template.md` | `docs/security/threat-model-checkout.md` |
| Security | Abuse-case catalogue | Markdown doc listing misuse scenarios and mitigations | `docs/security/abuse-cases-checkout.md` |
```

- [ ] **Step 2: `web-app-security-audit/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Web application audit report | Markdown doc covering config, auth, input validation, and session handling findings | `docs/security/web-audit-2026-04-16.md` |
| Security | Remediation plan | Markdown doc listing findings, owners, and due dates | `docs/security/web-remediation-2026-04-16.md` |
```

- [ ] **Step 3: `llm-security/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | LLM threat model | Markdown doc covering prompt injection, data exfiltration, and output-handling risks | `docs/security/llm-threat-model-assistant.md` |
| Security | Prompt-injection test suite results | CI log or archived test report | `docs/security/llm-injection-tests-2026-04-16.md` |
```

- [ ] **Step 4: `cicd-devsecops/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Pipeline security gate configuration | YAML or JSON defining SAST/DAST/dependency/secret scan steps | `.github/workflows/security.yml` |
| Security | Scan-exception register | Markdown doc listing accepted findings, owner, and expiry | `docs/security/scan-exceptions.md` |
| Release evidence | Signed build and provenance record | SBOM plus signature or attestation output | `artifacts/sbom-2026-04-16.spdx.json` |
```

- [ ] **Step 5: Validate all four**

Run:
```bash
cd C:/Users/BIRDC/.claude/skills
for s in vibe-security-skill web-app-security-audit llm-security cicd-devsecops; do
  python -X utf8 skill-writing/scripts/quick_validate.py "$s" || echo "FAIL: $s"
done
```
Expected: no `FAIL` lines.

---

### Task 15: Add Evidence Produced to Data safety, Performance, and Operability skills

**Files:**
- Modify: `database-design-engineering/SKILL.md`
- Modify: `dpia-generator/SKILL.md`
- Modify: `frontend-performance/SKILL.md`
- Modify: `observability-monitoring/SKILL.md`
- Modify: `reliability-engineering/SKILL.md`

- [ ] **Step 1: `database-design-engineering/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Data safety | Migration plan | Markdown doc per `skill-composition-standards/references/migration-plan-template.md` | `docs/data/migration-2026-04-16-add-tenant-column.md` |
| Data safety | Entity model | Markdown doc per `skill-composition-standards/references/entity-model-template.md` | `docs/data/entity-model-billing.md` |
| Data safety | Access pattern register | Markdown doc per `skill-composition-standards/references/access-patterns-template.md` | `docs/data/access-patterns-billing.md` |
```

- [ ] **Step 2: `dpia-generator/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Data safety | Data Protection Impact Assessment | Markdown doc covering lawful basis, data flows, risks, and mitigations | `docs/compliance/dpia-customer-onboarding.md` |
| Data safety | PII / retention register | Markdown doc mapping personal data fields to basis and retention window | `docs/compliance/pii-retention-register.md` |
```

- [ ] **Step 3: `frontend-performance/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Performance | Performance budget document | Markdown doc stating page, API, and interaction budgets | `docs/performance/budgets-checkout.md` |
| Performance | Real-user and synthetic metrics evidence | Dashboard link plus archived snapshot | `docs/performance/rum-snapshot-2026-04-16.md` |
```

- [ ] **Step 4: `observability-monitoring/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | SLO record | Markdown doc per `skill-composition-standards/references/slo-template.md` | `docs/slo/checkout-service.md` |
| Operability | Observability wiring note | Markdown doc listing logs, metrics, traces, and dashboards wired | `docs/observability/checkout-wiring.md` |
| Operability | Alert catalogue | Markdown doc listing alert name, threshold, and runbook link | `docs/observability/checkout-alerts.md` |
```

- [ ] **Step 5: `reliability-engineering/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` | `docs/runbooks/payment-failures.md` |
| Operability | Rollback plan | Markdown doc per `skill-composition-standards/references/rollback-plan-template.md` | `docs/releases/2026-04-16-rollback.md` |
| Operability | Failure-mode catalogue | Markdown doc listing known failure modes and mitigations | `docs/reliability/failure-modes-checkout.md` |
```

- [ ] **Step 6: Validate all five**

Run:
```bash
cd C:/Users/BIRDC/.claude/skills
for s in database-design-engineering dpia-generator frontend-performance observability-monitoring reliability-engineering; do
  python -X utf8 skill-writing/scripts/quick_validate.py "$s" || echo "FAIL: $s"
done
```
Expected: no `FAIL` lines.

---

### Task 16: Add Evidence Produced to UX quality and Release evidence skills

**Files:**
- Modify: `design-audit/SKILL.md`
- Modify: `ux-writing/SKILL.md`
- Modify: `ai-slop-prevention/SKILL.md`
- Modify: `deployment-release-engineering/SKILL.md`
- Modify: `sdlc-post-deployment/SKILL.md`

- [ ] **Step 1: `design-audit/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Design audit report | Markdown doc covering visual hierarchy, typography, spacing, colour, and accessibility findings | `docs/ux/design-audit-checkout.md` |
| UX quality | Accessibility pass report | Markdown doc summarising WCAG conformance | `docs/ux/a11y-checkout.md` |
```

- [ ] **Step 2: `ux-writing/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Content and microcopy review | Markdown doc reviewing button labels, errors, empty states, and confirmations | `docs/ux/content-review-checkout.md` |
```

- [ ] **Step 3: `ai-slop-prevention/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | AI slop check report | Markdown doc flagging generic typography, colour, layout, and motion anti-patterns in AI-generated UI | `docs/ux/ai-slop-check-checkout.md` |
```

- [ ] **Step 4: `deployment-release-engineering/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Release plan | Markdown doc per `skill-composition-standards/references/release-plan-template.md` | `docs/releases/2026-04-16-release-plan.md` |
| Release evidence | Rollback plan | Markdown doc per `skill-composition-standards/references/rollback-plan-template.md` | `docs/releases/2026-04-16-rollback-plan.md` |
| Release evidence | Change record | PR range or tagged commit list | `docs/releases/2026-04-16-change-record.md` |
```

- [ ] **Step 5: `sdlc-post-deployment/SKILL.md`**

```markdown
## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Post-Deployment Evaluation Report | Markdown doc covering deploy outcome, KPIs, and remediation actions | `docs/releases/pder-2026-04-16.md` |
| Release evidence | Post-deploy verification log | Markdown doc or CI artifact listing checks run and results | `docs/releases/verify-2026-04-16.md` |
```

- [ ] **Step 6: Validate all five**

Run:
```bash
cd C:/Users/BIRDC/.claude/skills
for s in design-audit ux-writing ai-slop-prevention deployment-release-engineering sdlc-post-deployment; do
  python -X utf8 skill-writing/scripts/quick_validate.py "$s" || echo "FAIL: $s"
done
```
Expected: no `FAIL` lines.

---

### Task 17: Commit Phase 3

- [ ] **Step 1: Review staged changes**

Run: `cd C:/Users/BIRDC/.claude/skills && git status && git diff --stat`
Expected: 16 modified files (one per specialist skill).

- [ ] **Step 2: Sanity-check every edited skill has exactly one Evidence Produced section**

Run:
```bash
cd C:/Users/BIRDC/.claude/skills
for s in advanced-testing-strategy api-testing-verification vibe-security-skill web-app-security-audit llm-security cicd-devsecops database-design-engineering dpia-generator frontend-performance observability-monitoring reliability-engineering design-audit ux-writing ai-slop-prevention deployment-release-engineering sdlc-post-deployment; do
  count=$(grep -c "^## Evidence Produced" "$s/SKILL.md")
  if [ "$count" != "1" ]; then echo "FAIL: $s has $count Evidence Produced sections"; fi
done
```
Expected: no `FAIL` lines.

- [ ] **Step 3: Commit**

```bash
cd C:/Users/BIRDC/.claude/skills
git add advanced-testing-strategy/SKILL.md api-testing-verification/SKILL.md vibe-security-skill/SKILL.md web-app-security-audit/SKILL.md llm-security/SKILL.md cicd-devsecops/SKILL.md database-design-engineering/SKILL.md dpia-generator/SKILL.md frontend-performance/SKILL.md observability-monitoring/SKILL.md reliability-engineering/SKILL.md design-audit/SKILL.md ux-writing/SKILL.md ai-slop-prevention/SKILL.md deployment-release-engineering/SKILL.md sdlc-post-deployment/SKILL.md
git commit -m "$(cat <<'EOF'
feat: declare Evidence Produced in 16 directly-validating specialist skills

Adds the `## Evidence Produced` section defined by validation-contract
to the canonical contributors for all seven evidence categories. The
remaining ~150 specialist skills receive their declarations in the
repository-wide normalisation rollout.

Skills updated:
- Correctness: advanced-testing-strategy, api-testing-verification
- Security: vibe-security-skill, web-app-security-audit, llm-security,
  cicd-devsecops
- Data safety: database-design-engineering, dpia-generator
- Performance: frontend-performance
- Operability: observability-monitoring, reliability-engineering
- UX quality: design-audit, ux-writing, ai-slop-prevention
- Release evidence: deployment-release-engineering, sdlc-post-deployment

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: commit succeeds.

---

## Phase 4 — Acceptance check

### Task 18: End-to-end acceptance

- [ ] **Step 1: Run validator across every affected skill**

Run:
```bash
cd C:/Users/BIRDC/.claude/skills
for s in validation-contract world-class-engineering skill-composition-standards advanced-testing-strategy api-testing-verification vibe-security-skill web-app-security-audit llm-security cicd-devsecops database-design-engineering dpia-generator frontend-performance observability-monitoring reliability-engineering design-audit ux-writing ai-slop-prevention deployment-release-engineering sdlc-post-deployment; do
  python -X utf8 skill-writing/scripts/quick_validate.py "$s" || echo "FAIL: $s"
done
```
Expected: no `FAIL` lines.

- [ ] **Step 2: Confirm every acceptance criterion from the spec**

- [ ] `validation-contract/` directory exists with `SKILL.md` and four reference files. Verify with `ls validation-contract validation-contract/references`.
- [ ] Validator passes on `validation-contract`. Verified in step 1.
- [ ] Sixteen directly-validating specialist skills carry `## Evidence Produced` tables. Verify with the loop from Task 17 Step 2.
- [ ] `world-class-engineering/SKILL.md` and `skill-composition-standards/SKILL.md` cross-reference `validation-contract`. Verify with `grep -l "validation-contract" world-class-engineering/SKILL.md skill-composition-standards/SKILL.md`.
- [ ] `CLAUDE.md`, `README.md`, `PROJECT_BRIEF.md` mention `validation-contract`. Verify with `grep -l "validation-contract" CLAUDE.md README.md PROJECT_BRIEF.md`.

- [ ] **Step 3: Review commit history**

Run: `cd C:/Users/BIRDC/.claude/skills && git log --oneline -5`
Expected: the three commits from this plan (Phase 1, Phase 2, Phase 3) on top of the spec commit `e1aa5da`.

- [ ] **Step 4: Report completion**

Summarise:
- Number of files created (5 under `validation-contract/`).
- Number of files modified (5 baseline/doc + 16 specialist = 21).
- Validator status for all 19 touched skills.
- Any deferred items (remaining ~150 specialist declarations → item 1; mechanical enforcement → item 5).

---

## Self-Review Summary

Spec coverage: all thirteen spec sections map to tasks above — Task 1 covers spec §9 (SKILL.md outline) and §8 (frontmatter); Tasks 2–5 cover the four reference files from §7; Tasks 7–11 cover §6 (integration); Tasks 13–16 cover §6.2 (16 specialist skills); Task 18 covers §13 (acceptance criteria).

Placeholders: no `TBD`, `TODO`, `add appropriate X`, or "similar to" references remain.

Type/name consistency: the seven category names (`Correctness`, `Security`, `Data safety`, `Performance`, `Operability`, `UX quality`, `Release evidence`) appear identically in SKILL.md, references, declaration tables, and the Release Evidence Bundle template.
