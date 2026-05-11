# PHI Agent Constraints — Engineering Reference

This document is the engineering contract for agents that touch PHI. Used by the runtime to refuse registration, by code review to gate prompt/tool changes, and by the auditor to verify control implementation.

---

## 1. PHI Scope Field on Every Agent Feature

`agent_features.phi_scope` is one of:

```python
class PHIScope(str, Enum):
    NO_PHI         = "no_phi"
    METADATA_ONLY  = "metadata_only"
    READ_PHI       = "read_phi"
    WRITE_PHI      = "write_phi"
    TRANSMIT_PHI   = "transmit_phi"
    CLINICAL_WRITE = "clinical_write"   # subset of write_phi with admin-only constraint
```

The classification is reviewed quarterly by the HIPAA Security Officer; changes require a formal change ticket.

## 2. Runtime Refusal at Registration Time

```python
# runtime/agent_registration.py
def register_agent_feature(feature: AgentFeature):
    if feature.phi_scope in (PHIScope.NO_PHI, PHIScope.METADATA_ONLY):
        return _register_no_phi(feature)

    # Any PHI scope: BAA path required
    providers = feature.model_pin.providers()
    for p in providers:
        baa = LLMProviderBAA.get(p.id)
        if not baa or not baa.baa_signed:
            raise RegistrationRefused(
                reason=f"Provider {p.id} has no BAA; cannot register PHI-scoped feature.")
        if not baa.zero_retention:
            raise RegistrationRefused(
                reason=f"Provider {p.id} BAA does not include zero-retention; PHI may persist at provider.")
        if not baa.training_opt_out:
            raise RegistrationRefused(
                reason=f"Provider {p.id} training opt-out not configured.")
        if feature.phi_scope.value not in (baa.allowed_phi_scopes or []):
            raise RegistrationRefused(
                reason=f"Provider {p.id} BAA does not cover scope {feature.phi_scope.value}.")
    return _register_phi(feature)
```

## 3. Tool Registry Metadata

Every tool carries PHI-relevant flags:

```python
@dataclass
class ToolRegistration:
    name: str
    version: str
    reversibility: Reversibility
    # ... existing fields ...
    phi_flag: bool                       # tool reads or writes PHI
    phi_scope_required: PHIScope         # the minimum scope the agent feature must have
    baa_scoped: bool                     # tool calls a BAA-scoped service
    data_classification: DataClass       # internal / confidential / phi / restricted
    transmission_target: str | None      # if external transmission, the target system
```

A tool with `phi_flag=True` cannot be registered to a feature with `phi_scope=NO_PHI`. Enforcement at registry, not in prompt.

## 4. Clinical Write Admin-Only Constraint

Features classified `clinical_write` must:

1. Have **plan_preview** as the only allowed approval pattern (`ai-agent-action-approval-and-hitl` §1).
2. Approver must hold the `clinician_approver` role.
3. Approval row in `agent_approvals` includes `clinician_id` (NPI or equivalent).
4. The agent's plan_preview UI shows the source data (chart fragment), the draft action, and "what is irreversible clinically".
5. Auto-approve / standing approval / undo-window patterns are **forbidden**.

```python
# runtime/clinical_guard.py
def validate_clinical_approval(feature: AgentFeature, approval: AgentApproval):
    if feature.phi_scope != PHIScope.CLINICAL_WRITE:
        return  # not a clinical write
    if approval.pattern != "plan_preview":
        raise ClinicalConstraintViolation("clinical_write requires plan_preview pattern")
    approver = User.get(approval.approver_id)
    if "clinician_approver" not in approver.roles:
        raise ClinicalConstraintViolation("approver lacks clinician_approver role")
    if not approval.metadata.get("clinician_id"):
        raise ClinicalConstraintViolation("approval missing clinician_id (NPI)")
    if approval.metadata.get("rationale", "").strip() == "":
        raise ClinicalConstraintViolation("approval missing clinical rationale")
```

## 5. PHI in Logs / Traces

**Never plaintext.** The trace pipeline runs a PHI redactor before persistence:

```python
# observability/redactor.py
PHI_FIELDS = ("name", "dob", "ssn", "mrn", "address", "phone", "email",
              "insurance_id", "patient_id", "diagnosis", "medication")

def redact_for_trace(payload: dict) -> dict:
    redacted = {}
    for k, v in payload.items():
        if any(p in k.lower() for p in PHI_FIELDS):
            redacted[k] = f"<redacted:{sha256_short(str(v))}>"
        else:
            redacted[k] = v
    return redacted
```

The unredacted version exists only in the action audit log under stricter ACL, encrypted column-level. The evidence vault unredacted copy requires HIPAA Security Officer dual-approval to read.

## 6. PHI in Memory

| Memory tier | PHI eligibility |
|---|---|
| Short-term (turn buffer) | PHI allowed; purged at session end + 24h grace |
| Working (episode) | PHI allowed; purged at task close + 7 days |
| **Long-term (semantic)** | **PHI forbidden unless an explicit clinical retention reason is recorded with a documented retention timer.** |

```python
# memory/phi_gate.py
def gate_long_term_write(row: MemoryRow):
    if not row.tenant_in_phi_scope():
        return  # non-PHI tenant
    if row.contains_phi() and not row.clinical_retention_reason:
        raise MemoryGateRefusal(
            reason="HIPAA: cannot persist PHI to long-term memory without documented clinical retention reason")
```

## 7. PHI Transmission

Tools with `transmission_target` set must:

- Use TLS 1.2+ (cipher allow-list).
- Sign the payload with the platform key.
- Verify the receiver's signature on response.
- Log the transmission to the action audit log with `phi_flag=True`.

The receiver must be on the **partner BAA chain**: the platform has a BAA with the receiver or the receiver is the Covered Entity.

## 8. Workforce Training Requirement

Engineers building agents in PHI scope complete:

1. General HIPAA Security training (annual).
2. **Agent-specific PHI handling training** (annual): the eight constraints above.
3. Sign-off recorded in `evidence/hipaa/training-YYYY-MM.csv`.

Code review for any change in a PHI-scoped agent feature requires at least one reviewer who has completed the agent-specific training within the last 12 months. Enforce in the repository's CODEOWNERS + a CI check.

## 9. Quarterly PHI Scope Review

The HIPAA Security Officer reviews:

- New features added in the quarter with PHI scope.
- Tools registered with `phi_flag=True`.
- BAA register: any expired BAAs, any new providers awaiting BAA.
- Sample of PHI-access events from the action audit log (10 events).
- Training completion gap (engineers missing the agent-specific course).

Review sign-off is the evidence artefact for §164.308(a)(8) annual evaluation, monthly fragment.
