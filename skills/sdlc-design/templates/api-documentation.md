# API Documentation -- Template & Guide

**Back to:** [SDLC Design Skill](../SKILL.md)

## Purpose

Comprehensive **consumer-facing API reference** for frontend developers, mobile developers, and third-party integrators. This document tells API consumers everything they need to call your APIs correctly.

## Audience

Frontend developers (JavaScript/Tabler), mobile developers (Kotlin/Retrofit), third-party integrators.

## When to Create

- After the Technical Specification defines endpoint contracts
- Before frontend or mobile development begins
- When onboarding third-party integrators

## Typical Length

20-40 pages. Split into `05-api/` subdirectory files for large endpoint inventories.

## Important Cross-References

- **`api-error-handling` skill** -- Error response format and SweetAlert2 integration
- **`api-pagination` skill** -- Pagination request/response patterns
- **`dual-auth-rbac` skill** -- Authentication and authorization flows

---

## Template

```markdown
# [Project Name] -- API Documentation

**Version:** 1.0
**API Base URL:** https://[domain]/api/
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Published

---

## 1. API Overview

### 1.1 Base URLs

| Environment | Base URL | Purpose |
|------------|---------|---------|
| Development | http://localhost/[project]/api/ | Local development |
| Staging | https://staging.[domain]/api/ | QA testing, client demos |
| Production | https://[domain]/api/ | Live traffic |

### 1.2 Content Types

| Content-Type | When Used |
|-------------|-----------|
| application/json | All standard requests and responses |
| multipart/form-data | File uploads (images, documents) |

### 1.3 Versioning

- Current version: v1 (implicit, no URL prefix needed)
- Future breaking changes: `/api/v2/` URL prefix
- Non-breaking additions are backward-compatible within a version
- Deprecation notice: `Sunset` header with retirement date

---

## 2. Authentication & Authorization

### 2.1 Authentication Methods

| Method | Client | How It Works |
|--------|--------|-------------|
| Session + CSRF | Web frontend (Tabler) | PHP session cookie + CSRF token in header |
| JWT Bearer | Mobile app (Android) | Access token in Authorization header |
| API Key | Third-party integrators | API key in X-API-Key header |

### 2.2 Session Authentication (Web)

**Login:** `POST /api/auth/login.php` with `{"username": "...", "password": "..."}`
**Response:** Returns `user` object, `csrf_token`, and `redirect` URL.
**Subsequent Requests:** Session cookie sent automatically; include `X-CSRF-Token` header.

### 2.3 JWT Authentication (Mobile)

**Login:** `POST /api/auth/mobile-login.php` with `{"username": "...", "password": "..."}`
**Response:** Returns `user` object, `access_token`, `refresh_token`, and `expires_in`.
**Subsequent Requests:** `Authorization: Bearer {access_token}` header on every request.

### 2.4 Token Lifecycle

| Token | Lifetime | Storage (Android) | Refresh |
|-------|----------|-------------------|---------|
| Access Token | 1 hour | EncryptedSharedPreferences | POST /api/auth/refresh.php |
| Refresh Token | 30 days | EncryptedSharedPreferences | Re-login required |

**Refresh:** `POST /api/auth/refresh.php` with `{"refresh_token": "..."}` returns new access_token + new refresh_token (rotation). See: `dual-auth-rbac` skill for breach detection and token revocation.

### 2.5 Permission Model (RBAC)

- Every endpoint requires a specific permission (e.g., `products.create`)
- Permissions are checked by middleware BEFORE the controller executes
- franchise_id is extracted from the token, NEVER accepted from the client
- Insufficient permissions return 403 Forbidden

---

## 3. Common Patterns

### 3.1 Standard Request Headers

| Header | Required | Value | Purpose |
|--------|----------|-------|---------|
| Content-Type | Yes | application/json | Request body format |
| Authorization | Yes (except login) | Bearer {token} OR session cookie | Authentication |
| X-CSRF-Token | Web only | CSRF token value | CSRF protection |
| X-App-Version | Mobile recommended | 1.0.0 | Client version tracking |
| Accept-Language | Optional | en, fr, sw | Localization hint |

### 3.2 Success Response Envelope

```json
{
  "success": true,
  "message": "Human-readable success description",
  "data": {
    "...": "endpoint-specific payload"
  }
}
```

### 3.3 Error Response Envelope

```json
{
  "success": false,
  "message": "Human-readable error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "errors": {
    "field_name": ["Validation message 1", "Validation message 2"]
  }
}
```

See: `api-error-handling` skill for complete error handling patterns and SweetAlert2 integration.

### 3.4 Pagination

**Request:** Append query parameters to list endpoints:
```
GET /api/products/list.php?page=2&per_page=25&sort=name&order=asc
```

**Response:**
```json
{
  "success": true,
  "data": [
    {"id": 26, "name": "Product 26"},
    {"id": 27, "name": "Product 27"}
  ],
  "pagination": {
    "page": 2,
    "per_page": 25,
    "total": 142,
    "total_pages": 6
  }
}
```

See: `api-pagination` skill for full offset-based pagination implementation.

### 3.5 Filtering & Sorting

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (1-based) |
| per_page | int | 25 | Items per page (max 100) |
| sort | string | name | Column to sort by |
| order | string | asc | Sort direction (asc/desc) |
| search | string | widget | Full-text search across searchable fields |
| status | string | active | Filter by status field |
| date_from | date | 2026-01-01 | Filter records from this date |
| date_to | date | 2026-12-31 | Filter records up to this date |

### 3.6 File Upload Pattern

```
POST /api/uploads/image.php
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: [binary image data]
entity_type: product
entity_id: 42
```

**Constraints:**
- Max file size: 10 MB
- Allowed types: jpg, png, pdf, xlsx, csv
- Images compressed client-side before upload (see `image-compression` skill)

---

## 4. Endpoint Documentation

[Organize endpoints by module. Repeat this block per endpoint.]

### 4.1 Authentication Endpoints

#### POST /api/auth/login.php

| Attribute | Value |
|-----------|-------|
| Description | Authenticate user (web session) |
| Auth Required | No |
| Permission | None |
| Rate Limit | 10 requests/minute per IP |

**Request Body:**

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| username | string | Yes | 3-100 chars |
| password | string | Yes | 8-255 chars |

**Success (200):** Returns user object, CSRF token, redirect URL.
**Errors:**

| HTTP | Code | Cause |
|------|------|-------|
| 400 | VALIDATION_ERROR | Missing username or password |
| 401 | INVALID_CREDENTIALS | Wrong username or password |
| 403 | ACCOUNT_LOCKED | Too many failed attempts |
| 403 | ACCOUNT_INACTIVE | User account is disabled |

#### POST /api/auth/mobile-login.php

[Same structure, returns JWT tokens instead of session.]

#### POST /api/auth/refresh.php

[Token refresh endpoint with rotation.]

#### POST /api/auth/logout.php

[Session/token invalidation.]

### 4.2 Module Endpoints

[Group by business module. Example: Products]

#### GET /api/products/list.php

| Attribute | Value |
|-----------|-------|
| Description | List products for the authenticated franchise |
| Auth Required | JWT or Session |
| Permission | products.view |
| Rate Limit | 120 requests/minute |
| Pagination | Yes (offset-based) |

**Query Parameters:**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| page | int | No | 1 | Page number |
| per_page | int | No | 25 | Items per page (max 100) |
| search | string | No | -- | Search by name or SKU |
| status | string | No | -- | Filter by status |
| category_id | int | No | -- | Filter by category |

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Widget A",
      "sku": "WDG-001",
      "price": 25.50,
      "status": "active",
      "category": {"id": 3, "name": "Widgets"},
      "stock_level": 142
    }
  ],
  "pagination": {
    "page": 1, "per_page": 25, "total": 85, "total_pages": 4
  }
}
```

