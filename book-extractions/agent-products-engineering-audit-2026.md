# AI Agent Products Engineering Skills Audit — May 2026

**Lens:** **Agentic features** (LLMs that plan, call tools, take actions, run multi-step, run hours-to-days, coordinate with other agents) built **inside** a multi-tenant SaaS — where every agent task must be tenant-scoped, action-gated, reversible-or-approved, cost-bounded, blast-radius-capped, observable, replayable, evaluated, and operable (kill-switchable per task / per tenant / globally) by a back-office team.

**Inputs:** The new AI-on-SaaS stack (`ai-on-saas-architecture`, `ai-model-gateway`, `ai-tenant-isolation-patterns`, `ai-cost-per-tenant-attribution`, `ai-eval-harness`, `ai-hallucination-slo-and-grounding`, `ai-prompt-injection-and-tenant-safety`, `ai-observability-and-debugging`, `ai-rag-multi-tenant`, `ai-feature-rollout-and-experimentation`, `ai-entitlements-and-feature-gating`, `ai-usage-metering-and-billing`), plus existing `ai-agents-tools`, `ai-agentic-ui`, `custom-sub-agents`, `openai-agents-sdk`.

**Prior verdict:** the engine has solid RAG/copilot coverage but treats agents as a chapter inside `ai-agents-tools`. Agents are now a **product class**, not a pattern: they ship as features customers buy on the Pro/Enterprise tier, they own real money + real state, they fail differently (irreversible action, runaway loop, indirect prompt injection from tool output, cross-tool data exfil, abandonment of a 2-day task), and they are operated differently (per-task kill-switch, plan-preview UX, agent inbox, async progress, replay-based debugging). Single-skill coverage is now a liability.

---

## Existing Agent Skill Audit

| Skill | Coverage today | Gap for agent-as-product |
|---|---|---|
| `ai-agents-tools` | Strong on ReAct loop, tool contract rules, multi-agent decomposition, compound-accuracy problem, PHP execution loop, simple human-approval gate | Single-tenant lens. Missing: per-tenant tool allow-lists, reversibility classification, blast-radius caps, step/wallclock/cost budgets, action-approval UX patterns, durable long-running state, agent observability/replay, agent eval (task success vs token cost), agent-specific red-team. |
| `ai-agentic-ui` | Some UX patterns | No agent inbox, no plan preview / approve-edit-cancel, no "agent at work" indicators, no mobile approval flow. |
| `custom-sub-agents` | Claude-specific subagent feature | Not the gap target — it's about Claude Code subagents, not product agents. |
| `openai-agents-sdk` | Provider-specific SDK guide | Not the gap target. |
| `ai-on-saas-architecture` | Five control-plane AI services | Agent runtime not listed as a control-plane service. |
| `ai-prompt-injection-and-tenant-safety` | Strong on direct injection | Light on **indirect** prompt injection (tool output, retrieved chunk, web page the agent visits) — the dominant agent-era threat. |
| `ai-cost-per-tenant-attribution` | Token-cost pipeline | No agent-step / agent-task cost rollup; no "cost-per-completed-task" view. |
| `ai-entitlements-and-feature-gating` | Plan-tier gating | No agent-tier (`agent_enabled`, `max_steps`, `max_tools`, `concurrent_agents`, `allowed_tools[]`). |
| `ai-observability-and-debugging` | Trace per request | No task trace, step span, tool I/O capture, deterministic replay. |
| `ai-eval-harness` | Golden datasets, judge-LLM | No agent eval section: task success rate, step efficiency, tool-choice quality, irreversible-action rate, intervention rate. |
| `saas-rate-limiting-and-quotas` | Token / call quotas | No concurrent-agent-session quota, no agent-step/day, no per-task wallclock cap. |
| `saas-admin-backoffice-tooling` | Tenant + billing ops | No agent ops console: kill task, force-pause, view trace, override approval, retrace. |

---

## Cross-Cutting Gaps (agent-as-product)

