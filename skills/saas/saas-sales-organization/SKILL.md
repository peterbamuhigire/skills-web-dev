---
name: saas-sales-organization
description: Use when designing or scaling a SaaS sales organisation — sales motions, roles (SDR/BDR/AE/CSM/SE), pipeline stages, lead-to-cash, territory design, quota/commission, sales ops fundamentals, onboarding/ramp, and hiring rubrics. Sourced from "Blueprints for a SaaS Sales Organization" (van der Kooij, Pizarro).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Sales Organization
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

- Use when designing or scaling a SaaS sales organisation — sales motions, roles (SDR/BDR/AE/CSM/SE), pipeline stages, lead-to-cash, territory design, quota/commission, sales ops fundamentals, onboarding/ramp, and hiring rubrics. Sourced from "Blueprints for a SaaS Sales Organization" (van der Kooij, Pizarro).

## Workflow

- For premium or enterprise offers, align the sales motion with account research, executive problem framing, proof assets, business case, stakeholder mapping, and concrete next-step commitments.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Sales organisation design document | Markdown doc covering motions, role mix (SDR/BDR/AE/CSM/SE), pipeline stages, and lead-source allocation | `docs/business/sales-org-design.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Design a sales organisation that matches your product motion, customer segment, and deal size. This skill is the "how we sell" counterpart to `saas-business-metrics`, `subscription-billing`, `software-pricing-strategy`.

## When this skill applies

- Founder-led sales has worked; it's time for the first hires.
- Scaling from $1M to $10M ARR and the sales team is breaking.
- Launching into a new segment (SMB → mid-market, or mid-market → enterprise).
- Designing sales ops foundations: CRM hygiene, forecasting, pipeline reviews, QBRs.
- Replacing a broken commission plan.
- Hiring SDRs, AEs, CSMs, or SEs and getting the roles right.

## Pick the sales motion before hiring anyone

```text
Deal size < $500 ARR, high volume, instant value           -> Self-service (product-led growth)
Deal size $1k-$10k ARR, low touch                          -> SMB transactional (inside sales)
Deal size $10k-$100k ARR, medium touch, some evaluation    -> Mid-market (inside + SE)
Deal size $100k+ ARR, complex evaluation, procurement      -> Enterprise (field sales + SE + security review)
```

Rule: your motion is determined by the customer, not by preference. If buyers research and decide solo, self-service works. If buyers need help articulating value to a buying committee, enterprise is the only motion.

Premium sales rule: do not ask high-value buyers for time with generic outreach. Use trigger events, role-specific pains, relevant proof, a diagnostic point of view, and a clear reason the meeting is worth executive attention.

See `references/sales-motions-picker.md`.

## Roles and when to specialise

**SDR (Sales Development Representative)** — outbound prospecting; qualifies leads; hands off to AE.
**BDR (Business Development Representative)** — inbound-focused; qualifies marketing leads.
**AE (Account Executive)** — owns the deal from qualified opportunity to close.
**CSM (Customer Success Manager)** — post-sale adoption, renewal, expansion.
**SE (Solutions Engineer / Sales Engineer)** — technical discovery, demos, custom POCs.
**AM (Account Manager)** — named-account relationship, renewal, expansion.

**When to split AE into SDR + AE:**

- AEs spend >30% of time on prospecting.
- Deal cycle has distinct "qualify" and "close" phases.
- Team of 3+ AEs and growing.

**When to add SE:**

- Deals need custom demos or POCs.
- Win rate drops after technical stage.
- AEs cannot articulate the product deeply enough on technical probes.

**When to add CSM:**

- Net revenue retention is flat or declining.
- You have 50+ customers and adoption is inconsistent.
- Renewals are missed through neglect, not dissatisfaction.

See `references/roles-specialisation.md`.

## Pipeline stages that stand up to scrutiny

Every stage has an exit criterion. No exit criterion = not a stage.

```text
0. Lead               — identified contact with fit signal
1. Qualified          — BANT / MEDDIC / SPICED criteria met; discovery call scheduled
2. Discovery          — pain identified, quantified impact, buying process mapped
3. Evaluation         — demo / POC / trial in progress; champion identified
4. Proposal           — pricing + terms delivered; procurement engaged
5. Negotiation        — contract red-lines; legal review
6. Closed Won / Lost  — booked
```

Discipline: a stage can only move forward when the exit criterion is provable (email, calendar invite, signed MSA). "I feel they're close" is not a criterion.

See `references/pipeline-stages.md`.

## Lead-to-cash

```text
Marketing / SDR produces lead
  -> Qualified (MQL -> SQL) — agreed definition with sales
    -> Opportunity (AE owns) — stages 2 to 6
      -> Closed Won -> Order booked -> Onboarding starts
        -> Customer Success adoption + expansion
          -> Renewal + upsell
