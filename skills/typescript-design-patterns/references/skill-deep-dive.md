# typescript-design-patterns Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

- `STRUCTURAL — Composing objects and classes`
- `BEHAVIORAL — Object communication and responsibility`
- `Pattern Selection Guide`

## STRUCTURAL — Composing objects and classes

### 7. Adapter
**When:** Make an incompatible interface work with existing code (legacy system integration).
```typescript
interface ModernLogger { logMessage(msg: string): void; }
class LegacyLogger { writeLog(text: string) { console.log('[LEGACY]', text); } }

class LoggerAdapter implements ModernLogger {
  constructor(private legacy: LegacyLogger) {}
  logMessage(msg: string) { this.legacy.writeLog(msg); }
}

const adapter = new LoggerAdapter(new LegacyLogger());
adapter.logMessage('Hello'); // uses legacy underneath
```

### 8. Composite
**When:** Treat individual objects and compositions uniformly (file systems, UI trees, menus).
```typescript
interface Graphic { render(): void; }
class Circle implements Graphic {
  render() { console.log('Drawing circle'); }
}
class GraphicGroup implements Graphic {
  private children: Graphic[] = [];
  add(g: Graphic) { this.children.push(g); }
  render() { this.children.forEach(c => c.render()); }
}

const group = new GraphicGroup();
group.add(new Circle());
group.add(new Circle());
group.render(); // renders all children
```

### 9. Proxy
**When:** Control access to another object — caching, logging, lazy init, access control.
```typescript
interface DataService { fetchData(id: string): string; }
class RealDataService implements DataService {
  fetchData(id: string): string { return `data:${id}`; }
}
class CachingProxy implements DataService {
  private cache = new Map<string, string>();
  constructor(private real: DataService) {}
  fetchData(id: string): string {
    if (!this.cache.has(id)) this.cache.set(id, this.real.fetchData(id));
    return this.cache.get(id)!;
  }
}
```

### 10. Flyweight
**When:** Share common state among many fine-grained objects to reduce memory (text formatting, game objects).
```typescript
class TextFormat {
  constructor(public font: string, public size: number, public color: string) {}
}
class FlyweightFactory {
  private formats = new Map<string, TextFormat>();
  getFormat(font: string, size: number, color: string): TextFormat {
    const key = `${font}-${size}-${color}`;
    if (!this.formats.has(key)) this.formats.set(key, new TextFormat(font, size, color));
    return this.formats.get(key)!;
  }
}
```

### 11. Bridge
**When:** Decouple abstraction from implementation so both can vary independently (device + remote).
```typescript
interface Renderer { renderCircle(radius: number): void; }
class SVGRenderer  implements Renderer { renderCircle(r: number) { console.log(`<circle r="${r}"/>`); } }
class CanvasRenderer implements Renderer { renderCircle(r: number) { console.log(`ctx.arc(0,0,${r})`); } }

abstract class Shape {
  constructor(protected renderer: Renderer) {}
  abstract draw(): void;
}
class Circle extends Shape {
  constructor(renderer: Renderer, private radius: number) { super(renderer); }
  draw() { this.renderer.renderCircle(this.radius); }
}
```

### 12. Decorator
**When:** Add behaviour to objects dynamically without subclassing (middleware, logging, validation).
```typescript
interface TextProcessor { process(text: string): string; }
class PlainText implements TextProcessor {
  process(text: string): string { return text; }
}
class UpperCaseDecorator implements TextProcessor {
  constructor(private wrapped: TextProcessor) {}
  process(text: string): string { return this.wrapped.process(text).toUpperCase(); }
}
class TrimDecorator implements TextProcessor {
  constructor(private wrapped: TextProcessor) {}
  process(text: string): string { return this.wrapped.process(text).trim(); }
}

const processor = new UpperCaseDecorator(new TrimDecorator(new PlainText()));
processor.process('  hello world  '); // "HELLO WORLD"
```

### 13. Facade
**When:** Simplify a complex subsystem behind a single clean interface (payment gateway, auth system).
```typescript
class PaymentFacade {
  private validator  = new CardValidator();
  private processor  = new PaymentProcessor();
  private notifier   = new EmailNotifier();
  private logger     = new TransactionLogger();

  processPayment(card: CardDetails, amount: number): boolean {
    if (!this.validator.validate(card)) return false;
    const txId = this.processor.charge(card, amount);
    this.notifier.send(card.email, txId);
    this.logger.log(txId, amount);
    return true;
  }
}
// Client only calls facade.processPayment(card, 99.99)
```

