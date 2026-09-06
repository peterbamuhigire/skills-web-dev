# Enterprise Java capability update

Date: 2026-09-05  
Objective: add one production-grade Java/JVM engineering capability and apply
its measurable requirements contract to the SRS engine.

## Research and source treatment

Eight supplied Markdown conversions were inventoried. Seven were readable and
synthesised; the *Spring in Action* conversion was empty and remains
`NOT ASSESSED`. Publisher metadata was used where available to identify
editions. Unsafe, obsolete, corrupt and provenance-ambiguous material was
quarantined. No book files or extended extracts were copied.

Current claims were independently verified through OpenJDK, Oracle, Spring,
Jakarta EE, Hibernate, Maven, Gradle, Quarkus, Micronaut, Helidon, GraalVM,
JUnit, Testcontainers, OpenTelemetry and relevant vendor/project sources. The
dated claim/source/review ledger is
`docs/source-registers/java-enterprise.md`.

## Architecture and changes

One active route was added:

`skills/languages/java-enterprise-development/SKILL.md`

It progressively loads 14 focused references, six evidence templates, a
transactional enterprise reference scenario, and a 16-case red-team scenario
set. It delegates generic architecture, API, database, security, testing,
cloud, Kubernetes, reliability, SaaS, AI and finance doctrine to existing
owners.

Routing was added to the root router, routing index, overview documents,
catalogue counts and 28 fixtures: 20 Java-positive and eight negative
specialist cases. No alias or additional Java active skill was created.

The SRS engine received an inactive requirements overlay and six links from
elicitation, analysis, validation, traceability, transition and engineering
strategy routes. It adds Java-specific evidence fields and acceptance oracles
without duplicating implementation doctrine or increasing its active count.

## Files created

- `skills/languages/java-enterprise-development/SKILL.md`
- `skills/languages/java-enterprise-development/references/`: language/runtime,
  architecture selection, Spring, Jakarta/runtimes, persistence/Oracle,
  API/messaging, security/testing, build/release, containers/cloud,
  performance/operations, Oracle platforms, legacy, AI and source-study notes
- `skills/languages/java-enterprise-development/templates/`: architecture,
  production readiness, incident, performance, migration and release records
- `skills/languages/java-enterprise-development/examples/enterprise-java-reference.md`
- `skills/languages/java-enterprise-development/examples/red-team-scenarios.md`
- `docs/source-registers/java-enterprise.md`
- `docs/continuous-improvement/enterprise-java-kaizen-2026-09-05.md`
- this update record
- `C:/wamp64/www/srs-skills/02-requirements-engineering/references/java-enterprise-requirements-overlay.md`
- `C:/wamp64/www/srs-skills/docs/updates/2026-09-05-java-enterprise-requirements-overlay.md`

## Files modified

- Engine routing/governance: `AGENTS.md`, `SKILL.md`,
  `docs/skill-routing-index.md`, `docs/skill-aliases.yml` and
  `skills/sdlc-meta/kaizen-improvement-system/SKILL.md`
- Overview/plans: `README.md`, `docs/overview/README.md`,
  `docs/overview/ARCHITECTURE.md`, `docs/overview/PROJECT_BRIEF.md`,
  `docs/overview/TECH_STACK.md`, `docs/plans/INDEX.md` and
  `docs/plans/NEXT_FEATURES.md`
- Deterministic checks: `scripts/routing_fixtures.yml`,
  `tests/test_engine_control_plane.py` and
  `tests/test_all_engine_currentness_policy.py`
- SRS routes: the six owning `SKILL.md` files named in its update record and
  `C:/wamp64/www/srs-skills/README.md`

## Current verified baseline

| Area | Observation on access date |
|---|---|
| Java | 25 LTS; 26 current feature release; 27 GA not established |
| Spring | Boot 4.1.1; Framework 7.0.9; Security 7.1.1 |
| Jakarta EE | 11 released; 12 under development |
| Hibernate | ORM 7.4.7.Final standalone stable; use framework-managed version where applicable |
| Build | Maven 3.9.16 GA; Maven 4 RC; Gradle 9.7.1 |
| Cloud-native | Quarkus 3.33 LTS/3.39 feature; Micronaut 5.1.3; Helidon 4.5.4 |
| GraalVM | 25.3.4.1 observed |
| Test/telemetry | JUnit 6.1.3 standalone, Testcontainers 2.0.5, OpenTelemetry Java 1.65.0 core; managed stacks may pin other compatible versions |
| Oracle | JDBC/UCP 26ai documentation and WebLogic 15.1.1 current documentation reviewed |

This table is a dated observation, not a permanent dependency prescription.

## Validation evidence

| Gate | Result |
|---|---|
| Java skill quick validator | PASS |
| Validation-contract helper | NOT APPLICABLE to language skill path; helper scans direct `skills/sdlc-meta` children only |
| Catalogue guardrail | PASS, 179 active under cap 200, 0 findings |
| Routing smoke test | PASS, 157 fixtures, 143/157 top-one, 157/157 top-three |
| Collision report | PASS for change: ten pre-existing pairs, no Java pair at 0.45 |
| Source-ingestion guardrail | PASS, 0 findings |
| Engine control plane | PASS, 12 engines, 0 findings |
| Cross-engine runtime budget | PASS, 179 skills, 0 findings |
| Repository tests | PASS, 22 tests |
| SRS skill-engine validator | PASS, 157 active, 0 failures |
| SRS routing | PASS, 52/52 top-three |
| SRS engine contract | PASS |
| SRS tests | PASS, 234 tests and 2 skipped with project addopts disabled; configured coverage gate `NOT ASSESSED` because pytest-cov is unavailable |
| Diff whitespace check | PASS in both repositories; line-ending notices only |

Unknown downstream runtime behaviour remains `NOT ASSESSED`.

## Known limitations

- No downstream Java application was compiled or executed.
- Oracle RAC/Application Continuity/Data Guard failover, load, restore,
  rollback and native-image compatibility were not tested.
- Commercial support, licensing entitlement and legal conclusions are
  `NOT ASSESSED`.
- The empty book conversion could not be studied.
- Raw Kaizen score is 84/100; published score is capped at 65/100. The 95
  target requires applied production evidence.

Next routine review: 2026-10-05, with earlier source-driven review triggers
defined in the source register and Kaizen audit.
