---
name: event-driven-architecture
description: Use when designing event-driven systems, async service integration, event sourcing,
  CQRS, saga workflows, or message-broker topologies — covers domain event modeling, schema
  evolution, idempotency, outbox delivery, dead-letter handling, and multi-tenant routing for
  production SaaS.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Event-Driven Architecture
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing asynchronous service integration, decoupled workflows, or eventual-consistency boundaries
- Introducing event sourcing, CQRS, or saga orchestration into a SaaS platform
- Selecting a message broker (RabbitMQ vs SQS/SNS vs Kafka) and a delivery guarantee model
- Hardening an existing EDA: idempotency, outbox, DLQs, schema evolution, tenant isolation

## Do Not Use When

- The interaction is strictly request/response with low latency SLOs — use REST or gRPC directly (`api-design-first`)
- The system has a single service and no integration partners — events add cost with no benefit
- The use case needs strong cross-aggregate transactions — reconsider bounded contexts first

## Required Inputs

- Target domain (bounded contexts, aggregates, business events)
- Delivery guarantee needs (at-least-once vs at-most-once vs exactly-once)
- Ordering and partition requirements (per-tenant, per-aggregate, or none)
- Scale budget: peak events/sec, retention window, expected consumers

## Workflow

1. Model domain events before choosing a broker — brokers are an implementation detail.
2. Decide ordering and partitioning; this constrains broker choice.
3. Pick the simplest delivery guarantee that meets the SLA — idempotency is cheaper than exactly-once.
4. Design the outbox + relay before writing producers.
5. Design the DLQ + replay tooling before production.
6. Add schema registry and versioning before a second consumer joins.

## Quality Standards

- Every event name is past-tense and domain-meaningful (`OrderPlaced`, not `OrderEvent`).
- Every event carries `event_id`, `event_type`, `event_version`, `tenant_id`, `occurred_at`, `causation_id`, `correlation_id`.
- Every consumer is idempotent and keeps a dedup ledger.
- Every topic has a documented owner, schema, and retention policy.

## Anti-Patterns

- Event spaghetti: any service can publish anything anyone listens to — no bounded contexts.
- Using events as disguised RPC (request/reply via two queues with tight coupling).
- "Exactly-once delivery" claimed without idempotent consumers — always false in practice.
- Sharing a single broker topic across tenants with no partition key — noisy-neighbour outages guaranteed.

## Outputs

