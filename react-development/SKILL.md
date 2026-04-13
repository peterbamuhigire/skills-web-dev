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

## 2. Core Hooks — Quick Reference

Full examples with all edge cases in `references/hooks.md`.

### useState

```jsx
const [count, setCount] = useState(0);
const [form, setForm] = useState({ name: '', email: '' });

// Functional update — safe in async contexts
setCount(prev => prev + 1);

// Update nested field without mutation
setForm(prev => ({ ...prev, name: 'Alice' }));

// Lazy initialiser for expensive initial state
const [data, setData] = useState(() => JSON.parse(localStorage.getItem('data') ?? '[]'));
```

### useEffect

```jsx
useEffect(() => {
  let cancelled = false;
  async function load() {
    const data = await fetchUser(userId);
    if (!cancelled) setUser(data);
  }
  load();
  return () => { cancelled = true; };   // always clean up async effects
}, [userId]);
```

Rules: declare all deps. Empty `[]` = mount only. Return cleanup always for subscriptions.

### useCallback and useMemo

```jsx
// Stable function reference — prevents child re-renders when using React.memo
const onDelete = useCallback((id) => {
  setItems(prev => prev.filter(item => item.id !== id));
}, []);

// Expensive computation — only recompute when deps change
const filtered = useMemo(
  () => items.filter(i => i.status === filter).sort(...),
  [items, filter]
);
```

### useRef

```jsx
// DOM access
const inputRef = useRef(null);
useEffect(() => { inputRef.current?.focus(); }, []);
return <input ref={inputRef} />;

// Mutable value that does NOT trigger re-render
const timerRef = useRef(null);
timerRef.current = setInterval(tick, 1000);
```

### useContext

```jsx
const ThemeContext = createContext('light');
const theme = useContext(ThemeContext);   // consume from anywhere in subtree
```

### useReducer

```jsx
function reducer(state, action) {
  switch (action.type) {
    case 'INCREMENT': return { ...state, count: state.count + 1 };
    case 'FETCH_SUCCESS': return { ...state, status: 'success', data: action.payload };
    default: throw new Error(`Unknown: ${action.type}`);
  }
}
const [state, dispatch] = useReducer(reducer, { count: 0, status: 'idle' });
dispatch({ type: 'INCREMENT' });
```

Use `useReducer` when state has multiple sub-values or transitions are complex.

---

## 3. Custom Hooks

```jsx
// Data fetching
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(url)
      .then(r => r.json())
      .then(d => { if (!cancelled) { setData(d); setLoading(false); } })
      .catch(e => { if (!cancelled) { setError(e); setLoading(false); } });
    return () => { cancelled = true; };
  }, [url]);

  return { data, loading, error };
}

// Form state
function useForm(initialValues) {
  const [values, setValues] = useState(initialValues);
  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  }, []);
  const reset = useCallback(() => setValues(initialValues), [initialValues]);
  return { values, handleChange, reset };
}

// Debounce
function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}
```

See `references/custom-hooks.md` for `useLocalStorage`, `usePrevious`, `useIntersectionObserver`.

---

## 4. State Management

```
Simple UI state (open/closed)      → useState
Form state                         → useState + useForm hook
Shared state: small/medium app     → Context + useReducer
Shared state: large/complex app    → Zustand or Redux Toolkit
Server state (fetch + cache)       → React Query / SWR
```

### Context + useReducer

```jsx
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, { user: null, isAuth: false });
  const login  = useCallback((user) => dispatch({ type: 'LOGIN', payload: user }), []);
  const logout = useCallback(() => dispatch({ type: 'LOGOUT' }), []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
```

### Zustand (Lightweight Alternative)

```jsx
import { create } from 'zustand';

const useCardStore = create((set) => ({
  cards: [],
  addCard: (card) => set(state => ({ cards: [...state.cards, card] })),
  updateCard: (id, data) => set(state => ({
    cards: state.cards.map(c => c.id === id ? { ...c, ...data } : c)
  })),
}));
```

Full Redux Toolkit patterns in `references/state-management.md`.

---

## 5. Performance Optimisation

### React.memo

```jsx
const TaskItem = React.memo(function TaskItem({ task, onToggle }) {
  return <li onClick={() => onToggle(task.id)}>{task.name}</li>;
});
// Pair with useCallback in parent for onToggle reference stability
```

### Code Splitting

```jsx
const Dashboard = React.lazy(() => import('./pages/Dashboard'));

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Suspense>
  );
}
```

