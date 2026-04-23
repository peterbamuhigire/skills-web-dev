---
name: ai-llm-integration
description: Integrate LLMs into any application — OpenAI, Anthropic Claude, DeepSeek,
  and Gemini APIs directly (no framework required), streaming responses, function
  calling/tool use, embeddings and semantic search, multi-model routing, prompt caching,
  rate...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# LLM API Integration
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Integrate LLMs into any application — OpenAI, Anthropic Claude, DeepSeek, and Gemini APIs directly (no framework required), streaming responses, function calling/tool use, embeddings and semantic search, multi-model routing, prompt caching, rate...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-llm-integration` or would be better handled by a more specific companion skill.
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
| Security | Provider key handling note | Markdown doc covering secret storage, rotation, and per-tenant isolation | `docs/ai/llm-key-handling.md` |
| Correctness | Provider contract test results | CI log or recorded test report covering response shape and streaming | `docs/ai/llm-contract-tests.md` |
| Performance | Token-usage and latency budget | Markdown doc stating per-call token and latency budgets | `docs/ai/llm-budgets.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Direct integration patterns for all major LLM providers.
For framework patterns (Vercel AI SDK, agents), see `ai-web-apps` and `openai-agents-sdk` skills.

## Provider Quick Reference

| Provider | Best For | SDK | Base URL |
|---|---|---|---|
| OpenAI GPT-4o | General, function calling | `openai` | `api.openai.com/v1` |
| Anthropic Claude | Long context, coding, analysis | `@anthropic-ai/sdk` | `api.anthropic.com` |
| DeepSeek V3 | Cost-effective general tasks | `openai` (compatible) | `api.deepseek.com/v1` |
| DeepSeek R1 | Reasoning, math, science | `openai` (compatible) | `api.deepseek.com/v1` |
| Google Gemini | Multimodal, large context | `@google/generative-ai` | via SDK |
| Ollama (local) | Privacy, offline, zero cost | `openai` (compatible) | `localhost:11434/v1` |

See `deepseek-integration` skill for DeepSeek-specific details and model selection.

---

## 1. OpenAI API — Python

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
```

```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env

# Basic chat
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Summarise this contract in 3 bullet points."},
    ],
    max_tokens=512,
    temperature=0.3,
)
print(response.choices[0].message.content)
print(f"Tokens: {response.usage.total_tokens}")
```

### Streaming (Python)

```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a business plan intro."}],
    stream=True,
    max_tokens=1024,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

### Function Calling / Tool Use (Python)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_invoice",
            "description": "Retrieve invoice details by invoice number",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice_number": {"type": "string"},
                    "include_line_items": {"type": "boolean", "default": False},
                },
                "required": ["invoice_number"],
            },
        },
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Show me invoice INV-2025-001"}],
    tools=tools,
    tool_choice="auto",
)

if response.choices[0].finish_reason == "tool_calls":
    tool_call = response.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    result = get_invoice(**args)

    # Send tool result back
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result),
    })
    final = client.chat.completions.create(model="gpt-4o", messages=messages)
```

### Structured Output (JSON mode)

```python
from pydantic import BaseModel

class InvoiceSummary(BaseModel):
    total: float
    currency: str
    due_date: str
    items: list[str]

response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[{"role": "user", "content": f"Extract invoice data: {invoice_text}"}],
    response_format=InvoiceSummary,
)
invoice = response.choices[0].message.parsed  # fully typed InvoiceSummary
```

### Embeddings

```python
result = client.embeddings.create(
    model="text-embedding-3-small",     # or text-embedding-3-large
    input=["Chicken recipe with garlic", "Install solar panels"],
)
embedding = result.data[0].embedding   # list of 1536 floats
```

---

## 2. Anthropic Claude API — Python

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a legal document reviewer. Be precise and thorough.",
    messages=[
        {"role": "user", "content": "Review this contract clause for risks: ..."}
    ],
)
print(message.content[0].text)
print(f"Input tokens: {message.usage.input_tokens}")
```

### Claude Streaming

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[{"role": "user", "content": "Write a detailed report on..."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Claude Tool Use

```python
tools = [
    {
        "name": "search_database",
        "description": "Search the product database by name or SKU",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    }
]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Find products matching 'solar panel 250W'"}],
)

# Handle tool use
for block in response.content:
    if block.type == "tool_use":
        result = search_database(**block.input)
        # Continue conversation with tool result
```

### Prompt Caching (Reduce Costs for Repeated Context)

```python
# Cache large system context — reduces cost by ~90% on repeated calls
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": large_document_text,  # e.g. a 50-page manual
            "cache_control": {"type": "ephemeral"},  # cached for 5 min
        }
    ],
    messages=[{"role": "user", "content": "What does section 4.2 say about safety?"}],
)
```

---

## 3. OpenAI API — JavaScript/TypeScript

```bash
npm install openai
```

```typescript
import OpenAI from "openai";

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Basic
const response = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "Translate to Swahili: Hello world" }],
  max_tokens: 100,
});
console.log(response.choices[0].message.content);

// Streaming in Node.js
const stream = client.chat.completions.stream({
  model: "gpt-4o",
  messages: [{ role: "user", content: "Write a poem about Kampala." }],
  stream: true,
});
for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content ?? "");
}

// Streaming in Next.js API route
export async function POST(req: Request) {
  const { prompt } = await req.json();
  const stream = await client.chat.completions.create({
    model: "gpt-4o",
    messages: [{ role: "user", content: prompt }],
    stream: true,
  });
  return new Response(stream.toReadableStream());
}
```

---

## 4. Anthropic Claude — JavaScript/TypeScript

```bash
npm install @anthropic-ai/sdk
```

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Analyse the sentiment of: 'Great service!'" }],
});
console.log(message.content[0].text);
```

---

## 5. PHP — LLM Integration

```php
<?php
class LLMClient {
    private string $apiKey;
    private string $baseUrl;
    private string $defaultModel;

