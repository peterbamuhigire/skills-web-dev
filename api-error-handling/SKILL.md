---
name: api-error-handling
description: Comprehensive, standardized error response system for PHP REST APIs with
  SweetAlert2 integration. Use when building REST APIs that need consistent error
  formatting, specific error message extraction from database exceptions, validation
  error...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Claude Code: use Superpowers or similar helpers when they are available and materially useful.
- Codex: apply this skill normally; do not treat optional plugins as a prerequisite.

# API Error Handling

<!-- dual-compat-start -->
## Use When

- Comprehensive, standardized error response system for PHP REST APIs with SweetAlert2 integration. Use when building REST APIs that need consistent error formatting, specific error message extraction from database exceptions, validation error...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `api-error-handling` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references, examples` only as needed.
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

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use the `examples/` directory for concrete patterns when implementation shape matters.
<!-- dual-compat-end -->
Implement comprehensive, standardized error response system for PHP REST APIs with consistent JSON envelopes, specific error message extraction, and SweetAlert2 integration.

**Core Principles:**

- Consistent JSON envelope across all endpoints
- Specific error messages extracted from all exception types
- Appropriate HTTP status codes for all error categories
- Machine-readable error codes for programmatic handling
- Human-readable messages for SweetAlert2 display
- Secure error handling (no stack traces in production)
- Comprehensive logging with request IDs
- **CRITICAL: Always show error messages to users in SweetAlert (never silent failures)**

**Security Baseline (Required):** Always load and apply the **Vibe Security Skill** for PHP API work. Do not leak sensitive data in responses or logs.

**Cross-Platform:** APIs deploy to Windows (dev), Ubuntu (staging), Debian (production), all running MySQL 8.x. Use `utf8mb4_unicode_ci` collation. Match file/directory case exactly in require paths (Linux is case-sensitive). Use forward slashes in paths.

**See subdirectories for:**

- `references/` - Complete PHP classes (ApiResponse, ExceptionHandler, Exceptions)
- `examples/` - Full endpoint implementation, frontend client

## Response Envelope Standard

**Success:**

```json
{
  "success": true,
  "data": {
    /* payload */
  },
  "message": "Optional success message",
  "meta": {
    "timestamp": "2026-01-24T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**Error:**

```json
{
  "success": false,
  "message": "Human-readable error for SweetAlert2",
  "error": {
    "code": "ERROR_CODE",
    "type": "validation_error",
    "details": {
      /* field-specific errors */
    }
  },
  "meta": {
    "timestamp": "2026-01-24T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

## HTTP Status Codes

| Status | Error Type            | Use Case                       | Error Code Examples                   |
| ------ | --------------------- | ------------------------------ | ------------------------------------- |
| 400    | Bad Request           | Malformed JSON, missing params | INVALID_JSON, MISSING_PARAMETER       |
| 401    | Unauthorized          | Missing/invalid auth token     | TOKEN_MISSING, TOKEN_EXPIRED          |
| 403    | Forbidden             | Valid auth but no permission   | PERMISSION_DENIED, ACCESS_FORBIDDEN   |
| 404    | Not Found             | Resource doesn't exist         | RESOURCE_NOT_FOUND, INVOICE_NOT_FOUND |
| 405    | Method Not Allowed    | Wrong HTTP method              | METHOD_NOT_ALLOWED                    |
| 409    | Conflict              | Business rule violation        | ALREADY_EXISTS, OVERPAYMENT           |
| 422    | Unprocessable Entity  | Validation errors              | VALIDATION_FAILED, INVALID_EMAIL      |
| 429    | Too Many Requests     | Rate limiting                  | RATE_LIMIT_EXCEEDED                   |
| 500    | Internal Server Error | Unexpected errors              | INTERNAL_ERROR, DATABASE_ERROR        |
| 503    | Service Unavailable   | Maintenance/overload           | SERVICE_UNAVAILABLE, DEADLOCK         |

## ApiResponse Helper (Quick Reference)

**See `references/ApiResponse.php` for complete implementation**

```php
// Success responses
ApiResponse::success($data, $message, $status);
ApiResponse::created($data, $message);

// Error responses
ApiResponse::error($message, $code, $status, $type, $details);
ApiResponse::validationError($errors, $message);
ApiResponse::notFound($resource, $identifier);
ApiResponse::unauthorized($message);
ApiResponse::forbidden($permission);
ApiResponse::conflict($message, $code);
ApiResponse::methodNotAllowed($allowedMethods);
ApiResponse::rateLimited($retryAfter);
ApiResponse::serverError($message);
ApiResponse::serviceUnavailable($message);
```

## Exception Handler (Quick Reference)

**See `references/ExceptionHandler.php` for complete implementation**

**Key Features:**

- Extracts specific messages from PDOException
- Parses SQLSTATE 45000 (user-defined exceptions from triggers)
- Extracts constraint violation messages
- Handles deadlocks gracefully
- Logs all errors with request ID
- Hides stack traces in production

**PDOException Parsing:**

```php
// SQLSTATE 45000: Business rule from trigger
// "SQLSTATE[45000]: <<1>>: 1644 Overpayment not allowed"
// Extracted: "Overpayment not allowed"

// SQLSTATE 23000: Duplicate entry
// "Duplicate entry 'john@example.com' for key 'uk_email'"
// Extracted: "A record with this Email already exists: 'john@example.com'"

// SQLSTATE 23000: Foreign key violation
// "Cannot delete or update a parent row..."
// Extracted: "Referenced Customer does not exist or cannot be deleted"
```

## Custom Exception Classes

**See `references/CustomExceptions.php` for all classes**

```php
// Validation (422)
throw new ValidationException([
    'email' => 'Invalid email format',
    'phone' => 'Phone number required'
], 'Validation failed');

// Authentication (401)
throw new AuthenticationException('Token expired', 'expired');

// Authorization (403)
throw new AuthorizationException('MANAGE_USERS');

// Not Found (404)
throw new NotFoundException('Invoice', 'INV-123');

// Conflict (409)
throw new ConflictException('Already voided', 'ALREADY_VOIDED');

// Rate Limit (429)
throw new RateLimitException(60);
```

## API Bootstrap Pattern

**See `references/bootstrap.php` for complete file**

Include at top of all API endpoints:

```php
require_once __DIR__ . '/bootstrap.php';

// Helper functions available:
require_method(['POST', 'PUT']);
$data = read_json_body();
validate_required($data, ['customer_id', 'amount']);
$db = get_db();
$token = bearer_token();
require_auth();
require_permission('MANAGE_INVOICES');
handle_request(function() { /* endpoint logic */ });
```

## Endpoint Implementation Pattern

**See `examples/InvoicesEndpoint.php` for complete example**

```php
require_once __DIR__ . '/../bootstrap.php';
use App\Http\ApiResponse;
use App\Http\Exceptions\{NotFoundException, ValidationException};

require_auth();
handle_request(function() {
    $method = $_SERVER['REQUEST_METHOD'];
    match ($method) {
        'POST' => handlePost(),
        default => ApiResponse::methodNotAllowed('POST')
    };
});

function handlePost(): void {
    $data = read_json_body();
    validate_required($data, ['customer_id', 'items']);

    if (empty($data['items'])) {
        throw new ValidationException(['items' => 'Required']);
    }

    // Business logic...
    ApiResponse::created(['id' => $id], 'Created successfully');
}
```

## Frontend Integration

**See `examples/ApiClient.js` for complete implementation**

```javascript
const api = new ApiClient("./api");

// GET - Errors automatically shown via SweetAlert2
const response = await api.get("invoices.php", { status: "pending" });
if (response) renderInvoices(response.data);

// POST - Validation errors highlight form fields
showLoading("Creating...");
const result = await api.post("invoices.php", formData);
hideLoading();
if (result) showSuccess("Created successfully");

// DELETE - With confirmation
const { value: reason } = await Swal.fire({
  title: "Void?",
  input: "textarea",
  showCancelButton: true,
});
if (reason) {
  const res = await api.delete(`invoices.php?id=${id}`, { reason });
  if (res) showSuccess("Voided");
}

// Helpers: showSuccess/Error/Warning/Info, showConfirm, showLoading, hideLoading
```

## Critical Error Display Pattern

**MANDATORY: Always show API errors to users in SweetAlert2**

```javascript
try {
  const response = await $.ajax({
    url: "./api/endpoint.php?action=verify",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ id: 123 }),
  });

  // Check response.success BEFORE using data
  if (!response.success) {
    await Swal.fire({
      icon: "error",
      title: "Operation Failed",
      text: response.message || "An error occurred",
      confirmButtonText: "OK",
    });
    return; // Stop execution
  }

  // Success path
  await Swal.fire({
    icon: "success",
    title: "Success!",
    text: response.message || "Operation completed",
  });

} catch (error) {
  // Extract error message from different formats
  let errorMessage = "An unexpected error occurred";

  if (error.responseJSON && error.responseJSON.message) {
    errorMessage = error.responseJSON.message; // API error message
  } else if (error.message) {
    errorMessage = error.message; // JavaScript error
  }

  await Swal.fire({
    icon: "error",
    title: "Error",
    text: errorMessage,
    confirmButtonText: "OK",
  });
}
```

**Key Points:**
- ✅ Always check `response.success` before proceeding
- ✅ Show error message in SweetAlert (never silent failure)
- ✅ Extract message from `response.message` or `error.responseJSON.message`
- ✅ Close any open modals before showing error
- ✅ Use `await` to ensure user sees error before code continues

## Debugging Data Shape Mismatches

- When you see `not a function` errors in JS, trace the full chain: service return → API wrapper → JS consumer.
- Services may intentionally wrap arrays (e.g., `{ sales: [...] }`) for mobile consumers while web UI expects a flat array.
- Normalize defensively when response shape may vary:

```javascript
const rows = Array.isArray(data)
  ? data
  : Array.isArray(data?.sales)
    ? data.sales
    : [];
