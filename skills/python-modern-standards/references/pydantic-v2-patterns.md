# Pydantic v2 Patterns

Expands the **Pydantic v2** section of `SKILL.md`. Covers models, field validators, model validators, serialization, settings, discriminated unions, and performance notes.

## Version discipline

Pydantic v2 only. Pydantic v1 is end-of-life and its API (`@validator`, `Config` class, `.dict()`) is forbidden in new code. Migrate legacy code at touch-time.

Use `pydantic >= 2.9` (2.11+ preferred). Install the settings add-on separately:

```bash
uv add "pydantic>=2.9" "pydantic-settings>=2.5"
```

## Basic model

```python
from datetime import datetime, UTC
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class InvoiceCreate(BaseModel):
    model_config = ConfigDict(
        frozen=True,          # immutable once built
        extra="forbid",       # unknown fields raise instead of silently dropping
        str_strip_whitespace=True,
        str_min_length=1,
    )

    tenant_id: int = Field(..., gt=0)
    customer_email: EmailStr
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(..., pattern=r"^[A-Z]{3}$")
    due_date: datetime
    notes: str | None = Field(default=None, max_length=500)
```

`model_config` is the replacement for v1's `Config` class. `ConfigDict` is typed and picked up by mypy/pyright.

## Field validators

Field validators run on a single field's value. Use `mode="before"` to normalise input, `mode="after"` to enforce invariants on the parsed value.

```python
from pydantic import BaseModel, field_validator

class ProductCode(BaseModel):
    value: str

    @field_validator("value", mode="before")
    @classmethod
    def upper_and_strip(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("value", mode="after")
    @classmethod
    def check_format(cls, v: str) -> str:
        if not v.isalnum() or len(v) < 4:
            raise ValueError("must be 4+ alphanumeric chars")
        return v
```

Rules:

- Always mark as `@classmethod`. Pydantic v2 requires it.
- `mode="before"` sees the raw input (might be any type). Type hints are honoured but runtime coercion can differ.
- `mode="after"` sees the parsed value. Use this for business invariants.
- Prefer `Field(...)` constraints (`gt`, `pattern`, `max_length`) over validators when they suffice — they produce better error messages and are cheaper.

## Model validators — cross-field checks

Use `@model_validator` when validation depends on more than one field.

```python
from pydantic import BaseModel, model_validator
from typing import Self

class DateRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def check_order(self) -> Self:
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self
```

`mode="after"` gives a fully built instance. `mode="before"` gives a raw dict — use only when you need to mutate one field based on another before parsing.

## Serialization

Pydantic v2 serialization is method-based and typed.

```python
invoice = InvoiceCreate(tenant_id=1, customer_email="user@example.com", ...)

invoice.model_dump()             # dict, native types
invoice.model_dump(mode="json")  # dict, JSON-safe (Decimal -> str, datetime -> ISO)
invoice.model_dump_json()        # str, JSON payload
invoice.model_dump(exclude={"notes"})
invoice.model_dump(exclude_none=True)
invoice.model_dump(by_alias=True)

# parsing
InvoiceCreate.model_validate(some_dict)
InvoiceCreate.model_validate_json(some_json_str)
```

Never use the v1 methods (`.dict()`, `.json()`, `parse_obj`, `parse_raw`). They emit deprecation warnings and are slower.

### Custom serializers

Use when the default representation is wrong for your API contract.

```python
from pydantic import field_serializer

class Money(BaseModel):
    amount: Decimal
    currency: str

    @field_serializer("amount")
    def amount_as_str(self, v: Decimal) -> str:
        # Stripe / Decimal-safe JSON: always emit as string
        return format(v, "f")
```

## Settings management — pydantic-settings

`BaseSettings` loads values from env vars, `.env` files, and secret files in that order. All validation features of `BaseModel` are available.

```python
from pathlib import Path
from pydantic import Field, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",              # tolerate unrelated env vars
        case_sensitive=False,
        env_nested_delimiter="__",   # DATABASE__POOL_SIZE -> database.pool_size
    )

    environment: str = Field(default="development", pattern=r"^(development|staging|production)$")
    database_url: PostgresDsn
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")
    php_app_base_url: str
    internal_shared_secret: SecretStr = Field(..., min_length=32)
    log_level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR)$")

settings = Settings()  # fails fast on import if invalid
```

