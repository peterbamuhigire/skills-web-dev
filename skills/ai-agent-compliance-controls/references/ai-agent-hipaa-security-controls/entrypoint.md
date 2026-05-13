> Consolidated from skills/ai-agent-hipaa-security-controls/SKILL.md into ai-agent-compliance-controls on 2026-05-13. Load this through skills/ai-agent-compliance-controls/SKILL.md, not as an active skill entrypoint.

# AI Agent HIPAA Security Controls
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Implementing HIPAA Security Rule controls (45 CFR §§ 164.306–.318) for agents that touch ePHI in any way.
- Deciding whether a given agent feature can touch ePHI at all, and if so, in what mode (admin-only / read-only / write-with-approval).
- Choosing an LLM provider for an agent in PHI scope — BAA requirement, data residency, retention zero-retention setting, model training opt-out.
- Wiring access controls (164.312(a)), audit controls (164.312(b)), integrity (164.312(c)), transmission security (164.312(e)) for agents.
- Wiring contingency planning (164.308(a)(7)) for the agent runtime in a healthcare deployment.
- Wiring the breach notification path (164.404–.414) for PHI exposed by an agent.

## Do Not Use When

- The task is the **HIPAA Risk Analysis** document — that is the SRS engine.
- The task is the platform-wide HIPAA program — general healthcare security skills.
- The task is the HIPAA Privacy Rule (Part 164 Subpart E) — different scope, handled by clinical workflow design.
- The task is SOC 2 / ISO 27001 — companion skills.

## Required Inputs

- The agent feature catalogue with PHI scope per feature (does this agent ever see ePHI? write ePHI? transmit ePHI?).
- The SRS engine's HIPAA Risk Analysis (which threats apply, which safeguards mitigate).
- The chosen LLM providers and their BAA status / zero-retention configuration / training opt-out.
- The tenant model (is this a B2B2C health SaaS where each customer is a Covered Entity? a B2B platform serving Business Associates?).
- The Covered Entity vs Business Associate role classification (are we a BA, BAA-subprocessor, or both?).

## Workflow

1. Read this `SKILL.md`.
2. Classify the agent's **PHI scope** (§1): no-PHI / metadata-only / read-PHI / write-PHI / transmit-PHI. Constrain accordingly.
3. Apply the **admin-only constraint** for clinical agents (§2). PHI-writing clinical decisions remain human-led; agents draft only.
4. Decide the **LLM provider BAA path** (§3). See `references/baa-implications.md`. Without a BAA, the provider cannot see PHI.
5. Implement **technical safeguards** (§4) per 164.312: access control, audit control, integrity, transmission security.
6. Implement **administrative safeguards** (§5) per 164.308: workforce training on agent PHI handling, access management, incident procedures, contingency.
7. Wire **breach detection and notification** (§6) per 164.404–.414. Agent-PHI breach is a sub-class of breach.
8. Build the **evidence pipeline** (§7) for each safeguard.
9. Apply anti-patterns (§8).

## Quality Standards

- An agent in PHI scope without a BAA-covered LLM provider is **disabled**. The runtime refuses to register tools for that agent until BAA is confirmed.
- PHI never enters logs or traces in plaintext. Redaction is at the gateway before persistence.
- Action audit log captures every PHI access (164.312(b) audit controls); query log retention ≥ 6 years.
- Clinical decision-support agents are admin-only: they never act on PHI without a clinician's confirmed approval in the action audit log.
- Memory of PHI is constrained — short-term only, scoped to the encounter, purged by retention class within 24h of session end (unless an explicit clinical retention reason is recorded).
- A breach involving agent-handled PHI is detected within 24h and notified per the regulatory clock.

## Anti-Patterns

- Sending PHI to an LLM provider without a BAA "because the prototype is just for testing". Civil penalty exposure.
- LLM provider with a BAA but training opt-out not configured. PHI may train future models.
- Agent that writes a clinical decision (diagnosis, dose, referral) directly to the EHR without a human-in-the-loop approval. Practice-of-medicine and HIPAA exposure.
- Action audit log not capturing PHI access — 164.312(b) failure.
- PHI in the agent's long-term memory tier. Retention violation by default.
- Agent feature ships in the same release as the BAA review — release without BAA assumed in place.
- "We'll get the BAA later" — the provider already saw production PHI.

## Outputs

- PHI scope classification per agent feature.
- Admin-only enforcement code path.
- LLM provider BAA register; provider-config-as-code (zero-retention, training opt-out).
- HIPAA technical safeguards implementation.
- Administrative safeguards procedures.
- Breach detection + notification path.
- Evidence pipeline per safeguard.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Compliance | PHI scope register | DB + monthly export | `evidence/hipaa/phi-scope-YYYY-MM.csv` |
| Compliance | BAA register + provider config | DB + monthly export | `evidence/hipaa/baa-register-YYYY-MM.csv` |
| Compliance | PHI access log (audit controls 164.312(b)) | Hash-chained log | `evidence/hipaa/phi-access-YYYY-MM.jsonl` |
| Compliance | Workforce training records (164.308(a)(5)) | Records | `evidence/hipaa/training-YYYY-MM.csv` |
| Compliance | Breach incident records | Records | `evidence/hipaa/breach-YYYY-MM.csv` |

