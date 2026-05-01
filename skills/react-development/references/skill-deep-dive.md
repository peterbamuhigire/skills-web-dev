# react-development Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

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
