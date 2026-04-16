---
name: ios-project-setup
description: 'iOS project setup with Xcode: project structure, SPM dependencies, build
  schemes (Dev/Staging/Prod), xcconfig files, Info.plist configuration, code signing,
  provisioning profiles, and deployment preparation. Use when creating a new iOS project
  or...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Project Setup

<!-- dual-compat-start -->
## Use When

- iOS project setup with Xcode: project structure, SPM dependencies, build schemes (Dev/Staging/Prod), xcconfig files, Info.plist configuration, code signing, provisioning profiles, and deployment preparation. Use when creating a new iOS project or...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-project-setup` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Xcode project setup record | Markdown doc covering schemes, xcconfig per environment, Info.plist keys, and SPM dependencies | `docs/ios/project-setup.md` |
| Release evidence | Build configuration record | Markdown doc covering Dev/Staging/Prod scheme settings and signing configuration | `docs/ios/build-config-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
> Xcode project configuration, build schemes, code signing, provisioning,
> and deployment preparation for SwiftUI apps.

## Companion Skills

| Skill | When to Load |
|-------|-------------|
| `android-development` | Cross-platform reference (equivalent Android patterns) |
| `multi-tenant-saas-architecture` | Backend API that the iOS app connects to |
| `vibe-security-skill` | Security baseline for API communication |
| `dual-auth-rbac` | Authentication and role-based access |
| `image-compression` | Client-side image handling before upload |
| `healthcare-ui-design` | Clinical-grade UI when building health apps |

---

## 1. Creating a New Project

**Xcode > File > New > Project > App**

| Setting | Value |
|---------|-------|
| Interface | SwiftUI |
| Language | Swift |
| Storage | SwiftData (if persistence needed) |
| Testing | Include Tests + Include UI Tests |
| Bundle ID | `com.{company}.{appname}` |
| Minimum deployment | iOS 17.0 |

**Bundle ID is permanent.** You cannot change it after shipping to the App Store.
Choose carefully: `com.companyname.appname` (lowercase, no special characters).

### Recommended Directory Structure

```
MyApp/
├── App/
│   ├── MyApp.swift              # @main entry point
│   └── RootView.swift           # Auth routing
├── Core/
│   ├── Network/
│   │   ├── APIClient.swift
│   │   ├── APIEndpoints.swift
│   │   └── NetworkMonitor.swift
│   ├── Auth/
│   │   ├── AuthService.swift
│   │   ├── KeychainHelper.swift
│   │   └── TokenManager.swift
│   ├── Storage/
│   │   └── ModelContainer+App.swift
│   └── Config/
│       └── AppEnvironment.swift
├── Features/
│   ├── Login/
│   ├── Dashboard/
│   ├── Sales/
│   └── Settings/
├── Shared/
│   ├── Components/
│   ├── Extensions/
│   ├── Models/
│   └── Utilities/
├── Resources/
│   ├── Assets.xcassets/
│   ├── Localizable.strings
│   └── Info.plist
├── Config/
│   ├── Dev.xcconfig
│   ├── Staging.xcconfig
│   └── Prod.xcconfig
├── Tests/
│   └── MyAppTests/
└── UITests/
    └── MyAppUITests/
```

---

## Additional Guidance

Extended guidance for `ios-project-setup` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Swift Package Manager Dependencies`
- `3. Build Schemes and xcconfig Files`
- `4. Info.plist Configuration`
- `5. Code Signing`
- `6. Asset Catalog Setup`
- `7. Localisation Setup`
- `8. App Entry Point`
- `9. Development Network`
- `10. Archive and Upload`
- `11. TestFlight`
- `12. New Project Setup Checklist`
- `Anti-Patterns`
