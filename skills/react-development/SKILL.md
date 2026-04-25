---
name: react-development
description: 'Comprehensive React patterns and best practices: functional components,
  all hooks (useState, useEffect, useCallback, useMemo, useRef, useContext, useReducer),
  custom hooks, state management (local/Context/external), performance optimisation...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# react-development
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Comprehensive React patterns and best practices: functional components, all hooks (useState, useEffect, useCallback, useMemo, useRef, useContext, useReducer), custom hooks, state management (local/Context/external), performance optimisation...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `react-development` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Component test plan | Markdown doc covering hook, context, and rendering tests | `docs/web/react-component-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Production-grade React patterns drawn from Mastering React (Horton & Vice), Pro React (Antonio), and modern React 18/19 best practices.

## Quick Reference

| Topic | Reference |
|---|---|
| All hooks with examples | `references/hooks.md` |
| Custom hooks library | `references/custom-hooks.md` |
| State management patterns | `references/state-management.md` |
| Performance optimisation | `references/performance.md` |
| TypeScript + React | `references/typescript.md` |
| TS + React production gotchas (Fullstack React with TS) | `references/react-typescript-gotchas.md` |
| Testing (RTL) | `references/testing.md` |
| Forms and validation | `references/forms.md` |
| React 18/19 features | `references/react-18-19.md` |

---

## 1. Component Architecture

### Functional Components — Canonical Form

```jsx
function UserCard({ name, email, onSelect }) {
  return (
    <div className="user-card" onClick={() => onSelect(email)}>
      <h3>{name}</h3>
      <p>{email}</p>
    </div>
  );
}
```

Always use function declarations for named components. Arrow functions for callbacks only.

### Composition — Parent Owns State

Build from small autonomous pieces. Parent owns state; children receive props and call
callback props to signal events upward (unidirectional data flow).

```jsx
function KanbanBoard() {
  const [cards, setCards] = useState([]);

  const addCard  = (card) => setCards(prev => [...prev, card]);
  const updateCard = (id, data) =>
    setCards(prev => prev.map(c => c.id === id ? { ...c, ...data } : c));

  return (
    <div className="board">
      {cards.map(card => (
        <KanbanCard key={card.id} card={card} onUpdate={(d) => updateCard(card.id, d)} />
      ))}
      <AddCardForm onAdd={addCard} />
    </div>
  );
}
```

### props.children and Slot Pattern

```jsx
function Card({ title, children, footer }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="card__body">{children}</div>
      {footer && <div className="card__footer">{footer}</div>}
    </div>
  );
}
// <Card title="Summary" footer={<button>Save</button>}><p>Content</p></Card>
```

### Container / Presentational Split

```jsx
// Presentational — pure UI, all data via props
function TaskList({ tasks, onToggle }) {
  return (
    <ul>
      {tasks.map(t => (
        <li key={t.id} className={t.done ? 'done' : ''} onClick={() => onToggle(t.id)}>
          {t.name}
        </li>
      ))}
    </ul>
  );
}

// Container — fetches data, manages state, delegates rendering
function TaskListContainer() {
  const [tasks, setTasks] = useState([]);
  useEffect(() => { fetchTasks().then(setTasks); }, []);
  const toggle = (id) =>
    setTasks(prev => prev.map(t => t.id === id ? { ...t, done: !t.done } : t));
  return <TaskList tasks={tasks} onToggle={toggle} />;
}
```

---

## Additional Guidance

Extended guidance for `react-development` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Core Hooks — Quick Reference`
- `3. Custom Hooks`
- `4. State Management`
- `5. Performance Optimisation`
- `6. Forms`
- `7. Error Boundaries`
- `8. React 18 / 19 Concurrent Features`
- `9. Testing`
- `10. Anti-Patterns Checklist`
- `11. Architecture Checklist`