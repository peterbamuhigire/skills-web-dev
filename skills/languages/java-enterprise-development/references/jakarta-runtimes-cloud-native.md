# Jakarta Runtimes and Cloud-Native Reference

Parent skill: [Java Enterprise Development](../SKILL.md)

This reference is a production decision aid for Jakarta EE specifications,
application servers, standalone runtimes, and native deployment. It covers
portable contracts and the places where the contract stops: vendor JNDI,
classloading, clustering, recovery, build-time analysis, and operations. The
decision rules are authored synthesis from the cited official sources. They do
not certify a runtime or replace a target-server test.

## Start with the deployment contract

Name the required specifications, packaging unit, resource bindings, transaction
model, messaging model, lifecycle, observability, and recovery path before
choosing a runtime. Jakarta EE publishes platform and profile specifications,
individual specification documents, Javadocs, TCKs, and compatible
implementations ([Jakarta EE specifications](https://jakarta.ee/specifications/)).
Use that evidence to separate a portable application contract from a product
configuration contract (synthesis).

### Profile and runtime selection

| Requirement | Starting point | Move to another choice when | Evidence required |
| --- | --- | --- | --- |
| REST or small service with the essential APIs | Jakarta EE Core Profile or a standalone runtime | Persistence, transactions, messaging, or full container services are required | Profile API inventory, packaged smoke, and dependency scan |
| Web application with persistence, security, and transactions | Jakarta EE Web Profile | Enterprise modules or full platform services are part of the contract | WAR deployment, resource bindings, transaction test, and probe behaviour |
| Coordinated enterprise modules or legacy full-platform APIs | Full Jakarta EE Platform on a compatible application server | The required services are narrower and an embedded or standalone shape removes material operating cost | EAR/WAR deployment, server support statement, failover, and recovery test |
| Standalone cloud service | Quarkus, Micronaut, Helidon, or a Spring runtime chosen by measured constraints | An application-server contract, shared JNDI, container-managed JMS, or XA recovery is required | JVM and native artefacts, configuration, probes, shutdown, and load evidence |
| Native executable | GraalVM Native Image through a framework integration | Reflection, dynamic class loading, runtime-generated proxies, or tooling compatibility cannot be controlled | Reachability metadata, native integration tests, debug plan, and rollback artefact |

Profiles are subsets of the platform for particular application classes; they
are not interchangeable labels. The official platform guide describes Core,
Web, and full-platform use cases and packaging expectations
([Jakarta EE platform guide](https://jakarta.ee/learn/specification-guides/jakarta-ee-platform/)).
Select the smallest profile that contains the required contract, then verify the
actual compatible product and its supported Java runtime (synthesis).

## The `javax` and `jakarta` boundary

The namespace transition changed enterprise API packages from `javax.*` to
`jakarta.*`. The official platform specification records that the transition is
not source-code or binary compatible with the preceding namespace
([Jakarta EE platform migration notes](https://jakarta.ee/specifications/platform/9/jakarta-platform-spec-9)).
Treat this as an API and packaging migration, not a search-and-replace task
(synthesis).

Before changing the namespace, inventory:

- imports, annotations, descriptors, persistence metadata, and generated code;
- application-server modules and libraries that still expose `javax.*`;
- providers, drivers, client libraries, test fixtures, and build plugins;
- serialised class names, reflection strings, service-loader files, and
  configuration keys; and
- the target server's profile, compatible-product entry, and supported Java
  runtime.

Do not mix `javax.*` and `jakarta.*` APIs in one boundary unless the adapter,
classloader isolation, and test evidence are explicit. A successful compile is
not proof that the runtime has one coherent API namespace (synthesis).

## WAR, EAR, JAR, and server boundaries

Use a WAR when the deployable unit is a web application with a clear context
and resource contract. Use an EAR when several modules must be assembled as
one application with shared application scope, coordinated deployment, or
server-managed module relationships. Do not introduce an EAR solely to retain
historical packaging. The platform specification defines standalone modules
and multi-module applications, including WAR and EAR deployment units
([Jakarta EE platform specification](https://jakarta.ee/specifications/platform/11/jakarta-platform-spec-11.0.pdf)).

Keep deployment descriptors and annotations focused on deployment metadata.
Put business policy in application code that can run without the server. For a
WAR or EAR, record:

- module contents and ownership;
- `META-INF` and `WEB-INF` resources that are required at deployment;
- JNDI names and their scope;
- container-managed transactions and resource adapters;
- classloader visibility and excluded or shared libraries; and
- start, stop, health, failover, rollback, and migration behaviour.

The packaging rules and evidence list above are an operational synthesis of the
platform contract and deployment concerns.

An application-server deployment is a contract with the server administrator.
The server owns resource provisioning and container lifecycle; the application
must state what it expects and what it does when the expectation is absent
(synthesis).

## JNDI, JTA, and JMS semantics

### JNDI

Jakarta EE defines component, module, application, and global naming scopes.
The platform specification describes `java:comp`, `java:module`, `java:app`, and
`java:global`, with scope and deployment behaviour that must be respected by a
portable application ([Jakarta EE naming requirements](https://jakarta.ee/specifications/platform/11/jakarta-platform-spec-11.0.pdf)).

Prefer application-scoped or component-scoped names for resources owned by one
deployment. Use global names only when cross-application sharing is deliberate,
documented, and tested. Treat the name, type, authentication, pool, timeout,
transaction enlistment, and ownership as one resource contract (synthesis).

### JTA

Jakarta Transactions defines interfaces for transaction demarcation and
coordination with XA-aware resource managers
([Jakarta Transactions](https://jakarta.ee/specifications/transactions/2.0/jakarta-transactions-spec-2.0.html)).
Prefer a local transaction plus an idempotent workflow or outbox when resources
do not need atomic coordination. Choose JTA or XA only when the invariant
requires atomic resource participation and the target server, drivers,
recovery logs, timeout policy, and operator recovery have been exercised
(synthesis).

For each JTA flow, record:

- transaction owner and propagation boundary;
- enlisted resources and their XA support;
- timeout, isolation, rollback, and heuristic outcome policy;
- recovery log location and ownership; and
- what a partially completed external effect requires the operator to do.

Do not claim that JTA makes a remote service call atomic. XA covers enlisted
resource managers, not arbitrary HTTP APIs or a second deployment's business
state (synthesis).

### JMS

Jakarta Messaging provides point-to-point and publish-subscribe messaging. Its
administered objects, including connection factories and destinations, are
normally provisioned by the provider and made available through JNDI
([Jakarta Messaging API](https://jakarta.ee/specifications/platform/10/apidocs/jakarta/jms/package-summary),
[Jakarta Messaging specification](https://jakarta.ee/specifications/messaging/)).
Record acknowledgement, redelivery, ordering, duplicate handling, poison
message routing, expiry, replay, and shutdown behaviour. Provider-specific
administration is part of the deployment contract; do not hide it behind a
portable API claim (synthesis).

## Classloading and clustering

The Jakarta EE platform deliberately does not prescribe one classloader
hierarchy. Portable applications must rely on visibility requirements rather
than a vendor's loader arrangement; the platform also describes the context
classloader for dynamically loading application classes
([Jakarta EE classloading requirements](https://jakarta.ee/specifications/platform/11/jakarta-platform-spec-11.0.pdf)).

Use the following classloading test matrix for every server upgrade or library
override (synthesis):

- server-provided API versus application-bundled API;
- provider implementation versus application client library;
- shared library versus module-private library;
- thread context classloader at startup, request, message, and shutdown; and
- service-loader and reflection discovery.

Do not solve a linkage error by copying another API implementation into the
archive. First identify the owner of the API, the provider, and the classloader
that loaded each class (synthesis).

Jakarta EE naming scope may extend across an application-server instance, and
the specification notes that the meaning of an instance may include a cluster
but is product-dependent. Clustering, session replication, singleton state,
timers, caches, JMS consumers, and transaction recovery therefore require
vendor-specific evidence; they are not portable consequences of deploying an
EAR or WAR (synthesis).

## Runtime trade-offs

The following comparison is an explicit synthesis of the cited runtime
documentation and the production evidence each option still requires.

The application-server families that must be recognised include WildFly,
Red Hat JBoss EAP, Open Liberty, IBM WebSphere Liberty, Payara, GlassFish and
Oracle WebLogic. A dated observation on 2026-09-05 found JBoss EAP 8.1
documentation, Open Liberty/WebSphere Liberty 26.0.0.8, Payara Community
7.2026.8, GlassFish 8.0.4 and WebLogic 15.1.1 documentation. These are
currentness clues, not a universal compatibility set. Resolve the target's
edition, patch, JDK, Jakarta/Java EE level, OS, database, support entitlement
and upgrade path from its vendor matrix before design or migration
([JBoss EAP 8.1](https://docs.redhat.com/en/documentation/red_hat_jboss_enterprise_application_platform/8.1),
[Open Liberty releases](https://openliberty.io/blog/),
[WebSphere Liberty support](https://www.ibm.com/support/pages/node/7282043),
[Payara releases](https://github.com/payara/Payara/releases),
[GlassFish releases](https://github.com/eclipse-ee4j/glassfish/releases),
[WebLogic 15.1.1](https://docs.oracle.com/en/middleware/standalone/weblogic-server/15.1.1/index.html)).
WildFly release/support selection remains project-time `NOT ASSESSED` in this
register and must be checked through the official WildFly release and
documentation pages.

| Runtime choice | Where it fits | Cost or failure mode to prove |
| --- | --- | --- |
| Traditional Jakarta application server | Existing WAR/EAR, JNDI, JTA, JMS, resource adapters, and vendor operations are material | Server configuration, classloading, patch cadence, cluster behaviour, recovery, and exit cost |
| Quarkus | A standalone service needs build-time processing, framework extensions, or an optional native executable | Native closed-world constraints, build time, extension compatibility, and JVM-versus-native performance |
| Micronaut | Compile-time dependency injection and AOP fit a service that values less runtime reflection and a small runtime model | Compile-time generated metadata, integration coverage, debugging model, and migration cost |
| Helidon SE | A small standalone service benefits from direct APIs and no application-server dependency | More application-owned wiring and fewer container services; prove lifecycle, telemetry, and resource management |
| Helidon MP | A standalone service wants MicroProfile and Jakarta-style APIs without a full server | Profile coverage, implementation boundaries, and portable deployment assumptions |
| GraalVM Native Image | Startup, density, or distribution shape justifies ahead-of-time compilation | Reflection, proxies, resources, JNI, class initialisation, build toolchain, diagnostics, and native-only regressions |

Quarkus documents JVM and native modes, build-time processing, and native
integration testing; its native guide also directs attention to the closed-world
and toolchain constraints ([Quarkus native build](https://quarkus.io/guides/building-native-image/)).
Micronaut documents compile-time dependency injection and compile-time AOP
without runtime reflection for those mechanisms
([Micronaut guide](https://docs.micronaut.io/latest/guide/)).
Helidon documents SE and MP programming models, with MP adding MicroProfile and
Jakarta APIs on a standalone runtime
([Helidon MP introduction](https://helidon.io/docs/v4/mp/introduction)).

GraalVM Native Image performs static reachability analysis under a closed-world
assumption. Dynamic reflection, proxies, resources, and JNI may require
reachability metadata; missing metadata can become a runtime failure
([GraalVM Native Image](https://www.graalvm.org/latest/reference-manual/native-image/),
[GraalVM reachability metadata](https://www.graalvm.org/latest/reference-manual/native-image/metadata/)).
Choose native execution only after the packaged native artefact passes the same
business, security, integration, probe, shutdown, and recovery checks as the
JVM artefact (synthesis).

For Jakarta compatibility, use the official compatible-product and TCK evidence
as a starting point. Compatibility does not prove vendor configuration,
performance, clustering, support response, or application correctness
([Jakarta compatible products](https://jakarta.ee/compatibility/),
[Jakarta compatibility process](https://jakarta.ee/committees/specification/compatibility/)) (synthesis).

## Failure and evidence matrix

This matrix is an operational synthesis; it does not claim that a specification
or product supplies the listed test evidence automatically.

| Boundary | Required decision | Failure test |
| --- | --- | --- |
| Deployment | profile, archive, descriptor, resource names, and server owner | missing binding, invalid descriptor, and rollback of a failed deployment |
| Namespace | one coherent `javax.*` or `jakarta.*` contract per boundary | transitive old API, provider mismatch, generated-code drift, and runtime linkage |
| JNDI | scope, type, pool, credentials, timeout, and transaction enlistment | missing name, wrong type, stale resource, and redeploy |
| JTA | local or XA, timeout, recovery, and partial-effect policy | deadlock, timeout, crash during prepare or commit, and recovery replay |
| JMS | acknowledgement, redelivery, ordering, poison route, and replay owner | duplicate, provider outage, listener stop, and uncommitted work |
| Classloading | visibility owner and context classloader expectation | duplicate classes, service-loader failure, reflection failure, and server patch |
| Cluster | state ownership, routing, replication, and recovery owner | node loss, session loss, duplicate consumer, split-brain risk, and failback |
| Native | metadata, build environment, supported features, and rollback artefact | native-only startup, resource, proxy, TLS, diagnostic, and shutdown failure |

Missing failover, restore, native, classloading, or target-server evidence is
`NOT ASSESSED`. A compatible product listing is evidence of a compatibility
claim, not proof of this application's production readiness (synthesis).

## Specialist handoffs

Keep this reference focused on Java runtime semantics. Route generic identity,
authorisation, secrets, threat modelling, and supply-chain controls to
`vibe-security-skill` and `web-app-security-audit`. Route service topology,
containers, cluster policy, and deployment architecture to
`cloud-architecture`, `kubernetes-platform`, and
`deployment-release-engineering`. Route AI model choice, prompt/data policy,
agent permissions, evaluation, and AI-specific observability to
`ai-llm-integration`, `ai-security`, `ai-evaluation`, and
`ai-observability-and-debugging`. The Java decision remains the adapter and
failure boundary, not a duplicate of those owners (synthesis).

## Source and currentness record

Access date for this research wave: 2026-09-05. The cited pages are official
Jakarta, Eclipse, framework, or vendor documentation. They support the stated
specification and runtime capability boundaries; compatibility with a particular
application, server build, Java runtime, or deployment target remains
`NOT ASSESSED` until tested. Publication or revision dates are not stated on
every current page; that is a gap. Re-check time-sensitive support, compatibility,
and native-toolchain claims before a release. Freshness is stable for the
specification concepts and context-bound for product support (synthesis).

| Source ID | Source scope | Publication or version date | Access date | Freshness and review date | Support status | Confidence and uncertainty | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S-JAKARTA-PLATFORM | Jakarta EE specifications, profiles, migration, packaging, naming, classloading, and compatible-product pages linked below | The cited pages expose historical and current release material; exact page revision dates are not stated on every page (gap) | 2026-09-05 | Stable specification concepts; review 2026-09-05 and before a profile, server, or namespace change | Verified for the documented specification boundary | High for specification scope; target-server portability and support `NOT ASSESSED` | Java capability owner |
| S-JAKARTA-RESOURCE | Jakarta Transactions and Jakarta Messaging sources linked below | Exact page revision date not stated on every page (gap) | 2026-09-05 | Stable API concepts; review 2026-09-05 and before a resource-provider change | Verified for the documented API boundary | High for API scope; provider recovery, XA, and redelivery behaviour `NOT ASSESSED` | Java capability owner |
| S-JVM-RUNTIMES | Quarkus, Micronaut, Helidon, and GraalVM sources linked below | Exact page revision date not stated on every page (gap) | 2026-09-05 | Context-bound; review 2026-09-05 and before a runtime, native toolchain, or deployment change | Verified for the documented runtime capability | High for page scope; local build, native compatibility, and operating evidence `NOT ASSESSED` | Java capability owner |

- [Jakarta EE specifications](https://jakarta.ee/specifications/)
- [Jakarta EE platform guide](https://jakarta.ee/learn/specification-guides/jakarta-ee-platform/)
- [Jakarta EE platform migration notes](https://jakarta.ee/specifications/platform/9/jakarta-platform-spec-9)
- [Jakarta EE platform specification](https://jakarta.ee/specifications/platform/11/jakarta-platform-spec-11.0.pdf)
- [Jakarta Transactions](https://jakarta.ee/specifications/transactions/2.0/jakarta-transactions-spec-2.0.html)
- [Jakarta Messaging specification](https://jakarta.ee/specifications/messaging/)
- [Jakarta Messaging API](https://jakarta.ee/specifications/platform/10/apidocs/jakarta/jms/package-summary)
- [Jakarta compatible products](https://jakarta.ee/compatibility/)
- [Jakarta compatibility process](https://jakarta.ee/committees/specification/compatibility/)
- [Quarkus native build](https://quarkus.io/guides/building-native-image/)
- [Micronaut guide](https://docs.micronaut.io/latest/guide/)
- [Helidon MP introduction](https://helidon.io/docs/v4/mp/introduction)
- [GraalVM Native Image](https://www.graalvm.org/latest/reference-manual/native-image/)
- [GraalVM reachability metadata](https://www.graalvm.org/latest/reference-manual/native-image/metadata/)
