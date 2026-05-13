# Eval-Gated Re-Promotion

A rollback is the easy half. Getting back to the new version safely is the hard half. This document specifies the gates that block re-promotion and the flow that runs them.

## Gate Set (default)

Every re-promotion must pass these gates. Feature owners can add gates; they cannot remove these defaults without an AI-leadership exception logged.

### 1. Regression Golden Green

- The exact failing pattern from the incident is encoded as a golden test.
- The new candidate passes it.
- The pinned-but-old version (the current production state) also passes it, demonstrating that the gate is **discriminating** — otherwise it's a green-on-anything gate and worthless.

### 2. Shadow Window Green

- Shadow run for ≥ 24 hours, ≥ 1,000 requests, stratified by tenant tier.
- Pass rate (judge + spot-check) ≥ a per-feature floor (default 96%).
- Per-axis breakdown shows no regression on any axis > 1 pp vs pinned.

### 3. Eval Suite at Parity or Better

- Whole-suite score within 1 pp of pinned.
- No subset regression > 2 pp.

### 4. Cost Neutral

- Tokens-per-request ≤ 10% more than pinned.
- USD-per-request ≤ 10% more than pinned (factor in price tables).
- Or: cost regression accepted explicitly by the feature owner with rationale in the recovery plan.

### 5. Time Since Incident Floor

- Default 48h since incident close.
- 1 week if sev-1 with data implications.
- 2 weeks if a regulator was notified.

### 6. On-Call Coverage Window

- Re-promotion executes only in the primary on-call's business hours.
- Never on Fridays after 14:00 local; never weekends; never holidays without explicit exemption.

### 7. Sign-Off

- Feature owner approval (named).
- AI-lead approval for sev-1 incidents (named).
- Decision logged.

## Optional Gates (per Incident)

- **Tenant smoke test.** For incidents affecting named high-risk tenants, the candidate must pass a tenant-specific smoke test using a sandbox tenant set.
- **Red-team test.** For safety-class incidents, the captured attack must fail (i.e., be refused) against the candidate.
- **Tool contract test.** For tool-incidents, a live contract test against the tool passes.
- **Provider health.** For provider-incidents, the provider's status page is green and a recent eval comparison is acceptable.

## Gate Runner

```python
# tools/gate_runner.py
from dataclasses import dataclass

@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str

def run_gates(incident_id: str, candidate: str, config_path: str) -> list[GateResult]:
    cfg = load(config_path)
    results = []
    for g in cfg["gates"]:
        if g["name"] == "regression_golden_green":
            results.append(check_regression_golden(g, candidate))
        elif g["name"] == "shadow_window_green":
            results.append(check_shadow(g, candidate, incident_id))
        elif g["name"] == "eval_suite_parity":
            results.append(check_eval_suite(g, candidate))
        elif g["name"] == "cost_neutral":
            results.append(check_cost(g, candidate))
        elif g["name"] == "time_floor":
            results.append(check_time_floor(g, incident_id))
        elif g["name"] == "on_call_coverage":
            results.append(check_on_call(g))
        # ... and so on
    return results

def all_passed(results) -> bool:
    return all(r.passed for r in results)
```

The runner is invoked by the release pipeline; it writes results to the recovery plan and to a structured log.

## Re-Promotion Flow

```
1. Recovery plan drafted; gates encoded in YAML.
2. Add regression golden (CI green).
3. Build candidate (new prompt / model / index / tool version).
4. Start shadow run.
5. Wait shadow window ≥ 24h.
6. Run gate-runner.
7. If all green AND business-hours coverage AND time floor met:
     promote to canary (1 internal tenant 24h → 1–3 friendly 1w → 5% tier 1w → tier ramp).
   Any auto-rollback signal during canary → back to gate 4 after fix.
8. Each stage's pass extends the rollout one step.
9. GA reached.
10. Mitigation primitive removed. `ai_*_pin_registry` updated.
11. Incident closed-out comms sent. Recovery decision log entry written.
```

## When to Choose "Make Permanent"

The rollback becomes the new permanent state when:

- The new version cannot be fixed (provider regression with no resolution date).
- The fix is non-trivial and the pinned version is acceptable indefinitely.
- A planned migration replaces the new version entirely.

Make-permanent requires:
- Postmortem decision section documents the choice with rationale.
- `ai_*_pin_registry` row's `permanent: true` flag set.
- `incident_id` reference retained but the row no longer shows on the open-rollback list.
- Re-evaluation scheduled (default 90 days).

## Decision Log

Every re-promotion or make-permanent action writes one entry:

```jsonl
{
  "ts": "2026-05-13T12:14:00Z",
  "actor": "alice@example.com",
  "approvers": ["bob@example.com", "carol@example.com"],
  "incident_id": "inc-1923",
  "decision": "re_promoted",
  "candidate": "prompt-v19",
  "from": "prompt-v17",
  "gates_passed": ["regression_golden_green", "shadow_window_green", "eval_suite_parity", "cost_neutral", "time_floor", "on_call_coverage"],
  "stage_reached": "GA",
  "notes": "Shadow showed parity; tier ramp held; no recurrence of abstain-vs-fabricate axis regression."
}
```

## Anti-Patterns

- Gates exist as a doc; never executed; re-promotion happens on judgment.
- "Time floor" exception granted casually — incidents recur because we re-promoted in 6 hours.
- Shadow ran for 1 hour with 50 requests — confidence is fiction.
- Gates green on the eval that missed the original regression — same blind spot.
- Re-promotion at 16:55 Friday — nobody to respond if it recurs.
- Make-permanent decision implicit — pin sits, undocumented, for months.