Rules:

- Instantiate once at module import, export as `settings`. Never re-read env vars downstream.
- Use `SecretStr` for anything sensitive so `repr()` doesn't leak. Extract with `.get_secret_value()` at the point of use.
- Use `PostgresDsn` / `RedisDsn` / `AnyHttpUrl` / `AmqpDsn` for URLs — they validate shape and are typed.
- The `extra="ignore"` allows adding env vars in the runtime without breaking the service.

## Discriminated unions

When one field determines the shape of the rest of the model, use a discriminated union. Pydantic picks the right variant fast, without trying them all.

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field, TypeAdapter

class EmailEvent(BaseModel):
    kind: Literal["email"]
    recipient: EmailStr
    subject: str

class SmsEvent(BaseModel):
    kind: Literal["sms"]
    phone: str
    body: str = Field(..., max_length=160)

class PushEvent(BaseModel):
    kind: Literal["push"]
    device_token: str
    title: str

NotificationEvent = Annotated[
    EmailEvent | SmsEvent | PushEvent,
    Field(discriminator="kind"),
]

# Use a TypeAdapter to parse bare union types outside of a containing model
adapter = TypeAdapter(NotificationEvent)
event = adapter.validate_python({"kind": "email", "recipient": "u@x.com", "subject": "Hi"})
```

Useful for queue payloads, webhook events, and tagged messages. Parsing is O(1) on the number of variants.

## Parsing many items — TypeAdapter

`TypeAdapter` is the escape hatch for parsing lists, dicts, or union types without wrapping them in a model. Cache it at module scope.

```python
from pydantic import TypeAdapter

_invoice_list_adapter = TypeAdapter(list[InvoiceCreate])

def load_invoices(raw_json: str) -> list[InvoiceCreate]:
    return _invoice_list_adapter.validate_json(raw_json)
```

## Computed fields

```python
from pydantic import computed_field

class LineItem(BaseModel):
    quantity: int = Field(..., gt=0)
    unit_price: Decimal

    @computed_field
    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price
```

`@computed_field` appears in `model_dump()` and schema output, unlike plain `@property`.

## Integrating with SQLAlchemy

Pydantic v2 plays well with SQLAlchemy 2.0 via `model_config = ConfigDict(from_attributes=True)` (was `orm_mode`).

```python
class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    amount: Decimal
    status: str

# In a FastAPI handler:
invoice_row = session.get(Invoice, invoice_id)
return InvoiceOut.model_validate(invoice_row)
```

## Performance notes — v2 vs v1

Pydantic v2 is roughly 5–50x faster than v1 because the core is in Rust (pydantic-core). A few specific gotchas:

- `model_validate` is much faster than v1's `parse_obj`. Use it.
- `Literal` and discriminated unions are nearly free. Prefer them over dynamic type checks.
- `strict=True` on `Field` disables implicit coercion (`"1"` -> `1`). Use for payloads coming from trusted sources; keep loose for user input where coercion is a feature.
- `@field_validator(..., mode="after")` with classmethod lookup is a cache hit on the model class — not a per-instance overhead.
- Avoid `arbitrary_types_allowed=True` except as a last resort. It opts out of validation and serialisation for that field.

## Anti-patterns

- Using v1 syntax (`@validator`, `.dict()`, `Config` class) — forbidden.
- Using `BaseModel` with `extra="allow"` as a silent dict container — that's what TypedDict or `dict[str, Any]` is for.
- Deriving a Pydantic model from a SQLAlchemy model and hoping it will be coherent — separate DTO from ORM model always, even if they mirror each other.
- Calling `.model_dump()` just to reconstruct a dict for another model — pass the model instance instead, or use `model_validate(other.model_dump())` only across module boundaries where coupling is undesirable.
- Mutating a frozen model — convert with `model.model_copy(update={...})`.

## Cross-references

- Config loading: see Settings section above, plus `SKILL.md` main file.
- Boundary validation rule: `security-baseline.md`.
- FastAPI integration: `python-saas-integration` skill.
- Serialisation with logging: `logging-structlog.md`.
