# Testing React Components

Stack: React Testing Library + Jest (or Vitest) + `@testing-library/user-event`.

## Setup

```bash
npm install --save-dev @testing-library/react @testing-library/user-event @testing-library/jest-dom
```

```js
// jest.setup.js
import '@testing-library/jest-dom';
```

## Core Querying Principles

Query by **role, label, text** — never by CSS class or data-testid (use those as last resort).

```js
// Priority order (most to least accessible-friendly)
screen.getByRole('button', { name: /submit/i })  // best
screen.getByLabelText(/email address/i)          // for form inputs
screen.getByPlaceholderText(/search/i)           // fallback
screen.getByText(/welcome/i)                     // text content
screen.getByDisplayValue('John')                 // current input value
screen.getByTestId('custom-element')             // last resort

// Async queries
await screen.findByText('Loaded data')           // waits for appearance
screen.queryByText('Error')                      // returns null if not found (use for assertions)
```

## Component Tests

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Basic render test
test('displays user name and email', () => {
  render(<UserCard name="Alice Mwangi" email="alice@example.com" onSelect={jest.fn()} />);
  expect(screen.getByText('Alice Mwangi')).toBeInTheDocument();
  expect(screen.getByText('alice@example.com')).toBeInTheDocument();
});

// Interaction test
test('calls onSelect with email when card clicked', async () => {
  const user = userEvent.setup();
  const onSelect = jest.fn();
  render(<UserCard name="Alice" email="alice@example.com" onSelect={onSelect} />);

  await user.click(screen.getByRole('article'));  // or getByText('Alice')
  expect(onSelect).toHaveBeenCalledTimes(1);
  expect(onSelect).toHaveBeenCalledWith('alice@example.com');
});

// Form interaction test
test('validates and submits login form', async () => {
  const user = userEvent.setup();
  const onSubmit = jest.fn();
  render(<LoginForm onSubmit={onSubmit} />);

  // Type invalid email
  await user.type(screen.getByLabelText(/email/i), 'notvalid');
  await user.click(screen.getByRole('button', { name: /log in/i }));
  expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
  expect(onSubmit).not.toHaveBeenCalled();

  // Fix and submit
  await user.clear(screen.getByLabelText(/email/i));
  await user.type(screen.getByLabelText(/email/i), 'alice@example.com');
  await user.type(screen.getByLabelText(/password/i), 'password123');
  await user.click(screen.getByRole('button', { name: /log in/i }));
  expect(onSubmit).toHaveBeenCalledWith({ email: 'alice@example.com', password: 'password123' });
});

// Keyboard interaction
test('closes modal on Escape', async () => {
  const user = userEvent.setup();
  const onClose = jest.fn();
  render(<Modal isOpen onClose={onClose}><p>Content</p></Modal>);

  await user.keyboard('{Escape}');
  expect(onClose).toHaveBeenCalled();
});
```

## Async Tests (Data Fetching)

```jsx
// Mock fetch
beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});

test('fetches and renders user list', async () => {
  const mockUsers = [
    { id: 1, name: 'Alice', email: 'alice@example.com' },
    { id: 2, name: 'Bob',   email: 'bob@example.com' },
  ];
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve(mockUsers),
  });

  render(<UserListContainer />);

  // Loading state
  expect(screen.getByText(/loading/i)).toBeInTheDocument();

  // Data loaded
  await waitFor(() => {
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
  });

  expect(global.fetch).toHaveBeenCalledWith('/api/users');
});

test('shows error message on fetch failure', async () => {
  global.fetch.mockRejectedValueOnce(new Error('Network error'));
  render(<UserListContainer />);
  await waitFor(() => expect(screen.getByText(/network error/i)).toBeInTheDocument());
});

// Using MSW (Mock Service Worker) for integration tests
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(ctx.json([{ id: 1, name: 'Alice' }]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Testing Custom Hooks

```jsx
import { renderHook, act } from '@testing-library/react';

test('useCounter increments and decrements', () => {
  const { result } = renderHook(() => useCounter(5));

  expect(result.current.count).toBe(5);

  act(() => result.current.increment());
  expect(result.current.count).toBe(6);

  act(() => result.current.decrement());
  expect(result.current.count).toBe(5);
});

test('useDebounce delays value update', async () => {
  jest.useFakeTimers();
  const { result, rerender } = renderHook(({ v }) => useDebounce(v, 300), {
    initialProps: { v: 'hello' },
  });

  expect(result.current).toBe('hello');
  rerender({ v: 'world' });
  expect(result.current).toBe('hello');  // not updated yet

  act(() => jest.advanceTimersByTime(300));
  expect(result.current).toBe('world');  // now updated
  jest.useRealTimers();
});

// Hook with context dependency
test('useAuth returns user from provider', () => {
  const wrapper = ({ children }) => (
    <AuthProvider initialUser={{ id: 1, name: 'Alice' }}>{children}</AuthProvider>
  );
  const { result } = renderHook(() => useAuth(), { wrapper });
  expect(result.current.user.name).toBe('Alice');
});
```

## Testing Context Providers

```jsx
// Test utility — wrap component with all required providers
function renderWithProviders(ui, { initialState = {}, ...options } = {}) {
  function Wrapper({ children }) {
    return (
      <AuthProvider>
        <ThemeProvider>
          <QueryClientProvider client={new QueryClient()}>
            {children}
          </QueryClientProvider>
        </ThemeProvider>
      </AuthProvider>
    );
  }
  return render(ui, { wrapper: Wrapper, ...options });
}

test('Dashboard renders for authenticated user', async () => {
  renderWithProviders(<Dashboard />, { initialState: { user: { id: 1 } } });
  expect(await screen.findByText('Welcome back')).toBeInTheDocument();
});
```

## Testing Error Boundaries

```jsx
// Suppress console.error for expected errors
const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

test('renders fallback on render error', () => {
  function BrokenComponent() { throw new Error('Oops!'); }

  render(
    <ErrorBoundary fallback={<p>Something went wrong.</p>}>
      <BrokenComponent />
    </ErrorBoundary>
  );

  expect(screen.getByText('Something went wrong.')).toBeInTheDocument();
  consoleSpy.mockRestore();
});
```

## Snapshot Testing (Use Sparingly)

```jsx
// Good for: static UI components, design system components
test('Button snapshot — primary variant', () => {
  const { container } = render(<Button variant="primary">Save</Button>);
  expect(container.firstChild).toMatchSnapshot();
});
// Run: jest --updateSnapshot to update after intentional changes
```

## Best Practices

- Write tests that resemble how users use the app (behaviour, not implementation)
- Avoid testing internal state — test visible output
- One logical assertion per test (can have multiple `expect` calls in one flow test)
- Use `userEvent` over `fireEvent` for realistic interaction simulation
- Mock at the network layer (MSW) rather than mocking React components
- Aim for: many unit tests, fewer integration tests, minimal E2E tests
- Never test implementation details (internal state, component method names)
