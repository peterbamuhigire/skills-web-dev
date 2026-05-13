# Agentic Patterns — Expanded Reference

The five agentic patterns, with concrete UI snippets and screen treatments. Based on Macfadyen, *Designing AI Interfaces* (O'Reilly, 2025).

---

## 1. Reflection

The agent reviews its own output and corrects before returning.

**High-stakes domains (finance, medical, legal) — make reflection visible:**

```
Step 3 of 5: Drafting response
  [OK] Drafted initial answer
  [REVIEW] Reviewing for factual errors...
  [FIXED] Corrected currency reference (USD -> UGX)
  [OK] Ready
```

**Low-stakes domains — reflection runs silently.** Showing "reviewing my own work" for a casual chat reply adds friction without trust value.

**UI placement:** inline within the Tier 2 progress panel. Never as a blocking modal.

---

## 2. Tool Use

The agent calls external tools (search, code execution, API). The UI must show:

- Which tool was called.
- What parameters were passed (redact secrets).
- What returned (summary + expandable raw).

**Snippet:**

```
[Tool] web_search
  Query: "Uganda DPPA 2019 breach notification timeline"
  Returned: 4 results - [expand]
  Selected: ugandalegal.gov (accessed 2026-04-25 14:02)
```

Pair with the tiered permission framework. Read-only tools (search, fetch, grep) auto-execute; moderate and destructive tools prompt.

---

## 3. Planning

The agent decomposes a goal into subtasks before executing any of them.

**Plan-preview component (required for any task with 3+ steps or any side-effect):**

```
Proposed plan:
  1. Read current invoice template
  2. Identify fields that need VAT breakdown
  3. Draft modified template
  4. Save as new version (does not overwrite)
  5. Show diff for review

[Edit plan]  [Run plan]  [Cancel]
```

**Branch points:** conditional plans must expose the decision.

```
  3. Draft modified template
  4. IF tenant has VAT enabled: add VAT line
     ELSE: add note "VAT not applicable"
  5. Save as new version
```

**Plan editing:** users can delete steps, reorder, or add constraints before running. After run, the plan is read-only.

---

## 4. Multi-agent

Two or more agents collaborate. Every output must be attributed.

**Attribution format:**

```
[Analyst Agent] Extracted 3 risk factors from the Q3 report.
[Writer Agent]  Drafted executive summary based on Analyst's factors.
[Reviewer]      Flagged 1 inconsistency: summary mentions 4 factors,
                analyst identified 3. Resolve before sending.
```

**Conflict surfacing:** when agents disagree, do not auto-resolve silently. Show the conflict as a user decision point with both positions visible.

---

## 5. ReAct (Reason-Act-Observe loop)

The agent iterates: reason about what to do, act, observe the result, reason again.

**Iteration counter is mandatory.** Without it, a loop looks like a hang.

```
Attempt 1: Searched for "company X quarterly report"
           -> 0 relevant results
Attempt 2: Searched for "company X Q3 2025 10-Q"
           -> Found 2 candidates, both paywalled
Attempt 3: Trying alternative: SEC EDGAR direct
           -> Retrieved 10-Q filing (success)
```

**Escalation path:** after N attempts (typically 3), hand off to the user. "I tried 3 approaches and couldn't access the data. Here's what I tried. Can you paste the document, or should I try something else?"

Never loop silently past the escalation threshold.
