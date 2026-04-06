# State Management — Complete Reference

## Decision Matrix

| Scenario | Solution |
|---|---|
| Component-local UI toggle | `useState` |
| Form with validation | `useState` + `useForm` hook |
| Small shared state (theme, auth) | Context + `useReducer` |
| Medium app global state | Zustand |
| Large app with complex logic | Redux Toolkit |
| Server data (fetch, cache, sync) | React Query or SWR |
| URL-derived state | React Router `useSearchParams` |

## Context + useReducer Pattern

```jsx
// 1. Define types
const ACTIONS = {
  LOGIN: 'LOGIN', LOGOUT: 'LOGOUT', UPDATE_PROFILE: 'UPDATE_PROFILE',
};

// 2. Reducer — pure function, no side effects
function authReducer(state, action) {
  switch (action.type) {
    case ACTIONS.LOGIN:
      return { user: action.payload, isAuth: true, loading: false };
    case ACTIONS.LOGOUT:
      return { user: null, isAuth: false, loading: false };
    case ACTIONS.UPDATE_PROFILE:
      return { ...state, user: { ...state.user, ...action.payload } };
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

// 3. Context + Provider
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null, isAuth: false, loading: false
  });

  // Memoize actions to prevent unnecessary re-renders
  const login = useCallback(async (credentials) => {
    const user = await loginApi(credentials);
    dispatch({ type: ACTIONS.LOGIN, payload: user });
  }, []);

  const logout = useCallback(() => {
    logoutApi();
    dispatch({ type: ACTIONS.LOGOUT });
  }, []);

  // Memoize context value — only re-renders consumers when state changes
  const value = useMemo(() => ({
    ...state, login, logout,
  }), [state, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// 4. Typed consumer hook
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
```

## Zustand (Recommended for Medium/Large Apps)

```jsx
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Basic store
const useAppStore = create((set, get) => ({
  // State
  user: null,
  notifications: [],
  sidebarOpen: false,

  // Actions
  setUser: (user) => set({ user }),
  clearUser: () => set({ user: null }),
  addNotification: (n) => set(state => ({
    notifications: [...state.notifications, { id: Date.now(), ...n }]
  })),
  dismissNotification: (id) => set(state => ({
    notifications: state.notifications.filter(n => n.id !== id)
  })),
  toggleSidebar: () => set(state => ({ sidebarOpen: !state.sidebarOpen })),

  // Computed (getter pattern)
  get unreadCount() { return get().notifications.filter(n => !n.read).length; },
}));

// With persistence
const useSettingsStore = create(
  persist(
    (set) => ({
      theme: 'light',
      language: 'en',
      setTheme: (theme) => set({ theme }),
      setLanguage: (lang) => set({ language: lang }),
    }),
    { name: 'app-settings', storage: localStorage }
  )
);

// Selective subscription — only re-render when user changes
const user = useAppStore(state => state.user);
const { setUser, clearUser } = useAppStore();
```

## Redux Toolkit (Large / Complex Apps)

```jsx
import { createSlice, createAsyncThunk, configureStore } from '@reduxjs/toolkit';

// Async thunk
export const fetchCards = createAsyncThunk('cards/fetchAll', async (_, { rejectWithValue }) => {
  try {
    const response = await fetch('/api/cards');
    return await response.json();
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

// Slice
const cardsSlice = createSlice({
  name: 'cards',
  initialState: { items: [], status: 'idle', error: null },
  reducers: {
    addCard: (state, action) => { state.items.push(action.payload); },
    updateCard: (state, action) => {
      const idx = state.items.findIndex(c => c.id === action.payload.id);
      if (idx !== -1) state.items[idx] = action.payload;
    },
    deleteCard: (state, action) => {
      state.items = state.items.filter(c => c.id !== action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCards.pending, (state) => { state.status = 'loading'; })
      .addCase(fetchCards.fulfilled, (state, action) => {
        state.status = 'success';
        state.items = action.payload;
      })
      .addCase(fetchCards.rejected, (state, action) => {
        state.status = 'error';
        state.error = action.payload;
      });
  },
});

export const { addCard, updateCard, deleteCard } = cardsSlice.actions;

// Selectors
export const selectAllCards = (state) => state.cards.items;
export const selectCardById = (id) => (state) => state.cards.items.find(c => c.id === id);

// Usage in component
function CardList() {
  const dispatch = useDispatch();
  const cards = useSelector(selectAllCards);
  const status = useSelector(state => state.cards.status);

  useEffect(() => { dispatch(fetchCards()); }, [dispatch]);

  if (status === 'loading') return <Spinner />;
  return <>{cards.map(c => <Card key={c.id} card={c} />)}</>;
}
```

## React Query (Server State)

```jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch with caching, auto-refetch, loading states
function useCards() {
  return useQuery({
    queryKey: ['cards'],
    queryFn: () => fetch('/api/cards').then(r => r.json()),
    staleTime: 5 * 60 * 1000,   // 5 minutes
    cacheTime: 10 * 60 * 1000,  // 10 minutes
  });
}

// Optimistic mutation
function useAddCard() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (card) => fetch('/api/cards', { method: 'POST', body: JSON.stringify(card) }),
    onMutate: async (newCard) => {
      await queryClient.cancelQueries({ queryKey: ['cards'] });
      const prev = queryClient.getQueryData(['cards']);
      queryClient.setQueryData(['cards'], old => [...old, { ...newCard, id: 'temp' }]);
      return { prev };   // rollback context
    },
    onError: (err, newCard, ctx) => {
      queryClient.setQueryData(['cards'], ctx.prev);  // rollback
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['cards'] });
    },
  });
}
```

## React Router v6

```jsx
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useParams, useNavigate, useLocation, useSearchParams, Link, NavLink } from 'react-router-dom';

// Nested routes with layout
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="users" element={<UserList />} />
          <Route path="users/:id" element={<UserDetail />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

// Layout renders <Outlet /> for children
function Layout() {
  return (
    <div>
      <Nav />
      <main><Outlet /></main>
    </div>
  );
}

// Protected route wrapper
function RequireAuth({ children }) {
  const { isAuth } = useAuth();
  const location = useLocation();
  if (!isAuth) return <Navigate to="/login" state={{ from: location }} replace />;
  return children;
}

// Router hooks
function UserDetail() {
  const { id } = useParams();            // :id from path
  const navigate = useNavigate();         // programmatic navigation
  const location = useLocation();         // current URL info
  const [params, setParams] = useSearchParams();  // ?key=value

  const page = params.get('page') ?? '1';
  const setPage = (p) => setParams({ page: String(p) });

  return (
    <>
      <button onClick={() => navigate(-1)}>Back</button>
      <button onClick={() => navigate('/users', { replace: true })}>All Users</button>
      <Link to={`/users/${id}/edit`}>Edit</Link>
      <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'active' : ''}>
        Dashboard
      </NavLink>
    </>
  );
}
```
