# JSONB and Full-Text Search

Deep reference for sections 3 and 4 of `SKILL.md`.

## JSONB operators (full table)

Source: postgresql.org/docs/current/datatype-json.html.

| Operator | Returns | Meaning |
|---|---|---|
| `->` | jsonb | Extract field as JSONB |
| `->>` | text | Extract field as text |
| `#>` | jsonb | Extract path (text array) as JSONB |
| `#>>` | text | Extract path as text |
| `@>` | bool | Containment (left contains right) |
| `<@` | bool | Containment (right contains left) |
| `?` | bool | Top-level key exists |
| `?|` | bool | Any of the listed keys exists |
| `?&` | bool | All of the listed keys exist |
| `||` | jsonb | Concatenate |
| `-` | jsonb | Delete key or index |
| `#-` | jsonb | Delete at path |
| `@?` | bool | JSONPath returns any item |
| `@@` | bool | JSONPath predicate result |

## GIN operator classes

The default `jsonb_ops` class supports `?`, `?|`, `?&`, `@>`, `@?`, `@@`. The alternative `jsonb_path_ops` class is faster and smaller for containment-only workloads but does not support key-existence operators.

```sql
-- General-purpose
CREATE INDEX api_jdoc_gin ON api USING GIN (jdoc);

-- Containment-only, faster
CREATE INDEX api_jdoc_path_gin ON api USING GIN (jdoc jsonb_path_ops);
```

For a single-field access pattern, a B-tree expression index on `(jdoc->>'field')` outperforms GIN.

## JSONB vs relational decision table

| Need | Choice |
|---|---|
| Fixed schema, queryable by many fields, joins | Relational columns |
| Truly variable per-row schema (AI metadata, integration payloads, webhook envelopes) | JSONB column with GIN index on the access pattern |
| 1-to-many with fixed child shape | Child table |
| Storage of opaque blobs read whole | TEXT or BYTEA |

JSONB is not a substitute for normalisation. Reach for it only when the schema is genuinely heterogeneous across rows.

## Full-text search end-to-end

PostgreSQL FTS uses `tsvector` (lexeme-indexed normalised document) and `tsquery` (normalised query). Match operator `@@`. Source: postgresql.org/docs/current/textsearch-intro.html.

Production pattern:

```sql
ALTER TABLE articles
  ADD COLUMN search_doc tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
    setweight(to_tsvector('english', coalesce(body,'')),  'B')
  ) STORED;

CREATE INDEX articles_search_gin ON articles USING GIN (search_doc);

SELECT id, ts_rank_cd(search_doc, q) AS rank
FROM articles, websearch_to_tsquery('english', 'database postgres') q
WHERE search_doc @@ q
ORDER BY rank DESC LIMIT 10;
```

Notes:

- `setweight()` lets ranking favour title matches over body matches.
- `websearch_to_tsquery` accepts user-style input (quoted phrases, `OR`, `-`) safely; prefer it over hand-built `tsquery` strings for end-user search boxes.
- Stemming dictionary is per language. Pick the right config (`english`, `french`, `simple`) at index time and at query time.
- For multi-language documents, store the language alongside the row and use a CASE expression in the generated column.

## When to choose external search instead

PostgreSQL FTS is excellent up to roughly 10M rows on a well-tuned single host. Beyond that, or when the workload needs faceted search, typo tolerance with edit-distance matching, or per-user relevance models, move search to Elasticsearch, OpenSearch, or Meilisearch and let PostgreSQL keep the source of truth.
