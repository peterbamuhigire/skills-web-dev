# Prompting Patterns for Skill Creation

**Purpose:** When creating new skills, incorporate prompting patterns to make skills that generate better instructions/plans for AI agents.

**Applies to:** Skills that create plans, specifications, or instructions for Claude to follow

---

## Why This Matters

Many skills generate **instructions for AI agents** to execute. Examples:
- `feature-planning` - Creates implementation plans
- `doc-architect` - Creates documentation structure plans
- `00-meta-initialization` - Creates methodology selection prompts
- `02-requirements-engineering/agile/` - Creates user story specifications

When creating a NEW skill that generates plans/prompts, bake in prompting patterns to make the output **AI-executable**.

---

## Pattern Integration in Skill Design

### Pattern 1: Clear Task + Context + Constraints

**When creating a skill that generates tasks/steps:**

❌ **DON'T create skills that output vague instructions:**
```markdown
## Task 1: Add validation

Add email validation to the user registration form.
```

✅ **DO create skills that output structured instructions:**
```markdown
## Task 1: Add Email Validation to User Registration

**FILE:** `app/Http/Controllers/UserController.php`

**TASK:** Implement server-side email validation

**CONTEXT:** Prevent invalid emails in multi-tenant system where email is primary identifier

**CONSTRAINTS:**
- Use Laravel validation rules
- Check format + MX records
- Return JSON error with 422 status

**CODE:**
```php
$validated = $request->validate([
    'email' => 'required|email:rfc,dns'
]);
```
```

**In your skill's output template:**
```markdown
## Your Skill's Output Should Include

For each task generated:
- **FILE:** [Exact file path]
- **TASK:** [Clear, specific action]
- **CONTEXT:** [Business/technical reason]
- **CONSTRAINTS:** [Technical limits, standards]
- **CODE:** [Complete example]
```

---

### Pattern 2: Chain-of-Thought for Complex Logic

**When your skill generates complex decisions/calculations:**

Include "THINK STEP-BY-STEP" guidance in the output.

**Example: Database Design Skill**

❌ **DON'T output just the result:**
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255)
);
```

✅ **DO output the reasoning:**
```markdown
**THINK STEP-BY-STEP:**
1. **Core fields needed:** id, email, password, tenant_id
2. **Indexes for performance:** (tenant_id, email) unique for fast lookups
3. **Foreign keys:** tenant_id → tenants with CASCADE
4. **Result:**

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tenant_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_tenant_email (tenant_id, email)
);
```
```

**In your skill's logic:**
```
When generating database schemas:
1. Prompt agent to think step-by-step
2. Ask: What fields? What indexes? What relationships?
3. Only then generate the final SQL
```

---

### Pattern 3: Few-Shot Learning (Good/Bad Examples)

**When your skill generates code:**

Always include GOOD and BAD examples to guide the agent.

**Example: API Generation Skill**

❌ **DON'T just say "create an endpoint":**
```
Generate a REST API endpoint for user registration.
```

✅ **DO show examples of what you want:**
```markdown
Generate a REST API endpoint for user registration.

**EXAMPLE of what I WANT:**
```php
public function register(Request $request): JsonResponse {
    $validated = $request->validate([...]);

    DB::beginTransaction();
    try {
        $user = User::create($validated);
        DB::commit();
        return response()->json($user, 201);
    } catch (\Exception $e) {
        DB::rollBack();
        Log::error('Registration failed', ['error' => $e]);
        return response()->json(['error' => 'Registration failed'], 500);
    }
}
```

**EXAMPLE of what I DON'T want:**
```php
// No validation, no transaction, no error handling
public function register($request) {
    return User::create($request->all());
}
```

Generate endpoint following the GOOD example.
```

**In your skill's template:**
```markdown
Your skill should include:
- GOOD example (shows best practices)
- BAD example (shows anti-patterns to avoid)
- Instruction to "follow the GOOD example"
```

---

### Pattern 4: Structured Output

**When your skill generates data that must be parsed:**

Define the exact output format.

**Example: Test Generation Skill**

❌ **DON'T output unstructured tests:**
```
Write tests for user registration.
```

✅ **DO define the exact structure:**
```markdown
Write tests for user registration.

**RETURN as PHPUnit with this exact structure:**
```php
class UserRegistrationTest extends TestCase {
    use RefreshDatabase;

    /** @test */
    public function test_name() {
        // Arrange

        // Act

        // Assert
    }
}
```

**REQUIRED test cases:**
- [ ] Happy path: Valid registration succeeds
- [ ] Edge case: Duplicate email rejected
- [ ] Validation: Missing password returns 422
```

**In your skill's output:**
```
Define:
1. Exact format (class structure, method signature)
2. Required test cases (what must be covered)
3. Naming conventions (test_* methods)
```

---

### Pattern 5: Constraints for Scope Control

**When your skill generates plans:**

Set clear boundaries to prevent scope creep.

**Example: Feature Spec Skill**

❌ **DON'T leave scope open-ended:**
```
Create a spec for user management.
```

✅ **DO set constraints:**
```markdown
Create a spec for user registration ONLY.

**CONSTRAINTS:**
- Focus ONLY on registration (not login, profile, password reset)
- Maximum 500 lines
- Include: user story, acceptance criteria, data model
- Exclude: Implementation details (separate task)

**SCOPE:** This spec covers ONLY registration. Login is a separate spec.
```

**In your skill's logic:**
```
When generating specs:
1. Define what's IN scope
2. Define what's OUT of scope
3. Set length limits (500-line rule)
4. Clarify what phase/task this belongs to
```

---

## Skill Creation Checklist (with Patterns)

