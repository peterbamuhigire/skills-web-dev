# Interface Control Document (ICD) -- Template & Guide

**Back to:** [SDLC Design Skill](../SKILL.md)

## Purpose

Specifies **all interfaces** between system components and external systems -- protocols, data formats, authentication, error handling, and versioning. This is the contract that integration teams, frontend developers, and mobile developers rely on.

## Audience

Integration engineers, API consumers, frontend/backend teams, third-party integrators.

## When to Create

- After the SDD defines component boundaries and the Technical Spec defines API details
- Before any cross-team integration work begins
- When adding external system integrations (payment gateways, SMS, email)

## Typical Length

15-30 pages. Split into subdirectory files for large interface inventories.

---

## Template

```markdown
# [Project Name] -- Interface Control Document

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**SDD Reference:** [Link to System Design Document]

---

## 1. Interface Inventory

| ID | Name | Type | Provider | Consumer | Protocol | Auth |
|----|------|------|----------|----------|----------|------|
| IF-001 | Web Admin API | REST | PHP Backend | Web Frontend (Tabler) | HTTPS | Session + CSRF |
| IF-002 | Mobile API | REST | PHP Backend | Android App (Retrofit) | HTTPS | JWT Bearer |
| IF-003 | Super Admin API | REST | PHP Backend | Admin Panel (Tabler) | HTTPS | Session + CSRF |
| IF-004 | Database Connection | TCP | MySQL 8.x | PHP Backend (PDO) | MySQL Protocol | Credentials |
| IF-005 | Android Layer Boundary | Internal | Data Layer | Domain Layer | Function Call | N/A |
| IF-006 | Payment Gateway | REST | M-Pesa / Paystack | PHP Backend | HTTPS | API Key + Webhook |
| IF-007 | SMS Service | REST | SMS Provider | PHP Backend | HTTPS | API Key |
| IF-008 | Email Service | SMTP/API | Email Provider | PHP Backend | SMTP/HTTPS | Credentials |
| IF-009 | File Storage | Filesystem | Local/Cloud | PHP Backend | Filesystem/S3 | Credentials |

---

## 2. Internal Interfaces

### 2.1 Backend <-> Database (IF-004)

**Protocol:** MySQL wire protocol via PDO
**Connection:** Persistent connections with connection pooling

| Attribute | Value |
|-----------|-------|
| Driver | PDO MySQL (mysqlnd) |
| Charset | utf8mb4 |
| Collation | utf8mb4_general_ci |
| Max connections | 100 (configurable per environment) |
| Query timeout | 30 seconds |

**Query Patterns:**
- ALL tenant-scoped queries MUST include `WHERE franchise_id = ?`
- franchise_id is ALWAYS parameterized (never string concatenation)
- franchise_id comes from session/JWT, NEVER from client request body

**Example:**
```php
$stmt = $pdo->prepare(
    "SELECT id, name, price FROM products
     WHERE franchise_id = :franchise_id AND status = 'active'
     ORDER BY name ASC LIMIT :limit OFFSET :offset"
);
$stmt->execute([
    ':franchise_id' => $auth->getFranchiseId(),
    ':limit' => $perPage,
    ':offset' => ($page - 1) * $perPage,
]);
```

### 2.2 Backend <-> Mobile App (IF-002)

**Protocol:** HTTPS REST API
**Base URL:** `https://{domain}/api/`
**Authentication:** JWT Bearer token in Authorization header
**Content-Type:** `application/json` (requests and responses)

**Request Format:**
```
POST /api/products/create.php HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiI...
Content-Type: application/json

{"name": "Widget", "price": 25.50}
```

**Response Format (success):**
```json
{
  "success": true,
  "message": "Product created",
  "data": { "id": 42, "name": "Widget" }
}
```

**Response Format (error):**
```json
{
  "success": false,
  "message": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "errors": { "name": ["Name is required"] }
}
```

**Token Lifecycle:**
| Token | Lifetime | Storage | Refresh |
|-------|----------|---------|---------|
| Access Token | 1 hour | EncryptedSharedPreferences | Via refresh endpoint |
| Refresh Token | 30 days | EncryptedSharedPreferences | Via login |

See: `dual-auth-rbac` skill for full token rotation and breach detection.

### 2.3 Backend <-> Web Frontend (IF-001, IF-003)

**Protocol:** HTTPS (AJAX/fetch calls from JavaScript to PHP endpoints)
**Authentication:** PHP session cookie + CSRF token
**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

**CSRF Protection:**
- Server generates CSRF token per session
- Client sends token in `X-CSRF-Token` header or hidden form field
- Server validates token on all POST/PUT/DELETE requests

