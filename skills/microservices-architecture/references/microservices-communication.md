# Absorbed Skill: microservices-communication

Original entrypoint: `skills/microservices-communication/SKILL.md`
Active parent skill: `skills/microservices-architecture/SKILL.md`
Status: Absorbed as reference material; this file preserves the old skill content for progressive disclosure.

---
name: microservices-communication
description: Inter-service communication patterns — synchronous (HTTP/REST, gRPC)
  vs asynchronous (events, message queues), service discovery (client-side, server-side,
  DNS-based), inter-service authentication, data isolation rules, and API contract
  design...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Microservices Communication
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Inter-service communication patterns — synchronous (HTTP/REST, gRPC) vs asynchronous (events, message queues), service discovery (client-side, server-side, DNS-based), inter-service authentication, data isolation rules, and API contract design...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `microservices-communication` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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
| Correctness | Service-to-service contract test plan | Markdown doc covering REST/gRPC contracts and async event payload contracts | `docs/services/comm-contract-tests.md` |
| Operability | Async messaging operations note | Markdown doc covering broker choice, partitioning, retention, and DLQ inspection | `docs/services/async-ops-note.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
- Companion skill: `event-driven-architecture` — for event sourcing, CQRS, saga orchestration, outbox, DLQ, and broker selection details when moving beyond basic async messaging.
<!-- dual-compat-end -->
## The Two Communication Styles

### Synchronous (Request/Response)

Caller waits for a response before continuing.

| Protocol | When to Use | Pros | Cons |
|----------|------------|------|------|
| **HTTP/REST** | CRUD operations, external APIs, browser clients | Universal, simple, human-readable | Higher latency, coupling |
| **gRPC** | High-frequency inter-service calls, polyglot services | Binary protocol, ~7× faster than REST, strict contracts via Protobuf | Harder to debug, not browser-native |

**Use synchronous when:**
- The caller needs the response to continue processing (e.g., "get student details before generating invoice").
- The operation is user-facing and latency matters (real-time UI response).
- It's a query (read) with no side effects.

**Avoid synchronous for:**
- Long-running operations (> 2s expected time).
- Triggering workflows across multiple services (cascade of synchronous calls = brittle).
- Anything where partial failure must not block the caller.

### Asynchronous (Event-Driven)

Caller publishes an event or message and continues immediately. One or more consumers handle it independently.

| Broker | When to Use | Throughput |
|--------|------------|-----------|
| **Redis Pub/Sub** | Simple events, low volume, fire-and-forget | Medium |
| **RabbitMQ** | Reliable delivery, complex routing, task queues | High |
| **Kafka** | High-throughput event streams, audit log, replay | Very High |

**Use async when:**
- The operation takes > 2s (AI calls, report generation, file processing).
- Multiple services need to react to the same event (fan-out).
- You need decoupling — the publisher should not know who consumes.
- The operation must survive service restarts (durable queues).

**Example — async AI report generation:**
```
User requests report
→ report-service publishes {job_id, tenant_id, params} to queue
→ HTTP 202 Accepted returned immediately to user
→ ai-worker-service consumes message, calls AI API
→ ai-worker-service stores result, publishes {job_id, status: "complete"}
→ report-service marks job done; user polls /report/{job_id}/status
```

---

## Service Discovery

### The Problem
In a microservices environment, service instances come and go. IP addresses change. You cannot hardcode endpoints.

### Three Approaches

**1. DNS-Based Discovery (Recommended for NGINX MRA)**

A service registry (Consul, etcd, K8s CoreDNS) maps service names to live instance IPs. NGINX queries DNS asynchronously in the background.

```nginx
resolver 127.0.0.1:8600 valid=1s;  # Consul DNS, refresh every 1s

upstream enrollment_service {
    server enrollment.service.consul resolve;  # resolved dynamically
}
```

**Key:** Set `valid=Ns` not relying on DNS TTL — TTL in microservices contexts can be dangerously stale.

**2. Client-Side Discovery**

The calling service queries the registry directly to get instance IPs, then load-balances itself.

```php
// Service client queries Consul HTTP API
$instances = Http::get('http://consul:8500/v1/catalog/service/enrollment-service')
    ->json();
