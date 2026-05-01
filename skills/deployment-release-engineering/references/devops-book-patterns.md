# DevOps Book Patterns

Use this reference when a software project needs stronger delivery, operations, or release guidance. It synthesises the DevOps source set supplied by Peter: *Strategic DevOps*, *DevOps for PHP Developers*, *The DevOps Handbook, Second Edition*, and *Modern DevOps Practices*.

## Core Operating Model

DevOps is not only automation. Treat it as an operating system for software delivery:

- optimise the full technology value stream from idea to production feedback;
- keep work small, visible, and integrated frequently;
- reduce handoff delay between development, operations, security, QA, product, and support;
- build fast feedback through tests, telemetry, user signals, and incident learning;
- improve daily work by making recurring pain visible and removing it.

Use the Three Ways as the default diagnostic:

| Lens | What to check | Evidence to request |
|---|---|---|
| Flow | Can changes move from commit to production without long queues or heroic coordination? | Lead time, WIP, branch age, deployment frequency, queue time, release calendar |
| Feedback | Can teams detect defects, incidents, performance issues, and customer harm quickly? | Test results, alerts, dashboards, error budgets, user support trends |
| Learning | Does the organisation improve from incidents, failed releases, and pipeline friction? | Post-incident actions, recurring failure analysis, runbook changes, automation backlog |

## Value Stream and Delivery Metrics

For delivery-system assessment, capture:

- deployment frequency;
- lead time for changes;
- change failure rate;
- mean time to restore service;
- pipeline duration, red time, rerun count, and flaky-stage rate;
- escaped defect rate;
- manual approval wait time;
- incident count by severity;
- unplanned work percentage.

Use these measures together. High deployment frequency with poor recovery is recklessness; low failure rate with month-long lead time is stagnation.

## Pipeline Design Rules

A trustworthy deployment pipeline should:

1. make the pipeline the normal path to production;
2. build once and promote the same artifact through environments;
3. keep environment differences in configuration, not rebuilt code;
4. run fast commit checks on every normal integration;
5. run deeper acceptance, contract, security, performance, and resilience checks according to risk;
6. publish release evidence: artifact version, commit range, test evidence, skipped checks, migration notes, rollback notes;
7. emit release markers into logs, traces, metrics, and dashboards;
8. treat a broken default-branch pipeline as a stop-the-line event.

## Branching and Integration

Prefer trunk-based development or short-lived branches. Long-lived branches increase merge risk and hide integration defects. If feature work cannot be released immediately, use feature flags, dark launches, or canary exposure rather than long integration delays.

Branching review questions:

- How old is the average open branch?
- Can `main` be deployed at any time?
- Are release branches exceptional or routine?
- Are integration conflicts caught by the pipeline or by release-day manual effort?

## Deployment and Rollback Patterns

Choose rollout strategy by risk:

| Pattern | Use when | Watch-outs |
|---|---|---|
| Rolling | Low-risk stateless service change | Version skew and slow rollback |
| Blue-green | Need fast cutover and clear rollback | Data compatibility and duplicate infrastructure cost |
| Canary | Need real-user feedback with limited blast radius | Requires good metrics, routing, and rollback triggers |
| Dark launch | Deployment should precede feature exposure | Requires feature flag hygiene |
| GitOps pull model | Kubernetes or cloud-native estate needs auditable desired state | Requires repository discipline and drift monitoring |

For rollback-hostile changes, define the forward-fix and compensating-action plan before deployment.

## Database and State Safety

For live systems, use expand-contract migration where possible:

1. expand schema in a backward-compatible way;
2. deploy code that can work with old and new shape;
3. backfill or dual-write where needed;
4. verify data consistency;
5. contract only after old code paths are gone.

Classify every migration as reversible, compensating-only, or forward-fix-only. Never imply that restoring code also restores business data after external side effects have occurred.

## Observability and On-Call

Monitoring should support decisions, not produce noise. Define:

- service-level indicators and objectives;
- RED metrics for request/response services: rate, errors, duration;
- USE metrics for infrastructure: utilisation, saturation, errors;
- structured logs with request ID, user or tenant context where safe, service, version, and trace ID;
- alert classes: page immediately, ticket, dashboard only;
- escalation paths and alert ownership;
- release markers that tie incidents to recent changes.

Alerts should be actionable. If no one knows what action to take, convert the alert into a dashboard panel or create a runbook before paging people.

## Security and DevSecOps

Security should be built into the delivery flow:

- dependency and vulnerability scanning in the pipeline;
- secret scanning before merge;
- infrastructure policy checks for IaC;
- container image scanning and minimal base images;
- threat modelling for sensitive releases;
- least-privilege deployment credentials;
- security findings tracked with owners and remediation dates.

Do not create a security gate that teams work around. Put fast checks early, deeper checks where they fit, and make failures explainable.

## PHP Delivery Notes

For PHP applications, include:

- Composer dependency install with lockfile verification;
- static analysis and coding standards in the commit stage;
- PHPUnit or Pest test suite in CI;
- environment-specific `.env` managed outside version control;
- PHP-FPM pool configuration, OPcache settings, and restart or reload procedure;
- web server config as code;
- database migration and seed discipline;
- cache clear/warm steps;
- queue worker restart strategy;
- file permissions and upload directory ownership;
- unattended security updates policy on servers;
- backup and restore procedure for database and uploaded files.

For WAMP or shared-hosting-style projects, still apply the same principles: repeatable deployment steps, source-controlled config templates, manual step elimination, backup before change, and post-deploy smoke tests.

## Cloud-Native and GitOps Notes

For containerised or Kubernetes systems:

- keep Dockerfiles small, reproducible, and scanned;
- separate build-time and runtime secrets;
- use readiness and liveness probes deliberately;
- define CPU and memory requests and limits;
- use rolling update, canary, or blue-green strategy intentionally;
- manage desired state through GitOps when team maturity supports it;
- monitor drift between repository state and cluster state;
- keep namespaces, network policies, and secrets aligned with tenancy and environment boundaries.

## Anti-Patterns

- Automating a broken process instead of simplifying it first.
- Manual deployment steps that are not documented or repeatable.
- Rebuilding artifacts separately per environment.
- Treating monitoring as CPU graphs only.
- Long-lived branches used as a substitute for release slicing.
- Security review after production deployment.
- Rollback plans that ignore migrations, caches, queues, and external side effects.
- Incident reviews that assign blame but do not change the system.

## Output Checklist

When applying this reference, produce or update:

- value-stream diagnosis;
- pipeline stage map;
- branch and release-control model;
- deployment and rollback plan;
- migration safety classification;
- observability and alert plan;
- incident-learning loop;
- security checks in the delivery path;
- PHP or cloud-native runtime notes where relevant.
