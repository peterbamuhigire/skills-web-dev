# Risk-Driven Testing

Use this reference to design a test portfolio that improves release confidence without creating slow, noisy automation.

## Layer Selection Rules

- Put fast checks in the commit stage: build, lint, unit tests, static analysis, packaging.
- Use integration tests where persistence, framework behavior, serialization, jobs, or real dependency contracts create risk.
- Use contract tests where separate deployable components must remain compatible.
- Use acceptance tests for business workflows at the application boundary.
- Use end-to-end tests only for the few journeys that truly need browser-to-backend or device-to-backend proof.
- Use exploratory testing where UX ambiguity, platform variance, or recent failures make automation insufficient.

## Determinism Rules

- Control time, randomness, and asynchronous completion where possible.
- Isolate test data so cases can run in any order.
- Prefer explicit fixtures and builders over hidden global setup.
- Make retries inside tests rare and justified; repeated retries often hide product or test defects.

## Flake Policy

- A flaky test is a production risk to the delivery system.
- Assign an owner when quarantining a flaky test.
- Keep quarantined tests visible and scheduled for repair.
- Do not let a flaky suite silently become informational if it guards real risk.

## Evidence Expectations By Risk

- Low risk: commit stage plus targeted integration coverage.
- Medium risk: commit stage, integration coverage, manual verification of affected flow.
- High risk: add contract or acceptance coverage, explicit rollback notes, and stronger post-deploy telemetry watch.
- Very high risk: staged rollout, observation window, and residual-risk statement before release.
