# Evidence Chain of Custody

A bundle's evidence value depends on the chain of custody. This document defines who can do what to a bundle and how every interaction is recorded.

## Storage

- Object-lock storage (S3 Object Lock, GCS Bucket Lock, equivalent).
- Retention default 7 years; 10 years for high-risk-AI features under EU AI Act; legal-hold flag overrides retention timer.
- Two copies:
  - **Redacted** copy — bundle as documented in `evidence-bundle-spec.md`, with PII masked. Accessible to incident responders, postmortem authors, AI leadership.
  - **Unredacted** copy — full prompts, retrieval, outputs. Accessible only via legal-approval workflow.

## Signing

- Each bundle's `manifest.json` is signed at export time with the **production evidence key** (HSM-backed, rotated annually).
- Signature stored as `signature.txt` next to the bundle.
- Public key chain is in `evidence/keys/` (versioned). A validator can verify the bundle decades from now if the key chain is preserved.

## Access Control

| Role | Redacted bundle | Unredacted bundle | Custody log |
|---|---|---|---|
| AI on-call | read | request only | append-only write |
| Incident commander | read | request only | append-only write |
| Postmortem author | read | request only | append-only write |
| Security on-call | read | read (sev-1 only) | append-only write |
| Legal | read | read | read |
| Privacy officer | read | read | read |
| Engineering staff (general) | no | no | no |
| Customer (their data only) | request only via DSAR | no | DSAR record |

Every read of either copy generates a custody event:

```jsonl
{"ts":"2026-05-12T09:14:22Z","actor":"alice@example.com","action":"read","bundle":"inc-1923","copy":"redacted","reason":"postmortem draft","ticket":"PM-118"}
```

The custody log itself is append-only, replicated, and retained alongside the bundle.

## Legal Hold

- Any incident with: confirmed data exfil; irreversible customer harm; regulator engagement; or contractual notice from a customer enters legal hold automatically.
- Legal hold prevents deletion regardless of retention timer.
- Legal hold is set and cleared only by legal counsel; the action is logged.

## Regulator Submission

When a regulator requests evidence (EU AI Act Art. 73 serious-incident, GDPR DPA inquiry, sector regulator):
1. Legal opens a regulator submission case.
2. The unredacted bundle is copied to a regulator-package location with the submission scope.
3. A submission manifest documents what was sent, when, to whom, by whom, on what authority.
4. The custody log records the submission event.
5. Internal retention extends to the longer of: regulator's stated retention or our default.

## Customer DSAR

Where a customer makes a Data Subject Access Request affecting the bundle:
1. Privacy officer determines what is in scope (customer's own data only).
2. A redacted subset is extracted using the bundle's per-tenant index.
3. Subset is delivered per DSAR policy.
4. Custody log records the DSAR event.

## Validation

Quarterly: pull a random sample of bundles, run `ai-evidence-validate`, verify signatures, verify custody log integrity. Document the audit.

## Anti-Patterns

- Bundles stored on engineering laptops, in tickets, in chat threads.
- Custody log writable by anyone — chain of custody is theatre.
- Unredacted bundles emailed to lawyers — circumvents the vault.
- Retention "best effort" — bundle deleted before regulator window expires.
- Legal hold mechanism doesn't actually block deletion.
- Signing key handled outside HSM, lost when an engineer leaves.
