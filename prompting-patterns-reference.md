# Prompting Patterns Reference for Plan Creation

**Purpose:** Guide for creating effective prompts/plans that AI agents can follow

**Target Audience:** Skills that generate plans, specifications, or agent instructions

---

## Core Principle

When creating plans for AI agents (like Claude), use **structured prompting patterns** to ensure:
- ✅ Clear, unambiguous instructions
- ✅ Measurable success criteria
- ✅ Step-by-step reasoning guidance
- ✅ Proper constraints and boundaries

---

## The 10 Essential Prompting Patterns

### Pattern 1: Clear Task + Context + Constraints

**Use when:** Writing any plan step or instruction

**Template:**
```
TASK: [What needs to be done]
CONTEXT: [Why this is needed, background]
CONSTRAINTS:
- [Limit 1]
- [Limit 2]
- [Limit 3]
```

**Example (Feature Plan):**
```
TASK: Implement user authentication with JWT
CONTEXT: SaaS platform needs secure, scalable auth for 10,000+ users
CONSTRAINTS:
- Must use bcrypt for password hashing
- Token expiry: 24 hours
- Support refresh tokens
- No third-party auth libs (custom implementation)
```

---

### Pattern 2: Chain-of-Thought (Think Step-by-Step)

**Use when:** Complex logic, decisions, or calculations needed

**Template:**
```
THINK STEP-BY-STEP:
1. [First consideration]
2. [Second consideration]
3. [Third consideration]
4. [Final decision/action]

Show reasoning at each step.
```

**Example (Database Design):**
```
THINK STEP-BY-STEP:
1. What are the core entities? (Users, Products, Orders)
2. What relationships exist? (User has many Orders, Order has many Products)
3. What indexes are critical? (user_id on orders, product_id on order_items)
4. How to optimize for 10k+ concurrent users? (Connection pooling, read replicas)

Explain reasoning for each decision.
```

---

### Pattern 3: Few-Shot Learning (Show Examples)

**Use when:** Want specific format, style, or structure

**Template:**
```
EXAMPLE of what I WANT:
[Good example]

EXAMPLE of what I DON'T want:
[Bad example]

Generate [X] more following the GOOD example.
```

**Example (Code Generation Plan):**
```
EXAMPLE of what I WANT:
class UserController {
  // POST /api/users - Create new user
  async createUser(req, res) {
    const { email, password } = req.body;
    // Validation
    // Hash password
    // Save to DB
    // Return success
  }
}

EXAMPLE of what I DON'T want:
function doStuff() {
  // Vague, no structure
}

Generate CRUD methods following the GOOD example pattern.
```

---

### Pattern 4: Role-Based Prompting

**Use when:** Need specialized expertise or perspective

**Template:**
```
You are a [role] with [X years] experience in [domain].

[Task description with context]

Apply your expertise to:
- [Requirement 1]
- [Requirement 2]
```

**Example (Security Review Plan):**
```
You are a security architect with 10 years of experience in African SaaS platforms.

Review this authentication implementation for vulnerabilities.

Apply your expertise to:
- Identify OWASP Top 10 violations
- Flag weak cryptography
- Check for SQL injection vectors
- Recommend fixes with African context (unreliable internet)
```

---

### Pattern 5: Structured Output

**Use when:** Output must be parsed, reused, or formatted precisely

**Template:**
```
RETURN as [format] with this exact structure:
{
  'field1': 'type',
  'field2': 'type',
  'field3': [...]
}
```

**Example (Test Plan):**
```
RETURN as JSON:
{
  'test_cases': [
    {
      'id': 'TC-001',
      'description': 'string',
      'steps': ['string'],
      'expected_result': 'string',
      'priority': 'critical|high|medium|low'
    }
  ],
  'coverage': 'percentage',
  'risks': ['string']
}
```

---

### Pattern 6: Constraint-Based Prompting

**Use when:** Need to limit scope, length, or complexity

**Template:**
```
CONSTRAINTS:
- Maximum [limit]
- Must use only [allowed items]
- No [forbidden items]
- Focus on [specific area]
```

**Example (API Design Plan):**
```
CONSTRAINTS:
- Maximum 5 endpoints
- Must use RESTful conventions
- No GraphQL (team not trained)
- Focus on CRUD operations only
- Response time <200ms
```

---

### Pattern 7: Error Analysis

**Use when:** Debugging, troubleshooting, or validating