- Event catalogue (Markdown + JSON Schema) with owners, versions, and retention.
- Broker topology (topics, partitions, DLQs) and IaC stubs.
- Outbox migration + relay worker reference implementation.
- Consumer idempotency checklist and replay runbook.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Event schema and contract test results | Markdown doc plus CI log covering event schema tests, consumer compatibility, and saga workflow validation | `docs/events/contract-tests-2026-04-16.md` |
| Operability | Event broker operations runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` covering broker, partitioning, replay, and DLQ handling | `docs/events/broker-runbook.md` |

## References

- *Building Event-Driven Microservices* — Adam Bellemare (O'Reilly, 2020)
- *Designing Data-Intensive Applications* Ch. 11 — Martin Kleppmann (O'Reilly, 2017)
- Companion skills: `microservices-communication`, `microservices-architecture-models`, `distributed-systems-patterns`, `multi-tenant-saas-architecture`
<!-- dual-compat-end -->

## Overview

Event-driven architecture (EDA) replaces synchronous request chains with asynchronous event streams. Producers emit immutable facts; consumers react independently. Benefits: decoupling, scalability, temporal flexibility, audit. Costs: eventual consistency, operational complexity, harder debugging.

**Cardinal rule:** Events describe *facts that have happened*. They are immutable, past-tense, and owned by the producing context. Commands and queries are different animals — do not mix them with events on the same topic.

---

## 1. Events vs Commands vs Queries

| Concept | Direction | Mutability | Example |
|---------|-----------|------------|---------|
| Command | Request to change state | Imperative, intent | `PlaceOrder` |
| Event   | Notification of past fact | Immutable, past tense | `OrderPlaced` |
| Query   | Read request | Read-only | `GetOrderStatus` |

A command *may fail*. An event *already happened*. Conflating them leads to consumers trying to "reject" events — which makes no sense.

---

## 2. Domain Events

**Naming:** `<AggregateName><PastTenseVerb>` — `InvoiceIssued`, `PaymentSettled`, `TenantSuspended`. Never `InvoiceEvent`, `PaymentUpdate`, `UserChanged`.

**Envelope schema (JSON):**

```json
{
  "event_id": "7f3c...a2",
  "event_type": "order.placed",
  "event_version": 2,
  "tenant_id": "t_9a1c",
  "occurred_at": "2026-04-16T08:12:44.312Z",
  "correlation_id": "cor_61af",
  "causation_id": "evt_14e2",
  "producer": "order-service@v1.8.3",
  "data": {
    "order_id": "o_7812",
    "customer_id": "c_331",
    "total_cents": 125000,
    "currency": "UGX"
  }
}
```

**Event sizing rules:**

- Include enough data for common consumers to act without a callback.
- Do not include the whole aggregate — that couples downstream teams to your internal model.
- Include a stable reference URL if heavy payload is needed (`/orders/{id}`).

---

## 3. Event Sourcing

Store every state change as an append-only event. Rebuild current state by replaying events.

```sql
CREATE TABLE events (
  event_id     UUID PRIMARY KEY,
  aggregate_id UUID NOT NULL,
  aggregate_type TEXT NOT NULL,
  sequence_no  BIGINT NOT NULL,
  event_type   TEXT NOT NULL,
  payload      JSONB NOT NULL,
  occurred_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (aggregate_id, sequence_no)
);
CREATE INDEX events_aggregate_idx ON events (aggregate_id, sequence_no);
```

**Replay pattern (TypeScript):**

```ts
async function loadOrder(id: string): Promise<Order> {
  const rows = await db.query(
    "SELECT event_type, payload FROM events WHERE aggregate_id = $1 ORDER BY sequence_no", [id]
  );
  const order = new Order(id);
  for (const row of rows.rows) order.apply(row.event_type, row.payload);
  return order;
}
```

**Snapshots:** Persist aggregate state every N events to cap replay cost. Always keep events — snapshots are a cache.

**When event sourcing is overkill:** Most SaaS aggregates do not need it. Use it only when audit, temporal queries, or reprojection is a first-class requirement (accounting, inventory ledgers, healthcare records).

---

## 4. CQRS — Command Query Responsibility Segregation

Split the write model (optimised for transactions) from the read model (optimised for queries). Events are the contract between them.

```
Command → Write Model (aggregate) → Event → Projection → Read Model (denormalised)
                                                             ↑
                                                   Query ────┘
```

**Projection worker (pseudocode):**

```python
def handle_order_placed(event):
    with db.transaction() as tx:
        tx.exec(
            "INSERT INTO order_summary (order_id, tenant_id, total, status) "
            "VALUES (%s, %s, %s, 'placed') ON CONFLICT (order_id) DO NOTHING",
            (event.data.order_id, event.tenant_id, event.data.total_cents)
        )
        tx.exec(
            "INSERT INTO projection_cursor (projection, last_event_id) VALUES ('order_summary', %s) "
            "ON CONFLICT (projection) DO UPDATE SET last_event_id = EXCLUDED.last_event_id",
            (event.event_id,)
        )
```

**Eventual consistency contract:** Document the lag budget (e.g., 95% of `OrderPlaced` events visible in read model within 2 seconds). Expose a "projection freshness" metric and alarm on lag.

---

## 5. Message Broker Selection

| Broker | Model | Ordering | Use When |
|--------|-------|----------|----------|
| RabbitMQ | AMQP routing | Per-queue | Complex routing, low-to-mid throughput, classic task queues |
| AWS SQS + SNS | Queue + pub-sub | FIFO queues per-group | Serverless-first, simple fan-out, ops-light |
| Apache Kafka | Log | Per-partition | High throughput, replay, event sourcing, multi-consumer |
| NATS JetStream | Log + streams | Per-subject | Low latency, edge-friendly, lightweight Kafka alternative |
| Redis Streams | Log (lightweight) | Per-stream | Small scale, same box as cache, not for durable OLTP |

**Decision heuristic:**

1. Need replay + multi-consumer + high throughput → Kafka (or JetStream).
2. Need flexible routing + classic work queues → RabbitMQ.
3. Running on AWS with low ops budget → SNS/SQS.
4. Sub-millisecond latency on trusted network → NATS.

**Never choose a broker by framework preference — choose by ordering, retention, and operational model.**

---

## 6. Saga Pattern

Multi-service transactions without two-phase commit. Each step emits an event or command; compensations roll back on failure.

**Choreography saga** — each service listens for the previous event and emits its own:

```
OrderPlaced → [Payment] PaymentAuthorized → [Inventory] InventoryReserved → [Shipping] ShipmentScheduled
                    ↓ PaymentFailed                ↓ OutOfStock
               OrderCancelled ←──────────── PaymentRefunded
