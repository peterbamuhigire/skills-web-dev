# Conflict Resolution and Deadlock Detection

When two or more agents propose different answers, take different actions on the same resource, or wait on each other, the system needs a deterministic resolver. LLMs are bad arbiters; rules are reliable.

## Sources of Conflict

| Conflict | Example | Severity |
|---|---|---|
| Different answers | Analyst A: "MRR up 12%"; Analyst B: "MRR up 8%" | medium |
| Different actions | Agent A: "approve refund"; Agent B: "deny refund" | high |
| Same resource | Two agents update the same record concurrently | high |
| Different plans | Planner emits plan; critic emits a contradictory plan | medium |
| Deadlock | Agent A waits on B; B waits on A | critical |

## Strategy 1: Voting

Use when ≥ 3 odd-numbered judges and the answer space is small/canonical.

```python
def vote(proposals: list[Proposal]) -> Decision:
    grouped = group_by_canonical(proposals, key=lambda p: canonicalise(p.answer))
    majority = max(grouped, key=lambda g: len(g.members))
    if len(majority.members) > len(proposals) / 2:
        return Decision(answer=majority.representative, confidence=len(majority.members) / len(proposals))
    return Decision.tie()
```

`canonicalise` normalises trivial differences (whitespace, ordering, paraphrase) before grouping.

## Strategy 2: Score-Based

Each proposal carries a confidence score; pick highest.

```python
def by_confidence(proposals: list[Proposal]) -> Decision:
    return max(proposals, key=lambda p: p.confidence)
```

Only safe if confidence is **calibrated**. Uncalibrated LLM confidences are nearly useless — verify with a calibration set before relying.

## Strategy 3: Evidence-Weighted

Score is the count of distinct evidence references underneath the proposal.

```python
def by_evidence(proposals: list[Proposal]) -> Decision:
    def score(p):
        return len({e.ref for e in p.evidence}) * (1 + 0.5 * p.confidence)
    return max(proposals, key=score)
```

Reasonable default for analytical tasks where workers cite tool results.

## Strategy 4: Human Escalation

For irreversible / high-stakes conflicts, **escalate**. Do not let LLMs arbitrate money or external action.

```python
def escalate(proposals, ctx):
    return Decision.escalated(
        approval_request=AgentApproval.create(
            pattern="conflict_resolution",
            plan_payload={"proposals": [p.serialize() for p in proposals]},
            ...
        )
    )
```

Default policy:

| Stake | Resolver |
|---|---|
| Read-only output | by_evidence or vote |
| Reversible action | by_evidence + auto-approve unless tie |
| Irreversible action | always escalate |

## Strategy 5: Critic-and-Synthesise (Last Resort)

Two proposals; a third agent synthesises a unified answer. This is **another LLM call**, which can also be wrong; use sparingly.

Constraints when using:
- The synthesiser is a different model from the proposers (different failure modes).
- The synthesiser's output is also scored against the eval suite before adoption.
- Cost is added to the aggregate budget.

## Resource Conflict (Same Target)

When two agents try to mutate the same record:

```python
def claim_resource(resource_id, agent_id, task_id, ttl_s=60):
    return redis.set(f"agent:claim:{resource_id}", f"{agent_id}:{task_id}", nx=True, ex=ttl_s)
```

The first to claim wins. The loser receives `RESOURCE_LOCKED` and either:
- Waits with backoff (if within deadline);
- Re-plans without that resource;
- Hands off to the winning agent ("you already have this — please do X with it too").

## Deadlock Detection

Build a wait-for graph from claims and handoffs:

```python
class WaitForGraph:
    def __init__(self):
        self.edges = defaultdict(set)  # agent_instance -> set of agents it waits on
    
    def add_wait(self, waiter, waitee):
        self.edges[waiter].add(waitee)
    
    def has_cycle(self) -> Optional[list]:
        visited = set()
        stack = set()
        path = []
        def dfs(node):
            visited.add(node)
            stack.add(node)
            path.append(node)
            for neighbor in self.edges[node]:
                if neighbor in stack:
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:]
                if neighbor not in visited:
                    r = dfs(neighbor)
                    if r: return r
            stack.discard(node)
            path.pop()
            return None
        for node in list(self.edges):
            if node not in visited:
                r = dfs(node)
                if r: return r
        return None
```

A janitor job runs every 30s. On cycle: abort all agents in the cycle, transition the task to `FAILED` with `reason=deadlock`, page on-call.

## Optimistic Concurrency on Scratchpad

```python
def update_scratchpad(task_id, key, expected_version, new_value):
    updated = db.execute(
        "UPDATE agent_scratchpad SET value=?, version=version+1 "
        "WHERE task_id=? AND key=? AND version=?",
        new_value, task_id, key, expected_version
    )
    if updated == 0:
        raise ConcurrencyConflict()
```

Caller refetches and re-applies. After N retries (default 3), the calling agent gets `SCRATCHPAD_BUSY` and replans.

## Conflict Telemetry

Track:
- Conflicts per 100 tasks (by feature, by strategy).
- Conflict resolution time (p50, p90).
- Escalation rate (% of conflicts requiring human).
- Deadlock incidents (count).
- Retry storms on the scratchpad (count).

Trend these. Rising conflict rate signals plan-quality regression in the supervisor.

## Anti-Patterns

- "We'll let the agents talk it out." → infinite loops.
- Synthesiser is the same model as the proposers (same biases, same errors).
- No deadlock detection. The team finds them by customer complaint.
- Resource lock with no expiry. Crashed worker holds the lock forever.
- Escalating low-stake conflicts to humans. Alert fatigue.
- Not escalating high-stake conflicts. Bad outcome the customer pays for.
