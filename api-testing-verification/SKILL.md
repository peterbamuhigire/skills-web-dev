# API Testing Verification

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, code generation, debugging, quality checks, and any task where it offers enhanced capabilities. If superpowers provides a better way to accomplish something, prefer it over the default approach.

## Purpose

Enforce thorough API endpoint testing before declaring any API-dependent feature complete. Prevent backend-frontend mismatches that only surface during manual testing.

## When to Use

✅ **Before declaring any feature "complete" that involves API calls**
✅ **After implementing new DTOs or API services**
✅ **After creating new backend endpoints**
✅ **Before committing and pushing API-dependent features**
✅ **When integrating frontend with existing backend APIs**

❌ Don't use for pure UI-only features with no backend
❌ Don't use for unit tests that mock API responses

## The Problem This Solves

**Real example from Phase 3 Reports:**
- Built 8 report types with ViewModels, screens, and 26 unit tests
- All unit tests passed (mocked API responses)
- Build successful, APK installed on emulators
- Committed and pushed as "COMPLETE"
- **But never tested actual backend endpoints**

**Discovered after user manual testing:**
- Backend returns snake_case, Android expected camelCase without @Json annotations
- Commission/Remittance endpoints returned 404 (didn't exist)
- Inventory endpoint returned 500 (wrong query parameters)
- Sales reports failed due to field name mismatches (total_sales vs totalRevenue)

**Root cause:** Unit tests with mocked responses hide real API integration issues.

## Mandatory Pre-Completion Checklist

Before declaring ANY feature with API calls "complete", you MUST verify:

### 1. Backend Endpoint Existence (5 min)
```bash
# Check backend routing file or controller
# Verify the endpoint actually exists in code

# For PHP:
grep -r "sales-agent-portal.php" C:\wamp64\www\birdc_erp\public\api\

# For action-based APIs:
# Open the PHP file and verify the action exists in the switch/match statement
```

**Checklist:**
- [ ] Endpoint file exists at expected path
- [ ] Action/route handler exists in code
- [ ] No typos in endpoint URL
- [ ] Endpoint supports required HTTP method (GET/POST/PUT/DELETE)

### 2. API Response Structure Verification (10 min)

**Test with curl or Postman/Insomnia:**
```bash
# Example: Test with curl using actual auth token
curl -H "Authorization: Bearer <actual_jwt_token>" \
     "https://10.0.2.2/birdc_erp/public/api/sales-agent-portal.php?action=sales_by_product&page=1&per_page=20"
```

**Verify:**
- [ ] API returns 200 OK (not 404, 500, 401)
- [ ] Response structure matches ApiEnvelope expectations
- [ ] Field names match DTO @Json annotations
- [ ] Pagination structure matches (items, pagination.page, pagination.total_pages, etc.)
- [ ] Data types match (string vs int, nullable vs non-null)

### 3. Field Name Mapping (5 min)

**Backend typically uses snake_case:**
```json
{
  "item_name": "Product A",
  "total_revenue": 50000,
  "avg_price": 5000
}
```

**Android DTOs MUST use @Json annotations:**
```kotlin
data class ProductSalesDto(
    @Json(name = "item_name") val itemName: String,
    @Json(name = "total_revenue") val totalRevenue: Double,
    @Json(name = "avg_price") val averagePrice: Double
)
```

**Checklist:**
- [ ] All DTO fields have @Json annotations mapping to backend field names
- [ ] No assumptions about camelCase auto-conversion
- [ ] Nullable fields (?) match backend (null vs empty string vs missing)

### 4. Pagination Format (3 min)

**Verify backend pagination matches expectations:**

Backend returns:
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

Android expects:
```kotlin
data class PaginatedData<T>(
    val items: List<T>,
    val pagination: PaginationMeta
)

data class PaginationMeta(
    val page: Int,
    @Json(name = "per_page") val perPage: Int,
    val total: Int,
    @Json(name = "total_pages") val totalPages: Int
)
```

**Checklist:**
- [ ] Backend supports page and per_page query params
- [ ] Response includes pagination metadata
- [ ] Field names match (per_page, total_pages with underscores)

### 5. Error Scenario Testing (5 min)

**Test failure cases:**
```bash
# Invalid auth token (should return 401)
curl -H "Authorization: Bearer invalid_token" <endpoint>

# Missing required param (should return 400)
curl <endpoint>?page=abc

# Non-existent resource (should return 404)
curl <endpoint>?agent_id=99999
```

**Checklist:**
- [ ] 401 for invalid/expired tokens
- [ ] 400 for invalid parameters
- [ ] 404 for missing resources
- [ ] 500 errors return meaningful error messages in response body
- [ ] Error messages can be extracted by safeApiCall()

### 6. Integration Test (10 min)

**Run the actual app on emulator with real backend:**

1. Start WAMP server
2. Install APK on emulator
3. Login with test credentials
4. Navigate to each screen that uses the new API
5. Verify data loads correctly
6. Check Logcat for JSON parsing errors
7. Test pagination (scroll to trigger load more)
8. Test date filtering
9. Test search functionality
10. Test error states (disconnect WiFi, check error handling)

**Checklist:**
- [ ] Data displays correctly in UI
- [ ] No JSON parsing errors in Logcat
- [ ] Pagination works (loads next page)
- [ ] Filters work (date range, search query)
- [ ] Loading states show properly
- [ ] Error states show meaningful messages
- [ ] Empty states show when no data

## Workflow Integration

### During Feature Implementation

```
1. Write domain models (data classes)
2. Write DTOs with @Json annotations (check backend response structure first!)
3. Write API service interface
4. Write repository implementation
5. Write unit tests (with mocked responses)
6. ⚠️ BEFORE DECLARING COMPLETE:
   - Run through Pre-Completion Checklist above
   - Test with actual backend
   - Fix any mismatches
   - Re-test until all API calls work
7. NOW you can commit as "complete"
```

### Red Flags to Watch For

🚩 **"All unit tests pass" is NOT sufficient** - unit tests mock API responses
🚩 **"Build successful" is NOT sufficient** - build doesn't test actual APIs
🚩 **Never assume field names** - always verify backend response JSON
🚩 **Never assume endpoint exists** - check backend routing first
🚩 **Never skip manual testing** - run the app with real backend before committing

## Common Backend-Frontend Mismatches

### 1. Field Name Case Mismatch
```
Backend: total_revenue
Android without @Json: totalRevenue ❌ (won't match)
Android with @Json: @Json(name = "total_revenue") val totalRevenue ✅
```

### 2. Field Name Semantic Mismatch
```
Backend returns: total_sales
Android expects: totalRevenue ❌
Fix: Update DTO to expect total_sales OR fix backend
```

### 3. Missing Endpoint
```
Android calls: agent-commissions.php?action=get_commissions
Backend: Endpoint doesn't exist ❌
Fix: Add the action to backend routing
```

### 4. Wrong Pagination Structure
```
Backend returns: { items: [...], page: 1, total: 100 }
Android expects: { items: [...], pagination: { page: 1, total: 100 } } ❌
Fix: Normalize one or the other
```

### 5. Nullable Mismatches
```
Backend returns: phone_number: null
Android DTO: val phoneNumber: String ❌ (should be String?)
Fix: Make DTO field nullable: String?
```

## Quick Reference Commands

**Test endpoint with curl:**
```bash
# Get JWT token from app first (check Logcat or use /v1/auth/login)
export TOKEN="your_jwt_token_here"

# Test endpoint
curl -H "Authorization: Bearer $TOKEN" \
     "https://10.0.2.2/birdc_erp/public/api/sales-agent-portal.php?action=sales_by_product&page=1&per_page=20" \
     | jq .
```

**Check backend endpoint exists:**
```bash
# Search for endpoint definition
grep -n "sales_by_product" C:\wamp64\www\birdc_erp\public\api\sales-agent-portal.php

# Check service method exists
grep -n "getSalesByProduct" C:\wamp64\www\birdc_erp\src\Services\Sales\*.php
```

**Check Android DTO field names:**
```bash
# Search for DTO definition
grep -A 10 "data class ProductSalesDto" app/src/main/java/**/*.kt
```

**View Logcat for JSON errors:**
```bash
adb logcat | grep -i "json\|moshi\|retrofit\|http"
```

## Integration with Other Skills

```
feature-planning → Define API contract (request/response structure)
      ↓
android-development → Implement DTOs, API services, repositories
      ↓
android-tdd → Write unit tests (with mocked responses)
      ↓
api-testing-verification → MANDATORY: Test with real backend (THIS SKILL)
      ↓
update-claude-documentation → Document API contract in completion report
```

## Summary

**The Golden Rule:**
> "All unit tests passing" + "Build successful" ≠ Feature complete
>
> You MUST test with actual backend before declaring completion.

**Time Budget:**
- Pre-completion checklist: 30-40 minutes
- Cost of skipping: 2-3 hours fixing issues after user reports them

**Remember:**
Unit tests can't catch backend-frontend mismatches. Always verify with real API calls before committing.
