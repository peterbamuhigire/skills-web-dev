# Rollback Plan Template

Produced by `deployment-release-engineering`. Written before the release, used when it goes wrong.

## Template

```markdown
# Rollback plan — <change description>

**Linked release plan:** <path>
**Rollback owner:** <name> (usually the deployer)

## Trigger conditions

Rollback if ANY of:

- Availability SLO burn-rate > 14.4× (2% budget in 1h) for the affected service
- Error rate for change-scope endpoints > baseline + 50%
- p95 latency for critical flow > 2× target for > 10m
- Business KPI drop > 20% in any 10-minute window
- Manual decision by change owner or on-call

## Rollback steps

### Data-state assessment first

Before any action, determine:

- Is the database schema compatible with the previous code version? (If migration was additive-only: yes. If destructive: not safe to rollback without restore.)
- Are there in-flight requests that depend on the new code path?
- Are there queued messages encoded for the new version?

If any of the above require special handling, escalate to the change owner + DB owner + staff engineer before proceeding.

### Standard rollback (additive-only changes)

1. Flip feature flag OFF:
   `curl -X POST https://launchdarkly.../flags/new_checkout -d '{"on": false}'`
   Verified by: flag dashboard shows OFF.
2. (If flag-only rollback fixes it, stop here. Document the incident.)
3. Revert deploy:
   `kubectl -n prod rollout undo deployment/checkout --to-revision=<N-1>`
   Verified by: `kubectl rollout status` reports success, pods are running `v1.2.2` (prior version).
4. Wait 5 minutes. Re-check SLOs. If green, continue. If still red, escalate to staff engineer.
5. Disable related cron jobs if they trigger the new path:
   `kubectl -n prod patch cronjob new-checkout-reconcile -p '{"spec":{"suspend":true}}'`
6. Clear the queue of messages encoded for the new version:
   (Decide: drain, drop, or hold. Drain requires backward-compatible consumer. Dropping loses work. Holding requires capacity.)

### Destructive migration rollback

If the migration was destructive (column dropped, type changed, constraint added):

1. Standard rollback will fail because old code expects the old schema.
2. Option A — roll forward: fix the code and deploy again. Preferred if the fix is obvious and fast.
3. Option B — restore: take the service to maintenance mode, restore the DB from the pre-release snapshot, deploy previous version. Data loss window = time since snapshot.
4. Any destructive migration must have had a pre-release snapshot with the name `pre-<change>-<date>`.

## Verification after rollback

- [ ] SLOs back within target within 15 minutes
- [ ] Error rate baseline within 10 minutes
- [ ] No residual alerts firing
- [ ] Feature flag shows OFF
- [ ] Deploy shows previous version
- [ ] Customer reports in support channel slow/stop

## Communication

- **Trigger:** Slack #incidents. "Rolling back <change> due to <cause>."
- **Complete:** Slack #incidents + #releases. "Rollback complete. Service restored at HH:MM. Postmortem to follow."
- **Postmortem:** within 48h, linked to the release plan.

## Rollback time budget

- Standard rollback (flag flip): < 2 minutes
- Standard rollback (deploy revert): < 10 minutes
- Destructive rollback (restore): < 60 minutes, possibly with data loss

If rollback takes longer than budget, escalate and consider if the situation warrants a postmortem-level incident.

## Known rollback hazards

- **Queue encoding mismatch:** messages produced by new version can't be consumed by old version. Plan for a drain step or backward-compatible message schema.
- **Cache poisoning:** new version may have cached data in a format the old version can't parse. Plan cache flush as a rollback step.
- **Client version mismatch:** mobile clients may have cached a new API response shape. Server-side rollback doesn't reverse that.
- **Third-party dependency:** if we notified a third party of a new webhook URL or capability, rollback may fail without their coordination.

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial | ... |
```

## Rules

1. Written before the release, not after something goes wrong.
2. Has explicit trigger conditions — no "when it seems bad".
3. Time budget stated per rollback path.
4. Data-state assessment is step 1, before any action.
5. Destructive migrations require a pre-release snapshot named predictably.

## Common failures

- **Rollback plan = "revert commit and redeploy"** without considering schema, queues, caches, or clients.
- **No trigger conditions** — the team argues whether to roll back while the SLO burns.
- **Rollback time budget absent** — deployer keeps trying long after they should have escalated.
- **No cache flush step** when caching is involved.
- **No communication** during rollback — support team is blindsided.
