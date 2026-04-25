# Excel Formulas & Functions Reference

*Sources: Ultimate Excel Formula & Function Reference Guide (500+ Tips); Microsoft Excel 365 Bible; Excel 2025 All-in-One*

---

## Table of Contents

1. [Formula Best Practices](#formula-best-practices)
2. [Lookup Functions](#lookup-functions)
3. [Aggregation Functions](#aggregation-functions)
4. [Dynamic Array Functions](#dynamic-array-functions)
5. [Text Functions](#text-functions)
6. [Date and Time Functions](#date-and-time-functions)
7. [Logical Functions](#logical-functions)
8. [LET and LAMBDA](#let-and-lambda)
9. [Error Handling](#error-handling)
10. [Formula Patterns by Use Case](#formula-patterns-by-use-case)

---

## Formula Best Practices

- **Use structured references** in Tables: `=Table1[Column]` not `=C:C`
- **Never hard-code values** in formulas — put constants in named cells or a Config sheet
- **Avoid volatile functions** (NOW(), TODAY(), RAND(), INDIRECT()) in large datasets — they recalculate on every change, causing slowness
- **Use LET** for any formula exceeding 60 characters — it improves readability and performance
- **Avoid deeply nested IFs** — use IFS(), SWITCH(), or XLOOKUP with arrays instead
- **Document complex formulas** with a comment (right-click cell → Insert Comment)
- **Never use entire column references** (C:C) in SUMIFS — use Table column references or defined ranges

---

## Lookup Functions

### XLOOKUP (preferred over VLOOKUP in all cases)

```excel
=XLOOKUP(lookup_value, lookup_array, return_array, [not_found], [match_mode], [search_mode])
```

| Argument | Use |
|---|---|
| lookup_value | Value to search for (or `[@ID]` in a Table) |
| lookup_array | Column to search in |
| return_array | Column(s) to return — can return multiple columns |
| not_found | Default: "Not found" (prevents #N/A) |
| match_mode | 0 = exact, -1 = exact or next smaller, 1 = exact or next larger, 2 = wildcard |
| search_mode | 1 = first-to-last, -1 = last-to-first, 2 = binary ascending |

```excel
# Basic lookup
=XLOOKUP([@CustomerID], Customers[ID], Customers[Name], "Unknown")

# Return multiple columns at once
=XLOOKUP([@ProductID], Products[ID], Products[[Name]:[Price]], "Not found")

# Last matching value (useful for latest record)
=XLOOKUP([@ID], Log[ID], Log[Status], , 0, -1)

# Approximate match (tax brackets, tiered pricing)
=XLOOKUP([@Income], TaxTable[Threshold], TaxTable[Rate], , -1)
```

### INDEX/MATCH (when XLOOKUP unavailable or for 2D lookups)

```excel
=INDEX(return_range, MATCH(lookup_value, lookup_range, 0))

# 2D lookup (row and column)
=INDEX(DataMatrix, MATCH([@Month], MonthList, 0), MATCH([@Category], CategoryList, 0))
```

### VLOOKUP (legacy — avoid in new work)

If forced to use VLOOKUP, always use `FALSE` (exact match) as the 4th argument. Never use TRUE (approximate) for exact lookups.

---

## Aggregation Functions

### SUMIFS / COUNTIFS / AVERAGEIFS

```excel
=SUMIFS(sum_range, criteria_range1, criteria1, [criteria_range2, criteria2, ...])

# Sum sales for East region in Q1
=SUMIFS(Sales[Amount], Sales[Region], "East", Sales[Quarter], "Q1")

# Dynamic criteria from cell reference
=SUMIFS(Sales[Amount], Sales[Region], B2, Sales[Status], "Paid")

# Date range criteria
=SUMIFS(Sales[Amount], Sales[Date], ">="&DATE(2026,1,1), Sales[Date], "<="&DATE(2026,3,31))

# Wildcard partial match
=SUMIFS(Sales[Amount], Sales[Product], "*Widget*")

# Count non-blank
=COUNTIFS(Leads[Email], "<>")

# Average excluding zeros
=AVERAGEIFS(Data[Score], Data[Score], ">0")
```

### MAXIFS / MINIFS (Excel 2019+)

```excel
=MAXIFS(max_range, criteria_range1, criteria1, ...)
=MINIFS(min_range, criteria_range1, criteria1, ...)

# Highest sale amount in the East region
=MAXIFS(Sales[Amount], Sales[Region], "East")

# Lowest score for students who passed
=MINIFS(Scores[Score], Scores[Result], "Pass")

# Max amount for East region in Q1
=MAXIFS(Sales[Amount], Sales[Region], "East", Sales[Quarter], "Q1")
```

### SUBTOTAL and AGGREGATE

```excel
# SUBTOTAL respects filtered rows; use instead of SUM in filtered tables
=SUBTOTAL(9, Sales[Amount])   # 9 = SUM
=SUBTOTAL(1, Sales[Amount])   # 1 = AVERAGE
=SUBTOTAL(3, Sales[ID])       # 3 = COUNT

# AGGREGATE ignores errors and hidden rows
=AGGREGATE(9, 5, Sales[Amount])   # SUM ignoring errors and hidden
=AGGREGATE(14, 6, Sales[Score], 3)  # 3rd largest, ignoring errors
```

---

## Dynamic Array Functions (Excel 365 / 2021+)

These functions spill results into multiple cells automatically.

### FILTER

```excel
=FILTER(array, include, [if_empty])

# Basic filter
=FILTER(Sales[#All], Sales[Region]="East")

# Multiple conditions (AND)
=FILTER(Sales[#All], (Sales[Region]="East") * (Sales[Status]="Paid"))

# Multiple conditions (OR)
=FILTER(Sales[#All], (Sales[Region]="East") + (Sales[Region]="West"))

# Filter with result if empty
=FILTER(Sales[#All], Sales[Amount]>100000, "No results")
```

### SORT and SORTBY

```excel
=SORT(array, [sort_index], [sort_order], [by_col])

# Sort table by Amount descending
=SORT(Sales[#All], 3, -1)   # column 3 descending

# Sort by multiple criteria
=SORTBY(Employees[#All], Employees[Department], 1, Employees[Name], 1)
```

### UNIQUE

```excel
=UNIQUE(array, [by_col], [exactly_once])

# Unique list of regions
=UNIQUE(Sales[Region])

# Items that appear exactly once
=UNIQUE(Orders[ProductID], , TRUE)
```

### SEQUENCE

```excel
=SEQUENCE(rows, [cols], [start], [step])

# 12 monthly dates starting Jan 2026
=SEQUENCE(12, 1, DATE(2026,1,1), 30)

# Number series 1–100
=SEQUENCE(100)

# 5×4 matrix starting at 0, step 5
=SEQUENCE(5, 4, 0, 5)
```

### CHOOSECOLS / CHOOSEROWS (Excel 365)

```excel
# Return specific columns from a range
=CHOOSECOLS(Sales[#All], 1, 3, 5)   # columns 1, 3, and 5 only

# Return specific rows
=CHOOSEROWS(DataMatrix, 1, 5, 10)
```

### TEXTSPLIT / TEXTBEFORE / TEXTAFTER (Excel 365)

```excel
=TEXTSPLIT("John, Doe, 42", ", ")          # splits to array: John | Doe | 42
=TEXTBEFORE("Report_2026-04-05.xlsx", "_") # "Report"
=TEXTAFTER("user@example.com", "@")        # "example.com"
```

---

## Text Functions

```excel
# Concatenation (prefer & or CONCAT over CONCATENATE)
=[@FirstName] & " " & [@LastName]
=CONCAT(A2:A10)              # joins array

# TEXTJOIN — join with delimiter, skip blanks
=TEXTJOIN(", ", TRUE, Tags[Tag])

# Case functions
=PROPER("john doe")          # "John Doe"
=UPPER("hello")              # "HELLO"
=LOWER("HELLO")              # "hello"

# Padding / trimming
=TRIM([@Name])               # removes extra spaces
=CLEAN([@Data])              # removes non-printable characters
=TEXT([@Amount], "#,##0.00") # format number as text

# Left / Right / Mid
=LEFT([@Code], 3)
=RIGHT([@Reference], 6)
=MID([@Code], 3, 4)

# Find and Replace
=SUBSTITUTE([@Phone], "-", "")   # remove dashes
=REPLACE([@Code], 1, 2, "XX")    # replace first 2 chars

# Find position
=FIND("-", [@Code])          # case-sensitive
=SEARCH("*widget*", [@Name]) # case-insensitive, wildcard

# String length
=LEN([@Name])
```

---

## Date and Time Functions

```excel
# Today / Now
=TODAY()          # current date (volatile)
=NOW()            # current date + time (volatile)

# Date construction
=DATE(2026, 4, 5)
=DATEVALUE("2026-04-05")

# Date parts
=YEAR([@Date])
=MONTH([@Date])
=DAY([@Date])
=WEEKDAY([@Date], 2)    # 2 = Monday=1 ... Sunday=7
=WEEKNUM([@Date], 2)    # ISO week number

# Date arithmetic
=[@EndDate] - [@StartDate]           # days between dates
=EDATE([@StartDate], 3)              # 3 months later
=EOMONTH([@Date], 0)                 # last day of same month
=NETWORKDAYS([@Start], [@End], Holidays[Date])  # working days

# Text to date (when importing)
=DATEVALUE(TEXT([@RawDate], "0000-00-00"))

# Display formats (use TEXT function for labels)
=TEXT([@Date], "DD MMM YYYY")        # "05 Apr 2026"
=TEXT([@Date], "MMMM YYYY")          # "April 2026"
=TEXT([@Date], "Q")&"Q "&TEXT([@Date], "YYYY")  # "2Q 2026" (approx)
```

---

## Logical Functions

```excel
# IF / IFS
=IF([@Score]>=50, "Pass", "Fail")
=IFS([@Score]>=90, "A", [@Score]>=75, "B", [@Score]>=60, "C", TRUE, "F")

# SWITCH (cleaner than nested IFs for discrete values)
=SWITCH([@Status],
  "Paid",    "✓",
  "Pending", "⏳",
  "Overdue", "⚠",
  "Unknown")

# AND / OR / NOT
=AND([@Amount]>0, [@Status]="Active")
=OR([@Region]="East", [@Region]="West")
=NOT(ISBLANK([@Email]))

# ISNUMBER / ISTEXT / ISBLANK / ISERROR
=IF(ISNUMBER([@Phone]), "Valid", "Check phone")
=IF(ISBLANK([@Email]), "Missing", [@Email])
```

---

## LET and LAMBDA

### LET — named variables in formulas

```excel
=LET(
  name1, value1,
  name2, value2,
  result_formula
)

# Real example: revenue per day calculation
=LET(
  days,    [@EndDate] - [@StartDate] + 1,
  revenue, [@TotalAmount],
  daily,   IF(days=0, 0, revenue / days),
  TEXT(daily, "#,##0.00")
)
```

Benefits: each sub-expression is calculated once (performance), readable names replace cryptic cell refs.

### LAMBDA — reusable custom functions

```excel
# Define in Name Manager as: TaxAmount
=LAMBDA(amount, rate, amount * rate)

# Use it like a built-in function
=TaxAmount([@GrossAmount], TaxRate)

# Recursive LAMBDA (e.g., factorial)
=LAMBDA(n, IF(n<=1, 1, n * Factorial(n-1)))
```

---

## Error Handling

```excel
# IFERROR — catch any error
=IFERROR(XLOOKUP([@ID], Products[ID], Products[Price]), 0)

# IFNA — catch #N/A only (better for lookups — other errors still surface)
=IFNA(XLOOKUP([@ID], Products[ID], Products[Price]), "Not found")

# ISERROR in conditional formatting — highlight error cells
Formula: =ISERROR(A1)   → red fill

# Suppress #DIV/0!
=IF([@Total]=0, 0, [@Value]/[@Total])
# or
=IFERROR([@Value]/[@Total], 0)
```

---

## Formula Patterns by Use Case

### Running total
```excel
=SUMIFS(Sales[Amount], Sales[Date], "<="&[@Date], Sales[ID], "<="&[@ID])
```

### Year-to-date total
```excel
=SUMIFS(Sales[Amount],
  Sales[Date], ">="&DATE(YEAR(TODAY()),1,1),
  Sales[Date], "<="&TODAY())
```

### Rank within group
```excel
=COUNTIFS(Sales[Region], [@Region], Sales[Amount], ">"&[@Amount]) + 1
```

### Age from date of birth
```excel
=DATEDIF([@DOB], TODAY(), "Y")
```

### Fiscal year (July start)
```excel
=IF(MONTH([@Date])>=7, YEAR([@Date]), YEAR([@Date])-1)
```

### Dynamic dropdown list (unique, sorted)
```excel
=SORT(UNIQUE(FILTER(Sales[Category], Sales[Category]<>"")))
```

### Weighted average
```excel
=SUMPRODUCT(Scores[Weight], Scores[Value]) / SUM(Scores[Weight])
```

### Concatenate list from filtered results
```excel
=TEXTJOIN(", ", TRUE, FILTER(Products[Name], Products[Category]=[@Category]))
```
