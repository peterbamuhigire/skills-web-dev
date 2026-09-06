# Java enterprise currentness register

Owner: engineering-engine maintainer  
Scope: Java/JVM, enterprise frameworks, build/test/observability, and Oracle
integration claims used by `java-enterprise-development`  
Verification/access date: 2026-09-05  
Default review date: 2026-10-05 for active release lines; earlier on a release,
security advisory, support notice, or compatibility change

This register applies the Digital Research source-evaluation and
source-verification contract. Sources are authoritative primary project/vendor
pages (tier 1). A version is a dated observation, not a permanent default.
Downstream work must prefer project/runtime evidence and re-open any record past
its review date.

Status values: `verified`, `context-bound`, `partial`, `stale`, and
`NOT_ASSESSED`. Freshness classes: `stable`, `context-bound`, `time-sensitive`,
`partial`, and `unusable`.

## Verified baseline

| Claim ID | Claim and scope | Source ID | Version/publication date | Freshness/review | Support/status and uncertainty |
|---|---|---|---|---|---|
| JAVA-001 | Java 25 is an LTS line; Oracle lists GA in September 2025 and Premier Support to September 2030 for Oracle customers | SRC-JAVA-ROADMAP | Updated 2026-04-02 | time-sensitive; 2027-03-05 | verified for Oracle's roadmap, not every distribution/licence |
| JAVA-002 | JDK 26 reached GA on 2026-03-17 and is the current non-LTS feature line on the access date | SRC-JDK26, SRC-JAVA-ROADMAP | 2026-03-17 | time-sensitive; 2026-09-16 | verified; Oracle's non-LTS support table ends in September 2026 |
| JAVA-003 | JDK 27 GA was not established by an accessible official GA announcement on 2026-09-05 | SRC-JAVA-ROADMAP | Roadmap forecasts September 2026 | partial; 2026-09-16 | `NOT_ASSESSED` as GA; do not use for production until verified |
| SPR-001 | Spring Boot stable documentation listed 4.1.1; 4.2.0-M1 was preview | SRC-SPRING-BOOT | accessed 2026-09-05 | time-sensitive; 2026-10-05 | verified project-page status |
| SPR-002 | Spring Framework documentation listed 7.0.9 | SRC-SPRING-FW | accessed 2026-09-05 | time-sensitive; 2026-10-05 | verified documentation version |
| SPR-003 | Spring Security documentation listed 7.1.1 stable, 7.2.0-M1 preview | SRC-SPRING-SEC | accessed 2026-09-05 | time-sensitive; 2026-10-05 | verified documentation status |
| SPR-004 | Spring Data 2026.0.1, Batch 6.0.5, Integration 7.1.1, Cloud 2025.1.3, Modulith 2.1.1, Kafka 4.1.1 and AI 2.0.1 were current stable/service lines | SRC-SPRING-PORTFOLIO | 2026-08-20 through 2026-08-26 | time-sensitive; 2026-10-05 | verified release/project listings; exact Boot/Cloud pairing remains context-bound |
| JAK-001 | Jakarta EE 11 was released on 2025-06-26; Jakarta EE 12 remained under development | SRC-JAKARTA-RELEASES | 2025-06-26/accessed 2026-09-05 | time-sensitive; 2026-10-05 | verified; EE 12 must not be treated as production GA |
| JAK-002 | Jakarta EE 11 supports Java 17+, adds Jakarta Data 1.0, and includes Persistence 3.2, REST 4.0, CDI 4.1, Servlet 6.1, Security 4.0, Validation 3.1 and Concurrency 3.1 | SRC-JAKARTA11 | 2025-06-26 | context-bound; 2027-03-05 | verified for Jakarta EE 11 platform/profile pages |
| HIB-001 | Hibernate ORM 7.4.7.Final was the latest stable ORM line; 8.0.0.Beta1 was development | SRC-HIBERNATE | 2026-08-30 | time-sensitive; 2026-10-05 | verified project release status |
| BUILD-001 | Apache Maven 3.9.16 was the recommended GA release; Maven 4.0.0-rc-6 was not GA | SRC-MAVEN | 2026-05-13/2026-08-04 | time-sensitive; 2026-10-05 | verified; do not mandate Maven 4 for production |
| BUILD-002 | Gradle 9.7.1 was the current stable release and supports running on JVM 17 through 26 | SRC-GRADLE-DIST | 2026-08-19/accessed 2026-09-05 | time-sensitive; 2026-10-05 | verified from official release and compatibility pages; toolchain compatibility remains separate |
| QUA-001 | Quarkus recommended 3.33 as the production LTS; 3.39 was the active feature line | SRC-QUARKUS | 2026-03-25/2026-08-26 | time-sensitive; 2026-10-05 | verified; select supported patch and support model at project time |
| MIC-001 | Micronaut release index listed 5.1.3 | SRC-MICRONAUT | 2026-08-31 | time-sensitive; 2026-10-05 | verified release version; public lifecycle calendar remains `NOT_ASSESSED` |
| HEL-001 | Helidon releases listed 4.5.4; Helidon 4 requires Java 21 and recommends Java 25 | SRC-HELIDON | 2026-08-28/accessed 2026-09-05 | time-sensitive; 2026-10-05 | verified release/docs state; commercial support terms require separate review |
| GRAAL-001 | GraalVM release calendar listed 25.3.4.1 on 2026-08-25; release families have distinct distribution/support implications | SRC-GRAAL-CALENDAR | 2026-08-25 | time-sensitive; 2026-10-05 | verified version; licensing/support remains context-bound |
| TEST-001 | JUnit documentation listed 6.1.3 in the 6.1 line; 6.1.0 was released 2026-05-19 | SRC-JUNIT | 2026-05-19/accessed 2026-09-05 | time-sensitive; 2026-10-05 | verified docs listing; use framework-managed version where applicable |
| TEST-002 | Testcontainers for Java documentation listed 2.0.5 and its BOM | SRC-TESTCONTAINERS | accessed 2026-09-05 | time-sensitive; 2026-10-05 | verified; runtime/licensing for each test dependency remains contextual |
| TEST-003 | ArchUnit project page listed 1.4.2 | SRC-ARCHUNIT | 2026-04-18 | time-sensitive; 2026-10-05 | verified release; formal support lifecycle was not published and is `NOT_ASSESSED` |
| OTEL-001 | OpenTelemetry Java traces, metrics, and logs were stable; core 1.65.0 and Java instrumentation 2.31.1 were listed | SRC-OTEL-JAVA | modified 2026-08-28 | time-sensitive; 2026-10-05 | verified page state; semantic conventions may have separate stability |
| OTEL-002 | Micrometer 1.17.1 was current stable with published OSS support for the 1.17 line through July 2027 | SRC-MICROMETER | 2026-08-20 | time-sensitive; 2026-10-05 | verified project release/support table |
| ORA-001 | Oracle WebLogic Server 15.1.1.0.0 is a Jakarta EE 9.1 application server in the current documentation | SRC-WEBLOGIC15 | accessed 2026-09-05 | context-bound; 2026-12-05 | verified product documentation; exact patch/certification requires Oracle support matrices |
| ORA-002 | Oracle Database 26ai JDBC documentation provides JDBC 26/21/19 interoperability and JDK compatibility matrices | SRC-OJDBC26 | accessed 2026-09-05 | context-bound; 2026-10-05 | verified for documented combinations; test exact artefacts/runtime |
| ORA-003 | Oracle JDBC 26ai documents Application Continuity auto-enablement for driver data sources when the database service enables AC/TAC | SRC-ORACLE-AC | accessed 2026-09-05 | context-bound; 2026-10-05 | verified conditionally; safe replay and application acceptance still require tests |

