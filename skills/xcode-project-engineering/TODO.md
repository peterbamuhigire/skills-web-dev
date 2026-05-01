# TODO: xcode-project-engineering Skill

## Purpose

Create a skill for production Xcode project setup, targets, schemes, build settings, xcconfig files, signing, capabilities, and package management.

## Why GlassHub Needs It

- GlassHub needs separate App Store and direct-download build paths.
- Test targets, snapshot tests, and CI schemes must be reliable.
- Sparkle must be excluded from App Store builds.

## Study Before Writing

- Xcode project and workspace structure.
- `.xcodeproj`, schemes, configurations, and `.xcconfig`.
- Swift Package Manager integration.
- Code signing, provisioning, and capabilities.
- Xcode build settings reference.

## Skill Should Cover

- Target and scheme design.
- Build configuration naming and inheritance.
- `.xcconfig` organization.
- Package dependency risk review.
- Entitlements per configuration.
- Command-line `xcodebuild` recipes.

## Starter Evidence To Collect

- Minimal multi-configuration macOS app template.
- Build-settings review checklist.
- App Store/direct-download divergence checklist.
