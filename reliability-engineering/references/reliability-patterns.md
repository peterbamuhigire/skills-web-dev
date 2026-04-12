# Reliability Patterns

Use these patterns when designing fault-tolerant systems.

## Timeout and Retry Rules

- Set a timeout for every network or dependency boundary.
- Make retryability explicit by operation type.
- Use backoff with jitter for transient failures.
- Bound total retry duration so the system does not amplify incidents.
- Prefer surfacing partial failure quickly over silently hanging.

## Idempotency Rules

- Use idempotency keys for payment, provisioning, webhook, and import flows.
- Store enough result state to answer duplicate requests safely.
- Make consumers replay-safe before increasing automation.

## Queue Safety Rules

- Define delivery guarantee assumptions: at-most-once, at-least-once, effectively-once.
- Handle poison messages with dead-letter queues and operator visibility.
- Track lag, retries, age, and failure rate for every important queue.
- Document replay tooling before a production emergency requires it.

## Degradation Rules

- Keep the revenue-critical or user-critical path usable in reduced mode when possible.
- Shut off optional enrichments before core actions.
- Do not degrade in ways that compromise security, data integrity, or financial correctness.

## Recovery Rules

- Prefer reconciliation for systems that cross storage or service boundaries.
- Prefer compensation when reversing business effects is possible and auditable.
- Prefer rollback only when state compatibility and side effects are clearly bounded.
