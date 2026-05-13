---
name: ai-economic-value-engine
description: Use when discovering, designing, prioritizing, or auditing AI-powered products
  for measurable business value. Applies to AI opportunity mapping, ROI cases, product
  strategy, client workshops, and deciding whether an AI feature should be built.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Economic Value Engine
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->

## Use When

- A client or internal team wants AI features, AI transformation, agentic workflows, analytics, automation, or AI-powered apps.
- The work needs prioritization by business value, feasibility, data readiness, risk, and maintainability.
- You must turn AI capability into a proposal, PRD, roadmap, SRS, architecture, or implementation plan.

## Do Not Use When

- The request is not materially about AI value, AI product selection, AI ROI, or AI investment prioritization.
- The user already has a committed AI feature and needs a narrower implementation, evaluation, security, RAG, or agent runtime skill.

## Core Principle

AI must improve an economic system: revenue, margin, productivity, quality, speed, risk, compliance, retention, or decision accuracy. Do not recommend AI for novelty.

## Required Inputs

- Target users and business process.
- Current pain, baseline metric, cost of the pain, and decision/action affected.
- Available data, data owner, freshness, quality, sensitivity, and access constraints.
- Risk tolerance, legal/compliance constraints, and human approval requirements.
- Budget, timeline, operating owner, and success metric.

## Workflow

1. **Map the workflow**: Trigger, actors, data, decisions, actions, handoffs, delays, and failure points.
2. **Find AI leverage**: Classify opportunities as insight, prediction, generation, extraction, search, recommendation, decision support, or action automation.
3. **Estimate value**: Quantify time saved, extra revenue, reduced leakage, fewer errors, faster turnaround, lower service cost, or reduced risk exposure.
4. **Assess feasibility**: Check data readiness, integration complexity, model reliability, evaluation difficulty, security, and maintenance burden.
5. **Choose architecture**: Prefer deterministic workflow, RAG, analytics, or simple model call before agents or fine-tuning.
6. **Define evaluation**: Set quality, cost, latency, safety, business, and adoption thresholds.
7. **Plan operations**: Assign owner, monitoring, feedback loop, incident response, model/prompt update cadence, and client reporting.

## Opportunity Scorecard

Score each item 1-5.

| Dimension | Question |
|---|---|
| Business value | Does it move a financially or operationally important metric? |
| User pull | Will users adopt it inside their real workflow? |
| Data advantage | Do we have proprietary or hard-to-copy context/data? |
| Feasibility | Can current models and integrations meet the required quality? |
| Risk control | Can failures be detected, bounded, reversed, or escalated? |
| Evaluation clarity | Can we prove whether it works before and after launch? |
| Maintainability | Can the client or agency operate it for years? |

Prioritize high-value, high-feasibility, low-regret use cases first. Defer low-value or unmeasurable ideas even if they are technically impressive.

## AI Product Patterns

- **Decision cockpit**: Aggregates data, explains options, and recommends next actions.
- **Knowledge worker assistant**: Drafts, checks, summarizes, and retrieves from trusted sources.
- **Operational copilot**: Guides staff through repeatable workflows with validation and approvals.
- **Predictive engine**: Forecasts demand, churn, risk, maintenance, fraud, or cash flow.
- **Autonomous workflow**: Executes bounded actions with tool contracts, audit logs, and human approval gates.
- **AI analytics layer**: Turns operational data into segmentation, anomaly detection, root-cause analysis, and dashboards.

## Outputs

- AI opportunity map with value, feasibility, risk, and recommended sequence.
- Business case with assumptions, ROI model, cost drivers, and non-financial benefits.
- AI product brief or PRD with user stories, acceptance criteria, data needs, evaluation plan, and rollout stages.
- Architecture recommendation with model, RAG/tool/workflow choice, governance, and operating model.
- No-build recommendation when AI cannot be justified.

## Quality Standards

- Tie every recommendation to a measurable business, operational, risk, quality, or adoption outcome.
- Make assumptions, baselines, data readiness, operating owner, and failure modes explicit.
- Prefer no-build, deterministic workflow, analytics, or RAG recommendations when they create more value than agents.

## Anti-Patterns

- Recommending AI because it is technically possible rather than economically justified.
- Treating model accuracy as the only success metric.
- Ignoring adoption, ownership, data readiness, cost, risk, and post-launch operations.

## Hard Rules

- Never skip baseline measurement. If there is no baseline, propose how to collect it.
- Never promise perfect accuracy. State confidence, failure modes, human review, and fallback.
- Never build agents where deterministic automation or workflow design is safer.
- Never ignore post-launch ownership; AI products degrade without monitoring and feedback.
## References

- Use companion AI implementation, evaluation, security, RAG, analytics, or agentic skills after the opportunity is economically justified.

<!-- dual-compat-end -->
