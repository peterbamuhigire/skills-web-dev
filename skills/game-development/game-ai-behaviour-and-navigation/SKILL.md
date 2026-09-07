---
name: game-ai-behaviour-and-navigation
description: Use when designing, implementing, profiling, or reviewing non-player-agent behaviour, navigation, perception, decision systems, crowds, reservations, behaviour trees, state trees, utility logic, encounter AI, or AI validation in a game; load an engine skill for concrete APIs.
metadata:
  portable: true
  compatible_with: [claude-code, codex]
---

# Game AI Behaviour and Navigation

Build deterministic, debuggable and budgeted runtime agents whose decisions, movement, perception and interaction remain legible under worst-case gameplay conditions.

## Prerequisites

Load `world-class-engineering`, `gameplay-systems-engineering`, `level-world-and-content-production`, the selected engine skill, performance/testing skills, and the game's accessibility, difficulty and narrative contracts.

<!-- dual-compat-start -->
## Use When

- Defining agent goals, states, decisions, behaviour trees/state machines/utility systems, blackboards, perception, navigation, avoidance, crowds or Smart-Object-style reservations.
- Debugging stuck, oscillating, unfair, expensive, nondeterministic or unreadable NPC behaviour.
- Specifying AI architecture, data contracts, budgets, telemetry, authoring tools and validation scenarios.

## Do Not Use When

- The task is generative AI, model training or an online LLM feature.
- The task is animation rigging; use `blender-game-asset-production` and animation systems.
- The requested API is engine-specific but engine/version is unknown; freeze a versioned spike first.

## Required Inputs

| Input | Required | Missing-input response |
|---|---:|---|
| Agent fantasy, capabilities, fairness/readability rules and difficulty envelope | yes | Stop architecture and return gameplay decisions required. |
| World topology, traversal types, collision, interactions and animation contract | yes | Limit work to an abstract state model. |
| Pinned engine/version and feature maturity policy | yes for implementation | Mark APIs and performance `not assessed`. |
| Simultaneous-agent envelope, frame/memory/network budgets and target hardware | yes | Block scale claims and crowd architecture. |
| Determinism, save/load, replay, authority and multiplayer constraints | conditional | Flag state ownership and reproduction gaps. |

## Workflow

1. Define each agent archetype by player-observable goals, verbs, senses, knowledge limits, reaction windows, failure modes and fairness contract.
2. Separate sensing, memory/world state, decision, action execution, navigation, animation and feedback. Keep engine controllers/adapters outside reusable domain logic.
3. Choose the simplest decision model that explains the behaviour: finite state for bounded modes, behaviour tree for reactive hierarchy, utility for competing scored choices, planner for expensive compositional goals, or hybrid with explicit boundaries.
4. Give all shared state typed keys, ownership, defaults, lifetime and update/event policy. Prefer event-driven reevaluation; bound polling rates.
5. Specify navigation agents, mesh generation/update, areas/costs/filters, links, path failure, partial paths, moving targets, avoidance, off-mesh traversal and recovery.
6. Treat interactable locations as capacity-controlled resources: eligibility, reservation, timeout, cancellation, completion and orphan cleanup are explicit.
7. Integrate animation and gameplay with named events and bounded waits. Define root-motion, turning, hit reaction, interruption and fallback contracts.
8. Instrument decision transitions, perception changes, path requests/failures, stuck recovery, reservation lifecycle and per-archetype cost without shipping noisy debug output.
9. Test single-agent correctness, adversarial geometry, simultaneous worst case, save/load, network authority, difficulty variants and target hardware. Retain seeds, scenario, build and trace.
10. Stop on unbounded search/polling, missing recovery, unstable experimental dependency, unfair information access, unreachable state or budget failure.
11. Load `references/behaviour-telemetry-and-tuning.md` before tuning behaviour. Retain
    the exact build, seed, configuration, scenario, state trace, path failures, and
    guardrail result for every experiment; never promote learned or probabilistic
    behaviour without a deterministic fallback and rollback path.

## Outputs

| Artefact | Acceptance condition |
|---|---|
| AI behaviour contract and state/key registry | States, transitions, ownership, defaults and failure recovery are deterministic. |
| Navigation/interaction contract | Agents, costs, links, reservations, invalidation and fallback are explicit. |
| Engine adapter and feature-status decision | Version, plugin/feature maturity, fallback and upgrade evidence are recorded. |
| AI verification and profiling report | Named scenarios prove correctness, legibility and worst-case cost. |

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Correctness | Transition, perception, path, reservation, save/load and recovery traces. | Trace log with build, seed, scenario and state transitions | `docs/game-ai/navigation-traces.jsonl` |
| Performance | Per-agent and simultaneous worst-case CPU, memory and path-query evidence. | Profiling report with scenario, target hardware and measured costs | `docs/game-ai/navigation-profile.md` |
| UX quality | Reaction, telegraph, knowledge-boundary and difficulty playtests. | Playtest report with fairness/readability observations and findings | `docs/game-ai/fairness-playtests.md` |
| Release evidence | Engine/plugin version, feature status, known failure states and regression suite. | Release record with version identity, limitations and regression results | `docs/game-ai/release-evidence.md` |
<!-- dual-compat-end -->

## Capability and Degraded Mode

Changing navigation generation, runtime authority or experimental plugins requires implementation authority and rollback. Without the pinned engine and representative build, provide contracts and test scenarios only; mark API fit, feature stability and performance `not assessed`.

## Decision Rules

| Condition | Action |
|---|---|
| Behaviour can be expressed with a small explicit state machine | Do not introduce a planner or deep tree. |
| Agent reads information the player could not reasonably expose | Add a perception/memory path or label the intentional difficulty rule. |
| Decision checks run every frame without need | Convert to events, services at bounded intervals, or scheduled batches. |
| Path or interaction can fail | Specify timeout, retry/backoff, alternate goal and safe idle—not an infinite wait. |
| Engine feature is beta/experimental | Record status in the pinned release, isolate behind an adapter and define fallback. |

## Quality Standards

- Name behaviours by intent; keep tasks/actions small, reusable and independently testable.
- Do not mutate decision-node configuration at runtime; keep changing state in typed runtime data.
- AI difficulty changes decision quality, timing, resources or coordination explicitly—not hidden omniscience.
- Measure worst cases with actual agents, geometry, animation and target hardware.
- Record time and memory complexity, update frequency, worst-case path/search cost, and invariants for critical behaviours. Test a bounded degraded path before standardising a Kaizen change.

## Anti-Patterns

- Giant behaviour tree as a visual script. Fix: split domain decisions, reusable actions and engine adapters.
- Polling everything every frame. Fix: event-driven updates and budgeted schedules.
- Navigation success treated as guaranteed. Fix: handle invalid targets, partial paths, topology change and stuck recovery.
- Reservation without cancellation. Fix: define ownership, timeout and cleanup on death/unload/disconnect.
- Debugging by animation alone. Fix: capture state, reason, key changes, path status and timestamps.
- Tutorial agent counts treated as product budgets. Fix: measure project worst cases.

## Read Next

- The selected Unity/Unreal/Godot skill for concrete implementation.
- `level-world-and-content-production` for nav-ready spaces and encounter topology.
- `game-testing-polish` and performance skills for scenario and target-device evidence.

## References

- [AI architecture and runtime contract](references/ai-architecture-and-runtime-contract.md)
- [AI verification matrix](references/ai-verification-matrix.md)
- [Behaviour telemetry and tuning](references/behaviour-telemetry-and-tuning.md)
- [Game-development source register](../../../docs/game-dev-analysis/source-register.md)
