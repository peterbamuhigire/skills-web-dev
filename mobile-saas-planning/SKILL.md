---
name: mobile-saas-planning
description: Create comprehensive planning documentation for a native mobile app (Android
  or iOS) that integrates with an existing web-based SaaS platform. Use when building
  a mobile companion app for any SaaS — ERP, CRM, POS, logistics, healthcare, fintech...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Mobile SaaS Planning Skill

<!-- dual-compat-start -->
## Use When

- Create comprehensive planning documentation for a native mobile app (Android or iOS) that integrates with an existing web-based SaaS platform. Use when building a mobile companion app for any SaaS — ERP, CRM, POS, logistics, healthcare, fintech...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `mobile-saas-planning` or would be better handled by a more specific companion skill.
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
| Release evidence | Mobile app planning document | Markdown doc covering scope, milestones, integration points with the SaaS backend, and store-submission timeline | `docs/mobile/saas-planning-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Generate a complete, implementation-ready documentation suite for a native mobile app (Android or iOS) that serves as a mobile client for an existing web-based SaaS system.

## When to Use

- Building a new native mobile app (Android or iOS) for an existing web SaaS
- Porting a web application's functionality to mobile
- Planning a mobile-first or mobile-companion SaaS experience
- Scoping MVP features for a mobile client
- Creating a structured handoff document for mobile developers

## When NOT to Use

- Building a standalone mobile app with no web backend
- Cross-platform frameworks (Flutter/React Native) — this skill targets native apps
- **KMP projects**: Use this skill but select "KMP" as the project type below.
  SDS will include the shared module architecture (Ktor, SQLDelight, Koin).
  API Contract will account for shared networking layer in `commonMain`.
  Testing Strategy will reference `kmp-tdd` for shared module tests alongside
  `android-tdd` and `ios-tdd` for platform UI tests
- Adding a WebView wrapper — this skill targets fully native screens
- Incremental feature additions to an existing mobile app

## Prerequisites — Context the Agent MUST Gather

Before generating ANY documents, the agent must have or discover:

### 1. SaaS Profile (Required)

| Field         | What to Find                                      |
| ------------- | ------------------------------------------------- |
| Product name  | Brand name and domain                             |
| Domain        | ERP, CRM, POS, Healthcare, Fintech, etc.          |
| Target market | Region, language, currency, payment methods       |
| Backend stack | PHP/MySQL, Node/PostgreSQL, Django, Laravel, etc. |
| API base URL  | Per environment (see standard 3-env setup below)  |
| Auth model    | JWT, OAuth2, session-based, API keys              |
| Multi-tenancy | Tenant ID in JWT, subdomain, DB-per-tenant        |
| Target platform | Android, iOS, or both                           |

### 2. Module Inventory (Required)

Audit the web app to identify all modules. For each module determine:

- **Name and description** (what the module does)
- **Mobile relevance** — does it make sense on a phone? (e.g., complex admin panels may not)
- **MVP classification** — P0 (ship without), P1 (within 2 sprints), P2 (future)
- **Offline requirement** — must it work offline?
- **API endpoints** — existing endpoints that serve this module

### 3. Feature Scope (Required — Accept from User)

The user may request a **subset** of modules. Respect their selection:

- If the user specifies "only POS and Inventory" — plan only those modules
- If the user says "full app" — plan all mobile-relevant modules
- Always include Auth and Dashboard as baseline modules unless explicitly excluded

### 4. Technical Constraints (Discover or Ask)

**Android constraints:**

- Minimum Android API level (default: API 29 / Android 10)
- Apps must be tested against the latest stable Android release
- Max APK size (default: 50MB)

**iOS constraints:**

- Minimum iOS version (default: iOS 17)
- Xcode 16+
- Max IPA size (default: 200MB)

**Shared constraints:**

- Offline requirements (none / basic caching / full offline-first)
- Hardware peripherals (Bluetooth printer, barcode scanner, NFC)
- Biometric authentication (fingerprint, face)
- Push notifications (FCM for Android, APNs for iOS)
- Local dev networking: Android emulator must connect via the host machine's static LAN IP (not `localhost`); iOS Simulator can use `localhost` directly

### 5. Standard Backend Environment Setup

All SaaS companion apps target these three backend environments:

| Environment | OS | Database | API Base URL Pattern |
|---|---|---|---|
| **Development** | Windows 11 (WAMP) | MySQL 8.4.7 | `http://{LAN_IP}:{port}/{project}/api/` |
| **Staging** | Ubuntu VPS | MySQL 8.x | `https://staging.{domain}/api/` |
| **Production** | Debian VPS | MySQL 8.x | `https://{domain}/api/` |

