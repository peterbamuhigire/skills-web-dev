# Release Plan Template

Produced by `deployment-release-engineering` for any non-trivial change. Consumed by the deployer, on-call, and stakeholders.

## Template

```markdown
# Release plan — <change description>

**Change owner:** <name>
**Planned release date:** YYYY-MM-DD HH:MM TZ
**Change scope:** <feature flag | schema migration | infra | dependency upgrade>
**Risk level:** low | medium | high

## Summary

<One paragraph: what is changing, why, and what success looks like.>

## Rollout strategy

- **Pattern:** canary | blue-green | rolling | feature-flag | direct
- **Stages:**
  1. Internal-only — 1h soak
  2. 1% of production — 1h soak
  3. 10% — 2h soak
  4. 50% — 4h soak
  5. 100%
- **Go-criteria per stage:**
  - SLOs within target
  - No elevated error codes for > 5 minutes
  - Manual smoke test of critical flow passes
- **Stage advance:** automatic on green; requires explicit human go on stage 4.

## Dependencies

| Dependency | Type | Pre-release action | Post-release verification |
|---|---|---|---|
| orders-db schema | data | apply migration 0042 before deploy | check schema version |
| identity-service v2.1 | service | already released | check upstream health |
| config.launch_darkly.flag_new_checkout | config | set default OFF | flip per stage |

## Pre-release checklist

- [ ] Migration applied in staging and verified
- [ ] Rollback plan reviewed and linked below
- [ ] On-call paged (informational) with release window
- [ ] Feature flag defaulted OFF in production
- [ ] Dashboard opened for the change-scope metrics
- [ ] Test evidence bundle attached

## Deployment window

- **Start:** YYYY-MM-DD HH:MM TZ
- **End (latest):** YYYY-MM-DD HH:MM TZ
- **Freeze windows avoided:** <list — e.g., mobile app store release, tax filing deadline>
- **On-call during window:** <name>, <pager>

## Post-deploy verification

Within 1h of stage 5:

- [ ] All critical-flow SLOs still within target
- [ ] Error rate for change-scope endpoints within baseline ± 10%
- [ ] Business KPI (e.g., checkout-rate) within baseline ± 5%
- [ ] Manual smoke of 3 end-to-end user journeys
- [ ] No elevated alert volume

## Rollback plan

Linked: `rollback-plan-<change>.md`

Summary: revert deploy tag + flip flag OFF + no DB action required (additive-only migration).

## Communication plan

- **Pre:** Slack #releases, 24h ahead
- **During:** Slack #incidents if anything degrades
- **Post:** Slack #releases, summary + metrics within 2h of stage 5

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| new checkout flow triggers 3DS challenge for a cohort | medium | medium | feature flag allows immediate disable |
| migration lock on orders table > 30s | low | high | migration tested in staging with prod-size data |

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial | ... |
```

## Rules

1. Every non-trivial change has a release plan. Trivial = typo, log-only changes, unused code removal.
2. Risk level drives stage count; high-risk changes cannot skip stages.
3. Go-criteria are observable — no "looks fine" criteria.
4. Rollback plan is written before the release, not during.
5. Feature flags default OFF in production at deploy time.
6. Pre-release checklist is completed, not just copied.

## Common failures

- **No go-criteria** — deployer advances on instinct.
- **Rollback plan written after rollback is needed** — too late.
- **Release during a freeze window** — check calendars first.
- **No post-deploy verification** — problems surface via customer reports, not metrics.
- **Feature flag defaulted ON at deploy** — no way to disable without another deploy.
