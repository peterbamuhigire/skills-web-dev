# Experiment Spec Template

Pre-register every experiment against this template before code is written. A spec that cannot be completed is not an experiment that should run.

## Header

- **Experiment name:**
- **Experiment ID:** (unique, stable; e.g., `exp_2026_activation_banner_v2`)
- **Owner:** (one person, not a team)
- **Reviewer sign-off:** (PM, eng lead, data)
- **Pre-registration date:**
- **Target launch date:**
- **Target read-out date:**

## Hypothesis

- **If** we change [X]
- **Then** [primary metric] will improve by [Z] percentage points (or relative %)
- **Because** [causal mechanism — the user story that explains why]

A hypothesis that lacks the "because" clause is a guess, not a hypothesis.

## Business Objective

Which business goal does this serve? Name the North Star or the specific funnel stage (acquisition, activation, retention, revenue, referral). If the experiment improves the primary metric but does not serve any declared objective, it is not worth running.

## Success Metric

- **Metric name:**
- **Exact definition:** (event name, aggregation window, user-level or session-level)
- **SQL query or event-analytics query:** (inline, executable)
- **Current baseline:** (last 28 days)
- **Minimum detectable effect (MDE):** (absolute and relative)

## Guardrail Metrics

List every metric that must NOT regress. For each, specify the regression threshold that triggers auto-halt.

| Metric | Threshold | Halt action |
|---|---|---|
| p95 latency | +10% absolute | halt + rollback |
| Error rate | +0.5 percentage points | halt + rollback |
| Crash rate (mobile) | +0.2 percentage points | halt + rollback |
| Revenue per session | -5% | halt + review |
| Support ticket volume | +15% | halt + review |

## User Segment

- **Inclusion criteria:**
- **Exclusion criteria:** (internal users, bot traffic, QA accounts)
- **Traffic allocation:** (e.g., 50/50, or 90/10 holdout)

## Trigger Definition

- **Pattern:** exposure-based / action-based / hybrid
- **Event name:** (e.g., `experiment_triggered`)
- **Logged fields:** `experiment_id`, `variant`, `user_id`, `session_id`, `timestamp`, `client_ip_hash`, `device_context`
- **Fired from:** server-side endpoint or client event
- **Rendered counterfactual?** yes/no (what is logged for the unseen variant)

## Variants

- **Control:** (exact description of the current experience)
- **Treatment:** (exact description of the new experience, with screenshots or mock references)

## Sample Size and Run Time

- **Required sample size per variant:** (cite formula or calculator)
- **Expected daily traffic to trigger:** (triggered users per day, not total DAU)
- **Estimated run time:** (sample size / daily triggered users)
- **Minimum run time:** 14 days regardless of sample size (to cover one full business cycle)

## Rollback Plan

- **Feature flag name:**
- **Rollback trigger conditions:** (any guardrail breach; platform SRM; incident)
- **Rollback owner on-call:**
- **Rollback verification:** (how do we confirm the old path is restored?)

## Pre-Launch Checklist

- [ ] A/A test passed on this platform within the last 90 days
- [ ] Trigger fires server-side
- [ ] Counterfactual logging wired
- [ ] Guardrail dashboards exist and alerting is configured
- [ ] Sample size calculator output attached
- [ ] Feature flag tested in staging with both variants
- [ ] Rollback path rehearsed
