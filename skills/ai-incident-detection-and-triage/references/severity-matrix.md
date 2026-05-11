# AI Severity Matrix

Severity for an AI incident is not the same as severity for a generic SaaS outage. The API can return 200 OK while the product is failing catastrophically (silent hallucination, cross-tenant leak, agent destroying customer state). Severity must be set by **three axes** combined.

## Axes

1. **Signal severity** — what is the signal telling us?
   - `quality_degraded` — measurable degradation but still within product-acceptable bounds.
   - `quality_breached` — SLO breached, error budget burning.
   - `safety_event` — confirmed jailbreak, PII leak, cross-tenant leak, indirect injection action.
   - `cost_runaway` — cost > N× baseline; money bleeding.
   - `outage` — feature returning errors or unavailable.

2. **Tenant scope** — who is affected?
   - `single_tenant`
   - `tenant_tier` (e.g., all Pro)
   - `region`
   - `all_tenants`

3. **Autonomy** — what can the AI do without a human?
   - `suggestion_only` — AI proposes, human accepts every action.
   - `human_approves` — AI executes after explicit approval per action.
   - `agent_acts_reversibly` — AI executes, undo window exists.
   - `agent_acts_irreversibly` — AI executes, no undo.

## Severity Table

| Signal | Scope | Autonomy | Severity |
|---|---|---|---|
| quality_degraded | single | suggestion | sev-4 |
| quality_degraded | tier | suggestion | sev-3 |
| quality_degraded | all | suggestion | sev-3 |
| quality_breached | single | suggestion | sev-3 |
| quality_breached | tier | suggestion | sev-2 |
| quality_breached | all | suggestion | sev-2 |
| quality_breached | any | agent_acts_irreversibly | **sev-1** |
| safety_event (confirmed jailbreak w/ data exfil) | any | any | **sev-1** |
| safety_event (pii_in_output) | tier or all | any | sev-1 |
| safety_event (pii_in_output) | single | any | sev-2 |
| cost_runaway (>10× baseline) | tier or all | any | **sev-1** |
| cost_runaway (>5× baseline) | tier or all | any | sev-2 |
| cost_runaway | single, Free tier | any | sev-4 |
| cost_runaway | single, Enterprise tier | any | sev-3 (could be legitimate) |
| outage | any | any | platform severity matrix |

## Escalation Rules (always)

These raise severity automatically regardless of base row:

- The affected tenant is on the **HIGH_RISK_TENANTS** list (regulated bank, hospital, government). +1 severity.
- The affected feature is on the **HIGH_RISK_FEATURES** list (anything taking irreversible action, anything on the EU AI Act high-risk list). +1 severity.
- Public visibility / press / social-media attention. +1 severity.
- > 1h of failed mitigation attempts. Move to sev-1 regardless.

## Worked Examples

**Example 1.** Support copilot's faithfulness drops from 96% → 90% (SLO is 95%) on the Pro tier; suggestion-only feature.
- Signal: quality_breached
- Scope: tier
- Autonomy: suggestion_only
- Base: sev-2.
- No escalation rules apply. **Result: sev-2.**

**Example 2.** Same as above but the tenant affected is a top-10 financial-services customer flagged HIGH_RISK.
- Base: sev-2.
- HIGH_RISK_TENANTS → +1.
- **Result: sev-1.**

**Example 3.** A new agent feature took an irreversible "delete customer record" action that fell outside the tenant's approved scope, on one tenant.
- Signal: safety_event (action_approval_bypass) — single occurrence threshold.
- Autonomy: agent_acts_irreversibly.
- **Result: sev-1 (always).**

**Example 4.** Cost for one Free-tier tenant spiked 8× because they integrated a noisy webhook.
- Signal: cost_runaway, scope single, Free tier.
- **Result: sev-4. Send the tenant a quota alert, no page.**

**Example 5.** Aggregate cost across the platform is 4× rolling baseline because OpenAI silently doubled the price of a model overnight.
- Signal: cost_runaway, scope all, base 5× threshold not met but anomaly_z5 fired.
- **Result: sev-2. Page ai-platform. Pin all features to the cheaper provider via gateway routing pin while we negotiate.**

## How Severity Maps to Response

| Severity | Time-to-ack | Time-to-classify | Time-to-mitigate target | Comms |
|---|---|---|---|---|
| sev-1 | 5 min | 10 min | 1h (any mitigation, full fix may be longer) | Status page within 15 min; named-tenant DM within 30; regulator within window if applicable |
| sev-2 | 15 min | 30 min | 4h | Status page within 1h |
| sev-3 | 1h | 2h | 24h | Status-page maintenance entry, summary in weekly digest |
| sev-4 | next business day | n/a | best effort | Internal only |

## Anti-Patterns

- Severity decided by escalation pressure, not the matrix.
- One severity per incident lifetime; never revisited as scope changes.
- "Sev-2 unless customer complains" — informal, opaque, unfair.
- No HIGH_RISK_TENANTS list — every escalation is litigated in the moment.
