---
name: advanced-testing-strategy
description: Use when designing or reviewing test strategy for production systems, APIs, mobile apps, SaaS platforms, ERP workflows, and AI-enabled systems. Covers unit, integration, contract, end-to-end, regression, release-gate, and risk-based testing decisions.
---

# Advanced Testing Strategy

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
