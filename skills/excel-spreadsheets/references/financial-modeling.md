# Financial Modeling & What-If Analysis

*Sources: Excel 2019 Advanced Topics (George); Advanced Excel for Productivity (Urban)*

---

## Table of Contents

1. [Financial Functions](#financial-functions)
2. [Excel Modeling Golden Rules](#excel-modeling-golden-rules)
3. [Goal Seek](#goal-seek)
4. [Data Tables (Sensitivity Analysis)](#data-tables-sensitivity-analysis)
5. [Scenario Manager](#scenario-manager)
6. [Solver](#solver)
7. [Formula Debugging Tools](#formula-debugging-tools)

---

## Financial Functions

### PMT — Loan / Mortgage Payments

```excel
=PMT(rate, nper, pv, [fv], [type])
```

- `rate` — interest rate **per period** (annual rate ÷ 12 for monthly)
- `nper` — total payment periods
- `pv` — present value (loan principal, as a positive number)
- `type` — 0 = end of period (default), 1 = beginning of period

**Rule:** Rate and nper must use the same time unit. Monthly payments → `rate=annual/12`, `nper=years*12`.

```excel
# Monthly payment on $10,000 loan, 8% p.a., 12 months
=PMT(8%/12, 12, 10000)          # result: -$869.88 (negative = cash out)

# Total loan cost
=PMT(8%/12, 12, 10000) * 12     # multiply by nper
```

---

### PV — Present Value

```excel
=PV(rate, nper, pmt, [fv], [type])
```

Returns what a future stream of payments is worth today.

```excel
# PV of 60 monthly payments of $500 at 5% p.a.
=PV(5%/12, 60, 500)             # result: -$26,279.33

# PV of lump sum $100,000 received in 10 years at 6%
=PV(6%, 10, 0, 100000)
```

---

### FV — Future Value

```excel
=FV(rate, nper, pmt, [pv], [type])
```

Returns the future value of an investment given regular payments.

```excel
# Future value of $200/month for 10 months at 6% p.a.
=FV(6%/12, 10, -200)            # pmt is negative (money paid out)

# With initial lump sum of $1,000 + 12 payments of $100
=FV(6%/12, 12, -100, -1000)
```

---

### NPV — Net Present Value

```excel
=NPV(rate, value1, [value2, ...])
```

**Key difference from PV:** NPV handles variable cash flows; assumes cash flows start at **end of period 1** (not period 0).

```excel
# NPV of 5-year investment: initial outlay in B1, cash flows in B2:B6
=B1 + NPV(10%, B2:B6)           # add initial outlay separately (it's period 0)
```

**Tip:** If the initial investment is in the cash flow range, it will be discounted — add it outside NPV instead.

---

### IRR — Internal Rate of Return

```excel
=IRR(values, [guess])
```

```excel
# IRR for cash flows in B1:B6 (B1 = negative initial investment)
=IRR(B1:B6)
```

---

## Excel Modeling Golden Rules

From *Advanced Excel for Productivity* (Urban):

1. **Separate inputs, calculations, outputs** — put assumptions on a dedicated "Inputs" or "Config" sheet, never hard-code in formula cells
2. **One row per time period, one column per variable** — consistent structure enables SUMIFS, PivotTables, and charting
3. **Never mix data types in a column** — a column is either numbers, text, or dates
4. **Name all input cells** — use Name Manager so formulas read `=Revenue * TaxRate` not `=B4 * D2`
5. **Colour-code inputs vs formulas** — standard convention: blue text = hardcoded input, black = formula, green = external link
6. **Use absolute references for shared inputs**: `=$B$4` — protects against breaking when rows/columns are inserted
7. **Document assumptions** — add a comment (right-click → Insert Comment) to every non-obvious input cell
8. **Test with extreme values** — enter 0, negative numbers, very large numbers to verify formulas don't break
9. **Avoid circular references** — except in intentional iterative models; mark them clearly

---

## Goal Seek

Goal Seek finds the **input value** needed to achieve a **target output**.

**Use case:** "What loan amount can I afford if I want payments under $500/month?"

**Steps:**
1. Build a model with one input → one output formula
2. **Data** tab → **What-If Analysis** → **Goal Seek**
3. Set Cell: the output formula cell (e.g., `C4` with `=PMT(...)`)
4. To Value: the target result (e.g., `-500`)
5. By Changing Cell: the input cell (e.g., `B2` = loan amount)
6. Click **OK**

**Note:** Goal Seek overwrites the input cell. Use `Ctrl+Z` to restore if you don't want the result.

---

## Data Tables (Sensitivity Analysis)

Data Tables calculate how one output changes across a range of input values — the "what-if" table.

### One-variable Data Table

Shows how the output (e.g., PMT) changes for different loan amounts.

1. Put the input values in a column (e.g., D2:D10 = different loan amounts)
2. Put a reference to the formula in the row above the first input (e.g., E1 = `=C4`)
3. Select D1:E10 (the block including the reference cell)
4. **Data** → **What-If Analysis** → **Data Table**
5. Column input cell: the cell in your model that the column values replace (e.g., `$B$2`)
6. Click OK — Excel fills the table with results

### Two-variable Data Table

Tests two inputs simultaneously (e.g., loan amount AND interest rate vs payment).

1. Input values for variable 1 in a column (D2:D10)
2. Input values for variable 2 in a row (E1:J1)
3. Put the formula at the intersection (D1)
4. Select D1:J10 → **Data** → **Data Table**
5. Row input cell: the cell your row values replace
6. Column input cell: the cell your column values replace

---

## Scenario Manager

Scenario Manager stores and compares multiple named sets of input values.

**Use case:** Compare "Base Case", "Optimistic", "Pessimistic" revenue projections.

**Steps:**
1. **Data** → **What-If Analysis** → **Scenario Manager**
2. Click **Add** → name the scenario (e.g., "Base Case")
3. Select **Changing Cells**: the input cells that differ between scenarios
4. Enter values for this scenario
5. Repeat for each scenario (Optimistic, Pessimistic, etc.)
6. Click **Summary** → Scenario Summary → select result cells → OK

**Output:** A new sheet with a structured comparison table showing all scenarios side by side.

**Integration with Solver:** Solver can save its solution as a named scenario for comparison.

---

## Solver

Solver finds **optimum values for multiple inputs** subject to **constraints** — for complex optimisation problems.

**Use cases:** Maximise profit, minimise cost, find allocation that meets all constraints.

**Setup:**
1. Install: **File** → **Options** → **Add-ins** → **Solver Add-in** → Go → check box
2. Build a model: objective cell (to maximise/minimise), variable cells, constraint formulas

**Steps:**
1. **Data** → **Solver**
2. **Set Objective:** select the cell to optimise (e.g., `$C$8` = total income)
3. **To:** Max / Min / Value Of (specify target)
4. **By Changing Variable Cells:** cells Solver can modify (e.g., `$D$4:$D$6` = growth rates)
5. **Subject to Constraints:** click **Add** → set limits (e.g., `$D$4 >= 0%`, `$D$6 <= 20%`)
6. **Select Solving Method:**
   - GRG Nonlinear — default for smooth non-linear problems
   - Simplex LP — for linear problems (faster)
   - Evolutionary — for non-smooth / discontinuous problems
7. Click **Solve** → Keep Solver Solution or Restore Original Values
8. Optionally: **Save Scenario** to store the result in Scenario Manager

---

## Formula Debugging Tools

### Trace Precedents / Dependents

Visually draws arrows showing which cells feed into a formula.

- **Formulas** tab → **Trace Precedents** — shows what the selected cell depends on
- **Formulas** tab → **Trace Dependents** — shows what uses the selected cell
- **Remove Arrows** to clear

### Evaluate a Formula

Steps through a complex formula one calculation at a time.

- **Formulas** → **Evaluate Formula** → click **Evaluate** repeatedly to see each step resolve

### Watch Window

Monitors cells across sheets without navigating to them — useful for large models.

- **Formulas** → **Watch Window** → **Add Watch** → select cells to monitor
- The window stays visible while you edit other sheets

### F2 — Edit Mode

Press `F2` to enter edit mode on any formula cell — Excel colour-codes all referenced ranges, making it easy to spot errors visually.