```

Low coupling but the full flow is implicit — document it explicitly in the event catalogue.

**Orchestration saga** — a coordinator issues commands and handles compensations:

```python
class OrderSaga:
    def handle(self, state, event):
        match (state.step, event.type):
            case ("start", "order.placed"):
                return [Command("payment.authorize", state.order_id)], "awaiting_payment"
            case ("awaiting_payment", "payment.authorized"):
                return [Command("inventory.reserve", state.order_id)], "awaiting_inventory"
            case ("awaiting_inventory", "inventory.out_of_stock"):
                return [Command("payment.refund", state.order_id),
                        Command("order.cancel", state.order_id)], "failed"
```

Use orchestration for workflows with more than 3 steps, complex compensations, or human approvals. Use choreography when every step is a simple emit-and-forget.

---

## 7. Outbox Pattern — Guaranteed Delivery Without 2PC

**Problem:** After `INSERT INTO orders`, the process crashes before publishing `OrderPlaced`. Losing the event silently breaks downstream consumers.

**Fix:** Write the event into an `outbox` table in the same DB transaction as the state change. A separate relay worker polls the outbox and publishes to the broker.

```sql
CREATE TABLE outbox (
  id           BIGSERIAL PRIMARY KEY,
  aggregate_id UUID NOT NULL,
  event_type   TEXT NOT NULL,
  payload      JSONB NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  published_at TIMESTAMPTZ
);
CREATE INDEX outbox_unpublished ON outbox (id) WHERE published_at IS NULL;
```

**Relay worker (TypeScript):**

```ts
async function relayLoop() {
  while (true) {
    const { rows } = await db.query(
      "SELECT id, event_type, payload FROM outbox WHERE published_at IS NULL ORDER BY id LIMIT 100"
    );
    for (const row of rows) {
      await broker.publish(row.event_type, row.payload, { messageId: String(row.id) });
      await db.query("UPDATE outbox SET published_at = NOW() WHERE id = $1", [row.id]);
    }
    if (rows.length === 0) await sleep(500);
  }
}
```

**Transactional-log tailing** (Debezium CDC against the outbox or WAL) is an upgrade when polling latency becomes a bottleneck.

---

## 8. Event Schema Registry and Evolution

Multiple services share event schemas. Without discipline, a change breaks every consumer silently.

**Formats:**

- **JSON Schema** — human-readable, simple, largest payload. Use for low-throughput, public APIs.
- **Avro** — compact binary, strong schema, mature Kafka ecosystem (Confluent Schema Registry).
- **Protobuf** — compact, tooling-rich, good for gRPC + events hybrid stacks.

**Evolution rules (backwards-compatible changes only):**

- ✅ Add optional field with default.
- ✅ Remove optional field (consumers ignore it).
- ✅ Add new event type.
- ❌ Rename field.
- ❌ Change field type (string → int).
- ❌ Make optional field required.

Any breaking change bumps the major version: `order.placed.v2`. Run v1 and v2 topics in parallel until all consumers have migrated. Retire v1 with a dated deprecation notice.

---

## 9. Idempotency — The "Exactly-Once" Illusion

Brokers offer at-least-once delivery. Consumers must tolerate duplicates. "Exactly-once" is only possible with idempotent consumers.

**Consumer dedup ledger:**

```sql
CREATE TABLE processed_events (
  event_id   UUID PRIMARY KEY,
  consumer   TEXT NOT NULL,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

```python
def handle(event):
    with db.transaction() as tx:
        inserted = tx.exec(
            "INSERT INTO processed_events (event_id, consumer) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (event.event_id, "order-projection")
        )
        if inserted.rowcount == 0:
            return  # already processed
        apply_side_effects(event, tx)
```

**Idempotency keys on the producer side** (HTTP POST) match the same pattern: store the key + result, return cached result on retry.

---

## 10. Dead Letter Queues and Poison Messages

A poison message (malformed, schema-incompatible, or triggering a bug) blocks consumer progress forever if retried indefinitely.

**Retry policy:**

1. Immediate retry: 0 attempts (the broker redelivery covers this).
2. Backoff retries: 3–5 attempts with exponential backoff (1s, 5s, 30s, 2m, 10m).
3. After max attempts → route to DLQ.

**DLQ hygiene:**

- Alarm on any DLQ depth > 0. Silent DLQs are undiscovered outages.
- Tag each DLQ message with last error, stack trace, attempt count.
- Build a replay CLI: inspect, fix, and republish to the main topic.
- Document a DLQ runbook; on-call must know the replay procedure before launch.

---

## 11. EDA for Multi-Tenant SaaS

**Tenant partitioning options:**

| Option | Isolation | Cost | Use When |
|--------|-----------|------|----------|
| Partition key = `tenant_id` | Logical, shared topic | Low | Most SaaS — fair scheduling via partition assignment |
| Topic per tenant | Strong, but topic count explodes | High | Enterprise tier, compliance-driven |
| Broker per tenant | Full isolation | Highest | Regulated data residency |

**Noisy-neighbour controls:**

- Per-tenant rate limits at the producer (token bucket keyed on `tenant_id`).
- Consumer partitions sized to worst-case tenant throughput × 2.
- Tenant-level quota metric emitted with every consume — feeds billing + throttling.

**Every event carries `tenant_id`.** Downstream joins, replays, and audit queries all require it.

---

## 12. Testing Event-Driven Systems

**Unit:** Test aggregate state transitions in-memory with fake event bus.

```ts
class InMemoryBus {
  published: Envelope[] = [];
  async publish(type: string, payload: unknown) {
    this.published.push({ type, payload, occurredAt: new Date().toISOString() });
  }
}
```

**Contract:** Producer publishes a sample of every event type; consumer tests validate against the registry schema.

**Integration:** Spin up the real broker in Docker (Testcontainers). Drive end-to-end: command in, event out, projection visible.

**Replay tests:** Load a fixture stream; assert read-model state matches expected snapshot. Protects against projection drift during refactors.

**Chaos tests:** Inject duplicate delivery, out-of-order delivery, and consumer crashes. If the suite passes under chaos, production will survive broker upgrades.

---

## 13. Anti-Patterns

- **Event spaghetti.** No bounded contexts, no owners. Refactor by naming owners per aggregate and moving publication rights there.
- **Over-eventification.** Making every state change an event inflates the catalogue and taxes every consumer. Publish only events other contexts need.
- **Event as RPC.** Topic `order.get-request` + topic `order.get-response` is synchronous RPC with extra latency. Use gRPC instead.
- **Leaky payloads.** Publishing internal ORM shapes couples every consumer to your schema. Publish a stable contract.
- **No schema registry.** Schemas live in Slack threads. Introduce a registry before the second consumer joins.
- **No DLQ strategy.** Retries loop forever on poison messages, lagging all healthy events. Always define DLQ + replay path.
- **Ignoring ordering needs.** Payments must process in order per customer. Choose partition keys that respect this; random partitioning corrupts balances.

---

## Minimal Reference Stack for a New SaaS

- Broker: RabbitMQ (if ops-light) or Kafka (if replay/scale).
- Outbox: Postgres `outbox` table + single relay worker per service.
- Schema: JSON Schema + a Git-tracked `schemas/` directory, validated in CI.
- Dedup: Consumer-side `processed_events` table per consumer.
- DLQ: One DLQ per topic; alarm on depth; replay CLI.
- Observability: OpenTelemetry span propagation via `correlation_id` and `causation_id`; Prometheus lag metrics; structured logs with `event_id`.

Load `microservices-communication` for broker-level operational patterns, `multi-tenant-saas-architecture` for tenant isolation strategy, and `observability-monitoring` for lag and DLQ alerting.