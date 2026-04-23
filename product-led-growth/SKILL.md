---
name: product-led-growth
description: Use when designing PLG motions for a SaaS product — freemium tiers, PQL
  definition, activation flows with time-to-value targets, in-app upgrade prompts, viral
  loops, NPS surveys, feature flags for gradual rollout, and PostHog-based product
  analytics for funnel and cohort tracking.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Product-Led Growth
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing PLG motions for a SaaS product — freemium tiers, PQL definition, activation flows with time-to-value targets, in-app upgrade prompts, viral loops, NPS surveys, feature flags for gradual rollout, and PostHog-based product analytics for funnel and cohort tracking.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `product-led-growth` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->

## PLG vs Sales-Led vs Marketing-Led

Pick the motion from product characteristics, not preference. The wrong motion wastes 12 to 18 months of runway.

- **PLG fit:** product delivers tangible outcome in under 10 minutes without sales conversation; user can sign up and extract value alone; ACV $0 to $2,000; buyer and user are the same person.
- **Sales-led fit:** ACV exceeds $10,000; buyer committee has 3+ stakeholders; procurement, security review, legal redlines gate every purchase; integration effort exceeds 2 weeks.
- **Marketing-led fit:** category is awareness-scarce; purchases episodic; buying decision is research-heavy and emotional.

Unit-economics contrast:

- PLG: CAC $50 to $300, free-to-paid conversion 2% to 5%, payback under 6 months when retention holds.
- Sales-led: CAC $5,000 to $40,000, win rate 15% to 25%, payback 12 to 24 months; higher ACV compensates.
- Marketing-led: CAC $100 to $1,500, conversion dependent on creative fatigue and channel saturation.

Hybrid is the steady state above $10M ARR — PLG acquires individuals and small teams, sales closes the enterprise contract once usage crosses a threshold.

## Freemium Design

Freemium fails when the free tier gives too much (no upgrade pressure) or too little (no adoption). Pick a split deliberately.

- **Core-value-free, advanced-value-paid** (default): free tier delivers primary job-to-be-done; paid tiers add team, scale, admin, compliance.
- **Seat limits:** restrict collaborators. Works when collaboration is the value (Slack, Figma, Notion).
- **Usage limits:** restrict volume — rows, API calls, storage, events. Works when usage scales with customer size (Airtable, Segment, PostHog).
- **Feature limits:** restrict SSO, audit log, custom roles, integrations. Works when buyer and user diverge at scale.

Example: Notion free tier = unlimited pages for an individual; Plus unlocks unlimited uploads, 30-day history, unlimited guests; Business adds SAML SSO and private team spaces; Enterprise adds audit log and SCIM.

Guardrails:

- Never gate a feature the first-run user needs to experience core value.
- Always gate at least one feature a 3-person team will hit within 2 weeks of adoption.
- Publish limits transparently; hidden limits destroy trust.

## Product-Qualified Lead (PQL)

A PQL is a user whose in-product behaviour signals buying intent strong enough to hand to sales or trigger an upgrade sequence. Unlike an MQL, a PQL has demonstrated value extraction.

Concrete PQL definition for a collaborative work tool:

- Created 3+ projects within 7 days of signup.
- Invited at least 1 team member who accepted the invite.
- Hit a free-tier feature limit at least once.

Operationalise as a SQL query:

```sql
SELECT u.user_id, u.email, u.signup_date
FROM users u
JOIN (SELECT user_id FROM events
      WHERE event_name = 'project_created'
        AND event_time >= NOW() - INTERVAL '7 days'
      GROUP BY user_id HAVING COUNT(*) >= 3) p ON p.user_id = u.user_id
JOIN (SELECT DISTINCT inviter_id FROM invites
      WHERE accepted_at IS NOT NULL) i ON i.inviter_id = u.user_id
JOIN (SELECT DISTINCT user_id FROM events
      WHERE event_name = 'limit_hit') l ON l.user_id = u.user_id
WHERE u.plan = 'free';
```

Or as a PostHog cohort: users where `project_created` (last 7 days) >= 3 AND `invite_accepted` at least once AND `limit_hit` at least once.

## Activation Flow Design

Activation is the moment a new user first experiences core value. Target time-to-first-value (TTFV) under 10 minutes; every minute beyond drops activation by 5 to 10 percentage points.

Activation checklist with 4 to 6 steps shown as a dashboard progress bar:

1. Sign up and verify email.
2. Set up the workspace (name, timezone, team size).
3. Create the first meaningful item (project, dashboard, survey, document).
4. Invite a teammate.
5. Receive the first value event (a reply, a shared view, a generated report).
6. Return the next day (habit seed).