$target = $instances[array_rand($instances)];
$url = "http://{$target['ServiceAddress']}:{$target['ServicePort']}/api/v1/students";
```

- Pro: calling service controls load-balancing strategy.
- Con: every service needs registry client code (language coupling).

**3. Server-Side Discovery (Preferred)**

The API gateway or router mesh handles discovery. Services call a fixed gateway address. No registry knowledge needed in service code.

```
Service A → http://gateway/enrollment/api/v1/students
Gateway → resolves enrollment service from registry → routes to healthy instance
```

This is what the NGINX Proxy and Router Mesh models implement. **Prefer this** — it keeps service code simple.

---

## Inter-Service Authentication

Services must authenticate each other. Do not leave internal APIs open.

| Pattern | How | Use When |
|---------|-----|---------|
| **JWT Propagation** | Gateway validates JWT from client; passes `X-User-Id`, `X-Tenant-Id`, `X-Role` headers downstream | User-context calls where identity matters |
| **Service-to-Service API Key** | Each service has a shared secret per downstream dependency | Background jobs, no user context |
| **mTLS (mutual TLS)** | Both sides present certificates (Fabric Model handles this at NGINX level) | High-security inter-service calls |

**JWT header propagation (PHP/Laravel middleware):**
```php
// After gateway validates JWT, downstream services trust these headers
$userId   = $request->header('X-User-Id');
$tenantId = $request->header('X-Tenant-Id');
$role     = $request->header('X-Role');
// Never re-validate JWT downstream — gateway is the trust boundary
```

**Never expose internal service ports to the public internet.** All external traffic must go through the API gateway. Internal services communicate within a private network.

---

## Data Isolation Rule

*From Stetson's adaptation of Factor 7.*

**The rule:** A service's data belongs to that service alone. No direct database access by another service.

```
✅ Correct: finance-service calls enrollment-service HTTP API to get student status
âŒ Wrong:   finance-service runs SELECT on enrollment_db.student_accounts
```

### Cross-Service Query Patterns

**Problem:** Reporting needs data from 5 services. N synchronous calls = N latency hops.

**Solutions:**

**Option A — API Aggregation (BFF)**
Create a Backend for Frontend service that fans out to multiple services and stitches results.
```
report-service → enrollments API  â”
report-service → finance API      ├→ aggregate → response
report-service → grades API       ┘
```
Adds latency but keeps service boundaries clean.

**Option B — Event-Sourced Read Model**
Services publish events on data change. A reporting service consumes all events and maintains a denormalized read-only view optimised for queries.
```
enrollment-service  →  events bus  →  reporting-db (denormalized)
finance-service     →  events bus  →  reporting-db
grades-service      →  events bus  →  reporting-db
```
Fast queries, eventual consistency.

---

## API Contract Design

Services must not break their callers. Contract discipline is essential.

### Versioning

```
/api/v1/students/{id}   â† stable, never broken
/api/v2/students/{id}   â† new version with breaking changes
```

Run both versions simultaneously during migration. Deprecate v1 only after all callers have migrated.

### Backward-Compatible Changes (safe — no new version needed)
- Adding optional fields to a JSON response.
- Adding new endpoints.
- Adding optional query parameters.

### Breaking Changes (requires new version)
- Removing fields from a response.
- Changing field types or names.
- Changing error response structure.
- Making optional fields required.

### Contract Testing

Each service publishes a contract (OpenAPI spec). Consumer services test against the contract, not the live service. This catches breaking changes before deployment.

```bash
# Example: Pact contract test (consumer-driven)
pact verify --provider enrollment-service --pact-url http://pact-broker/pacts/finance-service
```

---

## Message Queue Patterns

### Task Queue (Point-to-Point)

One producer, one consumer. Used for job dispatch.

```php
// Producer (PHP/Laravel)
dispatch(new GenerateAIReportJob($tenantId, $userId, $params))
    ->onQueue('ai-reports');

// Consumer (Laravel worker)
class GenerateAIReportJob implements ShouldQueue {
    public function handle(AIMeteredClient $ai) {
        $result = $ai->call($this->tenantId, $this->userId, 'report-generation', ...);
        Report::create(['tenant_id' => $this->tenantId, 'content' => $result]);
    }
}
```

### Event Bus (Fan-Out)

One event, multiple independent consumers.

```php
// Publisher
event(new StudentEnrolled($studentId, $tenantId, $programmeId));

// Multiple listeners react independently
EnrollmentAuditListener::class,     // writes audit log
FeeScheduleListener::class,         // creates fee schedule
WelcomeNotificationListener::class, // sends welcome message
AIRiskBaselineListener::class,      // initialises AI risk model
```

---

## Communication Decision Guide

```
Is the caller waiting for a result to continue?
  YES → Synchronous
    Is it high-frequency inter-service (> 1,000/min) and latency-critical?
      YES → gRPC
      NO  → HTTP/REST
  NO → Asynchronous
    Does exactly one service handle each message?
      YES → Task Queue (RabbitMQ / Redis Queue)
      NO  → Event Bus (multiple consumers) → Kafka or RabbitMQ fanout exchange
