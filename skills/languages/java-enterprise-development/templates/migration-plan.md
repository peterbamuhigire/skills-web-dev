# Java enterprise migration plan

## Baseline and target

| Dimension | Current | Target | Support/currentness evidence | Compatibility owner |
|---|---|---|---|---|
| JDK/language/bytecode | | | | |
| Framework/Jakarta namespace | | | | |
| Build/plugins/dependencies | | | | |
| Persistence/driver/database | | | | |
| Server/packaging/deployment | | | | |

## Inventory and safety net

- Critical business flows and invariants:
- Deprecated/removed/internal APIs and reflection/serialization use:
- Dependency, agent, certificate, protocol, and vendor compatibility:
- Existing compile/test/integration/performance/production baseline:
- Gaps marked `NOT ASSESSED`:

## Stages

| Stage | Smallest compatible change | Entry evidence | Normal/failure checks | Rollback boundary | Exit evidence |
|---|---|---|---|---|---|
| | | | | | |

Use intermediate supported stages where direct migration combines language,
namespace, framework, persistence, packaging, and operational risks. Separate
schema expansion, data movement, code activation, and schema contraction.

## Rollout and closure

- Canary/parallel/strangler or in-place strategy:
- Data reconciliation and compatibility window:
- Performance comparison and capacity effect:
- Roll-forward/rollback decision rights:
- Deprecation removal and retirement evidence:

