# Supabase + Row-Level Security

Supabase wraps PostgreSQL + pgvector + auth + realtime + storage as a managed service. The engine treats it as the managed alternative for greenfield AI projects. Self-managed PostgreSQL on Debian/Ubuntu remains the default deployment shape for teams comfortable with PG ops.

Supabase position (supabase.com/docs/guides/ai): "The best vector database is the database you already have."

## Enable RLS on every tenant-scoped table

Verbatim policy syntax from supabase.com/docs/guides/auth/row-level-security:

```sql
alter table <schema_name>.<table_name> enable row level security;

create policy "User can see their own profile only."
on profiles
for select using ( (select auth.uid()) = user_id );

create policy "Users can create a profile."
on profiles for insert
to authenticated
with check ( (select auth.uid()) = user_id );
```

## Apply the same shape to embeddings

```sql
alter table embeddings enable row level security;

create policy "tenant_isolation_select" on embeddings
  for select using ( tenant_id = (select auth.jwt() ->> 'tenant_id')::bigint );

create policy "tenant_isolation_insert" on embeddings
  for insert to authenticated
  with check ( tenant_id = (select auth.jwt() ->> 'tenant_id')::bigint );

create policy "tenant_isolation_update" on embeddings
  for update to authenticated
  using ( tenant_id = (select auth.jwt() ->> 'tenant_id')::bigint )
  with check ( tenant_id = (select auth.jwt() ->> 'tenant_id')::bigint );

create policy "tenant_isolation_delete" on embeddings
  for delete to authenticated
  using ( tenant_id = (select auth.jwt() ->> 'tenant_id')::bigint );
```

Notes:

- The four policies (select, insert, update, delete) must all exist; missing one silently denies that operation for non-superusers, but missing one and granting wide privilege via roles is the typical bug.
- Cast the JWT claim to the same type as the column (`bigint`, `uuid`, etc.). A type mismatch produces a runtime error or a silently empty result depending on the operator.
- The `select` in `(select auth.uid())` is a Supabase performance idiom that lets the planner cache the subquery.

## supabase-js + pgvector

The supabase-js query builder does not natively understand pgvector operators. Wrap vector queries in a SQL function and call it via `supabase.rpc()`.

```sql
create or replace function match_embeddings(
  query_embedding vector(1536),
  match_count int,
  tenant bigint
) returns table (id bigint, source_id bigint, similarity float)
language sql stable as $$
  select id, source_id, 1 - (embedding <=> query_embedding) as similarity
  from embeddings
  where tenant_id = tenant
  order by embedding <=> query_embedding
  limit match_count;
$$;
```

```ts
const { data, error } = await supabase.rpc('match_embeddings', {
  query_embedding: queryVector,
  match_count: 10,
  tenant: tenantId,
});
```

The RPC inherits RLS, so the function should be `security invoker` (the default) and rely on the calling user's policies. Use `security definer` only when you intentionally need to bypass RLS, and constrain it tightly with `set search_path = public`.

## Operational considerations

- Supabase's free tier suspends idle projects. Production workloads need a paid plan.
- Connection counts on Supabase are capped per plan; place the application behind PgBouncer (Supabase ships its own pooler at port 6543) and use transaction pooling for serverless functions.
- The Supabase service role key bypasses RLS. Treat it like a database root password: never ship it to the browser.
