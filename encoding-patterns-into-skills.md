# Encoding Orchestration & Error Handling into Skills

**Purpose:** Guide for creating skills that enforce patterns automatically

**Target Audience:** Developers creating reusable AI skills

**Question:** Can Claude automatically follow orchestration and error handling patterns?

**Answer:** YES! Through properly designed skills.

---

## Core Concept: Skills as Automatic Pattern Enforcers

### What is a Skill?

```
A Skill is:
├─ Knowledge base Claude reads
├─ Instructions Claude follows
├─ Best practices Claude applies
├─ Patterns Claude remembers
└─ Constraints Claude respects
```

### How Skills Enforce Patterns

```
You create SKILL with patterns
    ↓
Claude reads SKILL
    ↓
Claude learns patterns
    ↓
Claude applies patterns AUTOMATICALLY
    ↓
Result: Consistent, high-quality output
```

---

## The Formula for Pattern-Enforcing Skills

```
Effective Skill = Rules + Examples + Checklists + Decision Trees

1. RULES: Clear, measurable requirements
   ✓ "Every step MUST have try-catch"
   ✗ "Add error handling"

2. EXAMPLES: Show correct and incorrect patterns
   ✓ Show good code, bad code, and why
   ✗ Just describe without showing

3. CHECKLISTS: Verifiable requirements
   ✓ "Before finishing: [ ] Steps clear [ ] Errors handled"
   ✗ "Make sure it's good"

4. DECISION TREES: Clear branching logic
   ✓ "IF independent → parallel, ELSE sequential"
   ✗ "Do what makes sense"
```

---

## Pattern Encoding Template

### Template Structure

```markdown
# SKILL_NAME

## When to Use This Skill
[Specific triggers: "When generating X", "When building Y"]

## Core Principles
[The 5-10 commandments - non-negotiable rules]

## Pattern 1: [Name]
**Rule:** [Clear, measurable requirement]

```language
// DON'T: [Bad example]
[code showing anti-pattern]

// DO: [Good example]
[code showing correct pattern]
```

**Why:** [Explanation]

## Pattern 2: [Name]
[Repeat structure]

## Checklist
Before finishing, verify:
□ [Requirement 1]
□ [Requirement 2]
□ [Requirement 3]

## Anti-Patterns (What NOT to Do)
❌ [Anti-pattern 1]
❌ [Anti-pattern 2]

## Integration
Use this skill WITH: [Related skills]
```

---

## Real Example: Orchestration Pattern Encoding

### Encoding Sequential Orchestration

```markdown
### Pattern: Sequential Steps

**Rule:** Every multi-step operation MUST define clear steps with:
1. Step number in comments
2. Console log at start
3. Try-catch for errors
4. Output validation

**Example:**
```javascript
// ❌ DON'T: No clear steps
function process() {
  const a = step1();
  const b = step2(a);
  return step3(b);
}

// ✅ DO: Clear orchestration
async function process() {
  // STEP 1: Initial processing
  console.log("STEP 1: Starting");
  let a;
  try {
    a = await step1();
    if (!a) throw new Error("Step 1 failed");
  } catch (error) {
    console.error("STEP 1 FAILED:", error);
    return { success: false, step: 1 };
  }

  // STEP 2: Transformation
  console.log("STEP 2: Starting");
  let b;
  try {
    b = await step2(a);
    if (!b) throw new Error("Step 2 failed");
  } catch (error) {
    console.error("STEP 2 FAILED:", error);
    return { success: false, step: 2 };
  }

  // STEP 3: Finalization
  console.log("STEP 3: Starting");
  return step3(b);
}
```

**Checklist:**
□ Steps numbered in comments
□ Console logs at each step
□ Try-catch per step
□ Output validated
□ Error includes step number
```

---

## How to Tell Claude to Use Pattern-Enforcing Skills

### Option 1: Explicit Reference

```
"Use orchestration-best-practices skill to generate this feature:
[your request]"
```

Claude will:
1. Read the skill
2. Apply all 10 orchestration rules
3. Include step comments, error handling, validation
4. Show checklist verification

### Option 2: Include in Prompt

```
"Generate code following these patterns:
- Define clear steps (numbered)
- Add error handling per step
- Validate outputs
- Log progress

[your request]"
```

### Option 3: After Teaching (Implicit)

After using a skill once, Claude remembers:

```
First time:
You: "Use orchestration skill for inventory sync"
Claude: Reads skill, applies patterns

Second time:
You: "Build payment processing"
Claude: Remembers patterns, applies automatically
```

---

## Pattern Library: Common Patterns to Encode

### 1. Orchestration Patterns

**Encode in skill:**
- Sequential steps
- Parallel execution
- Conditional routing
- Looping with exit conditions
- Retry with backoff

### 2. Validation Patterns

**Encode in skill:**
- Input validation (always first)
- Output validation (after each step)
- Type checking
- Range checking
- Format validation

### 3. Error Handling Patterns

**Encode in skill:**
- Try-catch per step
- Specific error messages
- Recovery strategies
- Fallback mechanisms
- Error logging

### 4. Testing Patterns

