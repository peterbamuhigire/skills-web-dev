# API Contract Validation - Detailed Guide

Complete reference for frontend-backend data contract validation and debugging.

## Problem: Silent Contract Mismatches

When frontend sends incomplete data, generic 400 errors don't indicate which fields are missing:

```json
// Frontend sends:
{
  "agent_id": 2,
  "payment_method": "Cash",
  "amount": 10000
}

// API expects (but doesn't clearly communicate):
{
  "agent_id": 2,
  "sales_point_id": 5,        // ❌ MISSING
  "remittance_date": "2026-02-10", // ❌ MISSING
  "payment_method": "Cash",
  "amount": 10000
}

// Result: Generic 400 Bad Request
```

## Solution 1: Detailed Validation Errors

**Backend should return field-specific errors:**

```php
$errors = [];
if (empty($input['agent_id'])) {
    $errors['agent_id'] = 'Agent ID is required';
}
if (empty($input['sales_point_id'])) {
    $errors['sales_point_id'] = 'Sales point ID is required';
}
if (empty($input['remittance_date'])) {
    $errors['remittance_date'] = 'Remittance date is required';
}
if (empty($input['amount']) || $input['amount'] <= 0) {
    $errors['amount'] = 'Amount must be positive';
}
if (empty($input['payment_method'])) {
    $errors['payment_method'] = 'Payment method is required';
}

if (!empty($errors)) {
    ResponseHandler::validationError($errors);
    // Returns HTTP 422 with:
    // {
    //   "success": false,
    //   "message": "Validation failed",
    //   "error": {
    //     "code": "VALIDATION_FAILED",
    //     "type": "validation_error",
    //     "details": {
    //       "sales_point_id": "Sales point ID is required",
    //       "remittance_date": "Remittance date is required"
    //     }
    //   }
    // }
}
```

## Solution 2: API Contract Documentation

**Document required fields at the top of each endpoint:**

```php
/**
 * Create Remittance
 *
 * Required Fields:
 * - agent_id (int): Agent ID
 * - sales_point_id (int): Sales point where remittance occurs
 * - remittance_date (string): Date in Y-m-d format
 * - amount (float): Positive remittance amount
 * - payment_method (string): Cash|BankTransfer|MobileMoney|Cheque
 *
 * Optional Fields:
 * - bank_reference (string): Bank reference/receipt number
 * - notes (string): Additional notes
 * - invoice_ids (array): Invoice IDs being remitted
 *
 * @return HTTP 201 with remittance details on success
 * @return HTTP 422 with validation errors on invalid data
 */
function handleCreateRemittance(AgentRemittanceService $service): void
{
    $input = json_decode(file_get_contents('php://input'), true);

    // Validation...
}
```

## Solution 3: Contract Testing

**Test frontend data against API requirements:**

```javascript
// Frontend: Before sending
function validateRemittanceData(data) {
  const required = [
    'agent_id',
    'sales_point_id',
    'remittance_date',
    'amount',
    'payment_method'
  ];

  const missing = required.filter(field => !data[field]);

  if (missing.length > 0) {
    console.error('❌ Missing required fields:', missing);
    throw new Error(`Missing fields: ${missing.join(', ')}`);
  }

  return true;
}

// Usage
const remittanceData = {
  agent_id: state.agent.id,
  sales_point_id: state.agent.store_id, // Don't forget!
  remittance_date: new Date().toISOString().split('T')[0], // Don't forget!
  payment_method: paymentMethod,
  amount: amount
};

validateRemittanceData(remittanceData); // Catches missing fields early
const response = await api.post('agent-remittances.php', {
  action: 'create_remittance',
  ...remittanceData
});
```

## Complete Data Flow Example

**HTML → JavaScript → API → Database**

```javascript
// 1. HTML data attributes
<option value="2"
        data-code="AG-001"
        data-store-id="5">  ← Store ID here
  AG-001 - John Doe
</option>

// 2. JavaScript extracts
const selectedOption = $(this).find("option:selected");
state.agent = {
  id: parseInt(selectedOption.val()),
  store_id: parseInt(selectedOption.data("store-id")) ← Read correctly
};

// 3. Include in API call
await api.post('remittances.php', {
  agent_id: state.agent.id,
  sales_point_id: state.agent.store_id, ← Send as sales_point_id
  remittance_date: '2026-02-10',
  amount: 10000
});

// 4. API validates
if (empty($input['sales_point_id'])) {
  throw new ValidationException(['sales_point_id' => 'Required']);
}
```

