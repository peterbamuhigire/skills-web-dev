---
name: ai-ux-patterns
description: UX design patterns for AI-powered features — loading states, streaming
  display, confidence indicators, progressive disclosure, error recovery, human-in-the-loop
  controls, usage/budget display, and feedback collection. Invoke during UI design
  for...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI UX Patterns

<!-- dual-compat-start -->
## Use When

- UX design patterns for AI-powered features — loading states, streaming display, confidence indicators, progressive disclosure, error recovery, human-in-the-loop controls, usage/budget display, and feedback collection. Invoke during UI design for...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-ux-patterns` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Purpose

AI features fail the user more often than traditional software. They are slow, sometimes wrong, and opaque. These patterns manage user expectations, build trust, and reduce frustration — without making the AI feel like a gimmick.

**Core principle:** AI should feel like a capable colleague, not a magic button.

---

## Pattern 1: Progressive Reveal Loading

AI responses take 2–8 seconds. Never show a blank screen.

```
Immediate (0ms):   Show skeleton placeholder with "Analysing your data..."
Early (500ms):     Animate a progress indicator specific to the task
Mid (2s):          If streaming: show first tokens as they arrive
Complete:          Replace skeleton with result; fade in smoothly
```

**Android (Jetpack Compose):**
```kotlin
when (uiState) {
    is AIState.Idle    -> AIPromptButton(onClick = { vm.generate() })
    is AIState.Loading -> AISkeletonCard(label = "Analysing sales data...")
    is AIState.Streaming -> AIStreamingText(text = uiState.partial)
    is AIState.Success -> AIResultCard(result = uiState.result, onFeedback = vm::submitFeedback)
    is AIState.Error   -> AIErrorCard(message = uiState.message, onRetry = vm::retry)
    is AIState.Gated   -> AIUpgradePrompt(tier = uiState.requiredTier)
}
```

**Web (PHP/Blade + Alpine.js):**
```html
<div x-data="aiFeature()" x-init="init()">
    <template x-if="state === 'idle'">
        <button @click="generate()" class="btn-ai">Generate Summary</button>
    </template>
    <template x-if="state === 'loading'">
        <div class="ai-skeleton animate-pulse">Analysing your data...</div>
    </template>
    <template x-if="state === 'done'">
        <div class="ai-result" x-text="result"></div>
    </template>
    <template x-if="state === 'gated'">
        <div class="ai-upgrade-banner">Upgrade to AI Growth to use this feature.</div>
    </template>
