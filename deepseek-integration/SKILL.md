---
name: deepseek-integration
description: Integrate DeepSeek AI models into apps — DeepSeek V3 (general), R1 (reasoning/CoT),
  API setup (OpenAI-compatible), local deployment with Ollama, distilled model selection,
  cost vs OpenAI comparison, and Python/JavaScript code patterns. Use when...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# DeepSeek Integration

<!-- dual-compat-start -->
## Use When

- Integrate DeepSeek AI models into apps — DeepSeek V3 (general), R1 (reasoning/CoT), API setup (OpenAI-compatible), local deployment with Ollama, distilled model selection, cost vs OpenAI comparison, and Python/JavaScript code patterns. Use when...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `deepseek-integration` or would be better handled by a more specific companion skill.
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
DeepSeek provides high-performance LLMs at a fraction of the cost of OpenAI.
The API is **fully OpenAI-compatible** — swap the base URL and model name, everything else is identical.

---

## Model Selection

| Model | Use Case | Context | Notes |
|---|---|---|---|
| `deepseek-chat` | General chat, code, reasoning | 128K | DeepSeek V3 — fast and cheap |
| `deepseek-reasoner` | Complex reasoning, math, science | 128K | DeepSeek R1 — slow but powerful |
| `deepseek-r1-distill-qwen-32b` | Local/self-hosted reasoning | 128K | Good balance of size vs quality |
| `deepseek-r1-distill-llama-70b` | Local/self-hosted, best quality | 128K | Rivals o1-mini |
| `deepseek-r1-distill-qwen-7b` | Edge/on-device | 128K | Smallest usable reasoning model |

**Quick rule:**
- General tasks → `deepseek-chat` (V3)
- Math, science, complex reasoning → `deepseek-reasoner` (R1)
- Local/private deployment → `deepseek-r1-distill-llama-70b` via Ollama

---

## API Setup — Cloud (api.deepseek.com)

DeepSeek API is OpenAI-compatible. Use the OpenAI SDK with a different base URL.

```bash
pip install openai
export DEEPSEEK_API_KEY="sk-..."
```

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
)

response = client.chat.completions.create(
    model="deepseek-chat",     # or "deepseek-reasoner"
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum entanglement simply."},
    ],
    max_tokens=1024,
    temperature=0.7,
)
print(response.choices[0].message.content)
```

### Streaming

```python
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Write a short story about a robot."}],
    stream=True,
    max_tokens=2048,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### JavaScript/Node.js (OpenAI SDK)

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.DEEPSEEK_API_KEY,
  baseURL: "https://api.deepseek.com/v1",
});

const response = await client.chat.completions.create({
  model: "deepseek-chat",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "What is the capital of Uganda?" },
  ],
  max_tokens: 512,
});
console.log(response.choices[0].message.content);
```

### Function Calling (Tool Use)

Identical to OpenAI tool use syntax:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                },
                "required": ["city"],
            },
        },
    }
]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "What's the weather in Kampala?"}],
    tools=tools,
    tool_choice="auto",
)
```

---

## DeepSeek R1 — Reasoning Model

R1 uses Chain-of-Thought (CoT) internally. It "thinks" before answering, making it ideal for:
- Complex math and science problems
- Multi-step logical reasoning
- Code debugging and generation
- Data analysis

```python
# R1 returns a reasoning_content field alongside the answer
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role": "user", "content": "Solve: If 3x + 7 = 22, what is x?"}
    ],
)

# Access the chain-of-thought reasoning (R1 specific)
reasoning = response.choices[0].message.reasoning_content
answer = response.choices[0].message.content
print(f"Reasoning: {reasoning}")
print(f"Answer: {answer}")
```

**Note:** `reasoning_content` only exists in `deepseek-reasoner` (R1) responses.

---

## Local Deployment with Ollama

Run DeepSeek models locally — fully private, no API costs.

```bash
# Install Ollama (Windows/Mac/Linux)
# https://ollama.ai/download

# Pull a DeepSeek model
ollama pull deepseek-r1:7b        # small, fast
ollama pull deepseek-r1:14b       # balanced
ollama pull deepseek-r1:70b       # best quality (requires 48GB+ RAM)
ollama pull deepseek-v2.5         # V2.5 general model

# Verify
ollama list
ollama run deepseek-r1:7b "Explain machine learning in one sentence"
```

