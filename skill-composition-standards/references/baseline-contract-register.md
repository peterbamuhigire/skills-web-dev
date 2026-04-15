# Baseline Contract Register

Authoritative list of the artifacts each baseline-skill type must produce. Specialist skills depend on these. If you add a new baseline skill, add its contract here.

## `world-class-engineering`

Inputs: None (repository-wide baseline).

Outputs:

| Artifact | Description | Template |
|---|---|---|
| Release gate checklist | minimum bar before any change ships | inline in SKILL.md |
| Production-readiness rubric | scorecard across correctness, security, operability, UX | inline in SKILL.md |

## `system-architecture-design`

Inputs: product / problem description, existing system context.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| Context map | services/modules, ownership, relationships | `context-map-template.md` |
| Critical-flow table | key user journeys with latency/availability targets | `critical-flow-template.md` |
| ADR set | architectural decision records with alternatives considered | `adr-template.md` |
| Dependency diagram notes | cross-service + external dependencies with fallback behaviour | inline |
| Failure-mode list | what can fail, blast radius, degradation plan | inline, feeds reliability-engineering |

## `database-design-engineering`

Inputs: context map + critical flows.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| Entity model | tables, columns, relationships, invariants | `entity-model-template.md` |
| Access-pattern list | read/write patterns per entity with frequency + latency | `access-patterns-template.md` |
| Index plan | indexes with justification and cost | inline |
| Migration plan | ordered migrations with rollback path | `migration-plan-template.md` |
| Retention + tenancy notes | TTL, soft-delete, tenant isolation strategy | inline |

## `api-design-first`

Inputs: context map + access-pattern list.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| OpenAPI contract | complete OpenAPI 3 spec with examples | `openapi-contract.md` |
| Auth model | authn method, authz rules, role/scope matrix | inline |
| Error model | error codes, envelope shape, retry semantics | `error-model.md` |
| Idempotency keys | which endpoints require them, scope, TTL | inline |
| Observability notes | span names, metrics, log fields per endpoint | feeds observability-monitoring |

## `observability-monitoring`

Inputs: context map + critical flows + error model.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| SLO set | SLI definition + target + window per critical flow | `slo-template.md` |
| Alert rules | alert + severity + runbook link per SLO breach | inline |
| Dashboards | Grafana/Kibana dashboard specs per service | inline |
| Runbook per service | symptoms, diagnosis, mitigation, escalation | `runbook-template.md` |

## `reliability-engineering`

Inputs: context map + failure-mode list + dependency diagram.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| Retry / timeout matrix | per dependency: timeout, retries, backoff, circuit-breaker config | inline |
| Degradation plan | what works when each dependency is down | inline |
| Incident playbook | detection, triage, escalation, comms | inline |
| Postmortem template | blameless postmortem format and required sections | inline |

## `deployment-release-engineering`

Inputs: migration plan + SLO set + test plan.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| Release plan | rollout strategy (canary/blue-green/rolling), stages, go-criteria | `release-plan-template.md` |
| Rollback plan | trigger conditions, step-by-step rollback, data-safe ordering | `rollback-plan-template.md` |
| Migration choreography | order of deploys when schema + code change together | inline |
| Post-deploy verification | smoke tests, SLO checks, rollback-window length | inline |

## `advanced-testing-strategy`

Inputs: context map + critical flows + OpenAPI contract.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| Test plan | test pyramid split per service/feature | `test-plan-template.md` |
| Test evidence bundle | coverage + run logs + flaky-test status | inline |
| Risk-based coverage map | which flows get which depth of test (unit/integration/contract/E2E) | inline |

## `vibe-security-skill`

Inputs: context map + auth model + access patterns.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| Threat model | assets, trust boundaries, threats, mitigations | `threat-model-template.md` |
| Abuse case list | intentional misuse scenarios with mitigations | inline |
| Auth/authz matrix | role × resource × action, with default-deny | inline |
| Secret handling plan | where secrets live, rotation, audit | inline |

## `distributed-systems-patterns`

Inputs: context map + failure-mode list.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| Consistency model | per boundary: strong/eventual/read-your-writes | inline |
| Message semantics | at-least-once vs exactly-once, ordering, deduplication | inline |
| Saga / compensation plan | cross-service workflow with compensating actions | inline |

## `engineering-management-system`

Inputs: team shape and scope.

Outputs:

| Artifact | Description | Template |
|---|---|---|
| Operating rhythm | standup / planning / retro / QBR cadence | inline |
| Prioritisation framework | scoring rubric + decision authority | inline |
| Delegation matrix | task → owner → review level | inline |

## Contract enforcement

When a skill claims an input (e.g., "requires a context map"), the upstream skill producing that artifact must be declared in the Inputs table with the exact artifact name.

When CI gains an input/output parser, it will:

1. Build a graph: artifact type → (producing skill, consuming skills).
2. Warn when a consuming skill claims an input that no skill declares as output.
3. Warn when a skill produces an artifact that no template exists for.

Until CI exists, reviewers run this check manually.

## Adding a new artifact type

1. Add a template file to `skill-composition-standards/references/<artifact>-template.md`.
2. Add the artifact to this register under the producing baseline skill.
3. Update the Outputs section of the producing skill to reference the template.
4. Update any specialist skills that should consume it.
