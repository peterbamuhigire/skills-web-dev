# Security Baseline

Expands the **Security baseline** section of `SKILL.md`. Covers secrets handling, parameterised SQL, input validation, dependency scanning, SAST, and concrete before/after rewrites of the most common unsafe patterns.

## Scope

This is the Python-side minimum. For web-app-level concerns (CSRF, session cookies, CSP headers) also load `vibe-security-skill`. For AI-integration concerns (prompt injection, PII scrubbing) also load `llm-security` / `ai-security`.

## Secrets handling

Rules:

- Secrets come from environment variables, loaded via `pydantic-settings`.
- `os.environ[...]` outside `config.py` is forbidden.
- Secrets that appear in logs are a security incident. Use `SecretStr` and log `settings.secret.get_secret_value()` only when strictly necessary.
- Never commit `.env` files. Commit `.env.example` with dummy values.
- Never hardcode secrets in tests. Use fixtures that inject test values.

```python
# GOOD
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    stripe_api_key: SecretStr
    internal_shared_secret: SecretStr

settings = Settings()
# usage:
headers = {"Authorization": f"Bearer {settings.stripe_api_key.get_secret_value()}"}
```

```python
# BAD — hardcoded, logged in cleartext
API_KEY = "sk_live_abcdef123456"
logger.info("calling stripe", key=API_KEY)
```

## Parameterised SQL

Never build SQL with f-strings or `%` formatting on user input. Use parameter binding everywhere.

### SQLAlchemy Core / ORM — safe by default

```python
# GOOD
from sqlalchemy import select
stmt = select(Invoice).where(Invoice.tenant_id == tenant_id, Invoice.status == status)
rows = session.execute(stmt).scalars().all()

# GOOD (raw SQL through text() with bound params)
from sqlalchemy import text
stmt = text("SELECT * FROM invoices WHERE tenant_id = :tid AND status = :s")
rows = session.execute(stmt, {"tid": tenant_id, "s": status}).fetchall()
```

### Raw DB-API — cursor.execute with params

```python
# GOOD
cursor.execute(
    "INSERT INTO audit_log (tenant_id, action, data) VALUES (%s, %s, %s)",
    (tenant_id, action, json.dumps(data)),
)
```

### Unsafe patterns — before/after

```python
# BAD — SQL injection
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
cursor.execute("SELECT * FROM users WHERE email = '%s'" % email)
session.execute(text(f"DELETE FROM invoices WHERE tenant_id = {tenant_id}"))

# GOOD
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
session.execute(
    text("DELETE FROM invoices WHERE tenant_id = :tid"),
    {"tid": tenant_id},
)
```

### Dynamic identifiers

Column / table names cannot be bound as parameters. Validate against a whitelist:

```python
ALLOWED_SORT = {"created_at", "amount", "status"}

def list_invoices(sort_by: str) -> list[Invoice]:
    if sort_by not in ALLOWED_SORT:
        raise ValidationError(f"invalid sort: {sort_by}")
    stmt = text(f"SELECT * FROM invoices ORDER BY {sort_by}")
    return session.execute(stmt).scalars().all()
```

## Input validation at every boundary

Every external payload (HTTP body, query string, queue message, webhook, file upload) is validated by a Pydantic model before the domain sees it. This is the single biggest security lever Python gives you.

```python
# GOOD
from fastapi import APIRouter
from pydantic import BaseModel, Field, EmailStr

class CreateUserIn(BaseModel):
    model_config = {"extra": "forbid"}
    email: EmailStr
    tenant_id: int = Field(..., gt=0)
    role: Literal["admin", "user", "viewer"]

@router.post("/users")
async def create_user(body: CreateUserIn) -> UserOut:
    return await user_service.create(body)
```

Rules:

- `extra="forbid"` catches unknown fields — prevents mass-assignment vulnerabilities.
- Use `Literal` or `Enum` for status-like fields; don't accept a free-form string.
- `Field(..., max_length=...)` everywhere you accept a string; unbounded strings are a DoS vector.
- Validate filenames, URLs, paths with specific types (`AnyHttpUrl`, not `str`).

## Path traversal — safe filesystem access

```python
from pathlib import Path

UPLOAD_ROOT = Path("/var/app/uploads").resolve()

def save_upload(tenant_id: int, filename: str, data: bytes) -> Path:
    # Never trust filename. Normalise and confirm it stays inside UPLOAD_ROOT.
    safe_name = Path(filename).name      # strips any ../
    target = (UPLOAD_ROOT / str(tenant_id) / safe_name).resolve()
    if not target.is_relative_to(UPLOAD_ROOT):
        raise ValidationError("invalid filename")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target
```

## eval, exec, pickle — forbidden with untrusted input

Never. Not for quick prototypes, not for "it's internal only".

```python
# BAD
data = eval(request.body)                 # RCE
func = globals()[user_input](arg)          # attacker-controlled function call
obj = pickle.loads(queue_message)          # RCE via crafted pickle

# GOOD
data = json.loads(request.body)
obj = MyModel.model_validate_json(queue_message)
```

Exception: you may use `pickle` for data you have produced and sealed (e.g. an internal cache keyed by an HMAC). Even then, `orjson` or a Pydantic model is usually safer.

## Subprocess — never shell=True with user data

```python
# BAD — command injection
subprocess.run(f"convert {filename} output.pdf", shell=True)
subprocess.run("convert " + filename + " output.pdf", shell=True)

# GOOD — argv list, no shell
subprocess.run(
    ["convert", filename, "output.pdf"],
    check=True,
    timeout=30,
    capture_output=True,
)
```