## Source records

| Source ID | Owner/title/scope | URL | Publication/version date | Accessed | Tier | Support/status | Limitation/uncertainty | Review |
|---|---|---|---|---|---:|---|---|---|
| SRC-JAVA-ROADMAP | Oracle, Java SE Support Roadmap; Oracle JDK LTS/non-LTS dates and licence transitions | https://www.oracle.com/java/technologies/java-se-support-roadmap.html | updated 2026-04-02 | 2026-09-05 | 1 | current vendor roadmap | Oracle product/support/licensing scope; not legal advice or other-distribution policy | 2027-03-05 |
| SRC-JDK25 | Oracle, JDK 25 release notes | https://www.oracle.com/java/technologies/javase/25-relnote-issues.html | 2025-09-16 | 2026-09-05 | 1 | GA | Oracle JDK scope; read consolidated updates for patch baseline | 2026-10-05 |
| SRC-JDK26 | Oracle, JDK 26 release notes | https://www.oracle.com/java/technologies/javase/26-relnote-issues.html | 2026-03-17 | 2026-09-05 | 1 | GA | Oracle JDK scope; feature line nears supersession | 2026-09-16 |
| SRC-SPRING-BOOT | Spring, Spring Boot project/stable/preview listing | https://spring.io/projects/spring-boot/ | live project page | 2026-09-05 | 1 | 4.1.1 stable | Patch/support policy can change; use managed dependency set | 2026-10-05 |
| SRC-SPRING-FW | Spring, Spring Framework reference overview | https://docs.spring.io/spring-framework/reference/overview.html | live documentation | 2026-09-05 | 1 | 7.0.9 listed | Commercial/OSS support differs by generation | 2026-10-05 |
| SRC-SPRING-SEC | Spring, Spring Security reference "What's New" | https://docs.spring.io/spring-security/reference/whats-new.html | live 7.1 documentation | 2026-09-05 | 1 | 7.1.1 stable listed | Security patch status can change immediately | 2026-10-05 |
| SRC-SPRING-HIGHLIGHTS | Spring, Boot 4.1 release-train highlights | https://spring.io/projects/release-highlights/ | 2026-06 | 2026-09-05 | 1 | 4.1 train | Overview only; component docs own APIs | 2026-10-05 |
| SRC-SPRING-PORTFOLIO | Spring, portfolio project and release pages for Data, Batch, Integration, Cloud, Modulith, Kafka and AI | https://spring.io/projects/ | 2026-08 releases | 2026-09-05 | 1 | stable/service lines listed | Resolve each component through the chosen Boot/Cloud BOM; Cloud 2025.1.3 direct pairing with Boot 4.1.1 needs CI proof | 2026-10-05 |
| SRC-JAKARTA-RELEASES | Eclipse Foundation, Jakarta EE release index | https://jakarta.ee/release/ | live release index | 2026-09-05 | 1 | EE 11 released; EE 12 WIP | WIP scope can change | 2026-10-05 |
| SRC-JAKARTA11 | Eclipse Foundation, Jakarta EE 11 release/spec profile | https://jakarta.ee/release/11/ | 2025-06-26 | 2026-09-05 | 1 | released | Compatible-product certification remains product-specific | 2027-03-05 |
| SRC-HIBERNATE | Hibernate, ORM releases and compatibility matrix | https://hibernate.org/orm/releases/ | 7.4.7.Final 2026-08-30 | 2026-09-05 | 1 | 7.4 stable; 8.0 development | Framework integrations may pin another supported line | 2026-10-05 |
| SRC-MAVEN | Apache Maven, download/history | https://maven.apache.org/download.cgi | 3.9.16/4.0.0-rc-6 | 2026-09-05 | 1 | 3.9 GA; 4 preview | Plugins have independent compatibility | 2026-10-05 |
| SRC-GRADLE-DIST | Gradle, releases and Java compatibility | https://gradle.org/releases/ | 9.7.1 2026-08-19 | 2026-09-05 | 1 | current stable release | Build runtime and Java toolchain support are distinct; consult versioned upgrade notes | 2026-10-05 |
| SRC-QUARKUS | Quarkus, release history and support status | https://quarkus.io/releases/ | live release index | 2026-09-05 | 1 | 3.33 LTS recommended; 3.39 feature | Community and enterprise support windows differ | 2026-10-05 |
| SRC-MICRONAUT | Micronaut, official release index | https://micronaut.io/tag/release/ | 5.1.3, 2026-08-31 | 2026-09-05 | 1 | current release | Public lifecycle/support calendar not established | 2026-10-05 |
| SRC-HELIDON | Helidon, official releases | https://github.com/helidon-io/helidon/releases | 4.5.4, 2026-08-28 | 2026-09-05 | 1 | current release | Verify exact Java baseline and support contract for target | 2026-10-05 |
| SRC-GRAAL-CALENDAR | GraalVM, release calendar | https://www.graalvm.org/release-calendar/ | 2026-08-25 | 2026-09-05 | 1 | active 25.x lines | Community/Oracle distributions and licence/support differ | 2026-10-05 |
| SRC-JUNIT | JUnit, 6.1 release notes/version navigation | https://docs.junit.org/6.1.0/release-notes.html | 2026-05-19 | 2026-09-05 | 1 | 6.1.3 listed | Build framework may manage a different compatible patch | 2026-10-05 |
| SRC-TESTCONTAINERS | Testcontainers, Java documentation | https://java.testcontainers.org/ | live docs | 2026-09-05 | 1 | 2.0.5 listed | Docker/provider and module-specific constraints apply | 2026-10-05 |
| SRC-ARCHUNIT | ArchUnit, official project page | https://www.archunit.org/ | 1.4.2, 2026-04-18 | 2026-09-05 | 1 | current release observed | Formal support policy not stated | 2026-10-05 |
| SRC-OTEL-JAVA | OpenTelemetry, Java ecosystem/status and releases | https://opentelemetry.io/docs/languages/java/intro/ | modified 2026-08-28 | 2026-09-05 | 1 | traces/metrics/logs stable | Profiles and some semantic conventions remain less stable | 2026-10-05 |
| SRC-MICROMETER | Micrometer, installation and support matrix | https://micrometer.io/support/ | 1.17.1, 2026-08-20 | 2026-09-05 | 1 | current stable and support window listed | Framework BOM may manage a different compatible patch | 2026-10-05 |
| SRC-WEBLOGIC15 | Oracle, WebLogic Server 15.1.1 documentation | https://docs.oracle.com/en/middleware/standalone/weblogic-server/15.1.1/index.html | 15.1.1 docs | 2026-09-05 | 1 | current documented release | Patch set, JDK/OS/database certification and Premier Support require current support matrices | 2026-12-05 |
| SRC-OJDBC26 | Oracle, JDBC 26 getting started/compatibility | https://docs.oracle.com/en/database/oracle/oracle-database/26/jjdbc/JDBC-getting-started.html | Database/JDBC 26ai | 2026-09-05 | 1 | current 26ai guide | Exact JAR, patch and framework compatibility must be resolved in build | 2026-10-05 |
| SRC-ORACLE-AC | Oracle, JDBC Application Continuity | https://docs.oracle.com/en/database/oracle/oracle-database/26/jjdbc/application-continuity.html | Database/JDBC 26ai | 2026-09-05 | 1 | current guide | Requires configured service/driver and application-level acceptance testing | 2026-10-05 |
| SRC-UCP | Oracle, UCP Application Continuity | https://docs.oracle.com/en/database/oracle/oracle-database/26/jjucp/application-continuity-using-ucp.html | UCP/JDBC 26ai | 2026-09-05 | 1 | current guide | Configuration differs for older drivers/servers | 2026-10-05 |

