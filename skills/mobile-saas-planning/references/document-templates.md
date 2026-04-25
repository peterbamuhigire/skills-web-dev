# Document Templates Reference

Detailed content requirements for each of the 7 planning documents. The agent must follow these templates when generating documentation for a new Android SaaS app.

[Back to SKILL.md](../SKILL.md)

---

## Document 1: README.md (Master Index)

```markdown
# [Product Name] Android App — Planning Documentation

## Document Index
| # | Document | Description | Path |
|---|----------|-------------|------|
| 1 | PRD | Product vision, personas, user stories, MVP | `01_PRD.md` → `prd/` |
| 2 | SRS | Functional & non-functional requirements | `02_SRS.md` → `srs/` |
| ... | ... | ... | ... |

## Quick Reference
### Tech Stack
| Layer | Technology |
|-------|-----------|
| ... | ... |

### Modules
| Module | MVP? | Status |
|--------|------|--------|
| ... | ... | ... |

### API Summary
| Category | Endpoint Count |
|----------|---------------|
| ... | ... |

## Navigation
- Start here, then read documents in order (1-7)
- Each index file links to its sub-files
- Sub-files link back to their index
```

---

## Document 2: PRD (Product Requirements Document)

### Index: `01_PRD.md`

Links to 3 sub-files in `prd/` directory.

### Sub-file: `prd/01-vision-personas.md`

**Required Sections:**

1. **Product Vision** — 2-3 sentence statement: what the app is, who it's for, why it matters
2. **Problem Statement** — 4-6 bullet points describing pain points in the target market that the mobile app solves (not just "the web app needs a mobile version")
3. **Target Personas** — 3-5 detailed personas:

```markdown
### Persona: [Name] — [Role]
- **Age**: [range], **Tech Comfort**: [Low/Medium/High]
- **Device**: [budget phone / mid-range / tablet], **Connectivity**: [reliable / spotty / offline-heavy]
- **Goals**:
  - [Goal 1]
  - [Goal 2]
  - [Goal 3]
- **Frustrations**:
  - [Frustration 1]
  - [Frustration 2]
  - [Frustration 3]
- **Key Scenarios**:
  - [When/where they use the app]
  - [Critical workflow they perform]
```

4. **Competitive Landscape** — Table of 5-7 competitors with columns: Name, Strengths, Weaknesses, Our Differentiator
5. **Product Differentiators** — 3-5 bullet points explaining why this app wins

### Sub-file: `prd/02-user-stories-mvp.md`

**Required Sections:**

1. **User Stories by Module** — grouped by module, minimum 5 per module:

```markdown
### Module: [Name]
| ID | Story | Priority | Acceptance Criteria |
|----|-------|----------|-------------------|
| US-MOD-001 | As a [persona], I want to [action] so that [benefit] | P0 | [measurable criteria] |
```

2. **MVP Scope** — Release roadmap:
   - v1.0 (MVP): List exact modules and features
   - v1.1: Next priority additions
   - v2.0: Full feature set
3. **Feature Dependency Graph** — Which modules require others (ASCII diagram)
4. **Module Unlock Model** — How modules are gated (subscription, role, all-inclusive)

### Sub-file: `prd/03-requirements-metrics.md`

**Required Sections:**

1. **Success Metrics** with specific numeric targets:
   - User adoption: DAU, MAU, D7/D30 retention rates
   - Business: Transaction volume, sync success rate, average session duration
   - Technical: Crash-free rate (>99.5%), ANR rate (<0.5%), API latency p95
2. **App Store Strategy** — Listing name, short description, full description, ASO keywords, screenshot plan
3. **Risk Register** — Table: Risk, Probability (H/M/L), Impact (H/M/L), Mitigation
4. **Assumptions and Constraints** — Numbered lists
5. **Glossary** — 15+ domain-specific terms
6. **API Endpoint Appendix** — Table mapping each feature to its backend endpoint(s)

---

## Document 3: SRS (Software Requirements Specification)

### Index: `02_SRS.md`

Links to 3 sub-files in `srs/` directory.

### Sub-file: `srs/01-functional-requirements.md`

**Format for every requirement:**

```markdown
| ID | Requirement | Priority | API Endpoint |
|----|------------|----------|-------------|
| FR-AUTH-001 | The app shall allow login with email and password | P0 | POST /auth/login |
| FR-AUTH-002 | The app shall store JWT tokens securely in EncryptedSharedPreferences | P0 | — |
```

**Priority Definitions:**
- P0: Cannot ship without — blocks release
- P1: Must have within 2 sprints post-launch
- P2: Planned for future release

**Minimum per module:**
- Auth: 15+ requirements (login, logout, refresh, biometric, 2FA, password reset, permissions)
- Core transaction module (POS/Orders/etc.): 20+ requirements
- Supporting modules: 10+ requirements each
- Dashboard: 10+ requirements
- Settings: 8+ requirements
- Sync (if offline): 10+ requirements

**Each module section must cover:** CRUD, search/filter, validation, error states, offline behavior, role visibility.

### Sub-file: `srs/02-nonfunctional-data-models.md`

**Non-Functional Requirements (with measurable targets):**

