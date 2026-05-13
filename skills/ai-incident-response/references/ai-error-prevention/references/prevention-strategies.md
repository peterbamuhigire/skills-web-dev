# The 7 Prevention Strategies (Detailed Guide)

**Purpose:** Detailed explanation of each prevention strategy with examples

**Parent Skill:** ai-error-prevention

---

## Strategy 1: Verification-First (Catch Errors Immediately)

**Rule:** NEVER accept code without verification

**Workflow:**
```
Claude generates code
    ↓
YOU STOP (don't use it yet)
    ↓
Check 1: Does it match your requirement?
Check 2: Do all imports/APIs exist?
Check 3: Are there obvious bugs?
Check 4: Does it handle edge cases?
Check 5: Is it secure?
    ↓
If ALL checks pass → Use it
If ANY check fails → Ask Claude to fix
```

**Example:**
```javascript
// ❌ Claude gives you this:
const validate = (email) => {
  return email.includes('@');
};

// ✓ YOU VERIFY:
// PROBLEM 1: Doesn't validate format after @
// PROBLEM 2: No error handling
// PROBLEM 3: Doesn't handle edge cases (spaces, etc)

// ✓ YOU ASK CLAUDE:
"This validation is too simple. It should:
1. Check format: user@domain.com
2. Handle spaces and uppercase
3. Reject invalid domains
4. Return error message if invalid

Provide complete solution with test cases."
```

**Checklist Before Accepting Code:**
```
□ Matches all requirements
□ All imports/libraries exist
□ No obvious bugs
□ Handles edge cases
□ Secure (no SQL injection, XSS, etc)
□ Error handling included
□ Documented
```

---

## Strategy 2: Test-Driven Validation (Prove It Works)

**Rule:** Test Claude's code IMMEDIATELY before using

**Workflow:**
```
Claude generates function
    ↓
YOU WRITE TESTS FIRST (before using in app)
    ↓
Test 1: Happy path (normal case)
Test 2: Edge case 1
Test 3: Edge case 2
Test 4: Error case
    ↓
RUN TESTS
    ↓
If tests fail → Ask Claude to fix
If tests pass → Code is probably correct
```

**Example:**
```javascript
// Claude generates: calculateGrade(score)

// ✓ YOU TEST IMMEDIATELY:
test('Happy path: 85 → B', () => {
  expect(calculateGrade(85)).toBe('B');
});

test('Boundary: 90 → A', () => {
  expect(calculateGrade(90)).toBe('A');
});

test('Edge: 0 → F', () => {
  expect(calculateGrade(0)).toBe('F');
});

test('Error: negative throws', () => {
  expect(() => calculateGrade(-10)).toThrow();
});

test('Error: >100 throws', () => {
  expect(() => calculateGrade(150)).toThrow();
});

// If ANY test fails → Back to Claude with specific failure
```

**Test Categories (All Required):**
```
□ Happy path (normal use)
□ Boundary cases (min/max values)
□ Edge cases (empty, null, special characters)
□ Error cases (invalid input)
□ Security cases (injection attempts)
```

---

## Strategy 3: Specification Matching (Prevent Incomplete Solutions)

**Rule:** Make Claude review against spec BEFORE implementing

**Workflow:**
```
You have SPEC with requirements
    ↓
Claude generates code
    ↓
YOU ASK CLAUDE:
"Check this code against the requirements.
Does it:
□ Requirement 1?
□ Requirement 2?
□ Requirement 3?
List any gaps."
    ↓
Claude identifies gaps
    ↓
If gaps found → Claude fixes them
If no gaps → Code is complete
```

**Example:**
```
YOUR SPEC for validateEmail:
□ REQUIREMENT 1: Accept RFC 5322 format
□ REQUIREMENT 2: Reject invalid characters
□ REQUIREMENT 3: Handle international domains
□ REQUIREMENT 4: Return error messages
□ REQUIREMENT 5: Logic-based (not regex)

Claude generates code
    ↓
YOU ASK:
"Does this implementation meet all 5 requirements? Check each one."

Claude responds:
"Checking:
✓ Requirement 1: YES
✓ Requirement 2: YES
✗ Requirement 3: NO - doesn't handle international domains
✓ Requirement 4: YES
✗ Requirement 5: NO - uses regex"

Claude fixes both gaps → Recheck → All pass ✓
```

**Specification Checklist:**
```
□ All functional requirements implemented
□ All edge cases covered
□ All error cases handled
□ All performance requirements met
□ All security requirements met
□ No assumptions made without confirming
```

---

## Strategy 4: Incrementalism (Small, Verifiable Steps)

**Rule:** Break big requests into small steps, verify each

**Workflow:**
```
❌ DON'T: Ask for complete feature (Claude gets 50% right)

✓ DO: Break into steps:
Step 1: Data model → VERIFY ✓
Step 2: Core function → VERIFY ✓
Step 3: Edge case handling → VERIFY ✓
Step 4: Error handling → VERIFY ✓
Step 5: Integration → VERIFY ✓
    ↓
Each step verified → Whole system correct
```

**Example:**
```
❌ DON'T DO THIS:
"Create complete exam management system with questions,
grading, analytics, reporting, and student notifications"

Result: Claude generates 1000 lines, 50% correct, hard to debug

✓ DO THIS INSTEAD:

Request 1: "Create database schema for exams and questions"
  → Review schema
  → Test with sample data
  → VERIFY ✓

Request 2: "Create question generator. Input: topic, count.
           Output: array of questions with difficulty"
  → Test with examples
  → Verify difficulty scoring
  → VERIFY ✓

Request 3: "Create grading function. Input: answers, correct_answers.
           Output: score, grade, feedback"
  → Test with sample answers
  → Verify edge cases (all wrong, all correct)
  → VERIFY ✓

Each step: 10-20 lines, easy to verify, catches errors early
```

