# orchestration-best-practices Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays compact.

## Included Sections

- `Decision Tree: When to Use What`
- `Checklist: Before Finishing`
- `Anti-Patterns (What NOT to Do)`
- `Summary`

## Decision Tree: When to Use What

```
Is this a multi-step operation?
├─ NO → Use simple function
└─ YES → Continue

Do steps depend on each other?
├─ YES → Sequential orchestration
└─ NO → Parallel orchestration

Can it fail?
├─ YES → Add error handling + fallback
└─ NO → Add error handling anyway (Murphy's Law)

Is it critical?
├─ YES → Add retry logic + multiple fallbacks
└─ NO → Add single fallback

Does quality matter?
├─ YES → Add output validation loops
└─ NO → Add output validation anyway (quality always matters)
```

---

## Checklist: Before Finishing

Every time you generate orchestration code, verify:

```
□ Steps clearly defined (numbered comments)
□ Dependencies identified (diagram in comments)
□ Inputs validated (at entry point)
□ Error handling added (try-catch per step)
□ Outputs validated (after each step)
□ Progress logged (start + complete per step)
□ Documentation added (JSDoc with examples)
□ Tests included (happy + edge + error cases)
□ Fallback included (for critical operations)
□ Parallelization considered (Promise.all if independent)
```

**If all checked → Good to go!**
**If any missing → Add before finishing!**

---

## Anti-Patterns (What NOT to Do)

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Everything in one function | No clear steps, no error handling, impossible to debug | Break into numbered steps |
| Silent failures (`catch {}`) | Errors disappear, bugs become invisible | Always log and return error details |
| No input validation | Crashes on unexpected data, security vulnerabilities | Validate at every entry point |
| Generic error messages ("Something went wrong") | Useless for debugging and user support | Include step name, specific error, recovery hint |
| No logging | Can't trace what happened when things fail | Log start + completion of every step |

- `feature-planning` - Implementation plans should follow these patterns
- `ai-assisted-development` - AI agents should generate orchestrated code
- `api-error-handling` - API endpoints need orchestration
- `prompting-patterns-reference` - Better prompts = better orchestrated code

**This skill ensures:**
- Consistent code structure across all AI-generated code
- Better debugging (clear logs, error messages)
- Higher reliability (error handling, fallbacks)
- Faster execution (parallelization where possible)

---

## Summary

**The 10 Commandments:**
1. Define steps explicitly
2. Identify dependencies
3. Validate inputs
4. Handle errors
5. Validate outputs
6. Log progress
7. Document thoroughly
8. Test comprehensively
9. Have fallbacks
10. Consider parallelization

**When Claude generates code:**
- Claude MUST follow all 10 rules
- Claude MUST include checklist verification
- Claude MUST explain orchestration strategy
- Claude MUST show dependency diagram

**Result:** Production-ready, debuggable, reliable code every time.

---

**Related Skills:**
- `ai-assisted-development/` - AI agent orchestration patterns
- `api-error-handling/` - API-specific error handling
- `feature-planning/` - Implementation planning with orchestration
- `prompting-patterns-reference.md` - Better AI instructions

**Last Updated:** 2026-02-07
**Line Count:** ~476 lines (compliant)
