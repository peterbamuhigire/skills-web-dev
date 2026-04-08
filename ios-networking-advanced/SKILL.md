---
name: ios-networking-advanced
description: Production-grade iOS networking — URLSession async/await with typed errors, interceptor/middleware pattern (auth token injection + 401 refresh), exponential backoff retry, request deduplication, background URLSession for large downloads/uploads...
---

# iOS Networking — Advanced Production Patterns

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

## Section 2: Type-Safe Endpoint Pattern

```swift
struct Endpoint {
    let path: String
    let method: HTTPMethod
    let queryItems: [URLQueryItem]?
    let body: Encodable?
    let requiresAuth: Bool

    enum HTTPMethod: String {
        case get = "GET", post = "POST", put = "PUT", delete = "DELETE", patch = "PATCH"
    }

    func urlRequest(token: String?, baseURL: URL = Config.apiBaseURL) throws -> URLRequest {
        var components = URLComponents(url: baseURL.appendingPathComponent(path),
                                       resolvingAgainstBaseURL: false)!
        components.queryItems = queryItems
        guard let url = components.url else { throw NetworkError.invalidURL }

        var request = URLRequest(url: url, timeoutInterval: 30)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if requiresAuth, let token { request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization") }
        if let body { request.httpBody = try JSONEncoder().encode(body) }
        return request
    }
}

extension Endpoint {
    static func login(email: String, password: String) -> Endpoint {
        Endpoint(path: "/auth/login", method: .post, queryItems: nil,
                 body: LoginRequest(email: email, password: password), requiresAuth: false)
    }
    static func refreshToken(token: String) -> Endpoint {
        Endpoint(path: "/auth/refresh", method: .post, queryItems: nil,
                 body: RefreshRequest(refreshToken: token), requiresAuth: false)
    }
    static func userProfile(id: String) -> Endpoint {
        Endpoint(path: "/users/\(id)", method: .get, queryItems: nil, body: nil, requiresAuth: true)
    }
}
```

---

## Section 3: Auth Token Refresh Interceptor (401 Auto-Retry)

```swift
// Key insight: deduplicate with a stored Task so N concurrent 401s = 1 refresh call.
actor AuthenticatedClient {
    private let client: NetworkClient
    private let tokenStore: TokenStore
    private var refreshTask: Task<String, Error>?

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        do {
            return try await client.request(endpoint)
        } catch NetworkError.unauthorized {
            let newToken = try await refreshAccessToken()
            await client.setToken(newToken)
            return try await client.request(endpoint)   // retry once
        }
    }

    private func refreshAccessToken() async throws -> String {
        if let existing = refreshTask { return try await existing.value }   // piggyback

        let refreshToken = try tokenStore.refreshToken()
        let task = Task<String, Error> {
            defer { Task { await self.clearRefreshTask() } }
            let response: TokenResponse = try await client.request(.refreshToken(token: refreshToken))
            try self.tokenStore.save(accessToken: response.accessToken,
                                     refreshToken: response.refreshToken)
            return response.accessToken
        }
        refreshTask = task
        return try await task.value
    }

    private func clearRefreshTask() { refreshTask = nil }
}
```

**Rules:**
- Retry once only — if the second attempt also gets 401, propagate the error
- Store refresh token in Keychain, never UserDefaults
- Clear `refreshTask` in `defer` so the next genuine expiry triggers a fresh refresh

---

## Section 4: Exponential Backoff Retry

```swift
extension NetworkClient {
    func requestWithRetry<T: Decodable>(
        _ endpoint: Endpoint,
        maxAttempts: Int = 3,
        baseDelay: TimeInterval = 1.0
    ) async throws -> T {
        var lastError: Error?

        for attempt in 0..<maxAttempts {
            do {
                return try await request(endpoint)
            } catch NetworkError.serverError(let code) where code >= 500 {
                lastError = NetworkError.serverError(code)
                guard attempt < maxAttempts - 1 else { break }
                // Exponential backoff + jitter: 1s, 2s, 4s ± 0–500ms
                let delay = baseDelay * pow(2.0, Double(attempt)) + Double.random(in: 0...0.5)
                try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
            } catch NetworkError.forbidden, NetworkError.unauthorized {
                throw lastError!          // auth errors: never retry
            }
        }
        throw lastError ?? NetworkError.noData
    }
}
```

**Retry matrix:**

| Status | Retryable | Strategy |
|---|---|---|
| 2xx | No — success | — |
| 401 | Yes (once) | Refresh token then retry |
| 403 | No | Throw immediately |
| 429 | Yes | Honour `Retry-After` header |
| 500–599 | Yes | Exponential backoff, max 3 |
| Network timeout | Yes | Exponential backoff |

---

## Section 5: Background URLSession (Large Downloads/Uploads)

