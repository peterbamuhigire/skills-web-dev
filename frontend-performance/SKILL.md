---
name: frontend-performance
description: Use when defining, implementing, or auditing frontend performance for web apps and SaaS frontends — produces a performance budget per critical flow, a measurement plan tied to SLOs, and a regression gate for CI. Covers Core Web Vitals (LCP, INP, CLS), loading, rendering, and framework-specific recipes. Not for backend latency, API shape (see api-design-first), or server SLOs (see observability-monitoring).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Frontend Performance

Specialist frontend skill. Produces the three deliverables that give a team an operable performance posture: a budget per critical flow, a measurement plan tied to the SLO set, and a regression gate in CI. Not a generic optimisation checklist.

**Prerequisites:** Load `system-architecture-design` (for the critical-flow table) and `observability-monitoring` (for the SLO set and RUM dashboard conventions) before this skill. Load `react-development` or `nextjs-app-router` if the stack is React/Next.

<!-- dual-compat-start -->
## Use When

- Defining the performance budget for a new product or critical flow.
- Diagnosing a field regression on LCP, INP, or CLS captured by RUM.
- Wiring up a regression gate before a team scales frontend merges.
- Auditing an existing frontend and translating findings into budgets and gates.
- Choosing between inline CSS vs deferred, server vs client rendering, or route vs component code-split.

## Do Not Use When

- The bottleneck is server latency or database query time — use `observability-monitoring`, the relevant database skill, or `reliability-engineering`.
- The work is API contract design — use `api-design-first`.
- The work is pure visual/interaction design without a measurable performance cost — use the UI/UX baseline skills.

## Required Inputs

- Critical-flow table from `system-architecture-design`.
- SLO set and RUM dashboard conventions from `observability-monitoring`.
- Device and network mix for the target user base.

## Workflow

- Read this SKILL.md, then load `references/budgets-and-regression-gate.md` plus whichever of `loading-performance.md`, `rendering-and-inp.md`, `framework-recipes.md` the task requires.
- Produce the three deliverables (budget, measurement plan, regression gate) before chasing individual optimisations.
- Tie every SLI back to an SLO owned by `observability-monitoring`.

## Quality Standards

- Budget rows and SLIs map one-to-one with critical flows and SLOs; no orphan metrics.
- Gate is blocking in CI, not advisory.
- Field measurement (RUM) is primary; lab measurement is a leading indicator.

## Anti-Patterns

- Chasing Lighthouse score without a field measurement plan.
- Declaring a budget without naming the device class and network.
- Adding a regression gate that only warns and never blocks.

## Outputs

- Performance budget per critical flow.
- Measurement plan (SLIs, source, reporting surface, alert thresholds).
- Regression gate in CI.

## References

- `references/budgets-and-regression-gate.md`
- `references/loading-performance.md`
- `references/rendering-and-inp.md`
- `references/framework-recipes.md`
<!-- dual-compat-end -->

## When this skill applies

- Establishing a performance budget for a new product or each critical flow in an existing product.
- Investigating a field regression in LCP, INP, or CLS flagged by RUM.
- Designing a CI regression gate before the team scales frontend merges.
- Auditing an existing frontend and producing budgets plus gates, not just a "make it faster" ticket list.
- Choosing between competing rendering strategies (SSR vs SSG vs CSR, inline vs deferred CSS, route vs component split).

## Inputs

| Artifact | Produced by | Required? | Why |
|---|---|---|---|
| Critical-flow table | `system-architecture-design` | required | Budgets are defined per critical flow, not per page |
| SLO set | `observability-monitoring` | required | Frontend SLIs must align with owned SLOs and alert pipelines |
| RUM dashboard conventions | `observability-monitoring` | required | Where field measurements are reported and alerted |
| Device + network mix | product/analytics | required | Determines the reference device class and throttling profile |
| API error model | `api-design-first` | optional | Informs retry + fallback UI budget |
| Threat model | `vibe-security-skill` | optional | Gates CSP and third-party script decisions |