```

## API Contract Validation (Frontend-Backend Alignment)

**See `references/contract-validation.md` for complete guide**

**Critical Pattern:** Always validate that frontend data matches backend API requirements. Missing fields cause 400 errors that are difficult to debug without detailed error messages.

**Common Scenario:**
```javascript
// Frontend sends incomplete data
{ agent_id: 2, payment_method: "Cash", amount: 10000 }

// API expects (but doesn't communicate):
{ agent_id: 2, sales_point_id: 5, remittance_date: "2026-02-10", ... }

// Result: Generic 400 Bad Request ❌
```

**Solution: Field-Specific Validation**

```php
// Backend: Return specific errors (HTTP 422)
$errors = [];
if (empty($input['sales_point_id'])) {
    $errors['sales_point_id'] = 'Sales point ID is required';
}
if (empty($input['remittance_date'])) {
    $errors['remittance_date'] = 'Remittance date is required';
}
if (!empty($errors)) {
    ResponseHandler::validationError($errors);
}
```

**Quick Checklist:**
- ✅ Document required fields in endpoint comments
- ✅ Return field-specific errors (HTTP 422, not 400)
- ✅ Validate frontend data before API call
- ✅ Match parameter names exactly (snake_case consistency)
- ✅ Log validation failures with request context
- ✅ **Action in query string, payload in JSON body** (see below)

**Action Parameter Location:**
```javascript
// ✅ CORRECT: Action in URL
url: "./api/endpoint.php?action=create",
data: JSON.stringify({ agent_id: 2, amount: 10000 })