    public function __construct(string $provider = 'openai') {
        match ($provider) {
            'openai'   => [$this->baseUrl, $this->apiKey, $this->defaultModel] =
                ['https://api.openai.com/v1', getenv('OPENAI_API_KEY'), 'gpt-4o'],
            'deepseek' => [$this->baseUrl, $this->apiKey, $this->defaultModel] =
                ['https://api.deepseek.com/v1', getenv('DEEPSEEK_API_KEY'), 'deepseek-chat'],
            'ollama'   => [$this->baseUrl, $this->apiKey, $this->defaultModel] =
                ['http://localhost:11434/v1', 'ollama', 'deepseek-r1:7b'],
        };
    }

    public function chat(array $messages, array $options = []): string {
        $payload = array_merge([
            'model'      => $this->defaultModel,
            'messages'   => $messages,
            'max_tokens' => 1024,
            'temperature'=> 0.7,
        ], $options);

        $ch = curl_init($this->baseUrl . '/chat/completions');
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => json_encode($payload),
            CURLOPT_HTTPHEADER     => [
                'Content-Type: application/json',
                'Authorization: Bearer ' . $this->apiKey,
            ],
        ]);
        $response = json_decode(curl_exec($ch), true);
        curl_close($ch);
        return $response['choices'][0]['message']['content'] ?? '';
    }
}

// Usage
$llm = new LLMClient('deepseek');
$answer = $llm->chat([
    ['role' => 'system', 'content' => 'You are a business assistant.'],
    ['role' => 'user',   'content' => 'Draft a payment reminder email.'],
]);
```

---

## 6. Multi-Model Routing

Route to different models based on task complexity and cost:

```python
def route_to_model(task_type: str, token_estimate: int) -> tuple[str, str]:
    """Returns (provider, model) based on task."""
    if task_type == "reasoning" or "math" in task_type:
        return "deepseek", "deepseek-reasoner"       # R1 for reasoning
    if token_estimate > 50000:
        return "anthropic", "claude-sonnet-4-6"       # Claude for long context
    if task_type in ("quick", "simple", "classify"):
        return "deepseek", "deepseek-chat"            # cheap for simple tasks
    return "openai", "gpt-4o"                         # GPT-4o as default
```

---

## 7. Rate Limiting + Retry with Backoff

```python
import time
from openai import RateLimitError, APIError

def call_with_retry(client, **kwargs, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError:
            wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
            time.sleep(wait)
        except APIError as e:
            if e.status_code in (500, 502, 503) and attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise
    raise RuntimeError("Max retries exceeded")
```

---

## 8. Cost Tracking

```python
# Track spend per API call
def log_usage(model: str, usage, tenant_id: int):
    # Approximate costs (update as pricing changes)
    costs = {
        "gpt-4o":            (2.50, 10.00),    # (input per M, output per M)
        "deepseek-chat":     (0.27,  1.10),
        "deepseek-reasoner": (0.55,  2.19),
        "claude-sonnet-4-6": (3.00, 15.00),
    }
    if model in costs:
        in_rate, out_rate = costs[model]
        cost = (usage.prompt_tokens * in_rate + usage.completion_tokens * out_rate) / 1_000_000
        db.execute("INSERT INTO ai_usage (tenant_id, model, cost) VALUES (?,?,?)",
                   [tenant_id, model, cost])
```

---

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| No `max_tokens` limit | Always set — prevents runaway costs |
| API keys in code/git | Use environment variables only |
| No retry logic | LLM APIs fail ~1–5% of the time — always retry with backoff |
| Awaiting full response before displaying | Stream responses for better UX |
| Using GPT-4o for simple classify tasks | Use DeepSeek V3 — 10× cheaper |
| No token/cost logging | Log every API call — you will need this for billing |
| Sending raw user input to LLM | Validate and sanitise — see `ai-security` skill |

---

*Sources: OpenAI API docs; Anthropic docs; Aremu — DeepSeek AI (2025); Habib — Building Agents with OpenAI Agents SDK (2025)*