| Category | Count | Example Metrics |
|----------|-------|----------------|
| Performance | 10+ | Cold start <3s, search <500ms, scroll 60fps, APK <50MB |
| Security | 10+ | TLS 1.2+, cert pinning, encrypted storage, biometric, ProGuard |
| Offline | 5-7 | Queue writes, staleness budgets, 72h operation |
| Reliability | 5-7 | 99.5% crash-free, exponential backoff, corruption recovery |
| Accessibility | 5+ | 48dp touch targets, WCAG AA contrast, TalkBack, RTL |
| Localization | 5+ | All supported languages, number/date/currency formatting |

**Room Entity Definitions:**

For every local table, provide:

```markdown
### Entity: [TableName]Entity
| Column | Type | PK? | FK? | Index? | Notes |
|--------|------|-----|-----|--------|-------|
| id | String | Yes | — | — | UUID from server |
| name | String | — | — | Yes | Searchable |
| tenantId | String | — | tbl_franchises.id | Yes | Tenant scope |
| syncStatus | Int | — | — | — | 0=synced, 1=pending, 2=conflict |
| updatedAt | Long | — | — | — | Epoch millis |
```

**Also include:** Android version support matrix, third-party dependency table.

### Sub-file: `srs/03-error-handling-traceability.md`

**Error Categories:**

| Category | Examples | Retry Policy | User Message Pattern |
|----------|----------|-------------|---------------------|
| Network | Timeout, no connection | Auto-retry 3x with backoff | "No internet. Working offline." |
| Auth | Token expired, revoked | Auto-refresh, then re-login | "Session expired. Please log in." |
| Validation | Missing field, invalid format | No retry, fix input | "[Field] is required." |
| Business Logic | Insufficient stock, duplicate | No retry, user action needed | Specific message from server |
| Sync | Conflict, queue overflow | Auto-retry with conflict resolution | "Sync conflict. Server version kept." |

**Traceability Matrix:** Requirements → Modules → Room Entities → API Endpoints

---

## Document 4: API Contract

### Index: `04_API_CONTRACT.md`

Links to sub-files in `api-contract/` directory, split by domain.

### Sub-file: `api-contract/01-overview.md`

Must contain: Base URLs table, JWT structure (header/payload/claims), auth flow diagram, standard response envelope, standard error format, HTTP status codes used, pagination model with examples, rate limits, common request/response headers.

### Endpoint Sub-files: `api-contract/02-endpoints-[domain].md`

**Every endpoint must include:**

```markdown
### POST /auth/login
**Description:** Authenticate user with email and password.
**Auth Required:** No
**Rate Limited:** Yes (5 requests / minute)

**Request:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email format |
| password | string | Yes | Min 8 characters |

```json
{ "email": "user@example.com", "password": "securePass123" }
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "dGhpcyBpcyBh...",
    "expires_in": 900,
    "user": { "id": 1, "name": "John", "role": "cashier" }
  }
}
```

**Error Responses:**
| Status | Code | Condition |
|--------|------|-----------|
| 401 | INVALID_CREDENTIALS | Wrong email or password |
| 429 | RATE_LIMITED | Too many login attempts |
```

### Last sub-file: `api-contract/XX-error-codes.md`

Complete error code reference table: HTTP Status, Error Code, Description, User Message, Retry Policy.

---

## Document 5: User Journeys

### `05_USER_JOURNEYS.md` (split if >500 lines)

**Each journey format:**

```markdown
## Journey: [Title]
**Preconditions:** [What must be true before this journey starts]

### Flow Diagram
┌─────────┐    ┌──────────┐    ┌─────────┐
│  Start  │───>│  Step 1  │───>│  Step 2 │──> ...
└─────────┘    └──────────┘    └─────────┘
                     │
                     ▼ (error)
               ┌──────────┐
               │  Error   │
               └──────────┘

### Steps
1. **[Screen Name]**: User sees [description]. Taps [action].
2. **[Screen Name]**: App shows [description]. User enters [data].
...

### Alternative Paths
- **Offline**: [What happens when offline during this journey]
- **Error**: [What happens on failure]
- **Cancel**: [How user exits mid-journey]
```

**Mandatory journeys (adapt to domain):**
1. First-time setup / onboarding
2. Login (standard + biometric shortcut)
3. Primary transaction (sale, order, booking, etc.)
4. Offline transaction (if offline-first)
5. Search / lookup
6. Dashboard interaction
7. Module discovery / upgrade (if module-gated)
8. Error states and recovery

---

## Document 6: Testing Strategy

See `references/architecture-patterns.md` for test code examples.

### `testing/01-unit-ui-tests.md`

Must include: Test pyramid with percentages and counts, ViewModel test example using Turbine, UseCase test areas table, Repository test checklist, Compose UI test example, screen test matrix.

### `testing/02-integration-security-performance.md`

Must include: MockWebServer API contract tests, Room in-memory DB tests, security test checklist (7+ items), performance benchmarks (10+ metrics), test environment matrix, GitHub Actions test pipeline YAML, test data fixtures.

---

## Document 7: Release Plan

### `07_RELEASE_PLAN.md`

Must include: Play Store setup, signing strategy (upload key + Play App Signing), release channel progression (internal → alpha → beta → production), staged rollout percentages, semantic versioning, privacy policy checklist, app store listing content, in-app update implementation, pre-release checklist (12+ items), rollback procedure, post-launch monitoring metrics with alert thresholds.
