# Pipeline Stages

A stage without a provable exit criterion is not a stage — it is wishful reporting. Use exit criteria your manager can verify in the CRM without asking the rep.

## Canonical B2B SaaS stages

| # | Stage | Exit criterion (provable artefact) | Stage weight (mid-market) | Owner |
|---|---|---|---|---|
| 0 | Lead | Contact identified with fit signal (firmographic + behaviour) | n/a (not in forecast) | SDR |
| 1 | Qualified (SQO) | Discovery meeting held; MEDDIC/SPICED fields populated; next step calendared | 10% | SDR -> AE |
| 2 | Discovery | Pain quantified (£/$ impact); buying process mapped; champion named | 20% | AE |
| 3 | Evaluation | Demo delivered OR POC kicked off with success criteria; economic buyer engaged at least once | 40% | AE + SE |
| 4 | Proposal | Written proposal + pricing delivered; procurement/legal contact introduced | 60% | AE |
| 5 | Negotiation | Redline in progress or verbal agreement on price/terms; MSA under review | 80% | AE + Deal Desk |
| 6 | Closed Won / Lost | Signed order form; Closed Lost requires disposition code + competitor + primary reason | 100% / 0% | AE |

Rule: a deal can only advance when the exit criterion for the current stage is evidenced in CRM (email thread, meeting note, document link). "Strong intent" is not evidence.

## Qualification framework — pick one, use consistently

### MEDDIC (best for enterprise)

- **M**etrics — quantified business impact the buyer expects (£/$/%).
- **E**conomic buyer — the person who can say yes without escalation.
- **D**ecision criteria — how they will judge options.
- **D**ecision process — the steps and timeline from evaluation to signature.
- **I**dentify pain — the consequence of doing nothing.
- **C**hampion — internal sponsor who sells for you.
- (MEDDICC adds **C**ompetition.)

### BANT (best for SMB transactional)

- **B**udget — money allocated or available.
- **A**uthority — can the contact sign?
- **N**eed — is the pain validated?
- **T**imeline — when do they need to be live?

### SPICED (best for mid-market, consultative)

- **S**ituation, **P**ain, **I**mpact, **C**ritical event, **D**ecision.

Whichever you pick, map the framework fields to your CRM as required fields at the correct stage. Forecast reviews should walk through the framework, not through vibes.

## Stage weights and forecasting

Weights are for pipeline-value roll-up, not individual deal probability. Good AEs will have some 40% deals they call commit and some 60% deals they call best-case. Use the weights for bottom-up pipeline maths; use the commit/best-case call for forecast.

## Dead-deal rules

A deal is dead when any one of these is true:

- No contact with the buyer in 21 days (30 for enterprise) and no scheduled next step.
- Champion has left or gone silent after three touches.
- Budget confirmed gone (cycle, reorg, procurement freeze).
- Close date has slipped 2+ times without stage advancement.

Dead deals must be marked Closed Lost with a disposition code. They do not "float" back into the current quarter. If they revive, create a new opportunity.

## Sample exit-criteria template (CRM field set)

```text
Stage 1 (Qualified) requires:
  - Meeting held (date logged)
  - Economic buyer or champion identified (contact linked)
  - Problem statement captured (free-text field)
  - Estimated close date set
  - Expected ACV set

Stage 3 (Evaluation) requires:
  - Demo or POC delivered (attachment or link)
  - Success criteria documented (custom field)
  - At least one stakeholder beyond champion engaged
  - Competitor named (picklist)

Stage 4 (Proposal) requires:
  - Proposal sent (document attached)
  - Procurement contact captured
  - Decision date from buyer (not guess) captured
```

## Stage hygiene rituals

- **Weekly scrub (Monday)**: each AE removes or updates any stage without artefact.
- **Forecast review (Tuesday)**: manager challenges every commit and best-case deal against MEDDIC/SPICED fields.
- **Pipeline council (end of month)**: cross-functional review of any deal >$100k or sliding stage for 3 weeks.

## Cross-references

- `saas-business-metrics` — win rates and cycle time benchmarks per stage.
- `subscription-billing` — order form and billing fields needed at Closed Won.
- `software-pricing-strategy` — when Proposal stage requires pricing approval.

## Anti-patterns

- Stages named after what the rep did ("Demo given") rather than what the buyer agreed to ("Buyer committed to evaluation plan").
- Advancing deals to reach a pipeline coverage number — kills forecast accuracy.
- Allowing "on hold" or "nurture" mid-pipeline stages that accumulate zombie deals; route to a re-engage cadence instead.
- Keeping close dates in the past — a close date that has slipped is a data signal, not an inconvenience.
