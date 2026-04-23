---
name: distributed-systems-patterns
description: Use when designing or reviewing multi-service, message-driven, or eventually
  consistent systems. Covers service boundaries, consistency tradeoffs, event workflows,
  outbox and inbox patterns, sagas, ordering, and idempotency.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Distributed Systems Patterns
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing multi-service, message-driven, or eventually consistent systems. Covers service boundaries, consistency tradeoffs, event workflows, outbox and inbox patterns, sagas, ordering, and idempotency.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `distributed-systems-patterns` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Service consistency and idempotency note | Markdown doc covering chosen consistency model, idempotency keys, and saga sequences | `docs/dist/consistency-note-checkout.md` |
| Operability | Failure-mode catalogue | Markdown doc listing partition, retry, and replay failure modes with mitigations | `docs/dist/failure-modes-checkout.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
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