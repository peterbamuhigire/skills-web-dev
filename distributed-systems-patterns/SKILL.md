---
name: distributed-systems-patterns
description: Use when designing or reviewing multi-service, message-driven, or eventually consistent systems. Covers service boundaries, consistency tradeoffs, event workflows, outbox and inbox patterns, sagas, ordering, and idempotency.
---

# Distributed Systems Patterns

Use this skill when a design crosses process, service, queue, or region boundaries. The goal is to keep distributed complexity deliberate and bounded rather than accidental.

## Load Order

1. Load `world-class-engineering`.
2. Load `system-architecture-design` first for the overall shape.
3. Load this skill only when the system genuinely needs multiple services, asynchronous workflows, or weakly consistent boundaries.

## Decision Workflow

### 1. Justify Distribution

State why distribution is necessary:

- team ownership and release independence
- scaling asymmetry
- fault isolation
- compliance or tenancy isolation
- long-running or bursty workflows

If none of these are strong, prefer a modular monolith.

### 2. Define Boundaries and Contracts

For each service or asynchronous component, define:

- owned data
- API or event contracts
- consistency expectation
- failure effect on upstream and downstream flows
- observability and ownership requirements

### 3. Choose Interaction Patterns

Use:

- synchronous calls when the caller needs immediate confirmation
- messaging when work is slow, bursty, or naturally eventual
- outbox and inbox patterns when reliability across boundaries matters
- sagas or compensations when one business workflow spans multiple durable states

### 4. Design Consistency and Recovery

Make explicit:

- source of truth
- ordering requirements
- deduplication strategy
- reconciliation path
- timeout and retry policy
- compensation or manual repair path

### 5. Prove the Design

Before calling it production-ready, provide:

- consistency model
- failure-mode examples
- idempotency and replay notes
- contract evolution rules
- operational signals for stuck or divergent workflows

## Non-Negotiable Standards

### Service Boundaries

- Each service owns its data and rules.
- Do not share databases across services as a convenience.
- Keep contracts narrow and versionable.
- Avoid chatty request chains on critical paths.

### Messaging

- Assume at-least-once delivery unless proven otherwise.
- Design consumers to be idempotent and replay-safe.
- Define ordering needs explicitly; unordered by default is safer to assume.
- Include correlation IDs and causation metadata.

### Consistency

- Strong consistency has operational cost; use it where business correctness needs it.
- Eventual consistency requires visible user and operator handling.
- If divergence is possible, define reconciliation before shipping.

### Sagas and Compensation

- Use compensation when the workflow spans multiple irreversible boundaries.
- Compensation must be explicit, auditable, and tested.
- Never describe a workflow as atomic if it crosses systems that cannot commit atomically.

## Deliverables

For distributed-system work, produce:

- service and ownership map
- contract list
- consistency decision table
- event and retry flow notes
- reconciliation or compensation plan
- stuck-workflow and replay detection signals

## Review Checklist

- [ ] Distribution is justified by real constraints.
- [ ] Data ownership is explicit and not undermined by shared persistence shortcuts.
- [ ] Idempotency and replay behavior are defined.
- [ ] Ordering assumptions are explicit.
- [ ] Consistency and compensation strategy match business risk.
- [ ] Operational detection exists for stuck, duplicated, or divergent workflows.

## References

- [references/consistency-decision-matrix.md](references/consistency-decision-matrix.md): How to choose synchronous, asynchronous, strong, or eventual consistency.
- [references/messaging-checklist.md](references/messaging-checklist.md): Event, queue, and saga review prompts.
