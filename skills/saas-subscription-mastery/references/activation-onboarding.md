# Activation and Onboarding

Drives the first 7 days — the highest-leverage window in any subscription business. Everything after is retention maintenance; this is retention creation.

## Targets

| Metric | SMB SaaS target | Consumer / prosumer target |
|---|---|---|
| Time-to-first-value (TTFV) | 10–20 minutes | < 5 minutes |
| Day-1 activation rate | 50–70% | 40–60% |
| Day-7 activation rate | 70–85% | 60–75% |
| Trial-to-paid conversion | 15–25% (card-free) / 50–70% (card) | 2–5% (freemium) |
| Day-30 retention of activated users | > 80% | > 60% |

Set your own based on cohort baselines; these are starting points only.

## TTFV design principles

1. One primary first action. Not three. The user should know within 30 seconds what to do.
2. Remove every pre-value obstacle: email verification walls, long profile forms, tour videos.
3. Defer data collection. Ask at sign-up for the minimum (email, password). Collect role, company size, team invites after first value.
4. Pre-populate. Sample data, templates, suggested projects. Users almost never start blank.
5. Reward the first action visibly — confetti, a checkmark, a count updating — humans track progress.

## Empty-state patterns

Avoid blank canvases. Patterns in decreasing order of effectiveness:

- **Sample data with "replace with yours" action** — user sees the full product shape immediately.
- **Template gallery** — pick a starter; a blank template is the last option, not the first.
- **Guided first-creation** — a modal that asks 2–3 questions and generates the starter state.
- **"Copy from" flows** — duplicate an example project into the user's workspace.
- **Illustrated empty state with one CTA** — acceptable but least effective.

## Product-tour design

Rules:

- Keep tours to 3–5 steps maximum.
- Anchor each step to a real action, not a description ("click here to add" > "this is where you add").
- Allow dismiss on every step; never trap the user.
- Trigger tours on first visit only, not on every return.
- Use tooltips for affordance discovery, not for content-marketing copy.

Tool choices:

- **Userflow / Appcues / Pendo** — third-party, fast to ship, designer-friendly, monthly cost.
- **Intercom Tours** — good if Intercom is already the support tool.
- **In-app native** — best UX and performance, engineering cost; prefer for mature apps.

## Checklist component

A visible onboarding checklist beats most other single interventions. Design:

- 3–7 items, ordered by dependency and value.
- Each item is an action, not a concept.
- Progress visible (3/5 done).
- Dismissible after completion, never before.
- Persistent location — sidebar, bottom-right pill, or account menu badge.
- Reappearing rules — once dismissed, not shown again unless user triggers from help menu.

Example SMB SaaS checklist:

1. Import your first dataset.
2. Invite a teammate.
3. Create your first dashboard.
4. Share a link with someone outside your team.
5. Connect one integration.

## Week-1 email sequence

Trigger on events, not just calendar days. Send to the sign-up email, optional to invited teammates.

| Day / Trigger | Subject | Goal |
|---|---|---|
| Minute 1 (sign-up) | Welcome — do this first | Direct link to first action |
| Hour 24 (if no first action) | Still got 2 minutes? | Reduce friction, show GIF of first action |
| Day 2 (after first action) | Nice work — here's what's next | Nudge second step |
| Day 3 (if stalled) | Need a hand? | Offer help, link to 5-min demo, chat option |
| Day 4 (collaboration step) | Invite your team | Reinforce multi-user value |
| Day 6 (before trial end, if trial) | 2 days left — here's what you've done | Value recap, upgrade CTA |
| Day 7 | You're set — here's how to go deeper | Feature depth, community invite |

Rules:

- Short emails. 2–3 paragraphs, one CTA.
- Plain-text design often outperforms heavy HTML for B2B.
- Sender from a human, not "noreply".
- Exit the sequence when the user has completed the goal — don't nag.

## In-app trigger playbook

- **First sign of stall** — 3 minutes idle on a key screen — show a contextual tooltip with the next step.
- **Feature discovery** — when a user lingers near an unused key feature, show a one-line prompt.
- **Milestone hit** — fire a celebration + next-step hint.
- **Risk signal** — if user searches "cancel" in help, trigger a save modal with assisted chat.

Keep triggers rate-limited. No more than 2 per session, never overlapping.

## Instrumentation

- Every onboarding step has a named event. Document in an event schema.
- Dashboard: funnel from sign-up -> step 1 -> step 2 -> activated, by cohort week.
- Alert: activation rate drops > 10% week-over-week.
- A/B testing infrastructure for tour copy, step order, and email timing.

## Tool picks

| Need | Tools |
|---|---|
| In-app tours / checklists | Appcues, Userflow, Pendo, Intercom |
| Lifecycle email | Customer.io, Braze, HubSpot, Loops |
| Product analytics | Amplitude, Mixpanel, PostHog, Heap |
| Session replay | FullStory, Hotjar, PostHog |
| Reverse ETL | Census, Hightouch |
| In-app chat / support | Intercom, Crisp, Front |

## Anti-patterns

- 10-step tour on first visit.
- Email verification blocking first action.
- Activation metric = "signed up".
- No empty-state content; users face a blank workspace.
- Sending the same lifecycle email regardless of whether the user has activated.
- Ignoring invited teammates — they have separate activation needs.
- Running A/B tests on onboarding without a minimum sample size.

## Cross-references

- `retention-point.md` — how to define activation.
- `engagement-loops.md` — what happens after activation.
- `ux-principles-101`, `habit-forming-products` — UX and habit design background.