## References

- `references/security-rule-mapping.md` — §164.306–.318 → agent implementation table.
- `references/phi-agent-constraints.md` — Admin-only constraint, BAA-scoped tool flags, allowed model providers.
- `references/baa-implications.md` — BAA decision tree for LLM providers.
- Companion: `ai-agent-soc2-controls`, `ai-agent-iso27001-controls`, `ai-agent-audit-log-integrity`, `ai-agent-memory-erasure-proof`, `ai-agent-action-approval-and-hitl`, `ai-agent-tool-catalogue-and-action-gating`, `saas-tenant-data-portability-and-erasure`, `healthcare-ui-design`.

<!-- dual-compat-end -->

## §1 PHI Scope Classification

Every agent feature is classified before being allowed near production:

| Scope | Definition | Constraints |
|---|---|---|
| **No-PHI** | Agent never receives, processes, or outputs PHI | Standard agent controls |
| **Metadata-only** | Agent sees PHI metadata (counts, IDs) but no identifying data | PHI metadata fields tagged; classification enforced at tool boundary |
| **Read-PHI** | Agent reads PHI (e.g. summarising a chart) | BAA-covered LLM provider required; audit log every read; PHI never in long-term memory |
| **Write-PHI** | Agent writes PHI (e.g. drafting a note) | All Read-PHI + write requires human-in-the-loop approval; admin-only for clinical |
| **Transmit-PHI** | Agent transmits PHI to another system (referrals, claims) | All Write-PHI + transmission security (TLS, signing); receiver in BA chain |

Stored in the asset register (`agent_assets.phi_scope`). The runtime enforces scope at tool registration time — a tool tagged `read_phi` cannot be registered to an agent whose feature is classified `no_phi`.

## §2 Admin-Only Constraint for Clinical Agents

Clinical decision-making (diagnosis, treatment, prescription, referral) is **practice of medicine**. Agents in clinical scope:

- May draft, summarise, suggest. Never **act** on PHI to make a clinical decision without a clinician approval recorded in the audit log.
- Every write-PHI clinical action requires a `plan_preview` approval with the clinician's identity, time, and rationale recorded (`ai-agent-action-approval-and-hitl`).
- Auto-execute is forbidden for clinical write-PHI. Even reversible writes need approval (because clinical reversals are clinically meaningful).
- The agent's plan_preview shows the clinician: source data, draft action, what cannot be undone clinically.

```python
# runtime/clinical_guard.py
def gate_clinical_action(tool_call: ToolCall, task: AgentTask) -> ToolCall:
    if not tool_call.tool.is_clinical_phi:
        return tool_call
    if not task.clinician_approval_for(tool_call.id):
        raise ClinicalApprovalRequired(
            tool_call=tool_call,
            reason="HIPAA 164.308(a)(4) — admin-only clinical PHI write")
    audit_log.emit(
        event="clinical_write_with_approval",
        clinician=task.approval_for(tool_call.id).clinician_id,
        rationale=task.approval_for(tool_call.id).rationale,
        tool=tool_call.tool.name,
        phi_summary=redact_for_audit(tool_call.args))
    return tool_call
```

## §3 LLM Provider BAA Decision

Without a BAA, the LLM provider cannot see PHI. Period.

Decision tree (full version in `references/baa-implications.md`):

```
Is the agent feature in any PHI scope (Read / Write / Transmit)?
├─ NO → any provider allowed; document the no-PHI declaration
└─ YES → BAA required
   ├─ Provider offers BAA → confirm signed BAA on file, current revision
   │  ├─ Zero-retention available? → ENABLED
   │  └─ Zero-retention NOT available → REQUIRES Risk Analysis decision (default DENY)
   ├─ Provider does NOT offer BAA → BLOCK
   │  └─ Find alternative provider OR descope feature
   └─ Self-hosted model → BAA does not apply to provider; internal controls apply
```

A provider config table enforces this at runtime:

```sql
CREATE TABLE llm_provider_baa (
  provider_id           VARCHAR(64) PRIMARY KEY,
  provider_name         VARCHAR(128) NOT NULL,
  baa_signed            BOOLEAN NOT NULL,
  baa_signed_at         DATE,
  baa_version           VARCHAR(64),
  zero_retention        BOOLEAN NOT NULL,
  training_opt_out      BOOLEAN NOT NULL,
  data_residency        VARCHAR(64),
  allowed_phi_scopes    JSON,                     -- e.g. ["read","write"]
  notes                 TEXT,
  reviewed_at           DATE NOT NULL,
  next_review_due       DATE NOT NULL
);
```

The agent runtime queries this at tool-registration time; mismatch → registration refused.

## §4 Technical Safeguards (164.312)

