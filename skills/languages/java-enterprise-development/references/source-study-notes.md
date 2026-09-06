# Source study notes

Return to [Java Enterprise Development](../SKILL.md).

These notes record independent synthesis from the eight supplied book files.
They are not substitutes for the books and reproduce no chapters or extended
passages. Product, API, lifecycle, security, and version claims are admitted
only after comparison with the current primary-source register.

## Admission method

For each source, separate durable engineering ideas from release-bound recipes.
Use a book for explanation and design judgement; use specifications, JEPs,
official release notes, support policies, and the target build for current facts.
Contradictions and extraction defects are quarantined rather than silently
normalised. An unreadable source is `NOT ASSESSED`.

## Source matrix

| Source | Edition/date and target | Durable contribution | Version-sensitive or rejected material | Engine use |
|---|---|---|---|---|
| *Pro Spring Boot 4* - Felipe Gutierrez and DaShaun Carter | 4th ed., 2026; modern Java/Spring Boot 4 | DI and boundaries, HTTP lifecycle, validation, parameterised data access, transactional tests, security, events, observability | Individual APIs and an internal Java-version inconsistency require target-BOM verification | Strong conceptual and workflow input for Spring production doctrine |
| *255 Java Interview Success Questions* - Jonathan Middaugh | Copyright 2020; edition/publisher and exact Java target `NOT ASSESSED` | Retrieval prompts can expose gaps in language fundamentals | Shallow explanations and demonstrably unreliable examples are not admitted as authority | Question prompts only; no normative doctrine |
| *Learning Java: A Test-Driven Approach* - Joshua Crotts | 1st ed., 2024; Java 22 era | TDD cadence, edge cases, method design, algorithms, complexity, concurrency fundamentals | Simplified or over-general API claims require correction against Java specifications | Testing pedagogy and small-feedback-loop discipline |
| *Mastering Java Spring Boot: Advanced Techniques and Best Practices* | Local author/title metadata conflicts with external listings; date/edition `NOT ASSESSED` | Configuration discipline, testing intent, least privilege, monitoring | Legacy `javax` APIs and retired Spring Security/Sleuth/Springfox/container recipes; provenance is uncertain | Durable concepts only; implementation recipes quarantined |
| *Spring in Action* - Craig Walls | Supplied conversion is empty; edition/date/targets `NOT ASSESSED` | `NOT ASSESSED` | The source contained no readable text | No doctrine admitted |
| *Cloud Native Java* - Josh Long and Kenny Bastani | 1st ed., Aug. 2017; Spring Boot 1.x, Spring 4.2-era, Java EE/`javax` | Platform contract, external configuration, layered and contract testing, failure isolation, observability, continuous delivery | Netflix-era Spring Cloud, old Actuator/OAuth, Cloud Foundry commands and unsafe TLS/credential examples are rejected as current guidance | Historical architecture and operations doctrine only |
| *Spring Boot: Up & Running* - Mark Heckler | 1st ed., Feb. 2021; examples use Java 11, Boot 2.4.0, Spring 5.3.x and `javax` | Autoconfiguration literacy, testability, focused tests, end-to-end reactive reasoning, packaging and operations | Old security adapter, milestone BOM, namespace and init-script recipes are quarantined | Production teaching sequence, verified against the current Boot BOM |
| *Pro Spring Boot 2* - Felipe Gutierrez | 2nd ed., ebook Dec. 2018/copyright 2019; Java 8, Boot 2.0.x, Spring 5.0.x | Boot extension boundaries, messaging breadth, testing, Actuator/Micrometer and integration patterns | The supplied filename says "Spring Boot Messaging"; old APIs, plaintext credentials and client-secret-like examples are rejected | Conceptual messaging and extension guidance only |

## Per-source assessment

### Pro Spring Boot 4

- Identity: Felipe Gutierrez and DaShaun Carter, fourth edition, Springer/Apress,
  2026; the exact examples span a modern Spring Boot 4 generation, but the
  internal Java baseline is not consistent enough to admit without build proof.
- Topics/depth: broad and advanced coverage of Boot configuration, web, data,
  integration, security, events, testing and operations.
- Philosophy: use dependency injection and explicit application boundaries;
  understand the HTTP, transaction and configuration lifecycle behind
  annotations.
- Testing/operations/security: parameterised data access, transactional
  integration tests, validation, observability and security boundaries are
  durable; exact APIs and defaults are time-sensitive.
- Contribution/disposition: strongest current Spring-oriented source in the
  set, admitted for workflow and design judgement after official verification.

### 255 Java Interview Success Questions

- Identity: Jonathan Middaugh, copyright 2020. Publisher, edition, publication
  date and exact Java generation could not be authoritatively established.
- Topics/depth: broad recall questions across language and library basics, but
  shallow explanatory depth.
- Philosophy: useful as retrieval practice, not as an architecture, testing,
  operations or security method.
- Quality concerns: multiple examples or rationales are inaccurate or
  incomplete; no claim is admitted merely because it appears in this source.
- Contribution/disposition: use prompts to discover knowledge gaps, then answer
  from the Java specification, JEPs, official API documentation and executable
  tests.

### Learning Java: A Test-Driven Approach

- Identity: Joshua Crotts, first edition, Springer, 2024; Java 22-era.
- Topics/depth: progressive language learning, method design, collections,
  algorithms, complexity and concurrency through tests.
