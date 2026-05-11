# Agent vs Workflow vs Cron — Decision Matrix

The most expensive engineering mistake in agent products is **using an agent when a workflow would do**. Agents cost 5-50× the tokens, are 10× harder to evaluate, fail differently each time, and require human oversight. Workflows are deterministic, testable, and cheap.

This document is the decision framework.

## Definitions

| Pattern | LLM role | Control flow |
|---|---|---|
| **Cron** | None (or a single deterministic call) | Scheduled, fixed steps |
| **Workflow** | One or more LLM calls at fixed points | Fixed order, deterministic branching on LLM output |
| **Agent** | LLM decides the next step, including which tool to call | Loop until LLM emits "done" |
| **Multi-agent** | Multiple LLMs collaborate | Supervisor coordinates, or peers negotiate |

## The 5 Questions

Answer in order. The first "yes" determines the pattern.

1. **Are the steps fixed and known at design time?** → **Workflow** (or cron if scheduled). LLM may be one of the steps.
2. **Is the branching enumerable and decidable from LLM output?** (e.g., classify intent → route to one of 4 sub-workflows) → **Workflow** with a routing step.
3. **Does the tool choice depend on intermediate observation in ways you can't enumerate?** → **Agent**.
4. **Do multiple specialists need to negotiate or debate the answer?** → **Multi-agent**.
5. **Is the task long-running and external state must be polled?** → **Async agent** (`ai-agent-async-and-long-running-tasks`).

## Worked Examples

### Example 1: "Summarise this PDF"
- Fixed steps: extract text → chunk → summarise → return.
- LLM call: one (summarise step).
- **Verdict: Workflow.** Not an agent.

### Example 2: "Classify the support ticket and respond"
- Fixed: classify → look up FAQ → draft response → human approval.
- **Verdict: Workflow with one routing step.**

### Example 3: "Plan a 3-day trip itinerary"
- Steps: search hotels → search flights → check weather → re-plan if rain → suggest restaurants.
- The order depends on intermediate observations (rain forecast changes the plan).
- **Verdict: Agent.** Maybe with a "find_alternatives" loop.

### Example 4: "Investigate why MRR dropped last month"
- Steps not enumerable. Could be: pull dashboards → look at cohort → segment by region → check churn → email the CFO.
- **Verdict: Agent.** A senior analyst's job, mid-skilled.

### Example 5: "Reconcile yesterday's payments and email anomalies to finance"
- Steps fixed: pull yesterday → diff against bank → categorise anomalies → email summary.
- **Verdict: Cron + workflow.** An LLM step classifies anomalies; the rest is deterministic.

### Example 6: "Help the user draft a contract by negotiating with the counterparty's agent"
- Multi-agent debate, escalations.
- **Verdict: Multi-agent.** With strict HITL gates.

## When in Doubt, Build the Workflow First

If you cannot enumerate the steps, write the most likely sequence as a workflow. Then look at how often it deviates. If deviation rate < 10%, keep the workflow + fall back to a human for edge cases. Above 10%, the workflow doesn't capture the variability; upgrade to an agent.

This rule alone eliminates 70% of "we need an agent" requests.

## Cost Implications

| Pattern | Typical tokens / task | Typical USD / task | Evaluation difficulty |
|---|---|---|---|
| Cron | 0 | 0 | trivial |
| Workflow | 500 - 5,000 | $0.001 - $0.05 | easy (golden set per step) |
| Agent (5 steps) | 10,000 - 50,000 | $0.10 - $1.00 | hard (task-level eval) |
| Agent (20+ steps) | 100,000+ | $1 - $20+ | very hard (replay-based) |
| Multi-agent | 200,000+ | $5 - $100+ | extreme |

**Implication:** the same feature spec costs 100-1000× more as an agent. Demand a strong reason.

## Anti-Patterns

- "Let's build it as an agent so it can do anything." — Premature flexibility. Build the workflow; widen later.
- "Each step is a different team's API, so we need an agent." — No, that's a workflow with multiple service calls.
- "The PM wants it to feel intelligent." — Intelligence is in the output, not the loop. A well-tuned workflow feels just as intelligent.
- "We'll know what tools it needs once we deploy." — Deploying an under-specified agent to production is an outage waiting to happen.

## Decision Record Template

Every agent feature ships with a decision record:

```yaml
feature: support-copilot
candidate_patterns: [workflow, agent]
chosen: agent
rationale: |
  Ticket investigation requires variable tool choice — sometimes
  search KB, sometimes look up recent customer events, sometimes
  fetch billing state. Order depends on the ticket text. Workflow
  would require >40 branches.
fallback_workflow: |
  If agent fails or exceeds budget, route to standard FAQ + canned
  response workflow with human review.
max_steps: 8
max_tools: 6
estimated_cost_per_task_usd: 0.40
```

This record is checked into the repo with the agent code.
