# Canvas vs Chat — Decision Matrix

Two output paradigms. Pick deliberately; do not mix.

---

## Decision Matrix

| Question | Chat | Canvas |
|---|---|---|
| Is the output shareable? | No | Yes |
| Does the user want to return to it? | No | Yes |
| Is version history needed? | No | Yes |
| Does it live in a transcript? | Yes | No |
| Is it under ~200 words? | Usually | Occasionally |
| Is it a document, image, plan, or code? | No | Yes |
| Is it a quick Q&A? | Yes | No |

**Rule:** move to canvas the moment the output becomes shareable or returnable. A 3-page policy draft in chat is friction; the same draft in canvas is a deliverable.

---

## Chat Paradigm

**Use for:**

- Quick Q&A.
- Conversational iteration.
- Short outputs (a paragraph, a bullet list, a snippet).

**Prescriptions:**

- Linear transcript, oldest to newest.
- Streaming tokens with a blinking cursor.
- Recent history visible (scroll to load older).
- Messages are first-class; artifacts are not.
- Copy/save per message is fine; version history is overkill.

---

## Canvas Paradigm

**Use for:**

- Documents (policy drafts, reports, memos).
- Plans (project plans, OKRs, roadmaps).
- Images (illustrations, layouts).
- Code (multi-file projects, single files over ~50 lines).

**Prescriptions:**

- Editable workspace alongside (or instead of) chat.
- Version history with named versions.
- Undo / redo at the editor level.
- Diff between versions.
- Shareable link with access control.

**Claude Artifacts pattern:** every regeneration is a versioned sibling. Users switch between versions via a dropdown or side panel. Deleting a version is explicit.

**Runway pattern (generative media):** node-based iteration graph. Each generation is a node; users branch, combine, and select. Supports non-linear exploration.

---

## Versioning

- Auto-version on regenerate, on "Elaborate", on knob change, on inline refinement.
- Manual version on user save with optional label.
- Diff view: side-by-side or inline; both modes available.
- Restore a version: creates a new version at the head, does not rewrite history.

---

## Collaboration Primitives (Canvas Only)

- **Shareable link** with role (viewer, commenter, editor).
- **Snapshot** — a frozen, read-only version for sending to stakeholders.
- **Fork** — user takes a copy into their own workspace.
- **Comments** tied to a selection range, like Google Docs.
- **Presence indicators** when multiple users are on the canvas.

Chat does not need these primitives. Trying to add them to chat produces Slack — a different product.

---

## Anti-Patterns

- **Chat used for durable artifacts.** Users scroll forever to find yesterday's draft.
- **Canvas used for ephemeral Q&A.** Every "what's the weather" becomes a saved document.
- **Canvas with no version history.** Every regeneration is destructive.
- **Chat with full edit history per message.** Over-engineered; users expect chat to be linear.