</div>
```

---

## Pattern 2: Streaming Text Display

Stream responses token-by-token for chat and long-form output. Eliminates the "waiting for a response" problem.

**Rules:**
- Stream whenever output > 100 tokens.
- Show a blinking cursor at the end of partial text.
- Allow the user to stop streaming mid-response.
- Do not let the user submit again while streaming.
- Scroll to follow the latest token automatically.

**Key UX detail:** Label the result clearly as AI-generated. Use a subtle AI badge (✦ or a model icon), never pretend the output is from a human.

---

## Pattern 3: Confidence Indicator

Show confidence level when the AI makes a prediction or recommendation.

```
┌─────────────────────────────────────────┐
│ ✦ AI Risk Assessment                    │
│ Student: Aisha Nakato                   │
│                                         │
│ Risk Level:  ████████░░  HIGH           │
│ Confidence:  ███████░░░  Medium         │
│                                         │
│ Reason: Attendance below 60% in last    │
│ 4 weeks; 3 missed assignments.          │
│                                         │
│ [Review] [Dismiss] [Send Alert]         │
└─────────────────────────────────────────┘
```

**Confidence levels:**
- **High** — show action buttons prominently.
- **Medium** — show action buttons, add "Please verify before acting."
- **Low** — do not show action buttons. Show "Insufficient data — manual review recommended."

Do not display raw probability scores to end users. Map to High / Medium / Low.

---

## Pattern 4: Human-in-the-Loop Controls

Match control level to action severity.

| Action | Control Pattern |
|--------|----------------|
| View summary / report | Auto-display. No confirmation needed. |
| Accept recommendation | "Accept" / "Dismiss" buttons. One click. |
| Send alert to user | Confirmation dialog: "Send risk alert to Aisha's guardian?" |
| Approve/reject financial action | Full review screen + typed confirmation ("Type CONFIRM to approve") |
| Irreversible action | Disabled by AI — human must initiate separately. |

**Anti-pattern:** Never let AI take any action that cannot be undone without a confirmation step.

---

## Pattern 5: AI Error Recovery

Design error states that feel helpful, not broken.

| Error | User-Facing Message | Action |
|-------|--------------------|----|
| Timeout | "Analysis is taking longer than expected." | Auto-retry once; then show retry button |
| Invalid output | "We couldn't generate a result this time." | Retry button + "Report issue" link |
| Budget exceeded | "Your AI usage limit for this month has been reached. Contact your administrator to increase your limit." | Link to admin panel |
| Module not active | "This feature requires the AI add-on. Contact your system administrator." | No upgrade link (admin decides) |
| API provider down | "AI analysis is temporarily unavailable. Your request has been queued." | Show queue confirmation |

**Rules:**
- Never expose technical errors (HTTP codes, stack traces) to end users.
- Never say "AI error" — say "analysis unavailable."
- Always provide a next step (retry / contact admin / queue).

---

## Pattern 6: AI Budget / Usage Display

Tenants that pay for AI want visibility into what they are spending.

### User-Level Display (compact, in-app)

```
✦ AI Usage this month
████████░░  82% of your allocation used
[18% remaining — resets in 11 days]
```

Show this in user settings or profile. Not on every screen.

### Admin-Level Dashboard (tenant admin)

Columns:
- User name / email
- Total AI calls this month
- Input tokens used
- Output tokens used
- Estimated cost (UGX)
- Top feature used

Show a tenant-level totals row. Include a trend chart (this month vs last month).

### Super-Admin Dashboard (your SaaS ops)

Columns:
- Tenant name
- AI tier (Starter / Growth / Enterprise)
- Budget (UGX)
- Tokens used this month
- Raw cost (USD)
- Revenue (UGX)
- Margin (%)

Alert row: tenants at > 80% budget consumption.

---

## Pattern 7: Feedback Collection

AI improves with feedback. Collect it unobtrusively.

```
┌─────────────────────────────────────────┐
│ ✦ AI Sales Summary — Today             │
│ Total sales UGX 2,450,000. Top item:   │
│ Maize flour (340 units). 3 stockouts   │
│ flagged for reorder.                    │
│                                         │
│ Was this useful?  👍  👎               │
└─────────────────────────────────────────┘
```

- Collect thumbs up / down per response. No form required.
- For 👎: optionally show "What was wrong?" (one-tap options: "Inaccurate / Irrelevant / Too long / Other").
- Log feedback to `ai_feedback_log(response_id, user_id, rating, reason, created_at)`.
- Review 👎 responses weekly to improve prompts.

---

## Pattern 8: AI Feature Discoverability

AI features are invisible until users know they exist.

- Use a consistent **✦ AI** badge or icon on every AI-powered element.
- On first activation, show a 3-step onboarding card: "What this does / How it works / What it costs."
- Show AI features in a dedicated "AI Insights" section in the nav, not buried in menus.
- For admin: show a setup checklist when AI module is first activated.

---

## AI UX Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Blank white screen while AI loads | User thinks app crashed | Show skeleton + loading message immediately |
| Raw JSON shown to user | Confusing; breaks trust | Always transform output before display |
| "AI says to do X" with no explanation | No trust basis | Always show reason + data points used |
| One-click irreversible AI actions | Catastrophic if wrong | Add confirmation gate |
| AI badge on non-AI features | Misleading | Only badge genuine AI-generated content |
| Hiding AI errors silently | User doesn't know result is missing | Always show a graceful error state |
| Prompt text visible to users | Confusing | Keep prompts server-side only |

---

**See also:**
- `ai-feature-spec` — Output schema that drives these UX states
- `ai-architecture-patterns` — Gate state that triggers upgrade prompt
- `ai-metering-billing` — Data behind the usage dashboard
- `ux-for-ai` — Deeper AI trust and transparency principles
- `ai-slop-prevention` — Avoiding low-quality AI output in UI
