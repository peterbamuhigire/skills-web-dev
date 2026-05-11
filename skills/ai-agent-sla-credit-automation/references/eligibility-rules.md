# Eligibility Rules — Exclusions Matrix

Every breach passes through eligibility before credit issues. Exclusions are **enumerated** (no "vendor discretion"). Each exclusion class has:
- a rule for *applies-during*,
- a source of evidence,
- a customer-visible disclosure policy.

## Exclusion Classes

### 1. force_majeure

**Applies-during** windows when an external uncontrollable event is registered.

**Evidence:** an entry in `force_majeure_log` posted by an officer (typically VP Engineering or Head of Platform). Each entry has `start_ts`, `end_ts`, `summary`, `external_reference`.

**Customer-visible:** yes. The dashboard shows "Excluded period: <span>" with the summary.

**Examples:** datacentre fire, regional internet outage, sanctions.

```python
class ForceMajeureRule:
    def applies_during(self, start, end, tenant_id):
        return force_majeure_log.overlapping(start, end)
```

### 2. provider_outage_ack

**Applies-during** windows when an upstream LLM/tool provider had a confirmed outage that the platform acknowledged on its own status page.

**Evidence:** a status-page entry from the provider AND an entry on our own status page citing it. Both required — provider status alone doesn't qualify.

**Customer-visible:** yes. Dashboard shows the upstream provider and the status-page links.

```python
class ProviderOutageAckRule:
    def applies_during(self, start, end, tenant_id):
        windows = []
        for upstream in tenants[tenant_id].used_upstream_providers():
            ours = status_page.entries_citing(upstream, start, end)
            for our_entry in ours:
                if our_entry.references_provider_status_url:
                    windows.append(Window(our_entry.start, our_entry.end, label=f'provider:{upstream}'))
        return windows
```

### 3. customer_caused

**Applies-during** windows when the breach is attributable to a tenant action.

**Evidence:** an audit-log row showing a tenant change that materially affected the affected feature (e.g., disabled a required tool, changed an entitlement, hit a self-imposed budget cap).

**Customer-visible:** yes, with the specific change cited. This is a sensitive disclosure; copy must be neutral and factual.

```python
class CustomerCausedRule:
    def applies_during(self, start, end, tenant_id):
        candidates = audit_log.tenant_actions(
            tenant_id, start - timedelta(days=1), end,
            kinds=['tool.entitlement.changed', 'agent.budget.lowered',
                   'sla.exclusion.acknowledged', 'feature.disabled.by.tenant'],
        )
        # Only those whose effect window overlaps the breach window
        return [Window(c.effective_from, c.effective_to or end, label=c.kind)
                for c in candidates if c.materially_affects(self.metric)]
```

### 4. scheduled_maintenance

**Applies-during** windows from the published maintenance calendar.

**Evidence:** an entry in `maintenance_window` published ≥ 7 days in advance for Pro/Business, ≥ 14 days for Enterprise. Maintenance not pre-announced cannot retroactively exclude.

**Customer-visible:** yes. Dashboard cross-references maintenance calendar.

```python
class ScheduledMaintenanceRule:
    REQUIRED_NOTICE = {'class-A': 7, 'class-AA': 7, 'bespoke': 14}
    def applies_during(self, start, end, tenant_id):
        tier = tenants[tenant_id].sla_class
        notice_days = self.REQUIRED_NOTICE.get(tier, 7)
        return [w for w in maintenance_window.overlapping(start, end)
                if w.announced_at <= w.start - timedelta(days=notice_days)]
```

### 5. beta_feature

**Applies-during** if the affected feature was in `beta` for that tenant at the time.

**Evidence:** `feature.flag` history shows the feature in beta for the tenant during the window.

**Customer-visible:** yes — beta features should not have SLA expectations.

```python
class BetaFeatureRule:
    def applies_during(self, start, end, tenant_id):
        flag_history = feature_flags.history(
            tenant_id=tenant_id, feature=self.feature, between=(start, end)
        )
        return [Window(p.start, p.end, label='beta') for p in flag_history if p.beta]
```

### 6. abuse_protection_engaged

**Applies-during** if the tenant was rate-limited or quota-blocked during the window for abuse.

**Evidence:** `abuse_protection_engaged_log` row with `tenant_id`, `start`, `end`, and the matched rule.

**Customer-visible:** yes (with the abuse signal — keeps the tenant honest).

## Application Order

Exclusions apply in this order, accumulating excluded time:

```
force_majeure
provider_outage_ack
customer_caused
scheduled_maintenance
beta_feature
abuse_protection_engaged
```

After excluded periods are removed from the breach window, the metric is **recomputed on the remaining time**. Only if the recomputed metric still breaches does the credit proceed.

```python
def recompute_metric_excluding(breach, excluded_periods):
    # Subtract excluded periods from the window
    sub_windows = subtract_periods(breach.window, excluded_periods)
    if not sub_windows:
        return None        # nothing left; treat as no-breach
    # Re-query the underlying counter over remaining time
    return counter_query.run_over(breach.metric, breach.tenant_id, sub_windows)
```

If the excluded periods amount to > 60% of the original window, treat as `no-breach (de-facto)` and surface a special banner to the customer explaining why.

## Disclosure UX

Customers always see, in the SLA dashboard:

```
Resolution rate (last 30 days): 87% — meets your SLA floor of 85%.

Excluded periods this window:
  • 2026-05-04 09:00–11:00 UTC — provider outage (anthropic-status-page-2026-05-04)
  • 2026-05-08 22:00–23:00 UTC — scheduled maintenance (notice posted 2026-05-01)

Adjusted rate (excluding above): 89%.
```

This is non-negotiable. Silent exclusions destroy trust.

## Special Cases

### Partial-Window Exclusion that Lowers Sample Size

If after exclusion the remaining time has < `min_sample_size` tasks, the metric is *indeterminate* for that window, not a breach. The dashboard shows the sample-size note.

### Concurrent Exclusions

If multiple exclusions overlap, the union of their time spans is excluded (not double-counted).

### Bespoke Exclusion Clauses

Enterprise contracts may add (rarely subtract) exclusion classes. They live in `tenant_sla_overrides.exclusions_override` and are evaluated *in addition* to the base set.

## Cap and Stacking Rules

The per-tenant per-period **credit cap** (defined in `ai-agent-sla-and-commitments`) is enforced after exclusion. Once the cap is reached, further breaches are flagged in audit as `cap-reached` but no credit issues.

Irreversible-incident credits sit **above** the cap by default (severe operational signal). This is a deliberate policy choice; document it in the proposal.

## Anti-Patterns

- Exclusions evaluated after credit is issued. Either causes claw-back or accidental over-credit.
- "Customer caused" applied without a specific audit-log citation. Looks like blame-shifting.
- Force-majeure used for an internal incident (e.g., our own deploy regression). That is not force majeure; pay the credit.
- Beta-feature exclusion applied retroactively after GA. Use the historical flag state.
- Exclusion logic only in code, no human-readable disclosure. Customers will dispute.

## Audit and Retention

Every eligibility decision (eligible / ineligible / which exclusions hit) writes to `sla_credit_decisions.excluded_periods` and is retained with the rest of the audit row.
