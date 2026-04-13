---
name: ios-monetization
description: StoreKit 2 in-app purchases, subscriptions, and monetization for iOS
  apps. Use when implementing consumables, non-consumables, auto-renewable subscriptions,
  paywall UI, receipt validation, or App Store Connect configuration.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Monetization — StoreKit 2

<!-- dual-compat-start -->
## Use When

- StoreKit 2 in-app purchases, subscriptions, and monetization for iOS apps. Use when implementing consumables, non-consumables, auto-renewable subscriptions, paywall UI, receipt validation, or App Store Connect configuration.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-monetization` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Architecture Principles

StoreKit 2 is async/await-native. The entire `SKPaymentQueue`/delegate callback model is abandoned. Every purchase, verification, and entitlement check is a Swift concurrency operation.

**Transaction observer is not optional.** It must start at app entry point — before any UI renders. Transactions that completed while the app was terminated are delivered via `Transaction.updates` on next launch. Starting this loop in the paywall means you silently drop those deliveries.

```swift
// App.swift — Swift 6 actor-isolated entry point
@main
struct MyApp: App {
    @StateObject private var store = StoreService()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(store)
                .task { await store.observeTransactions() }
        }
    }
}
```

---

## StoreService — Core Implementation

```swift
import StoreKit

@MainActor
final class StoreService: ObservableObject {
    @Published private(set) var products: [Product] = []
    @Published private(set) var purchasedProductIDs: Set<String> = []

    private var transactionObserver: Task<Void, Never>?

    init() {
        transactionObserver = Task { await observeTransactions() }
    }

    deinit {
        transactionObserver?.cancel()
    }

    // MARK: - Product Loading

    func loadProducts(ids: [String]) async {
        do {
            products = try await Product.products(for: ids)
            // Products come back unordered — sort by price or custom order
            products.sort { $0.price < $1.price }
        } catch {
            // StoreKitError.networkError — retry with backoff
            // StoreKitError.notEntitled — sandbox/config issue
        }
    }

    // MARK: - Transaction Observer (MUST run for app lifetime)

    func observeTransactions() async {
        for await result in Transaction.updates {
            await process(result)
        }
    }

    // MARK: - Purchase

    func purchase(_ product: Product,
                  options: Set<Product.PurchaseOption> = []) async throws -> Transaction? {
        let result = try await product.purchase(options: options)
        switch result {
        case .success(let verification):
            let transaction = try checkVerified(verification)
            await updateEntitlements(transaction)
            await transaction.finish()   // CRITICAL — unfinished = re-delivered on next launch
            return transaction
        case .userCancelled:
            return nil
        case .pending:
            // Awaiting Ask to Buy or billing fix — show "payment pending" UI
            return nil
        @unknown default:
            return nil
        }
    }

    // MARK: - Entitlement Refresh

    func refreshEntitlements() async {
        purchasedProductIDs.removeAll()
        for await result in Transaction.currentEntitlements {
            guard case .verified(let transaction) = result else { continue }
            guard transaction.revocationDate == nil else { continue }  // Apple refunded
            purchasedProductIDs.insert(transaction.productID)
        }
    }

    // MARK: - Restore

    func restore() async throws {
        // AppStore.sync() triggers re-validation + re-delivery of current entitlements
        // Do NOT use SKPaymentQueue.restoreCompletedTransactions — it is deprecated
        try await AppStore.sync()
        await refreshEntitlements()
    }

    // MARK: - Private

    private func process(_ result: VerificationResult<Transaction>) async {
        await updateEntitlements(try? checkVerified(result))
    }

    private func updateEntitlements(_ transaction: Transaction?) async {
        guard let transaction else { return }
        if transaction.revocationDate == nil {
            purchasedProductIDs.insert(transaction.productID)
        } else {
            purchasedProductIDs.remove(transaction.productID)
        }
    }

    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified:
            // JWS signature invalid — tampered receipt or configuration error
            throw StoreError.failedVerification
        case .verified(let value):
            return value
        }
    }
}

enum StoreError: LocalizedError {
    case failedVerification
    var errorDescription: String? { "Purchase could not be verified." }
}
```

---

## Subscription Status — Full Detail

`Transaction.currentEntitlements` gives current owned state. `Product.subscription?.status` gives renewal metadata.

```swift
struct SubscriptionStatus {
    let isActive: Bool
    let willAutoRenew: Bool
    let expirationDate: Date?
    let isInBillingRetry: Bool
    let scheduledDowngradeProductID: String?
}

