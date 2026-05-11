---
name: ai-incident-evidence-capture
description: Use when defining what evidence must be captured during an AI incident — at the moment of the incident, before state changes — for postmortem reconstruction and regulator submission. Specifies the evidence bundle (trace bundle, prompt+model+tool versions, retrieval set, eval-suite output at time of incident, customer-affected list, action audit log, reproduce script, price-table snapshot), chain-of-custody, redaction, retention, and the one-command exporter.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Incident Evidence Capture
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building the evidence-capture pipeline for AI incidents in a multi-tenant SaaS.
- Responding to an AI incident — calling the exporter to freeze state at T+5.
- Preparing regulator submission (EU AI Act serious-incident report, GDPR breach, sector regulator).
- Producing the evidence pack for a postmortem.

## Do Not Use When

- The task is generic platform forensics — use SOC2 incident-response procedures.
- The task is the trace schema — `ai-observability-and-debugging`.
- The task is the audit log spine — `saas-control-plane-engineering`.

## Required Inputs

- AI trace schema (`ai-observability-and-debugging`).
- AI audit log (`ai-on-saas-architecture`).
- Eval harness output history (`ai-eval-harness`).
- Cost pipeline (`ai-cost-per-tenant-attribution`).
- Action audit log for agents (`ai-agents-tools`).
- Storage tier for evidence bundles (object storage with object-lock).

## Workflow

1. Read this `SKILL.md`.
2. Define the **evidence bundle spec** (§1) — exactly what's in it.
3. Build the **one-command exporter** (§2) — `ai-evidence-export`.
4. Define **chain-of-custody** (§3) — who can read, where it lives, how it's signed.
5. Build the **reproduce-script generator** (§4) — from a trace, generate a runnable script.
6. Define **redaction and retention** (§5).
7. Apply anti-patterns (§6).

## Quality Standards

- Evidence bundle export runs in < 5 minutes for any AI incident.
- The bundle is captured **at T+5** of the incident — before mitigations change state.
- Bundle is content-addressed and signed; chain-of-custody is verifiable.
- A reproduce script is generated for at least 10 representative failing requests.
- Bundle is retained per the longest applicable clock (regulatory window, customer contract, internal policy).
- Redaction is by policy, not by responder discretion: PII is masked before the bundle leaves the production boundary, except for an "evidence-vault" copy held under strict access control.

## Anti-Patterns

- Evidence captured after the incident, when state has changed and traces have aged out.
- Bundle is "whatever the on-call thought to grab" — unstructured, incomplete, unreproducible.
- Bundle stored in Slack DMs or engineering laptops. Not legally defensible.
- No redaction — leaks customer PII into the evidence vault and into the postmortem.
- Reproduce script calls live providers — distorts cost, rate-limits, replays the bug into production again.
- Retention shorter than regulatory window — evidence destroyed before the regulator requests it.

## Outputs

- Evidence bundle specification.
- `ai-evidence-export` CLI/service.
- Chain-of-custody policy.
- Reproduce-script generator.
- Redaction + retention policy.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Compliance | Evidence bundle | tar.gz + manifest.json + signature | `evidence/inc-1923/bundle.tar.gz` |
| Compliance | Chain-of-custody log | append-only | `evidence/inc-1923/custody.log` |
| Operability | Reproduce script | Python | `evidence/inc-1923/reproduce_<request_id>.py` |
| Compliance | Retention policy | YAML | `ops/ai/evidence-retention.yaml` |

## References

- `references/evidence-bundle-spec.md` — full bundle contents and manifest schema.
- `references/chain-of-custody.md` — access control, signing, audit, legal hold.
- `references/reproduce-script-template.md` — generator pattern and an example.
- Companion: `ai-observability-and-debugging`, `ai-on-saas-architecture`, `ai-eval-harness`, `ai-agents-tools`, `ai-incident-response-runbook`, `ai-incident-customer-comms`, `saas-control-plane-engineering`.

<!-- dual-compat-end -->

## §1 Evidence Bundle Spec (Summary)

A bundle is one tar.gz with a manifest. Required entries:

- `manifest.json` — incident id, severity, failure class, window, time of export, exporter version, sha256 of every file.
- `traces/` — exported trace records (OTel JSON) for representative failing requests (10–50).
- `prompts/` — exact prompt versions resolved at request time, including system message, developer messages, retrieved context.
- `models/` — model id + provider + version + region per request.
- `tools/` — agent tool calls (request + response), per request.
- `retrieval/` — retrieval set per request (chunk ids, scores, source documents) and the active index snapshot id.
- `eval/` — eval suite output for the affected feature for the day of incident + last 7 days.
- `affected.json` — list of affected tenants, request count, severity per tenant.
- `audit/` — AI audit log for the window.
- `agent_actions/` — action audit log for the window (if agent-class incident).
- `prices/` — provider price-table snapshot at incident time.
- `mitigations/` — `ai_incident_mitigation_log` entries (what was flipped, when, by whom).
- `reproduce/` — reproduce scripts.
- `signature.txt` — detached signature over manifest.json.

See `references/evidence-bundle-spec.md` for the full schema.

## §2 One-Command Exporter

The exporter is a CLI and a service endpoint:

```sh
ai-evidence-export \
  --incident-id inc-1923 \
  --signal hallucination_burn_rate_5x \
  --feature support-copilot \
  --window-start 2026-05-11T14:00:00Z \
  --window-end   2026-05-11T15:00:00Z \
  --sample-size 50 \
  --tenant-filter all \
  --output /incidents/inc-1923/
```