---

## BEHAVIORAL — Object communication and responsibility

### 14. Strategy
**When:** Family of interchangeable algorithms; swap behaviour at runtime (sorting, payment, pricing).
```typescript
interface SortStrategy<T> { sort(data: T[]): T[]; }
class BubbleSort<T> implements SortStrategy<T> {
  sort(data: T[]): T[] { return [...data].sort(); } // simplified
}
class QuickSort<T> implements SortStrategy<T> {
  sort(data: T[]): T[] { return [...data].reverse(); } // simplified
}
class DataSorter<T> {
  constructor(private strategy: SortStrategy<T>) {}
  setStrategy(s: SortStrategy<T>) { this.strategy = s; }
  sort(data: T[]): T[] { return this.strategy.sort(data); }
}
```

### 15. Observer
**When:** One-to-many dependency; when state changes, all dependents notified automatically (events, pub/sub).
```typescript
interface Observer { update(event: string, data: unknown): void; }
class EventEmitter {
  private listeners = new Map<string, Observer[]>();
  subscribe(event: string, obs: Observer) {
    (this.listeners.get(event) ?? this.listeners.set(event, []).get(event)!).push(obs);
  }
  emit(event: string, data: unknown) {
    this.listeners.get(event)?.forEach(o => o.update(event, data));
  }
}
```

### 16. Command
**When:** Encapsulate requests as objects; supports undo/redo, queuing, logging (text editors, macros).
```typescript
interface Command { execute(): void; undo(): void; }
class TextEditor {
  private text = '';
  private history: Command[] = [];
  addText(text: string) {
    const cmd: Command = {
      execute: () => { this.text += text; },
      undo:    () => { this.text = this.text.slice(0, -text.length); },
    };
    cmd.execute();
    this.history.push(cmd);
  }
  undoLast() { this.history.pop()?.undo(); }
  getText()  { return this.text; }
}
```

### 17. Iterator
**When:** Traverse a collection without exposing its implementation (custom data structures, ranges).
```typescript
class PlaylistIterator implements Iterator<string> {
  private index = 0;
  constructor(private tracks: string[]) {}
  next(): IteratorResult<string> {
    if (this.index < this.tracks.length) {
      return { value: this.tracks[this.index++], done: false };
    }
    return { value: '', done: true };
  }
}

const playlist = ['Song A', 'Song B', 'Song C'];
const iter = new PlaylistIterator(playlist);
let result = iter.next();
while (!result.done) { console.log(result.value); result = iter.next(); }
```

### 18. State
**When:** Object behaviour changes based on its state; avoids large if/switch chains (order status, traffic light).
```typescript
interface DocumentState { approve(): void; reject(): void; name: string; }
class DraftState implements DocumentState {
  name = 'Draft';
  constructor(private doc: Document) {}
  approve() { this.doc.setState(new ReviewState(this.doc)); }
  reject()  { console.log('Cannot reject draft'); }
}
class ReviewState implements DocumentState {
  name = 'Review';
  constructor(private doc: Document) {}
  approve() { this.doc.setState(new ApprovedState()); }
  reject()  { this.doc.setState(new DraftState(this.doc)); }
}
class ApprovedState implements DocumentState {
  name = 'Approved';
  approve() { console.log('Already approved'); }
  reject()  { console.log('Cannot reject approved'); }
}
class Document {
  private state: DocumentState = new DraftState(this);
  setState(s: DocumentState) { this.state = s; }
  approve() { this.state.approve(); }
  reject()  { this.state.reject(); }
  getState() { return this.state.name; }
}
```

### 19. Template Method
**When:** Define skeleton of algorithm in base class; subclasses fill in specific steps (data processing, reports).
```typescript
abstract class DataProcessor {
  // Template method — defines the algorithm
  process(data: string[]): string[] {
    const loaded   = this.load(data);
    const filtered = this.filter(loaded);
    const sorted   = this.sort(filtered);
    return this.format(sorted);
  }
  protected abstract filter(data: string[]): string[];
  private load(data: string[]) { return data; }
  private sort(data: string[]) { return [...data].sort(); }
  protected format(data: string[]) { return data; }
}
class ActiveUserProcessor extends DataProcessor {
  protected filter(data: string[]) { return data.filter(d => d.startsWith('active:')); }
}
```

