---
name: product-discovery
description: Structured product discovery before building. Covers the four product risks, opportunity assessment, customer discovery, prototype selection, discovery sprints, and evidence-based build / pivot / kill decisions. Use when evaluating whether a product, feature, or workflow deserves delivery investment.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Product Discovery

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

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Use the four risks to decide what needs evidence, then choose the cheapest prototype or test that can answer the risk.
- End with a concrete recommendation and the evidence supporting it.

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
