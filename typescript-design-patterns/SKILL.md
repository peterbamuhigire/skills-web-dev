---
name: typescript-design-patterns
description: All 23 GoF design patterns implemented in TypeScript — Creational (Singleton,
  Factory Method, Abstract Factory, Builder, Prototype, Object Pool), Structural (Adapter,
  Composite, Proxy, Flyweight, Bridge, Decorator, Facade), Behavioral (Strategy...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Design Patterns in TypeScript

<!-- dual-compat-start -->
## Use When

- All 23 GoF design patterns implemented in TypeScript — Creational (Singleton, Factory Method, Abstract Factory, Builder, Prototype, Object Pool), Structural (Adapter, Composite, Proxy, Flyweight, Bridge, Decorator, Facade), Behavioral (Strategy...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `typescript-design-patterns` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
All 23 GoF patterns + Object Pool. Use TypeScript interfaces and generics to make patterns type-safe and self-documenting.

---

## CREATIONAL — Object creation strategies

### 1. Singleton
**When:** Exactly one instance needed globally (logger, DB connection, config).
```typescript
class Logger {
  private static instance: Logger;
  private constructor() {}
  static getInstance(): Logger {
    if (!Logger.instance) Logger.instance = new Logger();
    return Logger.instance;
  }
  log(msg: string) { console.log(`[${new Date().toISOString()}] ${msg}`); }
}
const logger = Logger.getInstance(); // same instance everywhere
```

### 2. Factory Method
**When:** Subclasses decide which class to instantiate; client uses the abstract type.
```typescript
interface Document { open(): void; save(): void; }
class WordDocument implements Document {
  open()  { console.log('Opening Word doc'); }
  save()  { console.log('Saving Word doc'); }
}
class PdfDocument implements Document {
  open()  { console.log('Opening PDF'); }
  save()  { console.log('Saving PDF'); }
}
abstract class DocumentCreator {
  abstract createDocument(): Document;
  openDocument() { this.createDocument().open(); }
}
class WordCreator extends DocumentCreator {
  createDocument(): Document { return new WordDocument(); }
}
```

### 3. Abstract Factory
**When:** Create families of related objects that must be compatible (e.g., cross-platform UI).
```typescript
interface Button   { render(): void; }
interface Checkbox { render(): void; }

interface UIFactory { createButton(): Button; createCheckbox(): Checkbox; }

class WindowsFactory implements UIFactory {
  createButton():   Button   { return { render: () => console.log('Windows button') }; }
  createCheckbox(): Checkbox { return { render: () => console.log('Windows checkbox') }; }
}
class MacFactory implements UIFactory {
  createButton():   Button   { return { render: () => console.log('Mac button') }; }
  createCheckbox(): Checkbox { return { render: () => console.log('Mac checkbox') }; }
}
function renderUI(factory: UIFactory) {
  factory.createButton().render();
  factory.createCheckbox().render();
}
```

### 4. Builder
**When:** Constructing complex objects step-by-step; same construction process, different representations.
```typescript
interface Computer { cpu: string; ram: number; storage: number; gpu?: string; }

class ComputerBuilder {
  private computer: Partial<Computer> = {};
  setCPU(cpu: string)        { this.computer.cpu = cpu; return this; }
  setRAM(ram: number)        { this.computer.ram = ram; return this; }
  setStorage(gb: number)     { this.computer.storage = gb; return this; }
  setGPU(gpu: string)        { this.computer.gpu = gpu; return this; }
  build(): Computer          { return this.computer as Computer; }
}

const pc = new ComputerBuilder()
  .setCPU('Intel i9').setRAM(32).setStorage(1000).setGPU('RTX 4090').build();
```

### 5. Prototype
**When:** Clone existing objects without coupling to their concrete classes.
```typescript
interface Cloneable<T> { clone(): T; }

class ProductConfig implements Cloneable<ProductConfig> {
  constructor(public name: string, public price: number, public tags: string[]) {}
  clone(): ProductConfig {
    return new ProductConfig(this.name, this.price, [...this.tags]);
  }
}

const base = new ProductConfig('Widget', 9.99, ['sale']);
const variant = base.clone();
variant.price = 12.99; // base unchanged
```

### 6. Object Pool
**When:** Expensive objects (DB connections, threads) — reuse instead of create/destroy.
```typescript
class ObjectPool<T> {
  private available: T[] = [];
  constructor(private factory: () => T, size: number) {
    for (let i = 0; i < size; i++) this.available.push(factory());
  }
  acquire(): T {
    return this.available.pop() ?? this.factory();
  }
  release(obj: T) { this.available.push(obj); }
}

// const pool = new ObjectPool(() => new DBConnection(), 5);
// const conn = pool.acquire();
// ... use conn ...
// pool.release(conn);
```

---

## Additional Guidance

Extended guidance for `typescript-design-patterns` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `STRUCTURAL — Composing objects and classes`
- `BEHAVIORAL — Object communication and responsibility`
- `Pattern Selection Guide`
