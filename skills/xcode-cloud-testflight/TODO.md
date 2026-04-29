# TODO: xcode-cloud-testflight Skill

## Purpose

Create a skill for Xcode Cloud, TestFlight, notarized distribution, and release candidate workflows for Apple-platform apps.

## Why GlassHub Needs It

- GlassHub will need beta validation before App Store release.
- CI must build, test, archive, sign, and preserve release evidence.
- Direct-download builds require a parallel notarized path.

## Study Before Writing

- Xcode Cloud workflow configuration.
- TestFlight internal and external testing.
- App Store Connect API basics.
- `xcodebuild archive` and `notarytool`.
- Fastlane for Apple platforms.

## Skill Should Cover

- Branch and release candidate model.
- Archive/export options.
- TestFlight group strategy.
- Notarization and stapling.
- Release evidence and rollback notes.
- Handling secrets and signing credentials in CI.

## Starter Evidence To Collect

- Xcode Cloud workflow checklist.
- TestFlight submission checklist.
- Notarization runbook.