## Outputs

| Artifact | Consumed by | Template |
|---|---|---|
| Performance budget per critical flow | `deployment-release-engineering`, `observability-monitoring`, QA | `references/budgets-and-regression-gate.md` |
| Measurement plan (SLIs, sources, reporting, thresholds) | `observability-monitoring`, on-call | `references/budgets-and-regression-gate.md` |
| Regression gate in CI | `cicd-pipelines`, `deployment-release-engineering` | `references/budgets-and-regression-gate.md` |
| Framework recipe notes | `react-development`, `nextjs-app-router`, Vue/Nuxt specialists | `references/framework-recipes.md` |

## Non-negotiables

- A budget is stated per critical flow with an explicit device class and network.
- Every SLI maps to an SLO owned by `observability-monitoring`; no stand-alone frontend dashboards.
- Regression gate blocks merges when thresholds are breached; it is not advisory.
- Field measurements (`web-vitals` beaconed to RUM) drive alerting. Lab metrics (Lighthouse CI) are a PR leading indicator only.
- Core Web Vitals targets: LCP p75 < 2.5s, INP p75 < 200ms, CLS p75 < 0.1 — unless a flow-specific budget supersedes them with written justification.

## Decision rules

### Rendering strategy

```text
Mostly static marketing / docs / blog      -> SSG (or ISR with long revalidate)
Authenticated dashboard, per-user data     -> SSR streaming + client islands
Highly interactive tool (editor, canvas)   -> CSR with aggressive code-split
Tenant-scoped SaaS app, mixed criticality  -> Server components + selective client

Wrong choice failure mode:
- SSG for per-user data        -> stale personalisation, auth leaks across caches
- SSR for heavy interactivity  -> slow TTFB, wasted server render on cold data
- CSR for content-first pages  -> poor LCP, poor SEO
```

### Inline CSS vs deferred

```text
Above-fold critical path, < 14KB critical CSS         -> inline in <head>
Route-specific, bulky, cachable                       -> external file, async preload
Third-party widget CSS (chat, analytics UI)           -> defer, load after interaction
Design tokens / reset / typography base               -> inline (tiny, load-blocking is fine)

Wrong choice failure mode:
- Inline everything            -> bloated HTML, no CSS caching across navigations
- Defer critical styles        -> FOUC and layout shift on first paint
```

### Code splitting strategy

```text
Route-based split                           -> default for every SPA/Next route
Component-level dynamic import              -> heavy widget (editor, chart, map) > 30KB
Vendor split (react/react-dom)              -> long-cache chunk, rarely updated
No split                                    -> only for single-page tools under 150KB total

Wrong choice failure mode:
- Over-splitting tiny chunks    -> HTTP request overhead + waterfall
- Single monolithic bundle      -> blocks initial interactivity, poor INP
```

### Image handling

```text
Hero / LCP candidate                        -> eager, fetchpriority=high, preload
Above fold, non-LCP                         -> eager, default priority
Below fold                                  -> loading=lazy, decoding=async
Vector/icon under 2KB                       -> inline SVG (no request)
Repeat background                           -> CSS background with responsive image-set()

Wrong choice failure mode:
- Lazy-loading LCP             -> catastrophic LCP regression
- Eager-loading below fold     -> bandwidth waste, contention with LCP
```

### When to add a new SLI

```text
Metric exists and alert correlates with user-visible harm -> keep, publish on dashboard
Metric is a proxy with no known user impact               -> do not alert, log for investigation
Metric is a per-flow variant of a global SLI              -> add as dimension, not new SLI
Metric overlaps a backend SLO                             -> owned by observability-monitoring, not here
```

## Core content

The three deliverables below are the contract. Everything else in `references/` supports producing them.

### 1. Performance budget per critical flow

For each row in the upstream critical-flow table, declare: target device class, target network, LCP, INP, CLS, compressed JS, compressed CSS, total compressed transfer, image-LCP cap. Example table and rules: `references/budgets-and-regression-gate.md`.

