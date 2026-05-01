---
name: ios-bluetooth-printing
description: CoreBluetooth integration for ESC/POS thermal printer communication on
  iOS. Covers BLE discovery, pairing, characteristic writing, ESC/POS command translation
  from Android, and receipt formatting. Use when connecting iOS apps to Bluetooth
  thermal...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# iOS Bluetooth Thermal Printing (ESC/POS over BLE)
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- CoreBluetooth integration for ESC/POS thermal printer communication on iOS. Covers BLE discovery, pairing, characteristic writing, ESC/POS command translation from Android, and receipt formatting. Use when connecting iOS apps to Bluetooth thermal...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-bluetooth-printing` or would be better handled by a more specific companion skill.
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
| Correctness | BLE thermal printer test plan | Markdown doc covering pairing, characteristic discovery, write-characteristic, and ESC/POS payload tests | `docs/ios/ble-printer-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
CoreBluetooth-based integration for ESC/POS thermal printers on iOS. Direct translation of Android `BluetoothPrinter.kt` and `EscPosReceipt.kt` patterns into Swift/SwiftUI.

**Stack:** Swift 5.9+ | CoreBluetooth | SwiftUI | ESC/POS byte protocol
**Min iOS:** 16.0 | **Target iOS:** 18.x
**Android Parity:** Receipt output must be byte-identical to `EscPosReceipt.kt`

## When to Use

- Connecting an iOS app to a Bluetooth thermal printer
- Printing receipts, invoices, or labels from an iOS POS or SaaS app
- Porting Android ESC/POS printing to iOS

## When NOT to Use

- AirPrint / network printers (use UIPrintInteractionController)
- USB/serial printers (not BLE)
- PDF generation without physical printing

---

## Additional Guidance

Extended guidance for `ios-bluetooth-printing` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `1. CoreBluetooth Architecture`
- `2. CBCentralManagerDelegate`
- `3. CBPeripheralDelegate`
- `4. ESC/POS Commands (Direct Translation from Android)`
- `5. Receipt Builder (Mirrors Android EscPosReceipt)`
- `6. Printing Data (Chunked BLE Writes)`
- `7. Info.plist Required Keys`
- `8. SwiftUI Integration`
- `9. Example: Full Receipt`
- `10. Common Issues`
- `11. Reconnection`
- `12. Implementation Checklist`
- Additional deep-dive sections continue in the reference file.