---
name: openai-agents-sdk
description: Build production AI agents with the OpenAI Agents SDK (Python) — 6 core
  primitives (Agent, Runner, Tools, Handoff, Guardrails, Tracing), multi-agent patterns
  (Centralized, Hierarchical, Decentralized, Swarm), dynamic/deterministic orchestration...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# OpenAI Agents SDK
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Build production AI agents with the OpenAI Agents SDK (Python) — 6 core primitives (Agent, Runner, Tools, Handoff, Guardrails, Tracing), multi-agent patterns (Centralized, Hierarchical, Decentralized, Swarm), dynamic/deterministic orchestration...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `openai-agents-sdk` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | OpenAI Agents SDK contract test plan | Markdown doc covering Agent, Runner, Tools, Handoff, and Guardrails primitive tests | `docs/ai/openai-agents-tests.md` |
| Security | Agent guardrail and key handling note | Markdown doc covering tool whitelisting, output filtering, and API key rotation | `docs/ai/openai-agents-security.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Minimal Python SDK for building AI agents. Six primitives: **Agent, Runner, Tools, Handoff, Guardrails, Tracing**.

```bash
pip install openai-agents
export OPENAI_API_KEY="sk-..."
```

---

## 1. Agent — The Core Primitive

A configurable wrapper around an LLM that can take actions.

```python
from agents import Agent

customer_service_agent = Agent(
    name="Customer Service Agent",
    model="gpt-4o",                    # or any OpenAI-compatible model
    instructions="""
        You are a helpful customer service agent.
        Handle returns, orders, and billing queries.
        Escalate complex issues to a human.
    """,
    tools=[get_order_status, process_refund, track_shipment],
    handoffs=[billing_agent, technical_agent],    # agents to delegate to
)
```

**Agent parameters:** `name`, `instructions` (system prompt), `model`, `tools`, `handoffs`, `guardrails`, `output_type`

---

## 2. Runner — The Agent Loop

Runs the agent's reasoning loop (think → act → observe → repeat).

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant.", model="gpt-4o")

# Synchronous (simple scripts, testing)
result = Runner.run_sync(agent, "What is the capital of France?")
print(result.final_output)

# Asynchronous (web apps, FastAPI)
import asyncio
result = await Runner.run(agent, "Summarise this document.", max_turns=10)
print(result.final_output)
```

**Key parameter:** `max_turns` — safety valve against infinite loops. Always set it.

```python
result = Runner.run_sync(agent, user_message, max_turns=15)
```

---

## 3. Tools — Extending Agent Capabilities

### Custom Tools (Python Functions)

Any Python function becomes a tool with `@function_tool`. The SDK reads the name, docstring, and type hints automatically.

```python
from agents import function_tool

@function_tool
def get_order_status(order_id: str) -> str:
    """Gets the current status of a customer order.
    
    Args:
        order_id: The unique order identifier (e.g. ORD-12345)
    """
    order = db.query("SELECT status FROM orders WHERE id = ?", [order_id])
    return f"Order {order_id} is: {order['status']}"

@function_tool
def calculate_refund(order_id: str, reason: str) -> dict:
    """Calculate and process a refund for an order.
    
    Args:
        order_id: The order to refund
        reason: Customer-provided reason for return
    """
    amount = get_order_total(order_id)
    return {"refund_amount": amount, "processing_days": 3}
```

### Hosted Tools (Built-in OpenAI)

```python
from agents import Agent
from agents.tools import WebSearchTool, FileSearchTool, CodeInterpreterTool

research_agent = Agent(
    name="Research Agent",
    model="gpt-4o",
    instructions="Research topics thoroughly and provide cited summaries.",
    tools=[
        WebSearchTool(),          # search the web
        FileSearchTool(            # search vector store
            vector_store_ids=["vs_abc123"]
        ),
        CodeInterpreterTool(),    # run Python code
    ],
)
```

### Agent as Tool

```python
# When you need a sub-agent but the calling agent retains control
analysis_tool = analysis_agent.as_tool(
    tool_name="RunAnalysis",
    tool_description="Run deep financial analysis on the provided data."
)

orchestrator = Agent(
    name="Orchestrator",
    tools=[analysis_tool, data_fetcher],
)
```

**Handoff vs as_tool:**
- `handoff` — complete transfer of control, caller stops
- `as_tool` — caller delegates subtask, caller resumes after

---

## 4. Handoffs — Multi-Agent Delegation

```python
from agents import Agent, Runner

# Specialized agents
billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle all billing, payment, and invoice queries.",
    tools=[lookup_invoice, process_payment],
)
technical_agent = Agent(
    name="Technical Agent",
    instructions="Resolve technical issues, bugs, and connectivity problems.",
    tools=[check_system_status, reset_connection],
)

# Triage agent with handoffs
triage_agent = Agent(
    name="Triage Agent",
    instructions="""
        Triage the user's request. If billing-related, route to Billing Agent.
        If technical, route to Technical Agent. Otherwise, answer directly.
    """,
    handoffs=[billing_agent, technical_agent],
)

result = Runner.run_sync(triage_agent, "My invoice shows the wrong amount")
print(result.final_output)
```

