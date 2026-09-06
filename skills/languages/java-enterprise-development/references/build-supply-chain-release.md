[Back to Java Enterprise Development](../SKILL.md)

# Build, dependencies, supply chain, and release

Use this reference to make a Java build reproducible, attributable, and
promotable. Pair it with `cicd-pipelines`, `deployment-release-engineering`, and
the security route; they own pipeline and release architecture.

## Inspect before changing

Record the wrapper and build-tool version, JDK running the build, Java
toolchain/release target, modules, parent/BOM/platform, repositories, plugin and
dependency locks, generated sources, integration-test lifecycle, packaging,
publishing, CI tasks, credentials, and produced artefact identity.

Run only repository-supported wrapper commands. On Windows this may be
`mvnw.cmd` or `gradlew.bat`; on POSIX it may be `./mvnw` or `./gradlew`. Never
invent a task, profile, module, or scanner because it is common elsewhere.

## Maven decision rules

- Put shared versions and constraints in dependency management, preferably an
  official framework BOM where the framework owns compatibility.
- Put plugin versions/configuration in plugin management; ensure lifecycle
  bindings execute in CI, not only an IDE.
- Use the Wrapper and verify its distribution URL/checksum policy. Keep the POM
  effective model understandable; profile combinations must not define an
  untestable product matrix.
- Use Enforcer or equivalent checks selectively for JDK/tool version,
  dependency convergence, banned dependencies, and repository policy.
- Separate fast unit tests from integration/system tests only when the pipeline
  still has an explicit task that runs both before release.
- Treat Maven 4 as a migration decision until the official source register
  marks a GA line compatible with the project plugins and CI.

## Gradle decision rules

- Commit and use the Wrapper. Define Java toolchains; do not rely on whichever
  JDK starts the daemon.
- Use dependency constraints/platforms and locking where reproducibility or
  controlled updates require them. Verify lock updates in review.
- Adopt version catalogues only when they reduce duplicated version ownership;
  they do not replace compatibility platforms.
- Make tasks configuration-cache/build-cache compatible where the measured
  benefit justifies plugin and build-logic work. Never trade correctness for a
  cache hit.
- Isolate convention plugins/build logic and test it. Keep multi-project
  dependencies explicit and acyclic.
- Choose Groovy or Kotlin DSL based on existing team/build evidence. A DSL
  rewrite with no delivery benefit is churn.

## Dependency admission

For every new library or plugin record:

| Question | Evidence |
|---|---|
| Does the coordinate and requested API exist? | Resolve it from an approved repository and inspect official docs for the pinned version |
| What requirement does it satisfy better than JDK/framework/local code? | ADR or concise dependency decision |
| Is it maintained and compatible with the JDK/framework/runtime? | Release/support/security evidence |
| What transitive graph, native/reflection, licence, data, and operational effects follow? | Resolved graph and specialist review where needed |
| Who owns updates, CVEs, configuration, and removal? | Named owner and trigger |

Reject repositories added to resolve one unexplained artefact, dynamic/changing
versions, unverified plugin portals, version ranges in release builds, and
dependencies copied from generated answers without registry verification.

## Reproducible release path

1. Pin the wrapper distribution and dependency/plugin constraints permitted by
   project policy. Isolate secrets and authenticate internal repositories.
2. Start from a clean checkout with declared JDK/toolchain. Restore only from
   trusted repositories; record checksums/signatures where the chosen tooling
   supports them.
3. Compile with warnings policy; run unit, integration, architecture, security,
   migration, packaging, and applicable failure/performance gates.
4. Build the deployable JAR, WAR, EAR, container image, or native executable
   once. Record commit, version, dependency graph, JDK, build tool, timestamp
   policy, and digest.
5. Produce an SBOM in the organisation's accepted format and scan the final
   artefact/image, not merely the source manifest. Review findings in context.
6. Sign or attach build provenance where required and supported. Keep signing
   keys outside CI logs and untrusted runners.
7. Promote the same immutable artefact through environments. Apply schema
   expansion before code that needs it; delay contraction until old consumers
   are gone.
8. Run post-deploy smoke, telemetry, and business-invariant checks. Exercise or
   document roll-forward/rollback decision rights, including irreversible data
   realities.

## Version and compatibility discipline

- Distinguish build JDK, language level, bytecode target, test runtime, and
  production runtime. Prove cross-runtime compatibility rather than assuming it.
- Prefer framework-managed dependency sets unless an override has a documented
  defect/security reason and compatibility test.
- Update one compatibility unit at a time: JDK, framework train, persistence,
  driver, build/plugins, or server. Combine only when official compatibility
  requires it and the rollback boundary remains clear.
- Treat generated clients, annotation processors, agents, JNI/native libraries,
  container base, certificates, and database drivers as dependencies.

## Supply-chain response

When a dependency is compromised or vulnerable, preserve the resolved graph and
artefact identities, identify affected builds/deployments, check reachability
and mitigations, revoke credentials if exposure is plausible, rebuild from a
trusted state, redeploy, and verify. Do not silently suppress a CVE because a
fixed version is inconvenient; record risk acceptance and expiry.

## Evidence checklist

- Wrapper/version/toolchain and repository policy.
- Resolved dependency/plugin graph and convergence/lock result.
- Clean build plus test/analysis/migration/package results.
- Immutable artefact digest, SBOM, scan disposition, signature/provenance status.
- Deployment, release marker, smoke, telemetry, migration, and rollback/forward
  evidence with owner.
- Any unavailable signing, reproducibility, scan, or deployment proof marked
  `NOT ASSESSED`.

## Anti-patterns

- Running a globally installed build tool while CI uses a wrapper. Use and test
  the repository's declared wrapper.
- Declaring a build reproducible because it passed twice on one machine. Control
  inputs and compare artefact metadata/digests under the stated policy.
- Updating dependencies by version number alone. Read compatibility and
  migration notes, run the actual graph and behavioural tests.
- Rebuilding separately per environment. Promote one immutable artefact and
  inject validated runtime configuration.
- Treating a reversible application deployment as proof of reversible schema
  change. Design expand/migrate/contract and roll-forward recovery.

