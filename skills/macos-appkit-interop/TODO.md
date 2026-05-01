# TODO: macos-appkit-interop Skill

## Purpose

Create a skill for bridging SwiftUI with AppKit when native macOS app work needs APIs not fully covered by SwiftUI.

## Why GlassHub Needs It

- Diff rendering may need `NSTextStorage`, `NSLayoutManager`, and `NSViewRepresentable`.
- File dialogs, pasteboard behavior, responder chain, menu commands, and window management need AppKit fluency.
- Advanced macOS table/list behavior may require AppKit fallback.

## Study Before Writing

- Apple AppKit documentation.
- SwiftUI `NSViewRepresentable` and `NSViewControllerRepresentable`.
- macOS responder chain and menu command architecture.
- TextKit 1 and TextKit 2 basics.

## Skill Should Cover

- When to stay in SwiftUI versus bridge to AppKit.
- Safe wrapper patterns for AppKit views.
- Coordinator lifecycle, delegate ownership, and memory rules.
- Focus, responder chain, menu validation, and keyboard shortcuts.
- Text rendering and syntax/diff highlighting patterns.
- Testing and preview strategies for bridged views.

## Starter Evidence To Collect

- Working example of a SwiftUI wrapper around an AppKit text view.
- Checklist for AppKit bridge review.
- Anti-patterns: main-thread blocking, retained delegates, and state desync.
