# Network Reachability + Offline Queue

## NWPathMonitor — @Observable Wrapper (iOS 17+)

```swift
import Network

@Observable
final class NetworkMonitor {
    static let shared = NetworkMonitor()
    private(set) var isConnected = true
    private(set) var isExpensive = false   // true = cellular connection

    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "com.app.network-monitor", qos: .utility)

    private init() {
        monitor.pathUpdateHandler = { [weak self] path in
            Task { @MainActor [weak self] in
                self?.isConnected = path.status == .satisfied
                self?.isExpensive = path.isExpensive
            }
        }
        monitor.start(queue: queue)
    }

    deinit { monitor.cancel() }
}

// SwiftUI usage
@Environment(NetworkMonitor.self) private var network
if !network.isConnected { OfflineBanner() }
```

## Actor-Based Offline Queue

Persists failed mutations in memory; drains automatically on reconnect.

```swift
actor OfflineQueue {
    private var pending: [QueuedRequest] = []

    struct QueuedRequest {
        let endpoint: Endpoint
        let enqueuedAt: Date
    }

    func enqueue(_ endpoint: Endpoint) {
        pending.append(QueuedRequest(endpoint: endpoint, enqueuedAt: Date()))
    }

    func startObservingConnectivity(client: AuthenticatedClient) {
        Task {
            // Poll connectivity — use NotificationCenter or Combine if preferred
            for await isConnected in connectivityStream() where isConnected {
                await drain(using: client)
            }
        }
    }

    private func drain(using client: AuthenticatedClient) async {
        let snapshot = pending
        pending.removeAll()
        for queued in snapshot {
            do {
                let _: EmptyResponse = try await client.request(queued.endpoint)
            } catch {
                pending.append(queued)   // re-enqueue on failure
            }
        }
    }
}
```

**For persistent offline queue** (survives app restart): use `PendingOperation` model in SwiftData. See `ios-data-persistence` skill Section 6.1–6.3.

## When to Use Each

| Scenario | Use |
|---|---|
| Short-lived actions (button taps) during brief network loss | In-memory `OfflineQueue` |
| Long operations that must survive app restart/kill | SwiftData `PendingOperation` + `SyncEngine` |
| Read operations with stale-while-revalidate | Repository cache fallback |