**Android:** Use Gradle build flavors to manage per-environment base URLs.
**iOS:** Use Xcode build configurations and `.xcconfig` files to manage per-environment base URLs.

All backends use `utf8mb4_unicode_ci` collation and MySQL 8.x. Always plan API contracts that work identically across all environments.

## Phase 1 Bootstrap Pattern (MANDATORY)

**Every mobile SaaS app MUST start with Phase 1: Login + Dashboard + Empty Tabs.**

This is the proven foundation pattern. Before planning any business features, the first implementation phase always delivers:

### Phase 1 Scope (Non-Negotiable)

1. **JWT Authentication** — Login/logout with the SaaS backend (access tokens + refresh token rotation + breach detection)
2. **Dashboard** — Real KPI stats from the backend, offline-first with Room caching (Android) or SwiftData (iOS), pull-to-refresh
3. **Bottom Navigation** — Maximum 5 major section tabs using BottomNavigation (Android) or TabView (iOS). Non-dashboard tabs show "Coming Soon" placeholder screens
4. **Core Infrastructure**
   - **Android:** Hilt DI modules, Retrofit + OkHttp interceptor chain (auth + tenant + logging), encrypted token storage, network monitor, Room database, Material 3 theme
   - **iOS:** Swift Package Manager, URLSession + async/await, Keychain token storage, network monitor, SwiftData, @Observable, custom theme
5. **Backend Endpoints** — Mobile login, token refresh, logout, and dashboard stats API endpoints with dual auth middleware (JWT for mobile + session for web backward compatibility)
6. **Unit Tests**
   - **Android:** Full test coverage with JUnit 5, MockK for ViewModels, Use Cases, Repositories, Interceptors
   - **iOS:** Full test coverage with XCTest/Swift Testing for Views, Services, Repositories

### Phase 1 Deliverables

| Component | Android | iOS | Backend |
|---|---|---|---|
| Auth | LoginScreen, LoginViewModel, AuthRepository, AuthApiService, TokenManager, interceptors | LoginView, AuthService, TokenManager, KeychainHelper | mobile-login.php, mobile-refresh.php, mobile-logout.php, MobileAuthHelper, ApiAuthMiddleware |
| Dashboard | DashboardScreen, DashboardViewModel, DashboardRepository, Room cache | DashboardView, DashboardService, SwiftData cache | dashboard-stats.php (dual auth) |
| Navigation | 5-tab BottomBar, NavGraph, PlaceholderScreen for future tabs | 5-tab TabView, NavigationStack | — |
| Infrastructure | DI modules, theme, encrypted prefs, network monitor | SPM packages, theme, Keychain | refresh_tokens table, .env loading |
| Tests | 40+ unit tests (JUnit 5/MockK) | 40+ unit tests (XCTest/Swift Testing) | curl/Postman endpoint verification |

### Why Phase 1 First

- Proves the entire vertical slice works (UI -> ViewModel/Service -> UseCase -> Repository -> API -> Backend -> Database)
- Establishes all infrastructure patterns that every future feature reuses
- Gives the user a working app they can install and log into immediately
- Uncovers backend integration issues early (auth, CORS, env loading, session handling)
- Creates the navigation skeleton that future phases fill in

### Tab Selection (Max 5)

When auditing modules, group them into a **maximum of 5 bottom navigation tabs**. Common patterns:

| App Type            | Tab 1 | Tab 2        | Tab 3     | Tab 4     | Tab 5    |
| ------------------- | ----- | ------------ | --------- | --------- | -------- |
| **MLM/Distributor** | Home  | Sales        | Network   | Knowledge | Training |
| **ERP/Business**    | Home  | Sales        | Inventory | Reports   | Settings |
| **CRM**             | Home  | Contacts     | Deals     | Tasks     | Settings |
| **POS/Retail**      | Home  | Sales        | Products  | Customers | Reports  |
| **Healthcare**      | Home  | Patients     | Schedule  | Records   | Settings |
| **Fintech**         | Home  | Transactions | Cards     | Savings   | Settings |

