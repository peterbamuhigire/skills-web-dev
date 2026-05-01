# Sales Motions Picker

Choose the motion that matches how your buyer actually buys. Forcing a motion on the wrong deal size destroys unit economics — either CAC blows past LTV (enterprise motion on SMB deals) or close rate collapses (self-service motion on complex buyers).

## Decision tree

```text
Q1. Can a single person evaluate, decide, and pay without asking anyone?
    Yes  -> Q2
    No   -> Q4

Q2. Does the buyer reach first value in under 15 minutes from signup?
    Yes  -> Q3
    No   -> treat as SMB transactional even if ACV is low

Q3. Is blended ACV under $1,200 / year?
    Yes  -> Self-service (PLG). No AE touch. Invest in activation, in-app guidance, and low-friction billing.
    No   -> Self-service with assisted upgrade path (a "growth" rep triggered on usage signal).

Q4. Is the decision owned by a single budget holder with simple procurement?
    Yes  -> Q5
    No   -> Q6

Q5. Is ACV $1k-$10k and the cycle under 30 days?
    Yes  -> SMB transactional (inside sales, one full-cycle rep).

Q6. Are there 2-6 stakeholders, a real evaluation (demo + trial or pilot), and ACV $10k-$100k?
    Yes  -> Mid-market (SDR + AE + shared SE, 30-90 day cycle).
    No   -> Q7

Q7. Are there 6+ stakeholders, security review, legal red-lines, and ACV $100k+?
    Yes  -> Enterprise (field AE + dedicated SE + deal desk, 90-270 day cycle).
```

## Motion reference table

| Motion | Blended ACV | Cycle | Touch | Typical team for $10M ARR | Example companies |
|---|---|---|---|---|---|
| Self-service / PLG | $0-$1.2k | minutes-hours | product-led, no human in buying | growth + PMM + support; no AEs | Notion (early), Calendly, Loom, Figma (free plan), Grammarly |
| SMB transactional | $1.2k-$10k | 1-30 days | inside, full-cycle rep | 6-10 full-cycle AEs, BDR for inbound | HubSpot (SMB), Pipedrive, Freshworks (SMB), Calendly Teams |
| Mid-market | $10k-$100k | 30-90 days | inside + light SE | 4-6 AEs, 4-6 SDRs, 1-2 SEs, 1-2 CSMs | Gong (mid), Asana Business, Monday.com Enterprise, Zendesk mid-market |
| Enterprise | $100k+ | 90-270 days | field + SE + procurement | 4-6 AEs, 4-6 SDRs, 3-4 SEs, 2-3 CSMs, 1 deal desk | Salesforce, Workday, Snowflake, Datadog (top tier), Palo Alto Networks |

## Signals you should split into two motions

Split when the motion you have is losing deals at the edges of the ACV band:

- Deals under $10k take the same AE hours as deals at $50k — you are over-serving. Create an SMB pod that closes under $10k with a lighter process.
- Deals over $100k repeatedly stall in procurement while your AEs run a mid-market playbook — create an enterprise motion with a dedicated SE and security lead.
- Win rate is >30% in one band and <10% in another — the playbook fits one, not the other.
- AE quota attainment is bimodal (top half >110%, bottom half <60%) and correlates with deal size — your reps are specialising informally; formalise it.
- Onboarding time varies 10x between the largest and smallest customers — product, not sales, is also forked; align CSM motions.

## Signals you should combine motions

Combine when carrying two motions is not paying for itself:

- You have <8 AEs total. Two motions at that scale means fewer than 4 reps per motion — no bench, no career path, no manager leverage.
- Your smallest "enterprise" deals and largest "mid-market" deals are indistinguishable in effort — the seam is fictional.
- One motion is shrinking (<20% of bookings) with no strategic reason to keep it — fold it.

## Common misassignments

- Pricing demands enterprise motion, product demands PLG. Symptom: sales-led onboarding for a product that users want to self-serve. Fix: unbundle free/self-serve tier from enterprise SKU and let PQL (product-qualified lead) signal AE engagement.
- Target personas are individual contributors but ACV pushes you to enterprise. Symptom: AEs never find budget holders. Fix: reposition to team or department-level buyer, raise entry ACV.
- Founder sells enterprise deals; first AE hire flounders with SMB leads. Fix: match hire profile to the motion you actually want to scale, not the motion the founder knows.

## Cross-references

- `saas-business-metrics` — CAC payback targets per motion (PLG <6 months; enterprise <24 months).
- `software-pricing-strategy` — packaging that supports the motion (self-serve plans vs enterprise SKU).
- `subscription-billing` — invoicing vs card capture differs per motion.

## Anti-patterns

- Hiring an enterprise AE to "upgrade" your SMB book. They will not prospect; they will wait for $100k deals that your pipeline cannot produce.
- Running PLG and enterprise from the same comp plan. PLG needs activation metrics; enterprise needs bookings. Mixing kills both.
- Declaring "product-led" without investing in activation, onboarding telemetry, and in-app conversion — that is just underfunded SMB.
