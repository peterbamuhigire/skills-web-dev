---
name: react-patterns
description: Advanced React design patterns for production apps — Container/Presentational,
  HOC with composition, Render Props, Control Props, Prop Collections/Getters, Compound
  Components (Context-based), State Reducer, and Immer. Use when designing...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# React Design Patterns

<!-- dual-compat-start -->
## Use When

- Advanced React design patterns for production apps — Container/Presentational, HOC with composition, Render Props, Control Props, Prop Collections/Getters, Compound Components (Context-based), State Reducer, and Immer. Use when designing...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `react-patterns` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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
| Correctness | Pattern usage decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering Container/Presentational, HOC, Render Props, and Compound Component picks | `docs/web/react-patterns-adr.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Advanced patterns for building scalable, reusable React components.
Use alongside `react-development` skill for hooks/state fundamentals.

## Pattern Decision Guide

```
Cross-cutting behaviour (auth, loading, analytics) → HOC
Shared stateful logic, no UI opinion               → Custom Hook (preferred)
Component that yields render control               → Render Props or Children-as-Function
Controlled OR uncontrolled flex                    → Control Props
Bundle reusable event props (drag, a11y)           → Prop Collections + Prop Getters
Interconnected sub-components sharing state        → Compound Components
Component whose state logic users must customise   → State Reducer
Complex nested state updates                       → Immer
Separate data logic from UI                        → Container / Presentational
```

---

## 1. Container / Presentational

Separate **how it looks** from **how it works**.

```tsx
// Presentational — pure props, no data fetching, visually testable
function UserCard({ name, email, onSelect }: {
  name: string; email: string; onSelect: (email: string) => void
}) {
  return (
    <div onClick={() => onSelect(email)}>
      <h3>{name}</h3><p>{email}</p>
    </div>
  );
}

