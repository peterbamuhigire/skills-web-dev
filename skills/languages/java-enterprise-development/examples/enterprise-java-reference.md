[Back to Java Enterprise Development](../SKILL.md)

# Enterprise order and financial operations reference

This scenario tests decision quality; it is not a starter application or a
universal stack. Accounting policy comes from the finance doctrine engine.

## Frame

An enterprise platform serves 5,000 concurrent users across tenant-scoped order,
inventory, invoice, payment, audit, reporting, and reconciliation workflows. It
exposes REST APIs, publishes Kafka events, runs background and batch work,
supports Oracle Database and PostgreSQL deployment variants, uses an external
OIDC provider, and may run on Kubernetes. Availability, recovery, throughput,
latency, retention, and jurisdictional obligations remain requirements to be
agreed; they are not inferred from the concurrency figure.

The critical slice is payment application to an issued invoice. A client may
retry after losing the response. The invariant is that one authorised payment
attempt produces at most one accepted payment and one corresponding approved
accounting effect, while every ambiguous outcome can be reconciled.

## Capability boundaries

```text
identity/access
  -> order and inventory
  -> invoicing
  -> payment application
  -> approved accounting adapter
  -> outbox/event publication
  -> reporting/read models
  -> audit and operations
```

Start as a modular monolith when one team/release and shared transactional
consistency dominate. Enforce module dependencies and API/event boundaries.
Extract only a capability that has independent ownership, release/scale or
security needs and an operable consistency model.

## Candidate production baseline

| Concern | Baseline candidate | Decision still required |
|---|---|---|
| Runtime | Current supported Java LTS and organisation-approved distribution | Exact support/licence/OS/container matrix |
| Platform | Spring Boot servlet application | Compare Jakarta runtime/Quarkus/Helidon if platform or density requires it |
| Concurrency | Synchronous request model; virtual threads only after compatibility/load check | Admission, downstream capacity, pinning/blocking evidence |
| Persistence | JPA/Hibernate for aggregate writes; jOOQ for complex reports/vendor SQL | Access patterns, portability, Oracle/PostgreSQL divergence |
| Schema | Versioned expand/migrate/contract changes | Flyway or Liquibase based on estate/governance |
| Identity | OIDC/OAuth resource server with server-side resource/tenant authorisation | Provider, claims, audience, key rollover, session needs |
| Messaging | Transactional outbox to Kafka, idempotent consumers | Ordering, schema compatibility, retention/replay, DLQ/reconciliation |
| Telemetry | Structured logs, Micrometer/OpenTelemetry, JVM/pool/queue metrics | Backend, sampling, retention, PII controls, alert ownership |
| Packaging | JVM OCI image; Kubernetes only if platform requirements justify it | Resource budget, probes, termination, autoscaling, recovery |

This table is a hypothesis. The current source register and project evidence
must resolve every version and compatibility choice.

## Critical flow

| Stage | Normal path | Failure/duplicate path | Evidence |
|---|---|---|---|
| Authenticate | Validate issuer, audience, signature, expiry and client | Reject missing/invalid/expired token without side effects | Security integration tests |
| Authorise | Derive tenant from trusted identity; check payment action and invoice ownership/state | Deny cross-tenant/client-supplied tenant override | Auth matrix and denied-path tests |
| Admit request | Validate currency, amount, reference and idempotency key; place bounded request deadline | Stable validation problem; no database write | API contract tests |
| Lock/version | Load invoice/payment attempt under defined transaction/isolation/locking policy | Detect stale/closed/overpaid invoice and concurrent update | Real database concurrency tests |
| Apply | Insert unique tenant/client/idempotency attempt and approved payment state | Existing key returns prior outcome; ambiguous commit enters reconciliation | Oracle and PostgreSQL integration tests |
| Accounting | Invoke approved posting contract in same local transaction or explicit workflow | No invented ledger policy; compensate/reconcile by approved doctrine | Finance-engine acceptance evidence |
| Publish | Commit outbox row with business state; relay to broker after commit | Retry relay; consumer deduplicates by event identity | Crash/restart/duplicate tests |
| Respond | Return stable payment resource/status and correlation | Client timeout can query key/resource rather than charge again | Timeout/retry API test |
| Operate | Emit safe audit event, trace and business/technical metrics | Alert on failed/ambiguous/reconciliation backlog | Dashboard/runbook exercise |

## Data and transaction decisions

- Define currency and amount as a value with decimal precision/scale and explicit
  rounding at approved boundaries. Do not use `double`.
- Use a database uniqueness constraint for the tenant/idempotency scope; an
  application pre-check alone races.
- Keep the local transaction short. Do not call the identity provider, payment
  network, broker, or model while holding database locks.
- Persist attempt, business transition, accounting handoff state, audit data,
  and outbox according to one explicit consistency design. A distributed
  transaction is considered only if resource atomicity and recovery justify it.
- Treat commit-response loss as an unknown outcome. Resolve by idempotency key,
  persisted attempt state, provider reference, and reconciliation.
- Keep reporting SQL outside aggregate loading when it needs complex joins,
  windows, vendor features, or large streaming results.

## Oracle and PostgreSQL variants

Keep domain and API contracts common while isolating dialect, driver, generated
identifier, stored-program, LOB, error, migration, and HA adapters. Run the same
business contract suite against both databases, then add vendor-specific tests
for plans, isolation/locking, sequence/identity, procedures/types, timeout,
failover and migration behaviour. Passing on one engine says nothing about the
other's untested behaviour.

For Oracle RAC, the database owner supplies supported service/failover and
continuity configuration. The application proves connection borrow/drain,
in-flight transaction outcome, safe replay/idempotency, and reconciliation.
Until a controlled event is exercised, Oracle failover is `NOT ASSESSED`.

## Batch reconciliation

For tens of millions of rows, partition by a stable business/data boundary,
use indexed/keyset access and bounded chunks, write restart/checkpoint state,
make item/chunk effects idempotent, quarantine poison records, and reconcile
input/control totals/output. Size concurrency against database and downstream
capacity. Record throughput, p99 chunk duration, memory, GC, query load, errors,
restart time, and correctness totals; do not derive production capacity from a
small development dataset.

## Release slice

1. Expand schema with backward-compatible attempt/outbox fields and indexes.
2. Deploy code that can read old/new state but keeps new write path disabled.
3. Run migration and production-shaped smoke/concurrency/duplicate tests.
4. Enable by tenant/canary, watch business and technical telemetry, reconcile.
5. Roll forward on data-shape problems; roll back application only while old
   readers remain compatible.
6. Contract old schema after all versions/consumers are gone and recovery is
   proven.

## Readiness snapshot

```text
Architecture decision: PARTIAL (requirements/SLOs incomplete)
Business invariant design: PASS (scenario-level, not implemented)
Build/tests: NOT ASSESSED (no downstream repository)
Security integration: NOT ASSESSED
Oracle/PostgreSQL behaviour: NOT ASSESSED
Kafka duplicate/replay behaviour: NOT ASSESSED
Load/capacity: NOT ASSESSED
Kubernetes termination/rollout: NOT ASSESSED
Oracle failover: NOT ASSESSED
Rollback/reconciliation drill: NOT ASSESSED
```

The reference proves how to reason and what evidence to request. It does not
claim that a production system exists.
