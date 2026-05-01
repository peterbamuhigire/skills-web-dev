# App-Specific Error Prevention

**Purpose:** Prevention checklists tailored to specific applications

**Parent Skill:** ai-error-prevention

**Applications:** MADUUKA, MEDIC8, BRIGHTSOMA, DDA, CROWNPOINT

---

## MADUUKA (Franchise ERP System)

### High-Risk Areas

```
□ Multi-tenancy (tenant isolation critical)
□ Pricing logic (complex formulas, discounts, taxes)
□ Inventory calculations (stock levels, movements)
□ Payment integration (revenue critical)
□ Commission calculations (affects salesperson pay)
```

### Prevention Checklist

**BEFORE Requesting Code:**
```
□ Specify tenant isolation explicitly
  "All queries MUST include WHERE tenant_id = ?"

□ Provide pricing formula with examples
  "Base price + Tax(15%) - Discount(if >= 10 items: 5%)"
  Example: 10 items @ $100 = $1000 - $50 (discount) + $142.50 (tax) = $1092.50

□ Show inventory calculation scenarios
  "Stock: 100, Sold: 30, Received: 20 → New stock: 90"
  "Transfer from Location A to B: Decrement A, Increment B (atomic)"

□ Demand test cases for each scenario
  "Test: Discount applies correctly, Tax calculated on discounted price"
```

**AFTER Receiving Code:**
```
□ Verify tenant_id in ALL queries
  Search for: "SELECT", "UPDATE", "DELETE" without "tenant_id"

□ Test pricing with edge cases
  - 0 items (no discount)
  - 10 items (discount applies)
  - Negative quantity (should reject)
  - Tax-exempt items
  - Combo discounts

□ Validate inventory math
  Test atomic transfers (both locations update or neither)
  Test concurrent stock updates (no race conditions)

□ Check payment error handling
  Test: Payment gateway timeout
  Test: Insufficient funds
  Test: Duplicate payment attempt
```

### Common MADUUKA-Specific Failures

**Failure: Forgot Tenant Isolation**
```javascript
// ❌ Claude generates:
const items = await db.query("SELECT * FROM inventory WHERE sku = ?", [sku]);

// ✓ Should be:
const items = await db.query(
  "SELECT * FROM inventory WHERE tenant_id = ? AND sku = ?",
  [tenantId, sku]
);
```

**Prevention:**
```
Explicitly state in EVERY request:
"Remember: This is multi-tenant. ALL queries must filter by tenant_id."
```

---

## MEDIC8 (Healthcare System)

### High-Risk Areas

```
□ Patient data privacy (HIPAA compliance)
□ Medication interactions (patient safety)
□ Dosage calculations (precision critical)
□ Prescription validations (regulatory)
□ Medical record access (authorization)
```

### Prevention Checklist

**BEFORE Requesting Code:**
```
□ List HIPAA requirements explicitly
  "Data must be encrypted at rest and in transit"
  "Log all access to patient records (who, when, what)"
  "Implement role-based access (doctors, nurses, admin)"

□ Provide medication interaction rules
  "Check drug_interactions table for conflicts"
  "Warn if patient allergic to drug family"
  "Block if contraindicated with existing prescriptions"

□ Show dosage calculation formulas
  "Adult: 10mg/kg body weight, max 500mg"
  "Pediatric: 5mg/kg, max 200mg"
  Example: 70kg adult → 700mg → Cap at 500mg

□ Specify validation rules
  "Verify prescriber has DEA number for controlled substances"
  "Check patient age for pediatric/geriatric medications"
```

**AFTER Receiving Code:**
```
□ Verify data encryption
  Check: Passwords hashed (bcrypt)
  Check: Sensitive fields encrypted (AES-256)
  Check: API uses HTTPS only

□ Test medication interaction logic
  Test: Warfarin + Aspirin → Warn (bleeding risk)
  Test: Patient allergic to Penicillin → Block Amoxicillin

□ Verify dosage math (MULTIPLE test cases)
  Test: 50kg child → Pediatric dose
  Test: 100kg adult → Capped at max dose
  Test: Negative weight → Error

□ Check prescription validation
  Test: Controlled substance without DEA → Reject
  Test: Pediatric drug for adult patient → Warn

□ MANUAL REVIEW before production
  Healthcare code MUST have human review
```