- Philosophy: build behaviour in small feedback loops, make edge cases
  executable and let tests improve design.
- Testing/operations/security: strongest testing philosophy in the set; it is
  not an enterprise operations or security reference.
- Contribution/disposition: admit TDD cadence and reasoning; correct simplified
  or over-general API statements against current specifications.

### Mastering Java Spring Boot

- Identity: the body attributes Adam Jones/NOB TREX while the supplied filename
  attributes Jennifer Robbins; similar external listings use different
  publisher metadata. Edition and publication date remain `NOT ASSESSED`.
- Topics/depth: configuration, security, data, testing, monitoring and
  deployment presented as an advanced Spring guide.
- Philosophy: encourages separation, least privilege and monitoring, but the
  treatment is uneven and recipe-heavy.
- Quality concerns: `javax.persistence`, retired Spring Security extension
  points, Sleuth, Springfox and old container images make implementation advice
  obsolete; provenance conflict lowers trust further.
- Contribution/disposition: admit only independently corroborated durable
  concepts; quarantine all coordinates, APIs, commands and examples.

### Spring in Action

- Identity/content: the supplied file has zero bytes. Craig Walls is present in
  the filename, but edition, date and Spring/Java target cannot be inferred
  because materially different editions exist.
- Topics, depth and all philosophies: `NOT ASSESSED`.
- Contribution/disposition: none. Recover and identify the exact edition before
  any future study.

### Cloud Native Java

- Identity: Josh Long and Kenny Bastani, first edition, O'Reilly, August 2017;
  Spring Boot 1.x, Spring 4.2-era and Java EE/`javax`.
- Topics/depth: deep system-level treatment of platform contracts,
  Twelve-Factor practice, distributed testing, data/messaging, failure,
  observability and continuous delivery.
- Philosophy: externalise configuration, own service/data boundaries, automate
  delivery and make operation part of development.
- Testing/operations/security: contract testing and operational feedback remain
  valuable; old OAuth, Netflix, Actuator and Cloud Foundry recipes are
  historical. Trust-all TLS and embedded/default credentials are rejected.
- Contribution/disposition: strongest architecture/operations narrative in the
  set, used only as historical durable doctrine.

### Spring Boot: Up and Running

- Identity: Mark Heckler, first edition, O'Reilly, February 2021; examples pin
  Java 11, Boot 2.4.0, Spring 5.3.x and `javax`.
- Topics/depth: moderate-depth end-to-end Boot path including configuration,
  web, data, messaging, reactive stacks, tests, security and packaging.
- Philosophy: understand starters and autoconfiguration, refactor for
  testability and treat reactive design as an end-to-end decision.
- Testing/operations/security: focused slices and full-context tests are
  durable; `WebSecurityConfigurerAdapter`, old BOMs and init-script deployment
  guidance are not current.
- Contribution/disposition: admit teaching sequence and production concerns;
  resolve every implementation against the current managed dependency set.

### Pro Spring Boot 2

- Identity: Felipe Gutierrez, second edition, Springer/Apress; ebook published
  December 2018, copyright 2019. The supplied filename is misleading.
- Targets/topics: Java 8, Boot 2.0.x, Spring 5.0.x, Finchley-era Cloud;
  unusually broad messaging, integration, data, testing, security, Actuator,
  Micrometer and starter-extension coverage.
- Philosophy: use POJOs, dependency injection, explicit extension boundaries
  and appropriate messaging abstractions.
- Testing/operations/security: testing and observability concepts remain useful;
  plaintext credentials, client-secret-like data, old endpoint and security
  APIs are rejected.
- Contribution/disposition: use conceptual messaging and framework-extension
  patterns only after current project documentation and target-build proof.

## Cross-source synthesis admitted

- Prefer short executable feedback loops: compile, test the affected boundary,
  integrate with realistic dependencies, and inspect runtime evidence.
- Make framework behaviour visible. Dependency injection, proxies,
  transactions, serialization, retries, and message acknowledgement are not
  magic and must be understood at their actual boundary.
- Keep domain decisions separate from transport, persistence, and framework
  mechanics without manufacturing layers that add no policy or isolation.
- Design for failure and operation as part of development: configuration,
  telemetry, recovery, deployment, and support lifecycle belong in the result.
- Treat interview-style recall, sample snippets, and old recipes as hypotheses,
  never as proof of a supported production implementation.

## Quarantine rules

- Old `javax.*` examples are migration evidence, not modern Jakarta defaults.
- Removed Spring Security configuration APIs and obsolete tracing/documentation
  integrations must not be generated.
- Trust-all TLS clients, hostname-verification bypasses, public object-store
  defaults, destructive cache commands, and embedded credentials found in old
  examples are security defects, not reusable shortcuts.
- Hystrix, Ribbon, Zuul, annotation-based legacy stream bindings, and old
  Actuator endpoints are historical evidence; current project documentation
  must establish any replacement or retained use.
- Old Docker tags, JDK flags, application-server assumptions, and dependency
  coordinates must be resolved from the target project and current official
  compatibility documentation.
- Any source with conflicting provenance can contribute only independently
  verified durable concepts.
- None of the supplied examples was compiled as part of this engine change;
  claims about their executable correctness are `NOT ASSESSED`.
