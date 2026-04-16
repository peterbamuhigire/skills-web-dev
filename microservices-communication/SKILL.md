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

**See also:**
- `microservices-architecture-models` — Where service discovery is handled (Proxy/Router/Fabric)
- `microservices-resilience` — Retry, timeout, circuit breaker for synchronous calls
- `microservices-ai-integration` — Async AI job queue pattern
- `api-error-handling` — Error response standards for service APIs