**Session Scoping:**
| Panel | Session Prefix | Cookie Path |
|-------|---------------|-------------|
| /public/ | pub_ | /public/ |
| /adminpanel/ | adm_ | /adminpanel/ |
| /memberpanel/ | mem_ | /memberpanel/ |

**AJAX Call Pattern (JavaScript):**
```javascript
async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content,
        },
        credentials: 'same-origin',
    };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(`/api/${endpoint}`, options);
    const data = await response.json();

    if (!data.success) {
        Swal.fire({ icon: 'error', title: 'Error', text: data.message });
        throw new Error(data.message);
    }
    return data;
}
```

### 2.4 Android Layer Boundaries (IF-005)

**Presentation -> Domain:** ViewModels call Use Cases
**Domain -> Data:** Use Cases call Repository interfaces
**Data -> Remote:** Repository implementations call Retrofit API services
**Data -> Local:** Repository implementations call Room DAOs

| Boundary | Contract Type | Example |
|----------|--------------|---------|
| ViewModel -> UseCase | Kotlin interface + suspend function | `GetProductsUseCase.invoke(page)` |
| UseCase -> Repository | Kotlin interface in domain layer | `ProductRepository.getProducts(page)` |
| Repository -> API | Retrofit interface | `ProductApiService.getProducts(page)` |
| Repository -> Room | DAO abstract class | `ProductDao.getAll()` |

**Data Flow (online):**
```
UI -> ViewModel -> UseCase -> Repository -> Retrofit -> PHP API -> MySQL
```

**Data Flow (offline):**
```
UI -> ViewModel -> UseCase -> Repository -> Room (local cache)
```

---

## 3. External Interfaces

### 3.1 Payment Gateway (IF-006)

[Repeat this block per payment provider.]

| Attribute | Value |
|-----------|-------|
| Provider | M-Pesa / Paystack / Stripe |
| Protocol | HTTPS REST |
| Auth | API Key + Secret (server-side only) |
| Webhook | POST callback to `/api/webhooks/payment.php` |
| Sandbox | Separate API keys for dev/staging |

**Webhook Security:**
- Verify signature/hash in webhook header before processing
- Respond with 200 within 5 seconds (process async if needed)
- Idempotent: handle duplicate webhook deliveries gracefully
- Log all webhook payloads for audit trail

**Webhook Payload Example:**
```json
{
  "event": "payment.completed",
  "data": {
    "transaction_id": "TXN-123456",
    "amount": 5000.00,
    "currency": "KES",
    "reference": "INV-2026-0042",
    "status": "success"
  },
  "timestamp": "2026-02-20T10:30:00Z"
}
```

### 3.2 SMS/Email Services (IF-007, IF-008)

| Attribute | SMS | Email |
|-----------|-----|-------|
| Protocol | REST API | SMTP or REST API |
| Auth | API Key | SMTP credentials or API Key |
| Rate Limit | Provider-specific | Provider-specific |
| Retry | 3 attempts, exponential backoff | 3 attempts, exponential backoff |
| Templating | Server-side string replacement | HTML email templates |

**Notification Delivery Pattern:**
```php
// Queue-based: fire and forget with retry
$notificationService->send(
    type: 'sms',
    to: $customer->phone,
    template: 'order_confirmation',
    data: ['order_id' => $orderId, 'total' => $total]
);
```

### 3.3 File Storage (IF-009)

| Attribute | Development | Staging/Production |
|-----------|------------|-------------------|
| Storage | Local filesystem | Local filesystem or S3-compatible |
| Upload path | `/uploads/{franchise_id}/{module}/` | Same pattern |
| Max file size | 10 MB | 10 MB |
| Allowed types | jpg, png, pdf, xlsx, csv | Same |
| Access control | franchise_id scoping on read | Same |

---

## 4. Interface Specifications (Per-Interface Detail)

[For critical interfaces, provide this detailed specification.]

### IF-002: Mobile API -- Detailed Specification

**Protocol:** HTTPS REST (TLS 1.2+)
**Data Format:** JSON (UTF-8)
**Authentication:** JWT Bearer token (RS256)
**Versioning:** URL path prefix `/api/v1/` (for future breaking changes)

**Standard Headers:**

| Header | Direction | Required | Value |
|--------|-----------|----------|-------|
| Content-Type | Request | Yes | application/json |
| Authorization | Request | Yes (except login) | Bearer {access_token} |
| Accept | Request | Recommended | application/json |
| X-App-Version | Request | Recommended | 1.0.0 |
| X-Platform | Request | Recommended | android |

**Rate Limits:**

| Endpoint Group | Limit | Window | Action on Exceed |
|---------------|-------|--------|-----------------|
| Authentication | 10 | 1 minute | 429 Too Many Requests |
| Read operations | 120 | 1 minute | 429 Too Many Requests |
| Write operations | 60 | 1 minute | 429 Too Many Requests |
| File uploads | 20 | 1 minute | 429 Too Many Requests |