**Note:** franchise_id is extracted from the auth token by middleware. The client never sends it.

#### POST /api/products/create.php

[Full endpoint documentation with request body, validation, responses.]

#### PUT /api/products/update.php

[Full endpoint documentation.]

#### DELETE /api/products/delete.php

[Full endpoint documentation.]

---

## 5. Error Reference

### 5.1 Error Code Table

| Error Code | HTTP Status | Message | Cause | Fix |
|-----------|------------|---------|-------|-----|
| VALIDATION_ERROR | 400 | Validation failed | Missing or invalid fields | Check `errors` object for field details |
| UNAUTHORIZED | 401 | Authentication required | Missing or expired token | Login or refresh token |
| INVALID_CREDENTIALS | 401 | Invalid username or password | Wrong credentials | Verify username/password |
| TOKEN_EXPIRED | 401 | Token has expired | Access token past expiry | Call refresh endpoint |
| FORBIDDEN | 403 | Insufficient permissions | User lacks required permission | Contact admin for permission |
| ACCOUNT_LOCKED | 403 | Account locked | Too many failed login attempts | Wait 15 minutes or contact admin |
| NOT_FOUND | 404 | Resource not found | Record does not exist or not in user's franchise | Verify ID and permissions |
| DUPLICATE_ENTRY | 409 | Duplicate entry | Unique constraint violation | Use different value for unique field |
| RATE_LIMITED | 429 | Too many requests | Rate limit exceeded | Wait and retry (check Retry-After header) |
| INTERNAL_ERROR | 500 | Internal server error | Unexpected server failure | Report to support with request ID |

### 5.2 SweetAlert2 Integration (Web Frontend)

Handle errors with `Swal.fire()`: show field-specific validation errors from `errors` object, redirect to login on `TOKEN_EXPIRED`, and display generic error message for other codes. See: `api-error-handling` skill for complete SweetAlert2 error display patterns and implementation code.

---

## 6. Webhooks

[If applicable for payment gateway or external system integration.]

### 6.1 Webhook Events

