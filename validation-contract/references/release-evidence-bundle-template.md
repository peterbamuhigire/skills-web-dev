# Release Evidence Bundle — Template

Copy this file into the consuming project as `docs/releases/YYYY-MM-DD-<feature>-evidence.md` and fill every row before declaring the release ready.

---

# Release Evidence Bundle — <feature or release name>

- **Date:** YYYY-MM-DD
- **Owner:** <name>
- **Scope:** <one-line description of what is shipping>
- **Risk tier:** <low | medium | high>

## 1. Correctness

- Test plan: <link or `N/A — reason`>
- Latest CI run: <link>
- Contract tests (API/data): <link or `N/A — reason`>

## 2. Security

- Threat model: <link or `N/A — reason`>
- Scan output (SAST/DAST/dependency): <link or `N/A — reason`>
- Secrets handling note: <link or `N/A — reason`>

## 3. Data safety

- Migration plan: <link or `N/A — no schema changes`>
- Backup verification: <link or `N/A — reason`>
- PII / retention note: <link or `N/A — reason`>

## 4. Performance

- Performance budget evidence: <link or `N/A — non-performance-sensitive`>
- Load profile / query plan review: <link or `N/A — reason`>

## 5. Operability

- SLO record: <link or `N/A — reason`>
- Runbook: <link or `N/A — reason`>
- Observability wiring (logs/metrics/traces): <link or `N/A — reason`>
- Rollback plan: <link or `N/A — reason`>

## 6. UX quality

- Design audit: <link or `N/A — no UI surface`>
- Accessibility pass: <link or `N/A — no UI surface`>
- Content / UX-writing review: <link or `N/A — no user-facing copy`>
- AI slop check: <link or `N/A — no AI-generated UI`>

## 7. Release evidence

- Change record (PR / commit range): <link>
- Rollout plan: <link or `N/A — reason`>
- Post-deploy verification: <link or `N/A — reason`>

---

## N/A semantics

- `N/A` is permitted **only with a reason on the same line**.
- An empty cell is not acceptable.
- At **high risk tier**, `N/A` is never permitted on Correctness, Security, Data safety, Operability, or Release evidence.

## Sign-off

- Owner: <name, date>
- Reviewer: <name, date>
