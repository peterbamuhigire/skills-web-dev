---
name: ai-agents-tools
description: Use when learning the **fundamentals** of LLM agents and tool use — the ReAct loop, tool contract rules, compound-accuracy problem, single-agent design, when to build an agent at all. For production agent product engineering in multi-tenant SaaS, route to the agent-* family of skills (runtime, tool catalogue, approval, reversibility, memory, multi-agent coordination, cost budgets, eval, observability, safety, long-running, mobile UX).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agents and Tool Use — Fundamentals
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Learning the agent paradigm — what an agent is, the ReAct loop, when to build one.
- Understanding the **tool contract** at the conceptual level — what a tool is, naming, schemas, idempotency, error contracts.
- Understanding the **compound-accuracy** problem and the **when-not-to-build-an-agent** decision.
- Onboarding an engineer to agentic features before they touch production code.

## Do Not Use When

- Building a production agent inside a multi-tenant SaaS — load the **agent-product stack** (see map below).
- Designing the agent runtime, durable execution, or state machine → `ai-agent-runtime-architecture`.
- Building the tool registry with per-tenant allow-lists and reversibility classification → `ai-agent-tool-catalogue-and-action-gating`.
- Designing the approval flow / plan preview / undo window → `ai-agent-action-approval-and-hitl`.
- Engineering reversibility (dry-run, staged commit, saga) → `ai-agent-reversibility-and-blast-radius`.
- Designing memory tiers → `ai-agent-memory`.
- Multi-agent topologies (supervisor/worker, debate, handoff) → `ai-agent-multi-agent-coordination`.
- Step / token / wallclock / cost budgets → `ai-agent-cost-and-step-budgets`.
- Task-level evaluation → `ai-agent-eval`.
- Trace, replay, task viewer → `ai-agent-observability-and-replay`.
- Indirect prompt injection, action escalation, exfil, red-team → `ai-agent-safety-and-red-team`.
- Long-running (minutes-to-days) agents → `ai-agent-async-and-long-running-tasks`.
- Agent inbox, plan preview UI, mobile approval → `ai-agent-mobile-and-web-ux-patterns`.

## The Agent Product Stack — Map

When building an agentic feature in a multi-tenant SaaS, load these in order:

1. **Architecture & deciding to build an agent**
   - This skill (fundamentals).
   - `ai-on-saas-architecture` — agent runtime as the 6th AI control-plane service.
   - `ai-agent-runtime-architecture` — agent vs workflow vs cron decision, state machine, durable execution.

2. **Tools & gating**
   - `ai-agent-tool-catalogue-and-action-gating` — registry, schemas, allow-lists, reversibility, side-effect budgets.
   - `ai-agent-reversibility-and-blast-radius` — dry-run, staged commits, saga, blast caps.

3. **HITL & UX**
   - `ai-agent-action-approval-and-hitl` — approval patterns, plan preview, JIT, undo, bulk.
   - `ai-agent-mobile-and-web-ux-patterns` — inbox, mobile push, persona.

4. **Memory & coordination**
   - `ai-agent-memory` — short / working / long-term + GDPR cascade.
   - `ai-agent-multi-agent-coordination` — supervisor/worker, handoff, conflict resolution.

5. **Cost, safety, eval, observability**
   - `ai-agent-cost-and-step-budgets`
   - `ai-agent-safety-and-red-team`
   - `ai-agent-eval`
   - `ai-agent-observability-and-replay`

6. **Long-running**
   - `ai-agent-async-and-long-running-tasks`

7. **Ops & commercial**
   - `ai-entitlements-and-feature-gating` (agent entitlements).
   - `saas-rate-limiting-and-quotas` (agent quotas).
   - `saas-admin-backoffice-tooling` (agent ops console).
   - `ai-cost-per-tenant-attribution` (agent-step cost rollup).
   - `ai-prompt-injection-and-tenant-safety` (agent-specific section).
   - `ai-observability-and-debugging` (agent trace section).
   - `ai-eval-harness` (agent eval section).

## Required Inputs

- The feature spec or business outcome the agent is meant to deliver.
- The multi-tenant context: tenancy model, plan tiers, region.
- Whether the deliverable is a learning artifact, a single-agent prototype, or a production agent.

## Workflow

1. Read this `SKILL.md`.
2. Apply the **when-to-build-an-agent** decision (§ When to Build an Agent below). If the answer is workflow, route to a workflow design.
3. Understand the **ReAct loop** (§ ReAct Pattern) and the **tool contract** (§ Tool Contract Rules).
4. Note the **compound-accuracy problem** and design for short chains + verification.
5. Route to the **agent product stack** above for any production work — do not implement runtime, approval, safety, etc. from this skill alone.

