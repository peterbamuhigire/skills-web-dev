# React 18 and 19 Features

## React 18 — Concurrent Rendering

### Automatic Batching

React 18 batches all state updates in all contexts (not just event handlers).

```jsx
// React 17: only batched inside synthetic events
// React 18: batched everywhere

// Inside setTimeout — batched in React 18
setTimeout(() => {
  setCount(c => c + 1);   // React 18: only 1 re-render total
  setFlag(f => !f);
  setName('updated');
}, 0);

// Inside Promise — batched in React 18
fetch('/api').then(data => {
  setData(data);         // React 18: only 1 re-render total
  setLoading(false);
  setError(null);
});

// Opt out when needed (force immediate render)
import { flushSync } from 'react-dom';
flushSync(() => setCount(c => c + 1));  // render immediately
flushSync(() => setFlag(f => !f));      // render immediately
```

### useTransition — Non-Blocking State Updates

Mark updates as non-urgent. React can interrupt them to handle urgent user input.

```jsx
function SearchPage() {
  const [query, setQuery]     = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  function handleChange(e) {
    // Urgent: update the controlled input immediately
    setQuery(e.target.value);

    // Non-urgent: allow React to defer and interrupt if needed
    startTransition(() => {
      const filtered = allItems.filter(item =>
        item.name.toLowerCase().includes(e.target.value.toLowerCase())
      );
      setResults(filtered);
    });
  }

  return (
    <div>
      <input value={query} onChange={handleChange} placeholder="Search..." />
      {isPending ? (
        <div className="pending-indicator">Updating...</div>
      ) : (
        <ResultsList items={results} />
      )}
    </div>
  );
}

// useTransition in router navigation
function NavButton({ to, label }) {
  const [isPending, startTransition] = useTransition();
  const navigate = useNavigate();

  return (
    <button
      onClick={() => startTransition(() => navigate(to))}
      disabled={isPending}
      aria-busy={isPending}
    >
      {isPending ? 'Loading...' : label}
    </button>
  );
}
```

### useDeferredValue — Defer Expensive Child Renders

```jsx
function SearchResults({ allItems }) {
  const [input, setInput] = useState('');

  // deferredInput lags behind input — React renders old value while typing
  // and updates when it has spare capacity
  const deferredInput = useDeferredValue(input);

  // Memoize to avoid re-rendering when input changes but deferredInput hasn't
  const filtered = useMemo(
    () => allItems.filter(item => item.name.includes(deferredInput)),
    [allItems, deferredInput]
  );

  const isStale = input !== deferredInput;

  return (
    <>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <div style={{ opacity: isStale ? 0.7 : 1 }}>
        <ItemList items={filtered} />
      </div>
    </>
  );
}
```

**useTransition vs useDeferredValue:**
- `useTransition`: you control the state update (wrap the setter)
- `useDeferredValue`: you receive a value from outside (e.g. from a prop)

### useId — Stable Unique IDs

```jsx
// SSR-safe: same ID generated on server and client
function TextField({ label, hint, errorMsg }) {
  const id = useId();

  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <input id={id} aria-describedby={`${id}-hint ${id}-error`} />
      {hint     && <p id={`${id}-hint`}>{hint}</p>}
      {errorMsg && <p id={`${id}-error`} role="alert">{errorMsg}</p>}
    </div>
  );
}

// Multiple IDs from one call
function MultiField() {
  const id = useId();
  const firstNameId = `${id}-first`;
  const lastNameId  = `${id}-last`;
  return (
    <>
      <label htmlFor={firstNameId}>First Name</label>
      <input id={firstNameId} />
      <label htmlFor={lastNameId}>Last Name</label>
      <input id={lastNameId} />
    </>
  );
}
```

### Suspense Improvements

