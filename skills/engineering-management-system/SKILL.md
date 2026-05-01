---
name: engineering-management-system
description: Use when designing or improving engineering management, team operating
  rhythm, prioritization, delegation, delivery health, or culture for software teams
  building production systems. Covers leverage, communication, coaching, execution
  discipline, and scaling knowledge.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Engineering Management System
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing or improving engineering management, team operating rhythm, prioritization, delegation, delivery health, or culture for software teams building production systems. Covers leverage, communication, coaching, execution discipline, and scaling knowledge.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `engineering-management-system` or would be better handled by a more specific companion skill.
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
Use this skill when the problem includes how a team develops, ships, and maintains software over time. The goal is to help software organizations produce high-quality systems repeatedly, not only through individual heroics.

## Load Order

1. Load `world-class-engineering`.
2. Load this skill when the request touches planning, team health, execution speed, delegation, or management behavior.
3. Pair it with `git-collaboration-workflow`, `advanced-testing-strategy`, and `deployment-release-engineering` for delivery-system work.

## Management Workflow

### 1. Clarify the Mission

Define:

- the business outcome the team exists to improve
- the top user and product priorities
- the current delivery bottlenecks
- the quality bar that cannot be traded away
- who owns decisions, execution, and operations
- the service or product metrics that show whether the team is actually improving the system

### 2. Prioritize for Leverage

Choose work based on:

- user or revenue impact
- risk reduction
- learning value
- speed multiplier for the team
- cost of delay

Avoid prioritizing only by urgency, loud stakeholders, or novelty.

### 3. Build an Operating Rhythm

Create a repeatable cadence for:

- planning and scoping
- design review
- code review and integration
- release readiness
- incident follow-up
- one-to-ones and coaching
- delivery-system review: pipeline health, flaky tests, deployment pain, alert fatigue, toil

Good rhythm reduces chaos without slowing learning.

### 4. Delegate Ownership

- Delegate outcomes, context, and decision boundaries, not only tasks.
- Match stretch to capability so engineers grow without being abandoned.
- Use coaching questions before directive answers when growth matters.
- Make escalation safe and expected for high-risk ambiguity.

### 5. Scale Knowledge and Quality

- Keep work visible early.
- Use review, docs, standards, and demos to spread knowledge.
- Remove single points of failure in people and systems.
- Protect maintainability and readability because they compound into velocity.
- Make incidents, rollback pain, and chronic manual work visible as management problems, not background noise.

### 6. Manage The Delivery System

- Track throughput and stability together: deployment frequency, lead time, change failure rate, recovery time.
- Stop and repair broken pipelines, high-flake suites, and unsafe release mechanics quickly.
- Use post-incident and post-release reviews to remove structural causes, not only assign local fixes.
- Treat architecture, testing, observability, and release process as parts of one management system.

## Management Standards

### Communication

- Share information by default unless there is a real reason not to.
- Be explicit about tradeoffs, priorities, and changed decisions.
- Do not let unresolved conflict hide behind politeness.

### Delivery Health

- Measure both throughput and stability.
- Improve the constraint with the highest leverage first.
- Prefer smaller validated slices over large speculative projects.
- Treat recurring coordination friction as a system design problem.
- Protect slack for tooling, documentation, automation, and training when they raise future throughput.

### Team Growth

- Create meaningful work, not constant reactive churn.
- Use one-to-ones for context, coaching, and unblockers, not status theater.
- Develop future leaders by giving them ownership and visibility.
- Do not force strong ICs into management paths they do not want.

## Deliverables

For management-system work, produce:

- team mission and priorities
- operating-rhythm outline
- delegation and ownership model
- delivery bottleneck analysis
- health metrics and review cadence
- knowledge-sharing improvements
- delivery-system scorecard and remediation priorities

## Review Checklist

- [ ] The team mission and quality bar are explicit.
- [ ] Prioritization reflects leverage rather than noise.
- [ ] Operating rhythm supports design, delivery, release, and learning.
- [ ] Ownership and delegation boundaries are clear.
- [ ] Knowledge sharing reduces heroics and hidden work.
- [ ] Delivery metrics balance speed with stability.
- [ ] Broken flow mechanisms such as flaky tests, risky releases, or weak telemetry have owners and follow-up plans.

## References

- [references/operating-rhythm.md](references/operating-rhythm.md): Cadence and meeting design for engineering teams.
- [references/coaching-and-delegation.md](references/coaching-and-delegation.md): Practical rules for growing engineers while keeping execution safe.
- [references/delivery-management-scorecard.md](references/delivery-management-scorecard.md): Delivery-system metrics, review prompts, and corrective actions.