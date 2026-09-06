[Back to Java Enterprise Development](../SKILL.md)

# Legacy maintenance, migration, and retirement

Use this reference for Java 8/11/17/21-era systems, older Spring and Hibernate,
Java EE `javax.*`, WebLogic/WebSphere/JBoss, WAR/EAR, JSP/Servlet, SOAP, and old
builds. A stable legacy service is not defective merely because it is old; an
unsupported service carrying mission-critical risk is not safe merely because
it still runs.

## Modernisation decision frame

| Dimension | Evidence to collect |
|---|---|
| Business | Critical flows, change demand, incidents, downtime cost, remaining life |
| Support/security | JDK/framework/server/database/OS support and vulnerability exposure |
| Architecture | Modules, dependencies, shared state/database, integrations, deployment coupling |
| Data/correctness | Transactions, stored logic, reconciliation, audit, batch windows, concurrency |
| Delivery | Build reproducibility, source/dependency access, tests, environments, release/rollback |
| Operations | Capacity, telemetry, runbooks, ownership, backup/restore/failover evidence |
| People | Domain knowledge, platform skill, vendor support, on-call capability |

Choose maintenance, in-place upgrade, replatforming, selective extraction,
replacement, or retirement by business risk and evidence. Default against a
big-bang rewrite when critical behaviour is poorly understood.

## Establish a safety net

1. Make the existing build reproducible in an isolated environment and record
   JDK, build tool, repositories, generated sources, server, database, and
   external contracts.
2. Capture characterisation tests around financial/clinical/government or other
   critical behaviour. Use production-derived cases only under approved privacy
   controls; otherwise create reviewed synthetic cases.
3. Baseline APIs/events/files/SOAP, database effects, batch output,
   authorisation, performance/capacity, and operational recovery.
4. Inventory internal/removed JDK APIs, reflection/serialization, agents/JNI,
   deprecated framework APIs, `javax.*`, XML/config, plugins, drivers, and
   vendor extensions.
5. Add release identity and enough logs/metrics/traces/JFR access to compare
   stages. Missing behaviour remains `NOT ASSESSED`, not assumed equivalent.

## Stage the change

Avoid combining all of these in one release: JDK runtime, source/language level,
Spring/Jakarta namespace, ORM, build/plugins, database driver, application
server, packaging, schema, and infrastructure. Official compatibility may
force some grouping; record that constraint and preserve rollback.

Typical stages are:

```text
reproducible current baseline
-> latest supported patch on current generation
-> remove unsupported/internal APIs and fix warnings
-> update build/plugins/tests/drivers within compatibility
-> advance JDK through supported intermediate runtime(s)
-> migrate framework or javax/jakarta boundary
-> change packaging/runtime topology only if justified
-> optimise and retire compatibility code after production evidence
```

The exact path comes from current vendor migration/support evidence. Do not
encode Java 8-to-current, Spring Boot 2-to-current, or WebLogic steps from memory.

## `javax.*` to `jakarta.*`

Treat the namespace move as an ecosystem migration, not a search-and-replace:

- inventory application imports, descriptors, XML namespaces/schema versions,
  generated sources, dependencies, transitive libraries, test utilities,
  providers, agents, application-server APIs, and serialised/public contracts;
- choose a target framework/server that implements the required Jakarta level;
- replace or upgrade incompatible dependencies; use transformation tooling only
  as a controlled stage whose output is reviewed and rebuilt from source;
- test CDI/injection, persistence mappings, validation, transactions, REST,
  servlet/filter/listener, security, messaging, WebSocket, and deployment;
- prevent a mixed namespace classpath unless an explicitly supported bridge
  owns the boundary.

## Monolith and application-server choices

First enforce module boundaries and tests inside the existing deployment. A
modular monolith can reduce change risk without network distribution. Extract a
service only when a bounded capability needs independent ownership, deployment,
scaling, security isolation, or lifecycle and the organisation can operate it.

For application server to executable JAR, retain an inventory of managed data
sources, JNDI, JTA/XA, JMS, security realm, clustering/session, work managers,
shared libraries, classloading, deployment descriptors, diagnostics, and
operational scripts. Each needs an explicit replacement or intentional carry-
forward. The reverse move is equally a platform decision, not packaging alone.

## Compatibility and rollout

- Keep APIs, events, files, and database schema backward compatible through the
  deployment window. Use expand/migrate/contract and tolerant event readers.
- Run old and new behaviour against reviewed cases; reconcile state and side
  effects. Shadow traffic must not duplicate irreversible actions.
- Canary by tenant/user/job/instance where containment and data semantics allow.
- Define rollback before schema/data/contract activation. Prefer roll-forward
  for irreversible migrations and keep the old reader/writer compatibility
  window long enough to recover.
- Retire old runtime, credentials, queues, schemas, flags, and compatibility
  code only after traffic/state/consumer evidence and an owner sign-off.

## Retirement

Retirement requires consumer discovery, legal/retention input from the proper
owner, data export/archive and verification, credential/repository/runtime
revocation, traffic and job removal, observability silence checks, recovery or
record-access plan, and accountable approval. Do not delete data or deployment
assets under this skill without explicit authority.

## Anti-patterns

- Rewrite first, understand later. Characterise critical flows and compare
  incremental options.
- Upgrade every dependency to latest in one pull request. Follow compatible
  trains and preserve causal diagnosis.
- Treat compilation as migration proof. Exercise runtime, data, security,
  integration, performance, failure, and operations.
- Use automated namespace transformation as the final source. Review ownership,
  dependencies, descriptors, generated code, and behaviour.
- Keep unsupported infrastructure indefinitely because migration is risky.
  Quantify current risk and fund the smallest risk-reducing stage.

