---
name: ios-rbac
description: Role-Based Access Control for iOS apps integrating with a multi-tenant
  SaaS backend. Covers permission fetching, Keychain caching, SwiftUI permission gates
  (PermissionGate, ModuleGate), module-gated TabView, navigation guards, offline-capable...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# iOS RBAC - Permission System

<!-- dual-compat-start -->
## Use When

- Role-Based Access Control for iOS apps integrating with a multi-tenant SaaS backend. Covers permission fetching, Keychain caching, SwiftUI permission gates (PermissionGate, ModuleGate), module-gated TabView, navigation guards, offline-capable...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-rbac` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Architecture Overview

Mobile RBAC uses a **hybrid client+server** approach:

1. **Backend enforces** - Every API call checked by PermissionMiddleware (returns 403 if denied)
2. **Client gates UI** - Cached permissions control button/tab/screen visibility for UX
3. **Fail-secure** - If permissions unknown, deny access (never grant)
4. **Offline-capable** - Cached permissions work without network

**Backend Environments:** Dev (Windows/MySQL 8.4.7), Staging (Ubuntu/MySQL 8.x), Production (Debian/MySQL 8.x). Permission APIs must behave identically across all environments. Use Xcode build configurations and schemes for environment-specific base URLs.

```
Login → Fetch Permissions → Cache in Keychain → UI Gates
         ↕ (refresh)                              ↕ (403 fallback)
     Backend always enforces ←────────────────────┘
```

## Core Principles

### 1. Two-Layer Gating

| Layer               | What It Controls | When Hidden/Disabled                  |
| ------------------- | ---------------- | ------------------------------------- |
| **Module Gate**     | TabView tabs     | Franchise hasn't subscribed to module |
| **Permission Gate** | Views, buttons   | User's role lacks the permission      |

**Rule:** Modules HIDE tabs entirely. Permissions DISABLE or HIDE individual actions.

### 2. Permission Resolution (Backend)

Backend resolves permissions using 5-tier priority: User Denial → User Grant → Franchise Override → Role Permission → Super Admin/Owner. The iOS client **never resolves permissions locally**. It receives the resolved set from `GET /user/permissions` and uses it as-is.

### 3. Storage: Keychain Services

Permissions are a flat set of ~20-50 string codes. Stored securely in the Keychain.

```
"user_permissions"    → Set<String> {"POS_CREATE_SALE", "DASHBOARD_VIEW", ...}
"user_modules"        → Set<String> {"POS", "INVENTORY", ...}
"user_roles"          → Set<String> {"CASHIER", ...}
"user_type"           → String "staff"
"permissions_updated" → TimeInterval (epoch seconds)
```

**Never use UserDefaults for permissions.** Keychain data survives app reinstalls and is encrypted at rest by the OS.

### 4. Refresh Strategy

| Trigger              | Action                        |
| -------------------- | ----------------------------- |
| After login          | Fetch immediately             |
| App startup (cold)   | Fetch if > 15 min stale       |
| App foreground (warm) | Fetch if > 15 min stale      |
| 403 from backend     | Fetch immediately, then retry |
| Pull-to-refresh      | Fetch immediately             |

Use `ScenePhase` to detect app foreground transitions for staleness checks.

### 5. Offline Behaviour

- Use cached permissions (last known good)
- If no cache exists (fresh install), deny all
- Never allow more access offline than last sync granted

## Additional Guidance

Extended guidance for `ios-rbac` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `PermissionManager (@Observable)`
- `UI Patterns`
- `App Lifecycle Integration`
- `403 Auto-Refresh`
- `Keychain Helper`
- `UX Guidelines`
- `Security Rules`
- `Integration with Other Skills`
- `Anti-Patterns`
- `Implementation Checklist`
