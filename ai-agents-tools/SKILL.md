---
name: ai-agents-tools
description: Use when building AI features that need to take actions, use multiple
  tools, or execute multi-step workflows — agent patterns, tool integration, ReAct
  loop, planning, multi-agent systems, and human approval gates
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agents and Tool Use

<!-- dual-compat-start -->
## Use When

- Use when building AI features that need to take actions, use multiple tools, or execute multi-step workflows — agent patterns, tool integration, ReAct loop, planning, multi-agent systems, and human approval gates
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-agents-tools` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Overview

An agent is an LLM that can perceive its environment and take actions. Tools extend the LLM beyond text generation into real-world operations: fetching data, calculating, writing to databases, sending emails.

**Core warning:** Write actions (email, database updates, payments) expose your system to severe risk. Always require human approval before irreversible actions.

---

## When to Build an Agent

Build an agent when:
- The task requires multiple sequential or parallel steps
- Different steps need different tools or data sources
- The workflow varies based on the input (not always the same steps)

Use a simple LLM call when:
- The task is a single transformation (summarise, classify, extract)
- The steps are always the same (use a prompt template instead)

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