**Encode in skill:**
- Happy path tests
- Edge case tests
- Error case tests
- Security tests
- Integration tests

### 5. Documentation Patterns

**Encode in skill:**
- JSDoc with types
- Usage examples
- Error documentation
- Dependency documentation

---

## Skill Effectiveness: Making Skills Stick

### Keys to Effective Pattern Encoding

1. **Be Specific**
   ```
   ✓ "Every function with >2 parameters MUST use object destructuring"
   ✗ "Use good parameter patterns"
   ```

2. **Show Examples**
   ```
   ✓ Show correct code + incorrect code + explanation
   ✗ Just describe the pattern
   ```

3. **Make it Measurable**
   ```
   ✓ "Code quality >= 80/100 points on checklist"
   ✗ "Code should be good quality"
   ```

4. **Provide Decision Logic**
   ```
   ✓ "IF (>3 steps) → orchestrate, ELSE → simple function"
   ✗ "Use orchestration when appropriate"
   ```

5. **Include Verification**
   ```
   ✓ Checklist: □ Item 1 □ Item 2 □ Item 3
   ✗ "Make sure everything is correct"
   ```

---

## Pattern Evolution: Improving Skills Over Time

### Iteration Workflow

```
STEP 1: Create Initial Skill
├─ Define patterns
├─ Show examples
└─ Create checklist

STEP 2: Use in Real Project
├─ Claude applies patterns
├─ Identify gaps or misunderstandings
└─ Note what Claude got wrong

STEP 3: Refine Skill
├─ Add clarifications for gaps
├─ Add examples for misunderstood patterns
├─ Update checklist
└─ Test with new request

STEP 4: Iterate
└─ Repeat steps 2-3 until Claude consistently produces correct output
```

### Example Refinement

**Initial Skill (vague):**
```markdown
"Add error handling to all functions"
```

**After Claude misunderstood:**
Claude added only one try-catch at top level

**Refined Skill (specific):**
```markdown
"Every step in a multi-step function MUST have its own try-catch block.

Example:
```javascript
// STEP 1
try {
  const result1 = await step1();
} catch (error) {
  console.error("STEP 1 FAILED:", error);
  return { success: false, step: 1, error };
}

// STEP 2
try {
  const result2 = await step2(result1);
} catch (error) {
  console.error("STEP 2 FAILED:", error);
  return { success: false, step: 2, error };
}
```

Checklist:
□ Each step has own try-catch
□ Each catch logs specific step number
□ Each catch returns which step failed
```

---

## Combining Skills for Maximum Effect

### Skill Stack Pattern

```
Base Skill: orchestration-best-practices
    ├─ Defines step structure
    ├─ Requires error handling
    └─ Enforces validation

Layer 2: ai-error-handling
    ├─ Adds 5-layer validation
    ├─ Enforces quality threshold
    └─ Requires documentation

Layer 3: app-specific-skill
    ├─ Applies domain rules
    ├─ Enforces business logic
    └─ Adds app-specific patterns

Result: Comprehensive, domain-specific, high-quality code
```

### How to Combine

```
"Use these skills together:
1. orchestration-best-practices (for structure)
2. ai-error-handling (for validation)
3. maduuka-patterns (for franchise-specific rules)

Generate inventory sync feature."
```

Claude will:
1. Apply orchestration (steps, error handling, logging)
2. Apply validation (5 layers, quality threshold)
3. Apply domain rules (tenant isolation, pricing rules)

---

## Quick Reference: Skill Creation Checklist

When creating a pattern-enforcing skill:

```
□ Title clearly describes when to use
□ Core principles listed (5-10 rules)
□ Each pattern has:
  □ Clear rule statement
  □ Good example
  □ Bad example (anti-pattern)
  □ Explanation of why
□ Decision tree for when to apply
□ Verification checklist
□ Integration notes (works with X skill)
□ Examples use real code (not pseudocode)
□ Anti-patterns explicitly shown
□ Measurable success criteria
```

---

## Summary

**Can Claude automatically follow patterns? YES!**

**How:**
1. Create skill with patterns
2. Include rules + examples + checklists + decision trees
3. Claude reads skill
4. Claude applies patterns automatically

**Formula:**
```
Skill = Rules + Examples + Checklists + Decision Trees
Claude + Skill = Automatic Pattern Enforcement
Result = Consistent, high-quality output
```

**Skills Created:**
- ✅ `orchestration-best-practices/` - The 10 orchestration rules
- ✅ `ai-error-handling/` - The 5-layer validation stack
- ✅ `ai-assisted-development/` - AI agent coordination patterns

**How to Use:**
- Reference skill explicitly: "Use [skill-name] for this task"
- Or after first use, Claude remembers and applies automatically

**Result:** Production-ready, pattern-compliant code every time.

---

**Related Skills:**
- `orchestration-best-practices/` - Orchestration enforcement
- `ai-error-handling/` - Validation enforcement
- `ai-assisted-development/` - AI coordination patterns
- `prompting-patterns-reference.md` - Better AI prompts
- `orchestration-patterns-reference.md` - Orchestration theory

**Last Updated:** 2026-02-07
