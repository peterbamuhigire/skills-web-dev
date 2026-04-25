# Sales Ops Fundamentals

Sales ops is the operating system of the revenue team. Without it, forecast is guessing, pipeline is fiction, and commission disputes eat the leadership team's calendar.

## CRM hygiene — non-negotiable rules

1. **Single source of truth**: CRM is the system of record. Deals live there, not in spreadsheets, decks, or Slack.
2. **Every opportunity has**: owner, stage, close date, ACV, source, next step, next-step date.
3. **Close date never drifts silently**: each slip requires a reason logged in the opportunity.
4. **Activity logging**: email sync + meeting sync auto-capture; manual notes for material commitments.
5. **Mandatory fields by stage**: enforce at the platform level (see `pipeline-stages.md`).
6. **No duplicate accounts or contacts**: dedupe runs weekly; ops owns the merges.
7. **Data-quality dashboard**: public, per-rep, updated daily.

## Weekly cadence

### Monday — pipeline scrub (30-45 minutes per AE with manager)

For each active opportunity:

- Stage correct? Evidence for current stage?
- Close date realistic? Slipped >2x?
- Next step scheduled with buyer?
- MEDDIC/SPICED fields complete?

Outcomes: moved, demoted, marked Closed Lost, or flagged for deal-desk review.

### Tuesday — forecast call (team)

- Each AE calls commit / best-case / pipeline (see `forecasting-accuracy.md`).
- Manager challenges, aggregates, commits to leadership.
- Week-on-week delta reviewed for systemic drift.

### Wednesday — cross-function sync

- Marketing: lead quality, MQL volume, campaign performance.
- CS: at-risk renewals feeding back into sales intel.
- Product: competitive wins/losses, feature gaps hurting deals.

### Friday — week-in-review

- Bookings YTD vs plan.
- New logos vs target.
- Pipeline coverage (target 3x quota for next quarter, 4x for SMB).
- SQO created vs target.

## Monthly cadence

- **Forecast-to-actual review**: commit accuracy, bias direction (sandbag vs happy ears), root cause.
- **Pipeline council**: any deal >threshold ($100k mid-market, $250k enterprise) reviewed.
- **Win/loss analysis**: structured interviews on 3-5 recent closed deals (mix of wins and losses).
- **Plan-to-attainment**: per-rep attainment, coverage, activity; early-warning flags.

## Quarterly cadence

### QBR (Quarterly Business Review)

Standard agenda:

1. **Numbers**: bookings, new ARR, NRR, pipeline generated, attainment distribution.
2. **Wins and losses**: top 3 wins (why?), top 3 losses (why?), competitive trends.
3. **Pipeline health**: coverage, quality, stage-conversion rates vs benchmark.
4. **Team**: hiring, ramping, ranking, retention risks.
5. **Product feedback**: top 3 feature gaps, top 3 competitive pressures.
6. **Plan for next quarter**: priorities, SPIFs, experiments, risks.

Attendees: VP Sales, Sales Managers, VP Marketing, VP CS, CFO, Product leader.

## Deal desk function

Deal desk owns non-standard commercials:

- **Scope**: any deal with discount >20%, multi-year, multi-entity, custom terms, non-standard payment.
- **SLA**: quote + terms turnaround within 48 hours.
- **Outputs**: approved quote, legal red-line starting position, finance margin note, order form template.
- **Escalation**: discount >35% or unit economics breached -> CRO/CFO sign-off.

Deal desk is the gatekeeper that stops the "end-of-quarter discount doom loop" where desperate reps give away margin that future reps cannot recover.

## Tools stack (representative)

| Function | Tool category | Examples |
|---|---|---|
| CRM | Core system of record | Salesforce, HubSpot, Pipedrive |
| Engagement | Outbound cadence | Outreach, Salesloft, Apollo |
| Enrichment | Firmographics, contact data | ZoomInfo, Clearbit, Lusha |
| Conversation intel | Call recording + analysis | Gong, Chorus, Fireflies |
| CPQ | Configure-price-quote | Salesforce CPQ, DealHub, Tacton |
| Commission | Automated comp | CaptivateIQ, Spiff, QuotaPath |
| Forecasting | Pipeline analytics | Clari, BoostUp, InsightSquared |
| BI | Dashboards | Looker, Tableau, Metabase |

## Sales ops KPIs

- CRM data-quality score (% of opportunities meeting mandatory-field rules).
- Forecast accuracy (commit vs actual, rolling 4 quarters).
- Time-to-quote for non-standard deals.
- Commission dispute rate and resolution time.
- Ramp time for new AEs (see `onboarding-ramp.md`).

## Cross-references

- `saas-business-metrics` — the metrics sales ops produces and publishes.
- `subscription-billing` — order form to invoice integration.
- `observability-monitoring` — treat sales ops dashboards with the same rigour as product telemetry.

## Anti-patterns

- Sales ops as "the CRM admin" — undervalued and under-resourced; the function must own data, process, and insight.
- Dashboards nobody trusts — fix data quality first; no amount of BI polish fixes bad input.
- Forecast rituals that are performances — the manager already "knows" the number; stop asking the AE.
- Deal desk seen as the "no" function — reframe as the "yes, structured" function, or reps route around it.
- Tools bought without process — the tool inherits the dysfunction.
