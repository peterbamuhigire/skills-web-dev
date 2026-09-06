# Java release readiness

| Gate | Evidence | Status | Owner/exception |
|---|---|---|---|
| Wrapper-based clean build and compiler warnings | | | |
| Unit, integration, contract, architecture, and failure tests as applicable | | | |
| Static analysis, dependency, secret, and vulnerability checks | | | |
| Database migration compatibility and rehearsal | | | |
| Packaged JAR/WAR/EAR/container/native artefact smoke test | | | |
| Artefact identity, dependency lock/BOM, SBOM, signature/provenance as required | | | |
| Runtime config validation, secrets, health, telemetry, and release marker | | | |
| Performance/capacity gate for affected critical paths | | | |
| Rolling/blue-green/canary plan and termination behaviour | | | |
| Rollback or roll-forward rehearsal and database reality | | | |
| Release notes, runbook, alerts, escalation, and accountable owner | | | |

Status values: `PASS`, `PARTIAL`, `FAIL`, `NOT ASSESSED`, `NOT APPLICABLE`.
No release is called production-ready while a material gate is failed or
unassessed.
