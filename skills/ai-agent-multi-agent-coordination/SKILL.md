---
name: ai-agent-multi-agent-coordination
description: Use when designing systems where multiple agents collaborate on one task — supervisor/worker, debate, plan-execute, peer handoff. Covers handoff message contracts, shared scratchpad, conflict resolution, deadlock detection, and the cost/SLA discipline that keeps multi-agent setups from spiralling.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Multi-Agent Coordination
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- A single agent cannot reliably do the job (too many tools, too many domains, ambiguous routing).
- Standing up a **supervisor + workers** pattern (one planner, several specialists).
- Implementing a **debate** pattern where two agents propose answers and a judge picks (or a critic refines).
- Designing **plan-execute** (one plan-only agent, one execute-only agent) for separation of concerns.
- Implementing **agent-to-agent handoff** (sales agent hands to billing agent mid-task).

## Do Not Use When

- A single agent can do the task — use it. Multi-agent **multiplies cost and latency** and **divides reliability**. Default to single-agent.
- The task is just multi-tool — that's not multi-agent; one agent with N tools is still one agent.
- The task is a deterministic workflow with LLM steps — `ai-agent-runtime-architecture` §1 decision.

## Required Inputs

- Single-agent design first. Only escalate to multi-agent when single-agent demonstrably fails on eval.
- Agent runtime (`ai-agent-runtime-architecture`).
- Tool registry (`ai-agent-tool-catalogue-and-action-gating`).
- Cost / step budgets (`ai-agent-cost-and-step-budgets`) — multi-agent budgets are an order of magnitude larger.

## Workflow

1. Read this `SKILL.md`.
2. Justify multi-agent (§1). Reject it as default.
3. Choose a **coordination pattern** (§2): supervisor/worker, debate, plan-execute, peer-handoff.
4. Design the **handoff message contract** (§3). See `references/handoff-protocols.md`.
5. Implement the **shared scratchpad** with versioning (§4).
6. Implement **conflict resolution** for divergent proposals (§5). See `references/conflict-resolution.md`.
7. Implement **deadlock detection** (§6).
8. Apply **cost discipline** (§7) — multi-agent budgets are per-aggregate, with kill-switches.
9. Apply anti-patterns (§8).

## Quality Standards

- Multi-agent justified by a written rationale + eval data comparing to single-agent.
- A **named supervisor** (or named protocol) coordinates. No leaderless free-for-all.
- Handoffs are **structured messages** with schemas, not natural-language guesses.
- Shared state is versioned; concurrent writers use optimistic concurrency.
- Conflict resolution rule is deterministic, not "another LLM call". Use voting, scoring, or human escalation.
- Total step budget covers the **aggregate**, not per-agent. One agent can starve others if budgets are local.
- Deadlock detection runs every N seconds; circular waits abort with a structured failure.
- Multi-agent runs are **traced as one task** with sub-spans per agent. Replay must reconstruct the whole.
- Cost-per-task is measured and reported; if > 3× single-agent baseline, the multi-agent design is reviewed.

## Anti-Patterns

- "Crew of agents" with no supervisor and no protocol — emergent loops, infinite back-and-forth.
- Handoff via free-text "@billing_agent please help" parsed by regex. Fragile, non-replayable.
- Shared scratchpad as a global mutable dict in memory — lost on worker crash, no audit.
- "Critic" agent that just re-runs the planner with "be better". No measurable improvement, doubled cost.
- Per-agent budgets without an aggregate cap. One agent burns its budget; supervisor spawns another; infinite spawn.
- Multi-agent for a task the eval shows a single agent handles with > 90% success. You bought 3× cost for no quality gain.
- Two agents writing to the same resource without idempotency / conflict detection. Race conditions become bugs that look like hallucinations.

## Outputs

- Multi-agent justification document (single-agent baseline + eval comparison).
- Coordination pattern decision.
- Handoff message schema per agent pair.
- Shared scratchpad schema + concurrency model.
- Conflict resolution rule.
- Deadlock detector spec.
- Aggregate cost / step budget policy.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Multi-agent topology spec | Markdown + diagram | `docs/ai/multi-agent-topology.md` |
| Correctness | Handoff protocol tests | CI report | `tests/ai/handoff/` |
| Release evidence | Multi-agent vs single-agent eval | Markdown | `docs/ai/eval/multi-vs-single.md` |
| Operability | Deadlock incident runbook | Markdown | `docs/runbooks/multi-agent-deadlock.md` |

## References

- `references/supervisor-worker.md` — supervisor/worker contract.
- `references/handoff-protocols.md` — agent-to-agent handoff message schemas.
- `references/conflict-resolution.md` — conflict and deadlock resolution.
- Companion: `ai-agents-tools`, `ai-agent-runtime-architecture`, `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-cost-and-step-budgets`, `ai-agent-observability-and-replay`, `ai-agent-eval`, `distributed-systems-patterns`.

<!-- dual-compat-end -->

## §1 Justify Multi-Agent

Multi-agent is **5-50× the cost** of single-agent, **2-10× the latency**, and **substantially harder to evaluate and debug**. Justify before adopting.