```swift
class BackgroundTransferManager: NSObject {
    static let shared = BackgroundTransferManager()
    var backgroundCompletionHandler: (() -> Void)?

    private lazy var backgroundSession: URLSession = {
        let config = URLSessionConfiguration.background(withIdentifier: "com.app.bg-transfer")
        config.isDiscretionary = false          // transfer immediately, not when convenient
        config.sessionSendsLaunchEvents = true  // wake app on completion
        config.allowsCellularAccess = true
        return URLSession(configuration: config, delegate: self, delegateQueue: nil)
    }()

    func download(from url: URL) {
        backgroundSession.downloadTask(with: url).resume()
    }

    func upload(fileURL: URL, to request: URLRequest) {
        // Background uploads MUST use file-based variant, not Data
        backgroundSession.uploadTask(with: request, fromFile: fileURL).resume()
    }
}

extension BackgroundTransferManager: URLSessionDownloadDelegate {
    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didFinishDownloadingTo location: URL) {
        // Move immediately — temp file deleted after this method returns
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let dest = docs.appendingPathComponent(
            downloadTask.response?.suggestedFilename ?? UUID().uuidString
        )
        try? FileManager.default.moveItem(at: location, to: dest)
        NotificationCenter.default.post(name: .downloadCompleted, object: dest)
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didWriteData bytesWritten: Int64, totalBytesWritten: Int64,
                    totalBytesExpectedToWrite: Int64) {
        let progress = Double(totalBytesWritten) / Double(totalBytesExpectedToWrite)
        DispatchQueue.main.async {
            NotificationCenter.default.post(name: .downloadProgress, object: progress)
        }
    }

    func urlSessionDidFinishEvents(forBackgroundURLSession session: URLSession) {
        DispatchQueue.main.async {
            self.backgroundCompletionHandler?()
            self.backgroundCompletionHandler = nil
        }
    }
}

// AppDelegate — required to reconnect session and call system completion handler
// func application(_ app: UIApplication, handleEventsForBackgroundURLSession id: String,
//     completionHandler: @escaping () -> Void) {
//     BackgroundTransferManager.shared.backgroundCompletionHandler = completionHandler
// }
```

---

## Section 6: Certificate Pinning

```swift
// Pin the server's leaf certificate public key hash (SHA-256, base64-encoded).
// Generate hash: openssl s_client -connect api.example.com:443 | openssl x509 -pubkey -noout |
//                openssl pkey -pubin -outform DER | openssl dgst -sha256 -binary | base64
class PinnedSessionDelegate: NSObject, URLSessionDelegate {
    private let pinnedKeyHashes: Set<String>

    init(hashes: Set<String>) { self.pinnedKeyHashes = hashes }

    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {

        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        var cfError: CFError?
        guard SecTrustEvaluateWithError(serverTrust, &cfError) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        guard let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0),
              let publicKey = SecCertificateCopyKey(certificate),
              let keyData = SecKeyCopyExternalRepresentation(publicKey, nil) as Data? else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Prepend ASN.1 header for RSA-2048 public key before hashing
        let rsa2048Header = Data([0x30, 0x82, 0x01, 0x22, 0x30, 0x0d, 0x06, 0x09,
                                   0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01,
                                   0x01, 0x05, 0x00, 0x03, 0x82, 0x01, 0x0f, 0x00])
        var hashData = Data(SHA256.hash(data: rsa2048Header + keyData))
        let hash = hashData.base64EncodedString()

        if pinnedKeyHashes.contains(hash) {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}

// Usage
// #if !DEBUG  ← disable pinning in debug builds so Charles/Proxyman work
// let delegate = PinnedSessionDelegate(hashes: ["your-sha256-hash="])
// let session = URLSession(configuration: .default, delegate: delegate, delegateQueue: nil)
// #endif
```

---

## Section 7: Multipart Form Data Upload

```swift
struct MultipartFormData {
    private let boundary = "Boundary-\(UUID().uuidString)"
    private var body = Data()
    private let crlf = "\r\n"

    mutating func addTextField(name: String, value: String) {
        append("--\(boundary)\(crlf)")
        append("Content-Disposition: form-data; name=\"\(name)\"\(crlf)\(crlf)")
        append("\(value)\(crlf)")
    }

    mutating func addFileField(name: String, filename: String,
                               data: Data, mimeType: String = "image/jpeg") {
        append("--\(boundary)\(crlf)")
        append("Content-Disposition: form-data; name=\"\(name)\"; filename=\"\(filename)\"\(crlf)")
        append("Content-Type: \(mimeType)\(crlf)\(crlf)")
        body.append(data)
        append(crlf)
    }

    func finalize() -> (data: Data, contentType: String) {
        var final = body
        if let closing = "--\(boundary)--\(crlf)".data(using: .utf8) { final.append(closing) }
        return (final, "multipart/form-data; boundary=\(boundary)")
    }

    private mutating func append(_ string: String) {
        if let data = string.data(using: .utf8) { body.append(data) }
    }
}

// Usage
var form = MultipartFormData()
form.addTextField(name: "user_id", value: userId)
form.addFileField(name: "avatar", filename: "avatar.jpg", data: imageData)
let (body, contentType) = form.finalize()

var request = URLRequest(url: uploadURL)
request.httpMethod = "POST"
request.setValue(contentType, forHTTPHeaderField: "Content-Type")
request.httpBody = body
```

