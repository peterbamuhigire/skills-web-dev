# Custom Hooks — Complete Library

Rules: name starts with `use`, can call other hooks, encapsulates stateful logic.

## Data & API Hooks

```jsx
// Generic fetch hook with loading/error/data
function useFetch(url, options = {}) {
  const [state, dispatch] = useReducer(
    (s, a) => ({ ...s, ...a }),
    { data: null, loading: true, error: null }
  );

  useEffect(() => {
    if (!url) return;
    let cancelled = false;
    dispatch({ loading: true, error: null });
    fetch(url, options)
      .then(r => { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then(data => { if (!cancelled) dispatch({ data, loading: false }); })
      .catch(error => { if (!cancelled) dispatch({ error, loading: false }); });
    return () => { cancelled = true; };
  }, [url]);

  return state;
}

// Pagination hook
function usePagination(fetchFn, { pageSize = 20 } = {}) {
  const [page, setPage]     = useState(1);
  const [items, setItems]   = useState([]);
  const [total, setTotal]   = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchFn({ page, pageSize })
      .then(({ data, total }) => { setItems(data); setTotal(total); })
      .finally(() => setLoading(false));
  }, [page, pageSize, fetchFn]);

  return {
    items, total, page, loading,
    totalPages: Math.ceil(total / pageSize),
    nextPage: () => setPage(p => Math.min(p + 1, Math.ceil(total / pageSize))),
    prevPage: () => setPage(p => Math.max(p - 1, 1)),
    goToPage: setPage,
  };
}

// Infinite scroll hook
function useInfiniteScroll(fetchFn) {
  const [items, setItems] = useState([]);
  const [page, setPage]   = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const sentinel = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && hasMore && !loading) setPage(p => p + 1);
    });
    if (sentinel.current) observer.observe(sentinel.current);
    return () => observer.disconnect();
  }, [hasMore, loading]);

  useEffect(() => {
    setLoading(true);
    fetchFn(page).then(({ data, hasMore: more }) => {
      setItems(prev => [...prev, ...data]);
      setHasMore(more);
      setLoading(false);
    });
  }, [page, fetchFn]);

  return { items, loading, hasMore, sentinel };
}
```

## Form Hooks

```jsx
// Full form hook with validation
function useForm(initialValues, validationRules = {}) {
  const [values, setValues]   = useState(initialValues);
  const [errors, setErrors]   = useState({});
  const [touched, setTouched] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    setValues(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    // Clear error when user starts typing
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
  }, [errors]);

  const handleBlur = useCallback((e) => {
    setTouched(prev => ({ ...prev, [e.target.name]: true }));
  }, []);

  const validate = useCallback(() => {
    const errs = {};
    Object.entries(validationRules).forEach(([field, rules]) => {
      rules.forEach(rule => {
        if (!errs[field]) {
          const msg = rule(values[field], values);
          if (msg) errs[field] = msg;
        }
      });
    });
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }, [values, validationRules]);

  const handleSubmit = (onSubmit) => async (e) => {
    e.preventDefault();
    // Mark all fields as touched
    setTouched(Object.keys(initialValues).reduce((acc, k) => ({ ...acc, [k]: true }), {}));
    if (!validate()) return;
    setSubmitting(true);
    try { await onSubmit(values); }
    finally { setSubmitting(false); }
  };

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  return { values, errors, touched, submitting, handleChange, handleBlur, handleSubmit, reset, setValues };
}

// Validation rule factories
const rules = {
  required: (msg = 'Required') => (v) => !v ? msg : null,
  minLength: (n, msg) => (v) => v && v.length < n ? (msg || `Min ${n} characters`) : null,
  email: (msg = 'Invalid email') => (v) => v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? msg : null,
  matches: (field, msg) => (v, all) => v !== all[field] ? msg : null,
};

// Usage
const { values, errors, handleChange, handleSubmit } = useForm(
  { email: '', password: '' },
  {
    email: [rules.required(), rules.email()],
    password: [rules.required(), rules.minLength(8)],
  }
);
```

## UI / UX Hooks

```jsx
// Debounce — delay processing until user stops typing
function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

// Local storage with JSON serialisation
function useLocalStorage(key, defaultValue) {
  const [value, setValue] = useState(() => {
    try { return JSON.parse(localStorage.getItem(key)) ?? defaultValue; }
    catch { return defaultValue; }
  });
  const set = useCallback((v) => {
    const toStore = typeof v === 'function' ? v(value) : v;
    setValue(toStore);
    localStorage.setItem(key, JSON.stringify(toStore));
  }, [key, value]);
  const remove = useCallback(() => {
    setValue(defaultValue);
    localStorage.removeItem(key);
  }, [key, defaultValue]);
  return [value, set, remove];
}

// Track previous value
function usePrevious(value) {
  const ref = useRef(undefined);
  useEffect(() => { ref.current = value; });
  return ref.current;
}

// Media query / responsive
function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const mq = window.matchMedia(query);
    const handler = (e) => setMatches(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [query]);
  return matches;
}
// const isMobile = useMediaQuery('(max-width: 768px)');

// Click outside to close dropdown / modal
function useClickOutside(ref, callback) {
  useEffect(() => {
    function handler(e) {
      if (ref.current && !ref.current.contains(e.target)) callback();
    }
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [ref, callback]);
}

// Toggle boolean state
function useToggle(initial = false) {
  const [state, setState] = useState(initial);
  const toggle = useCallback(() => setState(s => !s), []);
  const setTrue  = useCallback(() => setState(true), []);
  const setFalse = useCallback(() => setState(false), []);
  return [state, { toggle, setTrue, setFalse }];
}

// Intersection observer — lazy load / animate on scroll
function useIntersectionObserver(options = {}) {
  const ref = useRef(null);
  const [isIntersecting, setIsIntersecting] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
    }, options);
    observer.observe(el);
    return () => observer.unobserve(el);
  }, [options]);
  return [ref, isIntersecting];
}

// Window size
function useWindowSize() {
  const [size, setSize] = useState({ width: window.innerWidth, height: window.innerHeight });
  useEffect(() => {
    const handler = () => setSize({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);
  return size;
}
```
