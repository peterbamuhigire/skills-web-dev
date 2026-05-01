# Alert Design

## Severity Model

- `P1`: immediate user or revenue impact, page now
- `P2`: serious degradation, urgent but not total outage
- `P3`: trend or capacity issue, create ticket
- `Info`: dashboard only

## Good Alerts

Good alerts answer:

- what is failing
- who is affected
- how severe it is
- what changed recently
- what to check first
- who owns the first response

## Bad Alerts

Avoid:

- averages without tail context
- alerts with no runbook or owner
- duplicate alerts from multiple layers for the same symptom
- alerts on low-action signals such as routine retries unless they indicate user impact
- alerts that cannot be correlated to a release, tenant, or dependency

## Routing Rule

- page when immediate action is required
- ticket when delayed action is acceptable
- dashboard when it is purely diagnostic
