---
name: ios-debugging-mastery
description: Expert LLDB debugging for iOS — non-obvious commands (regex breakpoints,
  breakpoint persistence, register manipulation), Python scripting for custom LLDB
  commands (SBDebugger API, optparse, resymbolication), watchpoints for ObjC ivar
  writes...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Debugging Mastery

<!-- dual-compat-start -->
## Use When

- Expert LLDB debugging for iOS — non-obvious commands (regex breakpoints, breakpoint persistence, register manipulation), Python scripting for custom LLDB commands (SBDebugger API, optparse, resymbolication), watchpoints for ObjC ivar writes...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-debugging-mastery` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | iOS debugging playbook | Markdown doc covering LLDB regex breakpoints, register manipulation, and persistent breakpoint setup for repeat investigations | `docs/ios/lldb-playbook.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
**Source:** Advanced Apple Debugging & Reverse Engineering — Derek Selander
**Scope:** Production-grade LLDB, Python scripting, DTrace, memory analysis, binary RE

---

## 1. Non-Obvious LLDB Commands

### Regex Breakpoints

```lldb
# One-shot breakpoint on every function in a module (auto-removes after first hit)
rbreak . -s ModuleName -o 1

# Match viewDidLoad across Swift AND ObjC simultaneously
b viewDidLoad
```

### Breakpoint Persistence

```lldb
# Save all breakpoints to JSON — survives Xcode restarts
breakpoint write -f ~/Desktop/breakpoints.json

# Reload in future sessions
breakpoint read -f ~/Desktop/breakpoints.json
```

### Expression Evaluation Control

```lldb
# -i0 = stop ignoring breakpoints — step into called function
expression -i0 -- getenv("HOME")

# -u0 = prevent stack unwind if expression crashes
expression -u0 -O -- [UIApplication test]
```

### Type Summaries (Permanent, Survives Relaunches)

```lldb
# Override `p` output for any type — survives app re-launches
type summary add Signals.MasterVC --summary-string "VC: %1"
```

### Register and Flag Manipulation

```lldb
# Toggle Zero Flag (bit 6) to flip conditional branch WITHOUT touching source
register write rflags `$rflags ^ 64`

# Intel-flavor disassembly with mixed source/asm (more readable than AT&T default)
disassemble -F intel -m

# Force screen update while paused (Core Animation flush)
expression -l objc -- (void)[CATransaction flush]
```

### Swift vs ObjC Context — Critical Pitfall

LLDB defaults to ObjC context when you pause manually. Variables created with `$`
in ObjC context are NOT accessible from Swift context.

```lldb
# Create in ObjC context
po id $test = [NSObject new]

# Access from Swift context — explicit flag required
expression -l swift -- $test
```

Forgetting this causes silent failures. Always use `-l swift` or `-l objc` explicitly
when crossing contexts.

---

## 2. Watchpoints — Catch ALL Ivar Writes

Breakpoints on property setters miss direct ivar access and hardcoded offset writes.
Watchpoints catch all three paths. Hardware limit: 4 watchpoints per process, max 8 bytes each.

```lldb
# Step 1: Get ivar offset
language objc class-table dump ClassName -v

# Step 2: Find instance address (Debug Memory Graph or search.py)
# Example: address = 0x600001234567, offset = 0x18

# Step 3: Set watchpoint on write
watchpoint set expression -s 1 -w write -- (0x600001234567 + 0x18)

# Step 4: Add condition — only trigger when value becomes NO/false
watchpoint modify 1 -c '*(BOOL*)(0x600001234567 + 0x18) == 0'

# List all watchpoints
watchpoint list
```

---

## 3. Python Scripting for Custom LLDB Commands

### Required Function Signature

```python
def your_command(debugger, command, result, internal_dict):
    # result is SBCommandReturnObject
    # Use result.AppendMessage() NOT print()
    # print() goes to console — invisible in LLDB output pane
    result.AppendMessage("Found: " + str(value))
```

### Class Hierarchy for Introspection

```
SBDebugger → SBTarget → SBProcess → SBThread → SBFrame → SBValue
```

### Always Use optparse, Never argparse

`argparse` depends on `sys.argv` which LLDB Python does not support. Use `optparse`:

