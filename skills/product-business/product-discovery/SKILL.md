---
name: product-discovery
description: Use when testing whether a product, feature, or workflow deserves investment through risk framing, prototypes, research, and build-pivot-kill decisions.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Product Discovery
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.


## Required Inputs

| Input | Required | Use |
|---|---|---|
| Decision, audience, and deliverable | yes | Bound the business outcome |
| Source evidence, constraints, and owner | yes | Ground recommendations and accountability |
| Approved budget, customer data, or production artefacts | conditional | Support high-impact execution |

## Capability and permission contract

Default to read-only analysis and drafting. Do not publish, send, price, promise, alter customer records, commit budget, or modify production artefacts without explicit authority and a named approver. Minimise confidential data, preserve provenance, and keep reversible copies.

## Degraded mode

If evidence, stakeholder decisions, specialist tooling, or authoritative commercial data are unavailable, deliver a labelled draft, checklist, or decision memo. State what was not verified and do not claim approval, publication, financial accuracy, or customer acceptance.

## Decision rules

| Condition | Action | Stop condition |
|---|---|---|
| Output creates a commercial, customer, or delivery commitment | Obtain named approval before release | Authority or terms are unclear |
| Evidence supports a reversible draft | Produce it with assumptions and owner | Required evidence conflicts |
| Tooling or data is incomplete | Specify validation | A final executable artefact is expected |

## Domain Anti-Patterns

- Inventing customer evidence, prices, benchmarks, or approvals. Fix: cite the source or mark the gap.
- Publishing or sending a draft without authority. Fix: retain draft status and name the approver.
- Hiding assumptions inside polished prose. Fix: expose them beside each affected decision.
- Polishing presentation while the decision remains unclear. Fix: resolve audience, owner, and acceptance criteria.
- Treating unavailable tooling as passed validation. Fix: record the unassessed check.


<!-- dual-compat-start -->
## Use When

- Evaluating a new product idea or market opportunity.
- De-risking a major feature before it enters the backlog.
- Deciding whether to pivot or persevere on an existing product direction.
- Running a time-boxed discovery sprint with a cross-functional team.

## Do Not Use When

- The work is already defined at feature level and only needs implementation sequencing.
- The request is a narrow screen-level UX refinement with no product-risk question.

## Required Inputs

- Business objective, target market, and the product or feature idea under review.
- Available research, usage data, constraints, and stakeholder context.

## Workflow

- Use the four risks to decide what needs evidence, then choose the cheapest prototype or test that can answer the risk.
- End with a concrete recommendation and the evidence supporting it.
- For premium products, test willingness to pay, proof threshold, perceived quality, decision process, and buyer commitment before treating positive feedback as demand.

## Quality Standards

- Discovery must produce decisions, not theater.
- Success metrics must be defined before deeper investment.
- Prototype fidelity should stay as low as possible while still answering the risk question.

## Anti-Patterns

- Treating output volume as discovery progress.
- Asking customers about hypothetical future preferences instead of present behavior.
- Using colleagues or stakeholders as stand-ins for target users without recording the limitation.

## Outputs

- Opportunity assessment, discovery brief, test plan, prototype recommendation, evidence summary, and build / pivot / kill recommendation.

## References

- Use `enterprise-ux-process` when the work has enterprise constraints, stakeholder churn, or requirement ambiguity.
## Evidence ladder and scale gate

Before recruiting or building, run a lightweight market preflight: define the
problem and target segment, inspect demand and alternatives, and distinguish
search/interest signals from observed behaviour. Then escalate evidence only as
the decision requires: interviews/observation, a concept or landing test, a
click-through or workflow prototype, concierge/manual delivery, and finally
real use, payment, renewal, or another material commitment. Predeclare the
threshold, guardrail, time window, denominator, and persevere/pivot/kill rule.

For SaaS or product-scale decisions, do not treat acquisition or a polished
prototype as product-market fit. Require a named activation event, repeat
behaviour/retention evidence, a viable delivery and support path, and capacity
to maintain the product/design system before recommending scale. If an
AI-assisted workflow is used, preserve source context, record decisions, verify
research against the original product/source, and review scoped prototype
deltas before adoption.

Practitioner cross-checks: [Eleken product-idea validation](https://www.eleken.co/blog-posts/how-to-validate-product-ideas), [SaaS launch](https://www.eleken.co/blog-posts/how-to-launch-a-saas-business), [startup scaling](https://www.eleken.co/blog-posts/scaling-your-startup-how-it-looks-from-the-product-design-perspective), and [AI design workflow](https://www.eleken.co/blog-posts/ai-design-workflow). Use as prompts, not as proof of market size, outcomes, or tool performance.

<!-- dual-compat-end -->

Based on Cagan (2017) *INSPIRED: How to Create Tech Products Customers Love*, 2nd ed.

## The 4 Product Risks

Every product must clear four risks before full delivery investment:

| Risk | Question | Validated By |
|------|----------|-------------|
| Value | Will customers choose to use or buy this? | Demand tests, interviews |
| Usability | Can customers figure out how to use it? | Prototype testing |
| Feasibility | Can we build it with our team, tech, and time? | Engineering spike |
| Business Viability | Does it work for the business? | Stakeholder review |

For premium offers, add a fifth commercial proof question: will the right buyer pay a premium now, and what proof, risk reduction, service layer, or authority asset is required for that decision?

## Opportunity Assessment

Before committing to deeper discovery, capture:

1. Business objective
2. Key results
3. Customer problem
4. Target market

If these are unclear, the opportunity is not ready.

## Customer Discovery Rules

- Ask about current behavior, not speculative future wishes.
- Keep the target market narrow.
- Recruit real reference customers early when possible.
- Use prototypes and manual concierge work before large build commitments.

## Prototype Selection

Choose the cheapest prototype that answers the risk:

| Prototype Type | Best For |
|---|---|
| Feasibility prototype | Technical uncertainty |
| User prototype | Usability and task flow |
| Live-data prototype | Value and workflow realism |
| Hybrid prototype | Mixed risk across value, usability, and feasibility |

## Discovery Sprint

Run a 1-2 week cycle:

1. Frame the opportunity.
2. Interview target users.
3. Prototype 2-3 directions.
4. Test with real users.
5. Make a build / pivot / kill recommendation.

## Companion Skills

- `enterprise-ux-process` for feature-definition inside enterprise delivery environments.
- `feature-planning` once the opportunity passes discovery.
---

## ARRIVE: separating Research from Reframe

Many discovery processes collapse "research" and "synthesis" into one phase, which is exactly the failure mode that produces decks nobody acts on. The ARRIVE framework treats them as distinct stages — Research is ethnographic gathering, Reframe is the deliberate scope-and-meaning shift that names what to build against.

Load `references/arrive-framework.md` for:

- The two-R front end (Research, then Reframe — never collapsed).
- The Persona Needs Matrix and the Reframed Project Vision template that locks in scope.
- The Concept Board (A) for low-fidelity concepts that test the *idea*, not the polish.
- The Assumption Map (importance × evidence) that prioritises which assumptions to validate first.
- Strategic Suitability as a fourth dimension alongside Desirability/Viability/Feasibility.

Use ARRIVE's Reframe stage as a hard checkpoint: the client signs off on the new frame before any concept work begins. Without that gate, ideation becomes unanchored.
