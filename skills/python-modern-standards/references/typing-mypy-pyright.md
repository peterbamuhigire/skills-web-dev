# Typing: mypy --strict and pyright

Expands the **Typing** section of `SKILL.md`. Covers the patterns we actually use in production: generics, Protocols, TypedDict, Literal, NewType, overloads, exhaustive checks, and the config snippets to make strict mode pleasant.

## The rule

Every function signature has types. No exceptions. If you cannot type something, stop and work out why — usually it is a design problem, not a typing problem.

Pick one type checker per project. mypy is the default. pyright is appropriate when the team already uses VS Code heavily and wants the editor feedback loop. Do not run both — their disagreements waste time.

## PEP 695 syntax (Python 3.12+)

Prefer the modern syntax. It reads better and removes the `TypeVar` declaration boilerplate.

```python
# GOOD (3.12+)
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None

# OLD (still works, but only use for 3.11 targets)
from typing import TypeVar
T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

## Generics

Use generics when the same function or class works identically over different types. Do not use generics when you actually mean "any object with method X" — that is a Protocol.

```python
from collections.abc import Callable, Iterable

def apply_to_each[T, U](items: Iterable[T], fn: Callable[[T], U]) -> list[U]:
    return [fn(item) for item in items]

class Repository[Entity]:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, id: int) -> Entity | None: ...
    def save(self, entity: Entity) -> None: ...

class InvoiceRepository(Repository[Invoice]):
    ...
```

Bound generics constrain the type parameter to a base class or Protocol:

```python
from decimal import Decimal

def total[T: (int, float, Decimal)](items: list[T]) -> T:
    return sum(items, start=type(items[0])(0))
```

## Protocols — structural typing

Protocols describe shape, not inheritance. Use them when multiple classes should share an interface without a common base class. Much lighter than ABCs.

```python
from typing import Protocol

class SupportsPublish(Protocol):
    def publish(self, topic: str, payload: bytes) -> None: ...

class RedisPublisher:
    def publish(self, topic: str, payload: bytes) -> None:
        ...  # RedisPublisher satisfies SupportsPublish without inheriting

def broadcast(publisher: SupportsPublish, events: list[Event]) -> None:
    for event in events:
        publisher.publish(event.topic, event.payload)
```

Use Protocols for dependency injection boundaries between domain and adapter layers. The domain defines the Protocol; the adapter implements it.

## TypedDict — typed JSON-ish dicts

Use TypedDict for data that arrives as `dict` and cannot be easily wrapped in a Pydantic model — typically third-party API responses you only peek at before handing off. For anything we construct ourselves, use Pydantic.

```python
from typing import TypedDict, NotRequired

class StripeCustomerPayload(TypedDict):
    id: str
    email: str
    name: NotRequired[str]          # optional field
    metadata: dict[str, str]

def extract_email(payload: StripeCustomerPayload) -> str:
    return payload["email"]
```

TypedDict does not validate at runtime. If you need validation, use Pydantic.

## Literal — constrained strings

Use `Literal` for small enumerations of string values. Prefer real `Enum` classes when the values are referenced in more than one place.

```python
from typing import Literal

Environment = Literal["development", "staging", "production"]

def log_level_for(env: Environment) -> str:
    return "DEBUG" if env == "development" else "INFO"
```

## NewType — semantic aliases

`NewType` gives the type checker a way to stop you passing the wrong kind of `int` or `str`. Cheap, invisible at runtime, catches whole classes of bugs.

```python
from typing import NewType

TenantId = NewType("TenantId", int)
UserId = NewType("UserId", int)

def invoices_for_tenant(tenant_id: TenantId) -> list[Invoice]: ...

user = UserId(42)
invoices_for_tenant(user)  # mypy error: expected TenantId, got UserId
```

Use for: IDs, tokens, tenant-scoped handles, anything you want the type checker to track across a codebase.

## Overloads — function signatures that differ by argument

Use overloads when a function returns a different type depending on its inputs. Keep overload count to 3 or fewer; more than that is a code smell.

```python
from typing import overload

@overload
def parse_value(raw: str, *, as_type: type[int]) -> int: ...
@overload
def parse_value(raw: str, *, as_type: type[Decimal]) -> Decimal: ...
@overload
def parse_value(raw: str, *, as_type: type[bool]) -> bool: ...

