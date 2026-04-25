# Python Excel Automation

*Sources: Automate Excel with Python (Wengler, 2026); Python in Excel Advanced (Van Der Post)*

---

## Table of Contents

1. [The Excel–Python–Excel Workflow](#the-excelpythonexcel-workflow)
2. [Advanced read_excel() Patterns](#advanced-read_excel-patterns)
3. [The 6-Step Export Workflow](#the-6-step-export-workflow)
4. [pandas Data Analysis Patterns](#pandas-data-analysis-patterns)
5. [Email Automation from Python](#email-automation-from-python)
6. [Python in Excel (=PY() Function)](#python-in-excel-py-function)
7. [xlwings — Live Excel Interaction](#xlwings--live-excel-interaction)
8. [Modular Workflow Architecture](#modular-workflow-architecture)

---

## The Excel–Python–Excel Workflow

The standard automation loop: **read** Excel into a DataFrame → **transform** in Python → **write** back to Excel.

```
Excel file (.xlsx)
    ↓  pd.read_excel()
DataFrame (pandas)
    ↓  transform, filter, aggregate, merge
Processed DataFrame
    ↓  pd.ExcelWriter + openpyxl formatting
Formatted Excel output (.xlsx)
    ↓  optionally: email via smtplib
Recipient
```

**Core imports for any Excel automation script:**

```python
import pandas as pd
import openpyxl as op
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import date, datetime
import smtplib
from pathlib import Path
```

---

## Advanced read_excel() Patterns

### Basic import

```python
df = pd.read_excel('report.xlsx', sheet_name='Sales', header=0)
```

### Multi-tab workbook

```python
# Import a specific tab by name or position (0-indexed)
df_sales = pd.read_excel('report.xlsx', sheet_name='Sales')
df_q1    = pd.read_excel('report.xlsx', sheet_name=0)   # first tab

# Import all tabs at once → returns dict {tab_name: DataFrame}
all_tabs = pd.read_excel('report.xlsx', sheet_name=None)
df_sales = all_tabs['Sales']
```

### Handling messy spreadsheets

```python
# Title row exists above the column headers — tell pandas which row to use
df = pd.read_excel('report.xlsx', header=2)      # column labels on row 3

# Use a column as the DataFrame index
df = pd.read_excel('report.xlsx', header=2, index_col='ID')

# Skip footer rows (totals, disclaimers)
df = pd.read_excel('report.xlsx', nrows=100, skipfooter=2)

# Fix hard returns (newline characters) inside cells
df['City'] = df['City'].str.replace('\n', ' ')
```

### Robust import with validation

```python
def load_excel(path: str, sheet=0, required_cols: set = None) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet, header=0)
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

    if required_cols:
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

    # Standard coercions
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip() if df[col].dtype == object else df[col]

    return df.reset_index(drop=True)
```

---

## The 6-Step Export Workflow

Follow this sequence every time you write a formatted Excel file from Python:

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

# ── Step 1: Create the writer object and Excel file ───────────
writer = pd.ExcelWriter('output.xlsx', engine='openpyxl')

# ── Step 2: Write DataFrames to sheets ────────────────────────
df_sales.to_excel(writer, sheet_name='Sales',   index=False, startrow=3)
df_summary.to_excel(writer, sheet_name='Summary', index=False, startrow=3)

# ── Step 3: Get the workbook object ───────────────────────────
wb = writer.book

# ── Step 4: Format each sheet with openpyxl ──────────────────
for sheet_name, df in [('Sales', df_sales), ('Summary', df_summary)]:
    ws = wb[sheet_name]

    # Add title rows above the data (startrow=3 left rows 1-3 empty)
    ws.insert_rows(1, amount=3)
    ws['A1'] = sheet_name
    ws['A1'].font = Font(name='Calibri Light', size=16, bold=True, color='FFFFFF')
    ws['A1'].fill = PatternFill('solid', fgColor='1F3864')

    # Format headers (now row 4 after insert)
    n_cols = len(df.columns)
    for col_idx in range(1, n_cols + 1):
        cell = ws.cell(row=4, column=col_idx)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='1F3864')

    # Add Table definition
    last_col = get_column_letter(n_cols)
    last_row = 4 + len(df)
    tbl = Table(displayName=sheet_name.replace(' ', ''), ref=f'A4:{last_col}{last_row}')
    tbl.tableStyleInfo = TableStyleInfo(name='TableStyleMedium2', showRowStripes=True)
    ws.add_table(tbl)

    # Freeze header row
    ws.freeze_panes = 'A5'

    # Auto column widths
    for col in ws.columns:
        max_len = max((len(str(c.value or '')) for c in col), default=0)
        ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 8), 60)

# ── Step 5: Close the writer (saves the file) ─────────────────
writer.close()

# ── Step 6: Verify by opening in Excel ────────────────────────
# (manual step — always test before production)
```

---

## pandas Data Analysis Patterns

### value_counts — frequency distribution

```python
# Count occurrences of each unique value
df['Status'].value_counts()

# As percentages
df['Status'].value_counts(normalize=True)

# Count specific values
df['Region'].value_counts()[['East', 'West']]
```

### crosstab — cross-tabulation

```python
pd.crosstab(df['Region'], df['Product'])              # frequency
pd.crosstab(df['Region'], df['Product'],
            values=df['Amount'], aggfunc='sum')        # sum of amounts
pd.crosstab(df['Region'], df['Product'],
            margins=True, margins_name='Total')        # add row/col totals
```

### pivot_table — Excel-style pivot in Python

```python
summary = df.pivot_table(
    index='Region',
    columns='Product',
    values='Sales',
    aggfunc='sum',
    fill_value=0
)
summary.plot(kind='bar', figsize=(10, 6))             # chart from pivot
summary.to_excel('pivot_output.xlsx')
```

### merge — replaces VLOOKUP

```python
# Inner join (only matching rows) — equivalent to strict VLOOKUP
result = df_orders.merge(df_customers, on='CustomerID', how='inner')

# Left join (all orders, fill NaN if no matching customer)
result = df_orders.merge(df_customers, on='CustomerID', how='left')

# Join on different column names
result = df_orders.merge(df_customers,
                         left_on='CustID', right_on='ID', how='left')

# Verify no duplicate keys after merge
assert result.shape[0] == df_orders.shape[0], "Unexpected duplicate keys in merge"
```

### Date calculations

```python
import datetime as dt

df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
df['Age_Days'] = (pd.Timestamp.today() - df['Date']).dt.days
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year
df['MonthLabel'] = df['Date'].dt.strftime('%b %Y')  # "Apr 2026"

# Filter by date range
mask = (df['Date'] >= '2026-01-01') & (df['Date'] <= '2026-03-31')
df_q1 = df[mask]
```

---

## Email Automation from Python

Send Excel reports via email after generating them.

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path

def send_report(to: str, subject: str, body_html: str, attachment_path: str):
    """Send an Excel file as an email attachment."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = 'reports@example.com'
    msg['To']      = to

    msg.attach(MIMEText(body_html, 'html'))

    with open(attachment_path, 'rb') as f:
        part = MIMEApplication(f.read(), Name=Path(attachment_path).name)
    part['Content-Disposition'] = f'attachment; filename="{Path(attachment_path).name}"'
    msg.attach(part)

    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('user@example.com', 'password')
        server.sendmail(msg['From'], [to], msg.as_string())

# DataFrame as HTML table in email body
def df_to_html_table(df: pd.DataFrame) -> str:
    return df.to_html(index=False, border=0,
                      classes='report-table',
                      float_format=lambda x: f'{x:,.2f}')
```

---

## Python in Excel (=PY() Function)

Microsoft's native Python integration (Excel 365, requires Python in Excel preview). Executes Python **in the cloud** (Anaconda environment), not locally.

### Basic syntax

```excel
=PY("python_code_here")
```

### Data cleaning

```excel
=PY("
import pandas as pd
data = {'Name': ['John', None, 'Anna'], 'Age': [28, 35, None]}
df = pd.DataFrame(data)
df['Age'].fillna(df['Age'].mean(), inplace=True)
df.dropna(inplace=True)
df
")
```

### Machine learning in Excel

```excel
=PY("
from sklearn.linear_model import LinearRegression
import numpy as np
X = np.array([5,15,25,35,45,55]).reshape(-1,1)
y = np.array([5,20,14,32,22,38])
model = LinearRegression().fit(X, y)
predictions = model.predict(X)
predictions
")
```

### Embed a matplotlib chart

```excel
=PY("
import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_excel('data.xlsx')
fig, ax = plt.subplots(figsize=(8,4))
ax.bar(df['Month'], df['Sales'])
ax.set_title('Monthly Sales')
fig
")
```

**Limitations of =PY():**
- Runs in Anaconda cloud — no access to local files unless uploaded
- Cannot directly reference arbitrary cell ranges without using `xl()` helper
- Results returned as static values or images — not live-updating formulas

**Reference ranges from Excel cells:**

```excel
=PY("
import pandas as pd
df = xl('SalesTable[#All]', headers=True)   # reference Excel Table
total = df['Amount'].sum()
total
")
```

---

## xlwings — Live Excel Interaction

xlwings runs Python scripts that **read and write a live, open Excel workbook** — ideal for Jupyter Notebook integration and two-way automation.

```python
import xlwings as xw

# Connect to a new or open workbook
wb  = xw.Book()                  # new workbook
sht = wb.sheets[0]

# Write to cells
sht.range('A1').value = 'Hello from Python!'
sht.range('B1').value = [1, 2, 3, 4, 5]              # write a list as a row
sht.range('A2').options(transpose=True).value = [10, 20, 30]  # as a column

# Read from cells
data = sht.range('A1:D10').value  # returns list of lists
df   = sht.range('A1').expand().options(pd.DataFrame).value  # as DataFrame

# Charts
chart = sht.charts.add()
chart.chart_type = 'line'
chart.set_source_data(sht.range('A1:B10'))
```

---

## Modular Workflow Architecture

For recurring automated workflows, separate concerns into reusable functions:

```python
# File structure
# automation/
#   main.py        — orchestrator: calls all steps
#   load.py        — all read_excel / data loading functions
#   transform.py   — all cleaning, merging, calculation functions
#   export.py      — all write_excel / formatting functions
#   notify.py      — email / alerting functions

# main.py
from load import load_sales, load_customers
from transform import clean_sales, merge_with_customers, calc_summaries
from export import write_report
from notify import send_report

def run_daily_report():
    # 1. Load
    df_sales = load_sales('data/sales.xlsx')
    df_cust  = load_customers('data/customers.xlsx')

    # 2. Transform
    df = clean_sales(df_sales)
    df = merge_with_customers(df, df_cust)
    summary = calc_summaries(df)

    # 3. Export
    output_path = f"reports/daily_{date.today():%Y-%m-%d}.xlsx"
    write_report(df, summary, output_path)

    # 4. Notify
    send_report(to='team@example.com',
                subject=f'Daily Report {date.today():%d %b %Y}',
                body_html=f'<p>Report attached.</p>',
                attachment_path=output_path)

if __name__ == '__main__':
    run_daily_report()
```

**Key principle (Wengler):** Write and call UDFs (user-defined functions). Importing a UDF module keeps `main.py` as a short orchestrator — each function does one thing and is testable in isolation.
