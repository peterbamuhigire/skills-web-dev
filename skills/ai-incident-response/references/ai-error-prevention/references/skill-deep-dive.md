# ai-error-prevention Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

- `The Core Problem`
- `The 7 Prevention Strategies (Quick Reference)`
- `Common Claude Failure Modes (Summary)`
- `AI Development Error Prevention Framework`
- `App-Specific Prevention (Summary)`
- `The Golden Rule`
- `Acceptance Checklist`
- `Token Waste Prevention`
- `Integration with Other Skills`
- `Summary`

## The Core Problem

### Traditional vs AI-Assisted Development

```
Traditional Development:
You write code → Code fails → You debug → You fix

AI-Assisted Development:
You ask Claude → Claude generates code → Code might be:
├─ Perfect ✓
├─ Partially wrong (hallucination)
├─ Missing edge cases
├─ Insecure
├─ Inefficient
└─ Doesn't match your spec

YOU MUST: Verify, test, catch mistakes, know when to trust/distrust
```

### Why Claude Can Fail

```
1. HALLUCINATION - Invents facts/APIs/methods that don't exist
2. INCOMPLETE SOLUTIONS - Solves 80%, misses the 20%
3. MISUNDERSTANDING - Misunderstood your requirement
4. OUTDATED KNOWLEDGE - Knows old way, not new way
5. CONTEXT LIMITS - Forgot earlier context
6. LAZY SOLUTIONS - Simplest answer, not best answer
7. WRONG ASSUMPTIONS - Assumes constraints you didn't mention
```

---

## The 7 Prevention Strategies (Quick Reference)

**📖 See [prevention-strategies.md](references/prevention-strategies.md) for complete details with examples.**

### Strategy 1: Verification-First

**Rule:** NEVER accept code without verification

```
Claude generates → YOU STOP → Check:
□ Matches requirement?
□ Imports exist?
□ Obvious bugs?
□ Edge cases?
□ Secure?
→ Pass? Use it | Fail? Ask Claude to fix
```

---

### Strategy 2: Test-Driven Validation

**Rule:** Test Claude's code IMMEDIATELY

```
Claude generates → YOU WRITE TESTS:
□ Happy path
□ Boundary cases
□ Edge cases
□ Error cases
□ Security cases
→ Tests pass? Good | Tests fail? Fix
```

---

### Strategy 3: Specification Matching

**Rule:** Make Claude review against spec

```
You have SPEC → Claude generates → ASK CLAUDE:
"Check this against requirements. Does it:
□ Requirement 1?
□ Requirement 2?
□ Requirement 3?"
→ Gaps found? Fix | No gaps? Complete
```

---

### Strategy 4: Incrementalism

**Rule:** Break big requests into small steps

```
❌ DON'T: Ask for complete feature (Claude gets 50% right)

✓ DO: Break into steps:
Step 1: Data model → VERIFY ✓
Step 2: Core function → VERIFY ✓
Step 3: Edge cases → VERIFY ✓
Step 4: Error handling → VERIFY ✓
Step 5: Integration → VERIFY ✓
```

**Each step: 10-20 lines, easy to verify**

---

### Strategy 5: Dual Approach

**Rule:** Ask Claude to solve problem TWO ways

```
Ask Claude: "Solve problem X"
→ Claude gives Solution A

Ask Claude (new message): "Solve problem X differently"
→ Claude gives Solution B

COMPARE:
If A == B → Probably correct
If A ≠ B → One might be wrong
→ Ask Claude: "Compare. Which is better?"
```

---

### Strategy 6: Fallback Code

**Rule:** Keep simple backup implementation

```
Claude generates: Complex optimized solution
YOU ALSO WRITE: Simple naive solution (Plan B)

try {
  return claudeSolution();  // Try Claude's
} catch {
  return simpleFallback();  // Use backup
}
```

---

### Strategy 7: Documentation Validation

**Rule:** If Claude can't explain it, code might be wrong

