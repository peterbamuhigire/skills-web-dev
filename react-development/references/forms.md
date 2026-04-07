# Forms and Validation

## React Hook Form + Zod (Recommended for Production)

The standard combination for complex forms. RHF manages form state
without controlled inputs. Zod provides schema-based validation with
TypeScript type inference.

```bash
npm install react-hook-form zod @hookform/resolvers
```

### Basic Form

```tsx
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const loginSchema = z.object({
  email:    z.string().email('Invalid email'),
  password: z.string().min(8, 'Min 8 characters'),
});

type LoginValues = z.infer<typeof loginSchema>;

function LoginForm({ onSubmit }: { onSubmit: (v: LoginValues) => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} type="email" placeholder="Email" />
      {errors.email && <p className="text-red-500">{errors.email.message}</p>}

      <input {...register('password')} type="password" placeholder="Password" />
      {errors.password && <p className="text-red-500">{errors.password.message}</p>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Logging in…' : 'Log In'}
      </button>
    </form>
  );
}
```

### Complex Form with Nested Fields

```tsx
const userSchema = z.object({
  name:     z.string().min(2),
  email:    z.string().email(),
  age:      z.number().min(18).max(120),
  address:  z.object({
    street: z.string().min(1),
    city:   z.string().min(1),
  }),
  role:     z.enum(['admin', 'editor', 'viewer']),
  active:   z.boolean().default(true),
});

type UserForm = z.infer<typeof userSchema>;

function UserForm() {
  const { register, handleSubmit, watch, setValue, formState: { errors } } =
    useForm<UserForm>({
      resolver: zodResolver(userSchema),
      defaultValues: { active: true, role: 'viewer' },
    });

  return (
    <form onSubmit={handleSubmit(console.log)}>
      <input {...register('name')} />
      <input {...register('email')} type="email" />
      <input {...register('age', { valueAsNumber: true })} type="number" />

      {/* Nested */}
      <input {...register('address.street')} />
      <input {...register('address.city')} />

      <select {...register('role')}>
        <option value="admin">Admin</option>
        <option value="editor">Editor</option>
        <option value="viewer">Viewer</option>
      </select>

      <input {...register('active')} type="checkbox" />
      <button type="submit">Save</button>
    </form>
  );
}
```

### Dynamic Field Arrays

```tsx
import { useFieldArray } from 'react-hook-form';

const schema = z.object({
  tags: z.array(z.object({ value: z.string().min(1) })).min(1),
});

function TagsForm() {
  const { control, register, handleSubmit } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { tags: [{ value: '' }] },
  });
  const { fields, append, remove } = useFieldArray({ control, name: 'tags' });

  return (
    <form onSubmit={handleSubmit(console.log)}>
      {fields.map((field, i) => (
        <div key={field.id}>
          <input {...register(`tags.${i}.value`)} />
          <button type="button" onClick={() => remove(i)}>Remove</button>
        </div>
      ))}
      <button type="button" onClick={() => append({ value: '' })}>Add Tag</button>
      <button type="submit">Save</button>
    </form>
  );
}
```

### Watch and Conditional Fields

```tsx
function SignupForm() {
  const { register, watch, handleSubmit } = useForm<{
    role: string;
    adminCode: string;
  }>();

  const role = watch('role');

  return (
    <form onSubmit={handleSubmit(console.log)}>
      <select {...register('role')}>
        <option value="user">User</option>
        <option value="admin">Admin</option>
      </select>

      {role === 'admin' && (
        <input {...register('adminCode')} placeholder="Admin access code" />
      )}

      <button type="submit">Sign up</button>
    </form>
  );
}
```

---

## Zod Schema Patterns

```tsx
// Common validations
const schema = z.object({
  // String
  name:     z.string().min(2).max(50).trim(),
  email:    z.string().email(),
  url:      z.string().url().optional(),
  phone:    z.string().regex(/^\+?[\d\s-]{10,}$/, 'Invalid phone'),

  // Number
  price:    z.number().positive().multipleOf(0.01),
  quantity: z.number().int().min(0).max(999),

  // Date
  dob:      z.coerce.date().max(new Date(), 'Must be in the past'),

  // Enum
  status:   z.enum(['active', 'inactive', 'pending']),

  // Optional / nullable
  bio:      z.string().optional(),         // undefined is OK
  avatar:   z.string().nullable(),         // null is OK
  nickname: z.string().nullish(),          // null or undefined is OK

  // Boolean
  agree:    z.literal(true, { errorMap: () => ({ message: 'Must agree' }) }),
});

// Refinement (custom validation)
const passwordSchema = z.object({
  password: z.string().min(8),
  confirm:  z.string(),
}).refine(data => data.password === data.confirm, {
  message: 'Passwords must match',
  path: ['confirm'],  // error appears on 'confirm' field
});

// Transform on parse
const priceSchema = z.string().transform(v => parseFloat(v));
```

---

## Manual useState Forms (Simple Cases)

Use for simple 2–3 field forms where RHF overhead isn't justified.

```tsx
function QuickSearchForm({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim().length < 2) { setError('Min 2 characters'); return; }
    setError('');
    onSearch(query.trim());
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={query}
        onChange={e => { setQuery(e.target.value); setError(''); }}
        placeholder="Search…"
      />
      {error && <p>{error}</p>}
      <button type="submit">Search</button>
    </form>
  );
}
```

---

## Form UX Rules

- Show validation errors on blur (not on type) — use `mode: 'onBlur'` in RHF
- Keep submit button enabled; show errors after first submit attempt
- Use `aria-describedby` to link error messages to inputs for screen readers
- Never disable the submit button to communicate state — use loading indicator
- Clear errors immediately when the user corrects the field