```

---

## Workflow Automation Engines (Async Orchestration)

Reach for a workflow engine when synchronous request/response is not enough:
the unit of work spans minutes to days, must survive process crashes and
deploys, or has dependency structure (a DAG, or a saga with compensations).

Three engines cover three different shapes of "async":

- n8n — connect SaaS APIs and internal endpoints with low-code; webhook- or
  schedule-triggered.
- Temporal — author durable, long-running workflows in real code with
  exactly-once-effect semantics on activities.
- Airflow — schedule data pipelines (ETL/ELT) where DAG structure is fixed
  and runs are time-boxed.

For deployment topology, full retry semantics, signals/queries, XCom, HA, and
backup discipline see `references/workflow-engines.md`.

### n8n

Visual workflows built from nodes (Code, HTTP Request, Filter, Set, IF) wired
by connections. Triggered by webhooks ("event-driven activation through HTTP
requests") or the Schedule Trigger ("time-based automation"). Credentials are
encrypted at rest with `N8N_ENCRYPTION_KEY`. Every execution is logged and
retriable from the UI.

Self-host on Debian/Ubuntu via Docker (`n8nio/n8n:latest`), PostgreSQL backing
store, Nginx or Traefik in front for HTTPS. Set `N8N_HOST`, `WEBHOOK_URL`,
`DB_TYPE=postgresdb`, and `N8N_ENCRYPTION_KEY_FILE` via secrets. For HA,
enable queue mode (`EXECUTIONS_MODE=queue`) with Redis and run multiple
`n8n worker` processes alongside the main UI/webhook process.

Fits: webhook-to-SaaS glue, ops-owned automations, scheduled exports.
Skip: long-running customer-facing transactional workflows (use Temporal),
complex backfillable batch ETL (use Airflow).

### Temporal

Temporal separates **workflow code** (durable, deterministic) from **activity
code** (side effects, may fail and retry). The Event History is the source of
truth — workers replay it after a crash to rebuild state.

```ts
// workflows.ts — runs inside the Temporal worker, must be deterministic
import { proxyActivities, sleep } from "@temporalio/workflow";
import type * as activities from "./activities";

const { chargeCard, sendReceipt } = proxyActivities<typeof activities>({
  startToCloseTimeout: "30s",
  retry: { initialInterval: "1s", maximumAttempts: 5, backoffCoefficient: 2 },
});

export async function onboardingWorkflow(customerId: string, amount: number) {
  const chargeId = await chargeCard(customerId, amount);
  await sleep("5s");
  await sendReceipt(customerId, chargeId);
}
```

**Determinism rule (mandatory).** Workflow code is replayed from history on
worker restart. Every replay must reach the same decisions, so workflow code
must not call `Date.now()` / `time.Now()`, `Math.random()` / `rand.Int()`,
`os.Getenv()`, or do direct network/filesystem I/O. Use `workflow.Now`,
`workflow.SideEffect`, or push the call into an activity. Violating this
rule corrupts replay and the workflow fails non-deterministically on the next
worker restart.

**Retry policy parameters** (per `docs.temporal.io/encyclopedia/retry-policies`):

| Parameter | Definition | Default |
|-----------|------------|---------|
| Initial Interval | Amount of time that must elapse before the first retry occurs. | 1 second |
| Backoff Coefficient | The value dictates how much the retry interval increases. | 2.0 |
| Maximum Interval | Specifies the maximum interval between retries. | 100 x Initial Interval |
| Maximum Attempts | Specifies the maximum number of execution attempts that can be made in the presence of failures. | unlimited |
| Non-Retryable Errors | Non-Retryable Errors specify errors that shouldn't be retried. | none |

Tune Initial Interval high (e.g. 30s) for downstream APIs with strict rate
limits, and bound Maximum Attempts to escalate noisy failures to humans
rather than retry forever.

**Other control-flow features:**

- Timeouts — `startToCloseTimeout` (one attempt), `scheduleToCloseTimeout`
  (including retries), `heartbeatTimeout` (long activities report progress).
- Signals — async external messages into a running workflow (approval,
  cancellation, payload updates).
- Queries — synchronous, read-only inspection of workflow state without
  mutating it (`workflow.query('getStatus')`).
- Child workflows — decompose long workflows into composable sub-workflows.
- Continue-as-new — refresh history when a workflow accumulates too many
  events.

SDKs: Go, TypeScript, Java, Python, .NET, PHP. Self-host topology covered in
the deep-dive reference.

### Apache Airflow

DAG = "a model that encapsulates everything needed to execute a workflow",
including schedule, tasks, dependencies, callbacks. Tasks are "discrete units
of work that are run on workers" and "come in the form of either Operators,
Sensors or TaskFlow".

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {"owner": "data-team", "retries": 3,
                "retry_delay": timedelta(minutes=5)}

with DAG(dag_id="daily_revenue_sync", default_args=default_args,
         start_date=datetime(2026, 1, 1), schedule="0 2 * * *",
         catchup=False) as dag:
    extract = PythonOperator(task_id="extract", python_callable=extract_stripe)
    transform = PythonOperator(task_id="transform", python_callable=transform_rows)
    load = PythonOperator(task_id="load", python_callable=load_warehouse)
    extract >> transform >> load
```