---

## Section 8: Network Reachability + Offline Queue

See [references/offline-queue.md](references/offline-queue.md) — `NWPathMonitor` `@Observable` wrapper, actor-based offline queue, drain-on-reconnect pattern, and `isExpensive` (cellular) detection.

---

## Section 9: Request Deduplication

```swift
// Prevents duplicate network calls when multiple views request the same resource simultaneously.
actor RequestDeduplicator {
    private var inFlight: [String: Task<Data, Error>] = [:]

    func fetch(key: String, perform: @escaping () async throws -> Data) async throws -> Data {
        if let existing = inFlight[key] {
            return try await existing.value   // piggyback — no new request
        }

        let task = Task<Data, Error> {
            defer { Task { await self.remove(key: key) } }
            return try await perform()
        }
        inFlight[key] = task
        return try await task.value
    }

    private func remove(key: String) { inFlight.removeValue(forKey: key) }
}

// Usage: 10 cells requesting same avatar → 1 HTTP call
let deduplicator = RequestDeduplicator()
let avatarData = try await deduplicator.fetch(key: "avatar-\(userId)") {
    try await session.data(from: avatarURL).0
}
```

---

## Section 10: Combine + URLSession (Legacy)

See [references/combine-networking.md](references/combine-networking.md). Use `async/await` for all new networking. Combine is only relevant when chaining with other Combine publishers (e.g. debounced search, timer-based polling).

---

## Section 11: Structured Concurrency

Use `async-let` for parallel independent requests; `withThrowingTaskGroup` for dynamic fan-out.

```swift
// async-let — parallel, compile-time fixed set of requests
async let user    = client.request(.user(id: userId)) as UserProfile
async let orders  = client.request(.orders(userId: userId)) as [Order]
async let stats   = client.request(.stats(userId: userId)) as DashboardStats
let (profile, orderList, dashboard) = try await (user, orders, stats)
// Total time: max(t1, t2, t3) — not t1 + t2 + t3

// Task group — dynamic fan-out (N items, N concurrent requests)
func fetchAll(ids: [String]) async throws -> [UserProfile] {
    try await withThrowingTaskGroup(of: UserProfile.self) { group in
        for id in ids { group.addTask { try await self.client.request(.user(id: id)) } }
        var results: [UserProfile] = []
        for try await profile in group { results.append(profile) }
        return results
    }
}
```

**Data race rule**: Never mutate shared state from inside `addTask` closures. Return values; collect via `for await` sequentially outside the group.

See [references/structured-concurrency.md](references/structured-concurrency.md) for bounded concurrency, cancellation propagation, Task priorities, and detached tasks.

---

## Section 12: Production Anti-Patterns

| Anti-Pattern | Consequence | Fix |
|---|---|---|
| `URLSession.shared` for background transfers | Transfer cancelled when app backgrounds | `URLSessionConfiguration.background(withIdentifier:)` |
| Force-cast `response as! HTTPURLResponse` | Crash on non-HTTP responses | `guard let http = response as? HTTPURLResponse` |
| No retry on 5xx | Users see errors on transient server failures | Exponential backoff, max 3 attempts |
| Multiple 401 handlers each refresh independently | N concurrent requests = N token refresh calls | Deduplicate with actor + stored `Task` |
| Certificate pinning in DEBUG builds | Cannot proxy traffic in Charles/Proxyman | Wrap pinning in `#if !DEBUG` |
| Hardcoded base URL | Different environments need code changes | `Config.apiBaseURL` from xcconfig |
| Default 60s `URLRequest` timeout | Users wait too long on poor connections | 30s standard, 300s uploads |
| Storing refresh tokens in UserDefaults | Token readable by other processes | Always Keychain for tokens |
| Data-based background upload | Upload silently fails in background | File-based `uploadTask(with:fromFile:)` only |
| Ignoring `Retry-After` on 429 | Banned by server for hammering | Read header, sleep exact duration |

---

## REST Client Assembly Checklist

```
[ ] NetworkClient actor — generic typed request<T: Decodable>
[ ] Endpoint enum/struct — type-safe path, method, body, auth flag
[ ] AuthenticatedClient — wraps NetworkClient, intercepts 401, deduplicates refresh
[ ] TokenStore — Keychain-backed, never UserDefaults
[ ] RequestDeduplicator — actor with inFlight Task dictionary
[ ] RetryPolicy — exponential backoff, 5xx only, max 3 attempts
[ ] NetworkMonitor — NWPathMonitor, @Published isConnected
[ ] OfflineQueue — actor, drains on reconnect
[ ] BackgroundTransferManager — separate URLSession with background config
[ ] Certificate pinning — PinnedSessionDelegate, disabled in DEBUG
[ ] Multipart helper — boundary generation, field/file append
[ ] Config.apiBaseURL — from xcconfig, environment-specific
[ ] Unit tests — mock URLProtocol, test retry, 401 refresh, deduplication
```
