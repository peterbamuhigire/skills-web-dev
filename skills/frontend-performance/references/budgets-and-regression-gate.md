# Performance Budgets, Measurement Plan, and Regression Gate

Parent skill: `../SKILL.md`.

The three deliverables the parent skill commits to producing. This file is the template.

## 1. Performance budget per critical flow

One budget row per critical flow from the `system-architecture-design` critical-flow table. Do not budget per page — budget per user journey.

```text
Flow                    | Device class        | LCP    | INP    | CLS   | JS (gz) | CSS (gz) | Total (gz) | Image-LCP
------------------------+---------------------+--------+--------+-------+---------+----------+------------+----------
Marketing landing       | Moto G Power, 4G    | 2.0s   | 150ms  | 0.05  | 150KB   | 60KB     | 500KB      | 120KB
Product listing         | Moto G Power, 4G    | 2.2s   | 180ms  | 0.08  | 200KB   | 80KB     | 650KB      | 180KB
Cart + checkout         | Moto G Power, 4G    | 2.0s   | 150ms  | 0.05  | 220KB   | 80KB     | 600KB      | n/a
Authenticated dashboard | Desktop, Cable      | 2.5s   | 200ms  | 0.10  | 350KB   | 120KB    | 900KB      | n/a
```

Rules:

- Device class is explicit — mid-range mobile and 4G as default unless the flow is desktop-only.
- Totals are compressed (Brotli) bytes, not uncompressed source bytes.
- Every row maps to an entry in the critical-flow table.
- Flows without a critical-flow entry do not get a budget — add them to the upstream artifact first.

## 2. Measurement plan

| SLI | Measurement | Source | Reported where | Threshold |
|---|---|---|---|---|
| LCP p75 | Field | `web-vitals` JS, beaconed to RUM backend | Observability dashboard `frontend-vitals` | Alert if p75 > 2.5s for 1h |
| INP p75 | Field | `web-vitals` JS | Same dashboard | Alert if p75 > 200ms for 1h |
| CLS p75 | Field | `web-vitals` JS | Same dashboard | Alert if p75 > 0.1 for 1h |
| JS transfer p75 | Field | Navigation Timing + ResourceTiming | Same dashboard | Alert if p75 > budget * 1.1 |
| Lighthouse score | Lab | Lighthouse CI on every PR | PR check | Fail if score drops >5 points |
| Bundle size | Lab | `size-limit` in CI | PR check | Fail if any route chunk exceeds budget |

Rules:

- Every SLI ties back to an SLO owned by `observability-monitoring`. Do not invent a one-off dashboard.
- Field measurement is primary; lab measurement is a leading indicator for PRs.
- Reporting cadence: real-time alerting, weekly trend review, quarterly budget revision.

## 3. Regression gate for CI

A PR fails the gate if any of the following are true:

```text
size-limit job: any entry exceeds the budget declared in size-limit.config.js
lighthouse-ci  : performance score drops > 5 points against baseline
lighthouse-ci  : LCP lab value regresses > 300ms against baseline
bundle-diff    : new dependency larger than 30KB compressed, without an ADR
web-vitals RUM : p75 LCP/INP/CLS regression > 10% over previous 24h post-deploy
```

Minimal workflow (GitHub Actions example):

```yaml
name: perf-gate
on: [pull_request]
jobs:
  size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci
      - run: npm run build
      - run: npx size-limit --json > size.json
      - uses: andresz1/size-limit-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
  lighthouse:
    runs-on: ubuntu-latest
    needs: size
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci && npm run build
      - run: npx @lhci/cli autorun
```

Gate rules:

- The gate is blocking, not advisory. A passing gate is a merge prerequisite.
- Baseline regeneration requires a deliberate PR that updates `lighthouserc.js` and `size-limit.config.js`.
- Post-deploy RUM regression triggers a rollback consultation per `deployment-release-engineering`.