func subscriptionStatus(for product: Product) async -> SubscriptionStatus? {
    guard let subscription = product.subscription,
          let statusArray = try? await subscription.status else { return nil }

    // statusArray contains one entry per subscription in the group
    for status in statusArray {
        guard case .verified(let renewalInfo) = status.renewalInfo,
              case .verified(let transaction) = status.transaction else { continue }

        let isActive = status.state == .subscribed || status.state == .inGracePeriod
        return SubscriptionStatus(
            isActive: isActive,
            willAutoRenew: renewalInfo.willAutoRenew,
            expirationDate: transaction.expirationDate,
            isInBillingRetry: status.state == .inBillingRetryPeriod,
            scheduledDowngradeProductID: renewalInfo.autoRenewProductID != product.id
                ? renewalInfo.autoRenewProductID : nil
        )
    }
    return nil
}
```

Subscription states to handle:

| State | Meaning | Action |
|---|---|---|
| `.subscribed` | Active | Full access |
| `.inGracePeriod` | Billing failed, grace period active | Full access + soft prompt |
| `.inBillingRetryPeriod` | Grace expired, Apple retrying | Restricted access + hard prompt |
| `.expired` | Lapsed | Paywall |
| `.revoked` | Family sharing revoked | Remove access immediately |

---

## Introductory Offers

Intro offers are Apple ID-scoped — once consumed, the user is ineligible forever. Check before displaying.

```swift
func introOfferDetails(for product: Product) async -> Product.SubscriptionOffer? {
    guard let subscription = product.subscription,
          await subscription.isEligibleForIntroOffer == true else { return nil }
    return subscription.introductoryOffer
}

// Render based on paymentMode
func introLabel(_ offer: Product.SubscriptionOffer) -> String {
    switch offer.paymentMode {
    case .freeTrial:
        return "Free for \(offer.period.localizedDescription)"
    case .payAsYouGo:
        return "\(offer.displayPrice)/\(offer.period.value) \(offer.period.unit) for \(offer.periodCount) periods"
    case .payUpFront:
        return "\(offer.displayPrice) for \(offer.periodCount) periods"
    @unknown default:
        return offer.displayPrice
    }
}
```

---

## Promotional Offers (Win-Back / Loyalty)

Promotional offers require a server-generated signature. The signature proves your server authorised the discount.

```swift
// Server returns: keyID, nonce, signature, timestamp
let offerID = "annual_winback_50"
let signature = try await fetchPromoSignature(productID: product.id, offerID: offerID)

let purchaseOption = Product.PurchaseOption.promotionalOffer(
    offerID: offerID,
    keyID: signature.keyID,
    nonce: signature.nonce,
    signature: signature.data,
    timestamp: signature.timestamp
)
let transaction = try await storeService.purchase(product, options: [purchaseOption])
```

Never hard-code or generate signatures client-side — App Store will reject them.

---

## Paywall ViewModel

```swift
@MainActor
final class PaywallViewModel: ObservableObject {
    enum PurchaseState: Equatable {
        case idle, loading, purchasing, purchased, failed(String)
    }

    @Published var products: [Product] = []
    @Published var purchaseState: PurchaseState = .idle
    @Published var selectedProduct: Product?
    @Published var introOffer: Product.SubscriptionOffer?

    private let store: StoreService

    init(store: StoreService) {
        self.store = store
    }

    func load(productIDs: [String]) async {
        purchaseState = .loading
        await store.loadProducts(ids: productIDs)
        products = store.products
        selectedProduct = products.first(where: { $0.type == .autoRenewable })
        if let selected = selectedProduct {
            introOffer = await introOfferDetails(for: selected)
        }
        purchaseState = .idle
    }

    func purchase() async {
        guard let product = selectedProduct else { return }
        purchaseState = .purchasing
        do {
            guard try await store.purchase(product) != nil else {
                // userCancelled or pending — no error, just reset
                purchaseState = .idle
                return
            }
            purchaseState = .purchased
        } catch {
            purchaseState = .failed(error.localizedDescription)
        }
    }

    func restore() async {
        purchaseState = .loading
        do {
            try await store.restore()
            purchaseState = store.purchasedProductIDs.isEmpty ? .idle : .purchased
        } catch {
            purchaseState = .failed(error.localizedDescription)
        }
    }
}
```

---

## Receipt Validation — JWS vs Legacy

StoreKit 2 signs every transaction as a JWS (JSON Web Signature). You do not need the old base64 `appReceipt` + `/verifyReceipt` endpoint.

**Client-side (sufficient for most apps):**
`VerificationResult.verified` means Apple's signature checked out locally. Use this.

**Server-side (required for high-value entitlements, fraud prevention):**

```
1. Decode JWS: split by ".", base64url-decode payload
2. Verify signature using Apple's public key from WWDR certificate chain
3. Check: environment, bundleID, productID, expirationDate, revocationDate
4. Use App Store Server API for real-time status (not polled receipts)
```

App Store Server Notifications v2 (webhooks) push events to your server:
- `DID_RENEW`, `EXPIRED`, `REFUND`, `GRACE_PERIOD_EXPIRED`, `REVOKE`

Register the endpoint in App Store Connect > App Information > App Store Server Notifications.

---

## Consumables — Delivery Pattern

Consumables are **not** tracked by `Transaction.currentEntitlements`. You must persist delivery yourself.

```swift
func purchaseConsumable(_ product: Product) async throws {
    guard let transaction = try await store.purchase(product) else { return }
    // Deliver immediately before finish — if app crashes between deliver+finish,
    // transaction re-delivers on next launch via Transaction.updates
    await deliverConsumable(transaction.productID, quantity: transaction.purchasedQuantity)
    await transaction.finish()
}