## Debugging Checklist

When you see "400 Bad Request" or "Submission Failed":

1. **Check browser console:** Look for validation error details
2. **Check network tab:** Inspect request payload vs API expectations
3. **Check PHP error log:** Look for validation failures
4. **Compare contracts:** Match frontend data structure to backend requirements
5. **Test with curl:** Send minimal valid request to isolate missing fields

```bash
# Test API contract with curl
curl -X POST http://localhost/api/agent-remittances.php \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create_remittance",
    "agent_id": 2,
    "sales_point_id": 5,
    "remittance_date": "2026-02-10",
    "amount": 10000,
    "payment_method": "Cash"
  }'
```

## Anti-Patterns

**❌ Don't:**
- Return generic "Bad Request" without details
- Assume frontend knows all required fields
- Use different parameter names (frontend: `storeId`, backend: `sales_point_id`)
- Skip validation in favor of database constraints (harder to debug)
- Fail silently on missing fields

## Best Practices

**Backend:**
1. ✅ Return field-specific validation errors (HTTP 422)
2. ✅ Document required/optional fields in endpoint comments
3. ✅ Use descriptive error messages ("Sales point ID is required")
4. ✅ Include error codes for programmatic handling
5. ✅ Log validation failures with request context

**Frontend:**
1. ✅ Validate data before sending to API
2. ✅ Display field-specific errors to users
3. ✅ Log missing fields to console for debugging
4. ✅ Match API parameter names exactly (snake_case vs camelCase)
5. ✅ Include all required fields even if empty/null

## Action Parameter Location (Query String vs JSON Body)

**Critical Pattern:** Use query string for action/method routing, JSON body for request payload.

### Problem: Inconsistent Action Parameter Location

```javascript
// Frontend sends action in JSON body
$.ajax({
  url: "./api/remittances.php",
  method: "POST",
  data: JSON.stringify({
    action: "create_remittance",  // ❌ In body
    agent_id: 2,
    amount: 10000
  })
});
```

```php
// But backend reads from query string
$action = $_GET['action'] ?? '';  // ❌ Always empty!

switch ($action) {
  case 'create_remittance':
    // Never reached!
}
```

**Result:** "Invalid action" error despite sending correct action.

### Solution: Consistent Action Parameter Location

**Best Practice:** Action/method in query string, payload in JSON body.

```javascript
// ✅ CORRECT: Action in URL, payload in body
$.ajax({
  url: "./api/remittances.php?action=create_remittance",  // ✅ Query string
  method: "POST",
  contentType: "application/json",
  data: JSON.stringify({
    agent_id: 2,           // ✅ Payload only
    amount: 10000
  })
});
```

```php
// ✅ CORRECT: Read action from query string
$action = $_GET['action'] ?? '';
$input = json_decode(file_get_contents('php://input'), true);

switch ($action) {
  case 'create_remittance':
    // Payload from $input, not $_GET
    createRemittance($input);
    break;
}
```

### Why Query String for Actions?

**Benefits:**

1. **Clear URLs:** `GET /api/users.php?action=list` vs `POST /api/users.php` (body: `{action: 'list'}`)
2. **Browser caching:** Query strings allow browser/proxy caching by action type
3. **Logs are readable:** Apache logs show `GET /api/users.php?action=list` instead of just `POST /api/users.php`
4. **REST clarity:** Action determines route, body contains data
5. **No parsing needed:** Available immediately via `$_GET`, no need to decode JSON first

**Anti-Pattern:**
```javascript
// ❌ Action in body makes URLs ambiguous
POST /api/endpoint.php
{ "action": "create", "data": {...} }

POST /api/endpoint.php
{ "action": "update", "data": {...} }

// Both look identical in logs!
```

### Standard Pattern

