---
name: ux-for-ai
description: "Use when designing or reviewing AI-powered features (chatbots, copilots, search, recommendations, generative outputs) to ensure they feel premium, trustworthy, and world-class. Applies the RETCH trust framework, progressive disclosure for AI capabilities, human oversight requirements, and graceful error degradation patterns. Based on Nudelman (2024)."
user-invocable: true
triggers:
  - design AI feature
  - AI UX review
  - chatbot UX
  - copilot design
  - AI trust patterns
  - AI onboarding
  - review AI interface
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# UX for AI — Design Framework

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building any AI-powered feature, chatbot, copilot, or AI search interface
- Designing AI recommendations, anomaly detection, or generative output surfaces
- Reviewing existing AI features for trust, transparency, and premium feel
- Onboarding users to AI capabilities without overwhelming them
- Avoiding the "AI slop" feeling in AI-assisted products

## Do Not Use When

- The feature has no AI component — use general UX skills instead
- Building backend AI infrastructure with no user-facing surface
- The task is purely about ML model accuracy or training, not user experience

## Required Inputs

- The AI feature type (chatbot, copilot, search, recommendations, generative)
- Target user context (domain expertise level, risk tolerance, task complexity)
- Whether this is new feature design or an audit of existing AI UX

## Workflow

1. Read this `SKILL.md` for core principles and patterns
2. Identify which RETCH principles (Restate, Calibrate, Explain, Transparent, Human oversight) apply
3. Apply the relevant design patterns from sections 2-7 below
4. Validate against the anti-patterns checklist in section 8
5. Produce the deliverable with explicit assumptions about AI accuracy and failure modes

## Quality Standards

- Every AI interaction must leave the user holding something useful ("never leave empty-handed")
- All AI error-recovery procedures must be visible on screen, not hidden in documentation
- Manual fallback paths must exist for every AI-assisted workflow
- Confidence levels must be communicated when AI output accuracy varies

## Anti-Patterns

- Replacing an expert directly — AI should assist and augment, never compete
- Chat-only information architecture — chat is a command line, not a complete product
- Copying ChatGPT patterns blindly — invent patterns suited to your specific use case
- Optimising on accuracy metrics alone — real-world ROI is the metric that matters
- Large overlay copilot panels that obscure parent content — use side panels instead

## Outputs

