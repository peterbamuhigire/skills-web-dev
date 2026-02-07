# Common Claude Failure Modes & Prevention

**Purpose:** Identify and prevent Claude's most common mistakes

**Parent Skill:** ai-error-prevention

---

## The 5 Most Common Failure Modes

### Failure Mode 1: Incomplete Understanding

**Symptoms:**
```
You ask for feature
Claude implements basic version
Missing: Critical security, edge cases, error handling
```

**Example:**
```
You ask: "Create login system"
Claude creates: Basic login function
Missing:
- Password hashing
- Rate limiting
- Session management
- CSRF protection
- Account lockout
```

**Prevention:**
```
✓ Ask for COMPLETE specification first:

"List ALL requirements for a secure login system.
Include:
- Authentication method
- Password handling  (hashing, min length, complexity)
- Session management (duration, storage, renewal)
- Security measures (rate limiting, CSRF, lockout)
- Error handling (wrong password, account not found)
- Edge cases (concurrent logins, expired sessions)

Don't implement yet, just list requirements with details."

✓ Verify list is complete
✓ Add any missing requirements
✓ THEN ask for implementation
```

**Why This Works:**
- Forces Claude to think through complete requirements
- Reveals gaps in understanding
- Prevents incomplete implementation

---

### Failure Mode 2: Wrong Pattern/Approach

**Symptoms:**
```
Claude chooses suboptimal approach
Doesn't understand your use case
Solution works but isn't suitable
```

**Example:**
```
You ask: "Optimize this database query"
Claude adds generic index
Problems:
- Doesn't understand your data patterns
- Index might not help actual queries
- Might slow down writes
- Breaks other queries
```

**Prevention:**
```
✓ Provide CONTEXT about data and usage:

"Optimize this query. Context:
- Table: inventory_items
- Rows: 1M (growing 10K/month)
- Current queries:
  * 80%: SELECT * WHERE tenant_id = ? AND date > ?
  * 15%: SELECT * WHERE tenant_id = ? AND sku = ?
  * 5%: SELECT * WHERE tenant_id = ? AND category = ?
- Write frequency: 1000 inserts/day
- Current slow queries: [paste EXPLAIN output]

What indexes would help? Explain reasoning.
Consider: Index overhead on writes, query coverage, index size."

✓ Ask Claude to explain approach BEFORE implementing
✓ Verify approach makes sense for YOUR use case
```

**Why This Works:**
- Claude understands actual usage patterns
- Can choose right optimization strategy
- Considers trade-offs

---

### Failure Mode 3: Hallucinated Libraries

**Symptoms:**
```
Claude suggests library/API that doesn't exist
Or suggests deprecated/outdated library
```

**Example:**
```
Claude: "Use library awesome-validator v3.0"
Reality: Library is awesome-validator v2.5 (v3 doesn't exist)
Or: Library deprecated 2 years ago
```

**Prevention:**
```
✓ Always verify libraries exist BEFORE using:

"Before implementing, verify library X:
1. Provide official documentation URL
2. Current stable version number
3. Installation command (npm, composer, etc)
4. Confirm it's actively maintained (last update < 6 months)
5. Check for known vulnerabilities
6. Any better alternatives?

Don't implement until verified."

✓ Check npm/packagist/github yourself
✓ Don't install unverified libraries
```

**Why This Works:**
- Catches hallucinated libraries early
- Prevents wasted time debugging non-existent code
- Ensures library is current and maintained

---

### Failure Mode 4: Misunderstood Requirement

**Symptoms:**
```
Claude implements something different from what you wanted
Fulfills literal words but not intent
```

**Example:**
```
You: "Handle offline sync"
Claude creates: Basic sync function
Missing:
- Data order preservation (FIFO queue)
- Conflict resolution (multiple edits)
- Bandwidth management (batching)
- Resume after interruption
```

