# Lead-to-Cash

The handoffs are where revenue leaks. Document each handoff as a contract between two roles with an SLA, required fields, and a rejection path.

## End-to-end map

```text
Anonymous visitor
  -> Marketing captures (form fill, content download, event, PLG signup)
    -> Lead scored (MQL if above threshold)
      -> Routed to BDR (inbound) or SDR (outbound for target account)
        -> Qualified (SQL / SQO) — discovery meeting held
          -> AE accepts opportunity — stages 2 through 6
            -> Closed Won
              -> Order processed (billing, provisioning)
                -> Onboarding specialist (kickoff, configuration, go-live)
                  -> CSM assumes ownership (adoption, QBRs, expansion)
                    -> Renewal (AM or CSM, depending on motion)
                      -> Expansion (upsell / cross-sell)
```

## Handoff contracts

### 1. Marketing -> BDR (MQL -> SQL)

- **SLA**: BDR first touch within 5 minutes for high-intent inbound (demo request, pricing page dwell), 2 hours for content MQLs.
- **Required fields**: lead source, campaign, company, role, firmographic match score, UTM.
- **Rejection path**: if not qualified, BDR returns lead with reason code (wrong persona, wrong ICP, student/competitor, duplicate). Marketing reviews rejection rate weekly. Target rejection <25%.
- **Definition of qualified (SLA contract)**: written, agreed once per quarter, signed by CMO and VP Sales.

### 2. SDR/BDR -> AE (SQO acceptance)

- **SLA**: AE accepts or rejects the opportunity within 48 hours. On accept, AE runs first meeting within 5 business days.
- **Required fields**: discovery notes, pain statement, company size, estimated ACV, expected close date, next step.
- **Rejection path**: AE rejects with reason (no budget, wrong title, no timeline, unqualified). SDR reviews; if disputed, Sales Manager adjudicates. Rejection rate >30% triggers a joint SDR-AE calibration.
- **SDR credit**: booked on SQO acceptance, not on Closed Won, to prevent AE gaming.

### 3. AE -> Onboarding (Closed Won)

- **SLA**: within 24 hours of Closed Won, AE schedules a kickoff call including onboarding specialist, CSM, and the customer's champion + admin.
- **Required fields**: signed order form, billing contact, technical contact, use cases, success criteria from the deal, any commitments made during the sale.
- **"Scar tissue" field**: AE documents any unusual commitments (custom feature promises, discount conditions, contractual deviations) so onboarding and CSM do not discover them later.

### 4. Onboarding -> CSM (Go-live)

- **SLA**: 30/60/90-day plan established at kickoff; CSM assumes ownership at go-live (users provisioned, first value delivered).
- **Required fields**: go-live date, admin users trained, success criteria status, adoption milestones, red/amber/green health score.
- **Rejection path**: CSM can refuse handoff if onboarding milestones incomplete; onboarding continues until passed.

### 5. CSM -> Renewal / Expansion

- **SLA**: renewal motion starts 120 days before term end (enterprise) or 90 days (mid-market), 60 days (SMB). Expansion pipeline tracked in CRM with close date.
- **Required fields**: NRR forecast, risk flags, expansion opportunities, multi-year conversion candidates.
- **Ownership**: CSM owns adoption and renewal conversation; AM (if split) or AE-named-account owns commercial renegotiation above a threshold.

## CRM field minimums by stage

```text
Lead:        Name, Company, Email, Source, UTM, Consent
MQL:         + Score, Persona, Firmographics
SQO:         + Discovery notes, Pain, ACV estimate, Close date, Next step
Opportunity: + Stage-exit artefacts (see pipeline-stages.md)
Closed Won:  + Order form link, Billing contact, Commitments, Use cases
Onboarding:  + Kickoff date, 30/60/90 plan, Go-live target
Live:        + Health score, Adoption %, QBR cadence, Renewal date, Risk level
```

## Deal-desk handoff (for complex commercials)

For any deal with non-standard discount (>20%), multi-year, multi-entity, custom legal terms, or unusual payment terms, deal desk is a required handoff at Stage 4. Deal desk provides:

- Pricing approval (or escalation path).
- Standard language for legal.
- Revenue-recognition guidance.
- Margin impact summary for finance.

Deals cannot move to Stage 5 (Negotiation) without deal-desk sign-off on the quote.

## Measurement

- **Handoff SLA compliance**: % of handoffs meeting SLA, per handoff, weekly.
- **Handoff rejection rate**: % of handoffs rejected, per handoff, with reason codes.
- **Leakage**: deals dropped between handoffs with no next step — root cause review monthly.
- **Cycle time per handoff**: identify the slowest handoff and fix it first.

## Cross-references

- `saas-business-metrics` — NRR, GRR, logo retention feed off the CSM handoff.
- `subscription-billing` — order form, billing contact, and revenue rec live here.
- `saas-erp-system-design` — if you run CRM + billing + provisioning as separate systems, this document is also your integration spec.

## Anti-patterns

- Handoffs over Slack/email with no CRM record — audit trail disappears.
- No rejection path — bad leads fester in AE pipelines.
- Onboarding learning about a custom promise six weeks after close.
- Renewal that starts 30 days before term end — too late to fix adoption problems.