```
Claude generates → YOU ASK:
"Document this:
1. What it does
2. Inputs (with types)
3. Outputs (format)
4. Possible errors
5. Edge cases
6. Usage examples"

If Claude explains clearly → Probably correct
If Claude struggles → Code might be wrong
```

---

## Common Claude Failure Modes (Summary)

**📖 See [failure-modes.md](references/failure-modes.md) for detailed prevention strategies.**

### Failure Mode 1: Incomplete Understanding
```
Problem: Claude implements basic version, misses critical parts
Prevention: Ask for COMPLETE spec first, verify before implementing
```

### Failure Mode 2: Wrong Pattern/Approach
```
Problem: Claude chooses suboptimal approach
Prevention: Provide context (data patterns, usage, constraints)
```

### Failure Mode 3: Hallucinated Libraries
```
Problem: Claude suggests library that doesn't exist
Prevention: Verify library exists (docs URL, version, install command)
```

### Failure Mode 4: Misunderstood Requirement
```
Problem: Claude implements something different
Prevention: Provide examples and scenarios
```

### Failure Mode 5: Lazy Solution
```
Problem: Claude gives simplest answer, misses edge cases
Prevention: Explicitly demand edge case handling with test cases
```

---

## AI Development Error Prevention Framework

**Complete Workflow:**

```
┌─────────────────────────────────────┐
│ PHASE 1: REQUEST PREPARATION        │
├─────────────────────────────────────┤
│ □ Use Clear Task pattern            │
│ □ Include specific constraints      │
│ □ Ask for structured output         │
│ □ Show examples                     │
│ □ Break into small steps            │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ PHASE 2: CLAUDE GENERATES           │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ PHASE 3: IMMEDIATE VERIFICATION     │
├─────────────────────────────────────┤
│ □ VERIFY: Match spec?               │
│ □ READ: Imports exist?              │
│ □ CHECK: Obvious bugs?              │
│ □ ASK: "Document this"              │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ PHASE 4: TESTING                    │
├─────────────────────────────────────┤
│ □ Write tests (happy, edge, error)  │
│ □ Run tests                         │
│ □ If fails → Back to Claude         │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ PHASE 5: QUALITY CHECKS             │
├─────────────────────────────────────┤
│ □ SECURITY: Vulnerabilities?        │
│ □ PERFORMANCE: Bottlenecks?         │
│ □ EDGE CASES: All handled?          │
│ □ ERROR HANDLING: Clear messages?   │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ PHASE 6: ITERATION (if needed)      │
├─────────────────────────────────────┤
│ If ANY check fails:                 │
│   → Specific feedback to Claude     │
│   → Claude fixes                    │
│   → Return to Phase 3               │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ PHASE 7: ACCEPTANCE                 │
├─────────────────────────────────────┤
│ All checks passed → USE CODE ✓      │
└─────────────────────────────────────┘
```

---

## App-Specific Prevention (Summary)

**📖 See [app-specific-prevention.md](references/app-specific-prevention.md) for complete checklists.**

### MADUUKA (Franchise ERP)
```
High-Risk: Multi-tenancy, pricing, inventory, payments
Prevention:
□ Explicitly require tenant isolation
□ Provide pricing formulas with examples
□ Test edge cases (discounts, taxes, stock)
□ Verify tenant_id in ALL queries
```

### MEDIC8 (Healthcare)
```
High-Risk: HIPAA, medication interactions, dosage calculations
Prevention:
□ List HIPAA requirements explicitly
□ Provide medication interaction rules
□ Show dosage formulas with examples
□ MANUAL REVIEW before production
```

### BRIGHTSOMA (Education)
```
High-Risk: Curriculum alignment, grading fairness
Prevention:
□ Provide curriculum reference
□ Show grading rubric
□ Define difficulty criteria
□ Human review of first batch
```

### DDA (Database Tool)
```
High-Risk: Schema compliance, data integrity
Prevention:
□ Provide full schema
□ Show realistic data examples
□ Test referential integrity
□ Backup before running
```

---

## The Golden Rule

