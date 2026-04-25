# Three Channels of Intent and AI Feature Discovery

Source: Macfadyen, *Designing AI Interfaces* (O'Reilly, 2025), Chapters 2 and 3.

## Three Channels of Intent

Every AI interaction carries intent through three simultaneous channels. Each can succeed or fail independently; the best AI UIs use all three.

| Channel | What it is | Example | Design prescription |
|---|---|---|---|
| Implicit context | What the system knows about the user's situation without asking | Selected text, open document, current URL, device, locale, time of day | Make implicit context **visible** to the user. Show a context chip: "Editing: selected text", "Reading: contract.pdf", "Location: Kampala". Users must be able to confirm or correct what the system has assumed. |
| Explicit prompting | What the user types or speaks | Typed request, voice command, pasted content | Provide a free-text field but **do not rely on it alone**. Users often do not know what to type. Pair with starter prompts and direct manipulation. |
| Direct manipulation | UI controls the user operates directly | Tone slider, length selector, format buttons, selection rectangles | Expose the most common parameters as controls. QuillBot's Fluency/Formal sliders outperform a "make it more formal" text prompt for the same task. |

### Hybrid over conversational-only

The Lehmann/Buschek study cited in the book found users produced better output and reported higher satisfaction when given a toolbar + free-text field compared with a chat-only interface for the same task. The toolbar discharges the common 80% of intents in one click; the free-text handles the long tail. A pure chat UI forces every intent through one channel.

Rule: for any AI feature where the common operations are known, build the hybrid. Reserve chat-only for exploratory or unbounded tasks.

## Feature Discovery 2×2

Most AI features fail because users never discover them. Map every AI feature on two axes before designing the entry point.

|  | Low user intent | High user intent |
|---|---|---|
| **Low system initiative** | *Organic discovery.* Rely on social proof, onboarding tours, empty-state hints. Do not interrupt. | *Frictionless activation.* User is looking for the feature; surface it one click away. Command palette, prominent button, keyboard shortcut. |
| **High system initiative** | *Strong context cues + exit paths.* System suggests because it notices a signal (anomaly, pattern). Always provide an unambiguous "Not now / Never" option. | *Accelerate.* User wants it and system knows they want it. Auto-run with a prominent "Undo" and a summary of what just happened. |

### Four discovery pattern families

1. **Input-based** — command triggers (`/`, `@`), gestures (swipe, long-press), empty-state prompts ("Start with an idea"). Use when the user knows roughly what they want.
2. **Context-aware** — surfaces the feature based on current content, behaviour, or location. "You are editing a contract — enable Clause Review?" Use when user intent is inferable.
3. **Ambient / proactive** — the system initiates without being asked, driven by anomaly detection or predictive signals. Use sparingly; always allow dismissal.
4. **Progressive** — feature graduation and contextual tutorials. Early sessions hide advanced AI; later sessions unlock it based on usage signals. Use to avoid overwhelming new users while still reaching power-user features.

## Starter prompts are product positioning

Generic starter prompts ("Write a poem about autumn") are a sign the team did not think about the product. Good starter prompts:

- Reflect the product's specific integrations and tone
- Are context-aware (Monday vs Friday; document type currently open; user plan tier)
- Change monthly; they are content, not fixture

A SaaS CRM's starter should be "Draft a follow-up to my three oldest open deals" — not "Write a professional email."

## CARE framework as UI scaffold

The NN/g CARE framework (Context, Action, Results, Examples) can be built as a structured input form rather than a free-text prompt:

- Context field: "What's the situation?" (pre-filled from implicit context where possible)
- Action field: verb-driven selector ("Summarise", "Draft", "Translate")
- Results knobs: length, audience, format, tone — as direct-manipulation controls
- Examples: file upload or paste area for "like this"

The form-based CARE composer produces better outputs than the same prompt typed free-text, because it forces the user to fill all four slots and prevents under-specified requests.

## Anti-patterns

- Sole reliance on a free-text prompt box for a feature with known common operations
- Hidden implicit context — user cannot see or correct what the system assumed
- Proactive suggestions with no dismissal or "never again" option
- Generic starter prompts that could appear in any product
- Separate "AI" tab the user must navigate to (deprives the feature of context-aware discovery)

## See also

- `skills/ai-ux-patterns/SKILL.md` — core AI UI patterns.
- `skills/ai-output-design/SKILL.md` — the receiving end: designing the AI output surface.
- `skills/ai-agentic-ui/SKILL.md` — when the AI feature becomes agentic.
