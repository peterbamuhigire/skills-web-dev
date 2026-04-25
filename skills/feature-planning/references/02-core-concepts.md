## 🏗️ Core Concepts You Need to Understand

### 1. Step (Definition)

A **Step** is a single, executable action in a plan.

```javascript
// A STEP is like a function call
{
  id: 1,
  name: "Analyze Market",
  action: "planning-agent.analyzeMarket",
  input: { sector: "SaaS", region: "East Africa" },
  expected_output: "market_analysis_report",
  duration: "5 minutes",
  depends_on: []  // This step has no dependencies
}
```

**In your CS class**:

- Step = function call
- id = function identifier
- depends_on = what inputs we need (prerequisites)

---

### 2. Dependency (Definition)

A **Dependency** means "step X needs output from step Y before it can run."

```javascript
// Example: Can't bake pizza before adding toppings

STEP 1: Add sauce
  └─ Output: sauced_dough

STEP 2: Add toppings
  └─ Depends on: STEP 1 output
  └─ Input: sauced_dough
  └─ Output: topped_pizza

STEP 3: Bake
  └─ Depends on: STEP 2 output
  └─ Input: topped_pizza
  └─ Output: baked_pizza
```

**In your CS class**:

- This is like function composition: `f(g(h(x)))`
- Can't call `g()` until `h()` finishes
- Dependencies create an **execution order**

---

### 3. Parallelization (Definition)

**Parallelization** means "multiple steps that have NO dependencies can run at the same time."

```javascript
// PLAN: Prepare for exam
STEP 1: Read Chapter 1        [PARALLEL GROUP 1]
STEP 2: Read Chapter 2        [PARALLEL GROUP 1]
STEP 3: Solve practice problems [STEP 1 + 2 output needed]
STEP 4: Review notes          [PARALLEL GROUP 1]
STEP 5: Take practice test    [STEP 3 output needed]

// Execution:
// Time 0:   START STEP 1, 2, 4 together (no dependencies)
// Time 30:  STEP 1, 2, 4 finish
// Time 30:  START STEP 3 (needs STEP 1, 2 output)
// Time 40:  STEP 3 finishes
// Time 40:  START STEP 5 (needs STEP 3 output)
// Time 50:  STEP 5 finishes, DONE

// Total time: 50 minutes (not 60, because we parallelized!)
```

**In your CS class**:

- This is like **multithreading** or **async programming**
- Instead of waiting for A to finish, start B and C while A runs
- Speedup = running tasks in parallel instead of sequentially

---

### 4. Directed Acyclic Graph (DAG) (Definition)

A **DAG** is the structure that represents all steps and their dependencies.

```
STEP 1: Analyze Market
  ↓
STEP 2: Identify Audience
  ↓
STEP 3: Define Positioning  ← Needs STEP 1 & 2
  ↓
STEP 4: Create Messaging    ← Needs STEP 3
  ↓
STEP 5: Validate Strategy   ← Needs STEP 4

This is a DAG (Directed Acyclic Graph):
- Directed = arrows have direction (STEP 1 → STEP 2)
- Acyclic = no loops (STEP 5 doesn't go back to STEP 1)
- Graph = visual representation of dependencies
```

**In your CS class**:

- DAGs are used in: Build systems, task schedulers, compilers
- Example: Make files use DAGs to determine build order
- You've probably studied graph theory in discrete math

---

### 5. Validation (Definition)

**Validation** means "check that the output of a step is correct before moving to the next step."

```javascript
STEP 1: Create sales plan
  └─ Output: { goals: [...], timeline: [...] }

VALIDATION:
  ✓ goals array is not empty
  ✓ timeline has dates in correct format
  ✓ Each goal has a measurable target

If validation PASSES:
  → Proceed to STEP 2

If validation FAILS:
  → Mark step as FAILED
  → Handle error (retry, fallback, etc)
```

**In your CS class**:

- This is like **unit testing** — verify output before next step
- In databases, this is **data integrity checks**
- In networks, this is **packet validation**
