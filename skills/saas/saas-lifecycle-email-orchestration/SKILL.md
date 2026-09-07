---
name: saas-lifecycle-email-orchestration
description: Use when designing SaaS lifecycle email triggers, branches, suppression, churn signals, upgrades, reactivation, referrals, or attribution.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Lifecycle Email Orchestration
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.


## Required Inputs

| Input | Required | Use |
|---|---|---|
| Tenant, product, and lifecycle scope | yes | Bound the SaaS decision |
| Current architecture, plans, policies, and constraints | yes | Preserve enforceable behaviour |
| Production data or verified evidence | conditional | Validate thresholds and migrations |

## Capability and permission contract

Default to read-only analysis. Change configuration, billing, identity, tenant data, infrastructure, or customer communications only with explicit authority, least-privilege credentials, tenant scope, rollback, and auditable approval. Never expose secrets or cross tenant boundaries.

## Degraded mode

If production access, policy, telemetry, or authoritative records are unavailable, produce a labelled design or dry-run plan. Do not claim deployment, reconciliation, deletion, delivery, or measured outcomes; list missing evidence and verification.

## Decision rules

| Condition | Action | Stop condition |
|---|---|---|
| Tenant isolation, money, identity, or deletion is affected | Require approval and rollback evidence | Scope or authority is ambiguous |
| Evidence supports a reversible change | Stage, test, and record it | Acceptance checks fail |
| Only partial context is available | Return assumptions and validation | A production claim cannot be verified |

## Domain Anti-Patterns

- Applying one tenant's policy or data to another. Fix: enforce tenant scope at every boundary.
- Mutating production from an advisory request. Fix: remain read-only until authority is explicit.
- Inventing limits, prices, metrics, or compliance claims. Fix: use authoritative records or mark them unresolved.
- Shipping without rollback and audit evidence. Fix: stage and retain before/after proof.
- Treating a missing dependency as successful. Fix: name the blocked verification.


<!-- dual-compat-start -->
## Use When

- Designing the six core lifecycle email sequences for a SaaS — welcome / onboarding, behavioral / feature-discovery, upgrade / upsell, retention, reactivation, referral.
- Replacing a single "drip campaign" with event-driven branched automation.
- Coordinating in-app upgrade prompts with email upgrade prompts so they don't double-fire.
- Attributing revenue to email touches (control vs treatment cohorts).
- Wiring PQL signals into upgrade emails and churn-risk signals into retention emails.

## Do Not Use When

- The task is the underlying email infrastructure (ESP, deliverability, suppression) — use `saas-transactional-email-infrastructure`.
- The task is HTML template authoring — use `tabler-email-templates`.
- The task is acquisition cold email — use sales/marketing tooling outside this engine.

## Required Inputs

- The product's activation event (the "aha moment") — from `product-led-growth`.
- PQL scoring outputs — from `product-led-growth`.
- Churn-risk signals — from `saas-growth-metrics` or `product-led-growth`.
- Plan / tier catalogue and upgrade paths — from `subscription-billing` and `saas-entitlements-and-plan-gating`.
- Trial policy — from `subscription-billing`.

## Workflow

1. Read this `SKILL.md`.
2. Define the user data model the email tool needs (§2) — contact attributes + event stream.
3. Design each of the six sequences (§3-§8) — trigger, branches, suppression, send cadence.
4. Wire the trigger contract (§9) — what events fire what sequences.
5. Coordinate with in-app prompts (§10) — avoid double-firing.
6. Set up revenue attribution (§11) — control vs treatment per sequence.
7. Apply anti-patterns (§12).

## Quality Standards

- Every email belongs to exactly one of the six sequences (or is purely transactional).
- Every sequence is **event-triggered**, not scheduled blast.
- Every email obeys the suppression list (transactional / lifecycle / marketing categories).
- Every send/open/click written to the warehouse with cohort attributes.
- Revenue attributed per sequence; under-performing sequences killed, not iterated forever.

## Anti-Patterns

- "Drip campaigns" running on calendar schedule regardless of user behavior.
- Welcome email sent after the user has already activated (looks robotic).
- Upgrade emails sent to users on the highest plan.
- Retention emails sent to users who just renewed.
- Reactivation emails ignoring transactional consent → spamming.
- Sequences without branches (every user gets the same email at T+1, T+3, T+5).
- No A/B test cadence — sequences ossify.

## Outputs

- The six sequence specs (trigger, branches, emails, send conditions).
- Trigger contract — event → sequence mapping.
- Suppression matrix per sequence.
- Coordination contract with in-app prompts.
- Revenue-attribution dashboard.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Six-sequence catalogue | Markdown doc with branch diagrams | `docs/email/lifecycle-sequences.md` |
| Release evidence | Trigger-event contract | Markdown table | `docs/email/trigger-contract.md` |
| Operability | Email revenue attribution dashboard | Dashboard link | `docs/email/attribution-dashboard.md` |