**Handoff prompt best practices:**
- Explicitly name which conditions trigger a handoff in each agent's instructions
- Each specialist agent must clearly state its purpose and domain
- Use `result.last_agent` to track which agent handled the final response

---

## 5. Multi-Agent Patterns

### Centralized (Most Common)

One triage/orchestrator routes to specialists. Best for: customer support, internal assistants, helpdesks.

```python
# One central agent → N specialized agents
triage_agent = Agent(
    name="Triage",
    handoffs=[billing_agent, technical_agent, sales_agent],
)
```

### Hierarchical

Multi-tier routing: triage → managers → specialists. Best for: deep research, complex enterprise workflows.

```python
# Triage → Domain Manager → Domain Specialists
science_manager = Agent(name="Science Manager",
    handoffs=[physics_agent, chemistry_agent])
history_manager = Agent(name="History Manager",
    handoffs=[politics_agent, warfare_agent])
triage = Agent(name="Research Triage",
    handoffs=[science_manager, history_manager])
```

### Dynamic vs Deterministic Orchestration

```python
# Deterministic — hardcoded routing (predictable, inflexible)
def orchestrate(message: str):
    if "complaint" in message.lower():
        return Runner.run_sync(complaints_agent, message)
    return Runner.run_sync(inquiry_agent, message)

# Dynamic — LLM decides routing (flexible, less predictable)
triage_agent = Agent(
    name="Triage",
    instructions="Route requests to the most appropriate specialized agent.",
    handoffs=[complaints_agent, inquiry_agent],  # LLM picks at runtime
)
```

### Decentralized (Debate / Brainstorm)

No central agent; agents exchange turns. Best for: ideation, debate, negotiation.

```python
agents = [Agent(name=f"{role}", instructions=f"You are a {role}...") for role in roles]
# Manual round-robin loop — SDK does not auto-manage decentralized flow
for i in range(rounds):
    result = Runner.run_sync(agents[i % len(agents)], history, session=session)
```

### Swarm (Parallel Exploration)

Many simple agents in parallel, results aggregated. Best for: creative generation, optimization.

```python
import concurrent.futures

def run_agent(agent, prompt):
    return Runner.run_sync(agent, prompt).final_output

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(lambda a: run_agent(a, prompt), specialist_agents))

summary = Runner.run_sync(aggregator_agent, "\n".join(results))
```

---

## 6. Memory Management

```python
from agents import SQLiteSession

# Persistent conversation memory (survives restarts)
session = SQLiteSession("my_app_db")
last_agent = triage_agent

while True:
    user_input = input("You: ")
    result = Runner.run_sync(last_agent, user_input, session=session)
    print("Agent:", result.final_output)
    last_agent = result.last_agent  # continue with whoever last responded
```

**Sliding window for long conversations:**

```python
# Summarize old messages when context grows too large
if len(messages) > 20:
    summary = Runner.run_sync(summarizer_agent, "\n".join(messages[-20:]))
    messages = [{"role": "system", "content": f"Conversation so far: {summary.final_output}"}]
```

---

## 7. Guardrails — Safety Validation

```python
from agents import Agent, Runner, GuardrailFunctionOutput, RunContextWrapper
from agents import input_guardrail, output_guardrail, InputGuardrailTripwireTriggered
from agents.types import TResponseInputItem

@input_guardrail
async def scope_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """Only allow customer service queries."""
    is_valid = any(kw in str(input).lower()
                   for kw in ['order', 'refund', 'account', 'billing', 'payment', 'delivery'])
    return GuardrailFunctionOutput(
        output_info="valid" if is_valid else "out of scope",
        tripwire_triggered=not is_valid,
    )

agent = Agent(
    name="CS Agent",
    instructions="Handle customer service queries.",
    input_guardrails=[scope_guardrail],
)

try:
    result = Runner.run_sync(agent, "What's the meaning of life?")
except InputGuardrailTripwireTriggered:
    print("Sorry, I can only help with customer service queries.")
```

---

## 8. Third-Party Models (OpenAI-Compatible)

```python
from agents.extensions.models.litellm_model import LitellmModel

# Use DeepSeek, Anthropic, Gemini, Llama — anything via LiteLLM
agent = Agent(
    name="Multi-Model Agent",
    model=LitellmModel(model="deepseek/deepseek-chat", api_key="..."),
    instructions="You are a helpful assistant.",
)

# Or set globally
import agents
agents.set_default_openai_api("chat_completions")
agents.set_default_openai_client(AsyncOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.environ["DEEPSEEK_API_KEY"],
))
```

---

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| No `max_turns` limit | Always set `max_turns` — prevents runaway agent loops |
| Vague agent instructions | Explicitly name routing conditions and domain boundaries |
| Too many tools per agent | Keep 5–8 tools max per agent — too many confuses the model |
| Write actions without approval | Add human approval gate before any irreversible action |
| No session management | Use `SQLiteSession` for multi-turn conversations |
| Missing error handling | Wrap `Runner.run_sync()` in try/except for guardrail errors |

---

*Source: Habib — Building Agents with OpenAI Agents SDK (Packt, 2025)*