### Common MEDIC8-Specific Failures

**Failure: Dosage Calculation Precision**
```javascript
// ❌ Claude generates (floating point error):
const dosage = weight * 10.5;  // Might be 104.99999

// ✓ Should be (fixed decimal):
const dosage = Math.round(weight * 10.5 * 100) / 100;  // Always 105.00
```

**Prevention:**
```
"Use fixed decimal arithmetic for all medical calculations.
No floating point for dosages, always round to 2 decimals."
```

---

## BRIGHTSOMA (Education Platform)

### High-Risk Areas

```
□ Question generation (curriculum alignment)
□ Grade calculation (fairness)
□ Difficulty ranking (accuracy)
□ Student data privacy (FERPA)
□ Plagiarism detection (false positives)
```

### Prevention Checklist

**BEFORE Requesting Code:**
```
□ Provide curriculum reference
  "Generate questions from: Grade 10 Biology, Chapter 5: Cell Division"
  "Topics: Mitosis, Meiosis, Cell Cycle"
  "Bloom's taxonomy: 40% Remember, 40% Understand, 20% Apply"

□ Show grading rubric
  "MCQ: 1 point correct, 0 points wrong"
  "Short answer: 0-2 points (rubric: concept, detail, example)"
  "Essay: 0-5 points (thesis, arguments, evidence, conclusion, grammar)"

□ Define difficulty criteria
  "Easy: Recall facts (What is mitosis?)"
  "Medium: Understand concepts (Explain difference mitosis/meiosis)"
  "Hard: Apply knowledge (Predict if cell count doubles after mitosis)"

□ Specify privacy requirements
  "Student names, grades, emails encrypted"
  "Parents can only see their own child's data"
  "Teachers can only see their own class"
```

**AFTER Receiving Code:**
```
□ Test question samples against curriculum
  Pick 10 generated questions
  Verify each tests a curriculum concept
  Check difficulty matches target

□ Verify grade logic with examples
  Test: All correct → Full score
  Test: All wrong → Zero
  Test: Partial credit calculation

□ Validate difficulty scoring
  Test: "Define mitosis" → Classified as Easy
  Test: "Compare mitosis and meiosis" → Medium
  Test: "Design experiment to observe mitosis" → Hard

□ Ask Claude to explain reasoning
  "Why is this question Medium difficulty?"
  "What curriculum concept does this test?"

□ Human review of first batch
  Teacher reviews 20-30 questions before production
```

### Common BRIGHTSOMA-Specific Failures

**Failure: Generated Questions Don't Match Curriculum**
```
❌ Claude generates:
"What is the capital of France?" (Wrong subject - geography not biology!)

✓ Should be:
"What are the main phases of mitosis?" (Matches curriculum: Grade 10 Biology)
```

**Prevention:**
```
"Generate questions ONLY from concepts in the provided curriculum.
After generating, verify each question maps to a specific curriculum topic.
List the topic for each question."
```

---

## DDA (Database Design Analyzer)

### High-Risk Areas

```
□ Data generation (must match schema)
□ Schema assumptions (might be wrong)
□ Performance impact (large data sets)
□ Data integrity (relationships)
□ SQL injection (from generated data)
```

### Prevention Checklist

**BEFORE Requesting Code:**
```
□ Provide schema explicitly
  Paste full CREATE TABLE statements
  Include all constraints, indexes, foreign keys

□ Show realistic data examples
  "users: first_name (John), last_name (Doe), email (john@example.com)"
  "Not: first_name (User1), last_name (LastName)"

□ Specify performance requirements
  "Generate 10K rows without timeout"
  "Batch inserts (1000 per transaction)"

□ Define data integrity rules
  "Every order must reference valid customer_id"
  "Every product must have valid category_id"
```