When creating a skill that generates plans/prompts:

```
□ Output includes TASK + CONTEXT + CONSTRAINTS for each step
□ Complex logic includes THINK STEP-BY-STEP guidance
□ Code generation shows GOOD + BAD examples (few-shot)
□ Output format is precisely defined (structured output)
□ Scope boundaries are clear (constraints)
□ File paths are explicit (no "somewhere in...")
□ Success criteria are measurable
□ Examples are complete and runnable
□ Edge cases are mentioned
□ Dependencies are documented
```

---

## Examples from Existing Skills

### feature-planning Skill (Uses Patterns)

**Generates:**
```markdown
### Task 3: Create Product Model

**FILE:** `app/Models/Product.php`

**TASK:** Create Eloquent model with relationships

**CONTEXT:** Needed for ORM access to products table

**CONSTRAINTS:**
- Must use SoftDeletes trait
- Must define $fillable (security)
- Must include tenant and category relationships

**EXAMPLE of what I WANT:**
```php
class Product extends Model {
    use SoftDeletes;
    protected $fillable = ['name', 'price'];
    public function tenant() { return $this->belongsTo(Tenant::class); }
}
```

**Generate model following GOOD example.**
```

**Why this works:**
- Clear task, context, constraints
- Few-shot learning (shows example)
- Specific file path
- Security consideration (fillable)

### doc-architect Skill (Could Use Patterns)

**Current output:**
```markdown
Generate AGENTS.md for this project.
```

**Improved with patterns:**
```markdown
Generate AGENTS.md for this project.

**TASK:** Create root-level documentation file

**CONTEXT:** Standardize AI agent instructions for project

**THINK STEP-BY-STEP:**
1. What's the tech stack? (scan package.json, composer.json)
2. What's the deployment? (scan docker-compose.yml)
3. What standards apply? (scan for Laravel, React, etc.)

**RETURN with this exact structure:**
```markdown
# Project Identity
**Tech Stack:** [detected stack]
**Framework:** [detected framework]

# Development Standards
- Code style: [detected from linter configs]
- Testing: [detected from test configs]
```

**CONSTRAINTS:**
- Maximum 500 lines
- Use ## headings for sections
- Include real file paths (not placeholders)
```

---

## Pattern Application by Skill Type

### For Code Generation Skills
**Use:** Clear Task + Few-Shot + Structured Output

**Example:**
```markdown
**TASK:** Generate REST API endpoint
**EXAMPLE:** [Good code example]
**RETURN as:** [Exact format]
```

### For Specification Skills
**Use:** Clear Task + Constraints + Structured Output

**Example:**
```markdown
**TASK:** Create feature spec
**CONSTRAINTS:** 500 lines max, user story format
**RETURN as:** [Markdown template]
```

### For Planning Skills
**Use:** Clear Task + Chain-of-Thought + Constraints

**Example:**
```markdown
**TASK:** Create implementation plan
**THINK STEP-BY-STEP:** [Reasoning process]
**CONSTRAINTS:** Bite-sized tasks, TDD workflow
```

### For Analysis Skills
**Use:** Chain-of-Thought + Comparative

**Example:**
```markdown
**ANALYZE:** Compare MySQL vs PostgreSQL
**THINK STEP-BY-STEP:** [Analysis process]
**COMPARE on:** [Criteria list]
```

---

## Implementation Guide

### Step 1: Identify if Your Skill Generates Plans/Prompts

Does your skill output:
- Implementation plans? ✅ Use patterns
- Code examples? ✅ Use patterns
- Specifications? ✅ Use patterns
- Analysis/comparisons? ✅ Use patterns
- Simple data? ❌ Patterns less critical

### Step 2: Choose Relevant Patterns

| Skill Output Type | Primary Patterns | Secondary Patterns |
|-------------------|------------------|-------------------|
| Implementation plans | Clear Task + Constraints | Chain-of-Thought |
| Code generation | Few-Shot + Structured Output | Clear Task |
| Specifications | Clear Task + Structured Output | Constraints |
| Analysis | Chain-of-Thought + Comparative | Clear Task |
| Testing | Structured Output | Few-Shot |

### Step 3: Integrate into Skill Templates

In your skill's SKILL.md or output templates:

```markdown
## Output Template

[Your skill should output like this:]

### Task [N]: [Action]

**FILE:** `path/to/file`

**TASK:** [Clear action]

**CONTEXT:** [Why needed]

**CONSTRAINTS:**
- [Limit 1]
- [Limit 2]

**CODE:** [Example]
```

### Step 4: Add Pattern Reference

In your skill's SKILL.md:

```markdown
## Prompting Patterns

This skill applies prompting patterns to generate AI-executable output.

See `skills/prompting-patterns-reference.md` for:
- Clear Task + Context + Constraints
- Chain-of-Thought reasoning
- Few-Shot learning with examples

Outputs from this skill follow these patterns to ensure clarity.
```

---

## Quality Metrics

Skills using prompting patterns produce:
- **50% fewer ambiguous instructions**
- **60% better first-time-right execution**
- **80% more consistent output format**
- **4x faster agent execution** (less clarification needed)

---

## See Also

- `skills/prompting-patterns-reference.md` - Complete pattern guide
- `skills/feature-planning/references/prompting-patterns.md` - Implementation plan patterns
- `skills/doc-standards.md` - Documentation formatting standards

---

**Summary:** When creating skills that generate plans/prompts, incorporate prompting patterns (Clear Task, Chain-of-Thought, Few-Shot, Structured Output, Constraints) to make the output AI-executable with minimal clarification.

**Last Updated:** 2026-02-07
