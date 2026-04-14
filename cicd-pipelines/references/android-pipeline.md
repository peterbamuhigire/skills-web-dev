# Android Pipeline

Gradle build, unit tests, signed Android App Bundle (AAB), and release to Google Play via Fastlane Supply.

## Secrets Required

Store as GitHub environment secrets on the `android` environment:

- `ANDROID_KEYSTORE_BASE64` (base64 of the `.jks` / `.keystore` file)
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`
- `PLAY_SERVICE_ACCOUNT_JSON` (service account with "Release manager" role)

For large teams, store the keystore in a secure vault (Vault or a managed secret store) and fetch it in the build step rather than keeping a base64 blob in GitHub secrets.

## `build.gradle.kts` — Signing Block

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("keystore.jks")
            storePassword = System.getenv("ANDROID_KEYSTORE_PASSWORD")
            keyAlias = System.getenv("ANDROID_KEY_ALIAS")
            keyPassword = System.getenv("ANDROID_KEY_PASSWORD")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

## Fastlane — `fastlane/Fastfile` (Android)

```ruby
default_platform(:android)

platform :android do
  lane :test do
    gradle(task: "testDebugUnitTest")
  end

  lane :beta do
    gradle(
      task: "bundle",
      build_type: "Release"
    )
    upload_to_play_store(
      track: "internal",
      aab: "app/build/outputs/bundle/release/app-release.aab",
      json_key_data: ENV["PLAY_SERVICE_ACCOUNT_JSON"],
      skip_upload_metadata: true,
      skip_upload_changelogs: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )
  end

  lane :release do
    gradle(
      task: "bundle",
      build_type: "Release"
    )
    upload_to_play_store(
      track: "production",
      rollout: "0.1",
      aab: "app/build/outputs/bundle/release/app-release.aab",
      json_key_data: ENV["PLAY_SERVICE_ACCOUNT_JSON"]
    )
  end

  lane :promote do |options|
    upload_to_play_store(
      track_promote_to: "production",
      track: "internal",
      rollout: options[:rollout] || "0.1",
      json_key_data: ENV["PLAY_SERVICE_ACCOUNT_JSON"],
      skip_upload_aab: true,
      skip_upload_metadata: true,
      skip_upload_changelogs: true
    )
  end
end
```

## `.github/workflows/android.yml`

```yaml
name: android

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      lane:
        description: 'Fastlane lane'
        required: true
        default: 'test'
        type: choice
        options: [test, beta, release, promote]

permissions:
  contents: read

jobs:
  android:
    runs-on: ubuntu-24.04
    timeout-minutes: 60
    environment: android
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'

      - uses: gradle/actions/setup-gradle@v4

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.3'
          bundler-cache: true

      - name: Decode keystore
        if: github.event.inputs.lane != 'test'
        env:
          KEYSTORE_B64: ${{ secrets.ANDROID_KEYSTORE_BASE64 }}
        run: |
          echo "$KEYSTORE_B64" | base64 -d > app/keystore.jks

      - name: Run lane
        env:
          ANDROID_KEYSTORE_PASSWORD: ${{ secrets.ANDROID_KEYSTORE_PASSWORD }}
          ANDROID_KEY_ALIAS: ${{ secrets.ANDROID_KEY_ALIAS }}
          ANDROID_KEY_PASSWORD: ${{ secrets.ANDROID_KEY_PASSWORD }}
          PLAY_SERVICE_ACCOUNT_JSON: ${{ secrets.PLAY_SERVICE_ACCOUNT_JSON }}
        run: |
          LANE="${{ github.event.inputs.lane || 'test' }}"
          bundle exec fastlane "$LANE"

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: android-build-${{ github.run_id }}
          path: |
            app/build/outputs/bundle/release/*.aab
            app/build/outputs/apk/release/*.apk
            app/build/outputs/mapping
            fastlane/report.xml
```

## Track Strategy

- `internal` track for every build from `main` → fastest Play review path; visible only to whitelisted testers.
- `alpha` / `beta` tracks for broader internal validation.
- `production` with staged rollout: 1% → 5% → 20% → 50% → 100% over 5–10 days.

Use `fastlane promote` to move a build that already passed `internal` up to `production` without re-uploading the AAB.

## Play Integrity and Mapping

- Upload ProGuard/R8 mapping files with each AAB so Play Console can deobfuscate crash reports.
- Enable Play Integrity API server-side if the app ships any premium feature you want to gate by genuine-device check.

## Rollback (Android)

- In Play Console, halt a staged rollout at any time — existing users stay on the version they have.
- To push users off a bad version, release a new AAB with a higher version code containing the fix.
- Maintain a feature-flag kill switch for new behaviour so regressions can be disabled server-side without a Play submission.

## Common Failures

- `Signing config not found` → keystore file was not decoded or the path is wrong.
- `invalid service account credentials` → JSON is malformed or the service account lacks "Release manager" role in Play Console.
- `versionCode must be greater than` → Play rejects duplicate or lower version codes. Derive from `GITHUB_RUN_NUMBER` or a monotonic timestamp.
- ProGuard strips reflection-heavy code → add rules in `proguard-rules.pro` and test the release build before shipping.