```jsx
// Suspense works with any async data, not just React.lazy
// Data-fetching libraries (React Query, SWR, Relay) can trigger Suspense

// Multiple Suspense boundaries — granular loading states
function App() {
  return (
    <ErrorBoundary fallback={<Error />}>
      <Suspense fallback={<NavSkeleton />}>
        <Navigation />
      </Suspense>
      <Suspense fallback={<PageSkeleton />}>
        <MainContent />
      </Suspense>
      <Suspense fallback={<SidebarSkeleton />}>
        <Sidebar />
      </Suspense>
    </ErrorBoundary>
  );
}

// SuspenseList — coordinate reveal order
import { SuspenseList } from 'react';
<SuspenseList revealOrder="forwards" tail="collapsed">
  <Suspense fallback={<Skeleton />}><Card1 /></Suspense>
  <Suspense fallback={<Skeleton />}><Card2 /></Suspense>
  <Suspense fallback={<Skeleton />}><Card3 /></Suspense>
</SuspenseList>
```

## React 19 Features

### use() Hook — Read Promises and Context

```jsx
import { use } from 'react';

// Read a promise directly in render (Suspense handles loading state)
function UserProfile({ userPromise }) {
  const user = use(userPromise);  // suspends until resolved
  return <h1>{user.name}</h1>;
}

// Read context (alternative to useContext)
const theme = use(ThemeContext);  // can be called conditionally unlike useContext
```

### Server Components (React 19 / Next.js App Router)

```jsx
// Server Component — runs on server, no hooks, no interactivity
// app/users/page.jsx (Next.js App Router)
async function UsersPage() {
  const users = await fetchUsersFromDB();  // direct DB access, no useEffect
  return (
    <div>
      <h1>Users</h1>
      {users.map(u => <UserRow key={u.id} user={u} />)}
    </div>
  );
}

// Client Component — must opt in with 'use client'
'use client';
function UserRow({ user }) {
  const [expanded, setExpanded] = useState(false);  // hooks work here
  return (
    <div onClick={() => setExpanded(e => !e)}>
      <p>{user.name}</p>
      {expanded && <UserDetails user={user} />}
    </div>
  );
}
```

### Server Actions

```jsx
// app/actions.js
'use server';
export async function createUser(formData) {
  const name  = formData.get('name');
  const email = formData.get('email');
  await db.users.create({ name, email });
  revalidatePath('/users');
}

// Client usage
import { createUser } from './actions';

function CreateUserForm() {
  return (
    <form action={createUser}>
      <input name="name" required />
      <input name="email" type="email" required />
      <button type="submit">Create</button>
    </form>
  );
}
```

### useFormStatus — Form Submission State

```jsx
'use client';
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Saving...' : 'Save'}
    </button>
  );
}

// Must be used inside a <form> component
function EditForm({ action }) {
  return (
    <form action={action}>
      <input name="title" />
      <SubmitButton />
    </form>
  );
}
```

### useOptimistic — Optimistic UI Updates

```jsx
'use client';
import { useOptimistic } from 'react';

function MessageThread({ messages, sendMessage }) {
  const [optimisticMessages, addOptimistic] = useOptimistic(
    messages,
    (currentMessages, newMessage) => [...currentMessages, { ...newMessage, pending: true }]
  );

  async function handleSend(formData) {
    const text = formData.get('text');
    const message = { id: Date.now(), text, author: 'me' };

    addOptimistic(message);           // show immediately with pending: true
    await sendMessage(message);       // actual API call
    // React reverts optimistic state and replaces with server response
  }

  return (
    <div>
      {optimisticMessages.map(m => (
        <div key={m.id} style={{ opacity: m.pending ? 0.6 : 1 }}>
          {m.text}
        </div>
      ))}
      <form action={handleSend}>
        <input name="text" />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

## Strict Mode Behaviour

React 18 Strict Mode (development only) double-invokes:
- Component render functions
- State initialiser functions
- Reducer functions
- `useEffect` setup AND cleanup (then setup again)

This surfaces bugs from non-idempotent setup or effects that don't clean up properly.

```jsx
// Your effects must handle double-invocation
useEffect(() => {
  const ws = new WebSocket(url);
  ws.onmessage = (e) => setMessage(e.data);

  // Without cleanup: two connections opened in Strict Mode
  return () => ws.close();  // cleanup makes this safe
}, [url]);
```