```
TRUST BUT VERIFY

✓ Trust Claude's speed
✓ Trust Claude's knowledge
✓ Trust Claude to explain

✗ Don't trust without verification
✗ Don't skip testing
✗ Don't assume it's secure
✗ Don't use without understanding

YOUR JOB: Skeptical, test, verify
CLAUDE'S JOB: Generate, explain, fix
```

---

## Acceptance Checklist

Before accepting ANY code from Claude:

```
□ REQUIREMENTS
  □ Matches all requirements
  □ Handles edge cases
  □ Error cases handled

□ VERIFICATION
  □ Imports/libraries exist
  □ No hallucinated APIs
  □ Parses without errors

□ TESTING
  □ Happy path tested
  □ Edge cases tested
  □ Error cases tested
  □ All tests passing

□ SECURITY
  □ No SQL injection
  □ No XSS
  □ No exposed secrets
  □ Input validation present

□ QUALITY
  □ Readable
  □ Documented
  □ Follows patterns
  □ No performance issues

□ EXPLANATION
  □ Claude can explain it
  □ Edge cases explained
  □ Assumptions documented
  □ Usage examples provided

□ INTEGRATION
  □ Works with existing code
  □ No conflicts
  □ Error handling integrated
  □ Logging present
```

**If ALL checked → Accept**
**If ANY unchecked → Back to Claude**

---

## Token Waste Prevention

**How This Skill Saves Tokens:**

```
WITHOUT prevention:
Request → Wrong code → Discover later → Fix → Still wrong → Fix again
TOKENS WASTED: 4-5x

WITH prevention:
Request (clear spec) → Generate → Verify immediately → Fix once
TOKENS USED: 1-2x

SAVINGS: 50-75% fewer tokens
```

**Best Practices:**
```
✓ Be specific (prevents misunderstanding)
✓ Verify immediately (catch errors early)
✓ Specific feedback (faster fixes)
✓ Small steps (easier to verify)
✓ Test each step (no cascading errors)
```

---

## Integration with Other Skills

**Use this skill WITH:**
- `orchestration-best-practices` - Structure in generated code
- `ai-error-handling` - Validation after prevention
- `ai-assisted-development` - Prevent errors across multiple agents
- `prompting-patterns-reference` - Better requests = fewer errors

**Workflow:**
```
1. AI-ERROR-PREVENTION (this) → Request correctly, verify immediately
2. ORCHESTRATION-BEST-PRACTICES → Ensure code structure
3. AI-ERROR-HANDLING → Final validation layers
4. AI-ASSISTED-DEVELOPMENT → Coordinate multiple agents

Result: Minimal errors, maximum efficiency, lowest token waste
```

---


## Summary

**Core Concept:** Prevent errors BEFORE they happen by changing HOW you interact with Claude

**The 7 Strategies:**
1. Verification-First
2. Test-Driven Validation
3. Specification Matching
4. Incrementalism
5. Dual Approach
6. Fallback Code
7. Documentation Validation

**5 Common Failures:**
1. Incomplete Understanding
2. Wrong Pattern
3. Hallucinated Libraries
4. Misunderstood Requirement
5. Lazy Solution

**Result:** 50-75% fewer tokens wasted, higher quality code, faster development

**Next Steps:**
1. 📖 Read [prevention-strategies.md](references/prevention-strategies.md) for detailed strategy examples
2. 📖 Read [failure-modes.md](references/failure-modes.md) for failure prevention
3. 📖 Read [app-specific-prevention.md](references/app-specific-prevention.md) for your app's checklist
4. Apply to your next Claude request!

---

**Related Skills:**
- `orchestration-best-practices/` - Code structure enforcement
- `ai-error-handling/` - Validation after generation
- `ai-assisted-development/` - Multi-agent coordination
- `prompting-patterns-reference.md` - Better prompts
- `encoding-patterns-into-skills.md` - Creating pattern-enforcing skills

**Last Updated:** 2026-02-07
**Line Count:** ~481 lines (compliant)