Acceptable justifications:
- Domain partition is sharp — sales agent and billing agent need different prompts, tools, models, and personas.
- One agent cannot fit all required tools (> 15 tools degrades selection).
- Adversarial review (debate) measurably improves quality on the eval suite vs single-agent + critic-prompt.
- Different agents need different model tiers (planner = flagship, worker = distilled, judge = mid).

Unacceptable:
- "Crews are cool right now."
- "We want it to feel like a team."
- "Maybe we'll need it later."

The justification doc lives in `docs/ai/multi-agent-justification-<feature>.md` and includes the eval data.

## §2 Coordination Patterns

| Pattern | Topology | When |
|---|---|---|
| **Supervisor / Worker** | One planner; N specialist workers; supervisor synthesises | Multiple domains, clear partition |
| **Plan-Execute** | One planner agent emits a structured plan; one executor agent runs it | Separation of concerns; planner can be a stronger model |
| **Debate** | Two agents propose; a judge picks (or a synthesiser merges) | Quality-critical tasks; eval shows debate improves baseline |
| **Peer Handoff** | Agents pass control via structured messages; no central supervisor | Conversation-style flows (sales → billing → support) |

See `references/supervisor-worker.md` for the dominant pattern.

## §3 Handoff Message Contract

Handoffs are not free-text:

```json
{
  "handoff_id": "h_2026_0511_001",
  "from_agent": "sales_agent",
  "to_agent": "billing_agent",
  "task_id": 12345,
  "tenant_id": 42,
  "reason": "Customer requested an invoice for last month's hours.",
  "context_summary": "ACME, May 2026, 32 hours at $400/h, billing contact ben@acme.example.",
  "structured_state": {
    "customer_id": 88,
    "billing_period": {"start": "2026-05-01", "end": "2026-05-31"},
    "computed_hours": 32,
    "rate_usd_per_hour": 400
  },
  "expected_outcome": "Invoice created and sent.",
  "deadline_iso": "2026-05-12T10:00:00Z",
  "trust_level": "structured_only"
}
```

The receiving agent reads `structured_state` as ground truth and `context_summary` as advisory. The receiving agent does **not** trust the free-text fields to make irreversible decisions; it re-validates via its own tools.

Full protocol in `references/handoff-protocols.md`.

## §4 Shared Scratchpad

A versioned key-value store per task:

```sql
CREATE TABLE agent_scratchpad (
  task_id      BIGINT NOT NULL,
  key          VARCHAR(128) NOT NULL,
  value        JSON NOT NULL,
  version      INT NOT NULL DEFAULT 1,
  written_by   VARCHAR(64) NOT NULL,
  written_at   DATETIME NOT NULL,
  PRIMARY KEY (task_id, key)
);
```

Writes are optimistic-concurrency: `UPDATE ... WHERE version = :expected_version`. Mismatch → caller refetches and merges.

Agents read snapshots; writes go through a runtime helper that records the writing agent's identity.

## §5 Conflict Resolution

Two agents propose different answers. The deterministic resolver:

```python
def resolve(proposals):
    # Group by canonical answer
    groups = group_by(proposals, key=canonicalise)
    if len(groups) == 1:
        return groups[0].representative
    # Voting if odd number of judges
    if len(proposals) >= 3 and len(proposals) % 2 == 1:
        majority = max(groups, key=lambda g: len(g.members))
        if len(majority.members) > len(proposals) / 2:
            return majority.representative
    # Tie-breaker: confidence score
    return max(proposals, key=lambda p: p.confidence)
```

For high-stakes tasks (irreversible actions, money), conflict → human escalation, not another LLM call.

## §6 Deadlock Detection

Build a wait-for graph from handoff history:

```python
def detect_deadlock(task_id):
    handoffs = db.query("SELECT from_agent, to_agent FROM handoffs WHERE task_id = ?", task_id)
    g = build_directed_graph(handoffs)
    cycles = find_cycles(g)
    if cycles:
        abort_task(task_id, reason=f"deadlock_cycle: {cycles[0]}")
        page_oncall(...)
```

A scheduled job runs every 30 seconds. Default deadlock detection threshold: any cycle that has had ≥ 3 traversals in the last 5 minutes.

## §7 Cost Discipline

Aggregate budget: `task.cost_budget_usd` and `task.step_budget` cap the **sum across all agents in the task**, not per-agent. A child agent's costs decrement the parent's budget.

When budget hits 80%, the supervisor's next call is annotated `BUDGET_PRESSURE_80` so the supervisor can summarise and exit early.

When budget hits 100%, the task transitions `BUDGET_EXCEEDED` regardless of which agent is mid-step.

## §8 Anti-Patterns

- Multi-agent as default. It's an escalation, not a starting point.
- Free-text handoff. Loses replayability.
- Per-agent budgets without an aggregate cap. Spawn loops.
- Critic agent that doesn't measurably improve outcomes.
- No deadlock detection. Tasks hang for hours.
- Shared scratchpad in process memory. Lost on crash.
- Agents writing to the same external resource without coordination. Race conditions become "hallucinations".
- "Agents will figure it out." They will not.