def parse_value(raw: str, *, as_type: type) -> int | Decimal | bool:
    if as_type is bool:
        return raw.lower() in {"1", "true", "yes"}
    return as_type(raw)
```

## Exhaustive matching with `assert_never`

When matching on an `Enum` or Literal, add a `case _:` branch that hits `assert_never` so mypy complains if a new variant is added and you forget to handle it.

```python
from enum import Enum
from typing import assert_never

class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"

def human_label(status: PaymentStatus) -> str:
    match status:
        case PaymentStatus.PENDING:
            return "Pending"
        case PaymentStatus.SUCCEEDED:
            return "Paid"
        case PaymentStatus.FAILED:
            return "Failed"
        case PaymentStatus.REFUNDED:
            return "Refunded"
        case _ as unreachable:
            assert_never(unreachable)   # mypy enforces exhaustiveness here
```

## TYPE_CHECKING — break import cycles

`TYPE_CHECKING` is `False` at runtime and `True` when mypy is analysing. Use it to import types that would cause a runtime cycle.

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from service_name.domain.invoicing import Invoice

def report(invoice: Invoice) -> str: ...
```

`from __future__ import annotations` at the top of every module that uses forward references makes all annotations lazy — a free performance win on import time.

## final and Final

`Final` prevents reassignment of a variable. `@final` prevents overriding a method or subclassing a class. Use them to lock down invariants.

```python
from typing import Final, final

MAX_RETRIES: Final = 5

@final
class Settings: ...        # subclassing is forbidden
```

## dataclasses + frozen

Use `@dataclass(frozen=True, slots=True, kw_only=True)` for internal value objects that do not need Pydantic's validation. They are cheaper than Pydantic models and are perfectly typed.

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True, kw_only=True)
class Money:
    amount: Decimal
    currency: str
```

Use Pydantic when the data crosses an external boundary. Use `@dataclass` when it lives entirely inside the process.

## mypy strict config (recommended)

The defaults in the `pyproject.toml` in `project-layout.md` are a good starting point. Tweak these when friction appears:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]

# Relax in places where strict mode adds noise without catching bugs:
disallow_any_explicit = false     # allow explicit Any for dynamic third-party APIs
warn_return_any = true
warn_unused_ignores = true
warn_redundant_casts = true
enable_error_code = [
    "possibly-undefined",
    "redundant-expr",
    "unused-awaitable",
]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disable_error_code = ["no-untyped-def"]

[[tool.mypy.overrides]]
module = ["third_party_without_stubs.*"]
ignore_missing_imports = true
```

## pyright alternative

pyright (the engine behind Pylance) is stricter by default, faster on large codebases, and has better inference around conditional imports. Use when the team lives in VS Code.

```toml
# pyproject.toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "strict"
include = ["src"]
exclude = ["**/migrations"]
reportMissingTypeStubs = false
reportPrivateUsage = "warning"
```

Differences from mypy to watch for:

- pyright infers `Self` more aggressively — some decorators that mypy needs explicit help with just work.
- pyright reports unused `# type: ignore` differently. Run it in CI and read the first 20 errors, not the last.
- pyright can warn on `unknown` types leaking from untyped third-party code; silence with targeted `# pyright: ignore[reportUnknownMemberType]` comments, not with globally disabled rules.

## When typing hurts

Sometimes strict mode fights you:

- Decorators that change function signatures. Use `ParamSpec` and `Concatenate` (PEP 612). If the decorator mutates return types, accept a small amount of `Any` inside the decorator's body.
- SQLAlchemy 2.0 model typing is good but verbose. Use `Mapped[int]` consistently and the `pydantic.mypy` plugin for FastAPI ergonomics.
- pandas: cast at the boundary. Inside a data pipeline, the cost of fully typing DataFrames outweighs the benefit. Convert to Pydantic models or dataclasses before anything leaves the pipeline.

## Cross-references

- Pydantic v2 models: `pydantic-v2-patterns.md`.
- Exception hierarchy types: `error-handling.md`.
- `asyncio.to_thread` typing: `async-vs-sync.md`.
- Companion skill: `typescript-mastery` covers the same concepts for TS.
