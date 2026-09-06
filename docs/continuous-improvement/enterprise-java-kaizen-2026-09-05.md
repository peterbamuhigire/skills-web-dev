# Enterprise Java capability Kaizen audit

Audit date: 2026-09-05  
Scope: Java/JVM engineering route, deep references, evidence templates,
currentness, routing and SRS requirements handoff  
Cycle: Observe -> Baseline -> Select -> Experiment -> Check -> Standardise ->
Teach -> Re-measure

## Outcome and consequence

The outcome is a Java-specific judgement layer capable of guiding long-lived,
regulated and high-availability systems without stealing generic architecture,
security, database, cloud, SaaS, AI or accounting ownership. Failure would
produce plausible Java code without transaction, support, migration, runtime or
recovery evidence.

## Baseline

Before this change the active catalogue had no authoritative Java/JVM route.
Java-specific routing, Oracle integration, JVM incidents, framework selection
and migration playbooks were absent. Generic specialists covered useful
cross-cutting concerns but could not resolve Java-specific implementation
choices. Baseline raw assessment: **18/100**; published score: **18/100**.

## Selected experiment

Add one active Java skill, not a technology-per-skill tree. Put detailed
doctrine in progressively loaded references, reuse cross-cutting specialists,
add deterministic positive and negative routing fixtures, and add an inactive
Java requirements overlay to the SRS engine.

Reversal trigger: split the active route only if measured routing failures show
stable, distinct intents that cannot be resolved by one concise router and deep
references.

## Re-measurement

| Dimension | Weight | Evidence | Raw score |
|---|---:|---|---:|
| Routing and catalogue discipline | 10 | One active route; 179 under cap 200; 157/157 top-three routing; no new collision above 0.45 | 10 |
| Java language, JVM and concurrency | 10 | Feature-state rules, modelling, memory/JIT/GC/JFR and bounded concurrency reference | 9 |
| Framework and architecture judgement | 10 | Spring, Jakarta, app-server and cloud-native choices; modular-monolith bias where justified | 9 |
| Persistence, transactions and Oracle DB | 10 | JDBC/JPA/Hibernate/jOOQ, transaction anomalies, UCP/RAC/AC/Data Guard decision boundaries | 9 |
| APIs, messaging and distributed correctness | 10 | Compatibility, idempotency, outbox/inbox, Kafka/JMS and partial-failure doctrine | 9 |
| Security, testing and supply chain | 10 | Java threat controls, realistic dependency tests, static analysis and provenance gates | 8 |
| Build, release, container and cloud | 10 | Maven/Gradle, BOM/toolchain, OCI image, K8s/JVM memory and release evidence | 9 |
| Performance, observability and incidents | 10 | Measurement contract and symptom-to-evidence JVM runbooks | 9 |
| Legacy lifecycle and maintainability | 10 | Staged Java/Spring/Jakarta/WebLogic migration and retirement rules | 8 |
| Applied production proof | 10 | Engine validators pass; no downstream Java build, load, RAC failover, restore or rollback drill | 4 |
| **Total** | **100** | | **84** |

Published audit score: **65/100**, the mandatory cap.  
Raw capability score: **84/100**.  
Gap-to-95: **11 points**.

The requested 95 target is not claimed. The missing points require target
application evidence, not more prose.

## Hard-case review

Sixteen scenarios exercise JDK upgrades, WebLogic/`javax` modernisation,
latency, container OOM, Hibernate N+1, payment idempotency, Kafka redelivery,
premature microservices, Native Image, Oracle RAC, OIDC, large batch,
deadlocks, untested Java 8, WebFlux selection and Oracle-heavy reporting.
Each response names discriminating evidence and rejects technology-by-fashion.

## Standardised learning

- Current versions live in a dated source register, not permanent doctrine.
- Framework BOM versions and standalone latest versions are separate facts.
- Java work pairs with existing specialists and exposes `NOT ASSESSED`.
- Production means code plus configuration, data, artifact, runtime, telemetry,
  recovery, support and lifecycle.
- Books supply durable concepts only; obsolete and unsafe examples are
  quarantined.
- SRS owns measurable requirements and acceptance oracles; engineering owns
  Java implementation.

## Gap-to-95 plan

| Priority | Gap | Required evidence | Owner | Review trigger |
|---|---|---|---|---|
| P0 | No reference Java project executed | Compile/test/static-analysis/container/smoke evidence for Spring and Jakarta variants | Java capability maintainer | Suitable downstream repositories available |
| P0 | Oracle HA not exercised | Exact certified driver/JDK matrix plus RAC/Application Continuity and Data Guard drills | Java + Oracle DB specialists | Oracle test estate available |
| P0 | No realistic load evidence | Same-workload JVM/native and MVC/virtual-thread/reactive comparisons | Performance owner | Architecture selection requiring comparison |
| P1 | No migration rehearsal | Characterisation tests and staged Java/Spring/`javax` migration on a legacy estate | Modernisation owner | Legacy project supplied |
| P1 | External security review absent | Threat-model and dependency/supply-chain review of generated Java baseline | Security specialist | Before production use |
| P1 | Runtime mirror not validated with new skill | Cross-engine budget/routing validation after host mirror refresh | Runtime maintainer | Next native registry sync |

## Evidence statuses

| Evidence | Status |
|---|---|
| Official-source currentness | PASS |
| Book inventory | PARTIAL: seven readable conversions; empty *Spring in Action* file is `NOT ASSESSED` |
| Skill/catalog/routing structure | PASS |
| Engine unit/guardrail tests | PASS |
| Downstream Java compilation and tests | NOT ASSESSED |
| Load, failover, restore and rollback drills | NOT ASSESSED |
| Legal/licensing approval and commercial entitlements | NOT ASSESSED |
| Independent human production review | NOT ASSESSED |

Next routine review: 2026-10-05. Review earlier on a Java GA/security baseline,
Spring release/security advisory, Jakarta/Hibernate/build-tool generation,
Oracle licensing/WebLogic/JDBC support change, or a newly supplied production
estate.