## Quality Standards

- An agent decision is documented with rationale; "agent by default" is rejected.
- Tools follow the contract: typed schemas, authorisation inside the tool, idempotency, structured errors, concise observations.
- Every production agent task has a step budget, a tool budget, a wallclock budget, and a kill-switch.
- Every irreversible action passes through human approval.
- Every agent feature has goldens, eval thresholds, and a red-team suite.

## Anti-Patterns

- Building an agent because "agents are cool". See `ai-agent-runtime-architecture` §1.
- A `tools` array hard-coded in feature code. Use the registry (`ai-agent-tool-catalogue-and-action-gating`).
- No step cap, no token cap, no wallclock cap. Runaway loops, surprise bills.
- Irreversible actions auto-executed.
- One generic `db_query(sql)` tool. The agent will write `DROP TABLE`.
- Tool descriptions that say "use this to do anything with X".
- Treating retrieved KB chunks as trusted instructions. Indirect injection.

## Outputs

- A clear decision: agent / workflow / cron, with rationale.
- A tool list with classifications (read-only / reversible / irreversible).
- A pointer to the agent product stack for downstream implementation.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Agent-vs-workflow decision record | Markdown | `docs/ai/agent-decision-<feature>.md` |
| Correctness | Tool contract tests | CI log | `tests/ai/tools/` |
| Security | Tool reversibility classification | CSV / Markdown | `docs/ai/tool-reversibility.csv` |
| Release evidence | Agent product stack handoff checklist | Markdown | `docs/ai/agent-stack-checklist-<feature>.md` |

## References

- `ai-agent-runtime-architecture` and its references for the runtime.
- `ai-agent-tool-catalogue-and-action-gating` and its references for the tool registry.
- Each agent-* skill carries its own reference files.
- Companion: `ai-on-saas-architecture`, `ai-llm-integration`, `ai-prompt-engineering`, `ai-rag-multi-tenant`, `ai-evaluation`, `ai-security`.
- Agent incident handoff: irreversible-action surprises, action-approval bypass, indirect prompt injection via tool output, and runaway loops are detection signals in `ai-incident-detection-and-triage`. See `ai-incident-response-runbook` failure class `agent-action` for first mitigation and `ai-rca-taxonomy` domain `tool-agent` for RCA categories.
<!-- dual-compat-end -->
## Overview

An agent is an LLM that can perceive its environment and take actions. Tools extend the LLM beyond text generation into real-world operations: fetching data, calculating, writing to databases, sending emails.

**Core warning:** Write actions (email, database updates, payments) expose your system to severe risk. Always require human approval before irreversible actions.

## Agent Platform Standard

Build agents as production software components with explicit contracts, not as free-form prompts. A reliable agent platform needs:

- A host application that owns identity, tenant context, UI, permissions, budgets, logging, and approval flows.
- Tool servers or adapters with typed schemas, narrow scopes, deterministic errors, pagination, timeouts, and audit logs.
- Resource access rules for files, databases, APIs, and knowledge bases.
- Prompt and policy versioning for planner instructions, tool descriptions, refusal rules, and escalation paths.
- Execution traces that record plan, tool calls, observations, approvals, final output, model version, and cost.
- Evaluation cases that cover happy paths, edge cases, adversarial prompts, permission failures, and tool outages.

If using MCP or another tool protocol, treat the protocol boundary as an API boundary: authenticate it, version it, test it, monitor it, and document it.

---

## When to Build an Agent

Build an agent when:
- The task requires multiple sequential or parallel steps
- Different steps need different tools or data sources
- The workflow varies based on the input (not always the same steps)
- The value of automation exceeds the cost of evaluation, guardrails, monitoring, and incident response

Use a simple LLM call when:
- The task is a single transformation (summarise, classify, extract)
- The steps are always the same (use a prompt template instead)
- A deterministic workflow can express the business process more safely

---

## Tool Categories

### 1. Knowledge Tools (Read-Only)
Extend what the model knows. Safe to automate.

| Tool | What It Does |
|---|---|
| RAG retriever | Fetch relevant chunks from private knowledge base |
| SQL query executor | Query reports, inventory, customer data |
| Web search | Current events, competitor prices |
| REST API reader | Fetch supplier prices, exchange rates, weather |
| File reader | Parse uploaded CSV, PDF, invoice |