Behaviour:
- Snapshots all referenced state objects (index version, prompt registry, model pin) **as of window-end**.
- Pulls traces, audit, eval, prices, mitigations into the bundle.
- Generates reproduce scripts for the sample.
- Computes manifest with sha256s.
- Signs the manifest with the production evidence key (HSM-backed).
- Uploads to the evidence vault (object-lock S3 / Cloud Storage with retention).
- Returns the bundle URL and a one-line summary.

Implementation sketch:

```python
# tools/ai_evidence_export.py
def export_bundle(incident_id: str, signal: str, feature: str,
                  window_start: datetime, window_end: datetime,
                  sample_size: int = 50, tenant_filter: str = "all",
                  output_dir: Path = Path("./out")) -> Path:
    bundle = Bundle(incident_id)

    # 1. Snapshot state-at-window-end (immutable references)
    bundle.add("snapshots/prompts.json", PromptRegistry.snapshot(window_end))
    bundle.add("snapshots/models.json", ModelPinRegistry.snapshot(window_end))
    bundle.add("snapshots/index.json", RetrievalIndex.snapshot(window_end, feature))
    bundle.add("snapshots/prices.json", PriceTable.snapshot(window_end))
    bundle.add("snapshots/eval.json", EvalHarness.results(feature, window_end - timedelta(days=7), window_end))

    # 2. Pull traces — sample failing requests
    failing = TraceStore.query(feature=feature, signal=signal,
                                start=window_start, end=window_end,
                                limit=sample_size)
    for t in failing:
        bundle.add(f"traces/{t.request_id}.json", t.to_otel())
        bundle.add(f"prompts/{t.request_id}.json", t.resolved_prompt())
        bundle.add(f"models/{t.request_id}.json", t.model_metadata())
        bundle.add(f"tools/{t.request_id}.json", t.tool_calls())
        bundle.add(f"retrieval/{t.request_id}.json", t.retrieval_set())
        # Reproduce script (uses mock provider, not live)
        bundle.add(f"reproduce/{t.request_id}.py", generate_reproduce_script(t))

    # 3. Audit + actions
    bundle.add("audit/window.jsonl", AuditLog.query(window_start, window_end))
    if feature_has_agents(feature):
        bundle.add("agent_actions/window.jsonl",
                   AgentActionLog.query(feature, window_start, window_end))

    # 4. Affected tenant list
    bundle.add("affected.json", compute_affected_tenants(feature, window_start, window_end))

    # 5. Mitigation log (so far)
    bundle.add("mitigations/window.jsonl",
               MitigationLog.query(incident_id))

    # 6. Manifest + signature
    bundle.add("manifest.json", bundle.build_manifest(
        incident_id=incident_id, signal=signal, feature=feature,
        window=(window_start, window_end), exporter_version=__version__))
    bundle.sign(EvidenceKey.production())

    # 7. Persist to evidence vault with object-lock retention
    return EvidenceVault.upload(bundle, retention_years=7)
```

## §3 Chain of Custody (Summary)

- Bundle written to object-lock storage; retention set per policy (7 years default; 10 years for high-risk-AI features under EU AI Act).
- Bundle is signed at creation; signature stored alongside.
- Access requires a custody event: who read it, when, why, approved by whom. Append-only log per bundle (`custody.log`).
- Legal hold: a flag prevents deletion regardless of retention timer.
- Redaction policy applied **inside** the bundle for plain readers; an unredacted version exists in the evidence vault under stricter ACL.

See `references/chain-of-custody.md`.

## §4 Reproduce-Script Generator

Each failing request gets a Python script that re-runs the exact request offline, using a mock provider that replays the recorded response. This makes the bug reproducible during the postmortem without re-hitting production providers (cost, rate-limit, side effects) and without making the failure recurrent for customers.

```python
# evidence/inc-1923/reproduce_req_abc.py — auto-generated
from ai_replay import MockProvider, Replay

REPLAY = Replay.from_file("traces/req_abc.json")
provider = MockProvider.from_replay(REPLAY)

prompt = REPLAY.resolved_prompt()
context = REPLAY.retrieval_set()
result = provider.chat(model=REPLAY.model_id, messages=prompt, context=context)

print("Expected (recorded):", REPLAY.output)
print("Got:                 ", result.output)
assert result.output == REPLAY.output, "Replay drift — provider non-determinism or schema change."
```

The script is part of the bundle and is used both in the postmortem and as the seed for a regression golden.

See `references/reproduce-script-template.md`.

## §5 Redaction and Retention

- PII in prompts and outputs: masked (`<email>`, `<phone>`, `<name>`) in the standard bundle.
- An unredacted "vault" version exists for regulator submission; access requires legal approval.
- Tenant data classes treated per the data classification: any data class with redaction policy applies.
- Retention: default 7 years; high-risk AI features 10 years; legal hold overrides.

## §6 Anti-Patterns

- "Just download the traces" — without a manifest, without snapshots of mutable state, without a signature.
- Bundle has prompts but not the *resolved* prompt at request time — different prompt registry state today vs the incident.
- Reproduce script hits live providers — re-triggers the bug, distorts metrics.
- No retention policy — evidence destroyed in the routine 30-day cleanup before postmortem completes.
- Redaction is "responder removed what they thought was PII" — inconsistent, sometimes too much, sometimes too little.
- Unredacted vault accessible to every engineer — privacy violation by way of incident response.