| Event | Trigger | Endpoint |
|-------|---------|----------|
| payment.completed | Payment processed successfully | /api/webhooks/payment.php |
| payment.failed | Payment processing failed | /api/webhooks/payment.php |
| subscription.renewed | Tenant subscription renewed | /api/webhooks/subscription.php |

### 6.2 Webhook Security

- Verify signature hash in `X-Webhook-Signature` header before processing
- Respond with HTTP 200 within 5 seconds
- Process webhook payload asynchronously if needed
- Handle duplicate deliveries idempotently (use transaction_id as idempotency key)
- Log all webhook payloads for audit trail

### 6.3 Retry Policy

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 5 minutes |
| 3 | 30 minutes |
| 4 | 2 hours |
| 5 (final) | 24 hours |

---

## 7. SDK / Client Examples

### 7.1 Kotlin (Android -- Retrofit)

```kotlin
interface ProductApiService {
    @GET("products/list.php")
    suspend fun getProducts(
        @Query("page") page: Int,
        @Query("per_page") perPage: Int = 25,
        @Query("search") search: String? = null,
        @Query("status") status: String? = null
    ): ApiResponse<PaginatedResponse<ProductDto>>

    @POST("products/create.php")
    suspend fun createProduct(
        @Body request: CreateProductRequest
    ): ApiResponse<ProductDto>

    @PUT("products/update.php")
    suspend fun updateProduct(
        @Body request: UpdateProductRequest
    ): ApiResponse<ProductDto>

    @DELETE("products/delete.php")
    suspend fun deleteProduct(
        @Query("id") productId: Int
    ): ApiResponse<Unit>
}
```

### 7.2 JavaScript (Web Frontend -- fetch)

```javascript
async function getProducts(page = 1, search = '') {
    const params = new URLSearchParams({ page, per_page: 25, search });
    const response = await fetch(`/api/products/list.php?${params}`, {
        headers: {
            'X-CSRF-Token': getCsrfToken(),
        },
        credentials: 'same-origin',
    });
    const data = await response.json();
    if (!data.success) {
        handleApiError(data);
        return null;
    }
    return data;
}
```

### 7.3 PHP (Internal Service-to-Service)

Use `$httpClient->post()` with `Authorization: Bearer {serviceToken}` header and JSON body. Same request/response format as mobile API.

---

## 8. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | YYYY-MM-DD | Initial API release |
| 1.1 | YYYY-MM-DD | Added search parameter to list endpoints |
| 1.2 | YYYY-MM-DD | Added webhook support for payment notifications |
```

---

## Section-by-Section Guidance

| Section | Key Guidance |
|---------|-------------|
| API Overview | Include all environment base URLs and content types. |
| Authentication | Document ALL auth methods (session, JWT, API key) with full examples. |
| Common Patterns | Define the response envelope ONCE here; reference from all endpoints. |
| Endpoint Docs | Every endpoint: method, path, auth, permission, request, response, errors. |
| Error Reference | Complete error code table. Include SweetAlert2 integration for web. |
| Webhooks | Document security (signature verification), retry policy, idempotency. |
| SDK Examples | Include Kotlin (Retrofit), JavaScript (fetch), and PHP examples. |
| Changelog | Update every time the API changes. Never remove old entries. |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| No error code table | Consumers guess at error handling | Document every error code with cause and fix |
| Missing auth documentation | Integration teams blocked | Document all auth methods with full flow examples |
| No pagination specification | Consumers fetch all data or guess at format | Define pagination envelope and query parameters |
| franchise_id in request body | Enables tenant impersonation attacks | Extract from token in middleware; never accept from client |
| No rate limit documentation | Consumers hit limits unexpectedly | Document limits per endpoint group |
| No SDK examples | Every consumer team writes boilerplate from scratch | Provide Kotlin, JavaScript, and PHP examples |
| Changelog not maintained | Consumers don't know what changed | Update changelog with every API modification |
| Vague error messages ("Error occurred") | Consumers can't diagnose issues | Specific error codes with actionable fix instructions |

## Quality Checklist

- [ ] Base URLs documented for all environments (dev, staging, prod)
- [ ] All authentication methods documented with full flow examples
- [ ] Token lifecycle (access, refresh, rotation) documented
- [ ] Success and error response envelopes defined
- [ ] Pagination pattern defined with request/response examples
- [ ] Every endpoint has: method, path, auth, permission, request, response, errors
- [ ] Error code table is complete with cause and fix for every code
- [ ] SweetAlert2 integration documented for web frontend errors
- [ ] Webhook security (signature verification) documented
- [ ] SDK examples provided for Kotlin, JavaScript, and PHP
- [ ] franchise_id sourcing documented (from auth token, never from client)
- [ ] Rate limits documented per endpoint group
- [ ] Changelog started with initial API version
- [ ] Cross-references to `api-error-handling` and `api-pagination` skills

---

**Back to:** [SDLC Design Skill](../SKILL.md) | **Related:** [Interface Control Document](interface-control-document.md) | [Technical Specification](technical-specification.md)