## Primary-source catalogue for task-time verification

Use these source owners rather than copying a fixed version into doctrine:

| Area | Primary source |
|---|---|
| Java language/JVM/JEPs | https://openjdk.org/ and https://jdk.java.net/ |
| Oracle JDK updates/licensing | https://www.oracle.com/java/technologies/ and Oracle licence/support pages |
| Eclipse Temurin | https://adoptium.net/support/ and Adoptium release pages |
| Spring portfolio | https://spring.io/projects/ and https://docs.spring.io/ |
| Jakarta specifications/products | https://jakarta.ee/specifications/ and https://jakarta.ee/compatibility/ |
| Hibernate | https://hibernate.org/orm/ |
| jOOQ | https://www.jooq.org/ and versioned manual/release notes |
| Flyway/Liquibase | Official versioned documentation and release notes |
| Quarkus/Micronaut/Helidon/GraalVM | Official release/support/versioned documentation pages |
| Maven/Gradle | Official download, history, wrapper, dependency and upgrade documentation |
| JUnit/Testcontainers/ArchUnit | Official versioned docs/releases and repository artefacts |
| OpenTelemetry/Micrometer | Official Java/versioned docs, stability and release pages |
| Kafka/Kubernetes | Apache Kafka and Kubernetes versioned documentation |
| Oracle Database/JDBC/UCP/WebLogic/OCI | Oracle Help Center, certification/support matrices, and current service docs |