```python
import optparse
import shlex
import lldb

def create_options():
    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose', action='store_true',
                      dest='verbose', default=False)
    parser.add_option('-c', '--count', type='int', dest='count', default=1)
    return parser

def my_command(debugger, command, result, internal_dict):
    parser = create_options()
    try:
        options, args = parser.parse_args(shlex.split(command))
    except SystemExit:
        return

    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()

    opts = lldb.SBExpressionOptions()
    opts.SetIgnoreBreakpoints(False)
    value = target.EvaluateExpression('(int)strlen("hello")', opts)
    result.AppendMessage(f"Result: {value.GetValue()}")


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        'command script add -f my_module.my_command mycommand'
    )
```

### Register Command in .lldbinit

```python
# In ~/.lldbinit:
command script import ~/lldb_scripts/my_module.py
```

### Resymbolication of Stripped Binaries

Pattern for recovering ObjC method names from `___lldb_unnamed_symbolNNN` frames:

1. Enumerate all ObjC method addresses via `objc_copyClassNamesForImage` + `class_copyMethodList`
2. Compare against `SBSymbol.GetStartAddress()` for unnamed symbol frames
3. Swap in the real ObjC selector string

### Debugging Python LLDB Scripts

```python
import pdb; pdb.set_trace()
```

Works ONLY in Terminal LLDB. Does NOT work in Xcode console.

---

## 4. DTrace for Stripped Binaries

`objc$target` provider misses Swift `@objc` methods since SE-0160. Use `pid$target` for Swift.

```dtrace
# Trace all ObjC method calls — class + selector visible even in stripped builds
sudo dtrace -n '
objc$target:*:*:entry {
    printf("%s %s\n", probemod, probefunc)
}' -p $(pgrep YourApp)

# Swift functions (Swift 4+ unmangles names — glob patterns work directly)
sudo dtrace -n '
pid$target:YourApp:*viewDidLoad*:entry {
    trace(timestamp)
}' -p $(pgrep YourApp)

# Hook objc_msgSend to recover class/selector in fully stripped binary
sudo dtrace -n '
pid$target:libobjc*:objc_msgSend:entry {
    printf("%s %s\n",
        (string)*(uintptr_t*)arg0,
        (string)arg1
    )
}' -p $(pgrep YourApp)
```

`arg0` = self (isa pointer → class name), `arg1` = SEL → selector string.
`objc_msgSend` is the universal ObjC dispatch bottleneck — every ObjC call passes through it.

---

## 5. Malloc Stack Logging for Use-After-Free

### Enable Logging

```
Xcode: Scheme → Run → Diagnostics → Malloc Stack Logging
Environment variable: MallocStackLogging=1
Output: /tmp/stack-logs.PID...index
```

### Query Any Address

```lldb
(lldb) msl 0x600001234567
# Shows: full allocation site stack trace
# Shows: full deallocation site stack trace
```

Install `msl.py` from github.com/DerekSelander/LLDB.

**When to use**: `EXC_BAD_ACCESS` on a seemingly valid address. The standard backtrace
shows the crash site, not the free site. `msl` shows both — essential for use-after-free
and over-released objects.

---

## 6. .lldbinit Configuration

### Load Order

```
~/.lldbinit           # applies everywhere
~/.lldbinit-lldb      # Terminal LLDB only
~/.lldbinit-Xcode     # Xcode LLDB only
```

`.lldbinit` loads BEFORE process attachment — no process exists yet. Put only command
definitions and settings there, not arbitrary code execution.

### Practical command regex Patterns

```lldb
# Toggle any view hidden/visible and flush to screen without resuming execution
command regex tv 's/(.+)/expression -l objc -O -- @import UIKit; \
    UIView *view = (id)%1; \
    [view setHidden:![view isHidden]]; \
    (void)[CATransaction flush]; \
    view/'

# Usage:
tv 0x7fa234
```

### Load Chisel

```lldb
# In ~/.lldbinit:
command script import /path/to/chisel/fbchisellldb.py
```

### Key Chisel Commands

```lldb
pviews          # full view hierarchy with addresses
pvc             # view controller hierarchy
visualize       # open UIImage/UIView/CGImage in Preview.app
fv UILabel      # find all visible views of a given class
taplog          # log all tap events with coordinates
border          # add colored border to a view for visual identification
```

