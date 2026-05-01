# React Hooks — Complete Reference

## useState — All Patterns

```jsx
// Primitive
const [count, setCount] = useState(0);
const [name, setName]   = useState('');
const [open, setOpen]   = useState(false);

// Object state — ALWAYS spread, never mutate
const [user, setUser] = useState({ name: '', email: '', role: 'viewer' });
const updateField = (field, value) => setUser(prev => ({ ...prev, [field]: value }));

// Array state
const [items, setItems] = useState([]);
const addItem    = (item) => setItems(prev => [...prev, item]);
const removeItem = (id)   => setItems(prev => prev.filter(i => i.id !== id));
const updateItem = (id, data) => setItems(prev =>
  prev.map(i => i.id === id ? { ...i, ...data } : i)
);

// Functional update — always use when next state depends on previous
setCount(prev => prev + 1);  // safe in async, batched updates
setItems(prev => [...prev, newItem]);

// Lazy initialiser — runs once, avoids re-parsing on every render
const [prefs, setPrefs] = useState(() => {
  try { return JSON.parse(localStorage.getItem('prefs')) ?? defaultPrefs; }
  catch { return defaultPrefs; }
});
```

## useEffect — Data Fetching, Subscriptions, DOM

```jsx
// Fetch with cleanup (prevents stale state after unmount)
useEffect(() => {
  let cancelled = false;
  async function fetchData() {
    try {
      const res = await fetch(`/api/users/${userId}`);
      const data = await res.json();
      if (!cancelled) setUser(data);
    } catch (err) {
      if (!cancelled) setError(err.message);
    }
  }
  fetchData();
  return () => { cancelled = true; };
}, [userId]);  // re-run when userId changes

// AbortController pattern (preferred for fetch)
useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/data`, { signal: controller.signal })
    .then(r => r.json())
    .then(setData)
    .catch(err => { if (err.name !== 'AbortError') setError(err); });
  return () => controller.abort();
}, []);

// Event listener
useEffect(() => {
  const handler = (e) => {
    if (e.key === 'Escape') onClose();
  };
  document.addEventListener('keydown', handler);
  return () => document.removeEventListener('keydown', handler);
}, [onClose]);

// Subscription pattern
useEffect(() => {
  const subscription = dataStream.subscribe(setData);
  return () => subscription.unsubscribe();
}, [dataStream]);

// Run only once on mount
useEffect(() => {
  initializeApp();
}, []);

// Run on every render (rare — omit dependency array)
useEffect(() => { document.title = `Count: ${count}`; });
```

**Exhaustive deps rule:** Always list every value from component scope used inside effect.
Use `useCallback`/`useMemo` to stabilise function/object deps if needed.

## useCallback — Stable Function References

```jsx
// Basic — stable reference for React.memo children
const handleDelete = useCallback((id) => {
  setItems(prev => prev.filter(item => item.id !== id));
}, []);  // no deps: setItems is always stable from useState

// With dependencies
const fetchWithQuery = useCallback(async () => {
  const data = await fetchUsers({ filter, page });
  setUsers(data);
}, [filter, page]);

// Event handler passed to child with React.memo
const handleChange = useCallback((e) => {
  setValue(e.target.value);
}, []);

// When NOT to use: callbacks used only within the same component
// and not passed to memoised children — adds overhead for no benefit
```

## useMemo — Expensive Computations

```jsx
// Sort + filter — only recompute when source data changes
const processedList = useMemo(() => {
  return items
    .filter(item => item.status === statusFilter)
    .filter(item => item.name.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => {
      if (sortDir === 'asc') return a[sortField] > b[sortField] ? 1 : -1;
      return a[sortField] < b[sortField] ? 1 : -1;
    });
}, [items, statusFilter, searchTerm, sortField, sortDir]);

// Derived stats object
const analytics = useMemo(() => ({
  total:   orders.length,
  revenue: orders.reduce((sum, o) => sum + o.amount, 0),
  avg:     orders.length ? orders.reduce((s, o) => s + o.amount, 0) / orders.length : 0,
  byStatus: orders.reduce((acc, o) => ({
    ...acc, [o.status]: (acc[o.status] || 0) + 1
  }), {}),
}), [orders]);

// Stable object reference for useEffect dependency
const options = useMemo(() => ({ method: 'POST', headers }), [headers]);
```

## useRef

```jsx
// DOM reference — focus, scroll, measure
function AutoFocus() {
  const ref = useRef(null);
  useEffect(() => { ref.current?.focus(); }, []);
  return <input ref={ref} placeholder="Auto-focused" />;
}