### 2. Calculation Tools
LLMs are bad at math. Always delegate.

| Tool | What It Does |
|---|---|
| Calculator | Arithmetic, tax, margins, totals |
| Date/time | Current time, due date arithmetic, timezone |
| Unit converter | Currency, weight, volume |
| Word/character counter | Validate response length |

### 3. Action Tools (Read-Write) — REQUIRE APPROVAL
These modify state. Use with extreme care.

| Tool | Risk | Approval Required |
|---|---|---|
| Send email | Medium | Yes, unless explicitly automated |
| Create invoice | Medium | Yes |
| Update database | High | Yes |
| Initiate payment | Very High | Always |
| Delete record | Very High | Always |

### Tool Contract Rules

- Name tools by business action, not implementation detail: `create_invoice_draft`, not `db_write`.
- Keep tools small. One tool should do one auditable thing.
- Validate inputs before tool execution and return structured errors the agent can handle.
- Enforce authorization inside the tool, not only in the prompt.
- Add idempotency keys for actions that create, update, send, charge, or schedule.
- Add dry-run/preview modes for destructive or client-facing actions.
- Return concise observations. Do not dump raw secrets, full tables, or unrelated records into the model context.
- Log every call with tenant, user, tool name, arguments hash, result status, latency, and approval id where relevant.

## MCP-Style Capability Design

| Capability | Use For | Hardening Rule |
|---|---|---|
| Tools | Actions and calculations | Typed schema, permission check, timeout, structured error |
| Resources | Read-only context such as docs, files, records | Tenant-scoped access, freshness label, source metadata |
| Prompts | Reusable task instructions | Versioned templates, input validation, review owner |
| Sampling | Model calls requested by a server | Explicit host approval and cost limits |
| Roots | Filesystem/project boundaries | Restrict to approved paths and deny path traversal |

Do not expose broad tools such as shell, SQL, email, or browser automation directly to an agent unless a human is in the loop and the scope is strongly constrained.

---

## ReAct Pattern (Recommended Loop)

ReAct (Reasoning + Acting) interleaves thought and action.

```
Thought: I need to find the total spent on chicken this month.
Act: query_database(query="SELECT SUM(amount) FROM expenses WHERE category='chicken' AND month='2026-04'")
Observation: {"total": 450000, "currency": "UGX"}
Thought: I have the total. Now I'll format the response.
Act: respond("Chicken spend this month: UGX 450,000")
```

Each cycle: Thought → Act → Observation → repeat until done.

## Planning and Control Loop

- Add a max step count and max tool-call budget.
- Require the agent to explain the next intended action before high-risk tools.
- Stop and ask for human approval when confidence is low, permissions are missing, or an action is irreversible.
- Prefer plan -> execute -> verify -> summarize for business workflows.
- Store traces so failed runs can be replayed against new prompts, tools, or models.

### ReAct Prompt Template

```
You have access to these tools:
{tool_descriptions}

Use this format exactly:
Thought: [your reasoning]
Action: tool_name
Input: {"param": "value"}
Observation: [tool result]
... (repeat as needed)
Final Answer: [your response to the user]

Current task: {user_query}
Context: {conversation_history}
```

---

## Tool Definition Schema

Define tools clearly. The model reads these descriptions to decide which tool to use.

```php
$tools = [
    [
        'name' => 'query_sales_report',
        'description' => 'Query the restaurant sales database. Use for: total revenue, top-selling items, sales by period, comparison between branches. Returns JSON.',
        'parameters' => [
            'type' => 'object',
            'properties' => [
                'start_date' => ['type' => 'string', 'description' => 'Start date ISO8601 (YYYY-MM-DD)'],
                'end_date'   => ['type' => 'string', 'description' => 'End date ISO8601 (YYYY-MM-DD)'],
                'metric'     => ['type' => 'string', 'enum' => ['revenue', 'orders', 'items'], 'description' => 'What to measure'],
                'branch_id'  => ['type' => 'integer', 'description' => 'Optional: specific branch ID'],
            ],
            'required' => ['start_date', 'end_date', 'metric'],
        ],
    ],
    [
        'name' => 'calculate',
        'description' => 'Evaluate a mathematical expression. Use for arithmetic, percentages, tax calculations.',
        'parameters' => [
            'type' => 'object',
            'properties' => [
                'expression' => ['type' => 'string', 'description' => 'Math expression e.g. "45000 * 0.18"'],
            ],
            'required' => ['expression'],
        ],
    ],
];
```

