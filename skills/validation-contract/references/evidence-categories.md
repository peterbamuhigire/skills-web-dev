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