## References

- `references/sequence-welcome-onboarding.md` — branched welcome flow with activation check.
- `references/sequence-behavioral.md` — feature-discovery, approaching-limit, inactive nudges.
- `references/sequence-upgrade.md` — PQL-triggered upgrade flow.
- `references/sequence-retention.md` — churn-risk triggered save sequences.
- `references/sequence-reactivation.md` — long-dormant win-back.
- `references/sequence-referral.md` — NPS-promoter and active-user referral.
- Companion: `saas-transactional-email-infrastructure`, `tabler-email-templates`, `product-led-growth`, `saas-growth-metrics`, `saas-entitlements-and-plan-gating`.

<!-- dual-compat-end -->

## §1 The Six Sequences

From Garbugli's *SaaS Email Marketing Playbook*:

| # | Sequence | Trigger | Primary goal |
|---|---|---|---|
| 1 | **Welcome & Onboarding** | `user.signed_up` or `tenant.created` | Drive to activation (the aha moment) |
| 2 | **Behavioral & Lifecycle** | Specific feature/usage events (or their absence) | Drive depth, prevent stall |
| 3 | **Upgrade / Upsell / Expansion** | PQL signals (approaching limit, gated-feature hit, sustained engagement) | Expand revenue |
| 4 | **Retention / Churn Prevention** | Churn-risk score threshold crossed | Save accounts |
| 5 | **Reactivation** | Long inactivity (e.g., 60 days no login) | Win back dormants |
| 6 | **Referral** | NPS-promoter score, sustained activity | Drive viral acquisition |

Bonus (out of scope here, owned by sales): **Cold / acquisition** — outbound prospecting.

## §2 The Data Model the Email Tool Receives

Contact attributes (sticky on the contact record in Customer.io / Braze):
- `email`, `name`, `tenant_id`, `tenant_name`, `tenant_plan`, `tenant_mrr`
- `role` (owner / admin / member / billing)
- `signup_date`, `first_login_date`, `last_login_date`
- `lifecycle_stage` (visitor / signup / trial / activated / paid / churned / reactivated)
- `acquisition_channel`, `utm_source/medium/campaign`
- `firmographics` (industry, company_size, country, language)
- `activation_state` (boolean + date)
- `pql_score`, `churn_risk_score`, `nps_score`, `last_nps_date`
- `unsubscribed_categories[]`

Events (firehose):
- `user.signed_up`, `user.activated`, `user.logged_in`, `user.invited_teammate`
- `feature.X.used_first_time`, `feature.X.used_repeat`
- `trial.started`, `trial.day_N`, `trial.ended`, `trial.converted`
- `subscription.upgraded/.downgraded/.cancelled`
- `payment.failed`, `payment.succeeded`
- `support.ticket.created`, `support.csat_low`
- `usage.approaching_limit`, `usage.limit_hit`
- `gate.denied` (feature locked behind higher plan)

Wire via the event bridge from `saas-transactional-email-infrastructure`.

## §3 Sequence 1 — Welcome & Onboarding

**Trigger:** `user.signed_up` (or `tenant.created` if more than one user joins simultaneously).

**Goal:** drive to activation event within trial window.

**Structure (typical 5-7 email branch):**
```
T+0       Welcome — confirm signup, deliver core CTA, set expectations
T+1d      Getting Started — concrete first step
T+3d      Feature Discovery — high-value feature the user hasn't touched
            if user.activated: branch → "you're flying" follow-up
            else:               branch → "having trouble? here's help"
T+5d      Social proof — case study from similar customer
T+7d      Activation check
            if user.activated: branch → "next milestone" + power-feature
            else:              branch → support-offer + troubleshooting
T+trial-3 Trial-end warning — value-led
T+trial   Trial-end conversion — offer + paywall CTA
            branch on subscription.created → "welcome to paid" (sequence ends)
            branch on no subscription → "extended trial" or downgrade-to-free
```

**Suppression:**
- Skip if already `paid` plan at signup (B2B paid trial → straight to enterprise sequence).
- Stop sending if `user.activated` past T+3 + `feature.X.used_repeat` (user is in product).
- Always honour explicit unsubscribe.

## §4 Sequence 2 — Behavioral & Lifecycle

**Trigger:** event presence or absence in product.

**Examples:**

| Email | Trigger condition |
|---|---|
| "Try the X feature" | `user.activated AND NOT feature.X.used_first_time AND days_since_signup ≥ 7` |
| "Approaching your limit" | `usage.approaching_limit (80% threshold)` |
| "We noticed you haven't logged in" | `last_login_date < now - 14d` |
| "Your team is collaborating" | `collaboration_event_count ≥ 5 in last 7d` (positive reinforcement) |
| "How can we help?" | `support.csat_low` recently OR repeat-failed actions |

**Send cadence:** event-driven; capped at 2 / week per user / category.

## §5 Sequence 3 — Upgrade / Upsell / Expansion