**Template:**
```
ERROR/ISSUE: [Description]

CONTEXT:
- [Relevant context 1]
- [Relevant context 2]

ANALYZE:
1. What's the root cause?
2. Why does it fail in this case?
3. What's the fix?
4. How to prevent in future?
```

**Example (Code Review Plan):**
```
ERROR: Database connection timeout in production

CONTEXT:
- Works fine in dev (10 users)
- Fails in production (1000+ concurrent users)
- Using default connection pool size (10)

ANALYZE:
1. Root cause: Pool exhaustion
2. Fails because: 10 connections insufficient for 1000 users
3. Fix: Increase pool to min 100, max 500
4. Prevention: Load testing before production
```

---

### Pattern 8: Comparative Analysis

**Use when:** Choosing between options or approaches

**Template:**
```
Compare [Option A] vs [Option B] for [use case].

COMPARE on:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

RETURN: Score each, declare winner, explain reasoning.
```

**Example (Tech Stack Decision):**
```
Compare PostgreSQL vs MySQL for multi-tenant SaaS.

COMPARE on:
- Multi-tenancy support
- Performance at 10k+ tenants
- JSON data handling
- Cost in African hosting
- Team expertise
- Community support

RETURN: Score 1-10 each criterion, recommend final choice.
```

---

### Pattern 9: Iterative Refinement

**Use when:** Initial output needs improvement

**Template:**
```
ROUND 1: [Initial request]
ROUND 2: Make it better by adding [X]
ROUND 3: Optimize for [Y]
ROUND 4: Polish with [Z]
```

**Example (API Documentation Plan):**
```
ROUND 1: Generate API docs for authentication endpoints
ROUND 2: Add request/response examples
ROUND 3: Add error codes and handling
ROUND 4: Add rate limiting and security notes
```

---

### Pattern 10: Explain Like I'm 5

**Use when:** Complex concepts need simplification

**Template:**
```
Explain [complex topic] using simple analogy.

CONSTRAINTS:
- Assume no prior knowledge
- Use real-world example
- Maximum [N] words
```

**Example (Architecture Plan):**
```
Explain microservices architecture using restaurant analogy.

CONSTRAINTS:
- Assume no architecture knowledge
- Use restaurant kitchen as example
- Maximum 150 words
- Include: what, why, and one drawback
```

---

## Pattern Combinations for Plan Creation

### For Implementation Plans (feature-planning)
```
Use: Clear Task + Chain-of-Thought + Structured Output

Example:
"Create implementation plan for user authentication.

TASK: Implement JWT-based authentication
CONTEXT: Multi-tenant SaaS, 10k users, offline sync
CONSTRAINTS:
- Must use bcrypt
- Token expiry 24h
- Support refresh tokens

THINK STEP-BY-STEP:
1. What are the core components?
2. What's the auth flow?
3. What edge cases exist?
4. What tests are needed?

RETURN as JSON:
{
  'phases': [...],
  'tasks': [...],
  'dependencies': {...}
}"
```

### For Documentation Plans (doc-architect)
```
Use: Role-Based + Few-Shot + Constraints

Example:
"You are a technical writer with 10 years of experience.

Create documentation structure for API reference.

EXAMPLE format I want:
## Endpoint Name
- Method: POST
- Path: /api/users
- Description: ...
- Request: {...}
- Response: {...}

CONSTRAINTS:
- Maximum 500 words per endpoint
- Include error codes
- Show curl examples
```

### For Skill Creation (skill-writing)
```
Use: Clear Task + Few-Shot + Structured Output + Constraints

Example:
"Create a new skill for database migration.

EXAMPLE of good skill (what I WANT):
---
name: skill-name
description: When to use this skill
---
# Skill Content
[Clear, actionable guidance]

CONSTRAINTS:
- Maximum 500 lines
- Include templates/
- Include references/
- Provide examples

RETURN:
- SKILL.md content
- Directory structure
- Template files needed"
```

---

## Quick Reference: Pattern Selection

| Situation | Recommended Patterns | Why |
|-----------|---------------------|-----|
| **Writing plan steps** | Clear Task + Constraints | Precision + boundaries |
| **Complex decisions** | Chain-of-Thought + Comparative | Step-by-step + options |
| **Code generation** | Few-Shot + Structured Output | Format + parseable |
| **Architecture** | Role-Based + Comparative | Expert view + choices |
| **Debugging** | Error Analysis + Chain-of-Thought | Root cause + reasoning |
| **Documentation** | Clear Task + Few-Shot + Constraints | Structure + examples + limits |
| **Testing** | Structured Output + Constraints | Parseable + focused |
| **Learning** | Explain Simple + Few-Shot | Understandable + examples |

