# VBA Macros & Keyboard Shortcuts

*Sources: Advanced Excel for Productivity (Urban); Excel 2019 Advanced Topics (George)*

---

## Table of Contents

1. [Recording Macros](#recording-macros)
2. [Running Macros](#running-macros)
3. [VBA Basics](#vba-basics)
4. [VBA Golden Rules](#vba-golden-rules)
5. [Common VBA Patterns](#common-vba-patterns)
6. [Keyboard Shortcuts Reference](#keyboard-shortcuts-reference)

---

## Recording Macros

Excel records your mouse clicks and keystrokes as VBA code — the fastest way to write automation.

**Three ways to start recording:**
1. Status bar → **Record Macro** button (bottom left, next to "Ready")
2. **View** tab → **Macros** → **Record Macro**
3. **Developer** tab → **Record Macro** (enable Developer tab in File → Options → Customize Ribbon)

**Before recording — choose reference style:**
- **Absolute references (default):** Macro always acts on the same cells — use for fixed-position tasks
- **Relative references:** Macro acts relative to the current cell — use for repeatable row operations
  - Toggle: View → Macros → **Use Relative References** (click before recording)

**Record Macro dialog settings:**
- **Macro name:** No spaces — use CamelCase or underscores (e.g., `FormatSalesTable`)
- **Shortcut key:** Use `Ctrl+Shift+Letter` to avoid overwriting standard shortcuts
- **Store macro in:** Choose `Personal Macro Workbook` (PERSONAL.XLSB) for global availability; `This Workbook` for file-specific macros
- **Description:** Brief note on what the macro does

**Stop recording:** Status bar button → **Stop Recording**, or View → Macros → Stop Recording.

---

## Running Macros

Three ways to run a macro:
1. `Alt+F8` → select macro name → **Run**
2. Assigned shortcut key (e.g., `Ctrl+Shift+M`)
3. Button on sheet: Insert → Shapes or Form Controls → right-click → Assign Macro

**Add to Quick Access Toolbar (QAT):**
File → Options → Quick Access Toolbar → Choose commands from: Macros → select → Add

---

## VBA Basics

### Open the VBA Editor

`Alt+F11` — opens the Visual Basic Editor (VBE).

### Macro structure

```vba
Sub MacroName()
    ' This is a comment
    ' All macro code goes between Sub and End Sub
    
    Range("A1").Value = "Hello"
    Range("B1").Select
    
End Sub
```

### Variables

```vba
Sub VariableExample()
    Dim customerName As String
    Dim orderAmount  As Double
    Dim rowCount     As Long
    Dim isActive     As Boolean
    
    customerName = "Acme Corp"
    orderAmount  = 15000.50
    rowCount     = Cells(Rows.Count, "A").End(xlUp).Row  ' last used row in col A
    isActive     = True
End Sub
```

### Interacting with cells and ranges

```vba
' Read / write cell values
Range("A1").Value = "Header"
Cells(2, 1).Value = 100              ' row 2, column 1

' Get the last row with data in column A
Dim lastRow As Long
lastRow = Cells(Rows.Count, "A").End(xlUp).Row

' Loop through all data rows
Dim i As Long
For i = 2 To lastRow
    If Cells(i, 3).Value > 0 Then
        Cells(i, 4).Value = Cells(i, 3).Value * 1.1
    End If
Next i
```

### Math functions in VBA

```vba
Dim result As Double
result = Application.WorksheetFunction.Sum(Range("C2:C100"))
result = Application.WorksheetFunction.Average(Range("C2:C100"))
result = Application.Max(10, 20, 5)   ' or Application.WorksheetFunction.Max(...)
```

### Conditional logic

```vba
If score >= 90 Then
    grade = "A"
ElseIf score >= 75 Then
    grade = "B"
ElseIf score >= 60 Then
    grade = "C"
Else
    grade = "F"
End If
```

---

## VBA Golden Rules

From *Advanced Excel for Productivity* (Urban):

1. **Always use `Option Explicit`** at the top of every module — forces variable declaration, catches typos
2. **Declare variable types** — `As Long`, `As String`, `As Double` — never use `Variant` unless necessary
3. **Always turn off screen updating** when running long macros: `Application.ScreenUpdating = False` (restore to `True` at end)
4. **Use `With` blocks** to avoid repeating object references
5. **Never use `.Select` / `.Activate`** — reference cells directly: `Range("A1").Value = x` not `Range("A1").Select: ActiveCell.Value = x`
6. **Always handle errors**: `On Error GoTo ErrorHandler` with a cleanup section
7. **Comment non-obvious logic** — future-you will thank present-you
8. **Test with small data** before running on full datasets

```vba
' Good pattern
Sub FormatReport()
    Application.ScreenUpdating = False
    On Error GoTo ErrorHandler

    With ActiveSheet
        .Range("A1").Font.Bold = True
        .Range("A1").Font.Size = 14
        .Range("A1").Interior.Color = RGB(31, 56, 100)
        .Range("A1").Font.Color = RGB(255, 255, 255)
    End With

    Application.ScreenUpdating = True
    Exit Sub

ErrorHandler:
    Application.ScreenUpdating = True
    MsgBox "Error " & Err.Number & ": " & Err.Description
End Sub
```

---

## Common VBA Patterns

### Delete empty rows

```vba
Sub DeleteEmptyRows()
    Dim lastRow As Long
    Dim i As Long
    lastRow = Cells(Rows.Count, "A").End(xlUp).Row
    For i = lastRow To 1 Step -1        ' loop backwards to avoid skipping rows
        If Application.WorksheetFunction.CountA(Rows(i)) = 0 Then
            Rows(i).Delete
        End If
    Next i
End Sub
```

### Custom function (UDF) usable in cells

```vba
Function TaxAmount(amount As Double, rate As Double) As Double
    TaxAmount = amount * rate
End Function
' Use in a cell: =TaxAmount(B2, 0.18)
```

### Auto-run when file opens

```vba
' In the ThisWorkbook module:
Private Sub Workbook_Open()
    ' Refresh all PivotTables on open
    ThisWorkbook.RefreshAll
    ' Navigate to the Summary sheet
    Sheets("Summary").Activate
End Sub
```

---

## Keyboard Shortcuts Reference

Essential shortcuts from *Advanced Excel for Productivity* (Urban) — mouse-free navigation.

### Navigation

| Shortcut | Action |
|---|---|
| `Ctrl+Arrow` | Jump to end of contiguous data range |
| `Ctrl+Home` | Go to cell A1 |
| `Ctrl+End` | Go to last used cell |
| `Ctrl+Shift+Arrow` | Select to end of data range |
| `Ctrl+Shift+End` | Select to last used cell |
| `Ctrl+Page Down/Up` | Move to next/previous sheet |

### Editing

| Shortcut | Action |
|---|---|
| `F2` | Enter edit mode on current cell (shows formula colour-coding) |
| `Ctrl+D` | Fill Down (copy top cell of selection to all below) |
| `Ctrl+R` | Fill Right |
| `Ctrl+;` | Insert today's date |
| `Ctrl+Shift+;` | Insert current time |
| `Alt+Enter` | Insert line break inside a cell |
| `Ctrl+1` | Open Format Cells dialog |
| `Ctrl+-` | Delete selected rows/columns |
| `Ctrl+Shift++` | Insert rows/columns |

### Formulas

| Shortcut | Action |
|---|---|
| `F4` | Toggle absolute/mixed/relative reference (`$A$1` → `A$1` → `$A1` → `A1`) |
| `Ctrl+Shift+Enter` | Enter array formula (legacy — use dynamic arrays instead) |
| `Ctrl+`` ` | Toggle formula view (show formulas instead of values) |
| `Ctrl+[` | Select all precedent cells |
| `F9` | Evaluate selected part of formula |

### Formatting (Alt key sequences)

| Shortcut | Action |
|---|---|
| `Alt+H+O+I` | Auto-fit column width |
| `Alt+H+O+A` | Auto-fit row height |
| `Alt+H+B+A` | Apply all borders |
| `Alt+H+H` | Fill colour picker |
| `Alt+H+F+C` | Font colour picker |

### Paste Special

| Shortcut | Action |
|---|---|
| `Ctrl+Alt+V` | Open Paste Special dialog |
| `Ctrl+Alt+V, V, Enter` | Paste Values only |
| `Ctrl+Alt+V, T, Enter` | Paste Formats only |
| `Ctrl+Alt+V, F, Enter` | Paste Formulas only |

### Grouping / Hiding

| Shortcut | Action |
|---|---|
| `Alt+Shift+Right` | Group selected rows/columns |
| `Alt+Shift+Left` | Ungroup |
| `Ctrl+9` | Hide selected rows |
| `Ctrl+0` | Hide selected columns |
| `Ctrl+Shift+9` | Unhide rows |
| `Ctrl+Shift+0` | Unhide columns |

### Workbook management

| Shortcut | Action |
|---|---|
| `Ctrl+N` | New workbook |
| `Ctrl+W` | Close current workbook |
| `Ctrl+F6` | Switch between open workbooks |
| `Alt+F4` | Close Excel |
| `Alt+F11` | Open VBA Editor |
| `Alt+F8` | Open Macro dialog |
