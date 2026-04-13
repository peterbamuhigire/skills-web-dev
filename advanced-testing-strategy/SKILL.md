---
name: advanced-testing-strategy
description: Use when designing or reviewing test strategy for production systems,
  APIs, mobile apps, SaaS platforms, ERP workflows, and AI-enabled systems. Covers
  unit, integration, contract, end-to-end, regression, release-gate, and risk-based
  testing decisions.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Advanced Testing Strategy

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing test strategy for production systems, APIs, mobile apps, SaaS platforms, ERP workflows, and AI-enabled systems. Covers unit, integration, contract, end-to-end, regression, release-gate, and risk-based testing decisions.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `advanced-testing-strategy` or would be better handled by a more specific companion skill.
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
Use this skill when testing must be designed as an engineering system rather than appended as a final step. The goal is to match test depth to business risk, failure modes, and release confidence.

## Load Order

1. Load `world-class-engineering`.
2. Load this skill before declaring architecture or implementation work production-ready.
3. Pair it with `deployment-release-engineering` for release gates and `observability-monitoring` for post-deploy verification.

## Testing Workflow

### 1. Identify Risk

Classify the change:

- domain-critical
- security-sensitive
- financially material
- migration-heavy
- high-traffic or high-scale
- UX-critical

Higher risk requires broader validation depth.

### 2. Map Failure Modes

List what can fail:

- domain logic
- contract mismatch
- integration dependency
- concurrency or retry behavior
- data migration and backward compatibility
- degraded-state UX

Tests should prove these failures are either prevented or detected.

### 3. Choose Test Layers

Use the smallest layer that can prove the behavior, but do not stop below the layer where failure is likely.

- unit tests for pure logic and branching rules
- integration tests for DB, API, queue, and persistence boundaries
- contract tests for service and API compatibility
- end-to-end tests for high-value user journeys
- manual verification for visual, usability, or platform-sensitive flows

### 4. Define Release Evidence

Before shipping, state:

- what was validated automatically
- what was verified manually
- what remains unproven
- what rollback or mitigation exists if the risk materializes

## Strategy Rules

### Unit Tests

- Use for fast feedback on logic, validation, state transitions, and edge cases.
- Do not use unit tests alone as proof of integration correctness.

### Integration Tests

- Use for repositories, APIs, data access, queues, workers, and migration-sensitive behavior.
- Prefer real boundaries over excessive mocking in high-risk flows.

### Contract Tests

- Use when service or client compatibility matters.
- Validate request, response, schema, error model, and version evolution.

### End-To-End Tests

- Use sparingly for revenue-critical, auth-critical, or workflow-critical flows.
- Focus on a small number of high-signal journeys.

### Manual Verification

- Required for platform behavior, accessibility, visual correctness, and critical degraded states.
- Explicitly list manual checks in release notes or change evidence.

## AI And Workflow-Specific Testing

For AI-enabled systems, add:

- schema validation checks
- prompt or tool regression sets
- fallback path verification
- unsafe output and abuse-case checks
- cost and latency budget verification

For ERP and workflow systems, add:

- approval and reversal flows
- audit event verification
- period-lock and entitlement checks
- multi-role and multi-tenant scenario coverage

## Deliverables

For meaningful changes, produce:

- risk classification
- test matrix by layer
- release evidence summary
- manual verification list
- open risk list

See [references/test-matrix-template.md](references/test-matrix-template.md).

## Review Checklist

- [ ] Test depth matches business and operational risk.
- [ ] Integration boundaries are tested where failures are plausible.
- [ ] Contracts are validated where clients or services depend on them.
- [ ] End-to-end tests are focused on the highest-value flows.
- [ ] Manual verification covers the platform or UX gaps automation cannot.
- [ ] Release evidence makes residual risk explicit.

## References

- [references/test-matrix-template.md](references/test-matrix-template.md): Test plan by risk and layer.
- [references/release-evidence.md](references/release-evidence.md): What must be true before shipping.
