# Supervisor / Worker Pattern

The dominant multi-agent pattern. One supervisor agent decomposes the task, dispatches subtasks to specialist workers, collects results, synthesises the final answer.

## Topology

```
                ┌──────────────┐
                │  Supervisor  │
                └──┬──┬──┬─────┘
        dispatch │  │  │ dispatch
                 ▼  ▼  ▼
            ┌────┐┌────┐┌────┐
            │ W1 ││ W2 ││ W3 │   workers (specialists)
            └────┘└────┘└────┘
                 │  │  │
                 ▼  ▼  ▼
                ┌──────────────┐
                │  Supervisor  │   synthesise
                └──────┬───────┘
                       ▼
                    answer
```

## Contracts

### Supervisor → Worker

```typescript
type Dispatch = {
  task_id: string;             // parent task
  subtask_id: string;          // child id
  worker: string;              // "data_agent" | "analysis_agent" | ...
  goal: string;                // 1-2 sentences
  inputs: Record<string, any>; // structured args (from scratchpad)
  expected_output_schema: JSONSchema;
  step_budget: number;
  cost_budget_usd: number;
  wallclock_budget_s: number;
  deadline: string;            // ISO
};
```

### Worker → Supervisor (Result)

```typescript
type SubtaskResult = {
  subtask_id: string;
  worker: string;
  status: "ok" | "partial" | "blocked" | "failed";
  output: any;                 // matches expected_output_schema
  evidence: Array<{ kind: "tool_call" | "memory_fact" | "kb_chunk"; ref: string }>;
  confidence: number;          // 0-1
  steps_used: number;
  usd_cost: number;
  notes_for_supervisor: string; // free text, advisory only
};
```

### Worker → Supervisor (Block)

If a worker can't continue (needs approval, missing input, capability limit):

```typescript
type SubtaskBlock = {
  subtask_id: string;
  worker: string;
  status: "blocked";
  block_reason: "needs_approval" | "missing_input" | "out_of_capability" | "budget_exceeded";
  requested_inputs?: Array<string>;
  proposed_action?: any;       // if needs_approval, the concrete proposed action
};
```

## Dispatch Modes

| Mode | Behaviour |
|---|---|
| `sequential` | Supervisor dispatches one worker, awaits result, dispatches next |
| `parallel` | Supervisor dispatches N workers, awaits all |
| `parallel_first` | Supervisor dispatches N workers; first viable result wins; others canceled |

Cost-aware default: `sequential` for medium tasks; `parallel` only when subtasks are demonstrably independent.

## Implementation (Python sketch)

```python
class Supervisor:
    def __init__(self, workers: dict[str, WorkerAgent]):
        self.workers = workers
        self.scratchpad = Scratchpad(task_id)
    
    def run(self, goal: str) -> str:
        plan = self.plan(goal)  # LLM call, returns ordered subtasks
        for sub in plan:
            result = self.dispatch(sub)
            if result.status == "blocked":
                if result.block_reason == "needs_approval":
                    approval = request_approval(result.proposed_action)
                    if not approval.granted:
                        return self.summarise_partial(plan)
                    sub.proceed_with_approval = approval.id
                    result = self.dispatch(sub)
            self.scratchpad.put(sub.subtask_id, result.output)
        return self.synthesise(self.scratchpad.snapshot())
    
    def dispatch(self, sub: Dispatch) -> SubtaskResult:
        worker = self.workers[sub.worker]
        return worker.run(sub)
```

## Budget Allocation

Supervisor receives `task.cost_budget_usd`. It allocates per subtask:

```python
def allocate_budget(total_budget: float, subtasks: list[Subtask]) -> dict:
    # Reserve 20% for supervisor synthesis
    available = total_budget * 0.8
    # Weighted by estimated complexity (LLM emits a weight per subtask)
    total_weight = sum(s.weight for s in subtasks)
    return {s.subtask_id: available * s.weight / total_weight for s in subtasks}
```

If a subtask exceeds its allocation, the worker returns `blocked: budget_exceeded`; the supervisor decides to top-up (from the reserve) or abort.

## Synthesis

Supervisor reads the scratchpad and produces the final answer. The synthesis prompt explicitly cites subtask outputs:

```
You have results from these workers:
- data_agent (subtask_data): { rows: 245, summary: "..." }
- analysis_agent (subtask_analysis): { findings: ["..."] }
- advisory_agent (subtask_advisory): { recommendations: ["..."] }

Synthesise a concise answer for the user. When you cite a finding, indicate
which worker produced it.
```

## Failure Handling

| Worker outcome | Supervisor action |
|---|---|
| `ok` | Continue per plan |
| `partial` | Re-dispatch with adjusted goal, or accept partial in synthesis |
| `blocked` | Resolve block (approval / additional input) or skip subtask |
| `failed` | If critical: abort task; if optional: skip and note in synthesis |

## Observability

Each subtask is a child span of the parent task. The trace shows:

```
agent.task                                     12,400ms  $0.42
├── supervisor.plan                                 220ms  $0.04
├── worker.data_agent.subtask_data                4,800ms  $0.18
│   ├── tool.query_sales_report                    320ms
│   └── tool.kb_search                             180ms
├── worker.analysis_agent.subtask_analysis        3,200ms  $0.12
└── supervisor.synthesise                         3,800ms  $0.08
```

## Anti-Patterns

- Supervisor talks to workers in free text. Lose schema validation.
- Workers can spawn their own subworkers without supervisor permission. Cost explodes.
- Workers share state via shared globals instead of the scratchpad. Race conditions.
- Synthesis re-fetches data the workers already gathered. Duplicate cost.
- Supervisor and workers use the same model. The supervisor should be the strongest model; workers can be cheaper.
- No deadline on workers. One slow worker stalls the whole task.