// Scroll to element
function ScrollableList({ items, highlightId }) {
  const highlightRef = useRef(null);
  useEffect(() => {
    if (highlightRef.current) {
      highlightRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [highlightId]);
  return (
    <ul>
      {items.map(item => (
        <li key={item.id} ref={item.id === highlightId ? highlightRef : null}>
          {item.name}
        </li>
      ))}
    </ul>
  );
}

// Store interval / timeout without triggering re-render
function Stopwatch() {
  const [elapsed, setElapsed] = useState(0);
  const intervalRef = useRef(null);
  const startRef    = useRef(null);

  const start = () => {
    startRef.current = Date.now() - elapsed;
    intervalRef.current = setInterval(() => {
      setElapsed(Date.now() - startRef.current);
    }, 100);
  };
  const stop = () => clearInterval(intervalRef.current);

  return (
    <div>
      <p>{(elapsed / 1000).toFixed(1)}s</p>
      <button onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
    </div>
  );
}

// Track previous value
function usePrevious(value) {
  const ref = useRef(undefined);
  useEffect(() => { ref.current = value; });
  return ref.current;
}
```

## useContext

```jsx
// Define context + provider
const SettingsContext = createContext(null);

export function SettingsProvider({ children }) {
  const [settings, setSettings] = useLocalStorage('settings', defaultSettings);
  const update = useCallback((key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  }, [setSettings]);

  return (
    <SettingsContext.Provider value={{ settings, update }}>
      {children}
    </SettingsContext.Provider>
  );
}

// Safe consumption hook with error boundary
export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error('useSettings must be used within SettingsProvider');
  return ctx;
}

// Usage
function LanguagePicker() {
  const { settings, update } = useSettings();
  return (
    <select value={settings.language} onChange={e => update('language', e.target.value)}>
      <option value="en">English</option>
      <option value="sw">Swahili</option>
    </select>
  );
}
```

**Performance:** Context re-renders ALL consumers when value changes.
Split contexts by update frequency (e.g. UserContext vs ThemeContext vs SettingsContext).
Memoize provider value: `const value = useMemo(() => ({ user, login, logout }), [user])`.

## useReducer — Complex State

```jsx
// Full example: async operation with loading/error states
const initialState = {
  data: null,
  status: 'idle',   // 'idle' | 'loading' | 'success' | 'error'
  error: null,
};

function dataReducer(state, action) {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, status: 'loading', error: null };
    case 'FETCH_SUCCESS':
      return { ...state, status: 'success', data: action.payload };
    case 'FETCH_ERROR':
      return { ...state, status: 'error', error: action.payload };
    case 'RESET':
      return initialState;
    default:
      throw new Error(`Unhandled action type: ${action.type}`);
  }
}

function DataView({ resourceId }) {
  const [state, dispatch] = useReducer(dataReducer, initialState);

  useEffect(() => {
    dispatch({ type: 'FETCH_START' });
    fetchResource(resourceId)
      .then(data => dispatch({ type: 'FETCH_SUCCESS', payload: data }))
      .catch(err => dispatch({ type: 'FETCH_ERROR', payload: err.message }));
  }, [resourceId]);

  if (state.status === 'loading') return <Spinner />;
  if (state.status === 'error')   return <ErrorMessage msg={state.error} />;
  if (state.status === 'success') return <DataDisplay data={state.data} />;
  return null;
}
```

## useLayoutEffect

Like `useEffect` but fires synchronously after DOM mutations, before paint.
Use for: measuring DOM elements, synchronising scroll positions, animations.

```jsx
useLayoutEffect(() => {
  const { height } = ref.current.getBoundingClientRect();
  setMeasuredHeight(height);
}, []);  // measure after render but before paint
```

## useImperativeHandle + forwardRef

Expose a controlled API from a child component to its parent.

```jsx
const FancyInput = forwardRef(function FancyInput(props, ref) {
  const inputRef = useRef(null);

  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current.focus(),
    clear: () => { inputRef.current.value = ''; },
  }));

  return <input ref={inputRef} {...props} />;
});

// Parent
const inputRef = useRef(null);
<FancyInput ref={inputRef} />
<button onClick={() => inputRef.current.focus()}>Focus</button>
```
