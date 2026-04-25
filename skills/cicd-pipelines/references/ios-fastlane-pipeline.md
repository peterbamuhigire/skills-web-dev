# iOS Fastlane Pipeline

Fastlane lanes for test, TestFlight beta, and App Store release. GitHub Actions drives the lanes. Code signing is managed by Match.

## Secrets Required

Store as GitHub environment secrets on the `ios` environment:

- `APP_STORE_CONNECT_API_KEY_ID`
- `APP_STORE_CONNECT_ISSUER_ID`
- `APP_STORE_CONNECT_API_KEY_BASE64` (base64 of the `.p8` file)
- `MATCH_GIT_URL` (private repo URL for certificates)
- `MATCH_PASSWORD` (decryption password for the Match repo)
- `FASTLANE_USER`, `FASTLANE_PASSWORD` (legacy, only if Match is not used)

Do not store `.p12`, provisioning profiles, or raw certificates as secrets. Match keeps them versioned in a private Git repo encrypted with `MATCH_PASSWORD`.

## `fastlane/Appfile`

```ruby
app_identifier "com.example.app"
apple_id       "ci-apple@example.com"
itc_team_id    "1234567"
team_id        "ABCDE12345"
```

## `fastlane/Matchfile`

```ruby
git_url("git@github.com:my-org/ios-certs.git")
storage_mode("git")
type("development")
app_identifier(["com.example.app"])
readonly(true)
```

## `fastlane/Fastfile`

```ruby
default_platform(:ios)

platform :ios do
  before_all do
    setup_ci if ENV['CI']
  end

  lane :test do
    run_tests(
      scheme: "App",
      device: "iPhone 15 Pro",
      code_coverage: true
    )
  end

  lane :beta do
    api_key = app_store_connect_api_key(
      key_id:      ENV["APP_STORE_CONNECT_API_KEY_ID"],
      issuer_id:   ENV["APP_STORE_CONNECT_ISSUER_ID"],
      key_content: ENV["APP_STORE_CONNECT_API_KEY_BASE64"],
      is_key_content_base64: true
    )

    match(type: "appstore", readonly: true)

    increment_build_number(
      build_number: Time.now.to_i.to_s,
      xcodeproj: "App.xcodeproj"
    )

    build_app(
      scheme: "App",
      export_method: "app-store",
      output_directory: "build"
    )

    upload_to_testflight(
      api_key: api_key,
      skip_waiting_for_build_processing: true,
      changelog: changelog_from_git_commits(
        commits_count: 20,
        pretty: "- %s"
      )
    )
  end

  lane :release do
    api_key = app_store_connect_api_key(
      key_id:      ENV["APP_STORE_CONNECT_API_KEY_ID"],
      issuer_id:   ENV["APP_STORE_CONNECT_ISSUER_ID"],
      key_content: ENV["APP_STORE_CONNECT_API_KEY_BASE64"],
      is_key_content_base64: true
    )

    match(type: "appstore", readonly: true)

    build_app(
      scheme: "App",
      export_method: "app-store",
      output_directory: "build"
    )

    upload_to_app_store(
      api_key: api_key,
      submit_for_review: true,
      automatic_release: false,
      force: true,
      precheck_include_in_app_purchases: false,
      submission_information: {
        add_id_info_uses_idfa: false,
        export_compliance_uses_encryption: false
      }
    )
  end
end
```

## `.github/workflows/ios.yml`

```yaml
name: ios

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
        options: [test, beta, release]

permissions:
  contents: read

jobs:
  ios:
    runs-on: macos-14
    timeout-minutes: 90
    steps:
      - uses: actions/checkout@v4

      - uses: maxim-lobanov/setup-xcode@v1
        with:
          xcode-version: '15.4'

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.3'
          bundler-cache: true

      - uses: actions/cache@v4
        with:
          path: Pods
          key: pods-${{ hashFiles('Podfile.lock') }}

      - run: pod install --repo-update

      - name: Run lane
        env:
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.APP_STORE_CONNECT_API_KEY_ID }}
          APP_STORE_CONNECT_ISSUER_ID: ${{ secrets.APP_STORE_CONNECT_ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY_BASE64: ${{ secrets.APP_STORE_CONNECT_API_KEY_BASE64 }}
          MATCH_GIT_URL: ${{ secrets.MATCH_GIT_URL }}
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_BASIC_AUTHORIZATION }}
        run: |
          LANE="${{ github.event.inputs.lane || 'test' }}"
          bundle exec fastlane "$LANE"

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: build-${{ github.run_id }}
          path: |
            build/*.ipa
            fastlane/logs
            fastlane/report.xml
```

## Match Bootstrap (one-time)

```bash
fastlane match init
fastlane match development
fastlane match appstore
```

This creates the encrypted cert/profile repo. Rotate `MATCH_PASSWORD` yearly and any time an engineer who had access leaves the team.

## Promotion Flow

1. Pull request merges to `main` → `test` lane runs on every PR.
2. On `main` push, `beta` lane uploads the build to TestFlight with automatic changelog.
3. Release manager dispatches `release` lane from the Actions UI once the TestFlight build has been validated by QA.
4. `upload_to_app_store` sets `submit_for_review: true, automatic_release: false` so release timing remains manual.

## Rollback (iOS)

- Apple does not offer a binary rollback. Rollback means shipping the prior version as a new build with a higher build number and submitting for expedited review when the regression is critical.
- Maintain a feature-flag kill switch for any new capability added in a release so you can disable server-side without resubmitting the app.

## Common Failures

- `exportArchive` fails with missing profile → Match did not sync; check `MATCH_GIT_BASIC_AUTHORIZATION` and `MATCH_PASSWORD`.
- `itunesconnect` API auth fails → key ID or issuer ID mismatch, or the `.p8` was not base64-encoded correctly.
- Build number collision → use `Time.now.to_i` or `latest_testflight_build_number + 1` for monotonic numbering.