If more than 5 sections exist, nest sub-sections within tabs or use drawer navigation for secondary items.

### Phase 1 Implementation Plan Structure

**Android** — The Phase 1 plan MUST be structured as 11 sections:

```
docs/plans/phase-1-login-dashboard/
├── 00-build-variants.md          # Dev/Staging/Prod flavors
├── 01-project-bootstrap.md       # Gradle, manifest, strings, packages
├── 02-backend-api.md             # PHP JWT endpoints + DB migration
├── 03-core-infrastructure.md     # DI, security, network, interceptors
├── 04-authentication-feature.md  # Login vertical slice (DTO->Entity->Domain)
├── 05-dashboard-feature.md       # Dashboard with offline-first Room caching
├── 06-navigation-tabs.md         # Bottom nav + placeholder screens
├── 07-room-database.md           # Database class, converters, module
├── 08-theme-ui-components.md     # Material 3 theme + reusable components
├── 09-testing.md                 # 40+ unit tests across all layers
└── 10-verification.md            # Backend curl tests + Android manual checklist
```

**iOS** — The Phase 1 plan MUST be structured as 11 sections:

```
docs/plans/ios-phase-1-login-dashboard/
├── 00-xcode-setup.md             # Build configs, .xcconfig, schemes
├── 01-project-bootstrap.md       # SPM packages, Info.plist, project structure
├── 02-backend-api.md             # PHP JWT endpoints + DB migration (shared with Android)
├── 03-core-infrastructure.md     # Networking, security, Keychain, monitors
├── 04-authentication-feature.md  # Login vertical slice (DTO->Model->Domain)
├── 05-dashboard-feature.md       # Dashboard with offline-first SwiftData caching
├── 06-navigation-tabs.md         # TabView + NavigationStack + placeholder screens
├── 07-swiftdata-persistence.md   # SwiftData models, containers, queries
├── 08-theme-ui-components.md     # Custom theme + reusable SwiftUI components
├── 09-testing.md                 # 40+ unit tests across all layers
└── 10-verification.md            # Backend curl tests + iOS manual checklist
```

### Phase 2+ Planning

Only after Phase 1 is **fully implemented, tested, and verified E2E** should Phase 2 features be planned. Phase 2 fills in the placeholder tabs with real functionality, reusing all the infrastructure from Phase 1.

---

## Document Generation Workflow

Generate documents **one at a time**, in order. Each document builds on the previous.

### Step 1: Audit the Existing Web App

Before writing any documents:

1. **Read the codebase** — scan API routes, controllers, models, database schema
2. **Identify modules** — group endpoints by business domain
3. **Map data models** — understand entities, relationships, field types
4. **Note auth flow** — how login, tokens, permissions, and multi-tenancy work
5. **Find existing docs** — API docs, database docs, architecture docs
6. **Present findings** to the user for confirmation before proceeding

### Step 2: Generate Documents in Order

| Order | Document              | Index File               | Sub-files Directory        |
| ----- | --------------------- | ------------------------ | -------------------------- |
| 1     | README                | `README.md`              | —                          |
| 2     | Product Requirements  | `01_PRD.md`              | `prd/`                     |
| 3     | Software Requirements | `02_SRS.md`              | `srs/`                     |
| 4     | Software Design       | `03_SDS.md`              | `sds/`                     |
| 5     | API Contract          | `04_API_CONTRACT.md`     | `api-contract/`            |
| 6     | User Journeys         | `05_USER_JOURNEYS.md`    | — (or split if >500 lines) |
| 7     | Testing Strategy      | `06_TESTING_STRATEGY.md` | `testing/`                 |
| 8     | Release Plan          | `07_RELEASE_PLAN.md`     | —                          |

### Step 3: Review and Refine

After all documents are generated, verify:

