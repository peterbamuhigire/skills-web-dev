---
name: algorithm-selection-and-complexity
description: Use when choosing, reviewing, or explaining an algorithm under explicit correctness, time, space, input-scale, or maintainability constraints; use system-architecture-design for service boundaries and language skills for implementation syntax.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Algorithm Selection and Complexity

Choose algorithms by the problem contract and operating constraints, then prove
the choice with edge cases and measurements. This skill covers a small,
production-relevant catalogue; it does not replace domain, language, or
architecture review.

<!-- dual-compat-start -->
## Use When

- A feature has a non-trivial search, matching, assignment, optimisation, graph, cache, or pathfinding problem.
- Two correct implementations have different worst-case time, memory, or operational behaviour.
- A developer needs a plain-language explanation before writing or reviewing code.
- An early implementation works on examples but its behaviour at scale or at failure boundaries is unknown.

## Do Not Use When

- A standard library operation already satisfies the measured contract; use the language skill and document the chosen primitive.
- The main decision is service decomposition, data ownership, or deployment; use the applicable architecture or operations skill.
- The request is an interview-only puzzle with no implementation, correctness, or maintenance decision.

## Inputs

| Input | Required | Purpose |
|---|---:|---|
| Problem statement and expected output | yes | Establish correctness and generality |
| Input shape, scale, and distribution | yes | Bound time and memory behaviour |
| Failure, freshness, and determinism constraints | conditional | Expose operational risks |
| Baseline implementation or brute-force comparator | conditional | Measure whether optimisation earns its complexity |

## Outputs

- Algorithm decision record naming the selected algorithm, rejected alternatives, assumptions, and complexity bounds.
- Edge-case and correctness test matrix.
- Benchmark evidence on representative and adversarial inputs, or an explicit `NOT ASSESSED` record.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Correctness | Decision record | Markdown record: selected algorithm and rejected alternatives are traceable to constraints | `docs/algorithms/pathfinding-decision.md` |
| Correctness | Correctness matrix | Markdown matrix: edge and failure cases are covered or marked open | `docs/algorithms/pathfinding-correctness.md` |
| Performance | Benchmark record | Markdown record: inputs, environment, result, and threshold are retained | `docs/algorithms/pathfinding-benchmark.md` |

## Non-negotiables

- Start with a clear, correct baseline before optimising.
- Analyse worst-case time and space, not only a favourable example.
- State what the algorithm assumes about ordering, alphabet, graph weights, cache workload, or input validity.
- Prefer a simpler correct algorithm when the measured constraint does not require the extra machinery.
- Do not treat a book example or asymptotic bound as production evidence.
<!-- dual-compat-end -->

## Decision Rules

| Problem shape or constraint | Candidate route | Required caution |
|---|---|---|
| Stable matching between two preference lists | Gale-Shapley | Define proposer-side outcome and incomplete or tied preferences before implementation |
| Minimum-cost assignment between equal or rectangular sets | Hungarian algorithm | Confirm the cost matrix, forbidden assignments, and padding policy |
| Many pattern searches or rolling-hash-friendly text | Rabin-Karp | Verify hash hits with exact comparison; collisions are not matches |
| Pattern search over a stream that cannot be rewound | Knuth-Morris-Pratt | Test fallback-table construction and repeated-prefix cases |
| Long static text with a diverse alphabet | Horspool | Do not use its skip assumptions blindly on tiny alphabets or short patterns |
| Bounded value/capacity optimisation | Knapsack dynamic programming | State whether the problem is 0/1 or unbounded and bound the table size |
| Heuristic exploration of combinatorial paths | Ant colony optimisation | Define convergence, reproducibility, and a usable fallback; it is not an exact guarantee |
| All-pairs shortest paths on a manageable graph | Floyd-Warshall | Reject negative cycles and bound the cubic work before choosing it |
| Maximum flow through a capacity network | Push-relabel | Validate capacities, residual edges, and conservation invariants |
| Maximal cliques in a graph | Bron-Kerbosch | Expect output-sensitive growth; constrain graph size and result volume |
| Lowest-cost path with a useful heuristic | A* | The heuristic must be admissible for optimality; handle no-path and stale-node cases |
| Cache with recency and frequency shifts | Adaptive replacement cache | Measure workload, memory overhead, and eviction stability against a simpler policy |

## Workflow

1. Write the problem as input, output, invariants, and failure behaviour.
2. Implement or retain a transparent baseline and test it on empty, minimum,
   maximum, duplicate, malformed, and adversarial inputs.
3. Compare candidate algorithms by correctness risk, worst-case cost, memory,
   data-shape assumptions, observability, and maintenance burden.
4. Choose the smallest candidate that satisfies the stated contract. Record the
   reason, rejected alternative, and any heuristic or probabilistic caveat.
5. Add proof-oriented tests for invariants and differential tests against the
   baseline on generated inputs where practical.
6. Benchmark representative and worst-case distributions. Keep input fixtures,
   environment, result, and regression threshold with the decision record.
7. Revisit the choice when data shape, throughput, memory budget, or failure
   consequences change; do not optimise from an old measurement.

## Anti-patterns

- Choosing an algorithm because its name is fashionable. Fix: start with the problem contract and measured constraint.
- Reporting average-case speed without naming the input distribution. Fix: include worst-case analysis and a distribution-specific benchmark.
- Replacing a correct baseline before writing differential tests. Fix: keep the baseline as an oracle for bounded fixtures.
- Using a probabilistic hash match as proof of equality. Fix: perform exact verification after a candidate hash hit.
- Applying A* with an overestimating heuristic while claiming optimality. Fix: prove admissibility or label the result heuristic.
- Introducing a cache policy without measuring hit rate, memory, and eviction churn. Fix: compare it with a documented baseline.

## Read next

- `python-modern-standards` or the relevant language skill for implementation and tests.
- `system-architecture-design` when the algorithm changes a service or data boundary.
- `database-design-engineering` when indexes or query plans are the real solution.
- `advanced-testing-strategy` for risk-scaled evidence and regression thresholds.

## References

- [Algorithm selection matrix](references/algorithm-selection-matrix.md)

## Capability Contract

Read and search are required. Execution is preferred for benchmarks and tests.
Editing is allowed only within the authorised implementation scope.

## Degraded Mode

Without representative inputs or execution, return the decision, assumptions,
complexity analysis, and an explicit `NOT ASSESSED` benchmark requirement.