| Standard | Implementation |
|---|---|
| 164.312(a)(1) Access control — unique user identification | SSO user ID flows from request → agent task → tool call → audit log row |
| 164.312(a)(2)(i) Emergency access procedure | Back-office break-glass with audit + post-incident review |
| 164.312(a)(2)(iii) Automatic logoff | Session timeout enforced at front door; agent task auto-paused on user signout |
| 164.312(a)(2)(iv) Encryption / decryption | TLS in transit; AES-256 at rest; tool args encrypted in audit log |
| **164.312(b) Audit controls** | Hash-chained action audit log; PHI-access events tagged; 6-year retention |
| 164.312(c)(1) Integrity | Audit log hash chain; nightly integrity verification |
| 164.312(c)(2) Mechanism to authenticate ePHI | EHR cross-check of patient ID before write |
| 164.312(d) Person or entity authentication | SSO + MFA on approvers |
| 164.312(e)(1) Transmission security | TLS to all providers; signed payloads for partner-to-partner transmissions |
| 164.312(e)(2)(i) Integrity controls | Receiver signature verification |
| 164.312(e)(2)(ii) Encryption | TLS 1.2+ enforced; cipher suite allow-list |

## §5 Administrative Safeguards (164.308)

| Standard | Implementation |
|---|---|
| 164.308(a)(1) Security management process | HIPAA Risk Analysis (SRS engine) + Risk Management Plan |
| 164.308(a)(2) Assigned security responsibility | Named HIPAA Security Officer in `control-owners.md` |
| 164.308(a)(3) Workforce security | Background screening, agent-handling training |
| 164.308(a)(4) Information access management | Per-tenant tool allow-list + per-tool min-role; PHI scope enforcement |
| **164.308(a)(5) Security awareness and training** | Mandatory training on agent PHI handling for engineers and approvers; completion records |
| 164.308(a)(6) Security incident procedures | AI incident runbook + breach notification path |
| **164.308(a)(7) Contingency plan** | Resumability drill; backup of agent state; data recovery from action audit log replay |
| 164.308(a)(8) Evaluation | Annual HIPAA evaluation via control test suite |
| 164.308(b) Business associate contracts | BAA register; subprocessor list; provider BAA enforcement |

## §6 Breach Detection and Notification (164.404-.414)

A breach is **acquisition, access, use, or disclosure of PHI not permitted by the Privacy Rule that compromises the security or privacy of the PHI**. For agents:

| Trigger | Likely breach class |
|---|---|
| PHI in trace persisted plaintext | Disclosure (internal) |
| PHI sent to LLM provider without BAA | Disclosure (external) |
| Cross-tenant memory leak surfaces PHI to wrong tenant | Disclosure (external) |
| Prompt-injection extracts another patient's PHI | Disclosure (external) |
| Agent emails PHI to wrong recipient | Disclosure (external) |
| Agent writes PHI to wrong chart | Integrity + disclosure |

Detection signals are wired into the AI incident triage tree:

```yaml
# ops/hipaa/breach-signals.yaml
signals:
  - id: cross_tenant_phi_leak
    detector: tenant_isolation_test_fail
    severity: critical
  - id: phi_to_provider_without_baa
    detector: provider_baa_mismatch_at_call_time
    severity: critical
  - id: phi_in_trace_plaintext
    detector: trace_pii_classifier_hit
    severity: high
  - id: agent_phi_to_wrong_recipient
    detector: action_audit_log_recipient_mismatch
    severity: critical
```

Each `critical` signal pages the HIPAA Security Officer; the breach assessment runs within 24h. If a breach is confirmed:

- Affected individuals notified within 60 days (164.404).
- HHS notified within 60 days (more than 500 affected → immediately; less → annually).
- Media notification if more than 500 in a state (164.406).
- Breach evidence pack assembled using the incident evidence exporter, retained 6 years.

## §7 Evidence Pipeline

Per safeguard, a collector pulls evidence on cadence. Codes follow the SOC 2 collector pattern.

```python
# compliance/hipaa/safeguard_164_312_b_audit.py
class HIPAA312BCollector(EvidenceCollector):
    control_id = "164.312(b)"
    name = "Audit controls for PHI access"
    cadence = "0 4 1 * *"            # monthly 1st 04:00
    owner = "hipaa-security-officer@example.com"
    window_days = 30

    def gather(self, start, end):
        from audit_log import ActionAuditLog
        phi_events = ActionAuditLog.query(
            phi_flag=True, start=start, end=end)
        return {
            "phi_access_events.jsonl": phi_events,
            "by_clinician.json": _count_by(phi_events, "actor"),
            "by_tool.json": _count_by(phi_events, "tool"),
            "anomalies.jsonl": ActionAuditLog.anomaly_review(start, end),
            "retention_compliance.json": ActionAuditLog.retention_check("phi", 6 * 365),
        }
```

## §8 Anti-Patterns

- Calling a non-BAA LLM provider in a "PoC" path that uses real PHI. Production breach risk.
- BAA on file but zero-retention not enabled at the provider — PHI lives 30 days at the provider.
- Clinical decision-support that auto-files notes without clinician approval.
- Audit log captures the action but not the PHI scope flag — auditor cannot prove 164.312(b).
- PHI in memory long-term ("agent remembers patient preferences forever"). Retention violation.
- Breach detected but no notification within the 60-day clock.
- Workforce training on HIPAA but not specifically on agent PHI handling — auditor scopes as a finding.