- [ ] All module requirements trace to API endpoints
- [ ] Local entities (Room/SwiftData) match backend data models
- [ ] Auth flow matches the web app's actual auth implementation
- [ ] Offline sync strategy covers all P0 modules
- [ ] No fabricated endpoints — every endpoint references real backend routes

## Formatting Rules (Strict)

1. **500-line max** per markdown file — split into sub-files if exceeded
2. **Numbered requirement IDs** — `FR-AUTH-001`, `NFR-PERF-003`, etc.
3. **Real code** — not pseudocode; include actual imports and versions (Kotlin for Android, Swift for iOS)
4. **JSON examples** — complete request/response bodies for every endpoint
5. **ASCII diagrams** — flow charts, architecture layers, sync flows
6. **Markdown tables** — for requirements, endpoints, metrics, comparisons
7. **Cross-references** — link between documents liberally
8. **Back-links** — every sub-file links back to its parent index
9. **Navigation** — every index links to all its sub-files with descriptions

## Tech Stack Defaults

### Android Tech Stack

Use these unless the project context requires alternatives:

| Layer         | Technology                                  | Version                             |
| ------------- | ------------------------------------------- | ----------------------------------- |
| Language      | Kotlin                                      | 2.0+                                |
| UI            | Jetpack Compose + Material 3                | BOM 2024.06+                        |
| Icons         | Custom PNGs (no icon libraries)             | Use placeholders + PROJECT_ICONS.md |
| Reports       | Table-first for >25 rows                    | Use android-report-tables           |
| Architecture  | MVVM + Clean Architecture                   | —                                   |
| DI            | Dagger Hilt                                 | 2.51+                               |
| Networking    | Retrofit + OkHttp + Moshi                   | 2.11+ / 4.12+                       |
| Local DB      | Room                                        | 2.6+                                |
| Async         | Coroutines + Flow                           | 1.8+                                |
| Background    | WorkManager                                 | 2.9+                                |
| Navigation    | Navigation Compose                          | 2.7+                                |
| Image Loading | Coil                                        | 2.6+                                |
| Charting      | Vico (Compose-first)                        | Use guide                           |
| Security      | EncryptedSharedPreferences, BiometricPrompt | AndroidX                            |
| Logging       | Timber                                      | 5.0+                                |
| Testing       | JUnit 5, MockK, Turbine, Compose UI Testing | —                                   |
| CI/CD         | GitHub Actions                              | —                                   |

### iOS Tech Stack

Use these unless the project context requires alternatives:

| Layer         | Technology                              | Version            |
| ------------- | --------------------------------------- | ------------------ |
| Language      | Swift                                   | 6.0+               |
| UI            | SwiftUI                                 | iOS 17+            |
| Icons         | Custom PNGs (no SF Symbols)             | Asset Catalogs + PROJECT_ICONS.md |
| Reports       | Table-first for >25 rows               | Use mobile-report-tables |
| Architecture  | MVVM + Clean Architecture               | —                  |
| DI            | Swift native / Factory pattern          | —                  |
| Networking    | URLSession + async/await                | —                  |
| JSON          | Codable                                 | —                  |
| Local DB      | SwiftData                               | iOS 17+            |
| Async         | Swift Concurrency (async/await)         | —                  |
| Background    | BGTaskScheduler                         | —                  |
| Navigation    | NavigationStack                         | —                  |
| Image Loading | AsyncImage / Kingfisher                 | —                  |
| Charting      | Swift Charts                            | iOS 16+            |
| Security      | Keychain Services, LocalAuthentication  | —                  |
| Logging       | os.Logger                               | —                  |
| Testing       | XCTest, Swift Testing                   | —                  |
| CI/CD         | GitHub Actions + Xcode Cloud            | —                  |

## Document Content Requirements

Detailed templates for each document are in `references/document-templates.md`.
Architecture and code patterns are in `references/architecture-patterns.md`.
API integration patterns are in `references/api-integration-patterns.md`.

### Quick Reference — What Each Document Must Contain

**01_PRD** — Vision, personas (3-5), user stories (5+ per module), MVP scope with release phases, competitive analysis, success metrics, risk register, glossary

**02_SRS** — Numbered functional requirements (10+ per core module), non-functional requirements (performance, security, offline, accessibility, localization), local entity definitions (Room/SwiftData), traceability matrix