// Container — fetches data, manages state, delegates rendering
function UserCardContainer({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  useEffect(() => { fetchUser(userId).then(setUser); }, [userId]);
  if (!user) return <Spinner />;
  return <UserCard name={user.name} email={user.email} onSelect={sendEmail} />;
}
```

**When to use:** Large teams where UI and logic owners differ; components needing
visual testing (Storybook) separate from unit tests.

**Modern note:** Hooks often replace container components. Prefer hooks for new code
unless team separation is a concrete requirement.

---

## 2. Higher-Order Component (HOC)

A function that takes a component and returns an enhanced component.

```tsx
// withAsync — eliminates repeated loading/error state
const withAsync = <P extends { data?: unknown }>(
  Component: React.ComponentType<P>
) => (props: P & { loading?: boolean; error?: Error | null }) => {
  if (props.loading) return <div>Loading…</div>;
  if (props.error)   return <div>Error: {props.error.message}</div>;
  return <Component {...props} />;
};

// Usage
const AsyncTodoList = withAsync(BasicTodoList);
<AsyncTodoList loading={isLoading} error={error} data={data} />
```

### HOC Composition

Avoid nested HOC calls — use a `compose` utility:

```tsx
const compose = (...hocs: Function[]) =>
  (Component: React.ComponentType<any>) =>
    hocs.reduceRight((acc, hoc) => hoc(acc), Component);

// Clean instead of withA(withB(withC(withD(MyComponent))))
const Enhanced = compose(
  withErrorBoundary,
  withAuth,
  withAnalytics,
  withAsync,
)(MyComponent);
```

### HOC vs Hooks

| Concern | Use HOC | Use Hook |
|---|---|---|
| Inject/manipulate props | ✅ | ❌ |
| Control rendering of wrapped component | ✅ | ❌ |
| Reuse stateful logic | ⚠️ (adds wrapper) | ✅ (preferred) |
| TypeScript ergonomics | Tricky | Easy |
| Testing isolation | Harder | Easier |

**Rule:** Use hooks by default. Reach for HOCs when you need to control rendering
or inject props from outside (e.g., `withAuth`, `withAsync`, `React.memo`, `React.forwardRef`).

---

## 3. Render Props / Children as Function

A component that yields render control to its parent via a prop.

```tsx
// Children as function (preferred spelling)
function WindowSize({ children }: { children: (size: { w: number; h: number }) => ReactNode }) {
  const [size, setSize] = useState({ w: window.innerWidth, h: window.innerHeight });
  useEffect(() => {
    const onResize = () => setSize({ w: window.innerWidth, h: window.innerHeight });
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);
  return <>{children(size)}</>;
}

// Usage
<WindowSize>
  {({ w, h }) => <p>Window: {w}×{h}</p>}
</WindowSize>
```

**When to use:** When you want a headless component that manages behaviour but
lets parents own the UI. **Modern note:** Custom hooks (`useWindowSize`) achieve the
same with less ceremony — prefer hooks unless you need JSX isolation.

---

## 4. Control Props

A component that works in both **controlled** (parent owns state) and
**uncontrolled** (component owns state) modes.

```tsx
function Toggle({
  on,          // controlled: parent provides value
  onToggle,    // controlled: parent receives changes
  defaultOn = false,  // uncontrolled: initial value
}: {
  on?: boolean;
  onToggle?: (next: boolean) => void;
  defaultOn?: boolean;
}) {
  const [internalOn, setInternalOn] = useState(defaultOn);
  const isControlled = on !== undefined;
  const isOn = isControlled ? on : internalOn;

  const handleToggle = () => {
    const next = !isOn;
    if (!isControlled) setInternalOn(next);
    onToggle?.(next);
  };

  return (
    <button onClick={handleToggle}>
      {isOn ? 'On' : 'Off'}
    </button>
  );
}

// Controlled
<Toggle on={externalState} onToggle={setExternalState} />
// Uncontrolled
<Toggle defaultOn={true} onToggle={(v) => console.log(v)} />
```

**When to use:** Library components (form inputs, modals, date pickers) that need to
work in both modes. React's own `<input>` uses this pattern.

---

## 5. Prop Collections + Prop Getters

Bundle related props together; merge custom overrides without clobbering defaults.

```tsx
// Prop Collection — simple bundle of related props
export const draggableProps = {
  draggable: true,
  onDragStart: (e: DragEvent) => e.dataTransfer.effectAllowed = 'move',
  onDragEnd:   (_e: DragEvent) => {},
};

// Prop Getter — function that composes defaults with custom overrides
const compose = (...fns: Function[]) =>
  (...args: unknown[]) => fns.forEach(fn => fn?.(...args));

export function getDroppableProps({ onDragOver, ...rest }: Partial<HTMLAttributes<HTMLDivElement>> = {}) {
  return {
    onDragOver: compose(
      (e: DragEvent) => e.preventDefault(),  // default: allow drop
      onDragOver,                             // user's override added, not replacing
    ),
    ...rest,
  };
}

// Usage — user's onDragOver runs AND default preventDefault runs
<Dropzone {...getDroppableProps({ onDragOver: () => console.log('dragged!') })} />
```

**Key insight:** Prop getters solve the problem where spreading a custom prop would
silently override the default handler. Widely used for accessibility aria-* bundles.

---

## 6. Compound Components

Interconnected components that share state via Context but render independently.

```tsx
// AccordionContext — shared state among all accordion parts
const AccordionContext = createContext<{
  activeIndex: number;
  setActiveIndex: (i: number) => void;
} | null>(null);

// Root — owns state, provides context
function Accordion({ children }: { children: ReactNode }) {
  const [activeIndex, setActiveIndex] = useState(0);
  return (
    <AccordionContext.Provider value={{ activeIndex, setActiveIndex }}>
      <ul>{children}</ul>
    </AccordionContext.Provider>
  );
}

// Item — consumes context, unaware of siblings
function AccordionItem({ index, label, children }: {
  index: number; label: string; children: ReactNode;
}) {
  const ctx = useContext(AccordionContext)!;
  const isOpen = ctx.activeIndex === index;
  return (
    <li>
      <button onClick={() => ctx.setActiveIndex(index)}>{label}</button>
      {isOpen && <div>{children}</div>}
    </li>
  );
}

Accordion.Item = AccordionItem; // attach as static property

// Usage — full control of element tree, shared state awareness
<Accordion>
  <Accordion.Item index={0} label="Section 1">Content A</Accordion.Item>
  <hr />
  <Accordion.Item index={1} label="Section 2">Content B</Accordion.Item>
</Accordion>
```

**When to use:** Complex UI components with multiple parts (Tabs, Select, Menu,
Accordion) where consumers need element-level control but children must share state.
Attach child components as static properties for clean consumer API.

---

## 7. State Reducer Pattern

Let consumers customise a component's internal state transitions without forking it.
Pattern by Kent C. Dodds.

```tsx
type ToggleState = { on: boolean };
type ToggleAction = { type: 'TOGGLE'; changes: ToggleState };

function defaultReducer(_state: ToggleState, action: ToggleAction) {
  return action.changes; // default: accept all changes
}

function Toggle({ stateReducer = defaultReducer }: {
  stateReducer?: (state: ToggleState, action: ToggleAction) => ToggleState;
}) {
  const [state, dispatch] = useReducer(
    (state: ToggleState, action: { type: 'TOGGLE' }) => {
      const changes = { on: !state.on };                      // internal logic
      return stateReducer(state, { ...action, changes });     // external override
    },
    { on: false }
  );

  return (
    <button onClick={() => dispatch({ type: 'TOGGLE' })}>
      {state.on ? 'On' : 'Off'}
    </button>
  );
}

// Consumer customises behaviour without modifying Toggle
function App() {
  // Business rule: can't turn off on Wednesdays
  const noWednesdayOff = (state: ToggleState, action: ToggleAction) => {
    if (new Date().getDay() === 3 && !action.changes.on) return state;
    return action.changes;
  };
  return <Toggle stateReducer={noWednesdayOff} />;
}
```

**When to use:** Library components (design systems, npm packages) where business
rules vary per consumer. Passes control to the caller while preserving defaults.

---

## 8. Immer — Ergonomic Immutable State

Use when state is deeply nested and spread syntax becomes unwieldy.

```tsx
import { produce } from 'immer';

// Without Immer — verbose and error-prone at depth
setState(prev => ({
  ...prev,
  user: { ...prev.user, address: { ...prev.user.address, city: 'Kampala' } }
}));

// With Immer — mutate the draft, Immer produces a new immutable object
setState(produce(draft => {
  draft.user.address.city = 'Kampala';
}));

// With useReducer
import { useImmerReducer } from 'use-immer';

const [state, dispatch] = useImmerReducer((draft, action) => {
  switch (action.type) {
    case 'UPDATE_CITY':
      draft.user.address.city = action.city; // mutable-style update
      break;
  }
}, initialState);
```

**Install:** `npm install immer use-immer`

---

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Deeply nested HOC wrapping | Use `compose()` utility |
| Render prop when a hook suffices | Extract custom hook instead |
| Prop spread overriding default handlers | Use prop getters with `compose` |
| Context for every shared state | Only use Context when prop drilling > 2 levels |
| State reducer that ignores `changes` | Always return `action.changes` as default |
| Compound component without Context | Never use `React.cloneElement` — use Context |

---

*Sources: Kumar — Fluent React (O'Reilly, 2023); Santana Roldán — React 18 Design Patterns and Best Practices (Packt, 2024)*