```

The handoffs are where deals die. Document exactly who owns what at each handoff and what fields in CRM must be populated.

See `references/lead-to-cash.md`.

## Territory design

Options:

- **Round-robin** — simplest; fair; no vertical expertise.
- **Geographic** — by country / region / time zone.
- **Vertical** — by industry (fintech, health, logistics).
- **Named-account** — each AE owns a list; best for enterprise.
- **Segment** — by employee count or ARR band.

Rule: design for fairness and motion. Don't split territories such that one person gets all the easy accounts. Rebalance yearly.

See `references/territory-design.md`.

## Quota + commission

Quota = annual sales target per AE. OTE = base + variable at 100% quota.

Typical structures:

- **Base : variable = 50:50** for AEs (SaaS norm).
- **Accelerators** — earn more above 100% attainment (e.g., 1.5x or 2x rate).
- **SPIFs** — short incentive pushes (new product, specific segment).
- **Clawbacks** — commission repaid if customer churns before N months.
- **Commission paid on cash collected** — not just bookings, to align with collections.

Rule of thumb: quota = 5× OTE for AEs in most SaaS categories. Less and you underperform; more and top performers leave.

See `references/quota-commission-design.md`.

## Sales ops fundamentals

CRM hygiene non-negotiables:

- Every opportunity has a close date that moves only with justification.
- Every stage has the required fields populated.
- Activity is logged in CRM, not in email or Slack.
- Weekly pipeline scrub — owners remove dead deals.
- Monthly forecast — bottom-up from AEs, reviewed by managers, committed to leadership.

Forecasting accuracy bands:

- Commit: >90% confidence, weighted average.
- Best case: >50% confidence.
- Pipeline: the rest.

If forecast is off by >15% two quarters in a row, there's a stage-definition problem, not a people problem.

See `references/sales-ops-fundamentals.md` and `references/forecasting-accuracy.md`.

## Onboarding + ramp

New AE ramp = time from start to quota-carrying. Typical 3–6 months.

Onboarding curriculum (weeks 1–4):

1. Product + value — pitch, demo script, objection handling.
2. Industry + personas — who buys, why, typical pain.
3. Proof assets — case studies, calculators, diagnostics, implementation roadmaps, objection handling, and premium positioning.
4. Process + tools — CRM, stage definitions, forecasting, cadence tools.
5. Shadow + role-play — with peers + manager.
6. First calls + first demos — supervised.

Rule: protect ramp. Don't throw accounts at an unfinished AE; outcomes hurt the AE, the customer, and the brand.

See `references/onboarding-ramp.md`.

## Hiring rubrics

Per role, define:

- **Success profile** — the 3–5 behaviours the top 25% demonstrate.
- **Disqualifiers** — signals that mean no, regardless of rapport.
- **Interview loop** — who evaluates what (recruiter screen, manager, peer, role-play, cross-functional).
- **Role-play** — always. Close one discovery call with the candidate as the AE.
- **Reference calls** — on-list + back-channel.

See `references/hiring-rubrics.md`.

## Anti-patterns

- Hiring AEs before product-market fit — they can't close what the market doesn't want.
- Hiring one AE and expecting them to figure it out alone. Hire two or wait.
- Splitting SDR from AE before you have 3+ AEs — too much overhead for a small team.
- Commission plans that reward non-retaining deals (no clawback on churn).
- Stage definitions that allow subjective advancement.
- Forecasting by gut instead of stage-weighted methodology.
- Quotas that no one hits (demotivating) or everyone hits (too low).
- Not firing reps clearly below quota after 2–3 quarters with coaching — unfair to team and customers.

## Read next

- `saas-business-metrics` — the metrics the sales org drives (MRR, CAC, payback, NRR).
- `subscription-billing` — the billing side of the quote-to-cash flow.
- `software-pricing-strategy` — what you sell at what price.
- `product-strategy-vision` — product direction that the sales org communicates.
- `competitive-analysis-pm` — win/loss analysis inputs.

## References

- `references/sales-motions-picker.md`
- `references/roles-specialisation.md`
- `references/pipeline-stages.md`
- `references/lead-to-cash.md`
- `references/territory-design.md`
- `references/quota-commission-design.md`
- `references/sales-ops-fundamentals.md`
- `references/forecasting-accuracy.md`
- `references/onboarding-ramp.md`
- `references/hiring-rubrics.md`
## Quality Standards

Role design, stage exits, capacity, quota, compensation, handoffs, and ramp measures must derive from one declared sales motion and named customer segment.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| SaaS sales operating model | Revenue leadership and sales operations | Sales motion, role handoffs, stage exits, territory rules, capacity assumptions, quota logic, and ramp measures align with the chosen market segment |