Track completion as a single `activated_at` timestamp per user. Each step should take under 90 seconds. Order reflects the shortest path to value, not the easiest path to navigate. Skipping is allowed but discouraged (soft dismiss, not permanent hide).

## Empty State Design

Empty states are the most under-invested surface in SaaS. A blank dashboard on first login produces 40% of churn in the first 24 hours. Treat first-use empty state as onboarding:

- **Sample-data toggle:** one-click switch populating the view with realistic demo data the user can explore and delete.
- **60-second video walkthrough:** embedded, autoplay-muted, captions on.
- **"Create your first X" CTA:** primary action button leading to a guided creation flow, not a raw form.

Minimal React empty-state component:

```tsx
interface EmptyStateProps {
  title: string; description: string
  primaryActionLabel: string; onPrimaryAction: () => void
  onLoadSampleData?: () => void; videoUrl?: string
}

export function EmptyState(p: EmptyStateProps) {
  return (
    <div className="empty-state">
      <h2>{p.title}</h2>
      <p>{p.description}</p>
      {p.videoUrl && <video src={p.videoUrl} autoPlay muted loop playsInline />}
      <button className="btn-primary" onClick={p.onPrimaryAction}>{p.primaryActionLabel}</button>
      {p.onLoadSampleData && (
        <button className="btn-secondary" onClick={p.onLoadSampleData}>Load sample data</button>
      )}
    </div>
  )
}
```

## In-App Upgrade Prompts

Upgrade prompts must be contextual, not interruptive. The highest-converting moment is the instant the user hits a limit — they have demonstrated need.

- Warn at 80% of limit ("You have used 8 of 10 projects").
- Prompt at 100% ("You have reached the 10-project limit. Upgrade to create more.").
- Never show an upgrade prompt during the first 5 minutes of a session.
- Never interrupt a save, publish, or share action with an upgrade modal.

Copy focuses on unlocked value, not price. Yes: "Unlock unlimited projects and advanced analytics." No: "Upgrade now for $29/month."

Example upgrade modal with three paid tiers:

```tsx
function UpgradeModal({ open, onClose, reason }: UpgradeModalProps) {
  const tiers = [
    { name: 'Pro', price: '$12/seat/mo', features: ['Unlimited projects', 'Priority support'] },
    { name: 'Team', price: '$24/seat/mo', features: ['Pro +', 'Admin controls', 'SSO'] },
    { name: 'Enterprise', price: 'Contact us', features: ['Team +', 'SLA', 'Audit log'] },
  ]
  if (!open) return null
  return (
    <dialog open>
      <h2>Unlock more with a paid plan</h2>
      <p>{reason}</p>
      <div className="tier-grid">
        {tiers.map((t) => (
          <article key={t.name}>
            <h3>{t.name}</h3><p className="price">{t.price}</p>
            <ul>{t.features.map((f) => <li key={f}>{f}</li>)}</ul>
            <button className="btn-primary">Choose {t.name}</button>
          </article>
        ))}
      </div>
      <button className="btn-link" onClick={onClose}>Maybe later</button>
    </dialog>
  )
}
```

## Viral Loops

Viral loops are structural, not campaigns. Build them into the product shape. Four types:

- **Referral programs (give-to-get):** Dropbox gives 500 MB to referrer and referee. Works when storage or usage is natural currency.
- **Shareable outputs:** Typeform and Calendly expose the user's output to every respondent; each respondent is a candidate new user.
- **Collaboration invites:** Slack requires inviting teammates to extract any value. Works when the product is inherently multiplayer.
- **Public profiles:** Calendly scheduling links, Linktree profiles, Notion public pages. Works when the user wants visibility.

Viral coefficient: $K = i \times c$ — `i` is average invites per user, `c` is conversion rate of invites to active users. K > 1 compounds without paid acquisition; K between 0.5 and 1 amplifies paid/organic; K < 0.5 is a bonus, not an engine. Measure K monthly per cohort; it decays as the addressable network saturates.

## NPS Collection

NPS is a coarse but comparable satisfaction metric. Collect it in-app, not by email.

- Single question: "How likely are you to recommend [Product] to a friend or colleague?" on a 0-10 scale.
- Follow-up open text: "What is the primary reason for your score?"
- Timing: Day 30 after activation, then every 90 days; once per user per cycle.
- Display as a non-blocking toast or side panel, not a modal.

Response workflow by segment:

