# Pipeline Health Runbook

Five mandatory alerts. Every alert pages on-call. Every alert has a named response procedure.

## 1. Ingestion Lag Alert

- **Threshold:** end-to-end lag from client event to warehouse table > 10 minutes for 5 consecutive minutes.
- **Page:** data platform on-call.
- **Response:**
  1. Check stream broker health (Kafka/Kinesis/Pub/Sub dashboard).
  2. Check transformation job worker count and error rate.
  3. Check warehouse load job status.
  4. If a single stage is the bottleneck, scale that stage; if all stages are clean, inspect upstream client SDK for batching changes.
- **Escalation:** if lag > 30 minutes, escalate to data platform lead. Notify growth team that dashboards will lag.

## 2. Row-Count Deviation Alert

- **Threshold:** daily row count deviates from the 7-day median by more than ±20%.
- **Page:** data platform on-call.
- **Response:**
  1. Compare per-event row counts against the 7-day median. Narrow to the specific event(s) that caused the deviation.
  2. Check recent deploys to client apps (new SDK version? removed instrumentation?).
  3. Check recent schema registry changes.
  4. If the deviation is downward, suspect pipeline data loss; if upward, suspect a loop or a duplicate-firing bug.
- **Escalation:** if deviation > 50%, escalate immediately and freeze downstream scorecards until the root cause is found.

## 3. Schema Violation Rate Alert

- **Threshold:** rejected events > 0.1% of total ingested events over a 15-minute window.
- **Page:** data platform on-call.
- **Response:**
  1. Pull the top rejected event names and the top violation reasons (type mismatch, missing required property, unknown event).
  2. Correlate with recent client app releases.
  3. If a new required property is missing on old client versions, the registry change was not backwards-compatible — roll back the registry change.
- **Escalation:** if violation rate > 1%, treat as a severity-2 incident. Consumers downstream are seeing wrong data.

## 4. Null Identifier Rate Alert

- **Threshold:** `user_id` OR `session_id` null on > 1% of events over a 15-minute window.
- **Page:** data platform on-call.
- **Response:**
  1. Separate logged-in null-rate from anonymous null-rate.
  2. If anonymous-id generation is broken on the client, patch the client SDK and force a re-release.
  3. If session-id is breaking, inspect the session-management middleware.
- **Escalation:** high null rates silently break funnel and cohort analyses. Freeze downstream cohort reports until root cause is identified.

## 5. Backfill Job Failure Alert

- **Threshold:** any backfill or modelled-table refresh job failure.
- **Page:** data platform on-call.
- **Response:**
  1. Read the job error from the orchestrator (Airflow/Dagster/Prefect).
  2. Re-run idempotently if the error was transient.
  3. If persistent, diagnose and fix before the next scheduled window.
- **Escalation:** backfill failures that persist > 24 hours degrade dashboards silently; notify dashboard owners.

## Alert Tiering

- **Page** — the five alerts above. Always.
- **Email** — schema-deprecation warnings, slow-query warnings, storage-cost warnings.
- **Dashboard-only** — informational drift, low-severity anomalies.

Rule: 50 alerts per day means 0 alerts. If any of the five page-tier alerts fires more than 3 times per week, the underlying cause is infrastructure, not data — fix it and stop treating the alert as routine.