**AFTER Receiving Code:**
```
□ Test generated data matches schema
  Check data types (INT not VARCHAR)
  Check constraints (NOT NULL, UNIQUE, CHECK)
  Check value ranges

□ Verify data looks realistic
  Names: Real-looking, not "User1, User2"
  Emails: Valid format, diverse domains
  Dates: Reasonable ranges
  Amounts: Realistic values

□ Performance test before production
  Generate 1K rows → Measure time
  If >5 seconds → Optimize
  Test with actual database load

□ Backup before running
  ALWAYS backup before generating data
  Test on development database first

□ Rollback plan ready
  Know how to undo generated data
  Test rollback procedure
```

### Common DDA-Specific Failures

**Failure: Generated Data Violates Foreign Keys**
```sql
-- ❌ Claude generates:
INSERT INTO orders (customer_id, ...) VALUES (999, ...);
-- But customer_id=999 doesn't exist!

-- ✓ Should be:
SELECT id FROM customers ORDER BY RANDOM() LIMIT 1;  -- Get valid ID
INSERT INTO orders (customer_id, ...) VALUES (selected_id, ...);
```

**Prevention:**
```
"When generating data with foreign keys:
1. First query existing IDs from parent table
2. Randomly select from valid IDs
3. Use that ID in child table
Provide code that ensures referential integrity."
```

---

## CROWNPOINT (Inventory Management)

### High-Risk Areas

```
□ Stock calculations (accuracy critical)
□ Multi-location tracking
□ Batch/expiry management
□ Audit trail (who changed what when)
□ Reporting accuracy
```

### Prevention Checklist

**BEFORE Requesting Code:**
```
□ Specify stock calculation rules
  "Stock = Opening + Received - Sold - Damaged - Transferred"
  "Must be atomic (all or nothing)"

□ Define location tracking
  "Each item tracks location_id"
  "Transfers update both locations atomically"

□ Show batch/expiry scenarios
  "FIFO: Oldest batch sold first"
  "Alert: 30 days before expiry"
  "Block: Don't sell expired items"

□ Require audit trail
  "Log: user_id, action, timestamp, old_value, new_value"
  "Never delete, only mark inactive"
```

**AFTER Receiving Code:**
```
□ Test stock calculations
  Test: Receive 100, Sell 30 → Stock 70
  Test: Transfer 20 A→B → A:50, B:20
  Test: Concurrent updates (race conditions)

□ Verify batch/expiry logic
  Test: FIFO ordering
  Test: Expiry alerts
  Test: Block expired sales

□ Check audit trail completeness
  Every change logged
  Log entries immutable
  Searchable by user, date, item
```

---

## Universal Prevention Checklist

**For ALL Apps:**
```
□ SECURITY
  □ SQL injection prevented (parameterized queries)
  □ XSS prevented (output escaping)
  □ CSRF tokens present
  □ Secrets not hardcoded
  □ Input validation present

□ ERROR HANDLING
  □ Try-catch on risky operations
  □ Clear error messages
  □ Logging for debugging
  □ Graceful degradation

□ TESTING
  □ Happy path covered
  □ Edge cases covered
  □ Error cases covered
  □ Integration tested

□ DOCUMENTATION
  □ Function documented
  □ Edge cases explained
  □ Usage examples provided
```

---

## Summary

**App-Specific Prevention:**
- MADUUKA: Tenant isolation, pricing accuracy
- MEDIC8: HIPAA compliance, dosage precision, manual review
- BRIGHTSOMA: Curriculum alignment, grading fairness, human review
- DDA: Schema compliance, data realism, referential integrity
- CROWNPOINT: Stock accuracy, audit trails, FIFO logic

**Pattern:** Every app has unique high-risk areas → Tailor prevention to those risks

---

**See also:**
- `../SKILL.md` - Main ai-error-prevention skill
- `prevention-strategies.md` - The 7 prevention strategies
- `failure-modes.md` - Common Claude failures

**Last Updated:** 2026-02-07
