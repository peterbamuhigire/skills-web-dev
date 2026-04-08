# Combine + URLSession Networking

Legacy reference. Load only when maintaining Combine-based networking code or integrating with a Combine publisher chain.

**Prefer async/await** for all new networking code. Use Combine only when the result must chain with other Combine publishers (e.g., timer-based retries, debounced search).

---

## URLSession Publisher Extension

```swift
extension URLSession {
    func publisher<T: Decodable>(for endpoint: Endpoint,
                                  token: String?,
                                  decoder: JSONDecoder = .init()) -> AnyPublisher<T, NetworkError> {
        guard let request = try? endpoint.urlRequest(token: token) else {
            return Fail(error: NetworkError.invalidURL).eraseToAnyPublisher()
        }
        return dataTaskPublisher(for: request)
            .tryMap { output -> Data in
                guard let http = output.response as? HTTPURLResponse else { throw NetworkError.noData }
                switch http.statusCode {
                case 200...299: return output.data
                case 401:       throw NetworkError.unauthorized
                case 403:       throw NetworkError.forbidden
                default:        throw NetworkError.httpError(statusCode: http.statusCode, data: output.data)
                }
            }
            .decode(type: T.self, decoder: decoder)
            .mapError { error -> NetworkError in
                switch error {
                case let ne as NetworkError: return ne
                case is DecodingError:       return NetworkError.decodingFailed(error)
                default:                     return NetworkError.httpError(statusCode: 0, data: nil)
                }
            }
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}
```

## Combine Retry with Token Refresh

```swift
session.publisher(for: endpoint, token: token)
    .retry(2)
    .catch { error -> AnyPublisher<UserProfile, NetworkError> in
        guard case .unauthorized = error else {
            return Fail(error: error).eraseToAnyPublisher()
        }
        return refreshAndRetry(endpoint: endpoint)
    }
    .sink(receiveCompletion: { _ in }, receiveValue: { profile in /* ... */ })
    .store(in: &cancellables)
```

## Migration Path to async/await

```swift
// Combine publisher → async/await bridge
let profile = try await session.publisher(for: endpoint, token: token).values.first(where: { _ in true })

// Or use .value on single-value publishers (Combine 2021+)
let profile: UserProfile = try await session.publisher(for: endpoint, token: token).value
```