**Prevention:**
```
✓ Provide detailed spec with EXAMPLES:

"Implement offline sync. Requirements:

1. OPERATION QUEUING
   - Store operations in FIFO queue
   - Preserve order (create before update)
   Example: User creates item, then edits → Must sync in that order

2. CONFLICT RESOLUTION
   - Strategy: Last-write-wins
   - Track timestamps
   Example: User A edits offline, User B edits online → B's changes kept

3. BATCH SYNCHRONIZATION
   - Batch 10 operations per sync
   - Don't send one-by-one
   Example: 50 pending ops → 5 batches of 10

4. BANDWIDTH MANAGEMENT
   - Check connection quality
   - Defer large uploads on slow connection
   Example: Uploading image on 3G → Queue for WiFi

5. RESUME CAPABILITY
   - Track sync progress
   - Resume from interruption point
   Example: Synced 30/50 ops, lost connection → Resume from 31

Provide implementation plan BEFORE coding."

✓ Ask Claude to describe approach first
✓ Verify approach matches ALL requirements
```

**Why This Works:**
- Examples clarify intent
- Prevents misunderstanding
- Claude can ask questions before implementing

---

### Failure Mode 5: Lazy Solution

**Symptoms:**
```
Claude gives simplest answer
Doesn't handle edge cases
Works for happy path only
```

**Example:**
```
You: "Validate email"
Claude: email.includes('@')
Problems:
- Allows "a@" (no domain)
- Allows "@@test.com" (double @)
- Allows spaces
- Doesn't check domain format
```

**Prevention:**
```
✓ Explicitly demand edge case handling:

"Validate email. Must handle ALL these cases:

VALID (return true):
- user@domain.com
- first.last@sub.domain.com
- user+tag@domain.co.uk
- 123@domain.com

INVALID (return false):
- @ (no user or domain)
- user@ (no domain)
- @domain.com (no user)
- user@@domain.com (double @)
- user @domain.com (space)
- user@domain (no TLD)
- user@.domain.com (dot before domain)

Provide validation logic + tests for ALL 11 cases."

✓ Demand completeness upfront
✓ Provide test cases that MUST pass
```

**Why This Works:**
- Forces Claude to handle edge cases
- Prevents lazy solutions
- Test cases verify completeness

---

## Quick Reference: Failure Mode Prevention

| Failure Mode | Prevention Strategy | Key Action |
|--------------|---------------------|------------|
| Incomplete Understanding | Ask for spec first | List ALL requirements before code |
| Wrong Pattern | Provide context | Explain use case, data patterns, constraints |
| Hallucinated Libraries | Verify before use | Request docs URL, version, verify yourself |
| Misunderstood Requirement | Examples + scenarios | Show concrete examples of what you want |
| Lazy Solution | Demand edge cases | Provide test cases that MUST pass |

---

## Advanced: Detecting Failure Modes Early

### Red Flags (Warning Signs)

```
🚩 Claude uses vague language ("handle this", "process data")
   → Ask for specifics

🚩 Claude skips error handling
   → Demand try-catch and error messages

🚩 Claude doesn't mention edge cases
   → Ask "What edge cases does this handle?"

🚩 Claude's explanation is generic
   → Ask for concrete examples

🚩 Code has no input validation
   → Demand validation logic

🚩 Claude suggests library you've never heard of
   → Verify it exists before using
```

---

## Iterative Refinement Pattern

```
Claude generates code
    ↓
YOU: "What edge cases does this handle?"
    ↓
Claude lists 2-3 cases
    ↓
YOU: "What about [specific edge case]?"
    ↓
Claude: "Good point, I'll add that"
    ↓
Repeat until all edge cases covered
```

**This teaches Claude what you care about!**

---

## Summary

**5 Common Failure Modes:**
1. **Incomplete Understanding** - Missing security, edge cases, error handling
2. **Wrong Pattern** - Doesn't fit your use case
3. **Hallucinated Libraries** - Invents or uses deprecated libraries
4. **Misunderstood Requirement** - Fulfills words not intent
5. **Lazy Solution** - Simplest answer, misses edge cases

**Prevention:**
- Ask for spec BEFORE code
- Provide context and examples
- Verify libraries exist
- Demand edge case handling
- Watch for red flags

**Result:** Catch 80% of errors before they happen

---

**See also:**
- `../SKILL.md` - Main ai-error-prevention skill
- `prevention-strategies.md` - The 7 prevention strategies
- `app-specific-prevention.md` - App-specific prevention checklists

**Last Updated:** 2026-02-07