- **Promoters (9-10):** trigger a review or referral ask within 24 hours.
- **Passives (7-8):** no immediate action; include in next feature-feedback cohort.
- **Detractors (0-6):** auto-open a customer-success ticket; human outreach within 1 business day reduces churn by 15 to 25 percentage points.

NPS = `(% promoters) - (% detractors)`. Above 40 is good for B2B SaaS; above 50 strong; above 70 elite.

## Feature Flags for PLG

Feature flags decouple deploy from release. For PLG they enable gradual rollout, A/B testing of onboarding, and flag-gated premium features.

Rollout ramp: deploy behind disabled flag -> enable for internal + paid pilots (1%) -> 5% free users, monitor 48h -> 25%, monitor 72h -> 100% if metrics stable or improved.

Minimal PostHog flag check:

```tsx
import { useFeatureFlagEnabled } from 'posthog-js/react'

export function OnboardingEntrypoint() {
  const newOnboarding = useFeatureFlagEnabled('new-onboarding-v2')
  return newOnboarding ? <OnboardingV2 /> : <OnboardingV1 />
}
```

Server-side equivalent in Node:

```ts
import { PostHog } from 'posthog-node'
const client = new PostHog(process.env.POSTHOG_KEY!)
const flag = await client.isFeatureEnabled('new-onboarding-v2', userId)
```

Always pair flag rollout with an A/B analysis measuring statistical significance on the primary metric (activation, conversion, retention).

## PLG Metrics

Six metrics are sufficient to run a PLG motion. Add more only when an executive can name the decision each will drive.

- **Activation rate** = activated users / signups. Target >= 40%. Measured weekly per cohort.
- **PQL conversion rate** = paid conversions within 30 days / PQLs in period. Target >= 25%.
- **Expansion MRR** = MRR from upgrades and seat additions as % of total MRR. Target 10% to 30% for mature PLG.
- **Viral coefficient (K-factor)** — monthly per cohort. Target >= 0.5 if viral is a material channel.
- **Time-to-value (P50 and P95)** — P50 under 10 minutes, P95 under 60 minutes.
- **Free-to-paid conversion rate** — rolling 90-day window. Target >= 3% for self-serve freemium; 15% to 25% for free-trial.

Review all six on a single weekly dashboard with a 4-week moving average next to every metric; single snapshots lie.

## Product Analytics Setup (PostHog)

PostHog is the reference implementation because it supports events, session replay, feature flags, experiments, and cohorts in one product. Mixpanel or Amplitude work equivalently; adjust syntax.

Complete client-side setup:

```ts
import posthog from 'posthog-js'

posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: 'https://eu.i.posthog.com',
  person_profiles: 'identified_only',
  capture_pageview: false,
})

// Identify on sign-in
posthog.identify(userId, { email, plan, signupDate })

// Capture custom events
posthog.capture('project_created', { projectId, templateId })

// Feature flag check
if (posthog.isFeatureEnabled('new-onboarding-v2')) {
  // render new flow
}
```

Event naming: `object_verb_past` — `project_created`, `invite_accepted`, `limit_hit`, `upgrade_completed`. Always attach a stable object id (`projectId`) and super-properties (`plan`, `tenant_id`) so every event is segmentable.

Build funnels for activation, PQL-to-paid, and upgrade; cohorts for PQLs, power users, detractors; retention charts weekly per signup cohort.

## Onboarding Checklist Pattern

Progressive disclosure through a persistent checklist turns onboarding from a one-shot tour into a multi-session activation engine.

Checklist item schema:

```ts
interface ChecklistItem {
  id: string
  title: string
  helpText: string
  action: { label: string; href?: string; onClick?: () => void }
  completedPredicate: (state: UserState) => boolean
}

const onboardingChecklist: ChecklistItem[] = [
  {
    id: 'create_workspace',
    title: 'Set up your workspace',
    helpText: 'Name your workspace and pick a timezone.',
    action: { label: 'Set up', href: '/settings/workspace' },
    completedPredicate: (s) => Boolean(s.workspace?.name && s.workspace?.timezone),
  },
  {
    id: 'first_project',
    title: 'Create your first project',
    helpText: 'Projects group related work; start with one.',
    action: { label: 'New project', onClick: () => openNewProjectModal() },
    completedPredicate: (s) => s.projectCount >= 1,
  },
  {
    id: 'invite_teammate',
    title: 'Invite a teammate',
    helpText: 'Collaboration is where this product compounds.',
    action: { label: 'Invite', onClick: () => openInviteModal() },
    completedPredicate: (s) => s.acceptedInviteCount >= 1,
  },
]
```

