---
name: ios-security-and-rbac
description: iOS security and authorization orchestration for Keychain, Secure Enclave, privacy, tamper resistance, permissions, RBAC, and tenant-safe mobile access.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Security And RBAC
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Securing an iOS app, reviewing mobile threat models, designing permission gates, protecting secrets, or implementing tenant-aware RBAC.
- The task mentions Keychain, Secure Enclave, Data Protection, ATS, certificate pinning, jailbreak/tamper checks, privacy manifests, roles, permissions, or offline authorization caches.
- A retired iOS security or RBAC skill is referenced by name.

## Do Not Use When

- The task is general iOS implementation with no security, privacy, or authorization impact.
- The task is cross-platform Android-first RBAC; use `mobile-platform-operations` for the absorbed Android/mobile RBAC reference.

## Required Inputs

- Auth model, tenant model, roles/permissions, data sensitivity, offline requirements, API authorization contract, storage choices, and compliance/privacy constraints.

## Workflow

1. Load `ios-development` for baseline implementation standards.
2. Load `vibe-security-skill` for broader product threat modeling when the risk crosses backend, API, or web surfaces.
3. Load `references/ios-app-security.md` for device/app hardening and `references/ios-rbac.md` for permission gates.
4. Verify server-side authorization, local cache expiry, secret storage, privacy disclosure, and test evidence.

## Quality Standards

- Client RBAC must never replace server-side authorization.
- Secrets belong in Keychain or stronger platform storage, not UserDefaults or logs.
- Offline permission caches need expiry, invalidation, auditability, and conservative fallback behaviour.

## Anti-Patterns

- Trusting client-side role flags as the source of truth.
- Logging tokens, PII, Keychain errors, or authorization payloads.
- Adding jailbreak checks without a clear policy for detection, false positives, and support.

## Outputs

- iOS threat model, security checklist, RBAC matrix, permission-gate implementation notes, review findings, or verification evidence.

## References

- `references/ios-app-security.md` for Keychain, Secure Enclave, ATS, pinning, signing, privacy manifests, and tamper resistance.
- `references/ios-rbac.md` for permission models, SwiftUI gates, offline caches, and tenant-safe authorization UX.
<!-- dual-compat-end -->