**Trigger:** PQL score threshold OR specific gate hit.

**Examples:**

| Trigger | Email |
|---|---|
| `usage.approaching_limit (90%)` on a plan-tied limit | "You're close to your limit — upgrade to keep moving" |
| `gate.denied (feature=X)` repeated 3x in 7 days | "Try X free for 14 days" (in-app trial of feature) |
| `pql_score >= threshold` (Pro-tier behavior on Free plan) | "It looks like you're ready for Pro" |
| `active_users / max_seats >= 0.8` | "Add 5 seats and save 20%" |

**Coordinate with in-app:** if the in-app prompt fires today, suppress the email today.

## §6 Sequence 4 — Retention / Churn Prevention

**Trigger:** churn-risk score crosses threshold OR specific churn-precursor events.

**Examples:**

| Trigger | Email |
|---|---|
| `churn_risk_score >= 0.7` | "Are we missing something?" — survey + CS contact |
| `subscription.downgraded` | "Welcome to the new plan — here's what you keep" |
| `subscription.cancel_initiated` (in-product) | Save flow — pause / discount / direct CS |
| `payment.failed` | Dunning email + card update CTA |

**Suppression:** stop if user un-cancels or upgrades.

## §7 Sequence 5 — Reactivation

**Trigger:** long inactivity (`last_login_date < now - 60d`, configurable).

**Structure:**
```
T+60d   "We miss you" — emotional, value-led
T+67d   "What's new" — features added since they left
T+74d   "Special offer" — discount, extended use, or restore-data offer
T+81d   "Final goodbye" — last chance + permission to fully unsubscribe
```

After the sequence, mark `permanently_dormant` and move to broadcast-only suppression.

## §8 Sequence 6 — Referral

**Trigger:** `nps_score >= 9` recent OR `active_user >= 30d sustained + plan = paid`.

**Examples:**
- "You're getting value — would you tell a friend?" (links to in-app invite flow)
- "Give X, get X" referral CTA
- Champion-program invite (for enterprise)

## §9 Trigger Contract

The contract between product events and sequence enrolment:

| Event | Sequences it can trigger |
|---|---|
| `user.signed_up` | Welcome & Onboarding (enroll) |
| `user.activated` | Welcome & Onboarding (branch), Behavioral (enroll) |
| `usage.approaching_limit` | Behavioral (warning), Upgrade (if plan-tied) |
| `gate.denied` | Upgrade (after threshold) |
| `pql_score_increase` | Upgrade |
| `churn_risk_increase` | Retention |
| `subscription.cancel_initiated` | Retention (save flow) |
| `last_login_date passed N days` | Behavioral nudge → Reactivation after 60d |
| `nps_score >= 9` | Referral |
| `subscription.cancelled` | Retention (exit survey), then Reactivation in 60-90d |

The email tool (Customer.io / Braze) consumes events and routes per the contract.

## §10 Coordination with In-App Prompts

Single rule: **one channel at a time per user per upgrade-context per day**.

```
On upgrade_signal_for_user:
  if user.in_app_session_active:
    → fire in-app prompt (Pendo / Appcues / built-in)
    → suppress email today
  else:
    → fire email
    → suppress in-app prompt for 24h after click
```

Store the coordination state in a `prompt_dispatcher` service that the email tool and in-app tool both consult.

## §11 Revenue Attribution

Every send writes:
- `send_id`, `user_id`, `tenant_id`, `sequence`, `email_id`, `template_id`, `cohort_tag`, `timestamp`.

Every open/click/conversion writes back with the `send_id` lineage.

Materialise in the warehouse:
- Per-sequence conversion rate (sent → opened → clicked → converted).
- Per-email revenue (sum of `subscription.upgraded` MRR delta in 7d post-click).
- Control vs treatment: maintain a hold-out cohort (e.g., 5% random skip) per sequence to measure incremental revenue.

## §12 Anti-Patterns

- **Scheduled drip ignoring user behavior** — welcome email T+3 still hits a user who already activated and upgraded by T+1.
- **No A/B test rhythm** — emails go stale, conversion decays silently.
- **Upgrade emails to users on the top plan** — annoying; bad attribution.
- **Reactivation that pings explicit unsubscribers** — legal liability + spam.
- **No `prompt_dispatcher` — in-app + email double-fire** — user sees the same nudge twice in 5 minutes.
- **Sequences live in the email tool only** — engineering can't reason about them; can't test the trigger logic.
- **Cancellation reason not captured** — win-back sequence can't personalise.

## §13 Read Next

- `saas-transactional-email-infrastructure` — the infra underneath.
- `tabler-email-templates` — the templates each sequence uses.
- `product-led-growth` — PQL + activation signals.
- `saas-entitlements-and-plan-gating` — `gate.denied` event source.
- `saas-growth-metrics` — churn-risk + cohort retention.
- `subscription-billing` — billing-event triggers.
