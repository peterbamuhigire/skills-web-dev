# Reliability Verification

Use this reference when reliability claims need evidence beyond design intent.

## What To Verify

- timeout, retry, and backoff behavior
- idempotency under duplicate requests or messages
- degraded-mode user experience
- replay and reconciliation safety
- queue growth, saturation, and backpressure behavior
- alert usefulness and runbook clarity

## Evidence Sources

- targeted automated tests
- staging drills and rollback rehearsals
- load or soak tests for critical paths
- queue replay exercises
- incident simulations or game days

## Exercise Selection

- Run lightweight drills for common recoveries such as dependency outage or queue backlog.
- Run deeper exercises for financially material, security-sensitive, or compliance-sensitive workflows.
- Keep exercises focused on learning and system improvement, not theater.