- AI surface design specification with trust/transparency patterns applied
- Error state and graceful degradation design for AI failure modes
- Human oversight control placement (start, stop, pause, approve)

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | AI surface design review | Markdown doc covering trustworthiness, error tolerance, and refusal-state handling for AI-powered features | `docs/ai/ux-design-review.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Based on Nudelman (2024) *UX for AI: A Framework for Product Design.*

## When to Use

Load this skill when:
- Building any AI-powered feature, chatbot, or copilot
- Designing AI search, recommendations, anomaly detection, or generative outputs
- Reviewing AI features for trust, transparency, and premium feel
- Avoiding the "AI slop" feeling in AI-assisted products

---

## 1. Core Principles (RETCH)

Five non-negotiable principles for trustworthy AI UX:

**Restate** — Before acting, the AI must echo back what it understood. "Showing results for: [interpreted query]." This closes the gap between what the user meant and what AI understood without requiring re-entry.

**Calibrate** — AI must know what it doesn't know. Communicate confidence levels. When confidence is low, fall back to deterministic baselines or say "I don't know." An AI that cannot self-assess accuracy is a liability.

**Explain** — Show the "why" behind AI decisions. Citations, recommended reasons, translated queries. "Recommended because you viewed X." Users who understand AI reasoning trust it more and use it better.

**Transparent** — State what data the AI uses and whether conversations are stored. Don't bury privacy stance in documentation — state it directly in the AI interface.

**Human oversight** — Never remove manual override controls. Always provide stop, pause, and override buttons for any AI action. The Boeing 737 Max crash (346 deaths) is the foundational case study for what happens when AI silently overrides humans with no visible intervention path.

---

## 2. Mental Models Users Hold About AI

**Users want outcomes, not AI.** The mechanism is irrelevant. If a simpler deterministic solution delivers the outcome, use it. Never force AI into a product just because it is technically possible.

**Algorithm aversion is real and manageable.** Users tolerate bad AI output less than equivalent bad human output. However, aversion decreases when users can slightly modify the AI output, or when the system demonstrates it is improving over time.

**AI must not claim to replace experts.** Positioning AI as a direct replacement for an established expert (farmer, doctor, analyst) provokes distrust and resistance. AI should *assist* and *augment* the expert — never compete with their core skill.

**Users expect contextual intelligence.** Modern AI should infer context from calendar data, location, time of day, and prior conversation — without making users re-specify what they clearly mean.

**Deskilling warning.** Over-reliance on AI erodes the user's own capability. Design for augmentation, not replacement, especially in high-stakes domains (medicine, security, finance).

---

## 3. Making AI Feel Premium (Not Sloppy)

**Domain-specific training is the single biggest differentiator.** Generic ChatGPT answers feel wrong for your product. Fine-tune on your specific dataset or use RAG (retrieval-augmented generation). An AI that gives domain-accurate answers feels intelligent; one that gives generic LLM responses feels broken.

**Stateful AI feels intelligent; stateless AI feels dumb.** Allow users to resume investigations, maintain context across sessions, and build on prior interactions. Statelessness makes AI feel disconnected and forgetful.

**Size the copilot to match task importance:**
- Side panel → page-level, context-aware tasks (preferred)
- Large overlay → generally avoid; obscures parent page
- Full-page dedicated experience → deep, analytical, complex tasks

**Context-aware initial suggestions feel like mind-reading.** Surface the right suggestions before the user types anything — based on time of day, data type, prior sessions, and usage patterns. Generic "What can I help you with?" prompts feel cheap.

**Use Promptbooks to reduce prompt engineering burden.** Users should never need to write complex prompts. Provide pre-built recipes for common workflows. Curated, plain-language queries that interact with domain data in predictable ways is the target.

**Give AI a deliberate personality.** Define the persona explicitly (supportive health coach, expert security analyst, etc.). Avoid pedantic or preachy tone. Generic LLM personality is a missed differentiator.

**Test with real AI output, not mocked text.** Products that demo well on polished placeholder copy but fail with actual AI responses are caught in research, not production. Use Python notebooks + paper prototype ("Wizard of Oz") for honest testing.

---

## 4. Error States & Graceful Degradation

**The core product must be resilient to bad AI output.** AI autocomplete and pre-fill should save time when correct but must never block the user when wrong. Always preserve the manual fallback path.

**Wrap all AI output in business logic guardrails.** Never pass raw model output directly to users or downstream systems. Hard-code limits (max bid, medication dose, allowed actions) regardless of what the AI recommends.

**The Value Matrix principle.** False positive vs false negative costs are not equal. Calculate the real cost of each error type before choosing how to handle AI failures. Optimise for real-world ROI, not data science accuracy metrics. A "Balanced AI" regularly outperforms a "Accurate (Conservative) AI" in real-world ROI.

**Progressive accuracy improvement is critical for retention.** Users will abandon an AI product within 3–5 interactions if accuracy does not visibly improve with use. Design AI systems to learn from user corrections.

**Guardrails layer required for all LLM outputs.** Define explicitly what the AI will and will not output. Code explicit failure responses for denied or malformed requests. Guardrails must be designed, not improvised.

---

## 5. Onboarding AI Features

**"Set it and forget it" for low-stakes AI.** Activate with zero setup when the downside is minimal and immediate value is clear. Zoom AI Companion activating automatically on meeting start is the benchmark.

**Lead with immediate, tangible value.** The benefit must be clear in the first interaction. Users should not need to invest effort to see value.

**Promptbooks and initial suggestions cure cold-start anxiety.** An empty prompt box paralyses users. Offer context-aware suggestions based on data type, time of day, and prior sessions.

**Validate the use case with storyboards first.** A use case that sounds reasonable as text often falls apart when storyboarded step-by-step. The conclusion panel of the storyboard must follow naturally from the rest. If it doesn't, the use case is wrong.

**Train on 2,000+ domain-specific examples before launch.** An untrained LLM answering domain-specific queries feels broken. Users who encounter generic responses in their first interaction rarely return.

---

## 6. Progressive Disclosure for AI Capabilities

**Start with the "one thing."** Every AI feature needs a single, clear primary job. What is the one thing users should always be able to do with this AI? Everything else is secondary.

**Reveal AI capabilities through contextual next steps, not documentation.** After each AI interaction, surface the 2–3 most valuable next questions the user is likely to have. This teaches users what the AI can do — inside their actual workflow.

**Use Mad Lib fill-in-the-blank for complex AI configuration.** Write the configuration as a complete English sentence with embedded drop-downs: "Trigger a [Critical] alert whenever the value exceeds [90%] for [1 minute]" is far more comprehensible than a table of parameters.

**Information architecture still matters in AI-first apps.** Chat alone is not a complete interface. Users need predetermined starting points, context-aware alerts, and structured navigation. A blank chat box communicates nothing about what the product does.

---

## 7. Human-AI Collaboration Patterns

**In agentic AI, the human's job is to accept or reject evidence, not direct every step.** Design accept/reject flows for observations and hypotheses. The human is a reviewer and quality gate, not a director.

**Agentic AI requires start, stop, pause, and approval controls.** Agents are asynchronous and semi-autonomous. Without stop and pause controls, agents create runaway costs ("Sorcerer's Apprentice" problem). Approval gates for expensive or irreversible actions are mandatory.

**Agents require RBAC, data isolation, and versioning.** Treat AI agents like employees — with access controls, data isolation, and version management. This governance UI is a new and urgent design challenge.

**Augmented intelligence, not replacement.** Machines handle pattern recognition, data processing, and hypothesis generation. Humans handle empathy, ethics, judgment, and creative synthesis.

---

## 8. Anti-Patterns

1. **Replacing an expert directly** — Always fails. AI should assist, not compete.
2. **Optimising on accuracy metrics alone** — Real-world ROI is the only metric that matters.
3. **Large overlay copilot panels** — Obscure parent content, force repeated open/close cycles. Use side panels instead.
4. **Chat-only information architecture** — Chat is a command line, not a complete product.
5. **Copying ChatGPT patterns blindly** — Invent patterns suited to your specific use case.
6. **Using synthetic users for AI research** — AI research hallucinations miss contextual nuance. Real user research is non-optional.
7. **Assuming AI will behave correctly without UX oversight** — The primary cause of automation-related disasters. Always design for failure.
8. **Fully automated report generation without human selection** — For legally important documents, require humans to pin relevant data before AI writes the report.

---

## 9. Key Mantras

1. **"AI is too important to be left to data scientists."** UX must be present from use case discovery through ethics review.
2. **"Never let the user leave empty-handed."** Every AI interaction must end with the user holding something useful.
3. **"Accuracy optimised alone almost always underperforms AI that considers real-world costs."**
4. **"If you cannot tell a compelling story, you don't have a chance."** Storyboard every AI use case before building.
5. **"Now is not the time to copy — it is the time to invent."** Find what is unique about your use case.
6. **"Recognition over recall."** Even Boeing 737 Max pilots died partly because they had to remember a checklist under extreme stress. All AI error-recovery procedures must be on screen.
7. **"The best AI is augmented intelligence."** Let machines handle what machines do best. Let humans handle the rest.

---

## Sources

- Nudelman, G. (2024). *UX for AI: A Framework for Product Design.* Wiley.