XCom passes small values between tasks via the metadata DB; sensors wait for
external conditions (file arrival, partition availability, API readiness).

**Pitfalls.** Scheduler latency means tasks can sit in `scheduled` state for
seconds-to-minutes — Airflow is not a sub-second orchestrator. Dynamic DAG
generation evaluated at parse time hammers the scheduler — prefer TaskFlow or
dynamic task mapping for fan-out. XCom is not a queue: store large payloads
in S3/MinIO and pass a pointer in XCom.

### Decision Matrix

| Concern | n8n | Temporal | Airflow |
|---------|-----|----------|---------|
| Programming model | Visual / low-code; JS Code nodes for escape hatch | Workflow-as-code (Go / TS / Java / Python) | DAGs in Python |
| Durability across crashes | Yes (DB-persisted execution history) | Yes (Event History is the source of truth) | Yes (metadata DB) |
| Sub-second step latency | Limited | Designed for it | No (scheduler tick) |
| Long-running (days+) | OK for simple cases | Yes — designed for it | Use sensors / external triggers |
| Authoring audience | Ops / non-engineers | Backend engineers | Data engineers |
| Best fit | SaaS integrations, ops glue | Customer-facing async transactions, sagas, durable retry | Scheduled batch / data pipelines |

Picking rule:

- "Glue this webhook to that API and Slack me on failure" → n8n.
- "This onboarding takes 30 days, must survive deploys, and we cannot lose
  state" → Temporal.
- "Refresh six tables every night and backfill last week" → Airflow.

For shorter background jobs that do not need durable orchestration (image
resize, email send), prefer a simple queue (BullMQ, Laravel queue, RQ) over
Temporal — the cluster overhead is not justified.

### Operational Concerns

- Observability — n8n built-in execution logs; Temporal exports Prometheus
  metrics from server and SDKs (integrate with SigNoz via OTel collector);
  Airflow scheduler/worker metrics via StatsD or OpenTelemetry. All three
  ship structured logs to the central store.
- HA — n8n queue mode + multi-worker; Temporal Frontend/History/Matching
  cluster on Postgres or Cassandra; Airflow active-active scheduler with
  CeleryExecutor or KubernetesExecutor.
- Backup — n8n: Postgres dump + encrypted-credentials file (both required to
  restore). Temporal: persistence DB IS the workflow state — back it up and
  rehearse restore quarterly. Airflow: metadata DB; DAGs live in source
  control.
- Upgrades — pin versions; rehearse on a staging DB clone. Temporal's
  `GetVersion` API lets in-flight workflows take a different code path on
  resume when changing workflow logic in replay-breaking ways.

---

**See also:**
- `references/workflow-engines.md` — n8n / Temporal / Airflow deep dive: deployment topology, full retry semantics, signals/queries/child workflows, XCom, HA, backup, security
- `microservices-architecture-models` — where service discovery is handled (Proxy/Router/Fabric)
- `microservices-resilience` — retry, timeout, circuit breaker for synchronous calls
- `microservices-ai-integration` — async AI job queue pattern
- `api-error-handling` — error response standards for service APIs
- `event-driven-architecture` — broker selection, outbox, sagas
- `realtime-systems` — push channels (WebSocket, SSE) for status updates while a workflow runs
- `distributed-systems-patterns` — idempotency, exactly-once-effect, cross-service consistency tradeoffs
