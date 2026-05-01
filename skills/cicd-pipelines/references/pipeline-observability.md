# Pipeline Observability

Treat the CI/CD pipeline as a production system: it has SLOs, error budgets, and on-call. The four DORA metrics (deployment frequency, lead time for changes, change failure rate, mean time to restore) are the canonical health indicators; augment them with pipeline-internal signals.

## Metrics to emit

| Metric | Source | Target |
|--------|--------|--------|
| Deploy frequency | deployment-record sink | track per service |
| Lead time for changes | commit timestamp → prod deploy | p50 < 1 day, p95 < 1 week |
| Change failure rate | rollbacks + post-deploy incidents / total deploys | < 15% |
| MTTR | incident open → resolved | p95 < 1 hour |
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

Deploy frequency, lead time, and change-failure rate are computed from this table — not reconstructed from logs.

## Dashboards

- One repo-level dashboard: failure rate, queue time p95, duration p95 per workflow, last 100 runs.
- One service-level dashboard: DORA quad, last 50 deploys with rollback markers, deploy → first-error latency.
- One platform-level dashboard: top 10 slowest workflows org-wide, top 10 flakiest, runner queue depth.

Pair with `observability-monitoring` for SLO and alert design; this file only covers what to emit from the pipeline.
