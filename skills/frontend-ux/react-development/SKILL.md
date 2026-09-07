---
name: react-development
description: Use when implementing or reviewing React components, hooks, state ownership, forms, rendering performance, error boundaries, or component tests. Use nextjs-app-router for Next.js server boundaries and ux-content-strategy for product content systems.
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

## Decision rules

| Condition | Choice | Failure avoided |
|---|---|---|
| State is used by one component | Keep it local | Premature global state |
| State is shared by a tight subtree | Lift it or use focused context | Global-store coupling |
| Value is derived from props or state | Compute during render | Synchronisation effects |

## Anti-Patterns

- Mirroring derived values in state. Fix: compute them during render.
- Using an effect for user-triggered logic. Fix: use the event handler.
- Mutating state arrays or objects. Fix: create a new value through the setter.
- Keying changing lists by array index. Fix: use a stable domain identifier.
- Adding context for state used by one component. Fix: keep ownership local.

## Capability contract

Read and search the component tree and tests first. Edit only when authorised; execute type-checks, component tests, accessibility checks, and the production build when available.

## Degraded mode

If the repository or test runner is unavailable, return a component-level plan and mark rendering, accessibility, and regression behaviour as unverified.
## Inputs
| Artefact | Required? | Purpose |
|---|---|---|
| Component behaviour, state/data boundaries, accessibility, and project conventions | yes | Shape React implementation |
## Outputs
- Produce React code or findings with state coverage, accessibility, tests, and performance evidence.
