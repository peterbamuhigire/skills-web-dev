---
name: ios-networking-advanced
description: Production-grade iOS networking — URLSession async/await with typed errors,
  interceptor/middleware pattern (auth token injection + 401 refresh), exponential
  backoff retry, request deduplication, background URLSession for large downloads/uploads...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Networking — Advanced Production Patterns
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Production-grade iOS networking — URLSession async/await with typed errors, interceptor/middleware pattern (auth token injection + 401 refresh), exponential backoff retry, request deduplication, background URLSession for large downloads/uploads...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-networking-advanced` or would be better handled by a more specific companion skill.
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
| Correctness | API contract test output | CI log or recorded test report covering URLSession contracts | `docs/ios/network-tests-2026-04-16.md` |
| Security | TLS / certificate-pinning configuration note | Markdown doc covering ATS, pinning, and credential transport | `docs/ios/network-security-config.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Quick Reference

| Topic | Section |
|---|---|
| Typed errors + async/await foundation | Section 1 |
| Type-safe endpoint building | Section 2 |
| Auth token refresh interceptor (401) | Section 3 |
| Exponential backoff retry | Section 4 |
| Background URLSession (downloads/uploads) | Section 5 |
| Certificate pinning | Section 6 |
| Multipart form data upload | Section 7 |
| Network reachability + offline queue | Section 8 (→ references) |
| Request deduplication | Section 9 |
| Combine + URLSession (legacy) | Section 10 (→ references) |
| Structured concurrency (async-let, Task groups) | Section 11 |
| Production anti-patterns | Section 12 |

---

## Section 1: Typed Errors + Async/Await Foundation

```swift
enum NetworkError: Error, LocalizedError {
    case invalidURL
    case noData
    case decodingFailed(Error)
    case httpError(statusCode: Int, data: Data?)
    case unauthorized          // 401 — triggers token refresh
    case forbidden             // 403 — no point retrying
    case serverError(Int)      // 5xx — retry eligible
    case cancelled
    case noInternetConnection

    var errorDescription: String? {
        switch self {
        case .unauthorized:            return "Session expired. Please log in again."
        case .noInternetConnection:    return "No internet connection."
        case .httpError(let code, _):  return "Request failed with status \(code)"
        default:                       return "Something went wrong. Please try again."
        }
    }
}

actor NetworkClient {
    private let session: URLSession
    private let decoder: JSONDecoder
    private(set) var authToken: String?

    init(session: URLSession = .shared) {
        self.session = session
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
        self.decoder.dateDecodingStrategy = .iso8601
    }

    func setToken(_ token: String) { authToken = token }

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let urlRequest = try endpoint.urlRequest(token: authToken)
        let (data, response) = try await session.data(for: urlRequest)

        guard let http = response as? HTTPURLResponse else { throw NetworkError.noData }

        switch http.statusCode {
        case 200...299:
            do { return try decoder.decode(T.self, from: data) }
            catch { throw NetworkError.decodingFailed(error) }
        case 401: throw NetworkError.unauthorized
        case 403: throw NetworkError.forbidden
        case 500...599: throw NetworkError.serverError(http.statusCode)
        default: throw NetworkError.httpError(statusCode: http.statusCode, data: data)
        }
    }
}
```

---

## Additional Guidance

Extended guidance for `ios-networking-advanced` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Section 2: Type-Safe Endpoint Pattern`
- `Section 3: Auth Token Refresh Interceptor (401 Auto-Retry)`
- `Section 4: Exponential Backoff Retry`
- `Section 5: Background URLSession (Large Downloads/Uploads)`
- `Section 6: Certificate Pinning`
- `Section 7: Multipart Form Data Upload`
- `Section 8: Network Reachability + Offline Queue`
- `Section 9: Request Deduplication`
- `Section 10: Combine + URLSession (Legacy)`
- `Section 11: Structured Concurrency`
- `Section 12: Production Anti-Patterns`
- `REST Client Assembly Checklist`