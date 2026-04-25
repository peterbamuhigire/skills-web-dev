# Engagement and Habit Loops

Once users cross the retention point, the game shifts to building habits so that return visits happen without prompting. Nir Eyal's Hook model — trigger, action, reward, investment — applied to subscription products.

## The Hook model, briefly

```text
Trigger  -> Action  -> Variable reward  -> Investment
   ^                                             |
   |_____________________________________________|
```

- **Trigger** — what gets the user to return (external at first, internal with habit).
- **Action** — the smallest useful thing they can do.
- **Variable reward** — the payoff, with some element of variability to deepen engagement.
- **Investment** — the user puts work or data into the product, making it harder to leave.

## Triggers

### External triggers (early phase)

- Email — digests, alerts, social, transactional.
- Push notification — mobile or desktop.
- Calendar — scheduled report, recurring meeting.
- SMS — high-urgency only (payments, security).
- Physical — a physical card, a printed report.
- Inside other apps — Slack bot, browser extension, Zapier.

### Internal triggers (mature phase)

The user returns because an emotion or situation reminds them of the product:

- Boredom -> open social app.
- "How are we doing this quarter?" -> open dashboard.
- "I need to pay this bill" -> open banking app.
- "Something's wrong with the server" -> open monitoring tool.

Internal triggers beat external ones every time. Design the product so that a specific situation reliably makes the user think of you.

## Action

- Lower the friction floor. Open app, glance, done.
- One tap / one click to the value surface.
- Don't gate the frequent action behind auth walls if session-based auth can be extended safely.
- Mobile and notification-first design matters for habitual use.

## Variable reward

Variability is what keeps actions from going stale. Three flavours:

- **Tribe** — social reinforcement (likes, comments, team acknowledgement, peer progress).
- **Hunt** — information or resources (new results, fresh data, a deal, a match).
- **Self** — personal achievement (streaks, mastery, progress).

Subscription examples:

- B2B monitoring: new incidents (hunt), team comments (tribe), "all clear" satisfaction (self).
- Consumer fitness: new workouts (hunt), community cheers (tribe), streaks and PRs (self).
- SaaS CRM: new leads (hunt), team assignments (tribe), deal progress (self).

## Investment

Investment is the user-generated asset that grows with use:

- Data imported, connected accounts, integrations set up.
- Preferences, custom workflows, saved views.
- Followers / contacts / teammates invited.
- Content created (documents, reports, boards).
- Reputation / history (review count, transaction history, status level).

Subscription software is defensible in proportion to how much users have invested. Optimise for investment early.

## Applying the hook to a feature

Walk through a feature and write down each step:

| Hook stage | Question to answer |
|---|---|
| Trigger | What makes the user return to this feature? External and internal. |
| Action | What is the minimal useful action? How many taps? |
| Variable reward | What's the payoff and how does it vary? Tribe / hunt / self? |
| Investment | What does the user leave behind that makes next time better? |

If you can't fill every row with something specific, the feature probably won't build habit.

## Engagement metrics

### Active-user ratios

- **DAU / MAU** — daily over monthly active users. 20%+ indicates strong habit; 50%+ is exceptional. B2B products often sit at 40–70% when usage is daily-by-role.
- **WAU / MAU** — weekly over monthly. Better signal for tools used weekly.
- **L7** (7-day login density) — of 7 days, how many did the user log in? Power users sit at 5–7.

### Session patterns

- **Session frequency** — sessions per user per period.
- **Session depth** — actions per session.
- **Session duration** — careful: long sessions can mean confusion, not engagement.
- **Feature-depth ratio** — unique features used / features available.

### Cohort curves

- Plot retention by cohort against time since sign-up.
- Target: smiling curve (dip then rise) or at minimum a flat plateau after week 2.
- Declining curve = activation problem; flat floor high = product-market fit signal.

## Building a loop in practice

1. Map the hook per persona (the busy manager's hook differs from the analyst's).
2. Pick one external trigger that reliably brings users back.
3. Reduce action friction — test one-click deep links.
4. Introduce variability in the reward — freshness, personalisation, rank changes.
5. Give the user a reason to invest — preferences that stick, content they create, relationships they build inside the app.
6. Measure DAU/WAU and session depth month over month.

## When engagement loops fail

- Trigger fatigue — too many emails / pushes, unsubscribes spike.
- Action friction — new login each day, captchas, slow load.
- Static reward — same dashboard, same numbers; user stops checking.
- No investment — nothing personalised accumulates; switching cost is zero.
- Reward before investment — flashy gamification without real utility feels hollow.

## Ethics guardrail

Habit-forming does not mean manipulative. The classic test: would the user, on reflection, be glad they used the product? If not, the loop is dark-pattern territory. Subscription businesses burn trust fast this way.

## Cross-references

- `habit-forming-products` — deeper Hook model treatment.
- `retention-point.md` — where engagement loops begin.
- `churn-prevention.md` — when loops break.
- `ux-psychology`, `laws-of-ux` — cognitive science background.