**Incremental Request Pattern:**
```
1. Start with data model/types
2. Then core logic (one function)
3. Then edge case handling
4. Then error handling
5. Then integration
6. Then optimization

VERIFY after EACH step (not at the end!)
```

---

## Strategy 5: Dual Approach (Verify Through Comparison)

**Rule:** Ask Claude to solve problem TWO different ways

**Workflow:**
```
Ask Claude: "Solve problem X"
    ↓
Claude gives Solution A
    ↓
Ask Claude (NEW CONTEXT): "Solve problem X differently"
    ↓
Claude gives Solution B
    ↓
COMPARE:
If A == B (same logic) → Probably correct
If A ≠ B (different) → One might be wrong
    ↓
Ask Claude: "Compare these. Which is better? Why?"
```

**Example:**
```
REQUEST 1: "Calculate tax. Sales tax is 15%. Handle rounding."

Claude gives Solution A:
function calculateTax(amount) {
  return Math.round(amount * 0.15 * 100) / 100;
}

REQUEST 2 (new message): "Calculate tax. 15% rate. Handle rounding.
                          Use different approach than typical."

Claude gives Solution B:
function calculateTax(amount) {
  const cents = Math.floor(amount * 100);
  const taxCents = Math.floor(cents * 15 / 100);
  return taxCents / 100;
}

COMPARE:
- Solution A: Floating point math (potential precision issues)
- Solution B: Integer math (more accurate for money!)

Ask: "Which handles edge cases better?"
Claude explains Solution B better for money calculations
```

**When to Use Dual Approach:**
```
□ Critical calculations (money, dosage, grades)
□ Security-sensitive code
□ Complex algorithms
□ Performance-critical code
□ When you're unsure of Claude's approach
```

---

## Strategy 6: Fallback Code (Always Have Plan B)

**Rule:** Keep simple backup implementation

**Workflow:**
```
Claude generates: Complex optimized solution
    ↓
YOU ALSO WRITE: Simple naive solution (Plan B)
    ↓
Use Claude's IF:
├─ It works ✓
├─ It's tested ✓
├─ It's secure ✓
    ↓
USE FALLBACK IF:
├─ Claude's breaks
├─ Can't verify it
├─ Edge cases fail
```

**Example:**
```javascript
// Claude's complex solution (optimized)
const efficientSort = (arr) => {
  // Complex algorithm Claude generated
  // Might have edge cases you haven't found
};

// Your simple fallback (always works)
const simpleSortFallback = (arr) => {
  return arr.sort((a, b) => a - b);
};

// Production usage:
try {
  return efficientSort(data);  // Try Claude's version
} catch (e) {
  console.error("Complex sort failed, using fallback:", e);
  return simpleSortFallback(data);  // Use backup
}
```

**Fallback Strategy:**
```
CRITICAL OPERATIONS: Always have fallback
NON-CRITICAL: Fallback optional but recommended

Examples of critical operations needing fallback:
□ Payment processing
□ Data validation
□ Authentication
□ Inventory calculations
□ Grade calculations
```

---

## Strategy 7: Documentation Validation (Explanation Test)

**Rule:** If Claude can't explain it clearly, code might be wrong

**Workflow:**
```
Claude generates code
    ↓
YOU ASK:
"Before I use this, document it:
1. Function signature with types
2. What it does (1-2 sentences)
3. Input requirements (edge cases)
4. Output format
5. Possible errors
6. Usage examples"
    ↓
IF Claude explains clearly → Probably correct
IF Claude struggles → Code might be wrong/unclear
```

**Example:**
```
Claude generates: Complex algorithm

You ask: "Document this function comprehensively"

✓ GOOD RESPONSE (code probably correct):
"Function: calculateShippingCost(weight, distance, speed)

What it does: Calculates shipping cost based on weight (kg),
distance (km), and delivery speed (standard/express)

Inputs:
- weight: number (0.1 - 1000 kg)
- distance: number (1 - 10000 km)
- speed: 'standard' | 'express'

Edge cases handled:
- weight < 0.1: throws error
- distance < 1: throws error
- invalid speed: defaults to 'standard'

Output: number (cost in USD, 2 decimal places)

Possible errors:
- InvalidWeightError: if weight out of range
- InvalidDistanceError: if distance < 1

Usage:
const cost = calculateShippingCost(5.5, 250, 'express');
// Returns: 45.75"

✗ BAD RESPONSE (code might be wrong):
"It calculates shipping cost based on some factors"
(Vague, no details → code unclear/wrong)
```

---

## Summary

**The 7 Strategies:**
1. **Verification-First** - Check before using (catch errors immediately)
2. **Test-Driven Validation** - Test immediately (prove it works)
3. **Specification Matching** - Verify completeness (prevent incomplete solutions)
4. **Incrementalism** - Small verifiable steps (easier debugging)
5. **Dual Approach** - Ask twice, compare (verify through comparison)
6. **Fallback Code** - Always have Plan B (safety net)
7. **Documentation Validation** - If Claude can't explain, it's wrong

**Apply ALL 7 for critical code**
**Apply 1, 2, 3, 7 minimum for all code**

---

**See also:**
- `../SKILL.md` - Main ai-error-prevention skill
- `failure-modes.md` - Common Claude failure modes and prevention
- `app-specific-prevention.md` - Prevention for MADUUKA, MEDIC8, BRIGHTSOMA, DDA

**Last Updated:** 2026-02-07
