---
name: mobile-platform-operations
description: Cross-platform mobile operations orchestration for app icons, mobile RBAC, SaaS planning, Play Store review, and operational mobile delivery assets.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Mobile Platform Operations
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Planning or reviewing mobile delivery assets that span Android/iOS operations, app packaging, custom icons, RBAC, SaaS companion planning, or Google Play readiness.
- The task references `mobile-custom-icons`, `mobile-rbac`, `mobile-saas-planning`, or `google-play-store-review`.
- A mobile project needs operational documentation, app-store evidence, or cross-platform implementation coordination.

## Do Not Use When

- The task is platform implementation only; use `android-development`, `ios-development`, or `kmp-development`.
- The task is only report UI; use `mobile-reports`.
- The task is iOS-only App Store release; use `ios-quality-and-release`.

## Required Inputs

- Target platforms, app distribution channels, icon/asset constraints, auth/RBAC model, SaaS backend assumptions, release timeline, and store policy obligations.

## Workflow

1. Load platform implementation skills first: `android-development`, `ios-development`, or `kmp-development`.
2. Choose the operations concern: icon assets, mobile RBAC, SaaS planning, or Play Store review.
3. Load only the relevant reference below.
4. Produce the operational artifact, checklist, implementation guidance, or review evidence required for launch.

## Quality Standards

- Operational mobile work must be traceable: asset names, permissions, store evidence, release notes, and backend/API assumptions should be explicit.
- RBAC and SaaS plans must keep backend authority, offline behaviour, and platform UX states clear.
- Store review guidance must include privacy, permissions, policy risk, testing, and rollback notes.

## Anti-Patterns

- Treating store review, icons, and RBAC as last-minute polish.
- Shipping mobile apps without documented backend contracts and offline/error-state expectations.
- Using icon libraries where a project explicitly requires custom PNG assets.

## Outputs

- Mobile operations checklist, app asset manifest, RBAC matrix, SaaS companion app plan, Play Store review checklist, or release evidence.

## References

- `references/mobile-custom-icons.md` for custom PNG icon naming, asset directories, and tracking.
- `references/mobile-rbac.md` for Android/cross-platform permission gates and offline authorization caches.
- `references/mobile-saas-planning.md` for native mobile SaaS planning documents and implementation sequencing.
- `references/google-play-store-review.md` for Android Play Store policy, testing, listing, and submission readiness.
<!-- dual-compat-end -->
