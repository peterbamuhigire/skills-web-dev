[Back to Java Enterprise Development](../SKILL.md)

# Security, testing, and quality engineering

This reference translates the threat model and risk-based test plan into Java
controls. Use `vibe-security-skill`, `web-app-security-audit`, and
`advanced-testing-strategy` as the owners of generic security and test doctrine.

## Security workflow

1. Trace subject, credential, action, resource, tenant, policy, and audit event
   through the real request, message, batch, and administrator paths.
2. Use a maintained identity provider and framework security integration.
   Validate issuer, audience, signature, expiry, authorised client, scopes or
   roles, and resource ownership. Authentication never substitutes for
   authorisation.
3. Validate and bound data at each transport and deserialisation boundary. Map
   into explicit command/API types; do not bind untrusted input into entities.
4. Use parameterised JDBC, JPA parameters, or jOOQ bind values. Allowlist any
   identifier or sort fragment that cannot be bound.
5. Harden parsers and outbound clients against XXE, unsafe polymorphic
   deserialisation, SSRF, path traversal, archive expansion, command/template
   injection, and unbounded payloads.
6. Keep keys, passwords, certificates, and tokens outside source and artefacts.
   Define retrieval, scope, rotation, revocation, audit, and compromised-secret
   handling; prevent them from entering logs, dumps, traces, or error payloads.
7. Review dependency graph, plugins, repositories, generated code, agents, and
   runtime image as one supply chain. Quarantine unverified coordinates.
8. Test controls at the outer boundary and the domain/resource boundary. A
   controller-only authorisation test cannot prove tenant isolation.

## Spring Security and Jakarta security boundary

| Context | Required design evidence | Typical failure to reject |
|---|---|---|
| Browser session | Cookie attributes, CSRF model, session fixation defence, logout/invalidation, CORS rationale | Disabling CSRF because an endpoint returns JSON |
| OAuth/OIDC resource server | Issuer/audience/trust anchors, claim-to-authority mapping, clock/key rollover behaviour | Decoding a JWT without validating its intended audience |
| Service identity | Workload credential, mutual authentication where required, short lifetime, rotation and authorisation | Treating network location as identity |
| Method security | Stable policy boundary and tests through proxies | Assuming self-invoked or unproxied methods enforce annotations |
| Multi-tenant access | Server-derived tenant context plus subject/action/resource check at data access | Trusting a client-supplied tenant ID |

Do not invent an authentication protocol, password store, token format, or
cryptographic construction. A specialist review is required when established
platform mechanisms cannot meet the requirement.

## Java-specific attack surfaces

- Treat native Java serialisation as hostile at trust boundaries. Prefer an
  explicit, bounded data format and allowlisted types; inventory unavoidable
  legacy use and isolate it.
- Disable external entity and unneeded external-resource resolution in XML
  processing. Test the actual parser factory/configuration in use.
- Constrain reflection, expression languages, script engines, templating, and
  dynamic class loading to trusted inputs. Native-image metadata is not a
  security allowlist by itself.
- Normalise and contain file paths, verify content independently of extension,
  cap sizes/counts, store outside executable/static roots, and scan where the
  threat model requires it.
- Configure outbound HTTP clients with destination policy, DNS/rebinding
  considerations, redirect limits, connection/read deadlines, response limits,
  and safe proxy/TLS behaviour.
- Preserve causal exceptions for operators while returning stable, user-safe
  problem details. Log a failure once at its handling boundary.

## Risk-based test stack

| Layer | Proves | Does not prove |
|---|---|---|
| Unit/property | Domain invariants, edge partitions, rounding, state transitions | Framework wiring, SQL dialect, security filters |
| Component/slice | Mapping, validation, security policy, serialisation, transaction proxy behaviour | Real broker/database/server behaviour when replaced by fakes |
| Integration | Actual migrations, SQL, locks, drivers, identity/broker contracts | Production capacity or failover unless exercised there |
| Contract | Provider/consumer compatibility and event/API evolution | End-to-end business correctness |
| Architecture | Package/module dependency rules | Runtime behaviour |
| Mutation | Whether selected tests detect changed logic | Correct oracle design or integration fitness |
| Load/failure | Latency, throughput, saturation, timeout/retry/recovery behaviour | Every production workload or disaster scenario |

Use real infrastructure through disposable containers or controlled test
environments when database dialect, transaction isolation, broker semantics,
or runtime integration matters. An in-memory substitute is not evidence for
Oracle, PostgreSQL, Kafka, WebLogic, or container-specific behaviour.

## Test design rules

- Start from business invariants and failure consequences, not from methods.
- Control clock, zone, locale, random seeds, generated identifiers, scheduling,
  and external responses. Record seeds for property tests.
- Keep mocks at owned boundaries. Mocking the ORM, database, framework context,
  or every collaborator often tests call choreography instead of behaviour.
- Test parameter boundaries, malformed payloads, duplicate requests/messages,
  stale versions, deadlocks/lock timeouts, downstream timeout, retry exhaustion,
  partial writes, restart, cancellation, and unauthorised cross-tenant access.
- Treat flaky tests as defects. Preserve failure artefacts and eliminate hidden
  time/network/order/shared-state dependencies.
- Report coverage only as one observation. Map critical flows and risks to
  executable tests; do not infer correctness from a percentage.

## Quality-tool selection

| Need | Selection rule |
|---|---|
| Formatting/style | One deterministic formatter and a small project-owned style policy |
| Compiler/static defects | Enable compiler warnings, then select SpotBugs, Error Prone, PMD, or equivalent by defects found and build compatibility |
| Architecture | Add ArchUnit/module tests for boundaries whose violation would create real coupling |
| Dependency risk | Resolve the complete graph, scan known vulnerabilities, review reachability/context, and define patch/exception ownership |
| Broader quality | Use Sonar or equivalent only when findings, exclusions, and release policy are owned; a dashboard is not a gate by itself |

Do not mandate every analyser. Pilot each tool on the repository, tune false
positives without hiding security defects, pin compatible versions, and measure
whether it catches failures not already covered.

## Evidence checklist

- Threat model and auth/authz matrix linked to Java enforcement points.
- Exact JDK/framework/dependency graph used by scans and tests.
- Unit, integration, security, architecture, migration, contract, and failure
  results appropriate to the risk; absent layers marked `NOT ASSESSED`.
- Real database/broker/server identity for integration tests.
- Vulnerability findings with exploitability/context, decision, owner, and due
  date; no silent suppression.
- Test failure artefacts and reproducible commands retained.

## Anti-patterns

- `permitAll`, disabled CSRF/CORS wildcard, or broad role checks used to make a
  test pass. Fix the trust model and write positive and denied-path tests.
- `@SpringBootTest` for every test. Use the smallest layer that proves the risk,
  and retain full-context tests for critical wiring.
- Mockito verification of implementation detail as the main oracle. Assert
  state, result, side effects, contracts, and invariant preservation.
- H2 used as proof of Oracle/PostgreSQL mappings, isolation, or SQL. Run the
  supported production engine or mark those behaviours `NOT ASSESSED`.
- A scanner report treated as secure. Combine threat-led review, configuration,
  runtime, dependency, and abuse-path evidence.

