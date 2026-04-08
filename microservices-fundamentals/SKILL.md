---
name: microservices-fundamentals
description: Core microservices concepts — monolith vs microservices trade-offs, decomposition patterns, the 12-Factor App adapted for microservices, bounded contexts, data isolation, and stateless design. Invoke before designing any microservices-based...
---

# Microservices Fundamentals

## What Microservices Are

A **microservices architecture** structures an application as a collection of small, independently deployable services. Each service:
- Owns a single bounded business capability
- Has its own process and data store
- Communicates with others only through well-defined APIs
- Is developed, deployed, and scaled independently

---

## Monolith vs Microservices — Honest Trade-Offs

Do not recommend microservices by default. Make the call deliberately.

| Factor | Monolith | Microservices |
|--------|----------|---------------|
| **Team size** | < 10 developers | 10+ developers (or multiple teams) |
| **Deployment** | One release for everything | Independent per service |
| **Scalability** | Scale the whole app | Scale only bottleneck services |
| **Complexity** | Low (one codebase) | High (network, distributed state) |
| **Technology** | Single stack | Best tool per service |
| **Data** | Shared DB (easy joins) | Separate DB per service (complex queries) |
| **Failure** | One crash = total outage | Service isolation limits blast radius |
| **Testing** | Straightforward integration tests | Requires contract + integration testing |
| **Startup speed** | Fast to start | Slow — many services to orchestrate |

**When to choose microservices:**
- The app has multiple distinct business domains with separate scaling needs.
- Different teams own different capabilities and need independent release cycles.
- One module's load spikes independently (e.g., a reporting service vs. a transaction service).

**When to stay monolithic:**
- Team is small (< 10 developers).
- The bounded contexts are unclear — premature decomposition creates distributed monolith hell.
- It's an MVP or proof of concept.
- The overhead of network communication, distributed tracing, and service orchestration is unjustified.

**Migration path:** Start monolithic → extract services one at a time using the **Strangler Fig pattern** as boundaries become clear.

---

## Decomposition Patterns

### By Business Capability (Recommended)
Align services with what the business *does*, not what the technology *is*.

```
School Management System
├── enrollment-service      (admissions, registrations)
├── academic-service        (grades, reports, transcripts)
├── finance-service         (fees, payments, invoices)
├── communication-service   (notifications, messages)
├── ai-service              (analytics, predictions)   ← separate, gated
└── identity-service        (auth, roles, tenants)
```

### By Subdomain (DDD)
Use Domain-Driven Design bounded contexts. Each subdomain becomes a service boundary. Cross-subdomain communication = API call, never a shared table.

### Strangler Fig (Migration)
Incrementally replace a monolith:
1. Put an API gateway / reverse proxy in front of the monolith.
2. Extract one service at a time — route its traffic to the new service.
3. Leave the monolith in place until all traffic is redirected.
4. Decommission the monolith.

**Key rule:** Never split a service before you understand the boundary. A wrong split creates a distributed monolith — all the complexity of microservices, none of the benefits.

---

## The 12-Factor App — Adapted for Microservices

*Source: Stetson, NGINX MRA Ch. 5*

| Factor | Rule | Microservices-Specific Adaptation |
|--------|------|-----------------------------------|
| **1. Codebase** | One codebase per service in revision control | One Git repo per service (not a monorepo unless using proper tooling) |
| **2. Dependencies** | Explicitly declare and isolate dependencies | Use language dependency manager + Dockerfile for OS deps |
| **3. Config** | Store config in environment variables | `.env` files locally (never committed); Vault or platform secrets in CI/CD |
| **4. Backing Services** | Treat all external services as attached resources | Other microservices are backing services too — swap them by config |
| **5. Build/Release/Run** | Strictly separate build and run stages | Docker image from every commit = deployment artifact; CI/CD mandatory |
| **6. Processes** | Stateless processes | Services must be stateless — store shared state in Redis, not in-memory |
| **7. Data Isolation** | Each service manages its own data | Access another service's data only via its API — never via direct DB query |
| **8. Concurrency** | Scale via process model | Scale each service independently; horizontal scaling by adding instances |
| **9. Disposability** | Fast startup, graceful shutdown | Containers start/stop instantly; queues absorb in-flight work on shutdown |
| **10. Dev/Prod Parity** | Keep all environments identical | Docker containers enforce parity; diff in data can still cause surprises |
| **11. Logs** | Treat logs as event streams | Stream to centralized log system (ELK, Loki) — services never write log files |
| **12. Admin Processes** | Run admin tasks as one-off processes | Spin up a container for migrations/admin tasks, then destroy it |

---

## Bounded Contexts and Data Isolation

**The cardinal rule:** Each service owns its data. No other service may read or write that data directly.

```
❌ WRONG — finance-service queries enrollment DB directly
SELECT balance FROM enrollment.student_accounts WHERE student_id = 42;

✅ CORRECT — finance-service calls enrollment-service API
GET /api/v1/students/42/enrollment-status
→ { "enrolled": true, "programme": "S.4" }
```

**Why this matters:**
- Allows each service to choose its own data store (MySQL, Redis, MongoDB).
- Prevents tight coupling — enrollment-service can change its schema without breaking finance-service.
- Makes services independently deployable.

**Handling cross-service queries (reporting):**
- Use an event-driven approach: each service publishes events; a read-model service consumes them and maintains a denormalized reporting view.
- Or use an API aggregation layer (BFF — Backend for Frontend).

---

## Stateless Services

Services must not hold state in memory between requests.

**Stateful (bad):**
```php
// ❌ — session stored in service memory; breaks horizontal scaling
$_SESSION['cart'] = $cartItems;
```

**Stateless (good):**
```php
// ✅ — session stored in Redis backing service
$redis->set("cart:{$userId}", json_encode($cartItems), 3600);
```

**What goes in backing services:**
- User sessions → Redis
- File uploads → Object storage (S3 / MinIO)
- Job queues → Redis Queue / RabbitMQ / Kafka
- Persistent data → MySQL / PostgreSQL (per-service database)

---

## Key Vocabulary

| Term | Definition |
|------|-----------|
| **Bounded Context** | The boundary within which a domain model is consistent and self-contained |
| **Service Mesh** | Infrastructure layer managing service-to-service communication |
| **API Gateway** | Single entry point that routes, authenticates, and transforms requests |
| **Service Registry** | Database of live service instances (Consul, etcd, Kubernetes DNS, ZooKeeper) |
| **Circuit Breaker** | Pattern that stops calling a failing service to allow recovery |
| **Strangler Fig** | Migration pattern for incrementally replacing a monolith |
| **Sidecar** | A helper container deployed alongside each service instance |

---

**See also:**
- `microservices-architecture-models` — Proxy, Router Mesh, Fabric models
- `microservices-communication` — Service discovery, sync vs async, inter-service auth
- `microservices-resilience` — Circuit breaker, health checks, load balancing
- `microservices-ai-integration` — AI as a microservice, AI gateway, async AI pipelines
