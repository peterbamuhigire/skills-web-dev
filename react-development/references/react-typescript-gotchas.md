# React + TypeScript gotchas (production-grade)

Distilled from *Fullstack React with TypeScript* (Newline) and field experience. Focuses on places where TS and React idioms collide.

## Component prop typing

- Use `type Props = { ... }` then `function Foo({ ... }: Props) { ... }`. Avoid `React.FC` — it implicitly adds `children`, fights generics, and can't return `null` cleanly in older versions. (React 18+ removed implicit children from FC, so it's less harmful, but the explicit form is still clearer.)
- Type `children` as `React.ReactNode` (not `JSX.Element` — that breaks for arrays, strings, nulls).
- Discriminated props for "either A or B" components:

```ts
type Props = { variant: "icon"; icon: string } | { variant: "text"; text: string };
```

## Event handlers

- Inline handlers: TS infers from JSX (`onClick={(e) => ...}` gets `MouseEvent<HTMLButtonElement>`). Externalised handlers must be annotated:

```ts
const onSubmit: React.FormEventHandler<HTMLFormElement> = (e) => { e.preventDefault(); };
```

- Custom callback props on a component: type the parameter explicitly, not `Function`. `onChange: (value: string) => void`.

## `useState` typing

- Primitive narrowing: `useState<"loading" | "ready" | "error">("loading")`. Without the generic, TS infers `string` and your switch loses exhaustiveness.
- Nullable initial: `useState<User | null>(null)`. Don't `useState({} as User)` — that's a lie.
- Lazy init for expensive values: `useState(() => buildInitialState(props))`. Function form is called once.

## `useReducer` (Fullstack React with TS pattern)

The book's Trello example shows the canonical typed pattern:

```ts
type State = { lists: List[]; draggedItem: DragItem | null };

type Action =
  | { type: "ADD_LIST"; payload: string }
  | { type: "ADD_TASK"; payload: { text: string; listId: string } }
  | { type: "MOVE_LIST"; payload: { dragIndex: number; hoverIndex: number } }
  | { type: "SET_DRAGGED_ITEM"; payload: DragItem | null };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "ADD_LIST":
      return { ...state, lists: [...state.lists, { id: nanoid(), text: action.payload, tasks: [] }] };
    // ...
    default: {
      const _exhaustive: never = action;
      return state;
    }
  }
}
```

Discriminated union for `Action` + exhaustive default = compile error when you add a new action and forget a case. Critical for any non-trivial reducer.

## `useRef` typing

- DOM refs: `useRef<HTMLInputElement>(null)`. The `null` initial is required; the ref is `RefObject<T>` (read-only `.current`).
- Mutable instance refs: `useRef<number | null>(null)` with explicit init — gives `MutableRefObject<T>`.
- Don't pass an unwrapped ref to a generic-typed library expecting `RefObject<HTMLDivElement>`; cast the generic, not the result.

## Context typing — the "no default" pattern

```ts
const AuthContext = createContext<AuthState | null>(null);

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
```

Throwing in the hook saves every consumer from null-checking. Never default to a fake object — it hides "Provider missing" bugs in production.

## Generic components

```tsx
type ListProps<T> = { items: T[]; render: (item: T) => React.ReactNode };
function List<T>({ items, render }: ListProps<T>) {
  return <ul>{items.map((it, i) => <li key={i}>{render(it)}</li>)}</ul>;
}
```

Gotchas: in `.tsx`, `<T>` is parsed as JSX. Workarounds: `<T,>` (trailing comma) or `<T extends unknown>`. Pick one convention.

## Render props vs children-as-function

The Fullstack React book demonstrates both for the music-keyboard example. Decision rule:

- One render slot, simple → `children` as function (`children: (api: Api) => ReactNode`).
- Multiple slots (header / body / footer) → named render props.
- Cross-cutting behaviour with state but no UI → custom hook (almost always preferred over either pattern in modern React).

## HOC typing

HOCs are painful in TS. Modern guidance: prefer custom hooks. When you must (auth, theme, analytics wrappers for class components), type carefully:

```ts
function withAuth<P>(Wrapped: React.ComponentType<P & { auth: Auth }>) {
  return function WithAuth(props: P) {
    const auth = useAuth();
    return <Wrapped {...props} auth={auth} />;
  };
}
```

Forwarding refs through HOCs requires `forwardRef` plus `ComponentPropsWithRef<typeof Wrapped>` — usually not worth the complexity. Reach for hooks first.

## Drag-and-drop with react-dnd + TS

From the Trello chapter:

- Define `type DragItem = { id: string; type: "CARD" | "LIST"; index: number }`.
- `useDrag` and `useDrop` are generic in the item type — pass the discriminated `DragItem`.
- Hover handler runs on every pixel — debounce reducer dispatches by comparing `dragIndex !== hoverIndex` before dispatching.
- Mutate `item.index = hoverIndex` inside `hover` callback so subsequent moves use the new position. This is the one place where mutation is correct.

## GraphQL + Apollo + TS (book's GitHub example)

- Generate types via `graphql-codegen` from the schema introspection. Never hand-write GraphQL response types.
- The generated `useFooQuery` hook returns `{ data, loading, error }` with `data` typed as `FooQuery | undefined`. Always narrow on `data` before using.
- Mutations: pass typed variables; let codegen infer the response.

## Redux Toolkit + TS

- Use `createSlice` — gives you typed actions and reducers automatically.
- Type the root `RootState = ReturnType<typeof store.getState>` and `AppDispatch = typeof store.dispatch`.
- Wrap `useDispatch`/`useSelector` once: `export const useAppDispatch: () => AppDispatch = useDispatch`. Components import the wrapped versions.
- Thunks: `createAsyncThunk<Returned, ThunkArg, { state: RootState }>(...)` — third generic gives access to typed `getState`.

## Common error message → fix

| Error | Cause | Fix |
|---|---|---|
| "Type 'X' is missing properties from type 'Y'" on JSX | Forgot a required prop | Add prop or make it optional |
| "JSX element implicitly has type 'any'" | Component returns `any` (often from missing return) | Add explicit return type or fix render path |
| "Cannot find namespace 'JSX'" | Old types | `@types/react` >= 18; update tsconfig `jsx` to `react-jsx` |
| "Property 'children' does not exist on type" | React 18 removed implicit children from `FC` | Add `children: React.ReactNode` to your Props |
| "RefObject is read-only" | Trying to assign to `.current` from a `useRef<T>(null)` | Use `useRef<T \| null>(null)` for mutable refs |

## Anti-patterns

- `as any` to silence prop errors. Solve the type instead.
- `any` for event handlers (`(e: any) => ...`). Always use the React event type.
- Typing state as `object` or `{}`. Be specific.
- Spreading `...props` into a DOM element without `React.HTMLAttributes<HTMLDivElement>` — leaks unknown attrs to the DOM.
- Defining context default as a fake object (`createContext<Auth>({} as Auth)`) — kills the "Provider missing" runtime check.
- Putting reducer `Action` types in the same file as components. Move to `types.ts` so the reducer is testable in isolation.
