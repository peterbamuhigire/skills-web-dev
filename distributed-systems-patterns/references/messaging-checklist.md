# Messaging Checklist

Use this checklist for queues, event buses, and saga-driven workflows.

## Contract Design

- event name reflects business meaning
- payload contains stable identifiers and versioning
- producer and consumer ownership are known
- correlation and causation IDs are included

## Reliability Design

- delivery guarantee assumption is explicit
- consumer idempotency is defined
- retry and dead-letter behavior are documented
- replay tooling and permissions are known

## Workflow Design

- ordering assumptions are stated
- timeout behavior is bounded
- compensation or reconciliation path exists
- user-facing pending or failure states are designed

## Observability Design

- lag, age, retry count, and dead-letter metrics exist
- stuck workflow detection exists
- release markers allow change correlation