### Key Rules

```jsx
// Always use stable IDs — never array index for dynamic/reorderable lists
{cards.map(card => <Card key={card.id} card={card} />)}
```

Virtualisation with `react-window` for 500+ row lists — see `references/performance.md`.

---

## 6. Forms

```jsx
function LoginForm({ onSubmit }) {
  const [values, setValues] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const validate = () => {
    const errs = {};
    if (!values.email.includes('@')) errs.email = 'Invalid email';
    if (values.password.length < 8)  errs.password = 'Min 8 characters';
    return errs;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    onSubmit(values);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="email" value={values.email} onChange={handleChange} />
      {errors.email && <span className="error">{errors.email}</span>}
      <input name="password" type="password" value={values.password} onChange={handleChange} />
      {errors.password && <span className="error">{errors.password}</span>}
      <button type="submit">Log In</button>
    </form>
  );
}
```

---

## 7. Error Boundaries

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) { return { hasError: true }; }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught:', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) return this.props.fallback ?? <div>Something went wrong.</div>;
    return this.props.children;
  }
}
// Wrap lazy routes and data-driven sections
<ErrorBoundary fallback={<ErrorPage />}><Dashboard /></ErrorBoundary>
```

---

## 8. React 18 / 19 Concurrent Features

### useTransition — Non-Urgent Updates

```jsx
const [isPending, startTransition] = useTransition();

const handleSearch = (e) => {
  setQuery(e.target.value);                     // urgent: input updates immediately
  startTransition(() => setResults(filter(e.target.value)));  // deferrable
};
```

### useDeferredValue

```jsx
const deferredInput = useDeferredValue(input);  // lags deliberately
<ExpensiveList filter={deferredInput} />         // renders with old value while typing
```

### Automatic Batching (React 18)

All `setState` calls are batched automatically — inside setTimeout, Promises, native events.
Use `flushSync` only when you need an immediate DOM update.

### useId — Stable Unique IDs (SSR-safe)

```jsx
function FormField({ label }) {
  const id = useId();
  return <><label htmlFor={id}>{label}</label><input id={id} /></>;
}
```

---

## 9. Testing

```jsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Query by role/label — not class names or IDs
test('renders and calls onSelect', async () => {
  const user = userEvent.setup();
  const onSelect = jest.fn();
  render(<UserCard name="Alice" email="a@b.com" onSelect={onSelect} />);
  expect(screen.getByText('Alice')).toBeInTheDocument();
  await user.click(screen.getByText('Alice'));
  expect(onSelect).toHaveBeenCalledWith('a@b.com');
});

// Async with mock fetch
test('renders fetched items', async () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({ json: () => Promise.resolve([{ id: 1, name: 'Task A' }]) })
  );
  render(<TaskListContainer />);
  await waitFor(() => expect(screen.getByText('Task A')).toBeInTheDocument());
});
```

Full testing patterns (custom hooks, forms, context) in `references/testing.md`.

---

## 10. Anti-Patterns Checklist

| Anti-Pattern | Fix |
|---|---|
| Mutate state directly | Spread: `setArr(prev => [...prev, item])` |
| Missing useEffect deps | Declare all; use `react-hooks/exhaustive-deps` ESLint rule |
| Derive state in useEffect | Compute with `useMemo` instead |
| Array index as key | Use stable IDs |
| Calling hooks conditionally | Hooks at top level, unconditional only |
| No useEffect cleanup | Return cleanup function for subscriptions/timers |
| Props drilling 3+ levels | Lift to Context or compose differently |
| Premature memoisation | Profile first, memo after |

---

## 11. Architecture Checklist

```
src/
├── components/   # Reusable UI — no data fetching, pure props
├── pages/        # Route-level — may fetch, composes components
├── hooks/        # Custom hooks — all stateful logic extraction
├── context/      # Context providers (auth, theme, etc.)
├── store/        # Global state (Zustand / Redux)
├── api/          # Fetch/axios wrappers — pure async functions
└── utils/        # Pure utility functions
```

**Non-negotiable rules:**
- One component per file; filename = component name
- ESLint with `eslint-plugin-react-hooks` always enabled
- Strict Mode on in development
- ErrorBoundary at page level minimum
- All lazy routes wrapped in Suspense
- All lists have stable `key`; all images have `alt`
- Optimistic UI: update state immediately, revert on API error — TypeScript: `references/typescript.md` | Routing: `references/state-management.md`
