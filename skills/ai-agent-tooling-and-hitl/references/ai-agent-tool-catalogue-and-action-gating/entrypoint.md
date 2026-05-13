> Consolidated from skills/ai-agent-tool-catalogue-and-action-gating/SKILL.md into ai-agent-tooling-and-hitl on 2026-05-13. Load this through skills/ai-agent-tooling-and-hitl/SKILL.md, not as an active skill entrypoint.

# AI Agent Tool Catalogue and Action Gating
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building the **tool registry** as a control-plane service that agents consume — not as a `tools = [...]` array hard-coded in feature code.
- Adding per-tenant tool allow-lists so an Enterprise tenant can use `create_invoice` but a Free tenant cannot.
- Classifying every tool as **reversible** or **irreversible**, with side-effect budgets per session.
- Pinning a tenant to a specific tool version while you roll out a new one.
- Deprecating a tool without breaking agents that pin it.

## Do Not Use When

- The task is the agent loop / ReAct pattern — `ai-agents-tools`, `ai-agent-runtime-architecture`.
- The task is the action approval UX — `ai-agent-action-approval-and-hitl`.
- The task is the make-it-reversible pattern (dry-run, staged commit) — `ai-agent-reversibility-and-blast-radius`. This skill *classifies* tools; that skill *engineers* the reversibility.
- The task is MCP server design itself — `ai-agents-tools` MCP section. This skill defines what the registry around any tool protocol must hold.

## Required Inputs

- The list of agentic features and what each agent is expected to accomplish.
- The catalogue of internal and external systems the agent can touch (CRM, ERP, email, payments, KB, calendar, ticketing).
- Plan / tier catalogue from `ai-entitlements-and-feature-gating`.
- Audit log baseline from `ai-on-saas-architecture`.

## Workflow

1. Read this `SKILL.md`.
2. Build the **tool registry schema** (§1). One row per tool, fully typed.
3. Classify **reversible vs irreversible** for every tool (§2). See `references/reversible-vs-irreversible-classification.md`.
4. Define **per-tenant allow-lists** (§3) — derived from plan + per-tenant overrides.
5. Define **side-effect budgets** per tool, per session, per tenant (§4). See `references/tool-side-effect-budgets.md`.
6. Wire **tool version pinning + deprecation** (§5).
7. Apply **tool contract conventions** (§6). See `references/tool-schema-conventions.md`.
8. Apply anti-patterns (§7).

## Quality Standards

- One source of truth for tool definitions: the **tool registry service**, not feature-code arrays.
- Every tool has: `name`, `version`, `description_for_model`, `description_for_humans`, `input_schema`, `output_schema`, `reversibility`, `blast_radius`, `side_effect_budget`, `requires_approval`, `min_role`, `min_plan_tier`, `deprecated`, `replaced_by`, `owner`.
- Tool authorisation enforced **inside the tool**, not in the prompt. The prompt is advisory.
- An agent for a given tenant sees only the tools that tenant is allowed to use. The model never sees the existence of a tool the tenant cannot call.
- Side-effect budgets are enforced atomically at the registry boundary, not in the tool body.
- Tool changes ship as **new versions**; old versions remain callable until tenants are migrated.

## Anti-Patterns

- `tools = [...]` array defined in feature code, with one tool that takes `query: string` and runs raw SQL.
- Tools that auto-execute side-effects with no idempotency key.
- Tool description that says "use this to do anything with the database" — the agent will. And shouldn't.
- Tenant-tier check done in the prompt (`if plan is Free, do not call delete_record`). Trivial to jailbreak.
- "Reversibility" not classified — half the tools are wrongly assumed safe.
- Deprecation by deletion. Pinned tenants break overnight.
- Tool returns raw provider response — leaks internal schema and PII into the model context.

## Outputs

- `tool_registry` table schema + sample seed data.
- Reversibility classification per tool.
- Per-tenant allow-list resolution algorithm.
- Side-effect budget table per tool / session / tenant.
- Tool versioning + deprecation policy.
- Tool author contract document.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Tool registry service spec | Markdown | `docs/ai/tool-registry.md` |
| Security | Reversibility classification doc | Markdown / CSV | `docs/ai/tool-reversibility.csv` |
| Release evidence | Per-tool contract tests | CI report | `tests/ai/tools/` |
| Operability | Tool deprecation runbook | Markdown | `docs/runbooks/agent-tool-deprecation.md` |

## References

- `references/tool-schema-conventions.md` — JSON-schema conventions, naming, error contracts.
- `references/reversible-vs-irreversible-classification.md` — classification rubric + examples.
- `references/tool-side-effect-budgets.md` — budget design + enforcement.
- Companion: `ai-agents-tools`, `ai-agent-runtime-architecture`, `ai-agent-action-approval-and-hitl`, `ai-agent-reversibility-and-blast-radius`, `ai-agent-safety-and-red-team`, `ai-entitlements-and-feature-gating`, `ai-on-saas-architecture`.