Extra rules:

- Always set `timeout=`. A stuck subprocess holds a thread forever.
- Always `check=True` unless you explicitly handle the return code.
- Validate `filename` against a whitelist of allowed extensions before passing to the binary.

## Deserialising from trusted sources only

YAML has the same `pickle` problem with `yaml.load`. Use `yaml.safe_load` (loads only primitive types).

```python
# BAD
cfg = yaml.load(payload, Loader=yaml.Loader)

# GOOD
cfg = yaml.safe_load(payload)
```

## Cryptography — use `secrets`, not `random`

```python
# BAD — not cryptographically secure
import random
token = "".join(random.choices(string.ascii_letters, k=32))

# GOOD
import secrets
token = secrets.token_urlsafe(32)
```

For password hashing use `passlib[argon2]` or `bcrypt`. Never SHA256. Never MD5.

## Comparing secrets — use `hmac.compare_digest`

```python
import hmac

# GOOD — constant-time comparison
if hmac.compare_digest(provided_signature, expected_signature):
    accept()
```

Regular `==` on strings is short-circuit and leaks length information through timing.

## Dependency scanning

`pip-audit` runs weekly and on PRs. It reads `uv.lock` and checks the OSV database.

```bash
uv run pip-audit --strict            # fails the build if any CVE is found
uv run pip-audit --ignore-vuln GHSA-xxxx-yyyy-zzzz   # explicit exception with reason in CHANGELOG
```

Add to CI. Respond to findings:

- Critical or High: patch within 72 hours.
- Medium: patch within 2 weeks, or document risk acceptance.
- Low: next normal dependency bump.

`safety` is an alternative; pick one and stick with it.

## SAST — ruff S rules and semgrep

Ruff's `S` rule set (bandit) runs on every commit. It catches the big ones: `eval`, `pickle.loads`, `shell=True`, hardcoded passwords, `assert_used`, weak crypto.

Exceptions via per-file ignores:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]      # asserts are fine in tests
"scripts/*" = ["S603", "S607"]   # subprocess without shell, checked separately
```

For deeper scanning, `semgrep` with the `p/python` and `p/security-audit` rule packs. Run weekly in CI. Do not block PRs on it — signal is low on a first pass. Triage results into tickets.

## Authentication and authorisation boundaries

At the HTTP boundary:

- All authenticated endpoints depend on a single `Depends(current_user)` or similar that raises `AuthenticationError` / `AuthorizationError`.
- Authorisation checks happen in the use-case layer, not at the top of the handler. The handler confirms the caller is authenticated; the use-case enforces "this tenant can do this".
- Tenant isolation: every query filters by `tenant_id`. Use a typed `TenantId = NewType("TenantId", int)` so mypy catches mismatches (see `typing-mypy-pyright.md`).
- Never accept `tenant_id` from the client body. Take it from the authenticated session.

## Logging security events

Log every:

- Failed authentication attempt (with anonymised identifier).
- Authorisation denial (with actor and attempted resource).
- Rate-limit hit.
- Configuration error at startup.

Do not log:

- Passwords, tokens, session IDs, full cookies, card numbers.
- Full webhook bodies from payment processors without redacting sensitive keys.

See `logging-structlog.md` for the `redact_sensitive` processor pattern.

## Rate limiting

Every public endpoint has a rate limit. For FastAPI we use `slowapi` or reverse-proxy-level limits (nginx, Cloudflare). Internal-to-internal RPC calls use an HMAC-shared-secret header plus an IP allow-list.

## Session / token handling

- JWTs signed with `HS256` and a secret from settings, or `RS256` with a key pair. Never `none`.
- Short expiry (15 min for access tokens; refresh tokens rotated per use).
- Store refresh tokens in the DB so they can be revoked.
- Compare token signatures with `hmac.compare_digest`.

## File upload handling

- Enforce max size at the web server (nginx `client_max_body_size`) and in the app.
- Validate extension against a whitelist; verify content-type; sniff magic bytes for binary formats.
- Store in a directory that the web server does not execute from.
- Generate new filenames — never trust the uploaded name.

## Concrete before/after — everything in one place

```python
# BAD
@app.get("/search")
def search(q: str):
    cursor.execute(f"SELECT * FROM posts WHERE body LIKE '%{q}%'")
    return cursor.fetchall()

# GOOD
class SearchIn(BaseModel):
    q: str = Field(..., min_length=1, max_length=100)

@app.get("/search")
def search(params: SearchIn = Depends()) -> list[Post]:
    stmt = text("SELECT * FROM posts WHERE body LIKE :q")
    rows = session.execute(stmt, {"q": f"%{params.q}%"}).fetchall()
    return [Post.model_validate(r) for r in rows]
```

```python
# BAD
subprocess.run(f"wkhtmltopdf {url} {out}", shell=True)

# GOOD
subprocess.run(
    ["wkhtmltopdf", url, str(out)],
    check=True, timeout=60, capture_output=True,
)
```

```python
# BAD
raw = request.body
obj = pickle.loads(raw)

# GOOD
obj = MyModel.model_validate_json(request.body)
```

## Cross-references

- Web-app security (headers, CSRF, cookies): `vibe-security-skill`, `php-security` (for the PHP side of the stack).
- AI-specific security: `ai-security`, `llm-security`.
- Anti-patterns: `anti-patterns.md`.
- CI gates: `tooling-uv-ruff.md`.