Evaluate `completedPredicate` on every render, not from a stored boolean — users complete steps through back-door paths (API, imports) and the checklist must reflect reality.

Track checklist completion as the activation metric; surface it until completed; fade it on first completion and hide after 7 days.

## Self-Serve Documentation

PLG products fail without self-serve documentation because nobody is paid to hold the user's hand. Treat docs as product surface.

- **In-app help widget** (Intercom, Crisp, built-in drawer) on every screen, pre-scoped to current page context.
- **Contextual tooltips** next to complex fields — an info icon opening a 1-sentence explanation, not a wall of text.
- **Knowledge base with search-first layout** — search bar is the hero element; categories are a fallback.
- **Video snippets under 90 seconds** per concept, not 20-minute tutorials. Loom, YouTube unlisted, or self-hosted with captions.

Structure around jobs ("How do I invite a teammate?") not features ("User management"). Every article answers one question and links to 3 related questions.

Measure time-on-page, search zero-results, and ticket-deflection rate. A deflection rate above 60% is the break-even point for PLG support economics.

## PLG for B2B SaaS

B2B PLG follows bottom-up adoption: individual contributor adopts, team follows, department standardises, executive signs the master contract.

Timeline pattern (Slack, Figma, Notion, Linear, Loom):

1. **Month 0:** individual sign-up on free tier solves a personal workflow problem.
2. **Month 1 to 3:** invites 1 to 3 teammates, team plan activated, billing on a personal card.
3. **Month 3 to 6:** department adoption, procurement conversation starts, team plan grows to 20 to 50 seats.
4. **Month 6 to 12:** executive signs a master agreement; SSO, audit, invoicing, SLA; ACV jumps from $1k to $50k+.

Operational consequences:

- Sales is triggered by usage signals (PQA — product-qualified account), not outbound prospecting.
- Billing must support personal card upgrades and later migration to invoice billing without losing data or seats.
- Admin features (SSO, SCIM, audit log, custom roles) are the upgrade lever, not individual features.
- Procurement artefacts (SOC 2, DPA, MSA, security questionnaire) must be ready before the first enterprise conversation, or the deal stalls for a quarter.

Example: Figma reached $400M ARR through bottom-up adoption — design team invites PMs, PMs invite engineers, organisation standardises, CTO signs the enterprise contract.

## Growth Loops vs Funnels

Funnels and loops model different growth dynamics. Confusing them produces wasted spend.

- **Funnels:** linear, users enter at the top, leak at each step, require continuous fresh inputs. Good for modelling conversion in a single session or campaign.
- **Loops:** output of one cycle feeds the input of the next cycle. Sustainable compounding comes from loops, not funnels.

Three canonical loops:

- **Viral loop:** user creates content or invites -> new users see content or receive invite -> new users sign up -> new users create more content or invites.
- **Content loop:** user-generated content indexed by search -> search visitors sign up -> more users create more content.
- **Paid loop:** revenue funds paid acquisition -> paid acquisition brings users -> users pay -> more revenue funds more acquisition.

ASCII diagram of a viral loop:

```
  +-----------+    +----------+    +--------+    +-------------+
  | New User  |--> | Activate |--> | Invite |--> | Invitee     |--+
  | Sign-up   |    | (value)  |    | /share |    | sees value  |  |
  +-----------+    +----------+    +--------+    +-------------+  |
       ^                                                          |
       +----------------------------------------------------------+
                         (feeds next cycle)
```

Design the loop explicitly: name each node, measure conversion between nodes, identify the weakest edge, improve it, rerun. A loop with a 10% leak per node still compounds if cycle time is short enough.

## Companion Skills

- `saas-growth-metrics` — AARRR funnel, NPS, cohort retention, A/B testing framework
- `saas-business-metrics` — MRR/ARR/LTV/CAC — the revenue metrics that PLG ultimately drives
- `habit-forming-products` — Hooked model, variable rewards, investment phase
- `lean-ux-validation` — validate PLG hypotheses with smoke tests before building
- `subscription-billing` — trial/plan lifecycle that PLG motions convert into
- `ux-writing` — microcopy for activation prompts, empty states, upgrade CTAs

## Sources

- *Product-Led Growth* — Wes Bush (Product-Led Alliance)
- *Hacking Growth* — Sean Ellis & Morgan Brown (Currency)
- *Hooked* — Nir Eyal (Portfolio)
- PostHog documentation — `posthog.com/docs`
- OpenView PLG Index — `openviewpartners.com`