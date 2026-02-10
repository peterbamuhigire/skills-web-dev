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

## Key Takeaway

**"Always validate API requirements against the frontend data being sent. The API's validation error (400 Bad Request) indicated missing fields, but without detailed error messages, debugging took longer."**

Design APIs that fail fast with specific, actionable error messages. This saves hours of debugging time and improves developer experience.