1. **No agent runtime architecture skill.** Where does the agent loop live? Inline in a web request (synchronous), in a worker (async), in a durable execution engine (Temporal / Inngest / Restate)? When does an agent become a *workflow* instead? When does a *workflow* become a *cron*? No decision framework.
2. **No tool catalogue + action gating skill.** Tools are listed in `ai-agents-tools` but not as a **registry** with per-tenant allow-lists, reversibility classification, side-effect budgets, and version pinning per tenant.
3. **No action-approval / HITL skill.** Approvals exist as a SQL table in `ai-agents-tools`, but the **UX patterns** (plan preview, bulk approval, just-in-time approval, "explain plan", undo windows) are not encoded.
4. **No reversibility / blast-radius skill.** Make-it-reversible (dry-run, staged commit, transactional group), blast-radius caps per session (e.g., max-emails-sent-by-agent / hour / tenant), sandbox-first — none of this is engineered into the engine.
5. **No agent memory skill.** Short-term (turn buffer) vs working (episode) vs long-term (semantic per tenant) memory; forget-on-erase cascade tied to `saas-tenant-data-portability-and-erasure`; cross-conversation isolation.
6. **No multi-agent coordination skill.** `ai-agents-tools` shows an orchestrator diagram. The engine lacks: supervisor/worker contract, handoff protocols, shared scratchpad, conflict resolution, deadlock detection.
7. **No agent cost-and-step-budget skill.** Step budget × token budget × wallclock budget × tool-cost budget × per-tenant-tier overrides × refusal-on-budget — all needed for agents that can run hours.
8. **No agent eval skill.** Agents need *task-level* eval: success rate, intervention rate, irreversible-action rate, step-efficiency, tool-choice quality. Replay-based eval (re-run an episode with a new model and diff outcomes).
9. **No agent observability + replay skill.** Per-task trace, per-step span, tool I/O capture, deterministic replay, "what would the agent do differently with a new prompt".
10. **No agent safety / red-team skill.** Indirect prompt injection via tool output, action escalation (agent uses one tool's output as input to a higher-privilege tool), tenant-data exfil via tool-call chain, recursive self-modification.
11. **No async / long-running-agent skill.** Durable state, resumability after crash, progress UX, abandonment policy, notifications when done.
12. **No agent-in-the-product UX skill.** Agent inbox, plan preview, approve/edit/cancel buttons, "agent at work" status, mobile-safe approval, agent persona patterns.

---

## NEW SKILLS (12)

| # | Skill | Purpose |
|---|---|---|
| 1 | `ai-agent-runtime-architecture` | The agent loop as a control-plane service: state machine, retries, max-step caps, deterministic resumability; agent vs workflow vs cron decision matrix. |
| 2 | `ai-agent-tool-catalogue-and-action-gating` | Tool registry with typed schemas, per-tenant allow-lists, reversible-vs-irreversible classification, side-effect budgets, version pinning. |
| 3 | `ai-agent-action-approval-and-hitl` | Plan preview, single-shot vs bulk vs just-in-time approval, "explain plan", undo windows, approval-UX patterns. |
| 4 | `ai-agent-reversibility-and-blast-radius` | Dry-run, staged commits, transactional groups, blast-radius caps per tenant/role/session, sandbox-first. |
| 5 | `ai-agent-memory` | Short-term / working / long-term memory tiers; per-tenant semantic memory; forget-on-erase cascade; cross-conversation isolation. |
| 6 | `ai-agent-multi-agent-coordination` | Supervisor/worker, debate, plan-execute, handoff protocols, shared scratchpad, conflict resolution, deadlock detection. |
| 7 | `ai-agent-cost-and-step-budgets` | Step / token / wallclock / tool-cost budgets per tenant tier; refusal-on-budget; cost-per-task attribution. |
| 8 | `ai-agent-eval` | Task success rate, step efficiency, tool-choice quality, hallucinated tool args, irreversible-action rate, intervention rate; golden tasks; replay-based eval. |
| 9 | `ai-agent-observability-and-replay` | Trace per task, per-step span, tool I/O capture, deterministic replay, "what-would-agent-do-differently" debugging. |
| 10 | `ai-agent-safety-and-red-team` | Indirect prompt injection (tool output, web), action escalation, tenant-data exfil via tool chain, recursive self-modify; CI red-team suite. |
| 11 | `ai-agent-async-and-long-running-tasks` | Hours-to-days agents: durable state, resumability, progress UX, notifications, abandonment policy. |
| 12 | `ai-agent-mobile-and-web-ux-patterns` | Agent inbox, plan preview, approve/edit/cancel, agent status, mobile-safe approval, "agent at work" indicators. |

---

## ENHANCEMENTS to existing skills

| Skill | Enhancement |
|---|---|
| `ai-agents-tools` | Major refactor: scope narrows to "agent fundamentals (ReAct loop, tool contract, compound accuracy)" and cross-links the 12 new skills for everything else. |
| `ai-prompt-injection-and-tenant-safety` | Add §Agent-specific section: indirect prompt injection threat model + defences. |
| `ai-cost-per-tenant-attribution` | Add §Agent-step cost attribution: `cost-per-completed-task`, step-cost rollups. |
| `ai-entitlements-and-feature-gating` | Add Agent entitlements: `agent_enabled`, `max_steps`, `max_tools`, `concurrent_agents`, `allowed_tools[]`, `max_wallclock_minutes`. |
| `ai-observability-and-debugging` | Add Agent trace patterns: task / step / tool spans + replay link. |
| `ai-eval-harness` | Add Agent eval section: task success, intervention rate, step efficiency. |
| `ai-on-saas-architecture` | Add agent runtime as a 6th AI control-plane service. |
| `saas-rate-limiting-and-quotas` | Add agent quotas: concurrent agent sessions, agent-step/day, per-task wallclock cap. |
| `saas-admin-backoffice-tooling` | Add agent ops console: kill task, force-pause, view trace, override approval, retrace. |

---

## REFERENCE FILES (15)

| Skill | Reference | Purpose |
|---|---|---|
| `ai-agent-runtime-architecture` | `agent-loop-state-machine.md` | Formal state machine (PERCEIVE → PLAN → ACT → OBSERVE → ...) with retry and idempotency. |
| `ai-agent-runtime-architecture` | `agent-vs-workflow-vs-cron-decision.md` | Decision matrix with examples. |
| `ai-agent-tool-catalogue-and-action-gating` | `tool-schema-conventions.md` | JSON-schema conventions, naming, error contracts. |
| `ai-agent-tool-catalogue-and-action-gating` | `reversible-vs-irreversible-classification.md` | Classification rubric + examples. |
| `ai-agent-tool-catalogue-and-action-gating` | `tool-side-effect-budgets.md` | Side-effect budgets per session / tenant. |
| `ai-agent-action-approval-and-hitl` | `approval-ux-patterns.md` | 6 approval UX patterns. |
| `ai-agent-action-approval-and-hitl` | `just-in-time-approval-flow.md` | JIT approval implementation. |
| `ai-agent-reversibility-and-blast-radius` | `dry-run-patterns.md` | Dry-run engineering patterns. |
| `ai-agent-reversibility-and-blast-radius` | `transactional-group-patterns.md` | Saga + compensating actions. |
| `ai-agent-memory` | `memory-tiers.md` | Short / working / long-term memory schemas. |
| `ai-agent-memory` | `forget-on-erase-cascade.md` | GDPR erasure cascade through memory tiers. |
| `ai-agent-multi-agent-coordination` | `supervisor-worker.md` | Supervisor/worker contract. |
| `ai-agent-multi-agent-coordination` | `handoff-protocols.md` | Agent-to-agent handoff message contract. |
| `ai-agent-multi-agent-coordination` | `conflict-resolution.md` | Conflict + deadlock resolution. |
| `ai-agent-cost-and-step-budgets` | `budget-enforcement-pipeline.md` | Budget pipeline implementation. |
| `ai-agent-eval` | `golden-tasks-construction.md` | How to build agent golden tasks. |
| `ai-agent-eval` | `replay-based-eval.md` | Replay-based eval pipeline. |
| `ai-agent-observability-and-replay` | `trace-schema-agent.md` | OTel trace schema for agents. |
| `ai-agent-safety-and-red-team` | `indirect-prompt-injection-test-suite.md` | Test corpus + CI integration. |
| `ai-agent-async-and-long-running-tasks` | `durable-state-patterns.md` | Durable state implementation patterns. |
| `ai-agent-mobile-and-web-ux-patterns` | `agent-inbox-spec.md` | Agent inbox component spec. |

---

## Cross-Engine Handoffs

- **SRS engine** should expect: agent-feature SRS template including `max_steps`, `allowed_tools[]`, reversibility classification per tool, blast-radius caps, plan-preview UX, kill-switch contract, agent SLOs (success rate, intervention rate, time-to-complete).
- **Proposal engine** should expect: pricing implication of "agent included" tier; agent-as-feature differentiator; risk disclosure (irreversibility, oversight, audit, GDPR memory erasure); KPIs the buyer should ask for.
- **Business-plan engine** should expect: COGS model with agent-task cost line; agent abandonment rate as a leading indicator of refunds.

---

## Critical Gaps Still Open

- **Agent SLAs to customers.** What does a customer get when an agent task fails halfway? No skill yet on agent service-level commitments and the credit/comms playbook. (Future: `ai-agent-sla-and-commitments`.)
- **Agent fine-tuning / specialisation.** When does an agent need a tuned model vs a smarter prompt? Punted to `ai-llm-integration` for now.
- **Voice / embodied agents.** Out of scope.
- **Cross-tenant agent collaboration.** (e.g., one tenant's agent talks to another tenant's agent via federation.) Out of scope.

---

## Recommended Next Sessions

1. **Agent commercial layer:** SLAs, pricing, "agent included" packaging, refund logic on failed tasks.
2. **Agent compliance:** SOC2 / ISO27001 controls specific to agentic systems (action audit, approval audit, kill-switch drill).
3. **Agent model selection:** task-router patterns (cheap model for routing, expensive for planning, cheap for tool-arg generation).
4. **Agent platform vs agent feature:** when a B2B SaaS exposes agent-building primitives to *its* customers (the agentic-PaaS lens).
