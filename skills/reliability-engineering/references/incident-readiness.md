# Incident Readiness

Use this checklist before calling a critical system operationally ready.

## Before Production

- Identify the top incident scenarios.
- Assign service owners and escalation expectations.
- Link alerts to dashboards, logs, traces, and runbooks.
- Prepare safe operator tooling for replay, disable, requeue, or feature-flag rollback.
- Record release markers so incidents can be correlated with changes.
- Rehearse the first actions for the highest-cost scenarios.

## During Incident Design

Define for each major incident type:

- detection signal
- likely customer impact
- first 15-minute actions
- rollback trigger
- communication owner
- follow-up evidence needed
- whether rollback, failover, or degraded mode is the preferred first move

## After Incident

- Capture timeline, impact, contributing factors, and what detection missed.
- Separate root causes from trigger events.
- Fix systemic causes before adding process theater.
- Convert useful lessons into monitoring, tests, tooling, or simplified design.
