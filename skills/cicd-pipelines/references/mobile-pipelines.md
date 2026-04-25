# Mobile Pipelines — iOS and Android

Deep-dive reference for iOS and Android CI/CD on GitHub Actions. Pairs with `ios-fastlane-pipeline.md` and `android-pipeline.md` in this directory.

## Runner Choice

- iOS: `macos-14` (Apple Silicon, Xcode 15+). Costs ~10x ubuntu minutes, so keep iOS jobs fast — cache aggressively.
- Android: `ubuntu-24.04` is enough; only use `macos-*` if the build needs the JDK bundled with Xcode.

## iOS CI/CD

### Fastlane setup

1. Code signing: Fastlane `match` stores certificates and provisioning profiles in a private Git repo or S3 bucket, encrypted with a shared passphrase. CI runs `match` in read-only mode.
2. Build: `gym` (a.k.a. `build_app`) archives and exports the `.ipa`.
3. Upload: `pilot` for TestFlight, `deliver` for App Store submission.

Minimal `fastlane/Fastfile`:

```ruby
default_platform(:ios)

platform :ios do
  desc "Build and upload to TestFlight"
  lane :beta do
    setup_ci
    match(type: "appstore", readonly: true)
    gym(
      scheme: "MyApp",
      export_method: "app-store",
      clean: true
    )
    pilot(
      skip_waiting_for_build_processing: true,
      distribute_external: false
    )
  end
end
```

### GitHub Actions job

```yaml
name: ios-release

on:
  push:
    tags: ['v*.*.*']

permissions: { contents: read, id-token: write }

jobs:
  testflight:
    runs-on: macos-14
    env:
      MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
      FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
      APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.ASC_KEY_ID }}
      APP_STORE_CONNECT_API_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
      APP_STORE_CONNECT_API_KEY_CONTENT: ${{ secrets.ASC_PRIVATE_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.3', bundler-cache: true }
      - uses: maxim-lobanov/setup-xcode@v1
        with: { xcode-version: '15.4' }
      - uses: actions/cache@v4
        with:
          path: Pods
          key: pods-${{ hashFiles('**/Podfile.lock') }}
          restore-keys: pods-
      - run: bundle exec pod install --repo-update
      - run: bundle exec fastlane beta
```

### Notes

- Keep `MATCH_PASSWORD` in a repository secret; rotate quarterly.
- Use App Store Connect API key (not username/password) for uploads. 2FA on user accounts breaks CI.
- Run UI tests on a subset of simulators in a separate job; release builds only need unit tests pass.

## Android CI/CD

### Signing the release

- The keystore never lives in the repo. Base64-encode it once locally and store as a GitHub Secret:

```bash
base64 -w 0 release.keystore > release.keystore.b64
```

  Paste the result into `ANDROID_KEYSTORE_BASE64`. Also store `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, and `ANDROID_KEY_PASSWORD`.

- In CI, decode back to a file, wire it into `signingConfigs`, then delete on job teardown.

### GitHub Actions job

```yaml
name: android-release

on:
  push:
    tags: ['v*.*.*']

jobs:
  play-internal:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17', cache: 'gradle' }
      - name: Decode keystore
        run: |
          echo "${{ secrets.ANDROID_KEYSTORE_BASE64 }}" | base64 -d > "$RUNNER_TEMP/release.keystore"
          echo "RELEASE_KEYSTORE=$RUNNER_TEMP/release.keystore" >> "$GITHUB_ENV"
      - run: ./gradlew bundleRelease
        env:
          ANDROID_KEYSTORE_PASSWORD: ${{ secrets.ANDROID_KEYSTORE_PASSWORD }}
          ANDROID_KEY_ALIAS: ${{ secrets.ANDROID_KEY_ALIAS }}
          ANDROID_KEY_PASSWORD: ${{ secrets.ANDROID_KEY_PASSWORD }}
      - uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_SERVICE_ACCOUNT_JSON }}
          packageName: com.example.myapp
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
          status: completed
      - if: always()
        run: rm -f "$RUNNER_TEMP/release.keystore"
```

### Fastlane supply (alternative uploader)

```ruby
platform :android do
  desc "Upload AAB to Play internal track"
  lane :internal do
    supply(
      aab: "app/build/outputs/bundle/release/app-release.aab",
      track: "internal",
      json_key_data: ENV["PLAY_SERVICE_ACCOUNT_JSON"],
      skip_upload_metadata: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )
  end
end
```

### Promotion tracks

- `internal` → `alpha` → `beta` → `production`. Each track has its own staged rollout percentage.
- Use `upload-google-play` `status: draft` for production, then promote via the Play Console once the internal QA pass is signed off. Never upload directly to `production` from CI.

## Shared Mobile Conventions

- Tag-driven releases only. Mobile builds triggered on `push: tags: ['v*.*.*']`. `main` builds produce nothing shippable.
- Version bumps via `fastlane/increment_version_number` (iOS) and a `versionCode` derived from the tag (Android). Never hand-edit version numbers in CI.
- Keep dSYMs (iOS) and mapping.txt (Android) as build artefacts; upload to Sentry/Crashlytics for de-obfuscation. A crash report without symbols is useless.
- Screenshots, metadata, and store listing changes go through `fastlane deliver` / `supply` and are reviewed in PRs just like code.

## Related

- `ios-fastlane-pipeline.md` — TestFlight and App Store release lanes with `match`.
- `android-pipeline.md` — signed AAB + Play Console release via Fastlane `supply`.
- `../SKILL.md` — top-level CI/CD patterns, OIDC, caching, and promotion.
