# The Retention Point

The retention point is the observable moment a customer crosses from "evaluating" to "committed". Before it, churn is elevated and interventions are cheap. After it, churn collapses and expansion becomes the dominant lever. Finding and shortening the path to this point is the single highest-leverage activity in early subscription life.

## What qualifies as a retention point

A candidate retention point must satisfy all of:

1. Observable — the product can log whether the user has reached it.
2. Reachable in the trial / first billing cycle — not 90 days out.
3. Correlates strongly with month-3 retention (use cohort analysis).
4. Represents real value delivery, not a vanity action (e.g. "verified email" is not a retention point).
5. Actionable — onboarding, nudges or CS can move users toward it.

## Retention points in the wild

| Product | Retention point |
|---|---|
| Slack | Team sends ~2,000 messages |
| Dropbox | User uploads one file on one device, then accesses from a second |
| Facebook | Adds 7 friends in 10 days |
| Twitter | Follows 30 accounts |
| Netflix | Finishes one complete show |
| B2B analytics SaaS | Imports one dataset, builds one dashboard, shares one link |
| B2B accounting SaaS | Reconciles first bank statement |
| Project management | Creates project, adds 3 tasks, invites 2 teammates |
| Inventory SaaS | Records first stock movement across two locations |

## Finding yours: the cohort method

1. Define the outcome — customer retained at day 90 (or day 180 for annual).
2. Pull a cohort of 200+ customers with known outcomes.
3. For each candidate action (10–30 events you suspect matter) compute:
   - percent of retained customers that did the action in week 1
   - percent of churned customers that did the action in week 1
   - retention rate among customers who did vs did not do the action
4. Rank actions by the lift: `retained_with / retained_without`.
5. Prefer actions that are early, repeatable, and product-meaningful. Avoid collinear actions (e.g. "logged in twice" will correlate with almost anything).
6. Look for a combination of 2–4 actions that together predict retention better than any single action.

## Activation metric design

- One metric, not a dashboard. "Activated" is a yes/no flag at the user or account level.
- Time-boxed. Activation has a deadline ("by end of day 7") so it pressures onboarding design.
- Account-level for B2B ("team has invited 3+ users and created 1 project"), user-level for B2C.
- Instrumented end-to-end: event fires once, idempotently, into the warehouse and the in-app system simultaneously.
- Reviewed quarterly. Product evolution shifts what "value" means.

## Instrumentation checklist

- [ ] Event schema agreed with product, CS and data (name, properties, source-of-truth).
- [ ] Events fire from the server, not only the client, for actions that matter.
- [ ] Deduplication logic so re-runs, retries, and replays don't double-count.
- [ ] Dashboard: activation rate by cohort, by plan, by channel, by persona.
- [ ] Reverse ETL: activation flag available in CRM, customer success platform, in-app tour engine.
- [ ] Alert when cohort activation rate drops below target for 2 weeks running.

## Intervention playbook (before and after retention point)

| User state | Signal | Intervention |
|---|---|---|
| Signed up, inactive day 1 | No event since sign-up | Day-1 email with the single first action, in-app checklist visible |
| Partial activation, stalled | 1 of N activation steps done, 72h no progress | Triggered in-app tip, optional chat prompt, personalised email with loom-style guide |
| Approaching trial end unactivated | Day 10 of 14, not activated | CS outreach (high-value tier) or assisted-onboarding invite (SMB) |
| Activated, low usage | Activated but < 2 sessions / week | Habit-building email series, feature-depth nudge |
| Churning account | Seat drop, login drop, ticket spike | Alert to CSM, pause-offer in cancel flow |
| Power user | Activated and expanding | Referral ask, case study candidate, expansion offer |

## Shortening the path

- Cut steps. Each extra step before the retention point sheds 10–30% of users.
- Default, don't decide. Pre-populate, suggest templates, auto-import demo data.
- Remove empty states. No new user should see a blank canvas — show sample data with a clear "replace with yours" affordance.
- Parallelise. Ask for less up-front; gather profile data after the first win.
- Make progress visible. A checklist with 3–5 items beats an opaque tour.

## Anti-patterns

- Declaring "activation = signed up". Signed up is acquisition, not activation.
- Using login count as the activation metric. Logins without outcome are a vanity signal.
- Designing activation in a workshop without cohort data. Guesses rarely survive contact with cohorts.
- Never re-measuring. Product changes invalidate activation definitions; re-run the cohort analysis annually.
- Activation defined per-feature, not per-outcome. Users don't care about features; they care about results.

## Tools

- Analytics: Amplitude, Mixpanel, PostHog, Heap for event analysis and cohort definition.
- In-app: Appcues, Userflow, Intercom Product Tours, Pendo for guided experiences.
- Data warehouse: Snowflake / BigQuery / Redshift with dbt models exposing an `activations` table.
- Reverse ETL: Census, Hightouch, to sync activation into CRM / CS tools.

## Cross-references

- `activation-onboarding.md` — how to drive users to the retention point.
- `churn-prevention.md` — what to do when users stall short of it.
- `engagement-loops.md` — what happens after the retention point.