### 20. Memento
**When:** Capture and restore an object's state (undo in editors, game save points).
```typescript
interface Memento<T> { getState(): T; }
class EditorMemento implements Memento<string> {
  constructor(private state: string) {}
  getState(): string { return this.state; }
}
class Editor {
  private content = '';
  type(text: string) { this.content += text; }
  save(): Memento<string> { return new EditorMemento(this.content); }
  restore(m: Memento<string>) { this.content = m.getState(); }
  getContent() { return this.content; }
}
```

### 21. Chain of Responsibility
**When:** Pass requests along a chain of handlers; each decides to handle or forward (logging levels, auth middleware).
```typescript
abstract class LogHandler {
  protected next?: LogHandler;
  setNext(handler: LogHandler): LogHandler { this.next = handler; return handler; }
  abstract handle(level: string, msg: string): void;
}
class ErrorHandler extends LogHandler {
  handle(level: string, msg: string) {
    if (level === 'error') console.error('[ERROR]', msg);
    else this.next?.handle(level, msg);
  }
}
class InfoHandler extends LogHandler {
  handle(level: string, msg: string) {
    if (level === 'info') console.info('[INFO]', msg);
    else this.next?.handle(level, msg);
  }
}
// const chain = new ErrorHandler();
// chain.setNext(new InfoHandler());
// chain.handle('error', 'Failed!'); chain.handle('info', 'Started');
```

### 22. Mediator
**When:** Reduce direct dependencies between objects by centralising communication (chat rooms, air traffic control).
```typescript
interface ChatMediator { sendMessage(from: string, msg: string): void; register(user: ChatUser): void; }
class ChatRoom implements ChatMediator {
  private users: ChatUser[] = [];
  register(user: ChatUser) { this.users.push(user); }
  sendMessage(from: string, msg: string) {
    this.users.filter(u => u.name !== from).forEach(u => u.receive(from, msg));
  }
}
class ChatUser {
  constructor(public name: string, private room: ChatMediator) { room.register(this); }
  send(msg: string)                { this.room.sendMessage(this.name, msg); }
  receive(from: string, msg: string) { console.log(`${this.name} ← ${from}: ${msg}`); }
}
```

### 23. Visitor
**When:** Add new operations to objects without modifying them; separate algorithm from object structure (AST traversal, DOM manipulation).
```typescript
interface DOMElement { accept(visitor: DOMVisitor): void; }
interface DOMVisitor { visitDiv(el: DivElement): void; visitText(el: TextElement): void; }

class DivElement implements DOMElement {
  constructor(public children: DOMElement[] = []) {}
  accept(v: DOMVisitor) { v.visitDiv(this); }
}
class TextElement implements DOMElement {
  constructor(public content: string) {}
  accept(v: DOMVisitor) { v.visitText(this); }
}
class HTMLRenderer implements DOMVisitor {
  visitDiv(el: DivElement)   { el.children.forEach(c => c.accept(this)); }
  visitText(el: TextElement) { console.log(el.content); }
}
```

---

## Pattern Selection Guide

| Need | Pattern |
|---|---|
| One global instance | Singleton |
| Subclass decides what to create | Factory Method |
| Compatible families of objects | Abstract Factory |
| Step-by-step object construction | Builder |
| Clone existing objects | Prototype |
| Reuse expensive objects | Object Pool |
| Wrap incompatible interface | Adapter |
| Tree of objects treated uniformly | Composite |
| Control access / lazy load | Proxy |
| Share memory between many instances | Flyweight |
| Decouple abstraction & implementation | Bridge |
| Add behavior dynamically | Decorator |
| Simplify complex subsystem | Facade |
| Swap algorithms at runtime | Strategy |
| Notify dependents automatically | Observer |
| Encapsulate requests / undo | Command |
| Traverse without exposing internals | Iterator |
| Behavior changes by state | State |
| Algorithm skeleton, steps vary | Template Method |
| Save / restore state | Memento |
| Pass request along a chain | Chain of Responsibility |
| Centralize inter-object communication | Mediator |
| New operations without modification | Visitor |

---

*Source: Akintoye, A. — Mastering Design Patterns in TypeScript (Juri Books, 2024)*
