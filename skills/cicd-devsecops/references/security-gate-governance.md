# Security Gate Governance

Use this reference when security controls need clear policy and traceability, not only tooling.

## Exception Rules

- Every suppression or waiver needs a reason, owner, and review date.
- Temporary exceptions should expire automatically or be re-approved explicitly.
- Exceptions must not hide whether the normal security posture is currently degraded.

## Evidence Rules

- Keep security scan outputs long enough to support incident review and audit.
- Link security gate failures to the release or artifact they affected.
- Separate advisory findings from hard blockers so engineers know what must stop the line.

## Escalation Rules

- Block merge when findings indicate active code or dependency risk on the changed path.
- Block production when a release carries unresolved high-severity risk without approved exception.
- Escalate rapidly when secrets, signing, or deployment credentials may be compromised.