// ❌ WRONG: Action in body
url: "./api/endpoint.php",
data: JSON.stringify({ action: "create", agent_id: 2 })
```

**Why:** Query string for routing, JSON body for payload. Makes URLs clear, enables caching, readable logs.

**Debugging:** Check browser console → network tab → PHP error log → compare contracts → test with curl

**Key Takeaways:**
- *"Always validate API requirements against the frontend data being sent. Generic 400 errors without field details make debugging exponentially harder."*
- *"Use query string for action/method routing, JSON body for request payload. Check BOTH where API reads it (`$_GET` vs `$input`) AND where frontend sends it (URL vs body)."*

## Error Message Extraction

**SQLSTATE 45000 (Trigger):**

```sql
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Overpayment not allowed';
-- Extracted: "Overpayment not allowed" → Code: OVERPAYMENT_NOT_ALLOWED
```

**SQLSTATE 23000 (Duplicate):**

```
"Duplicate entry 'john@example.com' for key 'uk_email'"
-- Extracted: "A record with this Email already exists: 'john@example.com'"
```

**SQLSTATE 23000 (Foreign Key):**

```
"Cannot delete or update a parent row..."
-- Extracted: "Referenced Customer does not exist or cannot be deleted"
```

**Deadlock:**

```
"Deadlock found when trying to get lock..."
-- Extracted: "Database conflict. Please try again." → HTTP 503
```

## Validation Pattern

**Backend:**

```php
$errors = [];
if (empty($data['email'])) $errors['email'] = 'Email required';
elseif (!filter_var($data['email'], FILTER_VALIDATE_EMAIL))
    $errors['email'] = 'Invalid email';

