# Agentic AI Operating Model Source Synthesis

Self-contained synthesis prepared from the supplied agentic AI and AI transformation source files. It preserves practical operating rules without depending on the original files.

## Table Of Contents

- Autonomy ladder
- Use-case selection scorecard
- Production agent spine
- Instruction, plan, and tool contracts
- Memory, retrieval, and context discipline
- Multi-agent team design
- Evaluation, observability, and deployment stages
- Human-agent team operating model
- Governance and transformation gates

## Autonomy Ladder

Treat autonomy as something the agent earns through evidence.

| Level | Agent authority | Use when | Required control |
|---|---|---|---|
| 0 Assist | Drafts or analyses only | First deployment, unclear data, high-stakes workflow | Human performs all actions |
| 1 Recommend | Produces ranked next actions | Team can review quickly and has baseline metrics | Human approval before external action |
| 2 Supervised act | Uses low-risk tools inside a bounded workflow | Tool contracts, evals, and rollback exist | Approval for irreversible/external actions |
| 3 Conditional autonomy | Acts without review in pre-approved cases | Stable workflow, strong observability, low exception rate | Escalation thresholds and kill switch |
| 4 Managed autonomy | Owns an operational outcome | Mature operating team, audited controls, proven ROI | Periodic audit, budget caps, incident drills |

Before increasing autonomy, ask whether a capable new employee in week one would be trusted with the same authority. If not, keep the agent in review mode.

## Use-Case Selection Scorecard

Score each candidate from 1 to 5. Pilot only candidates with a clear owner and measurable baseline.

| Criterion | Good signal | Bad signal |
|---|---|---|
| Workflow pain | Repetitive, slow, costly, error-prone | Vague innovation goal |
| Outcome ownership | One named owner and one success metric | No accountable operator |
| Data readiness | Clean source, access rights, known freshness | Scattered, stale, ambiguous data |
| Tool readiness | Stable APIs and reversible side effects | Manual-only systems or risky write tools |
| Exception shape | Known exception paths and escalation rules | Hidden approvals and edge cases |
| Business value | Time, revenue, quality, risk, or SLA impact | Demo value only |
| Risk fit | Low-risk first or strong HITL controls | High-stakes decisions with no review |

Reject "agent" as the default. If the path is known, build a deterministic workflow with LLM judgment at decision points.

## Production Agent Spine

Production agents need a spine, not a chat loop:

1. Task intake with `task_id`, tenant, user, objective, data scope, and budget.
2. State machine with explicit states, retries, pauses, approvals, terminal states, and resumability.
3. Instruction stack: role, objective, operating policy, output contract, escalation rules.
4. Tool registry with schemas, scopes, side-effect class, provenance, and approval requirement.
5. Memory and retrieval policies for what can be read, written, forgotten, corrected, or cited.
6. Evaluation harness with normal, edge, adversarial, and incident-derived cases.
7. Observability with run trace, step log, tool calls, model/version, cost, latency, artifacts, and reviewer decisions.
8. Governance loop: owner, review cadence, incident response, kill switch, and autonomy promotion criteria.

## Instruction, Plan, And Tool Contracts

- Split instructions into stable policy, workflow-specific rules, examples, and output schema.
- Use plan-execute-verify loops. Planning is a control artifact, not hidden "thinking".
- Require checkpoints for long tasks, high-cost calls, external side effects, and uncertainty.
- Define tools as contracts: purpose, parameters, data classification, tenant scope, idempotency key, timeout, failure response, and audit event.
- Keep allowed-action tables beside each agent. The agent should know what it may do, what needs approval, and what is forbidden.

## Memory, Retrieval, And Context Discipline

- Treat memory as a tool with consequences, not a dumping ground.
- Write memory only when the data is durable, useful, consented/allowed, and scoped to the correct tenant/user.
- Add expiration and correction rules for memories.
- Prefer small, curated context over large context dumps.
- For retrieval, store source, date, authority, permission scope, and conflict rules. When sources conflict, stop or escalate instead of blending.

## Multi-Agent Team Design

Use multiple agents only when role separation reduces risk or improves throughput. Start with three roles:

| Role | Responsibility | Guardrail |
|---|---|---|
| Planner/router | Decides task path and delegate | Cannot execute external actions |
| Executor/specialist | Performs bounded task with approved tools | Tool scope and budget caps |
| Verifier/reviewer | Checks output against policy and evidence | Independent context where possible |

Avoid multi-agent systems where one agent could complete the task safely. Every handoff needs context, acceptance criteria, and failure routing.

## Evaluation, Observability, And Deployment Stages

Minimum release path:

1. Prototype: no irreversible side effects, manual run logs.
2. Internal draft-first pilot: human sends/executes outputs, baseline metric captured.
3. Limited beta: bounded tools, approval gates, eval suite, trace review.
4. Monitored scale: expanded cases, incident drills, cost caps, reviewer sampling.
5. Conditional autonomy: only after stable pass rate, low escalation, and clear rollback.

Evaluation sets should include at least normal cases, messy real inputs, edge cases, hostile inputs, permission-denied cases, tool failures, and recovery cases. Update evals after every production incident.

## Human-Agent Team Operating Model

AI transformation is mostly operating change, not tool selection. A serious deployment names:

- workflow owner
- reviewer or approver
- escalation owner
- data owner
- prompt/tool owner
- support owner
- governance cadence

Measure whether people actually adopt the new workflow. Time saved that creates rework, mistrust, or support burden is not real value.

## Governance And Transformation Gates

- Process redesign comes before automation.
- Human control remains mandatory for high-stakes, regulated, irreversible, external, financial, legal, safety, personnel, and reputation-sensitive actions.
- Governance and security are one operating system: data boundaries, model access, tool scopes, audit trails, redaction, incident response, and compliance evidence.
- Make carbon, compute, cost, and vendor dependency visible when AI is used at scale.
- Treat agents as managed operators with onboarding, permissions, performance reviews, and retirement criteria.