### Use Ollama via OpenAI SDK

```python
# Ollama exposes an OpenAI-compatible endpoint at localhost:11434
client = OpenAI(
    api_key="ollama",              # any non-empty string
    base_url="http://localhost:11434/v1",
)

response = client.chat.completions.create(
    model="deepseek-r1:7b",       # match the ollama pull name
    messages=[{"role": "user", "content": "What is 17 × 19?"}],
)
print(response.choices[0].message.content)
```

### Ollama in Node.js

```javascript
const client = new OpenAI({
  apiKey: "ollama",
  baseURL: "http://localhost:11434/v1",
});

const response = await client.chat.completions.create({
  model: "deepseek-r1:7b",
  messages: [{ role: "user", content: "Summarise this text: ..." }],
});
```

---

## Cost Comparison

DeepSeek V3 API is dramatically cheaper than OpenAI:

| Provider | Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|---|
| DeepSeek | V3 (deepseek-chat) | ~$0.27 | ~$1.10 |
| DeepSeek | R1 (deepseek-reasoner) | ~$0.55 | ~$2.19 |
| OpenAI | GPT-4o | ~$2.50 | ~$10.00 |
| OpenAI | o1 | ~$15.00 | ~$60.00 |
| Anthropic | Claude Sonnet 4.6 | ~$3.00 | ~$15.00 |

**DeepSeek V3 is ~10× cheaper than GPT-4o for equivalent tasks.**

Training cost: DeepSeek R1 was trained for $5.58M vs OpenAI's estimated $6B+.

---

## Provider Abstraction (Use DeepSeek + OpenAI Interchangeably)

```python
import os
from openai import OpenAI

def get_client(provider: str = "deepseek") -> tuple[OpenAI, str]:
    if provider == "deepseek":
        return OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com/v1",
        ), "deepseek-chat"
    elif provider == "openai":
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"]), "gpt-4o"
    elif provider == "ollama":
        return OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
        ), "deepseek-r1:7b"
    raise ValueError(f"Unknown provider: {provider}")

def chat(message: str, provider: str = "deepseek") -> str:
    client, model = get_client(provider)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
        max_tokens=1024,
    )
    return response.choices[0].message.content
```

---

## In Next.js / Vercel AI SDK

```typescript
import { createOpenAI } from "@ai-sdk/openai";
import { streamText } from "ai";

const deepseek = createOpenAI({
  apiKey: process.env.DEEPSEEK_API_KEY!,
  baseURL: "https://api.deepseek.com/v1",
});

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = await streamText({
    model: deepseek("deepseek-chat"),    // or "deepseek-reasoner"
    messages,
    maxTokens: 2048,
  });
  return result.toDataStreamResponse();
}
```

---

## DeepSeek V3 Architecture Notes

- **Mixture of Experts (MoE)** — 671B total parameters, only 37B activated per forward pass
- **128K context window** — handles long documents and conversations
- **OpenAI-compatible API** — drop-in replacement for any OpenAI code
- **MIT License for R1** — free for commercial use and modification
- **Distilled models** — smaller versions (1.5B–70B) that preserve R1 reasoning quality

---

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Using R1 for simple tasks | Use V3 (`deepseek-chat`) for general tasks — R1 is slower and pricier |
| Hardcoding DeepSeek API key | Use environment variables |
| Not handling rate limits | DeepSeek has lower rate limits than OpenAI — add retry with backoff |
| Expecting `reasoning_content` from V3 | Only R1 (`deepseek-reasoner`) returns chain-of-thought reasoning |
| Running 70B model on inadequate hardware | Check VRAM: 7B needs 6GB, 70B needs 48GB+ |

---

*Sources: Aremu — DeepSeek AI from Beginner to Paid Professional (2025); Chakraborty — DeepSeek AI: A Comprehensive Guide (2025); Kits For Life — Mastering DeepSeek-v3 (2025)*