---

## Agent Execution Loop (PHP)

```php
class AiAgent {
    private int $maxSteps = 10;

    public function run(string $query, int $tenantId, int $userId): string {
        // Check AI module gate
        checkAiQuota($tenantId);

        $messages = $this->buildInitialMessages($query);
        $totalTokensIn = 0;
        $totalTokensOut = 0;

        for ($step = 0; $step < $this->maxSteps; $step++) {
            $response = $this->callLLM($messages, $this->tools);
            $totalTokensIn  += $response['usage']['prompt_tokens'];
            $totalTokensOut += $response['usage']['completion_tokens'];

            $choice = $response['choices'][0];

            // Check if done
            if ($choice['finish_reason'] === 'stop') {
                $this->logTokens($tenantId, $userId, 'agent', $totalTokensIn, $totalTokensOut);
                return $choice['message']['content'];
            }

            // Execute tool call
            if ($choice['finish_reason'] === 'tool_calls') {
                $toolCall = $choice['message']['tool_calls'][0];
                $toolName = $toolCall['function']['name'];
                $toolArgs = json_decode($toolCall['function']['arguments'], true);

                // Human approval gate for write actions
                if ($this->requiresApproval($toolName)) {
                    if (!$this->requestApproval($tenantId, $userId, $toolName, $toolArgs)) {
                        return 'Action requires your approval. Please confirm in the approvals section.';
                    }
                }

                $toolResult = $this->executeTool($toolName, $toolArgs, $tenantId);

                // Append tool call + result to messages
                $messages[] = $choice['message'];
                $messages[] = [
                    'role' => 'tool',
                    'tool_call_id' => $toolCall['id'],
                    'content' => json_encode($toolResult),
                ];
            }
        }

        $this->logTokens($tenantId, $userId, 'agent', $totalTokensIn, $totalTokensOut);
        return 'Maximum steps reached. Please try a more specific question.';
    }
}
```

---

## Human Approval Gate

```sql
CREATE TABLE ai_approval_requests (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  tenant_id     INT NOT NULL,
  user_id       INT NOT NULL,
  tool_name     VARCHAR(100),
  tool_args     JSON,
  status        ENUM('pending','approved','rejected') DEFAULT 'pending',
  reviewed_by   INT,
  reviewed_at   TIMESTAMP,
  created_at    TIMESTAMP DEFAULT NOW()
);
```

**Approval rules:**
- Send email: require approval (default)
- Create/update records: require approval
- Payments: always require approval + 2FA
- Read-only queries: no approval needed

---

## Agent Types for Client Apps

| Agent Type | Trigger | Use Case |
|---|---|---|
| **Report Agent** | Scheduled / on-demand | Weekly sales summary, cost analysis |
| **Analysis Agent** | User query | "Why did revenue drop last week?" |
| **Advisory Agent** | User query | "What should I reorder?" |
| **Alert Agent** | Event-driven | "Stock below threshold — notify owner" |
| **Document Agent** | File upload | "Analyse this supplier invoice" |

---

## Multi-Agent Pattern

For complex tasks, decompose into specialised agents.

```
User: "Give me a full analysis of last month's performance and suggest improvements."

Orchestrator Agent
    ├── Data Agent: fetch sales, costs, inventory data
    ├── Analysis Agent: identify trends and anomalies
    ├── Benchmark Agent: compare to same period last year
    └── Advisory Agent: generate improvement suggestions

Orchestrator: synthesise all outputs → final report
```

Each agent has its own system prompt, tool set, and token budget.

---

## Compound Accuracy Problem

If each step has 95% accuracy, over N steps:

| Steps | Compound Accuracy |
|---|---|
| 3 | 86% |
| 5 | 77% |
| 10 | 60% |
| 20 | 36% |

**Implication:** Keep agent workflows short. Use strong models for planning. Add self-verification steps.

---

## Anti-Patterns

- **No step limit** — runaway agents can drain token budgets
- **Unguarded write actions** — agents that can delete or send without approval
- **No token logging per tool** — you cannot see which tools are costing the most
- **Vague tool descriptions** — the model picks wrong tools from unclear descriptions
- **Too many tools** — keep each agent focused; max 5–8 tools per agent
- **No fallback** — always define what happens when the agent exceeds max steps

---

## Sources
Chip Huyen — *AI Engineering* (2025) Ch.6; David Spuler — *Generative AI Applications* (2024) Ch.20–21
