# Test Plan Template

Produced by `advanced-testing-strategy`. Consumed by `deployment-release-engineering` as release-gate evidence and by `observability-monitoring` as the baseline for post-deploy verification.

## Template

```markdown
# Test plan — <feature or change>

**Owner:** <name>
**Risk level:** low | medium | high

## Scope

<One paragraph: what is being tested; what is deliberately out of scope.>

## Risk-based depth

For each risk area, the planned test depth:

| Risk area | Risk level | Test depth |
|---|---|---|
| Money handling in checkout | high | unit + integration + contract + E2E + manual exploratory |
| Order status transitions | high | unit + integration + property-based |
| Email notification content | medium | unit + snapshot |
| Admin report pagination | low | unit |
| Static copy change | negligible | none |

## Test layers

### Unit tests

- **Scope:** pure functions, value objects, business rules
- **Tool:** vitest / pytest / xctest
- **Target coverage:** domain modules ≥ 80%, entire codebase ≥ 60%
- **Exclusions:** UI components handled by component tests

### Integration tests

- **Scope:** module + real DB, module + real cache, module + HTTP client to stubbed upstream
- **Tool:** vitest + testcontainers / pytest + docker-compose
- **Fixtures:** deterministic seed; each test starts from clean DB
- **Target:** every access pattern in `access-patterns-<context>.md` has at least one integration test

### Contract tests

- **Scope:** API provider contract matches published OpenAPI spec; consumer tests stubs match real responses
- **Tool:** schemathesis (OpenAPI-driven) OR pact (consumer-driven)
- **Gate:** breaking change to spec fails CI

### E2E tests

- **Scope:** critical flows from the critical-flow table; user journeys across services
- **Tool:** Playwright for web; Detox for mobile
- **Environment:** staging with production-like data shape
- **Target:** every critical flow has one happy-path E2E test and one failure-path E2E test

### Manual / exploratory

- **Scope:** high-risk changes to money handling, UX-heavy flows, security-sensitive code
- **Evidence:** notes + screenshots attached to the release plan

## Test data

- **Source:** synthetic fixtures; never production PII
- **Scale:** representative for performance-sensitive paths (≥ 10k rows)
- **Isolation:** each test run isolates its own tenant or schema

## Flaky-test policy

- First failure: investigate within 2h; quarantine if cause unclear.
- Quarantined tests: must be fixed or deleted within 7 days.
- Quarantine list ≥ 5: stop adding new features until it drains.
- No `retry on failure` masking — if a test needs retries, the code is wrong or the test is wrong.

## Coverage gates

Release gate requires:

- Unit coverage ≥ target per module
- Every critical flow covered by at least one E2E
- No quarantined test > 7 days old
- OpenAPI contract tests green
- No known regression in bug database

## Evidence bundle (for release gate)

| Evidence | Location |
|---|---|
| Unit test run | CI log URL |
| Integration test run | CI log URL |
| Contract test run | CI log URL |
| E2E test run | CI log URL |
| Manual exploratory notes | release plan attachment |
| Performance regression test | if hot-path change |

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial | ... |
```

## Rules

1. Test depth is risk-based, not uniform. Low-risk changes get shallow tests; high-risk get the full pyramid.
2. Every critical flow from the critical-flow table has at least one E2E test.
3. Every access pattern from the access-patterns table has at least one integration test.
4. Contract tests fail the build on breaking OpenAPI change.
5. Flaky tests are fixed or deleted, not retried.
6. Evidence bundle is attached to the release plan.

## Common failures

- **Uniform coverage target** ("80% everywhere") — high-risk modules under-tested, low-risk over-tested.
- **E2E tests for everything** — slow, flaky, and the pyramid flips to an hourglass.
- **Contract tests absent** — breaking changes ship and break consumers.
- **Retry-on-failure masking flakes** — the flake is the signal; masking it loses the signal.
- **Fixtures from production snapshot** — PII in CI, compliance violation.
- **No evidence bundle at release** — you know tests ran, but can't prove it later.
