[Back to Java Enterprise Development](../SKILL.md)

# Java APIs, messaging, and distributed failure semantics

Use this reference when a Java component crosses an HTTP, RPC, JMS, Kafka, or
AMQP boundary. It turns protocol capability into an explicit contract for
deadlines, delivery, idempotency, schema change, retries, and recovery. Pair it
with `api-design-first` for the API contract, `distributed-systems-patterns`
for cross-service consistency and sagas, and `reliability-engineering` for
timeouts, circuit breakers, overload, and incident operation.

## Evidence boundary and currentness

Protocol names do not prove delivery or recovery semantics. Use the [Java
enterprise currentness register](../../../../docs/source-registers/java-enterprise.md)
for the portfolio evidence record, then pin the Java client,
broker, protocol profile, serializer, schema tooling, deployment topology, and
transaction manager before admitting a concrete configuration or API call. The
source ledger below records the official material consulted at the recorded
access date.
Exact client defaults, broker limits, compatibility modes, and framework binding
behaviour are `NOT ASSESSED` until tested in the target build.

| Source | Scope admitted | Currentness record |
|---|---|---|
| [HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) | Method idempotency and safe retry reasoning | Published 2022-06; accessed 2026-09-05; protocol concept is stable, implementation policy remains local |
| [gRPC core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/) | Service definition, streaming order, deadlines, cancellation, and RPC lifecycle | Updated 2026-05-11; accessed 2026-09-05; Java binding details remain client-version-bound |
| [Jakarta Messaging specification](https://jakarta.ee/specifications/messaging/3.1/jakarta-messaging-spec-3.1.html) | Session transactions, acknowledgement, recovery, and redelivery metadata | Accessed 2026-09-05; specification level is context-bound; provider delivery limits remain `NOT ASSESSED` |
| [Apache Kafka delivery semantics](https://kafka.apache.org/41/design/design/) | At-most/at-least/exactly-once scopes, idempotent production, transactions, and offsets | Accessed 2026-09-05; Kafka release documentation is time-sensitive; verify the pinned broker/client pair |
| [RabbitMQ acknowledgements and confirms](https://www.rabbitmq.com/docs/confirms) | AMQP consumer acknowledgements, publisher confirms, requeueing, and prefetch | Accessed 2026-09-05; RabbitMQ/AMQP profile-specific; client library details remain `NOT ASSESSED` |
| [RabbitMQ reliability](https://www.rabbitmq.com/docs/reliability) | Duplicate possibility after lost confirmation and acknowledgement responsibility | Accessed 2026-09-05; broker topology and queue type remain context-bound |

The text uses no direct quotations. Claims assembled from several sources are
marked `(synthesis)`; operational deductions are marked `(inference)`. Generic
outbox, saga, consistency, and circuit-breaker doctrine remains owned by the
linked specialist skills rather than being copied here.
Archive snapshots were not captured in this task, so archival proof for the live
links remains `NOT ASSESSED`; run the archive check before publishing a release
evidence packet.

## Protocol selection matrix

| Boundary need | Candidate | Choose it when | Evidence before release | Main failure to design for |
|---|---|---|---|---|
| Public or partner resource contract | HTTP REST | Clients need resource semantics, broad tooling, cache/control metadata, or human-inspectable requests | OpenAPI contract, auth/error model, idempotency map, contract tests, and timeout behaviour | Ambiguous retries, incompatible response change, and client-visible partial work |
| Typed internal RPC or streaming call | gRPC | The service boundary benefits from an IDL, generated stubs, streaming, and explicit deadlines | Proto compatibility, generated-code build, deadline/cancellation test, and cross-language contract test | Caller gives up while server continues expensive work or commits a side effect |
| Jakarta enterprise messaging contract | JMS/Jakarta Messaging | Application-server or provider-managed queues/topics and session transaction semantics are required | Provider transaction/ack test, redelivery test, poison-message policy, and connection recovery | Acknowledgement occurs before the durable side effect or rollback semantics are misunderstood |
| Durable partitioned event stream | Kafka | Consumers need replay, partition-key ordering, consumer progress, or Kafka-scoped transactions | Key/order test, offset/side-effect test, producer/consumer failure test, and schema compatibility gate | Duplicate processing, reordering across partitions, and offset committed before work |
| Routed queue or broker exchange | AMQP, such as RabbitMQ's AMQP profile | Work needs explicit routing, queue ownership, publisher confirmation, consumer acknowledgement, and bounded in-flight delivery | Confirm/ack/requeue test, dead-letter/replay test, prefetch/load test, and topology contract | Publish or consume outcome is assumed from socket success; requeue creates duplicates |

Do not select a protocol from throughput folklore. State the caller's required
confirmation, ordering scope, replay need, payload contract, failure owner, and
operator action. If a boundary is request/response with no asynchronous or
independent failure, keep it in the API route; if it is naturally deferred,
bursty, or replayable, assess the messaging route `(inference)`.

## API contract rules

### HTTP

- Define the intended effect of every method. RFC 9110 describes `PUT`,
  `DELETE`, and safe methods as idempotent and explains why an idempotent request
  can be retried after a communication failure; it also advises against
  automatic retry of a non-idempotent request unless the application proves
  equivalent semantics. See [RFC 9110 idempotent methods](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2).
- For a non-idempotent command, require an idempotency key or an equivalent
  durable business key. Store the request fingerprint, terminal outcome, and
  ownership scope; decide whether a repeated key returns the same outcome,
  rejects a different payload, or permits a new attempt.
- Document whether a response means validation accepted, durable state committed,
  side effect accepted by a dependency, or work merely queued. Do not use one
  success code to hide these different states.
- Treat a timeout after server execution as an unknown outcome. Reconcile by
  key or query the resource before retrying. A client-visible timeout is not
  proof that the server rolled back `(inference)`.

### gRPC

- Set a deadline for every outbound RPC from the remaining caller budget. The
  official guide states that a client can otherwise wait indefinitely and that a
  deadline can end as `DEADLINE_EXCEEDED`; choose the value from measured work,
  network, queue, and retry budgets. See [gRPC deadlines](https://grpc.io/docs/guides/deadlines/).
- Propagate cancellation and stop spawned work when the operation is no longer
  wanted. gRPC documents that cancellation does not roll back changes already
  made; therefore cancellation and database rollback must be designed as
  separate boundaries. See [gRPC cancellation](https://grpc.io/docs/guides/cancellation/).
- Define retryable status classes and idempotency at the method contract, not in
  a shared interceptor that guesses from an error string. Preserve correlation,
  causation, deadline, and attempt metadata without exposing secrets.

`api-design-first` owns the OpenAPI or RPC contract, auth model, error model,
and idempotency map. This reference supplies the Java boundary questions and
failure tests; do not duplicate the API skill's generic response grammar.

## Delivery semantics

| Semantic | How it is obtained | What the consumer must still prove | Suitable evidence |
|---|---|---|---|
| At-most-once | Advance acknowledgement/offset before the side effect or accept loss by design | Loss is acceptable and no replay is required | Crash before processing, loss accounting, and business approval |
| At-least-once | Acknowledge/commit after the durable side effect or use broker confirmation | Duplicate delivery and replay are safe | Crash after side effect before acknowledgement; duplicate count and dedup result |
| Exactly-once within a provider scope | Use the provider's transaction/idempotence features within their stated boundary | External database, email, HTTP, and human effects still need idempotency or compensation | Provider-specific transaction test plus an external side-effect failure test |
| Exactly-once business effect | Make the business mutation idempotent and reconcile the full workflow | No transport feature alone proves this across independent resources | Duplicate, timeout, replay, reconciliation, and audit evidence |

Kafka's official design material distinguishes delivery semantics and describes
idempotent production and transactions for Kafka records and offsets. That does
not establish exactly-once effect across an external database or HTTP service;
the latter is a boundary synthesis, not a broker guarantee `(synthesis)`. RabbitMQ
documents that acknowledgement loss can require retransmission and therefore
can produce duplicates. See [Kafka message delivery semantics](https://kafka.apache.org/41/design/design/)
and [RabbitMQ reliability](https://www.rabbitmq.com/docs/reliability).

## Kafka, JMS, and AMQP operating rules

### Kafka

- Choose a record key from the ordering invariant. State the ordering scope;
  do not claim topic-wide order when the business invariant is per customer,
  account, or aggregate `(inference)`.
- Treat consumer progress as a separate durable decision from the database
  mutation unless the selected Kafka transaction boundary actually includes the
  effect. Commit progress after successful idempotent work; recover and replay
  when the process dies in the gap.
- Use producer idempotence or transactions only after verifying broker/client
  support and the operational recovery model. Test fencing, producer restart,
  aborted records, consumer restart, and an external database failure.
- Schema compatibility, retention, compaction, replay, and partition changes
  belong in the event contract. Record the owner and the rollback or forward-fix
  action for every incompatible change.

### JMS/Jakarta Messaging

Jakarta Messaging defines a transacted session that groups a session's produced
and consumed messages into an atomic unit for that provider; commit acknowledges
consumed messages and sends produced messages, while rollback recovers consumed
messages. The specification also says redelivery metadata and redelivery limits
can be provider-dependent. See [Jakarta Messaging transactions and acknowledgement](https://jakarta.ee/specifications/messaging/3.1/jakarta-messaging-spec-3.1.html#_transactions)
and [message acknowledgement](https://jakarta.ee/specifications/messaging/3.1/jakarta-messaging-spec-3.1.html#_message_acknowledgment).

- Select acknowledgement mode with the provider and container contract in
  view. Do not mix a local session transaction with a database transaction and
  call the result atomic unless a supported coordinator and recovery test prove
  it.
- Acknowledge only after the durable side effect is complete. On rollback,
  classify the message as retryable, poison, or operator-review; do not allow an
  infinite redelivery loop.
- Carry a stable message identifier, correlation identifier, causation
  identifier, producer timestamp, schema identifier, and tenant/owner scope
  where applicable.

### AMQP and RabbitMQ

RabbitMQ documents consumer acknowledgements and publisher confirms as separate
mechanisms: confirms cover publisher-to-broker responsibility, while consumer
acknowledgements cover broker-to-consumer processing. Its reliability guidance
also warns that retransmission after a lost confirmation can duplicate a
message. See [RabbitMQ confirms and acknowledgements](https://www.rabbitmq.com/docs/confirms).

- Use publisher confirms when the producer must know that the broker accepted
  responsibility. Handle negative or missing confirmation as an unknown outcome
  and deduplicate retransmission.
- Use manual consumer acknowledgements after the durable side effect. Bound
  unacknowledged work with the selected prefetch/back-pressure mechanism and
  monitor queue age, unacknowledged count, and redelivery.
- Distinguish a rejected message, a requeued message, a dead-lettered message,
  and an operator replay. These are different state transitions and need
  different metrics and permissions.

## Outbox, inbox, and deduplication

Use the following boundary when a database mutation must lead to a message:

| Stage | Durable action | Failure and recovery |
|---|---|---|
| Command transaction | Write domain state and an outbox record in one local database transaction | Rollback removes both; commit creates a publishable intent |
| Relay | Claim an outbox record with a lease/version and publish with broker confirmation | Relay crash can republish; retain a stable event identifier and make the consumer idempotent |
| Consumer admission | Insert the event identifier into an inbox/deduplication table or equivalent durable store | Unique conflict means the effect was already admitted; verify the prior outcome |
| Consumer effect | Apply the business mutation and record outcome in the same local transaction where possible | Crash before acknowledgement causes replay; the mutation must be safe to repeat |
| Acknowledgement | Acknowledge/commit broker progress only after the durable effect | Missing acknowledgement is a replay signal, not proof of failure |

This table is an implementation handoff to
[`distributed-systems-patterns`](../../../architecture/distributed-systems-patterns/SKILL.md),
which owns the generic outbox, inbox, saga, ordering, and consistency doctrine.
The Java implementation must still prove transaction-manager participation,
database uniqueness, relay concurrency, payload serialisation, and replay
behaviour. Do not promise exactly-once delivery where only an exactly-once
business effect has been engineered `(inference)`.

## Schema evolution

| Change | Default disposition | Gate |
|---|---|---|
| Add optional field | Usually compatible when old consumers ignore it | Consumer fixture, serialiser test, and replay of old payloads |
| Add required field | Breaking unless every deployed consumer can supply or default it | Expand/compatibility window, dual-read/write or default rule, and rollback test |
| Rename or remove field | Treat as breaking until all readers and replay stores are migrated | Deprecation record, compatibility test, and retained historical decoder |
| Change meaning, units, identity, or ordering | Breaking even when the wire shape is unchanged | New semantic contract, migration/reconciliation plan, and consumer sign-off |
| Change enum or error value | Additive only if unknown values are safely handled | Unknown-value test, dead-letter policy, and observability field review |

For every API or event schema record owner, purpose, compatibility direction,
unknown-field rule, version identifier, replay horizon, deserialisation failure
action, and deprecation/removal evidence. A schema registry or generated model
does not replace a compatibility policy; its exact product capability is
`NOT ASSESSED` until checked against the pinned tool.

## Sagas, retries, timeouts, and circuit breakers

| Decision | Prefer | Do not do |
|---|---|---|
| Saga shape | Orchestration when state, deadlines, compensation, and operator visibility need one owner; choreography when independent event reactions are genuinely simpler | Hide a long workflow in a chain of unowned callbacks |
| Retry | Bounded retry with jitter for a classified transient failure and an idempotent effect | Retry validation, authorisation, deterministic business rejection, or an unknown non-idempotent write |
| Timeout | A deadline smaller than the caller's remaining budget and dependency collapse threshold | Leave a client, pool, thread, or broker call unbounded |
| Circuit breaker | A measured protection around a failing dependency with an explicit fallback and probe policy | Treat an open circuit as a correctness repair or choose thresholds without workload evidence |
| Overload | Bound concurrency, queue depth, message age, and in-flight work; shed or defer by business priority | Allow retries and queued work to multiply without an admission rule |
| Compensation | An explicit inverse or corrective state transition with audit and owner | Assume a failed forward step can always be undone, especially after an external side effect |

`reliability-engineering` owns the generic retry, timeout, circuit-breaker,
degradation, and runbook policy. Java code must expose the boundary signals:
remaining deadline, attempt, idempotency key, circuit state, queue age,
redelivery, cancellation, and final outcome. Use a state machine for a saga and
test compensation failure as a first-class path.

## Failure tests and evidence outputs

| Scenario | Test | Evidence |
|---|---|---|
| HTTP response lost after commit | Commit the server-side effect, drop the response, then repeat the request | Idempotency lookup, same/outcome response, and no duplicate effect |
| gRPC deadline or cancellation | Cancel during CPU work, database work, and an outbound call | Cancellation propagation, server stop behaviour, and committed-state check |
| Kafka process crash | Crash after business effect and before offset progress | Replay, deduplication, final state, and offset evidence |
| Kafka producer restart | Interrupt publish and restart the producer | Duplicate record check, transaction outcome, and fencing/recovery evidence |
| JMS rollback/redelivery | Fail after consumption and before commit | Redelivery metadata, bounded retry, dead-letter/quarantine outcome |
| AMQP confirmation loss | Drop publisher confirmation and retransmit | Stable message identifier, broker confirmation evidence, and consumer deduplication |
| Consumer crash before acknowledgement | Apply durable effect then terminate | Replay safety, acknowledgement timing, and one business outcome |
| Outbox relay crash | Terminate after publish and before marking sent | Republish behaviour, duplicate event handling, and reconciliation |
| Incompatible schema | Deploy old and new readers/writers across the change window | Compatibility result, rejected payload handling, and rollback/forward-fix decision |
| Saga compensation failure | Fail a compensating action or make it unavailable | Stuck state, alert, operator action, retry budget, and audit trail |
| Retry storm | Make a dependency slow or return transient failures | Attempt rate, queue growth, circuit state, load shedding, and recovery time |

Produce an API/RPC contract, message envelope, delivery-semantics decision,
idempotency map, schema-evolution record, saga state model, retry/timeout
matrix, failure-test report, and operational runbook. Telemetry should join
correlation and causation identifiers with protocol, route/topic/queue,
partition or delivery identifier where safe, attempt, deadline, acknowledgement,
redelivery, schema, outcome, and owner. Never put credentials or sensitive
payloads in those fields.

## Handoffs

| Handoff | Send | Receiving owner |
|---|---|---|
| API contract | Methods, schemas, error states, auth boundary, idempotency key, deadline, and compatibility policy | `api-design-first` |
| Distributed workflow | Ownership, source of truth, event state, ordering, outbox/inbox, saga, compensation, replay, and reconciliation | `distributed-systems-patterns` |
| Database coupling | Outbox/inbox tables, unique keys, transaction boundary, indexes, retention, and migration choreography | `database-design-engineering` |
| Reliability policy | Retryable failures, timeout budget, circuit/degradation behaviour, overload bounds, alerts, and runbook owner | `reliability-engineering` and `observability-monitoring` |
| Security review | Trust boundaries, identity propagation, payload confidentiality, replay protection, and operator permissions | `vibe-security-skill` and `web-app-security-audit` |

## Anti-patterns

- Call a non-idempotent endpoint again because the client saw a timeout. Fix:
  reconcile by idempotency key or query the resource before retrying.
- Commit a Kafka offset or acknowledge a JMS/AMQP message before the durable
  effect. Fix: order acknowledgement after the effect and make replay safe.
- Publish directly after a database commit with no durable intent. Fix: use the
  local outbox boundary and reconcile relay state.
- Treat Kafka transactions, JMS session transactions, or AMQP confirms as an
  atomic transaction with an unrelated database. Fix: state the real scope and
  use idempotency or a saga across resources.
- Requeue every message indefinitely. Fix: classify poison messages, cap
  attempts, quarantine them, and provide permissioned replay.
- Put retry and circuit-breaker defaults in a shared interceptor with no method
  contract. Fix: derive policy from operation semantics and measured budgets.
- Change an event's meaning while preserving its field shape. Fix: issue a
  semantic contract change and migrate or reconcile consumers.
- Call a saga complete when a compensating action is only scheduled. Fix: expose
  pending, failed, and operator-repair states.

## Read next

- [`api-design-first`](../../../architecture/api-design-first/SKILL.md) for OpenAPI, error, auth, and idempotency contracts.
- [`distributed-systems-patterns`](../../../architecture/distributed-systems-patterns/SKILL.md) for consistency, outbox, inbox, saga, and ordering decisions.
- [`database-design-engineering`](../../../backend-databases/database-design-engineering/SKILL.md) for durable keys, outbox/inbox schema, indexes, and migrations.
- [`reliability-engineering`](../../../devops-cloud/reliability-engineering/SKILL.md) for retry, timeout, circuit-breaker, degradation, and recovery evidence.
- [`observability-monitoring`](../../../devops-cloud/observability-monitoring/SKILL.md) for telemetry, SLOs, alert rules, and runbooks.
