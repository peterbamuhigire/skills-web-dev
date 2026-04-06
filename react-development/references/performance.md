# React Performance Optimisation

## When to Optimise

Profile first. Use React DevTools Profiler to identify actual bottlenecks.
Add `React.memo`, `useMemo`, `useCallback` after measuring — not preemptively.

## React.memo — Prevent Unnecessary Re-renders

```jsx
// Memoised child — only re-renders when task or onToggle reference changes
const TaskItem = React.memo(function TaskItem({ task, onToggle, onDelete }) {
  console.log('TaskItem render', task.id);  // check in DevTools
  return (
    <li className={task.done ? 'done' : ''}>
      <span onClick={() => onToggle(task.id)}>{task.name}</span>
      <button onClick={() => onDelete(task.id)}>Delete</button>
    </li>
  );
});

// Parent MUST use useCallback for the handlers — otherwise new function = re-render
function TaskList({ tasks }) {
  const [items, setItems] = useState(tasks);

  const handleToggle = useCallback((id) => {
    setItems(prev => prev.map(t => t.id === id ? { ...t, done: !t.done } : t));
  }, []);

  const handleDelete = useCallback((id) => {
    setItems(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ul>
      {items.map(task => (
        <TaskItem key={task.id} task={task} onToggle={handleToggle} onDelete={handleDelete} />
      ))}
    </ul>
  );
}

// Custom comparison function when default shallow-compare is insufficient
const ComplexCard = React.memo(function ComplexCard({ data, config }) {
  return <div>{data.title}</div>;
}, (prevProps, nextProps) => {
  // Return true = skip re-render (props are equal)
  // Return false = re-render (props have changed)
  return prevProps.data.id === nextProps.data.id &&
         prevProps.data.updatedAt === nextProps.data.updatedAt;
});
```

## Code Splitting — Dynamic Imports

```jsx
// Route-based splitting (most impactful)
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Reports   = React.lazy(() => import('./pages/Reports'));
const Settings  = React.lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/"          element={<Home />} />  {/* eager-loaded */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/reports"   element={<Reports />} />
        <Route path="/settings"  element={<Settings />} />
      </Routes>
    </Suspense>
  );
}

// Component-level splitting — heavy components loaded on demand
const RichTextEditor = React.lazy(() => import('./components/RichTextEditor'));
const MapView = React.lazy(() => import('./components/MapView'));

function ArticleEditor({ showMap }) {
  return (
    <div>
      <Suspense fallback={<EditorSkeleton />}>
        <RichTextEditor />
      </Suspense>
      {showMap && (
        <Suspense fallback={<div>Loading map...</div>}>
          <MapView />
        </Suspense>
      )}
    </div>
  );
}

// Named exports with lazy
const { Chart } = React.lazy(() =>
  import('./charts').then(module => ({ default: module.Chart }))
);
```

## Virtual Lists (react-window)

```jsx
import { FixedSizeList, VariableSizeList, FixedSizeGrid } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';

// Fixed-height rows
function VirtualUserList({ users }) {
  const Row = ({ index, style }) => (
    <div style={style} className="row">
      <UserCard user={users[index]} />
    </div>
  );

  return (
    <AutoSizer>
      {({ height, width }) => (
        <FixedSizeList
          height={height}
          width={width}
          itemCount={users.length}
          itemSize={72}       // px per row
          overscanCount={5}   // render 5 extra rows outside viewport
        >
          {Row}
        </FixedSizeList>
      )}
    </AutoSizer>
  );
}

// Variable-height rows
function VirtualCommentList({ comments, heights }) {
  const getItemSize = useCallback((index) => heights[index] ?? 80, [heights]);

  return (
    <VariableSizeList
      height={600}
      width="100%"
      itemCount={comments.length}
      itemSize={getItemSize}
    >
      {({ index, style }) => <Comment style={style} comment={comments[index]} />}
    </VariableSizeList>
  );
}
```

## State Colocation and Context Splitting

```jsx
// BAD: one giant context — any update re-renders all consumers
const AppContext = createContext({ user, theme, notifications, settings });

// GOOD: split by update frequency
const UserContext      = createContext(null);  // changes: login/logout
const ThemeContext     = createContext(null);  // changes: rarely
const NotifContext     = createContext(null);  // changes: frequently
const SettingsContext  = createContext(null);  // changes: rarely

// Colocation — keep state as close to consumers as possible
function SearchPage() {
  const [query, setQuery] = useState('');  // local to SearchPage, not global
  const results = useMemo(() => search(allData, query), [query]);
  return <><SearchInput value={query} onChange={setQuery} /><Results items={results} /></>;
}
```

## Avoiding Inline Objects and Functions in JSX

```jsx
// BAD — new object on every render
<Component style={{ marginTop: 16 }} options={{ sort: 'asc' }} />

// GOOD — stable references
const STYLE  = { marginTop: 16 };
const OPTIONS = { sort: 'asc' };
<Component style={STYLE} options={OPTIONS} />

// Or compute with useMemo if derived from props/state
const style = useMemo(() => ({ marginTop: spacing * 4 }), [spacing]);
```

## Image Optimisation

```jsx
// Lazy-load images with native loading attribute
<img src={product.image} alt={product.name} loading="lazy" decoding="async" />

// Responsive images
<img
  src={`/images/${id}-400.webp`}
  srcSet={`/images/${id}-400.webp 400w, /images/${id}-800.webp 800w, /images/${id}-1200.webp 1200w`}
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  alt={alt}
  loading="lazy"
/>
```

## useTransition for Heavy Renders

```jsx
function SearchWithTransition() {
  const [input, setInput] = useState('');
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    setInput(e.target.value);   // urgent — input stays responsive
    startTransition(() => {
      setQuery(e.target.value); // deferred — can be interrupted
    });
  };

  return (
    <>
      <input value={input} onChange={handleChange} placeholder="Search..." />
      {isPending && <div className="updating-indicator" />}
      <ExpensiveFilteredList query={query} />
    </>
  );
}
```

## Production Build Checklist

- Run `npm run build` and analyse bundle with `webpack-bundle-analyzer` or `vite-bundle-analyzer`
- All images optimised (WebP, proper dimensions, lazy loaded)
- React.lazy on all routes and heavy components
- No console.log statements (add ESLint rule `no-console`)
- Service worker for caching static assets
- Code split vendor bundles (React, lodash, etc.) separately
- Tree-shaking: use named imports — never `import _ from 'lodash'`
- Measure with Lighthouse before and after optimisations