---

## 5. Interface Change Management

### 5.1 Breaking vs Non-Breaking Changes

| Change Type | Breaking? | Requires Version Bump? |
|------------|-----------|----------------------|
| Add new endpoint | No | No |
| Add optional field to response | No | No |
| Add optional query parameter | No | No |
| Remove or rename field | Yes | Yes |
| Change field type | Yes | Yes |
| Remove endpoint | Yes | Yes |
| Change authentication method | Yes | Yes |

### 5.2 Change Process

1. **Propose:** Document the change in an ADR (see SDD)
2. **Notify:** Alert all consumer teams at least 2 sprints before breaking change
3. **Implement:** Add new version alongside old (parallel running)
4. **Migrate:** Consumer teams update to new version
5. **Deprecate:** Mark old version as deprecated with sunset date
6. **Remove:** Remove old version after sunset date (minimum 3 months)

### 5.3 Versioning Strategy

- **URL versioning:** `/api/v1/`, `/api/v2/` for major breaking changes
- **Within version:** Non-breaking additions are backward-compatible
- **Deprecation header:** `Sunset: Sat, 01 Jun 2026 00:00:00 GMT`

---

## 6. Testing Strategy for Interfaces

### 6.1 Contract Testing

- Verify request/response schemas match this ICD
- Use automated schema validation in CI/CD
- Mobile team and web team run contract tests against staging API

### 6.2 Mock Servers

- Provide mock server for mobile team during parallel development
- Mock server implements this ICD's response schemas
- External webhooks: use provider sandbox environments for testing

### 6.3 Integration Testing Checklist

- [ ] Authentication flow works end-to-end (login, token refresh, logout)
- [ ] Tenant isolation verified (User A cannot see User B's data)
- [ ] Error responses match ICD format for all error codes
- [ ] Pagination works correctly for list endpoints
- [ ] File upload/download respects size limits and type restrictions
- [ ] Webhook signature verification rejects tampered payloads
- [ ] Rate limiting returns 429 and Retry-After header
- [ ] Offline fallback works on Android (Room cache serves data)

---

## 7. Interface Monitoring & Health Checks

| Monitor | What It Checks | Alert Threshold |
|---------|---------------|-----------------|
| API Health | `/api/health.php` returns 200 | > 3 consecutive failures |
| DB Connection | PDO connect succeeds | Any failure |
| Response Time | p95 latency of API endpoints | > 2 seconds |
| Error Rate | 5xx responses / total responses | > 1% in 5-minute window |
| Webhook Delivery | Payment webhook processing success | > 2 failures in 1 hour |
| SSL Certificate | Certificate expiry date | < 14 days before expiry |
```

---

## Section-by-Section Guidance

| Section | Key Guidance |
|---------|-------------|
| Interface Inventory | List EVERY interface, even internal ones. Assign unique IDs. |
| Internal Interfaces | Show code examples for each communication pattern. |
| External Interfaces | Document webhook security, idempotency, and retry policies. |
| Detailed Specs | Only needed for critical or complex interfaces. |
| Change Management | Define breaking vs non-breaking before development starts. |
| Testing | Include contract tests and mock server availability. |
| Monitoring | Define alert thresholds with specific numbers. |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Undocumented interfaces | Teams guess at contracts, causing integration bugs | Document every interface in the inventory table |
| Breaking changes without versioning | Consumers break silently | Use URL versioning and deprecation headers |
| No webhook signature verification | Security vulnerability (spoofed webhooks) | Always verify webhook signatures |
| Hardcoded franchise_id in queries | Tenant data leakage | Extract from session/JWT via middleware |
| No rate limiting | API abuse, denial of service | Define and enforce rate limits per endpoint group |
| Missing error response format | Each developer invents their own error format | Use standardized error envelope (api-error-handling) |
| No CSRF protection on web forms | Cross-site request forgery attacks | Include CSRF token in all state-changing web requests |

## Quality Checklist

- [ ] Interface inventory table is complete (all interfaces listed with IDs)
- [ ] Every internal interface has a code example
- [ ] External interfaces document webhook security and retry policies
- [ ] Authentication method specified for every interface
- [ ] Rate limits defined for API interfaces
- [ ] Breaking vs non-breaking change policy documented
- [ ] Interface versioning strategy defined
- [ ] Testing strategy includes contract tests and mock servers
- [ ] Monitoring and health check endpoints specified
- [ ] All JSON examples are valid and complete
- [ ] franchise_id sourcing documented (from auth, never from client)
- [ ] CSRF protection documented for web interfaces

---

**Back to:** [SDLC Design Skill](../SKILL.md) | **Related:** [API Documentation](api-documentation.md) | [System Design Document](system-design-document.md)