<!-- dual-compat-end -->

## §1 Tool Registry Schema

```sql
CREATE TABLE tool_registry (
  name                     VARCHAR(128) NOT NULL,
  version                  VARCHAR(32)  NOT NULL,
  description_for_model    TEXT NOT NULL,
  description_for_humans   TEXT NOT NULL,
  input_schema             JSON NOT NULL,
  output_schema            JSON NOT NULL,
  reversibility            ENUM('read_only','reversible','irreversible') NOT NULL,
  blast_radius             ENUM('self','tenant','platform','external') NOT NULL,
  side_effect_budget       JSON NOT NULL,
  requires_approval        BOOLEAN NOT NULL DEFAULT FALSE,
  min_role                 VARCHAR(32),
  min_plan_tier            VARCHAR(32),
  deprecated_at            DATETIME,
  replaced_by              VARCHAR(128),
  owner_team               VARCHAR(64) NOT NULL,
  created_at               DATETIME NOT NULL,
  PRIMARY KEY (name, version)
);
```

The registry is loaded by the agent runtime at task start; the resolved tool list is **pinned on the task row** so a registry update mid-flight doesn't swap tools out from under the agent.

## §2 Reversibility Classification (Three Buckets)

| Bucket | Definition | Approval default | Examples |
|---|---|---|---|
| `read_only` | No state change, no email sent, no external call with side-effect | No approval | search_kb, fetch_dashboard, calculate, get_customer |
| `reversible` | State change exists but can be undone in < 5 min via a documented compensating action | Optional, by feature | create_invoice_draft (delete draft), set_assignment (reassign), tag_record (untag) |
| `irreversible` | Cannot be undone, or undo is costly / customer-visible / regulated | **Always approval** | send_email, charge_card, delete_record, post_to_public_channel, file_government_form |

Full rubric and worked examples in `references/reversible-vs-irreversible-classification.md`.

## §3 Per-Tenant Allow-List

Three layers, resolved in order:

```
effective_tools(tenant) =
    plan_tools(tenant.plan_tier)
  ∪ per_tenant_grants(tenant)
  ∖ per_tenant_denies(tenant)
  ∖ deprecated_tools_after_grace(tenant)
```

The resolved list is cached per tenant (Redis), with a 60-second TTL or invalidated on entitlement change.

```python
def resolve_tools(tenant_id: int) -> list[Tool]:
    tenant = tenants.get(tenant_id)
    plan_tool_names = plan_catalogue[tenant.plan_tier].tools
    grants = tenant_tool_grants.where(tenant_id=tenant_id, expires_at__gt=now())
    denies = tenant_tool_denies.where(tenant_id=tenant_id)
    names = (set(plan_tool_names) | {g.tool_name for g in grants}) - {d.tool_name for d in denies}
    return [tool_registry.get(n, version=tenant.tool_pins.get(n, "latest")) for n in names]
```

The prompt that the LLM sees lists **only** these tools. The model never learns of a tool it cannot call.

## §4 Side-Effect Budgets

Per tool, define:

```yaml
name: send_email
side_effect_budget:
  per_task_max: 5         # one task can send max 5 emails
  per_session_max: 20     # one user session, max 20
  per_tenant_per_hour: 200
  per_tenant_per_day: 2000
```

Atomic check-and-increment in Redis before the tool body runs. On exceed: tool returns `BUDGET_EXCEEDED` to the agent (which the agent treats as a recoverable failure and replans).

Full design in `references/tool-side-effect-budgets.md`.

## §5 Versioning and Deprecation

- Tool versions are **immutable**. A schema change → new version.
- `replaced_by` points to the successor. Old version remains callable for the deprecation window (default: 90 days).
- Tenants can pin to a version via `tenant_tool_pins`. Default pin is "latest non-deprecated".
- Deprecation announcement emits `agent.tool.deprecation_announced` and shows on the admin console.

## §6 Tool Contract Conventions

Naming: `<noun>_<verb>` business-domain names — `invoice_create`, not `db_insert`. See `references/tool-schema-conventions.md`.

Errors: structured, not exceptions. `{ "error": { "code": "NOT_FOUND", "retriable": false, "user_message": "...", "operator_message": "..." } }`.

Pagination: cursor-based. Never `OFFSET` (model loops over pages and explodes context).

Observability: every tool call writes a span with `tool.name`, `tool.version`, `tool.args.hash`, `tool.result.status`, `tool.latency_ms`, `tool.usd_cost`.

## §7 Anti-Patterns

- Generic `db_query(sql)` tool. The agent will write `DROP TABLE`.
- Generic `http_request(url, method, body)` tool exposed to a customer-facing agent. SSRF, exfil, escalation — all enabled.
- Tool description-for-model that lists more than 6 use cases. The model gets confused; tool routing degrades.
- Side-effect budgets only enforced "in the application layer" with no atomic counter. Race conditions allow burst above limit.
- Tool returns the raw provider object. Provider field rename breaks the agent and leaks PII.


