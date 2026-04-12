# World-Class Gates

Use these gates before describing any output as production-ready.

## Architecture Gate

- [ ] Core user journeys and failure-sensitive flows are defined.
- [ ] Modules have explicit responsibilities and bounded dependencies.
- [ ] Business rules are isolated from transport, UI, and storage concerns.
- [ ] High-impact decisions have tradeoff reasoning or ADR notes.
- [ ] Backward compatibility and migration strategy are defined for live systems.

## Security Gate

- [ ] Trust boundaries and privileged operations are identified.
- [ ] Authentication, authorization, and tenant scoping are explicit.
- [ ] Inputs are validated and outputs are encoded for their context.
- [ ] Secrets, sessions, tokens, webhooks, and admin actions have dedicated controls.
- [ ] Logging and alerting exist for high-risk actions and abuse paths.

## Performance Gate

- [ ] Performance budgets exist for the critical path.
- [ ] Slow work is measured, bounded, cached, batched, or moved off the request path.
- [ ] Database access, network calls, and rendering hot spots are profiled or reasoned about.
- [ ] Third-party dependencies are justified by user or business value.
- [ ] Representative-device or representative-load verification exists.

## UX Gate

- [ ] Main tasks are obvious and use familiar patterns.
- [ ] Empty, loading, success, and error states are designed intentionally.
- [ ] Copy is specific, concise, and recovery-oriented.
- [ ] Accessibility, keyboard use, contrast, semantics, and dynamic type/responsive concerns are covered.
- [ ] The interface reduces choice overload and cognitive friction.

## Testing Gate

- [ ] Core logic has automated tests at the right level.
- [ ] Edge cases and failure modes have explicit verification.
- [ ] Integration boundaries are tested where contracts matter.
- [ ] Manual verification steps exist for UX-critical and release-critical flows.
- [ ] Test names and structure make regressions diagnosable.

## Operability Gate

- [ ] Logs, metrics, traces, and audit records exist where diagnosis matters.
- [ ] Background jobs are idempotent and replay-safe.
- [ ] Rollout, rollback, and recovery steps are known.
- [ ] Ownership is clear for alerts, incidents, and follow-up maintenance.
- [ ] Documentation is sufficient for the next engineer to operate the system safely.
