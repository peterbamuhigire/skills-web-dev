# TODO: macos-app-sandbox-security Skill

## Purpose

Create a skill for macOS sandboxing, hardened runtime, entitlements, Keychain, notarization, and secure local-file access.

## Why GlassHub Needs It

- GlassHub must access user-selected repositories safely.
- GitHub tokens must live only in Keychain.
- Direct-download builds need hardened runtime and notarization.
- App Store builds need strict entitlement discipline.

## Study Before Writing

- Apple App Sandbox guide.
- Security-scoped bookmarks.
- Keychain Services.
- Hardened Runtime and notarization docs.
- App Store Review privacy and file-access guidance.

## Skill Should Cover

- Security-scoped bookmark lifecycle.
- User-selected file read/write entitlements.
- Keychain item grouping and deletion.
- Hardened runtime options.
- Notarization pipeline.
- Privacy and diagnostics rules for local repository apps.

## Starter Evidence To Collect

- Security-scoped bookmark sample.
- Keychain token storage sample.
- Entitlement review checklist.
