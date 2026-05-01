# React with TypeScript — Patterns Reference

## Component Props Typing

```tsx
// Basic props interface
interface ButtonProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  children?: React.ReactNode;
  className?: string;
}

function Button({ label, variant = 'primary', disabled = false, onClick, children }: ButtonProps) {
  return (
    <button className={`btn btn--${variant}`} disabled={disabled} onClick={onClick}>
      {children ?? label}
    </button>
  );
}

// Extending HTML element props
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
}

function Input({ label, error, hint, ...inputProps }: InputProps) {
  return (
    <div className="field">
      <label>{label}</label>
      <input {...inputProps} aria-invalid={!!error} />
      {error && <span className="error">{error}</span>}
      {hint  && <span className="hint">{hint}</span>}
    </div>
  );
}
```

## Event Handler Types

```tsx
// Input events
const handleChange  = (e: React.ChangeEvent<HTMLInputElement>)   => setName(e.target.value);
const handleSelect  = (e: React.ChangeEvent<HTMLSelectElement>)  => setChoice(e.target.value);
const handleTextarea = (e: React.ChangeEvent<HTMLTextAreaElement>) => setText(e.target.value);

// Form submit
const handleSubmit  = (e: React.FormEvent<HTMLFormElement>) => { e.preventDefault(); submit(); };

// Button click
const handleClick   = (e: React.MouseEvent<HTMLButtonElement>) => doSomething();

// Keyboard
const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter') submit();
};

// Focus / blur
const handleFocus   = (e: React.FocusEvent<HTMLInputElement>) => e.target.select();
```

## Refs

```tsx
// DOM ref — specify the element type
const inputRef  = useRef<HTMLInputElement>(null);
const divRef    = useRef<HTMLDivElement>(null);
const buttonRef = useRef<HTMLButtonElement>(null);

// Usage — null check required
inputRef.current?.focus();
const height = divRef.current?.getBoundingClientRect().height ?? 0;

// Mutable ref (no null)
const countRef = useRef<number>(0);
countRef.current++;  // no null check needed
```

## useState with Types

```tsx
// Type inferred from initial value
const [count, setCount] = useState(0);           // number
const [name, setName]   = useState('');           // string

// Explicit type for complex/nullable values
const [user, setUser]   = useState<User | null>(null);
const [items, setItems] = useState<Item[]>([]);

// Union state
type Status = 'idle' | 'loading' | 'success' | 'error';
const [status, setStatus] = useState<Status>('idle');

// Interface
interface FormState {
  name: string;
  email: string;
  role: 'admin' | 'viewer' | 'editor';
}
const [form, setForm] = useState<FormState>({ name: '', email: '', role: 'viewer' });
```

## useReducer with Types

```tsx
interface State {
  items: Item[];
  loading: boolean;
  error: string | null;
}

type Action =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: Item[] }
  | { type: 'FETCH_ERROR'; payload: string }
  | { type: 'ADD_ITEM'; payload: Item }
  | { type: 'DELETE_ITEM'; payload: string };  // id

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, items: action.payload };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'ADD_ITEM':
      return { ...state, items: [...state.items, action.payload] };
    case 'DELETE_ITEM':
      return { ...state, items: state.items.filter(i => i.id !== action.payload) };
    default: {
      const _exhaustive: never = action;  // compile error if case missed
      return state;
    }
  }
}
```

## Context with Types

```tsx
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggle: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const toggle = useCallback(() => setTheme(t => t === 'light' ? 'dark' : 'light'), []);
  const value = useMemo(() => ({ theme, toggle, setTheme }), [theme, toggle]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextType {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
```

## Generic Custom Hooks

```tsx
// Generic list management
function useList<T extends { id: string }>(initial: T[] = []) {
  const [items, setItems] = useState<T[]>(initial);

  const add    = useCallback((item: T) => setItems(prev => [...prev, item]), []);
  const remove = useCallback((id: string) => setItems(prev => prev.filter(i => i.id !== id)), []);
  const update = useCallback((id: string, data: Partial<T>) =>
    setItems(prev => prev.map(i => i.id === id ? { ...i, ...data } : i)), []);
  const reset  = useCallback(() => setItems(initial), [initial]);

  return { items, add, remove, update, reset };
}

// Generic async state
interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

function useAsync<T>(asyncFn: () => Promise<T>): AsyncState<T> & { execute: () => void } {
  const [state, setState] = useState<AsyncState<T>>({ data: null, loading: false, error: null });

  const execute = useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const data = await asyncFn();
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ data: null, loading: false, error: err as Error });
    }
  }, [asyncFn]);

  return { ...state, execute };
}
```

## Component Patterns

```tsx
// Polymorphic component (render as different HTML elements)
type As = keyof JSX.IntrinsicElements;
interface BoxProps<T extends As = 'div'> {
  as?: T;
  children?: React.ReactNode;
  className?: string;
}

function Box<T extends As = 'div'>({ as, children, ...props }: BoxProps<T> & JSX.IntrinsicElements[T]) {
  const Component = as ?? 'div';
  return <Component {...props}>{children}</Component>;
}
// <Box as="section" aria-label="Content">...</Box>
// <Box as="button" onClick={handleClick}>Click</Box>

// Render prop with types
interface DataProviderProps<T> {
  data: T[];
  render: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function DataList<T>({ data, render, keyExtractor }: DataProviderProps<T>) {
  return <ul>{data.map((item, i) => <li key={keyExtractor(item)}>{render(item, i)}</li>)}</ul>;
}

// forwardRef with TypeScript
const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input({ label, ...props }, ref) {
  return (
    <div>
      <label>{label}</label>
      <input ref={ref} {...props} />
    </div>
  );
});
```

## Common Type Utilities

```tsx
// React built-in utility types
React.FC<Props>               // function component (avoid — use function declaration)
React.ReactNode               // any renderable content
React.ReactElement            // JSX element specifically
React.CSSProperties           // inline style object type
React.PropsWithChildren<P>    // P & { children?: ReactNode }
React.ComponentProps<typeof Button>  // extract props from component

// Partial and Required
type OptionalForm = Partial<FormState>;    // all optional
type RequiredForm = Required<FormState>;   // all required

// Pick and Omit
type UserPreview = Pick<User, 'id' | 'name' | 'avatar'>;
type UserWithoutPassword = Omit<User, 'password' | 'hashedPassword'>;
```
