# Pipeline Observability

Treat the CI/CD pipeline as an operated service. Measure the five delivery metrics in the [DORA guide](https://dora.dev/guides/dora-metrics/): deployment frequency, change lead time, failed deployment recovery time, change fail rate and deployment rework rate. Add pipeline-internal signals and distinguish deployment-induced recovery from generic incident MTTR. Source scope and verification limits are recorded in the [engineering benchmark](../../../../docs/audits/2026-09-06-kaizen/06-standards-benchmark.md).

## Metrics to emit

Targets below are illustrative local budgets, not DORA performance bands or universal requirements. Select them with the service owner and record event definitions, exclusions and observation windows. Count affected deployments once even when one deployment triggers several incidents.

| Metric | Source | Target |
|--------|--------|--------|
| Deploy frequency | deployment-record sink | track per service |
| Lead time for changes | commit timestamp → prod deploy | p50 < 1 day, p95 < 1 week |
| Change failure rate | rollbacks + post-deploy incidents / total deploys | < 15% |
| Failed deployment recovery time | deployment-induced impairment → recovery | agree a service-specific budget |
| Deployment rework rate | unplanned remedial deployments / deployments in the same window | track per service; define classification |
| Generic incident MTTR (separate) | incident open → resolved | illustrative p95 < 1 hour |
| Queue time | run.created_at → run.started_at | p95 < 60 s |
| Stage duration p50/p95/p99 | per-job timings | p95 commit-stage < 5 min |
| Cache hit rate | actions/cache + BuildKit logs | > 80% |
| Workflow failure rate | conclusion == failure / total | < 10% on `main` |

## Scraper sketch

GitHub exposes timings via `GET /repos/{owner}/{repo}/actions/runs` and `/runs/{id}/jobs`. A small scraper polls and ships line-protocol to the platform observability backend (Prometheus pushgateway or SigNoz OTLP):

```python
# pseudocode — runs every 60s in a sidecar
for run in gh.list_runs(repo, since=last_seen):
    queue_s = (run.run_started_at - run.created_at).total_seconds()
    duration_s = (run.updated_at - run.run_started_at).total_seconds()
    emit("ci.queue_seconds",     queue_s,    tags={"workflow": run.name, "status": run.conclusion})
    emit("ci.duration_seconds",  duration_s, tags={"workflow": run.name, "status": run.conclusion})
    for job in gh.list_jobs(run.id):
        emit("ci.job.duration_seconds", job_duration(job),
             tags={"workflow": run.name, "job": job.name, "status": job.conclusion})
```

Pin the schema: `metric{repo, workflow, job, branch, status}`. Without those tags the dashboard cannot answer "which workflow on `main` is slowest p95 this week".

## Deployment record

Every successful production deploy emits one row to an append-only store (S3 + Athena, BigQuery, or a Postgres `deployments` table):

```json
{
  "ts": "2026-04-30T14:22:11Z",
  "service": "api",
  "env": "production",
  "git_sha": "a1b2c3d",
  "image_digest": "sha256:9f...",
  "actor": "alice",
  "run_url": "https://github.com/acme/api/actions/runs/123",
  "duration_s": 312,
  "rolled_back": false
}
```

This success-row sketch is not a complete measurement model. Retain deployment attempts/outcomes, commit timestamps, causally linked failures/recovery and remedial-deployment classifications in related records. Failed attempts and recoveries must not disappear because the sketch shows only a successful event.

Acceptance example (synthetic, not an observed service): one deployment triggers two incidents, followed by one unplanned remedial deployment. The failure numerator counts the affected deployment once; the remedial deployment contributes to rework. An unrelated infrastructure outage belongs to incident metrics, not automatically to failed-deployment recovery. Verify those classifications and the chosen denominator against stored event IDs before publishing a dashboard.

## Dashboards

- One repo-level dashboard: failure rate, queue time p95, duration p95 per workflow, last 100 runs.
- One service-level dashboard: DORA delivery metrics, last 50 deploys with rollback markers, deploy → first-error latency.
- One platform-level dashboard: top 10 slowest workflows org-wide, top 10 flakiest, runner queue depth.

Pair with `observability-monitoring` for SLO and alert design; this file only covers what to emit from the pipeline.
