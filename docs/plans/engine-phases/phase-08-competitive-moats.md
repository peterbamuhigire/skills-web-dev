# Phase 08: Competitive Moats

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the growth, architecture, and API skills that compound value over time — making products stickier, harder to replace, and more capable of self-distributing.

**Architecture:** Four new skill directories: `product-led-growth` (PLG tactics for SaaS), `event-driven-architecture` (event sourcing and CQRS for scale), `graphql-patterns` (API layer — complements existing `graphql-security`), and `saas-growth-metrics` (instrument and act on product data). These are the skills that separate a product from a commodity.

**Tech Stack:** PostHog (analytics), Mixpanel, RabbitMQ/SQS, EventStore, Apollo Server, GraphQL Federation, Stripe metered events, A/B testing infrastructure.

---

## Dual-Compatibility Contract

Every `SKILL.md` must include:
```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Frontmatter:
```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

Platform Notes only. Validate after every write:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Task 1: Create `product-led-growth` skill

**Files:**
- Create: `product-led-growth/SKILL.md`
- Create: `product-led-growth/references/freemium-design.md`
- Create: `product-led-growth/references/activation-flows.md`
- Create: `product-led-growth/references/viral-loops.md`

**Step 1:** Write `product-led-growth/SKILL.md` covering:

- PLG vs. sales-led: when PLG works (self-serve, short time-to-value, broad ICP), when it does not (enterprise, compliance-heavy, long integration)
- Freemium design: free tier must be genuinely useful (not crippled), limits must be felt before paywall, upgrade prompt appears at the moment of value
- Activation: define the "aha moment" for your product — the action that predicts retention. Design the onboarding flow to reach it in < 10 minutes.
- In-app upgrade prompts: trigger at usage limit, at feature gate, at milestone ("You've processed 100 invoices — unlock unlimited with Pro"). Not on login or after arbitrary time.
- Viral loops: referral mechanics (give-get), team invitations (Slack model), public share links, embed/widget distribution
- NPS implementation: in-app survey at 30 days (not on first login), Promoters → case study pipeline, Detractors → support escalation
- Churn prevention: usage drop alert (< 50% of last month's usage triggers outreach), failed payment proactive outreach, cancellation exit survey + pause offer
- PQL (Product Qualified Lead): define the usage threshold that signals sales-readiness, route to human outreach

Anti-Patterns: a free tier with zero real value, upgrade prompts that appear before user has experienced value, NPS surveys on first login, single-player products with no collaboration hooks.

**Step 2:** Write `references/freemium-design.md` — tier design framework: free limits that are generous enough to attract, tight enough to create upgrade pressure. Limit types: seats, storage, API calls, AI tokens, feature gates. Include example tier matrices for SaaS verticals.

**Step 3:** Write `references/activation-flows.md` — onboarding state machine: signup → verify email → connect data source → first value moment. Progress bar mechanics, milestone emails, in-app checklists, empty state CTAs.

**Step 4:** Write `references/viral-loops.md` — referral program mechanics (code generation, tracking, reward fulfilment), team invite flows, public embeddable widgets, share-to-social triggers.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py product-led-growth
git add product-led-growth/
git commit -m "feat: add product-led-growth skill (freemium, activation, viral loops, NPS, churn prevention)"
```

---

## Task 2: Create `event-driven-architecture` skill

**Files:**
- Create: `event-driven-architecture/SKILL.md`
- Create: `event-driven-architecture/references/event-sourcing-patterns.md`
- Create: `event-driven-architecture/references/cqrs-implementation.md`
- Create: `event-driven-architecture/references/message-broker-patterns.md`

**Step 1:** Write `event-driven-architecture/SKILL.md` covering:

- When to adopt EDA: when you need audit trails, when state reconstruction matters, when multiple services react to the same business event — not for simple CRUD apps
- Domain events: naming convention (`OrderPlaced`, `InvoicePaid`, `SubscriptionCancelled`), payload schema (event_id, aggregate_id, occurred_at, version, data), immutability
- Event sourcing: append-only event store, current state = replay of events, snapshots for performance
- CQRS: separate write model (commands → events) from read model (projections → read-optimised views), eventual consistency trade-off
- Sagas: distributed transaction pattern — choreography (events trigger next step) vs. orchestration (saga coordinator), compensating transactions for rollback
- Message brokers: RabbitMQ (AMQP, topic exchanges, dead-letter queues, consumer ACK) vs. SQS (managed, at-least-once, visibility timeout) vs. BullMQ (Redis-backed, already in nodejs-development)
- Outbox pattern: write event to DB in same transaction as state change, background worker publishes to broker — prevents lost events

Anti-Patterns: event sourcing every entity (only use for aggregate roots with audit requirements), events without version field (schema evolution becomes impossible), synchronous chains disguised as events.

**Step 2:** Write `references/event-sourcing-patterns.md` — EventStore schema, append, load, and snapshot SQL patterns for MySQL and PostgreSQL. State reconstruction example with TypeScript.

**Step 3:** Write `references/cqrs-implementation.md` — command handler → event store → projection worker → read model database pattern. Node.js/TypeScript implementation with BullMQ projection worker.

**Step 4:** Write `references/message-broker-patterns.md` — RabbitMQ topology (exchange, binding, queue) and SQS queue setup. Dead-letter queue pattern, poison message handling, consumer backpressure.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py event-driven-architecture
git add event-driven-architecture/
git commit -m "feat: add event-driven-architecture skill (event sourcing, CQRS, sagas, message brokers, outbox)"
```

---

## Task 3: Create `graphql-patterns` skill

**Files:**
- Create: `graphql-patterns/SKILL.md`
- Create: `graphql-patterns/references/apollo-server-setup.md`
- Create: `graphql-patterns/references/n-plus-one-prevention.md`
- Create: `graphql-patterns/references/graphql-federation.md`

**Step 1:** Write `graphql-patterns/SKILL.md` covering:
- When GraphQL vs. REST: GraphQL for client-driven queries with complex object graphs and multiple consumers; REST for simple CRUD, webhooks, file upload, third-party integration
- Schema-first design: SDL types, queries, mutations, subscriptions, interfaces, unions, custom scalars
- Resolver chain: root resolvers, field resolvers, DataLoader for batching, resolver context (auth, db connection)
- N+1 problem: how it arises, DataLoader batch function, caching within request lifecycle
- Mutations: input types, error handling (union return types — `Success | Error`), optimistic response in client
- Subscriptions: WebSocket transport, subscription resolver, filtering by viewer permissions
- Pagination: cursor-based (Relay Connection spec) vs. offset — always cursor for lists that change
- Persisted queries: client sends query hash, server looks up full query — reduces payload, prevents arbitrary queries in production
- Cross-reference with `graphql-security` for security patterns (depth limiting, complexity analysis, introspection control)

Anti-Patterns: returning raw database row types (leaks schema), no DataLoader (N+1 in production), exposing GraphQL introspection in production without auth, mutations without input validation.

**Step 2:** Write `references/apollo-server-setup.md` — Apollo Server 4 + Express, TypeScript codegen setup, context factory, plugin for logging and tracing, persisted query setup.

**Step 3:** Write `references/n-plus-one-prevention.md` — DataLoader implementation for common patterns: user → posts, order → line items, tenant → users. Batch function examples with TypeScript.

**Step 4:** Write `references/graphql-federation.md` — Apollo Federation v2: subgraph definition, `@key`, `@external`, `@requires`, router (Apollo Router) config — when to use federation vs. schema stitching.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py graphql-patterns
git add graphql-patterns/
git commit -m "feat: add graphql-patterns skill (schema design, DataLoader, federation, subscriptions)"
```

---

## Task 4: Create `saas-growth-metrics` skill

**Files:**
- Create: `saas-growth-metrics/SKILL.md`
- Create: `saas-growth-metrics/references/product-analytics-setup.md`
- Create: `saas-growth-metrics/references/cohort-analysis.md`

**Step 1:** Write `saas-growth-metrics/SKILL.md` covering:
- Metric hierarchy: North Star Metric → L1 metrics (MRR, DAU) → L2 metrics (activation rate, feature adoption) → L3 metrics (task completion, load time)
- MRR decomposition: new MRR + expansion MRR + reactivation MRR − churned MRR − contraction MRR = net new MRR
- Funnel metrics: visitor → trial → activated → paid — conversion rates at each stage, benchmark ranges
- Retention: Day 1, Day 7, Day 30 retention curves; cohort retention heatmap; leading indicator of churn
- Feature adoption: % of active users who have used feature X at least once; adoption velocity by cohort
- A/B testing: hypothesis format, sample size calculator, significance threshold (p < 0.05), minimum detectable effect
- PostHog setup: event naming convention (`user_signed_up`, `feature_used`, `upgrade_clicked`), person properties, group analytics for B2B (tenant-level metrics)
- SQL recipes: MRR by month, churn rate by cohort, feature adoption funnel — all runnable against a standard SaaS schema

Anti-Patterns: tracking every click without a measurement plan, using MAU as North Star (not sensitive enough), running A/B tests with insufficient sample sizes, not filtering internal team from analytics.

**Step 2:** Write `references/product-analytics-setup.md` — PostHog self-hosted install, event taxonomy design, person and group property conventions, funnel and retention report setup.

**Step 3:** Write `references/cohort-analysis.md` — SQL cohort retention matrix query (MySQL + PostgreSQL variants), MRR movement waterfall query, LTV calculation from Stripe data.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py saas-growth-metrics
git add saas-growth-metrics/
git commit -m "feat: add saas-growth-metrics skill (MRR decomposition, funnels, cohort retention, PostHog)"
```

---

## Success Gate

- [ ] `product-led-growth` passes validator, ≤ 500 lines, portable metadata present
- [ ] `event-driven-architecture` passes validator, ≤ 500 lines, portable metadata present
- [ ] `graphql-patterns` passes validator, ≤ 500 lines, portable metadata present — references `graphql-security`
- [ ] `saas-growth-metrics` passes validator, ≤ 500 lines, portable metadata present
- [ ] No `Required Plugins` blockers in any of the four

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | *Product-Led Growth* — Wes Bush | Book | ~$25 | `product-led-growth` full skill |
| 2 | *Building Event-Driven Microservices* — Adam Bellemare | Book | ~$45 | `event-driven-architecture` depth |
| 3 | *Hacking Growth* — Sean Ellis & Morgan Brown | Book | ~$25 | `saas-growth-metrics` tactics |
| 4 | *Learning GraphQL* — Eve Porcello & Alex Banks | Book | ~$40 | `graphql-patterns` schema design |
| 5 | PostHog documentation | Free (posthog.com/docs) | Free | Product analytics setup |
| 6 | Apollo GraphQL documentation | Free (apollographql.com/docs) | Free | Apollo Server + Federation |
| 7 | *Escaping the Build Trap* — Melissa Perri (already in library) | Book | owned | PLG product thinking |

**Read first:** *Product-Led Growth* (short, high-density) then *Building Event-Driven Microservices*.

---

*Next → `phase-09-advanced-ai-rag-depth.md`*