### 2. Measurement plan

For every SLI: the source (field or lab), the beacon/collector, the dashboard where it is reported, and the alert threshold. Field measurements use `web-vitals` JS beaconed to the RUM backend defined by `observability-monitoring`. Lab measurements use Lighthouse CI in the merge pipeline.

### 3. Regression gate

A blocking CI job with at least: `size-limit` per entry, Lighthouse CI score and LCP deltas, and a bundle-diff check that flags new dependencies above a threshold. Post-deploy RUM regression triggers a rollback per `deployment-release-engineering`. Full workflow in `references/budgets-and-regression-gate.md`.

### Working reference material

- Loading-path tactics (images, JS, CSS, fonts, hints, compression): `references/loading-performance.md`.
- Rendering, CLS, and INP mechanics: `references/rendering-and-inp.md`.
- Framework recipes (React, Next.js App Router, Vue, vanilla, service workers): `references/framework-recipes.md`.

## Anti-patterns

- **Global budget for the whole app.** Before: "JS < 200KB". After: per-flow budget with device class, e.g. "Product listing on Moto G Power, 4G: JS < 200KB, LCP p75 < 2.2s". A flat global budget lets heavy flows hide behind light ones.
- **Anti-patterns as principles, not mechanics.** Before: "Avoid tight coupling between UI and API". After: "Do not `await` sequential API calls inside a server component that blocks streaming — use `Promise.all` or move non-critical data to a `<Suspense>` boundary". Concrete fix, concrete diagnostic.
- **Lighthouse score as the sole KPI.** Before: "We target Lighthouse 90+ on PRs". After: Lighthouse CI is one lane in the gate; field LCP/INP/CLS p75 drive the alerting contract. Lab-only optimisation masks real-user regressions on low-end devices.
- **Lazy-loading the LCP image.** Before: `<img src="hero.jpg" loading="lazy">`. After: `<img src="hero.jpg" loading="eager" fetchpriority="high" width=... height=...>` plus `<link rel="preload" as="image" ...>` when the hero is below the HTML discoverability point.
- **Animating layout-triggering properties.** Before: `transition: width 300ms` on a sidebar. After: `transition: transform 300ms` with the sidebar off-canvas and translated in. Avoids forced layout on every frame.
- **Regression gate that only warns.** Before: CI job posts a comment with `size-limit` delta. After: job fails the required check when any entry exceeds budget; baseline regeneration is a deliberate PR. Non-blocking gates decay within two sprints.
- **Inventing frontend-only dashboards.** Before: a bespoke Grafana board owned by the frontend team. After: SLIs published on the RUM dashboard defined by `observability-monitoring`, with alert routing through the shared on-call pipeline.
- **Preloading everything.** Before: ten `<link rel="preload">` tags. After: preload only the LCP image and one critical font; everything else competes for bandwidth on the critical path.

## Read next

- `skill-composition-standards` — house-style and contract rules this skill conforms to.
- `observability-monitoring` — owner of SLOs, RUM dashboard, and alert pipeline that the measurement plan plugs into.
- `system-architecture-design` — source of the critical-flow table that budgets depend on.
- `react-development` — React-specific patterns referenced by the framework recipes.
- `nextjs-app-router` — Next.js App Router strategies for server components, streaming, and `next/image`.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Performance | Performance budget document | Markdown doc stating page, API, and interaction budgets | `docs/performance/budgets-checkout.md` |
| Performance | Real-user and synthetic metrics evidence | Dashboard link plus archived snapshot | `docs/performance/rum-snapshot-2026-04-16.md` |

## References

- `references/budgets-and-regression-gate.md` — the three deliverables in template form.
- `references/loading-performance.md` — image, JS, CSS, font, and resource-hint detail.
- `references/rendering-and-inp.md` — layout, paint, CLS, and INP mechanics.
- `references/framework-recipes.md` — React, Next.js App Router, Vue, vanilla, service workers.