**Frontend:**
```javascript
// List (GET)
$.ajax({
  url: "./api/remittances.php?action=list&agent_id=2",
  method: "GET"
});

// Create (POST)
$.ajax({
  url: "./api/remittances.php?action=create",
  method: "POST",
  contentType: "application/json",
  data: JSON.stringify({
    agent_id: 2,
    amount: 10000
  })
});

// Update (POST/PUT)
$.ajax({
  url: "./api/remittances.php?action=update&id=5",
  method: "POST",
  contentType: "application/json",
  data: JSON.stringify({
    amount: 15000
  })
});

// Delete (POST/DELETE)
$.ajax({
  url: "./api/remittances.php?action=delete&id=5",
  method: "POST"
});
```

**Backend:**
```php
$action = $_GET['action'] ?? '';
$method = $_SERVER['REQUEST_METHOD'];

// Read payload for POST/PUT
$input = null;
if (in_array($method, ['POST', 'PUT'])) {
    $input = json_decode(file_get_contents('php://input'), true);
}

switch ($action) {
    case 'list':
        $agentId = (int)($_GET['agent_id'] ?? 0);
        listRemittances($agentId);
        break;

    case 'create':
        createRemittance($input);  // From JSON body
        break;

    case 'update':
        $id = (int)($_GET['id'] ?? 0);
        updateRemittance($id, $input);  // ID from URL, data from body
        break;

    case 'delete':
        $id = (int)($_GET['id'] ?? 0);
        deleteRemittance($id);
        break;

    default:
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'error' => 'INVALID_ACTION',
            'message' => 'Valid actions: list, create, update, delete'
        ]);
}
```

### Debugging "Invalid Action" Errors

**When you see "Invalid action" or "Bad Request":**

1. **Check where API reads action:**
   ```php
   // Does it use $_GET?
   $action = $_GET['action'] ?? '';

   // Or $input from JSON body?
   $input = json_decode(file_get_contents('php://input'), true);
   $action = $input['action'] ?? '';
   ```

2. **Check where frontend sends action:**
   ```javascript
   // In URL query string?
   url: "./api/endpoint.php?action=create"

   // Or in JSON body?
   data: JSON.stringify({ action: "create", ... })
   ```

3. **Log both sides for comparison:**
   ```php
   // Backend: Log what you receive
   error_log("Action from GET: " . ($_GET['action'] ?? 'empty'));
   error_log("Action from JSON: " . ($input['action'] ?? 'empty'));
   ```

   ```javascript
   // Frontend: Log what you send
   console.log("URL:", url);
   console.log("Body:", data);
   ```

4. **Test with curl:**
   ```bash
   # Query string (correct pattern)
   curl "http://localhost/api/remittances.php?action=create" \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"agent_id":2,"amount":10000}'

   # JSON body (anti-pattern)
   curl "http://localhost/api/remittances.php" \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"action":"create","agent_id":2,"amount":10000}'
   ```

### Migration Strategy

**If you have inconsistent APIs:**

1. **Standardize new endpoints:** Use query string for actions
2. **Document existing patterns:** Comment which endpoints use which pattern
3. **Gradually refactor:** Update one endpoint at a time
4. **Add compatibility layer:** Support both temporarily during migration

```php
// Temporary compatibility layer
$action = $_GET['action'] ?? '';
if (empty($action)) {
    $input = json_decode(file_get_contents('php://input'), true);
    $action = $input['action'] ?? '';

    // Log deprecated usage
    error_log("DEPRECATED: Action in JSON body. Use query string instead.");
}
```

### Key Takeaways

**Best Practice:**
- ✅ **Action/method:** Query string (`?action=create`)
- ✅ **Resource IDs:** Query string (`?id=5`)
- ✅ **Filters/pagination:** Query string (`?status=active&page=2`)
- ✅ **Request payload:** JSON body (`{"agent_id": 2, "amount": 10000}`)

**Debugging Tip:**
*"When you see 'Invalid action' errors, check BOTH where the API reads it (`$_GET` vs `$input`) AND where the frontend sends it (URL vs body). Log both to compare!"*

**Design Principle:**
*"Use query string for action/method routing, JSON body for request payload. This makes URLs clearer and allows browser/proxy caching by action type."*

## Key Takeaway

**"Always validate API requirements against the frontend data being sent. The API's validation error (400 Bad Request) indicated missing fields, but without detailed error messages, debugging took longer."**

Design APIs that fail fast with specific, actionable error messages. This saves hours of debugging time and improves developer experience.
