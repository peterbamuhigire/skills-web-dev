---
name: payroll-postings-uganda
description: Use when designing Uganda payroll accounting postings for gross-to-net payroll, PAYE, NSSF employee deduction, NSSF employer expense, Local Service Tax, salary advances, staff loan recoveries, benefits, net pay, payroll liabilities, remittance journals, and payroll subledger-to-GL reconciliation. Rates and thresholds must be verified against current URA, NSSF, and local government guidance.
metadata:
  portable: true
---

# Payroll Postings Uganda

## Use When

- A Uganda tenant runs payroll or records payroll liabilities.
- The system must post PAYE, NSSF, LST, advances, loans, benefits, and remittances.

## Do Not Use When

- You need legal payroll advice or current statutory thresholds. Flag for verification with URA/NSSF/local government guidance.

## Hard Rules

- MUST separate employee deductions from employer costs.
- MUST not treat employee NSSF as an employer expense.
- MUST post payroll liabilities when payroll is run and clear them when remitted.
- MUST tag payroll lines by employee, department, branch, and period where available.

## Journal Shape

Payroll run:

- Debit salary/wage expense for gross pay.
- Debit employer NSSF expense for employer contribution.
- Credit PAYE payable.
- Credit NSSF payable for employee plus employer amounts.
- Credit LST payable where applicable.
- Credit staff advances receivable for advance recovery.
- Credit staff loans receivable for loan recovery.
- Credit net payroll payable or bank/mobile money for net pay.

Net pay remittance:

- Debit net payroll payable.
- Credit bank/mobile money.

Statutory remittance:

- Debit PAYE payable, NSSF payable, or LST payable.
- Credit bank/mobile money.

## Verification Flags

Uganda rates and thresholds can change. For live implementations, verify:

- PAYE bands and reliefs.
- NSSF employee and employer percentages.
- LST thresholds and district/city rules.
- Tax treatment of benefits, allowances, terminal benefits, and non-residents.

## Outputs

- Payroll posting matrix.
- Payroll liability reconciliation.
- Employee subledger report.
- Remittance checklist.
- Payroll close evidence pack.