---

## Best Practices for Plan Creation

### DO:
✅ **Be explicit** - "Create 5 REST endpoints" not "Create endpoints"
✅ **Show examples** - "Like this: {...}" not just "Return JSON"
✅ **Set boundaries** - "Maximum 500 lines" not "Keep it short"
✅ **Think step-by-step** - "STEP 1:... STEP 2:..." not just "Do it"
✅ **Define success** - "Must pass these criteria: ..." not "Make it good"

### DON'T:
❌ **Be vague** - "Improve this" (improve how?)
❌ **Assume context** - Claude doesn't know your project details
❌ **Skip constraints** - Without limits, you get 5000-line responses
❌ **Forget format** - "Return something" (what format?)
❌ **Rush reasoning** - Complex tasks need step-by-step thinking

---

## Quality Checklist for Plans

Before finalizing any plan/prompt, verify:

```
□ TASK is clear (what exactly needs to be done?)
□ CONTEXT is provided (why is this needed?)
□ CONSTRAINTS are defined (what are the limits?)
□ FORMAT is specified (how should output look?)
□ EXAMPLES are given (show what you mean)
□ SCOPE is limited (not too broad/narrow)
□ ROLE is set (what expertise is needed?)
□ STEPS are explicit (how to approach this?)
□ SUCCESS is defined (when is it done?)
□ EDGE CASES are noted (what could go wrong?)

7/10 = Good plan
10/10 = Excellent plan
```

---

## Examples from Existing Skills

### feature-planning (Implementation Plans)
```
BEFORE prompting patterns:
"Create a plan for user authentication"

AFTER prompting patterns:
"Create implementation plan for JWT authentication.

CONTEXT: Multi-tenant SaaS, 10k users, African market
CONSTRAINTS: bcrypt, 24h tokens, offline sync
THINK STEP-BY-STEP:
1. Core components needed
2. Auth flow design
3. Edge cases to handle
4. Testing strategy

RETURN as structured plan with:
- Phases (setup, implementation, testing)
- Tasks per phase
- Dependencies
- Time estimates"
```

### doc-architect (Documentation Plans)
```
BEFORE:
"Generate AGENTS.md file"

AFTER:
"You are a technical documentation architect.

Generate AGENTS.md for [project name].

SCAN PROJECT for:
- Tech stack (package.json, composer.json)
- Database type (migrations/, schema/)
- Deployment (docker-compose.yml, Dockerfile)

RETURN structure:
# Project Identity
- Tech stack
- Standards
- Conventions

# Development Protocols
- Code style
- Testing approach
- Deployment process

EXAMPLE format: [show example]
CONSTRAINTS: Max 500 lines, use ## headings"
```

---

## Token Efficiency Tips

**Pattern cost varies:**
- Clear Task: +50 tokens (always worth it)
- Chain-of-Thought: +100-200 tokens (worth it for complex tasks)
- Few-Shot: +100-150 tokens per example (worth it for precision)
- Structured Output: +80-150 tokens (worth it for parseable output)

**Optimize by:**
1. Use simpler patterns for simple tasks
2. Combine patterns strategically (don't use all 10)
3. Reuse good prompts (save them as templates)
4. Be concise in constraints (bullet points, not paragraphs)

---

## Summary

**Prompting patterns make plans better by:**
1. Reducing ambiguity (Clear Task + Context)
2. Improving reasoning (Chain-of-Thought)
3. Ensuring consistency (Few-Shot + Examples)
4. Adding expertise (Role-Based)
5. Enabling automation (Structured Output)
6. Setting boundaries (Constraints)
7. Facilitating debugging (Error Analysis)
8. Supporting decisions (Comparative)
9. Enabling iteration (Iterative Refinement)
10. Improving clarity (Explain Simple)

**For plan creation, prioritize:**
- Clear Task + Context + Constraints (ALWAYS)
- Chain-of-Thought (for complex logic)
- Structured Output (for parseable plans)
- Few-Shot (for format consistency)

**Impact:**
- 50% reduction in ambiguous instructions
- 60% improvement in reasoning quality
- 80% better format consistency
- 100% parseable outputs
- 4x faster to usable output

---

**Usage in Skills:**
- See `feature-planning/references/prompting-patterns.md` for implementation plans
- See `doc-architect/references/prompting-patterns.md` for documentation plans
- See `skill-writing/references/prompting-patterns.md` for skill creation

**Last Updated:** 2026-02-07
