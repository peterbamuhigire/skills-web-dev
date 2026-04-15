# MCP Integration — Servers, Clients, and Tool Exposure

Parent skill: [`ai-web-apps/SKILL.md`](../SKILL.md).

Model Context Protocol (MCP) is the standard way to expose tools to an AI model across applications. This reference covers server authoring, client wiring in a Next.js route, lifecycle, and hardening rules.

## When to use MCP

| Situation | MCP fits? | Why / alternative |
|---|---|---|
| Tools are internal to one app, one model | No | Inline `tools:` in `streamText` is simpler |
| Tools need to be reused across apps or across models | Yes | MCP decouples tool surface from the model client |
| Tools must run out-of-process (different runtime, sandbox) | Yes | stdio transport crosses process boundary |
| Tools require credentials the web process must not hold | Yes | Run MCP server as a separate service account |
| Latency budget under 150 ms per tool call | Reconsider | stdio handshake adds overhead on cold start |

## Server skeleton (stdio transport)

```javascript
// src/stdio/server.js
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const server = new McpServer({ name: 'my-mcp', version: '1.0.0' });

server.tool(
  'get-data',
  'Fetch data from internal API',
  { tenantId: z.string().uuid() },
  async ({ tenantId }) => {
    const data = await fetchInternalData(tenantId);
    return { content: [{ type: 'text', text: JSON.stringify(data) }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

Rules:

- Every tool declares a Zod schema for its parameters.
- The server authenticates against downstream systems using its own credentials, not the end user's token passed through the prompt.
- Tool output is JSON-serialisable and bounded in size (truncate before returning).

## Client in a Next.js route

```typescript
// app/api/chat/route.ts
import { streamText, convertToModelMessages, experimental_createMCPClient } from 'ai';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio';

export async function POST(req: Request) {
  const { messages } = await req.json();
  const transport = new StdioClientTransport({
    command: 'node',
    args: ['src/stdio/server.js'],
  });
  const mcpClient = await experimental_createMCPClient({ transport });
  const tools = await mcpClient.tools();

  const result = streamText({
    model: gemini('gemini-2.5-flash'),
    messages: convertToModelMessages(messages),
    tools,
    onFinish: async () => await mcpClient.close(),
  });
  return result.toUIMessageStreamResponse();
}
```

Rules:

- Always close the client in `onFinish` and on request abort — stdio processes leak otherwise.
- Cache the tool list per worker; re-handshaking on every request is wasteful.
- Treat tool results as untrusted. Re-validate them in the route before acting on privileged effects.

## Tool authority rules

| Authority level | Example | Guard |
|---|---|---|
| Read-only | fetch catalogue, query public data | allow by default |
| Read tenant-scoped | fetch orders for current tenant | require tenant context in every call |
| Write, reversible | draft invoice, stage email | require idempotency key, return preview |
| Write, irreversible | send payment, delete record | require human confirm in UI, not model-driven |

## Observability

Log per MCP call: tool name, caller userId + tenantId, params hash, duration, result size, error. Feed into the same audit sink as the LLM trace so a single request ID joins prompt, tool calls, and cost.
