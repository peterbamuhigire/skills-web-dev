# Prompt Injection Threat Model — Reference

A STRIDE-adjacent template for per-feature AI threat modelling.

## Inputs to gather

- Feature name, owner team.
- Inputs accepted (user text? file uploads? URLs? voice?).
- Sources concatenated into the prompt (KB chunks? web pages? tool outputs?).
- Tools the model can call (and what they can do).
- Auth scope when calling — which tenant, which user.
- Output sinks (UI? email? webhook? code execution? DB writes?).

## Threat categories (S-T-R-I-D-E adapted)

### S — Spoofing of instructions

Untrusted text is treated as an instruction. Vectors:
- User input that begins with "Ignore previous...".
- A retrieved chunk that contains "system: do X".
- A scraped webpage with hidden HTML comments.
- A tool response with embedded JSON-mimicking-tool-call structure.

Defences:
- Instruction hierarchy (`SKILL.md` §2).
- Boundary tokens around untrusted sections.
- Input classifier rejects high-signal injections.
- Model is conditioned to treat marked sections as data.

### T — Tampering with outputs

The model is induced to emit output that violates policy or contains exfiltration:
- Base64-encoded secrets.
- Image URLs pointing at attacker server (exfil via image load).
- Markdown links with smuggled query params.

Defences:
- Output filter scans for base64/long hex strings; PII; banned content.
- Render layer disables auto-loading of external images by default.
- Markdown link sanitisation.

### R — Repudiation

Without an audit trail, attribution of an incident is impossible.

Defences:
- AI audit log captures full request + response per `ai-on-saas-architecture` §5.
- Per-tenant signed payloads in storage.
- Retention sufficient to back-track an incident weeks later.

### I — Information disclosure

The model leaks:
- The platform system prompt.
- Another tenant's data (via shared KB bug — `ai-tenant-isolation-patterns`).
- PII the model memorised in fine-tuning.
- Internal IDs that enable IDOR.

Defences:
- Hard separation of system prompt from user-visible response.
- Tenant filter at every storage layer.
- PII redaction in output.
- Fine-tunes audited for memorisation (`ai-tenant-isolation-patterns` §5 test 5).

### D — Denial of service

A user issues queries that:
- Force long-running tool chains.
- Exhaust context.
- Trigger expensive model fallbacks.

Defences:
- Per-tenant token caps (`ai-cost-per-tenant-attribution`).
- Step caps for agents (`ai.agent.max_steps`).
- Tool concurrency caps.
- Gateway rate limiting.

### E — Elevation of privilege

User input causes the agent to call a tool with arguments outside the user's scope:
- `delete_record(id=...)` where id belongs to another user/tenant.
- `email_send(to=...)` where to is outside the tenant's domain.
- `sql(query=...)` where query reads admin tables.

Defences:
- Tool arguments validated against the calling user's scope, not the prompt-stated one.
- Per-tenant tool allow-list.
- Irreversible actions need explicit approval.

## Risk table template

| Threat | Vector | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| Direct injection | user input | high | high | input classifier + hierarchy | platform | implemented |
| Indirect via KB | chunk text | medium | high | chunk sanitisation + boundary | platform | implemented |
| Indirect via tool output | webpage scrape | medium | high | classify tool output before concat | feature | in progress |
| System prompt leak | prompt extraction | medium | medium | output filter + watermark | platform | implemented |
| Tool escalation | argument injection | low | high | per-call scope check | feature | implemented |
| PII memorisation in fine-tune | tuning data | low | high | data sanitisation + memorisation probes | platform | tested |

## Review cadence

- Per feature: at launch and quarterly.
- Triggered review: after any reported safety incident or after an external disclosure.
- Annual: comprehensive review across all features.

## Sign-off

- Feature owner — confirms surface inventory.
- Platform AI security — confirms defence layers.
- Tenant Success — confirms tenant-facing posture (BYOK, enterprise SOC2 mapping).