**03_SDS** — Architecture layers, complete build config (Gradle for Android, Xcode for iOS), project structure, DI setup, security implementation (cert pinning, encrypted storage, biometrics, code obfuscation), offline sync (Room DAOs or SwiftData queries, SyncWorker/BGTaskScheduler, conflict resolution, staleness budgets), networking layer, CI/CD workflows

**04_API_CONTRACT** — Base URLs, auth model, JWT structure, every endpoint with method + path + request JSON + response JSON + validation rules + error responses, pagination model, rate limits, error code reference

**05_USER_JOURNEYS** — 8-12 journeys with ASCII flow diagrams, step-by-step breakdowns, error paths, offline behavior. Must include: first-time setup, login, primary transaction, offline transaction, search, dashboard, error recovery

**06_TESTING_STRATEGY** — Test pyramid (60/25/10/5), unit test examples (ViewModel/Service tests, UseCase, Repository), UI test examples (Compose/SwiftUI), integration tests, security tests, performance benchmarks, CI gates, test data fixtures

**07_RELEASE_PLAN** — Store setup (Play Store and/or App Store), signing strategy, release channels with staged rollout, versioning, privacy policy checklist, app store listing, in-app update strategy, release checklist, rollback procedure, post-launch monitoring

## Adaptation Rules

### Partial Module Selection

When the user requests only specific modules:

1. Still generate ALL 7 documents, but scope content to selected modules
2. Auth module is always included (required for any authenticated app)
3. Dashboard adapts to show only KPIs relevant to selected modules
4. API Contract only documents endpoints for selected modules
5. User Journeys only cover flows for selected modules
6. Local entities only include tables needed by selected modules

### No Offline Requirement

If the user says offline support is not needed:

1. Remove offline sync section from SDS entirely
2. Simplify Repository pattern (no local-first fallback)
3. Remove SyncWorker/BGTaskScheduler sync setup
4. Remove offline-related NFRs from SRS
5. Remove offline user journeys
6. Keep local DB for caching only (not as offline data store)

### Module-Gated vs All-Inclusive

If modules are subscription-gated:

- Add module unlock system to SDS (feature flags, ModuleAccessManager)
- Add module discovery journey to User Journeys
- Add locked-module UI patterns (upgrade prompts, feature previews)

If all modules are available to all users:

- Remove module gating from SDS
- Remove module discovery journey
- Gate features by role/permission only

### Regional Customization

Adapt to target market:

- **East Africa**: M-Pesa/Mobile Money, UGX/KES/TZS, Swahili/English, low-bandwidth optimization
- **West Africa**: Paystack, NGN/GHS, French/English/Hausa, USSD fallback
- **Southeast Asia**: GrabPay/GCash, local currencies, multi-script support
- **Global**: Stripe, multi-currency, broad language support

## Quality Checklist (Run After All Documents)

- [ ] Every FR traces to at least one API endpoint
- [ ] Every API endpoint has complete request/response JSON
- [ ] Every local entity maps to a backend data model
- [ ] Auth flow matches the web app's actual implementation
- [ ] All code compiles conceptually (correct imports, types, annotations)
- [ ] No file exceeds 500 lines
- [ ] All sub-files have back-links to parent index
- [ ] All indexes link to all sub-files
- [ ] Requirement IDs are unique and sequential
- [ ] Version numbers for libraries are realistic and compatible
- [ ] Personas reflect the actual target market
- [ ] Success metrics have specific numeric targets
- [ ] Release plan includes rollback procedure

## Cross-Skill References

Load these skills alongside for deeper implementation guidance:

- `android-development` — Kotlin/Android coding standards
- `android-tdd` — Test-driven development workflow
- `android-data-persistence` — Room, DataStore, offline-first patterns
- `jetpack-compose-ui` — Compose UI standards and Material 3
- `ios-development` — Swift/iOS coding standards (when created)
- `swiftui-design` — SwiftUI UI standards (when created)
- `dual-auth-rbac` — Authentication and permission system
- `api-error-handling` — API error response patterns
- `modular-saas-architecture` — Module toggle and subscription gating
- `multi-tenant-saas-architecture` — Tenant isolation patterns
