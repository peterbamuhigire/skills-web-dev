---
name: ios-biometric-login
description: Optional biometric (Face ID/Touch ID) gate on iOS app launch using LocalAuthentication
  framework. Covers BiometricHelper utility, splash screen integration, settings toggle
  with verification, Keychain-backed preference storage, and graceful...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# iOS Biometric Login

<!-- dual-compat-start -->
## Use When

- Optional biometric (Face ID/Touch ID) gate on iOS app launch using LocalAuthentication framework. Covers BiometricHelper utility, splash screen integration, settings toggle with verification, Keychain-backed preference storage, and graceful...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-biometric-login` or would be better handled by a more specific companion skill.
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
| Security | Biometric authentication test plan | Markdown doc covering Face ID / Touch ID success, fallback, lockout, and policy-change scenarios | `docs/ios/biometric-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Add optional Face ID / Touch ID authentication as a gate on app launch. Uses the `LocalAuthentication` framework (`LAContext`). The feature is opt-in: users enable it in Settings, and it triggers on every app launch from the splash screen.

## Overview

**Flow:** App launch → Splash → Check biometric pref → LAContext prompt → Success (Main) or Failure (Login screen).

**Key principles:**
- **Optional, not mandatory** — users choose to enable via a Settings toggle
- **Verify before enabling** — require biometric auth to turn the feature ON (prevents unauthorised enabling)
- **Graceful degradation** — if device has no biometric hardware, hide the toggle entirely
- **Survive logout** — biometric preference persists across logout/re-login (stored in Keychain)
- **No custom UI** — use the system biometric dialog (consistent UX, handles retries)

## Framework

No third-party dependencies. Uses Apple's built-in `LocalAuthentication` framework.

```swift
import LocalAuthentication
```

No CocoaPods, SPM packages, or Cartfile entries needed.

## Additional Guidance

Extended guidance for `ios-biometric-login` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Architecture`
- `Step 1: BiometricHelper (Actor)`
- `Step 2: KeychainHelper for Preference Storage`
- `Step 3: Splash Screen with Biometric Gate`
- `Step 4: Settings Toggle with Verify-Before-Enable`
- `Step 5: Info.plist Configuration`
- `Flow Diagram`
- `Patterns & Anti-Patterns`
- `Edge Cases`
- `Integration with Other Skills`
- `Checklist`
