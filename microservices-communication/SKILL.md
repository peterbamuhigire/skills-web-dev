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
❌ Wrong:   finance-service runs SELECT on enrollment_db.student_accounts
```

### Cross-Service Query Patterns

**Problem:** Reporting needs data from 5 services. N synchronous calls = N latency hops.

**Solutions:**

**Option A — API Aggregation (BFF)**
Create a Backend for Frontend service that fans out to multiple services and stitches results.
```
report-service → enrollments API  ┐
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
/api/v1/students/{id}   ← stable, never broken
/api/v2/students/{id}   ← new version with breaking changes
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

## Workflow Automation & Async Orchestration

### n8n Self-Hosted

Install on Docker:

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=automation.example.com
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://automation.example.com
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD_FILE=/run/secrets/n8n_db
      - N8N_ENCRYPTION_KEY_FILE=/run/secrets/n8n_enc
    volumes:
      - n8n_data:/home/node/.n8n
    secrets:
      - n8n_db
      - n8n_enc
```

Core concepts:

- Nodes — building blocks (HTTP Request, Function, IF, Set, Schedule Trigger, Webhook)
- Triggers — how a workflow starts (webhook, schedule, database polling, event)
- Credentials — stored encrypted at rest with `N8N_ENCRYPTION_KEY`, referenced by node configuration
- Executions — each run is logged and retriable from the UI

### n8n for SaaS Automations

Example workflow: Stripe `checkout.session.completed` webhook → n8n enrich → send onboarding email → create Slack channel.

- Webhook Trigger — URL `https://automation.example.com/webhook/stripe`
- HTTP Request — `GET https://api.stripe.com/v1/customers/{{ $json.customer }}` (credentials: Stripe API)
- Set — map Stripe fields to internal schema
- HTTP Request — `POST https://api.example.com/internal/users` to provision the account
- SendGrid — send welcome email template
- Slack — `POST https://slack.com/api/conversations.create` with name `customer-{{ $json.company_slug }}`
- IF — route to SEV2 ticket on any failure (fallback branch)

### Temporal Workflow Orchestration

Temporal separates **workflow code** (durable, deterministic) from **activity code** (side effects, may fail and retry). The workflow engine persists state so crashes resume where they left off.

Minimal TypeScript workflow + activity:

```ts
// activities.ts
export async function chargeCard(customerId: string, amount: number): Promise<string> {
  const charge = await stripe.charges.create({ customer: customerId, amount });
  return charge.id;
}

export async function sendReceipt(customerId: string, chargeId: string): Promise<void> {
  await sendgrid.send({ to: customerId, templateId: "receipt", dynamic: { chargeId } });
}
```

```ts
// workflows.ts
import { proxyActivities, sleep } from "@temporalio/workflow";
import type * as activities from "./activities";

const { chargeCard, sendReceipt } = proxyActivities<typeof activities>({
  startToCloseTimeout: "30s",
  retry: { initialInterval: "1s", maximumAttempts: 5, backoffCoefficient: 2 },
});

export async function onboardingWorkflow(customerId: string, amount: number): Promise<void> {
  const chargeId = await chargeCard(customerId, amount);
  await sleep("5s");
  await sendReceipt(customerId, chargeId);
}
```

```ts
// worker.ts
import { Worker } from "@temporalio/worker";
import * as activities from "./activities";

await Worker.create({
  workflowsPath: require.resolve("./workflows"),
  activities,
  taskQueue: "onboarding",
}).then((w) => w.run());
```

### Temporal Patterns

Key durability and control-flow features:

- Retries with backoff — declared per activity (initial interval, max interval, coefficient, max attempts)
- Timeouts — `startToCloseTimeout` (activity), `scheduleToCloseTimeout` (total including retries), `heartbeatTimeout` (long activities report progress)
- Signals — external events into a running workflow (`workflow.signal('approved')`)
- Queries — read workflow state without mutating it (`workflow.query('getStatus')`)
- Child workflows — decompose long workflows into composable sub-workflows
- Continue-as-new — refresh history when a workflow accumulates too many events

### Temporal vs BullMQ

Decision criteria:

| Factor | Temporal | BullMQ |
|--------|----------|--------|
| Durability | Full workflow history persisted; resumes after crash | Job state in Redis; resumable but limited history |
| Programming model | Write workflow code in TS/Go/Java/Python | Submit jobs to queue with handlers |
| Best for | Multi-step business workflows, long-running processes | Short background jobs, fan-out tasks |
| Ops overhead | Temporal cluster (Cassandra/Postgres, frontend, matching, history services) | Single Redis instance |
| Visibility | Web UI with full execution history | Basic Redis-backed UI |

Rule of thumb — if the workflow is longer than 30 seconds or has multiple external calls with their own failure modes, use Temporal; else BullMQ.

### Apache Airflow

Apache Airflow schedules and orchestrates ETL-style DAGs. Each DAG is a Python file defining tasks and their dependencies.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data-team",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_revenue_sync",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
) as dag:
    extract = PythonOperator(task_id="extract", python_callable=extract_stripe)
    transform = PythonOperator(task_id="transform", python_callable=transform_rows)
    load = PythonOperator(task_id="load", python_callable=load_warehouse)

    extract >> transform >> load
```

XCom passes small values between tasks; sensors wait for external conditions (file arrival, partition availability, API readiness).

### Airflow vs Temporal

- Airflow — batch ETL pipelines with time-based scheduling, data-team ownership, Python-first
- Temporal — business-process workflows (orders, onboarding, refunds), engineering-team ownership, language-agnostic

Don't use Airflow for sub-second latency workflows; don't use Temporal for scheduled nightly ETL.

### Workflow Observability

- Temporal Web UI — every execution visible with full event history, click into any activity to see input/output and retry count
- n8n execution logs — per-workflow execution list with node-level inputs/outputs; filter by status
- Airflow task instance logs — per-task run log, DAG graph view, Gantt view for bottleneck analysis
- All three expose Prometheus metrics for scraping into Grafana

---

**See also:**
- `microservices-architecture-models` — Where service discovery is handled (Proxy/Router/Fabric)
- `microservices-resilience` — Retry, timeout, circuit breaker for synchronous calls
- `microservices-ai-integration` — Async AI job queue pattern
- `api-error-handling` — Error response standards for service APIs