// Idempotency: store transaction.id in your DB — re-delivery must not double-grant
func deliverConsumable(_ productID: String, quantity: Int) async {
    // Check if transaction.id already processed before crediting
}
```

---

## App Store Connect Configuration — Critical Steps

1. Create IAPs **before** running on device — Xcode cannot synthesise them
2. Subscription Group required before adding Auto-Renewable subscriptions; group name is user-visible in cancellation flow
3. All tiers in the same subscription group share one active subscription; Apple handles proration on upgrades automatically
4. Localisations on products are required — missing localisation = product not returned by `Product.products(for:)`
5. Tax categories must be set (Software, Newspaper, etc.) — affects storefront availability
6. Pricing: set a base territory first, then "Sync" to all territories — do not set each manually
7. Sandbox testers created in App Store Connect > Users and Access > Sandbox Testers — use a new Apple ID, not your own

---

## StoreKit Configuration File (Local Testing)

Add a `.storekit` file to the Xcode project, configure via Edit Scheme > Run > Options > StoreKit Configuration. This bypasses App Store Connect entirely.

Non-obvious capabilities of the config file:
- Simulate interrupted purchases (requires StoreKit testing in-process)
- Set transaction speed to "Monthly" = 1 minute, "Annual" = 12 minutes in sandbox
- Trigger refunds and revocations from Xcode debug menu
- Test subscription state transitions without waiting for real time

```swift
// In XCTest — use SKTestSession to script scenarios
import StoreKitTest

class SubscriptionTests: XCTestCase {
    var session: SKTestSession!

    override func setUp() async throws {
        session = try SKTestSession(configurationFileNamed: "Products")
        session.resetToDefaultState()
        session.disableDialogs = true
        session.timeRate = .monthlyRenewalEveryThirtySeconds
    }

    func testSubscriptionRenews() async throws {
        let store = StoreService()
        // purchase → wait 30s → verify renewal transaction delivered
    }
}
```

---

## Anti-Patterns

| Anti-Pattern | Consequence | Fix |
|---|---|---|
| Start `Transaction.updates` in paywall | Miss offline/terminated-app purchases | Start in App init or `@main` `.task` |
| Forget `transaction.finish()` | Re-delivered on every launch, double grants | Always finish after delivery |
| Use `SKPaymentQueue.restoreCompletedTransactions` | Deprecated, triggers App Store login alert unnecessarily | Use `AppStore.sync()` |
| Poll `isSubscribed()` on every `onAppear` | Rate limiting, perf degradation | Cache state, invalidate on `Transaction.updates` |
| Trust `.unverified` transactions | Security hole — spoofed purchase | Always throw/ignore unverified |
| Consumable delivery after `finish()` | Lost delivery if crash between them | Deliver first, then finish |
| Test with production Apple ID | Real charges, irreversible | Always use sandbox account |
| One product ID for multiple tiers | Cannot offer upgrade pricing or group logic | Separate product per tier |
| Not handling `.pending` state | User sees no feedback; assume purchase failed | Show "payment pending" UI |
| Client-side promo offer signatures | Rejected by App Store | Server-generated only |
| Infer subscription active from purchase date + duration | Clock skew, grace periods, billing retry | Use `Transaction.currentEntitlements` |
| Show intro offer without eligibility check | Offer silently fails; user confused | Always check `isEligibleForIntroOffer` |

---

## Launch Checklist

- [ ] `Transaction.updates` loop started at app entry point, not in paywall
- [ ] All transactions finished with `transaction.finish()` after delivery
- [ ] `Transaction.currentEntitlements` queried on app launch to restore entitlement state
- [ ] `transaction.revocationDate != nil` check before granting access
- [ ] Introductory offer eligibility verified before displaying offer UI
- [ ] `AppStore.sync()` called from Restore Purchases button
- [ ] `.pending` purchase state handled with visible user feedback
- [ ] Consumable delivery is idempotent (transaction ID deduplication)
- [ ] Sandbox test accounts created in App Store Connect
- [ ] StoreKit Config File added for local automated testing
- [ ] App Store Server Notifications v2 endpoint registered for subscriptions
- [ ] Server-side JWS validation implemented for high-value entitlements
- [ ] Subscription group configured in App Store Connect before testing
- [ ] All product localisations complete — missing localisation silently drops product