if ($errors) ApiResponse::validationError($errors);
```

**Frontend automatically:**

- SweetAlert2 with formatted error list
- Highlights fields with `.is-invalid`
- Adds `.invalid-feedback` elements

## Business Rule Pattern

```php
$stmt = $db->prepare("SELECT status FROM invoices WHERE id = ? FOR UPDATE");
$stmt->execute([$id]);
$invoice = $stmt->fetch();

if (!$invoice) throw new NotFoundException('Invoice', $id);
if ($invoice['status'] === 'voided')
    throw new ConflictException('Already voided', 'ALREADY_VOIDED');
if ($invoice['status'] === 'paid')
    throw new ConflictException('Cannot void paid invoice', 'INVOICE_PAID');
```

## Logging Pattern

All errors logged with context:

```
[req_abc123] PDOException: SQLSTATE[45000]: Overpayment not allowed in /api/payments.php:45
Context: {"user_id":123,"franchise_id":5,"url":"/api/payments.php","method":"POST"}
```

## Implementation Checklist

**Backend:**

- [ ] All endpoints use `ApiResponse` helper
- [ ] All exceptions caught by `ExceptionHandler`
- [ ] Specific error codes for each error type
- [ ] PDOException messages properly extracted
- [ ] Trigger errors parsed (SQLSTATE 45000)
- [ ] Constraint violations give meaningful messages
- [ ] Stack traces hidden in production
- [ ] All errors logged with request ID
- [ ] HTTP status codes match error types
- [ ] Bootstrap file included in all endpoints

**Frontend:**

- [ ] All API calls use centralized `ApiClient`
- [ ] Errors displayed via SweetAlert2 only (no native alert/confirm)
- [ ] Validation errors highlight form fields
- [ ] Network errors handled gracefully
- [ ] Loading states shown during requests
- [ ] Error codes displayed in footer
- [ ] Offline state detected and handled
- [ ] Request IDs logged for debugging

**Database:**

- [ ] Triggers use SQLSTATE 45000 for business rules
- [ ] Clear, user-friendly error messages in triggers
- [ ] Constraints have descriptive names (uk_email_franchise)
- [ ] Foreign key errors give context

## Quick Error Reference

```php
// 400 - Bad Request
ApiResponse::error('Invalid request', 'BAD_REQUEST', 400);

// 401 - Unauthorized
ApiResponse::unauthorized('Session expired');

// 403 - Forbidden
ApiResponse::forbidden('MANAGE_USERS');

// 404 - Not Found
ApiResponse::notFound('Invoice', 'INV-123');

---
> **Note:** Content trimmed to 500-line standard. Move overflow content to `references/` for on-demand loading.