## Review policy

### Must review

- A Java LTS or feature GA, new Spring Boot/Framework major or supported minor,
  Jakarta EE release, Hibernate major/stable-line change, Maven/Gradle major GA,
  Oracle JDK licensing/support change, WebLogic support/release change, or major
  security advisory affecting admitted guidance.
- Any task whose project version, vendor, database, runtime, or jurisdiction is
  outside a source record's scope.

### Should review

- New Quarkus LTS, Micronaut/Helidon/GraalVM major or support-policy change,
  Testcontainers/JUnit/OpenTelemetry major, Oracle JDBC/UCP/database generation,
  or cloud/Kubernetes compatibility change.

### Routine patch

Do not rewrite doctrine for every patch. Update the register when the patch
changes the recommended supported baseline, fixes a relevant security defect,
alters compatibility, or invalidates a command/API. Downstream builds should
consume compatible managed patches and retain their own evidence.

## Unresolved records

| Item | Status | Required evidence |
|---|---|---|
| JDK 27 GA on 2026-09-05 | `NOT_ASSESSED` | OpenJDK/Oracle GA announcement and release notes |
| Exact commercial support/licence for a chosen JDK, Spring, Oracle, Red Hat, IBM, or other distribution | context-bound | Contract, deployment and counsel/procurement review |
| WebLogic exact patch/certification matrix for a target estate | `NOT_ASSESSED` | My Oracle Support/public certification matrix for OS/JDK/database/patch |
| Oracle RAC/Data Guard/Application Continuity production behaviour | `NOT_ASSESSED` | Target service configuration plus controlled failover/switchover evidence |
| Framework benchmark superiority | `NOT_ASSESSED` | Same workload/environment and measured operational trade-offs |