---

## 7. Mach-O Binary Analysis

### Module and Symbol Lookup

```lldb
image list                              # all loaded modules (frameworks, dylibs)
image lookup -n symbolName             # find symbol across all modules
image lookup -rn pattern ModuleName    # regex match within specific module
image lookup -vs UIDebuggingOverlayIsEnabled.__overlayIsEnabled  # full info + address
language objc class-table dump ModuleName -v  # dump ObjC class table
```

### Key Mach-O Sections for Reverse Engineering

| Section | Contents |
|---|---|
| `__TEXT.__cstring` | Hardcoded strings, API keys, error messages |
| `__DATA.__nl_symbol_ptr` | External function pointers (imported symbols) |
| `__DATA.__got` | Global offset table — singleton addresses, global variables |

---

## 8. Bypassing UIDebuggingInformationOverlay (iOS 11+)

Apple guards the overlay with `dispatch_once`. Token starts at 0, becomes -1 (0xFFFFFFFFFFFFFFFF) when complete.

```lldb
# Find the dispatch_once token address
image lookup -vs UIDebuggingOverlayIsEnabled.__overlayIsEnabled

# Write -1 to the token (makes the guard think it already ran — off-by-one bug in LLDB display here)
memory write <token_address> 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF

# Enable the overlay
expression -- (void)[[UIDebuggingInformationOverlay overlay] toggleVisibility]
```

---

## 9. Anti-Debugging Bypass

Anti-debugging commonly uses `ptrace(PT_DENY_ATTACH, 0, 0, 0)` where `PT_DENY_ATTACH = 31 (0x1F)`.

### Interactive Bypass

```lldb
b ptrace
condition 1 $rdi == 31      # only trigger when PT_DENY_ATTACH
thread return 0             # return without executing ptrace
continue
```

### Persistent Bypass in .lldbinit

```lldb
# -C runs command on trigger, -G1 auto-continues after command
breakpoint set -n ptrace -C "thread return 0" -G1
```

---

## 10. Register Manipulation

```lldb
register read                   # all registers
register read rdi               # specific register

# RFLAGS bit 6 = Zero Flag — flip conditional branch without changing source
register write rflags `$rflags ^ 64`

# Change function call parameters mid-flight (ObjC: rdi=self, rsi=_cmd)
register write rdi 0x1
register write rsi 0x0
```

**Calling convention (x86-64 / arm64 mapping):**

| Register | Role |
|---|---|
| `rdi` / `x0` | 1st argument (ObjC: self) |
| `rsi` / `x1` | 2nd argument (ObjC: _cmd) |
| `rdx` / `x2` | 3rd argument |
| `rax` / `x0` | Return value |

---

## Anti-Patterns

| Pattern | Problem | Fix |
|---|---|---|
| Breakpoints on property setters only | Miss direct ivar writes via offset | Use watchpoints |
| `print()` in LLDB Python scripts | Output goes to console, not LLDB | Use `result.AppendMessage()` |
| `argparse` in LLDB Python | Crashes — no `sys.argv` | Use `optparse` |
| `objc$target` for Swift code | Misses `@objc` methods since SE-0160 | Use `pid$target` |
| Averages for memory analysis | Hides allocation hotspots | Use Instruments Allocations with VM Regions |
| Debugging only in Debug build | Different from production crashes | Reproduce in Release build |
| Single-context expressions | Silent failures crossing Swift/ObjC | Always use `-l swift` or `-l objc` flag |

---

## Quick Reference: When to Reach for What

| Scenario | Tool |
|---|---|
| "Where does this property get set?" | Watchpoint on ivar address |
| "App crashes with EXC_BAD_ACCESS on valid-looking address" | `msl` + MallocStackLogging |
| "Framework is stripped — need to see what it calls" | DTrace `objc$target` or `pid$target` |
| "Need reusable custom command with arguments" | Python script with `optparse` |
| "Conditional branch going wrong way — quick flip" | `register write rflags` toggle ZF |
| "App detects debugger and exits" | ptrace breakpoint + `thread return 0` |
| "Need breakpoints next session without resetting" | `breakpoint write/read` JSON |
| "View looks wrong — toggle without recompiling" | `tv` command regex + `CATransaction flush` |
