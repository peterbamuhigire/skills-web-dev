---
name: cicd-devsecops
description: Use when hardening CI/CD pipelines with security gates, secrets management,
  scan policy, exception handling, CI server hardening, and evidence retention for
  self-managed or cloud-hosted delivery systems.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# CI/CD DevSecOps

<!-- dual-compat-start -->
## Use When

- Use when hardening CI/CD pipelines with security gates, secrets management, scan policy, exception handling, CI server hardening, and evidence retention for self-managed or cloud-hosted delivery systems.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `cicd-devsecops` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Use this skill when pipeline security must be systematic, reviewable, and auditable. The goal is not to bolt scanners onto a build. The goal is to manage secrets, trust boundaries, evidence, and exceptions so risky changes do not move silently to production.

## Load Order

1. Load `world-class-engineering`.
2. Load `cicd-pipeline-design` to define the pipeline shape.
3. Load this skill to define security gates, secrets handling, and exception policy.
4. Pair it with `vibe-security-skill`, `deployment-release-engineering`, and `observability-monitoring`.

## Executable Outputs

For meaningful DevSecOps work, produce:

- security gate map by pipeline stage
- secret, identity, and credential flow
- exception and suppression policy
- evidence retention and audit trail plan
- incident and rollback triggers for security gate failures

## DevSecOps Workflow

### 1. Map the Trust Boundaries

Capture:

- source repositories and branch protections
- CI runners, agents, and build nodes
- artifact repositories and signing points
- secret stores and credential consumers
- deployment credentials and target environments
- security evidence that must be retained

### 2. Place Security Gates Deliberately

Typical gates include:

- static analysis and secure-code checks
- dependency and SBOM or package-risk checks
- container or artifact scanning
- dynamic or integration-time security checks
- policy or compliance checks for deployment-critical systems

Choose block, warn, or ticket behavior explicitly for each gate.

### 3. Secure Secrets and Identities

- Keep secrets out of source control and pipeline definitions.
- Prefer a dedicated secret manager with access control and audit trail.
- Use short-lived credentials where supported.
- Define rotation, revocation, and emergency disable procedures for every critical credential path.

### 4. Govern Exceptions and Suppressions

- Every suppression or waiver needs a reason, owner, and review date.
- Keep exceptions visible so teams know the current security posture is degraded.
- Separate false-positive suppression from accepted-risk exception handling.
- Do not let temporary waivers become permanent invisible policy.

### 5. Harden the Delivery Infrastructure

- Restrict access to CI servers, runners, and deployment endpoints.
- Use role-based access control for approval and production deployment actions.
- Protect signing keys, deploy credentials, and artifact repositories as high-trust systems.
- Keep security updates, backups, and audit logs current on CI infrastructure.

### 6. Retain Evidence and Respond

- Keep scan results long enough for incident review and audit.
- Link security findings to the release, artifact, or commit they affect.
- Define which findings block merge, block production, or open tracked follow-up work.
- Escalate rapidly when secrets, signing, or deployment credentials may be compromised.

## Standards

### Gate Policy

- Block on findings that create active release risk on the changed path.
- Warn or ticket on lower-risk findings when immediate stop-the-line action is not justified.
- Make policy severity understandable to engineers and operators.

### Secret Hygiene

- Secrets should be centrally managed, rotated, and auditable.
- Shared long-lived production credentials are a risk to remove, not a stable default.
- Secret access should follow least privilege and environment scoping.

### Exception Governance

- Exceptions are time-bounded unless explicitly renewed.
- Exception records must be reviewable by security and delivery owners.
- Exception policy should not hide whether the release carries unresolved risk.

## Review Checklist

- [ ] Trust boundaries and credential paths are explicit.
- [ ] Security gates are mapped to concrete pipeline stages.
- [ ] Gate behavior distinguishes blockers from advisory findings.
- [ ] Secret rotation, revocation, and ownership are defined.
- [ ] Suppressions and waivers are tracked with owners and review dates.
- [ ] CI and deployment infrastructure are hardened and access-controlled.
- [ ] Security evidence is retained and linked to artifacts or releases.

## References

- [references/security-gate-governance.md](references/security-gate-governance.md): Gate policy, suppression hygiene, and evidence retention.
- [../cicd-pipeline-design/references/pipeline-governance.md](../cicd-pipeline-design/references/pipeline-governance.md): Pipeline governance and trusted delivery rules.
- [../world-class-engineering/references/source-patterns.md](../world-class-engineering/references/source-patterns.md): DevOps and security-adjacent workflow patterns derived from the supplied books.
